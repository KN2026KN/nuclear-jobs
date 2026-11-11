# Nowe źródła ofert (11.2026): Polska (PAA i nabory KPRM, CLOR), Europa (EDF UK / HPC, Sizewell C, Orano, CEA, Kozloduy NPP,
# Nuclearelectrica, ČEZ, Slovenské elektrárne, Vattenfall), według sondy z runnera GitHub (data/log/sonda/).
# Każde źródło: lista co noc (pełna lista aktualnych ofert) + pełna treść tylko nowych ofert (pamięć data/cache/znane_<źródło>.json),
# z limitem czasu na źródło. Format pliku dziennego: raw/RRRR-MM-DD/kp_sw_<źródło>_<dzień>.json
#   {'fetched', 'zrodlo', 'pracodawca', 'kraj', 'filtr', 'lista': [{id, url, tytul, ...}], 'tresci': {id: {tekst, ...}}}
# Tylko GET. Bez formularzy, logowania, kont. Bez nazwisk rekruterów (treść czyszczona w kp_parse).
import os, re, json, time, datetime, urllib.parse
from bs4 import BeautifulSoup
from siec import get, znane, zapisz_znane, czas_ok, START, poprzedni_dzien

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def tekst_strony(html, sel=None):
    s = BeautifulSoup(html, 'html.parser')
    for x in s(['script', 'style', 'noscript', 'nav', 'header', 'footer', 'form', 'iframe', 'svg']): x.decompose()
    m = None
    for c in ([sel] if sel else []) + ['article', 'main', '[role=main]', '.job-description', '.content', '#content']:
        m = s.select_one(c)
        if m and len(m.get_text(strip=True)) > 200: break
        m = None
    m = m or s.body or s
    t = re.sub(r'[ \t\xa0]+', ' ', m.get_text('\n'))
    h1 = s.select_one('h1')
    return (h1.get_text(' ', strip=True) if h1 else ''), re.sub(r'\s*\n\s*', '\n', t).strip()[:30000]

def zapisz(out, day, zrodlo, meta, lista, tresci):
    json.dump({'fetched': NOW, 'zrodlo': zrodlo, 'lista_pelna': PELNA.get(zrodlo, True), **meta, 'lista': lista, 'tresci': tresci},
              open(os.path.join(out, f'kp_sw_{zrodlo}_{day}.json'), 'w', encoding='utf-8'), ensure_ascii=False)

def tresci_nowych(zrodlo, lista, day, limit_s, sel=None, pobierz=None, out=None):
    zn = znane(zrodlo); t0 = time.time()
    T = dict(poprzedni_dzien(os.path.join(out, f'kp_sw_{zrodlo}_{day}.json')).get('tresci') or {}) if out else {}
    for it in lista:
        if it['id'] in zn or it['id'] in T or it.get('bez_tresci'): continue
        if not czas_ok(t0, limit_s): break
        try:
            if pobierz: T[it['id']] = pobierz(it)
            else:
                h1, t = tekst_strony(get(it['url']).text, sel); T[it['id']] = {'h1': h1, 'tekst': t}
            zn[it['id']] = day
        except Exception as e:
            print(zrodlo, it['id'], str(e)[:150])
    zapisz_znane(zrodlo, zn, {x['id'] for x in lista})
    return T

def linki(url, wzorzec, idrx):
    """(lista ofert z jednej strony listy): linki pasujące do wzorca, id z idrx, tytuł = tekst linku (najdłuższy)."""
    html = get(url).text; s = BeautifulSoup(html, 'html.parser'); L = {}
    for a in s.find_all('a', href=True):
        h = urllib.parse.urljoin(url, a['href'].replace('&amp;', '&'))
        if not re.search(wzorzec, h): continue
        m = re.search(idrx, h); i = m.group(1) if m else h
        t = re.sub(r'\s+', ' ', a.get_text(' ', strip=True))
        if i not in L or len(t) > len(L[i]['tytul']): L[i] = {'id': i, 'url': h.split('?')[0] if '?' in h and 'jobs.cz' in h else h, 'tytul': t}
    return list(L.values()), html

PELNA = {}   # źródło -> czy lista jest kompletna (False: błąd w połowie, limit stron albo czasu - wtedy bez zamykania ofert)
LIMIT_LISTY = 240   # s na listę jednego źródła

