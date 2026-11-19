# 19.11.2026: diagnostyka źródeł z pustą listą (pracuj, opg, snn, nda, ukaea) - zapis surowych stron i próbek linków.
# Użycie: python3 narzedzia/diag_zrodla.py <katalog_wyjściowy>
import os, sys, re, json, requests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'collect'))
from siec import S

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
URL = {
    'pracuj_jadrowa': 'https://www.pracuj.pl/praca/j%C4%85drowa;kw',
    'pracuj_nuclear': 'https://www.pracuj.pl/praca/nuclear;kw',
    'opg_search': 'https://jobs.opg.com/search/?q=nuclear&locationsearch=&startrow=0',
    'opg_home': 'https://jobs.opg.com/',
    'snn_p1': 'https://nuclearelectrica.ro/snn/category/joburi/page/1/',
    'snn_cat': 'https://nuclearelectrica.ro/snn/category/joburi/',
    'snn_cariere': 'https://www.nuclearelectrica.ro/cariere/',
    'nda_p1': 'https://ndagroup.careers/current-opportunities/?page=1',
    'nda_home': 'https://ndagroup.careers/current-opportunities/',
    'ukaea': 'https://careers.ukaea.uk/current-vacancies/',
}
wynik = {}
for k, u in URL.items():
    try:
        r = S.get(u, timeout=40, allow_redirects=True)
        t = r.text
        open(os.path.join(OUT, k + '.html'), 'w', encoding='utf-8').write(t[:600000])
        linki = sorted(set(re.findall(r'href="([^"#]{8,300})"', t)))
        wynik[k] = {'status': r.status_code, 'final': r.url, 'bajty': len(t), 'title': (re.search(r'<title[^>]*>(.*?)</title>', t, re.S | re.I) or [None, ''])[1].strip()[:200],
                    'next_data': '__NEXT_DATA__' in t, 'linki_n': len(linki), 'linki_job': [l for l in linki if re.search(r'job|vacan|oferta|post|anunt|cariere|/20\d\d/', l, re.I)][:60],
                    'skrypty_api': sorted(set(re.findall(r'(https?://[^"\'\s]+(?:api|graphql|jobs?)[^"\'\s]{0,120})', t)))[:30]}
    except Exception as e:
        wynik[k] = {'blad': str(e)[:300]}
    print(k, json.dumps({x: y for x, y in wynik[k].items() if x not in ('linki_job', 'skrypty_api')}, ensure_ascii=False), flush=True)
json.dump(wynik, open(os.path.join(OUT, 'wynik.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
