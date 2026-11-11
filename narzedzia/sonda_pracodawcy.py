# Sonda potencjalnych pracodawców (11.11.2026): strona główna -> link do kariery -> platforma i liczba linków ofert. Tylko GET.
# Użycie: python3 narzedzia/sonda_pracodawcy.py data/pracodawcy/kandydaci.tsv data/pracodawcy/sonda.json
import sys, os, json, re, time, urllib.parse, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from bs4 import BeautifulSoup
from sonda_swiat import PLATF, UA
KAR = re.compile(r'career|karier|kariera|praca-w|pracuj|jobs?\b|vacanc|emploi|recrut|carri[eè]re|stellen|karriere|jobb|ura[a]?|työpaik|rekryt|cariere|kariér|kari[eé]r|empleo|trabaja|lavora|vacature|werken|kari[eé]ra|работа|кариер|join-us|join us|work-with-us|work with us|opportunit|offres', re.I)
JOB = re.compile(r'/(job|jobs|offre|offer|vacanc|position|stelle|requisition|posting|oferta|ogloszenie|nabor|praca)[/_-]?', re.I)
S = requests.Session(); S.headers.update(UA); last = {}
def get(u):
    d = urllib.parse.urlparse(u).netloc
    w = 1.2 - (time.time() - last.get(d, 0))
    if w > 0: time.sleep(w)
    try: return S.get(u, timeout=30, allow_redirects=True)
    finally: last[d] = time.time()
def plat(h, u): return [k for k, rx in PLATF.items() if k != 'elementor/wp' and re.search(rx, h + ' ' + u, re.I)]
wyn = []
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8'), delimiter='\t'))
for r in rows:
    o = dict(r)
    try:
        x = get(r['www']); o['status'] = x.status_code; h = x.text if 'html' in x.headers.get('content-type', '') else ''
        kand = []
        for a in BeautifulSoup(h, 'html.parser').find_all('a', href=True):
            t = a.get_text(' ', strip=True)[:60]; hr = urllib.parse.urljoin(x.url, a['href'])
            if hr.startswith('http') and (KAR.search(t) or KAR.search(urllib.parse.urlparse(hr).path + urllib.parse.urlparse(hr).netloc)): kand.append((hr, t))
        kand = sorted(set(kand), key=lambda k: (0 if re.search(r'job|vacanc|offre|oferty|stellen|career', k[0], re.I) else 1, len(k[0])))
        o['kariera_kandydaci'] = [k[0] for k in kand[:5]]
        o['platforma'] = plat(h, x.url)
        if kand:
            k = get(kand[0][0]); kh = k.text if k.status_code == 200 else ''
            o['kariera'] = k.url; o['kariera_status'] = k.status_code
            o['platforma'] = sorted(set(o['platforma'] + plat(kh, k.url)))
            o['linki_ofert'] = len({a['href'] for a in BeautifulSoup(kh, 'html.parser').find_all('a', href=True) if JOB.search(a['href'])})
    except Exception as e:
        o['blad'] = str(e)[:150]
    wyn.append(o); print(o['kraj'], o['nazwa'][:40], o.get('status'), o.get('kariera', '')[:70], o.get('platforma'), o.get('linki_ofert'), o.get('blad', ''), flush=True)
json.dump(wyn, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
