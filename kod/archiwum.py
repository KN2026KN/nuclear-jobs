# Robot archiwów (11.11.2026): stare oferty pracy z Internet Archive (Wayback) dla każdego pracodawcy,
# rok po roku od najnowszego do najstarszego, aż do pierwszego zapisu w archiwum („dno”).
# Stan i statystyka głębokości: data/archiwum/glebokosc.json; oferty: raw/archiwum/<cel>/<rok>.json.gz
# Cele: data/archiwum/cele.json (ręczne) + strony kariery z data/pracodawcy/sonda.json (automatycznie).
# Użycie: python3 kod/archiwum.py [limit_sekund]
import os, re, sys, json, gzip, time, datetime as dt
from urllib.parse import urlparse
import requests
sys.path.insert(0, os.path.dirname(__file__))
from bez_kontaktow import czysc
from kp_jadro import jadrowa

LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 5400
START = time.time()
UA = {'User-Agent': 'Mozilla/5.0 (keura.eu nuclear-jobs archive research; contact via keura.eu)'}
S = requests.Session(); S.headers.update(UA)
GL = 'data/archiwum/glebokosc.json'
SZCZEGOL = re.compile(r'(job|jobs|vacanc|vakan|offer|oferta|ofert|stellen|emploi|career|position|requisition|posting|jid|wakat|praca|вакан|rabota|empleo|vacature|tyopaikka|recruit)[^?#]*?\d{3,}', re.I)
SMIECI = re.compile(r'\.(css|js|png|jpe?g|gif|svg|ico|woff2?|ttf|pdf|xml|json)(\?|$)|/(search|login|apply|signin|register|rss|feed|share|print)\b', re.I)
CO_ROK = 1  # rok na krok
NA_CEL = float(os.environ.get('ARCH_NA_CEL', 900))   # sekund na jednego pracodawcę na noc - wszyscy idą w głąb równo

def czas_ok(zapas=60, od=None):
    if od and time.time() - od > NA_CEL: return False
    return time.time() - START < LIMIT - zapas

OSTATNI_BLAD = ['']   # powód ostatniego niepowodzenia - trafia do glebokosc.json (12.11.2026)

def get(url, proby=3, timeout=60, **kw):
    for proba in range(proby):
        try:
            r = S.get(url, timeout=timeout, **kw)
            if r.status_code == 429 or r.status_code >= 500:
                OSTATNI_BLAD[0] = f'HTTP {r.status_code}'
                time.sleep(min(30 * 2 ** proba, 240)); continue   # 30, 60, 120, 240 s - archiwum ogranicza tempo
            return r
        except requests.RequestException as e:
            OSTATNI_BLAD[0] = type(e).__name__
            time.sleep(min(15 * 2 ** proba, 120))
    return None

def _cdx_raz(cel, par):
    """Jedno zapytanie CDX ze stronicowaniem przez resumeKey (paczki po 5000) - duże domeny nie przekraczają czasu."""
    p = {'url': cel['url'], 'matchType': cel.get('match', 'prefix'), 'output': 'json', 'fl': 'timestamp,original', 'filter': 'statuscode:200', 'collapse': 'urlkey'}
    p.update(par)
    maks = int(p.pop('limit', 20000)); wynik = []; klucz = None
    while len(wynik) < maks:
        q = dict(p, limit=min(5000, maks - len(wynik)), showResumeKey='true')
        if klucz: q['resumeKey'] = klucz
        r = get('https://web.archive.org/cdx/search/cdx', proby=5, timeout=180, params=q)
        time.sleep(2.5)
        if r is None: return None
        if r.status_code != 200: OSTATNI_BLAD[0] = f'HTTP {r.status_code}'; return None
        try: w = r.json()
        except ValueError: OSTATNI_BLAD[0] = 'nie-JSON'; return None
        w = w[1:] if w else []
        klucz = None
        if len(w) >= 2 and w[-2] == []: klucz = w[-1][0]; w = w[:-2]   # [..., [], [resumeKey]]
        wynik += [x for x in w if len(x) == 2]
        if not klucz: break
    return wynik

