# Hangar roadmap: Airframe A+, Autopilot, and the Skyport AI workloads

This is the unified plan. It replaces the "next" section of the 2026-09-25 Skyport handoff and folds
in three streams that used to be separate: Skyport's remaining phases, the Airframe A+ program, and
Autopilot. All durations are estimates for one person; **ordering matters more than the numbers.**

Diagrams: `diagrams/plan/01-hangar-family.html`, `02-roadmap.html`, `03-dependencies.html`,
`04-scorecard.html`.

## 1. The shape of the plan

```
   Skyport (demo + quickstarts) ──────────────┐   builds new components → born A+
   Airframe A+ (AF-1 … AF-10) ─────────────────┼── contract first, so nothing is retrofitted
   Autopilot (Clearance, AgentRun, tools) ────┤   depends on the contract and ownership split
   Skyport AI workloads (parts 6-11) ─────────┘   depends on Autopilot phases A and B
```

**Why this order.** Three reasons, each of which would cost weeks if ignored:

1. **Build the contract before the next components.** MongoDB and OAuth are next in Skyport. If they
   ship before the contract exists, each needs a retrofit for outputs, verify checks and schema
   strictness. Ship the contract foundation first and they are born A+.
2. **Ownership before agents.** An agent that can edit a file mixing human and machine-owned keys is a
   risk that path-level scope cannot contain. Split the files (AF-5) before granting Clearance write tools.
3. **The planner is the acceptance test.** The parachute sentence needs AF-1 to AF-6 and the Autopilot
   core. Everything before it is a prerequisite; everything after it (Skyport AI) is a consumer.

**What changed from the 2026-09-25 plan:**

| Old | New |
|---|---|
| Phase 2 remainder: `baggage-api` next | Still first (M0), and used to dogfood `airframe validate` |
| Phase 3: MongoDB | M1, built as the first born-A+ component |
| Phase 4: OAuth | M2, born A+ |
| Phase 5: nginx (optional) | M5, born A+ |
| (none) | Airframe A+ program, Autopilot, six AI workloads |

## 2. Milestones

Score targets are the scorecard's overall (baseline 27/100, A+ needs 97 and 14 of 14 checks).

### M0 Stabilize and baseline (weeks 1-2), scorecard target 35
| Task | Notes |
|---|---|
| **AF-10a** chart guard: no Rollout until an image exists | worktree, test-via-copy on a scratch app; then flip `Features.rollout_guard`; the canary test in `tests/test_airframe_plan.py` fails on purpose when it lands |
| **AF-10b** chart tests and chart CI; scorecard in CI | baseline is committed; CI fails on regression |
| **AF-1a** `AGENTS.md` at the Airframe root | draft in `docs/autopilot/drafts/airframe/AGENTS.md` |
| **AF-4a** `airframe validate` v0: strict-derived schema and `helm template` | use it on `baggage-api`'s env files as they are written |
| **SP-2r** `baggage-api` (Python) through the current flow | record every stumble as a scorecard item; this is the manual version of the parachute sentence |
| **AP-0** answer the unverified list (section 5) | 30 to 60 minutes each; they de-risk M2 and M3 |
| **DX-0** decide and create the `autopilot` repo | move `~/tech/clearance` there; pytest as CI |

**Exit:** the guard is live on dev; `airframe validate` catches an injected typo on a real PR; `baggage-api` runs on dev; every item in section 5 has an answer.

### M1 Contract (weeks 3-6), target 60
| Task | Notes |
|---|---|
| **AF-2** strict schema, generated from one source | warn first, sweep the fleet, then enforce; descriptions to 95%; discriminated `components[]` |
| **AF-3** component outputs and `fromComponent` | Redis, Postgres, RabbitMQ, SecretStore |
| **AF-4b** `airframe validate` layers 3 to 6, dead-end rules seeded | required check on app, gitops and tenants repos |
| **AF-1b** contract bundle, `llms.txt`, XRD summaries | the generator from AF-2 emits the bundle |
| **AF-6a** status helper and reason codes | on the XRDs touched in this milestone |
| **SP-3** MongoDB component, then `baggage-api` on it (part 4 complete) | first born-A+ component: outputs, verify, sidecar meta, `AGENTS.md`, every field described |

