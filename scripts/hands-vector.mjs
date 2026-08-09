/**
 * Buduje czystą sylwetkę z wektorów w korzeniu repozytorium.
 *
 *   node scripts/hands-vector.mjs
 *
 * Źródła to obrysy bitmapy i żaden nie nadaje się do użycia wprost:
 * niosą płytę tła, stopnie antyaliasingu jako osobne ścieżki i kolor
 * wpisany na sztywno. Skrypt zostawia same ścieżki rysujące kształt,
 * przycina kadr do kreski i zapisuje z `fill="currentColor"`, żeby kolor
 * szedł z CSS.
 *
 * Kadr musi być przycięty tak samo jak w poprzednim potoku, bo układ
 * nagłówka stoi na dwóch liczbach: proporcji dłoni i pionowym położeniu
 * opuszka. Skrypt je wypisuje i porównuje z tymi, których używa HeroHands —
 * po podmianie źródeł trzeba sprawdzić, czy się nie rozjechały.
 */
import sharp from 'sharp';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const p = (rel) => fileURLToPath(new URL(rel, root));

mkdirSync(p('src/assets'), { recursive: true });

/** Wartości, na których stoi układ nagłówka. */
const HANDS = {
  robot: { sources: ['robot_better.svg', 'hand_robot.svg'], aspect: 3.89, tip: 0.3503, side: 'right' },
  human: { sources: ['human_better.svg', 'hand_human.svg'], aspect: 3.202, tip: 0.3029, side: 'left' },
};

const luminance = (hex) => {
  const v = hex.length === 4
    ? [1, 2, 3].map((i) => parseInt(hex[i] + hex[i], 16))
    : [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return (0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]) / 255;
};

/**
 * Próg jasności oddzielający kształt od cieniowania.
 *
 * Obrys ma trzy pasma: kształt poniżej 0,3, stopnie cieniowania między 0,3
 * a 0,5 i tło powyżej. Pasmo środkowe nie wnosi kształtu, a zalane na czarno
 * postrzępia kontur — bez niego krawędzie są gładsze, a pliki o połowę lżejsze.
 */
const SHAPE_BELOW = 0.3;

/**
 * Ścieżki rysujące kształt.
 *
 * Nowsze obrysy malują kształt ciemnymi wypełnieniami na białej płycie, więc
 * bierzemy ciemne. Starsze obrysowywały białą kreskę półprzezroczystymi
 * warstwami i tam liczy się jedna ścieżka o pełnym kryciu.
 */
function shapePaths(svg) {
  const paths = [...svg.matchAll(/<path([^>]*?)d="([\s\S]*?)"/g)].map((m) => ({
    attrs: m[1],
    d: m[2],
  }));

  const fillOf = (attrs) => {
    const m = /fill="(#[0-9a-fA-F]{3,6})"/.exec(attrs);
    return m ? m[1] : null;
  };

  const dark = paths.filter((x) => {
    const f = fillOf(x.attrs);
    return f && luminance(f) < SHAPE_BELOW;
  });
  if (dark.length) return { ds: dark.map((x) => x.d), kind: `ciemne ścieżki (${dark.length} z ${paths.length})` };

  const solid = paths
    .filter((x) => {
      const o = /fill-opacity="([\d.]+)"/.exec(x.attrs);
      return !o || parseFloat(o[1]) >= 0.999;
    })
    .sort((a, b) => b.d.length - a.d.length);
  if (solid.length) return { ds: [solid[0].d], kind: 'ścieżka o pełnym kryciu' };

  throw new Error('Nie znaleziono ścieżek rysujących kształt');
}

const viewBoxOf = (svg) => {
  const m = /viewBox="([\d.\-\s]+)"/.exec(svg);
  if (!m) throw new Error('Brak viewBox');
  return m[1].trim().split(/\s+/).map(Number);
};

/** Prostokąt kreski w jednostkach viewBox, liczony z rastra próbnego. */
async function inkBox(ds, [vx, vy, vw, vh]) {
  const W = 1600;
  const H = Math.round((W * vh) / vw);
  const probe =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vx} ${vy} ${vw} ${vh}" width="${W}" height="${H}">` +
    ds.map((d) => `<path d="${d}" fill="#000"/>`).join('') +
    '</svg>';

  const { data, info } = await sharp(Buffer.from(probe))
    .ensureAlpha()
    .extractChannel('alpha')
    .raw()
    .toBuffer({ resolveWithObject: true });

  let minX = info.width, maxX = 0, minY = info.height, maxY = 0;
  for (let y = 0; y < info.height; y++) {
    for (let x = 0; x < info.width; x++) {
      if (data[y * info.width + x] > 40) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  const sx = vw / info.width;
  const sy = vh / info.height;
  return {
    x: vx + minX * sx,
    y: vy + minY * sy,
    w: (maxX - minX + 1) * sx,
    h: (maxY - minY + 1) * sy,
    px: { data, W: info.width, minX, maxX, minY, maxY },
  };
}

/** Pionowe położenie opuszka: skrajna kolumna od strony wskazywania. */
function tipFraction({ px }, side) {
  const { data, W, minX, maxX, minY, maxY } = px;
  const col = side === 'right' ? maxX : minX;
  for (let y = minY; y <= maxY; y++) {
    if (data[y * W + col] > 40) return (y - minY) / (maxY - minY + 1);
  }
  return 0.5;
}

for (const [name, cfg] of Object.entries(HANDS)) {
  const source = cfg.sources.find((f) => existsSync(p(f)));
  if (!source) throw new Error(`Brak źródła dla ${name}`);

  const svg = readFileSync(p(source), 'utf8');
  const { ds, kind } = shapePaths(svg);
  const box = await inkBox(ds, viewBoxOf(svg));

  const aspect = box.w / box.h;
  const tip = tipFraction(box, cfg.side);

  const out =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.x.toFixed(2)} ${box.y.toFixed(2)} ${box.w.toFixed(2)} ${box.h.toFixed(2)}" fill="currentColor">` +
    ds.map((d) => `<path d="${d.replace(/\s+/g, ' ').trim()}"/>`).join('') +
    '</svg>\n';

  const file = `src/assets/hand-${name}.svg`;
  writeFileSync(p(file), out);

  console.log(
    `${file}  ${(out.length / 1024).toFixed(0)} kB  ← ${source}, ${kind}\n` +
      `   proporcja ${aspect.toFixed(3)} (układ zakłada ${cfg.aspect}, różnica ${((aspect / cfg.aspect - 1) * 100).toFixed(2)}%)\n` +
      `   opuszek na ${(tip * 100).toFixed(2)}% wysokości (układ zakłada ${(cfg.tip * 100).toFixed(2)}%, różnica ${((tip - cfg.tip) * 100).toFixed(2)} pkt proc.)`
  );
}
