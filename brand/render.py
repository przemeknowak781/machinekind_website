"""Wspólna rasteryzacja: HTML albo SVG → PNG w dokładnym kadrze.

Importowane przez skrypty budujące w `logo/` i `templates/`.

Chromium dostaje okno z zapasem, bo `--window-size` podaje rozmiar okna razem
z ramą, nie sam kadr; zrzut wraca potem do właściwych wymiarów przycięciem.
Ta sama pułapka co przy planszach — opisana w `slides/build.mjs`.
"""

import subprocess
import tempfile
from pathlib import Path

from PIL import Image

OVERSHOOT = 260


def find_chrome() -> str:
    import os
    import shutil

    if os.environ.get('CHROME_BIN'):
        return os.environ['CHROME_BIN']
    root = Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers'))
    if root.exists():
        builds = sorted(d for d in root.iterdir() if d.name.startswith('chromium-'))
        if builds:
            binary = builds[-1] / 'chrome-linux' / 'chrome'
            if binary.exists():
                return str(binary)
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit('Nie znaleziono Chrome ani Chromium. Ustaw CHROME_BIN.')


CHROME = find_chrome()


def html_to_png(html: str, out: Path, width: int, height: int, scale: int = 1,
                transparent: bool = False) -> Path:
    """Renderuje fragment HTML do PNG o dokładnych wymiarach width × height."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as fh:
        fh.write(f'<!doctype html><meta charset="utf-8">'
                 f'<body style="margin:0;width:{width}px;height:{height}px;overflow:hidden">'
                 f'{html}</body>')
        page = fh.name

    args = [CHROME, '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
            '--allow-file-access-from-files', f'--force-device-scale-factor={scale}',
            f'--window-size={width},{height + OVERSHOOT}', '--virtual-time-budget=8000',
            f'--screenshot={out}', f'file://{page}']
    if transparent:
        args.insert(1, '--default-background-color=00000000')
    subprocess.run(args, capture_output=True)

    shot = Image.open(out)
    want = (width * scale, height * scale)
    if shot.size != want:
        if shot.width != want[0] or shot.height < want[1]:
            raise SystemExit(f'{out.name}: zrzut {shot.size}, oczekiwano {want}')
        shot.crop((0, 0, *want)).save(out)
    return out


def svg_to_png(svg: Path, out: Path, width: int, height: int | None = None) -> Path:
    """Rasteryzuje plik SVG na przezroczystym tle."""
    box = height or _svg_height(svg, width)
    style = f'width:{width}px;height:{box}px'
    return html_to_png(f'<img src="file://{svg.resolve()}" style="{style};display:block">',
                       out, width, box, transparent=True)


def _svg_height(svg: Path, width: int) -> int:
    """Wysokość rastra wyliczona z viewBox, żeby kadr trzymał proporcje."""
    head = svg.read_text()[:400]
    box = head.split('viewBox="')[1].split('"')[0].split()
    ratio = float(box[3]) / float(box[2])
    return max(1, round(width * ratio))
