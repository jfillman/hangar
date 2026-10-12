// The Library's papers: reviews, reports and specs, next to the diagrams. Newest first.
//
// A paper is either an illustrated page built by tools/library (docs/library/, copied to
// public/papers/ by scripts/sync-assets.mjs) and shown at /library/<id>/, or a page that
// already lives elsewhere on the site (the docs, the scorecard), linked with `href`.
// `status` is the tracking half: what happened to the paper's findings, or where the spec stands.
export type Kind = 'review' | 'report' | 'spec';
export type Tone = 'done' | 'open' | 'info';
export type Paper = {
  id: string;
  kind: Kind;
  title: string;
  dek: string;
  date: string;
  product: 'hangar' | 'glidepath' | 'airframe' | 'tower' | 'autopilot' | 'site';
  page?: string;
  href?: string;
  status: { label: string; tone: Tone };
};

export const KIND_LABELS: Record<Kind, string> = { review: 'Reviews', report: 'Reports', spec: 'Specs and plans' };
export const KIND_BLURBS: Record<Kind, string> = {
  review: 'Someone, or something, looked hard at the work and said what they thought. Each one says what I did about it.',
  report: 'Measurements and findings: what a run, a test or an investigation actually showed.',
  spec: 'Designs, requirements and plans, written before the work and kept honest after it.',
};

export const papers: Paper[] = [
  {
    id: 'crossplane-v2-vocabulary', kind: 'review', product: 'hangar', date: '2026-10-05',
    title: 'Is "claim" the right word in a Crossplane v2 world?',
    dek: 'ChatGPT\'s analysis of one word across the site and docs, checked against the v2 docs and every repo: what held up, what didn\'t, and what changed.',
    page: 'papers/2026-10-05-crossplane-v2-vocabulary.html',
    status: { label: 'Done · 4 PRs merged', tone: 'done' },
  },
  {
    id: 'scorecard', kind: 'report', product: 'airframe', date: '2026-10-09',
    title: 'The Airframe A+ scorecard',
    dek: 'How ready Airframe is for agents to operate, scored by a tool against fourteen checks. Every committed run on one chart.',
    href: 'scorecard/',
    status: { label: '84 · past the M2 target', tone: 'done' },
  },
  {
    id: 'architecture-review', kind: 'review', product: 'hangar', date: '2026-09-27',
    title: 'Would a staff architect approve Hangar?',
    dek: 'A platform-approval review of the whole of Hangar: a conditional yes, ten findings with evidence, and five gates before production.',
    href: 'review/', page: 'reviews/2026-09-27-architecture-review.html',
    status: { label: 'Open · production gates', tone: 'open' },
  },
  {
    id: 'site-feedback-review', kind: 'review', product: 'site', date: '2026-09-27',
    title: 'What two reviews said about this site, and what I did about it',
    dek: 'Grok and ChatGPT on hangarplatform.dev a day after launch: eleven suggestions, eight shipped, two declined, and why.',
    page: 'papers/2026-09-27-site-feedback-review.html',
    status: { label: 'Done · 8 changes live', tone: 'done' },
  },
  {
    id: 'adr-0021-phase1', kind: 'report', product: 'glidepath', date: '2026-10-06',
    title: 'Release facts from the Rollout: phase 1 results',
    dek: 'One real gate-api release reported down both paths at once, the old hook Jobs and the new Rollout facts. The events matched.',
    href: 'docs/glidepath/admin/adr/0021-phase1-results/',
    status: { label: 'Exit criterion met', tone: 'done' },
  },
  {
    id: 'adr-0021-phase0', kind: 'report', product: 'glidepath', date: '2026-10-05',
    title: 'Release facts from the Rollout: phase 0 findings',
    dek: 'Five spikes before building: does the Rollouts notifications engine deliver the facts a release needs? Yes, with three design rules.',
    href: 'docs/glidepath/admin/adr/0021-phase0-findings/',
    status: { label: 'All spikes resolved', tone: 'done' },
  },
  {
    id: 'autopilot-design', kind: 'spec', product: 'autopilot', date: '2026-09-26',
    title: 'Autopilot design',
    dek: 'How Hangar runs any AI agent workload, bounded and audited: the planes, the Clearance gateway and the AgentRun XR.',
    href: 'docs/hangar/autopilot/design/',
    status: { label: 'Core built · runtime proposed', tone: 'open' },
  },
  {
    id: 'airframe-a-plus', kind: 'spec', product: 'airframe', date: '2026-09-26',
    title: 'The Airframe A+ program',
    dek: 'What it would take for agents to operate Airframe safely, as milestones the scorecard measures.',
    href: 'docs/hangar/autopilot/airframe-ai-friendly/',
    status: { label: 'M2 closed · 84 of 100', tone: 'done' },
  },
  {
    id: 'envs-overhaul', kind: 'spec', product: 'glidepath', date: '2026-10-04',
    title: 'Environments overhaul: requirements and plan',
    dek: 'Environments as one config model, defined once in cicd.yaml, with Glidepath owning the folder and the chart contract.',
    href: 'docs/glidepath/admin/envs-overhaul-requirements/',
    status: { label: 'Approved · migration done', tone: 'done' },
  },
  {
    id: 'break-glass-design', kind: 'spec', product: 'tower', date: '2026-10-11',
    title: 'Break-glass design decisions',
    dek: 'Emergency access to a cluster from Tower: short-lived, recorded, reviewed afterwards, and loud while it lasts.',
    href: 'docs/tower/break-glass/admin/design/',
    status: { label: 'Built', tone: 'done' },
  },
  {
    id: 'service-catalog-design', kind: 'spec', product: 'hangar', date: '2026-08-12',
    title: 'Service catalog design',
    dek: 'The running design log behind Airframe: every round of the catalog, from the first XRD to secret stores.',
    href: 'docs/hangar/service-catalog-design/',
    status: { label: 'Living document', tone: 'info' },
  },
  {
    id: 'gitops-strategy', kind: 'spec', product: 'hangar', date: '2026-08-12',
    title: 'GitOps strategy',
    dek: 'Two clusters, one source of truth: how repos, AppProjects and promotion fit together, and why upper and lower are a real boundary.',
    href: 'docs/hangar/gitops-strategy/',
    status: { label: 'Built', tone: 'done' },
  },
];

export const byKind = (kind: Kind) => papers.filter((p) => p.kind === kind).sort((a, b) => b.date.localeCompare(a.date));
export const paper = (id: string) => papers.find((p) => p.id === id);
