# Decisions log

Answers to the open decisions in [roadmap.md](roadmap.md), recorded 2026-09-26.

| Id | Decision | Status |
|---|---|---|
| D1 | Sign agent commits with a self-hosted Fulcio. A self-signed root CA for it is acceptable and to be evaluated. | Decided |
| D2 | `AgentRun` is a Crossplane XR (namespaced claim, composed by `function-agentrun`). | Decided |
| D3 | Clearance is a standalone component (its own deployment, one Kubernetes permission). | Decided |
| D4 | Agents get their own GitHub App, separate from the platform's. | Decided |
| D5 | Audit object lock: take the recommendation in roadmap.md. | Decided |
| D6 | Model-hub isolation: needs more context. | Deferred; briefing written ([briefings-d6-d10.md](briefings-d6-d10.md)), recommendation: hosted providers now, one hub per environment at M5 |
| D7 | Name for the evaluation harness. | **Decided 2026-09-26: Preflight** (replaces the working name Checkride) |
| D8 | A new `autopilot` repo, with Clearance as a package inside it. | Decided |
| D9 | Release-file split: yes; design it fully and prove it out. | Decided; designed and proven live on kiac-dev ([release-file-split.md](release-file-split.md)); Glidepath's writer change still to build |
| D10 | Strictness rollout timing. | Open; briefing written ([briefings-d6-d10.md](briefings-d6-d10.md)), recommendation: enforce now (the fleet sweep is clean) |
| D11 | Take the recommendation in roadmap.md. | Decided |
| D12 | Take the recommendation in roadmap.md. | Decided |

All experiments (U1–U12) in the roadmap run on kiac-dev.

## 2026-09-26, substrate review

Accepted: stable agent identity (AP-A4), model version in the record (AP-C1), cost accounting (AP-C2), upstream Agent Sandbox evaluation (U11), resumable state (AP-D1, U12), fixed T0 read set (AF-2b), rejection of a monolithic `AgentWorkspace`. See [industry-context.md](industry-context.md).
