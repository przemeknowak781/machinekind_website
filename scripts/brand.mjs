/**
 * Przygotowanie materiałów marki z plików źródłowych w korzeniu repozytorium.
 *
 *   node scripts/brand.mjs
 *
 * Źródła (białe kreski na przezroczystym tle):
 *   hand_human.png, hand_robot.png, machinekind_logo.svg
 *
 * Wynik:
 *   src/assets/hands-ink.png    — scena "Stworzenie", czarna, pod jasne tło
 *   src/assets/hands-paper.png  — ta sama scena, biała, pod ciemne tło
 *   src/assets/hand-*-ink.png   — pojedyncze dłonie do użycia dekoracyjnego
 *   public/mark.svg             — sam znak (logo bez sygnatury słownej)
 *   public/favicon.svg          — favicon
 */
import sharp from 'sharp';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const p = (rel) => fileURLToPath(new URL(rel, root));

mkdirSync(p('src/assets'), { recursive: true });
mkdirSync(p('public'), { recursive: true });

const INK = { r: 13, g: 15, b: 16 };
const PAPER = { r: 255, g: 255, b: 255 };

/** Przycina obraz do widocznej treści i skaluje do zadanej szerokości. */
async function trimmed(file, width) {
  const src = sharp(p(file));
  const meta = await src.metadata();
  const raw = await src.clone().extractChannel('alpha').raw().toBuffer();

  let minX = meta.width, maxX = 0, minY = meta.height, maxY = 0;
  for (let y = 0; y < meta.height; y++) {
    for (let x = 0; x < meta.width; x++) {
      if (raw[y * meta.width + x] > 40) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  const box = { left: minX, top: minY, width: maxX - minX + 1, height: maxY - minY + 1 };
  const alpha = await sharp(p(file))
    .extract(box)
    .resize({ width, fit: 'inside' })
    .extractChannel('alpha')
    .raw()
    .toBuffer({ resolveWithObject: true });
  return { alpha: alpha.data, width: alpha.info.width, height: alpha.info.height, box };
}

/** Nadaje kresce jednolity kolor, zachowując kanał alfa. */
function tint({ alpha, width, height }, color) {
  return sharp({ create: { width, height, channels: 3, background: color } })
    .joinChannel(alpha, { raw: { width, height, channels: 1 } })
    .png();
}

/** Pionowa pozycja opuszka (0–1) w przyciętym kadrze. */
async function tipY({ alpha, width, height }, side) {
  let best = null;
  for (let x = 0; x < width; x++) {
    const col = side === 'left' ? x : width - 1 - x;
    for (let y = 0; y < height; y++) {
      if (alpha[y * width + col] > 40) {
        best = y;
        break;
      }
    }
    if (best !== null) break;
  }
  return best / height;
}

const HAND_W = 1900;
const GAP = 150;

const robot = await trimmed('hand_robot.png', HAND_W);
const human = await trimmed('hand_human.png', HAND_W);

const robotTip = await tipY(robot, 'right');
const humanTip = await tipY(human, 'left');

// Opuszki mają leżeć w jednej linii poziomej; styk wypada dokładnie w połowie sceny.
const meetY = Math.round(Math.max(robotTip * robot.height, humanTip * human.height) + 24);
const robotTop = Math.round(meetY - robotTip * robot.height);
const humanTop = Math.round(meetY - humanTip * human.height);

const sceneW = HAND_W * 2 + GAP;
const sceneH = Math.max(robotTop + robot.height, humanTop + human.height) + 24;

async function scene(color, out) {
  const [r, h] = await Promise.all([
    tint(robot, color).toBuffer(),
    tint(human, color).toBuffer(),
  ]);
  await sharp({
    create: { width: sceneW, height: sceneH, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite([
      { input: r, left: 0, top: robotTop },
      { input: h, left: HAND_W + GAP, top: humanTop },
    ])
    .png({ compressionLevel: 9 })
    .toFile(p(out));
  console.log(`${out}  ${sceneW}×${sceneH}`);
}

await scene(INK, 'src/assets/hands-ink.png');
await scene(PAPER, 'src/assets/hands-paper.png');

await tint(robot, INK).toFile(p('src/assets/hand-robot-ink.png'));
await tint(human, INK).toFile(p('src/assets/hand-human-ink.png'));
await tint(robot, PAPER).toFile(p('src/assets/hand-robot-paper.png'));
await tint(human, PAPER).toFile(p('src/assets/hand-human-paper.png'));

console.log(
  `styk: x=${((HAND_W + GAP / 2) / sceneW * 100).toFixed(2)}%  y=${(meetY / sceneH * 100).toFixed(2)}%`
);

/* ---- znak z logotypu: kadr bez sygnatury słownej ---- */
const logo = readFileSync(p('machinekind_logo.svg'), 'utf8');
const mark = logo.replace(
  /viewBox="[^"]*"\s*width="[^"]*"\s*height="[^"]*"/,
  'viewBox="0 22 2496 1880" width="2496" height="1880"'
);
writeFileSync(p('public/mark.svg'), mark);
// Favicon: kwadratowy kadr znaku.
writeFileSync(
  p('public/favicon.svg'),
  logo.replace(
    /viewBox="[^"]*"\s*width="[^"]*"\s*height="[^"]*"/,
    'viewBox="0 22 2496 1880" width="512" height="512" preserveAspectRatio="xMidYMid slice"'
  )
);
console.log('public/mark.svg, public/favicon.svg');
