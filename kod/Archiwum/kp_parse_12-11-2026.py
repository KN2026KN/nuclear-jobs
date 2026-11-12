# Parsery ofert: Bechtel (Phenom JSON), Westinghouse (SuccessFactors HTML), PEJ (tekst ze strony pej.pl)
import json, re, html, hashlib, os, urllib.parse, gzip

def _open(path):
    return gzip.open(path, 'rt', encoding='utf-8') if path.endswith('.gz') else open(path, encoding='utf-8')

def clean_html(h):
    h = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</div>|</h\d>|</tr>', '\n', h or '')
    h = re.sub(r'(?i)<li[^>]*>', '\n• ', h)
    t = html.unescape(re.sub(r'<[^>]+>', '', h)).replace('\xa0', ' ').replace('​', '')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*•\s*\n', '\n', t)
    return re.sub(r'\n\s*\n+', '\n', t).strip()

def num(s):
    return int(re.sub(r'[^\d]', '', s)) if s and re.search(r'\d', s) else None

def h12(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:12]

# --- sekcje ---------------------------------------------------------------
SEC = [
    ('summary', r'job summary|opis stanowiska|about the role|role overview|position summary'),
    ('duties', r'responsibilit|zakres (zadań|obowiązków)|twój zakres|główne obowiązki|duties|what you will do|supplier assessment|supplier oversight|supplier development'),
    ('nice', r'preferred|preffered|mile widziane|nice to have|desired|dodatkowym atutem|preferred certifications'),
    ('must', r'qualifications|requirements|required knowledge|education and experience|oczekiwania|wymagania|wykształcenie i doświadczenie|wymagana wiedza|minimum qualifications|skills and competencies|^skills$|certificates'),
    ('offer', r'oferujemy|to oferujemy|benefits|total rewards|nagrody|why westinghouse|^offer|what we offer|employee referral|diverse teams build|różnorodne zespoły'),
    ('company', r'extraordinary teams|dowiedz się więcej|project overview|why westinghouse'),
    ('other', r'additional information|model of work'),
]

def split_sections(text):
    out = {k: [] for k, _ in SEC}; out['intro'] = []
    cur = 'intro'
    for line in text.split('\n'):
        l = line.strip(' •')
        if not l:
            continue
        low = l.lower().rstrip(':').strip()
        if len(l) < 80 and (l.endswith(':') or len(l.split()) <= 6):
            for k, rx in SEC:
                if re.search(rx, low):
                    cur = k; break
            else:
                out[cur].append(l); continue
            continue
        out[cur].append(l)
    return {k: v for k, v in out.items() if v}

def mode_of(t):
    tl = t.lower()
    if re.search(r'#li-remote|fully remote|praca zdalna|100% zdaln|remote work', tl): return 'zdalnie'
    if re.search(r'#li-hybrid|hybrid|hybryd|telework type: (part|partial)', tl): return 'hybrydowo'
    if re.search(r'#li-onsite|full-time office|on-site|onsite|stacjonar|na terenie budowy|codziennej pracy na terenie', tl): return 'stacjonarnie'
    return None

# --- Bechtel --------------------------------------------------------------
BKEEP = ['texpGrade', 'texpPostingGrade', 'texpGradeTrack', 'texpJobClassification', 'texpJobRole', 'texpDisciplineSpecialty',
         'texpExperienceLevel', 'jobBoardPostingType', 'texpEmploymentType', 'texpRelocationAuthorized', 'texpTeleworkType',
         'texpRequiredStartDate', 'texpPlannedEndDate', 'texpNoOfOpenings', 'noOfAvailableOpenings', 'texpProjectNo',
         'texpAssignedOrgUnit', 'texpBaseDepartment', 'texpBusinessUnit', 'texpOrganization', 'texpCompany', 'texpOfficeType',
         'texpRequisitionType', 'texpRoleHasDirectReports', 'texpSecurityClearance', 'texpNationalization', 'texpStatus',
         'texpEmployeeReferralAmount', 'department', 'category', 'jobCode', 'dateCreated', 'postedDate', 'jobUpdatedDate',
         'externalPostingStartDate', 'internalPostingStartDate', 'ml_skills', 'ai_summary', 'multi_location']
