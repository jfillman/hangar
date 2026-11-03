# Autopilot: AI agent workloads on Hangar

Autopilot is Hangar's sixth product: it runs any AI agent workload, bounded and audited, and it drives
the Airframe A+ program that makes the service catalog operable by agents.

> **One idea:** an agent is one more author of git commits. **Durable changes are commits. Ephemeral
> runs are direct requests to Crossplane.** Everything else follows from keeping those two planes apart.

**Brand:** the mark is Option A, Hold, chosen 2026-09-26; the five options considered are in `docs/brand/autopilot-logo-options.html` in the repo (open the file in a browser; TechDocs cannot link to standalone HTML), and the files are in [`brand/marks/`](../../brand/marks/).

**Code:** [github.com/jfillman/autopilot](https://github.com/jfillman/autopilot) (Hangar's backends, the `autopilot-gateway` image, triggers, agent definitions, Preflight cases, the AppSpec planner, the agent runtimes) and [github.com/jfillman/clearance](https://github.com/jfillman/clearance) (the policy, audit and session gateway, D16). **Status (2026-11-02):** M0 to M2 closed; M3's AP-A1, AP-A2, AP-A3, AP-B1 (less commit signing), AP-B2, AP-B2c, AP-B3 and AF-8a are built and live on hangar-dev (clearance v0.26.1 in gateway-v0.3.27); scorecard **97.3, 14 of 14**. Clearance is a product of its own: its runtime boundary is live, and the deployment gate's core and its GitHub App (check runs, deployment protection rule, `clearance register`) are built, with admission still to come. See [design.md section 0.1](design.md) and the roadmap's M3 status.

## Read in this order
| Doc | Read this when... |
|---|---|
| [roadmap.md](roadmap.md) | You want the plan: milestones M0 to M5, dependencies, decisions, unverified items, and the first ten actions. |
| [airframe-ai-friendly.md](airframe-ai-friendly.md) | You want the A+ program: the measured baseline, the ten workstreams, and the design. |
| [release-file-split.md](release-file-split.md) | You want to know how machine-owned and human-owned values will live in separate files, and the live proof. |
| [briefings-d6-d10.md](briefings-d6-d10.md) | You need to decide D6 (model hub) or D10 (when strictness starts blocking). |
| [design.md](design.md) | You want the Autopilot design: two planes, the workload model, tiers, policy, backends, failure modes. Section 0.1 is what Clearance becoming a product changes. |
| [skyport-ai-workloads.md](skyport-ai-workloads.md) | You want the six demo agents, one per workload shape, and their tests. |
| [glossary.md](glossary.md) | A term is unfamiliar. |
| [Diagram gallery](https://hangarplatform.dev/diagrams/) | You want pictures: 8 plan diagrams, 19 for Autopilot, 10 reference. |

## Where things are
| What | Where |
|---|---|
| Scorecard and the committed baseline | `hangar/tools/airframe-scorecard/` |
| Clearance (406 tests at v0.26.1) | the `clearance` repo (D16) |
| Hangar backends, the gateway image, planner, agent definitions, Preflight cases, runtimes (554 tests at gateway-v0.3.27) | the `autopilot` repo |
| Diagram generator | `hangar/tools/diagrams/` |
| Airframe drafts (`AGENTS.md`, sidecar meta) | [drafts/airframe/](drafts/airframe/) |
| The Skyport demo | `airframe/docs/user/skyport-demo.md` and `airframe/examples/skyport/` |

## Status, 2026-11-02
| | |
|---|---|
| Design | complete; Clearance-as-a-product folded in (design.md 0.1); the 2026-11-02 build spec moves the AI gateway into Autopilot and Clearance to Go |
| Clearance runtime boundary (gateway, policy, evidence chain, model proxy, inbox, person controls, run results, clearance-api) | **Built**, live on hangar-dev: clearance v0.26.1, 406 tests |
| Clearance deployment gate | core **Built** (v0.19.0) and fed by the advisory `clearance-gate-` check and `clearance register`; admission **Proposal** |
| Clearance GitHub App (`Hangar Clearance`) | **Built**, live: check runs (v0.21.0), deployment protection rule (v0.22.0), `clearance register` (v0.23.0) |
| Evidence signing, checkpoint, witness, ledger | **Proposal**, on the Clearance product roadmap |
| Autopilot gateway, backends, triggers, runtimes | **Built**, live: gateway-v0.3.27, 554 tests; runtime images generic, base-python, langgraph, claude-agent-sdk |
| `AgentRun` XRD, composition, function; `Agent` XRD | **Built**, live on hangar-dev (airframe catalog v0.3.172) |
| Scorecard | **Built**; **97.3 / 100**, 14 of 14 acceptance checks (baseline 27.3) |
| hangar-prod | nothing of Clearance or Autopilot runs there; Tower reads clearance-api on hangar-dev |

## Run it
```bash
python3 hangar/tools/airframe-scorecard/scorecard.py                # the grade
cd ~/tech/autopilot && ./.venv/bin/python -m pytest -q               # 554 tests
cd ~/tech/clearance && ./.venv/bin/python -m pytest -q               # 406 tests (Postgres ones need CLEARANCE_TEST_DSN)
```
