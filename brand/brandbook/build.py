"""Księga znaku: składa index.html, zrzuty stron, PDF i wersję jednoplikową.

    python3 build.py

Dokument jest generowany, nie pisany ręcznie — paleta, tabela kontrastu i skala
typograficzna wychodzą z `brand/tokens`, więc księga nie może rozminąć się
z kodem strony. Treść rozdziałów leży niżej w tym pliku, w stałych PAGES.
"""

import base64
import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
BRAND = HERE.parent
sys.path.insert(0, str(BRAND))
from render import CHROME, OVERSHOOT  # noqa: E402

PAGE_W, PAGE_H = 1123, 794
EXPORT = HERE / 'export'
THUMBS = HERE / 'thumbs'

TOKENS = json.loads((BRAND / 'tokens/tokens.json').read_text())
T = {n: v for g in TOKENS['grupy'].values() for n, v in g['tokeny'].items()}

spec = importlib.util.spec_from_file_location('contrast', BRAND / 'tokens/contrast.py')
contrast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contrast)
CONTRAST = contrast.rows()

MARK = '../logo/svg'
WERSJA = f'wyd. 1 · {date.today().strftime("%m.%Y")}'


# ============================================================
# Elementy powtarzalne
# ============================================================

def page(body: str, *, tone: str = '', head: str = '', foot_l: str = '',
         klass: str = '', wm: str = '') -> str:
    tone_cls = f' page--{tone}' if tone else ''
    mark = 'mark-white.svg' if tone in ('red', 'ink') else 'mark-red.svg'
    watermark = f'<img class="wm" src="{MARK}/{wm}" alt="">' if wm else ''
    header = (f'<header class="head"><p class="mono">{head}</p>'
              f'<p class="mono">Machinekind · księga znaku</p></header>') if head else ''
    footer = (f'<footer class="foot"><p class="mono">{foot_l}</p>'
              f'<p class="mono">{WERSJA}</p></footer>')
    return (f'<section class="page{tone_cls} {klass}">{watermark}{header}'
            f'<div class="main">{body}</div>{footer}</section>')


def title(text: str, dot: bool = True) -> str:
    end = '<span class="dot">.</span>' if dot else ''
    return f'<h2 class="h-page">{text}{end}</h2>'


def swatches(names: list[str]) -> str:
    cells = []
    for n in names:
        value = T[n]
        border = ';border-color:var(--line-2)' if n in ('paper',) else ''
        cells.append(
            f'<div><div class="sw__chip" style="background:{value}{border}"></div>'
            f'<p class="sw__name">{ROLE[n][0]}</p>'
            f'<p class="mono sw__meta">{value} · --{n}</p></div>')
    return f'<div class="swatches">{"".join(cells)}</div>'


ROLE = {
    'red': ('Czerwień marki', 'Prowadzi. Pełne pola, akcenty, znak.'),
    'red-deep': ('Czerwień głęboka', 'Drobny tekst w czerwieni na bieli.'),
    'red-soft': ('Czerwień jasna', 'Akcent na atramencie — czerwień marki jest tam za ciemna.'),
    'red-wash': ('Czerwień rozmyta', 'Tło wydzielonego bloku.'),
    'ink': ('Atrament', 'Tytuły i tekst na bieli, ciemne pola.'),
    'ink-1': ('Atrament 1', 'Tekst drugorzędny.'),
    'ink-2': ('Atrament 2', 'Akapit.'),
    'ink-3': ('Atrament 3', 'Podpis, monospace. Próg 4,8:1 na bieli.'),
    'paper': ('Papier', 'Tło dominujące.'),
    'paper-2': ('Papier 2', 'Powierzchnia wydzielona.'),
    'paper-3': ('Papier 3', 'Powierzchnia głębsza.'),
    'line': ('Linia', 'Hairline podstawowy.'),
    'line-2': ('Linia 2', 'Hairline mocniejszy, obrys.'),
}


