# Szablony

Materiały poza prezentacją: sieć, papier firmowy, podpis mailowy.
Wszystko składa jeden skrypt:

```bash
python3 build.py
```

Potrzebne: Chromium lub Chrome (szukany w `CHROME_BIN`, potem w zestawie
Playwrighta, potem w `PATH`) i Python z `pillow`.

## Sieć — `social/`

Cztery kadry w `social/index.html`; wymiary niesie atrybut `data-w`/`data-h`
przy karcie, więc dodanie piątej nie wymaga zmiany w skrypcie.

| Kadr | Rozmiar | Do czego |
| --- | --- | --- |
| `post-cytat` | 1080 × 1080 | Zasada albo zdanie z projektu. |
| `post-zapowiedz` | 1080 × 1080 | Zapowiedź wystąpienia. Szablon — podmień tytuł i osobę. |
| `post-znak` | 1080 × 1080 | Sam znak, gdy post niesie treść w opisie. |
| `story` | 1080 × 1920 | Relacja pionowa 9:16. |

Podgląd: otwórz `social/index.html` w przeglądarce. Pojedynczy kadr w skali
1:1: `social/index.html?only=2`. Wynik trafia do `social/export/` w 2×.

Grafiki stałe — Open Graph, baner LinkedIn, awatar — nie leżą tutaj, tylko
w `../logo/social/`, bo są częścią tożsamości, a nie szablonem do wypełnienia.

## Papier firmowy — `papier-firmowy/`

A4 pionowo. Do wydruku wprost z przeglądarki (marginesy: brak, grafika tła:
włączona) albo z gotowego `export/papier-firmowy.pdf`.

Czerwień jest tu cienką linią, nie plamą: strona zostaje biała, żeby dokument
dało się wydrukować w każdych warunkach i dopisać na nim notatkę.

## Podpis mailowy — `podpis-mailowy/`

Dwa warianty. `podpis.html` ma znak, `podpis-tekstowy.html` nie ma — ten drugi
jest do korespondencji z instytucjami, gdzie grafika w poczcie bywa blokowana.

Skopiuj zawartość `<table>` do ustawień podpisu w kliencie pocztowym. Układ
trzyma tabela, a style siedzą w atrybutach `style`, bo klienty pocztowe usuwają
arkusze stylów, a Outlook nie liczy flexboxa.

**Znak w podpisie musi stać pod publicznym adresem.** Poczta nie wyświetla
plików z dysku ani data URI (Gmail je wycina). Wgraj
`../logo/png/mark-red-128.png` na serwer strony i wstaw adres w miejsce
`ZNAK_URL`. Podgląd w `export/` używa pliku z dysku i służy tylko do oceny
wyglądu.

Kroje marki nie działają w poczcie — podpis stoi na Arialu i Helvetice.
Nie podmieniaj tego „na siłę": część odbiorców zobaczy wtedy losowy zamiennik.
