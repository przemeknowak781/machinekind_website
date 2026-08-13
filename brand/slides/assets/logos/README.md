# Logotypy instytucji i partnera

Znaki niosą własny kolor, więc na planszach stoją **wyłącznie na białym tle**
(`.slide--paper`, plansze 19 i 20). Na czerwieni marki biłyby się z nią i
z sobą nawzajem. Wyrównuje je wysokość, nie szerokość — patrz `.logos` w
`assets/deck.css`.

| plik | instytucja | skąd | stan |
| --- | --- | --- | --- |
| `pwr.png` | Politechnika Wrocławska | `src/assets/logos/pwr.avif` w tym repo | **lockup angielski** („Wrocław University of Science and Technology"), 1575 × 472 |
| `uew.png` | Uniwersytet Ekonomiczny we Wrocławiu | Wikimedia Commons | **362 × 81 — za mało na kadr 2×**, przy 60 px wysokości znak jest lekko miękki |
| `spyrosoft.png` | Spyrosoft, partner wydarzenia | `spyro-soft.com`, plik `spyrosoft_color_rgb.png` | 3416 × 790, wystarcza z zapasem |

Dwie rzeczy do podmiany, kiedy będą pliki od uczelni:

1. **PWr po polsku.** Strona ma ten sam problem (patrz
   `src/assets/logos/README.md`), więc najlepiej podmienić oba naraz.
2. **UEW w wektorze albo w bitmapie ≥ 1200 px** w dłuższym boku. Obecny plik
   wystarcza na podgląd i na projektor 1080p, ale nie na druk ani na ekran 4K.

Wymagania dla nowych plików:

- wersja na jasne tło, z przezroczystością (alfa);
- SVG bez osadzonych czcionek — tekst zamieniony na ścieżki;
- bitmapa co najmniej ~1200 px w dłuższym boku, żeby wystarczyło na eksport 2×;
- nazwa pliku bez zmian, wtedy nic w `index.html` nie wymaga poprawki.

Znaki pochodzą z materiałów właścicieli i nie wolno ich przerysowywać ani
przebarwiać — również na potrzeby dopasowania do czerwieni marki.
