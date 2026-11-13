# Robot zbierający oferty z oficjalnych stron: Bechtel, Westinghouse, PEJ.
# Zapisuje pliki w tym samym formacie co skrypty JS z przeglądarki, więc kod/kp_parse.py czyta je bez zmian.
# Użycie: python3 collect/collect.py raw/RRRR-MM-DD [bechtel wec pej]
import sys, os, json, re, time, datetime, urllib.parse
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siec import S, get, znane, zapisz_znane, czas_ok, poprzedni_dzien
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
# pola z nazwiskami osób - nie zapisujemy ich nigdzie
PERSONAL = {'dummy', 'dummy2', 'dummyRecruiter', 'texpTAManager', 'texpTACoordinater', 'texpTACoordinatorTeam', 'texpSupervisor',
            'texpFunctionalManager', 'texpBGMCUser', 'texpBGMCTeam', 'recruiterName', 'recruiterEmail', 'hiringManager'}

def ddo(html):
    i = html.index('phApp.ddo = ') + 12
    s = html[i:]
    return json.loads(s[:s.index('; phApp.experimentData')])

# Bechtel (11.2026): cała lista świata co noc; do bazy oferty w Polsce + oferty jądrowe na świecie (kandydaci z listy, filtr na treści w kp_parse).
# Pełna treść tylko dla nowych ofert (pamięć data/cache/znane_bechtel.json), z limitem czasu - reszta następnej nocy.
BECH_JADRO = re.compile(r'nuclear|reactor|radiolog|AP1000|\bSMR\b|NS&E|Nuclear, Security|uranium|fission|Hanford|Y-12|Oak Ridge|Sellafield|Richland|vitrif|tritium|naval reactor', re.I)
def bechtel(out, day):
    lista = []; total = 0
    for frm in range(0, 4000, 10):
        r = get(f'https://jobs.bechtel.com/us/en/search-results?from={frm}&s=1')
        e = ddo(r.text).get('eagerLoadRefineSearch') or {}
        js = (e.get('data') or {}).get('jobs') or []; total = e.get('totalHits') or 0
        lista += [{k: j.get(k) for k in ('jobId', 'title', 'country', 'city', 'cityStateCountry', 'multi_location', 'department', 'category', 'descriptionTeaser', 'ml_skills', 'postedDate', 'dateCreated')} for j in js]
        if not js or frm + 10 >= total: break
    if not lista: raise RuntimeError('Bechtel: pusta lista')
    def kand(j):
        return j.get('country') == 'Poland' or 'Poland' in json.dumps(j.get('multi_location') or '') or BECH_JADRO.search(' '.join(str(j.get(k) or '') for k in ('title', 'department', 'descriptionTeaser', 'ml_skills', 'city')))
    pl = lambda j: j.get('country') == 'Poland' or 'Poland' in json.dumps(j.get('multi_location') or '')
    ids = list(dict.fromkeys([str(j['jobId']) for j in lista if pl(j)] + [str(j['jobId']) for j in lista if kand(j)]))
    plik = os.path.join(out, f'kp_bechtel_{day}.json')
    zn = znane('bechtel'); J = dict(poprzedni_dzien(plik).get('jobs') or {}); t0 = time.time()
    for jid in ids:
        if jid in zn or jid in J: continue
        if not czas_ok(t0, 420): break
        try:
            job = ddo(get(f'https://jobs.bechtel.com/us/en/job/{jid}').text)['jobDetail']['data']['job']
            J[jid] = {k: v for k, v in job.items() if k not in PERSONAL and k != 'multiLocaleTranslationsData'}; zn[jid] = day
        except Exception as e:
            print('bechtel', jid, e)
    zapisz_znane('bechtel', zn, set(ids))
    json.dump({'fetched': NOW, 'format': 2, 'total': total, 'ids': ids, 'lista': lista, 'jobs': J}, open(plik, 'w', encoding='utf-8'), ensure_ascii=False)
    return len(lista), len(ids), len(J)

