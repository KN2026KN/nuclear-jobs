# Statystyki ofert - format danych (11.2026)

Tylko dla właściciela. Bez treści ofert, bez nazwisk.

## Gdzie
- Co noc `kod/statystyki.py` liczy statystyki z bazy (`/tmp/kp.sqlite`, odbudowywanej z `raw/`) i zapisuje `data/statystyki/RRRR-MM-DD.json` (historia w repo).
- `strona/statystyki_publikuj.py` wysyła ten sam JSON na **prywatną** stronę WordPress „KP statystyki - dane” (slug `kp-statystyki-dane`, status `private`).
  Treść strony: `<!-- wp:html --><script type="application/json" id="kp-stat">{…}</script><!-- /wp:html -->`.
  Panel w kokpicie WP buduje właściciel osobno: odczyt `GET /wp-json/wp/v2/pages?slug=kp-statystyki-dane&status=private&context=edit` (zalogowany administrator) → `content.raw` → JSON ze `script#kp-stat`.
- Pełne dane (każda oferta, każda wersja, każdy dzień obecności) są w bazie `kp.sqlite` (tabele `jobs`, `versions`, `observations`, `events`, `runs`) - z niej da się policzyć każdą inną statystykę.

## Panel w kokpicie WP (11.11.2026)
- Menu „Oferty pracy” w kokpicie (snippet WPCode 7243, tylko administrator) wyświetla stronę 7240: kraje i pracodawcy, źródła z ostatniej nocy, niepodłączone źródła, wykresy, wynagrodzenia wg kraju.
- Szablon: `strona/praca/statystyki.html` + `statystyki.js` (skrypt jako base64). Odświeżenie bez zbierania: workflow „Panel statystyk teraz”.

## Pola JSON
| Pole | Co zawiera |
|---|---|
| `dzien` | dzień przebiegu (UTC) |
| `wygenerowano` | znacznik czasu |
| `otwarte_razem` | liczba otwartych ofert widocznych na stronie lub możliwych do pokazania (bez `tylko_analiza`) |
| `tylko_analiza_otwarte` | otwarte oferty projektów Rosatomu, Rosji, Białorusi, Węgier - tylko do analizy, nigdy na stronie |
| `otwarte` | liczby otwartych ofert wg wymiarów: `kraj` (ISO), `projekt`, `typ_obiektu` (bud, eks, smr, bad, fuz, odp, ins), `pracodawca`, `zrodlo`, `funkcja`, `poziom`, `jezyk` |
| `tylko_analiza` | to samo dla ofert `tylko_analiza` |
| `nowe`, `zamkniete` | liczba ofert nowych / zamkniętych: klucz `RRRR-MM-DD` dla ostatnich 60 dni, `RRRR-MM` dla wcześniejszych miesięcy bieżącego roku, `RRRR` dla poprzednich lat |
| `nowe_tylko_analiza`, `zamkniete_tylko_analiza` | to samo dla `tylko_analiza` |
| `wynagrodzenia` | wg `funkcja`, `kraj`, `zrodlo`, `projekt`: lista `{waluta, okres (mies / rok / godz), n, mediana, min, max}` - środek widełek, waluta oryginalna, wszystkie oferty w historii |
| `wynagrodzenia_tylko_analiza` | to samo dla ofert `tylko_analiza` |
| `czas_zycia_dni` | średni i medianowy czas od pierwszego do ostatniego dnia oferty (zamknięte oferty), `n` |
| `pokrycie` | kraj -> pracodawca -> {n, zrodla} (otwarte w terminie, bez tylko_analiza) |
| `zrodla`, `rotacja`, `niepodlaczone` | stan źródeł z raportu nocy, źródła pominięte w rotacji, lista niepodłączonych |
| `zrodla_ostatni_przebieg` | źródła z dzisiejszego przebiegu: liczba ofert i tryb (`full` = pełna lista, `partial` = bez zamykania ofert) |

## Typy obiektów (`typ_obiektu`)
bud - w budowie · eks - w eksploatacji · smr - SMR · bad - reaktor badawczy · fuz - fuzja · odp - odpady i wycofywanie · ins - instytucja.

## Zasady
- Grupowanie czasu: 60 dni dziennie, bieżący rok miesięcznie, starsze lata rocznie (reguła dla wszystkich botów z 02.11.2026).
- Wynagrodzenia nie są przeliczane w statystykach (waluta oryginalna). Kurs NBP używany jest tylko do sortowania na stronie.