# celowo pomijamy pola z nazwiskami (rekruterzy, przełożeni)

def parse_bechtel(path, pam=None):
    # format 2 (11.2026): cała lista świata + treść tylko nowych; treść starszych z pamięci (pam) z wcześniejszych dni
    from kp_jadro import jadrowa
    d = json.load(_open(path)); pam = {} if pam is None else pam
    pam.update(d.get('jobs') or {})
    ids = d.get('ids') or list(d['jobs'])
    out = []
    for jid in ids:
        j = pam.get(str(jid))
        if not j: continue
        pl = j.get('country') == 'Poland' or 'Poland' in json.dumps(j.get('multi_location') or '')
        if not pl and not jadrowa('', j.get('title'), [('opis', clean_html(j.get('description', ''))), ('dzial', str(j.get('texpBusinessUnit') or '') + ' ' + str(j.get('texpProjectNo') or ''))])[0]:
            continue
        text = clean_html(j.get('description', ''))
        m = re.search(r'Salary Range:\s*([\d,\. ]+)\s*-\s*([\d,\. ]+)\s*PLN\s*(annually|monthly|per month|per year)?', text, re.I)
        smin = num(m.group(1)) if m else None; smax = num(m.group(2)) if m else None
        per = 'rok' if (m and (m.group(3) or 'annually').lower() in ('annually', 'per year')) else ('mies' if m else None)
        cur = 'PLN' if m else None
        if not m:
            smin, smax, per, cur = placa(text)
        locs = [l.get('cityStateCountry') or l.get('city') for l in (j.get('multi_location') or []) if isinstance(l, dict)]
        tele = j.get('texpTeleworkType') or ''
        mode = 'stacjonarnie' if 'Full-Time Office' in tele else ('hybrydowo' if tele else mode_of(text))
        emp = {k: j.get(k) for k in BKEEP if j.get(k) not in (None, '', '""', [])}
        out.append(dict(firm='bechtel', ext_id=str(jid), url='https://jobs.bechtel.com/us/en/job/' + str(jid),
                        title=j.get('title'), city=j.get('city'), locations=locs or [j.get('cityStateCountry')],
                        mode=mode, sal_min=smin, sal_max=smax, sal_period=per, currency=cur,
                        posted=(j.get('postedDate') or '')[:10], category=j.get('category'), employer=emp, text=text))
    return d.get('fetched', ''), out

# --- Westinghouse ---------------------------------------------------------
def parse_wec(path, pam=None):
    d = json.load(_open(path)); pam = {} if pam is None else pam
    pam.update(d.get('jobs') or {})
    out = []
    for p in ([x['path'] for x in d['list']] if d.get('format') == 2 else list(d['jobs'])):
        j = dict(pam.get(p) or {})
        if not j: continue
        it = next((x for x in d['list'] if x['path'] == p), None) if d.get('format') == 2 else None
        if it: j.update({k: it[k] for k in ('title', 'loc', 'date') if it.get(k)})
        text = clean_html(j.get('descHtml', ''))
        m = re.search(r'([\d][\d,\. ]*)\s*(?:PLN\s*)?(?:gross\s*)?(?:to|-|–)\s*([\d][\d,\. ]*)\s*PLN\s*(gross)?\s*(per month|monthly|per year|annually|a year|yearly)?', text, re.I)
        smin = num(m.group(1)) if m else None; smax = num(m.group(2)) if m else None
        per = None; cur = 'PLN' if m else None
        if m: per = 'rok' if m.group(4) and re.search(r'year|annual', m.group(4), re.I) else 'mies'
        else: smin, smax, per, cur = placa(text)
        loc = re.sub(r'\s+', ' ', j.get('loc') or '')
        more = re.search(r'\+(\d+) more', loc)
        city = loc.split(',')[0].strip()
        meta = j.get('meta', {})
        pid = re.search(r'/(\d+)/?$', p).group(1)
        out.append(dict(firm='westinghouse', ext_id=pid, url='https://careers.westinghousenuclear.com' + p,
                        title=j.get('title'), city=city, locations=[loc.split('+')[0].strip()] + ([f'+{more.group(1)} lokalizacji'] if more else []),
                        mode=mode_of(text), sal_min=smin, sal_max=smax, sal_period=per, currency=cur,
                        posted=j.get('date'), category=meta.get('industry'),
                        employer={'pl_primary': ', PL' in loc.split('+')[0], 'industry': meta.get('industry')}, text=text))
    return d.get('fetched', ''), out

