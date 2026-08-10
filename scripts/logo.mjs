/**
 * Znak marki z `logo.png` do postaci nadającej się na stronę.
 *
 * Plik źródłowy to zrzut z programu graficznego: znak leży na białym tle
 * z delikatną siatką kropek, ma szerokie marginesy i waży ponad megabajt.
 * Do nawigacji i glifikonu potrzeba czegoś przeciwnego — przyciętego do
 * kreski, z przezroczystym tłem i lekkiego.
 *
 * Tło zdejmuje się otoczką wypukłą czerwonych pikseli, a nie zalewaniem od
 * krawędzi. Zalewanie przeciekłoby białymi szczelinami, które przecinają
 * sześciokąt i dotykają jego obrysu — zżarłoby całą pętlę w środku znaku.
 * Otoczka wypukła zna granicę figury, więc biel w środku zostaje bielą,
 * a znika tylko to, co leży poza sześciokątem.
 *
 *   node scripts/logo.mjs
 *
 * Wynik:
 *   src/assets/mark.png        znak do nawigacji i stopki (przez astro:assets)
 *   public/favicon.png         glifikon 512 px, tło przezroczyste
 *   public/apple-touch-icon.png  180 px na papierze — iOS nie lubi alfy
 */
import sharp from 'sharp';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const p = (rel) => resolve(root, rel);

const SRC = p('logo.png');
const PAPER = { r: 255, g: 255, b: 255 };

/** Piksel znaku: wszystko, co wyraźnie odstaje od bieli tła. */
const isInk = (r, g, b) => Math.max(r, g, b) - Math.min(r, g, b) > 28 || (r + g + b) / 3 < 200;

/** Otoczka wypukła zbioru punktów — monotoniczny łańcuch Andrew. */
function hull(points) {
  const pts = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const build = (src) => {
    const out = [];
    for (const pt of src) {
      while (out.length >= 2 && cross(out[out.length - 2], out[out.length - 1], pt) <= 0) out.pop();
      out.push(pt);
    }
    out.pop();
    return out;
  };
  return [...build(pts), ...build(pts.reverse())];
}

const src = sharp(SRC);
const { width, height } = await src.metadata();
const { data } = await src.clone().ensureAlpha().raw().toBuffer({ resolveWithObject: true });

// Skrajne piksele znaku w każdym wierszu wystarczą — otoczka i tak bierze
// tylko punkty brzegowe, a tak zbiór schodzi z miliona do dwóch tysięcy.
const edge = [];
for (let y = 0; y < height; y++) {
  let first = -1;
  let last = -1;
  for (let x = 0; x < width; x++) {
    const i = (y * width + x) * 4;
    if (isInk(data[i], data[i + 1], data[i + 2])) {
      if (first < 0) first = x;
      last = x;
    }
  }
  if (first >= 0) edge.push([first, y], [last, y]);
}
if (!edge.length) throw new Error(`Brak pikseli znaku w ${SRC}`);

const poly = hull(edge);

// Maska: kształt otoczki na przezroczystym tle. `dest-in` zostawia obraz
// tylko tam, gdzie maska ma krycie, więc tło poza sześciokątem znika,
// a krawędź wygładza się razem z rasteryzacją ścieżki.
const path = poly.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join(' ') + ' Z';
const mask = Buffer.from(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
     <path d="${path}" fill="#fff"/>
   </svg>`
);

const xs = poly.map(([x]) => x);
const ys = poly.map(([, y]) => y);
const box = {
  left: Math.max(0, Math.min(...xs)),
  top: Math.max(0, Math.min(...ys)),
};
box.width = Math.min(width - box.left, Math.max(...xs) - box.left + 1);
box.height = Math.min(height - box.top, Math.max(...ys) - box.top + 1);

// Dwie tury: najpierw maska na pełnym kadrze, potem przycięcie z bufora.
// W jednym potoku `extract` po `composite` nie wchodzi — sharp zostawia
// wtedy pełny kadr, co widać po wymiarach wyniku.
const masked = await sharp(SRC).ensureAlpha().composite([{ input: mask, blend: 'dest-in' }]).png().toBuffer();
const cut = () => sharp(masked).extract(box);

mkdirSync(p('src/assets'), { recursive: true });

await cut().resize({ width: 512 }).png({ compressionLevel: 9 }).toFile(p('src/assets/mark.png'));

// Glifikon jest kwadratowy, więc znak wchodzi w kwadrat z marginesem —
// inaczej sześciokąt dotykałby krawędzi kafelka w zakładce.
const square = (size, background) => {
  const pad = Math.round(size * 0.07);
  return cut()
    .resize({
      width: size - 2 * pad,
      height: size - 2 * pad,
      fit: 'contain',
      background: { ...PAPER, alpha: 0 },
    })
    .extend({ top: pad, bottom: pad, left: pad, right: pad, background })
    // Znak ma dwie barwy i wygładzoną krawędź, więc paleta wystarcza —
    // pełny kolor robił z glifikonu 130 kB zamiast kilkunastu.
    .png({ compressionLevel: 9, palette: true });
};

await square(512, { ...PAPER, alpha: 0 }).toFile(p('public/favicon.png'));
await square(180, { ...PAPER, alpha: 1 }).toFile(p('public/apple-touch-icon.png'));

console.log(
  `źródło ${width}×${height}, znak ${box.width}×${box.height} (proporcja ${(box.width / box.height).toFixed(3)})`
);
console.log('src/assets/mark.png, public/favicon.png, public/apple-touch-icon.png');
