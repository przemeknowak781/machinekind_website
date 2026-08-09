/**
 * Ścieżki świadome bazy.
 *
 * GitHub Pages podaje bazę dopiero przy budowaniu: przy własnej domenie jest
 * to `/`, a przy adresie projektowym `/machinekind_website`. Dlatego nic
 * w źródłach nie może zaczynać się od twardego `/`.
 *
 * `import.meta.env.BASE_URL` bierze wartość wprost z konfiguracji, więc przy
 * bazie zapisanej bez końcowego ukośnika też go nie ma. Normalizujemy raz
 * tutaj, bo bez tego sklejanie daje `/machinekind_websitemark.svg`.
 */
export const BASE = import.meta.env.BASE_URL.replace(/\/*$/, '/');

/** Plik z katalogu `public/`, np. `asset('mark.svg')`. */
export function asset(path: string): string {
  return BASE + path.replace(/^\/+/, '');
}

/** Odsyłacz na stronie głównej, np. `link('#zespol')` albo `link()`. */
export function link(hash = ''): string {
  return BASE + hash.replace(/^\/+/, '');
}
