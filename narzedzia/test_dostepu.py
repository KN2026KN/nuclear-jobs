# Test: które źródła są osiągalne z serwerów GitHub
import requests, json, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36','Accept-Language':'pl-PL,pl;q=0.9,en;q=0.8'}
U={
 'keura_home':'https://keura.eu/',
 'keura_rest_post':'https://keura.eu/wp-json/wp/v2/posts/3912?_fields=id,modified,link',
 'keura_rest_pages':'https://keura.eu/wp-json/wp/v2/pages?per_page=5&_fields=id,link,modified',
 'baptysci':'https://baptysci-wejherowo.pl/',
 'pej_news':'https://pej.pl/dla-mediow/aktualnosci/',
 'pej_przetargi':'https://pej.pl/dla-dostawcow/przetargi/',
 'pej_plan':'https://pej.pl/dla-dostawcow/informacja-o-planowanych-zamowieniach-pej/',
 'gov_energia':'https://www.gov.pl/web/energia/wiadomosci',
 'gov_polskiatom':'https://www.gov.pl/web/polski-atom',
 'paa':'https://www.gov.pl/web/paa/wiadomosci',
 'sejm_mp':'https://api.sejm.gov.pl/eli/acts/MP/2026',
 'sejm_du':'https://api.sejm.gov.pl/eli/acts/DU/2026',
 'ec_press':'https://ec.europa.eu/commission/presscorner/api/search?language=en&text=nuclear%20poland&pagesize=5',
 'wec_news':'https://info.westinghousenuclear.com/news',
 'bechtel_news':'https://www.bechtel.com/press-releases/',
 'ppj':'https://polskaplatformajadrowa.pl/',
 'nqsa':'https://www.nqsa.org/',
 'ted_api':'https://api.ted.europa.eu/v3/notices/search',
 'ezamowienia':'https://ezamowienia.gov.pl/mo-board/api/v1/Board/Search?publicationDateFrom=2026-10-01&SearchPhrase=j%C4%85drow',
 'bzp_old':'https://ezamowienia.gov.pl/mo-client-board/bzp/list',
}
out={}
for k,u in U.items():
    t=time.time()
    try:
        if k=='ted_api':
            r=requests.post(u,json={'query':'FT~"ISO 19443"','fields':['publication-number','notice-title'],'limit':5},headers=UA,timeout=40)
        else:
            r=requests.get(u,headers=UA,timeout=40)
        body=r.text[:300].replace('\n',' ')
        out[k]={'status':r.status_code,'len':len(r.text),'ctype':r.headers.get('content-type','')[:40],'s':round(time.time()-t,1),'waf':any(x in r.text[:3000] for x in ['Proszę czekać','Секундочку','imunify','captcha','Just a moment']),'head':body[:160]}
    except Exception as e:
        out[k]={'err':str(e)[:200]}
    print(k,out[k],flush=True)
json.dump(out,open('data/log/test_dostepu.json','w'),ensure_ascii=False,indent=1)
