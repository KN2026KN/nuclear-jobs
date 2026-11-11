# Źródła ofert - świat (stan 10.11.2026)

Decyzje właściciela (10.11.2026): cały świat, priorytet Europa; bez Rosatomu i spółek, Rosji, Białorusi i Węgier (Paks II też) - takie oferty
trafiają do bazy ze znacznikiem `tylko_analiza` i nigdy na stronę; nic płatnego; link do strony pracodawcy, portal tylko gdy pracodawca sam tam publikuje.

Sondy: `narzedzia/sonda_swiat.py` + `.github/workflows/sonda_swiat.yml` (runner GitHub, tylko GET), wyniki i skróty HTML w `data/log/sonda/lista1..3/`.
Sesje Claude w chmurze nie mają dostępu do stron kariery (proxy 403) - każdą sondę i zbieranie uruchamiamy na runnerze GitHub.

## Podłączone (collect/collect.py, collect/swiat.py)
| Źródło (klucz) | Kraj | Platforma | Ofert na liście (10.11) | Filtr | Uwagi |
|---|---|---|---|---|---|
| Bechtel (`bechtel`) | świat | Phenom | ok. 1 110 (cała lista) | Polska + oferty jądrowe | lista co noc, treść tylko nowych kandydatów |
| Westinghouse (`wec`) | świat | SuccessFactors RMK | ok. 1 111 | wszystkie | dawniej tylko Polska |
| PEJ (`pej`) | PL | WordPress | 7 | wszystkie | bez zmian |
| pracuj.pl (`pracuj`) | PL | Next.js | 25 znalezionych / 13 jądrowych | `kp_jadro` | 14 słów kluczowych („ochrona radiologiczna” usunięta 11.11.2026) |
| NCBJ (`ncbj`) | PL | Drupal | 7 | `kp_jadro` | bez zmian |
| Nabory KPRM (`kprm`) | PL | własna | PAA + branża „atomistyka” + fraza „jądrow” | PAA wszystkie, reszta `kp_jadro` | służba cywilna (PAA, ministerstwa) |
| CLOR (`clor`) | PL | Joomla, ogłoszenia PDF | 3 | wszystkie | bez pełnej treści (PDF) |
| Hinkley Point C Jobs Service (`hpc`) | GB | SuccessFactors RMK (kafelki) | ok. 100 | wszystkie | EDF i partnerzy HPC |
| Sizewell C (`szc`) | GB | SuccessFactors RMK | 29 | wszystkie | |
| EDF Energy (`edfuk`) | GB | strona „-jid-” | 36 | `kp_jadro` | |
| Orano (`orano`) | FR | Avature | 787 | wszystkie | 12 na stronę |
| CEA (`cea`) | FR | Talentsoft | 836 | `kp_jadro` (FR: nucléaire…) | duża lista, treść stopniowo |
| ITER Organization (`iter`) | FR | SAP SuccessFactors | ok. 15 | wszystkie | |
| Kozloduy NPP (`kznpp`) | BG | własna | 6 | wszystkie | BG |
| Nuclearelectrica (`snn`) | RO | WordPress | 42 | wszystkie | RO |
| ČEZ (`cez`) | CZ | jobs.cz (kdejinde.jobs.cz - serwis ČEZ) | 188 | `kp_jadro` (CZ: jadern…) | portal, bo ČEZ publikuje tylko tam |
| Vattenfall (`vattenfall`) | SE / DE / NL | strona „-jid-” | 249 | `kp_jadro` (SV: kärnkraft, Ringhals, Forsmark) | treść stopniowo |
| Fortum (`fortum`) | FI / SE | SuccessFactors RMK | 22 (wyszukiwanie „nuclear”) | `kp_jadro` | |
| IAEA (`iaea`) | AT | Taleo, wyszukiwarka REST (POST, tylko odczyt - zgoda właściciela 11.11.2026) | 13 | wszystkie | treść z jobdetail.ftl |
| Ontario Power Generation (`opg`) | CA | SuccessFactors RMK | wyszukiwanie „nuclear” | `kp_jadro` | poziom 2 (świat) |

## Sprawdzone, NIE podłączone
| Źródło | Wynik sondy | Co dalej |
|---|---|---|
| ENEC (enec.gov.ae, careers.enec.gov.ae), Nawah (careers.nawah.ae) | brak połączenia z runnera GitHub (serwery w ZEA odrzucają) | Barakah: spróbować przez LinkedIn/agregator tylko do odkrywania albo przez inny runner - do decyzji |
| F4E (fusionforenergy.europa.eu/vacancies) | lista ładowana skryptem z platformy e-rekrutacji | do zrobienia |
| EDF FR (edf.fr/edf-recrute) | lista ładowana skryptem (Drupal), API nieznane | do rozpoznania |
| Framatome | 403 / brak połączenia | blokuje runner |
| Sellafield Ltd (careers.sellafieldsite.co.uk/vacancies) | lista przez admin-ajax (POST) | do zrobienia |
| Slovenské elektrárne (profesia.sk) | lista ładowana skryptem | wyłączone |
| OSGE (kariera.osge.com, softgarden) | brak ofert w HTML (skrypt) | do rozpoznania API softgarden |
| UDT (eRecruiter) | tylko formularze, brak listy ofert | ogłoszenia UDT trafiają też na pracuj.pl |
| ZUOP, KCOR (BIP) | 403 / strona ładowana skryptem | BIP blokuje runner |
| TVO | strona „open positions” bez listy (zewnętrzny system) | do rozpoznania |
| Kozloduy NPP-Newbuild, NDA, Urenco, Sogin, NPCIL | brak połączenia | |
| UKAEA, Rolls-Royce SMR, CNL, NEK, OKG, SKB, SCK CEN, NRG, Enresa, Tecnatom, Axpo, newcleo, Fermi Energia | 404 pod zgadywanym adresem | rozpoznanie właściwego adresu - kolejna sonda |
| Bruce Power, X-energy (Workday), TerraPower (Greenhouse) | platformy z publicznym API JSON | poziom 2 - do podłączenia, gdy zostaną minuty |
| Energoatom | 403 | |

