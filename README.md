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
logo.png                materiał źródłowy — znak marki
przemek.jpg             materiał źródłowy — portret do siatki zespołu
machinekind_logo.svg    logotyp
scripts/brand.mjs       generator materiałów pochodnych
scripts/logo.mjs        znak marki: nawigacja, stopka, glifikon
scripts/portret.mjs     portret do siatki zespołu
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
się do użycia wprost — to obrysy bitmapy, które niosą płytę tła, kolor wpisany
na sztywno i rozmytą krawędź rozłożoną na kilkaset osobnych ścieżek.

```bash
npm i --no-save potrace && node scripts/hands-vector.mjs
```

Pierwsza wersja skryptu wybierała ścieżki po jasności wypełnienia: brała pasmo
najciemniejsze, resztę odrzucała. To był błąd w samym założeniu. Pasmo
najciemniejsze nie jest kształtem, tylko jądrem rozmytej krawędzi — obrys
bitmapy na najciemniejszym poziomie jest z natury poszarpany, a otaczające go
jaśniejsze ścieżki właśnie tę granicę wygładzały. Sylwetka wychodziła o 2%
chudsza od źródła i miała ząbkowany grzbiet palca.

Teraz kształt powstaje inaczej: źródło idzie na raster 4000 px, próg tnie
w połowie rampy antyaliasingu — czyli tam, gdzie naprawdę biegnie krawędź —
i dopiero ten kształt obrysowuje potrace jedną gładką ścieżką. Jasne wnętrza
zostają dziurami, bo trasowanie prowadzi je w przeciwną stronę. Pole sylwetki
zgadza się ze źródłem w granicach 1%.

`potrace` wchodzi leniwym importem i nie siedzi w `package.json`: ciągnie za
sobą trzy megabajty zależności i kilka ostrzeżeń audytu, a potrzebny jest
wyłącznie przy podmianie materiału źródłowego. Wynik i tak leży w repo,
a wdrożenie instaluje devDependencies przy każdym budowaniu i tego skryptu
nigdy nie uruchamia. Bez pakietu skrypt kończy się instrukcją, co doinstalować.

Wynik to `src/assets/hand-robot.svg` i `hand-human.svg`, 45 i 72 kB. Skrypt
wypisuje proporcję dłoni i pionowe położenie opuszka i porównuje je
z wartościami, na których stoi układ nagłówka — po podmianie plików źródłowych
trzeba sprawdzić, czy się nie rozjechały. Przy obecnych różnice to 1,03%
i 0,04% na proporcji oraz 0,15 i 0,30 punktu procentowego na opuszku, więc
stałe w `HeroHands` zostały bez zmian; zetknięcie opuszków zmierzone
w przeglądarce przesunęło się o jeden piksel.

Nagłówek strony używa tych wektorów wstawionych w treść: kolor bierze z CSS,
a scena nie czeka na osobne żądanie, bo animacja wejścia startuje w zerowej
sekundzie. Tła sekcji i znak wodny w kontakcie zostają na bitmapach — przy
kryciu 4–8% wektor niczego nie wnosi, a byłby cięższy.

## Znak marki

`logo.png` to zrzut z programu graficznego: znak leży na białym tle z siatką
kropek, ma szerokie marginesy i waży ponad megabajt. `scripts/logo.mjs`
przycina go do kreski, zdejmuje tło i zapisuje w rozmiarach, które strona
faktycznie podaje:

```bash
node scripts/logo.mjs
```

Tło zdejmuje otoczka wypukła pikseli znaku, a nie zalewanie od krawędzi.
Zalewanie przeciekłoby białymi szczelinami, które przecinają sześciokąt
i dotykają jego obrysu — zżarłoby całą pętlę w środku. Otoczka zna granicę
figury, więc biel w środku zostaje bielą i znak czyta się i na bieli,
i na czerni stopki.

Wynik to `src/assets/mark.png` (nawigacja i stopka, przez `astro:assets`,
w wyjściu 4–12 kB WebP), `public/favicon.png` i `public/apple-touch-icon.png`.
Glifikony idą w palecie, bo znak ma dwie barwy — w pełnym kolorze ważyły
dziesięć razy więcej. Kafelek dla iOS jest na papierze, bo tam alfa wychodzi
czarnym tłem.

## Portrety zespołu