# --- PEJ ------------------------------------------------------------------
def parse_pej(path, pam=None, fetched='2026-10-31'):
    raw = _open(path).read()
    out = []
    valid = {}
    lst = raw.split('=====LIST')[1].split('=====JOB ')[0] if '=====LIST' in raw else ''
    lf = os.path.join(os.path.dirname(path), 'kp_pej_lista_' + os.path.basename(path)[7:].replace('.gz', ''))
    if not lst and os.path.exists(lf): lst = open(lf, encoding='utf-8').read()
    for row in lst.strip().split('\n'):
        c = row.split('|')
        if len(c) >= 4: valid[c[-1].strip('/')] = c[2]
    for block in raw.split('=====JOB ')[1:]:
        lines = block.split('\n')
        slug = lines[0].strip()
        pid = re.search(r'@pid (\d*)', block).group(1)
        body = [l for l in lines[1:] if not l.startswith('@')]
        body = [l for l in body if l.strip() and l.strip() not in ('Aplikuj na to stanowisko', 'Pozostałe oferty')]
        title = body[0].strip()
        city = ref = None
        for i, l in enumerate(body):
            if l.strip() == 'Miejsce pracy': city = body[i + 1].strip()
            if l.strip() == 'Numer referencyjny': ref = body[i + 1].strip()
        text = '\n'.join(body)
        m = re.search(r'(\d{1,3}[ .]?\d{3})\s*[–-]\s*(\d{1,3}[ .]?\d{3})\s*(?:zł)?\s*brutto', text)
        city_n = re.sub(r'\s*\(.*\)', '', city or '')
        out.append(dict(firm='pej', ext_id=slug, url='https://pej.pl/o-nas/kariera/oferty-pracy/' + slug + '/',
                        title=title, city=city_n, locations=[city] if city else [], mode=mode_of(text),
                        sal_min=num(m.group(1)) if m else None, sal_max=num(m.group(2)) if m else None,
                        sal_period='mies' if m else None, currency='PLN' if m else None,
                        posted=None, category=None, employer={'ref': ref, 'wp_post_id': pid, 'valid_until': valid.get(slug)}, text=text))
    return fetched, out

# --- Archiwum Wayback: PEJ ------------------------------------------------
def parse_pej_archive(path):
    """Zwraca (oferty, listy): oferty = lista (dzień, rekord); listy = migawki listy ofert z kolumną 'Ważne do'."""
    d = json.load(_open(path))
    jobs, lists = [], []
    for k, s in sorted(d.items(), key=lambda kv: kv[1]['ts']):
        day = f"{s['ts'][:4]}-{s['ts'][4:6]}-{s['ts'][6:8]}"
        slug = re.sub(r'^https?://(www\.)?pej\.pl(:80)?/o-nas/kariera/oferty-pracy/', '', s['url']).split('?')[0].strip('/')
        body = [l.strip() for l in s['text'].split('\n') if l.strip()]
        if not slug:
            lists.append((day, body)); continue
        body = [l for l in body if l not in ('Aplikuj na to stanowisko', 'Pozostałe oferty')]
        if 'Miejsce pracy' not in body: continue
        title = body[0]; city = ref = None
        for i, l in enumerate(body[:-1]):
            if l == 'Miejsce pracy': city = body[i + 1]
            if l == 'Numer referencyjny': ref = body[i + 1]
        stop = next((i for i, l in enumerate(body) if l.startswith('Pozostałe oferty') or l.startswith('Przejdź do')), len(body))
        text = '\n'.join(body[:stop])
        m = re.search(r'(\d{1,3}[ .]?\d{3})\s*[–-]\s*(\d{1,3}[ .]?\d{3})\s*(?:zł)?\s*brutto', text)
        jobs.append((day, dict(firm='pej', ext_id=slug, url='https://pej.pl/o-nas/kariera/oferty-pracy/' + slug + '/', title=title,
                               city=re.sub(r'\s*\(.*\)', '', city or ''), locations=[city] if city else [], mode=mode_of(text),
                               sal_min=num(m.group(1)) if m else None, sal_max=num(m.group(2)) if m else None, sal_period='mies' if m else None,
                               currency='PLN' if m else None, posted=None, category=None, employer={'ref': ref, 'wp_post_id': s.get('pid'), 'wayback_ts': s['ts']}, text=text)))
    return jobs, lists

