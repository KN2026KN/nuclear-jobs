# Agregatory ofert jądrowych - tylko do odkrywania pracodawców

Stan: 11.11.2026. Z agregatorów NIE kopiujemy ofert. Służą raz w miesiącu do znalezienia nowych nazw pracodawców; oferty bierzemy potem z oficjalnej strony pracodawcy.

| Agregator | Zasięg | Co daje | Dostęp z GitHub |
|---|---|---|---|
| jobs.nuclearinst.com (Nuclear Institute Jobs Board) | GB, AU, CA, NZ | ok. 14 stron po 30 ofert; AWE, Babcock, UKAEA, Dounreay, Mactech, Boccard UK, AECOM, uczelnie | do sprawdzenia |
| nuclearjobs.org (dawniej nuclearjobs.co.uk) | GB, CA | ok. 6 500 ofert, pracodawcy często ukryci | do sprawdzenia |
| nukeworker.com | US | ok. 1 400 - 1 700 ofert; Constellation, Dominion, Holtec, Fluor, Urenco USA, Vistra, Westinghouse, LANL | do sprawdzenia |
| smrintel.com/jobs | US, GB | ok. 340 ofert SMR i fuzji; TerraPower, Oklo, Kairos, CFS, Helion, Radiant, Last Energy | do sprawdzenia |
| euroengineerjobs.com/jobs/nuclear | Europa | kilka ofert (ITER, GB) | do sprawdzenia |
| euronuclear.org/education-training/career | Europa | lista 31 członków korporacyjnych ENS ze stronami kariery | do sprawdzenia |
| monavenirdanslenucleaire.fr (UMN, GIFEN, France Travail) | FR | ok. 7 000 ofert z France Travail ze słowem „nucléaire" | do sprawdzenia |
| jobs.cz, profesia.sk, pracuj.pl | CZ, SK, PL | lokalne rynki | pracuj.pl działa |

| Indeed (pl, uk, fr, de, com, RSS) | świat | sprawdzone 11.11.2026: 403 „Security Check" na każdej wersji | zablokowane |
| Glassdoor (com, co.uk, PL) | świat | sprawdzone 11.11.2026: 403 | zablokowane |
| Monster (com, co.uk, fr, de) | świat | sprawdzone 11.11.2026: 403 | zablokowane |

Indeed, Glassdoor i Monster: wszystkie wersje blokują serwery GitHub kontrolą antybotową, a regulaminy zabraniają automatycznego pobierania. Obchodzenia blokad nie robimy. Darmowych API dla nowych partnerów nie ma (Indeed Publisher i Glassdoor API zamknięte, Monster tylko płatne feedy). Wyszukiwarka przez `site:pl.indeed.com` też nie zwraca ich ofert. Wniosek: nie podłączamy do robota.

Sprawdzenie w przeglądarce właściciela (Chrome, 11.11.2026): wszystkie trzy działają normalnie.

| Wyszukiwanie | Wynik | Pracodawcy na 1. stronie |
|---|---|---|
| pl.indeed.com „elektrownia jądrowa" OR nuclear OR AP1000 | ponad 50 | Westinghouse, GE Vernova, Jacobs, WSI |
| uk.indeed.com nuclear | | AECOM (ogłoszenia sponsorowane) |
| fr.indeed.com nucléaire | ponad 3 000 | Altrad Endel, EDF, Framatome, Ardatem, Equans, Reatech, Chauvin Arnoux |
| de.indeed.com Kerntechnik | 100 | Bureau Veritas, Framatome, COPLA Burg, Safetec, Teicon, Ferchau (agencja) |
| glassdoor.com nuclear Poland | 74 | Westinghouse, GE Vernova, Amentum, Arabelle, WSI |
| monster.com nuclear | ponad 300 | głównie agencje (System One, Jobot, Johnson Service Group), GE Vernova |

Dopisane do `kandydaci.tsv`: Arabelle Solutions, Ardatem. Do uzupełnienia adresów: WSI, Reatech, COPLA Burg, Safetec, Teicon. Możliwe użycie: raz w miesiącu ręczny przegląd w Chrome tylko po nowe nazwy pracodawców. Pracodawców z tych serwisów i tak łapiemy przez ich własne strony kariery (lista w `kandydaci.tsv`).

Agencje rekrutacyjne (Thomas Thor, Morson, Orion, Russell Taylor, Astute) pomijamy: nie są pracodawcami.

## Dopisane 11.11.2026

- 33 pracodawców w `data/pracodawcy/kandydaci.tsv` (GB, CH, FR, SI, DK, US, CA, JP, IN, BR, AR, ZA, KR).
- 40 projektów w `kod/kp_projekty.py` (było 40, jest 80): eksploatacja i likwidacja w Europie (Leibstadt, Gösgen, Beznau, Doel / Tihange, Almaraz, Ascó / Vandellós, Cofrentes, Trillo, Heysham / Torness / Hartlepool, Dounreay, Ignalina, Konrad / Asse / Morsleben), badania i fuzja (MYRRHA, PALLAS, Jules Horowitz, STEP, Culham), nowe bloki i SMR (Fermi Energia, Khmelnytskyi 3-4, Natrium, Palisades, Crane / TMI, Hermes, Aurora, Xe-100, Clinch River, Bruce Power, Pickering, Wesleyville, Chalk River, Saeul / Shin Hanul, Chiny, Chashma 5, Rajasthan / PFBR, Ohma / Shimane, Angra 3, Atucha / CAREM), tylko do analizy: Uzbekistan SMR, Bałchasz, Leningrad II / Kursk II.
- Kraje: PK, UZ, KZ, NZ.
- Poprzednia wersja słownika: `kod/Archiwum/kp_projekty_11-11-2026.py`.

## Angielskie słowa kluczowe w Chrome (11.11.2026)

Zapytania: "NQA-1" nuclear, "small modular reactor", "nuclear quality", "nuclear safety", "nuclear decommissioning", "nuclear power plant", nuclear. Serwisy: Indeed US, UK, PL; Glassdoor (Europa, UK, NQA-1); Monster US. Indeed US nie obsługuje OR - każde słowo osobno.

| Rynek | Najczęstsi pracodawcy |
|---|---|
| Indeed UK | Assystem (dominuje), AECOM, AtkinsRéalis, Altrad, Rolls-Royce SMR, Amentum, Mott MacDonald, Mace, VINCI, Bilfinger, Capgemini Engineering, Turner & Townsend |
| Indeed PL | Westinghouse, GE Vernova, Arabelle, Jacobs, WSI |
| Indeed US | Sargent & Lundy, Vistra, Zachry, NANO Nuclear, Radiant, APTIM, Amentum, Kiewit, Black & Veatch, Enercon, Fluor, NuScale, Holtec, X-energy, Duke, NextEra, DTE |
| Glassdoor | Centrus, TerraPower, Amentum, BWXT, Holtec, Hatch, AtkinsRéalis, Orano, AWE, Babcock, Tradebe, LRQA, TÜV Rheinland, Gérard Perrier, Vulcain |
| Monster US | Sargent & Lundy, Enercon, w reszcie agencje |

Dopisane do `kandydaci.tsv`: 35 pracodawców (13 Europa i Kanada, 22 USA). Pominięte: agencje (Edgewater, System One, Johnson Service Group, Jobot, Ferchau, Kundlas) i firmy spoza branży, które wypadły przez luźne dopasowanie słowa NQA. Do uzupełnienia adresów: Vulcain Engineering, Hanford Tank Waste Operations & Closure.