def cdx(cel, **par):
    w = _cdx_raz(cel, par)
    if w is not None or 'from' not in par or par.get('from') != par.get('to') or len(str(par['from'])) != 4: return w
    # cały rok się nie udał - próbujemy miesiąc po miesiącu
    rok = str(par['from']); razem = []
    for m in range(1, 13):
        x = _cdx_raz(cel, dict(par, **{'from': f'{rok}{m:02d}', 'to': f'{rok}{m:02d}'}))
        if x is None: return None
        razem += x
    seen = set(); out = []
    for ts, u in razem:
        if u not in seen: seen.add(u); out.append((ts, u))
    return out

def cele():
    C = {}
    try: C.update(json.load(open('data/archiwum/cele.json', encoding='utf-8')))
    except FileNotFoundError: pass
    try: sonda = json.load(open('data/pracodawcy/sonda.json', encoding='utf-8'))
    except FileNotFoundError: sonda = []
    for x in sonda:
        u = x.get('kariera') or ''
        if not u or x.get('kariera_status') != 200: continue
        p = urlparse(u); host = p.netloc.lower()
        sciezka = p.path.rstrip('/')
        wspolne = re.search(r'myworkdayjobs|successfactors|taleo|smartrecruiters|teamtailor|greenhouse|lever\.co|avature|jobs\.cz|erecruiter', host)
        url = host + (sciezka if (wspolne or sciezka.count('/') > 1) else '')
        if '/' not in url: url = re.sub(r'^www\.', '', url)
        klucz = re.sub(r'[^a-z0-9]+', '_', x['nazwa'].lower()).strip('_')[:40]
        C.setdefault(klucz, {'firma': x['nazwa'], 'kraj': x['kraj'], 'url': url, 'match': 'prefix' if '/' in url else 'domain', 'zrodlo': 'sonda'})
    return C

def tekst(html):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, 'html.parser')
    for t in s(['script', 'style', 'noscript', 'nav', 'footer', 'header']): t.decompose()
    tyt = (s.find('h1').get_text(' ', strip=True) if s.find('h1') else '') or (s.title.get_text(' ', strip=True) if s.title else '')
    txt = re.sub(r'\n{3,}', '\n\n', s.get_text('\n', strip=True))
    return czysc(tyt)[:300], czysc(txt)[:15000]

