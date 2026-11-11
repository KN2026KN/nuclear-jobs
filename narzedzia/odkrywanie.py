# Rozpoznanie struktury źródeł + test autoryzacji WordPress (bez wypisywania sekretów)
import requests, json, os, re
from bs4 import BeautifulSoup
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36','Accept-Language':'pl-PL,pl;q=0.9,en;q=0.8'}
os.makedirs('data/log/odkrywanie',exist_ok=True)
def save(n,t): open(f'data/log/odkrywanie/{n}.txt','w',encoding='utf-8').write(t[:60000])
def links(u,flt=None):
    r=requests.get(u,headers=UA,timeout=40); s=BeautifulSoup(r.text,'html.parser')
    L=[(a.get_text(' ',strip=True)[:80],a.get('href')) for a in s.select('a[href]')]
    if flt: L=[x for x in L if re.search(flt,(x[0] or '')+' '+(x[1] or ''),re.I)]
    return r.status_code, L
# PEJ menu
st,L=links('https://pej.pl/',r'dostaw|przetarg|zam[oó]wie|ogłosze|aktualno|media|komunikat')
save('pej_menu',f'{st}\n'+'\n'.join(f'{a} | {b}' for a,b in dict.fromkeys(L)))
# PEJ aktualnosci struktura
r=requests.get('https://pej.pl/dla-mediow/aktualnosci/',headers=UA,timeout=40); s=BeautifulSoup(r.text,'html.parser')
arts=[(a.get_text(' ',strip=True)[:100],a['href']) for a in s.select('article a[href], .elementor-post a[href], h2 a[href], h3 a[href]')]
save('pej_aktualnosci','\n'.join(f'{a} | {b}' for a,b in dict.fromkeys(arts)))
# NQSA lista
for n,u in [('nqsa_lista','https://www.nqsa.org/iso19443-certified-organizations'),('nqsa_stat','https://www.nqsa.org/statistics')]:
    r=requests.get(u,headers=UA,timeout=40); s=BeautifulSoup(r.text,'html.parser')
    ifr=[i.get('src') for i in s.select('iframe')]
    tbl=s.select('table')
    txt=s.get_text('\n',strip=True)
    save(n,f'status {r.status_code}\niframes {ifr}\ntables {len(tbl)}\nforms {[f.get("action") for f in s.select("form")]}\nscripts {[x.get("src") for x in s.select("script[src]")][:20]}\n----\n{txt[:20000]}')
# gov.pl energia wiadomosci struktura
for n,u in [('gov_energia','https://www.gov.pl/web/energia/wiadomosci'),('gov_polskiatom','https://www.gov.pl/web/polski-atom/wiadomosci'),('paa','https://www.gov.pl/web/paa/wiadomosci')]:
    st,L=links(u,r'/web/(energia|polski-atom|paa)/[a-z0-9-]{12,}')
    save(n,f'{st}\n'+'\n'.join(f'{a} | {b}' for a,b in dict.fromkeys(L)))
for n,u in [('wec_news','https://info.westinghousenuclear.com/news'),('bechtel_news','https://www.bechtel.com/press-releases/'),('ppj','https://polskaplatformajadrowa.pl/')]:
    st,L=links(u,r'poland|polsk|news|press|aktual|202[56]')
    save(n,f'{st}\n'+'\n'.join(f'{a} | {b}' for a,b in list(dict.fromkeys(L))[:150]))
# TED: test zapytań
q={'ted_19443':'FT~"ISO 19443"','ted_nqa':'FT~"NQA-1"','ted_nuclear_pl':'FT~"jądrow*" AND buyer-country=POL'}
res={}
for n,qq in q.items():
    try:
        r=requests.post('https://api.ted.europa.eu/v3/notices/search',json={'query':qq,'fields':['publication-number','notice-title','buyer-name','publication-date','buyer-country'],'limit':10,'scope':'ALL'},headers=UA,timeout=40)
        j=r.json(); res[n]={'status':r.status_code,'total':j.get('totalNoticeCount'),'ex':[(x.get('publication-number'),str(x.get('notice-title'))[:150],str(x.get('buyer-name'))[:80],x.get('publication-date')) for x in j.get('notices',[])[:10]],'err':str(j)[:300] if r.status_code!=200 else ''}
    except Exception as e: res[n]={'err':str(e)}
save('ted',json.dumps(res,ensure_ascii=False,indent=1))
# e-Zamówienia
r=requests.get('https://ezamowienia.gov.pl/mo-board/api/v1/Board/Search?publicationDateFrom=2026-09-01&SearchPhrase=j%C4%85drow&PageSize=20',headers=UA,timeout=40)
save('ezamowienia',r.text[:30000])
# WordPress - autoryzacja (tylko odczyt)
u=os.environ.get('WP_USER'); p=os.environ.get('WP_APP_PASSWORD')
if u and p:
    r=requests.get('https://keura.eu/wp-json/wp/v2/posts/3912?context=edit&_fields=id,modified,status,title',auth=(u,p),headers=UA,timeout=40)
    save('wp_auth',f'status {r.status_code} ctype {r.headers.get("content-type")} body {r.text[:300]}')
    r=requests.get('https://keura.eu/wp-json/wp/v2/users/me?context=edit&_fields=id,roles,name',auth=(u,p),headers=UA,timeout=40)
    save('wp_me',f'status {r.status_code} body {r.text[:300]}')
else:
    save('wp_auth','brak sekretów')
