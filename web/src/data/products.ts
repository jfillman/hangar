import { gh } from '../lib/url';

export const products = [
  { key: 'hangar', name: 'Hangar', tag: 'Home base for building, releasing, and watching every service you run.', role: 'The platform as a whole: design, docs and the running status.', repo: gh('hangar') },
  { key: 'airframe', name: 'Airframe', tag: 'The structural core: what a compliant service is, defined once.', role: 'Crossplane XRDs, Compositions and Functions, and the one application chart every tier deploys through.', repo: gh('airframe') },
  { key: 'glidepath', name: 'Glidepath', tag: 'The guarded descent from a merged commit to a verified release.', role: 'CI/CD on Tekton and Pipelines-as-Code, chained by CDEvents, released by GitOps.', repo: gh('glidepath') },
  { key: 'tower', name: 'Tower', tag: 'Release orchestration and operational intelligence for Backstage.', role: 'The single pane of glass: releases, deployments, SLOs and fleet views.', repo: gh('tower') },
  { key: 'apron', name: 'Apron', tag: 'Ground infrastructure a cluster needs before a Hangar can run on it.', role: 'The template for a new cluster repo: one config file, one script, a known bootstrap order.', repo: gh('apron') },
  { key: 'autopilot', name: 'Autopilot', tag: 'Any AI agent workload, bounded and audited.', role: 'Clearance (policy, audit, sessions), agent definitions, Preflight evaluations and the AgentRun claim.', repo: gh('autopilot') },
];
