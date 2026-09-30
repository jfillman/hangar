// The Architecture section: pointed opinions, one essay each. Newest first.
export type Essay = { slug: string; title: string; dek: string; date: string; minutes: number; series?: string };

export const essays: Essay[] = [
  {
    slug: 'building-airframe',
    title: 'Building Airframe: the start of my Crossplane journey',
    dek: "I'd wanted to try Crossplane on one small secret store. Instead I built a whole service catalog on it. What six weeks of Airframe taught me about readiness, API budgets, and what a composition means when it renders nothing.",
    date: '2026-09-30',
    minutes: 11,
    series: 'Building Airframe, part 1',
  },
  {
    slug: 'cost-of-the-platform',
    title: 'What Hangar costs, and where Crossplane stops',
    dek: "Forty-seven tools is a bill, not a feature. What it costs to run, what I'd cut for a smaller team, and the line I draw between things that should be reconciled and things that should just happen once.",
    date: '2026-09-28',
    minutes: 9,
  },
];
