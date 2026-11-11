# Odbudowa bazy od zera w kolejności chronologicznej: archiwum Wayback, potem dni z raw/RRRR-MM-DD.
# Użycie: python3 rebuild_all.py <folder raw> <nowa_baza.sqlite>
import sys, os, glob, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kp_parse import parse_bechtel, parse_wec, parse_pej, parse_pej_archive, parse_wec_archive, parse_pracuj, parse_ncbj, parse_swiat, wzbogac
from kp_db import connect, ingest, reconcile, presence_only

raw, dbp = sys.argv[1], sys.argv[2]
db = connect(dbp)
db.execute('CREATE TABLE IF NOT EXISTS list_snapshots(firm TEXT, day TEXT, title TEXT, city TEXT, ref TEXT, valid_until TEXT)')
arch = os.path.join(raw, 'archiwum-wayback')
items = []
f = os.path.join(arch, 'kp_archiwum_pej_wayback.json.gz')
if not os.path.exists(f): f = f[:-3]
if os.path.exists(f):
    jobs, lists = parse_pej_archive(f)
    items += [(d, 'pej', r) for d, r in jobs]
    for day, body in lists:
        # tabela: Stanowisko / Lokalizacja / Nr ref. / Ważne do -> wiersze po 4 pola po nagłówku
        try:
            i = body.index('Ważne do')
        except ValueError:
            continue
        rest = body[i + 1:]
        j = 0
        while j + 3 < len(rest):
            t, c, r, v = rest[j:j + 4]
            if not re.match(r'(\d{2}[./-]\d{2}[./-]\d{4}|\d{4}-\d{2}-\d{2})', v): break
            db.execute('INSERT INTO list_snapshots VALUES(?,?,?,?,?,?)', ('pej', day, t, c, r, v)); j += 4
for fw in sorted(glob.glob(os.path.join(arch, 'kp_archiwum_wec_wayback*.json*'))):
    items += [(d, 'westinghouse', r) if t else (d, 'westinghouse-bez-tresci', r) for d, r, t in parse_wec_archive(fw)]
for day, firm, r in sorted(items, key=lambda x: x[0]):
    if firm.endswith('-bez-tresci'): presence_only(db, day, 'wayback', wzbogac(r))
    else: ingest(db, day, 'wayback', firm, [wzbogac(r)], full_list=False)
db.commit()
P = [('kp_bechtel', '.json', 'bechtel', parse_bechtel), ('kp_wec', '.json', 'westinghouse', parse_wec), ('kp_pej', '.txt', 'pej', parse_pej), ('kp_pracuj', '.json', 'pracuj', parse_pracuj), ('kp_ncbj', '.json', 'ncbj', parse_ncbj),
     ('kp_sw_', '.json', None, parse_swiat)]
PAM = {}   # 11.2026: pamięć pełnych treści z wcześniejszych dni (robot pobiera treść tylko nowych ofert)
for dd in sorted(glob.glob(os.path.join(raw, '20??-??-??'))):
    day = os.path.basename(dd)
    for fpath in sorted(glob.glob(os.path.join(dd, 'kp_*'))):
        n = os.path.basename(fpath)
        for pre, ext, firm, fn in P:
            if n.startswith(pre) and (n.endswith(ext) or n.endswith(ext + '.gz')) and '_lista_' not in n:
                if firm is None: firm = re.match(r'kp_sw_(.+)_\d{8}', n).group(1)
                wynik = fn(fpath, PAM.setdefault(firm, {}))
                recs = [wzbogac(r) for r in wynik[1]]
                if len(wynik) > 2 and not wynik[2]: print(f'UWAGA {day} {firm}: lista niepełna - bez zamykania ofert')
                prev = db.execute("SELECT n FROM runs WHERE firm=? AND note='full' ORDER BY day DESC LIMIT 1", (firm,)).fetchone()
                full = bool(recs) and not (prev and len(recs) < 0.7 * prev[0]) and (len(wynik) < 3 or wynik[2])
                if not full: print(f'UWAGA {day} {firm}: {len(recs)} ofert - wczytane bez zamykania ofert')
                ingest(db, day, 'employer', firm, recs, full_list=full)
reconcile(db)
for r in db.execute('SELECT firm, status, count(*) FROM jobs GROUP BY 1,2'): print(r)
print('migawki listy PEJ:', db.execute('SELECT count(*), count(DISTINCT day) FROM list_snapshots').fetchone())
