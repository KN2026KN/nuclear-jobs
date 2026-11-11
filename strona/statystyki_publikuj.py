# Statystyki ofert -> PRYWATNA strona WP „KP statystyki - dane” (slug kp-statystyki-dane), tylko dla właściciela (11.2026).
# Treść: <!-- wp:html --><script type="application/json" id="kp-stat">{…}</script><!-- /wp:html -->. Panel w WP buduje właściciel osobno.
# Użycie: python3 strona/statystyki_publikuj.py <statystyki.json>
import json, os, sys, requests
U, P = os.environ['WP_USER'], os.environ['WP_APP_PASSWORD']
UA = {'User-Agent': 'keura-robot/1.0 (+https://keura.eu)'}
API = 'https://keura.eu/wp-json/wp/v2/pages'
SLUG = 'kp-statystyki-dane'
dane = json.dumps(json.load(open(sys.argv[1], encoding='utf-8')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('&', '\\u0026')
# 11.11.2026: strona = gotowy panel (pokrycie krajów i pracodawców, źródła, wykresy) + ten sam JSON w script#kp-stat
import base64
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'praca')
js = base64.b64encode(open(os.path.join(B, 'statystyki.js'), encoding='utf-8').read().encode()).decode()
loader = "(function(){var b=atob('" + js + "');new Function(new TextDecoder('utf-8').decode(Uint8Array.from(b,function(c){return c.charCodeAt(0)})))()})();"
tresc = open(os.path.join(B, 'statystyki.html'), encoding='utf-8').read().replace('{{DANE}}', dane).replace('{{SKRYPT}}', loader)
assert '&&' not in tresc
r = requests.get(API, params={'slug': SLUG, 'status': 'private,draft,publish', 'context': 'edit', '_fields': 'id,status'}, auth=(U, P), headers=UA, timeout=60)
r.raise_for_status(); s = r.json()
if s:
    pid = s[0]['id']
    if s[0]['status'] != 'private': print('UWAGA: strona statystyk nie jest prywatna:', s[0]['status'])
    w = requests.post(f'{API}/{pid}', json={'content': tresc, 'status': 'private'}, auth=(U, P), headers=UA, timeout=120)
else:
    w = requests.post(API, json={'title': 'KP statystyki - dane', 'slug': SLUG, 'status': 'private', 'content': tresc}, auth=(U, P), headers=UA, timeout=120)
w.raise_for_status()
print('statystyki: strona', w.json().get('id'), 'status', w.json().get('status'), 'bajtów', len(tresc))