# --- Archiwum Wayback: Westinghouse ---------------------------------------
def _wec_slug_title(path):
    m = re.search(r'/job/([^/]+)/(\d+)/?', path)
    slug = urllib.parse.unquote(m.group(1)) if m else ''
    slug = re.sub(r'^(Krak[oó]w|Krakau|Cracow|Warszawa|Warsaw|Gda[nń]sk|Cranberry-Township)-', '', slug)
    slug = re.sub(r'-(MA|PL|NA|PA)(-[\d-]+)?$', '', slug)
    return slug.replace('-', ' ').strip(), (m.group(2) if m else None)

def parse_wec_archive(path):
    """Zwraca listę (dzień, rekord, ma_tekst)."""
    d = json.load(_open(path))
    out = []
    for k, s in sorted(d['wec'].items(), key=lambda kv: kv[1]['ts']):
        day = f"{s['ts'][:4]}-{s['ts'][4:6]}-{s['ts'][6:8]}"
        p = re.sub(r'^https?://[^/]+', '', s['url']).split('?')[0]
        st, pid = _wec_slug_title(p)
        if not pid: continue
        city = 'Krakow' if re.search(r'/job/(Krak|Cracow)', p, re.I) else ('Warszawa' if re.search(r'/job/Wars', p, re.I) else ('Cranberry Township' if 'Cranberry' in p else ''))
        text = clean_html(s.get('descHtml', ''))
        meta = s.get('meta') or {}
        title = (meta.get('title') or s.get('title') or st).strip() or st
        m = re.search(r'([\d][\d,\. ]*)\s*(?:PLN\s*)?(?:gross\s*)?(?:to|-|–)\s*([\d][\d,\. ]*)\s*PLN\s*(gross)?\s*(per month|monthly|per year|annually|a year|yearly)?', text, re.I)
        per = None
        if m: per = 'rok' if m.group(4) and re.search(r'year|annual', m.group(4), re.I) else 'mies'
        rec = dict(firm='westinghouse', ext_id=pid, url='https://careers.westinghousenuclear.com' + p, title=title, city=city, locations=[city],
                   mode=mode_of(text) if text else None, sal_min=num(m.group(1)) if m else None, sal_max=num(m.group(2)) if m else None,
                   sal_period=per, currency='PLN' if m else None, posted=meta.get('datePosted'), category=meta.get('industry'),
                   employer={'wayback_ts': s['ts'], 'industry': meta.get('industry')}, text=text)
        out.append((day, rec, bool(text)))
    return out


