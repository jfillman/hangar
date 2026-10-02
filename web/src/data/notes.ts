// Field notes: shorter, looser posts than the Architecture essays. Tools I like, things I've learned, work
// outside Hangar. Newest first.
export type Note = { slug: string; title: string; dek: string; date: string; minutes: number; tags?: string[] };

export const notes: Note[] = [
  {
    slug: 'origin',
    title: 'How Hangar started, and what AI taught me along the way',
    dek: "Two projects at once: rebuild my home lab into a real platform, and learn to build with AI while doing it. Five mockups, a Star Trek replicator moment, a name that changed jobs, and the token bills I didn't see coming. Plus the lesson I'd pass on first: how to manage your sessions.",
    date: '2026-10-02',
    minutes: 9,
    tags: ['Hangar', 'AI'],
  },
  {
    slug: 'diagram-design',
    title: 'A shout-out to diagram-design',
    dek: "Every diagram on this site was drawn by an AI agent using one skill, Cathryn Lavery's diagram-design. What it is, why it works, and how Hangar uses it.",
    date: '2026-10-02',
    minutes: 3,
    tags: ['Open source', 'Diagrams'],
  },
  {
    slug: 'radar',
    title: 'A shout-out to Radar, and what I added to it',
    dek: "Radar is the Kubernetes UI I'd been waiting for. Here's who built it, what Skyhook offers alongside it, and the Tekton and Argo Rollouts features I added while learning to build with AI.",
    date: '2026-09-30',
    minutes: 5,
    tags: ['Open source', 'Kubernetes UI'],
  },
];
