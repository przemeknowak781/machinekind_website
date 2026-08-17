# Kroje

Trzy kroje, każdy z inną robotą do wykonania.

| Krój | Rola | Wagi w użyciu | Pliki |
| --- | --- | --- | --- |
| **Big Shoulders Display** | Sygnatura i tytuły. Kondensowany, wersaliki. | 500 | `big-shoulders-display-latin*.woff2` |
| **IBM Plex Sans** | Zdania i akapity. | 400, 500 | `ibm-plex-sans-latin*.woff2` |
| **IBM Plex Mono** | Pomiar: współrzędne, takty, liczności, oznaczenia. | 400, 500 | `ibm-plex-mono-latin*.woff2` |

Pliki w `pliki/` to te same, których używa strona — pochodzą z pakietów
[Fontsource](https://fontsource.org) w wersji 5.3.0. Każdy krój ma dwa podzbiory:
`latin` i `latin-ext`. **Podzbiór `latin-ext` jest obowiązkowy** — niesie polskie
znaki diakrytyczne. Bez niego „ą", „ę", „ł", „ś", „ż" wypadną na zamiennik
z systemu i napis rozjedzie się w połowie wyrazu.

Wersje zmienne (`wght`) dają całą oś wag w jednym pliku; system używa z niej
tylko 500 dla kroju wyświetlanego i 400/500 dla tekstowego.

## Licencja

Wszystkie trzy kroje są na **SIL Open Font License 1.1** — teksty licencji leżą
w `licencje/`. Wolno ich używać komercyjnie, osadzać w dokumentach i na stronie.
Nie wolno ich sprzedawać osobno ani zmieniać nazwy rodziny w zmodyfikowanej wersji.

## Poza siecią

Do materiałów drukowanych i do prezentacji składanych w programach biurowych
zainstaluj kroje w systemie — pliki `.ttf` pobierzesz z
[Google Fonts](https://fonts.google.com/specimen/Big+Shoulders+Display)
i [IBM Plex](https://github.com/IBM/plex). Pliki `.woff2` z tego katalogu są
przeznaczone dla przeglądarki i systemy operacyjne ich nie zainstalują.

W poczcie kroje marki nie działają — żaden klient pocztowy nie wczyta pliku
woff2. Podpis mailowy stoi więc na Arialu i Helvetice, patrz
`../templates/podpis-mailowy/`.

## Znak nie potrzebuje krojów

Litery w plikach znaku (`../logo/svg/wordmark-*.svg`, `lockup-*.svg`) są
zamienione na krzywe. Znak wygląda tak samo na maszynie bez zainstalowanych
krojów — i dlatego nigdy nie składa się go żywym tekstem.
