"""Tokeny marki w czterech formatach, wyprowadzone wprost z CSS strony.

    python3 build-tokens.py

Źródłem prawdy jest blok `:root` w `src/styles/global.css`. Skrypt go czyta,
grupuje tokeny i zapisuje `tokens.json`, `tokens.css`, `tokens.scss`
i `tokens.js`. Dzięki temu paczka marki nie może rozjechać się ze stroną:
zmiana w CSS i ponowne uruchomienie skryptu wystarczą.
"""

import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE.parent.parent / 'src/styles/global.css'

# Kolejność i opisy grup. Token, który nie pasuje do żadnego wzorca,
# ląduje w grupie „inne" — wtedy widać, że doszło coś nieopisanego.
GROUPS = [
    ('kolor-czerwien', 'Czerwień marki i jej warianty', r'^red'),
    ('kolor-atrament', 'Atrament: tekst i ciemne tła', r'^ink'),
    ('kolor-papier', 'Papier: jasne powierzchnie', r'^paper'),
    ('kolor-linie', 'Linie i hairline’y', r'^line'),
    ('kolor-na-ciemnym', 'Tekst na atramencie', r'^on-dark'),
    ('kolor-na-czerwieni', 'Tekst na czerwieni', r'^on-red'),
    ('typografia', 'Rodziny krojów', r'^(display|body|mono)$'),
    ('miara', 'Miara, marginesy, rytm sekcji', r'^(wrap|gutter|section-y|micro)$'),
    ('ruch', 'Krzywa czasowa przejść', r'^ease$'),
]


def read_root(css: str) -> dict[str, str]:
    block = re.search(r':root\s*\{(.*?)\n\}', css, re.S)
    if not block:
        raise SystemExit(f'Nie znalazłem bloku :root w {SOURCE}')
    return dict(re.findall(r'--([\w-]+)\s*:\s*([^;]+);', block.group(1)))


def group_of(name: str) -> str:
    for key, _, pattern in GROUPS:
        if re.search(pattern, name):
            return key
    return 'inne'


def main():
    tokens = {k: ' '.join(v.split()) for k, v in read_root(SOURCE.read_text()).items()}
    grouped: dict[str, dict[str, str]] = {}
    for name, value in tokens.items():
        grouped.setdefault(group_of(name), {})[name] = value

    order = [g[0] for g in GROUPS] + ['inne']
    labels = {g[0]: g[1] for g in GROUPS} | {'inne': 'Pozostałe'}
    grouped = {k: grouped[k] for k in order if k in grouped}

    stamp = (f'Wygenerowane z {SOURCE.name} przez brand/tokens/build-tokens.py — '
             f'{date.today().isoformat()}. Nie edytuj ręcznie.')

    # ---- JSON ----
    (HERE / 'tokens.json').write_text(json.dumps(
        {'$opis': stamp,
         'grupy': {k: {'opis': labels[k], 'tokeny': v} for k, v in grouped.items()}},
        ensure_ascii=False, indent=2) + '\n')

    # ---- CSS ----
    css = [f'/* {stamp} */', '', ':root {']
    for key, items in grouped.items():
        css.append(f'  /* {labels[key]} */')
        css += [f'  --{n}: {v};' for n, v in items.items()]
        css.append('')
    css[-1] = '}'
    (HERE / 'tokens.css').write_text('\n'.join(css) + '\n')

    # ---- SCSS ----
    scss = [f'// {stamp}', '']
    for key, items in grouped.items():
        scss.append(f'// {labels[key]}')
        scss += [f'${n}: {v};' for n, v in items.items()]
        scss.append('')
    (HERE / 'tokens.scss').write_text('\n'.join(scss))

    # ---- JS ----
    js = [f'// {stamp}', '', 'export const tokens = {']
    for key, items in grouped.items():
        js.append(f'  // {labels[key]}')
        js += [f"  '{n}': {json.dumps(v, ensure_ascii=False)}," for n, v in items.items()]
    js += ['}', '', 'export default tokens', '']
    (HERE / 'tokens.js').write_text('\n'.join(js))

    total = sum(len(v) for v in grouped.values())
    print(f'{total} tokenów w {len(grouped)} grupach → json, css, scss, js')
    for key, items in grouped.items():
        print(f'  {key:22} {len(items)}')


if __name__ == '__main__':
    main()
