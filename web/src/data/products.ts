import { gh } from '../lib/url';
import type { Status } from './principles';

// status/state: how finished each product is, shown on its card. Keep it honest when a product moves on.

export const products: { key: string; name: string; tag: string; role: string; repo: string; status: Status; state: string }[] = [
  { key: 'hangar', name: 'Hangar', tag: 'Home base for building, releasing, and watching every service you run.', role: 'The platform as a whole: design, docs and the running status.', repo: gh('hangar'), status: 'built', state: 'Running' },
  { key: 'airframe', name: 'Airframe', tag: 'The structural core: what a compliant service is, defined once.', role: 'Crossplane XRDs, Compositions and Functions, and the one application chart every tier deploys through.', repo: gh('airframe'), status: 'built', state: 'Built' },
  { key: 'glidepath', name: 'Glidepath', tag: 'The guarded descent from a merged commit to a verified release.', role: 'CI/CD on Tekton and Pipelines-as-Code, chained by CDEvents, released by GitOps.', repo: gh('glidepath'), status: 'built', state: 'Built' },
  { key: 'tower', name: 'Tower', tag: 'Release orchestration and operational intelligence for Backstage.', role: 'The single pane of glass: releases, deployments, SLOs and fleet views.', repo: gh('tower'), status: 'built', state: 'Built' },
  { key: 'apron', name: 'Apron', tag: 'Ground infrastructure a cluster needs before a Hangar can run on it.', role: 'The template for a new cluster repo: one config file, one script, a known bootstrap order.', repo: gh('apron'), status: 'built', state: 'Built' },
  { key: 'autopilot', name: 'Autopilot', tag: 'Any AI agent workload, bounded and audited.', role: 'Clearance (policy, audit, sessions), agent definitions, Preflight evaluations and the AgentRun XR.', repo: gh('autopilot'), status: 'draft', state: 'Early: core built, runtime proposed' },
];
