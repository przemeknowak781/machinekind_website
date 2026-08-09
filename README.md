# Machinekind

Strona kolektywu Machinekind. Astro, statyczne wyjście, bez frameworka po stronie klienta.

## Uruchomienie

```bash
npm install
npm run dev      # serwer deweloperski na :4321
npm run build    # wynik do dist/
npm run preview  # podgląd zbudowanej strony
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

## Ruch i zależność od skryptu

Strona nie ma wejścia sekcji w kadr. Jedyny autorski moment ruchu to scena
dłoni w nagłówku: obraz osiada, potem raz zapala się iskra. Całość leci w CSS,
więc **żadna treść nie zależy od JavaScriptu** — przy wyłączonym skrypcie strona
jest kompletna. Jedyny skrypt na stronie uruchamia film w karcie projektu po
wejściu w kadr; bez niego zostaje plakat.

Ruch wygasza się przy `prefers-reduced-motion`.

## Projekt Wojtek

Strona projektu W01-TEK żyje na razie osobno pod `machinekind.ai`. Docelowo ma
być podstroną `/wojtek` — do tego czasu odsyłacze prowadzą na zewnątrz. Adres
siedzi w jednej stałej `WOJTEK_URL` w `src/pages/index.astro` oraz w stopce.
