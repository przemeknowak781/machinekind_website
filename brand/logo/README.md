# Znak

## Co jest w środku

| Katalog | Co zawiera |
| --- | --- |
| `svg/` | Znak, sygnatura słowna i dwa lockupy — każde w czterech wariantach barwnych. **Stąd bierz pliki do nowych materiałów.** |
| `png/` | Rastry 128–2048 px, dla narzędzi, które SVG nie przyjmują. |
| `favicon/` | Ikony przeglądarki i aplikacji: `.svg`, `.ico`, PNG 16–512, wariant maskowalny. |
| `social/` | Open Graph 1200 × 630, baner LinkedIn 1128 × 191, awatar 400 i 1000 px. |

Warianty barwne: `-red` (podstawowy, na bieli), `-white` (na czerwieni,
atramencie i zdjęciu), `-ink` (druk jednobarwny), `-current` (dziedziczy kolor
przez `currentColor`, do osadzenia w HTML).

## Skąd się wziął wektor

W repozytorium nie było pliku wektorowego — istniał tylko `logo.png`, znak
wtopiony w białe tło. Wektor powstał z obrysu tej bitmapy:

1. `logo.png` → kanał alfa przez odjęcie papieru (`build-mark` w historii commitów);
2. czterokrotne powiększenie, rozmycie 3,6 px i próg — schodki skosów nie
   przenoszą się wtedy na krzywe;
3. obrys potrace'em (`alphamax 1,25`, `opttolerance 6,0`), 373 węzły w 5 krzywych;
4. sprawdzenie wierności: ponowna rasteryzacja i porównanie z bitmapą źródłową —
   **IoU 0,999**.

To jest obrys, nie oryginał. Jeśli gdzieś istnieje plik źródłowy od autora znaku
(AI, EPS, PDF), podmień `svg/mark-*.svg` na niego i przelicz resztę:

```bash
python3 build-logo.py     # sygnatura słowna i lockupy
python3 build-raster.py   # PNG, favikony, grafiki do sieci
```

## Sygnatura słowna i lockupy

Litery pochodzą z pliku kroju, którego używa strona (Big Shoulders Display,
waga 500), zamienione na krzywe przez `build-logo.py`. Kerning z GPOS jest
uwzględniony — dla „MACHINEKIND" wychodzi jedna para, „AC" o −12/2000 em.

Proporcje lockupów są przeniesione 1:1 z układów stojących na planszach
(`.lockup` i `.sig` w `../slides/assets/deck.css`), więc znak w prezentacji
i znak z tej paczki to ten sam znak.

## Favikony stoją na czerwieni

Przy 16 i 32 px kreska węzła jest cieńsza niż piksel. Sprawdzone zrzutami
w czterech wariantach: czerwony znak na przezroczystym tle zlewa się w plamę,
biały na czerwieni utrzymuje rysunek. Dlatego cały zestaw favikon ma czerwone
pole — inaczej niż znak w materiałach.

## Pole ochronne i minimalne rozmiary

Pole ochronne: **x = 1/6 szerokości znaku** ze wszystkich czterech stron.
Minimum: **32 px** albo **8 mm** dla samego znaku, **140 px** albo **34 mm**
dla lockupu poziomego. Poniżej — ikona z `favicon/`.

Pełny opis zasad i zakazów: `../brandbook/`.