Siatka zespołu kadruje portrety w proporcji 4:5 i przycina je `cover`, więc
materiał wchodzi w tej samej proporcji — inaczej przeglądarka obcięłaby go po
swojemu i głowa wypadłaby z kadru:

```bash
node scripts/portret.mjs przemek.jpg przemyslaw-nowak 0.53 0.22 0.66
```

Dwa pierwsze argumenty po slugu to punkt ostrości (udział szerokości
i wysokości źródła), trzeci to zbliżenie — ułamek największego kadru 4:5, jaki
mieści się w źródle. Portret całej sylwetki wymaga ciaśniejszego kadru niż
popiersie, bo w siatce liczy się twarz, a nie kurtka. Nazwa pliku musi się
zgadzać ze slugiem w `data/team.ts`; brak pliku to nie błąd — wtedy w kafelku
stoją inicjały.

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

## Nagłówek strony na wąskim ekranie

W układzie pionowym bryła dłoni nie wisi na ułamku wysokości sceny, tylko
kotwiczy się od dołu, tuż nad przyciskami. Przy kotwicy na 62% wysokość sceny
i wysokość dłoni rosły osobno, więc między dłońmi a przyciskami zostawało
kilkadziesiąt pikseli pustki, a nad tekstem drugie tyle. Odstęp w siatce jest
teraz równy dokładnie wysokości bryły plus światło, a nie stałemu minimum.

Rozmiar bryły ma dwa ograniczenia i bierze mniejsze: 160% szerokości okna,
żeby dłonie wychodziły poza obie krawędzie, i 44% jego wysokości, żeby na
tablecie nie zjadły całego ekranu. Sufit w `rem` tego nie umiał — przy 768px
zatrzymywał bryłę w środku kadru z marginesami po bokach i przekątna traciła
cały impet. Przy 390×844 cały nagłówek — sygnatura, tekst, dłonie i przyciski —
mieści się nad zgięciem.

Tekst pod sygnaturą stoi w dwóch taktach zamiast jednego bloku: twierdzenie
(`.hero__claim`, stopień wyżej, pełny atrament) i to, co je uzasadnia
(`.hero__sub`, mniejszy, przygaszony). Jednym akapitem rozłaził się na pięć
wierszy, w których nic nie było ważniejsze od reszty. Wyróżnienie jest jedno,
bo jedna rzecz odróżnia kolektyw od pracowni AI: warstwa inteligencji powstaje
razem ze sprzętem, na którym ma chodzić.

## Treść strony głównej

Strona jest o kolektywie, nie o jednym projekcie i nie o współpracy z uczelnią.
Wcześniej czytało się ją odwrotnie: „Punkt styku" stawiał obok siebie dwie
kolumny — Machinekind i Politechnikę — sekcja domen nazywała się „cztery
warstwy jednej maszyny", siatka zespołu pokazywała dwanaście osób z dwóch
instytucji, a osobna sekcja opisywała laboratorium uczelni. Wychodziło z tego,
że kolektyw jest połową cudzego projektu.

Teraz układ idzie tak:

| Sekcja | Co mówi |
| --- | --- |
| Punkt styku | kim jesteśmy i co z tego wynika — trzy zasady zamiast podziału pracy z kimkolwiek |
| Cały stos, jeden zespół | komplementarność: cztery domeny, po dwie osoby, cała droga od modelu do przegubu |
| Pierwsza maszyna | W01-TEK jako projekt kolektywu, z Politechniką wymienioną jako partner tego projektu |
| Kto to robi | osiem osób w czterech parach |
| Kontakt | pokaz maszyny |

Współpraca z Politechniką Wrocławską dotyczy wyłącznie W01-TEK, więc na stronie
głównej zostaje z niej jedno zdanie drobnym drukiem w karcie projektu —
prowadzenie projektu i własność maszyny — a szczegóły idą na podstronę
projektu. Skład uczelniany zostaje w `data/team.ts` z komentarzem, że należy do
projektu, a nie do kolektywu.

Liczności domen w sekcji „Cały stos" biorą się ze składu zespołu, więc zdanie
„po dwie osoby w każdej" nie rozjedzie się z siatką niżej.

## Projekt Wojtek

Strona projektu W01-TEK żyje na razie osobno pod `machinekind.ai`. Docelowo ma
być podstroną `/wojtek` — do tego czasu odsyłacze prowadzą na zewnątrz. Adres
siedzi w jednej stałej `WOJTEK_URL` w `src/pages/index.astro` oraz w stopce.