# Westinghouse (11.2026): wszystkie kraje (lista ok. 1100 ofert, 25 na stronę); pełna treść tylko nowych, z limitem czasu.
def sf_lista(base, zapytanie, maks=3000):
    """SuccessFactors RMK: układ tabeli (tr.data-row) albo kafelków (li.job-tile); stronicowanie startrow, koniec gdy brak nowych."""
    WL = []; seen = set()
    for s in range(0, maks, 25):
        soup = BeautifulSoup(get(f'{base}/search/?{zapytanie}&startrow={s}').text, 'html.parser')
        rows = soup.select('tr.data-row') or soup.select('li.job-tile')
        nowe = 0
        for r in rows:
            a = r.select_one('a.jobTitle-link')
            if not a or a['href'] in seen: continue
            seen.add(a['href']); nowe += 1
            loc = r.select_one('.jobLocation') or r.select_one('[id$="section-location-value"]')
            dt = r.select_one('.jobDate') or r.select_one('[id$="section-date-value"]')
            WL.append({'path': a['href'], 'title': a.get_text(strip=True), 'loc': loc.get_text(' ', strip=True) if loc else '', 'date': dt.get_text(strip=True) if dt else ''})
        if not nowe: break
    return WL

def sf_szczegoly(base, WL, zrodlo, day, limit_s, J=None):
    zn = znane(zrodlo); J = dict(J or {}); t0 = time.time()
    WL = sorted(WL, key=lambda x: 0 if re.search(r', PL\b|Poland|Krak|Warsz|Warsaw', x.get('loc') or '') else 1)   # Polska najpierw
    for it in WL:
        if it['path'] in zn or it['path'] in J: continue
        if not czas_ok(t0, limit_s): break
        try:
            soup = BeautifulSoup(get(base + it['path']).text, 'html.parser')
            desc = soup.select_one('span.jobdescription')
            meta = {}
            for m in soup.select('[itemprop]'):
                k = m.get('itemprop')
                if k and k != 'description' and k not in meta:
                    meta[k] = (m.get('content') or m.get_text(' ', strip=True) or '')[:300]
            J[it['path']] = {**it, 'descHtml': desc.decode_contents() if desc else '', 'meta': meta}; zn[it['path']] = day
        except Exception as e:
            print(zrodlo, it['path'], e)
    zapisz_znane(zrodlo, zn, {x['path'] for x in WL})
    return J

def wec(out, day):
    base = 'https://careers.westinghousenuclear.com'
    WL = sf_lista(base, 'q=&locationsearch=')
    if not WL: raise RuntimeError('Westinghouse: pusta lista')
    plik = os.path.join(out, f'kp_wec_{day}.json')
    J = sf_szczegoly(base, WL, 'wec', day, 420, poprzedni_dzien(plik).get('jobs'))
    json.dump({'fetched': NOW, 'format': 2, 'list': WL, 'jobs': J}, open(plik, 'w', encoding='utf-8'), ensure_ascii=False)
    return len(WL), len(J)

def pej(out, day):
    lst = 'https://pej.pl/o-nas/kariera/oferty-pracy/'
    soup = BeautifulSoup(get(lst).text, 'html.parser')
    rows = []
    for tr in soup.select('tr'):
        tds = [td.get_text(' ', strip=True) for td in tr.select('td')]
        a = tr.select_one('a[href*="/oferty-pracy/"]')
        if tds and a:
            rows.append('|'.join(tds) + '|' + a['href'].split('/oferty-pracy/')[1])
    links = []
    for a in soup.select('a[href*="/oferty-pracy/"]'):
        h = urllib.parse.urljoin(lst, a['href'])
        if not re.search(r'oferty-pracy/?$', h) and h not in links: links.append(h)
    txt = '=====LIST\n' + '\n'.join(rows) + '\n'
    for u in links:
        try:
            html = get(u).text
            s2 = BeautifulSoup(html, 'html.parser')
            pid = (re.search(r'postid-(\d+)', html) or [None, ''])[1]
            for x in s2(['script', 'style', 'noscript']): x.decompose()
            m = s2.select_one('.elementor-location-single') or s2.body
            t = m.get_text('\n')
            t = re.sub(r'[ \t]+', ' ', t); t = re.sub(r'\s*\n\s*', '\n', t).strip()
            txt += '=====JOB ' + u.split('/oferty-pracy/')[1].strip('/') + '\n@pid ' + pid + '\n' + t + '\n'
        except Exception as e:
            print('pej', u, e)
        pass  # odstęp pilnuje siec.get
    if not links: raise RuntimeError('PEJ: 0 ofert - plik nie zapisany')
    open(os.path.join(out, f'kp_pej_{day}.txt'), 'w', encoding='utf-8').write(txt)
    return len(links), len(rows)

