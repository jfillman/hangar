# Glossary

The aviation vocabulary is the brand's rule (see the Hangar Brand System): names teach the product.

## Environment tiers (existing)
| Term | Meaning |
|---|---|
| **Ground** | A disposable environment on the dev cluster, declared in `platform/envs/<env>.yaml` in the app repo. Image committed by the deploy stage straight to `main`. |
| **Flight** | A governed environment on an upper cluster, created by an `ApplicationEnvironment` XR, changed by reviewed PRs. |
| **Ground control** | Tower's CI/CD tab. |

## Products
| Term | Meaning |
|---|---|
| **Hangar** | The platform, and the docs umbrella. |
| **Apron** | The per-cluster bootstrap template. |
| **Airframe** | The service catalog: XRDs, compositions, the `airframe-application` chart, and (with the A+ program) the machine-readable contract. |
| **Glidepath** | CI/CD and release guardrails. |
| **Tower** | The Backstage command-center UI. |
| **Autopilot** | The sixth product: governed, bounded AI agent workloads. Accepted name. |
| **Clearance** | Autopilot's tool gateway and policy: every agent action is checked and audited here. Accepted name. Like Tower's *Ground Control* it is a feature of a product, so it has no mark. |
| **Flight recorder** | Autopilot's audit and correlation: one `task_id` on every record, plus a tamper-evident chain. Accepted name. Records both tiers, although "Flight" also names the upper tier. |
| **Checkride** | Autopilot's evaluation harness. **Name open** (decision D7); Airworthiness is the recommended alternative. |
| **Skyport** | The demo system (an airport). |

## Autopilot concepts
| Term | Meaning |
|---|---|
| **Agent workload** | Any AI agent, in any framework, that Hangar runs. |
| **AgentDefinition** | The durable, reviewed description of an agent: identity, ceiling, tools, APIs, models, network, compute, limits, image, triggers. YAML in git. |
| **AgentRun** | One bounded, disposable instance of a definition, created as a claim (an XR) and gone at its deadline. |
| **Workload shape** | Task, session, service, scheduled, event, team. |
| **Two planes** | The *durable* plane (git, reviewed, ArgoCD pulls) and the *ephemeral* plane (claims to Crossplane, bounded). |
| **Ephemerality test** | The five conditions a thing must meet to be a claim instead of a commit. |
| **Claim** | A request that can only **narrow** what its definition grants. |
| **Narrow-only** | The invariant that a claim, a child run or a runtime signal may lower authority, never raise it. Raising is a git commit. |
| **Tier T0 to T3** | T0 read; T1 reversible write (a PR, a lower-env sync, a child run, an artifact); T2 propose only (a PR to an upper environment); T3 never exposed. |
| **Tripwire** | A T3 tool name registered only so an attempt is denied, audited and trips the session breaker. |
| **Breaker** | Reduce-only runtime state that freezes a session. |
| **Session channel** | Per-session message queue in Clearance, so a human can talk to a run that has no inbound network. |
| **Trigger bridge** | An ordinary Airframe app that turns a broker message into a run start, idempotently. |

## Airframe A+ concepts
| Term | Meaning |
|---|---|
| **Scorecard** | `tools/airframe-scorecard`: the measured readiness of Airframe for AI agents, ten dimensions and 14 acceptance checks. |
| **A+** | Overall at least 97 and all 14 acceptance checks pass. |
| **Contract bundle** | `airframe-contract.json`: one generated, versioned artifact describing everything Airframe manages. |
| **Sidecar meta** | `contract/<kind>.meta.yaml`: owners, risks, effects, outputs and verify checks that cannot live in a CRD schema. |
| **`x-hangar-*`** | The annotation vocabulary (owner, risk, effects, outputs, verify, passthrough). |
| **AppSpec** | Desired state for an app and its environments in one document. |
| **ChangeSet** | The planner's ordered set of repo changes, each with a gate, dependencies and effects. |
| **`airframe validate`** | One validator, six layers, run in CI and as an agent tool. |
| **Born A+** | A new component must ship with outputs, verify checks, meta, `AGENTS.md` and full descriptions. |
| **One file, one owner** | Human-owned and machine-owned keys live in different files. |
