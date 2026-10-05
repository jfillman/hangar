// The seven principles the site is organised around, in order of how much they shape the work.
// Each one says what I believe, why, and where Hangar does it today, with an honest status.
import { gh, ghTree, u } from '../lib/url';

export type Status = 'built' | 'draft' | 'proposal';
export type Evidence = { text: string; status: Status; href?: string };

export type Principle = {
  slug: string;
  n: string;
  name: string;
  claim: string;
  body: string[];
  evidence: Evidence[];
  diagrams: string[];
  link?: { href: string; label: string };
};

export const principles: Principle[] = [
  {
    slug: 'platform-as-product',
    n: '01',
    name: 'The platform is a product',
    claim: 'The people using the platform are its customers, and the thing it sells is their time.',
    body: [
      'Everything else on this page follows from this one. A platform team exists so that the people building the business can spend their day on the business. That means a small, friendly contract on their side and a lot of careful engineering on ours, never the other way round.',
      'In Glidepath, that contract is a single file, <code>cicd.yaml</code>. Developers never have to read or write Tekton YAML, and when they get something wrong the schema tells them what, in plain words, before anything runs. New apps get that file scaffolded for them, so their very first push already runs a pipeline. The docs are written for two audiences (the people using the platform and the people running it), and the rough edges are written down in public, the way a product team keeps a backlog.',
    ],
    evidence: [
      { text: 'cicd.yaml: one file for developers, with a JSON Schema behind it', status: 'built', href: gh('glidepath', 'docs/user/cicd-yaml-reference.md') },
      { text: 'cicd.yaml scaffolded at onboarding rather than hand-written (ADR-0017)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0017-cicd-yaml-scaffolded-not-hand-authored.md') },
      { text: 'Self-service onboarding through Tower, with every request becoming a git commit', status: 'built', href: gh('tower') },
    ],
    diagrams: ['glidepath/02-pipeline-flow'],
    link: { href: 'cicd/', label: 'CI/CD as a product: the Glidepath practices' },
  },
  {
    slug: 'reviewed-commits',
    n: '02',
    name: 'Every change is a reviewed commit',
    claim: 'If it changes a cluster, it went through git and someone could have said no.',
    body: [
      'This is the thread that runs through my whole career. At Best Buy Canada it meant moving roughly 450 applications across 7 clusters from hand-run <code>kubectl apply</code> to a declarative, git-driven model. In Hangar it goes further: no cluster holds credentials for another cluster, no component calls across a cluster boundary, and the only thing that ever crosses one is a merged pull request.',
      'It sounds strict, and it is, but it buys a lot. Every change has an author, a reviewer and a history. Rolling back is a revert. Backstage holds no Kubernetes credentials at all, so even "create me a new service" is a commit someone can read. And when AI agents arrive, they fit straight in: an agent is just one more author of pull requests.',
    ],
    evidence: [
      { text: 'GitOps-only release: ArgoCD\'s sync is the only thing that changes a cluster (ADR-0004)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0004-gitops-only-release.md') },
      { text: 'An ArgoCD per cluster, with no remote-cluster credentials anywhere (ADR-0005)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0005-multicluster-per-cluster-argocd.md') },
      { text: 'The GitOps strategy, and the guiding constraint every later design carries forward', status: 'built', href: gh('hangar', 'docs/gitops-strategy.md') },
      { text: 'Agents change the platform only through pull requests', status: 'built', href: gh('hangar', 'docs/autopilot/design.md') },
    ],
    diagrams: ['glidepath/07-multi-cluster-topology', 'autopilot/03-write-path-spine'],
    link: { href: 'sdlc/release/', label: 'Release and deploy, the GitOps way' },
  },
  {
    slug: 'control-plane',
    n: '03',
    name: 'An API-driven control plane, ready for AI',
    claim: 'The platform should be an API that keeps reconciling, so people, portals and agents can all drive it the same way.',
    body: [
      'A platform built from scripts and tickets can only be driven by people. A platform built as a control plane (declared intent, typed APIs, and controllers that keep nudging reality back towards it) can be driven by a person, a portal, a pipeline or an AI agent, all through the same front door. That is the idea behind <a href="https://www.upbound.io/intelligent-control-plane">Upbound\'s intelligent control plane</a>, and it is the shape Hangar takes.',
      'Crossplane is the control plane and Airframe is its API. What a well-behaved service is (its app, its environments, its Redis, its SLOs) is defined once, and Backstage\'s catalog is generated from those definitions rather than written beside them. The intelligence lives in the control plane too: when a rollout degrades, a Composition Function asks for a diagnosis and comes back with a fix PR. Autopilot takes the next step and makes an agent run just another claim, typed, bounded and cleaned up like anything else.',
    ],
    evidence: [
      { text: 'Airframe: XRDs, Compositions and Composition Functions for the service catalog', status: 'built', href: gh('airframe') },
      { text: 'AI triage inside the control plane, proven end to end with a real broken canary and a real fix PR', status: 'built', href: ghTree('airframe', 'functions') },
      { text: 'The AgentRun XR: an agent run as a Crossplane resource', status: 'draft', href: gh('autopilot') },
      { text: 'A Crossplane provider for Infisical, generated with Upjet', status: 'built', href: gh('provider-infisical') },
    ],
    diagrams: ['plan/05-contract-architecture', 'autopilot/02-two-planes'],
    link: { href: 'platform/', label: 'How the platform fits together' },
  },
  {
    slug: 'paved-roads',
    n: '04',
    name: 'Paved roads, with security built in',
    claim: 'The safe way should also be the easy way, so nobody has to choose.',
    body: [
      'A golden path is good advice: here is how we recommend you do it. A paved road goes further. The recommended way is also the easiest one, the checks run whether anyone remembers them or not, and leaving the road is possible but deliberate. Security belongs in the road itself, not in a review at the end of it.',
      'I learned this the practical way, building PCI-driven supply-chain controls into pipelines rather than around them. In Hangar, every service gets the same secure defaults from one chart. Images are built without privilege and signed without long-lived keys. Release policy checks what the build really did, not just who signed it. Secrets come from the cluster\'s own identity, so there are no stored credentials to leak, and admission policy closes the gaps RBAC can\'t express. For agents, the paved road is the only road: every tool call goes through one gateway.',
    ],
    evidence: [
      { text: 'airframe-application: one chart for every tier, secure by default', status: 'built', href: ghTree('airframe', 'charts') },
      { text: 'Keyless signing and provenance checks on every release (ADR-0014, ADR-0015)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0014-keyless-signing-two-trust-roots.md') },
      { text: 'Secrets through the cluster\'s own identity, with nothing persisted (ADR-0009)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0009-eso-infisical-secrets-backend.md') },
      { text: 'Clearance core: the gateway every agent tool call goes through (real adapters are still a proposal)', status: 'built', href: gh('autopilot') },
    ],
    diagrams: ['glidepath/06-deploy-vs-release', 'reference/02-tool-gateway'],
    link: { href: 'sdlc/secure/', label: 'Security and governance in the lifecycle' },
  },
  {
    slug: 'event-driven',
    n: '05',
    name: 'Event-driven by default',
    claim: 'Components say what happened. Whoever cares, listens.',
    body: [
      'Coupling is what makes platforms brittle, and a direct call from one system into another is the tightest coupling there is. So Hangar\'s parts talk in events instead: a stage finished, a sync succeeded, a rollout degraded. Anything that cares can subscribe, and nothing has to know who is listening.',
      'Glidepath chains its pipeline stages through a shared CDEvents broker. Upper clusters report back to dev as events, never by reaching in. DORA metrics aren\'t a separate integration, just one more listener on the same stream. And Autopilot\'s event-shaped agents start from the same kind of signal: in the Skyport demo, a delayed flight becomes a draft, a small team of agents and, finally, a human decision.',
    ],
    evidence: [
      { text: 'A CDEvents broker, authenticated with TokenReview (ADR-0002)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0002-cdevents-broker-tokenreview.md') },
      { text: 'Outcomes from other clusters come back as events, not API calls (ADR-0005)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0005-multicluster-per-cluster-argocd.md') },
      { text: 'DORA exporter: a quiet listener on the same events', status: 'built', href: ghTree('glidepath', 'platform/dora-exporter') },
      { text: 'Event-triggered agent workloads in Autopilot', status: 'proposal', href: gh('hangar', 'docs/autopilot/skyport-ai-workloads.md') },
    ],
    diagrams: ['glidepath/05-chaining-sequence', 'plan/08-skyport-event-to-team'],
    link: { href: 'sdlc/operate/', label: 'Events as the source for observability' },
  },
  {
    slug: 'honest',
    n: '06',
    name: 'Honest by design',
    claim: 'A platform earns trust by saying exactly what it can and can\'t do yet.',
    body: [
      'The most dangerous thing a platform can do is look finished when it isn\'t. A security gate that always passes is worse than no gate, because people trust it. A metric that quietly drifts is worse than no metric, because people act on it.',
      'So Hangar is honest on purpose. Every design claim is labelled Built, Draft or Proposal. A governance gate that isn\'t real yet says "stub" everywhere it appears. MTTR is shown as experimental because I know where its blind spot is. When the docs and the source code disagree, the source wins, and the finding gets written down. And the problems I find using my own platform go on a public known-gaps list with their evidence. It is a small habit, and I think it matters more than almost anything else here.',
    ],
    evidence: [
      { text: 'Governance gates that are loud about being stubs (ADR-0003)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0003-governance-stubs.md') },
      { text: 'Glidepath known gaps, found in real use, each with its evidence', status: 'built', href: gh('glidepath', 'docs/admin/known-gaps.md') },
      { text: 'The Airframe scorecard: a published number, tracked over time, rather than a feeling', status: 'built', href: u('scorecard/') },
    ],
    diagrams: ['plan/04-scorecard'],
    link: { href: 'sdlc/improve/', label: 'Measuring and improving' },
  },
  {
    slug: 'interfaces',
    n: '07',
    name: 'Interfaces people trust',
    claim: 'A calm, clear, good-looking interface is how a platform earns the trust of people who never read its docs.',
    body: [
      'I like beautiful tools, and I don\'t think that\'s vanity. Engineers forgive an ugly tool, but they rarely love one, and they don\'t adopt what they don\'t love. A good interface is also where a platform\'s honesty shows up: what\'s live, what\'s failing, and what\'s waiting on a person.',
      'Tower is Hangar\'s single pane of glass, a Backstage plugin that follows a change through its whole life: pull requests, pipelines, deployments, releases, topology, images and SLOs, plus fleet views and a release matrix that shows which version is live where. Every configuration change it makes is a pull request. The same care goes into everything else people read: a brand with one mark per product and a "calm cockpit" colour rule, a shared notification style, and the diagrams you\'ll find across this site.',
    ],
    evidence: [
      { text: 'Tower: release orchestration and operational intelligence for Backstage', status: 'built', href: gh('tower') },
      { text: 'The Hangar brand system: six marks, one family, calm-cockpit colours', status: 'built', href: gh('hangar', 'brand/README.md') },
      { text: 'Glidepath\'s notification design language', status: 'built', href: gh('glidepath', 'docs/admin/design-language.md') },
    ],
    diagrams: [],
    link: { href: 'diagrams/', label: 'All 44 diagrams' },
  },
];
