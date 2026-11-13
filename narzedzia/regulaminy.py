# Regulaminy (terms of use) źródeł - czy zabraniają automatycznego zbierania (13.11.2026).
# Dla każdego zbieranego źródła: strona kariery + strona główna domeny -> linki do regulaminu / warunków / informacji prawnych
# -> pobranie -> wycinki zdań o robotach, scrapingu, eksploracji tekstów (TDM), kopiowaniu. Plus znacznik TDM (tdmrep.json, meta tdm-reservation).
# Wynik: data/zrodla/regulaminy.json i regulaminy.md - do oceny przez człowieka (robot nie rozstrzyga).
import json, re, time, datetime as dt
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

S = requests.Session()
S.headers['User-Agent'] = 'Mozilla/5.0 (KeuraNuclearJobs terms check; +https://keura.eu/praca/robot/)'
LINK = re.compile(r'terms|conditions|legal|regulamin|warunki|nota-prawna|nota prawna|mentions|cgu|nutzungsbedingungen|impressum|disclaimer|website-?terms|terms-of-use|terms-of-service|condiciones|termeni|условия|usage|copyright', re.I)
KLAUZULA = re.compile(r'[^.\n]{0,220}\b(scrap\w*|crawl\w*|spider\w*|robot\w*|bot\b|bots\b|automat\w*|data mining|text and data mining|TDM|harvest\w*|extract\w*|reproduc\w*|eksploracj\w*|zautomatyzowan\w*|pobierani\w*|kopiowani\w*|aspiration|extraction|reproduction|automatis\w*|Vervielfältig\w*|automatisiert\w*|frameworks?|framing)\b[^.\n]{0,260}', re.I)

def get(u):
    try:
        r = S.get(u, timeout=25, allow_redirects=True)
        return r if r.status_code == 200 and 'html' in r.headers.get('content-type', '') else None
    except requests.RequestException:
        return None

def linki_regulaminu(url):
    out = []
    for start in (url, '{0.scheme}://{0.netloc}/'.format(urlparse(url))):
        r = get(start)
        if not r: continue
        soup = BeautifulSoup(r.text, 'html.parser')
        for m in soup.find_all('meta', attrs={'name': re.compile('tdm', re.I)}):
            out.append(('META ' + m.get('name', '') + '=' + m.get('content', ''), None))
        for a in soup.find_all('a', href=True):
            t = (a.get_text(' ', strip=True) + ' ' + a['href'])
            if LINK.search(t) and not a['href'].startswith(('mailto:', 'tel:', '#')):
                out.append((a.get_text(' ', strip=True)[:60], urljoin(r.url, a['href'])))
        time.sleep(1)
    seen = set(); w = []
    for t, u in out:
        if u is None: w.append((t, None)); continue
        if u in seen: continue
        seen.add(u); w.append((t, u))
    return w[:8]

def main():
    src = json.load(open('data/zrodla/robots.json', encoding='utf-8'))['adresy']
    zb = {}
    for x in src:
        if x['rodzaj'] != 'zbierane': continue
        zb.setdefault(urlparse(x['url']).netloc, x)
    wynik = []
    for host, x in zb.items():
        rec = {'host': host, 'zrodlo': x['pracodawca'] or x['zrodlo'], 'url': x['url'], 'tdmrep': None, 'strony': []}
        try:
            r = S.get(f'https://{host}/.well-known/tdmrep.json', timeout=15)
            if r.status_code == 200 and r.text.strip().startswith('['): rec['tdmrep'] = r.text[:500]
        except requests.RequestException: pass
        for tytul, u in linki_regulaminu(x['url']):
            if u is None: rec['strony'].append({'tytul': tytul, 'url': None, 'klauzule': []}); continue
            r = get(u); time.sleep(1)
            if not r: continue
            tekst = BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)
            kl = [m.group(0).strip() for m in KLAUZULA.finditer(tekst)][:12]
            rec['strony'].append({'tytul': tytul, 'url': u, 'klauzule': kl})
        wynik.append(rec); print(host, len(rec['strony']), sum(len(s['klauzule']) for s in rec['strony']))
    json.dump({'data': dt.date.today().isoformat(), 'zrodla': wynik}, open('data/zrodla/regulaminy.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open('data/zrodla/regulaminy.md', 'w', encoding='utf-8') as f:
        f.write(f'# Regulaminy źródeł - wycinki (robot, {dt.date.today().isoformat()}) - do oceny\n\n')
        for r in wynik:
            f.write(f"## {r['zrodlo']} ({r['host']})\n")
            if r['tdmrep']: f.write(f"- tdmrep.json: `{r['tdmrep'][:200]}`\n")
            for s in r['strony']:
                f.write(f"- {s['tytul']}: {s['url']}\n")
                for k in s['klauzule']: f.write(f"  - {k[:400]}\n")
            f.write('\n')

if __name__ == '__main__':
    main()