def stronicuj(szablon, wzorzec, idrx, maks_stron, start=1, krok=1, zrodlo=None):
    wszystkie = {}; p = start; pelna = False; t0 = time.time()
    for n in range(maks_stron):
        if time.time() - t0 > LIMIT_LISTY or time.time() - START > 1200: print('lista: limit czasu', zrodlo); break
        try: L, _h = linki(szablon.format(p=p), wzorzec, idrx)
        except Exception as e:
            print('lista', szablon.format(p=p), str(e)[:120])
            if n == 0: raise
            if 'HTTP 404' in str(e): pelna = True        # strona za ostatnią = koniec listy
            break
        nowe = [x for x in L if x['id'] not in wszystkie]
        for x in nowe: wszystkie[x['id']] = x
        if not nowe or '{p}' not in szablon: pelna = True; break
        p += krok
    if zrodlo: PELNA[zrodlo] = pelna
    print(f'lista {zrodlo}: {len(wszystkie)} ofert, stron {n + 1}, {round(time.time() - t0)} s, pełna: {pelna}', flush=True)
    return list(wszystkie.values())

# ---------------------------------------------------------------- Polska
def kprm(out, day):
    """nabory.kprm.gov.pl (służba cywilna): PAA (instytucja 1020) + branża „atomistyka” (1486) + fraza „jądrow”."""
    baza = 'https://nabory.kprm.gov.pl/'
    zap = {'paa': 'Ad%5Bid_institution%5D%5B0%5D=inst1020', 'atom': 'Ad%5Bbranch_ids%5D%5B0%5D=1486', 'fraza': 'Ad%5Bphrase%5D=j%C4%85drow'}
    L = {}; PELNA['kprm'] = True
    for nazwa, q in zap.items():
        for p in range(1, 30 if nazwa != 'fraza' else 6):     # fraza: tylko 5 stron najnowszych (reszta to oferty niejądrowe)
            try: s = BeautifulSoup(get(f'{baza}?{q}&search-button=&page={p}&per-page=10').text, 'html.parser')
            except Exception as e:
                print('kprm', nazwa, p, str(e)[:120]); PELNA['kprm'] = False; break
            items = s.select('a.single'); przed = len(L)
            for a in items:
                pola = {}
                for r in a.select('.r'):
                    sp = r.select_one('span'); b = r.select_one('b')
                    if sp and b: pola[sp.get_text(strip=True).rstrip(':').lower()] = b.get_text(' ', strip=True)
                nr = (a.select_one('.id').get_text(strip=True) if a.select_one('.id') else '').replace('NR', '').strip()
                t = a.select_one('.title')
                i = nr or a['href']
                L.setdefault(i, {'id': i, 'url': urllib.parse.urljoin(baza, a['href']), 'tytul': t.get_text(' ', strip=True) if t else '',
                                 'pracodawca': pola.get('urząd'), 'dzial': pola.get('dział'), 'miasto': pola.get('miejscowość'), 'wazne_do': pola.get('ważne do'), 'zapytania': []})['zapytania'].append(nazwa)
            if len(items) < 10 or len(L) == przed: break
    dzis = datetime.date.today().isoformat()
    def termin(w):
        m = re.match(r'(\d{2})\.(\d{2})\.(\d{4})', w or '')
        return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else '9999'
    lista = [x for x in L.values() if termin(x.get('wazne_do')) >= dzis]     # 11.11.2026: po terminie - pomijamy (bez treści)
    print(f'kprm: {len(L)} na liście, {len(lista)} w terminie', flush=True)
    if not lista: raise RuntimeError('KPRM: pusta lista')
    T = tresci_nowych('kprm', lista, day, 150, sel='.job-details, .content, main', out=out)
    zapisz(out, day, 'kprm', {'pracodawca': None, 'kraj': 'PL', 'filtr': 'kprm'}, lista, T)
    return len(lista), len(T)

