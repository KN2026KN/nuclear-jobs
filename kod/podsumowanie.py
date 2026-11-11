# Krótkie podsumowanie dnia z bazy: python3 kod/podsumowanie.py kp.sqlite RRRR-MM-DD > data/dzien/RRRR-MM-DD.json
import sys, json, sqlite3
db = sqlite3.connect(sys.argv[1]); day = sys.argv[2]
ev = [dict(zip(('firma', 'id', 'stanowisko', 'typ', 'szczegoly', 'url'), r)) for r in db.execute(
    "SELECT j.firm, j.ext_id, j.title, e.type, e.detail, j.url FROM events e JOIN jobs j USING(job_key) WHERE e.day=? AND e.detail NOT LIKE 'wayback%' ORDER BY j.firm", (day,))]
otw = dict(db.execute("SELECT firm, count(*) FROM jobs WHERE status='open' GROUP BY firm").fetchall())
runs = [dict(zip(('firma', 'n', 'tryb'), r)) for r in db.execute("SELECT firm, n, note FROM runs WHERE day=? AND source='employer'", (day,))]
print(json.dumps({'dzien': day, 'otwarte': otw, 'przebiegi': runs, 'zdarzenia': ev}, ensure_ascii=False, indent=1))
