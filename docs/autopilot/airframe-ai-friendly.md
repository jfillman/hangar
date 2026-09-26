# Airframe A+ program: a service catalog an AI agent can operate

Goal: an agent (Claude Code, a workload, a client) can discover, configure, validate, change and
verify anything Airframe manages, using only machine-readable contracts and governed tools, and can
tell when it has failed and why. Success is measured, not felt: `tools/airframe-scorecard/scorecard.py`.

The test we are building toward is one sentence typed into a Claude Code session:

> provision a new python application named parachute. give it a dev and test ground environment.
> a staging and prod flight environment. and configure it with 1 100% weight canary step, an
> URL=http://myendpoint.io env var.

Status labels used here: **Built**, **Draft** (written, not applied), **Proposal**, **Unverified**.

## 1. Baseline (2026-09-26)

Measured by the scorecard tool against the real repos. It scores readiness against the full A+
contract, so it is a progress meter: most of the gap is artifacts that do not exist yet, not things
that are broken. It is stricter than a "does it work with a careful agent" judgment, which is why it
reads lower than an eyeball grade would.

| Dimension | Score | What the measurement found |
|---|---|---|
| 1 Discoverability | 35 | Human docs and a Backstage catalog exist; 6 of 13 XRDs are added to the catalog. No `AGENTS.md`, no contract bundle, no `llms.txt`. |
| 2 Schema precision | 45 | `values.schema.json` covers all 29 top-level keys and a wrong type fails at render. But **12 of 234 nodes have a description (5%)**, **0 of 68 objects reject unknown keys**, and **4 of 4 live values files still render with a typo injected**. XRDs: 78 of 125 fields described, one CEL rule in 13 XRDs. |
| 3 Component contracts | 4 | **22 of 25 live env entries hard-code a derived name** (`cache-master`, `<name>-connection`, `svc.cluster.local`). No component declares outputs. |
| 4 Pre-merge validation | 22 | No `airframe validate`, no required check on env, gitops or tenants repos (none found). 11 chart guards. Ground env files are committed straight to `main`. |
| 5 Write safety | 13 | **4 of 4 live values files mix human and machine-owned keys** (`releaseTracking` and the image tag beside replicas and env). No base layer, no field ownership, no risk classes. Secrets are references, never values. |
| 6 Observe and verify | 21 | Crossplane's `Ready`/`Synced` conditions and one custom condition (`CicdOnboarded`). No reason codes, no verify contracts, no describe. |
| 7 Docs for agents | 39 | Quickstarts are true (walked live) and all 14 YAML blocks parse. None is validated in CI; nothing is executable. |
| 8 Interaction surface | 27 | One GitOps write path. The only config editor is Tower's UI; no API. |
| 9 Safety integration | 20 | Tiers reach paths, not fields. `extraManifests` is an arbitrary-manifest escape hatch with no special handling. |
| 10 Hygiene | 46 | `helm lint` passes and the fleet renders. **No chart tests, no chart CI.** |
| **Overall** | **27 / 100** | **1 of 14 acceptance checks pass.** |

Re-run any time: `python3 tools/airframe-scorecard/scorecard.py --json out.json`. The committed
baseline is `tools/airframe-scorecard/baseline-2026-09-26.json`.

### Two findings from running the chart, not reading it

1. **Typos pass.** `rolout:`, `replcas: 5` and `totallyMadeUp` render with exit 0 and are ignored.
   A component with `size: gigantic` (the Redis XRD allows small, medium, large) also renders; it
   fails only after merge, on the cluster, or is pruned silently.
2. **Configuring before the first image renders a broken Rollout.** Setting `rollout.steps` and `env`
   with no image renders `image: ':'`. The quickstart works around it with `rollout: null`, but then
   you cannot configure the rollout. An agent declaring everything up front, which is the natural
   thing to do, hits this on the first environment. `clearance/tests/test_airframe_plan.py::test_CANARY_the_chart_bug_the_workaround_exists_for`
   pins the behaviour and will fail on purpose when the chart is fixed.

