"""Archiwum paczki marki do przekazania na zewnątrz.

    python3 spakuj.py

Do środka wchodzą pliki gotowe do użycia i dokumentacja. Nie wchodzą źródła
pośrednie, katalogi robocze ani skrypty budujące — osoba, która dostaje paczkę,
ma otworzyć plik, a nie uruchamiać Pythona. Wersje z historią zostają w repo.
"""

import zipfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'dist' / f'machinekind-marka-{date.today().isoformat()}.zip'

# (wzorzec, opis w wykazie) — kolejność wyznacza układ archiwum
INCLUDE = [
    'README.md',
    'brandbook/export/machinekind-ksiega-znaku.pdf',
    'brandbook/export/machinekind-ksiega-znaku.html',
    'logo/README.md',
    'logo/arkusz-znaku.pdf',
    'logo/arkusz-znaku.png',
    'logo/svg/*.svg',
    'logo/png/*.png',
    'logo/favicon/*',
    'logo/social/*.png',
    'tokens/README.md',
    'tokens/tokens.json',
    'tokens/tokens.css',
    'tokens/tokens.scss',
    'tokens/tokens.js',
    'design-system/README.md',
    'design-system/system.css',
    'design-system/index.html',
    'design-system/export/machinekind-design-system.html',
    'slides/README.md',
    'slides/export/machinekind-plansze.pdf',
    'slides/export/machinekind-plansze.pptx',
    'slides/export/machinekind-plansze.html',
    'slides/export/png/*.png',
    'templates/README.md',
    'templates/social/export/*.png',
    'templates/papier-firmowy/papier-firmowy.html',
    'templates/papier-firmowy/export/*',
    'templates/podpis-mailowy/*.html',
    'fonts/README.md',
    'fonts/pliki/*.woff2',
    'fonts/licencje/*.txt',
]


SETS = {
    'logotypy': ['logo/README.md', 'logo/arkusz-znaku.pdf', 'logo/arkusz-znaku.png',
                 'logo/svg/*.svg', 'logo/png/*.png', 'logo/favicon/*', 'logo/social/*.png'],
    'design-system': ['design-system/README.md', 'design-system/system.css',
                      'design-system/components.css', 'design-system/index.html',
                      'design-system/export/machinekind-design-system.html',
                      'tokens/README.md', 'tokens/tokens.json', 'tokens/tokens.css',
                      'tokens/tokens.scss', 'tokens/tokens.js',
                      'fonts/README.md', 'fonts/pliki/*.woff2', 'fonts/licencje/*.txt'],
}


def collect(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        if '*' in pattern:
            found = sorted(HERE.glob(pattern))
            if not found:
                raise SystemExit(f'Nic nie pasuje do {pattern} — uruchom najpierw eksporty.')
            files += [f for f in found if f.is_file()]
        else:
            path = HERE / pattern
            if not path.exists():
                raise SystemExit(f'Brak {pattern} — uruchom najpierw eksporty.')
            files.append(path)
    return files


def pack(name: str, files: list[Path], root: str):
    out = OUT.parent / name
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in files:
            zf.write(f, Path(root) / f.relative_to(HERE))
    print(f'{out.relative_to(HERE)} — {len(files)} plików, {out.stat().st_size / 1e6:.1f} MB')


def main():
    OUT.parent.mkdir(exist_ok=True)
    pack(OUT.name, collect(INCLUDE), 'machinekind-marka')
    for name, patterns in SETS.items():
        pack(f'machinekind-{name}-{date.today().isoformat()}.zip',
             collect(patterns), f'machinekind-{name}')


if __name__ == '__main__':
    main()
