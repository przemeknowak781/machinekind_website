"""Składa pliki znaku: sygnaturę słowną w krzywych i lockupy.

    python3 build-logo.py

Litery wychodzą z tego samego pliku kroju, którego używa strona
(`../slides/assets/fonts/big-shoulders-display-latin-wght-normal.woff2`),
zamienione na ścieżki — plik znaku nie może zależeć od kroju w systemie.
Proporcje lockupów są przeniesione 1:1 z układów, które już stoją na
planszach (`.lockup` i `.sig` w `../slides/assets/deck.css`), więc znak
w prezentacji i znak z tej paczki to ten sam znak.
"""

from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).parent
FONT = HERE.parent / 'slides/assets/fonts/big-shoulders-display-latin-wght-normal.woff2'
SVG_DIR = HERE / 'svg'

WORD = 'Machinekind'.upper()
WEIGHT = 500          # ta sama waga co w systemie strony

# Znak: kadr obrysu z build-mark (viewBox 1118 × 956).
MARK_W, MARK_H = 1118.0, 956.0
MARK_PATH = (SVG_DIR / 'mark-red.svg').read_text().split(' d="')[1].split('"')[0]

COLORS = {'red': '#bd3e3e', 'white': '#ffffff', 'ink': '#0d0f10', 'current': 'currentColor'}

# Proporcje z deck.css, liczone w szerokościach znaku:
#   .lockup  — img 48 px, gap 20 px, font-size 36 px
#   .sig     — img 300 px, gap 52 px, font-size 104 px
H_SIZE, H_GAP, H_TRACK = 36 / 48, 20 / 48, 0.055
V_SIZE, V_GAP, V_TRACK = 104 / 300, 52 / 300, 0.16


def load_font():
    return instantiateVariableFont(TTFont(FONT), {'wght': WEIGHT}, inplace=True,
                                   updateFontNames=False)


def kern_pairs(font, gids):
    """Wartości kerningu z GPOS dla kolejnych par — w jednostkach kroju."""
    gpos = font['GPOS'].table
    lookups = []
    for rec in gpos.FeatureList.FeatureRecord:
        if rec.FeatureTag == 'kern':
            lookups += list(rec.Feature.LookupListIndex)

    def value(a, b):
        total = 0
        for index in lookups:
            for sub in gpos.LookupList.Lookup[index].SubTable:
                sub = getattr(sub, 'ExtSubTable', sub)
                cov = getattr(sub, 'Coverage', None)
                if cov is None or a not in cov.glyphs:
                    continue
                if sub.Format == 1:
                    for pair in sub.PairSet[cov.glyphs.index(a)].PairValueRecord:
                        if pair.SecondGlyph == b and pair.Value1 and pair.Value1.XAdvance:
                            total += pair.Value1.XAdvance
                elif sub.Format == 2:
                    c1 = sub.ClassDef1.classDefs.get(a, 0)
                    c2 = sub.ClassDef2.classDefs.get(b, 0)
                    rec2 = sub.Class1Record[c1].Class2Record[c2]
                    if rec2.Value1 and rec2.Value1.XAdvance:
                        total += rec2.Value1.XAdvance
        return total

    return [value(gids[i], gids[i + 1]) for i in range(len(gids) - 1)]


def wordmark(font, size, tracking):
    """Zwraca (ścieżka, szerokość, wysokość wersalika) dla WORD przy danym stopniu."""
    upem = font['head'].unitsPerEm
    scale = size / upem
    cap = font['OS/2'].sCapHeight * scale
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    gids = [cmap[ord(ch)] for ch in WORD]
    kerns = kern_pairs(font, gids) + [0]
    track = tracking * size / scale          # światło międzyliterowe w jednostkach kroju

    parts, x = [], 0.0
    for gid, kern in zip(gids, kerns):
        pen = SVGPathPen(glyphs, ntos=lambda v: f'{v:.2f}')
        # Krój liczy Y w górę, SVG w dół — odbicie i przesunięcie o wysokość wersalika.
        tp = TransformPen(pen, Transform(scale, 0, 0, -scale, x * scale, cap))
        glyphs[gid].draw(tp)
        parts.append(pen.getCommands())
        x += glyphs[gid].width + kern + track
    width = (x - track) * scale              # ostatnia litera nie niesie światła z prawej
    return ' '.join(p for p in parts if p), width, cap


