# Nocna aktualizacja strony keura.eu/praca (strona 7194) i wersji EN z bazy ofert (10.11.2026, EN 11.2026).
# Status strony się nie zmienia: szkic zostaje szkicem, dopóki właściciel nie zatwierdzi publikacji.
# Użycie: python3 strona/praca_publikuj.py <plik_pl.html> [<plik_en.html>]
# Wersja EN: strona-szkic o slugu „nuclear-jobs” (tworzona jako SZKIC przy pierwszym przebiegu, język WPML: en).
import hashlib, json, os, re, sys, requests
U, P = os.environ['WP_USER'], os.environ['WP_APP_PASSWORD']
UA = {'User-Agent': 'keura-robot/1.0 (+https://keura.eu)'}
API = 'https://keura.eu/wp-json/wp/v2/pages'
STRONA_PL = 7194
SLUG_EN, TYTUL_EN = 'nuclear-jobs', 'Jobs in the nuclear sector'

def zapisz(pid, html, jez):
    api = f'{API}/{pid}'
    teraz = requests.get(api + '?context=edit&_fields=status,content', auth=(U, P), headers=UA, timeout=60).json()
    stare = (teraz.get('content') or {}).get('raw', '')
    n = len(json.loads(re.search(r'id="kp-dane">(.*?)</script>', html, re.S).group(1).replace('<\\/', '</'))['oferty'])
    if hashlib.sha1(stare.strip().encode()).hexdigest() == hashlib.sha1(html.strip().encode()).hexdigest():
        print(f'praca {jez}: bez zmian ({n} ofert, status {teraz.get("status")})'); return True
    r = requests.post(api, auth=(U, P), headers=UA, json={'content': html}, timeout=120); r.raise_for_status()
    po = requests.get(api + '?context=edit&_fields=status,content,link', auth=(U, P), headers=UA, timeout=60).json()
    zgodne = (po.get('content') or {}).get('raw', '').strip() == html.strip()
    print(f"praca {jez}: strona {pid}, zapisano {n} ofert, status {po.get('status')}, zgodne po odczycie: {zgodne}")
    return zgodne

def strona_en():
    r = requests.get(API, params={'slug': SLUG_EN, 'status': 'draft,private,publish,pending', 'context': 'edit', '_fields': 'id,status', 'lang': 'en'}, auth=(U, P), headers=UA, timeout=60)
    s = r.json() if r.ok else []
    if s: return s[0]['id']
    w = requests.post(API + '?lang=en', json={'title': TYTUL_EN, 'slug': SLUG_EN, 'status': 'draft', 'content': '<!-- wp:html --><!-- /wp:html -->'}, auth=(U, P), headers=UA, timeout=60)
    w.raise_for_status(); print('praca en: utworzono SZKIC strony', w.json()['id']); return w.json()['id']

ok = zapisz(STRONA_PL, open(sys.argv[1], encoding='utf-8').read(), 'pl')
if len(sys.argv) > 2:
    ok = zapisz(strona_en(), open(sys.argv[2], encoding='utf-8').read(), 'en') and ok
if not ok: sys.exit(1)