# --- pracuj.pl (10.11.2026) ------------------------------------------------
def parse_pracuj(path, pam=None):
    """Tylko oferty związane z energetyką jądrową (kp_jadro). Oferty PEJ / Bechtel / Westinghouse obecne na stronie pracodawcy
    są pomijane tutaj (bierzemy je ze strony pracodawcy) - dopasowanie w strona_praca.py; tu zostawiamy je z flagą."""
    from kp_jadro import jadrowa, sektor
    d = json.load(_open(path)); out = []; pam = {} if pam is None else pam
    for pid, o in d.get('oferty', {}).items():
        if o.get('oferta'): pam[pid] = o['oferta']
        of = o.get('oferta') or pam.get(pid) or {}; a = of.get('attributes') or {}; L = o.get('lista') or {}
        if not of: continue
        emp = a.get('displayEmployerName') or L.get('companyName') or ''
        title = a.get('jobTitle') or L.get('jobTitle') or ''
        sek = [(x.get('sectionType'), x.get('plainText') or '') for x in of.get('textSections') or []]
        ok, hit = jadrowa(emp, title, sek)
        if not ok: continue
        text = '\n'.join(f"{typ}: {t}" for typ, t in sek)
        sal = L.get('salaryDisplayText') or ''
        m = re.search(r'([\d ]+)[–-]([\d ]+)\s*zł\s*(brutto|netto)?\s*/\s*(mies|godz|rok)', sal.replace('\xa0', ' '))
        m1 = m or re.search(r'([\d ]+)\s*zł\s*(brutto|netto)?\s*/\s*(mies|godz|rok)', sal.replace('\xa0', ' '))
        smin = num(m.group(1)) if m else (num(m1.group(1)) if m1 else None)
        smax = num(m.group(2)) if m else smin
        per = (m.group(4) if m else (m1.group(3) if m1 else None))
        per = {'mies': 'mies', 'godz': 'godz', 'rok': 'rok'}.get(per)
        modes = ' '.join(L.get('workModes') or [])
        mode = 'zdalnie' if 'zdaln' in modes and 'hybryd' not in modes else ('hybrydowo' if 'hybryd' in modes else ('stacjonarnie' if modes else mode_of(text)))
        miejsce = (o.get('miejsce') or '').split(',')[0].strip()
        ref = ((a.get('applying') or {}).get('referenceNumber'))
        out.append(dict(firm='pracuj', ext_id=str(pid), url=o['url'], title=title, city=miejsce, locations=[o.get('miejsce')], mode=mode,
                        sal_min=smin, sal_max=smax, sal_period=per, currency='PLN' if smin else None, posted=(L.get('initialPublicated') or '')[:10],
                        category=None, employer={'name': emp, 'company_id': L.get('companyId'), 'sektor': sektor(emp), 'ref': ref, 'trafienie': hit,
                                                 'wazne_do': (L.get('expirationDate') or '')[:10], 'poziom': L.get('positionLevels'), 'umowa': L.get('typesOfContract'),
                                                 'brutto_netto': (m or m1).group(3 if m else 2) if (m or m1) else None, 'kw': o.get('kw')}, text=text))
    return d.get('fetched', ''), out


# --- NCBJ (10.11.2026) -------------------------------------------------------
def parse_ncbj(path, pam=None):
    # NCBJ: tytuł z linii "Stanowisko | nr ref.", termin z "Termin zbierania ofert"; opis instytutu (reaktor MARIA itd.) nie liczy się do filtra jądrowego
    from kp_jadro import jadrowa
    d = json.load(_open(path)); out = []
    MIES = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
    for slug, o in d.get('oferty', {}).items():
        lines = [x.strip() for x in (o.get('tekst') or '').split('\n') if x.strip()]
        title = o.get('tytul') or ''; posted = deadline = None
        if len(lines) > 3 and lines[0].isdigit() and lines[1][:3] in MIES and lines[2].isdigit():
            posted = '%s-%02d-%02d' % (lines[2], MIES[lines[1][:3]], int(lines[0]))
            title = title or re.sub(r'\s*\|.*$', '', lines[3]).strip()
        for i, x in enumerate(lines[:-1]):
            if x.startswith('Termin zbierania ofert'):
                m = re.match(r'(\d{2})-(\d{2})-(\d{4})', lines[i + 1])
                if m: deadline = f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
                break
        tresc = [x for x in lines[4:] if not re.search(r'jest jednym z największych instytutów|Computing Centre|only nuclear reactor in Poland|Termin zbierania ofert|^\d{2}-\d{2}-\d{4}$', x)]
        text = '\n'.join(tresc)
        # bez opisu instytutu, klauzul RODO i nazwy NCBJ (zawierają "jądrow"/"Nuclear", ale nie mówią nic o stanowisku)
        text = re.sub(r'Narodowe Centrum Badań Jądrowych \(NCBJ\) jest.*?instalacji jądrowych\.', ' ', text, flags=re.S)
        text = re.sub(r'Our infrastructure not only supports.*?\.', ' ', text, flags=re.S)
        cut = re.search(r'Personal Data Controller|Administrator\w* (Pani|danych)|Klauzul\w* informacyjn|HR Excellence|I hereby (agree|consent)|Wyrażam zgodę|Information clause|processed by National Centre', text)
        if cut: text = text[:cut.start()]
        text = re.sub(r'National Cent(re|er) for Nuclear Research|Narodow\w* Centrum Badań Jądrowych', 'NCBJ', text)
        if not title: continue
        ok, hit = jadrowa('Narodowe Centrum Badań Jądrowych', title, [('opis', text)])
        if not ok: continue
        city = 'Warszawa' if re.search(r'Lokalizacja[\s:]*Warszawa|Pasteura|Hoża', text) else 'Otwock-Świerk'
        m = re.search(r'(\d{1,2}[ .]?\d{3})\s*[–-]\s*(\d{1,2}[ .]?\d{3})\s*(?:zł|PLN)\s*(brutto)?', text)
        out.append(dict(firm='ncbj', ext_id=slug, url=o['url'], title=title, city=city, locations=[city], mode=mode_of(text),
                        sal_min=num(m.group(1)) if m else None, sal_max=num(m.group(2)) if m else None, sal_period='mies' if m else None, currency='PLN' if m else None,
                        posted=posted, category=None, employer={'name': 'Narodowe Centrum Badań Jądrowych', 'sektor': 'nau', 'trafienie': hit, 'wazne_do': deadline}, text=text))
    return d.get('fetched', ''), out


