/* Eksport plansz: jeden plik HTML bez zależności, PNG-i w 2× i pakiet PDF/PPTX.
 *
 *   node build.mjs
 *
 * Renderuje Chromium z zestawu Playwrighta (PLAYWRIGHT_BROWSERS_PATH) albo
 * dowolny inny podany w CHROME_BIN. Poza przeglądarką i Pythonem z biblioteką
 * python-pptx nic nie jest potrzebne — kroje i grafiki wchodzą do HTML-a
 * jako data URI, więc plik eksportu otwiera się wszędzie tak samo.
 */

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ASSETS = join(HERE, 'assets');
const EXPORT = join(HERE, 'export');
const PNG_DIR = join(EXPORT, 'png');

/** Nazwy plików eksportu — kolejność musi zgadzać się z kolejnością plansz. */
const NAMES = [
  'otwarcie',
  'zaproszenie',
  'znak',
  'program',
  'za-chwile',
  'rozdzial',
  'wystapienie-spyrosoft',
  'wystapienie-pogoda-rosikon',
  'wystapienie-piotrowski',
  'wystapienie-wysocki',
  'wystapienie-janiec',
  'punkt-styku',
  'locomotion-ai',
  'world-models-vlm',
  'robotics-engineering',
  'design-program',
  'wojtek',
  'teza',
  'partner-spyrosoft',
  'organizatorzy',
  'przerwa',
  'pytania',
  'dziekujemy',
];

const MIME = {
  '.woff2': 'font/woff2',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

const dataUri = (path) => {
  const ext = path.slice(path.lastIndexOf('.'));
  const mime = MIME[ext];
  if (!mime) throw new Error(`Nieznany typ zasobu: ${path}`);
  return `data:${mime};base64,${readFileSync(path).toString('base64')}`;
};

/** Znajduje przeglądarkę: CHROME_BIN, potem zestaw Playwrighta, potem PATH. */
function findChrome() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;

  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  if (existsSync(root)) {
    const build = readdirSync(root)
      .filter((d) => d.startsWith('chromium-'))
      .sort()
      .pop();
    if (build) {
      const bin = join(root, build, 'chrome-linux', 'chrome');
      if (existsSync(bin)) return bin;
    }
  }

  for (const bin of ['google-chrome', 'chromium', 'chromium-browser']) {
    try {
      return execFileSync('which', [bin], { encoding: 'utf8' }).trim();
    } catch {
      /* szukamy dalej */
    }
  }
  throw new Error('Nie znaleziono Chrome ani Chromium. Ustaw CHROME_BIN.');
}

/** Skleja HTML, CSS, kroje i grafiki w jeden plik. */
function bundle() {
  let css = readFileSync(join(ASSETS, 'deck.css'), 'utf8');
  const fonts = readFileSync(join(ASSETS, 'fonts.css'), 'utf8').replace(
    /url\('fonts\/([^']+)'\)/g,
    (_, file) => `url('${dataUri(join(ASSETS, 'fonts', file))}')`,
  );

  css = css.replace(/@import 'fonts\.css';/, fonts);

  let html = readFileSync(join(HERE, 'index.html'), 'utf8');
  html = html.replace(
    /<link rel="stylesheet" href="assets\/deck\.css" \/>/,
    `<style>\n${css}\n</style>`,
  );
  html = html.replace(
    /src="assets\/([^"]+)"/g,
    (_, file) => `src="${dataUri(join(ASSETS, file))}"`,
  );
  return html;
}

const chrome = findChrome();
console.log(`Przeglądarka: ${chrome}`);

rmSync(PNG_DIR, { recursive: true, force: true });
mkdirSync(PNG_DIR, { recursive: true });

const html = bundle();
const bundlePath = join(EXPORT, 'machinekind-plansze.html');
writeFileSync(bundlePath, html);
console.log(`HTML  → ${bundlePath} (${(html.length / 1e6).toFixed(2)} MB)`);

const slideCount = (html.match(/class="frame"/g) || []).length;
if (slideCount !== NAMES.length) {
  throw new Error(`Plansz w HTML: ${slideCount}, nazw w build.mjs: ${NAMES.length}.`);
}

// Zrzut każdej planszy osobno, w podwójnej gęstości (3840 × 2160).
//
// `--window-size` podaje rozmiar okna, nie kadru: w trybie bezgłowym część
// wysokości zjada rama okna (w tej wersji 87 px), więc okno w sam raz 1080
// obcina dolny margines plansz. Okno idzie z zapasem, a `build-pack.py`
// przycina zrzut do właściwego kadru.
const OVERSHOOT = 240;

for (let i = 0; i < slideCount; i++) {
  const out = join(PNG_DIR, `${String(i + 1).padStart(2, '0')}-${NAMES[i]}.png`);
  execFileSync(
    chrome,
    [
      '--headless',
      '--disable-gpu',
      '--no-sandbox',
      '--hide-scrollbars',
      '--force-device-scale-factor=2',
      `--window-size=1920,${1080 + OVERSHOOT}`,
      '--virtual-time-budget=8000',
      `--screenshot=${out}`,
      `file://${bundlePath}?only=${i + 1}`,
    ],
    { stdio: ['ignore', 'ignore', 'pipe'] },
  );
  console.log(`PNG   → ${out}`);
}

// PDF i PPTX składa Python — obie biblioteki są tam pod ręką.
execFileSync('python3', [resolve(HERE, 'build-pack.py')], { stdio: 'inherit' });