**Exit:** typo acceptance is 0% across every live file; the Mongo component ships with its contract; validate is a required, green check on three repos.

### M2 Safe write (weeks 7-10), target 75
| Task | Notes |
|---|---|
| **AF-5** base layer and release-file split | migrate dev first, then kind-prod, each via a scratch app; coordinate airframe, glidepath's `open-release-pr` and deploy stage, and Tower's Config tab |
| **AF-5b** ownership gate, risk classes, comment-preserving patch engine | |
| **AF-9a** field-level `agent-scope` specified and tested | Clearance policy grows a JSON-pointer allow and deny |
| **SP-4** OAuth component, `skyport-auth`, enforced JWTs (part 5) | born A+ |
| **AF-7a** walkthrough runner; convert quickstart parts 1 to 3 | each step: command, expected result, verify |

**Exit:** no live file mixes owners; a release PR and a config PR never conflict (property test); part 1 replays green from a walkthrough.

### M3 Autopilot core (weeks 11-18), target 88
| Task | Notes |
|---|---|
| **AP-A1** apron `components.autopilot` toggle, registry `autopilotReady`, network-policy canary | refused on `type: upper`; the canary fails honestly on kiac-dev |
| **AP-A2** Clearance as an InfraService; T0 tools with real adapters | Backstage MCP, ArgoCD read-only account |
| **AP-A3** `AgentRun` XRD, `function-agentrun`, `provider-kubernetes` grants, namespaced Role | copy-tested; expiry proven with Clearance stopped and with the function pod killed |
| **AP-B1** interceptor `/agent-installation-token`, separate GitHub App, ArgoCD accounts | commit-signing decision executed |
| **AP-B2** T1 tools with real adapters; `agent-scope` and `agent-identity` gates, stub then real | field-aware, from AF-9a |
| **AP-B3** model proxy v0 (HTTP forwarder), hosted model route, key via Infisical | |
| **AF-8** `airframe.*` tools, planner adapters | **the parachute sentence passes live**, with a seeded bad run and a resume test |
| **AF-6b** `describe` and verify contracts; **AF-10c** chart `agent:` block | |
| **AP-C1** Flight recorder: `task_id` everywhere, audit chain anchor | |

**Exit:** the parachute sentence works end to end on dev (a human merges the flight PRs); killing Clearance mid-run still ends every run on time; the seeded bad run scores as failed.

### M4 Skyport AI workloads (weeks 19-24), target 93
Parts 6 to 11, in shape order: task, session, service, scheduled, event, team. Each is walked live, has
a Checkride case with a seeded bad run, and updates its quickstart's verified-state note.

| Task | Notes |
|---|---|
| Part 6 `flight-briefer` | first agent; proves the whole path |
| Part 7 `gate-copilot` | session channel and Tower's chat and approvals |
| Part 8 `passenger-assistant` | the hardened-sandbox fail-closed moment; injection test |
| Part 9 `delay-digest` | trigger runner; artifact store |
| Part 10 `disruption-responder` | trigger bridge; redelivery and storm demos |
| Part 11 `irregular-ops-team` | narrow-only, a denied spawn, a checker catching a wrong fact |
| Tower Agent tab; `Agent` XRD and two templates; Holmes via Clearance (drop `github-mcp-token`) | |

**Exit:** six Checkride cases pass and their seeded bad runs fail; one `task_id` traces a disruption from broker message to final artifact.

### M5 Evidence and widen (weeks 25-28), target 97 and 14 of 14
- Checkride as a regression gate on the Autopilot repo: profile, model and policy changes are PRs that must pass.
- Autonomy tracker for one alert class (shadow, then approve, then auto), with the breaker.
- Modelplane hub trial on a dedicated kind cluster, behind the OpenAI-compatible contract.
- Part 12: the nginx edge (optional), born A+.
- Conformance on kind-prod: upper clusters get no runs, and a run cannot be created there.
- The A+ run: scorecard 14 of 14 and overall at least 97, recorded.

## 3. Critical path
`chart guard → validate → contract → ownership split → Autopilot core → planner (parachute) → Skyport AI`.
Parallel and safe to interleave: Skyport components (born A+), docs and walkthroughs, the Autopilot
repo setup, Modelplane reading. Do not parallelize the ownership split with Clearance write tools.