# --- wynagrodzenie w dowolnej walucie (11.2026) ---------------------------------
WAL = [('GBP', r'£|GBP'), ('EUR', r'€|EUR|euro'), ('USD', r'US\$|USD|\$'), ('CZK', r'Kč|CZK'), ('BGN', r'лв\.?|BGN'), ('RON', r'\bRON\b|\blei\b'),
       ('SEK', r'\bSEK\b|\bkr\b'), ('AED', r'AED'), ('CAD', r'CAD'), ('CHF', r'CHF'), ('PLN', r'PLN|zł')]
def placa(text):
    """(min, max, okres, waluta); 11.11.2026: kwota „miesięczna” powyżej 25 000 EUR/GBP/USD/CHF/CAD to w praktyce roczna (np. Westinghouse Włochy: „€29.100 to €37.000 per month”)."""
    lo, hi, per, kod = _placa(text)
    if per == 'mies' and kod in ('EUR', 'GBP', 'USD', 'CHF', 'CAD') and lo and lo > 25000: per = 'rok'
    return lo, hi, per, kod

def _placa(text):
    """(min, max, okres, waluta) z treści; None gdy brak. Szuka zakresu z walutą i okresem."""
    t = (text or '').replace('\xa0', ' ')
    for kod, w in WAL:
        n = r'(\d{1,3}(?:[ ,.]\d{3})+|\d{2,7})(?:[.,]\d{1,2})?\s*(k\b)?'
        rx = re.compile(rf'(?:(?:{w})\s*{n}\s*(?:-|–|to|do|až)\s*(?:{w})?\s*{n}|{n}\s*(?:-|–|to|do|až)\s*{n}\s*(?:{w}))'
                        r'[^\n]{0,40}?(per annum|p\.?a\.?|annual|year|an\b|par an|/an|brut annuel|per month|monthly|mois|month|/m|měsíčně|месечно|lunar|per hour|hour|/h)?', re.I)
        m = rx.search(t)
        if not m: continue
        g = [x for x in m.groups()]
        a, ak, b, bk = (g[0], g[1], g[2], g[3]) if g[0] else (g[4], g[5], g[6], g[7])
        lo, hi = num(a), num(b)
        if ak: lo *= 1000
        if bk or ak: hi = hi * 1000 if hi < 1000 else hi
        okr = (m.group(9) or '').lower()
        if not lo or not hi or hi < lo or lo < (5 if re.search(r'hour|/h', okr) else 100): continue
        if 1990 <= lo <= 2100 and 1990 <= hi <= 2100: continue          # lata, nie kwoty
        per = 'godz' if re.search(r'hour|/h', okr) else ('mies' if re.search(r'month|mois|/m|měsíč|месеч|lunar', okr) else ('rok' if okr or lo > 15000 else 'mies'))
        if kod in ('PLN', 'CZK', 'BGN', 'RON', 'SEK') and not okr: per = 'mies' if lo < 200000 else 'rok'
        return lo, hi, per, kod
    return placa_jedna(t)

