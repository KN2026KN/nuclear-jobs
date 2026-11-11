# Statystyki ofert dla właściciela (11.2026) - bez treści ofert. Format: docs/STATYSTYKI.md.
# Użycie: python3 kod/statystyki.py <baza.sqlite> <dzień> <wyjście.json>
import json, sqlite3, sys, statistics, datetime, re
from collections import Counter, defaultdict

db = sqlite3.connect(sys.argv[1]); DZIEN = sys.argv[2]
d0 = datetime.date.fromisoformat(DZIEN)
rows = db.execute('''SELECT j.job_key, j.firm, j.status, j.first_seen, j.last_seen, j.closed_on, j.func, j.level,
  v.sal_min, v.sal_max, v.sal_period, v.currency, v.employer
  FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1)''').fetchall()

def okres(dzien):
    """dzień -> klucz grupy: ostatnie 60 dni dziennie, bieżący rok miesięcznie, starsze lata rocznie"""
    if not dzien: return None
    d = datetime.date.fromisoformat(dzien[:10])
    if (d0 - d).days < 60: return d.isoformat()
    if d.year == d0.year: return d.strftime('%Y-%m')
    return str(d.year)

def wyn(lista):
    lista = sorted(lista)
    return {'n': len(lista), 'mediana': round(statistics.median(lista)), 'min': lista[0], 'max': lista[-1]} if lista else None

otwarte = defaultdict(Counter); analiza = defaultdict(Counter)
# pokrycie (11.11.2026): kraj -> pracodawca -> liczba otwartych ofert w terminie (to, co może być na stronie)
NAZWY = {'bechtel': 'Bechtel', 'westinghouse': 'Westinghouse', 'pej': 'Polskie Elektrownie Jądrowe (PEJ)', 'ncbj': 'Narodowe Centrum Badań Jądrowych (NCBJ)'}
pokrycie = defaultdict(lambda: defaultdict(lambda: {'n': 0, 'zrodla': set()}))
nowe = Counter(); zamk = Counter(); nowe_a = Counter(); zamk_a = Counter()
place = defaultdict(list)   # (wymiar, wartość, waluta, okres) -> wartości środka widełek
zycie = []
for key, firm, st, fs, ls, co, fn, lv, smin, smax, per, cur, emp in rows:
    e = json.loads(emp or '{}'); a = bool(e.get('tylko_analiza'))
    wym = {'kraj': e.get('kraj') or '?', 'projekt': e.get('projekt') or '-', 'typ_obiektu': e.get('typ_obiektu') or '-',
           'pracodawca': e.get('name') or firm, 'zrodlo': firm, 'funkcja': fn or '-', 'poziom': lv or '-', 'jezyk': e.get('jezyk') or '?'}
    if st == 'open':
        for k, v in wym.items(): (analiza if a else otwarte)[k][v] += 1
        dl = e.get('wazne_do') or e.get('valid_until')
        if not a and not (dl and str(dl)[:10] < DZIEN and str(dl)[:4].isdigit()):
            nz = NAZWY.get(firm) or (e.get('name') or firm).strip()
            if firm == 'pracuj':
                for k2, v2 in (('Bechtel', 'Bechtel'), ('Westinghouse', 'Westinghouse'), ('Polskie Elektrownie J', 'Polskie Elektrownie Jądrowe (PEJ)')):
                    if k2.lower() in nz.lower(): nz = v2
            x = pokrycie[e.get('kraj') or '?'][nz[:80]]; x['n'] += 1; x['zrodla'].add(firm)
    (nowe_a if a else nowe)[okres(fs)] += 1
    if st == 'closed':
        (zamk_a if a else zamk)[okres(co or ls)] += 1
        if fs and (co or ls): zycie.append((datetime.date.fromisoformat((co or ls)[:10]) - datetime.date.fromisoformat(fs[:10])).days)
    if smin and per in ('mies', 'rok', 'godz'):
        srodek = (smin + (smax or smin)) / 2
        for k in ('funkcja', 'kraj', 'zrodlo', 'projekt'):
            place[(('A:' if a else '') + k, wym[k], cur or '?', per)].append(round(srodek))

def tab(c): return dict(sorted(c.items(), key=lambda x: (-x[1], str(x[0]))))
def czas(c): return dict(sorted((k, v) for k, v in c.items() if k))
wynagrodzenia = defaultdict(dict)
for (k, v, cur, per), L in place.items():
    wynagrodzenia[k].setdefault(v, []).append({'waluta': cur, 'okres': per, **wyn(L)})

import os
ZR = {'pej': ('PEJ', 'PL'), 'pracuj': ('pracuj.pl', 'PL'), 'ncbj': ('NCBJ', 'PL'), 'kprm': ('Nabory KPRM (PAA, ministerstwa)', 'PL'), 'clor': ('CLOR', 'PL'),
      'kznpp': ('Kozloduy NPP', 'BG'), 'snn': ('Nuclearelectrica', 'RO'), 'szc': ('Sizewell C', 'GB'), 'hpc': ('HPC / SZC Jobs Service', 'GB'), 'iter': ('ITER', 'FR'),
      'iaea': ('IAEA', 'AT'), 'edfuk': ('EDF Energy', 'GB'), 'fortum': ('Fortum', 'FI'), 'cez': ('ČEZ', 'CZ'), 'orano': ('Orano', 'FR'), 'cea': ('CEA', 'FR'),
      'vattenfall': ('Vattenfall', 'SE'), 'bechtel': ('Bechtel', 'świat'), 'wec': ('Westinghouse', 'świat'), 'opg': ('Ontario Power Generation', 'CA')}
