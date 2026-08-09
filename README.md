# Machinekind

Strona kolektywu Machinekind. Astro, statyczne wyjście, bez frameworka po stronie klienta.

## Uruchomienie

```bash
npm install
npm run dev      # serwer deweloperski na :4321
npm run build    # wynik do dist/
npm run preview  # podgląd zbudowanej strony
```

## Wdrożenie

`.github/workflows/deploy.yml` buduje i publikuje stronę na GitHub Pages przy
każdym pchnięciu na `main`. W ustawieniach repozytorium **Settings → Pages →
Source** musi być ustawione **GitHub Actions** (nie „Deploy from a branch").

Adres i bazę podaje `actions/configure-pages`, a nie kod:

| Gdzie stoi | `PAGES_ORIGIN` | `BASE_PATH` |
| --- | --- | --- |
| Własna domena | `https://machinekind.ai` | `/` |
| Adres projektowy | `https://przemeknowak781.github.io` | `/machinekind_website` |

Dzięki temu ta sama konfiguracja obsługuje oba przypadki i przełączenie na
własną domenę nie wymaga zmiany w kodzie — wystarczy wpisać ją w ustawieniach
Pages. Bez zmiennych (czyli lokalnie) budują się adresy docelowej domeny.

Ponieważ baza nie jest znana przy pisaniu kodu, **żadna ścieżka w źródłach nie
może zaczynać się od twardego `/`**. Pliki z `public/` i odsyłacze na stronie
głównej przechodzą przez `asset()` i `link()` z `src/lib/paths.ts`.

Próba lokalna adresu projektowego:

```bash
BASE_PATH=/machinekind_website PAGES_ORIGIN=https://przemeknowak781.github.io npm run build
BASE_PATH=/machinekind_website npm run preview   # → /machinekind_website/
```

## Struktura

```
hand_human.png          materiał źródłowy — dłoń człowieka (biała kreska, alfa)
hand_robot.png          materiał źródłowy — dłoń maszyny
machinekind_logo.svg    logotyp
scripts/brand.mjs       generator materiałów pochodnych
src/
  assets/               obrazy przechodzące przez optymalizację Astro
  components/           Nav, Footer, HandsScene, HandsBackdrop, TeamGrid
  data/team.ts          skład zespołów
  layouts/Base.astro    szkielet strony, meta, obserwator wejścia w kadr
  pages/index.astro     strona kolektywu
  styles/global.css     system wizualny
public/media/           wideo
```

## Sylwetki wektorowe

`hand_human.svg` i `hand_robot.svg` to obrys bitmapy: około 485 ścieżek każdy,
z czego jedna niesie kształt przy pełnym kryciu, a reszta odtwarza antyaliasing
półprzezroczystymi warstwami. Surowo ważą 1,5 MB i na białym tle są niewidoczne,
bo obrysowano białą kreskę.

`scripts/hands-vector.mjs` wyciąga tę jedną ścieżkę, przycina kadr do samej
kreski i zapisuje z `fill="currentColor"`:

```bash
node scripts/hands-vector.mjs
```

Wynik to `src/assets/hand-robot.svg` i `hand-human.svg`, 87 i 71 kB (32 i 26 kB
po spakowaniu). Skrypt wypisuje proporcję dłoni i pionowe położenie opuszka
i porównuje je z wartościami, na których stoi układ nagłówka — po podmianie
plików źródłowych trzeba sprawdzić, czy się nie rozjechały. Przy obecnych
różnica to około 1%, więc stałe w `HeroHands` zostały bez zmian.

Nagłówek strony używa tych wektorów wstawionych w treść: kolor bierze z CSS,
a scena nie czeka na osobne żądanie, bo animacja wejścia startuje w zerowej
sekundzie. Tła sekcji i znak wodny w kontakcie zostają na bitmapach — przy
kryciu 4–8% wektor niczego nie wnosi, a byłby cięższy.

## Materiały marki

`scripts/brand.mjs` składa z dwóch plików źródłowych scenę „Stworzenia" — dłoń
maszyny z lewej, dłoń człowieka z prawej, opuszki w jednej osi, styk dokładnie
w połowie kadru. Skrypt wyznacza opuszki numerycznie z kanału alfa, więc po
podmianie plików źródłowych wystarczy go przepuścić ponownie:

```bash
node scripts/brand.mjs
```

Wypisuje pozycję styku — jeśli się zmieni, trzeba zaktualizować `MEET_X` /
`MEET_Y` w `src/components/HandsScene.astro`, bo tam siedzi iskra.

Skrypt tworzy też `public/mark.svg` i `public/favicon.svg` — kadr logotypu bez
sygnatury słownej.

## System wizualny

Biel jako tło podstawowe, czerń jako druga powierzchnia, czerwień `#bd3e3e`
wprost z logotypu — jako akcent i jako tło całych sekcji (`.red`).

Krój wyświetlany to Big Shoulders Display, dobrany do sygnatury z logotypu:
wąski, wysoki, płaskie zakończenia. Tekst czytany składa IBM Plex Sans, pomiar
IBM Plex Mono. Wszystkie trzy z podzbiorem `latin-ext`, więc polskie znaki się
zaciągają.

Monospace niesie wyłącznie pomiar: współrzędne, takty, liczności, oznaczenia.
Nie służy za kostium „technicznego" pod zwykłe etykiety.

Dłonie wracają jako tło sekcji (`HandsBackdrop`), w różnym stopniu skadrowane,
z paralaksą sterowaną przewijaniem tam, gdzie przeglądarka to obsługuje, i
powolnym dryfem tam, gdzie nie.

## Nagłówek strony

`HeroHands` układa dwie dłonie na przekątnej: maszyna wchodzi z dołu po lewej,
człowiek schodzi z góry po prawej, opuszki mijają się w prawej połowie kadru.
Położenia są liczone z geometrii obrazów — dla każdej dłoni znany jest
położenie opuszka w kadrze i kąt obrotu, więc `left` i `top` wynikają z tego,
gdzie opuszek ma wypaść po obrocie. Wszystko w `vw`, żeby kompozycja skalowała
się sztywno. Trzy zakresy: przekątna obok tekstu powyżej 900px, ta sama
przekątna niżej opuszczona w zakresie 761–899px, a poniżej 760px dłonie schodzą
pod tekst, bo wąski kadr ich obok nie pomieści.

Obrót siedzi w osobnej własności `rotate`, dzięki czemu przewijanie może
animować `translate` bez deptania kąta.

## Wejście na stronę

Strona zaczyna się od bieli i samych dłoni. Sekwencja ma trzy takty i trwa
około 2 sekund:

| Czas | Co się dzieje |
| --- | --- |
| 0 – 0,75 s | dłonie zjeżdżają z przeciwnych narożników w powiększeniu 1,9× |
| 0,75 – 0,85 s | opuszki stykają się i zatrzymują |
| 0,85 – 1,5 s | powiększenie schodzi do jedynki, kompozycja siada na miejscu |
| 1,4 – 2,1 s | wchodzi nawigacja, nagłówek, tekst i pasek pod nim |

Dłonie dojeżdżają odrobinę dalej, niż wynosi ich pozycja docelowa, bo przy
powiększeniu 1,9× docelowa przerwa też rośnie 1,9× i nie byłoby żadnego
zetknięcia. Rozchodzą się do właściwego odstępu dopiero razem z oddalaniem.

Powiększeniem steruje bryła, a dojazdem każdy obrazek z osobna. Ten podział
jest konieczny: `rotate` dłoni i `translate` przewijania siedzą na `.hand`,
więc animacja wejścia musi działać na innym elemencie, żeby się z nimi nie
biła.

Sekwencja jest krótka także dlatego, że w dłuższej wersji detektor łapał
stronę w trakcie przenikania tekstu i zgłaszał kontrast liczony na częściowej
przezroczystości.

## Ruch i zależność od skryptu

Poza wejściem strona nie ma animacji sekcji w kadrze. Drugi ruch to rozsuwanie
dłoni w miarę przewijania pierwszego ekranu. Steruje tym jedna dziedziczona liczba `--p` od 0 do 1, którą wypełnia
oś czasu przewijania (`scroll()`); tam gdzie przeglądarka jej nie zna, ustawia
ją kilkanaście linii skryptu zapasowego w `Base.astro`.

**Żadna treść nie zależy od JavaScriptu** — przy wyłączonym skrypcie strona
jest kompletna, a dłonie po prostu stoją. Drugi skrypt uruchamia film w karcie
projektu po wejściu w kadr; bez niego zostaje plakat.

Ruch wygasza się przy `prefers-reduced-motion`.

## Kontrola jakości

Projekt przechodzi detektor [impeccable](https://impeccable.style/slop/) na zero
trafień, statycznie i w przeglądarce, na 1440 i 390px:

```bash
node <ścieżka>/impeccable/skill/scripts/detect.mjs dist/index.html dist/_astro/*.css
node <ścieżka>/impeccable/skill/scripts/detect.mjs http://localhost:4321/
```

`.impeccable/config.json` wycisza jedną regułę, `clipped-overflow-container`,
wraz z uzasadnieniem: warstwa dłoni w nagłówku ma się przycinać, bo dłonie mają
wychodzić poza kadr sekcji. To jedyne odstępstwo.

## Projekt Wojtek

Strona projektu W01-TEK żyje na razie osobno pod `machinekind.ai`. Docelowo ma
być podstroną `/wojtek` — do tego czasu odsyłacze prowadzą na zewnątrz. Adres
siedzi w jednej stałej `WOJTEK_URL` w `src/pages/index.astro` oraz w stopce.
