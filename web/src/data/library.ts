// The Library's papers: reviews, reports and specs, next to the diagrams. Newest first.
//
// A paper is either an illustrated page built by tools/library (docs/library/, copied to
// public/papers/ by scripts/sync-assets.mjs) and shown at /library/<id>/, or a page that
// already lives elsewhere on the site (the docs, the scorecard), linked with `href`.
// `status` is the tracking half: what happened to the paper's findings, or where the spec stands.
export type Kind = 'review' | 'report' | 'spec' | 'architecture';
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

export const KIND_LABELS: Record<Kind, string> = { review: 'Reviews', report: 'Reports', spec: 'Specs and plans', architecture: 'Architecture' };
export const KIND_BLURBS: Record<Kind, string> = {
  review: 'Someone, or something, looked hard at the work and said what they thought. Each one says what I did about it.',
  report: 'Measurements and findings: what a run, a test or an investigation actually showed.',
  spec: 'Designs, requirements and plans, written before the work and kept honest after it.',
  architecture: 'How a product was actually wired on a given day, drawn from the code. Snapshots, so each one links to the living doc.',
};

export const papers: Paper[] = [
  {
    id: 'keyless-cloud-deploys', kind: 'spec', product: 'glidepath', date: '2026-10-16',
    title: 'No stored AWS key for cloud deploys',
    dek: 'Two never-expiring AWS keys replaced by one-hour roles a pod earns by proving who it is, one per Lambda function, with a hole in Crossplane\'s permissions closed on the way and the incident the switch caused.',
    page: 'papers/2026-10-16-keyless-cloud-deploys.html',
    status: { label: 'Lambda and ECS keyless', tone: 'done' },
  },
  {
    id: 'forge-registry-portability', kind: 'spec', product: 'hangar', date: '2026-10-15',
    title: 'Any forge, any registry',
    dek: 'A plan to run Hangar on GitLab and Bitbucket as well as GitHub, and on any OCI registry as well as GHCR: where GitHub is load-bearing today, two Hangar contracts with a driver per vendor, and six phases over about 24 weeks.',
    page: 'papers/2026-10-15-forge-registry-portability.html',
    status: { label: 'Proposed · 7 decisions open', tone: 'info' },
  },
  {
    id: 'tower-release-record-lifecycle', kind: 'spec', product: 'tower', date: '2026-10-13',
    title: 'Start the next release record when the last one ships',
    dek: 'A proposal to open Tower\'s Release Record as a live draft the moment the previous release ships, with sign-off before the Flight merge and an outcome after the bake.',
    page: 'papers/2026-10-13-tower-release-record-lifecycle.html',
    status: { label: 'Built · R1 to R4 shipped', tone: 'done' },
  },
  {
    id: 'glidepath-sdlc-review', kind: 'review', product: 'glidepath', date: '2026-10-12',
    title: 'Glidepath against the everyday software lifecycle',
    dek: 'A CI/CD review read from the code: strong from merge to production, thin on the inner loop, and most of its governance advises rather than enforces.',
    page: 'papers/2026-10-12-glidepath-sdlc-review.html',
    status: { label: 'Open · roadmap written', tone: 'open' },
  },
  {
    id: 'glidepath-production-roadmap', kind: 'spec', product: 'glidepath', date: '2026-10-12',
    title: 'Glidepath, from the lab to production',
    dek: 'The companion to the SDLC review: every weakness sorted by cause, and nine items in three lanes so a production install never waits on a feature it doesn\'t need.',
    page: 'papers/2026-10-12-glidepath-production-roadmap.html',
    status: { label: 'Under way · T2 and P3 started', tone: 'open' },
  },
  {
    id: 'tower-field-report-2', kind: 'report', product: 'tower', date: '2026-10-11',
    title: 'Tower, judged again as my only console',
    dek: 'Four weeks on: yes for looking, now yes for acting. What still sends me elsewhere is the platform under the console, not a missing button.',
    page: 'papers/2026-10-11-tower-field-report-2.html',
    status: { label: 'Open · 4 of 16 done', tone: 'open' },
  },
  {
    id: 'autopilot-architecture-map', kind: 'architecture', product: 'autopilot', date: '2026-10-07',
    title: 'Autopilot, drawn as Kubernetes resources',
    dek: 'One request through every resource it touches, the five documents that make up an agent\'s contract, and six things the code said that the docs didn\'t.',
    page: 'papers/2026-10-07-autopilot-architecture-map.html',
    status: { label: 'Snapshot · Oct 7, 2026', tone: 'info' },
  },
  {
    id: 'airframe-service-catalog', kind: 'architecture', product: 'airframe', date: '2026-09-20',
    title: 'Airframe, the service catalog underneath',
    dek: 'Eleven XRDs that turn a git commit into a running service, without any cluster ever holding credentials for another cluster\'s API.',
    page: 'papers/2026-09-20-airframe-service-catalog.html',
    status: { label: 'Snapshot · Sep 20, 2026', tone: 'info' },
  },
  {
    id: 'tower-field-report-1', kind: 'report', product: 'tower', date: '2026-09-14',
    title: 'Tower, judged as my only console',
    dek: 'Would I give up kubectl, Argo CD and the Tekton dashboard for Tower? Mostly for looking, not yet for acting, and a backlog to close the gap.',
    page: 'papers/2026-09-14-tower-field-report-1.html',
    status: { label: '10 of 11 done', tone: 'done' },
  },
  {
    id: 'airframe-crossplane-agent-api', kind: 'review', product: 'airframe', date: '2026-10-08',
    title: 'How well does Airframe use Crossplane, and can an agent drive it?',
    dek: 'Twenty findings on the Crossplane layer and the agent-facing API, ranked, and what happened to each one in the two days after.',
    page: 'papers/2026-10-08-airframe-crossplane-agent-api.html',
    status: { label: '15 of 20 fixed', tone: 'done' },
  },
  {
    id: 'glidepath-pipeline-performance', kind: 'report', product: 'glidepath', date: '2026-10-08',
    title: 'Where does a Glidepath pipeline spend its time?',
    dek: 'Three weeks of Tekton history, measured: most of the wall-clock was pods starting up to do almost nothing. Nine fixes, eight shipped.',
    page: 'papers/2026-10-08-glidepath-pipeline-performance.html',
    status: { label: '8 of 9 done', tone: 'done' },
  },
  {
    id: 'tower-break-glass', kind: 'spec', product: 'tower', date: '2026-10-10',
    title: 'Looking inside a production pod, without ever handing out exec',
    dek: 'Break-glass in Tower: a debug container instead of exec, a second person, a recording of every byte, and guardrails the cluster enforces. With its two-person test plan.',
    page: 'papers/2026-10-10-tower-break-glass.html',
    status: { label: 'Built · live', tone: 'done' },
  },
  {
    id: 'tower-cluster-credentials', kind: 'spec', product: 'tower', date: '2026-10-10',
    title: 'No long-lived Kubernetes credential for Tower, anywhere',
    dek: 'A never-expiring token replaced by federated ten-minute tokens, reads split from writes, and a bigger hole closed on the way.',
    page: 'papers/2026-10-10-tower-cluster-credentials.html',
    status: { label: 'Phases 0 to 4 live', tone: 'done' },
  },
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
    status: { label: '86.6 · past the M2 target', tone: 'done' },
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
    status: { label: 'M2 closed · 86.6 of 100', tone: 'done' },
  },
  {
    id: 'envs-overhaul', kind: 'spec', product: 'glidepath', date: '2026-10-04',
    title: 'Environments overhaul: requirements and plan',
    dek: 'Environments as one config model, defined once in cicd.yaml, with Glidepath owning the folder and the chart contract.',
    href: 'docs/glidepath/admin/envs-overhaul-requirements/',
    status: { label: 'Approved · migration done', tone: 'done' },
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
