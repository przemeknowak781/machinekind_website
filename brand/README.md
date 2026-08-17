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
python3 logo/build-hands.py        # scena dłoni z wektorów używanych przez stronę
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

## Co warto wiedzieć, zanim się coś podmieni

1. **Obecny znak nie ma nigdzie wersji wektorowej.** Sprawdzone w plikach,
   w historii gita i w metadanych — jedynym źródłem jest `logo.png`, zrzut
   z programu graficznego, i tak traktuje go też `scripts/logo.mjs` w repo.
   Wektor w paczce jest obrysem tej bitmapy o wierności 0,999. Jeśli
   u autora znaku leży plik źródłowy, podmiana jest jednym poleceniem.
2. **`machinekind_logo.svg` w korzeniu repo to poprzedni logotyp**, nie
   obecny — dłonie w czerwonym polu, wgrane dzień przed zmianą znaku.
   To samo dotyczy `public/mark.svg` z historii. Nie używać.
3. **Dłonie idą z wektora**, nie z rastra: `logo/svg/dlonie.svg` składa się
   z tych samych plików, które strona wstawia w nagłówek.
4. **Logotypy uczelni**: PWr mamy w wersji angielskiej, UEW w 362 px.
   Oba działają, oba warto wymienić na lepsze. Szczegóły
   w `slides/assets/logos/README.md`.

## Kontakt

hello@wo1.tech · machinekind.ai · Wrocław
