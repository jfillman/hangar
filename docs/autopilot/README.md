# Autopilot: AI agent workloads on Hangar

Autopilot is Hangar's sixth product: it runs any AI agent workload, bounded and audited, and it drives
the Airframe A+ program that makes the service catalog operable by agents.

> **One idea:** an agent is one more author of git commits. **Durable changes are commits. Ephemeral
> runs are direct requests to Crossplane.** Everything else follows from keeping those two planes apart.

**Brand:** the mark is Option A, Hold, chosen 2026-09-26; the five options considered are in `docs/brand/autopilot-logo-options.html` in the repo (open the file in a browser; TechDocs cannot link to standalone HTML), and the files are in [`brand/marks/`](../../brand/marks/).

**Code:** [github.com/jfillman/autopilot](https://github.com/jfillman/autopilot) (public; the `clearance` Python package, agent definitions, Preflight cases, the AppSpec planner, `AgentRun` drafts). **Status (2026-10-28):** M0 to M2 closed; M3 in progress (AP-A1 done, AF-8a next); scorecard 89.5, 11 of 14. **Clearance is now a product of its own** with a runtime gateway (built, Autopilot's) and a deployment gate (proposed); its code moves to a `clearance` repo. See [design.md section 0.1](design.md) and the roadmap's M3 status.

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
| Clearance, planner, Skyport agent definitions, Preflight cases, AgentRun drafts (308 tests) | the `autopilot` repo; Clearance's package moves to a `clearance` repo (D16) |
| Diagram generator | `hangar/tools/diagrams/` |
| Airframe drafts (`AGENTS.md`, sidecar meta) | [drafts/airframe/](drafts/airframe/) |
| The Skyport demo | `airframe/docs/user/skyport-demo.md` and `airframe/examples/skyport/` |

## Status, 2026-10-28
| | |
|---|---|
| Design | complete; Clearance-as-a-product folded in (design.md 0.1) |
| Clearance runtime gateway, planner, definitions, cases | **Built**, 308 tests, 23 rules; `glidepath.*` tools live through MCP |
| Clearance deployment gate, evidence record, ledger | **Proposal**, on the Clearance product roadmap |
| Scorecard | **Built**; **89.5 / 100**, 11 of 14 acceptance checks (baseline 27.3) |
| `AgentRun` XRD, composition, function | **Draft**, never applied |
| Clearance deployed on a cluster | not yet (AP-A2) |

## Run it
```bash
python3 hangar/tools/airframe-scorecard/scorecard.py                # the grade
cd ~/tech/autopilot && ./.venv/bin/python -m pytest -q               # 308 tests
```
