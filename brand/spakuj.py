"""Archiwa paczki marki do przekazania na zewnątrz.

    python3 spakuj.py

Powstają trzy pliki w `dist/`:

  machinekind-marka-<data>.zip          komplet, w układzie czytelnym dla człowieka
  machinekind-logotypy-<data>.zip       sam znak
  machinekind-design-system-<data>.zip  sam system z krojami

Układ w archiwum nie odwzorowuje repozytorium, tylko sposób, w jaki ktoś
tych plików szuka: ponumerowane foldery od księgi znaku po kroje. Nikogo
poza repozytorium nie obchodzi, że plansze leżą w `slides/export/png`.

Do środka wchodzą pliki gotowe do użycia i dokumentacja. Nie wchodzą źródła
pośrednie ani skrypty budujące — osoba, która dostaje paczkę, ma otworzyć
plik, a nie uruchamiać Pythona. Wersje z historią zostają w repo.
"""

import zipfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DIST = HERE / 'dist'
STAMP = date.today().isoformat()

# (wzorzec źródłowy, folder docelowy w archiwum)
# Kolejność wyznacza układ wykazu; numery w nazwach folderów utrzymują
# porządek na liście plików w każdym systemie.
FULL = [
    ('CZYTAJ-TO-NAJPIERW.txt', ''),
    ('README.md', ''),

    ('brandbook/export/machinekind-ksiega-znaku.pdf', '01 Ksiega znaku'),
    ('brandbook/export/machinekind-ksiega-znaku.html', '01 Ksiega znaku'),

    ('logo/README.md', '02 Logotypy'),
    ('logo/arkusz-znaku.pdf', '02 Logotypy'),
    ('logo/arkusz-znaku.png', '02 Logotypy'),
    ('logo/svg/*.svg', '02 Logotypy/SVG (wektor)'),
    ('logo/png/*.png', '02 Logotypy/PNG'),
    ('logo/favicon/*', '02 Logotypy/Favicon i ikony'),
    ('logo/social/*.png', '02 Logotypy/Social (OG, banery, awatar)'),

    ('design-system/README.md', '03 Design system'),
    ('design-system/system.css', '03 Design system'),
    ('design-system/components.css', '03 Design system'),
    ('design-system/index.html', '03 Design system'),
    ('design-system/export/machinekind-design-system.html', '03 Design system'),

    ('tokens/README.md', '04 Tokeny'),
    ('tokens/tokens.json', '04 Tokeny'),
    ('tokens/tokens.css', '04 Tokeny'),
    ('tokens/tokens.scss', '04 Tokeny'),
    ('tokens/tokens.js', '04 Tokeny'),

    ('slides/README.md', '05 Plansze prezentacyjne'),
    ('slides/export/machinekind-plansze.pptx', '05 Plansze prezentacyjne'),
    ('slides/export/machinekind-plansze.pdf', '05 Plansze prezentacyjne'),
    ('slides/export/machinekind-plansze.html', '05 Plansze prezentacyjne'),
    ('slides/export/png/*.png', '05 Plansze prezentacyjne/Plansze PNG'),

    ('templates/README.md', '06 Szablony'),
    ('templates/social/export/*.png', '06 Szablony/Posty i relacje'),
    ('templates/papier-firmowy/papier-firmowy.html', '06 Szablony/Papier firmowy'),
    ('templates/papier-firmowy/export/*', '06 Szablony/Papier firmowy'),
    ('templates/podpis-mailowy/*.html', '06 Szablony/Podpis mailowy'),
    ('templates/podpis-mailowy/export/*.png', '06 Szablony/Podpis mailowy/podglad'),

    ('fonts/README.md', '07 Kroje'),
    ('fonts/pliki/*.woff2', '07 Kroje/pliki'),
    ('fonts/licencje/*.txt', '07 Kroje/licencje'),
]

SETS = {
    'logotypy': [
        ('logo/README.md', ''),
        ('logo/arkusz-znaku.pdf', ''),
        ('logo/arkusz-znaku.png', ''),
        ('logo/svg/*.svg', 'SVG (wektor)'),
        ('logo/png/*.png', 'PNG'),
        ('logo/favicon/*', 'Favicon i ikony'),
        ('logo/social/*.png', 'Social (OG, banery, awatar)'),
    ],
    'design-system': [
        ('design-system/README.md', ''),
        ('design-system/system.css', ''),
        ('design-system/components.css', ''),
        ('design-system/index.html', ''),
        ('design-system/export/machinekind-design-system.html', ''),
        ('tokens/README.md', 'Tokeny'),
        ('tokens/tokens.json', 'Tokeny'),
        ('tokens/tokens.css', 'Tokeny'),
        ('tokens/tokens.scss', 'Tokeny'),
        ('tokens/tokens.js', 'Tokeny'),
        ('fonts/README.md', 'Kroje'),
        ('fonts/pliki/*.woff2', 'Kroje/pliki'),
        ('fonts/licencje/*.txt', 'Kroje/licencje'),
    ],
}


def collect(plan: list[tuple[str, str]]) -> list[tuple[Path, str]]:
    """Zwraca pary (plik na dysku, ścieżka w archiwum)."""
    out: list[tuple[Path, str]] = []
    for pattern, folder in plan:
        if '*' in pattern:
            found = sorted(f for f in HERE.glob(pattern) if f.is_file())
            if not found:
                raise SystemExit(f'Nic nie pasuje do {pattern} — uruchom najpierw eksporty.')
            out += [(f, f'{folder}/{f.name}' if folder else f.name) for f in found]
        else:
            path = HERE / pattern
            if not path.exists():
                raise SystemExit(f'Brak {pattern} — uruchom najpierw eksporty.')
            out.append((path, f'{folder}/{path.name}' if folder else path.name))
    return out


def pack(name: str, items: list[tuple[Path, str]], root: str):
    out = DIST / name
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for source, target in items:
            zf.write(source, f'{root}/{target}')

    # Sprawdzenie archiwum: nazwy bez duplikatów i całość odczytywalna.
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise SystemExit(f'{name}: zduplikowane ścieżki w archiwum.')
        broken = zf.testzip()
        if broken:
            raise SystemExit(f'{name}: uszkodzony wpis {broken}')
    folders = len({n.rsplit('/', 1)[0] for n in names})
    print(f'{out.relative_to(HERE)} — {len(items)} plików w {folders} folderach, '
          f'{out.stat().st_size / 1e6:.1f} MB')


def main():
    DIST.mkdir(exist_ok=True)
    pack(f'machinekind-marka-{STAMP}.zip', collect(FULL), 'Branding Machinekind')
    for name, plan in SETS.items():
        pack(f'machinekind-{name}-{STAMP}.zip', collect(plan), f'Machinekind — {name}')


if __name__ == '__main__':
    main()
