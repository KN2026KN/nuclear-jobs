# Dane i treść strony keura.eu/praca (PL) i jej wersji EN z bazy (10.11.2026, rozbudowa świat 11.2026).
# Użycie: python3 kod/strona_praca.py <baza.sqlite> <dzień> <wyjście_pl.html> [<wyjście_en.html>]
# Zasady właściciela:
# - cały świat, priorytet Europa; NIGDY na stronie: Rosatom i spółki, Rosja, Białoruś, Węgry (znacznik tylko_analiza - zostają w bazie)
# - oferty lokalne wszystkie, w oryginale, z plakietką języka; filtry „Kraj” (flagi - obrazki) i „Język ogłoszenia” pod wyszukiwarką
# - strona „żywa”: pracodawca / kraj / projekt / sektor tylko przy >= 1 ofercie
# - link do strony pracodawcy, gdy oferta tam jest; portal tylko gdy brak; kontrola eksportu nigdy na stronie; bez nazwisk rekruterów
# - oferta po terminie ważności znika ze strony
import base64, json, os, re, sqlite3, sys, unicodedata, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kp_db import func, lvl
from kp_jadro import sektor, stanowisko_jadrowe
from kp_projekty import NAZWA_PL, NAZWA_EN, PROJEKT_TYP

db = sqlite3.connect(sys.argv[1]); DZIEN = sys.argv[2]
NAZWY = {'bechtel': 'Bechtel', 'westinghouse': 'Westinghouse Electric Company', 'pej': 'Polskie Elektrownie Jądrowe (PEJ)', 'ncbj': 'Narodowe Centrum Badań Jądrowych (NCBJ)'}
TRYB = {'stacjonarnie': 'st', 'hybrydowo': 'hy', 'zdalnie': 'zd'}
# sektor wg pracodawcy, gdy projekt nie rozstrzyga (bud = budowa, eks = eksploatacja, dos = dostawcy, doz = dozór, nau = nauka, odp = odpady)
SEKTOR_ZR = {'westinghouse': 'dos', 'bechtel': 'bud', 'pej': 'bud', 'kprm': 'doz', 'clor': 'nau', 'orano': 'dos', 'cea': 'nau', 'ncbj': 'nau',
             'kznpp': 'eks', 'snn': 'eks', 'cez': 'eks', 'seas': 'eks', 'vattenfall': 'eks', 'edfuk': 'eks', 'hpc': 'bud', 'szc': 'bud',
             'iter': 'nau', 'iaea': 'doz', 'fortum': 'eks', 'opg': 'eks'}
SEKTOR_TYP = {'bud': 'bud', 'smr': 'bud', 'eks': 'eks', 'odp': 'odp', 'bad': 'nau', 'fuz': 'nau', 'ins': 'doz'}

def norm(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower()).encode('ascii', 'ignore').decode()).strip()

rows = db.execute('''SELECT j.job_key, j.firm, j.ext_id, j.url, j.title, j.city, j.posted, v.mode, v.sal_min, v.sal_max, v.sal_period, v.employer, v.category, v.locations, v.currency, v.text
  FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) WHERE j.status='open' ''').fetchall()
oficjalne = {f: set() for f in NAZWY}; ofref = set()
for r in rows:
    if r[1] in NAZWY: oficjalne[r[1]].add(norm(r[4])); ofref.add((r[1], str(r[2])))

out = []; pominiete = {'tylko_analiza': 0, 'po_terminie': 0, 'duplikat': 0}
for key, firm, ext, url, title, city, posted, mode, smin, smax, per, emp, cat, locs, cur, txt in rows:
    emp = json.loads(emp or '{}')
    if emp.get('tylko_analiza'): pominiete['tylko_analiza'] += 1; continue
    k = emp.get('kraj') or 'PL'
    pr = emp.get('projekt'); typ = emp.get('typ_obiektu')
    dl = emp.get('wazne_do') or emp.get('valid_until') or None
    if firm == 'pracuj':
        nazwa = emp.get('name') or ''
        f2 = 'bechtel' if re.search('Bechtel', nazwa, re.I) else 'westinghouse' if re.search('Westinghouse', nazwa, re.I) else 'pej' if re.search('Polskie Elektrownie J', nazwa, re.I) else None
        if f2 and ((f2, str(emp.get('ref'))) in ofref or norm(title) in oficjalne[f2]): pominiete['duplikat'] += 1; continue
        e, s = (NAZWY[f2] if f2 else nazwa), sektor(nazwa)
        s = {'bud': 'bud', 'odp': 'odp', 'doz': 'doz', 'nau': 'nau'}.get(s, 'dos')
    else:
        e = NAZWY.get(firm) or emp.get('name') or firm
        s = SEKTOR_TYP.get(typ) or emp.get('sektor_zr') or SEKTOR_ZR.get(firm, 'dos')
    if firm in ('bechtel', 'westinghouse', 'pej') and k == 'PL':     # inwestor i wykonawcy AP1000: każda oferta w Polsce dotyczy projektu
        s = 'bud'; pr = pr or 'AP1000 Lubiatowo-Kopalino'; typ = typ or 'bud'
    if dl and re.match(r'\d{2}\.\d{2}\.\d{4}', dl): dl = f'{dl[6:10]}-{dl[3:5]}-{dl[0:2]}'
    if dl and re.match(r'\d{4}-\d{2}-\d{2}', dl) and dl < DZIEN: pominiete['po_terminie'] += 1; continue
    c = (city or '').strip()
    if c and re.search(r'Lubiatowo|Choczewo|Kopalino', c, re.I): c = 'Lubiatowo-Kopalino'
    if c.lower() in ('unspecified', 'remote', ''): c = ''
    sal = None
    if smin and per in ('mies', 'rok', 'godz'):
        sal = {'min': smin, 'max': smax or smin, 'per': per, 'cur': cur or 'PLN'}
        if firm == 'pracuj': sal['typ'] = emp.get('brutto_netto')
    out.append({'t': title, 'e': e, 's': s, 'p': pr or '', 'k': k, 'l': emp.get('jezyk') or '', 'c': c, 'm': TRYB.get(mode, 'np'),
                'fn': (fn := func(firm, title, cat, txt)), 'nj': 1 if stanowisko_jadrowe(title, fn) else 0, 'lv': lvl(title), 'sal': sal, 'u': url, 'pub': (posted or '')[:10] if re.match(r'\d{4}-\d{2}-\d{2}', posted or '') else None, 'dl': dl})

