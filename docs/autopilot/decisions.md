# Decisions log

Answers to the open decisions in [roadmap.md](roadmap.md), recorded 2026-09-26.

| Id | Decision | Status |
|---|---|---|
| D1 | Sign agent commits with a self-hosted Fulcio. A self-signed root CA for it is acceptable and to be evaluated. | Decided |
| D2 | `AgentRun` is a Crossplane XR (namespaced claim, composed by `function-agentrun`). | Decided |
| D3 | Clearance is a standalone component (its own deployment, one Kubernetes permission). | Decided |
| D4 | Agents get their own GitHub App, separate from the platform's. | Decided |
| D5 | Audit object lock: take the recommendation in roadmap.md. | Decided |
| D6 | Model-hub isolation: needs more context. | Deferred |
| D7 | Checkride's name. "Checkride" is preferred over "Airworthiness", but neither is liked. | Open, needs a better name |
| D8 | A new `autopilot` repo, with Clearance as a package inside it. | Decided |
| D9 | Release-file split: yes; design it fully and prove it out. | Decided, next design task |
| D10 | Needs more context before answering. | Open |
| D11 | Take the recommendation in roadmap.md. | Decided |
| D12 | Take the recommendation in roadmap.md. | Decided |

Experiments U1–U8 in the roadmap run on kiac-dev.
