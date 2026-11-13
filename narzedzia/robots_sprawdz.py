# Sprawdzenie robots.txt wszystkich źródeł (13.11.2026, decyzja właściciela: zbieramy tylko tam, gdzie wolno).
# Wejście: adresy z collect/*.py, data/pracodawcy/podlaczone.json i strony kariery z data/pracodawcy/sonda.json.
# Wyjście: data/zrodla/robots.json (+ robots.md - tabela do przeglądu).
# Użycie (na runnerze): python3 narzedzia/robots_sprawdz.py
import json, os, re, glob, time, datetime as dt
from urllib.parse import urlparse
from urllib import robotparser
import requests

NASZ_UA = 'KeuraNuclearJobs'   # nazwa, pod którą robot będzie się przedstawiał
S = requests.Session()
S.headers['User-Agent'] = 'KeuraNuclearJobs/1.0 (+https://keura.eu/praca/robot/)'

def adresy():
    w = []
    for f in glob.glob('collect/*.py'):
        for u in set(re.findall(r"https?://[A-Za-z0-9./_%?=&:+-]+", open(f, encoding='utf-8').read())):
            w.append({'zrodlo': os.path.basename(f), 'pracodawca': '', 'kraj': '', 'url': u, 'rodzaj': 'zbierane'})
    try:
        for c in json.load(open('data/pracodawcy/podlaczone.json', encoding='utf-8')):
            w.append({'zrodlo': 'pr_' + c['klucz'], 'pracodawca': c['pracodawca'], 'kraj': c.get('kraj', ''), 'url': c['url'], 'rodzaj': 'zbierane'})
    except FileNotFoundError: pass
    try:
        for k in json.load(open('data/pracodawcy/sonda.json', encoding='utf-8')):
            if k.get('kariera'):
                w.append({'zrodlo': 'sonda', 'pracodawca': k['nazwa'], 'kraj': k.get('kraj', ''), 'url': k['kariera'], 'rodzaj': 'kandydat'})
    except FileNotFoundError: pass
    return w

def main():
    lista = adresy(); cache = {}; wynik = []
    for a in lista:
        p = urlparse(a['url']); host = f'{p.scheme}://{p.netloc}'
        if host not in cache:
            rp = robotparser.RobotFileParser(); kod = None; tresc = ''
            try:
                r = S.get(host + '/robots.txt', timeout=25); kod = r.status_code
                tresc = r.text if r.status_code == 200 and 'html' not in r.headers.get('content-type', '') else ''
            except requests.RequestException as e:
                kod = type(e).__name__
            rp.parse(tresc.splitlines())
            cache[host] = (rp, kod, tresc)
            time.sleep(0.7)
        rp, kod, tresc = cache[host]
        sciezka = a['url']
        nasz = rp.can_fetch(NASZ_UA, sciezka) if tresc else True
        ogolny = rp.can_fetch('*', sciezka) if tresc else True
        cd = rp.crawl_delay(NASZ_UA) or rp.crawl_delay('*') if tresc else None
        if kod in (401, 403) : stan = 'robots.txt zablokowany (%s) - ręcznie' % kod
        elif not isinstance(kod, int): stan = 'brak odpowiedzi - ręcznie'
        elif not tresc: stan = 'brak robots.txt - wolno'
        elif nasz and ogolny: stan = 'wolno'
        elif nasz and not ogolny: stan = 'wolno nam, zakaz dla wszystkich innych - ręcznie'
        else: stan = 'zakaz'
        wynik.append(dict(a, host=host, robots_http=kod, wolno_nam=nasz, wolno_wszystkim=ogolny, crawl_delay=cd, stan=stan))
    os.makedirs('data/zrodla', exist_ok=True)
    json.dump({'data': dt.date.today().isoformat(), 'adresy': wynik}, open('data/zrodla/robots.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open('data/zrodla/robots.md', 'w', encoding='utf-8') as f:
        f.write(f'# robots.txt źródeł - {dt.date.today().isoformat()}\n\n| Rodzaj | Pracodawca / źródło | Adres | robots.txt | Stan | Crawl-delay |\n|---|---|---|---|---|---|\n')
        for x in sorted(wynik, key=lambda x: (x['stan'] == 'wolno', x['rodzaj'], x['pracodawca'] or x['zrodlo'])):
            f.write(f"| {x['rodzaj']} | {x['pracodawca'] or x['zrodlo']} | {x['url'][:90]} | {x['robots_http']} | {x['stan']} | {x['crawl_delay'] or ''} |\n")
    from collections import Counter
    print(Counter((x['rodzaj'], x['stan']) for x in wynik))

if __name__ == '__main__':
    main()