def contrast_table(subset=None) -> str:
    rows = ''.join(
        f'<tr><td class="tok">--{d["fg"]}</td><td class="tok">--{d["bg"]}</td>'
        f'<td class="num">{d["ratio"]:.2f}:1</td><td class="num">{d["verdict"]}</td>'
        f'<td>{d["use"]}</td></tr>' for d in (subset or CONTRAST))
    return (f'<table class="table--tight"><thead><tr><th>Tekst</th><th>Tło</th>'
            f'<th>Kontrast</th><th>Próg</th><th>Zastosowanie</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


def panel(inner: str, label: str, ok: bool = False) -> str:
    cls = 'panel panel--ok' if ok else 'panel'
    return (f'<div class="{cls}"><div class="panel__box">{inner}</div>'
            f'<p class="panel__label">{label}</p></div>')


# ============================================================
# Strony
# ============================================================

def build_pages() -> list[tuple[str, str]]:
    """Zwraca listę (nazwa pliku, html strony)."""
    p: list[tuple[str, str]] = []

    # ---- 01 okładka ----
    p.append(('01-okladka', (
        f'<section class="page page--red cover">'
        f'<img class="wm" src="{MARK}/mark-white.svg" alt="">'
        f'<img class="cover__mark" src="{MARK}/mark-white.svg" alt="">'
        f'<div><h1 class="h-cover">Księga<br>znaku</h1>'
        f'<p class="lead" style="margin-top:22px">System wizualny Machinekind: znak, '
        f'kolor, typografia, układ i głos. Wszystko, co trzeba wiedzieć, żeby zrobić '
        f'nowy materiał i żeby wyglądał jak nasz.</p></div>'
        f'<footer class="foot"><p class="mono">Kolektyw robotyki i AI · Wrocław</p>'
        f'<p class="mono">{WERSJA}</p></footer></section>')))

    # ---- 02 o dokumencie ----
    # Numery stron liczy się z gotowej listy (niżej), bo wpisane ręcznie
    # rozjeżdżały się przy każdym dołożeniu rozdziału.
    p.append(('02-o-dokumencie', page(
        title('Co jest w środku') +
        '<p class="lead">Księga opisuje decyzje, które już stoją w kodzie strony '
        'i w materiałach. Każda liczba tu podana jest wzięta z plików, nie ustalona '
        'na potrzeby dokumentu — paleta i tabela kontrastu są generowane wprost '
        'z tokenów przy każdym złożeniu tej księgi.</p>'
        '<table><thead><tr><th>Str.</th><th>Rozdział</th><th>Zakres</th></tr></thead>'
        '<tbody>{{SPIS}}</tbody></table>',
        head='O dokumencie', foot_l='Machinekind')))

    # ---- 03 marka ----
    p.append(('03-marka', page(
        title('Kim jesteśmy') +
        '<p class="lead">Machinekind jest niezależnym kolektywem robotyki i AI '
        'z Wrocławia. Budujemy warstwę inteligencji razem ze sprzętem, na którym '
        'da się ją uruchomić.</p>'
        '<div class="cols cols--3">'
        '<div class="stack-sm"><h3 class="h-sub">Budujemy, nie doradzamy.</h3>'
        '<p class="body">Każda domena kończy się czymś, co się uruchamia. '
        'Nie oddajemy prezentacji.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Inteligencja powstaje razem ze sprzętem.</h3>'
        '<p class="body">Jeden zespół prowadzi drogę od zamiaru po moment na wale.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Pierwsza maszyna już chodzi.</h3>'
        '<p class="body">W01-TEK nie jest wizualizacją. Jest bazą platformy.</p></div>'
        '</div>'
        '<p class="body" style="max-width:70ch">Zdanie, którym marka przedstawia się '
        'najkrócej: <strong>Uczymy maszyny poruszać się w świecie ludzi.</strong> '
        'Wolno go używać jako podpisu pod znakiem i jako jedynej treści planszy.</p>',
        head='Marka', foot_l='Machinekind', wm='mark-red.svg')))

    # ---- 04 znak: warianty ----
    variants = ''.join(
        f'<div class="panel"><div class="panel__box" style="background:{bg}">'
        f'<img src="{MARK}/{f}" style="width:118px"></div>'
        f'<p class="mono">{name}</p><p class="body" style="font-size:12.5px">{note}</p></div>'
        for f, bg, name, note in [
            ('mark-red.svg', 'var(--paper)', 'mark-red', 'Podstawowy. Na bieli i na jasnych powierzchniach.'),
            ('mark-white.svg', 'var(--red)', 'mark-white', 'Na czerwieni, atramencie i na zdjęciu.'),
            ('mark-ink.svg', 'var(--paper)', 'mark-ink', 'Druk jednobarwny, faks, pieczątka.'),
            ('mark-current.svg', 'var(--paper-2)', 'mark-current', 'Dziedziczy kolor z otoczenia (currentColor).'),
        ])
    p.append(('04-znak-warianty', page(
        title('Znak') +
        '<p class="lead">Sześciobok z węzłem w środku. Znak stoi sam albo w lockupie '
        'ze słowem MACHINEKIND — poziomym, kiedy jest szerokość, pionowym, kiedy '
        'kadr jest wąski albo kwadratowy.</p>'
        f'<div class="panels">{variants}</div>'
        '<p class="body" style="max-width:74ch">Pliki wektorowe leżą w '
        '<code>logo/svg/</code>, rastry w <code>logo/png/</code>. Do nowych materiałów '
        'zawsze bierz wektor — raster jest tylko dla narzędzi, które SVG nie przyjmują.</p>',
        head='Znak · warianty', foot_l='logo/svg')))

    # ---- 05 lockupy ----
    p.append(('05-znak-lockupy', page(
        title('Lockupy') +
        '<p class="lead">Proporcje lockupów są stałe i wynikają z układów, które stoją '
        'na planszach. Nie składaj znaku ze słowem na nowo — weź gotowy plik.</p>'
        '<div class="cols cols--2" style="align-items:center">'
        f'<div><img src="{MARK}/lockup-poziomy-red.svg" style="width:100%;max-width:420px">'
        '<p class="mono" style="margin-top:16px">lockup poziomy</p>'
        '<p class="body" style="font-size:13px">Odstęp między znakiem a słowem to 0,42 '
        'szerokości znaku. Wersalik słowa jest wyśrodkowany na wysokości znaku.</p></div>'
        f'<div style="display:flex;flex-direction:column;align-items:flex-start">'
        f'<img src="{MARK}/lockup-pionowy-red.svg" style="width:190px">'
        '<p class="mono" style="margin-top:16px">lockup pionowy</p>'
        '<p class="body" style="font-size:13px">Słowo pod znakiem, światło międzyliterowe '
        '0,16 em. Do kadrów kwadratowych: awatar, plansza postojowa, naklejka.</p></div>'
        '</div>'
        '<p class="body" style="max-width:74ch">Litery w plikach są zamienione na krzywe, '
        'więc lockup nie zależy od kroju zainstalowanego w systemie. Nie składaj go '
        'żywym tekstem — inna waga albo inny fallback zmieni proporcje.</p>',
        head='Znak · lockupy', foot_l='logo/svg')))

    # ---- 06 pole ochronne ----
    p.append(('06-znak-pole', page(
        title('Pole ochronne') +
        '<p class="lead">Wokół znaku zostaje puste pole o szerokości <strong>x</strong>, '
        'gdzie x to jedna szósta szerokości znaku. W tym polu nie stoi nic: ani tekst, '
        'ani krawędź kadru, ani cudzy logotyp.</p>'
        '<div class="cols cols--2" style="align-items:center">'
        '<div style="--markw:180px;--x:30px">'
        '<div class="clear"><div class="clear__inner">'
        '<img src="' + MARK + '/mark-red.svg" alt=""></div></div></div>'
        '<div class="stack-sm">'
        '<h3 class="h-sub">Skąd x</h3>'
        '<p class="body">Znak ma 1118 × 956 jednostek w kadrze SVG. x = 1118 / 6 ≈ 186 '
        'jednostek, czyli 0,166 szerokości znaku. Przy znaku 48 px pole ochronne ma 8 px.</p>'
        '<h3 class="h-sub" style="margin-top:8px">W lockupie</h3>'
        '<p class="body">Pole liczy się od skrajnych krawędzi całego lockupu, nie od '
        'samego sześcioboku.</p></div></div>',
        head='Znak · pole ochronne', foot_l='x = 1/6 szerokości znaku')))

    # ---- 07 rozmiary ----
    sizes = ''.join(
        f'<div style="text-align:center"><img src="{MARK}/mark-red.svg" style="width:{w}px">'
        f'<p class="mono size__label">{w} px</p></div>' for w in (96, 64, 48, 32))
    p.append(('07-znak-rozmiary', page(
        title('Minimalne rozmiary') +
        '<p class="lead">Kreska węzła jest cienka. Poniżej 32 px szerokości znak przestaje '
        'być czytelny i zlewa się w plamę — wtedy zamiast niego wchodzi ikona: biały znak '
        'na czerwonym polu.</p>'
        f'<div class="sizes">{sizes}</div>'
        '<div class="cols cols--2">'
        '<div class="stack-sm"><h3 class="h-sub">Ekran</h3>'
        '<p class="body">Znak samodzielny: nie mniej niż <strong>32 px</strong> szerokości. '
        'Lockup poziomy: nie mniej niż <strong>140 px</strong>. Poniżej — ikona '
        'z <code>logo/favicon/</code>.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Druk</h3>'
        '<p class="body">Znak samodzielny: nie mniej niż <strong>8 mm</strong> szerokości. '
        'Lockup poziomy: nie mniej niż <strong>34 mm</strong>.</p></div></div>',
        head='Znak · rozmiary', foot_l='logo/favicon')))

    # ---- 08 czego nie robimy ----
    m = f'<img src="{MARK}/mark-red.svg" style="width:96px">'
    donts = ''.join([
        panel(f'<img src="{MARK}/mark-red.svg" style="width:130px;height:60px">',
              'Nie zmieniaj proporcji. Znak skaluje się tylko równomiernie.'),
        panel('<div style="background:#2f6bbd;padding:14px;display:flex">'
              f'<img src="{MARK}/mark-white.svg" style="width:88px"></div>',
              'Nie przebarwiaj. Znak ma cztery warianty i żadnego więcej.'),
        panel('<div style="background:var(--red);padding:14px;display:flex">'
              '<div style="outline:1px dashed rgba(255,255,255,.5);display:flex">'
              f'<img src="{MARK}/mark-red.svg" style="width:96px"></div></div>',
              'Nie stawiaj czerwonego znaku na czerwieni. Obrys pokazuje, gdzie stoi.'),
        panel(f'<div style="transform:rotate(-14deg)">{m}</div>',
              'Nie obracaj. Sześciobok stoi zawsze tak samo.'),
        panel(f'<div style="display:flex;align-items:center;gap:5px">{m}'
              '<span style="font:500 15px/1 var(--sans)">Machinekind</span></div>',
              'Nie składaj własnego lockupu. Są gotowe pliki.'),
        panel(f'<div style="filter:drop-shadow(0 6px 8px rgba(0,0,0,.45))">{m}</div>',
              'Nie dodawaj cienia, poświaty ani obrysu.'),
        panel('<div style="background:linear-gradient(45deg,#888,#ddd,#555);padding:14px;display:flex">'
              f'<img src="{MARK}/mark-white.svg" style="width:88px"></div>',
              'Nie stawiaj na niespokojnym tle bez wyrównania kontrastu.'),
        panel(f'<div style="background:var(--paper);padding:14px;display:flex">'
              f'<img src="{MARK}/mark-red.svg" style="width:96px"></div>',
              'Tak: pełny kontrast, pion, równa skala, wolne pole.', ok=True),
    ])
    p.append(('08-znak-zakazy', page(
        title('Czego ze znakiem nie robimy') +
        f'<div class="panels">{donts}</div>',
        head='Znak · zakazy', foot_l='Osiem przypadków, które wracają najczęściej')))

    # ---- 09 paleta ----
    p.append(('09-kolor-paleta', page(
        title('Paleta') +
        '<p class="lead">Czerwień z logotypu prowadzi cały system. Atrament niesie tekst '
        'i ciemne pola, papier daje oddech. Poza tymi trzema rodzinami system nie ma barw '
        '— nie ma koloru „sukcesu", „ostrzeżenia" ani drugiego akcentu.</p>' +
        swatches(['red', 'red-deep', 'red-soft', 'red-wash']) +
        swatches(['ink', 'ink-1', 'ink-2', 'ink-3']) +
        swatches(['paper', 'paper-2', 'paper-3', 'line']),
        head='Kolor · paleta', foot_l='tokens/tokens.json')))

    # ---- 10 role i proporcje ----
    p.append(('10-kolor-role', page(
        title('Role i proporcje') +
        '<p class="lead">W dłuższym materiale czerwień zajmuje mniej więcej połowę '
        'powierzchni, biel drugą połowę, atrament wchodzi raz. W zestawie plansz '
        'przerywnikowych wychodzi to na trzynaście plansz czerwonych, dziewięć białych '
        'i jedną atramentową.</p>'
        '<div class="bar">'
        f'<span style="background:{T["red"]};width:57%"></span>'
        f'<span style="background:{T["paper"]};width:39%"></span>'
        f'<span style="background:{T["ink"]};width:4%"></span></div>'
        '<div class="cols cols--3">' +
        ''.join(f'<div class="stack-sm"><h3 class="h-sub">{ROLE[n][0]}</h3>'
                f'<p class="body" style="font-size:13px">{ROLE[n][1]}</p>'
                f'<p class="mono">{T[n]}</p></div>'
                for n in ('red', 'ink', 'paper')) +
        '</div>'
        '<p class="body" style="max-width:74ch">Czerwień jest polem, nie obwódką. '
        'Jeśli materiał ma być czerwony, czerwone jest całe tło, a nie ramka wokół '
        'białego prostokąta.</p>',
        head='Kolor · role', foot_l='Czerwień prowadzi')))

    # ---- 11-12 kontrast ----
    weak = [d for d in CONTRAST if d['ratio'] < 4.5]
    jasne = [d for d in CONTRAST if d['bg'] in ('paper', 'paper-2', 'red-wash')]
    ciemne = [d for d in CONTRAST if d['bg'] in ('red', 'ink')]
    p.append(('11-kolor-kontrast-jasne', page(
        title('Kontrast na jasnym') +
        '<p class="lead">Liczby policzone ze wzoru na luminancję relatywną, '
        'z półprzezroczystymi warstwami złożonymi wcześniej z tłem. Progi WCAG: 4,5:1 '
        'dla tekstu zwykłego, 3:1 dla dużego — od 24 px, albo 18,7 px w wersji '
        'półgrubej.</p>' + contrast_table(jasne) +
        '<p class="body" style="max-width:78ch">Na bieli wszystkie pary przechodzą próg '
        'tekstu zwykłego. <code>--ink-3</code> trzyma 4,84:1 i to jest powód, dla którego '
        'drobny monospace w systemie ma właśnie ten odcień, a nie jaśniejszy.</p>',
        head='Kolor · kontrast', foot_l='tokens/contrast.py')))

    p.append(('12-kolor-kontrast-ciemne', page(
        title('Kontrast na ciemnym') +
        '<p class="lead">Na czerwieni i na atramencie tekst jest biały albo prawie biały. '
        'Wartości półprzezroczyste są tu policzone po złożeniu z tłem, więc mówią, co '
        'widać naprawdę.</p>' + contrast_table(ciemne) +
        f'<p class="body" style="max-width:78ch">Poniżej 4,5:1 schodzą {len(weak)} pary: '
        + ', '.join(f'<code>--{d["fg"]}</code> na <code>--{d["bg"]}</code> ({d["ratio"]}:1)'
                    for d in weak) +
        '. Wolno ich użyć wyłącznie na elementy dekoracyjne i duży stopień — na czerwieni '
        'akcentem jest kropka po tytule, a nie tekst. Na atramencie akcent bierze '
        '<code>--red-soft</code> (5,66:1), nie czerwień marki.</p>',
        head='Kolor · kontrast', foot_l='tokens/contrast.py')))

    # ---- 12 kroje ----
    p.append(('12-typografia-kroje', page(
        title('Kroje') +
        '<div style="height:10px"></div>'
        '<div class="spec"><p class="spec__sample" style="font-size:74px">Machinekind</p>'
        '<p class="mono">Big Shoulders Display · waga 500 · sygnatura i tytuły</p></div>'
        '<div class="spec"><p class="spec__sample spec__sample--sans" style="font-size:26px">'
        'Uczymy maszyny poruszać się w świecie ludzi.</p>'
        '<p class="mono">IBM Plex Sans · wagi 400 i 500 · zdania i akapity</p></div>'
        '<div class="spec"><p class="spec__sample spec__sample--mono" style="font-size:19px">'
        '300 mln kroków · sim-to-real · 400 Hz</p>'
        '<p class="mono">IBM Plex Mono · waga 400 i 500 · pomiar i oznaczenia</p></div>'
        '<p class="body" style="max-width:78ch">Monospace niesie pomiar: współrzędne, takty, '
        'liczności, oznaczenia części. Nie jest kostiumem „technicznego" pod zwykłe etykiety '
        '— jeśli podpis nie zawiera liczby ani oznaczenia, idzie krojem tekstowym.</p>',
        head='Typografia · kroje', foot_l='slides/assets/fonts')))

    # ---- 13 skala ----
    scale = [
        ('Sygnatura', 'h-display', 'clamp(3,6rem, 13,5vw, 12,5rem)', '0,84', 'Big Shoulders'),
        ('Tytuł 1', 'h1', 'clamp(2,9rem, 8vw, 6,8rem)', '0,86', 'Big Shoulders'),
        ('Tytuł 2', 'h2', 'clamp(2,2rem, 5vw, 4,2rem)', '0,90', 'Big Shoulders'),
        ('Tytuł 3', 'h3', 'clamp(1,2rem, 1,9vw, 1,6rem)', '1,14', 'IBM Plex Sans'),
        ('Wprowadzenie', 'lead', 'clamp(1,05rem, 1,5vw, 1,32rem)', '1,50', 'IBM Plex Sans'),
        ('Tekst', 'body', '1rem', '1,60', 'IBM Plex Sans'),
        ('Pomiar', 'mono', '0,72rem', '1,30', 'IBM Plex Mono'),
    ]
    rows = ''.join(f'<tr><td><strong>{n}</strong></td><td class="tok">.{c}</td>'
                   f'<td class="num">{s}</td><td class="num">{lh}</td><td>{fam}</td></tr>'
                   for n, c, s, lh, fam in scale)
    p.append(('13-typografia-skala', page(
        title('Skala') +
        '<p class="lead">Skala jest płynna: stopnie rosną z szerokością kadru, a nie skaczą '
        'na progach. Małe tytuły wychodzą z kroju tekstowego — kondensowany przy 20 px gubi '
        'czytelność.</p>'
        f'<table><thead><tr><th>Rola</th><th>Klasa</th><th>Stopień</th><th>Interlinia</th>'
        f'<th>Krój</th></tr></thead><tbody>{rows}</tbody></table>'
        '<p class="body" style="max-width:78ch">Próg drobnego tekstu to 11 px przy korzeniu '
        '16 px (<code>--micro: 0,72rem</code>). Niżej nie schodzimy nigdzie — ani w stopce, '
        'ani w podpisie pod ilustracją.</p>',
        head='Typografia · skala', foot_l='src/styles/global.css')))

    # ---- 14 polskie wersaliki ----
    sample = 'Od jednego<br>do wielu robotów'
    p.append(('14-typografia-wersaliki', page(
        title('Polskie wersaliki') +
        '<p class="lead">Kondensowany krój wyświetlany przy ciasnej interlinii zderza polskie '
        'znaki: kreska w „Ó" i ogonek w „Ą" wchodzą na sąsiedni wiersz. Reguła jest prosta '
        '— tytuł łamany na dwa wiersze i więcej dostaje interlinię nie mniejszą niż 0,96.</p>'
        '<div class="cols cols--2">'
        '<div><div style="font-family:var(--display);font-weight:500;font-size:56px;'
        'line-height:0.86;text-transform:uppercase;color:var(--ink)">Chód uczony<br>'
        'w symulacji</div>'
        '<p class="panel__label" style="margin-top:14px">Interlinia 0,86 — kreska w „Ó" '
        'dotyka wiersza wyżej.</p></div>'
        '<div><div style="font-family:var(--display);font-weight:500;font-size:56px;'
        'line-height:0.96;text-transform:uppercase;color:var(--ink)">Chód uczony<br>'
        'w symulacji</div>'
        '<div class="panel--ok"><p class="panel__label" style="margin-top:14px">Interlinia 0,96 '
        '— znaki diakrytyczne mają miejsce.</p></div></div></div>'
        '<p class="body" style="max-width:78ch">Jednowierszowy tytuł może zostać przy 0,86 — '
        'nie ma się z czym zderzyć. Zasada dotyczy wyłącznie kroju wyświetlanego w wersalikach; '
        'krój tekstowy ma dość światła przy każdej interlinii z tej księgi.</p>',
        head='Typografia · wersaliki', foot_l='Nie mniej niż 0,96 przy łamaniu')))

    # ---- 15 układ ----
    p.append(('15-uklad', page(
        title('Układ') +
        '<p class="lead">Treść trzyma miarę, nie rozlewa się na całą szerokość ekranu. '
        'Podziały niesie hairline, nie ramka i nie cień.</p>'
        '<div class="cols cols--2">'
        '<div class="stack-sm"><h3 class="h-sub">Miara i marginesy</h3>'
        f'<p class="body">Kolumna: <code>--wrap: {T["wrap"]}</code>. '
        f'Margines boczny: <code>{T["gutter"]}</code> — rośnie z szerokością kadru. '
        f'Rytm sekcji: <code>{T["section-y"]}</code>.</p>'
        '<p class="body">W materiałach o stałym kadrze margines jest stały: 128 px '
        'na planszy 1920 × 1080, 88 px na kwadracie 1080, 64 px na stronie A4.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Kotwiczenie</h3>'
        '<p class="body">Blok treści stoi przy dolnej krawędzi kadru, nie na środku. '
        'Wyjątek: kadr z jednym elementem — sam tytuł, sam znak — wtedy idzie na środek, '
        'bo kotwiczony do dołu wygląda na osiadły.</p>'
        '<h3 class="h-sub" style="margin-top:8px">Hairline</h3>'
        '<p class="body">Linia ma 1 px w każdej skali. Nie pogrubia się razem z kadrem '
        'i nie zamienia w ramkę dookoła bloku.</p></div></div>'
        '<p class="body" style="max-width:78ch">Narożniki są ostre. Zaokrąglenie ma tylko '
        'przycisk — pełna pigułka <code>999px</code>, nic pośredniego.</p>',
        head='Układ', foot_l='src/styles/global.css')))

    # ---- 16 obrazowanie ----
    p.append(('16-obrazowanie', page(
        title('Obrazowanie') +
        '<div class="cols cols--2" style="align-items:center">'
        '<img src="../logo/svg/dlonie-ink.svg" style="width:100%">'
        '<div class="stack-sm"><h3 class="h-sub">Dłonie</h3>'
        '<p class="body">Dłoń maszyny i dłoń człowieka, sięgające po sobie. Motyw sygnaturowy '
        '— używamy go na punkt styku między częścią o ludziach a częścią o maszynie. '
        'Dłonie nie stoją na każdym materiale; użyte wszędzie przestają cokolwiek znaczyć.</p></div>'
        '</div>'
        '<div class="cols cols--3">'
        '<div class="stack-sm"><h3 class="h-sub">Znak w tle</h3>'
        '<p class="body" style="font-size:13px">Wchodzi kadrowany krawędzią, nigdy w całości. '
        'Krycie: 0,09 na czerwieni, 0,05 na bieli, 0,15 na atramencie — biel na czerwieni daje '
        'słabszy ślad niż czerwień na bieli, więc każde tło ma własną wartość.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Fotografia</h3>'
        '<p class="body" style="font-size:13px">Zdjęcia maszyn schodzą do jednej barwy: skala '
        'szarości, mnożenie czerwienią, przyciemnienie od dołu pod tekst. Nie zostawiamy '
        'zdjęcia w oryginalnych kolorach obok czerwieni marki.</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Czego nie ma</h3>'
        '<p class="body" style="font-size:13px">Zdjęć stockowych z ludźmi w biurze, ikon '
        'z zestawów, ilustracji „AI" z sieciami neuronowymi i świecącymi mózgami.</p></div>'
        '</div>',
        head='Obrazowanie', foot_l='logo/svg/dlonie.svg')))

    # ---- 17 głos ----
    p.append(('17-glos', page(
        title('Głos') +
        '<p class="lead">Piszemy rzeczowo i krótko. Zdanie niesie decyzję albo liczbę, '
        'nie nastrój. O sobie mówimy przez to, co zrobiliśmy, nie przez przymiotniki.</p>'
        '<div class="cols cols--2">'
        '<div class="stack-sm"><h3 class="h-sub">Tak piszemy</h3>'
        '<p class="body">„Sieci sterujące chodem trenujemy w symulatorze pełnej dynamiki. '
        'Te same trajektorie przenosimy na maszynę."</p>'
        '<p class="body">„Napędy bezpośrednie, nogi o zamkniętym łańcuchu kinematycznym, '
        'sztywność wzięta ze struktury zamiast z dodatkowej masy."</p>'
        '<p class="body">„W01-TEK nie jest wizualizacją. Jest bazą platformy."</p></div>'
        '<div class="stack-sm"><h3 class="h-sub">Tak nie piszemy</h3>'
        '<p class="body">Bez „innowacyjny", „przełomowy", „nowoczesny", „dynamiczny", '
        '„unikalny", „dedykowany", „rozwiązanie szyte na miarę".</p>'
        '<p class="body">Bez obietnic bez liczby. Jeśli coś działa, podajemy przy jakim '
        'takcie, po ilu krokach, w jakim materiale.</p>'
        '<p class="body">Bez wykrzykników w tytułach — z jednym wyjątkiem: hasło wydarzenia, '
        'gdzie zaproszenie jest zaproszeniem.</p></div></div>'
        '<p class="body" style="max-width:78ch">Nadtytuł i podpis stawiamy tylko wtedy, '
        'kiedy mają co nieść: nazwę domeny, oznaczenie, pomiar, nazwisko prelegenta. '
        'Dopisany „na klimat" niesie ton zamiast treści i lepiej, żeby go nie było.</p>',
        tone='ink', head='Głos', foot_l='Rejestr rzeczowy')))

    # ---- 18 materiały ----
    thumbs = ''.join(
        f'<div class="thumb"><img src="thumbs/{f}"><p class="mono">{n}</p>'
        f'<p class="body" style="font-size:12px">{d}</p></div>'
        for f, n, d in [
            ('plansza.png', 'Plansze', '23 kadry 16:9 do wstawiania między wystąpienia.'),
            ('post.png', 'Sieć', 'Posty kwadratowe i relacja 9:16.'),
            ('papier.png', 'Papier firmowy', 'A4, do wydruku i do PDF.'),
            ('podpis.png', 'Podpis mailowy', 'Wariant ze znakiem i bez.'),
        ])
    p.append(('18-materialy', page(
        title('Materiały') +
        '<p class="lead">Gotowe zestawy leżą w paczce. Każdy ma źródło w HTML, skrypt '
        'eksportu i wynik w PNG, PDF albo PPTX — treść podmienia się w źródle, nie '
        'w wyeksportowanym pliku.</p>'
        f'<div class="thumbs">{thumbs}</div>',
        head='Materiały', foot_l='slides · templates')))

    # ---- 19 pliki ----
    files = [
        ('brandbook/', 'Ta księga: źródło, strony w PNG i PDF.'),
        ('logo/svg/', 'Znak, sygnatura słowna i lockupy w wektorze, po cztery warianty barwne.'),
        ('logo/png/', 'Rastry znaku i lockupów, 128–2048 px.'),
        ('logo/favicon/', 'Ikony przeglądarki i aplikacji, z .ico i wariantem maskowalnym.'),
        ('logo/social/', 'Open Graph, baner LinkedIn, awatar.'),
        ('tokens/', 'Tokeny w JSON, CSS, SCSS i JS oraz skrypt liczący kontrast.'),
        ('slides/', 'Plansze przerywnikowe: źródło, PNG, PDF, PPTX.'),
        ('templates/', 'Sieć, papier firmowy, podpis mailowy.'),
        ('fonts/', 'Pliki krojów i licencja.'),
    ]
    rows = ''.join(f'<tr><td class="tok">{p_}</td><td>{d}</td></tr>' for p_, d in files)
    p.append(('19-pliki', page(
        title('Pliki w paczce') +
        f'<table><thead><tr><th>Katalog</th><th>Co w środku</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        '<p class="body" style="max-width:78ch">Każdy katalog ma własny README z opisem, '
        'skąd pliki pochodzą i co wymaga podmiany. Materiały składa się skryptami '
        '(<code>build.py</code>, <code>build.mjs</code>) — po zmianie treści uruchom skrypt, '
        'nie poprawiaj wyeksportowanego pliku.</p>',
        head='Pliki', foot_l='brand/')))

    # ---- 20 zamknięcie ----
    p.append(('20-zamkniecie', (
        f'<section class="page page--red">'
        f'<img class="wm" src="{MARK}/mark-white.svg" alt="">'
        f'<header class="head"><p class="mono">Kontakt</p>'
        f'<p class="mono">Machinekind · księga znaku</p></header>'
        f'<div class="main" style="justify-content:center">'
        f'<h2 class="h-page" style="font-size:96px">Pytania<br>o znak<span class="dot">?</span></h2>'
        f'<div class="cols cols--3" style="max-width:760px">'
        f'<div class="stack-sm"><p class="mono">Kontakt</p>'
        f'<p class="h-sub">hello@wo1.tech</p></div>'
        f'<div class="stack-sm"><p class="mono">Strona</p>'
        f'<p class="h-sub">machinekind.ai</p></div>'
        f'<div class="stack-sm"><p class="mono">LinkedIn</p>'
        f'<p class="h-sub">machinekindai</p></div></div></div>'
        f'<footer class="foot"><p class="mono">Kolektyw robotyki i AI · Wrocław</p>'
        f'<p class="mono">{WERSJA}</p></footer></section>')))

    return fill_contents(p)


SECTIONS = [
    ('Znak', 'Warianty, lockupy, pole ochronne, minimalne rozmiary, zakazy.', 'znak'),
    ('Kolor', 'Paleta, role, proporcje, policzone progi kontrastu.', 'kolor'),
    ('Typografia', 'Trzy kroje, skala i zasada polskich wersalików.', 'typografia'),
    ('Układ', 'Miara, hairline, rama kadru, kotwiczenie treści.', 'uklad'),
    ('Obrazowanie', 'Dłonie, znak w tle, fotografia w jednej barwie.', 'obrazowanie'),
    ('Głos', 'Rejestr, przykłady, czego nie mówimy.', 'glos'),
    ('Materiały i pliki', 'Plansze, sieć, papier firmowy, podpis, mapa paczki.', 'materialy|pliki'),
]


def fill_contents(pages: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Wstawia do spisu treści numery stron policzone z gotowej listy."""
    rows = []
    for label, desc, prefixes in SECTIONS:
        keys = prefixes.split('|')
        nums = [i + 1 for i, (slug, _) in enumerate(pages)
                if any(re.match(rf'\d+-{k}', slug) for k in keys)]
        if not nums:
            raise SystemExit(f'Spis treści: nie znalazłem stron rozdziału „{label}".')
        span = f'{min(nums):02d}' if min(nums) == max(nums) else f'{min(nums):02d}–{max(nums):02d}'
        rows.append(f'<tr><td class="tok">{span}</td><td><strong>{label}</strong></td>'
                    f'<td>{desc}</td></tr>')
    spis = ''.join(rows)
    return [(slug, html.replace('{{SPIS}}', spis)) for slug, html in pages]


# ============================================================
# Złożenie i eksport
# ============================================================

def make_thumbs():
    THUMBS.mkdir(exist_ok=True)
    plan = [(BRAND / 'slides/export/png/01-otwarcie.png', 'plansza.png'),
            (BRAND / 'templates/social/export/post-cytat-1080x1080.png', 'post.png'),
            (BRAND / 'templates/papier-firmowy/export/papier-firmowy.png', 'papier.png'),
            (BRAND / 'templates/podpis-mailowy/export/podpis.png', 'podpis.png')]
    for src, name in plan:
        if not src.exists():
            raise SystemExit(f'Brak {src} — uruchom najpierw eksport materiałów.')
        im = Image.open(src).convert('RGB')
        im.thumbnail((520, 520), Image.LANCZOS)
        im.save(THUMBS / name, quality=88)


def write_html(pages: list[tuple[str, str]]) -> Path:
    frames = ''.join(f'<div class="frame">{html}</div>' for _, html in pages)
    doc = (f'<!doctype html><html lang="pl"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>Machinekind — księga znaku</title>'
           f'<link rel="stylesheet" href="brandbook.css"></head><body>'
           f'<!-- Dokument generowany przez build.py. Treść rozdziałów jest w tym skrypcie,'
           f' nie w tym pliku. -->'
           f'<div class="doc">{frames}</div>'
           f'<script>const only=new URLSearchParams(location.search).get("only");'
           f'if(only){{document.body.classList.add("single");'
           f'document.querySelectorAll(".frame").forEach((f,i)=>{{'
           f'if(String(i+1)!==only)f.remove()}})}}</script></body></html>\n')
    out = HERE / 'index.html'
    out.write_text(doc)
    return out


def check_overflow(count: int):
    """Sprawdza w przeglądarce, czy treść którejś strony nie wychodzi poza kadr."""
    probe = HERE / '.probe.html'
    html = (HERE / 'index.html').read_text()
    script = """
<script>
  document.fonts.ready.then(() => {
  const bad = [];
  document.querySelectorAll('.page').forEach((pg, i) => {
    const main = pg.querySelector('.main');
    if (!main) return;
    const over = main.scrollHeight - main.clientHeight;
    if (over > 1) bad.push((i + 1) + ':' + over);
  });
  document.title = 'OVERFLOW ' + (bad.join(',') || 'brak');
  });
</script>"""
    probe.write_text(html.replace('</body>', script + '</body>'))
    out = subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                          '--hide-scrollbars', '--allow-file-access-from-files',
                          '--virtual-time-budget=9000', '--dump-dom',
                          f'file://{probe.resolve()}'], capture_output=True, text=True)
    probe.unlink()
    found = re.search(r'<title>OVERFLOW ([^<]*)</title>', out.stdout)
    result = found.group(1) if found else '?'
    if result != 'brak':
        raise SystemExit(f'Treść wychodzi poza kadr na stronach (nr:px): {result}')
    print('kadr: wszystkie strony mieszczą treść')


def shoot_pages(count: int):
    EXPORT.mkdir(exist_ok=True)
    png_dir = EXPORT / 'png'
    # Katalog idzie do czyszczenia: nazwy stron zmieniają się przy przestawianiu
    # rozdziałów, a PDF składa się z tego, co w nim leży — stare pliki wchodziłyby
    # do środka jako zduplikowane strony.
    if png_dir.exists():
        for old in png_dir.glob('*.png'):
            old.unlink()
    png_dir.mkdir(exist_ok=True)
    names = [n for n, _ in build_pages()]
    for i in range(count):
        out = png_dir / f'{names[i]}.png'
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--hide-scrollbars', '--allow-file-access-from-files',
                        '--force-device-scale-factor=2',
                        f'--window-size={PAGE_W},{PAGE_H + OVERSHOOT}',
                        '--virtual-time-budget=9000', f'--screenshot={out}',
                        f'file://{(HERE / "index.html").resolve()}?only={i + 1}'],
                       capture_output=True)
        im = Image.open(out)
        want = (PAGE_W * 2, PAGE_H * 2)
        if im.size != want:
            if im.width != want[0] or im.height < want[1]:
                raise SystemExit(f'{out.name}: zrzut {im.size}, oczekiwano {want}')
            im.crop((0, 0, *want)).save(out)
    print(f'strony → export/png/ ({count})')


def make_pdf():
    pages = sorted((EXPORT / 'png').glob('*.png'))
    ims = [Image.open(p).convert('RGB') for p in pages]
    out = EXPORT / 'machinekind-ksiega-znaku.pdf'
    # 2 × 1123 px na 297 mm to 192 dpi — strona wychodzi dokładnie A4 poziomo.
    ims[0].save(out, 'PDF', save_all=True, append_images=ims[1:], resolution=192.0)
    print(f'pdf → {out.name} ({out.stat().st_size / 1e6:.1f} MB)')


def make_bundle():
    """Wersja jednoplikowa: kroje, grafiki i style w data URI."""
    css = (HERE / 'brandbook.css').read_text()
    fonts = (BRAND / 'slides/assets/fonts.css').read_text()

    def uri(path: Path) -> str:
        mime = {'.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.png': 'image/png',
                '.jpg': 'image/jpeg', '.webp': 'image/webp'}[path.suffix]
        return f'data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}'

    fonts = re.sub(r"url\('fonts/([^']+)'\)",
                   lambda m: f"url('{uri(BRAND / 'slides/assets/fonts' / m.group(1))}')", fonts)
    css = css.replace("@import '../slides/assets/fonts.css';", fonts)
    css = css.replace("@import '../tokens/tokens.css';",
                      (BRAND / 'tokens/tokens.css').read_text())

    html = (HERE / 'index.html').read_text()
    html = html.replace('<link rel="stylesheet" href="brandbook.css">', f'<style>{css}</style>')
    html = re.sub(r'src="([^"]+\.(?:svg|png|webp|jpg))"',
                  lambda m: f'src="{uri((HERE / m.group(1)).resolve())}"', html)
    out = EXPORT / 'machinekind-ksiega-znaku.html'
    out.write_text(html)
    print(f'html → {out.name} ({len(html) / 1e6:.1f} MB)')


if __name__ == '__main__':
    make_thumbs()
    pages = build_pages()
    write_html(pages)
    print(f'index.html → {len(pages)} stron')
    check_overflow(len(pages))
    shoot_pages(len(pages))
    make_pdf()
    make_bundle()
