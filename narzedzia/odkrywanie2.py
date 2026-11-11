import requests, re, json, os
from bs4 import BeautifulSoup
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36'}
os.makedirs('data/log/odkrywanie',exist_ok=True); out=[]
for u in ['https://www.gov.pl/web/polski-atom','https://www.gov.pl/web/polski-atom/wiadomosci','https://www.gov.pl/web/paa','https://www.gov.pl/web/paa/wiadomosci','https://www.gov.pl/web/paa/aktualnosci','https://www.nqsa.org/iso19443-certified-organizations']:
    r=requests.get(u,headers=UA,timeout=40); s=BeautifulSoup(r.text,'html.parser')
    out.append(f'### {u} {r.status_code} {r.url} title={s.title.string if s.title else ""}')
    for a in s.select('a[href]'):
        t=a.get_text(' ',strip=True)[:70]; h=a['href']
        if re.search(r'polski-atom|/paa|onusis|database|nqsa',h,re.I): out.append(f'{t} | {h}')
r=requests.get('https://ec.europa.eu/commission/presscorner/api/search?language=en&text=nuclear%20Poland&pagesize=3',headers=UA,timeout=40)
out.append('### EC '+r.text[:3000])
open('data/log/odkrywanie/gov2.txt','w').write('\n'.join(out))
