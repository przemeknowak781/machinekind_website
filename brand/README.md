# Machinekind — materiały marki

Komplet: znak w wektorze, tokeny, księga znaku, plansze prezentacyjne
i szablony do sieci, druku i poczty.

Wszystko stoi na jednym systemie — tym samym, który niesie strona. Tokeny są
generowane z `src/styles/global.css`, kroje to te same pliki, których używa
serwis, a proporcje lockupów są przeniesione z układów stojących na planszach.
Nic w tej paczce nie jest osobnym pomysłem obok strony.

## Od czego zacząć

**Robisz nowy materiał** → otwórz `brandbook/export/machinekind-ksiega-znaku.pdf`.
Dwadzieścia jeden stron: znak, kolor, typografia, układ, obrazowanie, głos.

**Potrzebujesz pliku znaku** → `logo/svg/`. Wektor, cztery warianty barwne.

**Wchodzisz w kod** → `tokens/tokens.css` albo `tokens.json`.

**Składasz prezentację** → `slides/export/` (PPTX, PDF, PNG).

## Mapa paczki

| Katalog | Co w środku |
| --- | --- |
| `brandbook/` | Księga znaku: źródło, 21 stron w PNG, PDF i wersja jednoplikowa HTML. |
| `logo/` | Znak, sygnatura słowna, lockupy. SVG, PNG, favikony, grafiki do sieci. |
| `tokens/` | Tokeny w JSON, CSS, SCSS i JS. Skrypt liczący kontrast WCAG. |
| `slides/` | 23 plansze przerywnikowe 16:9. Źródło, PNG, PDF, PPTX. |
| `templates/` | Sieć (post, relacja), papier firmowy A4, podpis mailowy. |
| `fonts/` | Pliki krojów i licencje OFL. |

Każdy katalog ma własny README z opisem, skąd pliki pochodzą i co wymaga
podmiany.

## Składanie od nowa

Materiały są generowane, nie rysowane ręcznie. Po zmianie treści albo tokena
uruchom skrypt — nie poprawiaj wyeksportowanego pliku, bo następne złożenie
i tak go nadpisze.

```bash
python3 tokens/build-tokens.py     # tokeny z global.css → json, css, scss, js
python3 logo/build-logo.py         # sygnatura słowna i lockupy z pliku kroju
python3 logo/build-raster.py       # PNG, favikony, Open Graph, awatar
node    slides/build.mjs           # plansze → PNG, PDF, PPTX
python3 templates/build.py         # sieć, papier firmowy, podpis
python3 brandbook/build.py         # księga znaku → PNG, PDF, HTML
python3 spakuj.py                  # archiwum do przekazania na zewnątrz
```

Kolejność ma znaczenie: brandbook bierze miniatury z plansz i szablonów,
a paleta i tabela kontrastu wychodzą z tokenów.

Potrzebne: Node, Chromium lub Chrome (szukany w `CHROME_BIN`, potem w zestawie
Playwrighta, potem w `PATH`), Python z `pillow`, `python-pptx`, `fonttools`
i `potracer`.

## Dwie rzeczy do podmiany

1. **Znak jest obrysem bitmapy**, nie plikiem od autora — wierność 0,999
   względem `logo.png`, ale jeśli gdzieś leży oryginał wektorowy, podmień go
   i przelicz resztę. Szczegóły w `logo/README.md`.
2. **Logotypy uczelni**: PWr mamy w wersji angielskiej, UEW w 362 px.
   Oba działają, oba warto wymienić na lepsze. Szczegóły
   w `slides/assets/logos/README.md`.

## Kontakt

hello@wo1.tech · machinekind.ai · Wrocław
