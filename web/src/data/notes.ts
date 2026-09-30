// Field notes: shorter, looser posts than the Architecture essays. Tools I like, things I've learned, work
// outside Hangar. Newest first.
export type Note = { slug: string; title: string; dek: string; date: string; minutes: number; tags?: string[] };

export const notes: Note[] = [
  {
    slug: 'radar',
    title: 'A shout-out to Radar, and what I added to it',
    dek: "Radar is the Kubernetes UI I'd been waiting for. Here's who built it, what Skyhook offers alongside it, and the Tekton and Argo Rollouts features I added while learning to build with AI.",
    date: '2026-09-30',
    minutes: 5,
    tags: ['Open source', 'Kubernetes UI'],
  },
];
