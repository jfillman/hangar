// The Architecture section: pointed opinions, one essay each. Newest first.
export type Essay = { slug: string; title: string; dek: string; date: string; minutes: number; series?: string };

export const essays: Essay[] = [
  {
    slug: 'why-testkube',
    title: 'Why Hangar runs its tests in Testkube',
    dek: "A proof of concept with a team of test engineers sold me on Testkube: tests as Kubernetes resources, parallel runs, any framework, and one place to see every result. How it works, why it fits an API-driven control plane, how Glidepath runs it today, and what the free tier taught me.",
    date: '2026-10-03',
    minutes: 10,
  },
  {
    slug: 'why-airframe',
    title: 'Why a platform still needs a service catalog',
    dek: "People and AI agents are going to be building software side by side for a long time. The service catalog is where the platform writes down what it offers, precisely enough for both. Why I think it matters more now than ever, where I'd push back on the usual version, and how I'd build one, starting with the developers.",
    date: '2026-09-30',
    minutes: 12,
  },
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
