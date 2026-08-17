"""Eksport szablonów: grafiki do sieci, papier firmowy, podgląd podpisu.

    python3 build.py

Karty do sieci czyta z `social/index.html` — wymiary kadru niesie atrybut
`data-w`/`data-h` przy każdej karcie, więc dodanie nowej nie wymaga zmiany
w tym pliku.
"""

import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from render import CHROME, OVERSHOOT  # noqa: E402

SOCIAL = HERE / 'social'
SHEET = HERE / 'papier-firmowy'
SIGN = HERE / 'podpis-mailowy'


def shoot(url: str, out: Path, w: int, h: int, scale: int = 2):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', f'--force-device-scale-factor={scale}',
                    f'--window-size={w},{h + OVERSHOOT}', '--virtual-time-budget=9000',
                    f'--screenshot={out}', url], capture_output=True)
    want = (w * scale, h * scale)
    im = Image.open(out)
    if im.size != want:
        if im.width != want[0] or im.height < want[1]:
            raise SystemExit(f'{out.name}: zrzut {im.size}, oczekiwano {want}')
        im.crop((0, 0, *want)).save(out)
    return out


def social():
    html = (SOCIAL / 'index.html').read_text()
    cards = re.findall(r'data-name="([^"]+)" data-w="(\d+)" data-h="(\d+)"', html)
    if not cards:
        raise SystemExit('Nie znalazłem kart w social/index.html')
    out = SOCIAL / 'export'
    for i, (name, w, h) in enumerate(cards, start=1):
        w, h = int(w), int(h)
        shoot(f'file://{(SOCIAL / "index.html").resolve()}?only={i}',
              out / f'{name}-{w}x{h}.png', w, h)
        print(f'social → {name}-{w}x{h}.png')


def letterhead():
    """A4 w 192 dpi: zrzut 2× z kadru 794 × 1123 px daje dokładnie 210 × 297 mm."""
    out = SHEET / 'export'
    png = shoot(f'file://{(SHEET / "papier-firmowy.html").resolve()}',
                out / 'papier-firmowy.png', 794, 1123)
    Image.open(png).convert('RGB').save(out / 'papier-firmowy.pdf', 'PDF', resolution=192.0)
    print('papier firmowy → png + pdf (A4)')


def signature():
    """Podgląd podpisu — do sprawdzenia, jak wygląda, zanim trafi do klienta poczty."""
    out = SIGN / 'export'
    for name in ('podpis', 'podpis-tekstowy'):
        body = (SIGN / f'{name}.html').read_text()
        # Podgląd stawia znak z dysku; w prawdziwym podpisie musi tam stać adres publiczny.
        body = body.replace('ZNAK_URL', f'file://{(HERE.parent / "logo/png/mark-red-128.png").resolve()}')
        page = SIGN / f'.{name}-podglad.html'
        page.write_text(f'<!doctype html><meta charset="utf-8">'
                        f'<body style="margin:0;padding:34px;background:#fff">{body}</body>')
        shoot(f'file://{page.resolve()}', out / f'{name}.png', 560, 150, scale=2)
        page.unlink()
        print(f'podpis → {name}.png')


if __name__ == '__main__':
    social()
    letterhead()
    signature()
