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

Obowiązują `robot_better.svg` i `human_better.svg`; starsze `hand_*.svg` zostają
jako zapas i skrypt sięga po nie, gdy nowszych nie ma. Żaden z nich nie nadaje
się do użycia wprost — to obrysy bitmapy, które niosą płytę tła, stopnie
cieniowania jako osobne ścieżki i kolor wpisany na sztywno.

`scripts/hands-vector.mjs` zostawia same ścieżki rysujące kształt, przycina
kadr do kreski i zapisuje z `fill="currentColor"`:

```bash
node scripts/hands-vector.mjs
```

Obrys ma trzy pasma jasności: kształt poniżej 0,3, stopnie cieniowania między
0,3 a 0,5 i tło powyżej. Liczy się tylko pierwsze — pasmo środkowe nie wnosi
kształtu, a zalane na czarno postrzępia kontur, więc `SHAPE_BELOW` odcina je
przy 0,3. Bez niego pliki są o połowę lżejsze, a krawędzie gładsze. Z 843 i 741
ścieżek zostaje 41 i 26.

Wynik to `src/assets/hand-robot.svg` i `hand-human.svg`, 74 i 87 kB (34 i 41 kB
po spakowaniu). Skrypt wypisuje proporcję dłoni i pionowe położenie opuszka
i porównuje je z wartościami, na których stoi układ nagłówka — po podmianie
plików źródłowych trzeba sprawdzić, czy się nie rozjechały. Przy obecnych
różnice to poniżej 1% na proporcji i 0,1 punktu procentowego na opuszku, więc
stałe w `HeroHands` zostały bez zmian.

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

Atrament ma cztery stopnie. `--ink` niesie nagłówki, `--ink-1` podtytuł
nagłówka strony, `--ink-2` tekst czytany, `--ink-3` drobny — ten ostatni trzyma
4,8:1 na bieli, więc nie schodzi niżej. Podtytuł nagłówka stoi sam na bieli pod
sygnaturą wysoką na kilkanaście centymetrów, więc idzie stopień wyżej niż
zwykły `.lead`: ciemniejszy atrament, interlinia 1,45 i miara 38 znaków. Przy
szarości, 1,5 i 34 znakach rozłaził się na pięć luźnych, krótkich wierszy.

Dłonie wracają jako tło sekcji (`HandsBackdrop`), w różnym stopniu skadrowane,
z paralaksą sterowaną przewijaniem tam, gdzie przeglądarka to obsługuje, i
powolnym dryfem tam, gdzie nie.

## Nagłówek strony

`HeroHands` układa dwie dłonie na przekątnej: maszyna wchodzi z dołu po lewej,
człowiek schodzi z góry po prawej, opuszki mijają się w prawej połowie kadru.
Przekątna wychodzi poza prawą krawędź — przedramię człowieka jest ucięte
kadrem. Bez tego kompozycja kończyła się dwieście pikseli przed krawędzią,
a prawa dolna ćwiartka nagłówka stała pusta.

Szerokość bryły ma dwa ograniczenia i bierze mniejsze: `104 × --hand-u` rządzi
na dużym ekranie, a sufit `82vw` wchodzi tam, gdzie okno jest niskie albo
wąskie. Bez sufitu bryła bywała szersza od kadru i z dłoni człowieka zostawały
przy 1024px same opuszki.
Położenia są liczone z geometrii obrazów — dla każdej dłoni znane jest
położenie opuszka w kadrze i kąt obrotu, więc `left` i `top` wynikają z tego,
gdzie opuszek ma wypaść po obrocie. Wszystko w udziałach bryły, więc
kompozycja skaluje się sztywno. Dwa zakresy: przekątna obok tekstu powyżej
780px, a poniżej dłonie schodzą pod tekst, bo wąski kadr ich obok nie
pomieści.

Obrót siedzi w osobnej własności `rotate`, dzięki czemu przewijanie może
animować `translate` bez deptania kąta.

