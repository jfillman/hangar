# Autopilot: AI agent workloads on Hangar

Autopilot is Hangar's sixth product: it runs any AI agent workload, bounded and audited, and it drives
the Airframe A+ program that makes the service catalog operable by agents.

> **One idea:** an agent is one more author of git commits. **Durable changes are commits. Ephemeral
> runs are claims to Crossplane.** Everything else follows from keeping those two planes apart.

**Code:** [github.com/jfillman/autopilot](https://github.com/jfillman/autopilot) (public; the `clearance` Python package, agent definitions, Preflight cases, the AppSpec planner, `AgentRun` drafts). **Status (2026-09-26):** M0 is nearly done; see the [roadmap](roadmap.md) status block. New: [release-file-split.md](release-file-split.md) (designed and proven), [briefings-d6-d10.md](briefings-d6-d10.md) (two decisions for you).

## Read in this order
| Doc | Read this when... |
|---|---|
| [roadmap.md](roadmap.md) | You want the plan: milestones M0 to M5, dependencies, decisions, unverified items, and the first ten actions. |
| [airframe-ai-friendly.md](airframe-ai-friendly.md) | You want the A+ program: the measured baseline, the ten workstreams, and the design. |
| [release-file-split.md](release-file-split.md) | You want to know how machine-owned and human-owned values will live in separate files, and the live proof. |
| [briefings-d6-d10.md](briefings-d6-d10.md) | You need to decide D6 (model hub) or D10 (when strictness starts blocking). |
| [design.md](design.md) | You want the Autopilot design: two planes, the workload model, tiers, policy, backends, failure modes. |
| [skyport-ai-workloads.md](skyport-ai-workloads.md) | You want the six demo agents, one per workload shape, and their tests. |
| [glossary.md](glossary.md) | A term is unfamiliar. |
| [diagrams/index.html](diagrams/index.html) | You want pictures: 8 plan diagrams, 19 for Autopilot, 10 reference. |

## Where things are
| What | Where |
|---|---|
| Scorecard and the committed baseline | `hangar/tools/airframe-scorecard/` |
| Clearance, planner, Skyport agent definitions, Preflight cases, AgentRun drafts (255 tests) | `~/tech/autopilot` (moves to an `autopilot` repo, decision D8) |
| Diagram generator | `hangar/tools/diagrams/` |
| Airframe drafts (`AGENTS.md`, sidecar meta) | [drafts/airframe/](drafts/airframe/) |
| The Skyport demo | `airframe/docs/user/skyport-demo.md` and `airframe/examples/skyport/` |

## Status, 2026-09-26
| | |
|---|---|
| Design | complete; two design changes from the owner folded in |
| Clearance core, planner, definitions, cases | **Built**, 255 tests |
| Scorecard | **Built**; baseline **27 / 100**, 1 of 14 acceptance checks |
| `AgentRun` XRD, composition, function | **Draft**, never applied |
| Real adapters, auth, the model proxy forwarder, CI gates | **Proposal** |
| Nothing is committed | all of this is uncommitted working-tree files |

## Run it
```bash
python3 hangar/tools/airframe-scorecard/scorecard.py                # the grade
cd ~/tech/autopilot && ./.venv/bin/python -m pytest -q               # 255 tests
```
