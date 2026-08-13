# Plansze przerywnikowe Machinekind

Zestaw czternastu plansz 16:9 do wstawiania między wystąpienia: otwarcie, plansza
postojowa, zapowiedzi, przerywniki sekcyjne, przerwa, pytania, podziękowanie.
Wiodąca czerwień `#bd3e3e`, biel i atrament `#0d0f10` — te same tokeny, kroje
i gesty co na stronie (`src/styles/global.css`), więc plansza wrzucona w cudzą
prezentację nadal czyta się jako Machinekind.

## Zestaw

| # | Plik | Do czego |
| --- | --- | --- |
| 01 | `otwarcie` | Wejście w blok. Sygnatura i zdanie o tym, co robimy. |
| 02 | `znak` | Plansza postojowa — stoi na ekranie, kiedy nikt nie mówi. |
| 03 | `punkt-styku` | Dłonie z hero strony. Przerywnik o styku człowieka i maszyny. |
| 04 | `za-chwile` | **Szablon.** Zapowiedź następnego wystąpienia. |
| 05 | `rozdzial` | **Szablon.** Przerywnik sekcyjny z numerem rozdziału. |
| 06 | `locomotion-ai` | Domena 01. |
| 07 | `world-models-vlm` | Domena 02. |
| 08 | `robotics-engineering` | Domena 03. |
| 09 | `design-program` | Domena 04. |
| 10 | `w01-tek` | Pierwsza maszyna, kadr na korpusie. |
| 11 | `teza` | Zasada kolektywu na atramencie. |
| 12 | `przerwa` | Przerwa w programie. |
| 13 | `pytania` | Q & A. |
| 14 | `dziekujemy` | Zamknięcie i kontakt. |

Czerwień prowadzi (osiem plansz), biel daje oddech przy dłuższych blokach,
atrament wchodzi raz — na tezie. Przy dłuższym paśmie warto je przeplatać,
zamiast puszczać osiem czerwonych z rzędu.

## Gotowe pliki

W `export/`:

- `png/` — po jednym pliku na planszę, 3840 × 2160 (2×). Do wrzucenia w dowolny
  program do prezentacji, na ekran w sali albo do social mediów.
- `machinekind-plansze.pdf` — cały zestaw, jedna plansza na stronę.
- `machinekind-plansze.pptx` — kadr panoramiczny 13,333 × 7,5 cala, każda plansza
  jako pełne tło slajdu. Do wklejenia między swoje slajdy.
- `machinekind-plansze.html` — cały zestaw w jednym pliku, z krojami i grafiką
  w środku. Działa bez internetu, także z pendrive'a.

## Edycja

Źródłem jest `index.html`; jedna plansza to jeden blok `.frame > .slide`.
Otwórz plik w przeglądarce, żeby zobaczyć cały zestaw; `index.html?only=6`
pokazuje szóstą planszę w pełnym kadrze 1920 × 1080.

Najczęstsza zmiana to podmiana treści w szablonach 04 i 05 — nadtytuł
(`.kicker`), tytuł (`.title`), zdanie pod spodem (`.lead`) i pomiar w lewym
dolnym rogu (`.foot--l`). Tło zmienia jedna klasa na `.slide`:

- `.slide--red` — czerwień marki,
- `.slide--paper` — biel, tytuł atramentem, numer rozdziału na różowo,
- `.slide--ink` — atrament.

Kolory pomocnicze (`--dim`, `--hair`, `--ghost`, `--accent`) ustawia samo tło,
więc bloki treści nie wymagają żadnych poprawek po zmianie klasy.

Stopka po prawej trzyma adres, nie numer slajdu: plansza wchodzi w cudzą
prezentację i własna numeracja byłaby tam nieprawdziwa.

## Ponowny eksport

```bash
node build.mjs
```

Skrypt składa `export/machinekind-plansze.html` (kroje i grafiki jako data URI),
zrzuca każdą planszę do PNG w 2× i oddaje PDF oraz PPTX do `build-pack.py`.

Potrzebne: Node, Chromium lub Chrome (szukany w `CHROME_BIN`, potem w zestawie
Playwrighta, potem w `PATH`) oraz Python z `pillow` i `python-pptx`.
Dodanie albo usunięcie planszy wymaga aktualizacji listy `NAMES` w `build.mjs` —
skrypt przerywa pracę, kiedy liczba nazw nie zgadza się z liczbą plansz.

## Zasoby

`assets/mark-{red,white,ink}.png` to znak z `logo.png` odcięty od papieru
i przemalowany na trzy warianty marki. `assets/hands-*.png` i `korpus.webp`
przyszły z `src/assets/`. Kroje (Big Shoulders Display, IBM Plex Sans, IBM Plex
Mono) leżą w `assets/fonts/` w tych samych plikach, których używa strona.
