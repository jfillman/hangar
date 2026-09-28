// The Architecture section: pointed opinions, one essay each. Newest first.
export type Essay = { slug: string; title: string; dek: string; date: string; minutes: number };

export const essays: Essay[] = [
  {
    slug: 'cost-of-the-platform',
    title: 'What Hangar costs, and where Crossplane stops',
    dek: "Forty-seven tools is a bill, not a feature. What it costs to run, what I'd cut for a smaller team, and the line I draw between things that should be reconciled and things that should just happen once.",
    date: '2026-09-28',
    minutes: 9,
  },
];
