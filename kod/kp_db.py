# Baza historii ofert: każda oferta = jeden wiersz w jobs, każda zmiana treści/zarobków = nowa wersja,
# każda obecność w danym dniu = obserwacja, każde zdarzenie (nowa, zmiana, zamknięta) = event.
import sqlite3, json, re, sys, os
from kp_parse import split_sections, h12
from kp_tags import extract

SCHEMA = '''
CREATE TABLE IF NOT EXISTS jobs(job_key TEXT PRIMARY KEY, firm TEXT, ext_id TEXT, url TEXT, title TEXT, city TEXT,
  first_seen TEXT, last_seen TEXT, status TEXT, closed_on TEXT, first_source TEXT, posted TEXT, func TEXT, level TEXT);
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY, job_key TEXT, seen TEXT, source TEXT, hash TEXT,
  title TEXT, city TEXT, locations TEXT, mode TEXT, sal_min INT, sal_max INT, sal_period TEXT, currency TEXT,
  sal_min_month INT, sal_max_month INT, posted TEXT, category TEXT, employer TEXT, text TEXT, sections TEXT, tags TEXT);
CREATE TABLE IF NOT EXISTS observations(job_key TEXT, seen TEXT, source TEXT, PRIMARY KEY(job_key, seen, source));
CREATE TABLE IF NOT EXISTS events(job_key TEXT, day TEXT, type TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS runs(day TEXT, firm TEXT, source TEXT, n INT, note TEXT);
'''

def lvl(t):
    tl = (t or '').lower()
    if re.search(r'intern|stażyst|praktyk', tl): return 'Praktyka lub staż'
    if re.search(r'director|manager|superintendent|team leader|supervisor|deputy|kierownik|dyrektor', tl): return 'Kierownik'
    if re.search(r'senior|lead\b|lead |principal|expert|ekspert|starsz|chartered|główn', tl): return 'Senior lub ekspert'
    if re.search(r'junior|młodszy|assistant|technician|coordinator|representative|admin\b|ślusarz|spawacz|pomocnik|malarz', tl): return 'Junior / wykonawczy'
    return 'Specjalista'

BMAP = {'Project Controls': 'Zarządzanie projektem i planowanie', 'Supply Chain': 'Zakupy i kontrakty', 'Human Resources': 'Administracja, HR i finanse',
        'Legal': 'Administracja, HR i finanse', 'Environmental, Safety & Health': 'BHP i ochrona środowiska (EHS)', 'Construction': 'Budowa i montaż',
        'Engineering': 'Inżynieria i projektowanie', 'Quality': 'Jakość i kontrola (QA/QC)', 'Project Management': 'Zarządzanie projektem i planowanie',
        'Information Technology': 'IT i systemy', 'Finance': 'Administracja, HR i finanse', 'Contracts': 'Zakupy i kontrakty'}