def clor(out, day):
    """CLOR - ogłoszenia jako pliki PDF; tytuł z linku, bez pełnej treści."""
    u = 'https://clor.waw.pl/ogloszenia/praca-i-praktyki.html'
    s = BeautifulSoup(get(u).text, 'html.parser'); lista = []
    for a in s.find_all('a', href=True):
        h = urllib.parse.urljoin(u, a['href'])
        if re.search(r'/praca_i_praktyki/.*\.pdf', h, re.I) and not re.search(r'RODO|Formularz|klauzul', h, re.I):
            t = re.sub(r'\s+', ' ', (a.find_parent(['p', 'li', 'td', 'div']) or a).get_text(' ', strip=True))[:300]
            lista.append({'id': h.rsplit('/', 1)[-1], 'url': h, 'tytul': t or a.get_text(' ', strip=True), 'bez_tresci': True})
    zapisz(out, day, 'clor', {'pracodawca': 'Centralne Laboratorium Ochrony Radiologicznej (CLOR)', 'kraj': 'PL', 'filtr': None}, lista, {})
    return len(lista)

# ---------------------------------------------------------------- Wielka Brytania (SuccessFactors RMK, jak Westinghouse)
def _sf(out, day, zrodlo, base, zapytanie, pracodawca, limit_s, kraj='GB', filtr=None):
    from collect import sf_lista, sf_szczegoly
    WL = sf_lista(base, zapytanie)
    if not WL: raise RuntimeError(f'{zrodlo}: pusta lista')
    stare = poprzedni_dzien(os.path.join(out, f'kp_sw_{zrodlo}_{day}.json')).get('tresci') or {}
    J = sf_szczegoly(base, WL, zrodlo, day, limit_s, {k: {'descHtml': v.get('html'), 'meta': v.get('meta')} for k, v in stare.items()})
    lista = [{'id': x['path'], 'url': base + x['path'], 'tytul': x['title'], 'lokalizacja': x['loc'], 'data': x['date']} for x in WL]
    tresci = {k: {'html': v.get('descHtml'), 'meta': v.get('meta')} for k, v in J.items()}
    zapisz(out, day, zrodlo, {'pracodawca': pracodawca, 'kraj': kraj, 'filtr': filtr}, lista, tresci)
    return len(lista), len(J)

def iter_(out, day):
    return _sf(out, day, 'iter', 'https://iter.jobs.hr.cloud.sap', 'q=&locationsearch=', 'ITER Organization', 90, kraj='FR')

def fortum(out, day):
    # Fortum: tylko wyszukiwanie „nuclear” + filtr jądrowy na treści (Loviisa, ydinvoima)
    return _sf(out, day, 'fortum', 'https://jobs.fortum.com', 'q=nuclear&locationsearch=', 'Fortum', 90, kraj='FI', filtr='jadrowy')

def opg(out, day):
    # Ontario Power Generation (Darlington, Pickering, Darlington SMR) - poziom 2 (świat), filtr jądrowy
    return _sf(out, day, 'opg', 'https://jobs.opg.com', 'q=nuclear&locationsearch=', 'Ontario Power Generation', 90, kraj='CA', filtr='jadrowy')

def hpc(out, day):
    return _sf(out, day, 'hpc', 'https://hpcjobsservice.edfenergy.com', 'q=&locationsearch=', 'Hinkley Point C / Sizewell C Jobs Service (EDF i wykonawcy)', 180)

def szc(out, day):
    return _sf(out, day, 'szc', 'https://jobs.sizewellc.com', 'q=&locationsearch=', 'Sizewell C', 120)

def edfuk(out, day):
    lista = stronicuj('https://careers.edfenergy.com/jobs?page={p}', r'/job/[^/]+-jid-\d+', r'jid-(\d+)', 40, zrodlo='edfuk')
    if not lista: raise RuntimeError('EDF Energy: pusta lista')
    T = tresci_nowych('edfuk', lista, day, 150, out=out)
    zapisz(out, day, 'edfuk', {'pracodawca': 'EDF Energy', 'kraj': 'GB', 'filtr': 'jadrowy'}, lista, T)
    return len(lista), len(T)

# ---------------------------------------------------------------- Francja
def orano(out, day):
    lista = stronicuj('https://jobs.orano.group/en_US/jobs/SearchJobs/?jobOffset={p}', r'/jobs/JobDetail/', r'/JobDetail/[^/]*/(\d+)', 90, start=0, krok=12, zrodlo='orano')
    if not lista: raise RuntimeError('Orano: pusta lista')
    T = tresci_nowych('orano', lista, day, 180, out=out)
    zapisz(out, day, 'orano', {'pracodawca': 'Orano', 'kraj': 'FR', 'filtr': None}, lista, T)
    return len(lista), len(T)

