/**
 * Zdjęcie do siatki zespołu.
 *
 *   node scripts/portret.mjs przemek.jpg przemyslaw-nowak
 *   node scripts/portret.mjs przemek.jpg przemyslaw-nowak 0.45 0.22 0.62
 *
 * Siatka zespołu kadruje portrety w proporcji 4:5 i przycina je `cover`, więc
 * materiał wchodzi tu w tej samej proporcji — inaczej przeglądarka obcięłaby
 * go po swojemu i głowa wypadłaby z kadru. Dwa opcjonalne argumenty to punkt
 * ostrości: udział szerokości i wysokości źródła, wokół którego trzyma się
 * kadr. Domyślnie środek szerokości i jedna piąta wysokości, bo na portrecie
 * całej sylwetki głowa jest u góry. Trzeci to zbliżenie: ułamek największego
 * kadru, jaki mieści się w źródle. Portret całej sylwetki wymaga ciaśniejszego
 * kadru niż popiersie, bo w siatce liczy się twarz, a nie kurtka.
 *
 * Wynik idzie do `src/assets/team/<slug>.webp`, skąd bierze go `data/team.ts`
 * — nazwa pliku musi się zgadzać ze slugiem w składzie zespołu.
 */
import sharp from 'sharp';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const p = (rel) => resolve(root, rel);

const [source, slug, fx = '0.5', fy = '0.2', zoom = '1'] = process.argv.slice(2);
if (!source || !slug) {
  throw new Error(
    'Użycie: node scripts/portret.mjs <plik źródłowy> <slug> [ostrość-x] [ostrość-y] [zbliżenie]'
  );
}

/** Kadr siatki zespołu. */
const RATIO = 4 / 5;
const OUT_W = 800;

const img = sharp(p(source));
const { width, height } = await img.metadata();

// Największy kadr 4:5, jaki mieści się w źródle, przesunięty na punkt ostrości
// i dociśnięty do krawędzi, gdy ten punkt leży zbyt blisko brzegu.
const maxH = Math.min(height, Math.round(width / RATIO));
const boxH = Math.round(maxH * Math.min(1, Math.max(0.2, Number(zoom))));
const boxW = Math.round(boxH * RATIO);
const clamp = (v, max) => Math.max(0, Math.min(max, Math.round(v)));
const left = clamp(Number(fx) * width - boxW / 2, width - boxW);
const top = clamp(Number(fy) * height - boxH / 2, height - boxH);

mkdirSync(p('src/assets/team'), { recursive: true });
const out = `src/assets/team/${slug}.webp`;

await img
  .extract({ left, top, width: boxW, height: boxH })
  .resize({ width: OUT_W })
  .webp({ quality: 82 })
  .toFile(p(out));

console.log(`${out}  ${OUT_W}×${Math.round(OUT_W / RATIO)}  ← ${source} ${width}×${height}, kadr ${boxW}×${boxH} od ${left},${top}`);
