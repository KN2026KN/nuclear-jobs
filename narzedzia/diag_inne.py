# 14.11.2026: tytuły ofert bez obszaru („Inne”) i bez zawodu - do uzupełniania słowników. Uruchamiać tylko w prywatnym repo (log niepubliczny).
import sqlite3, sys, json
sys.path.insert(0, 'kod')
from kp_obszar import obszar
from kp_zawody import zawod
db = sqlite3.connect(sys.argv[1])
q = '''SELECT j.title, v.category, v.employer FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) WHERE j.status='open' '''
ob, za = [], []
for t, cat, emp in db.execute(q):
    e = json.loads(emp or '{}')
    if obszar(t or '', cat or '') == 'Inne': ob.append(f"{e.get('kraj','?')} | {(t or '')[:90]} | kat: {(cat or '')[:40]}")
    if zawod(t or '') == 'inne': za.append(f"{e.get('kraj','?')} | {(t or '')[:90]}")
print('OBSZAR_INNE', len(ob)); [print('OB |', x) for x in sorted(ob)]
print('ZAWOD_INNE', len(za)); [print('ZA |', x) for x in sorted(za)]
from collections import Counter
c = Counter(json.loads(e or '{}').get('name') or f for f, e in db.execute("SELECT j.firm, v.employer FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) WHERE j.status='open'"))
print('OTWARTE', sum(c.values()), dict(c.most_common(12)))
from kp_jadro import jadrowa
import collections
_rows = list(db.execute("SELECT j.title, v.city, v.locations, v.text FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) WHERE j.status='open' AND j.firm='vattenfall'"))
print('VF otwarte po filtrze:', len(_rows))
for t, city, locs, tx in db.execute("SELECT j.title, v.city, v.locations, v.text FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) WHERE j.status='open' AND j.firm='vattenfall'"):
    ok, hit = jadrowa('Vattenfall', t or '', [('lok', f'{city or ""} {locs or ""}'), ('opis', tx or '')])
    print('VF |', 'TAK' if ok else 'NIE', '|', (hit or '')[:25], '|', (t or '')[:60], '|', (city or '')[:30])