def cea(out, day):
    lista = stronicuj('https://www.emploi.cea.fr/offre-de-emploi/liste-offres.aspx?page={p}', r'/offre-de-emploi/emploi-[^/]+_\d+\.aspx', r'_(\d+)\.aspx', 100, zrodlo='cea')
    if not lista: raise RuntimeError('CEA: pusta lista')
    T = tresci_nowych('cea', lista, day, 180, out=out)
    zapisz(out, day, 'cea', {'pracodawca': 'CEA', 'kraj': 'FR', 'filtr': 'jadrowy'}, lista, T)
    return len(lista), len(T)

# ---------------------------------------------------------------- Europa Środkowa i Wschodnia, Skandynawia
def kznpp(out, day):
    lista = stronicuj('https://www.kznpp.org/bg/jobs?page={p}', r'/bg/jobs/\d+$', r'/jobs/(\d+)', 10, zrodlo='kznpp')
    if not lista: raise RuntimeError('Kozloduy NPP: pusta lista')
    T = tresci_nowych('kznpp', lista, day, 60, out=out)
    zapisz(out, day, 'kznpp', {'pracodawca': 'АЕЦ Козлодуй (Kozloduy NPP)', 'kraj': 'BG', 'filtr': None}, lista, T)
    return len(lista), len(T)

def snn(out, day):
    lista = stronicuj('https://nuclearelectrica.ro/snn/category/joburi/page/{p}/', r'nuclearelectrica\.ro/snn/\d{4}/\d{2}/\d{2}/[^/]+/?$', r'/snn/(\d{4}/\d{2}/\d{2}/[^/]+)', 6, zrodlo='snn')
    if not lista: raise RuntimeError('Nuclearelectrica: pusta lista')
    T = tresci_nowych('snn', lista, day, 90, out=out)
    zapisz(out, day, 'snn', {'pracodawca': 'Nuclearelectrica (SNN)', 'kraj': 'RO', 'filtr': None}, lista, T)
    return len(lista), len(T)

def cez(out, day):
    # ČEZ publikuje oferty w swoim serwisie kdejinde.jobs.cz (portal jobs.cz, prowadzony przez ČEZ) - tylko jądrowe
    lista = stronicuj('https://beta.jobs.cz/prace/?keywords%5B%5D=%C4%8CEZ&page={p}', r'kdejinde\.jobs\.cz/pd/\d+', r'/pd/(\d+)', 40, zrodlo='cez')
    if not lista: raise RuntimeError('ČEZ: pusta lista')
    T = tresci_nowych('cez', lista, day, 150, out=out)
    zapisz(out, day, 'cez', {'pracodawca': 'ČEZ', 'kraj': 'CZ', 'filtr': 'jadrowy'}, lista, T)
    return len(lista), len(T)

def seas(out, day):
    # Slovenské elektrárne publikują oferty na profesia.sk (link z ich strony kariery) - tylko jądrowe
    lista = stronicuj('https://www.profesia.sk/praca/slovenske-elektrarne/C5070?page_num={p}', r'profesia\.sk/praca/slovenske-elektrarne/O\d+', r'/O(\d+)', 15, zrodlo='seas')
    if not lista: raise RuntimeError('Slovenské elektrárne: pusta lista')
    T = tresci_nowych('seas', lista, day, 120, out=out)
    zapisz(out, day, 'seas', {'pracodawca': 'Slovenské elektrárne', 'kraj': 'SK', 'filtr': 'jadrowy'}, lista, T)
    return len(lista), len(T)

def vattenfall(out, day):
    lista = stronicuj('https://careers.vattenfall.com/global/jobs?page={p}', r'/global/job/[^/]+-jid-\d+', r'jid-(\d+)', 60, zrodlo='vattenfall')
    if not lista: raise RuntimeError('Vattenfall: pusta lista')
    T = tresci_nowych('vattenfall', lista, day, 150, out=out)
    zapisz(out, day, 'vattenfall', {'pracodawca': 'Vattenfall', 'kraj': 'SE', 'filtr': 'jadrowy'}, lista, T)
    return len(lista), len(T)