## 2. What A+ means

**A+ = overall ≥ 97 and all 14 acceptance checks pass.** Each check is automated by the scorecard.

| # | Acceptance check | Baseline |
|---|---|---|
| 1 | Typo acceptance is 0%: every injected unknown key, in every live values file, fails | 4/4 accepted |
| 2 | Schema description coverage ≥ 95% | 5% |
| 3 | Every non-passthrough object rejects unknown keys | 0 of 68 |
| 4 | A versioned contract bundle is published | no |
| 5 | `AGENTS.md` at the root and on every component | no |
| 6 | All component XRDs declare outputs and verify checks | 0 of 6 |
| 7 | No derived-name literals in live env entries | 22 of 25 |
| 8 | `airframe validate` exists and is a required check | no |
| 9 | No live file mixes human and machine-owned keys | 4 of 4 mixed |
| 10 | A shared base layer exists in the ApplicationSets | no |
| 11 | `airframe.*` tools exist | no |
| 12 | An AppSpec schema exists | **Draft** (`clearance/schemas/appspec.schema.json`) |
| 13 | Executable walkthroughs replace prose quickstarts | 0 |
| 14 | Every live values file renders cleanly | **yes** |

Beyond the scorecard, the end-to-end acceptance test is the parachute sentence, run as a Checkride
case with a seeded bad run, and a resume test (kill the session mid-plan, resume by `task_id`).

## 3. The design: the values contract is the API

A NodeJS or Python application's *ongoing* configuration is its values files, not its XR. So
"making Airframe AI-friendly" means making that contract a first-class, machine-readable, validated,
ownership-aware API, and giving agents a small verb set over it: **describe, explain, plan, validate,
apply (as a PR), status, verify.**

Glidepath's `cicd.schema.json` is the model: `additionalProperties: false`, long descriptions,
explicit `oneOf` shapes. The Airframe schema should read like it.

### One source, generated artifacts

```
XRD OpenAPI + chart values schema + sidecar meta + dead-end rules
                            │
                    contract generator (CI)
                            │
                  airframe-contract.json   ← versioned with each Airframe tag
        ┌───────────┬──────────┼──────────┬──────────────┐
   airframe     Tower forms   airframe.*   docs, AGENTS.md,
   validate     + validator   tools (MCP)  reference (generated)
```

Diagram: `diagrams/plan/05-contract-architecture.html`.

**Sidecar meta.** A Kubernetes CRD's structural schema rejects unknown `x-` keys, so the extra
vocabulary cannot live in an XRD. It lives in `contract/<kind>.meta.yaml` next to it, keyed by JSON
pointer, and the generator merges it. In the chart's `values.schema.json` (not a CRD) the same keys
can be inline annotations; **Unverified:** that Helm's validator ignores unknown keywords. Check with
`helm lint` before relying on it.

| Key | Meaning | Used by |
|---|---|---|
| `x-hangar-owner` | `human`, `release` (Glidepath), `platform` (compositions) | ownership gate, Tower |
| `x-hangar-risk` | `low`, `medium`, `high`, `critical` | Clearance tier mapping |
| `x-hangar-effects` | what changing it does: restart, new namespace, external resource | `plan` output |
| `x-hangar-outputs` | on a component: Secrets, ConfigMaps, keys, DNS, ports it produces | wiring, lint |
| `x-hangar-verify` | machine-checkable expectations | `verify` |
| `x-hangar-passthrough` | deliberately open (`podSpec`, `extraManifests`) | strictness gate |

A sample is in `drafts/airframe/contract/redis.meta.yaml`.

## 4. The ten workstreams

