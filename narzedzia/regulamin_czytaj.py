# Wypisuje (tylko do logu, bez zapisu w repo) akapity regulaminów dotyczące robotów, kopiowania i baz danych.
import sys, re, requests
from bs4 import BeautifulSoup
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0 (KeuraNuclearJobs terms check; +https://keura.eu/praca/robot/)'
KL = re.compile(r'scrap|crawl|spider|robot|automat|data mining|harvest|extract|reproduc|copy|copie|kopiow|pobier|eksploracj|baz\w* danych|database|framing|deep.?link|aggregat|agregat|republish|commercial|komercyj|API|third part|partner', re.I)
for u in sys.argv[1:]:
    print('\n=====', u)
    try:
        r = S.get(u, timeout=30)
        print('HTTP', r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        for t in soup(['script', 'style', 'nav', 'header', 'footer']): t.decompose()
        akap = [p.get_text(' ', strip=True) for p in soup.find_all(['p', 'li', 'td', 'h2', 'h3'])]
        n = 0
        for a in akap:
            if 30 < len(a) < 1500 and KL.search(a):
                print('-', a[:900]); n += 1
            if n >= 40: break
        if n == 0: print('(brak akapitów z kluczowymi słowami; długość tekstu', len(soup.get_text()), ')')
    except Exception as e:
        print('błąd', e)
