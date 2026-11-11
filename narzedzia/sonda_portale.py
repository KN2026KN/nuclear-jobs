# Sonda: oficjalne strony instytucji (PAA w naborach KPRM, NCBJ, ZUOP, IChTJ, PGE, ORLEN Synthos) - 10.11.2026
import re, requests
from bs4 import BeautifulSoup
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Accept-Language': 'pl-PL,pl;q=0.9'}
for name, u in [('kprm-paa', 'https://nabory.kprm.gov.pl/wyniki-wyszukiwania?Query=&InstitutionName=Pa%C5%84stwowa+Agencja+Atomistyki'),
                ('kprm-paa2', 'https://nabory.kprm.gov.pl/?id_institution=1020'),
                ('kprm-q', 'https://nabory.kprm.gov.pl/wyniki-wyszukiwania?Query=j%C4%85drow'),
                ('ncbj', 'https://www.ncbj.gov.pl/praca'), ('ncbj2', 'https://www.ncbj.gov.pl/oferty-pracy'),
                ('zuop', 'https://www.zuop.pl/praca'), ('zuop2', 'https://www.zuop.pl/kariera'), ('zuop3', 'https://zuop.pl/'),
                ('ichtj', 'https://www.ichtj.waw.pl/praca'), ('osge', 'https://www.osge.com/kariera'), ('pgeej', 'https://www.pgeenergiajadrowa.pl/kariera')]:
    try:
        r = requests.get(u, headers=UA, timeout=30); s = BeautifulSoup(r.text, 'html.parser')
        links = [(a.get_text(' ', strip=True)[:70], a['href'][:90]) for a in s.select('a[href]') if re.search(r'prac|ofert|nabor|rekrut|kariera|job|ogłosz', a['href'] + a.get_text(), re.I)][:12]
        print('==', name, r.status_code, r.url[:90], len(r.text)); [print('   ', l) for l in links]
    except Exception as e: print('==', name, 'BLAD', e)
