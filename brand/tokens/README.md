# Tokeny

Wartości systemu w czterech formatach. **Nie edytuj tych plików ręcznie** —
są generowane z bloku `:root` w `src/styles/global.css`:

```bash
python3 build-tokens.py
```

Źródłem prawdy jest CSS strony. Dzięki temu paczka marki nie może rozjechać się
z tym, co realnie stoi na produkcji: po zmianie tokena na stronie wystarczy
przepuścić skrypt, a wszystkie formaty i brandbook wezmą nową wartość.

| Plik | Do czego |
| --- | --- |
| `tokens.json` | Wymiana z narzędziami projektowymi, import do Figmy przez wtyczkę. |
| `tokens.css` | Zmienne własne CSS — do wklejenia w nowy projekt webowy. |
| `tokens.scss` | Zmienne SCSS. |
| `tokens.js` | Moduł ES, gdy kolory wchodzą do kodu (canvas, wykresy, e-mail). |

28 tokenów w 9 grupach: czerwień, atrament, papier, linie, tekst na ciemnym,
tekst na czerwieni, kroje, miara i krzywa czasowa.

## Kontrast

```bash
python3 contrast.py            # tabela na wyjście
python3 contrast.py --json     # dane dla brandbooka
```

Skrypt liczy kontrast WCAG dla wszystkich par, które realnie występują
w systemie. Wartości półprzezroczyste (`--on-dark-*`, `--on-red-*`) są najpierw
składane z tłem — bez tego liczba nic nie znaczy.

Dwie pary schodzą poniżej 4,5:1 i obie są tam z rozmysłem: `--ink` na `--red`
i `--red` na `--ink`, po 3,59:1. To akcenty dekoracyjne (kropka po tytule),
nie tekst. Na atramencie tekstowym akcentem jest `--red-soft` — 5,66:1.

## Czego tu nie ma

System nie ma barw semantycznych: koloru sukcesu, ostrzeżenia ani błędu.
Jeśli kiedyś będą potrzebne, dokładaj je jako nową grupę w `global.css`
i przelicz tokeny — nie dopisuj wartości wprost w komponencie.