# 11.11.2026: pojedyncza kwota z okresem albo z etykietą (np. HPC: „Basic PAYE: £29.34/hr”, „Projected annual earnings: £91,854”)
OKRES_RX = (r'(?P<o>/\s?(?:hr|hour|h)\b|per hour|an hour|hourly|p/?h\b|/\s?godz|za godzin\w*|/\s?(?:year|yr|annum|rok)\b|per (?:annum|year)|p\.\s?a\.?|\bpa\b|annual(?:ly)?|a year|'
            r'/\s?(?:month|mo|m-c|mies)\.?|per month|monthly|miesięcznie|mies\.|par an|par mois|/mois|pro (?:Jahr|Monat|Stunde)|jährlich|monatlich|в месяц|/мес|měsíčně)')
ETYKIETA_RX = re.compile(r'salary|\bpay\b|rate|earnings|wynagrodzeni|stawk|zarob|pensj|salaire|rémunération|gehalt|vergütung|lohn|mzda|plat\b|зарплат|оклад|доход|compensation|remuneration|basic', re.I)
def _kwota(a, d):
    a = re.sub(r'[ ,.](?=\d{3}(\D|$))', '', a)
    try: return float(a + ('.' + d[1:] if d else ''))
    except ValueError: return None
def placa_jedna(t):
    for kod, w in WAL:
        kw = r'(?P<a>\d{1,3}(?:[ ,.]\d{3})+|\d{1,7})(?P<d>[.,]\d{1,2})?(?P<k>\s?k\b)?'
        for rx in (rf'(?:{w})\s?{kw}\s*{OKRES_RX}?', rf'{kw}\s?(?:{w})\s*{OKRES_RX}?'):
            for m in re.finditer(rx, t, re.I):
                v = _kwota(m.group('a'), m.group('d'))
                if not v: continue
                if m.group('k'): v *= 1000
                okr = (m.group('o') or '').lower()
                przed = t[max(0, m.start() - 70):m.start()]
                if not okr and not ETYKIETA_RX.search(przed): continue
                if not okr and re.search(r'annual|year|annum|rok|jahr|an\b', przed, re.I): okr = 'year'
                if not okr and re.search(r'hour|godzin|stund', przed, re.I): okr = 'hour'
                if re.search(r'hr|hour|/h|godz|stunde|p/?h', okr): per, ok = 'godz', 5 <= v <= 600
                elif re.search(r'month|mo\b|mies|m-c|mois|monat|мес|měsíč', okr): per, ok = 'mies', 300 <= v <= 150000
                elif okr: per, ok = 'rok', 5000 <= v <= 3000000
                else: per = 'rok' if v > 15000 else ('mies' if v >= 300 else 'godz'); ok = 5 <= v <= 3000000
                if 1990 <= v <= 2100 and not okr: continue
                if 'allowance' in przed.lower() or 'bonus' in przed[-25:].lower() or 'accommodation' in przed.lower(): continue
                if ok: return v, v, per, kod
    return None, None, None, None


# --- nowe źródła świata: raw/RRRR-MM-DD/kp_sw_<źródło>_<dzień>.json (11.2026) ----------
def _bez_osob(t):
    """Usuwa linie z danymi kontaktowymi rekruterów (e-mail, telefon, „Contact: Imię Nazwisko”)."""
    return '\n'.join(l for l in (t or '').split('\n') if not re.search(r'\S+@\S+\.\w+|\+?\d[\d \-]{8,}\d|^(contact|kontakt|recruiter|rekruter|kontaktní osoba|контакт)\b.{0,60}$', l.strip(), re.I))