RULES = [('licens', 'Dozór i licencjonowanie'), ('radiation', 'Bezpieczeństwo jądrowe i ochrona radiologiczna'), ('radiochem', 'Bezpieczeństwo jądrowe i ochrona radiologiczna'),
         ('instructor', 'Szkolenie personelu eksploatacji'), ('quality', 'Jakość i kontrola (QA/QC)'), ('jakości', 'Jakość i kontrola (QA/QC)'),
         ('supplier performance', 'Jakość i kontrola (QA/QC)'), ('product compliance', 'Jakość i kontrola (QA/QC)'), ('supplier manufacturing', 'Jakość i kontrola (QA/QC)'),
         ('fabrication follow', 'Jakość i kontrola (QA/QC)'), ('inspektor', 'Budowa i montaż'), ('procurement', 'Zakupy i kontrakty'), ('buyer', 'Zakupy i kontrakty'),
         ('contract', 'Zakupy i kontrakty'), ('subcontract', 'Zakupy i kontrakty'), ('sap', 'IT i systemy'), ('software', 'IT i systemy'), ('devops', 'IT i systemy'),
         ('platform', 'IT i systemy'), ('application support', 'IT i systemy'), ('records and information', 'IT i systemy'), ('cyber', 'IT i systemy'), ('infrastruktury cyber', 'IT i systemy'),
         ('project controls', 'Zarządzanie projektem i planowanie'), ('project manager', 'Zarządzanie projektem i planowanie'), ('pmo', 'Zarządzanie projektem i planowanie'),
         ('delivery stream', 'Zarządzanie projektem i planowanie'), ('project engineer', 'Zarządzanie projektem i planowanie'), ('planu generalnego', 'Zarządzanie projektem i planowanie'),
         ('pozwoleni', 'Dozór i licencjonowanie'), ('payroll', 'Administracja, HR i finanse'), ('tax', 'Administracja, HR i finanse'), ('vat', 'Administracja, HR i finanse'),
         ('accountant', 'Administracja, HR i finanse'), ('hr ', 'Administracja, HR i finanse'), ('total rewards', 'Administracja, HR i finanse'), ('exec admin', 'Administracja, HR i finanse'),
         ('market strategy', 'Administracja, HR i finanse'), ('product manager', 'Administracja, HR i finanse'), ('sustainability', 'Administracja, HR i finanse'),
         ('spaw', 'Produkcja i spawalnictwo'), ('ślusar', 'Produkcja i spawalnictwo'), ('weld', 'Produkcja i spawalnictwo')]

def func(firm, title, category, tekst=''):
    """Obszar oferty - 16 obszarów (12.11.2026, kod/kp_obszar.py). Stara wersja: kod/Archiwum/kp_db_12-11-2026.py."""
    from kp_obszar import obszar
    return obszar(title, category or '', tekst or '')

def monthly(v, per):
    if v is None: return None
    return round(v / 12) if per == 'rok' else v

def connect(path):
    db = sqlite3.connect(path); db.executescript(SCHEMA); return db