# seas (Slovenské elektrárne na profesia.sk): lista ładowana skryptem, 0 linków z serwera - wyłączone (11.2026), funkcja zostaje do ponownej próby
# ---------------------------------------------------------------- IAEA (Taleo): wyszukiwarka REST przez POST - tylko odczyt listy (decyzja właściciela 11.11.2026)
def iaea(out, day):
    import requests
    from siec import S
    api = 'https://iaea.taleo.net/careersection/rest/jobboard/searchjobs?lang=en&portal=8105100373'
    filtry = lambda ids: {'searchFilterSelections': [{'id': i, 'selectedValues': []} for i in ids]}
    lista = []; strona = 1; total = None
    while True:
        body = {'multilineEnabled': False, 'sortingSelection': {'sortBySelectionParam': '3', 'ascendingSortingOrder': 'false'},
                'fieldData': {'fields': {'KEYWORD': '', 'LOCATION': ''}, 'valid': True},
                'filterSelectionParam': filtry(['POSTING_DATE', 'LOCATION', 'JOB_FIELD']),
                'advancedSearchFiltersSelectionParam': filtry(['ORGANIZATION', 'LOCATION', 'JOB_FIELD', 'JOB_NUMBER', 'URGENT_JOB', 'EMPLOYEE_STATUS', 'STUDY_LEVEL', 'WILL_TRAVEL', 'JOB_SHIFT']),
                'pageNo': strona}
        time.sleep(1.2)
        r = S.post(api, json=body, headers={'Content-Type': 'application/json', 'tz': 'GMT+01:00', 'tzname': 'Europe/Vienna',
                                            'Referer': 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl?lang=en'}, timeout=40)
        if r.status_code != 200: raise RuntimeError(f'IAEA: HTTP {r.status_code} {r.text[:200]}')
        d = r.json(); req = d.get('requisitionList') or []
        if strona == 1: print('iaea diag', list(d.keys())[:10], json.dumps(req[:1])[:400], json.dumps(d.get('pagingData'))[:200], flush=True)
        for x in req:
            col = x.get('column') or []
            nr = x.get('contestNo') or x.get('jobId')
            try: lok = json.loads(col[1])[0] if len(col) > 1 else ''
            except Exception: lok = str(col[1]) if len(col) > 1 else ''
            cz = lok.split('-')
            miasto = cz[2] if len(cz) > 2 else 'Vienna'
            dl = re.match(r'(\d{4}-\d{2}-\d{2})', col[2]) if len(col) > 2 else None
            lista.append({'id': str(nr), 'url': 'https://iaea.taleo.net/careersection/ex/jobdetail.ftl?job=' + urllib.parse.quote(str(nr)) + '&lang=en',
                          'tytul': col[0] if col else '', 'miasto': miasto, 'lokalizacja': f'{miasto}, {cz[0] if cz else "Austria"}',
                          'wazne_do': dl.group(1) if dl else None})
        pg = d.get('pagingData') or {}; total = pg.get('totalCount') or total or 0
        if not req or strona * (pg.get('pageSize') or 25) >= total or strona > 20: break
        strona += 1
    if not lista: raise RuntimeError('IAEA: pusta lista')
    def pobierz(it):
        h = get(it['url']).text
        m = re.search(r'name="initialHistory"[^>]*value="([^"]*)"', h)
        if m:
            import html as H, urllib.parse as up
            v = up.unquote(H.unescape(m.group(1)))
            czesci = [c for c in v.split('!|!') if len(c) > 200]
            t = BeautifulSoup(max(czesci, key=len), 'html.parser').get_text('\n') if czesci else ''
        else:
            t = tekst_strony(h)[1]
        t = t.replace('!*!', '').replace('\\:', ':')
        return {'tekst': re.sub(r'\s*\n\s*', '\n', t).strip()[:30000]}
    T = tresci_nowych('iaea', lista, day, 120, pobierz=pobierz, out=out)
    zapisz(out, day, 'iaea', {'pracodawca': 'IAEA', 'kraj': 'AT', 'filtr': None}, lista, T)
    return len(lista), len(T)

# ---------------------------------------------------------------- pracodawcy z konfiguracji (11.11.2026): data/pracodawcy/podlaczone.json
# typ „linki”: strona listy (opcjonalnie {p} = numer strony) + wzorzec linku oferty; „workday”: publiczna wyszukiwarka JSON (POST, tylko odczyt);
# „smartrecruiters”: publiczne API; „sf”: SuccessFactors RMK. filtr „jadrowy” = tylko oferty z treścią jądrową.
def _konfig():
    try: return json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pracodawcy', 'podlaczone.json'), encoding='utf-8'))
    except Exception as e:
        print('podlaczone.json:', e); return []

def _workday(url):
    from siec import S
    m = re.match(r'(https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com)/(?:[a-z]{2}-[A-Z]{2}/)?([^/?]+)', url)
    base, tenant, site = m.group(1), m.group(2), m.group(4)
    api = f'{base}/wday/cxs/{tenant}/{site}/jobs'; L = []; off = 0
    while off < 2000:
        time.sleep(1.2)
        r = S.post(api, json={'appliedFacets': {}, 'limit': 20, 'offset': off, 'searchText': ''}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=40)
        r.raise_for_status(); d = r.json(); jp = d.get('jobPostings') or []
        for j in jp:
            L.append({'id': j.get('externalPath'), 'url': f'{base}/en-US/{site}' + j.get('externalPath', ''), 'tytul': j.get('title', ''), 'lokalizacja': j.get('locationsText', ''), 'data': j.get('postedOn', '')})
        off += 20
        if not jp or off >= (d.get('total') or 0): break
    def tresc(it):
        time.sleep(1.2)
        j = S.get(f'{base}/wday/cxs/{tenant}/{site}' + it['id'], headers={'Accept': 'application/json'}, timeout=40).json().get('jobPostingInfo') or {}
        return {'html': j.get('jobDescription', ''), 'meta': {'jobLocation': j.get('location', ''), 'datePosted': j.get('startDate', '')}}
    return L, tresc, True

def _smartr(firma):
    L = []; off = 0
    while off < 2000:
        d = get(f'https://api.smartrecruiters.com/v1/companies/{firma}/postings?limit=100&offset={off}').json()
        for j in d.get('content') or []:
            loc = j.get('location') or {}
            L.append({'id': j['id'], 'url': f"https://jobs.smartrecruiters.com/{firma}/{j['id']}", 'tytul': j.get('name', ''),
                      'lokalizacja': ', '.join(x for x in (loc.get('city'), (loc.get('country') or '').upper()) if x), 'data': (j.get('releasedDate') or '')[:10]})
        off += 100
        if off >= (d.get('totalFound') or 0): break
    def tresc(it):
        j = get(f"https://api.smartrecruiters.com/v1/companies/{firma}/postings/{it['id']}").json()
        sec = (j.get('jobAd') or {}).get('sections') or {}
        return {'html': ' '.join((sec.get(k) or {}).get('text', '') for k in ('companyDescription', 'jobDescription', 'qualifications', 'additionalInformation'))}
    return L, tresc, True

def _z_konfiguracji(c):
    def f(out, day):
        zr = 'pr_' + c['klucz']
        if c['typ'] == 'workday': lista, pob, pelna = _workday(c['url'])
        elif c['typ'] == 'smartrecruiters': lista, pob, pelna = _smartr(c['firma'])
        elif c['typ'] == 'sf':
            return _sf(out, day, zr, c['url'], c.get('zapytanie', 'q=&locationsearch='), c['pracodawca'], c.get('limit_s', 40), kraj=c['kraj'], filtr=c.get('filtr'))
        else:
            lista = stronicuj(c['url'], c['wzorzec'], c.get('id', r'(.+)'), c.get('strony', 1), start=c.get('start', 1), krok=c.get('krok', 1), zrodlo=zr)
            pob, pelna = None, PELNA.get(zr, True)
        if not lista: raise RuntimeError(f"{c['pracodawca']}: pusta lista")
        PELNA[zr] = pelna
        T = tresci_nowych(zr, lista, day, c.get('limit_s', 40), sel=c.get('sel'), pobierz=pob, out=out)
        zapisz(out, day, zr, {'pracodawca': c['pracodawca'], 'kraj': c['kraj'], 'filtr': c.get('filtr'), 'sektor': c.get('sektor')}, lista, T)
        return len(lista), len(T)
    return f

KOLEKTORY = {'kprm': kprm, 'clor': clor, 'hpc': hpc, 'szc': szc, 'edfuk': edfuk, 'orano': orano, 'cea': cea, 'kznpp': kznpp, 'snn': snn,
             'cez': cez, 'vattenfall': vattenfall, 'iter': iter_, 'fortum': fortum, 'opg': opg, 'iaea': iaea}
for _c in _konfig():
    if _c.get('aktywny', True): KOLEKTORY['pr_' + _c['klucz']] = _z_konfiguracji(_c)
