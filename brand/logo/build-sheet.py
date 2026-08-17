"""Arkusz znaku: wszystkie warianty na jednej stronie A4.

    python3 build-sheet.py

Do wysłania komuś, kto pyta „macie logo?" — jeden plik zamiast katalogu.
Pod każdym wariantem stoi nazwa pliku, więc z arkusza da się od razu wskazać,
o który chodzi.
"""

import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from render import html_to_png  # noqa: E402

SVG = (HERE / 'svg').resolve()
FONTS = (HERE.parent / 'slides/assets/fonts').resolve()
W, H = 1123, 794


def face(family, file, weight):
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-display:block;"
            f"src:url('file://{FONTS / file}') format('woff2');}}")


STYLE = (face('BSD', 'big-shoulders-display-latin-wght-normal.woff2', '100 900') +
         face('BSD', 'big-shoulders-display-latin-ext-wght-normal.woff2', '100 900') +
         face('Plex', 'ibm-plex-sans-latin-wght-normal.woff2', '100 700') +
         face('Plex', 'ibm-plex-sans-latin-ext-wght-normal.woff2', '100 700') +
         face('Mono', 'ibm-plex-mono-latin-400-normal.woff2', '400') +
         face('Mono', 'ibm-plex-mono-latin-ext-400-normal.woff2', '400') + """
  *{box-sizing:border-box}
  body{margin:0;font-family:Plex,system-ui;color:#0d0f10}
  .sheet{width:1123px;height:794px;padding:56px 64px 48px;display:flex;
         flex-direction:column;background:#fff}
  .head{display:flex;justify-content:space-between;align-items:baseline;
        padding-bottom:12px;border-bottom:1px solid #e4e7e8}
  .foot{margin-top:auto;padding-top:12px;border-top:1px solid #e4e7e8;
        display:flex;justify-content:space-between}
  .mono{font-family:Mono,monospace;font-size:10px;letter-spacing:.16em;
        text-transform:uppercase;color:#6b7376;margin:0}
  h1{font-family:BSD,sans-serif;font-weight:500;font-size:48px;line-height:.96;
     letter-spacing:.012em;text-transform:uppercase;margin:16px 0 0}
  h1 span{color:#bd3e3e}
  /* Dwie kolumny: sześć rzędów jeden pod drugim nie mieści się na A4. */
  .rows{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
        gap:16px 32px;padding-top:18px}
  .row{display:grid;grid-template-columns:84px 1fr;gap:14px;align-items:center}
  .row__label{font-family:Mono,monospace;font-size:10px;letter-spacing:.14em;
              text-transform:uppercase;color:#0d0f10}
  .cells{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
  .cell{display:flex;flex-direction:column;gap:6px;align-items:flex-start}
  .box{display:flex;align-items:center;justify-content:center;padding:12px;
       border:1px solid #e4e7e8;min-height:70px}
  .box--red{background:#bd3e3e;border-color:#bd3e3e}
  .box--ink{background:#0d0f10;border-color:#0d0f10}
  .box--flat{border-style:none;padding:0}
  .name{font-family:Mono,monospace;font-size:9px;letter-spacing:.08em;color:#6b7376}
""")


def cell(file: str, width: int, tone: str = '') -> str:
    box = 'box' + (f' box--{tone}' if tone else '')
    return (f'<div class="cell"><div class="{box}">'
            f'<img src="file://{SVG / file}" style="width:{width}px;display:block"></div>'
            f'<p class="name">{file}</p></div>')


def row(label: str, cells: str) -> str:
    return f'<div class="row"><p class="row__label">{label}</p><div class="cells">{cells}</div></div>'


def main():
    body = (
        row('Znak',
            cell('mark-red.svg', 56) + cell('mark-white.svg', 56, 'red')
            + cell('mark-ink.svg', 56)) +
        row('Sygnet',
            cell('sygnet-czerwony.svg', 54) + cell('sygnet-atrament.svg', 54)
            + cell('sygnet-bialy.svg', 54)) +
        row('Lockup poziomy',
            cell('lockup-poziomy-red.svg', 190) + cell('lockup-poziomy-white.svg', 190, 'red')) +
        row('Z podpisem',
            cell('lockup-z-podpisem-red.svg', 190)
            + cell('lockup-z-podpisem-white.svg', 190, 'red')) +
        row('Lockup pionowy',
            cell('lockup-pionowy-red.svg', 74) + cell('lockup-pionowy-white.svg', 74, 'red')) +
        row('Dłonie', cell('dlonie-ink.svg', 200) + cell('dlonie-white.svg', 200, 'red'))
    )

    html = (f'<style>{STYLE}</style><div class="sheet">'
            f'<header class="head"><p class="mono">Arkusz znaku</p>'
            f'<p class="mono">Machinekind</p></header>'
            f'<h1>Logotypy<span>.</span></h1>'
            f'<div class="rows">{body}</div>'
            f'<footer class="foot"><p class="mono">Wektory: brand/logo/svg · '
            f'rastry: brand/logo/png</p>'
            f'<p class="mono">Zasady użycia: brand/brandbook</p></footer></div>')

    out = HERE / 'arkusz-znaku.png'
    probe = html.replace('</div>', '</div>', 1) + (
        '<script>document.fonts.ready.then(()=>{const s=document.querySelector(".sheet");'
        'document.title="FIT "+(s.scrollHeight-s.clientHeight)})</script>')
    check = HERE / '.arkusz-probe.html'
    check.write_text(f'<!doctype html><meta charset="utf-8"><body style="margin:0">{probe}</body>')
    import re as _re
    import subprocess as _sp
    from render import CHROME as _CH
    dom = _sp.run([_CH, '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                   '--allow-file-access-from-files', '--virtual-time-budget=9000',
                   '--dump-dom', f'file://{check.resolve()}'],
                  capture_output=True, text=True).stdout
    check.unlink()
    over = _re.search(r'<title>FIT (-?\d+)</title>', dom)
    if over and int(over.group(1)) > 1:
        raise SystemExit(f'Arkusz nie mieści treści — brakuje {over.group(1)} px wysokości.')
    print('kadr: arkusz mieści treść')

    html_to_png(html, out, W, H, scale=2)
    Image.open(out).convert('RGB').save(HERE / 'arkusz-znaku.pdf', 'PDF', resolution=192.0)
    print(f'arkusz-znaku.png / .pdf  {W} × {H} (A4 poziomo)')


if __name__ == '__main__':
    main()