# --- pracuj.pl (10.11.2026): wyszukiwanie po słowach kluczowych sektora jądrowego, pełna treść każdej oferty ---
# Do bazy trafiają tylko oferty faktycznie związane z energetyką jądrową (filtr w kod/kp_jadro.py); tu zbieramy wszystko, co znalazło wyszukiwanie.
# 10.11.2026: lista 15 słów uzgodniona z właścicielem („ochrona radiologiczna” tylko przez filtr „naprawdę jądrowe” w kp_jadro.py)
PRACUJ_KW = ['jądrowa', 'atomistyka', 'nuclear', 'AP1000', 'BWRX-300', 'reaktor SMR', 'Lubiatowo', 'Choczewo', 'Świerk', 'ISO 19443', 'NQA-1',
             'CFSI', 'ITNS', 'odpady promieniotwórcze', 'radiochemia']
# 11.11.2026: „ochrona radiologiczna” usunięta (decyzja właściciela; wróci, gdy dojdzie medycyna nuklearna)
def _nd(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else {}
def pracuj(out, day):
    znal = {}
    for kw in PRACUJ_KW:
        for pn in range(1, 11):
            u = 'https://www.pracuj.pl/praca/' + urllib.parse.quote(kw) + ';kw' + (f'?pn={pn}' if pn > 1 else '')
            try: d = _nd(get(u).text)
            except Exception as e: print('pracuj szukanie', kw, pn, e); break
            q = [x for x in d.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', []) if isinstance(x.get('state', {}).get('data'), dict) and 'groupedOffers' in x['state']['data']]
            if not q: break
            grupy = q[0]['state']['data']['groupedOffers']
            for g in grupy:
                for o in g.get('offers') or []:
                    znal.setdefault(str(o['partitionId']), {'url': o['offerAbsoluteUri'], 'miejsce': o.get('displayWorkplace'), 'kw': [], 'lista': {k: g.get(k) for k in ('jobTitle', 'companyName', 'companyId', 'salaryDisplayText', 'lastPublicated', 'initialPublicated', 'expirationDate', 'positionLevels', 'typesOfContract', 'workModes', 'isRemoteWorkAllowed')}})['kw'].append(kw)
            if len(grupy) < 20: break
            pass  # odstęp pilnuje siec.get
        pass  # odstęp pilnuje siec.get
    oferty = {}; zn = znane('pracuj'); t0 = time.time()
    stare = (poprzedni_dzien(os.path.join(out, f'kp_pracuj_{day}.json')).get('oferty') or {})
    for pid, o in znal.items():
        if (stare.get(pid) or {}).get('oferta'): o['oferta'] = stare[pid]['oferta']
        if o.get('oferta') or pid in zn or not czas_ok(t0, 240):
            oferty[pid] = o; continue      # treść znana z wcześniejszej nocy (kp_parse bierze ją z pamięci)
        try:
            d = _nd(get(o['url']).text)
            qq = [x['state']['data'] for x in d.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', []) if isinstance(x.get('state', {}).get('data'), dict) and 'attributes' in x['state']['data']]
            if qq: o['oferta'] = {k: qq[0].get(k) for k in ('attributes', 'textSections', 'publicationDetails', 'secondaryAttributes')}; zn[pid] = day
        except Exception as e: print('pracuj oferta', pid, e)
        oferty[pid] = o
        pass  # odstęp pilnuje siec.get
    zapisz_znane('pracuj', zn, set(znal))
    if not oferty: raise RuntimeError('pracuj.pl: 0 ofert - plik nie zapisany')
    json.dump({'fetched': day, 'format': 2, 'oferty': oferty}, open(os.path.join(out, f'kp_pracuj_{day}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return len(oferty)

# --- NCBJ (10.11.2026): oficjalna strona ofert ncbj.gov.pl/praca; filtr „naprawdę jądrowe” w kod/kp_jadro.py ---
def ncbj(out, day):
    baza = 'https://www.ncbj.gov.pl'; links = []
    for pn in range(0, 6):
        s = BeautifulSoup(get(baza + '/praca' + (f'?page={pn}' if pn else '')).text, 'html.parser')
        nowe = [urllib.parse.urljoin(baza, a['href']) for a in s.select('a[href^="/praca/"]')]
        nowe = [u for u in dict.fromkeys(nowe) if u not in links]
        if not nowe: break
        links += nowe
    oferty = {}
    for u in links:
        try:
            s = BeautifulSoup(get(u).text, 'html.parser')
            for x in s(['script', 'style', 'noscript', 'nav', 'header', 'footer']): x.decompose()
            h1 = s.select_one('h1'); m = s.select_one('main') or s.body
            t = re.sub(r'\s*\n\s*', '\n', re.sub(r'[ \t]+', ' ', m.get_text('\n'))).strip()
            oferty[u.rsplit('/', 1)[-1]] = {'url': u, 'tytul': h1.get_text(' ', strip=True) if h1 else '', 'tekst': t[:20000]}
        except Exception as e: print('ncbj', u, e)
        pass  # odstęp pilnuje siec.get
    if not oferty: raise RuntimeError('NCBJ: 0 ofert - plik nie zapisany')
    json.dump({'fetched': day, 'oferty': oferty}, open(os.path.join(out, f'kp_ncbj_{day}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return len(oferty)

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    day = os.path.basename(out.rstrip('/')).replace('-', '')
    import swiat
    for k, f in swiat.KOLEKTORY.items(): globals()[k] = f
    # kolejność = priorytet przy limicie czasu: Polska, mała Europa, duża Europa, świat (Bechtel, Westinghouse, OPG)
    which = sys.argv[2:] or ['pej', 'pracuj', 'ncbj', 'kprm', 'clor', 'kznpp', 'snn', 'szc', 'hpc', 'iter', 'iaea', 'edfuk', 'fortum', 'cez', 'orano', 'cea', 'vattenfall'] + [k for k in swiat.KOLEKTORY if k.startswith('pr_')] + ['bechtel', 'wec', 'opg']
    # 11.2026: duże listy rotacyjnie co 2. noc (w noc przerwy źródło nie jest zbierane = oferty nie są zamykane, zostają z ostatniej listy)
    ROTACJA = {'cea': 0, 'vattenfall': 0, 'orano': 1}
    nr = datetime.date.today().toordinal() % 2
    if not sys.argv[2:]: which = [w for w in which if ROTACJA.get(w, nr) == nr]
    report = {'_rotacja': {'noc': nr, 'pominiete': [w for w, r in ROTACJA.items() if r != nr]}}
    for w in which:
        t = time.time()
        try:
            report[w] = {'ok': True, 'n': globals()[w](out, day)}
        except Exception as e:
            report[w] = {'ok': False, 'err': str(e)[:300]}
        report[w]['s'] = round(time.time() - t); report[w]['od_startu'] = round(time.time() - swiat.START)
        print(w, report[w], flush=True)
    json.dump(report, open(os.path.join(out, 'raport_zbierania.json'), 'w'), ensure_ascii=False, indent=1)