## Rozpoznanie reszty (ES, BE, NL, CH, DE, IT, SI, LT, EE, USA, CA, IN) - ocena kosztu
| Kraj | Pracodawcy | Ocena kosztu |
|---|---|---|
| Hiszpania | CNAT, ANAV, Enresa, ENUSA, Tecnatom, Westinghouse Madryt (już w `wec`), F4E Barcelona | średni: strony własne, część przez portale (InfoJobs); F4E przez e-rekrutację UE |
| Belgia | Engie Electrabel, SCK CEN, Tractebel | średni: SCK CEN własna strona (adres do ustalenia), Engie - SuccessFactors (filtr jądrowy) |
| Holandia | EPZ, NRG / PALLAS, Urenco NL | niski: kilka ofert, strony WordPress |
| Szwajcaria | Axpo, Alpiq / KKG, KKL | średni: portale firm energetycznych, filtr jądrowy |
| Niemcy | PreussenElektra, RWE Nuclear, EnBW, BGZ, BGE, Framatome GmbH, Urenco | średni-wysoki: wycofywanie; duże portale koncernów (SAP), filtr „Kernkraft / Rückbau” |
| Włochy | Sogin, newcleo, Ansaldo Nucleare | niski-średni: Sogin bez połączenia z runnera |
| Słowenia | NEK, GEN energija | niski: kilka ofert rocznie |
| Litwa / Estonia | INPP (Ignalina), Fermi Energia | niski |
| USA | Southern Nuclear, TVA, Constellation, Duke, Holtec, TerraPower, X-energy (+ Westinghouse, Bechtel już są) | wysoki wolumen; Workday i Greenhouse mają API JSON - tanie technicznie, drogie minutowo (tysiące ofert) |
| Kanada | OPG (podłączone), Bruce Power (Workday), NB Power, CNL, NWMO | średni |
| Indie | NPCIL | brak połączenia; ogłoszenia PDF |

## Zasady
- Każda oferta: kraj, miasto, projekt, sektor, język, pracodawca, link, wynagrodzenie jeśli podane (`kod/kp_parse.py: wzbogac()`, `kod/kp_projekty.py`).
- Kontrola eksportu tylko w bazie (`tags.kontrola_eksportu`), nigdy na stronie. Nazwiska i kontakty rekruterów usuwane z treści (`_bez_osob`).
- Zapytania: tylko GET (wyjątek do rozważenia: wyszukiwarki POST typu Taleo - tylko odczyt), >= 1,2 s między zapytaniami do jednej domeny (`collect/siec.py`).

## Potencjalni pracodawcy (11.11.2026)
`data/pracodawcy/kandydaci.tsv` - 226 firm i instytucji w 23 krajach (bez Rosatomu, Rosji, Białorusi, Węgier): dozór i regulatorzy, operatorzy i inwestorzy,
dostawcy z doświadczeniem w dostawach dla elektrowni jądrowych, inżynieria, badania (reaktory badawcze, laboratoria), medycyna nuklearna (izotopy), fuzja, odpady i wycofywanie.
Sonda stron kariery: `narzedzia/sonda_pracodawcy.py` (workflow „Sonda potencjalnych pracodawców”), wynik `data/pracodawcy/sonda.json`, widoczny w panelu „Oferty pracy” w kokpicie WP.
Kolejne podłączenia: najpierw Europa, w kolejności: regulatorzy i operatorzy z działającą stroną kariery, potem dostawcy z platformami z API (Workday, SuccessFactors, Teamtailor, Greenhouse).

## Pracodawcy z konfiguracji (11.11.2026) - `data/pracodawcy/podlaczone.json`
Dodanie pracodawcy = wpis w pliku (klucz, nazwa, kraj, sektor, typ: linki / sf / workday / smartrecruiters, adres listy, wzorzec linku oferty, filtr jądrowy), bez zmian w kodzie.
Test: workflow „Test zbierania” ze źródłem `pr_<klucz>`. Nieudane zostają w pliku z `aktywny: false` i powodem.
Aktywne od 11.11.2026: ANAV, GNS, Nagra, Blykalla, Altrad Endel (filtr), Axpo (filtr), PSI (filtr), Egis (filtr), NDA group, UKAEA.
Wyłączone: Kernkraftwerk Gösgen, Engie Electrabel (SuccessFactors - nowy układ), Seibersdorf, Urenco, Slovenské elektrárne (skrypt), Studsvik, GRS (brak linków), AWE (Workday 422), IFJ PAN.