def ingest(db, day, source, firm, recs, full_list=True):
    """full_list=True: recs to pełna lista aktualnych ofert firmy w danym dniu (oferty spoza listy -> zamknięte).
       full_list=False: częściowe dane (np. archiwum) - nie zamykamy niczego."""
    cur = db.cursor(); seen = set()
    for r in recs:
        key = f"{r['firm']}:{r['ext_id']}"; seen.add(key)
        sec = split_sections(r['text']); tags = extract(sec, r['text'])
        payload = json.dumps([r['title'], r['city'], r['mode'], r['sal_min'], r['sal_max'], r['sal_period'], r['text']], ensure_ascii=False)
        hh = h12(payload)
        row = cur.execute('SELECT status, first_seen, last_seen FROM jobs WHERE job_key=?', (key,)).fetchone()
        if not row:
            cur.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (key, r['firm'], r['ext_id'], r['url'], r['title'], r['city'], day, day, 'open', None, source,
                        r.get('posted'), func(r['firm'], r['title'], r.get('category')), lvl(r['title'])))
            cur.execute('INSERT INTO events VALUES(?,?,?,?)', (key, day, 'nowa', source))
        else:
            fs, ls = row[1], row[2]
            cur.execute('UPDATE jobs SET first_seen=?, last_seen=?, title=?, city=?, url=? WHERE job_key=?', (min(fs, day), max(ls, day), r['title'], r['city'], r['url'], key))
            if row[0] == 'closed' and day > (ls or ''):
                cur.execute("UPDATE jobs SET status='open', closed_on=NULL WHERE job_key=?", (key,))
                cur.execute('INSERT INTO events VALUES(?,?,?,?)', (key, day, 'wznowiona', source))
        last = cur.execute('SELECT hash, sal_min, sal_max, title, mode, tags FROM versions WHERE job_key=? AND seen<=? ORDER BY seen DESC, id DESC LIMIT 1', (key, day)).fetchone()
        if not last or last[0] != hh:
            if last:
                ch = []
                if (last[1], last[2]) != (r['sal_min'], r['sal_max']): ch.append(f"wynagrodzenie {last[1]}-{last[2]} -> {r['sal_min']}-{r['sal_max']}")
                if last[3] != r['title']: ch.append(f"tytuł '{last[3]}' -> '{r['title']}'")
                if last[4] != r['mode']: ch.append(f"tryb {last[4]} -> {r['mode']}")
                try:
                    oe = (json.loads(last[5] or '{}').get('kontrola_eksportu') or ['?'])[0]
                    if oe != tags['kontrola_eksportu'][0]: ch.append(f"kontrola eksportu {oe} -> {tags['kontrola_eksportu'][0]}")
                except Exception:
                    pass
                if not ch: ch.append('zmiana treści')
                cur.execute('INSERT INTO events VALUES(?,?,?,?)', (key, day, 'zmiana', '; '.join(ch)))
            cur.execute('INSERT INTO versions(job_key,seen,source,hash,title,city,locations,mode,sal_min,sal_max,sal_period,currency,sal_min_month,sal_max_month,posted,category,employer,text,sections,tags) '
                        'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (key, day, source, hh, r['title'], r['city'], json.dumps(r['locations'], ensure_ascii=False), r['mode'], r['sal_min'], r['sal_max'], r['sal_period'], r['currency'],
                         monthly(r['sal_min'], r['sal_period']), monthly(r['sal_max'], r['sal_period']), r.get('posted'), r.get('category'),
                         json.dumps(r.get('employer') or {}, ensure_ascii=False), r['text'], json.dumps(sec, ensure_ascii=False), json.dumps(tags, ensure_ascii=False)))
        cur.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?)', (key, day, source))
    if full_list:
        for (key,) in cur.execute("SELECT job_key FROM jobs WHERE firm=? AND status='open'", (firm,)).fetchall():
            if key not in seen:
                cur.execute("UPDATE jobs SET status='closed', closed_on=? WHERE job_key=?", (day, key))
                cur.execute('INSERT INTO events VALUES(?,?,?,?)', (key, day, 'zamknięta', 'brak na stronie pracodawcy'))
    cur.execute('INSERT INTO runs VALUES(?,?,?,?,?)', (day, firm, source, len(recs), 'full' if full_list else 'partial'))
    db.commit()

def reconcile(db):
    """Oferty niewidziane w ostatnim pełnym przebiegu firmy -> zamknięte (data zamknięcia nieznana, gdy ostatnio widziane tylko w archiwum)."""
    for firm, last in db.execute("SELECT firm, max(day) FROM runs WHERE note='full' GROUP BY firm").fetchall():
        for (key, ls) in db.execute("SELECT job_key, last_seen FROM jobs WHERE firm=? AND status='open' AND last_seen<?", (firm, last)).fetchall():
            db.execute("UPDATE jobs SET status='closed', closed_on=? WHERE job_key=?", (None, key))
            db.execute('INSERT INTO events VALUES(?,?,?,?)', (key, ls, 'zamknięta', 'po tej dacie brak w archiwum i na stronie (dokładna data nieznana)'))
    db.commit()

def presence_only(db, day, source, r):
    """Archiwum bez treści ogłoszenia: tylko dowód, że oferta istniała danego dnia (bez nowej wersji)."""
    key = f"{r['firm']}:{r['ext_id']}"
    row = db.execute('SELECT first_seen, last_seen FROM jobs WHERE job_key=?', (key,)).fetchone()
    if not row:
        db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (key, r['firm'], r['ext_id'], r['url'], r['title'], r['city'], day, day, 'open', None, source,
                   r.get('posted'), func(r['firm'], r['title'], r.get('category')), lvl(r['title'])))
        db.execute('INSERT INTO events VALUES(?,?,?,?)', (key, day, 'nowa', source + ' (bez treści)'))
    else:
        db.execute('UPDATE jobs SET first_seen=min(first_seen,?), last_seen=max(last_seen,?) WHERE job_key=?', (day, day, key))
    db.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?)', (key, day, source))