try: KONF = {'pr_' + c['klucz']: c for c in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pracodawcy', 'podlaczone.json'), encoding='utf-8'))}
except Exception: KONF = {}
raport = {}
try: raport = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw', DZIEN, 'raport_zbierania.json')))
except Exception: pass
# głębokość archiwów (11.11.2026): data/archiwum/glebokosc.json z robota kod/archiwum.py
try: archiwa = json.load(open('data/archiwum/glebokosc.json', encoding='utf-8'))
except Exception: archiwa = {}
# potencjalni pracodawcy (11.11.2026): lista data/pracodawcy/kandydaci.tsv + wynik sondy stron kariery
PODL = re.compile(r'PEJ|Polskie Elektrownie|NCBJ|Atomistyki|CLOR|Kozloduy NPP$|Nuclearelectrica|Sizewell C|EDF Energy|ITER|IAEA|Fortum|ČEZ|Orano|CEA$|Vattenfall|Ontario Power|Westinghouse', re.I)
kandydaci = []
try:
    for k in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pracodawcy', 'sonda.json'), encoding='utf-8')):
        stan = 'podłączony' if (PODL.search(k['nazwa']) or k['nazwa'] in {c['pracodawca'] for c in KONF.values()}) else ('strona kariery' if k.get('kariera') and k.get('kariera_status') == 200 else ('strona dostępna' if k.get('status') == 200 else 'brak dostępu z runnera'))
        kandydaci.append({'kraj': k['kraj'], 'kategoria': k['kategoria'], 'nazwa': k['nazwa'], 'www': k['www'], 'kariera': k.get('kariera'), 'platforma': k.get('platforma') or [],
                          'linki_ofert': k.get('linki_ofert'), 'stan': stan})
except Exception as ex:
    print('kandydaci:', ex)
out = {
    'dzien': DZIEN,
    'kandydaci': kandydaci,
    'archiwa': archiwa,
    'pokrycie': {k: dict(sorted(((p, {'n': v['n'], 'zrodla': sorted(v['zrodla'])}) for p, v in pr.items()), key=lambda t: -t[1]['n']))
                 for k, pr in sorted(pokrycie.items(), key=lambda t: (t[0] != 'PL', -sum(v['n'] for v in t[1].values())))},
    'zrodla': {k: {'nazwa': ZR.get(k, (KONF.get(k, {}).get('pracodawca', k), ''))[0], 'kraj': ZR.get(k, ('', KONF.get(k, {}).get('kraj', '')))[1], 'ok': v.get('ok'), 'n': v.get('n'), 's': v.get('s'), 'blad': v.get('err')}
               for k, v in raport.items() if isinstance(v, dict) and 'ok' in v},
    'rotacja': raport.get('_rotacja'),
    'niepodlaczone': [['ENEC (Barakah)', 'AE', 'brak połączenia z runnera GitHub'], ['Nawah (Barakah)', 'AE', 'brak połączenia z runnera GitHub'],
                      ['Framatome', 'FR', '403'], ['EDF (Francja)', 'FR', 'lista ładowana skryptem'], ['F4E', 'ES', 'lista ładowana skryptem'],
                      ['Sellafield Ltd', 'GB', 'lista przez admin-ajax (POST)'], ['Slovenské elektrárne', 'SK', 'lista ładowana skryptem'],
                      ['OSGE', 'PL', 'lista ładowana skryptem'], ['ZUOP', 'PL', '403 (BIP)'], ['KCOR', 'PL', '403 (BIP)'], ['UDT', 'PL', 'brak listy ofert (oferty na pracuj.pl)'],
                      ['TVO', 'FI', 'zewnętrzny system ofert'], ['Kozloduy NPP-Newbuild', 'BG', 'brak połączenia']], 'wygenerowano': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'otwarte_razem': sum(otwarte['kraj'].values()), 'tylko_analiza_otwarte': sum(analiza['kraj'].values()),
    'otwarte': {k: tab(v) for k, v in otwarte.items()},
    'tylko_analiza': {k: tab(v) for k, v in analiza.items()},
    'nowe': czas(nowe), 'zamkniete': czas(zamk), 'nowe_tylko_analiza': czas(nowe_a), 'zamkniete_tylko_analiza': czas(zamk_a),
    'wynagrodzenia': {k: v for k, v in wynagrodzenia.items() if not k.startswith('A:')},          # wszystkie oferty w historii, waluta oryginalna
    'wynagrodzenia_tylko_analiza': {k[2:]: v for k, v in wynagrodzenia.items() if k.startswith('A:')},
    'czas_zycia_dni': {'srednia': round(sum(zycie) / len(zycie), 1) if zycie else None, 'mediana': statistics.median(zycie) if zycie else None, 'n': len(zycie)},
    'zrodla_ostatni_przebieg': [dict(zip(('zrodlo', 'n', 'tryb'), r)) for r in db.execute("SELECT firm, n, note FROM runs WHERE day=? AND source='employer'", (DZIEN,))],
}
json.dump(out, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('statystyki:', out['otwarte_razem'], 'otwartych,', out['tylko_analiza_otwarte'], 'tylko do analizy,', len(out['nowe']), 'okresów')
