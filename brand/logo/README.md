# Znak

## Co jest w środku

| Katalog | Co zawiera |
| --- | --- |
| `svg/` | Znak, sygnatura słowna, dwa lockupy i scena dłoni. **Stąd bierz pliki do nowych materiałów.** |
| `png/` | Rastry 128–2048 px, dla narzędzi, które SVG nie przyjmują. |
| `favicon/` | Ikony przeglądarki i aplikacji: `.svg`, `.ico`, PNG 16–512, wariant maskowalny. |
| `social/` | Open Graph 1200 × 630, baner LinkedIn 1128 × 191, awatar 400 i 1000 px. |

Warianty barwne: `-red` (podstawowy, na bieli), `-white` (na czerwieni,
atramencie i zdjęciu), `-ink` (druk jednobarwny), `-current` (dziedziczy kolor
przez `currentColor`, do wstawienia w treść HTML).

## Skąd co pochodzi — ustalenia z przeglądu repozytorium

W repozytorium leży kilka plików, które wyglądają na znak marki, a nie są nim.
Warto wiedzieć, który jest który, zanim ktoś sięgnie po niewłaściwy.

| Plik w repo | Co to naprawdę jest |
| --- | --- |
| `logo.png` | **Źródło obecnego znaku.** Zrzut z programu graficznego: sześciobok z węzłem na białym tle z siatką kropek. Tak opisuje go `scripts/logo.mjs`, które robi z niego `mark.png`, `favicon.png` i `apple-touch-icon.png`. |
| `machinekind_logo.svg` | **Poprzedni logotyp**, nie obecny. Dłonie w czerwonym polu z sygnaturą pod spodem. Wgrany 09.08, dzień przed zmianą znaku. Nie używać. |
| `public/mark.svg`, `public/favicon.svg` | Ten sam poprzedni logotyp. Usunięte commitem `1efdd28` „Nowy znak marki w nawigacji, stopce i glifikonie". Do odzyskania przez `git show 1c688e8:public/mark.svg`. |
| `src/assets/hand-robot.svg`, `hand-human.svg` | **Wektory dłoni w użyciu.** Jedna ścieżka, `currentColor`, wstawiane w treść przez `HeroHands.astro`. Zbudowane przez `scripts/hands-vector.mjs`. |
| `robot_better.svg`, `human_better.svg`, `hand_robot.svg`, `hand_human.svg` | Obrysy pośrednie dłoni, po kilkaset ścieżek w odcieniach szarości. Materiał źródłowy dla skryptu, nie do użycia wprost. |

Wniosek, który z tego wynika: **obecny znak nie ma nigdzie wersji wektorowej**.
Ani w plikach, ani w historii gita, ani w metadanych `logo.png` (te niosą
tylko podpis C2PA narzędzia, którym plik zapisano). Wektor w `svg/` jest więc
obrysem bitmapy — świadomym, opisanym niżej, ale obrysem.

## Jak powstał wektor znaku

1. `logo.png` → kanał alfa przez odjęcie papieru;
2. czterokrotne powiększenie, rozmycie 3,6 px i próg — schodki skosów nie
   przenoszą się wtedy na krzywe;
3. obrys potrace'em (`alphamax 1,25`, `opttolerance 6,0`), 373 węzły w 5 krzywych;
4. sprawdzenie wierności: ponowna rasteryzacja i porównanie z bitmapą
   źródłową — **IoU 0,999**.

Jeśli u autora znaku leży plik źródłowy (AI, EPS, PDF), podmień
`svg/mark-*.svg` na niego i przelicz resztę:

```bash
python3 build-logo.py     # sygnatura słowna i lockupy
python3 build-raster.py   # PNG, favikony, grafiki do sieci
```

## Dłonie idą z wektora, nie z rastra

`svg/dlonie.svg` to scena „punkt styku" złożona z `src/assets/hand-robot.svg`
i `hand-human.svg` — tych samych plików, które strona wstawia w nagłówek.
Geometria sceny (dłonie po 1900 jednostek, odstęp 150, opuszki w jednej linii)
jest przeniesiona z `scripts/brand.mjs`, które składa wariant rastrowy.

Zgodność sprawdzona: obrys wektorowy pokrywa się z `src/assets/hands-ink.png`
w **IoU 0,966** — reszta różnicy to grubość krawędzi antyaliasingu.

```bash
python3 build-hands.py    # dlonie.svg + warianty barwne + kopie do slides/assets
```

## Sygnatura słowna i lockupy

Litery pochodzą z pliku kroju, którego używa strona (Big Shoulders Display,
waga 500), zamienione na krzywe przez `build-logo.py`. Kerning z GPOS jest
uwzględniony — dla „MACHINEKIND" wychodzi jedna para, „AC" o −12/2000 em.

Proporcje lockupów są przeniesione 1:1 z układów stojących na planszach
(`.lockup` i `.sig` w `../slides/assets/deck.css`).

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
