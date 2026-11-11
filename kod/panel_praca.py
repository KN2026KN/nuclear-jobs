# Prywatny panel ofert pracy (10.11.2026): statystyki i wynagrodzenia wg pracodawcy i rodzaju stanowiska, historia od 2021 r.
# Tylko dla właściciela (bot Keura, link z kluczem) - nie na stronie. Użycie: python3 kod/panel_praca.py <baza.sqlite> <dzień> <wyjście.html>
import json, os, re, sqlite3, sys
from collections import defaultdict
db = sqlite3.connect(sys.argv[1]); DZIEN = sys.argv[2]
NAZWY = {'bechtel': 'Bechtel', 'westinghouse': 'Westinghouse', 'pej': 'PEJ', 'ncbj': 'NCBJ'}
def mies(v, per):
    if v is None: return None
    return round(v / 12) if per == 'rok' else (round(v * 168) if per == 'godz' else v)
rows = db.execute('''SELECT j.job_key, j.firm, j.url, j.title, j.city, j.first_seen, j.last_seen, j.status, j.func, j.level,
  v.sal_min, v.sal_max, v.sal_period, v.employer, v.mode, v.tags
  FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1)''').fetchall()
def firma(firm, emp):
    n = NAZWY.get(firm) or ((emp or {}).get('name') or firm)
    for k, v in (('bechtel', 'Bechtel'), ('westinghouse', 'Westinghouse'), ('polskie elektrownie j', 'PEJ'), ('narodowe centrum bada', 'NCBJ'), ('finow', 'FINOW Polska')):
        if k in n.lower(): return v
    return n[:40]
J = []
for key, firm, url, title, city, fs, ls, st, fn, lv, smin, smax, per, emp, mode, tags in rows:
    emp = json.loads(emp or '{}')
    try: ek = (json.loads(tags or '{}').get('kontrola_eksportu') or [''])[0]
    except Exception: ek = ''
    J.append({'f': firma(firm, emp), 't': title, 'c': city or '', 'fn': fn, 'lv': lv, 'a': fs, 'b': ls, 'o': st == 'open',
              'mn': mies(smin, per), 'mx': mies(smax or smin, per), 'u': url, 'm': mode or '', 'ek': ek, 'src': 'portal' if firm == 'pracuj' else 'strona'})
# duplikaty: ta sama oferta na portalu i na stronie pracodawcy liczy się raz (zostaje oficjalna)
norm = lambda t: re.sub(r'[^a-z0-9]', '', (t or '').lower())
ofic = {(x['f'], norm(x['t'])) for x in J if x['src'] == 'strona'}
J = [x for x in J if x['src'] == 'strona' or (x['f'], norm(x['t'])) not in ofic]
# historia: liczba otwartych ofert na dzień, wg pracodawcy (z obserwacji)
H = defaultdict(lambda: defaultdict(int))
fm = {r['u']: r['f'] for r in J}
for day, firm, emp in db.execute('''SELECT o.seen, j.firm, (SELECT employer FROM versions WHERE job_key=j.job_key ORDER BY id DESC LIMIT 1)
  FROM observations o JOIN jobs j ON j.job_key=o.job_key'''):
    H[day[:7]][firma(firm, json.loads(emp or '{}'))] += 1
# średnio na dzień w miesiącu
dni = defaultdict(set)
for (day,) in db.execute('SELECT DISTINCT seen FROM observations'): dni[day[:7]].add(day)
hist = {m: {f: round(n / max(1, len(dni[m]))) for f, n in v.items()} for m, v in sorted(H.items())}
dane = json.dumps({'dzien': DZIEN, 'oferty': J, 'hist': hist}, ensure_ascii=False).replace('</', '<\\/')
SZ = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'strona', 'praca', 'panel.html'), encoding='utf-8').read()
open(sys.argv[3], 'w', encoding='utf-8').write(SZ.replace('{{DANE}}', dane))
print('panel: ofert w historii', len(J), '| otwartych', sum(1 for x in J if x['o']), '| z wynagrodzeniem', sum(1 for x in J if x['mn']))
