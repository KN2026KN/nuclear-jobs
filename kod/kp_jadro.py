# Czy oferta jest naprawdę związana z energetyką jądrową (10.11.2026, zasada właściciela):
# w opisie obowiązków / wymagań / projektu musi być coś jednoznacznie jądrowego (elektrownia jądrowa, nuclear, ISO 19443, ASME NQA-1, AP1000...).
# Nazwa i opis samej firmy się nie liczą (np. „Narodowe Centrum Badań Jądrowych” w stopce nie robi z księgowej oferty jądrowej).
# Wyjątek: inwestor i wykonawcy projektu pierwszej elektrowni (PEJ, Westinghouse, Bechtel) - każda ich oferta w Polsce dotyczy projektu.
# Wyjątek 2 (12.11.2026, zasada właściciela): praca NA obiekcie jądrowym (elektrownia w budowie / w eksploatacji, SMR,
# składowisko i likwidacja - np. Vogtle, Hinkley Point C) liczy się w całości, także stanowiska niejądrowe (np. administrator IT).
# Obiekt rozpoznajemy po tytule i lokalizacji, potem po początku treści. Reaktory badawcze, fuzja i instytucje - bez tego wyjątku.
import re
from kp_projekty import projekt as _projekt
# 10.11.2026 (po pierwszym przebiegu): sama „ochrona radiologiczna” / „dozymetria” łapała RTG w przychodniach - nie wystarcza.
SLOWA = re.compile(r'elektrown\w* jądrow|energetyk\w* jądrow|obiekt\w* jądrow|bezpieczeństw\w* jądrow|dozor\w* jądrow|dozór jądrow|zezwoleń jądrow|licencj\w* jądrow|'
                   r'technologi\w* jądrow|projekt\w* jądrow|sektor\w* jądrow|branż\w* jądrow|przemysł\w* jądrow|paliw\w* jądrow|reaktor\w*|reactor|nuclear|'
                   r'\bISO\s*19443|NQA[\s-]?1\b|AP\s?-?1000|\bSMR\b|BWRX|atomistyk|Lubiatow|Kopalin|Choczew|odpad\w* promieniotwórcz|wypalon\w* paliw|'
                   # 11.2026: inne języki i nazwy obiektów (oferty z Europy)
                   r'nucl[ée]air|nucleare|nuclear[ăe]|kerntechn|kernkraft|kernenergie|kerncentrale|jadern|jaderné|jadrov|jadrsk|ядрен|ядерн|\bАЕЦ\b|\bCNE\b|ydinvoim|ydinjäte|ydinturv|'
                   r'kärnkraft|kärnteknik|kärnbränsl|branduolin|tuumaj|radioprotection|radiation protection|health physics|'
                   r'Cernavod|Mochovc|Bohunic|Dukovan|Temel[ií]n|Kozlod|Козлодуй|Olkiluoto|Loviis|Forsmark|Ringhals|Oskarshamn|Hinkley|Sizewell|Sellafield|Flamanville|\bITER\b|Barakah|Krško|Krsko', re.I)
MEDYCYNA = re.compile(r'medycyn\w* jądrow|nuclear medicine|elektroradiolog|\bRTG\b|radiologi\w* (lekarsk|stomatolog)|tomograf|rezonans', re.I)
PROJEKT = re.compile(r'Polskie Elektrownie Jądrowe|Westinghouse|Bechtel|Orlen Synthos Green Energy|OSGE', re.I)   # OSGE = inwestor SMR BWRX-300
OBIEKT = ('bud', 'eks', 'smr', 'odp')   # typy obiektów z kp_projekty, na których każda praca się liczy
BEZ = ('about-us', 'about-company', 'benefits', 'offered', 'training-space', 'recruitment-stages', 'work-organization')

def sektor(pracodawca):
    p = pracodawca or ''
    if PROJEKT.search(p): return 'bud'
    if re.search(r'Unieszkodliwiania Odpadów|ZUOP|odpad\w* promien', p, re.I): return 'odp'
    if re.search(r'Agencja Atomistyki|Dozoru Technicznego|\bUDT\b|Ministerstw|Urząd', p, re.I): return 'doz'
    if re.search(r'Instytut|Centrum Badań|Uniwersytet|Politechnik|Akademi|NCBJ|IChTJ|Narodowe Centrum', p, re.I): return 'nau'
    return 'dos'

def jadrowa(pracodawca, tytul, sekcje):
    """sekcje: lista (typ, tekst). Zwraca (True/False, trafienie)."""
    if PROJEKT.search(pracodawca or ''): return True, 'projekt'
    nazwa = re.escape(pracodawca or '###')
    tekst = ' '.join([tytul or ''] + [t for typ, t in sekcje if typ not in BEZ])
    tekst = re.sub(nazwa, ' ', tekst, flags=re.I)
    tekst = re.sub(r'Narodowe(go)? Centrum Badań Jądrowych|Zakład(u)? Unieszkodliwiania Odpadów Promieniotwórczych|Państwow\w+ Agencj\w+ Atomistyki', ' ', tekst, flags=re.I)
    if MEDYCYNA.search(tekst) and not re.search(r'elektrown\w* jądrow|energetyk\w* jądrow|nuclear power|ISO\s*19443|NQA', tekst, re.I): return False, 'medycyna'
    m = SLOWA.search(tekst)
    if m: return True, m.group(0)
    lok = ' '.join(t for typ, t in sekcje if typ in ('lok', 'lokalizacja', 'miejsce', 'location'))
    e, t = _projekt(tytul or '', lok, tekst)
    if e and t in OBIEKT: return True, 'obiekt: ' + e
    return False, ''
