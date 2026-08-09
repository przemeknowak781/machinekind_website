/**
 * Wyciąga czystą sylwetkę z wektorów w korzeniu repozytorium.
 *
 *   node scripts/hands-vector.mjs
 *
 * Pliki hand_*.svg to obrys bitmapy: około 485 ścieżek, z czego jedna ma
 * pełne krycie i niesie kształt, a reszta odtwarza antyaliasing półprzezro-
 * czystymi warstwami. Bierzemy tę jedną, przycinamy kadr do samej kreski
 * i zapisujemy z `fill="currentColor"`, żeby kolor szedł z CSS.
 *
 * Kadr musi być przycięty tak samo jak bitmapy, bo układ nagłówka stoi na
 * dwóch liczbach: proporcji dłoni i pionowym położeniu opuszka. Skrypt je
 * wypisuje i porównuje z tymi, których używa HeroHands.
 */
import sharp from 'sharp';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const p = (rel) => fileURLToPath(new URL(rel, root));

mkdirSync(p('src/assets'), { recursive: true });

/** Wartości, na których stoi układ nagłówka (z bitmapowego potoku). */
const EXPECTED = {
  robot: { aspect: 3.89, tip: 0.3503, side: 'right' },
  human: { aspect: 3.202, tip: 0.3029, side: 'left' },
};

/** Ścieżka o pełnym kryciu, czyli sama sylwetka. */
function silhouette(svg) {
  const paths = [...svg.matchAll(/<path([^>]*?)d="([^"]*)"/g)].map((m) => ({
    attrs: m[1],
    d: m[2],
  }));

  const solid = paths
    .filter((x) => {
      const o = /fill-opacity="([\d.]+)"/.exec(x.attrs);
      return !o || parseFloat(o[1]) >= 0.999;
    })
    .sort((a, b) => b.d.length - a.d.length);

  if (!solid.length) throw new Error('Brak ścieżki o pełnym kryciu');
  return solid[0].d;
}

function viewBoxOf(svg) {
  const m = /viewBox="([\d.\-\s]+)"/.exec(svg);
  if (!m) throw new Error('Brak viewBox');
  return m[1].trim().split(/\s+/).map(Number);
}

/** Prostokąt kreski w jednostkach viewBox, liczony z rastra próbnego. */
async function inkBox(d, [vx, vy, vw, vh]) {
  const W = 1600;
  const H = Math.round((W * vh) / vw);
  const probe = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vx} ${vy} ${vw} ${vh}" width="${W}" height="${H}"><path d="${d}" fill="#000"/></svg>`;

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
    px: { minX, maxX, minY, maxY, W: info.width, H: info.height, data },
  };
}

/** Pionowe położenie opuszka: skrajna kolumna od strony wskazywania. */
function tipFraction(box, side) {
  const { data, W, minX, maxX, minY, maxY } = box.px;
  const col = side === 'right' ? maxX : minX;
  for (let y = minY; y <= maxY; y++) {
    if (data[y * W + col] > 40) return (y - minY) / (maxY - minY + 1);
  }
  return 0.5;
}

for (const [name, want] of Object.entries(EXPECTED)) {
  const src = readFileSync(p(`hand_${name === 'robot' ? 'robot' : 'human'}.svg`), 'utf8');
  const d = silhouette(src);
  const box = await inkBox(d, viewBoxOf(src));

  const aspect = box.w / box.h;
  const tip = tipFraction(box, want.side);

  const out = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.x.toFixed(2)} ${box.y.toFixed(2)} ${box.w.toFixed(2)} ${box.h.toFixed(2)}" fill="currentColor"><path d="${d}"/></svg>\n`;
  const file = `src/assets/hand-${name}.svg`;
  writeFileSync(p(file), out);

  const dAsp = ((aspect / want.aspect - 1) * 100).toFixed(2);
  const dTip = ((tip - want.tip) * 100).toFixed(2);
  console.log(
    `${file}  ${(out.length / 1024).toFixed(0)} kB\n` +
      `   proporcja ${aspect.toFixed(3)} (bitmapa ${want.aspect}, różnica ${dAsp}%)\n` +
      `   opuszek na ${(tip * 100).toFixed(2)}% wysokości (bitmapa ${(want.tip * 100).toFixed(2)}%, różnica ${dTip} pkt proc.)`
  );
}