Effort is for one person. **Born-A+ rule:** every component built from now on (MongoDB, OAuth, nginx,
the chart's agent block) ships with outputs, verify checks, sidecar meta, `AGENTS.md` and a description
on every field. Nothing new adds to the retrofit.

### AF-1 Discoverability (35 → A+)
- `airframe/AGENTS.md` (root) and `compositions/<x>/AGENTS.md`: where the contract lives, how to validate, what not to touch. Draft: `drafts/airframe/AGENTS.md`.
- `airframe/llms.txt`: an index of the contract and docs.
- `hangar.io/agent-summary` annotation on every XRD; `add-to-catalog` reviewed for all 13.
- `contract/airframe-contract.json` and the `airframe.capabilities` tool.
- **Accept:** a cold-start Checkride case answers 10 capability questions from the contract alone.
- **Effort:** 2 days after AF-2's generator exists.

### AF-2 Schema precision (45 → A+)
- Schema-first: move the 548 lines of prose from `values.yaml` comments into `values.schema.json` descriptions, then **generate** `values.yaml` (defaults and doc comments) from the schema so they cannot drift.
- `additionalProperties: false` on every object except marked passthroughs (`podSpec`, `extraManifests`, `canaryAnalysis`, `blueGreen`).
- Enums, patterns (DNS names, quantities), examples, defaults. Coverage gates in CI: descriptions ≥ 95%, strictness 100%.
- XRDs: CEL rules for cross-field constraints (`x-kubernetes-validations`), and required descriptions.
- Discriminated union for `components[]` on `type`, each arm generated from that component's XRD spec, so `size: gigantic` fails before merge. (Tower's hand-rolled validator has no `oneOf`; validate server-side or adopt a real validator.)
- **Accept:** a mutation test over every live values file (add a key, misspell a key, break an enum) is rejected 100%.
- **Rollout:** warn-only first, enforce after the fleet baseline sweep passes.
- **Effort:** 1 week. **Risk:** strictness can break an existing environment, hence the sweep.

### AF-3 Component contracts (4 → A+)
- Each component declares outputs in its sidecar meta: Secret and ConfigMap names, keys, service DNS, ports.
- Chart feature `fromComponent`: `env: [{name: REDIS_URL, fromComponent: {name: cache, output: url}}]`, resolved to a literal or a `valueFrom` reference. Agents stop guessing `cache-master`.
- Components publish `status.outputs` so it is discoverable at runtime.
- Lint AF-COMP-002: every reference resolves to a declared component output.
- **Accept:** zero derived-name literals across the fleet; every reference resolves.
- **Effort:** 1 week for Redis, Postgres, RabbitMQ, SecretStore; MongoDB and OAuth are born with it.

### AF-4 Pre-merge validation (22 → A+)
`airframe validate` is one tool with six layers. It runs as a required check on app repos
(`platform/envs`), gitops repos, and the tenants repo (`xr-requests`), and as an agent tool.

| Layer | Checks |
|---|---|
| L1 schema | values against the strict chart schema; XRs against the XRD schema |
| L2 render | `helm template` against the pinned chart version |
| L3 conformance | kubeconform against the CRDs |
| L4 policy | ownership, risk, secret-looking literals, `extraManifests` |
| L5 conventions | dead-end rules, below |
| L6 references | every `valueFrom` and `fromComponent` resolves |

Output is JSON and SARIF with a rule id, a JSON path and a fix hint, so an agent can retry against it.

Seed rules, each with a seeded failing fixture (the dead-ends list becomes lint):

| Id | Catches |
|---|---|
| AF-CLUSTER-001 | `devCluster` other than the registry's dev value (`kind-dev` even on kiac-dev) |
| AF-ENV-001 | an environment named like a pipeline stage (`test`) |
| AF-ENV-002 | `env` used where `envName` is meant |
| AF-ROLLOUT-001 | rollout config with no image (until the chart guard lands) |
| AF-PROBE-001 | Spring Boot probe not on `/actuator/health/liveness` |
| AF-ARCH-001 | `build.platforms` pinned to one architecture |
| AF-RABBIT-001 | RabbitMQ 4.1 with the pinned operator |
| AF-COMP-001 / 002 | unknown component type; unresolved output reference |
| AF-OWN-001 | a machine-owned key changed by a non-owner |
| AF-RISK-001 | `extraManifests` or another critical field without human approval |
| AF-SECRET-001 | a secret-looking literal in `env` or `configMaps` |

