"""Scena dłoni w wektorze, złożona z oryginałów używanych przez stronę.

    python3 build-hands.py

Źródłem są `src/assets/hand-robot.svg` i `hand-human.svg` — jednościeżkowe
sylwetki w `currentColor`, które strona wstawia w treść (`HeroHands.astro`).
Nie ma powodu sięgać po `hands-ink.png`: raster jest w tym łańcuchu wynikiem,
nie źródłem.

Geometria sceny jest przeniesiona 1:1 z `scripts/brand.mjs`, które składa
wariant rastrowy: dłonie po 1900 jednostek szerokości, odstęp 150, opuszki
wyrównane w jednej linii poziomej, 24 jednostki luzu u góry i u dołu.
Ułamki położenia opuszka pochodzą z `scripts/hands-vector.mjs` — to te same
liczby, na których stoi układ nagłówka strony.

Scena wychodzi w trzech wariantach: `currentColor` do wstawienia w treść
oraz biały i atramentowy do użycia przez `<img>`, gdzie dziedziczenie koloru
nie działa. Warianty barwne lądują też w `slides/assets/`, bo plansze
składają się z własnego katalogu zasobów.
"""

import re
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
OUT = HERE / 'svg'

# Wartości z scripts/brand.mjs
HAND_W = 1900
GAP = 150
PAD = 24

# Ułamki pionowego położenia opuszka z scripts/hands-vector.mjs
TIP = {'robot': 0.3503, 'human': 0.3029}

SOURCES = {
    'robot': REPO / 'src/assets/hand-robot.svg',
    'human': REPO / 'src/assets/hand-human.svg',
}


def read_hand(path: Path) -> tuple[str, float, float]:
    """Zwraca (ścieżka, szerokość, wysokość) z pliku sylwetki."""
    svg = path.read_text()
    box = re.search(r'viewBox="([^"]+)"', svg).group(1).split()
    d = re.search(r'<path[^>]*\sd="([^"]+)"', svg).group(1)
    if svg.count('<path') != 1:
        raise SystemExit(f'{path.name}: oczekiwano jednej ścieżki, jest {svg.count("<path")}')
    return d, float(box[2]), float(box[3])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hands = {}
    for name, src in SOURCES.items():
        d, w, h = read_hand(src)
        scale = HAND_W / w
        hands[name] = {'d': d, 'w': w, 'h': h, 'scale': scale, 'height': h * scale}
        # Pojedyncza dłoń też trafia do paczki — przydaje się osobno.
        (OUT / f'dlon-{name}.svg').write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" '
            f'role="img" aria-labelledby="t"><title id="t">'
            f'{"Dłoń maszyny" if name == "robot" else "Dłoń człowieka"}</title>'
            f'<path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>\n')
        print(f'dlon-{name}.svg  {w:g} × {h:g} (proporcja {w / h:.3f})')

    tips = {n: TIP[n] * hands[n]['height'] for n in hands}
    meet = max(tips.values()) + PAD
    tops = {n: meet - tips[n] for n in hands}

    scene_w = HAND_W * 2 + GAP
    scene_h = max(tops[n] + hands[n]['height'] for n in hands) + PAD

    groups = []
    for name, left in (('robot', 0), ('human', HAND_W + GAP)):
        s = hands[name]['scale']
        groups.append(
            f'<g transform="translate({left:g} {tops[name]:.2f}) scale({s:.6f})">'
            f'<path d="{hands[name]["d"]}"/></g>')

    def scene(fill: str) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {scene_w:g} '
                f'{scene_h:.0f}" fill="{fill}" fill-rule="evenodd" role="img" '
                f'aria-labelledby="t"><title id="t">Dłoń maszyny i dłoń człowieka '
                f'wyciągnięte ku sobie</title>{"".join(groups)}</svg>\n')

    for suffix, fill in (('', 'currentColor'), ('-white', '#ffffff'), ('-ink', '#0d0f10')):
        (OUT / f'dlonie{suffix}.svg').write_text(scene(fill))

    # Plansze składają się z własnego katalogu zasobów, więc dostają kopię.
    slides = HERE.parent / 'slides/assets'
    for name, fill in (('hands-white.svg', '#ffffff'), ('hands-ink.svg', '#0d0f10')):
        (slides / name).write_text(scene(fill))

    print(f'dlonie.svg   {scene_w} × {scene_h:.0f} · styk w '
          f'{(HAND_W + GAP / 2) / scene_w * 100:.2f}% / {meet / scene_h * 100:.2f}%')
    print('warianty: currentColor, white, ink · kopie w slides/assets/')


if __name__ == '__main__':
    main()