def parse_swiat(path, pam=None):
    from kp_jadro import jadrowa
    d = json.load(_open(path)); pam = {} if pam is None else pam
    pam.update(d.get('tresci') or {})
    zr = d['zrodlo']; out = []
    for it in d.get('lista') or []:
        tr = pam.get(it['id']) or {}
        if not tr and not it.get('bez_tresci'): continue          # treść pobierze następna noc
        text = clean_html(tr['html']) if tr.get('html') else (tr.get('tekst') or '')
        text = _bez_osob(text)
        tytul = it.get('tytul') or tr.get('h1') or ''
        if tr.get('h1') and len(tr['h1']) > 5 and len(tr['h1']) < 160 and zr not in ('kprm',): tytul = tr['h1']
        tytul = re.sub(r'\s+', ' ', tytul).strip()[:200]
        prac = it.get('pracodawca') or d.get('pracodawca') or ''
        if d.get('filtr') == 'jadrowy' or (d.get('filtr') == 'kprm' and 'Atomistyki' not in prac):
            ok, hit = jadrowa('', tytul, [('opis', text)])
            if not ok: continue
        meta = tr.get('meta') or {}
        lok = it.get('miasto') or it.get('lokalizacja') or meta.get('jobLocation') or meta.get('addressLocality') or ''
        smin, smax, per, cur = placa(text)
        if zr == 'kprm':
            m = re.search(r'(\d[\d ]{3,})[,.]\d{2}\s*zł[^\n]{0,30}brutto', text)
            if m and not smin: smin, smax, per, cur = num(m.group(1)), num(m.group(1)), 'mies', 'PLN'
        wd = it.get('wazne_do')
        if wd and re.match(r'\d{2}\.\d{2}\.\d{4}', wd): wd = f'{wd[6:10]}-{wd[3:5]}-{wd[0:2]}'
        out.append(dict(firm=zr, ext_id=str(it['id']), url=it['url'], title=tytul, city=(lok or '').split(',')[0].strip()[:80], locations=[lok] if lok else [],
                        mode=mode_of(text), sal_min=smin, sal_max=smax, sal_period=per, currency=cur, posted=(it.get('data') or meta.get('datePosted') or None),
                        category=it.get('dzial'), employer={'name': prac, 'kraj_zrodla': d.get('kraj'), 'wazne_do': wd, 'sektor_zr': d.get('sektor')}, text=text or tytul))
    return d.get('fetched', ''), out, d.get('lista_pelna', True)


# --- wzbogacenie każdej oferty: kraj, projekt, typ obiektu, język, tylko_analiza (11.2026) ---
def wzbogac(r):
    from kp_projekty import kraj, projekt, tylko_analiza, jezyk
    e = r.setdefault('employer', {}) or {}
    lok = ' | '.join(str(x) for x in (r.get('locations') or []) if x)
    domysl = e.get('kraj_zrodla') or ({'pej': 'PL', 'ncbj': 'PL', 'pracuj': 'PL'}.get(r['firm']))
    k = kraj(r.get('city'), lok, domyslny=None) or domysl or kraj(r.get('text', '')[:1500])
    if r['firm'] == 'bechtel':
        k = kraj(lok, r.get('city')) or k
    nazwa = e.get('name') or {'bechtel': 'Bechtel', 'westinghouse': 'Westinghouse', 'pej': 'Polskie Elektrownie Jądrowe', 'ncbj': 'Narodowe Centrum Badań Jądrowych'}.get(r['firm'], '')
    pr, typ = projekt(r.get('title'), f"{r.get('city') or ''} {lok}", r.get('text'), nazwa)
    if r['firm'] == 'pej' and not pr: pr, typ = 'AP1000 Lubiatowo-Kopalino', 'bud'
    from kp_projekty import PROJEKT_KRAJ
    if pr and k and PROJEKT_KRAJ.get(pr) not in (k, None) and pr not in ('IAEA', 'Fusion for Energy (F4E)'):
        # projekt z treści z innego kraju niż lokalizacja (np. wzmianka o Hinkley w ofercie z Polski) - nie przypisujemy
        pr2, t2 = projekt(r.get('title'), f"{r.get('city') or ''} {lok}", '', '')
        pr, typ = (pr2, t2) if pr2 and PROJEKT_KRAJ.get(pr2) == k else (None, None)
    e.update({'kraj': k, 'projekt': pr, 'typ_obiektu': typ, 'jezyk': jezyk(f"{r.get('title') or ''}\n{r.get('text') or ''}"),
              'tylko_analiza': tylko_analiza(nazwa, k, pr, r.get('text'))})
    if r['firm'] == 'westinghouse': e['pl_primary'] = (k == 'PL')
    r['employer'] = e
    return r
