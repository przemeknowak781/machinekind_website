"""Design system: składa `system.css` i żywą dokumentację.

    python3 build-system.py

`system.css` to jeden plik do wrzucenia w projekt: tokeny wygenerowane
z `src/styles/global.css` plus warstwa komponentów z `components.css`.
Tokenów nie przepisuje się ręcznie, więc system nie może rozjechać się
ze stroną.

Dokumentacja (`index.html`) stoi na tym samym pliku, który opisuje —
każda próbka na stronie jest zbudowana z klas systemu, nie ze stylów
napisanych obok. Jeśli komponent się zepsuje, widać to od razu.
"""

import base64
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
BRAND = HERE.parent
FONTS = BRAND / 'slides/assets/fonts'

STAMP = (f'Machinekind — system wizualny. Złożone przez '
         f'brand/design-system/build-system.py, {date.today().isoformat()}. '
         f'Tokeny pochodzą z src/styles/global.css — nie edytuj ich tutaj.')


# ============================================================
# system.css
# ============================================================

def build_css() -> str:
    tokens = (BRAND / 'tokens/tokens.css').read_text()
    tokens = re.sub(r'^/\*.*?\*/\n\n', '', tokens, flags=re.S)   # własna szapka niżej
    components = (HERE / 'components.css').read_text()
    css = (f'/* {STAMP} */\n\n'
           f'/* ---------- Kroje ----------\n'
           f'   Pliki woff2 leżą w brand/fonts/pliki. Wczytaj je @font-face albo\n'
           f'   przez pakiety @fontsource — podzbiór latin-ext jest obowiązkowy,\n'
           f'   bo niesie polskie znaki diakrytyczne. */\n\n'
           f'{tokens}\n{components}')
    (HERE / 'system.css').write_text(css)
    return css


# ============================================================
# Dokumentacja
# ============================================================