## 4. Decisions
| # | Decision | Recommendation | Needed by |
|---|---|---|---|
| D1 | Commit signing for agent PRs | sign with the self-hosted Fulcio; extend the `provenance` gate; do not exempt agent PRs | M3 |
| D2 | AgentRun as an XR | yes (not a bare Job, not a controller) | M3 |
| D3 | Clearance standalone or a Backstage module | standalone, federating Backstage MCP | M3 |
| D4 | A separate GitHub App for agents | yes, so agent traffic cannot starve CI of API budget | M3 |
| D5 | Audit store | enable MinIO object lock when the bucket is created | before AP-C1 |
| D6 | Hub isolation for Modelplane | per-environment hub, dedicated accounts | before M5 |
| D7 | **Checkride's name** | Airworthiness (open; the user likes Autopilot, Clearance, Flight recorder) | before AP-B2 |
| D8 | A new `autopilot` repo | yes; `clearance/` becomes a package in it | M0 |
| D9 | Release-file split and the ArgoCD `exclude` | prove on a scratch app first | M2 |
| D10 | Strictness rollout dates | warn in M1, enforce at the end of M1 | M1 |
| D11 | Debugging a run without pod exec | accept: debug via output, logs and audit | M3 |
| D12 | Where agent code lives | `airframe/examples/skyport/agents/` | M4 |

## 5. Unverified: answer these in M0
| # | Question | How to check |
|---|---|---|
| U1 | Does ArgoCD apply XRs so that unknown fields are rejected, or pruned silently? | apply an XR with a bogus field to kiac-dev via a scratch Application |
| U2 | Does the function response TTL re-invoke `function-agentrun` near expiry? | a toy composition on a scratch namespace; the expiry test in M3 depends on it |
| U3 | Is Backstage's `mcpActions` endpoint live on a cluster? | request it from the Tower backend |
| U4 | Were Tower's Tier 1 write actions ever live-verified? | click Refresh, Sync and Re-run against a genuinely stuck app |
| U5 | Does the ArgoCD glob `*-lower/*` match `<app>-lower` AppProject names? | `argocd proj list` against the policy |
| U6 | Does Helm ignore unknown `x-hangar-*` keywords in `values.schema.json`? | `helm lint` on a schema with the keys |
| U7 | Can the ArgoCD git files generator exclude `*.release.yaml`? | a scratch ApplicationSet |
| U8 | Does provider-kubernetes accept the rendered Namespace, Quota, NetworkPolicy, ServiceAccount and Job? | `crossplane render` is not possible without Docker; use a scratch XR on kiac-dev |
| U9 | Is pgvector available in the CloudNativePG image? | only if a vector store is wanted |
| U10 | What do Modelplane's usage records contain, and does short-lived auth work for `Existing` clusters? | read a real record, in the M5 trial |

## 6. Risks
- **One person, many repos.** airframe, glidepath, backstage, apron, the tenants repos and a new repo all change. Keep every change small, behind a gate, and reversible. Use worktrees.
- **Retrofit cost** if the contract slips behind the next components. Hence the ordering.
- **kiac-dev does not enforce NetworkPolicy.** `autopilotReady` is gated on a canary, and runs are never trusted on a claim.
- **kind-prod is resource-limited** (12 GB, observability scaled to 0). Runs are dev-only; kind-prod gets none.
- **Hosted model cost.** Token budgets and the breaker; two on-demand or scheduled spenders in the demo.
- **Upstream churn.** Modelplane is v0.1 and the mcp SDK is v2; both sit behind contracts and pins.
- **Strictness breaks an environment.** Warn first, sweep the fleet, then enforce.

## 7. First ten actions
1. Read `HANDOFF-hangar-autopilot-airframe-a-plus.md` and check each repo's branch and status.
2. Decide D8 (the `autopilot` repo) and D7 (Checkride's name).
3. Answer U1, U5, U6 and U7 (quick, no cluster changes).
4. Write the chart guard in an Airframe worktree with a fixture test; run it through a scratch app.
5. Wire the scorecard and chart tests into CI.
6. Commit `AGENTS.md` for Airframe.
7. Build `airframe validate` v0 (schema plus `helm template`).
8. Provision `baggage-api` through the current flow and log each stumble.
9. Put `airframe validate` on `baggage-api`'s PRs.
10. Re-run the scorecard and update this file's status.