def wczytaj(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except (FileNotFoundError, ValueError): return d

def czy_jadrowa(firma, o):
    """Adres strony też niesie dane (np. southerncompany.jobs/waynesboro-ga/it-analyst/...) - ważne, gdy archiwum ma tylko pustą powłokę JS."""
    sciezka = re.sub(r'[-_/+]+', ' ', urlparse(o.get('url', '')).path)
    return jadrowa(firma, (o.get('tytul', '') + ' ' + sciezka).strip(), [('lok', sciezka), ('opis', o.get('tekst', ''))])[0]

def przelicz(G):
    """Liczba ofert jądrowych we wszystkich zapisanych latach wg bieżącej reguły kp_jadro (np. po zmianie z 12.11.2026)."""
    for k, g in G.items():
        for rok, v in g.get('lata', {}).items():
            plik = f'raw/archiwum/{k}/{rok}.json.gz'
            if not os.path.exists(plik): continue
            of = json.load(gzip.open(plik, 'rt', encoding='utf-8'))['oferty']
            v['jadrowe'] = sum(1 for o in of if not o.get('blad') and czy_jadrowa(g['firma'], o))
        g['jadrowych_razem'] = sum(v.get('jadrowe', 0) for v in g.get('lata', {}).values())
    json.dump(G, open(GL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)

def main():
    G = wczytaj(GL, {})
    C = cele(); teraz = dt.date.today().year
    # najpierw cele bez ustalonego dna, potem wg najmniej przerobionych
    kolej = sorted(C, key=lambda k: (G.get(k, {}).get('status') in ('dno', 'brak w archiwum'), G.get(k, {}).get('ostatnio', '')))
    zrobione = 0
    for k in kolej:
        if not czas_ok(): break
        c = C[k]; g = G.setdefault(k, {'firma': c['firma'], 'kraj': c['kraj'], 'url': c['url'], 'lata': {}, 'status': 'nowy'})
        g.update({'firma': c['firma'], 'kraj': c['kraj'], 'url': c['url']})
        if g['status'] in ('dno', 'brak w archiwum') and g.get('sprawdzone_do_roku') == teraz: continue
        t_cel = time.time()
        if 'najstarszy' not in g:
            w = cdx(c, limit=1)
            if w is None:
                g.update(status='błąd archiwum', blad=OSTATNI_BLAD[0], bledow=g.get('bledow', 0) + 1, ostatnio=dt.date.today().isoformat()); continue
            if not w: g.update(status='brak w archiwum', sprawdzone_do_roku=teraz, ostatnio=dt.date.today().isoformat()); continue
            g['najstarszy'] = w[0][0][:8]
        najst = int(g['najstarszy'][:4])
        rok = g.get('nastepny_rok', teraz)
        while rok >= najst and czas_ok(od=t_cel):
            w = cdx(c, **{'from': str(rok), 'to': str(rok), 'limit': 20000})
            if w is None: g.update(status='błąd archiwum', blad=OSTATNI_BLAD[0], bledow=g.get('bledow', 0) + 1); break
            g.pop('blad', None); g['bledow'] = 0
            szcz = [(ts, u) for ts, u in w if SZCZEGOL.search(u) and not SMIECI.search(u)]
            plik = f'raw/archiwum/{k}/{rok}.json.gz'
            os.makedirs(os.path.dirname(plik), exist_ok=True)
            juz = {}
            if os.path.exists(plik): juz = {o['url']: o for o in json.load(gzip.open(plik, 'rt', encoding='utf-8'))['oferty']}
            for ts, u in szcz:
                if not czas_ok(od=t_cel): break
                st = juz.get(u)
                if st and not (st.get('blad') and st.get('prob', 1) < 3): continue   # nieudane strony - do 3 prób w kolejne noce
                r = get(f'https://web.archive.org/web/{ts}id_/{u}')
                time.sleep(1.2)
                if not r or r.status_code != 200 or 'html' not in r.headers.get('content-type', ''): juz[u] = {'url': u, 'ts': ts, 'blad': True, 'prob': (st or {}).get('prob', 0) + 1}; continue
                t, x = tekst(r.text)
                juz[u] = {'url': u, 'ts': ts, 'tytul': t, 'tekst': x}
            json.dump({'cel': k, 'firma': c['firma'], 'kraj': c['kraj'], 'rok': rok, 'adresow_w_archiwum': len(w), 'oferty': list(juz.values())},
                      gzip.open(plik, 'wt', encoding='utf-8'), ensure_ascii=False)
            ok = sum(1 for o in juz.values() if not o.get('blad'))
            jad = sum(1 for o in juz.values() if not o.get('blad') and czy_jadrowa(c['firma'], o))
            g['lata'][str(rok)] = {'adresow': len(w), 'szczegolow': len(szcz), 'pobrane': ok, 'jadrowe': jad}
            if len(juz) < len(szcz) or any(o.get('blad') and o.get('prob', 1) < 3 for o in juz.values()): g['status'] = 'w toku'; break   # rok niedokończony - ciąg dalszy następnej nocy
            rok -= CO_ROK; g['nastepny_rok'] = rok; zrobione += 1
        if rok < najst: g['status'] = 'dno'; g.pop('blad', None); g['sprawdzone_do_roku'] = teraz
        elif g['status'] != 'błąd archiwum': g['status'] = 'w toku'
        g['gleboko_do'] = str(g['nastepny_rok'] + 1) if 'nastepny_rok' in g else None   # najstarszy w pełni przerobiony rok
        g['ofert_razem'] = sum(v['pobrane'] for v in g['lata'].values())
        g['jadrowych_razem'] = sum(v.get('jadrowe', 0) for v in g['lata'].values())
        g['ostatnio'] = dt.date.today().isoformat()
        os.makedirs(os.path.dirname(GL), exist_ok=True)
        json.dump(G, open(GL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    przelicz(G)
    st = {}
    for g in G.values(): st[g['status']] = st.get(g['status'], 0) + 1
    print('archiwum: celów', len(C), '| przerobionych lat', zrobione, '| statusy', st, '| czas', int(time.time() - START), 's')

if __name__ == '__main__': main()