# kursy walut NBP (tabela A, dzień roboczy) - tylko do sortowania po wynagrodzeniu między walutami
KURSY = {'PLN': 1.0}
try:
    import requests
    for t in requests.get('https://api.nbp.pl/api/exchangerates/tables/A/?format=json', timeout=20).json()[0]['rates']:
        KURSY[t['code']] = t['mid']
except Exception as ex:
    print('kursy NBP niedostępne:', ex)

B = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strona', 'praca')
TEKST = {
 'pl': {'h1': 'Praca w sektorze jądrowym', 'ph': 'np. spawacz, inżynier jakości, ochrona radiologiczna', 'szukaj': 'Szukaj', 'oferty': 'Oferty', 'prac': 'Pracodawcy',
        'kraje': 'Kraje', 'zwyn': 'Z wynagrodzeniem', 'stan': 'Stan na', 'promo': 'Zespoły w projektach jądrowych pracują według ISO 19443 i ASME NQA-1. Szkolenia z tych wymagań prowadzę dla firm z łańcucha dostaw.',
        'tylko_j': 'Tylko stanowiska jądrowe', 'promo_btn': 'Zobacz szkolenia', 'promo_url': 'https://keura.eu/szkolenia/', 'filtry': 'Filtry', 'wyczysc': 'Wyczyść wszystko', 'pokaz': 'Pokaż oferty',
        'sort_sal': 'Najwyższe wynagrodzenie', 'sort_new': 'Najnowsze', 'sort_dl': 'Kończą się wkrótce', 'aktual': 'Aktualizacja', 'codz': 'codziennie'},
 'en': {'h1': 'Jobs in the nuclear sector', 'ph': 'e.g. welder, quality engineer, radiation protection', 'szukaj': 'Search', 'oferty': 'Jobs', 'prac': 'Employers',
        'kraje': 'Countries', 'zwyn': 'With salary', 'stan': 'As of', 'promo': 'Teams on nuclear projects work to ISO 19443 and ASME NQA-1. I run training on these requirements for supply chain companies.',
        'tylko_j': 'Nuclear roles only', 'promo_btn': 'See training', 'promo_url': 'https://keura.eu/en/training/', 'filtry': 'Filters', 'wyczysc': 'Clear all', 'pokaz': 'Show jobs',
        'sort_sal': 'Highest salary', 'sort_new': 'Newest', 'sort_dl': 'Closing soon', 'aktual': 'Updated', 'codz': 'daily'},
}

def strona(jez, plik):
    T = TEKST[jez]
    kraje = NAZWA_PL if jez == 'pl' else NAZWA_EN
    dane = {'stan': DZIEN, 'jez': jez, 'oferty': out, 'kraje': {o['k']: kraje.get(o['k'], o['k']) for o in out}, 'kursy': KURSY,
            'typy': {p: PROJEKT_TYP.get(p) for p in {o['p'] for o in out if o['p']}}}
    js = open(os.path.join(B, 'skrypt.js'), encoding='utf-8').read()
    # WordPress zamienia „&&” w treści strony na „&#038;&” - skrypt idzie jako base64 (bez „&&” w HTML)
    js64 = base64.b64encode(js.encode('utf-8')).decode()
    loader = "(function(){var b=atob('" + js64 + "');var u=new TextDecoder('utf-8').decode(Uint8Array.from(b,function(c){return c.charCodeAt(0)}));new Function(u)()})();"
    html = open(os.path.join(B, 'szablon.html'), encoding='utf-8').read()
    for k2, v in T.items(): html = html.replace('{{' + k2 + '}}', v)
    html = html.replace('{{LANG}}', jez).replace('{{STYL}}', open(os.path.join(B, 'styl.css'), encoding='utf-8').read()).replace('{{SKRYPT}}', loader)
    html = html.replace('{{DANE}}', json.dumps(dane, ensure_ascii=False).replace('</', '<\\/').replace('&', '\\u0026'))
    assert '&&' not in html, 'w HTML zostało „&&” - WordPress to zepsuje'
    open(plik, 'w', encoding='utf-8').write(html)

strona('pl', sys.argv[3])
if len(sys.argv) > 4: strona('en', sys.argv[4])
from collections import Counter
print('ofert na stronie:', len(out), '| kraje:', dict(Counter(o['k'] for o in out).most_common()), '| sektory:', dict(Counter(o['s'] for o in out)),
      '| pracodawcy:', len({o['e'] for o in out}), '| pominięte:', pominiete)
