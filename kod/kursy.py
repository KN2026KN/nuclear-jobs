# Kursy walut i parytet siły nabywczej do porównań wynagrodzeń (13.11.2026).
# - Kursy: EBC (euro foreign exchange reference rates, codziennie), brakujące waluty - Bank Światowy PA.NUS.FCRF (średni kurs roczny).
# - Parytet siły nabywczej (PPP): Bank Światowy PA.NUS.PPP - ile jednostek waluty lokalnej kosztuje koszyk wart 1 dolar
#   międzynarodowy; strefa euro jako punkt odniesienia (kod EMU).
# - Godziny pracy w roku - do przeliczenia stawek godzinowych (przyjęte założenia, pokazywane na stronie).
# Wynik: data/kursy.json (dane publiczne, bez informacji o ofertach). Przy błędzie sieci zostaje poprzedni plik.
import json, os, sys, datetime as dt, xml.etree.ElementTree as ET
import requests

S = requests.Session(); S.headers['User-Agent'] = 'keura-robot/1.0 (+https://keura.eu)'
WYJ = 'data/kursy.json'

# kraj -> waluta (kraje ze źródeł ofert; uzupełniać przy nowych krajach)
WALUTA = {'PL': 'PLN', 'GB': 'GBP', 'US': 'USD', 'CA': 'CAD', 'CH': 'CHF', 'SE': 'SEK', 'NO': 'NOK', 'DK': 'DKK', 'CZ': 'CZK',
          'HU': 'HUF', 'RO': 'RON', 'BG': 'BGN', 'TR': 'TRY', 'JP': 'JPY', 'KR': 'KRW', 'CN': 'CNY', 'IN': 'INR', 'AE': 'AED',
          'SA': 'SAR', 'ZA': 'ZAR', 'AU': 'AUD', 'NZ': 'NZD', 'BR': 'BRL', 'AR': 'ARS', 'MX': 'MXN', 'UA': 'UAH', 'RU': 'RUB',
          'BY': 'BYN', 'KZ': 'KZT', 'UZ': 'UZS', 'EG': 'EGP', 'BD': 'BDT', 'PK': 'PKR', 'AM': 'AMD', 'IR': 'IRR', 'ID': 'IDR',
          'PH': 'PHP', 'VN': 'VND', 'SG': 'SGD', 'TW': 'TWD', 'IL': 'ILS', 'GH': 'GHS', 'KE': 'KES', 'NG': 'NGN', 'RS': 'RSD'}
STREFA_EURO = ['AT', 'BE', 'HR', 'CY', 'EE', 'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PT', 'SK', 'SI', 'ES']
for k in STREFA_EURO: WALUTA[k] = 'EUR'

# godziny pracy w roku przy pełnym etacie - założenie do przeliczenia stawek godzinowych (tydzień pracy × 52)
GODZINY = {'US': 2080, 'CA': 2080, 'GB': 1950, 'IE': 1950, 'PL': 2000, 'FR': 1607, 'DE': 1720, 'AT': 1720, 'CH': 1900,
           'SE': 1800, 'FI': 1800, 'NO': 1750, 'DK': 1700, 'NL': 1750, 'BE': 1750, 'IT': 1800, 'ES': 1800, 'CZ': 2000,
           'SK': 2000, 'RO': 2000, 'BG': 2000, 'HU': 2000, '_': 2000}

def ebc():
    r = S.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml', timeout=30); r.raise_for_status()
    root = ET.fromstring(r.content); ns = {'e': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
    kursy = {'EUR': 1.0}; data = None
    for c in root.iter():
        if c.get('time'): data = c.get('time')
        if c.get('currency'): kursy[c.get('currency')] = float(c.get('rate'))
    return data, kursy   # 1 EUR = kursy[waluta]

def bank_swiatowy(wskaznik):
    r = S.get(f'https://api.worldbank.org/v2/country/all/indicator/{wskaznik}', params={'format': 'json', 'per_page': 20000, 'mrnev': 1}, timeout=60)
    r.raise_for_status(); d = r.json()
    w = {}
    for x in d[1] or []:
        if x.get('value') is not None:
            w[x['country']['id']] = (x['value'], x['date'])          # id = kod ISO2 albo kod grupy (EMU itp.)
    # kody ISO3 strefy euro w danych WB: EMU (Euro area)
    for x in d[1] or []:
        if x.get('countryiso3code') == 'EMU' and x.get('value') is not None: w['EMU'] = (x['value'], x['date'])
    return w

def main():
    stary = json.load(open(WYJ, encoding='utf-8')) if os.path.exists(WYJ) else {}
    wynik = dict(stary)
    try:
        data, k = ebc(); wynik['ebc'] = {'data': data, 'kursy': k, 'zrodlo': 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html'}
    except Exception as e:
        print('EBC: błąd', type(e).__name__, '- zostaje poprzedni kurs')
    try:
        ppp = bank_swiatowy('PA.NUS.PPP'); fx = bank_swiatowy('PA.NUS.FCRF')
        wynik['ppp'] = {'jednostka': 'waluta lokalna za 1 dolar międzynarodowy', 'wskaznik': 'PA.NUS.PPP',
                        'zrodlo': 'https://data.worldbank.org/indicator/PA.NUS.PPP', 'kraje': {k: {'ppp': v[0], 'rok': v[1]} for k, v in ppp.items()}}
        # strefa euro jako całość: Bank Światowy nie podaje agregatu w tym wskaźniku - mediana PPP krajów strefy euro
        import statistics
        ez = [ppp[k][0] for k in STREFA_EURO if k in ppp]
        if ez and 'EMU' not in ppp: ppp['EMU'] = (round(statistics.median(ez), 6), max(ppp[k][1] for k in STREFA_EURO if k in ppp))
        wynik['ppp'] = {'jednostka': 'waluta lokalna za 1 dolar międzynarodowy', 'wskaznik': 'PA.NUS.PPP',
                        'zrodlo': 'https://data.worldbank.org/indicator/PA.NUS.PPP', 'kraje': {k: {'ppp': v[0], 'rok': v[1]} for k, v in ppp.items()},
                        'EMU': 'mediana krajów strefy euro'}
        wynik['wb_kurs'] = {'wskaznik': 'PA.NUS.FCRF', 'jednostka': 'waluta lokalna za 1 USD (średnia roczna)', 'kraje': {k: {'kurs': v[0], 'rok': v[1]} for k, v in fx.items()}}
    except Exception as e:
        print('Bank Światowy: błąd', type(e).__name__, '- zostają poprzednie dane PPP')
    wynik['waluty_krajow'] = WALUTA; wynik['godziny_rok'] = GODZINY; wynik['odswiezone'] = dt.date.today().isoformat()
    # kurs EUR dla walut spoza tabeli EBC: przez USD z Banku Światowego
    try:
        k = wynik['ebc']['kursy']; usd = k['USD']
        for kraj, wal in WALUTA.items():
            if wal not in k and kraj in wynik.get('wb_kurs', {}).get('kraje', {}):
                k[wal] = wynik['wb_kurs']['kraje'][kraj]['kurs'] * usd
                wynik.setdefault('kursy_przez_usd', []).append(wal)
    except KeyError: pass
    os.makedirs('data', exist_ok=True)
    json.dump(wynik, open(WYJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print('kursy:', wynik.get('ebc', {}).get('data'), 'walut', len(wynik.get('ebc', {}).get('kursy', {})), '| PPP krajów', len(wynik.get('ppp', {}).get('kraje', {})))

if __name__ == '__main__':
    main()
