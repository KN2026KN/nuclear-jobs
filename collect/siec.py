# Wspólne: sesja HTTP z odstępem >= 1,2 s między zapytaniami do jednej domeny, pamięć znanych ofert (przyrostowo),
# budżet czasu na pobieranie pełnych treści (11.2026). Tylko GET - bez formularzy, logowania i kont.
import os, json, time, urllib.parse, requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
      'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8,fr;q=0.6'}
S = requests.Session(); S.headers.update(UA)
ODSTEP = 1.2
_ost = {}

def get(url, tries=3, **kw):
    dom = urllib.parse.urlparse(url).netloc
    last = ''
    for i in range(tries):
        czek = ODSTEP - (time.time() - _ost.get(dom, 0))
        if czek > 0: time.sleep(czek)
        try:
            r = S.get(url, timeout=40, **kw); _ost[dom] = time.time()
            if r.status_code == 200: return r
            last = f'HTTP {r.status_code}'
            if r.status_code in (403, 404, 410): break
        except Exception as e:
            _ost[dom] = time.time(); last = str(e)[:200]
        time.sleep(3 + 5 * i)
    raise RuntimeError(f'{url}: {last}')

# --- pamięć znanych ofert: data/cache/znane_<źródło>.json = {id: dzień pobrania pełnej treści} ---
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')

def znane(zrodlo):
    p = os.path.join(CACHE, f'znane_{zrodlo}.json')
    try: return json.load(open(p))
    except Exception: return {}

def zapisz_znane(zrodlo, d, aktualne=None):
    """aktualne: id z dzisiejszej listy - oferty zniknięte z listy usuwamy z pamięci (wrócą = pobierzemy treść od nowa)."""
    os.makedirs(CACHE, exist_ok=True)
    if aktualne is not None: d = {k: v for k, v in d.items() if k in aktualne}
    json.dump(d, open(os.path.join(CACHE, f'znane_{zrodlo}.json'), 'w'), ensure_ascii=False, indent=0, sort_keys=True)

# --- budżet czasu pełnych treści: każde źródło ma swój limit (s), a cała noc - limit od startu robota (KP_LIMIT_NOCY, s) ---
START = time.time()
LIMIT_NOCY = float(os.environ.get('KP_LIMIT_NOCY', 1080))   # 18 min na treści; listy do 20 min; reszta workflow - do 30 min

def czas_ok(start_zrodla, limit_zrodla):
    return (time.time() - start_zrodla) < limit_zrodla and (time.time() - START) < LIMIT_NOCY

def poprzedni_dzien(path):
    """Plik z tego samego dnia z wcześniejszego przebiegu (.json albo .json.gz) - żeby drugi przebieg nie zgubił pobranych treści."""
    import gzip
    for p in (path, path + '.gz'):
        if os.path.exists(p):
            try: return json.load(gzip.open(p, 'rt', encoding='utf-8') if p.endswith('.gz') else open(p, encoding='utf-8'))
            except Exception: pass
    return {}
