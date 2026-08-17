"""Kontrast wszystkich par barw, które realnie występują w systemie.

    python3 contrast.py            # tabela na wyjście
    python3 contrast.py --json     # do wczytania przez generator brandbooka

Półprzezroczyste tokeny (--on-dark-*, --on-red-*) są najpierw składane z tłem,
na którym stoją — inaczej liczba nie znaczy nic. Progi WCAG 2.1: 4,5:1 dla
tekstu zwykłego, 3:1 dla dużego (od 24 px, albo 18,7 px w wersji półgrubej)
i dla elementów nietekstowych.
"""

import json
import re
import sys
from pathlib import Path

TOKENS = json.loads((Path(__file__).parent / 'tokens.json').read_text())
T = {n: v for g in TOKENS['grupy'].values() for n, v in g['tokeny'].items()}


def rgb(value: str) -> tuple[float, float, float]:
    value = value.strip()
    if value.startswith('#'):
        h = value[1:]
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r'rgba?\(([^)]+)\)', value)
    parts = [p.strip() for p in m.group(1).replace('/', ',').split(',')]
    return tuple(float(p) for p in parts[:3])


def alpha_of(value: str) -> float:
    m = re.match(r'rgba\(([^)]+)\)', value.strip())
    if not m:
        return 1.0
    parts = [p.strip() for p in m.group(1).split(',')]
    return float(parts[3]) if len(parts) > 3 else 1.0


def over(fg: str, bg: str) -> tuple[float, float, float]:
    """Składa półprzezroczysty kolor z tłem."""
    a = alpha_of(fg)
    f, b = rgb(fg), rgb(bg)
    return tuple(a * f[i] + (1 - a) * b[i] for i in range(3))


def luminance(c: tuple[float, float, float]) -> float:
    def channel(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    a, b = luminance(over(fg, bg)), luminance(rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# (tekst, tło, opis zastosowania)
PAIRS = [
    ('ink', 'paper', 'tytuły i tekst na bieli'),
    ('ink-1', 'paper', 'tekst drugorzędny na bieli'),
    ('ink-2', 'paper', 'akapit na bieli'),
    ('ink-3', 'paper', 'podpis, monospace na bieli'),
    ('red', 'paper', 'akcent i tytuły w czerwieni na bieli'),
    ('red-deep', 'paper', 'czerwień na bieli przy drobnym stopniu'),
    ('ink', 'paper-2', 'tekst na szarej powierzchni'),
    ('ink-2', 'paper-2', 'akapit na szarej powierzchni'),
    ('paper', 'red', 'biel na czerwieni'),
    ('on-red-2', 'red', 'akapit na czerwieni'),
    ('ink', 'red', 'akcent atramentem na czerwieni'),
    ('paper', 'ink', 'biel na atramencie'),
    ('on-dark-1', 'ink', 'tytuł na atramencie'),
    ('on-dark-2', 'ink', 'akapit na atramencie'),
    ('on-dark-3', 'ink', 'podpis na atramencie'),
    ('red', 'ink', 'czerwień na atramencie'),
    ('red-soft', 'ink', 'czerwień jasna na atramencie'),
    ('red', 'red-wash', 'czerwień na swoim tle rozmytym'),
]


def verdict(r: float) -> str:
    if r >= 7:
        return 'AAA'
    if r >= 4.5:
        return 'AA'
    if r >= 3:
        return 'AA duży'
    return 'poniżej progu'


def rows():
    out = []
    for fg, bg, use in PAIRS:
        r = ratio(T[fg], T[bg])
        out.append({'fg': fg, 'bg': bg, 'use': use,
                    'ratio': round(r, 2), 'verdict': verdict(r)})
    return out


if __name__ == '__main__':
    data = rows()
    if '--json' in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f'{"tekst":12} {"tło":10} {"kontrast":>9}  {"próg":<12} zastosowanie')
        print('-' * 84)
        for d in data:
            print(f'{d["fg"]:12} {d["bg"]:10} {d["ratio"]:8.2f}:1  {d["verdict"]:<12} {d["use"]}')
        weak = [d for d in data if d['ratio'] < 4.5]
        print(f'\nponiżej 4,5:1 — {len(weak)} par, wolno ich użyć tylko w dużym stopniu:')
        for d in weak:
            print(f'  {d["fg"]} na {d["bg"]}: {d["ratio"]}:1 ({d["use"]})')