## Wejście na stronę

Strona zaczyna się od bieli, samych dłoni i przesypującej się sygnatury.
Sekwencja ma trzy takty i trwa niecałe 4 sekundy:

| Czas | Co się dzieje |
| --- | --- |
| 0 – 1,5 s | dłonie wjeżdżają poziomo z lewej i prawej, bez obrotu, w powiększeniu 1,9× |
| 0 – 1,5 s | sygnatura stoi na środku i przez cały ten lot składa się z liter |
| 1,5 – 1,71 s | opuszki zatrzymują się naprzeciw siebie, na środku szerokości ekranu, słowo jest już gotowe |
| 1,71 – 3,0 s | obrót w skos, oddalenie kadru i przesunięcie na miejsce docelowe — sygnatura jedzie razem z dłońmi |
| 3,05 – 3,78 s | odsłania się nawigacja, akapit, przyciski i pasek pod nimi |

Opuszki się nie stykają — zatrzymują się naprzeciw siebie z przerwą około
1,8% szerokości bryły, czyli 10–26 px zależnie od kadru. Wcześniej wchodziły
jedna w drugą na 30–76 px i zamiast zetknięcia wychodziło zlepienie.

Sygnatura formuje się od zerowej sekundy, w tym samym czasie, w którym dłonie
lecą ku sobie, i rusza z miejsca dopiero przy zetknięciu opuszków — czyli
dokładnie tam, gdzie zaczyna się obrót dłoni. Krycia nie ma w ogóle: napis
albo stoi w pełnym atramencie, albo nie ma w nim jeszcze liter.

Droga na miejsce docelowe liczy się z układu (`--title-x` to odległość od lewej
krawędzi kolumny tekstu do środka okna), więc wyśrodkowanie wychodzi samo na
każdej szerokości. W układzie pionowym kolumna zajmuje całą szerokość i napis
i tak stoi na środku, więc przejazdu nie ma — słowo po prostu składa się
w miejscu.

Tekst wchodzi odsłoną kadru (`clip-path`), a nie przenikaniem. Przenikanie
zostawiało pół sekundy, w której litera stoi na częściowej przezroczystości —
detektor łapał tam kontrast 1,1:1. Przy odsłonie litera albo stoi w pełnym
atramencie, albo jej jeszcze nie widać.

Przesypywanie sygnatury to jedyny efekt na stronie wymagający skryptu.
Losuje wyłącznie ze zbioru liter samego słowa, więc szerokości zostają
w tym samym zakresie, a napis nie zamienia się w przypadkowy szum. Każda
litera siedzi w kratce o szerokości zablokowanej po wczytaniu krojów —
bez tego podmiana glifów rozjeżdżałaby napis w poziomie. Szerokość mierzy
się na literze docelowej, nie na losowej. Zanim kroje dojadą, litery już się
przesypują, tylko bez blokady — dzięki temu gotowe słowo nie mignie na starcie.

Bez skryptu w nagłówku stoi po prostu gotowe słowo. Nazwa dostępnościowa
siedzi w `aria-label`, więc czytnik ekranu nigdy nie przeczyta
przesypywanych liter.

Zetknięcie i pozycja docelowa to dwa różne miejsca: w chwili styku bryła stoi
wyśrodkowana (`--shift-meet`), a po złożeniu przesuwa się w prawo
(`--shift-final`), żeby zrobić miejsce nagłówkowi i akapitowi. W układzie
pionowym dłonie leżą pod tekstem, więc oba ustawienia są tam takie same.

Obrót jest animowany od zera, a nie tylko ustawiony statycznie. Wymusza to
`animation-fill-mode: backwards` na dłoniach: po animacji `translate` musi
wrócić pod kontrolę przewijania, a `rotate` do kąta z układu. Przy `both`
obie własności zostałyby zamrożone na ostatniej klatce i paralaksa
przestałaby działać.

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
