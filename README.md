# Keura Nuclear - oferty pracy w sektorze jądrowym

Robot, który co noc zbiera oferty pracy w sektorze jądrowym z oficjalnych stron pracodawców (Polska, Europa, świat)
i buduje stronę [keura.eu/praca](https://keura.eu/praca/) oraz statystyki rynku.

- Źródła: tylko oficjalne strony kariery pracodawców i instytucji publicznych; agregatory służą wyłącznie do odkrywania nowych pracodawców (`docs/AGREGATORY.md`).
- Dane: `raw/<dzień>/` - listy i treści ofert (bez e-maili i telefonów rekruterów, `kod/bez_kontaktow.py`); `data/` - baza, podsumowania dni, statystyki.
- Przebieg: `.github/workflows/zbieranie.yml` (codziennie), procedura: `docs/PROCEDURA.md`, źródła: `docs/ZRODLA_SWIAT.md`, statystyki: `docs/STATYSTYKI.md`.

Prowadzi: Keura Nuclear, [keura.eu](https://keura.eu).
