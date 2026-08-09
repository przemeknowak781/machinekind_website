// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

/**
 * Adres i baza przychodzą z workflow GitHub Pages (`actions/configure-pages`),
 * więc ta sama konfiguracja obsługuje własną domenę i adres projektowy
 * `/machinekind_website`. Lokalnie i bez zmiennych zostaje domena docelowa.
 */
const site = process.env.PAGES_ORIGIN || 'https://machinekind.ai';
const base = process.env.BASE_PATH || '/';

const seen = new Set();

export default defineConfig({
  site,
  base,
  // Astro zgłasza korzeń dwa razy, z ukośnikiem i bez. Zostawiamy jedno
  // wystąpienie i doklejamy ukośnik, bo pod takim adresem strona stoi.
  integrations: [
    sitemap({
      filter: (page) => {
        const key = page.replace(/\/+$/, '');
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      },
      serialize: (item) => ({
        ...item,
        url: item.url.endsWith('/') ? item.url : `${item.url}/`,
      }),
    }),
  ],
  build: { inlineStylesheets: 'auto' },
  image: { responsiveStyles: true },
});