- **Accept:** every dead end has a rule and a failing fixture; every live file passes; under 10 seconds.
- **Effort:** 1 week for L1 to L3 as a container and a Tekton task; the rules accrue.

### AF-5 Write safety (13 → A+)
- **One file, one owner.** Ground: `platform/envs/<env>.yaml` (human) and `<env>.release.yaml` (the deploy stage). Flight: `values.yaml` (human) and `values.release.yaml` (Glidepath's release PR). ApplicationSets layer `base → env → release`, later wins.
- **A shared base layer:** `platform/base.yaml` and `gitops-<app>/base/values.yaml`, so "set this everywhere" is one edit.
- Field ownership and risk in the sidecar meta; an ownership gate (AF-OWN-001).
- `agent-scope` becomes field-aware (JSON-pointer allow and deny), not path-only. `extraManifests`, `rollout.image`, `releaseTracking`, `networkPolicy` and `httpRoute` are denied to agents by default.
- Canonical formatting and a comment-preserving patch engine, so agents do not drop the comments that carry meaning.
- **Accept:** no live file mixes owners; a property test shows a release PR and a config PR never conflict.
- **Coordination:** three repos change together (airframe, glidepath's `open-release-pr` and deploy stage, Tower's Config tab). **Unverified:** that ArgoCD's git files generator can exclude `*.release.yaml` so it does not create a second Application; the generator supports `exclude`, but test it on a scratch app first.
- **Effort:** 2 weeks with migration.

### AF-6 Observe and verify (21 → A+)
- A shared status helper: conditions `Ready`, `Synced` plus a closed list of reason codes, each with a hint string, and `observedGeneration`, on every XRD.
- Verify contracts per component and per app (`x-hangar-verify`): XR ready, Secret exists, port open, Rollout healthy, SLO not burning.
- `airframe.describe`: effective config (defaults merged), XR conditions, Argo health, last release, recent failures. Tower's backend already assembles most of this.
- **Accept:** every XRD status uses the closed reason list; `verify` passes and fails correctly on seeded fixtures.
- **Effort:** 1.5 weeks.

### AF-7 Docs for agents (39 → A+)
- Convert the quickstarts to executable walkthroughs (`docs/walkthroughs/*.yaml`): each step has a command, an expected result and a verify. Render them to markdown; the walkthrough runner replays them on the dev cluster.
- CI extracts every YAML block from the docs and validates it against the contract.
- Reference docs generated from the contract.
- **Accept:** part 1 replays green; doc YAML is validated in CI.
- **Effort:** 1 week; rides along with each Skyport part.

### AF-8 Interaction surface (27 → A+)
- **AppSpec** (`clearance/schemas/appspec.schema.json`, Draft): desired state for an app and its environments in one place.
- **Planner** (`clearance/src/clearance/airframe_plan.py`, **Built and tested**): AppSpec to an ordered ChangeSet across the tenants, app and gitops repos, with gates, dependencies, assumptions and warnings.
- Tools in Clearance: `airframe.capabilities`, `describe`, `explain`, `plan`, `apply` (opens PRs), `status`, `verify`, `diagnose` (via Holmes).
- Idempotent (same spec, same change set, a no-op when converged) and resumable (state on the `task_id`, PR labels and the audit log).
- **Accept:** the parachute sentence passes as a Checkride case, plus a resume test.
- **Effort:** 3 weeks, mostly adapters (GitHub, ArgoCD, Kubernetes).

### AF-9 Safety integration (20 → A+)
- Risk classes map to Clearance tiers: ground writes T1, flight PRs T2, creating flight environments T2.
- Escape hatches denied by default; field-level policy tested with negative cases.
- **Accept:** every high or critical field has a negative test.
- **Effort:** 3 days after AF-5.

### AF-10 Hygiene and determinism (46 → A+)
- Chart tests (helm-unittest or a script), chart CI, and a compatibility matrix (chart version by values fixtures). The fleet baseline runs on every schema change.
- Chart fixes: no Rollout without an image (**the parachute bug**), more guards with actionable messages, `devCluster` validated against the registry, an `agent:` block (below).
- **Accept:** chart CI green; scorecard runs in CI and fails on regression.
- **Effort:** 1 week, and the first thing to do.

## 5. Chart changes, in one list

1. **Guard:** render no Rollout, RolloutWatch or workload until `rollout.image` is set. Fixes the `image: ':'` bug and lets an agent configure before the first deploy. Then flip `Features.rollout_guard`.
2. **Base layer** and **release file** support in the templates and ApplicationSets.
3. **`fromComponent`** wiring in `env` and `secrets` entries.
4. **`agent:` block** for service agents (below).
5. **More guards** with actionable messages (11 today; the target is every invariant the docs state in prose).
6. **`devCluster`** validated against the cluster registry.

### The `agent:` block (service agents use the application path)
A service agent is an ordinary application, so the chart gives its pods what an AgentRun gets:

```yaml
agent:
  enabled: true
  definition: passenger-assistant          # name of the AgentDefinition in git
  network: clearance+model                 # narrow-only against the definition
  sandbox: hardened                        # rejected on a cluster with no runtime class
```

It renders audience-bound projected tokens (`clearance`, `model-proxy`), a default-deny egress policy
with the two exceptions, the runtime-contract environment, and the `hangar.io/agent` labels. Same
guarantees, one implementation of the contract in two places (`function-agentrun` and the chart), kept
in step by a shared conformance test.

## 6. AppSpec and the planner

The parachute sentence, as the agent writes it (`clearance/examples/parachute.appspec.yaml`):

```yaml
apiVersion: airframe/v1
kind: AppSpec
app: parachute
stack: python
environments:
  ground: [dev, test]
  flight: [{name: staging}, {name: prod}]
config:
  rollout: {strategy: canary, steps: [{setWeight: 100}]}
  env: [{name: URL, value: "http://myendpoint.io"}]
```

`plan` compiles it, today's Airframe, into:

| Step | Repo | Gate | Risk |
|---|---|---|---|
| `tenants` | gitops-cluster-dev-tenants | human merge | T2 |
| `repos-ready` (wait) | | | |
| `app-repo`: `cicd.yaml` patch, `platform/envs/dev.yaml`, `test.yaml` | parachute | auto-merge | T1 |
| `tekton-resync` | parachute | auto-merge | T1 |
| `gitops`: staging and prod values patches | gitops-parachute | human merge | T2 |
| `ground-rollout` (only because of the chart bug) | parachute | auto-merge | T1 |
| `verify` | | | T0 |

With the A+ features on, `ground-rollout` disappears and the config is written once into a base layer.

Assumptions and warnings the planner surfaces instead of hiding: the only upper cluster is `kind-prod`
so both flight environments go there; two upper clusters and no choice is a **question**, not a guess;
`test` collides with the `test` pipeline stage; a single 100% step promotes immediately.

## 7. Migration and safety

- **Never edit shared things in place.** Test-via-copy: chart and schema changes go through a scratch app first; a new composition through one XR's `compositionRef`.
- **Worktrees.** Airframe, glidepath and apron have all been on the user's branches before. Check the branch, work in a worktree, and leave tags to the user.
- **Strictness in stages:** warn, sweep the fleet (dev and kind-prod), enforce.
- **Multi-arch:** everything new builds for arm64 and amd64.
- **Unverified, check first:** how ArgoCD applies XRs (are unknown fields rejected or pruned?), the git-generator `exclude`, Helm and unknown `x-` keywords, and whether chart and schema changes need a chart version bump per your release process.

## 8. Run it

```bash
python3 tools/airframe-scorecard/scorecard.py                  # the grade
cd ~/tech/clearance && ./.venv/bin/python -m pytest -q          # 255 tests incl. the parachute planner
```
