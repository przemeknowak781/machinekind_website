# Plansze przerywnikowe Machinekind

Zestaw dwudziestu trzech plansz 16:9 do wstawiania między wystąpienia:
otwarcie, zaproszenie, program, zapowiedzi kolejnych prelekcji, przerywniki
sekcyjne, partner, organizatorzy, przerwa, pytania, podziękowanie.
Wiodąca czerwień `#bd3e3e`, biel i atrament `#0d0f10` — te same tokeny, kroje
i gesty co na stronie (`src/styles/global.css`), więc plansza wrzucona w cudzą
prezentację nadal czyta się jako Machinekind.

## Zestaw

| # | Plik | Do czego |
| --- | --- | --- |
| 01 | `otwarcie` | Wejście w blok. Sygnatura i zdanie o tym, czym się zajmujemy. |
| 02 | `zaproszenie` | Hasło wydarzenia i zaproszenie. |
| 03 | `znak` | Plansza postojowa — stoi na ekranie, kiedy nikt nie mówi. |
| 04 | `program` | Pięć punktów programu: kto mówi i o czym. |
| 05 | `za-chwile` | **Szablon.** Zapowiedź kolejnego wystąpienia. |
| 06 | `rozdzial` | **Szablon.** Przerywnik sekcyjny z numerem rozdziału. |
| 07 | `wystapienie-spyrosoft` | Zapowiedź 01 — Spyrosoft. |
| 08 | `wystapienie-pogoda-rosikon` | Zapowiedź 02 — Michał Pogoda-Rosikoń, bards.ai. |
| 09 | `wystapienie-piotrowski` | Zapowiedź 03 — Grzegorz Piotrowski, PWr. |
| 10 | `wystapienie-wysocki` | Zapowiedź 04 — Marcin Wysocki, Positive Surfer. |
| 11 | `wystapienie-janiec` | Zapowiedź 05 — Łukasz Janiec, PWr. |
| 12 | `punkt-styku` | Dłonie z hero strony. Przejście od ludzi do maszyny. |
| 13 | `locomotion-ai` | Domena 01. |
| 14 | `world-models-vlm` | Domena 02. |
| 15 | `robotics-engineering` | Domena 03. |
| 16 | `design-program` | Domena 04. |
| 17 | `wojtek` | Pies-robot z Politechniki Wrocławskiej, kadr na korpusie. |
| 18 | `teza` | Zasada kolektywu na atramencie. |
| 19 | `partner-spyrosoft` | Partner wydarzenia. |
| 20 | `organizatorzy` | Pięć instytucji i logotypy PWr oraz UEW. |
| 21 | `przerwa` | Przerwa w programie. |
| 22 | `pytania` | Q & A. |
| 23 | `dziekujemy` | Zamknięcie i kontakt. |

Czerwień prowadzi (trzynaście plansz), biel daje oddech przy dłuższych
blokach, atrament wchodzi raz — na tezie. Przy dłuższym paśmie warto je
przeplatać, zamiast puszczać kilka czerwonych z rzędu.

## Trzy zasady, na których stoi układ

1. **Stopka po prawej trzyma adres, nie numer slajdu.** Plansza wchodzi
   w cudzą prezentację i własna numeracja byłaby tam nieprawdziwa.
2. **Nadtytuł i stopka po lewej stoją tylko tam, gdzie mają co nieść** —
   nazwę domeny, oznaczenie, pomiar, nazwisko prelegenta. Na planszach
   ceremonialnych (znak, punkt styku, przerwa, pytania, podziękowanie)
   zostaje sam tytuł: dopisany tam nadtytuł niósłby ton zamiast treści.
3. **Logotypy instytucji stoją wyłącznie na białych planszach** (19 i 20),
   bo mają własny kolor. Szczegóły w `assets/logos/README.md` — są tam też
   dwa pliki do podmiany, kiedy uczelnie przyślą lepsze wersje.

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

Najczęstsza zmiana to podmiana treści w szablonach 05 i 06 — nadtytuł
(`.kicker`), tytuł (`.title`), zdanie pod spodem (`.lead`) i oznaczenie
w lewym dolnym rogu (`.foot--l`). Tło zmienia jedna klasa na `.slide`:

- `.slide--red` — czerwień marki,
- `.slide--paper` — biel, tytuł atramentem, numer rozdziału na różowo,
- `.slide--ink` — atrament.

Kolory pomocnicze (`--dim`, `--hair`, `--ghost`, `--accent`) ustawia samo tło,
więc bloki treści nie wymagają żadnych poprawek po zmianie klasy.

Długie tytuły wystąpień biorą `.title--talk`: stopień niżej i luźniejsza
interlinia, bo wersaliki z ogonkami przy ciasnym wierszu wchodzą na siebie.

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

Uwaga na kadr: `--window-size` w Chromium podaje rozmiar okna razem z ramą,
nie sam kadr. Okno idzie więc z zapasem (`OVERSHOOT`), a `build-pack.py`
przycina zrzut do 3840 × 2160.

## Zasoby

`assets/mark-{red,white,ink}.png` to znak z `logo.png` odcięty od papieru
i przemalowany na trzy warianty marki. `assets/hands-*.png` i `korpus.webp`
przyszły z `src/assets/`. Logotypy instytucji i partnera leżą w
`assets/logos/` — tam też opis, skąd pochodzą i co wymaga podmiany. Kroje
(Big Shoulders Display, IBM Plex Sans, IBM Plex Mono) leżą w `assets/fonts/`
w tych samych plikach, których używa strona.
