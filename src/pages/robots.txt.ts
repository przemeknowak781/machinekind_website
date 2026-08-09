import type { APIRoute } from 'astro';
import { BASE } from '../lib/paths';

/**
 * Generowane, a nie statyczne, bo adres mapy strony zależy od tego, gdzie
 * strona faktycznie stoi: własna domena czy adres projektowy GitHub Pages.
 */
export const GET: APIRoute = ({ site }) => {
  const root = new URL(BASE, site ?? 'https://machinekind.ai');
  const sitemap = new URL('sitemap-index.xml', root);

  return new Response(`User-agent: *\nAllow: /\n\nSitemap: ${sitemap.href}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
