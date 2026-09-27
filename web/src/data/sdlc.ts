// The SDLC, seen from the platform side. Each stage: the opinion, how Hangar carries it,
// the diagrams that show it, and what changes when the author is an AI agent.
import { gh, ghTree } from '../lib/url';
import type { Evidence } from './principles';

export type Stage = {
  slug: string;
  n: string;
  name: string;
  short: string;
  principle: string;
  themes: string[]; // principle slugs from principles.ts
  body: string[];
  evidence: Evidence[];
  diagrams: { id: string; caption?: string }[];
  agents: { title: string; body: string[]; diagrams: string[] };
};

const adr = (n: string, file: string) => gh('glidepath', `docs/admin/adr/${n}-${file}.md`);

export const stages: Stage[] = [
  {
    slug: 'design',
    n: '01',
    name: 'Plan and design',
    short: 'Contracts first, decisions in writing',
    principle: 'Define what a compliant service is once, as an API, and write down why.',
    themes: ['control-plane', 'paved-roads'],
    body: [
      'Most platform drift starts at design time: every team decides for itself what a "service" is, and the platform spends years reconciling the differences. Hangar settles it once. Airframe\'s XRDs are the definition of a compliant service, and every other part of the platform (the portal, the pipeline, the chart, the agents) consumes that one contract rather than restating it.',
      'Decisions are written down as they are made, dated, and never quietly rewritten. Glidepath has seventeen architecture decision records; Hangar\'s design docs are kept as dated narrative on purpose, including the first attempts that did not survive contact with a real cluster. Every claim carries a status (Built, Draft or Proposal), so a reader always knows whether they are looking at the platform or at a plan.',
    ],
    evidence: [
      { text: 'Service catalog design: the running log behind Airframe', status: 'built', href: gh('hangar', 'docs/service-catalog-design.md') },
      { text: 'GitOps strategy: repo topology, ArgoCD split, the lower/upper boundary', status: 'built', href: gh('hangar', 'docs/gitops-strategy.md') },
      { text: 'Glidepath architecture decision records (17)', status: 'built', href: ghTree('glidepath', 'docs/admin/adr') },
    ],
    diagrams: [{ id: 'reference/03-golden-path-contract' }, { id: 'plan/05-contract-architecture' }],
    agents: {
      title: 'An agent is designed like a service: a reviewed definition, then a disposable run',
      body: [
        'Agent definitions are durable, schema-validated files in git, with baseline deny paths that cannot be removed. A run is created from a definition and thrown away afterwards. Designing the definition is the reviewed, slow part; running it is cheap.',
      ],
      diagrams: ['autopilot/05-definition-to-run'],
    },
  },
  {
    slug: 'onboard',
    n: '02',
    name: 'Onboard and code',
    short: 'One file, scaffolded for you',
    principle: 'A developer\'s first commit should run a pipeline, and they should only ever maintain one file.',
    themes: ['platform-as-product', 'paved-roads'],
    body: [
      'Onboarding is where a platform shows whether it is a product or a set of instructions. In Hangar, a developer picks an app stack in Tower (Node.js, Spring Boot, Go or Python). Airframe scaffolds the source repo, the Dockerfile and a real, build-only <code>cicd.yaml</code>, and the platform provisions namespaces, identity and delivery behind it. Nothing is created by an API call from the portal: Backstage holds no Kubernetes credentials at all, and every request becomes a git commit.',
      'The one file a developer maintains is <code>cicd.yaml</code>. It is read fresh from the triggering commit and validated against a JSON Schema, so a mistake fails fast with a readable error instead of halfway through a pipeline.',
    ],
    evidence: [
      { text: 'cicd.yaml scaffolded at onboarding (ADR-0017)', status: 'built', href: adr('0017', 'cicd-yaml-scaffolded-not-hand-authored') },
      { text: 'The cicd.yaml reference and schema', status: 'built', href: gh('glidepath', 'docs/user/cicd-yaml-reference.md') },
      { text: 'Apron: a template for a new cluster repo, one config file and one script', status: 'built', href: gh('apron') },
    ],
    diagrams: [
      { id: 'glidepath/04-onboarding-sequence' },
      { id: 'glidepath/03-cicd-yaml-mapping' },
    ],
    agents: {
      title: 'From one sentence to a reviewed change set',
      body: [
        'The AppSpec planner compiles a plain-language request ("the parachute sentence") into the exact change set a human would have written, checked against the real XRD schemas, Glidepath\'s schema and a real <code>helm template</code>. The agent proposes a pull request; onboarding is still a reviewed commit.',
      ],
      diagrams: ['plan/06-plan-apply-sequence'],
    },
  },
  {
    slug: 'build',
    n: '03',
    name: 'Build and test',
    short: 'Rootless builds, pinned catalogs, real tests',
    principle: 'Build without privilege, pin what you share, and test against the real thing.',
    themes: ['platform-as-product', 'event-driven'],
    body: [
      'The pipeline is a fixed superset DAG whose stages are switched on and parameterised by <code>cicd.yaml</code>, not an arbitrary graph compiled from user config. That is a deliberate limit: it keeps every tenant\'s pipeline recognisable and supportable, and a compiler is a heavier pattern than the problem has needed so far.',
      'Images are built with kaniko under Pod Security Standards <code>restricted</code>: no privileged daemon, no host access, on any cluster. The shared Tekton catalog is a Helm release pinned by git tag, so upgrading a tenant is a reviewed change to a pin and a catalog change can be tried on a canary tenant first. Stages are separate PipelineRuns chained by events, which keeps each one small and independently re-runnable.',
      'Tests run in Testkube, and that decision is a good example of the habit behind this site: the documented multi-namespace mode turned out, in the source code, to be gated to a paid edition. The design that shipped runs in one shared namespace and closes the resulting secret-isolation gap with an admission policy.',
    ],
    evidence: [
      { text: 'Tekton plus Pipelines-as-Code, one fixed DAG (ADR-0001)', status: 'built', href: adr('0001', 'tekton-pipelines-as-code') },
      { text: 'Kaniko for rootless builds (ADR-0010)', status: 'built', href: adr('0010', 'kaniko-rootless-builds') },
      { text: 'A git-tag-pinned shared catalog (ADR-0013)', status: 'built', href: adr('0013', 'catalog-git-tag-pinned-distribution') },
      { text: 'Testkube in one shared namespace (ADR-0007)', status: 'built', href: adr('0007', 'testkube-shared-namespace') },
      { text: 'PR preview environments on the same chart, sha-only tags, TTL cleanup (ADR-0012)', status: 'built', href: adr('0012', 'ephemeral-environments-airframe-application') },
    ],
    diagrams: [{ id: 'glidepath/02-pipeline-flow' }, { id: 'glidepath/05-chaining-sequence' }],
    agents: {
      title: 'CI is the loop an agent retries against',
      body: [
        'For an agent, the pipeline is not just a gate; it is the feedback signal. Fast, deterministic checks with readable errors are what let an agent fix its own change before a human ever looks at it.',
      ],
      diagrams: ['reference/04-validation-loop'],
    },
  },
  {
    slug: 'secure',
    n: '04',
    name: 'Secure and govern',
    short: 'Honest gates, workload identity, no stored keys',
    principle: 'A gate that silently passes is worse than no gate at all, because it is trusted.',
    themes: ['paved-roads', 'control-plane'],
    body: [
      'Governance gates (SAST, image scanning, policy, SBOM) exist from day one as explicit extension points, and any gate that is still a stub says so loudly in its result and on the dashboard. Each is promoted to real enforcement on its own, and none is ever reported with more confidence than it has earned.',
      'Identity comes from the platform, not from secrets the platform has to guard. The event broker authenticates callers with Kubernetes TokenReview against each pod\'s own projected token. Images and provenance are signed keylessly against a self-hosted Fulcio that trusts the cluster\'s own issuer, while commits are signed against public Sigstore, because a human\'s GitHub identity is what the public instance already trusts. Release policy validates the provenance attestation itself (which tasks really ran), in addition to the commit signature, not instead of it.',
      'Tenancy is structural: every app gets a CI namespace and one namespace per environment, as peers, so pipeline permissions and running workloads never share a blast radius. Secrets come through External Secrets from Infisical, with no persisted credentials, and an admission policy closes the case RBAC cannot express.',
    ],
    evidence: [
      { text: 'Governance gates as structurally loud extension points (ADR-0003)', status: 'built', href: adr('0003', 'governance-stubs') },
      { text: 'Keyless signing with two trust roots (ADR-0014)', status: 'built', href: adr('0014', 'keyless-signing-two-trust-roots') },
      { text: 'Provenance policy validates the attestation as input (ADR-0015)', status: 'built', href: adr('0015', 'provenance-policy-validates-attestation-input') },
      { text: 'Two-namespace tenancy (ADR-0011)', status: 'built', href: adr('0011', 'two-namespace-tenancy-model') },
      { text: 'External Secrets with self-hosted Infisical (ADR-0009)', status: 'built', href: adr('0009', 'eso-infisical-secrets-backend') },
    ],
    diagrams: [{ id: 'reference/06-identity-blast-radius' }],
    agents: {
      title: 'An agent PR meets the same gates, plus two that are about agents',
      body: [
        'Agents are identities with a blast radius, not users with a token. Effective authority is the minimum of five inputs, and at runtime it can only go down. An agent\'s pull request passes every gate a human\'s does, plus scope and authority checks of its own.',
      ],
      diagrams: ['autopilot/14-pr-guardrails', 'autopilot/13-effective-authority'],
    },
  },
  {
    slug: 'release',
    n: '05',
    name: 'Release and deploy',
    short: 'Only a merged commit crosses a boundary',
    principle: 'No cluster holds another cluster\'s credentials. The only thing that crosses a boundary is a reviewed, merged commit.',
    themes: ['event-driven', 'control-plane'],
    body: [
      'Deploy and release answer different questions, so they get different rigor. Deploy is the fast inner loop to a lower environment: did my change work at all? Release is governed promotion: the release stage never touches a cluster. It opens a pull request against the app\'s GitOps repo, carrying the exact image digest that already passed test and deploy (never rebuilt). Governance gates report as required checks, a human reviews, and ArgoCD\'s own sync is the only thing that ever changes the target cluster.',
      'Every upper cluster runs its own ArgoCD watching the same GitOps repo, instead of one ArgoCD holding credentials for them all, because a remote-cluster credential is just the dev-to-prod blast radius moved somewhere else. Outcomes come back to dev as events. The first version used ArgoCD Notifications; live testing showed it fired on any sync, including drift correction with no release involved, so it was replaced with sync hooks that fire only when a release really converges.',
      'Workloads roll out as Argo Rollouts with analysis templates from a curated library, and the lower/upper environment split is enforced by a separate AppProject, not just by folder names.',
    ],
    evidence: [
      { text: 'GitOps-only release promotion (ADR-0004)', status: 'built', href: adr('0004', 'gitops-only-release') },
      { text: 'Per-cluster ArgoCD, event-driven outcomes (ADR-0005)', status: 'built', href: adr('0005', 'multicluster-per-cluster-argocd') },
      { text: 'Cluster-agnostic bootstrap: no cluster state in the app repo (ADR-0006)', status: 'built', href: adr('0006', 'cluster-agnostic-bootstrap') },
      { text: 'Lower and upper environments as an enforced security boundary', status: 'built', href: gh('hangar', 'docs/gitops-strategy.md') },
    ],
    diagrams: [
      { id: 'glidepath/06-deploy-vs-release' },
      { id: 'glidepath/07-multi-cluster-topology' },
      { id: 'reference/05-multicloud-gitops' },
    ],
    agents: {
      title: 'Durable changes are commits. Ephemeral runs are claims.',
      body: [
        'An agent\'s durable write is a git write, and it goes through the same release path as everyone else\'s. Only its run, which is short-lived, stateless and rebuildable from git, is created directly, as a narrowly scoped claim to Crossplane on dev clusters. Upper clusters get neither.',
      ],
      diagrams: ['autopilot/02-two-planes', 'autopilot/03-write-path-spine'],
    },
  },
  {
    slug: 'operate',
    n: '06',
    name: 'Operate and observe',
    short: 'One trace per change, one pane of glass',
    principle: 'Every change should be one trace you can follow end to end, and no metric should claim more certainty than it has.',
    themes: ['event-driven', 'beautiful-ui'],
    body: [
      'Every pipeline step emits an OpenTelemetry span, and the spans are stitched into one Tempo trace per end-to-end flow, even though each stage is a separate PipelineRun. Grafana shows the live and historical pipeline list, a per-stage drill-down and DORA metrics computed from the CDEvents stream. MTTR is shown as experimental, because a rollback done outside the pipeline is a blind spot that would otherwise make it quietly wrong.',
      'Run history is archived with Tekton Results; stalled pipelines are detected and alerted on; old runs are pruned. Tower brings it together for the people running services: releases per environment, rollout topology, SLO burn rates and fleet-wide views.',
      'When a rollout degrades, the control plane itself asks for a diagnosis and comes back with a fix PR.',
    ],
    evidence: [
      { text: 'Tracing: one Tempo trace per flow', status: 'built', href: gh('glidepath', 'docs/admin/tracing.md') },
      { text: 'DORA metrics from CDEvents, MTTR marked experimental', status: 'built', href: gh('glidepath', 'docs/admin/dora-metrics.md') },
      { text: 'Tekton Results archival (ADR-0016)', status: 'built', href: adr('0016', 'tekton-results-archival') },
      { text: 'Tower: SLOs, topology, Fleet Grid, Ops Wall', status: 'built', href: gh('tower') },
    ],
    diagrams: [{ id: 'glidepath/01-architecture-overview' }],
    agents: {
      title: 'A flight recorder for agents, and alerts that arrive with a tested hypothesis',
      body: [
        'Agent observability reuses the same telemetry and adds one tamper-evident, hash-chained audit trail. Triage moves from a bespoke integration to a bounded agent behind Clearance, and remediation earns autonomy one alert class at a time.',
      ],
      diagrams: ['autopilot/15-flight-recorder', 'reference/09-auto-remediation', 'autopilot/17-triage-before-after'],
    },
  },
  {
    slug: 'improve',
    n: '07',
    name: 'Measure and improve',
    short: 'Scorecards, evals and written-down gaps',
    principle: 'Measure it, publish the number, then move it. Write down every gap you find, with its evidence.',
    themes: ['platform-as-product'],
    body: [
      'A platform improves when its weaknesses are visible. Hangar measures how operable Airframe is by agents with a scorecard (ten dimensions, a committed baseline of 27 out of 100, and an A+ bar at 97 with all fourteen acceptance checks passing), and publishes the number rather than a feeling.',
      'Gaps found in real use are written down with their reproduction and a direction, not left in someone\'s head: Glidepath\'s known-gaps list is a product backlog in plain sight. Agent changes get the same treatment as code: Preflight scores every change against incidents that have already been solved.',
    ],
    evidence: [
      { text: 'Airframe scorecard and its committed baseline', status: 'built', href: ghTree('hangar', 'tools/airframe-scorecard') },
      { text: 'Glidepath known gaps, found in use, each with evidence', status: 'built', href: gh('glidepath', 'docs/admin/known-gaps.md') },
      { text: 'Preflight evaluation cases', status: 'built', href: gh('autopilot') },
    ],
    diagrams: [{ id: 'plan/04-scorecard' }],
    agents: {
      title: 'Evaluate agents like a regression suite, and let them earn autonomy',
      body: [
        'An infrastructure agent is judged by a regression suite built from real incidents, not by a demo. Autonomy is granted per alert class, earned by a track record, and revocable.',
      ],
      diagrams: ['autopilot/16-preflight', 'reference/10-agent-eval-harness', 'reference/08-autonomy-ladder'],
    },
  },
];