def svg(body, w, h, extra=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'role="img" aria-labelledby="t"{extra}><title id="t">Machinekind</title>'
            f'{body}</svg>\n')


def main():
    font = load_font()
    SVG_DIR.mkdir(parents=True, exist_ok=True)

    # ---- sama sygnatura słowna ----
    size = 1000.0
    path, w, cap = wordmark(font, size, H_TRACK)
    for name, fill in COLORS.items():
        (SVG_DIR / f'wordmark-{name}.svg').write_text(
            svg(f'<path fill="{fill}" d="{path}"/>', w, cap))
    print(f'wordmark    {w:.0f} × {cap:.0f}')

    # ---- lockup poziomy: znak i słowo w jednej linii ----
    size = MARK_W * H_SIZE
    path, w, cap = wordmark(font, size, H_TRACK)
    gap = MARK_W * H_GAP
    height = MARK_H
    y = (height - cap) / 2                   # wersalik centrowany na wysokości znaku
    total_w = MARK_W + gap + w
    for name, fill in COLORS.items():
        body = (f'<path fill="{fill}" fill-rule="evenodd" d="{MARK_PATH}"/>'
                f'<g transform="translate({MARK_W + gap:.2f} {y:.2f})">'
                f'<path fill="{fill}" d="{path}"/></g>')
        (SVG_DIR / f'lockup-poziomy-{name}.svg').write_text(svg(body, total_w, height))
    print(f'lockup poziomy  {total_w:.0f} × {height:.0f}')

    # ---- lockup pionowy: znak nad słowem ----
    size = MARK_W * V_SIZE
    path, w, cap = wordmark(font, size, V_TRACK)
    gap = MARK_W * V_GAP
    total_w = max(MARK_W, w)
    total_h = MARK_H + gap + cap
    mark_x = (total_w - MARK_W) / 2
    word_x = (total_w - w) / 2
    for name, fill in COLORS.items():
        body = (f'<g transform="translate({mark_x:.2f} 0)">'
                f'<path fill="{fill}" fill-rule="evenodd" d="{MARK_PATH}"/></g>'
                f'<g transform="translate({word_x:.2f} {MARK_H + gap:.2f})">'
                f'<path fill="{fill}" d="{path}"/></g>')
        (SVG_DIR / f'lockup-pionowy-{name}.svg').write_text(svg(body, total_w, total_h))
    print(f'lockup pionowy  {total_w:.0f} × {total_h:.0f}')

    # ---- sygnet: znak wpisany w kwadrat ----
    # Do awatarów, kafelków i wszędzie tam, gdzie kadr jest kwadratowy.
    side, pad = MARK_H * 1.6, 0.16
    inner = side * (1 - 2 * pad)
    s = inner / MARK_W
    for name, field, ink in (('czerwony', '#bd3e3e', '#ffffff'),
                             ('atrament', '#0d0f10', '#ffffff'),
                             ('bialy', '#ffffff', '#bd3e3e')):
        rect = (f'<rect width="{side:.0f}" height="{side:.0f}" fill="{field}"/>'
                if field != '#ffffff'
                else f'<rect x="0.5" y="0.5" width="{side - 1:.0f}" height="{side - 1:.0f}" '
                     f'fill="#ffffff" stroke="#d2d7d9"/>')
        body = (f'{rect}<g transform="translate({side * pad:.1f} '
                f'{(side - MARK_H * s) / 2:.1f}) scale({s:.4f})">'
                f'<path fill="{ink}" fill-rule="evenodd" d="{MARK_PATH}"/></g>')
        (SVG_DIR / f'sygnet-{name}.svg').write_text(svg(body, side, side))
    print(f'sygnet          {side:.0f} × {side:.0f}')


if __name__ == '__main__':
    main()
