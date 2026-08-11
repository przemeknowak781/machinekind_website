import type { ImageMetadata } from 'astro';

const photos = import.meta.glob<{ default: ImageMetadata }>('../assets/team/*.webp', {
  eager: true,
});

/** Zdjęcie po nazwie pliku; brak zdjęcia → inicjały. */
function photo(slug: string): ImageMetadata | undefined {
  return photos[`../assets/team/${slug}.webp`]?.default;
}

export interface Member {
  name: string;
  slug: string;
  photo?: ImageMetadata;
  initials: string;
}

export interface Group {
  label: string;
  members: Member[];
}

function member(name: string, slug: string): Member {
  const initials = name
    .replace(/^(dr|prof\.?|inż\.?|hab\.?|dr inż\.)\s+/gi, '')
    .split(/[\s-]+/)
    .filter((w) => /^[A-ZŁŚŻŹĆĄĘÓŃ]/.test(w))
    .slice(0, 2)
    .map((w) => w[0])
    .join('');

  return { name, slug, photo: photo(slug), initials };
}

/** Zespół Machinekind — cztery domeny. */
export const machinekind: Group[] = [
  {
    label: 'Locomotion AI',
    members: [
      member('Michał Pogoda-Rosikoń', 'michal-pogoda-rosikon'),
      member('Marcin Wysocki', 'marcin-wysocki'),
    ],
  },
  {
    label: 'World Models & VLM',
    members: [
      member('Grzegorz Piotrowski', 'grzegorz-piotrowski'),
      member('Maciej Gruszczyński', 'maciej-gruszczynski'),
    ],
  },
  {
    label: 'Robotics Engineering & Manufacturing',
    members: [
      member('Jakub Chmielewski', 'jakub-chmielewski'),
      member('Stepan Yurtsiv', 'stepan-yurtsiv'),
    ],
  },
  {
    label: 'Design & Program',
    members: [
      member('Przemysław Nowak', 'przemyslaw-nowak'),
      member('Grzegorz Borkowski', 'grzegorz-borkowski'),
    ],
  },
];

/**
 * Politechnika Wrocławska — Laboratorium Mechatroniki i Robotyki.
 *
 * Skład po stronie uczelni należy do projektu W01-TEK, a nie do kolektywu,
 * więc strona główna go nie pokazuje. Zostaje tutaj dla podstrony projektu.
 */
export const pwr: Group[] = [
  {
    label: 'Kierownictwo naukowe',
    members: [
      member('dr inż. Jarosław Szrek', 'jaroslaw-szrek'),
      member('prof. Radosław Zimroz', 'radoslaw-zimroz'),
    ],
  },
  {
    label: 'Konstrukcja i wykonanie',
    members: [member('Jakub Delicat', 'jakub-delicat'), member('Artur Moraszkowski', 'artur-moraszkowski')],
  },
];

export const machinekindCount = machinekind.reduce((n, g) => n + g.members.length, 0);
export const pwrCount = pwr.reduce((n, g) => n + g.members.length, 0);
