# Design system

Jeden plik do wrzucenia w projekt: **`system.css`**. Niesie tokeny i warstwę
komponentów, nic więcej nie trzeba dołączać — poza krojami.

```html
<link rel="stylesheet" href="system.css" />
```

Kroje wczytaj osobno z `../fonts/pliki/` przez `@font-face` albo pakietami
`@fontsource-variable/big-shoulders-display`, `@fontsource-variable/ibm-plex-sans`
i `@fontsource/ibm-plex-mono`. **Podzbiór `latin-ext` jest obowiązkowy** —
niesie polskie znaki diakrytyczne.

## Pliki

| Plik | Do czego |
| --- | --- |
| `system.css` | **Wynik.** Tokeny + komponenty. Tego używa projekt. Nie edytuj — jest generowany. |
| `components.css` | Warstwa komponentów. **Tu się edytuje.** |
| `index.html` | Żywa dokumentacja. Otwórz w przeglądarce. |
| `export/machinekind-design-system.html` | To samo w jednym pliku, z krojami w środku. Działa bez internetu. |

```bash
python3 build-system.py
```

Skrypt skleja `../tokens/tokens.css` z `components.css`, składa dokumentację
i wersję jednoplikową. Tokeny są generowane z `src/styles/global.css`, więc
system nie może rozjechać się ze stroną — po zmianie tokena na stronie
przepuść `../tokens/build-tokens.py`, a potem ten skrypt.

## Co jest skąd

Warstwa komponentów nie wymyśla systemu obok strony. Dzieli się na dwa zbiory:

**Przepisane bez zmian z `src/styles/global.css`** — `.wrap`, `.section`,
`.rule`, `.head`, skala typograficzna, `.btn` z wariantami, konteksty `.dark`
i `.red`, pominięcie nawigacji, pierścień skupienia, wyłączenie ruchu.

**Dołożone tutaj** — formularz (`.field`, `.input`, `.textarea`, `.select`,
`.check`), `.card`, `.list`, `.table`, `.tag`, `.note`, `.figure`, `.link`,
`.kicker`, `.stack`, `.cluster`, `.grid`. Strona ich jeszcze nie potrzebowała,
projekt, który weźmie ten plik, potrzebuje.

## Trzy zasady, na których to stoi

1. **Kolor ustawia kontekst, nie komponent.** Blok `.dark` albo `.red`
   podmienia atrament, włos i akcent, więc karta, tabela czy przycisk
   w środku nie wiedzą, na czym stoją. Nowy kolor dopisuj w kontekście.
2. **Podziały niesie włos, nie ramka i nie cień.** Linia ma 1 px w każdej
   skali. Pole formularza ma kreskę u dołu, nie obwódkę dookoła.
3. **Odstęp niesie rodzic.** `.stack`, `.cluster` i `.grid` odpowiadają za
   przestrzeń; komponenty nie mają własnych marginesów, więc nie zlepiają się
   i nie odpychają w nieprzewidziany sposób.

## Wersaliki po polsku

Tytuł w kroju wyświetlanym łamany na dwa wiersze i więcej bierze
`.h-wrapped` — interlinia 0,96 zamiast domyślnej. Przy ciaśniejszym wierszu
kreska w „Ó" i ogonek w „Ą" wchodzą na sąsiedni wiersz. Jednowierszowy tytuł
tego nie potrzebuje.

## Dostępność

Pierścień skupienia (`:focus-visible`) jest wspólny dla wszystkiego, co da się
dojść klawiaturą — nie zdejmuj go bez podstawienia własnego. `prefers-reduced-motion`
wyłącza przejścia i animacje. Progi kontrastu są policzone
w `../tokens/contrast.py`; dwie pary schodzą poniżej 4,5:1 i wolno ich użyć
wyłącznie na elementy dekoracyjne — dlatego na atramencie odsyłacz bierze
`--red-soft`, a nie czerwień marki.
