> OD 11.2026 (rozbudowa świat): robot zbiera ok. 20 źródeł z Polski, Europy i świata (lista: docs/ZRODLA_SWIAT.md). Co noc pobiera pełne listy ofert,
> a pełną treść tylko nowych ofert (pamięć `data/cache/znane_<źródło>.json`; rebuild bierze treść starszych ofert z wcześniejszych dni `raw/`).
> Limity: treści 18 min na noc (KP_LIMIT_NOCY), lista jednego źródła 4 min, całe zbieranie przerywane po 24 min; nieskończone treści - następnej nocy.
> Lista niepełna (błąd w połowie, limit) -> wczytanie bez zamykania ofert. Przebieg ręczny: workflow_dispatch „Nocny robot”; test bez bazy i strony: „Test zbierania”.
> Push NIE uruchamia już nocnego robota (od 11.2026).
> Każda oferta dostaje: kraj (ISO), projekt i typ obiektu (kod/kp_projekty.py), język ogłoszenia (langdetect), znacznik tylko_analiza
> (Rosatom, Rosja, Białoruś, Węgry - w bazie tak, na stronie nigdy). Strona /praca (PL, szkic 7194) i wersja EN (szkic, slug nuclear-jobs)
> aktualizowane co noc; publikacja tylko na komendę właściciela. Statystyki: docs/STATYSTYKI.md.

> OD 31.10.2026 zbieraniem zajmuje się robot GitHub Actions (`.github/workflows/zbieranie.yml`, `collect/collect.py`) codziennie ok. 03:40 - 04:40 czasu polskiego, bez komputera. Raport rano (07:52) wysyła zadanie Claude. Poniższa procedura przez Chrome to tryb zapasowy.

# Keura praca baza: procedura codziennego zbierania ofert

Folder: `Pobrane\Keura praca baza\`
- `raw\RRRR-MM-DD\` surowe pliki z danego dnia (nigdy nie usuwamy)
- `kp.sqlite` baza z historią (oferty, wersje treści, obserwacje dzienne, zdarzenia)
- `Keura praca baza - stan RRRR-MM-DD.xlsx` eksport do przeglądania (nowy plik co tydzień, stare zostają)
- `kod\` parsery, słownik, skrypty JS do przeglądarki

## Kroki (Chrome z rozszerzeniem Claude, komputer włączony)
1. Dla każdej firmy otworzyć NOWĄ kartę (Chrome pozwala na 1 automatyczne pobranie na kartę):
   - Bechtel: https://jobs.bechtel.com/us/en/search-results?qcountry=Poland, uruchomić `kod\js\collect_bechtel.js`
   - Westinghouse: https://careers.westinghousenuclear.com/search/?q=&locationsearch=Poland, uruchomić `kod\js\collect_wec.js`
   - PEJ: https://pej.pl/o-nas/kariera/oferty-pracy/, uruchomić `kod\js\collect_pej.js`
   Każdy skrypt ustawia `window.KP.saved=1` po zapisaniu pliku do Pobrane.
2. Skopiować `Pobrane\kp_*_RRRRMMDD.*` do `raw\RRRR-MM-DD\` (kopiowanie, bez usuwania).
3. Wczytać do bazy: `python3 kod/build_day.py raw/RRRR-MM-DD RRRR-MM-DD kp.sqlite`
   - oferta nowa -> zdarzenie „nowa”; zmiana wynagrodzenia, tytułu, trybu lub treści -> „zmiana” + nowa wersja; brak na stronie -> „zamknięta”; powrót -> „wznowiona”.
4. W poniedziałki: `python3 kod/export_xlsx.py kp.sqlite "Keura praca baza - stan RRRR-MM-DD.xlsx"`.
5. Jeśli któraś firma zwróci 0 ofert albo wyraźnie mniej niż poprzednio (>30%), NIE wczytywać jej jako pełnej listy (zamknęłoby to oferty), tylko zgłosić.

## Zasady
- Źródło: wyłącznie oficjalne strony pracodawców.
- Pomijamy nazwiska rekruterów i przełożonych (są w surowych danych Bechtel, nie trafiają do bazy).
- Pełne teksty tylko do analizy wewnętrznej, publikujemy statystykę.
- Słownik wymagań: `kod\kp_tags.py`, zmiany po akceptacji.

> 11.11.2026 - wynagrodzenia: oprócz zakresów parser bierze też pojedynczą kwotę z okresem albo etykietą (np. HPC „Basic PAYE: £29.34/hr”, „Projected annual earnings: £91,854”); dodatki (allowance, bonus, zakwaterowanie) pomijane; kwota „miesięczna” > 25 000 EUR/GBP/USD/CHF/CAD liczona jako roczna. Ofert z płacą: 255 -> 526. Poprzednia wersja: kod/Archiwum/kp_parse_11-11-2026.py.

## Praca na obiekcie jądrowym (12.11.2026)
Oferta z obiektu jądrowego (elektrownia w budowie lub w eksploatacji, SMR, składowisko i likwidacja - np. Vogtle, Hinkley Point C)
liczy się w całości, także stanowiska niejądrowe (administrator IT, księgowość, ochrona). Obiekt rozpoznajemy po tytule i lokalizacji
(w archiwum także po adresie strony, np. `/waynesboro-ga/`), potem po początku treści - słownik `kod/kp_projekty.py`.
Reaktory badawcze, fuzja i instytucje (NCBJ, IAEA) - bez tego wyjątku: tam nadal wymagana treść jądrowa.

## Archiwa - błędy (12.11.2026)
Zapytania CDX stronicowane (resumeKey, paczki po 5000), czas 180 s, do 5 prób z przerwami 30 - 240 s. Gdy cały rok się nie uda,
robot pyta miesiąc po miesiącu. Powód błędu i liczba kolejnych błędów: `blad`, `bledow` w data/archiwum/glebokosc.json.
Nieudane strony ofert - do 3 prób w kolejne noce. Liczba ofert jądrowych przeliczana na końcu każdego przebiegu wg bieżącej reguły.

## Klasy pracodawców i obszary (12.11.2026, decyzje właściciela 1a 2a 3a 4a)
- `data/pracodawcy/klasy.json`: A - firma jądrowa (operator obiektu, właściciel technologii, paliwo, odpady) - każda oferta, także administracja i IT;
  B - energetyka mieszana (EDF, ČEZ, Vattenfall, Fortum, Southern...) - tylko obiekty jądrowe lub treść jądrowa; jądrowe spółki i działy B (NNB, Sizewell C, Edvance) wpisane jako A;
  C - reszta (dostawcy, wykonawcy) - tylko treść jądrowa. Reaktory badawcze, fuzja i instytucje - bez wyjątku.
- Obszar: 16 obszarów, `kod/kp_obszar.py` (tytuł w wielu językach, potem kategoria źródła, przy tytułach ogólnych - początek treści).
- Stanowisko jądrowe / wspierające: `kp_jadro.stanowisko_jadrowe` - wspierające = obszar administracyjny (IT, finanse, HR, prawo, ochrona, zakupy, inne) bez słów jądrowych w tytule;
  staż oceniany po kierunku. Na /praca przełącznik „Tylko stanowiska jądrowe” (domyślnie wyłączony); w statystyce tabela „Obszary i rodzaj stanowiska”.
