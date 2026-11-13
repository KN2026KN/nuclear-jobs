# Kalkulator zarobków -> PRYWATNA strona WP „KP kalkulator zarobków” (slug kp-zarobki), tylko dla właściciela (13.11.2026).
# Ten sam wzór co statystyki_publikuj.py: szablon strona/praca/zarobki.html + skrypt zarobki.js (base64) + JSON w script#kz-dane.
# Użycie: python3 strona/zarobki_publikuj.py <zarobki.json> [--podglad plik.html]  (z --podglad tylko zapis lokalny, bez WP)
import json, os, sys, base64
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'praca')
dane = json.dumps(json.load(open(sys.argv[1], encoding='utf-8')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('&', '\\u0026')
js = base64.b64encode(open(os.path.join(B, 'zarobki.js'), encoding='utf-8').read().encode()).decode()
loader = "(function(){var b=atob('" + js + "');new Function(new TextDecoder('utf-8').decode(Uint8Array.from(b,function(c){return c.charCodeAt(0)})))()})();"
tresc = open(os.path.join(B, 'zarobki.html'), encoding='utf-8').read().replace('{{DANE}}', dane).replace('{{SKRYPT}}', loader)
assert '&&' not in tresc
if '--podglad' in sys.argv:
    open(sys.argv[sys.argv.index('--podglad') + 1], 'w', encoding='utf-8').write(tresc); print('podgląd zapisany'); sys.exit(0)
import requests
U, P = os.environ['WP_USER'], os.environ['WP_APP_PASSWORD']
UA = {'User-Agent': 'keura-robot/1.0 (+https://keura.eu)'}
API = 'https://keura.eu/wp-json/wp/v2/pages'
SLUG = 'kp-zarobki'
r = requests.get(API, params={'slug': SLUG, 'status': 'private,draft,publish', 'context': 'edit', '_fields': 'id,status'}, auth=(U, P), headers=UA, timeout=60)
r.raise_for_status(); s = r.json()
if s:
    pid = s[0]['id']
    if s[0]['status'] != 'private': print('UWAGA: strona zarobków nie jest prywatna:', s[0]['status'])
    w = requests.post(f'{API}/{pid}', json={'content': tresc, 'status': 'private'}, auth=(U, P), headers=UA, timeout=120)
else:
    w = requests.post(API, json={'title': 'KP kalkulator zarobków', 'slug': SLUG, 'status': 'private', 'content': tresc}, auth=(U, P), headers=UA, timeout=120)
w.raise_for_status()
print('zarobki: strona', w.json().get('id'), 'status', w.json().get('status'), 'link', w.json().get('link'), 'bajtów', len(tresc))
