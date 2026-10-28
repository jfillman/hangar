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
| **Clearance** | Change assurance for AI-enabled engineering, and since 2026-10-28 a Hangar product of its own (D16). Two boundaries: the **runtime gateway** (every tool call an agent makes is checked and audited; Autopilot's gateway) and the **deployment gate** (may this change land in a protected environment, and can we prove it did under policy). Accepted name; as a product it needs a mark. |
| **Flight recorder** | Autopilot's audit and correlation: one `task_id` on every record, plus a tamper-evident chain. Accepted name. Records both tiers, although "Flight" also names the upper tier. |
| **Preflight** | Autopilot's evaluation harness: cases run against an agent definition before promotion. Decided name (D7). |
| **Skyport** | The demo system (an airport). |

## Clearance concepts (2026-10-28)
| Term | Meaning |
|---|---|
| **Runtime gateway** | Clearance's first boundary: tool tiers T0 to T3, scope, narrow-only limits, CEL policy, audit. Built. |
| **Deployment gate** | Clearance's second boundary: a change to a protected environment needs a clearance bound to it. Proposal. |
| **Deployment tier 0 to 3** | Routine, Standard, Sensitive, Critical. Decides who may clear a change. Shares names with runtime T0 to T3, not rules. |
| **Clearance (token)** | A signed, short-lived authorization bound to one rendered change: the git commit, the manifest-tree digest and per-object hashes, plus target, policy version, tier and approvers. |
| **ClearanceGrant** | The in-cluster resource the controller materializes from a verified token; a ValidatingAdmissionPolicy checks writes against it. |
| **Evidence record** | One versioned record per clearance event or tool call, every field tagged *verified* or *claimed*. |
| **Coverage state** | authorized-and-verified, observed-not-attributed, out-of-band-detected, or coverage-unavailable. |
| **Assurance state** | checkpointed, recorded-not-checkpointed, or not-recorded: whether a record's hash has reached a witnessed checkpoint. |
| **Clearance Ledger** | A Tessera transparency log holding record hashes only, with C2SP checkpoints countersigned by witnesses. |
| **Witness** | A server run by a party the log operator does not control; it countersigns a checkpoint only if the tree extends the last one it saw. |
| **Provenance confidence** | confirmed agent, probable agent, confirmed human, unknown. Unknown never resolves to human. |
| **Gate provider** | A path a change can take (Argo CD native; Infisical, Spacelift federated; cloud audit logs observed), each filling one contract. |
| **Packet** | The evidence export for a date range: JSON first, CSV and PDF as presentation, with a coverage statement. |
| **AuthZEN PDP** | Policy decision point speaking OpenID AuthZEN; the proposed future shape of the runtime gateway behind Traefik's Sovereign Trust Plane. |

## Autopilot concepts
| Term | Meaning |
|---|---|
| **Agent workload** | Any AI agent, in any framework, that Hangar runs. |
| **AgentDefinition** | The durable, reviewed description of an agent: identity, ceiling, tools, APIs, models, network, compute, limits, image, triggers. YAML in git. |
| **AgentRun** | One bounded, disposable instance of a definition, created as a namespaced Crossplane XR and gone at its deadline. |
| **Workload shape** | Task, session, service, scheduled, event, team. |
| **Two planes** | The *durable* plane (git, reviewed, ArgoCD pulls) and the *ephemeral* plane (namespaced XRs created directly through the API, bounded). |
| **Ephemerality test** | The five conditions a thing must meet to be created directly instead of as a commit. |
| **Requested limits** | What a session or run asks for when it opens. They can only **narrow** what its definition grants. In code, a `LimitRequest`, passed as `limits` to `session_open` and `run.spawn`. |
| **Narrow-only** | The invariant that requested limits, a child run or a runtime signal may lower authority, never raise it. Raising is a git commit. |
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
