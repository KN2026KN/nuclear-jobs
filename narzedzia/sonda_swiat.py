# Sonda stron kariery (11.2026): odpowiada? jaka platforma? ile linków do ofert? Zapisuje skrót HTML do analizy offline.
# Tylko odczyt (GET), bez formularzy i logowania. Uruchamiane na runnerze GitHub (.github/workflows/sonda_swiat.yml).
# Użycie: python3 narzedzia/sonda_swiat.py <plik_listy.json> <folder_wyniku>
import sys, os, json, re, time, gzip, urllib.parse
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.9,pl;q=0.8,fr;q=0.7'}
PLATF = {'workday': r'myworkdayjobs|workday', 'successfactors': r'successfactors|jobs2web|sapsf|career\d*\.sapsf|rmkcdn', 'taleo': r'taleo',
         'oracle-hcm': r'oraclecloud\.com/hcmUI|CandidateExperience', 'smartrecruiters': r'smartrecruiters', 'teamtailor': r'teamtailor',
         'greenhouse': r'greenhouse\.io', 'lever': r'lever\.co', 'icims': r'icims', 'phenom': r'phenompeople|phApp\.ddo', 'recruitee': r'recruitee',
         'jobvite': r'jobvite', 'cornerstone': r'csod\.com|cornerstoneondemand', 'avature': r'avature', 'beetween': r'beetween', 'talentsoft': r'talent-soft|talentsoft|cegid',
         'softgarden': r'softgarden', 'personio': r'personio', 'eightfold': r'eightfold', 'erecruiter': r'erecruiter', 'elementor/wp': r'wp-content'}
JOBLINK = re.compile(r'(job|offre|offer|vacanc|career|kariera|praca|nabor|stanowisk|position|requisition|poste|emploi|stelle|työpaik|pozic|volno|cariere|ponuk)', re.I)

def main():
    lst = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    S = requests.Session(); S.headers.update(UA); wyn = {}; last = {}
    for nazwa, url in lst.items():
        dom = urllib.parse.urlparse(url).netloc
        if time.time() - last.get(dom, 0) < 1.2: time.sleep(1.2)
        r = {'url': url}
        try:
            t = time.time(); x = S.get(url, timeout=35, allow_redirects=True); last[dom] = time.time()
            body = x.text if 'text' in x.headers.get('content-type', '') or 'json' in x.headers.get('content-type', '') else ''
            r.update(status=x.status_code, final=x.url, ct=x.headers.get('content-type', '')[:60], bytes=len(x.content), s=round(time.time() - t, 1))
            r['platformy'] = [k for k, rx in PLATF.items() if re.search(rx, body + ' ' + x.url, re.I)]
            m = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I); r['title'] = re.sub(r'\s+', ' ', m.group(1)).strip()[:120] if m else ''
            links = re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', body, re.S | re.I)
            jl = []
            for h, txt in links:
                txt = re.sub(r'<[^>]+>|\s+', ' ', txt).strip()
                if JOBLINK.search(h) and len(txt) > 8: jl.append([urllib.parse.urljoin(x.url, h)[:200], txt[:90]])
            r['linki_ofert'] = len({h for h, _ in jl}); r['przyklady'] = jl[:25]
            r['json_api'] = sorted(set(re.findall(r'["\'](/[^"\'\s]*(?:api|rest|search|jobs?)[^"\'\s]*)["\']', body)))[:15]
            gzip.open(os.path.join(out, nazwa + '.html.gz'), 'wt', encoding='utf-8').write(body[:600000])
        except Exception as e:
            r['err'] = str(e)[:200]
        wyn[nazwa] = r
        print(nazwa, r.get('status'), r.get('bytes'), r.get('platformy'), r.get('linki_ofert'), r.get('err', ''), flush=True)
    json.dump(wyn, open(os.path.join(out, 'wynik.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
