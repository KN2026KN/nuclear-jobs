# Zbiór wynagrodzeń do kalkulatora zarobków (13.11.2026, decyzje właściciela: wszystkie warianty „tak”, z archiwami).
# Źródła: baza ofert (otwarte i zamknięte - wersja z wynagrodzeniem) + archiwa Internet Archive (raw/archiwum, poprzednie lata).
# Każdy rekord: zawód, kraj, waluta, wynagrodzenie roczne brutto w walucie oryginalnej (min-max), pracodawca, rok, obszar,
# poziom, projekt, status. Przeliczenia walut i siły nabywczej robi strona (data/kursy.json).
# Użycie: python3 kod/zarobki.py <baza.sqlite> <wyjście.json>
import json, sqlite3, sys, os, re, gzip, glob, datetime as dt
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kp_zawody import zawod, NAZWY, poziom, POZIOMY
from kp_obszar import obszar
from kp_jadro import jadrowa
from kp_parse import placa
from kp_zawody_slownik import slownik, JEZYKI, JEZYK_WALUTA

K = json.load(open('data/kursy.json', encoding='utf-8')) if os.path.exists('data/kursy.json') else {}
GODZ = K.get('godziny_rok', {'_': 2000}); WAL = K.get('waluty_krajow', {})
ROK_TERAZ = dt.date.today().year
J = {'k': {}, 'f': {}}   # jawność płac: kraj/firma -> rok -> [ofert, z wynagrodzeniem]

def jaw(kraj, firma, rok, z):
    kraj = kraj or '?'; rok = str(rok)
    a = J['k'].setdefault(kraj, {}).setdefault(rok, [0, 0]); a[0] += 1; a[1] += 1 if z else 0
    f = J['f'].setdefault(firma or '?', {'k': kraj, 'y': {}}); b = f['y'].setdefault(rok, [0, 0]); b[0] += 1; b[1] += 1 if z else 0

def roczna(v, per, kraj):
    if v is None: return None
    if per == 'rok': return v
    if per == 'mies': return v * 12
    if per == 'godz': return v * GODZ.get(kraj, GODZ.get('_', 2000))
    return None

def rekord(t, kraj, cur, lo, hi, per, prac, rok, st, url, lv='', proj='', anal=False):
    lo, hi = roczna(lo, per, kraj), roczna(hi or lo, per, kraj)
    if not lo or not cur: return None
    return {'t': t[:120], 'z': zawod(t), 'ob': obszar(t), 'k': kraj or '?', 'w': cur, 'lo': round(lo), 'hi': round(max(lo, hi)),
            'per': per, 'e': (prac or '')[:80], 'y': rok, 's': st, 'u': url, 'lv': lv or poziom(t), 'p': proj or '', 'a': 1 if anal else 0}

def z_bazy(db):
    out = []
    for firm, fs, emp, z in db.execute('''SELECT j.firm, j.first_seen, v.employer,
           EXISTS(SELECT 1 FROM versions w WHERE w.job_key=j.job_key AND w.sal_min IS NOT NULL)
           FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1)'''):
        e = json.loads(emp or '{}')
        if e.get('tylko_analiza'): continue
        jaw(e.get('kraj'), e.get('name') or firm, (fs or str(ROK_TERAZ))[:4], z)
    q = '''SELECT j.firm, j.title, j.status, j.first_seen, j.url, j.level, v.sal_min, v.sal_max, v.sal_period, v.currency, v.employer
           FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key AND sal_min IS NOT NULL ORDER BY seen DESC, id DESC LIMIT 1)'''
    for firm, t, st, fs, url, lv, lo, hi, per, cur, emp in db.execute(q):
        e = json.loads(emp or '{}')
        r = rekord(t or '', e.get('kraj'), cur, lo, hi, per, e.get('name') or firm, int((fs or str(ROK_TERAZ))[:4]), 'o' if st == 'open' else 'c', url, lv, e.get('projekt'), e.get('tylko_analiza'))
        if r: out.append(r)
    return out

