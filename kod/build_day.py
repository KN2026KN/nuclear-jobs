# Wczytuje surowe pliki z jednego dnia do bazy. Użycie: python3 build_day.py <katalog_raw_dnia> <data YYYY-MM-DD> <baza.sqlite>
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kp_parse import parse_bechtel, parse_wec, parse_pej
from kp_db import connect, ingest

raw, day, dbp = sys.argv[1], sys.argv[2], sys.argv[3]
db = connect(dbp)
P = [('kp_bechtel', '.json', 'bechtel', parse_bechtel), ('kp_wec', '.json', 'westinghouse', parse_wec), ('kp_pej', '.txt', 'pej', parse_pej)]
for f in sorted(glob.glob(os.path.join(raw, 'kp_*'))):
    n = os.path.basename(f)
    for pre, ext, firm, fn in P:
        if n.startswith(pre) and (n.endswith(ext) or n.endswith(ext + '.gz')) and '_lista_' not in n:
            recs = fn(f)[1]
            prev = db.execute("SELECT n FROM runs WHERE firm=? AND note='full' ORDER BY day DESC LIMIT 1", (firm,)).fetchone()
            full = True
            if not recs or (prev and len(recs) < 0.7 * prev[0]):
                full = False
                print(f'UWAGA {firm}: {len(recs)} ofert wobec {prev[0] if prev else "?"} poprzednio - wczytane bez zamykania ofert')
            ingest(db, day, 'employer', firm, recs, full_list=full)
for r in db.execute("SELECT firm, status, count(*) FROM jobs GROUP BY 1,2"): print(r)
for r in db.execute("SELECT type, count(*) FROM events WHERE day=? GROUP BY 1", (day,)): print('zdarzenia', r)