ARROW = ('<svg class="btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" '
         'aria-hidden="true"><path d="M1 12 12 1M4 1h8v8" stroke="currentColor" '
         'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# (kotwica, tytuł, opis, próbka HTML, klasa tła próbki)
SPECS = [
    ('typografia', 'Typografia',
     'Krój wyświetlany niesie sygnaturę i tytuły, tekstowy — zdania, monospace — pomiar. '
     'Tytuł łamany na dwa wiersze i więcej bierze <code>.h-wrapped</code>: polskie '
     'wersaliki przy ciaśniejszym wierszu wchodzą na siebie.',
     '<p class="kicker">Nadtytuł</p>\n'
     '<h2 class="h2 h-wrapped">Chód uczony<br>w symulacji</h2>\n'
     '<p class="lead">Sieci sterujące chodem trenujemy w symulatorze pełnej dynamiki.</p>\n'
     '<p class="body-text">Tekst akapitowy trzyma miarę 68 znaków, więc wiersz da się '
     'przeczytać bez gubienia linii.</p>\n'
     '<p class="mono">300 mln kroków · sim-to-real</p>', ''),

    ('uklad', 'Układ',
     'Treść trzyma miarę <code>--wrap</code>, podziały niesie włos. '
     '<code>.stack</code> i <code>.cluster</code> odpowiadają za odstępy, żeby '
     'komponenty nie nosiły własnych marginesów.',
     '<div class="stack">\n'
     '  <div class="cluster">\n'
     '    <span class="tag">jeden</span><span class="tag">dwa</span>'
     '<span class="tag">trzy</span>\n'
     '  </div>\n'
     '  <hr class="rule">\n'
     '  <div class="grid" style="--col:11rem">\n'
     '    <p class="body-text">Kolumna</p><p class="body-text">Kolumna</p>'
     '<p class="body-text">Kolumna</p>\n'
     '  </div>\n'
     '</div>', ''),

    ('przycisk', 'Przycisk',
     'Jedyne zaokrąglenie w systemie — pełna pigułka. Wersja domyślna na atramencie, '
     '<code>.btn--ghost</code> na włosie. Stan wyłączony nie reaguje na wskaźnik.',
     '<div class="cluster">\n'
     '  <a class="btn" href="#">Projekt Wojtek ' + ARROW + '</a>\n'
     '  <a class="btn btn--ghost" href="#">Kontakt</a>\n'
     '  <button class="btn btn--sm">Mniejszy</button>\n'
     '  <button class="btn" disabled>Wyłączony</button>\n'
     '</div>', ''),

    ('odsylacz', 'Odsyłacz',
     'W tekście ciągłym odsyłacz jest czerwony i podkreślony. Na czerwieni i na '
     'atramencie kolor podmienia kontekst — czerwień marki na atramencie daje 3,59:1 '
     'i nie nadaje się na tekst.',
     '<p class="body-text">Maszyna chodzi we Wrocławiu — '
     '<a class="link" href="#">zobacz projekt</a>.</p>', ''),

    ('formularz', 'Formularz',
     'Pole ma jedną kreskę u dołu, nie ramkę dookoła. Ramka robiłaby z formularza '
     'siatkę prostokątów, a system stoi na włosie. Błąd oznacza atrybut '
     '<code>data-invalid</code> na <code>.field</code>.',
     '<div class="stack" style="--stack-gap:1.75rem;max-width:32rem">\n'
     '  <div class="field">\n'
     '    <label class="label" for="e">Adres</label>\n'
     '    <input class="input" id="e" type="email" placeholder="hello@wo1.tech">\n'
     '  </div>\n'
     '  <div class="field">\n'
     '    <label class="label" for="t">Wiadomość</label>\n'
     '    <textarea class="textarea" id="t" placeholder="Napisz, co budujecie"></textarea>\n'
     '  </div>\n'
     '  <div class="field" data-invalid>\n'
     '    <label class="label" for="r">Rola</label>\n'
     '    <select class="select" id="r"><option>Wybierz</option></select>\n'
     '    <p class="error">Pole wymagane.</p>\n'
     '  </div>\n'
     '  <label class="check"><input type="checkbox" checked>'
     '<span class="body-text">Zgoda na kontakt</span></label>\n'
     '</div>', ''),

    ('karta', 'Karta',
     'Kreska u góry, oznaczenie, tytuł, treść. Karta klikalna zabiera akcent na '
     'tytuł i na kreskę — cała powierzchnia jest celem.',
     '<div class="grid" style="--col:15rem">\n'
     '  <a class="card" href="#">\n'
     '    <p class="card__meta">Domena 01</p>\n'
     '    <h3 class="card__title">Chód uczony w symulacji</h3>\n'
     '    <p class="card__body">Trajektorie z symulatora przenosimy na maszynę.</p>\n'
     '  </a>\n'
     '  <div class="card">\n'
     '    <p class="card__meta">Domena 02</p>\n'
     '    <h3 class="card__title">Rozumienie przestrzeni</h3>\n'
     '    <p class="card__body">Modele świata dają maszynie kontekst.</p>\n'
     '  </div>\n'
     '</div>', ''),

    ('lista', 'Lista pozycji',
     'Wiersze rozdzielone włosem. Kolumny ustawia <code>--list-cols</code>, więc ta '
     'sama lista niesie program wydarzenia i wykaz plików.',
     '<ol class="list">\n'
     '  <li class="list__row">\n'
     '    <span class="mono">01</span>\n'
     '    <span><strong>Spyrosoft</strong><br><span class="mono">Partner</span></span>\n'
     '    <span class="body-text">Kilka słów od partnera</span>\n'
     '  </li>\n'
     '  <li class="list__row">\n'
     '    <span class="mono">02</span>\n'
     '    <span><strong>Michał Pogoda-Rosikoń</strong><br>'
     '<span class="mono">bards.ai</span></span>\n'
     '    <span class="body-text">Dlaczego teraz jest czas na humanoidy</span>\n'
     '  </li>\n'
     '</ol>', ''),

    ('tabela', 'Tabela',
     'Bez linii pionowych i bez tła wierszy. Liczby biorą <code>.num</code> — monospace '
     'z cyframi tej samej szerokości, żeby kolumna stała w pionie. Szeroka tabela idzie '
     'w <code>.table-scroll</code>, żeby to ona przewijała się w bok, a nie strona.',
     '<div class="table-scroll">\n'
     '  <table class="table">\n'
     '    <thead><tr><th>Warstwa</th><th>Takt</th><th>Co robi</th></tr></thead>\n'
     '    <tbody>\n'
     '      <tr><td>Pętla momentu</td><td class="num">400 Hz</td><td>moment na wale</td></tr>\n'
     '      <tr><td>Sieć lokomocyjna</td><td class="num">50 Hz</td><td>krok</td></tr>\n'
     '      <tr><td>Rozumienie sceny</td><td class="num">1 Hz</td><td>zamiar</td></tr>\n'
     '    </tbody>\n'
     '  </table>\n'
     '</div>', ''),

    ('znacznik', 'Znacznik i notka',
     'Znacznik niesie stan albo kategorię, notka — uwagę na marginesie treści. '
     'Oba stoją na włosie, nie na wypełnieniu.',
     '<div class="stack">\n'
     '  <div class="cluster">\n'
     '    <span class="tag">domyślny</span>\n'
     '    <span class="tag tag--red">czerwony</span>\n'
     '    <span class="tag tag--ink">atrament</span>\n'
     '  </div>\n'
     '  <p class="note note--red">Maszyna jest własnością Politechniki Wrocławskiej.</p>\n'
     '</div>', ''),

    ('konteksty', 'Konteksty barwne',
     'Blok <code>.dark</code> albo <code>.red</code> podmienia atrament, włos i akcent, '
     'więc komponenty w środku nie wiedzą, na czym stoją. Nie dopisuj kolorów '
     'w komponencie — dopisz je w kontekście.',
     '<div class="red" style="padding:2rem">\n'
     '  <p class="kicker">Nadtytuł</p>\n'
     '  <h3 class="card__title" style="margin:.6rem 0">Punkt styku</h3>\n'
     '  <p class="body-text">Ten sam akapit, ta sama klasa.</p>\n'
     '  <div class="cluster" style="margin-top:1.25rem">\n'
     '    <a class="btn" href="#">Przycisk</a>\n'
     '    <a class="btn btn--ghost" href="#">Ghost</a>\n'
     '  </div>\n'
     '</div>\n'
     '<div class="dark" style="padding:2rem;margin-top:1rem">\n'
     '  <p class="kicker">Nadtytuł</p>\n'
     '  <h3 class="card__title" style="margin:.6rem 0">Budujemy, nie doradzamy</h3>\n'
     '  <p class="body-text">Akcent na atramencie bierze '
     '<a class="link" href="#">czerwień jasną</a>.</p>\n'
     '</div>', 'plain'),
]


def escape(code: str) -> str:
    return code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_docs() -> str:
    nav = ''.join(f'<a href="#{a}">{t}</a>' for a, t, *_ in SPECS)
    blocks = []
    for anchor, title, desc, sample, tone in SPECS:
        demo_cls = 'demo' + (' demo--plain' if tone == 'plain' else '')
        blocks.append(
            f'<section class="block" id="{anchor}">'
            f'<div class="block__head"><h2 class="h2 h-wrapped">{title}</h2>'
            f'<p class="lead">{desc}</p></div>'
            f'<div class="{demo_cls}">{sample}</div>'
            f'<pre class="code"><code>{escape(sample)}</code></pre>'
            f'</section>')

    doc = f"""<!doctype html>
<html lang="pl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Machinekind — design system</title>
    <link rel="stylesheet" href="../slides/assets/fonts.css" />
    <link rel="stylesheet" href="system.css" />
    <style>
      /* Chrom dokumentacji — wszystko poniżej dotyczy tylko tej strony,
         nie systemu. Próbki są zbudowane wyłącznie z klas systemu. */
      body {{ padding-bottom: 6rem; }}
      .top {{ border-bottom: 1px solid var(--line); }}
      .top__inner {{ display: flex; flex-wrap: wrap; gap: 1.5rem 2.5rem;
                     align-items: baseline; justify-content: space-between;
                     padding-block: 1.75rem; }}
      .lockup {{ display: flex; align-items: center; gap: .8rem; }}
      .lockup img {{ width: 2rem; }}
      .lockup span {{ font-family: var(--display); font-weight: 500; font-size: 1.5rem;
                      letter-spacing: .055em; text-transform: uppercase; line-height: 1; }}
      .toc {{ display: flex; flex-wrap: wrap; gap: .35rem 1.4rem; }}
      .toc a {{ font-family: var(--mono); font-size: var(--micro); letter-spacing: .12em;
                text-transform: uppercase; color: var(--ink-3); }}
      .toc a:hover {{ color: var(--red); }}
      .hero {{ padding-block: clamp(3rem, 7vw, 6rem) clamp(2rem, 4vw, 3.5rem); }}
      .block {{ padding-block: clamp(2.5rem, 5vw, 4rem); border-top: 1px solid var(--line); }}
      .block__head {{ display: grid; gap: 1rem; margin-bottom: 2rem; }}
      @media (min-width: 900px) {{
        .block__head {{ grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
                        gap: 2.5rem; align-items: start; }}
        .block__head .lead {{ padding-top: .55em; }}
      }}
      .demo {{ padding: clamp(1.5rem, 3vw, 2.5rem); background: var(--paper-2);
               display: flex; flex-direction: column; gap: 1.25rem; }}
      .demo--plain {{ padding: 0; background: none; }}
      .code {{ margin-top: 1rem; padding: 1.25rem 1.5rem; background: var(--ink);
               color: rgba(255,255,255,.86); font-family: var(--mono); font-size: .8rem;
               line-height: 1.65; overflow-x: auto; white-space: pre; }}
      .files {{ margin-top: 1.5rem; }}
    </style>
  </head>
  <body>
    <header class="top">
      <div class="wrap top__inner">
        <div class="lockup">
          <img src="../logo/svg/mark-red.svg" alt="" />
          <span>Machinekind</span>
        </div>
        <nav class="toc">{nav}</nav>
      </div>
    </header>

    <main class="wrap">
      <div class="hero">
        <p class="kicker">Design system</p>
        <h1 class="h1 h-wrapped" style="margin:1.5rem 0 1.25rem">
          Jeden plik<br />do wrzucenia<span class="accent">.</span>
        </h1>
        <p class="lead">
          <code>system.css</code> niesie tokeny i komponenty. Tokeny są generowane
          z <code>src/styles/global.css</code>, więc system nie może rozjechać się
          ze stroną. Ta dokumentacja stoi na tym samym pliku, który opisuje — każda
          próbka niżej jest zbudowana z klas systemu.
        </p>
        <div class="table-scroll files">
          <table class="table">
            <thead><tr><th>Plik</th><th>Co to</th></tr></thead>
            <tbody>
              <tr><td><code>system.css</code></td><td>Tokeny i komponenty w jednym.
                Tego pliku używa projekt.</td></tr>
              <tr><td><code>components.css</code></td><td>Sama warstwa komponentów.
                Tu się edytuje.</td></tr>
              <tr><td><code>../tokens/</code></td><td>Tokeny osobno, w JSON, CSS, SCSS i JS.</td></tr>
              <tr><td><code>../fonts/</code></td><td>Pliki krojów i licencje. Podzbiór
                latin-ext jest obowiązkowy.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      {''.join(blocks)}
    </main>
  </body>
</html>
"""
    (HERE / 'index.html').write_text(doc)
    return doc


def build_bundle(doc: str):
    """Wersja jednoplikowa — kroje, style i znak w data URI."""
    def uri(path: Path) -> str:
        mime = {'.woff2': 'font/woff2', '.svg': 'image/svg+xml'}[path.suffix]
        return f'data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}'

    fonts = (BRAND / 'slides/assets/fonts.css').read_text()
    fonts = re.sub(r"url\('fonts/([^']+)'\)",
                   lambda m: f"url('{uri(FONTS / m.group(1))}')", fonts)
    system = (HERE / 'system.css').read_text()

    html = doc.replace('<link rel="stylesheet" href="../slides/assets/fonts.css" />',
                       f'<style>{fonts}</style>')
    html = html.replace('<link rel="stylesheet" href="system.css" />',
                        f'<style>{system}</style>')
    html = re.sub(r'src="(\.\./[^"]+\.svg)"',
                  lambda m: f'src="{uri((HERE / m.group(1)).resolve())}"', html)
    out = HERE / 'export'
    out.mkdir(exist_ok=True)
    (out / 'machinekind-design-system.html').write_text(html)
    print(f'export/machinekind-design-system.html  ({len(html) / 1e6:.2f} MB)')


if __name__ == '__main__':
    css = build_css()
    print(f'system.css  {len(css) / 1024:.1f} kB '
          f'({css.count("--") // 2} tokenów, {len(SPECS)} rozdziałów dokumentacji)')
    doc = build_docs()
    print(f'index.html  {len(doc) / 1024:.1f} kB')
    build_bundle(doc)