ZLY_TYTUL = re.compile(r'search\s*&\s*apply|cookies?|apply now|job details|job search|careers? (at|home)|^jobs?\b|offres? d.emploi|stellenangebote|\bjobs?\s*\|', re.I)

def tytul_z_adresu(u):
    """13.11.2026: także adresy typu /jobs/5408455-soudeur-h-f (numer z przodu, oznaczenie płci na końcu)."""
    s = urlparse(u).path.strip('/').split('/')
    for x in reversed(s):
        x = re.sub(r'^\d+[-_]', '', x)
        x = re.sub(r'[-_](h[-_]f|f[-_]h|m[-_]w[-_]d|m[-_]f[-_]d|w[-_]m[-_]d|m[-_]k)$', '', x, flags=re.I)
        x = re.sub(r'[-_]\d+$', '', x)
        if re.search(r'[a-zà-ÿ]{5,}', x, re.I) and not re.match(r'^(jobs?|offres?|stellen|careers?|carriere|karriere|kariera|vacancies|vacancy|job-details|job-search-results|job-search|search|rest-of-the-world|details?|apply|index|default|[a-z]{2}(-[a-z]{2})?)$', x, re.I) and not re.search(r'\.(html?|aspx?|php)$', x, re.I):
            return re.sub(r'[-_]+', ' ', x).strip().capitalize()
    return ''

def tytul_z_tekstu(tx):
    for l in (tx or '').split('\n')[:15]:
        l = l.strip()
        if 6 <= len(l) <= 90 and not ZLY_TYTUL.search(l) and re.search(r'[A-Za-zÀ-ÿ]{4,}', l) and not re.search(r'[.!?]$', l): return l
    return ''

def z_archiwow():
    G = json.load(open('data/archiwum/glebokosc.json', encoding='utf-8')) if os.path.exists('data/archiwum/glebokosc.json') else {}
    out = []; byly = set()
    for cel, g in G.items():
        for plik in sorted(glob.glob(f'raw/archiwum/{cel}/*.json.gz')):
            rok = int(os.path.basename(plik)[:4])
            if rok >= ROK_TERAZ: continue                     # bieżący rok jest w bazie ofert
            try: of = json.load(gzip.open(plik, 'rt', encoding='utf-8'))['oferty']
            except Exception: continue
            for o in of:
                u = o.get('url', '')
                if o.get('blad') or u in byly: continue
                tx = o.get('tekst') or ''
                t = o.get('tytul') or ''
                if not t or len(t) < 6 or ZLY_TYTUL.search(t): t = tytul_z_adresu(u) or tytul_z_tekstu(tx) or ''
                sc = re.sub(r'[-_/+]+', ' ', urlparse(u).path)
                if not jadrowa(g.get('firma', ''), (t + ' ' + sc).strip(), [('lok', sc), ('opis', tx)])[0]: continue
                byly.add(u)
                lo, hi, per, cur = placa(tx)
                jaw(g.get('kraj'), g.get('firma'), rok, bool(lo and cur))
                r = rekord(t, g.get('kraj'), cur, lo, hi, per, g.get('firma'), rok, 'a', u) if t else None   # bez tytułu płaca nic nie mówi
                if r: out.append(r)
    return out

def main():
    db = sqlite3.connect(sys.argv[1])
    rek = z_bazy(db) + z_archiwow()
    zaw = {k: {'pl': v[0], 'en': v[1]} for k, v in NAZWY.items()}
    json.dump({'wygenerowano': dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'), 'rekordy': rek, 'zawody': zaw, 'poziomy': POZIOMY, 'jawnosc': J,
               'slownik': slownik(), 'jezyki': JEZYKI, 'jezyk_waluta': JEZYK_WALUTA,
               'kursy': {k: K.get(k) for k in ('ebc', 'ppp', 'waluty_krajow', 'godziny_rok', 'odswiezone', 'kursy_przez_usd')}},
              open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print('zarobki: rekordów', len(rek), '| status', dict(Counter(r['s'] for r in rek)), '| kraje', dict(Counter(r['k'] for r in rek).most_common(10)))

if __name__ == '__main__':
    main()
