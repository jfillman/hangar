// The five architectural themes the site is organised around. Each one names the claim,
// then the places in Hangar that carry it today, with an honest status on each.
import { gh, ghTree } from '../lib/url';

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
    slug: 'control-plane',
    n: '01',
    name: 'An intelligent, custom control plane',
    claim: 'The platform is an API, and the API is a control plane that keeps reconciling.',
    body: [
      'A platform built from scripts and tickets can only be driven by people. A platform built as a control plane (declared intent, typed APIs, controllers that keep reality converged on it) can be driven by people, by a portal, by CI and by an AI agent, all through the same front door. That is the idea behind <a href="https://www.upbound.io/intelligent-control-plane">Upbound\'s intelligent control plane</a>, and it is the shape Hangar takes.',
      'In Hangar, Crossplane is the control plane and Airframe is its API. What a compliant service is (its app, its environments, its Redis, its SLOs) is defined once as XRDs and Compositions. Backstage\'s catalog is generated from those CRDs rather than hand-written beside them, so the portal can never describe a platform that does not exist.',
      'The intelligence lives in the control plane, not beside it. A Composition Function watches every Argo Rollout and, when one degrades, dispatches a diagnosis to a shared HolmesGPT service, which opens a fix PR. Autopilot takes the next step: an agent run is itself a claim to the control plane, typed, bounded and garbage-collected like any other resource.',
    ],
    evidence: [
      { text: 'Airframe: XRDs, Compositions and Composition Functions for the service catalog', status: 'built', href: gh('airframe') },
      { text: 'AI triage in the control plane: function-rollout-watcher and diagnosis dispatch, proven with a real broken canary, a real diagnosis and a real fix PR (2026-08-13)', status: 'built', href: ghTree('airframe', 'functions') },
      { text: 'The AgentRun XRD: an agent run as a claim to Crossplane', status: 'draft', href: gh('autopilot') },
      { text: 'Crossplane providers for the APIs the platform manages, generated with Upjet (Infisical)', status: 'built', href: gh('provider-infisical') },
    ],
    diagrams: ['plan/05-contract-architecture', 'autopilot/02-two-planes'],
    link: { href: 'platform/', label: 'How the platform fits together' },
  },
  {
    slug: 'event-driven',
    n: '02',
    name: 'Event-driven architecture',
    claim: 'Components announce what happened. Nothing reaches across a boundary to make something happen.',
    body: [
      'Coupling is the thing that makes platforms brittle, and a direct API call is the tightest coupling there is. Hangar\'s components talk in events: a stage finishing, a sync succeeding, a rollout degrading. Whoever cares subscribes.',
      'Glidepath chains independently triggered pipeline stages through a shared CDEvents broker. Upper clusters report deploy outcomes back to dev as events from ArgoCD sync hooks, never as a pushed credential. DORA metrics are not a separate integration: they are one more consumer of the same event stream. Autopilot\'s event-shaped agents start from the same kind of signal, a delayed flight in the Skyport demo becoming a draft, a team and a human decision.',
    ],
    evidence: [
      { text: 'CDEvents broker with TokenReview authentication (Glidepath ADR-0002)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0002-cdevents-broker-tokenreview.md') },
      { text: 'Outcomes from upper clusters flow back as events, not API calls (ADR-0005)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0005-multicluster-per-cluster-argocd.md') },
      { text: 'DORA exporter: a stateless consumer of the same CDEvents', status: 'built', href: ghTree('glidepath', 'platform/dora-exporter') },
      { text: 'Event-triggered agent workloads in Autopilot', status: 'proposal', href: gh('hangar', 'docs/autopilot/skyport-ai-workloads.md') },
    ],
    diagrams: ['glidepath/chaining-sequence', 'plan/08-skyport-event-to-team'],
    link: { href: 'sdlc/operate/', label: 'Events as the source for observability' },
  },
  {
    slug: 'beautiful-ui',
    n: '03',
    name: 'Interfaces worth looking at',
    claim: 'If the platform is a product, its interface is the product people actually see.',
    body: [
      'Engineers forgive an ugly tool; they do not adopt one. A clear, calm, good-looking interface is how a platform earns trust from people who never read its design docs, and it is where a platform\'s honesty shows: what is live, what is failing, what is waiting on a human.',
      'Tower is Hangar\'s single pane of glass, a Backstage plugin that follows a change through its lifecycle: pull requests, pipelines, deployments, releases, topology, images, SLOs. It adds fleet views (Fleet Grid, Ops Wall) and a release matrix that shows which release is live in which environment along the app\'s real promotion order. Every configuration change it makes is a GitOps pull request, never a direct commit.',
      'The same care goes into everything else a person reads: a brand system with one mark per product and a "calm cockpit" colour rule (amber for what needs attention, sky for what informs, grey for ground infrastructure at rest), a notification design language, and the diagrams across this site.',
    ],
    evidence: [
      { text: 'Tower: the Backstage plugin for release orchestration and operational intelligence', status: 'built', href: gh('tower') },
      { text: 'Hangar brand system: six marks, one family, calm-cockpit status colours', status: 'built', href: gh('hangar', 'brand/README.md') },
      { text: 'Glidepath notification design language', status: 'built', href: gh('glidepath', 'docs/admin/design-language.md') },
    ],
    diagrams: [],
    link: { href: 'diagrams/', label: 'All 44 diagrams' },
  },
  {
    slug: 'platform-as-product',
    n: '04',
    name: 'Platform as a service, run as a product',
    claim: 'Application developers write one file. Everything else is the platform\'s job.',
    body: [
      'A platform team\'s customer is the application developer, and the product is the time they get back. That means a small, stable contract on the developer\'s side and a lot of engineering on the platform\'s side, not the other way round.',
      'In Glidepath the contract is one file, <code>cicd.yaml</code>, validated against a JSON Schema with readable errors. Developers never see or edit Tekton YAML. Onboarding scaffolds that file along with the rest of the repo, so the first pipeline runs without anyone writing configuration by hand. Docs are split by audience (user and admin) and published through Tower\'s TechDocs, and known gaps are written down with their evidence, the way a product team keeps a backlog.',
    ],
    evidence: [
      { text: 'cicd.yaml: the one-file developer contract, with a JSON Schema', status: 'built', href: gh('glidepath', 'docs/user/cicd-yaml-reference.md') },
      { text: 'cicd.yaml scaffolded at onboarding, not hand-authored (ADR-0017)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0017-cicd-yaml-scaffolded-not-hand-authored.md') },
      { text: 'Self-service onboarding through Tower, as git commits', status: 'built', href: gh('tower') },
      { text: 'Known gaps, each with evidence and a direction', status: 'built', href: gh('glidepath', 'docs/admin/known-gaps.md') },
    ],
    diagrams: ['glidepath/pipeline-flow', 'glidepath/cicd-yaml-mapping'],
    link: { href: 'cicd/', label: 'CI/CD as a product: the Glidepath practices' },
  },
  {
    slug: 'paved-roads',
    n: '05',
    name: 'Paved roads, not just golden paths',
    claim: 'A golden path is advice. A paved road is the path of least resistance, with the guardrails built in.',
    body: [
      'A golden path documents the recommended way and hopes people take it. A paved road makes the recommended way the easiest one and builds the safety in: the defaults are secure, the checks run whether anyone remembers them or not, and leaving the road is possible but deliberate and visible.',
      'Hangar\'s roads are paved at every layer. The Airframe chart gives every service the same Rollout, NetworkPolicy, ExternalSecret and SLOs by default, with a curated library and an explicit escape hatch rather than a blank page. The pipeline is a fixed DAG whose stages are toggled, not a graph you assemble. Guardrails are enforced by admission policy and required checks, not by convention. And for agents, the paved road is the only road: every tool call goes through one gateway, and every durable change is a pull request that meets the same gates as a human\'s.',
    ],
    evidence: [
      { text: 'airframe-application: one chart, every tier, secure defaults', status: 'built', href: ghTree('airframe', 'charts') },
      { text: 'Kyverno ValidatingPolicy closes a gap RBAC cannot (ADR-0008)', status: 'built', href: gh('glidepath', 'docs/admin/adr/0008-kyverno-testkube-secret-policy.md') },
      { text: 'Release guardrails as required checks, enforced by a GitHub ruleset', status: 'built', href: gh('glidepath', 'docs/admin/release-guardrails.md') },
      { text: 'Clearance core: the policy, audit and session gateway every agent tool call goes through (real adapters are still a proposal)', status: 'built', href: gh('autopilot') },
    ],
    diagrams: ['reference/02-tool-gateway', 'autopilot/03-write-path-spine'],
    link: { href: 'sdlc/secure/', label: 'Guardrails in the SDLC' },
  },
];
