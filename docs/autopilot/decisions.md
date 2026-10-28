# Decisions log

Answers to the open decisions in [roadmap.md](roadmap.md), recorded 2026-09-26.

| Id | Decision | Status |
|---|---|---|
| D1 | Sign agent commits with a self-hosted Fulcio. A self-signed root CA for it is acceptable and to be evaluated. | Decided |
| D2 | `AgentRun` is a namespaced Crossplane v2 XR (no Claim, composed by `function-agentrun`). | Decided |
| D3 | Clearance is a standalone component (its own deployment, one Kubernetes permission). | Decided |
| D4 | Agents get their own GitHub App, separate from the platform's. | Decided |
| D5 | Audit object lock: take the recommendation in roadmap.md. | Decided |
| D6 | Model-hub isolation: needs more context. | **Decided 2026-09-26:** hosted providers only for now (option 1); one hub per environment with dedicated accounts (option 2) is the M5 default |
| D7 | Name for the evaluation harness. | **Decided 2026-09-26: Preflight** (replaces the working name Checkride) |
| D8 | A new `autopilot` repo, with Clearance as a package inside it. | Decided |
| D9 | Release-file split: yes; design it fully and prove it out. | Decided; designed and proven live on the dev cluster ([release-file-split.md](release-file-split.md)); Glidepath's writer change still to build |
| D10 | Strictness rollout timing. | **Decided 2026-09-26: option A, enforce now.** Gate built (validator image, `values-check`); becomes required once every gitops repo has the check file. See [briefings-d6-d10.md](briefings-d6-d10.md) |
| D11 | Take the recommendation in roadmap.md. | Decided |
| D12 | Take the recommendation in roadmap.md. | Decided |

All experiments (U1–U12) in the roadmap run on the dev cluster.

## 2026-09-26, substrate review

Accepted: stable agent identity (AP-A4), model version in the record (AP-C1), cost accounting (AP-C2), upstream Agent Sandbox evaluation (U11), resumable state (AP-D1, U12), fixed T0 read set (AF-2b), rejection of a monolithic `AgentWorkspace`. See [industry-context.md](industry-context.md).

## 2026-10-09, before M3

| Id | Decision |
|---|---|
| D1 (detail) | Create a new Hangar root CA for the platform's Fulcio, rather than each cluster's self-generated root. |
| D13 | `cicd.yaml` is agent-editable: an agent allowed to configure an app may configure its CI/CD. It leaves Clearance's `BASELINE_DENY_PATHS` (`.tekton/**` stays). Human-only fields and rules (governance, releaseFile, chart, cloud targets, secrets, environment tier/production/cluster, gitops-image-bump, automatic production releases) are listed in roadmap.md "M3 status". |
| D14 | Holmes stays scaled to 0 on both clusters, on purpose; A5 (Holmes through Clearance) is deferred with it. |
| D15 | The U8 ClusterRole for AgentRun's provider-kubernetes objects is approved (`autopilot/airframe-drafts/rbac/provider-kubernetes-agentrun.yaml`). It ships only together with a ValidatingAdmissionPolicy confining the provider's service account to run namespaces, the agent-sandbox resources in place of Jobs, and a stable service-account binding; see roadmap.md "M3 status". |

kiac-dev enforces NetworkPolicy (Cilium 1.20), verified 2026-10-09; the AP-A1 canary is expected to pass there.

## 2026-10-28, Clearance becomes a product

Sources: the Clearance Brief, Architecture and Roadmap (2026-10-27/28). What they change in Autopilot is in [design.md section 0.1](design.md).

| Id | Decision |
|---|---|
| D4 (reconfirmed) | Agents get their own GitHub App. It is a different App from Clearance's provenance App: the one that writes agent PRs must not be the one that attests their provenance. |
| D5 (revised) | Audit integrity comes from the Clearance ledger: record hashes in a Tessera log, with checkpoints countersigned by at least one witness Clearance does not operate. MinIO object lock remains for retention only. |
| D16 | Clearance is a standalone Hangar product with its own `clearance` repo. This supersedes D8 for the package (the `autopilot` repo stays). The proposed split: policy, scope, sessions, gateway, audit and the deployment gate go to `clearance`; definitions, Preflight, AgentRun, the planner and the Hangar tool backends stay in `autopilot`. The owner accepted this split on 2026-10-28. |
| D17 | **Open:** the runtime boundary as an AuthZEN PDP behind Traefik Hub's Sovereign Trust Plane, or Clearance's own gateway. Hangar runs Traefik Proxy (not Hub), so the own gateway ships now, with the decision refactored into a pure, AuthZEN-shaped function. |
| D18 | AF-8a, the read-only `airframe.*` tools, is built before AP-A3. |
| AP-A2 | Built in this plan, not in a separate lab. Clearance is Hangar's AI gateway whatever the product's go/stop gates decide. |
