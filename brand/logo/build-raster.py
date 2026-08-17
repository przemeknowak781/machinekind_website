"""Rastry znaku: PNG w typowych rozmiarach, favikony i grafiki społecznościowe.

    python3 build-raster.py

Wszystko wychodzi z plików SVG obok — nic nie jest rysowane od nowa.
"""

import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from render import html_to_png, svg_to_png  # noqa: E402

SVG = HERE / 'svg'
PNG = HERE / 'png'
FAV = HERE / 'favicon'
SOCIAL = HERE / 'social'

RED, INK = '#bd3e3e', '#0d0f10'
MARK_RATIO = 956 / 1118          # proporcje kadru znaku

FONTS = HERE.parent / 'slides/assets/fonts'


def font_face(family: str, file: str, weight: str) -> str:
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-display:block;"
            f"src:url('file://{(FONTS / file).resolve()}') format('woff2');}}")


DISPLAY = (font_face('BSD', 'big-shoulders-display-latin-wght-normal.woff2', '100 900') +
           font_face('BSD', 'big-shoulders-display-latin-ext-wght-normal.woff2', '100 900'))
BODY = (font_face('Plex', 'ibm-plex-sans-latin-wght-normal.woff2', '100 700') +
        font_face('Plex', 'ibm-plex-sans-latin-ext-wght-normal.woff2', '100 700'))
MONO = (font_face('PlexMono', 'ibm-plex-mono-latin-400-normal.woff2', '400') +
        font_face('PlexMono', 'ibm-plex-mono-latin-ext-400-normal.woff2', '400'))


def png_exports():
    """Znak i lockupy w rozmiarach, po które sięga się najczęściej."""
    plan = [('mark', (128, 256, 512, 1024, 2048)),
            ('lockup-poziomy', (512, 1024, 2048)),
            ('lockup-pionowy', (512, 1024))]
    count = 0
    for stem, sizes in plan:
        for colour in ('red', 'white', 'ink'):
            for size in sizes:
                svg_to_png(SVG / f'{stem}-{colour}.svg', PNG / f'{stem}-{colour}-{size}.png', size)
                count += 1
    print(f'png: {count} plików')


def square(fill: str, mark: str, pad: float, size: int, out: Path, radius: int = 0):
    """Kwadratowa ikona: znak wpisany w pole z zadanym marginesem."""
    inner = round(size * (1 - 2 * pad))
    bg = f'background:{fill};' if fill else ''
    rad = f'border-radius:{radius}px;' if radius else ''
    html = (f'<div style="{bg}{rad}width:{size}px;height:{size}px;display:flex;'
            f'align-items:center;justify-content:center">'
            f'<img src="file://{(SVG / mark).resolve()}" style="width:{inner}px;display:block"></div>')
    html_to_png(html, out, size, size, transparent=not fill)
    return out


def favicons():
    """Komplet ikon: SVG do przeglądarki, PNG do zakładek i ekranu telefonu.

    W zakładce znak stoi na czerwieni, nie na przezroczystym tle. Przy 16 i 32 px
    kreska węzła jest cieńsza niż piksel; biel na czerwieni utrzymuje ją czytelną,
    czerwień na bieli zlewa się w plamę. Sprawdzone zrzutami w obu wariantach.
    """
    FAV.mkdir(parents=True, exist_ok=True)

    # Znak jest szerszy niż wyższy, więc w kwadracie stoi z marginesem bocznym.
    path = (SVG / 'mark-white.svg').read_text().split(' d="')[1].split('"')[0]
    side, h, pad = 1118, 956, 0.06
    inner = side * (1 - 2 * pad)
    scale = inner / side
    (FAV / 'favicon.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}" '
        f'role="img" aria-labelledby="t"><title id="t">Machinekind</title>'
        f'<rect width="{side}" height="{side}" fill="#bd3e3e"/>'
        f'<g transform="translate({side * pad:.1f} {(side - h * scale) / 2:.1f}) '
        f'scale({scale:.4f})">'
        f'<path fill="#ffffff" fill-rule="evenodd" d="{path}"/></g></svg>\n')

    for size in (16, 32, 48, 64):
        square(RED, 'mark-white.svg', 0.06, size, FAV / f'favicon-{size}.png')

    ico = [Image.open(FAV / f'favicon-{s}.png') for s in (16, 32, 48)]
    ico[0].save(FAV / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)],
                append_images=ico[1:])

    # Ikony aplikacji nie mogą być przezroczyste — znak stoi na czerwieni marki.
    square(RED, 'mark-white.svg', 0.18, 180, FAV / 'apple-touch-icon.png')
    for size in (192, 512):
        square(RED, 'mark-white.svg', 0.18, size, FAV / f'icon-{size}.png')
    # Wariant maskowalny ma większy margines, bo system może przyciąć rogi.
    square(RED, 'mark-white.svg', 0.28, 512, FAV / 'icon-512-maskable.png')
    print('favicon: svg, ico, 16/32/48/64, apple-touch, 192/512, maskable')


def social():
    """Grafiki do sieci: OG, baner LinkedIn, awatar."""
    SOCIAL.mkdir(parents=True, exist_ok=True)
    lockup = (SVG / 'lockup-poziomy-white.svg').resolve()
    style = f'<style>{DISPLAY}{BODY}{MONO}</style>'

    # Open Graph — kadr pod podgląd linku, więc treść trzyma się środka.
    html_to_png(
        f'{style}<div style="width:1200px;height:630px;background:{RED};position:relative;'
        f'display:flex;flex-direction:column;justify-content:center;padding:0 84px;'
        f"font-family:Plex,system-ui;box-sizing:border-box\">"
        f'<img src="file://{(SVG / "mark-white.svg").resolve()}" '
        f'style="position:absolute;right:-150px;top:50%;transform:translateY(-50%);'
        f'width:620px;opacity:.09">'
        f'<img src="file://{lockup}" style="width:470px;display:block;margin-bottom:30px">'
        f'<p style="margin:0;font-size:34px;line-height:1.34;color:rgba(255,255,255,.92);'
        f'max-width:15em;letter-spacing:-.01em;text-wrap:balance">'
        f'Uczymy maszyny poruszać się w świecie ludzi.</p>'
        f'<p style="margin:26px 0 0;font-family:PlexMono,monospace;font-size:17px;'
        f'letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.62)">'
        f'Kolektyw robotyki i AI · Wrocław</p></div>',
        SOCIAL / 'og-1200x630.png', 1200, 630)

    # LinkedIn: pas jest niski, a lewą trzecią zasłania awatar strony.
    html_to_png(
        f'{style}<div style="width:1128px;height:191px;background:{RED};position:relative;'
        f'display:flex;align-items:center;justify-content:flex-end;padding-right:60px;'
        f"font-family:Plex,system-ui;box-sizing:border-box\">"
        f'<img src="file://{(SVG / "mark-white.svg").resolve()}" '
        f'style="position:absolute;left:-90px;top:50%;transform:translateY(-50%);'
        f'width:300px;opacity:.1">'
        f'<p style="margin:0;font-size:27px;color:rgba(255,255,255,.94);letter-spacing:-.01em">'
        f'Uczymy maszyny poruszać się w świecie ludzi.</p></div>',
        SOCIAL / 'linkedin-baner-1128x191.png', 1128, 191)

    square(RED, 'mark-white.svg', 0.2, 400, SOCIAL / 'awatar-400.png')
    square(RED, 'mark-white.svg', 0.2, 1000, SOCIAL / 'awatar-1000.png')
    print('social: og, baner LinkedIn, awatar 400/1000')


if __name__ == '__main__':
    png_exports()
    favicons()
    social()
