/**
 * Buduje czystą sylwetkę z wektorów w korzeniu repozytorium.
 *
 *   node scripts/hands-vector.mjs
 *
 * Źródła to obrysy bitmapy i żaden nie nadaje się do użycia wprost: niosą
 * płytę tła, kolor wpisany na sztywno i — co najważniejsze — rozmytą
 * krawędź rozłożoną na kilkaset osobnych ścieżek.
 *
 * Poprzednia wersja wybierała ścieżki po jasności wypełnienia: brała pasmo
 * najciemniejsze, a resztę odrzucała. Pasmo najciemniejsze to jednak nie
 * kształt, tylko jądro rozmytej krawędzi — obrys bitmapy na najciemniejszym
 * poziomie jest z natury poszarpany, a otaczające go jaśniejsze ścieżki
 * właśnie tę postrzępioną granicę wygładzały. Po ich odrzuceniu dłoń
 * człowieka miała ząbkowany grzbiet palca i przedramię.
 *
 * Teraz kształt powstaje inaczej: źródło idzie na raster w dużej
 * rozdzielczości, próg tnie w połowie rampy antyaliasingu — czyli tam, gdzie
 * naprawdę biegnie krawędź — i dopiero ten kształt obrysowuje potrace jedną
 * gładką ścieżką. Jasne wnętrza zostają dziurami, bo trasowanie prowadzi je
 * w przeciwną stronę.
 *
 * Kadr musi być przycięty tak samo jak w poprzednim potoku, bo układ
 * nagłówka stoi na dwóch liczbach: proporcji dłoni i pionowym położeniu
 * opuszka. Skrypt je wypisuje i porównuje z tymi, których używa HeroHands —
 * po podmianie źródeł trzeba sprawdzić, czy się nie rozjechały.
 */
import sharp from 'sharp';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const p = (rel) => fileURLToPath(new URL(rel, root));

mkdirSync(p('src/assets'), { recursive: true });

/** Wartości, na których stoi układ nagłówka. */
const HANDS = {
  robot: { sources: ['robot_better.svg', 'hand_robot.svg'], aspect: 3.89, tip: 0.3503, side: 'right' },
  human: { sources: ['human_better.svg', 'hand_human.svg'], aspect: 3.202, tip: 0.3029, side: 'left' },
};

/** Szerokość rastra, z którego zdejmowany jest obrys. */
const RASTER_W = 4000;

/**
 * Próg jasności. Rampa antyaliasingu biegnie od kształtu do tła, więc
 * krawędź leży w jej połowie — nie przy jednym z końców.
 */
const THRESHOLD = 128;

/** Plamki poniżej tylu pikseli to śmieci po trasowaniu, nie kształt. */
const SPECK = 24;

/**
 * Obrys wchodzi dopiero tutaj, a nie w nagłówku pliku. `potrace` ciągnie za
 * sobą trzy megabajty zależności i kilka ostrzeżeń audytu, a potrzebny jest
 * wyłącznie przy podmianie materiału źródłowego — wynik i tak leży w repo.
 * Wdrożenie instaluje devDependencies przy każdym budowaniu i tego skryptu
 * nigdy nie uruchamia, więc nie ma po co go tam trzymać.
 */
async function loadPotrace() {
  try {
    return (await import('potrace')).default;
  } catch {
    throw new Error(
      'Do obrysu potrzebny jest potrace. Zainstaluj go na czas przebudowy:\n' +
        '  npm i --no-save potrace && node scripts/hands-vector.mjs'
    );
  }
}

const potrace = await loadPotrace();

const trace = (buffer, options) =>
  new Promise((resolve, reject) =>
    potrace.trace(buffer, options, (err, svg) => (err ? reject(err) : resolve(svg)))
  );

/** Prostokąt kreski i pionowe położenie opuszka, liczone z maski rastra. */
function inkBox(data, W, H, ch) {
  let minX = W;
  let maxX = -1;
  let minY = H;
  let maxY = -1;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      if (data[(y * W + x) * ch] < THRESHOLD) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (maxX < 0) throw new Error('Raster źródła jest pusty');
  return { minX, maxX, minY, maxY };
}

/** Pionowe położenie opuszka: skrajna kolumna od strony wskazywania. */
function tipFraction(data, W, ch, { minX, maxX, minY, maxY }, side) {
  const col = side === 'right' ? maxX : minX;
  for (let y = minY; y <= maxY; y++) {
    if (data[(y * W + col) * ch] < THRESHOLD) return (y - minY) / (maxY - minY + 1);
  }
  return 0.5;
}

for (const [name, cfg] of Object.entries(HANDS)) {
  const source = cfg.sources.find((f) => existsSync(p(f)));
  if (!source) throw new Error(`Brak źródła dla ${name}`);

  // Raster na białej płycie: kształt jest ciemny, wnętrza i tło jasne.
  const png = await sharp(readFileSync(p(source)))
    .resize({ width: RASTER_W })
    .flatten({ background: '#ffffff' })
    .greyscale()
    .png()
    .toBuffer();

  const { data, info } = await sharp(png).raw().toBuffer({ resolveWithObject: true });
  // Zapisany PNG bywa trójkanałowy mimo `greyscale`, więc krok w buforze
  // bierze się z metadanych, a nie z założenia „jeden bajt na piksel".
  const box = inkBox(data, info.width, info.height, info.channels);
  const w = box.maxX - box.minX + 1;
  const h = box.maxY - box.minY + 1;

  // Trasowanie idzie po przyciętym kadrze, więc układ współrzędnych ścieżki
  // od razu zaczyna się w rogu kreski i nie trzeba go potem przesuwać.
  const cropped = await sharp(png)
    .extract({ left: box.minX, top: box.minY, width: w, height: h })
    .png()
    .toBuffer();

  const traced = await trace(cropped, {
    threshold: THRESHOLD,
    blackOnWhite: true,
    turdSize: SPECK,
    optCurve: true,
    optTolerance: 0.35,
    color: 'currentColor',
    background: 'transparent',
  });

  const d = /<path[^>]*\sd="([^"]+)"/.exec(traced);
  if (!d) throw new Error(`Trasowanie ${source} nie zwróciło ścieżki`);

  const out =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" fill="currentColor">` +
    `<path fill-rule="evenodd" d="${d[1]}"/>` +
    '</svg>\n';

  const file = `src/assets/hand-${name}.svg`;
  writeFileSync(p(file), out);

  const aspect = w / h;
  const tip = tipFraction(data, info.width, info.channels, box, cfg.side);

  console.log(
    `${file}  ${(statSync(p(file)).size / 1024).toFixed(0)} kB  ← ${source}, obrys z rastra ${w}×${h}\n` +
      `   proporcja ${aspect.toFixed(3)} (układ zakłada ${cfg.aspect}, różnica ${((aspect / cfg.aspect - 1) * 100).toFixed(2)}%)\n` +
      `   opuszek na ${(tip * 100).toFixed(2)}% wysokości (układ zakłada ${(cfg.tip * 100).toFixed(2)}%, różnica ${((tip - cfg.tip) * 100).toFixed(2)} pkt proc.)`
  );
}
