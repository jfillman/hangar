---
title: Clearance & Autopilot Build Specification
program: Hangar · Clearance / Autopilot
board: https://claude.ai/artifact/7bptZqWD7RdUDxyR4TQ8o9
source: https://claude.ai/artifact/BCosjaYXnJzghRF6VZsL5D
updated: 2026-11-16
---

Nov 2, 2026 · @James

**Revised 2026-11-07, after W3.** This revision folds in the day's analysis and the updated Clearance documents: the Architecture's new chapter 09 (Observation) and its renumbered chapters 10 to 18, the coverage states `break-glass` and `attempted-refused`, the observation-health record, the verification statement and its insurer profile, approver independence extended to automation, and the four revenue-line companions ([Clearinghouse](https://claude.ai/artifact/3rPgELsmjQJ5rqsz386D9Q), [Intelligence](https://claude.ai/artifact/M2rDPgy5WJx8aG7dxsr3xf), [Verification](https://claude.ai/artifact/UfE1xys4nK9C7D2gNm25Lp), [Underwriting](https://claude.ai/artifact/PaZMadKYhzJSJgTBHxiw6B)). It adds three series as sections 15 to 17, after the open questions so that every existing section number still holds (O observation, P clearinghouse, I intelligence), two follow-up packages inside the existing series (R-9, C-14), two waves after W4 in section 11 (W5 Observation, W6 Clearinghouse), new rows in the component, gap, deferred-portal and open-question tables, and two guardrails in section 12. Nothing already merged changes; W4's entry is unchanged except that O-1 and C-14 join it so the packet is not frozen without the new states.

## How to use this spec {#how-to-use-this-spec}

This spec is written for a managing Claude Code session that builds Clearance and Autopilot by delegating work packages to subagents. Every package in sections 6 to 10 is self-contained: it names its repos, its dependencies, what to build, how to prove it on hangar-dev, and what only the user can do.

### Roles

| Role | Reads | Owns |
| --- | --- | --- |
| Managing agent | Sections 1 to 5, 11, 12, 14 and 15 to 17 in full; each package card before delegating it | Sequencing (section 11), release tags and pin bumps, the apron render and gitops PRs, live verification, memory and roadmap status, every hand-off to the user |
| Subagent | Its package card, section 12, and the repo's README, AGENTS.md and docs the card names | One PR in one repo (unless the card says otherwise), with tests and docs, reported back as a PR link plus what was verified and what was left out |
| User (platform owner) | The spec, PR links | Merges where the auto-mode classifier refuses the agent (Clearance and Backstage PRs), gitsign commits, Infisical secrets, GitHub App settings, public repos, prod cluster mutations, any decision a card marks "user" |

### Package card format

Every package has the same fields, so a subagent brief is the card copied verbatim plus section 12.

**Model per subagent (owner decision 2026-11-07).** The managing agent sets the Agent tool's `model` on every subagent it starts, chosen by the kind of work. It never leaves the model to inherit the managing session's.

| Work | Model | Agent `model` |
| --- | --- | --- |
| Coding: building a package, fixing PR Lens findings, merging main into a branch, regenerating contracts and clients, writing tests and docs with the code | Sonnet 5.5 | `sonnet` |
| Research: read-only exploration of repos, docs and logs, web and library lookups, evidence and cluster surveys, collecting digests or check results | Haiku 5.5 (the current Haiku; the owner said "haiku 5") | `haiku` |
| A card that is mostly design (a design pass with spikes, like G-ARGO-1) | Sonnet 5.5, with its research sub-steps given to Haiku | `sonnet` |

In practice:

- A resumed agent keeps the model it started with.
- Opus is used only if the owner asks for it on a package.
- The model goes on the card's brief line, `Model: sonnet` or `Model: haiku`, so the choice is visible before launch.
- If a Haiku research agent finds the task needs code changes, it stops and reports. It does not edit.

* **Id and title.** R-n refactor, A-n Autopilot gateway, C-n Clearance core, G-ARGO-n Argo CD gate, G-TF-n Terraform gate, O-n observation (collectors, pipeline, health), P-n the clearinghouse (receipts, sampling, statements, portal), I-n intelligence (the opt-in dataset).
* **Repos.** Where the PRs land. A move between repos is two PRs, add in the target first, remove in the source second.
* **Depends on.** Packages that must be merged, and where stated live on hangar-dev, before this one starts.
* **Build.** The concrete deliverable: modules, endpoints, resources, charts, docs.
* **Done when.** The acceptance tests, always including one negative test and one live check with quoted evidence.
* **Rollout.** Which steps of the release chain below the package needs.
* **User steps.** What the agent cannot do and must hand over.

### Rules every subagent follows

1. Work in a fresh worktree from origin/main; use `git -C <path>` and `gh --repo <owner/repo>` on every call; never `git stash` on a shared checkout, never force-push, never skip signing.
2. Clearance code lives only in jfillman/clearance; autopilot takes it by a version bump. Never edit Clearance code inside autopilot. After R-3 the AI gateway's code is autopilot's, and the gateway reaches Clearance only through its API.
3. A CI/CD capability is a glidepath-api endpoint first, then a Clearance tool, then Tower. Never add MCP concepts to glidepath-api; never give Tower or Clearance Tekton write access.
4. Docs change in the same PR as the code: clearance/docs, autopilot/docs, hangar/docs/autopilot, glidepath/docs.
5. Run the repo's full test suite and read `gh pr checks` before reporting a PR ready. A Clearance PR goes to the user only with green CI; a release is tagged only off a green main.
6. The final report names what was descoped and why, next to what was done.

### The release chain

Most packages end with the same chain, run by the managing agent one step per command, never chained with `;`:

1. The clearance PR merges (user); tag `vX.Y.Z` off main once CI is green.
2. The autopilot PR pins `clearance @ vX.Y.Z` with `uv lock`, merges after CI; tag `gateway-vA.B.C` (and `runtime-v*` when the runtime changed); wait for the image workflow and record the index digest.
3. The apron PR bumps the image digest and env; render gitops-hangar-dev over a clean `git archive origin/main` export and diff; the gitops PR touches exactly the expected files.
4. Watch the Argo sync on hangar-dev; an env-only or hook-only change may need a refresh annotation.
5. Verify live with evidence (an evidence sequence number, a kubectl or curl output) and record it in memory and the roadmap.

### The done bar

A package is done when its PRs are merged, its tag and pins are live on hangar-dev, its positive and negative tests passed against the live cluster with the evidence quoted, docs are updated, and the status in hangar/docs/autopilot/roadmap.md and the product's own docs reflects it. "No errors" is not evidence, and a passing check whose gate is off is not evidence.

Status words follow Hangar: **Built** (exists and tested), **Draft** (written, never applied), **Proposal** (designed, not written), **Unverified** (depends on something not checked).

## Hangar context and product boundaries {#hangar-context-and-product-boundaries}

Hangar is an internal developer platform of six products. Clearance and Autopilot are the two newest, and one rule separates them: Autopilot is the AI agent gateway and runtime, and Clearance is not a gateway at all. Clearance sits in the path of every change: the Autopilot gateway asks it for each decision and writes each record through it, and the deployment gate's providers do the same for changes that reach a protected environment. Clearance must install at a customer that runs no Airframe, no Glidepath and no Autopilot.

| Product | What it is | Repo | What Clearance and Autopilot take from it |
| --- | --- | --- | --- |
| Apron | Per-cluster bootstrap: renders gitops-hangar-dev and gitops-hangar-prod from templates plus cluster.yaml; Argo CD app-of-apps | jfillman/apron | Deploys Clearance and Autopilot (`55-autopilot/` today), their NetworkPolicies, ValidatingAdmissionPolicies, routes and image pins |
| Airframe | Service catalog: Crossplane XRDs, compositions, Python functions, the airframe-application chart, a generated contract bundle | jfillman/airframe | AgentRun XRD and function-agentrun, Agent XRD (pinned definitions), AgentRepository; the `airframe.*` tool backends read its contract |
| Glidepath | CI/CD: Tekton plus Pipelines-as-Code gates, release PRs, Ground to Flight promotion, and glidepath-api (Go, plain HTTP) | jfillman/glidepath | `glidepath.*` tools call glidepath-api; the `agent-gates-` and `clearance-gate-` PaC checks call Clearance; `GET /v1/events` feeds the trigger bridge; the broker mints GitHub App tokens |
| Tower | Backstage plugin UI, plus the Autopilot and Clearance Backstage plugins | jfillman/tower, jfillman/backstage | Reads clearance-api; writes through the delegate model. Portal work is deferred to section 13 |
| Autopilot | The AI agent gateway and runtime: the MCP surface agents call, sessions and the run tree, budgets and requested limits, tool dispatch to every Hangar backend, the model proxy, definitions, Preflight, AgentRun, the planner, the trigger bridge and scheduler, the runtime images | jfillman/autopilot | The gateway is the enforcement point for agents; it asks Clearance for every decision |
| Clearance | Change assurance in the path of every change: the decision service the gateway calls, the deployment gate and its providers, the evidence recorder and ledger, the GitHub provenance App | jfillman/clearance | The product |
| Hangar | Umbrella docs, roadmap, decisions, scorecard, site | jfillman/hangar | `docs/autopilot/{design,roadmap,decisions,glossary}.md` are the Autopilot source of truth; the Clearance artifacts are the Clearance source of truth |

### The boundary rule

| Belongs to clearance: in the path | Belongs to autopilot: the AI gateway and runtime |
| --- | --- |
| The decision service: the CEL deny rules, the shared tier vocabulary, path, repo and field scope checks, the narrow-only rule, answered as an AuthZEN-shaped evaluation the gateway calls for every tool call, model call, session open and spawn; the clearance token; the evidence record schema, the recorder and its Postgres store; the ledger, `clearance verify` and the packet; the deployment gate with its classifier, `clearance.yaml`, grants and approvals; the gate providers (Argo CD, Terraform, the GitHub App's protection rule, `clearance register`); provenance verification from receipts; tiering of agent-definition changes as a gate subject; clearance-api over evidence, clearances, policy, receipts and verdicts; approver identity | The MCP surface agents connect to; sessions, the run tree, budgets, the breaker and requested limits; the tool registry (which tools exist, their tier, their arguments) and dispatch to every backend; the model proxy; agent definitions, their schema and the cluster pin loader; the runtime catalog and images; the human inbox, person controls (freeze, end, hold), run results, artifacts and trigger history; the trigger bridge and scheduler; AgentRun; Preflight; the planner; the vendored Glidepath and Airframe contracts; the gateway's serve entrypoint and image |

The gateway enforces and Clearance decides and records. This follows the Clearance Architecture's decision of 2 November 2026 (ch. 01 and 13): the runtime boundary is a pluggable feeder, kept thin, and must not grow into a gateway business; the product is the deployment gate and the ledger. It amends D16 (2026-10-28), which put sessions, dispatch, the gateway and the MCP surface in the clearance repo. That is where that code sits today, and R-3 moves it to autopilot. Clearance's code keeps importing nothing from Hangar or Autopilot, and the gateway speaks to it only through its API.

### API layering

- glidepath-api is an API server, plain HTTP with OpenAPI; Clearance is the MCP server in front of it and one of its clients.
- Airframe's API is declarative: XRs committed by PR, synced by Argo CD, read back through the Kubernetes API.
- Glidepath runs without glidepath-api; Tower's CI/CD views and Clearance's `glidepath.*` tools depend on it.

### Where things run today

- **hangar-dev** (the lab cluster): namespace `autopilot-system` runs the Clearance gateway deployment, two clearance-api replicas, the CNPG `clearance-pg` cluster, people-dex, and the agentrun-reaper CronJob; `autopilot-runs` holds AgentRuns; glidepath-api runs in `platform-system`; Argo CD, Kyverno and Traefik Proxy v3.7.6 (GatewayClass `traefik`, HTTP only) are platform components.
- **hangar-prod** (laptop, podman): Backstage with Tower and the Autopilot and Clearance plugins, which read clearance-api on hangar-dev through a hostAlias; the Flight apps; Kyverno enforces Flight-only images.
- **gitops repos**: gitops-hangar-dev and gitops-hangar-prod are apron renders and must not be hand-edited without a template PR; gitops-hangar-dev-tenants holds tenant registrations and Agent XR pins.

## Current state as built {#current-state-as-built}

The code is split along D16's line, which put the agent gateway in the clearance repo. Measured against the 2 November architecture, three things are in the wrong place: the AI gateway's code (MCP surface, sessions, dispatch, model proxy) lives in clearance; the product's own deployable lives in autopilot, whose `serve.py` composes everything into `ghcr.io/jfillman/autopilot-gateway`, which also serves clearance-api; and Hangar's tool policy lives in clearance as `clearance.packs.hangar` with a vendored Glidepath scope, so a Glidepath contract change ripples through three repos. Inventory date 2026-11-02; sources are the four repo inventories in this session's scratchpad (`report-clearance.md`, `report-autopilot.md`, `report-glidepath.md`, `report-airframe-apron-hangar.md`), read from origin/main where local checkouts were behind.

### Live on hangar-dev

| Piece | Where | Pin |
| --- | --- | --- |
| Clearance gateway (MCP, model proxy, GitHub App webhook, event bridge, scheduler, Agent XR loader) | Deployment `clearance`, `autopilot-system` | `ghcr.io/jfillman/autopilot-gateway:gateway-v0.3.25@sha256:63b9c3c3…` = clearance v0.26.0 |
| clearance-api | Deployment `clearance-api`, 2 replicas, `autopilot-gateway api` | same image |
| Store | CNPG `clearance-pg`, 1 instance | postgresql 18.6 |
| People sign-in | `people-dex` | dex v2.46.0, GitHub connector, allowlist `jfillman` |
| Runs | `autopilot-runs` AgentRuns, agent-sandbox v1.0.8, `function-agentrun@sha256:cf9f288c…`, reaper CronJob | airframe catalog v0.3.172 |
| Agent pins | one `Agent` XR, `app-gate-api-cicd/gate-reader` | gate-api@eadde6b |
| Glidepath | glidepath-api 0.11.0 (`sha-c67322d`), checks `Glidepath / <gate>-`, `clearance-gate` advisory, `agent-gates` required | targetRevision main |
| GitHub Apps | `hangar-autopilot-agents` (writes PRs through the broker), `Hangar Clearance` id 5561694 (checks, protection rule, webhooks through a Cloudflare tunnel), `cicd-pac` |  |
| hangar-prod | nothing of Clearance or Autopilot; Tower reads clearance-api through a hostAlias to hangar-dev | airframe catalog v0.3.171 |

Every gateway flag is on in the lab: Glidepath with on-behalf-of, Argo lower sync, GitHub PRs, model proxy to Anthropic, events, schedules, Agent XR pins, the GitHub App, people OIDC, Tower federation, GitHub Actions OIDC for the scratch repo.

### What each repo holds today

| Repo | Holds | Release shape |
| --- | --- | --- |
| clearance (v0.26.0) | 30 modules, about 5,200 lines: dispatch, server (MCP, write routes, model proxy), api, pg, gate, github\_app, register, policy, auth, review, definitions, session, backends, limits, profile and the definition schema, inbox, audit, scope, control, modelproxy, tiers, events, runtimes, results, pack, `packs/hangar` with the vendored Glidepath scope. No Dockerfile, chart or server entrypoint; the only binary is `clearance register` | Manual: version bump, PR the user merges, hand-pushed tag; 14 tags from 10-30 to 11-01; CI is pytest with Postgres; no release workflow or changelog |
| autopilot | `src/autopilot` about 5,300 lines: `serve.py` (the deployable), `api_serve.py`, `gateway.py` handlers, backends, kube\_runs, manifests, glidepath\_api and glidepath\_live, cicd\_propose, github\_pr, argo\_sync, airframe\_api, airframe\_tools, airframe\_plan, reads, event\_bridge, scheduler, triggers, agent\_xrs, preflight, vendored airframe files; `runtime/` generic, base-python, langgraph, claude-agent-sdk; 8 bundled agents plus 9 Skyport ones that are not loaded; 8 Preflight cases | Images on tags: gateway-v0.3.25, runtime-v0.1.3, base-python v0.1.1, langgraph v0.1.0, claude-agent-sdk v0.1.0; the package version is never bumped |
| glidepath | glidepath-api 0.11.0 and its contract; the gate registry with agent-gates, clearance-gate, agent-definitions, agent-release; the broker's token endpoints; `/v1/events` SSE from an in-memory buffer | Bot image pins per merge; no tags |
| airframe | 25 XRDs on main, 26 on origin/main with AgentRepository untagged; `Agent` and `AgentRun`; function-agentrun in Python; no policy or Argo objects | Human tag v0.3.N, then apron pin |
| apron | `templates/55-autopilot/` for both products (11 clearance files, people-dex, grants, reaper, sandbox); `cluster.yaml` `autopilot:` keys configure Clearance features; the Glidepath wiring in `50-glidepath/` | No tags; renders committed by SHA |
| hangar | `docs/autopilot/{design,roadmap,decisions,glossary}.md`, the Clearance site pages, scorecard | PRs the user merges |

### What is living in the wrong place

1. **The AI gateway itself.** The MCP surface (`server.py`), sessions and the run tree (`session.py`), budgets and requested limits (`limits.py`), dispatch (`dispatch.py`), the tool registry (`tiers.py`), the model proxy (`modelproxy.py`), the human inbox, person controls, run results and artifacts live in the clearance repo. That is gateway code and belongs to Autopilot.
2. **Deciding and recording are not separable.** One in-process `Gateway` object authenticates, decides, spends, records and calls the backend. There is no decision API a second enforcement point could call; the deployment gate has its own routes beside it.
3. **The product's deployable.** The routes that are Clearance's (deployment gate, provenance, GitHub App webhook, clearance-api) are served by autopilot's image. Clearance cannot install alone, which the architecture requires.
4. **The platform's tool policy.** `clearance.packs.hangar` holds the `glidepath.*` and `airframe.*` tool specs, R021 to R023 and the vendored Glidepath scope. Every Glidepath contract change costs a clearance release, an autopilot pin, a gateway tag, an apron render and a gitops PR.
5. **Hangar vocabulary inside the core, as data.** `autopilot-runs` as the run identity namespace, `.tekton` and `release.yaml` baseline denies, `gitops-` environment tiering, Backstage group references, `profile.glidepath` and `profile.airframe` schema sections, trigger sources `rabbitmq` and `glidepath`, the runtime's input shape in `run_agent`. The boundary test checks imports only and cannot see this.
6. **Definitions machinery.** D16 said definitions and their schema stay in autopilot; `profile.py`, the schema, `definitions.py`, `runtimes.py` and `events.py` live in clearance.
7. **Deployment configuration.** One apron component carries both products, and Clearance's features are switched by `autopilot.*` keys.

### What is built but incomplete against the target

- **Evidence.** Hash chain, `clearance.evidence/v0-draft` envelope, verified and claimed fields, and an `assurance` column that only ever says recorded-not-checkpointed. No signing, checkpoint, witness, verifier or packet; the local `Checkpoint` is test-only.
- **Deployment gate.** Tiers, grants, approvals, TTL and supersession are real, and the Glidepath `clearance-gate-` check and `clearance register` feed them. There is no grant on any cluster, no admission policy, no `deploy.exception`, no outcome record, and the check is advisory. Tower's `hangar/release-signoff` still runs beside it. With the gate off and the App on, every protected deployment is rejected `DG-UNREGISTERED`.
- **Provenance.** Verdicts come from Clearance's own receipts (confirmed or not-agent); the four confidence levels, commit-signature and agent-header signals are not modelled. The App runs beside `agent-gates-` until their verdicts agree.
- **Events.** glidepath-api's stream is in memory (known gap #44); the bridge is its one unattended consumer and keeps no durable cursor.
- **Identity.** TokenReview, people-dex, Tower federation and GitHub Actions OIDC work; stable agent identity by ID-JAG waits on an issuer (D19).
- **Tools without a backend on Hangar.** `xr.request`, `app.api.get`, `chat.recv`, `chat.send`; `airframe.validate` is dropped from the image. The nine Skyport definitions depend on them.

### Hygiene found by the inventories

- Local checkouts behind origin on 2026-11-02: apron 50 commits, gitops-hangar-dev 63, hangar 5, autopilot, clearance, glidepath and airframe 2 each. Worktrees from past sessions: about 20 in clearance, 16 in autopilot, 29 in glidepath, 22 in airframe, 26 in apron; most sit on merged branches.
- autopilot's vendored `airframe-contract.json` and `appspec.schema.json` drift from airframe main; the re-vendor sits on three unmerged branches (`person-controls-pin`, `base-python-available`, `origin/pr-open-validates-cicd`).
- The airframe main checkout has 14 staged, uncommitted files re-adding deleted Tier-2 twins. The autopilot checkout has an untracked `lab/` directory containing a file named `api-key` outside `.gitignore`. Both are the user's to resolve.
- Stale status text: autopilot README pins v0.4.0 and counts 411 tests; clearance `docs/index.md` and `catalog-info.yaml` call the gate designed and the App not built; `__version__` is 0.1.0.dev0; hangar's Autopilot README status is dated 2026-10-28.
- Minor defects worth a line in the hygiene package: `flight_registries` empty by default so `image:not-flight-registry` never fires; `ChangeRequest.protected` unused; `human.request` registered twice when both a HumanBackend and an InboxStore are given; `PgAuditLog` loads the whole chain at start; `ModelDecision.headers` never forwarded.

## Target architecture {#target-architecture}

Clearance is a shared core and a record store that every enforcement point calls; the enforcement points themselves are not Clearance. The Autopilot AI gateway enforces for agents at runtime, and the deployment gate's providers enforce at the protected environment (Argo CD first, Terraform beside it). Each asks the core for a decision and writes its records through it. The product work is pulling decision, token and recorder out of today's in-process gateway into a core service, moving the gateway code itself to Autopilot, adding the deployment providers, and making the recorder a witnessed ledger. Sources: Clearance Brief, Architecture (ch. 01 to 18 as of 2026-11-07; ch. 09 is Observation and the former 09 to 17 are now 10 to 18), Roadmap, Change Attestation, the Clearinghouse, Intelligence, Verification and Underwriting companions, the Terraform provider note, and hangar/docs/autopilot/design.md section 0.1.

> Diagram: Clearance target architecture · 4 enforcement paths, 1 shared core, 1 record store. See the original document.

Each column is one path a change can take. Every path describes and holds its subject, asks the shared core for a decision, and lands the same record in the store. Only the runtime gateway runs inside Autopilot's image; the other providers are separate controllers that call the core's small API, so a provider crash never takes the core down.

### The two boundaries and the one record

| Boundary | Question | Subject of the decision | Status today |
| --- | --- | --- | --- |
| Runtime gateway | What may this agent call? Tool tiers T0 read, T1 reversible write, T2 propose only, T3 never; path and field scope; narrow-only limits; CEL deny rules; breaker; sessions and run tree; model-proxy decisions | One tool call, under one session principal | Built, live on hangar-dev |
| Deployment gate | May this change land in a protected environment, and can we prove afterwards that it did so under policy? Tiers 0 Routine, 1 Standard, 2 Sensitive, 3 Critical; grants cleared by policy or by named people | The rendered desired state: git commit, manifest-tree root digest, per-object rendered hashes; for Terraform the saved plan | Phase 1 core and the Glidepath `clearance-gate-` check Built; the hard gate at admission is Proposal |
| Observation (not a boundary: the second half of the coverage statement) | What else reached a protected environment, by whom, and could Clearance see it? Every observed write lands in exactly one coverage state (authorized-and-verified, observed-not-attributed, out-of-band-detected, break-glass, attempted-refused, coverage-unavailable), and every scope carries a health record (healthy, degraded, blind) | A normalized observation from a source the gate cannot influence: the API-server audit log, CloudTrail, Config, state-bucket versions; later the Azure Activity Log and Google Cloud Audit Logs | Reconciler form Built in W3 (G-ARGO-3 exceptions, G-TF-5 detectors); schema, pipeline, collectors and health record are Proposal (sections 15, O-1 to O-6) |

The two share one tier vocabulary, one evidence schema, one ledger and the `task_id`. Tier names are shared, tier rules are not: a T2 tool proposes a PR, and that PR is tiered again on its own merits at the deployment boundary. Three invariants no policy can relax: tier 3 is never auto-clearable; the proposing identity never satisfies a human clearance; the approver is never the initiating human.

### Components, as the product defines them

| Component | Responsibility | Runs where | Target state | Spec section |
| --- | --- | --- | --- | --- |
| Autopilot AI gateway (an enforcement point, not Clearance) | The MCP surface agents call; sessions, budgets, limits and the breaker; tool dispatch; the model proxy; asks the core for every decision and reports every outcome | Autopilot's gateway image, `autopilot-system` | Keep running; its decision, token and recorder logic moves into the core, and the gateway code moves from the clearance repo to autopilot | R, A |
| Decision service | AuthZEN-shaped evaluation over the CEL deny rules, the tier vocabulary, path, repo and field scope and the narrow-only rule; one call per tool call, model call, session open and spawn; the decision record | Shared core | Refactored out of `dispatch.py` | R-1 |
| Provenance detector (the Clearance GitHub App) | Confidence per PR and commit (confirmed agent, probable agent, confirmed human, unknown; unknown never resolves to human); check runs; deployment protection rule; `clearance register` | Clearance, webhooks from GitHub | Built phases 1, 2a, 2b; replaces Glidepath's `agent-gates-` once verdicts agree | C |
| Classifier and policy gate | Deterministic tier from rendered diff, resource kinds, paths, environment, provenance, CI; platform baseline plus tighten-only `clearance.yaml` per gitops repo; plain-language reason; rule-set version stored with every decision | Shared core | `gate.py` Built; structured-diff input from a real render, outage policy and Kyverno delegation still to build | C, G-ARGO |
| Config Management Plugin | Wrapper CMP in argocd-repo-server: runs helm or kustomize, canonicalizes and hashes the tree, looks up or requests a clearance, stamps grant reference and rendered hash on every object, injects the PreSync wait, fails generation for a denied tier 3 | Customer cluster, Argo repo-server sidecar | New | G-ARGO |
| Grant sync and admission | A grant-sync on the protected cluster pulls cleared grants from clearance-api, verifies them, and materializes `ClearanceGrant` objects; a ValidatingAdmissionPolicy admits a write by Argo's service account to a protected namespace only when a valid grant lists that object with that rendered hash; exceptions flow back as `deploy.exception` | Protected cluster | New; owner decision 2026-10-31: option A, grant pulled, Clearance holds no credential for any other cluster | G-ARGO |
| PreSync hook | Injected Job that polls Clearance until a named human clears or denies; the wait shows in Argo's UI; documented as skippable, never the gate | Application manifests | New | G-ARGO |
| Reconciler | Diffs live cluster state against cleared changes on an interval; out-of-band exceptions; break-glass as a recorded path | Protected cluster | New | G-ARGO |
| Terraform provider | `terraform-plan` subject, tier defaults (destroy, replace, IAM, network, KMS, database are tier 3; `-target` escalates), `clearance hold` and `clearance release` as a CI step, one managed-runner adapter (HCP run task), exception detection from state backend and cloud audit log | Runner adapter plus thin controller | New; first release beside Argo | G-TF |
| Recorder | Append-only evidence records, one versioned schema, every field verified or claimed, coverage and assurance states; the only writer of the chain | Shared core over Postgres (CNPG) and object storage | Postgres store Built; signing and the deployment-record fields to build | C |
| Attestation signer | After the sync outcome, assembles the in-toto Statement v1 (`https://clearance.hangarplatform.dev/change-attestation/v1`), signs it keyless with Hangar's Fulcio, appends it to the record | Clearance service | New | C |
| Ledger anchor | Tessera log of record hashes only; C2SP checkpoints countersigned by at least one witness Clearance does not operate; Rekor keeps the Sigstore-signed envelopes | Clearance service | New; replaces the local anchored checkpoint | C |
| Packet job and `clearance verify` | A date range to JSON, CSV and PDF with OSCAL control mappings and a coverage statement; an open offline verifier that recomputes hashes and names an altered line | Recorder, batch; CLI anywhere | New | C |
| clearance-api | Read-only process: evidence, receipts, provenance verdicts, clearances, policy and explain; roles person, delegate, notifier, auditor; generated contract vendored by Tower. Sessions, agents, the inbox, events and results move to the gateway's own read API | `autopilot-system` today | Built; splits along the boundary in R-3 and gains grant reads for grant-sync | R, C |
| Identity | Approver identity by IdP subject; provider identity (TokenReview, foreign workloads, GitHub Actions OIDC for `clearance register`); delegates and admins for gate approvals. The gateway authenticates agents and people itself and passes the principal in each evaluation | Shared core | Built; stable agent identity by ID-JAG terminates at the gateway (D19 open) | A, C |
| Hub adapter | Ingests Traefik Sovereign Trust Plane decision records as a federated runtime source | Shared core | Deferred until a record exists to test against | C |
| Surfaces | Tower, Autopilot and Clearance Backstage plugins; Slack approvals; Argo UI extension | hangar-prod Backstage | Partly Built; deferred to section 13 | 13 |
| Observation collectors (Architecture ch. 09) | Read sources the gate cannot influence and emit one normalized observation: the Kubernetes API-server audit log (webhook backend into a durable queue; CloudWatch, GKE Data Access logs or AKS kube-audit on managed clusters; Secrets at Metadata only); AWS (CloudTrail management events through EventBridge, the S3 trail with digest-chain validation, data events on the state bucket, Config items, state-bucket versions, delivered to a logging account); Azure and Google Cloud as adapters on the same schema | Customer cluster and cloud, as provider controllers with their own charts | New. G-ARGO-3's exception loop and G-TF-5's detectors are the reconciler backstop they extend | O-3, O-4, O-6 |
| Observation pipeline and health | Six CEL stages (normalize, scope, noise, attribute, classify, correlate) over the normalized observation; three immutable records (observation, assessment, resolution with a rollback cause); the noise allowlist as versioned policy; change transactions; the observation-health record (healthy, degraded, blind) per scope and source from live configuration; monitoring-protection operations as tier 3 observations; audit-gap records | Shared core | New | O-1, O-2, O-5 |
| Assurance providers and the verification statement (Architecture ch. 08 and 11) | Deliver a packet to a recipient the subscriber names, record its signed acceptance receipt as a ledger record, serve a statistically valid sample of cleared records with inclusion proofs, push summaries and links (never copies) to a GRC hub; the verification statement as a derived view of the packet with a public summary, a recipient detail recorded like auditor access, seven verification checks, supersession and revocation, a questionnaire-mapping block as data, and an insurer profile; the hosted verify page | Shared core, clearance-api and a small public page | New; the receipt record shape is in the architecture, nothing is built | P-1 to P-5 |
| Intelligence export (Architecture ch. 13) | A pipeline separate from the ledger: the operational change class as versioned data, an evidence-coverage score per tenant and period, an export of verified fields and counts (never approver subjects or diffs) under a separate consent, cell thresholds, an internal aggregate report | Shared core; aggregation outside the tenant | New; later. Only the operational class is needed early, as the classifier's comparison axis | I-1 (early), I-2, I-3 (later) |

### Contracts between the parts

- **Decision API.** `POST /access/v1/evaluation` (AuthZEN shape): subject (principal, agent, session), action (tool or model call, session open, spawn), resource (repo, path, fields, app, environment), context (session state the gateway holds: tier ceiling, budgets used, breaker, limits). Answer: allow or deny, the rule id and hint, and the spend the gateway must apply. The core records the decision; the gateway reports the outcome with the call's effect and receipt.
- **Provider interface.** Four methods: describe the subject (type, digest, target scope); intercept and hold until a clearance exists; report provenance signals with a confidence; report the outcome with the applied digest. The runtime gateway is a provider of the same shape: its subject is a tool call, its hold is allow or deny, its outcome is the call result. Federated and observed providers replace the hold with posture and correlate. A conformance test ships with the core, and every record names its provider and conformance version.
- **Evidence record.** Field groups Identities, Source, Target, Provenance, Decision, Outcome, Coverage state, Assurance state, Intent, Integrity; verified or claimed on every field; `boundary` runtime or deployment; `app` and `task_id` for correlation. Control assertions rest only on verified fields.
- **Clearance token.** Claims: subjects (commit, tree root, image digests as cross-references), per-object rendered hashes with `changed`, target cluster and environment, tier, policy ref and engine verdict, provenance level and `task_id`, approvals with IdP subject and issuer, `iat`, short `exp`, nonce. Format is open: JWT or DSSE envelope.
- **ClearanceGrant and admission.** A cluster-local resource carrying the object list and expiry; the policy matches on object identity plus the `clearance.hangar.io/rendered` annotation the CMP stamped at render, which survives mutating admission, rather than re-hashing the live object.
- **clearance-api contract.** `contract/clearance-api.json`, generated, vendored by the Backstage plugins with a drift test.
- **Policy bundles.** The core imports nothing from Hangar. Hangar's rules (R021 to R023) and the scope data they read are a policy bundle the deployment loads; the tool registry, tool tiers and handlers are the gateway's and travel in each evaluation.

### The Autopilot AI gateway, as the design defines it

Autopilot runs any AI agent workload, bounded and audited: durable changes are git commits, ephemeral runs are `AgentRun` XRs composed by `function-agentrun` into a namespaced sandbox that expires without Clearance's help. Its deliverables, from design.md and roadmap M3 to M5:

- **The gateway process** (`autopilot-gateway`): the MCP surface agents call; sessions, the run tree, budgets, the breaker and requested limits; the tool registry and dispatch to every Hangar backend (glidepath-api, Airframe reads, GitHub PRs through the broker and the agents' App, Argo lower sync, Kubernetes, Prometheus, Loki, Backstage catalog and directory, AgentRun launch and expiry); the model proxy with streaming and prompt-cache accounting; the event bridge on glidepath-api `/v1/events`; the interval scheduler; Agent XR pin loading; the human inbox, person controls, run results and artifacts. For every tool call, model call, session open and spawn it asks Clearance's decision service and reports the outcome. It no longer holds the evidence chain or serves clearance-api.
- **Runtime images**: generic, base-python, claude-agent-sdk, langgraph; a run calls `run_finish` and its result is kept 30 days.
- **Definitions in git**: `agents/<name>.yaml` in the app's repo, pinned by an `Agent` XR in the tenants repo, validated by the gateway, tiered as a change by Clearance (`POST /v1/definitions/review`), released by the `agent-release` pipeline; `AgentRepository` for team-owned agents.
- **Still owed by M3**: AP-A4 stable agent identity by ID-JAG (blocked on an issuer, D19); AF-8b `airframe.apply` and the parachute sentence live; AP-C1 Flight recorder fields (model version and Preflight result on every run record, in the evidence schema); AP-C2 cost accounting per run, agent and task tree; AF-2b the fixed T0 read set. M3 exits when the parachute sentence works end to end, killing Clearance mid-run still ends every run on time, and a seeded bad run scores as failed.
- **M4 and M5**: the six Skyport agents (one per workload shape), Preflight as a regression gate, the autonomy tracker, resumable state (AP-D1), the Modelplane hub trial behind an OpenAI-compatible contract.

## Gap analysis {#gap-analysis}

Every row maps one element of the target to what exists and to the package that closes the gap. The first eight rows are the refactor; the rest are new components. Nothing below changes the gateway's behaviour for agents; the refactor changes where processes run and where records go.

| Target element | Today | Gap | Packages |
| --- | --- | --- | --- |
| A decision service every enforcement point calls | Deciding is inside one in-process `Gateway` object that also authenticates, spends, records and calls backends | An AuthZEN-shaped decision API, a record API, a provider protocol and conformance harness | R-1 |
| Clearance installs alone | No Dockerfile, chart or entrypoint in the clearance repo | Image, Helm chart, release workflow, an install test on a bare kind cluster | R-2 |
| The AI gateway is Autopilot's | The MCP surface, sessions, run tree, limits, dispatch, tool registry, model proxy, inbox, person controls, results and artifacts are modules in the clearance repo | Move them to autopilot; the gateway calls Clearance for every decision and no longer holds the evidence chain | R-3 |
| Clearance's surfaces served by Clearance's image | The deployment gate, provenance, the GitHub App webhook and clearance-api are served by autopilot's image | Serve them from the Clearance image on hangar-dev with an unbroken evidence chain | R-4 |
| Policy is Clearance's, tools are the gateway's, without the three-repo ripple | The Hangar pack vendors Glidepath's scope; definitions carry Hangar sections in the core schema | Hangar rules as a policy bundle the deployment loads, with scope read from glidepath-api's contract; definitions and their schema move with the gateway | R-5 |
| One evidence schema every enforcement point writes | `v0-draft` envelope; no provider identity, no outcome group, assurance never changes | Freeze `clearance.evidence/v1` with the six packet questions mapped, provider identity, subject kinds, AP-C1 fields; migrate writers | R-6 |
| Clearance as its own Apron component | `55-autopilot/` carries both products; `autopilot.*` keys switch Clearance features | `components.clearance`, a `clearance:` block in cluster.yaml, chart-sourced Application, routes and policies split | R-7 |
| Accurate docs, versions and clean checkouts | Stale status text, unbumped versions, drifted vendored schemas, stale worktrees and branches | A hygiene pass with a changelog and a release workflow | R-8 |
| Clearance token: a signed object bound to the subject | A grant row in Postgres; nothing signed | Issue and verify tokens; format decision (DSSE recommended) | C-1 |
| Attestation signer after the sync outcome | None; Hangar's root CA for Fulcio (D1) not started | Keyless signing identity for the recorder, in-toto Statement v1, Rekor logging | C-2, C-2a |
| Ledger of hashes with witnessed checkpoints | Hash chain and a test-only checkpoint | Tessera log, C2SP checkpoints, one witness Clearance does not run, assurance states | C-3 |
| `clearance verify` | None | Open, offline verifier that names the altered line | C-4 |
| Packet with control mappings and a coverage statement | None | Packet v1, SOC 2 CC8.1 and 2027 draft mappings as versioned data, OSCAL export | C-5 |
| Outage policy, coverage states, break-glass, exceptions | Coverage is always authorized-and-verified; no outage block; no exception records | The clearance state machine, degraded-mode records, break-glass as a recorded path | C-6 |
| Provenance confidence from signals | Receipt-based verdicts only | Confirmed agent, probable agent, confirmed human, unknown, from App identity, commit signatures, agent headers and CI attestations; `agent-gates-` retired after parity | C-7 |
| Policy engine delegation recorded | Classifier only; Glidepath's policy-validation gate runs Kyverno offline but Clearance never records its verdict | `policy.engine` and `verdict` on every deployment decision | C-8 |
| Traefik Hub adapter | Nothing | Ingest Sovereign Trust Plane decision records as a federated runtime source; deferred | C-9 |
| clearance-api complete for the gates | Bespoke route table, no stream, no grant feed; also serves runtime reads that belong to the gateway | OpenAPI contract, `/v1/stream`, signed grant feed per cluster, installation filters; runtime reads move to the gateway | C-10, R-3 |
| Argo CD gate: bind at render, enforce at admission, show the wait, record the outcome | A Tekton render in `clearance-gate`, grants in Postgres, nothing on any cluster, `treeDigest` not persisted with the release record, events not durable | CMP, ClearanceGrant and ValidatingAdmissionPolicy, the Argo CD agent (grant sync, outcomes, exceptions), the PreSync wait, Glidepath parity and the lab rollout | G-ARGO-1 to 9 |
| Terraform gate | Nothing in any repo | Section 10 | G-TF-1 to 7 |
| Autopilot gateway complete | Gateway code in the wrong repo, ID-JAG, `airframe.apply`, recorder fields, cost accounting, durable triggers, Preflight in CI, runtime polish | R-3, then section 7 | A-1 to A-8 |
| Glidepath side | `clearance-gate` advisory beside `hangar/release-signoff`; `/v1/events` in memory; check-name prefix now configurable | Required check, sign-off retired, release record carries `clearanceId` and `treeDigest`, bridge cursor | G-ARGO-8, A-5 |
| Portal | A1 to A3, C1 to C3, T0 to T2 built read-only; gate panels, Argo UI extension, packet download, freeze and incident reports, auditor portal not built | Section 13 | deferred |
| Observation: the coverage statement's three parts, with a health record behind it | Detection is reconciler-only: G-ARGO-3 diffs protected namespaces against grants on an interval; G-TF-5 watches state versions and CloudTrail LookupEvents. No audit-log collector, no normalized observation, no health record; a clean exceptions list cannot say whether Clearance was looking; coverage states lack break-glass and attempted-refused | The observation schema and the two new coverage states (O-1); the six-stage CEL pipeline and the health record (O-2); the Kubernetes audit-log collector (O-3); the AWS collector that absorbs G-TF-5 (O-4); the packet's health summary and per-class exception rows (O-5); Azure and Google Cloud adapters on a trigger (O-6) | O-1 to O-6 |
| The clearinghouse: receipts, sampling, statements, portal | Nothing. The architecture specifies the receipt record and the four-method provider interface for assurance providers; the companions specify the verification statement, its seven checks and its insurer profile | Receipts and recipient access as records (P-1); the sampling call with inclusion proofs (P-2); the verification statement and the hosted verify page (P-3); GRC push, Vanta first (P-4); the auditor portal and the working-paper push (P-5, later) | P-1 to P-5 |
| Approver independence extends to automation | The two-human rule and no-self-clearance are enforced; a service identity or bot account that reaches the approval route is not refused by rule | Tier 3 approvers are distinct identity-provider subjects that can be people; an approval presented by a service identity or automation is refused with its own code, and the record says so | C-14 |
| Intelligence export | Nothing; the roadmap places the consent pipeline in phase 4 | The operational change class as data in the classifier now (I-1); the export pipeline, coverage score and cell rules (I-2); the internal aggregate report (I-3); both later | I-1 to I-3 |
| W2 and W3 follow-ups | Eleven items listed in the W2 report and seven in the W3 report, none owned by a package | One hygiene package that owns them, with the detector's image and chart moved to O-4 | R-9 |

Four decisions sit under these rows and are called out in section 14: what the gateway does when the decision service is unreachable (R-1, R-3), whether Hangar's policy bundle may read Glidepath's scope live instead of vendoring it (R-5), the token format (C-1), and native ValidatingAdmissionPolicy versus a Kyverno ValidatingPolicy for grant-match admission (G-ARGO-1).

## Work packages, R-series: the refactor {#work-packages-r}

Eight packages split today's in-process gateway into its two real parts: a Clearance core service that decides and records, with its own image, and the Autopilot AI gateway that enforces and calls it. Deployment configuration moves to match. Agents keep working throughout; each package leaves hangar-dev working and the evidence chain unbroken. The order is R-1, R-6 and R-8 first (they change no deployment), then R-2, R-3, R-5 and R-7, then R-4 as one cutover on hangar-dev.

### R-1 · Core API, provider protocol and conformance harness
<!-- pkg status=live wave=W0 -->

- **Repos.** clearance. The core is written in Go from this package on (section 12, Languages); the Python modules that stay with Clearance are ported, not wrapped.
- **Depends on.** Nothing. First package.
- **Build.** One Go module, `github.com/jfillman/clearance`, one binary `clearance` with subcommands. Split it into sub-tasks a managing agent can hand out:
  1. **R-1a Decision engine** (`internal/decide`): the runtime decision as a pure function from an AuthZEN-shaped evaluation (subject, action, resource, context) to a decision with rule id, hint and the spend the caller must apply. The context carries the session state the gateway holds (tier ceiling, budgets used, breaker, requested limits, parent), so the core holds no session. Rules run on cel-go, compiled and type-checked once at bundle load with a cost limit; a rule that fails to compile fails the load. Ports `policy.py`, `tiers.py`, `scope.py` and the rule set.
  2. **R-1b Record store** (`internal/record`): Postgres through pgx with a pooled connection; the evidence chain's hash function reproduced byte for byte from the Python one (canonical JSON, field order, separators), because the Go core must extend the live hangar-dev chain. Ports `pg.py` and `audit.py`.
  3. **R-1c Gate routes**: the deployment gate, change registration, review, definition-change tiering and provenance with the GitHub App webhook, ported from `gate.py`, `register.py`, `review.py`, `definitions.py`, `provenance.py` and `github_app.py`, behaviour unchanged.
  4. **R-1d HTTP API**: `POST /access/v1/evaluation` decides and records the decision; `POST /v1/decisions/{id}/outcome` takes the call's result, effect and receipt; `POST /v1/records` takes a registered provider's own records (`session.open`, `run.launch`, `run.delete`, `human.answer`, `session.freeze`, `trigger.hold`, `deploy.outcome`, `deploy.exception`); the gate, provenance and definition-change routes keep their paths. `CLEARANCE_PROVIDERS` lists registered providers with name and version; every record gains `provider`. `contract/clearance-core.json` (OpenAPI 3.1) is generated from the handlers and drift-tested.
  5. **R-1e Clients and test core**: a Go client package and a Python client (`clients/python`, generated from the contract, released with each tag) replace `CoreClient`. Both report an unreachable core as a distinct error the caller's outage policy acts on. `clearance core --memory` runs the whole core on an in-memory store for tests, in place of `LocalCore`.
  6. **R-1f Conformance**: `clearance conformance --provider <url>` runs a fake target and a fake change and proves hold, clear, release and an outcome whose digest matches the cleared subject.
- **Done when.** A golden corpus, recorded from the Python engine over every existing denial test and the fixture agents' calls, replays through the Go engine with identical decisions, rule ids, hints and record fields; any rule that evaluates differently under cel-go is fixed in the rule and listed in the PR. `clearance chain verify` in Go passes over a dump of the live hangar-dev chain. HTTP tests cover every route; the fuzz targets in section 12 run in CI; `go test -bench` shows the decide path under its budget; a fake runtime provider passes conformance; the contract is generated and drift-tested.
- **Rollout.** Clearance release; no deployment change yet. The same PR set records the boundary decided on 2026-11-02 as a new decision in hangar `docs/autopilot/decisions.md` (amending D16) and updates `design.md` section 0.1's split table.

### R-2 · Clearance's own image and chart
<!-- pkg status=live wave=W1 -->

- **Repos.** clearance.
- **Depends on.** R-1.
- **Build.** A static Go build (`CGO_ENABLED=0`, `-trimpath`, reproducible flags) onto `gcr.io/distroless/static-debian12:nonroot` pinned by digest: no shell, uid 65532, read-only root, all capabilities dropped, seccomp RuntimeDefault. Subcommands `clearance core` and `clearance api` of the one binary: the core serves the write routes, the deployment gate, provenance and the GitHub App webhook; the api serves the read API, ported from `api.py` and the serving logic now in autopilot's `serve.py` and `api_serve.py`, minus every Hangar backend. A workflow on `v*` tags builds amd64 and arm64, publishes `ghcr.io/jfillman/clearance` with an SPDX SBOM and a keyless signature, and packages `charts/clearance` to GHCR as OCI. The chart: core Deployment, api Deployment (2 replicas), Services, PodDisruptionBudget, default-deny NetworkPolicy, optional CNPG Cluster, optional ExternalSecrets, optional HTTPRoutes, and values for every setting now in `CLEARANCE_*`, `CLEARANCE_API_*`, providers, verifiers, delegates, admins, OIDC and the GitHub App. Chart CI: helm lint, render tests, and an install test on a kind cluster with Postgres and a fake provider.
- **Done when.** `helm install clearance oci://ghcr.io/jfillman/charts/clearance` on a fresh kind cluster with no Airframe and no Glidepath passes the install test in CI: healthz and readyz, a decision evaluated and recorded for the fake provider, a change registered and cleared by policy, chain verify ok. The image is under 40 MB and the core idles under 64 MiB.
- **Rollout.** Clearance release; the image and chart exist before anything on hangar-dev changes.

### R-3 · The AI gateway moves to Autopilot
<!-- pkg status=live wave=W1 -->

- **Repos.** autopilot first (add), then clearance (remove), then backstage (the Autopilot plugin's reads).
- **Depends on.** R-1, R-2.
- **Build.** Move the gateway code from the clearance repo into autopilot, still in Python, with history where practical (`git filter-repo` on the paths, as D16 moved it the other way): the MCP surface from `server.py`, the session, budget, run-tree and spend logic from `dispatch.py`, `session.py`, `limits.py`, the tool registry in `tiers.py` (the tier vocabulary stays shared as a schema), `modelproxy.py` and the model app, the backend protocols, `profile.py` and the agent-definition schema, `runtimes.py`, `inbox.py`, `control.py`, `results.py`, `events.py`, artifacts. The move changes no behaviour; the Go port of the gateway is A-9. Their tables move to a gateway-owned database, because sessions, inbox, results and artifacts are runtime state, not evidence. autopilot drops its `clearance` package dependency and pins the generated Python client from R-1 instead. The gateway calls the core's evaluation before every tool call, model call, session open and spawn, applies the spend locally, calls the backend and reports the outcome; runtime events (session open and close, run launch and delete, human answers, person controls) go through the record API. The gateway serves its own read API for sessions, runs, agents, the inbox, trigger history and results (`autopilot-gateway api`), and the Backstage Autopilot plugin moves its reads to it. Provider name `autopilot-gateway`. The runtime pod contract (`HANGAR_*`, `/mcp`, `MODEL_PROXY_URL`, `result.json`) does not change.
- **Outage policy (decided 2026-11-02).** When the core is unreachable the gateway fails closed for every T1-and-above call, every session open and every spawn. T0 reads fail closed too unless the deployment sets `GATEWAY_OUTAGE_ALLOW_READS=true`. With the switch on, each allowed read is written to an outbox table in the gateway's database and posted to the record API in order on recovery, marked `coverage-unavailable`. The client's timeout is 250 ms with one retry, and a breaker opens after 5 consecutive failures so agents get a fast, clear denial.
- **Then** a clearance PR removes the moved modules, bumps the version as a breaking release, and extends the boundary test to assert the core holds no session, MCP or tool-dispatch code.
- **Done when.** autopilot's tests pass against `clearance core --memory` and against a core container; replaying the fixture agents' calls gives the same decisions and the same record fields as before the move; an outage test proves each branch of the outage policy; a run on hangar-dev launches, calls tools, hits the model proxy and finishes with its result.
- **Rollout.** Gateway tag plus a clearance release; deployed together with R-4 and R-7.

### R-4 · The cutover on hangar-dev
<!-- pkg status=live wave=W1 -->

- **Repos.** apron, gitops-hangar-dev, backstage, clearance docs, autopilot docs.
- **Depends on.** R-2, R-3, R-7.
- **Build.** Three workloads replace one: the Clearance core (`ghcr.io/jfillman/clearance:vX`, the only writer of `clearance-pg` and the evidence chain), clearance-api (same image), and the Autopilot gateway (its own database for runtime state, no evidence DSN). At cutover the runtime tables are copied from `clearance-pg` to the gateway's database; evidence stays where it is. Routes: a new `autopilot.<domain>` for `/mcp`, the model proxy and the gateway's read API, with `clearance.<domain>/mcp` kept as an alias until Claude Code configs and Tower move; `clearance.<domain>/v1/*` and `clearance-api.<domain>` to the core and api. NetworkPolicies: gate pods and the Gateway namespace to the core; agent-run namespaces to the gateway; the gateway to the core; only the core and api to `clearance-pg`. The Cloudflare tunnel's webhook path points at the core.
- **Done when.** Live on hangar-dev with the evidence sequence continuing across the cutover and `GET /v1/evidence/verify` ok, and every existing live check re-run with evidence quoted: an `agent-gates-` verdict, a `clearance-gate-` change, a human request answered from Tower, a person control, a GitHub App check run, a `clearance register` from the scratch repo, an AgentRun that finishes with `run_finish`, and a streaming model call.
- **User steps.** Merge the apron, gitops and backstage PRs if the classifier refuses; rerun the tunnel installer; update the Claude Code MCP config to the new host.

### R-5 · Policy bundles and Hangar vocabulary
<!-- pkg status=live wave=W1 -->

- **Repos.** clearance, autopilot, apron, glidepath docs.
- **Depends on.** R-1, R-3. Live-scope read decided 2026-11-02 (section 14, #3).
- **Build.** `clearance.packs.hangar` splits along the new line. The `glidepath.*` and `airframe.*` tool specs (names, tiers, arguments) go to autopilot with the tool registry. Rules R021 to R023 become a Hangar policy bundle (CEL rules plus the data they read) that the core loads from configuration and names, with its version, in every decision it decides; apron ships the bundle. R021's Glidepath scope is read from glidepath-api's `GET /v1/contract` by the bundle loader at startup, with a `contractVersion` compatibility check, so the vendored `glidepath-scope.json` and `cicd_scope.py` go. The core's remaining Hangar vocabulary (baseline deny paths and fields, environment tiering patterns, group-reference formats) becomes `CoreConfig` values the deployment passes. `tests/test_boundary.py` gains a data-level check: the core's source contains no Hangar names.
- **Done when.** The core carries no Hangar vocabulary; the Hangar deployment decides exactly as before (same denials, same rule ids, same records) in autopilot's tests; a Glidepath contract change no longer needs a Clearance release.

### R-6 · Evidence record v1
<!-- pkg status=live wave=W0 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** Nothing; do it early, since records written after the freeze must not migrate again.
- **Build.** `schemas/evidence.schema.json`, `clearance.evidence/v1`: field groups Identities, Source, Target, Provenance, Decision (tier, policy ref, engine, verdict, rules, reason, approvals, token ref), Outcome, Coverage state, Assurance state, Intent, Integrity; `boundary`, `provider`, `subject` (kind and digests: tool call, manifest tree, terraform plan, definition), `app`, `task_id`; AP-C1's model version and Preflight result fields reserved now. The record check from the architecture is done on a real hangar-dev record and the result written into `docs/evidence.md`. Writers emit v1; v0-draft rows stay as written (they are hashed) and the api projects them. Intent capture defaults to redacted.
- **Done when.** The schema is published and versioned; every writer emits v1 in tests; verify passes across the v0 to v1 boundary on a copy of the lab chain.

### R-7 · Clearance as its own Apron component
<!-- pkg status=live wave=W1 -->

- **Repos.** apron, gitops-hangar-dev, hangar docs.
- **Depends on.** R-2.
- **Build.** `templates/55-clearance/` (`components.clearance`): a chart-sourced Application pinned by `versions.clearance`, the CNPG cluster, routes, NetworkPolicies, the reader-credential objects. `templates/55-autopilot/` keeps the AI gateway and its own database, the catalog-token policy, AgentRun grants, the reaper and agent-sandbox; people-dex moves to its own identity group because both products sign people in through it. `cluster.yaml` gains a `clearance:` block (people, admins, githubApp, githubWorkflows, verifiers, delegates, api auditors and notifiers); `autopilot:` keeps customImages, schedules, events and argoSync. `hack/check.py`: clearance may run on any cluster role, autopilot stays control-plane only. MANIFEST conditions, TOKENS.md, `tests/run.sh` and the render tests follow. The render is diffed over a clean export before it is committed.
- **Done when.** The hangar-dev render touches exactly the expected files; Argo Applications `clearance` and `autopilot-gateway` are Synced and Healthy; R-4's live checks pass.

### R-8 · Hygiene, docs and release automation
<!-- pkg status=built wave=W0 -->

- **Repos.** clearance, autopilot, hangar, airframe (user), apron.
- **Depends on.** Nothing; runs alongside R-1.
- **Build.** A clearance `CHANGELOG.md` and a release workflow (tag to image, chart, GitHub Release with notes); `__version__` from the package metadata; the stale status text fixed (autopilot README pin table and test count, the "What is not built" list, user and admin guides; clearance `docs/index.md` and `catalog-info.yaml`; hangar Autopilot README status, design.md section 4 table, roadmap rows); the airframe re-vendor landed from the three unmerged autopilot branches; the small defects from section 3 fixed; squash-merged branches and merged worktrees listed for the user to delete (only this session's own are removed).
- **Done when.** Docs match the code at the current tags; autopilot's drift tests pass against airframe main; the list of stale branches and worktrees is in the final report.
- **User steps.** Resolve the 14 staged airframe twins and the untracked `lab/` directory with its `api-key` file in the autopilot checkout.

### R-9 · W2 and W3 follow-ups
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, glidepath, autopilot, airframe, backstage, apron. Added 2026-11-07; owns the follow-up lists of the W2 and W3 build reports so none is lost between waves.
- **Depends on.** Nothing. Runs alongside W4 as one or two Sonnet subagents; each item is its own PR.
- **Build.** Core: de-duplicate `POST /v1/records` (C-9's adapter and the collectors are at-least-once; idempotency by provider, kind and the provider's own event id). Provenance: scan every commit of a PR, not only the head. Glidepath: map the `unattested` verdict to `person` in `clearance-gate` before it sends `coauthors`; the broker allows agent tokens for the tenants repo (needed by `xr.request` and A-3). Gate: pin the wait Job's `serviceAccountName` or remove the knob. Tower: the provenance view reads `hangar-trusted-root`. airframe: push `limits.tools` (02540fe) and re-vendor the XRD into autopilot in the same change; pin the Dockerfile bases in airframe and glidepath. Backstage ingestor: read the CRD list it needs, and make the mass-removal guard hold rather than empty a cluster after three runs. Lab: delete the four duplicate runtime tags; note the hangar-dev IP and the seeded `kubeadm.conf` in hangar docs. The detector's workflow, image and chart (a W3 follow-up) are not here; O-4 absorbs the detector.
- **Done when.** Each item is merged with its test, or listed as descoped with the reason; the W2 and W3 follow-up lists in this document are annotated with the PR that closed each line.
- **User steps.** Merge where the classifier refuses; delete the duplicate tags.

### R-10 · Product naming and placement
<!-- pkg status=in-progress -->

Added 2026-11-11. Owns the naming items left by R-4 (W1 build report: the gateway kept the name `clearance`, the `clearance.<domain>/mcp` alias) and two owner decisions of 2026-11-11: the gateway gets its own setting prefix, and Clearance moves to its own namespace. When it is done, every running name says which product it belongs to. Autopilot still depends on Clearance (the gateway enforces, Clearance decides, fail closed). Clearance still installs alone.

- **Repos.** autopilot, airframe (function-agentrun), apron, gitops-hangar-dev, glidepath (broker and delegate lists), clearance docs, hangar docs, backstage (Tower config).
- **Model.** Sonnet subagents, one per lettered step; the managing agent runs the live checks between steps. Each step leaves hangar-dev working and the evidence chain unbroken.
- **Depends on.** Nothing open. Runs alongside A-10.
- **Build.**
  1. **R-10a Gateway setting prefix (autopilot).** Settings the gateway owns move to `AUTOPILOT_*` (agents dir, Agent XR polling, OIDC for people, admins, delegates, resource URL, events, schedules, Argo, Airframe, model routes). The old `CLEARANCE_*` names stay as aliases for one release and log a deprecation warning. Names that configure the Clearance client keep their prefix: `CLEARANCE_CORE_URL`, `CLEARANCE_CORE_TOKEN_FILE`, `CLEARANCE_API_URL`. The refuse-list of core-only settings keeps working. Audience values are not names and do not change here.
  2. **R-10b Run-pod contract (airframe, autopilot runtime).** function-agentrun renders `AUTOPILOT_URL` beside `CLEARANCE_URL`, and the runtime reads the new name first. A run pod's gateway token gets its own audience, `autopilot`, so a token meant for the gateway cannot be presented to the Clearance core; the gateway accepts both audiences for one release. Ships as an Airframe tag, a function digest pin in apron and a runtime release.
  3. **R-10c Gateway rename (apron, glidepath, gitops).** Deployment, Service, labels, ServiceAccount, Argo Application and monitoring become `autopilot-gateway`. During one release the principal lists carry both `autopilot-system/clearance` and `autopilot-system/autopilot-gateway`: Clearance's provider registration, glidepath-api delegates and readers, the Argo sync VAP, the catalog-token VAP, the AgentRun Role, the broker callers. A `clearance` Service in `autopilot-system` stays as a selector alias for run pods still on the old contract. `model-proxy` selects the new label.
  4. **R-10d Clearance to `clearance-system` (apron, gitops).** `clearance-core`, `clearance-api` and `clearance-pg` move from `autopilot-system`. First a verified `pg_dump` of the chain, stored outside the cluster. The old core scales to zero before the new one starts, because of the one-writer lock. Restore into the new CNPG cluster, re-create the ledger volume and the ExternalSecrets, and make the NetworkPolicies cross-namespace (namespaceSelector) for the gateway, people-dex and the observers. Hostnames do not change: `clearance.<domain>` and `clearance-api.<domain>` are the cross-cluster contract with hangar-prod, so only the route backends move. Add a CNPG backup schedule; the chain has none today.
  5. **R-10e Hosts and clean-up.** `/mcp`, the model proxy and the gateway read API are served only on `autopilot.<domain>`. Fix `CLEARANCE_GATEWAY_URL` in `clearance-api` and `autopilot-api` to the same host. Retire the `clearance.<domain>/mcp` alias after the Claude Code config and Tower move. Then remove the one-release aliases: the old principal, the `clearance` Service, the old audience, the old env names.
  6. **R-10f Docs.** Admin guides, the install docs, hangar decisions.md (one decision row for the prefix and the namespace), the architecture section of this spec, and the new architecture pages.
- **Done when.** On hangar-dev, nothing named `clearance` runs in `autopilot-system`. An agent run finishes with `run_finish` and a model call, and its records name provider `autopilot-gateway` with principal `autopilot-system/autopilot-gateway`. The chain continues across the move with no gap in seq, and `GET /v1/evidence/verify` is ok. hangar-prod's gate still works: a CMP registration, a grant-feed sync and an observe-k8s record after the move. A packet builds and verifies offline. `/mcp` on `clearance.<domain>` returns 404.
- **Owner steps.** Point the Claude Code MCP config at `autopilot.<domain>`. Approve the namespace move's short write pause on hangar-dev. Merge any PR the classifier refuses.

## Work packages, A-series: the Autopilot AI gateway {#work-packages-a}

Nine packages finish the gateway as the design defines it: a conformant runtime provider, a stable agent identity, the write half of the Airframe tools, recorder and cost fields, durable triggers, Preflight in CI, runtime polish, the Skyport agents, and the port of the gateway to Go.

### A-1 · Runtime provider conformance and records
<!-- pkg status=unverified wave=W2 -->

- **Repos.** autopilot.
- **Depends on.** R-3.
- **Build.** The provider passes R-1's harness; every runtime record names `provider: autopilot-gateway/<gateway tag>`; the model proxy reports as the same provider with subject kind `model.call`; `describe()` output and the admin docs state the provider contract.
- **Done when.** Conformance is green in autopilot CI against a core container; a live run's records on hangar-dev carry the provider.

### A-2 · Stable agent identity by ID-JAG (AP-A4)
<!-- pkg status=later wave=W4 -->

- **Repos.** autopilot, clearance, apron. D19's issuer decided 2026-11-02 (section 14, #7).
- **Depends on.** R-3.
- **Build.** First, the issuer evaluation: a Dex build carrying dexidp/dex#4611 runs in people-dex's slot on hangar-dev, and the package records whether it issues a correct ID-JAG (RFC 8693 exchange, `aud`, `act`, lifetime, signature) against a test client. If it fails, Keycloak token exchange takes people-dex's place, and the evaluation says why. Then the run pod exchanges its service-account token at that issuer for an ID-JAG naming the agent identity (one per definition), the human it acts for and `aud: clearance`, and presents it as an RFC 7523 bearer; the gateway's session principal, which R001 compares in every evaluation, becomes the ID-JAG subject; narrow-only stays Clearance's at each hop. Ship behind `CLEARANCE_IDJAG_ISSUER` with a test issuer in CI.
- **Done when.** The evaluation is written up with its test output; a run on hangar-dev authenticates with an ID-JAG, R001 is decided from its subject, and the record names both the agent identity and the human.
- **User steps.** Approve the evaluation's result, and create any new OAuth client secrets in Infisical.

### A-3 · `airframe.apply` and the parachute sentence live (AF-8b)
<!-- pkg status=unverified wave=W4 -->

- **Repos.** autopilot, airframe docs.
- **Depends on.** R-3, C-7 (provenance confirmed-agent needs signed agent commits, D1).
- **Build.** `airframe.apply` as a T1 tool: the planner's change set opened as PRs through the agents' App (source repo, tenants repo, gitops repo), each PR receipted; the Flight half stays a human merge step; the `airframe.validate` tool restored to the image or removed from every definition. A `parachute` definition. A resume test and a seeded bad run.
- **Done when.** M3's exit: the parachute sentence runs end to end on hangar-dev with a human merging the Flight PRs; killing the core mid-run still ends every run on time; the seeded bad run scores as failed in Preflight.

### A-4 · Flight recorder fields and cost accounting (AP-C1, AP-C2)
<!-- pkg status=unverified wave=W2 -->

- **Repos.** autopilot, clearance.
- **Depends on.** R-6.
- **Build.** Every run record carries the pinned model version and the Preflight result of its definition; token and compute usage per run, per agent and per task tree accumulate in the records and are exposed by `GET /v1/evidence/counts?by=cost` and on the session; Tower reads them later.
- **Done when.** A live run's records show model version, Preflight result and cost; counts match the proxy's charged tokens.

### A-5 · Trigger durability
<!-- pkg status=unverified wave=W2 -->

- **Repos.** autopilot, clearance, glidepath docs.
- **Depends on.** R-3.
- **Build.** The bridge keeps its glidepath-api cursor in the gateway's own database, resumes with `Last-Event-ID` and `/v1/events/recent?since` on restart, and runs a reconciliation sweep comparing release records to events seen, so a missed `pipelinerun.finished` still launches once; a metric and alert for the gap. A RabbitMQ source behind a flag for the Skyport agents. ADR-0030 (AMQP fan-out in Glidepath) stays deferred by the user's 2026-11-01 decision.
- **Done when.** Restarting the gateway during a build loses no trigger on hangar-dev; a seeded gap is reconciled; the nightly slot runs on time.

### A-6 · Preflight harness and the CI gate
<!-- pkg status=unverified wave=W4 -->

- **Repos.** autopilot, clearance, glidepath.
- **Depends on.** A-1, R-6.
- **Build.** `RunRecord`s produced from real runs (results plus evidence) and from a local harness `autopilot preflight run --case`; on a definition PR the `agent-definitions-` check asks the gateway to launch a budgeted Preflight run of the candidate definition (`POST /v1/agents/{name}/runs` with the document), scores it against the cases and reports a `preflight-` check; the seeded bad run must fail.
- **Done when.** Six Preflight cases pass and their seeded bad runs fail in CI on hangar-dev; the score lands in the record.

### A-7 · Runtime images and run polish
<!-- pkg status=built wave=W2 -->

- **Repos.** autopilot, apron, gate-api (user).
- **Depends on.** R-3.
- **Build.** base-python rebuilt with `finish`; the tools list carried in `HANGAR_LIMITS`; gate-reader re-pinned to the new runtime; gateway logs shipped to Loki for `autopilot-system`; Dockerfile base images pinned by digest everywhere; `xr.request` implemented as a PR to the tenants repo through the agents' App; `app.api.get` and `chat.*` either implemented through the inbox or removed from definitions; a `/healthz` on the public route.
- **Done when.** Every bundled definition runs on an image that calls `finish`; no tool in a loaded definition lacks a backend.

### A-8 · The Skyport agents (M4)
<!-- pkg status=later -->

- **Repos.** autopilot, airframe docs.
- **Depends on.** A-5, A-7, the Tower chat surface (section 13).
- **Build.** The six demo agents, one per workload shape, each with a Preflight case and a seeded bad run; walked live and recorded in the quickstarts.
- **Done when.** One `task_id` traces a disruption from broker message to final artifact.
- Listed for completeness; it runs after the gates.

### A-9 · The gateway in Go
<!-- pkg status=in-progress wave=W4 -->

- **Repos.** autopilot, apron.
- **Depends on.** R-3 and R-4 live on hangar-dev; A-1 (conformance) merged.
- **Build.** Port the Python gateway that R-3 moved into a Go service in `autopilot/gateway/`, one binary with `serve` and `api` subcommands, on the same distroless base as Clearance. MCP on the official Go SDK (`github.com/modelcontextprotocol/go-sdk`); the model proxy as a streaming reverse proxy that never buffers a response body and passes server-sent events through; sessions, budgets, run tree and spend in the same gateway database schema, so both implementations can read it; the Clearance Go client from R-1e. The tool registry, backends and pod contract keep their names and shapes. Every dispatch runs under a context deadline, and every backend call has its own timeout and connection pool.
- **Done when.** The R-3 replay corpus gives identical decisions and record fields through the Go gateway; the conformance harness passes; a load test shows the gateway's own p99 overhead per tool call under 5 ms excluding the decision call, at 200 concurrent sessions; a canary agent definition runs on the Go gateway on hangar-dev for 7 days with no divergence in its records; then every definition moves and the Python gateway is removed.
- **Rollout.** A `gateway-v1.*` tag, canary through a per-definition gateway selector in the profile, then the full cutover through the release chain.
- **Why now and not in R-3.** Moving the code and rewriting it in one step would leave no working reference to compare against; R-3 keeps the Python gateway as that reference.

### A-10 · The Skyport agents on the cluster
<!-- pkg wave=W5 -->

Added 2026-11-09 for W5. A-8 wrote the definitions and Preflight cases, but they have never been deployed: the gateway loads only the top level of `agents/`, and no `Agent` XR pins them. This package deploys them as a team's own agents, so the image keeps only the core platform set.

- **Repos.** A new `skyport-agents` (composed by `AgentRepository`), autopilot, apron, airframe docs.
- **Model.** Sonnet subagents, one per numbered step below; the managing agent runs the live checks.
- **Depends on.** A-8 (the definitions), A-6's live wiring (the Preflight PR check). The event step also needs A-5's trigger durability. Runs alongside W5's observation work and is **not part of W5's gate**.
- **One repository.** All nine definitions share `skyport-agents`, owned by `group:default/team-skyport`. They are prompt-only on shared runtime images, which is what `AgentRepository` is for. Each `Agent` XR pins its own commit, so they still release independently, and each workload-identity agent still gets its own `autopilot-runs/<name>` identity. They also read several APIs, so no single app repo is their natural home. Split a repository out only for a different owning team, or for a code agent with its own image, which is onboarded as an application.
- **Build.**
  1. Install `AgentRepository` on hangar-dev. Its XRD ships in Airframe v0.3.173 but is missing from the include list in apron's `airframe-service-catalog` Application.
  2. Create `skyport-agents`, and move the nine definitions and six `skyport-*` Preflight cases out of autopilot, updating `tests/test_preflight.py` and `tests/test_airframe_apply.py`. First confirm which cases the `preflight-` check scores: the gateway reads its image's `preflight/cases`, while the scaffold gives the new repo its own.
  3. Set `APP_API_SERVICES` for flight-api, boarding-api and baggage-api, with the gateway's network reach to each. `app.api.get` has no backend until this is set.
  4. Release through the normal path (`agent-release`, the pin PR, Clearance's gate), read-only agents first. Release `irregular-ops-team` and its three members together. Confirm the deployed backends can run each kind, including `session` and `service`.
  5. Build the RabbitMQ reader in `docs/admin/trigger-durability.md` for `disruption-responder`, the one event-triggered agent. `EVENTS_RABBITMQ_ENABLED=1` refuses to start until then.
- **Identity limit.** Six of the nine are `delegated`. With A-2 deferred, they act for a signed-in person through `people-dex`, and a triggered run gets no delegated identity. The three `workload` agents are the ones that can run unattended.
- **Owner steps.** Clearing any hold that needs a person, and creating the broker credential in Infisical.
- **Done when.** Clearance's `GET /v1/agents` lists all nine with a cluster source and none in `rejected`, with no gateway image built for them. Moving one pin to a new commit changes only that agent within a poll. `app.api.get` reaches all three services from a real run. A-8's own test passes: one `task_id` traces a disruption from broker message to final artifact.

## Work packages, C-series: Clearance core, attestation and ledger {#work-packages-c}

Eleven packages complete the shared core as the architecture defines it: a signed token, an attestation signed after the sync outcome, a witnessed ledger of hashes, an open verifier, the packet, the outage and coverage machinery, provenance confidence, recorded policy verdicts, an AuthZEN decision point, and the read API the gates need. Three product lines (Slack approvals, the Infisical provider, the hosted App) are listed last and run after the gates.

### C-1 · The clearance token
<!-- pkg status=live wave=W2 -->

- **Repos.** clearance. Decision in section 14 (format).
- **Depends on.** R-1, R-6.
- **Build.** On `deploy.clear` the core issues a signed, short-lived token bound to the subject: subjects (commit, tree root or plan digest, image digests as cross-references), per-object rendered hashes with `changed`, target cluster and environment, tier, policy ref and engine verdict, provenance level and `task_id`, approvals with IdP subject and issuer, `iat`, `exp`, nonce. Recommended format: a DSSE envelope, so one signing path serves tokens and attestations; a JWT projection is available for the PreSync hook. The nonce is kept so a token cannot be replayed; a new head invalidates it. `GET /v1/clearances/{id}` returns the token to callers that may read the change; `GET /v1/clearances?cluster=&state=cleared` returns the feed grant-sync consumes.
- **Done when.** Token tests cover issue, verify, expiry, replay and a changed digest; the api serves the feed; the signing key is a file in the lab and a KMS reference in the chart values.

### C-2 · The attestation signer, and C-2a the signing identity
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance; glidepath and apron for C-2a.
- **Depends on.** R-6, C-1, G-ARGO-3 (outcomes) for the first real attestation.
- **Build.** C-2a is platform work: the Hangar signing PKI in the C-2a design below is rolled out (today each cluster's Fulcio self-generates), and the core gets an OIDC identity Fulcio trusts (`clearance-recorder@hangar-dev`). C-2 is the signer: after a `deploy.outcome` arrives, assemble the in-toto Statement v1 (subject: tree root, commit, image digests; predicate type `https://clearance.hangarplatform.dev/change-attestation/v1` with clearance id, tier, policy, approvals, provenance, outcome, coverage, limitations), wrap it in DSSE, sign keyless, log it in Rekor, append the envelope digest to the record and keep the envelope in object storage or Postgres. An approved change that never synced gets no attestation. The signer runs in the core, never in a CMP.
- **Done when.** A real hangar-prod change produces an attestation that `cosign verify-attestation` accepts against the Hangar root and Rekor; a held-but-unsynced change has none.
- **User steps.** Approve the root CA design; create the Fulcio OIDC client.

#### C-2a design: the Hangar signing PKI (decided 2026-11-02: design now)

Hangar gets one offline root and one Fulcio intermediate per cluster, and a versioned trusted-root file keeps every past signature verifiable across rotations. Today each cluster's Fulcio mints its own root on first sync (apron's fulcio-bootstrap hook), and the root has already rotated twice, leaving everything signed under the old roots unverifiable.

| Element | Design |
| --- | --- |
| Root CA | "Hangar Root CA", ECDSA P-384, 10 years, path length 1, key usage certificate and CRL signing only. Generated offline by the user; the key is stored encrypted offline in two places and is never in a cluster, Infisical or git |
| Fulcio intermediates | One per cluster (hangar-dev, hangar-prod): "Hangar Fulcio \<cluster>", ECDSA P-256, 2 years, path length 0, extended key usage code signing. Signed by the root in a key ceremony; the key goes to Infisical and reaches Fulcio through an ExternalSecret. Fulcio runs its file CA with the chain, replacing the bootstrap hook |
| Rekor key | Each cluster's Rekor signing key becomes managed the same way (Infisical, ExternalSecret), instead of generated in-cluster, so log entries stay verifiable after a redeploy |
| Leaf certificates | Fulcio's default 10-minute certificates. Rekor's signed entry timestamp proves each signature fell inside its certificate's window |
| Trusted root | A Sigstore `TrustedRoot` JSON listing every Fulcio chain and Rekor key with its validity window. `clearance trust-root build` generates it from the public certificates in apron. It is published as a ConfigMap on each cluster and as a release asset, and embedded in every packet. Every record names the trusted-root digest it was signed under |
| Signing identities | Fulcio admits only each cluster's API-server issuer (and the ID-JAG issuer after A-2). Allowed subjects: the `clearance-recorder` service account for change attestations, Tekton Chains for build provenance, agent run identities for gitsign commits. `clearance verify` checks issuer and subject against a per-predicate identity policy shipped in the packet |
| Rotation | Intermediates are re-issued at 18 months with a 6-month overlap; the old one stays in the trusted root with its window closed. On compromise, a new trusted-root version closes that intermediate's window at the compromise time; signatures logged before it stay valid. The root is re-keyed by cross-signing at year 8 |
| Scope | Code signing only. TLS stays on cert-manager's own CAs |
| Legacy | Current self-generated roots whose certificates still exist go into the trusted root as legacy entries for their windows. The 2026-08-24 root is gone, and its signatures stay unverifiable, as already recorded |

- **Agents build:** apron values and ExternalSecrets for the file CA and the Rekor key; removal of the bootstrap hook; `clearance trust-root build`; the identity policy and its use in `clearance verify`; a key-ceremony checklist and rotation runbook in hangar docs.
- **The user does:** generates the root and the two intermediates following the checklist, stores the root key offline, and creates the Infisical secrets. No agent ever handles private key material.
- **Done when:** on a kind cluster, a recorder attestation and an agent commit signature verify with `clearance verify` using only the published trusted root, before and after a simulated intermediate rotation; then the same holds on hangar-dev with the real chain.

### C-3 · The ledger
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, apron.
- **Depends on.** R-6.
- **Build.** A Tessera log (transparency-dev) holding record hashes only, with C2SP checkpoints signed every N records or every minute; a witness protocol client that collects countersignatures and refuses to publish a checkpoint a witness rejected; assurance state per record moves from recorded-not-checkpointed to checkpointed when its hash is under a witnessed checkpoint; the outage knob for tier 3 (wait while evidence cannot be checkpointed, default on). For the lab, one witness Clearance does not operate: a small witness Deployment on hangar-prod with its own key, run from the apron prod profile. The local anchored `Checkpoint` is retired.
- **Done when.** Truncating the ledger and re-signing is refused by the witness; rotating the signing key leaves old entries verifiable; an altered row is named; a witness outage during a tier 3 change makes the change wait and the assurance state shows it.

### C-4 · `clearance verify`
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance (Apache 2.0, its own small package so it stays installable alone).
- **Depends on.** C-3, C-5.
- **Build.** `clearance verify <packet>`: checks checkpoint signatures and witness countersignatures against known keys, proves inclusion for every cited record, recomputes committed hashes from the packet's originals, checks every attestation's Sigstore signature and Rekor inclusion proof, and names the altered line if one exists; keeps a local note of checkpoints seen (the weak-witness behaviour). Offline; no call to Clearance.
- **Done when.** A 30-day lab packet verifies on a machine that cannot reach the recorder; each tamper case in C-3 fails with the right message.

### C-5 · Packet v1 and control mappings
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** R-6, C-2, C-3, O-1 (the schema with the six coverage states and the health record, so the packet is not frozen without them) and C-14.
- **Build.** The packet job: a date range and scope to JSON (canonical), CSV projections and a PDF presentation; sections Header, Coverage statement (counts by coverage and assurance state, degraded windows, and the observation-health summary per scope from O-1, so "no exceptions detected" is printed only beside the window in which coverage was verified and a scope with no collector prints blind), Control assertions, Changes, Human-cleared changes (with approver kind from C-14), AI identities, Exceptions (one row per class: out-of-band with actor, diff and resolution; break-glass; attempted-refused; monitoring-protection; degraded-mode auto-clears; invalidated tokens; provider correlation failures), Policy changes, Verification, Acceptances. Mappings as data keyed by framework, version and control, with `soc2/2017` CC8.1 and `soc2/2027-draft` CC7.1 first, published as a signed OSCAL component definition. Terraform subjects render beside Argo ones. Freeze and incident reports as two scoped views.
- **Done when.** A 30-day lab packet that includes failures, a rollback and a deliberate bypass renders in all three forms, verifies with C-4, and the coverage statement counts match the records.

### C-6 · Outage policy, coverage states, break-glass and exceptions
<!-- pkg status=built wave=W2 -->

- **Repos.** clearance.
- **Depends on.** R-6, R-1.
- **Build.** The `outage` block of `clearance.yaml` and the platform baseline (tiers 0 and 1 allow-and-record, 2 and 3 hold); degraded-mode records when a provider reports the core was unreachable (`POST /v1/records` with `coverage: coverage-unavailable` on recovery); the clearance state machine with the side states (held, expired, superseded, degraded, exception); `deploy.exception` as a first-class record with kinds out-of-band, drift, untraced-apply and digest-mismatch; break-glass as `POST /v1/breakglass` with a named user, reason and TTL, recorded before the change and reconciled when the TTL ends. `ChangeRequest.protected` is used or removed; `flight_registries` becomes configuration so the image rule fires.
- **Done when.** State-machine tests cover every transition; a provider's degraded-mode report appears in the packet's exceptions; break-glass shows in the record before the change it covers.

### C-7 · Provenance confidence and the retirement of `agent-gates-`
<!-- pkg status=done wave=W3 -->

- **Repos.** clearance, glidepath, apron.
- **Depends on.** C-2a for commit signatures against Hangar's Fulcio.
- **Build.** `provenance.py` models the four levels: confirmed agent (the agents' App identity plus an agent-signed commit plus agent metadata), probable agent (metadata or bot identity without a signature, or a squash whose constituents were agent-signed), confirmed human (human-signed, no markers, a person initiated), unknown (treated as agent). Signals and their verified or claimed tag: App identity, commit signatures checked against Fulcio, Claude Code and Copilot metadata headers, Tekton Chains attestations, the initiating human from the session record. The GitHub App posts the level and reason on its check. On Hangar, after the App's verdicts agree with `agent-gates-` on real agent PRs, the onboarding template is removed, the guardrail renamed to the App's check, and the NetworkPolicy exception dropped.
- **Done when.** Each level is produced by a fixture PR; the App and `agent-gates-` agree on ten real PRs; `agent-gates-` is retired from the catalog and the Clearance verifiers list.
- **User steps.** Rulesets on the app repos name the App's checks.

### C-8 · Policy engine verdict in the record
<!-- pkg status=unverified wave=W2 -->

- **Repos.** clearance, glidepath.
- **Depends on.** R-6.
- **Build.** Every deployment decision records `policy: {ref: clearance.yaml@<commit>, engine: kyverno/<version>, verdict}`; on Hangar the `clearance-gate` task and the CMP pass the offline Kyverno result from the policy bundle (the policy-validation gate's mechanism) as a check result; the core keeps the rule-set version so a decision can be reproduced. The runtime stays CEL.
- **Done when.** A deployment record on hangar-dev carries the engine, version and verdict, and a changed `clearance.yaml` commit changes the ref.

### C-9 · The Traefik Hub adapter
<!-- pkg status=built wave=W2 -->

- **Repos.** clearance.
- **Depends on.** R-1, whose evaluation API is already the AuthZEN decision point: a customer who runs Traefik Hub can point the Sovereign Trust Plane at it and get Clearance's tiers and structured denials.
- **Build.** An adapter that ingests Sovereign Trust Plane decision records into the ledger as a federated runtime source, correlated to `task_id` through the access log's trace identifiers. Specified against the published record format and marked unverified until a record exists to test against.
- **Done when.** A recorded-format test passes; the live check waits for a Hub licence or a partner who runs one.

### C-10 · clearance-api for the gates
<!-- pkg status=live wave=W2 -->

- **Repos.** clearance, backstage (vendored contract only).
- **Depends on.** C-1.
- **Build.** The contract regenerated as OpenAPI 3 (the route table stays the source); `GET /v1/stream` as server-sent events of new records and clearances; the signed grant feed per cluster; `GET /v1/github/installations`; an installation filter on evidence and receipts. The runtime reads (sessions, run trees, agents, the inbox, trigger history, results) leave clearance-api for the gateway's read API in R-3. The Backstage plugins re-vendor both contracts.
- **Done when.** The grant-sync agent (G-ARGO-3) and Tower both read the new routes live; the stream replaces Tower's polling in a follow-up.

### C-14 · Approver independence extends to automation
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar docs. Added 2026-11-07 from the Underwriting companion; the Architecture's chapter 04 invariants and its decisions table carry it as decided.
- **Depends on.** C-1 (the token's approvals block), R-6.
- **Build.** The two tier 3 approvers must be distinct identity-provider subjects that can be people: the approval route refuses a principal whose issuer or subject marks it as a service identity, a bot account or any automation (TokenReview service accounts, GitHub Actions OIDC, the agents' App, an ID-JAG agent identity) with a new code `DG-APPROVER-AUTOMATION`, and refuses two approvals that resolve to one subject through aliases or the same session with `DG-APPROVER-SAME`. The existing no-self-clearance and outside-team rules stay. The approvals block in the token and in the record carries `kind: person` with the issuer, so the packet's human-cleared section and the verification statement's insurer profile can print "approvers: distinct subjects, none automation" from verified fields.
- **Done when.** Unit tests cover a service-account approval, a bot approval, an ID-JAG agent approval, two aliases of one person and two people; a hangar-prod tier 3 change cleared by two people shows `kind: person` on both approvals in the record; the Architecture's chapter 04 text and the business rules gain the rule with a stable id.
- **Rollout.** Clearance release.
- **User steps.** None.

### Later in this series

### C-11 · Slack approvals
<!-- pkg status=later -->

One-tap approve or deny for held changes, identity still resolved through the IdP. After the Argo gate is live.

### C-12 · Infisical as a federated provider
<!-- pkg status=later -->

Posture, correlate and coverage for secret rotations; the runtime gateway stamps `task_id` into the change request. Unverified whether Infisical's API carries metadata beyond a comment. Phase 2 of the product roadmap.

### C-13 · Hosted multi-tenant App
<!-- pkg status=later -->

Tenancy by installation, a KMS for the key, per-installation rate limits, the public listing. Phase 3.


### C-15 · Warm-standby core

Added 2026-11-12 (owner). A subscriber has one Clearance core: one chain, one ledger, one packet. Every gate, gateway and collector depends on it, and it runs as one replica, so a node loss or a bad rollout stalls gated deploys and agent calls everywhere until it is back. The core already takes a PostgreSQL advisory lock as the chain's only writer. This package runs a second replica that waits on that lock and takes over when the leader goes, and proves it with a failover test.

- **Repos.** clearance (core, chart), apron, gitops-hangar-dev.
- **Model.** One Sonnet subagent per lettered step; the managing agent runs the failover test.
- **Depends on.** Nothing open.
- **Build.**
  1. **C-15a Leader and standby.** Two replicas. The one holding the advisory lock is the leader: it serves writes, runs the background loops (ledger checkpoints, token refresh, expiry sweeps, the GitHub App's retries, the grant-feed signer) and reports `/readyz` ready. The standby connects, waits on the lock, keeps its policy bundles loaded and its chain verified up to the head, and reports `/readyz` not ready with `role: standby`, so the Service sends it nothing. `/healthz` stays ok on both.
  2. **C-15b Fencing.** A leader that loses its database session loses the lock, so it must stop writing at once: every chain write runs in a transaction that first confirms this session still holds the lock, and a leader that cannot confirm it steps down, fails its in-flight requests with 503 (callers already treat 503 as no decision) and goes back to waiting. No record is written by two cores, and none is skipped.
  3. **C-15c Takeover.** On acquiring the lock the standby re-reads the chain head, verifies from the last checkpoint, opens the ledger and catches up its volume from the chain (the volume is a rebuildable cache), checks the last witnessed root, then turns ready. The ledger moves to a volume per replica (a StatefulSet with a claim template), or a shared volume if the storage class allows it.
  4. **C-15d Chart and rollout.** Replicas 2 with anti-affinity across nodes, a PodDisruptionBudget of one available, and a rolling update that replaces the standby first. The same signing key, ledger key and GitHub App secret on both, from the same ExternalSecrets. Metrics: role, takeover count, takeover duration, time since the last lock check.
  5. **C-15e Failover test.** An automated test in CI against two core processes and one PostgreSQL, and a live run on hangar-dev with traffic flowing (the gateway's calls, the collectors' records and a gate registration): delete the leader pod; kill its database connection only (a network partition); stop PostgreSQL briefly; roll the Deployment. For each, measure the time with no ready core, count the 503s callers saw, and check the chain: sequence numbers with no gap and no duplicate, every `prev_hash` link intact, `GET /v1/evidence/verify` ok, and the next witnessed checkpoint consistent with the last.
- **Done when.** On hangar-dev with two replicas, deleting the leader gives a ready core again within 15 seconds; a partition of the leader from PostgreSQL leaves exactly one writer; the chain stays gap-free and verified through every case; the measured numbers are in the core's docs.
- **Not in this package.** PostgreSQL itself stays one instance on the lab (an earlier owner decision); a standby core does not survive a database outage, and the docs say so. A highly available database for a subscriber is a separate decision.
- **Owner steps.** None expected.

### C-16 · Bring your own gateway and CI

Added 2026-11-12 (owner). Clearance is meant to install alone, for a team that has its own CI/CD and its own agent gateway. The contract already exists and is Clearance's, not shared among Hangar's products: the published API (`contract/clearance-core.json`, `clearance-api.json`), the provider protocol, AuthZEN 1.0 for runtime decisions, policy bundles, and the conformance harness. Autopilot and Glidepath are its first clients. Four things stand between that and a team using it without Hangar.

- **Repos.** clearance (core, docs, examples), autopilot and glidepath (for the vocabulary switch).
- **Model.** One Sonnet subagent per lettered step; the managing agent runs the end-to-end example.
- **Depends on.** Nothing open.
- **Build.**
  1. **C-16a A neutral default vocabulary.** The receipt and trailer vocabulary is configuration, but its defaults still say Hangar: the `Hangar-*` commit trailers (`CLEARANCE_TRAILER_PREFIX`) and the `X-Hangar-On-Behalf-Of` header (`CLEARANCE_ON_BEHALF_OF_HEADER`). Make the product defaults `Clearance-*` and `X-Clearance-On-Behalf-Of`, and have Hangar set its own values explicitly in apron, so nothing on Hangar changes. Check every other default for a Hangar name (the vocabulary package, `internal/vocab`) and move it the same way.
  2. **C-16b Runtime conformance on record.** `clearance conformance --role runtime` is shown passing only for the Argo CD and Terraform paths in Clearance's docs. Run it against Autopilot's gateway and against a minimal reference gateway (C-16c), record both passes in `docs/provider-protocol.md`, and run the reference one in Clearance's CI.
  3. **C-16c A reference gateway and a reference deploy, in the repo.** `examples/byo/`: a small agent gateway (a few hundred lines) that asks `POST /access/v1/evaluation` before each tool call, applies the spend, opens a pull request, posts the outcome with its receipt (`repo`, `pr`, `commit`, `branch`, `paths`) and writes the trailers; a policy bundle for its two or three tools; and a GitHub Actions workflow that registers its deploy with `clearance register` and deploys to a GitHub environment behind Clearance's deployment protection rule. It runs against `clearance core --memory` in CI.
  4. **C-16d The guide.** `docs/byo.md`: install Clearance alone (the chart, PostgreSQL, the GitHub App), wire your gateway (the four calls and the trailers), wire your CI (register, Terraform, Argo CD, or the raw protocol for any other tool), turn on observation, and read a packet, using the C-16c example throughout. It states the limits: GitHub only for the App, provenance and register (GitLab and Bitbucket would need adapters), and what a team gives up without the Argo CD gate.
- **Done when.** On a fresh kind cluster with only Clearance installed, the reference gateway's agent opens a pull request that Clearance's App vouches for (`Clearance / agent-identity` and `agent-scope` confirmed), the reference workflow's deploy is held and cleared through the deployment protection rule, and a packet built from that chain verifies offline. Hangar's own trailers and headers are unchanged.
- **Owner steps.** A GitHub org or account for the example's App installation, if the lab's cannot be used.

### A-11 · Agent provisioning hardening (parachute test findings, 2026-11-12)
<!-- pkg status=built -->

**Why.** The owner's parachute test (six runs of the `parachute` agent, same free-form prompt) provisioned the app only with manual help. Each run spent 14 to 16 `airframe.plan` calls guessing the AppSpec; three runs produced three different specs, one silently dropped the env vars and canary; `airframe.apply` failed twice with a bare "backend error" and once refused with APPLY-EXISTS on a file onboarding creates; the Flight half (prod) was left for a person to write. Tokens were not the problem (about 50k charged per run); predictability was.

**Already fixed during the test (live on hangar-dev 2026-11-12).** Clearance 0.42.0 + gateway-v0.6.0: the gateway publishes its bundled agents to the core (`PUT /v1/definitions` `bundled`), so a bundled agent's PR passes `Clearance / agent-scope` instead of AS004. Clearance 0.41.3: Tower's alert poll (notifier + observer) answers 200. Both GitHub Apps now cover all repositories.

**Steps.**

- **a. `airframe.capabilities` returns the AppSpec.** A new `appspec` section: the top-level fields, how `config` (every environment) and `overrides` (one environment) map to the chart fields, and one complete worked example (env vars + canary). Under the runtime's 16,000-character tool-result limit (the vendored schema is 225 KB: summarise, never dump). `airframe.plan`'s description names `config` and `overrides`.
- **b. Clipped results say so.** The runtime marks a clipped tool result as clipped and says how to narrow the call (`section`, `kind`).
- **c. `apply` merges into onboarding-created files.** For `glidepath/envs/<env>.yaml` and the gitops `values.yaml`, apply adds its keys to the file the platform scaffolded and opens a PR showing the diff, instead of APPLY-EXISTS. It still refuses when a person has set the same key to another value.
- **d. `repos-ready` waits for onboarding to finish:** the onboarding resync PR merged, not only `CicdOnboarded=True` (the race behind parachute#2).
- **e. Errors pass through.** Glidepath's broker logs every failure; the gateway passes the broker's and GitHub's message to the agent ("the App is not installed on jfillman/parachute") instead of "backend error".
- **f. `parachute` instructions.** Call `capabilities` once and plan once; if the request asks for something the spec cannot express, stop and ask with `human.request`, never proceed with less than was asked; end every stop with a ready-to-paste resume prompt carrying the exact spec; wait on a human merge with `human.request` so one run carries the whole provisioning.
- **g. The `propose` scope (owner decision 2026-11-12: yes).** A new Glidepath scope class: an agent may add or change a Flight environment, its release step and the prod values, only in a pull request a person must merge. `Clearance / agent-scope` marks such a PR "needs a person" instead of failing it; it never auto-merges. `airframe.apply` opens the Flight-half PRs (`cicd.yaml` prod, the gitops prod `values.yaml`) instead of listing them. Secrets, signers, cloud deploy identity and the gates stay `human`: an agent still never edits a control that constrains it. Touches `tools/cicd_scope.py` and the contract (glidepath), Hangar's bundle (autopilot `policy/hangar/bundle.json`), the provenance verdict (clearance) and `airframe.apply`.
- **h. Core and gateway resilience.** The core finishes a ledger write on its own bounded context, so a cancelled request cannot drop the writer connection and lock (seen 16:01:57 UTC: one 306 ms write became a lock loss and three 503s); the gateway retries a decision once before `CORE-UNAVAILABLE`, with a decision timeout set for hangar-dev's disk.
- **i. Run-results check.** Flag a run that calls `airframe.plan` more than 3 times, or opens no PR after `apply` answered `ok`.
- **j. Tower re-run.** Re-run for any finished run (owner-gated), not only a failed one; a successful deploy whose result was undone had no way back from the UI.
- **k. Investigate.** Pipelines as Code's spurious "pipelinerun start failure" check (PATCH check-run 404; seen on boarding-api#63 and parachute#4, both green on retest), and `WatchCircuitOpen` "too many watch events" on `PythonApplication/parachute`.

**Gate.** The owner's original free-form parachute prompt, run on a fresh app, provisions dev and opens the prod PRs in one run, with the env vars and canary in both, at most 3 `airframe.plan` calls, and no manual file edits; every agent PR passes `Clearance / agent-identity` and `agent-scope` (or is marked "needs a person" for the Flight half).

## Work packages, G-ARGO: the Argo CD gate {#work-packages-g-argo}

Nine packages take the deployment gate from soft (a PaC check and grants in Postgres) to hard: a Config Management Plugin binds the rendered tree at generation, a ValidatingAdmissionPolicy admits only what a local ClearanceGrant covers, a PreSync hook shows the wait, and one agent on the protected cluster pulls grants, reports outcomes and files exceptions. The owner's decisions from 2026-10-31 hold: option A with the grant pulled, the gate replaces Hand-flown sign-off, `clearance.yaml` per gitops repo, `group:default/admins` as the outside group, 7-day holds. On Hangar the protected cluster is hangar-prod, whose tenant Applications live in the `argocd-apps` instance (Argo CD chart 10.3.2) and are generated by the `tenant-onboarding` ApplicationSet as multi-source apps (the airframe chart plus a `gitops-<app>` values source). Nothing of this exists today: no CMP, no hook, no grant object, no sync-time hook anywhere in apron or airframe. Every component here is Go (decided 2026-11-02; section 12, Languages).

### G-ARGO-1 · Design pass and spikes
<!-- pkg status=done wave=W2 -->

- **Repos.** clearance docs, hangar decisions.
- **Depends on.** R-1, R-6.
- **Build.** A `docs/gate.md` phase 2 section that settles, with a spike each: (a) a CMP on a multi-source tenant Application on Argo CD 3.5: the plugin source renders the airframe chart with the `$appsrc` values, or the plugin replaces the Helm source; (b) grant matching on the `clearance.hangar.io/rendered` annotation the CMP stamps (survives mutating admission) rather than normalized spec equality; (c) native ValidatingAdmissionPolicy with `paramKind: ClearanceGrant` and one binding per protected namespace via `paramRef` selector, versus a Kyverno ValidatingPolicy, measured for CEL cost against a 200-object grant and for failure modes on hangar-prod, where the Kyverno admission controller has been crash-looping under load; (d) the outcome source: the agent watching Application `status` versus Argo CD Notifications webhooks; (e) how the CMP on hangar-prod reaches the core on hangar-dev (the Tower foreign-workload path through the route). Output: decisions D21 to D24 in hangar/docs/autopilot/decisions.md.
- **Done when.** Each spike has a recorded result on a scratch namespace of hangar-prod in Warn mode; the design section names the chosen shapes.

### G-ARGO-2 · ClearanceGrant and the admission policy
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (`providers/argocd/crd`), apron, gitops-hangar-prod.
- **Depends on.** G-ARGO-1, C-1.
- **Build.** CRD `clearancegrants.clearance.hangar.io/v1` (namespaced in the protected namespace): `spec.subject` (commit, tree root), `spec.objects[] {kind, name, rendered, changed}`, `spec.expiresAt`, `spec.clearance` (id, tier, policy ref), `spec.signature`; `status.valid`. `ValidatingAdmissionPolicy clearance-protected-writes`: namespaceSelector `clearance.hangar.io/protected=true`, matchConditions guarded with `has()` and matching only argocd-apps' application-controller service account, validation that the object's grant annotation names a valid, unexpired grant listing this object with this rendered hash; a `ValidatingAdmissionPolicyBinding` per protected namespace with `paramRef` by selector; `auditAnnotations` naming the grant checked. A second policy, `clearance-grant-writer`, lets only the agent's service account write grants. Apron: `templates/56-clearance-gate/` under `zone == 'upper' and clearance.gate.enabled`, with a Warn to Deny toggle `clearance.gate.enforce` modelled on `admission.flight`.
- **Done when.** envtest covers admit, refuse (unlisted object, hash mismatch, expired grant, other writer), and the has()-guard cases; the rendered prod repo diff touches only the new files; applied in Warn mode on a scratch namespace of hangar-prod first.

### G-ARGO-3 · The Argo CD agent: grant sync, outcomes, exceptions
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (`providers/argocd/agent`, its own image and chart entry).
- **Depends on.** G-ARGO-2, C-10, R-1.
- **Build.** One controller on the protected cluster with three loops. Grant sync: every 30 s read the signed grant feed from clearance-api as its own identity (the hangar-prod foreign-workload path, read-only), verify each signature against the core's public key, create, update and remove ClearanceGrant objects, expire them. Outcomes: watch Applications in the protected projects and post `deploy.outcome` to the core (`POST /v1/records`) with sync phase, observed revision, health and the applied tree digest read from the stamped annotations; this is what C-2 signs. Exceptions: compare objects in protected namespaces against grants on an interval and post `deploy.exception` for objects with no grant annotation, a hash no grant lists, or a sync refused by the policy (read from the Application's operation state); honour a break-glass marker. Provider identity `argocd-agent/<version>` on every record. Fail closed: with clearance-api unreachable, grants stop updating and nothing running is touched.
- **Done when.** Conformance passes against a fake Argo; on hangar-prod a cleared change produces a grant within 30 s and an outcome record after the sync; a `kubectl apply` into a protected namespace appears as an exception within the interval.

### G-ARGO-4 · The Config Management Plugin
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (`providers/argocd/cmp`), apron.
- **Depends on.** G-ARGO-1, C-1, C-6.
- **Build.** A sidecar plugin for `argocd-apps`' repo-server (`plugin.yaml`, image): `generate` runs the customer's helm or kustomize render (on Hangar the airframe chart with the `$appsrc` values), canonicalizes every object (sorted keys, no server-populated fields), hashes each object and the sorted list into the tree root, looks the digest up in a local cache, and otherwise registers the change with the core (`POST /v1/clearances` as a verifier; the registering identity on hangar-prod is the repo-server's foreign-workload token). Three outcomes: cleared by policy, emit the manifests with `clearance.hangar.io/grant` and `clearance.hangar.io/rendered` stamped on every object; held for people, emit the manifests plus an injected PreSync Job carrying the clearance id; denied tier 3 or an outage hold, exit non-zero so the Application shows ComparisonError and nothing syncs. Opt-in by `spec.source.plugin.name: clearance`, set by the `tenant-onboarding` ApplicationSet template under `#@if clearance.gate.enabled`. On Hangar the CMP's change registration is the same object shape the `clearance-gate` task posts.
- **Done when.** Unit tests with recorded renders; a render of gate-api prod through the CMP equals the Tekton `clearance-gate` render for the same head (G-ARGO-8); on hangar-prod a tier 1 change syncs with annotations and a tier 3 denial shows ComparisonError.

### G-ARGO-5 · The PreSync wait
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (`providers/argocd/wait`, a tiny image).
- **Depends on.** G-TF-2's `wait` route (shared), G-ARGO-4.
- **Build.** The injected Job polls `GET /v1/clearances/{id}/wait` and exits 0 on clear, non-zero on deny or timeout, so the sync reads "PreSync: clearance awaiting approval" in Argo's UI and history. Documented as skippable with `--strategy apply`, which still meets admission.
- **Done when.** A held change shows the wait in the Argo UI on hangar-prod and proceeds when cleared in Tower; a sync with `--strategy apply` is still refused at admission.

### G-ARGO-6 · Outcome to attestation, and the release-record join
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance, glidepath.
- **Depends on.** G-ARGO-3, C-2.
- **Build.** A `deploy.outcome` triggers the signer; `GET /v1/clearances/{id}` shows outcome, attestation reference and Rekor index; Glidepath's `clearance-gate` task writes `clearanceId` and `treeDigest` into the release-tracking ConfigMap and the release log, and `GET /v1/apps/{app}/releases/{chainId}` returns them, so Tower and the packet can join a release to its clearance without guessing.
- **Done when.** A real hangar-prod release shows the joined chain: PR, change, grant, outcome, attestation, release record.

### G-ARGO-7 · Lab rollout on hangar-prod and the exit tests
<!-- pkg status=in-progress wave=W4 -->

- **Repos.** apron, gitops-hangar-prod, hangar docs.
- **Depends on.** G-ARGO-2 to 5.
- **Build.** The prod profile gains `clearance.gate: {enabled, enforce}`; the CMP sidecar is added to the `argocd-apps` Helm values; the agent, CRD and policy render under `56-clearance-gate/`; gate-api prod opts in first, then every app with `production: true`. Rollout: Warn for a week of real releases, then Deny. Self-gating: Clearance's own releases to hangar-prod run through the gate.
- **Done when.** The roadmap's phase 1 exit tests, run live and quoted: an agent PR to hangar-prod is held, cleared by a human, and syncs; the same change to hangar-dev auto-clears in under one second; a force-push after approval is refused at admission; a sync with `--strategy apply` that skips the hook is still refused; a ConfigMap-only change is tiered by its rendered diff and clears with the image digest unchanged; a direct `kubectl apply` to prod appears as an exception within the scan interval; with the core stopped a dev change proceeds and a secret rotation holds, both recorded on recovery.
- **User steps.** Merge the prod gitops PRs; perform the `kubectl apply` and the force-push tests on prod; accept the Warn-to-Deny flip.

### G-ARGO-8 · Glidepath integration
<!-- pkg status=built wave=W4 -->

- **Repos.** glidepath, backstage (Tower stops posting `hangar/release-signoff`), apron.
- **Depends on.** G-ARGO-4 for the parity test; otherwise independent.
- **Build.** `clearance-gate` becomes `required: true` once every gitops repo carries the check file (a resync), and Tower's `hangar/release-signoff` status retires; the task's render is parity-tested against the CMP's for the same head, and if they ever differ the CMP is the registrar and the check only reads; the check reads the catalog's `pipelinesAsCode.applicationName` and legacy names, never a hardcoded prefix; the fan-in and promote wait on the gate; `agent-gates-` retirement follows C-7.
- **Done when.** A release PR with a held change cannot promote; the sign-off status no longer appears; the parity test is green in catalog CI.
- **User steps.** Rulesets on gitops repos, where the plan allows them.

### G-ARGO-9 · Conformance, identity, docs
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar.
- **Depends on.** G-ARGO-3, G-ARGO-4.
- **Build.** Both components pass the conformance harness and name themselves in records; the Clearance Architecture rows for CMP, controller, reconciler and the PreSync hook move to Built; the glossary's ClearanceGrant entry matches the CRD; the business rules gain the gate's rules with stable ids.
- **Done when.** Conformance green in CI; docs merged.

### G-ARGO-10 · Protect any Argo CD app, on any instance
<!-- pkg status=in-progress -->

Added 2026-11-12 (owner). Today the gate protects one Application (`gate-api-prod`) on the apps instance, and turning it on means rewriting the Application's source to the plugin, labelling the namespace and listing the environment in the core. The platform instance (`argocd`, 37 Applications from the cluster repo) has no gate: its writes are only observed, and they show as out-of-band because attribution knows only the apps instance's grants. This package makes protection a two-step choice: install the plugin on an Argo CD instance once, then protect an Application with one annotation. Admission stays a native ValidatingAdmissionPolicy.

- **Repos.** clearance (plugin, agent, core, observe-k8s rules), apron, gitops-hangar-prod, gitops-hangar-dev, hangar docs.
- **Model.** Sonnet subagents, one per lettered step; the managing agent runs the live checks and the load test.
- **Depends on.** G-ARGO-2 to G-ARGO-9 (the gate as built), O-3 (the collector).
- **Build.**
  1. **G-ARGO-10a `platform-gitops` attribution (observe-k8s).** A write by an Argo CD instance's application-controller to an object whose Argo CD tracking annotation names an Application is attributed to that Application and its sync revision, not out-of-band. A write by that controller to an object with no tracking annotation stays out-of-band. The rule set names the platform instance's identity exactly.
  2. **G-ARGO-10b A generic renderer in the plugin.** Render what the Application already uses: Helm from a repo or OCI with value files, inline values and multi-source `$ref` values; Kustomize; a plain directory. A parity suite proves that the plugin's objects equal Argo CD's own render, object by object and hash by hash, across every Application on both clusters.
  3. **G-ARGO-10c Annotation opt-in.** `clearance.hangar.io/protect: "true"` on an Application. The argocd-agent switches only annotated Applications to the plugin, with an `ignoreDifferences` entry so the app-of-apps does not fight it; unannotated Applications never touch the plugin. The agent builds one merged grant per namespace from every protected Application's cleared objects that target it, keyed by group, kind, name and rendered hash, and reports two Applications claiming one object as an exception, keeping the last good grant. It labels a namespace protected from the cleared trees' destinations, only after that namespace's grant exists, removes the label when nothing protected targets it, and tells the core which app/environment pairs are protected, so nobody edits `CLEARANCE_PROTECTED_ENVIRONMENTS` by hand.
  4. **G-ARGO-10d Several Argo CD instances.** A policy binding per instance that matches that instance's controller, and an agent watching each instance (or one agent for several Argo CD namespaces).
  5. **G-ARGO-10e Load and stress test.** Measure the gate's cost before it covers the platform. With and without the plugin, on hangar-prod's repo-server and a synthetic set of Applications: generate time p50, p95 and p99 per Application; repo-server CPU, memory and queue depth during a commit that refreshes all 37 platform Applications at once and at 2x, 5x and 10x that count; the core's registration latency across clusters and its records per second; admission latency per write; grant size against object count, toward the \~1.5 MB object limit; the agent's grant-sync time with 1, 10 and 50 protected Applications; and behaviour under faults (the core unreachable, the core slow at 1 s and 5 s, a burst of refreshes). The results, the limits found and the settings chosen (repo-server replicas, `--parallelismlimit`, cache TTLs) go into the gate's docs and this card. Targets are set before step f.
  6. **G-ARGO-10f The platform instance, record only.** Install the plugin on `argocd`; annotated Applications register and get a tier, nothing holds, and admission runs in Warn.
  7. **G-ARGO-10g Protect chosen platform Applications.** Annotate the critical ones (RBAC, CRDs, Argo CD itself, ESO, CNPG). Clearance's own Applications stay unannotated so Clearance can always be repaired; break-glass covers emergencies.
  8. **G-ARGO-10h Cluster-scoped objects.** A cluster-scoped grant and a second, narrowly matched policy for CRDs, ClusterRoles and webhook configurations, in Warn for longer than the namespaced policy.
- **Done when.** An Application on either instance is protected by its annotation alone, with no source edit in git. A multi-namespace platform Application and two Applications sharing `kube-system` both sync through merged grants with no refusal in Warn. The parity suite passes for every Application. The load test's report is in the docs with its numbers and limits. Platform writes from tracked Applications no longer appear as out-of-band.
- **Owner steps.** Choose the platform Applications to annotate. Flip each instance's policy, and later the cluster-scoped policy, from Warn to Deny after a week in Warn.

## Work packages, G-TF: the Terraform gate {#work-packages-g-tf}

The Terraform gate ships beside the Argo CD gate. It binds a clearance to the saved plan, holds between plan and apply through a CI step, and detects applies that went around it rather than claiming to prevent them. Seven packages. The lab reference is the `network/lab` workspace in jfillman/hangar-infra (S3 backend `<lab state bucket>`, key `network/lab/terraform.tfstate`), which has no CI today. Nothing in Glidepath, Autopilot or Clearance mentions Terraform yet, so every seam below is new.

### G-TF-1 · The terraform-plan subject in the core
<!-- pkg status=live wave=W2 -->

- **Repos.** clearance.
- **Depends on.** R-1 (core API), R-6 (evidence schema v1).
- **Build.** `gate.py` gains a second subject kind beside the Kubernetes object diff: `ChangeRequest.subject = {kind: terraform-plan, planDigest, planJsonDigest, workspace: {backend, key, name}, versions: {terraform, providers}, summary: {create, update, replace, destroy, destroyedAddresses}, targeted, variableSetDigest}`. A Terraform baseline in `GatePolicy`: destroy or replace in a protected workspace is tier 3; a change to IAM, security-group, network-ACL, KMS or database resource types is tier 3; `-target` or `-replace` escalates one tier with a floor of 2; tag-only or description-only is tier 1; everything else is tier 2. `clearance.yaml` gains a `workspaces:` block, tighten-only like the gitops one. `classify()` names the resource addresses that set the tier. Secret variable values are never stored: the record carries the redacted plan JSON digest and the variable-set hash. Schema `schemas/change-request.schema.json` and the contract are regenerated.
- **Done when.** Unit tests cover the tier table, including the negatives: a destroy in a protected workspace never clears by policy, and a looser `clearance.yaml` is `DG-POLICY`. `POST /v1/clearances` accepts a terraform-plan change from a verifier and from a GitHub Actions OIDC principal, with `DG-REPO` still enforced. clearance-api lists it with `subject.kind`.
- **Rollout.** Clearance release only.
- **User steps.** None.

### G-TF-2 · Hold, release and outcome on the core API
<!-- pkg status=live wave=W2 -->

- **Repos.** clearance.
- **Depends on.** G-TF-1, C-1 (clearance token).
- **Build.** `GET /v1/clearances/{id}/wait?timeout=` long-polls up to 60 s and returns the state. `POST /v1/clearances/{id}/outcome` (the registering principal) carries the apply result: `{applied, planDigest, changes from the apply JSON log, startedAt, finishedAt, error}`; it writes `deploy.outcome` with `matched = planDigest == cleared digest`, and a mismatch also writes `deploy.exception`. A cleared change returns its clearance token bound to the plan digest. The hold TTL for this subject kind defaults to 24 hours, because plans go stale; the 7-day TTL stays for gitops changes. Registration is idempotent by repo, workspace and plan digest.
- **Done when.** State-machine tests pass; a second outcome for the same change is `DG-STATE`; evidence rows show a matched and a mismatched outcome; an expired hold is `deploy.expire`.
- **Rollout.** Clearance release.
- **User steps.** None.

### G-TF-3 · The plain-CI adapter: `clearance hold`, `release`, `report`
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (`terraform.py` beside `register.py`, subcommands on the `clearance` console script, `terraform/action.yml`).
- **Depends on.** G-TF-2.
- **Build.** `clearance hold --plan tfplan [--json plan.json] [--workspace name] [--binary terraform|tofu]` runs `terraform show -json` locally, computes the digests, registers the change and waits (exit 0 cleared, 3 holding with `--no-wait`, 1 denied, 2 usage). It never uploads the plan. `clearance release --plan tfplan --clearance <id>` re-hashes the plan, checks it equals the cleared digest, and exits 0; the workflow's apply step runs only after it, and the CLI itself never applies. `clearance report --apply-log apply.jsonl --clearance <id>` posts the outcome. Identity is the workflow's GitHub Actions OIDC token as in `register`, or `--token-file`. A composite action `jfillman/clearance/terraform@<ref>` with `step: hold|release|report`. Docs: a new `docs/terraform-gate.md` and a README row.
- **Done when.** Unit tests run against a recorded plan fixture for both terraform and tofu; a plan Terraform refuses to apply because state moved produces `deploy.exception`, not a silent re-plan; an apply with a different digest reports a mismatch.
- **Rollout.** Clearance release; the action ref is the tag.
- **User steps.** None.

### G-TF-4 · Lab reference: hangar-infra applies through the gate
<!-- pkg status=verified wave=W3 -->

- **Repos.** hangar-infra (new `.github/workflows/terraform.yaml`, `clearance.yaml`), apron and gitops-hangar-dev (`autopilot.githubWorkflows` gains `repo:jfillman/hangar-infra:*`), clearance docs.
- **Depends on.** G-TF-3; the existing GitHub Actions to AWS federation used by the keyless deployers; the Cloudflare tunnel path list, which already forwards `POST /v1/clearances`.
- **Build.** On a pull request: plan and comment. On merge: `terraform plan -out`, `clearance hold`, then `terraform apply tfplan` behind `clearance release`, then `clearance report` from `apply -json`. Apply credentials exist only on the gated job, through a GitHub environment that also lists the Clearance App as a deployment protection rule, so both enforcement paths are exercised. `clearance.yaml` declares `network/lab` protected.
- **Done when.** The roadmap's phase 2 milestone row: a tag-only change clears by policy and applies; a subnet destroy holds for two people, is cleared in Tower, applies, and `deploy.outcome` shows `matched: true`; a re-plan after state moved is held and recorded as an exception; the packet lists the workspace's applies.
- **Rollout.** hangar-infra PR, apron render, gitops PR.
- **User steps.** Create or reuse the IAM role the workflow assumes, run any `terraform apply` the agent is blocked from, clear the held change in Tower. Auto mode blocks the agent from applying against AWS and from creating IAM roles.

### G-TF-5 · Exception detection: drift and applies around the gate
<!-- pkg status=built wave=W3 -->

- **Repos.** clearance (a small `terraform-watch` provider controller with its own chart), apron (catalog entry).
- **Depends on.** G-TF-2.
- **Build.** Two detectors. A scheduled `terraform plan -detailed-exitcode` against each protected workspace: an unexpected diff is `deploy.exception kind=drift` with the addresses, and the period's coverage state becomes observed-not-attributed. A state-backend watch for S3 backends: object versions of the state key and CloudTrail `PutObject` events; a state version with no `deploy.outcome` inside the window is `deploy.exception kind=untraced-apply` naming the CloudTrail principal. Read-only IAM: `s3:ListBucketVersions`, `s3:GetObjectVersion` on the key, `cloudtrail:LookupEvents`.
- **Done when.** A laptop `terraform apply` by the user appears as an exception within the interval; a gated apply does not; drift seeded by hand is reported once, not every tick.
- **Rollout.** Clearance release, apron render.
- **User steps.** Run the laptop apply, create the read-only role.

### G-TF-6 · HCP Terraform run-task adapter, behind a flag
<!-- pkg status=unverified wave=W4 -->

- **Repos.** clearance.
- **Depends on.** G-TF-2.
- **Build.** `POST /v1/terraform/run-task`: verify HCP's `x-tfc-task-signature` HMAC, fetch the plan JSON from `plan_json_api_url` with the run's access token, compute the subject, register, answer the callback `running`, then `passed` or `failed` when the change clears or is denied. Per-installation HMAC key from a secret. Off unless configured.
- **Done when.** Contract tests against recorded HCP payloads pass. Live verification needs an HCP organization and waits for a design partner who runs one. Atlantis and Spacelift adapters are documented as deferred.
- **User steps.** An HCP organization, when a partner names it.

### G-TF-7 · Conformance, provider identity and docs
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar.
- **Depends on.** R-1 (conformance harness), G-TF-3.
- **Build.** The Terraform provider passes the conformance test (fake workspace: hold, clear, release, outcome whose digest matches the cleared subject). Every record names `provider: {name: terraform-ci, version}`. The packet (C-5) renders terraform-plan subjects. The Clearance Architecture status row for the Terraform provider moves to Built; hangar/docs/autopilot/decisions.md records the custody decision below.
- **Done when.** Conformance is green in CI and the docs are merged.

### Decisions this track recommends

- **Plan custody.** The plan stays in the runner's workspace; Clearance holds digests only, so no infrastructure plan enters the tenant boundary. The release step re-hashes before apply. The architecture lists this as open; this is the recommendation.
- **Hold TTL.** 24 hours for terraform-plan, configurable per workspace.
- **OpenTofu.** The same CLI with `--binary tofu`, covered by fixtures in G-TF-3.
- **The meter.** Whether a workspace counts as a governed scope is commercial and out of scope here.

## Sequencing {#sequencing}

The refactor goes first because every gate writes through the core it produces, and the ledger goes last because it needs real outcomes to anchor. Seven tracks run in parallel once the split is live; five gates mark when the managing agent may start the next wave. The diagram below predates the 2026-11-07 revision and shows the first four waves; W5 Observation and W6 Clearinghouse follow W4 in the table.

> Diagram: Build order · 5 tracks, 4 waves after the foundation, 3 gates. See the original document.

Shaded cells hold work; a wave's gate is passed only with the live evidence named in its packages. The Terraform and Argo CD tracks share the core's provider protocol, token and `wait` route, so neither starts its runner-facing packages before W2's cores exist.

### Waves and their entry conditions

| Wave | Packages | Starts when | Gate at the end |
| --- | --- | --- | --- |
| W0 Foundation | R-1, R-6, R-8 | Now. All three are code and docs only; R-1 and R-8 may run as parallel subagents, R-6 after R-1's record routes exist | Core API contract generated; evidence v1 schema published; docs match the tags |
| W1 Split | R-2, R-3, R-5, R-7, then R-4 | W0 done | **Installs alone**: the chart's install test passes on a bare kind cluster, and R-4's live checks pass on hangar-dev with the chain unbroken |
| W2 Gate cores | C-1, C-6, C-8, C-9, C-10; G-ARGO-1; G-TF-1, G-TF-2; A-1, A-4, A-5, A-7 | W1 gate passed | Signed tokens issued; the grant feed served; both subject kinds registered; the Argo design pass recorded with spike results |
| W3 Hard gates | G-ARGO-2 to 6; G-TF-3, 4, 5; C-2a, C-2, C-7 | W2 done; C-2a's design is decided and its key ceremony (user) can run any time before | **Hard gate on prod**: G-ARGO-7's exit tests, plus a Terraform plan cleared, applied and matched (G-TF-4) |
| W4 Ledger | C-3, C-4, C-5; O-1 and C-14 first, before C-5; I-1; G-ARGO-7, 8, 9; G-TF-6, 7; A-2, A-3, A-6, A-9; R-9 alongside | W3 gate passed (G-ARGO-7's exit tests and the Terraform lab run are the owner steps still open at the 2026-11-07 revision) | **Packet verifies**: a 30-day lab packet verifies offline against witnessed checkpoints, both providers pass conformance, and the packet's coverage statement carries the six coverage states and the health summary (blind where no collector exists yet) **Closed by the owner 2026-11-09**, on an 11-day packet. 30-day re-run due 2026-12-09; see the W4 build report. |
| W5 Observation | O-2, O-3, O-4, O-5; A-10 alongside (not part of this gate) | W4 gate passed; O-3 also needs G-ARGO-7's gate live on hangar-prod | **Coverage is verified, not assumed**: a `kubectl apply` and a console security-group change appear in the packet's exceptions with actor, diff and resolution; a Secret change appears with no value recorded; a `StopLogging` call appears as a monitoring-protection event and flips the account's health; with a collector stopped the packet reports a blind window, not a clean one; the reconciler and the collector report one exception, not two |
| W6 Clearinghouse | P-1, P-2, P-3, P-4 | W5 gate passed (P-1 and P-4 may start after W4, since they need only the packet). Status 2026-11-14: all four packages merged to clearance main (clearance#169, #170, #171, #172), proven against fakes, not released or deployed | **Accepted and verifiable by a stranger**: a fake assurance provider pulls a packet under a time-boxed credential and signs a receipt that the next packet carries; a 25-record sample verifies offline; a verification statement verifies on the hosted page (the lab run proves it against fakes: a fake assurance provider, offline sample verify, a fake GRC API; the hosted proof on verify.clearance.hangarplatform.dev is the Cloud K2 gate) with all seven checks (the lab run accepts a statement that prints "not yet independently witnessed"; the external witness is deferred to before the Cloud K2 gate, where all seven checks green is proven), shows revoked when revoked, and prints a blind window when there was one; a change appears as an evidence item in a Vanta sandbox with a link back |
| Later | O-6, P-5, I-2, I-3, A-8, C-11, C-12, C-13, section 13 | A paying partner, a second accepting firm, ten opted-in tenants, or the roadmap's phase 4 and 5 triggers |  |

### Parallel tracks and who runs what

- **Track 1, refactor and core** (R, C): one subagent per package; R-2 and R-3 can overlap once R-1 is merged, since R-3 tests against clearance core --memory first; R-4 and R-7 are the managing agent's own cutover, run step by step with the release chain in section 1.
- **Track 2, Argo CD gate** (G-ARGO): one subagent for the design spikes, then separate subagents for the CRD and policy, the agent and the CMP; the lab rollout is the managing agent's.
- **Track 3, Terraform gate** (G-TF): independent of track 2 after W2; G-TF-3 is a good first package for a fresh subagent because it is one repo and pure code.
- **Track 4, Autopilot** (A): A-1, A-4, A-5 and A-7 are independent of each other; A-2 starts with the Dex evaluation; A-9 follows R-4; A-3 waits for signed agent commits (C-2a).
- **Track 5, evidence** (C-2 to C-5): sequential, each needs the previous one's output; C-3's witness is the one piece on hangar-prod.

* **Track 6, observation** (O): O-1 is one subagent in W4 beside the ledger work; O-2 is pure code and a good first package for a fresh subagent; O-3 and O-4 are separate subagents with the lab rollouts the managing agent's; O-4 absorbs G-TF-5's detector and must not duplicate it.
* **Track 7, clearinghouse** (P): sequential after the packet; P-3 is the one with a public surface and gets the security-review pass of section 12 before its route is rendered; P-4 can run as soon as C-5 exists and a Vanta sandbox is available.

### The critical path

R-1 to R-2 to R-3 and R-7 to R-4 (installs alone) to C-1 and C-10 to G-ARGO-2, 3, 4 to G-ARGO-7 (hard gate on prod) to C-2 to C-3 to C-4 and C-5, with O-1 and C-14 landing before C-5 (packet verifies), to O-2 and O-3 (coverage verified), to P-1 and P-3 (accepted and verifiable by a stranger). Everything else hangs off that line. The product roadmap's dates (gate exit tests 2026-12-23, lab packet 2027-01-29) assume one engineer; with subagents the constraint is the user's merge and decision cadence, which section 14 lists. The roadmap's phase 1 "out-of-band detection" bullet is met in its reconciler form by W3 and in its collector form by W5; its phase 2 exit gate (the console change and \`StopLogging\` tests) is W5's gate.

### What the managing agent does at each gate

1. Re-reads the packages of the next wave and re-checks their dependencies against what is merged and live, not against this document's expectations.
2. Runs the gate's live tests itself and records the evidence (sequence numbers, kubectl output, check-run links) in memory and in hangar/docs/autopilot/roadmap.md.
3. Hands the user one message: what passed, what was descoped, which PRs and decisions wait on them.

## Cross-cutting rules {#cross-cutting-rules}

These apply to every package and are copied into every subagent brief. They come from the standing guidance in this project's memory and from incidents in the sessions that built the current code.

### Versions and releases

- Clearance: semantic `vX.Y.Z` tags on main after green CI; a release workflow (R-8) publishes image, chart and notes. Autopilot: `gateway-v*`, `runtime-v*`, `runtime-<name>-v*` image tags; until R-3, pin Clearance by tag with `uv lock`; after R-3, pin Clearance's generated Python client by the same tag, and A-9 pins the Go client module. Airframe: human-cut `v0.3.N`, then apron `versions.yaml`. Apron and gitops: renders committed by SHA, diff-checked. Glidepath: bot image pins on merge.
- Never tag off a red main; never let an autopilot pin PR merge before the Clearance tag exists and CI has re-run (the #30 and #33 lessons).
- Re-read apron's current image line and autopilot's current pin before bumping; another session may have moved them.
- A stacked PR merged after its base closes lands on the base branch, not main: retarget stacked PRs to main as soon as the base merges.

### Repos and tools

- `git -C` and `gh --repo` on every call; `cd X && git ...` chains have run in the wrong worktree before. Re-check `git log -1` and `git status` in the intended worktree before opening a PR.
- gitsign repos (boarding-api, flight-api, gate-api and the other app repos) need the user to commit; leave the change staged in a named worktree and say so. gitops-backstage does not need gitsign (user, 2026-10-26).
- Never force-push, never `--no-gpg-sign`, never `git stash` on a shared checkout, never `rm -rf`. Remove only worktrees this session created.
- The auto-mode classifier refuses: merging PRs on repos without PR CI ("Merge Without Review"), creating public repos, minting tokens to files, running `terraform apply`, prod cluster mutations, the tunnel installer. Hand those to the user with the exact command.

### Languages

Each component's language is chosen for security and efficiency on its own path, decided 2026-11-02. Clearance and every gate component are Go. The Autopilot gateway moves in Python (R-3) and is then ported to Go (A-9). Agent runtimes and Crossplane functions stay Python, and the portal is TypeScript.

| Component | Language | Why |
| --- | --- | --- |
| Clearance core: decision service, token, recorder, ledger, clearance-api, GitHub App, deployment gate | Go | cel-go is the reference CEL implementation and the one Kubernetes runs for ValidatingAdmissionPolicy, so a rule means the same at decision time and at admission. Tessera, sigstore-go, in-toto-golang and DSSE are Go libraries. It ships as one static binary, the decide path has a 20 ms p99 budget, and glidepath-api is already Go |
| `clearance` CLI: verify, packet, trust-root, hold, release, report, conformance | Go, the same module | Auditors and CI runners get one static binary with no interpreter, and verify runs offline |
| Argo CD CMP, grant agent, PreSync hook | Go | client-go and controller-runtime, the same stack as Argo CD; small sidecar images |
| Terraform pieces: HCP run-task adapter, state and CloudTrail detection | Go | terraform-json and the HCP API client; the same binary as the CLI |
| Autopilot AI gateway | Python through R-3 and R-4, then Go (A-9) | The most exposed service: it holds model and GitHub credentials and serves every agent call over long-lived streams. The official Go MCP SDK and Go's streaming proxy fit; the move keeps Python as the reference to compare against |
| Agent runtimes (run pods) | Python | The Claude Agent SDK and LangGraph; the security boundary is the sandbox, NetworkPolicy and the gateway, not the runtime's language |
| Crossplane composition functions | Python | The user's choice; off the hot path, on function-sdk-python |
| Policy | CEL | Not general code: type-checked, non-Turing-complete and cost-bounded |
| Backstage plugins (deferred portal) | TypeScript | Backstage requires it |

Rust was weighed for the core for its stronger guarantees, but the libraries this work needs are Go-first, and Go is memory-safe at the boundary that matters here.

### Security and efficiency principles

Every package's done bar includes these; a reviewer rejects a PR that breaks one without a recorded reason.

- **Images.** Go services: static builds onto distroless `nonroot`, pinned by digest. Python images: slim bases pinned by digest. All run as uid 65532 with a read-only root, all capabilities dropped and seccomp RuntimeDefault. Each image ships with an SBOM and a keyless signature (Hangar's Fulcio after C-2a).
- **Dependencies.** As few as practical; `go.sum`, and `uv.lock` with hashes. CI runs `govulncheck` and `pip-audit` and fails on a reachable known vulnerability.
- **Untrusted input.** Every request body is size-capped and strictly decoded (unknown fields rejected) and schema-validated. Every server sets read-header, read, write and idle timeouts, and every outbound call has a deadline. Parsers of evaluation requests, DSSE envelopes, Terraform plan JSON, rendered trees and webhook payloads have Go fuzz targets in CI.
- **Fail closed.** Missing policy, an uncompilable rule, an unreachable core or an unverifiable signature means deny, except the one recorded switch in R-3's outage policy.
- **Crypto and secrets.** Only the standard library and Sigstore libraries, no custom crypto, constant-time comparison of tokens, keyless signing, no private key outside a Secret, and no secret in a log line.
- **Service identity.** Every service-to-service call carries an audience-bound projected service-account token, and NetworkPolicy is default-deny. No service shells out, and Python never uses unsafe YAML loading or pickle.
- **Efficiency budgets.** Rules compile once per bundle version. The decide path stays under 2 ms p99 in-process and 20 ms p99 end to end in-cluster, with the durable record write group-committed. The gateway adds under 5 ms p99 per tool call. Postgres goes through one pool per process with an index behind every clearance-api query. No proxy buffers a streamed body. `go test -bench` guards the decide path in CI and fails on a regression over 20 percent.

### Security guardrails

- No live write credential to a protected cluster from the control plane; grants are pulled (G-ARGO-3). Clearance's one Kubernetes write stays AgentRun on the control-plane cluster, plus the confined Argo lower sync.
- Two GitHub Apps stay separate: the App that writes agent PRs never attests them.
- Every new pod-matching ValidatingAdmissionPolicy or Kyverno policy: `has()`-guard every `matchConditions` expression, match the narrowest identity, test in Warn on a scratch namespace before Fail, and never leave `request.subResource` unguarded (the 2026-10-30 outage).
- NetworkPolicies are part of every deployment change: who may reach the core, the provider, Postgres.
- Never print a secret value, not even one named `password`; redact every field of a Secret or an Infisical read.
- Rulesets on private repos are not enforced on GitHub Free; detective controls (`bypass-check-`, release-log `bypass`) are the live control until the plan changes.

* **Observation (added 2026-11-07).** Secrets are observed at `Metadata` only, wherever they live; a collector or audit policy that would record a Secret body fails its build. Raw audit logs and observations stay in the customer's cloud and cluster; the ledger holds hashes, and the intelligence export carries verified fields and counts only, never approver subjects or diffs. Monitoring-protection operations are tier 3 observations whether or not they succeeded, and flip the scope's health. A clean exceptions list is never printed for a window without a healthy health record; a feed that stops produces a blind window.
* **Statements and approvals (added 2026-11-07).** A verification statement is immutable: a correction supersedes, a revocation verifies as revoked, and totals, every coverage state, exceptions and unreconciled counts can never be omitted; the scope is the subscriber's only choice and is printed. No page scores or ranks a subscriber. The two tier 3 approvers are distinct identity-provider subjects that can be people; a service identity, bot account or agent identity presented as an approver is refused, not counted.

### Live verification

- Verify against the cluster, not the docs: evidence sequence numbers from clearance-api, glidepath-api audit lines (`msg=audit`), `kubectl get` and server-side dry runs, check-run links. Quote them.
- A passing check whose gate is off is not evidence: confirm the flag or guardrail is on before counting a pass.
- Through the API server's services proxy the path carries the `/api/v1/namespaces/.../proxy` prefix; through a port-forward it does not. `https://*.hangar-dev.local` is a Traefik 404; use `http://`.
- Argo CD: an env-only or hook-only change may need a refresh annotation; `Synced` can be the old revision, check `status.sync.revision`; the API server drops an empty env value, so omit the entry.
- hangar-dev and hangar-prod are resource-constrained: expect PaC to drop webhooks under load (an empty-commit push re-fires them), Kyverno and the scheduler to restart, and slow Argo syncs. Downtime in the lab is never a reason to hold a merge.

### Docs and memory

- Docs move with code in the same PR; status words are Built, Draft, Proposal, Unverified.
- After each package: update hangar/docs/autopilot/roadmap.md and decisions.md where a decision was taken, the product's own docs, and the session memory with PR links and live evidence.
- Memory files from earlier sessions are background: verify a file, flag or endpoint still exists before relying on it.

## Deferred: portal and UI work {#deferred-portal-and-ui-work}

The portal follows the gateway and the gates. Read the UI design doc ("Autopilot and Clearance in Backstage: UI design", https://claude.ai/artifact/9f8jNFAyjcvVGcRGX5Z2oU) and the nine-board canvas (https://claude.ai/artifact/9yqroF5srM4U7htTeCkqUj) before any of it; the design's open questions were decided on 2026-10-31 and the write path uses the delegate model (Tower's backend as itself with `X-Hangar-On-Behalf-Of`), not token forwarding.

| Surface | State | Waits on |
| --- | --- | --- |
| Autopilot plugin: Runs (A1), Agent profile (A2), New agent (A3, read-only), runtime picker, drift chip | Built in backstage, Tower v0.118.0 | A-4 for cost columns; A-6 for Preflight results |
| Clearance plugin: Clearances (C1), Evidence (C2), Policy (C3), person controls, Clear and Deny | Built | G-ARGO for the gate panels and marks: attestation mark, exceptions tab, outcome on the change detail |
| Tower tabs: Services marks (T0), app Clearance tab (T1, activity and the needs-you callout), Agent tab (T2, read-only) | Built | T2 chat and answer-in-place need the Skyport session agents (A-8) |
| Packet download, freeze and incident reports | Not built | C-5 |
| Policy editor ("would this be allowed?" exists; editing `clearance.yaml` through a PR does not) | Not built | C-6, R-5 |
| Argo CD UI extension and proxy extension (clearance status and a clear button on the application page) | Not built | G-ARGO-7, the product roadmap's phase 4 |
| Slack approvals | Not built | C-11 |
| Trust page, vendor-risk verification link, auditor portal, acceptance receipts | Not built | P-1 (receipts), P-2 (sampling), P-3 (the statement and the hosted verify page), P-4 (GRC push), P-5 (the portal, later); C-3 and C-4 underneath |
| Write path remainder: replay a past event, Open agent PRs, launchers | Decided, partly built | A-5 for replay |

Rules that carry over: the Clearance plugin imports nothing from Tower or Hangar; a profile is a file in git, so create and edit end in a PR; proposal-only screens carry a chip; every write is evidence naming the person and the delegate.

## Open questions and risks {#open-questions-and-risks}

Each question names the package it blocks, the recommendation, and who decides. A managing agent proceeds on the recommendation where the row says so and stops where it says user.

| # | Question | Blocks | Recommendation | Decides |
| --- | --- | --- | --- | --- |
| 1 | Confirm the boundary: Autopilot owns the AI gateway (MCP surface, sessions, run tree, limits and budgets, dispatch, tool registry, model proxy, definitions, inbox, person controls, results); Clearance decides and records and owns the gates and the ledger. This amends D16 of 2026-10-28 | R-1, R-3, R-5 | Record it as a new decision in hangar/docs/autopilot/decisions.md and update design.md section 0.1's split table | Decided 2026-11-02: boundary confirmed, recommendation adopted (R-1 rollout records it) |
| 2 | What the gateway does when the decision service is unreachable | R-1, R-3 | Fail closed for T1 and above and for every session open and spawn; T0 reads fail closed too by default, with a per-deployment switch to allow reads and record them as `coverage-unavailable` on recovery, mirroring the deployment outage block | Decided 2026-11-02: recommendation accepted (built in R-3) |
| 3 | May Hangar's policy bundle read Glidepath's scope from glidepath-api's contract at startup instead of a vendored copy? | R-5 | Yes: same trust as every other call to the API, the contract version is recorded, and the three-repo ripple ends | Decided 2026-11-02: yes (built in R-5) |
| 4 | Token format | C-1 | DSSE envelope, with a JWT projection for the hook | Proceed on the recommendation |
| 5 | Grant-match admission: native ValidatingAdmissionPolicy or Kyverno ValidatingPolicy | G-ARGO-1, 2 | Native VAP: no Kyverno dependency for customers, no webhook, and hangar-prod's Kyverno controller is unstable under load; spike both | Proceed, confirm with the spike |
| 6 | Language for the Argo CD CMP and agent | G-ARGO-3, 4 | Go, in `providers/argocd/` of the clearance repo with their own images and chart entries; the core is Go as well (section 12, Languages); Crossplane functions stay Python by the user's choice | Decided 2026-11-02: Go, and the user asked for the best language everywhere (section 12) |
| 7 | ID-JAG issuer (D19) | A-2 | Evaluate a Dex build with dexidp/dex#4611 on people-dex's slot; Keycloak as the fallback | Decided 2026-11-02: recommendation accepted (A-2 starts with the Dex evaluation) |
| 8 | Hangar root CA for the platform Fulcio (D1) and the recorder's signing identity | C-2a, C-2, C-7 | Design now; it gates every signature in the ledger and the confirmed-agent provenance level | Decided 2026-11-02: design now; the design is under C-2 (C-2a design) |
| 9 | Witness for the lab ledger | C-3 | A witness Deployment on hangar-prod with its own key, run by the prod profile; a second external witness before any customer record | Proceed |
| 10 | Plan-file custody for the Terraform gate | G-TF-3 | The runner keeps the plan; Clearance holds digests only | Proceed |
| 11 | Which Terraform runner adapter to build after plain CI | G-TF-6 | HCP run task, behind a flag, verified when a partner names it | Wait for a partner |
| 12 | Event durability | A-5, G-ARGO-3 | Gateway-side cursor and reconciliation now; ADR-0030 AMQP stays deferred (user, 2026-11-01) | Proceed |
| 13 | Where people-dex lives after the component split | R-7 | Its own identity group in apron, because the gateway signs people in for agents and Clearance resolves approvers through the same issuer | Proceed |
| 14 | Replace `agent-gates-` with the App | C-7 | Already decided (2026-11-01): after ten real agent PRs agree | User confirms the parity |
| 15 | The meter and whether a Terraform workspace is a governed scope | none | Commercial; out of scope here | User |
| 16 | Cloud onboarding mechanism for the AWS collector: a cross-account role, StackSets, or a Marketplace-managed deployment | O-4 | A cross-account role for the lab; decide the product mechanism with the first AWS partner, because it decides whether cloud observation is a product or a set of custom integrations | Open; user with the first partner |
| 17 | Rule language for detection | O-2 | CEL, so the gate's policy, the ValidatingAdmissionPolicy and the observation pipeline share one language; OPA through the existing delegation | Decided 2026-11-07 (Architecture ch. 16) |
| 18 | Observation health as a first-class record, and the build order of the collectors | O-1, O-3, O-4 | Health is a record per scope and source, checked from live configuration; Kubernetes first, AWS second beside the Terraform provider, Azure and Google Cloud as adapters on a trigger | Decided 2026-11-07 |
| 19 | Secrets in the audit policy | O-3 | Metadata only, wherever they live; the record needs that a Secret changed, which one, who and when, never the value | Decided 2026-11-07 |
| 20 | Approver independence extends to automation | C-14, P-3 | The two tier 3 approvers are distinct identity-provider subjects that can be people; a service identity, bot or agent identity is refused | Decided 2026-11-07 (Architecture ch. 04) |
| 21 | Verification statement: format published with the verifier; immutable with supersession and revocation; the insurer statement a profile of it, never a separate artifact; no page scores or ranks | P-3 | As stated; a reviewer or a trust-center platform must verify without Clearance | Decided 2026-11-07 (Architecture ch. 16) |
| 22 | Intelligence export as a pipeline separate from the ledger; the operational change class as versioned data; cell thresholds, give-to-get and a neutrality charter | I-1, I-2 | The first two are decided; the thresholds (20 tenants, 2,000 changes, 25 percent dominance, no interactive queries), give-to-get and the charter are proposals and commercial, settled before I-2 starts | Pipeline and class decided 2026-11-07; the rest user, before I-2 |
| 23 | Whether the reconciler (G-ARGO-3, G-TF-5) and the collectors (O-3, O-4) are one provider identity or two in the record | O-3, O-4 | Two providers, one change transaction: the collector is the primary source and the reconciler's finding is correlated into the same transaction as corroboration, so the packet never shows one change twice | Proceed on the recommendation |

### Risks the managing agent watches

- **Every agent call now crosses the network to the decision service.** The gateway's latency and availability depend on the core. Mitigation: core and gateway in one namespace, a decision budget measured on hangar-dev before the cutover (target p99 under 20 ms in-cluster), the outage policy from question 2, and a load test with the Skyport agents' call rates.

* **The cutover (R-4) breaks the evidence chain or the lab's live integrations.** Mitigation: the install test and a rehearsal on a scratch namespace first; cut over with both gateway images present; verify the sequence continues before deleting the old Deployment.
* **CMP parity with the Tekton render fails on multi-source apps.** Mitigation: the G-ARGO-1 spike; the fallback makes the CMP the registrar and the check a reader.
* **A fail-closed admission policy refuses more than intended on hangar-prod.** Mitigation: Warn first, `has()` guards, narrow match, a week of real releases before Deny, and the toggle to Audit kept.
* **hangar-prod load.** The laptop host already crash-loops Kyverno and starves Argo; a new sidecar, agent and policy add load. Mitigation: resource requests sized from measurements on hangar-dev; the agent's interval configurable.
* **The user's merge and decision cadence is the real schedule.** Clearance and Backstage PRs, gitsign commits, GitHub App settings, IAM roles and the Terraform applies all wait on one person. Mitigation: batch hand-offs per wave; keep every PR independently mergeable.
* **Stale local checkouts.** Subagents must branch from origin/main and read templates from origin/main, as section 1 requires.
* **Two products, one lab.** Clearance's own releases to hangar-prod go through the gate (self-gating); a broken gate blocks Clearance's own fix. Mitigation: break-glass (C-6) is a recorded path, built before Deny is turned on.

- **The Go port of the core changes a decision.** cel-python and cel-go differ at the edges (integer overflow, string functions, timestamps). R-1's golden corpus must replay with identical results before the core ships, and every rule fixed for it is listed.
- **The Go core breaks the live evidence chain.** The chain hash depends on exact JSON canonicalization. R-1b reproduces it byte for byte, and `chain verify` over the live hangar-dev chain is part of R-1's done bar.

* **Collector volume on hangar-prod (added 2026-11-07).** An unfiltered API-server audit log is tens of millions of events a day, and the laptop host already starves Argo. Mitigation: the audit policy template drops reads and control-plane loops before anything leaves the API server; the webhook batches into a queue; the collector's resource requests are measured on hangar-dev first; `clearance.observe.enabled` is a separate toggle from the gate.
* **The hosted verify page is a public surface (added 2026-11-07).** It is the first Clearance route reachable without an identity. Mitigation: a separate route with a rate limit, server-rendered with no JavaScript required, the statement id unguessable, the page reads only published statements and proofs, and the section 12 fuzz targets cover its inputs; the recipient detail level is never on the public route (the open route serves the public summary only; recipient detail, statement level V2, is behind sign-in). The production verify hostname is never rendered from the Hangar lab (apron); the lab tests on a lab host.
* **The same change counted twice (added 2026-11-07).** The reconciler and a collector can both see one `kubectl apply`. Mitigation: section 14 #23; O-3's done bar requires one exception, not two.

## Work packages, O-series: observation {#work-packages-o}

Six packages build the half of Clearance that makes the coverage statement complete, as the Architecture's chapter 09 defines it (added 2026-11-07; the [Clearinghouse companion](https://claude.ai/artifact/3rPgELsmjQJ5rqsz386D9Q) has the reasoning and the per-cloud detail). The gate proves a cleared change is the deployed change; observation proves what else was deployed, from sources the gate cannot influence, and prints a blind window rather than a clean one when it could not see. W3 shipped the reconciler form of detection (G-ARGO-3's exception loop, G-TF-5's drift and state-bucket detectors); these packages add the audit-log collectors, the shared pipeline and the health record on top of it, and the reconciler stays as the backstop. Everything here is Go in the clearance repo, under `internal/observe` for the core and `providers/observe-<source>/` for each collector with its own image and chart entry. Rules are CEL (decided 2026-11-07); OPA only through the existing policy delegation. The build order is Kubernetes, then AWS; Azure and Google Cloud only when a partner runs production there.

### O-1 · Observation schema, coverage states and the health record
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** R-6 (evidence v1), C-6 (exception kinds). Early in W4, before C-5 freezes the packet.
- **Build.** `clearance.evidence/v1.1`, additive: coverage states gain `break-glass` and `attempted-refused` (the architecture's six); every record's Integrity group gains an `integrity` sub-field for observation records that splits source integrity (`sourceVerified`: the delivered log files verified unaltered, for example by CloudTrail's digest chain) from completeness (`completenessClaimed`, supported by the health record). Three new record kinds: `observation` (the normalized event: provider, source, scope, resource, actor split into verified subject, chain, issuer, self-reported client and attributes; action with verb, api, succeeded and refused reason; change before and after where a state service has it; correlation with grant, plan, task\_id, run\_id and operation\_id; integrity; requested, observed and delivered times), `assessment` (coverage state, tier, rule-set version, the attribution signal that decided it), and `resolution` (reverted, ratified, declared break-glass, still live; with a cause on a revert: `agent-caused`, `policy-triggered`, `human-initiated`, `automated-remediation`, `requirement-changed`, `external-dependency`, `unattributed`). A fourth kind, `observation.health`, per scope and source per check: `healthy`, `degraded` or `blind`, with the checks that produced it (audit policy present and webhook delivering; trail enabled, regions and accounts covered, event selectors as expected, digests arriving and validating; recorder running, rules enabled, collector current) and an `audit-gap` record when a feed drops. `deploy.exception` gains kinds `attempted-refused` and `monitoring-protection`. `POST /v1/records` accepts all four kinds from registered observed providers and de-duplicates by provider, source and event id (R-9). clearance-api lists observations and health by scope; `GET /v1/coverage?scope=&from=&to=` returns the three-part statement (cleared and verified; seen, not cleared; could not see) with the health summary, which C-5 prints.
- **Done when.** Schema published and versioned; verify passes across the v1 to v1.1 boundary on a copy of the lab chain; a fake observed provider posts all four kinds and the coverage route prints `blind` for a scope whose health record is stale; the packet's coverage statement (C-5) consumes the route.
- **Rollout.** Clearance release.
- **User steps.** None.

### O-2 · The pipeline: six CEL stages, noise as policy, change transactions
<!-- pkg status=done wave=W5 -->

- **Repos.** clearance.
- **Depends on.** O-1, R-1 (cel-go, the bundle loader).
- **Build.** `internal/observe/pipeline`: six stages, each a rule set compiled once at bundle load with a cost limit. *Normalize* flattens the event and canonicalizes the stored object. *Scope* keeps writes in governed clusters, namespaces, accounts and kinds and counts the rest for the population. *Noise* drops legitimate controller writes under rules that pair an identity with the exact shape it may touch (the Argo controller may write objects of applications it manages, cert-manager may rotate Secrets it owns, the HPA may write `/scale`; "anything from a service account" is refused as a rule); the allowlist is a versioned policy bundle named in every assessment, and the packet prints "filtered: N events under rule X". *Attribute* ties what survives to an authorization, strongest signal first, per provider (the orders in the Architecture's chapter 09). *Classify* maps the outcome to a coverage state and a tier. *Correlate* collapses bursts into one change transaction using resource relationships and execution context (a `kubectl apply -f dir/` is a dozen events; a Terraform resource is several calls; a Deployment cascades) and folds an apply-and-revert into one exception. Monitoring-protection operations (AWS `StopLogging`, `DeleteTrail`, `UpdateTrail`, `PutEventSelectors`, `StopConfigurationRecorder`, `DeleteConfigurationRecorder`, `DisableRule`, `DeleteRule`; a Kubernetes audit-policy or webhook change; the Azure and Google equivalents) are tier 3 observations whether or not they succeeded, alert immediately and flip the scope's health. A `clearance observe replay` command runs recorded raw events through the pipeline for tests.
- **Done when.** A golden corpus of recorded Kubernetes and AWS raw events replays to the expected assessments; every rule compiles under the cost limit; a seeded apply-and-revert produces one exception; a seeded `StopLogging` produces a tier 3 observation and `degraded` health when the call is refused, blind when it succeeds (owner, 2026-11-09); `go test -bench` keeps the per-event path under 1 ms.
- **Rollout.** Clearance release.

### O-3 · The Kubernetes audit-log collector
<!-- pkg status=done wave=W5 -->

- **Repos.** clearance (`providers/observe-k8s`), apron, gitops-hangar-prod.
- **Depends on.** O-2, G-ARGO-3 (the reconciler it extends), G-ARGO-7 (the gate on hangar-prod).
- **Build.** A webhook receiver for the API-server audit backend (batches, acknowledged into a durable queue, so a collector outage loses nothing), and readers for managed clusters (CloudWatch Logs for EKS; GKE Data Access logs; the AKS `kube-audit` category), each a reader with its own latency and the same normalizer. The audit policy shipped as a template: drop control-plane loops, events, endpoints, leases and all reads; status writes at `Metadata`; writes to desired state in protected namespaces and to cluster-scoped governed kinds (RBAC, admission configuration, CRDs, Argo Applications) with bodies; every other write at `Metadata`; **Secrets at `Metadata` only, wherever they live**, with a test that fails the build if any rule would record a Secret body. Attribution per the Architecture: grant annotation and rendered hash matching, cleared; grant present and hash differing, out-of-band at high severity unless a mutating webhook in the audit annotations explains it; the Argo service account with no grant, out-of-band and cross-referenced to Argo's own log; a federated identity with no `task_id`, observed-not-attributed; a human, impersonation, unknown service account or `kubectl` agent, out-of-band with the diff; a live break-glass record, break-glass; a 403 with a VAP denial in the audit annotations, attempted-refused. A watch-stream change with no audit event becomes an `audit-gap` record; the reconciler in G-ARGO-3 stays as the backstop and its exceptions are correlated into the same transactions rather than duplicated. The health check reads the live audit policy and webhook configuration. On Hangar the lab cluster is hangar-dev (kind, webhook backend) and the protected cluster hangar-prod; apron renders the collector, its queue and NetworkPolicies under `56-clearance-gate/` behind `clearance.observe.enabled`.
- **Done when.** On hangar-prod a direct `kubectl apply` into a protected namespace appears as an exception within a minute with actor and diff; a Secret change appears with the key named and no value in any record; a 403 from the admission policy appears as attempted-refused; with the collector stopped, the coverage route and a packet report a blind window, not a clean one; the reconciler and the collector report one exception, not two, for the same change.
- **Rollout.** Clearance release, apron render, gitops-hangar-prod PR.
- **User steps.** Apply the audit policy on hangar-prod (control-plane flags); run the `kubectl apply` and the Secret test; merge the prod gitops PR.

### O-4 · The AWS collector
<!-- pkg status=done wave=W5 -->

- **Repos.** clearance (`providers/observe-aws`; absorbs G-TF-5's `terraform-watch`), apron, hangar-infra, hangar docs.
- **Depends on.** O-2, G-TF-4 (the gated lab workspace), G-TF-5 (the detectors it absorbs).
- **Build.** Three feeds through one normalizer. CloudTrail management events delivered to EventBridge, an EventBridge rule matching `readOnly: false` events whose identity is not `AWSService`, into an SQS queue the collector drains; data events on the state bucket, artifact buckets and secrets only; the S3 trail read in batches with log-file integrity validation (the AWS signature on each hourly digest and the file hashes, verified before extraction, the result recorded as `sourceVerified`; completeness stays claimed). AWS Config configuration items and an aggregator as the reconciler, with the diff and the pointers to the causing events. State-bucket versions as the second witness (G-TF-5's untraced-apply detector, now a stage of this collector) and the scheduled plan as the drift detector. Attribution per the Architecture: `userIdentity.type` (`Root` always an exception), `sessionIssuer.arn` (the apply role versus the SSO admin role), `sourceIdentity` as the actor the record quotes, the self-reported session name and user agent (the runner sets `TF_APPEND_USER_AGENT="clearance/grant=clr_…;plan=sha256:…"`), `errorCode` for refused attempts; the correlation hierarchy: signed execution attestation, verified pipeline identity and run, apply role and session, the cleared plan's resource-change set against the resource and action, commit and plan digest, the apply window last. The logging-account separation (the trail and the aggregator deliver into an account production administrators cannot write to; Clearance monitors it too) is a documented customer precondition and the lab's own setup. Health per account: trail enabled, regions and accounts covered, selectors as expected, digests validating, recorder running, rules enabled, collector current. First-release scope: IAM, CloudTrail and Config configuration, security groups, S3 policies and public access, KMS; VPC routing, Secrets Manager, Lambda configuration, EKS access and RDS second; SSM session contents, database content and partially covered services named as not evaluated. The collector's workflow, image and chart (the W3 follow-up) ship here; onboarding is a cross-account role for the lab, with StackSets and a Marketplace-managed deployment as the open question (section 14, #16).
- **Done when.** A console security-group change in the lab account appears in the exceptions with actor (`sourceIdentity`), the Config diff and a resolution; a gated apply does not; a `StopLogging` call appears as a monitoring-protection event and flips the account's health to `degraded` when the call is refused, blind when it succeeds (owner, 2026-11-09); the digest-chain validation result is on every observation from the S3 trail; the packet lists the account's observations beside the workspace's applies with coverage verified.
- **Rollout.** Clearance release, apron render, hangar-infra PR (the EventBridge rule, the queue, the logging-account delivery and the read-only role are Terraform in hangar-infra, applied through the gate).
- **User steps.** Create the logging account or bucket policy and the read-only role; run the console change and the `StopLogging` test; `terraform apply` where the agent is blocked.

### O-5 · Observation in the packet, Tower and the coverage statement
<!-- pkg status=done wave=W5 -->

- **Repos.** clearance, backstage (Clearance plugin, vendored contract), hangar docs.
- **Depends on.** O-1, C-5, O-3 (for live data).
- **Build.** The packet's coverage statement prints the three parts and the health summary per scope from `GET /v1/coverage`, and its exceptions section the per-class rows with actor, diff and resolution; freeze and incident reports gain the observed changes in their windows. Tower: an Exceptions tab on the Clearance plugin (observations by coverage state, the resolution record editable by a person with the cause, each edit evidence naming the person), a coverage banner per scope (healthy, degraded, blind), and an alert on `degraded` and on any monitoring-protection event. The Architecture's status rows for the collectors, the pipeline and the health record move to Built; the brief's chapter 05 coverage-statement text is checked against a real packet.
- **Done when.** A 30-day lab packet shows a blind window for a scope whose collector was stopped and a clean window for one that was not, and C-4 verifies it; an operator sets a resolution cause in Tower and the record shows the person.
- **Rollout.** Clearance release, Tower release.

### O-6 · Azure and Google Cloud adapters (on a trigger)
<!-- pkg status=later -->

- **Repos.** clearance (`providers/observe-azure`, `providers/observe-gcp`).
- **Depends on.** O-4; a design partner whose production runs there.
- **Build.** Azure: the Activity Log exported by a management-group diagnostic setting to an Event Hub, Resource Graph `resourcechanges` as the reconciler (before, after, `changedBy`, `clientType`, correlation id), Azure Policy `deny` denials from the Activity Log as attempted-refused, `caller` and the `appid` claim as the verified actor, workload identity for the runner, a `clearance-grant` tag through `default_tags` plus the correlation id for grant correlation (no user agent in the Activity Log), blob versioning for the state witness. Google Cloud: an organization-level aggregated Log Router sink with `includeChildren` to Pub/Sub, Admin Activity always on and Data Access opt-in (Secret Manager, Cloud Storage, Cloud SQL named), Cloud Asset Inventory feeds as the reconciler, Policy Denied logs and `authorizationInfo.granted: false` as attempted-refused, `principalEmail` and `serviceAccountDelegationInfo` for the actor and its chain, Workload Identity Federation for the runner, `callerSuppliedUserAgent` and `operation.id` for correlation. Each is a normalizer on O-2's pipeline, nothing more.
- **Done when.** The O-4 exit tests, run on the partner's cloud with the partner performing the console change; the coverage-statement burden per cloud documented (Azure highest, Google lowest).
- **User steps.** The partner's onboarding; no Hangar lab for either cloud.

## Work packages, P-series: the clearinghouse and the outward statements {#work-packages-p}

Five packages build what the packet is for once it exists: the recipients who accept it, the sample an auditor pulls, the statement a subscriber hands a prospect or a carrier, the push into a GRC hub, and, last, the portal (added 2026-11-07; the [Clearinghouse](https://claude.ai/artifact/3rPgELsmjQJ5rqsz386D9Q), [Verification](https://claude.ai/artifact/UfE1xys4nK9C7D2gNm25Lp) and [Underwriting](https://claude.ai/artifact/PaZMadKYhzJSJgTBHxiw6B) companions have the design). Three rules from those documents bind every package: verification, witness operation and acceptance are free and need no account; the subscriber grants access and Clearance records it, Clearance never submits on anyone's behalf and never pays a recipient; and no page ever scores or ranks a subscriber. Everything here is Go in the clearance repo; the public verify page is a small server-rendered page in the same binary, no JavaScript framework. Two UIs, separate by design and sharing no package: the standalone Clearance UI (clearance web and the jfillman/clearance-ui package; operational: clearances, evidence, exceptions, attestations, map, policy) and the Cloud portal (clearance-cloud web/, @clearance/cloud-ui, Cognito; business-facing).

### P-1 · Assurance providers: acceptance receipts and recipient access
<!-- pkg status=built wave=W6 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** C-5 (the packet), C-3 (the ledger the receipt lands in).
- **Build.** The assurance-provider contract from the Architecture's chapter 08 as a registered provider class: `POST /v1/packets/{id}/deliveries` (the subscriber names a recipient, a scope and a window; the delivery is a ledger record), `GET /v1/packets/{id}` for the recipient under a scoped, time-boxed credential (every fetch a record), issued and verified by the core (the Cloud API only passes it through and keeps its own grant register), and `POST /v1/packets/{id}/receipts` where the recipient signs an acceptance receipt with its own key (packet id, engagement, framework and mapping versions, checkpoint, verdict accepted, accepted with notes, questioned or rejected, per-control notes keyed to mapping row ids); a receipt signed after the delivery window ends is accepted, and one dated before the window began, or in the future, is refused. The receipt is a ledger record of its own; later packets carry prior receipts in their Acceptances section (C-5) and `clearance verify` checks the recipient's signature against the key it registered (a receipt passes only with keys supplied for that named recipient: --recipient-keys \<recipient>=\<file>). A `clearance receipt sign` subcommand for firms that have no system to sign from. Recipient identities are a registered key only in W6 (OIDC recipient identity is deferred, not built), never a Clearance account (no Clearance role or password; an external IdP identity is fine).
- **Done when.** A fake assurance provider pulls a lab packet under a time-boxed credential, signs a receipt, and the next packet's Acceptances section carries it and verifies; an expired credential is refused and the refusal is a record (there is no credential or key revocation in W6: a credential is good until it expires, from 1 minute to 30 days; successful reads are capped per delivery per hour; a new delivery is the remedy for a leaked credential); the roadmap's phase 3 "GRC lead forwards a packet unchanged" test (defined as: a second delivery of the same packet to a second recipient returns identical, verifiable bytes through the credentialed route; owner decision 2026-11-14) runs through this route.
- **Rollout.** Clearance release.
- **User steps.** The first real recipient's key.

### P-2 · The sampling call
<!-- pkg status=built wave=W6 -->

- **Repos.** clearance.
- **Depends on.** P-1, C-4.
- **Build.** `GET /v1/packets/{id}/sample?n=&seed=&stratify=` returns a statistically valid sample of cleared records (n from 1 to 100, default 25; at most 20 distinct samples per delivery) (uniform or stratified by tier and month, tier and month together or not at all, seed recorded so the auditor can reproduce it; the seed is required and supplied by the auditor, with no default, because a default derived from the packet could be steered by whoever builds the packet) with an inclusion proof per record against the packet's checkpoint range, and the sampling itself as a record. The population is every change in scope (changes cleared after the checkpoint are listed as excluded with a count, not sampled), printed with the sample, so a firm can test the population before the sample (the ChatGPT analysis's point and the auditor pilot's measurement). `clearance verify` checks a sample file offline the same way it checks a packet, and passes it as a full pass only when the sample's ledger record is supplied and matches; otherwise it reports not checked.
- **Done when.** A 25-record sample of a 30-day lab packet verifies offline; the same seed reproduces the same sample; a record outside the scope cannot be sampled; asking for more than the eligible population is refused, not clamped.
- **Rollout.** Clearance release.

### P-3 · The verification statement and the hosted verify page
<!-- pkg status=built wave=W6 -->

- **Repos.** clearance, apron (the public route), hangar docs.
- **Depends on.** C-3, C-4, C-5, O-1 (the three-part coverage), C-14 (approver kind), P-1 (receipts to show).
- **Build.** The verification statement as the packet's fourth derived view (Architecture chapter 11): `POST /v1/statements` from a period, a scope and a policy version (a packet with no checkpoint cannot get a statement; issuing needs the packet's proofs and the checkpoint and log keys on the core, and the core runs the checks before signing and refuses a packet that fails) produces an immutable, signed statement with two levels. The public summary (period, scope as printed, policy version, counts by every coverage state, exceptions by class, the observation-health summary, the verification result, receipt counts and verdict tallies, not the names of the firms, a questionnaire-mapping block shipped as data beside the control mapping with SOC 2 CC8.1 and CC6, ISO 27001 A.8.32, NIST SP 800-53 CM-3 and CM-5 and the SIG change-control and AI topics, worded as evidence for those objectives) and the recipient detail (exception rows with resolutions, record ids, proofs as files), opened by the subscriber to a named recipient and recorded like auditor access. Invariants enforced in the core: totals, every coverage state, exceptions and unreconciled counts can never be omitted; the scope is the only choice; a correction supersedes (`supersedes` on the new statement, `supersededBy` on the old); `POST /v1/statements/{id}/revoke` makes it verify as revoked; statements do not expire, they are superseded, revoked or reissued. The hosted page at `verify.<domain>/s/{id}` runs the seven checks in order (signed by the subscriber's Clearance identity; signature valid; every cited record has an inclusion proof against a checkpoint; checkpoints countersigned by a witness Clearance does not run; counts recompute from the cited records; exceptions and health present and matching; not superseded or revoked), prints one word and one colour at the top (when the witness's countersignature verifies the word is "VERIFIED, WITNESS INDEPENDENCE DECLARED", never plain VERIFIED, since independence is the issuer's declaration) with the checks behind a click, and links `clearance verify --statement <url>` for the reader who wants to run it alone. The insurer profile is the same statement with `profile: insurer`: the share of critical changes with two independent approvers (from C-14's `kind: person`), unresolved exceptions each with a disposition, telemetry coverage per scope as a share of the period, the agent share of changes, and a mapping block in carriers' words (privileged change, separation of duties, unauthorized-change detection); monthly cadence by the subscriber calling the issue route on its own schedule (W6 has no built-in scheduler). The statement format and the verification rules are published with the verifier (a `docs/statement.md` and a JSON schema), so a reviewer or a trust-center platform verifies without Clearance; the statement verification keys are published separately from the token key set and are never accepted for tokens. The page never scores or ranks.
- **Done when.** A lab statement verifies on the hosted page (headline "VERIFIED, WITNESS INDEPENDENCE DECLARED"; the hosted page never shows plain VERIFIED, because the witness's independence is the issuer's declaration, and the plain VERIFIED result with all seven green is the offline one, when the reader names the witness key) in under two seconds with all seven checks green (in the lab run the statement may print "not yet independently witnessed"; check 4 is proven at the Cloud K2 gate) and the proofs not downloadable from the public route (they are reached through the P-1 credentialed routes); a revoked statement shows revoked; a superseded one points at its successor; a statement with a stopped collector in its window prints the blind window; an insurer-profile statement prints the five figures; `clearance verify --statement` passes offline against the published trusted root; a page load with JavaScript disabled still shows the result.
- **Rollout.** Clearance release, apron render (the public route and its rate limit) (the public listener ships off by default and stays off until the owner accepts the security review; in the hosted deployment it runs as its own process, not inside the core), hangar docs.
- **User steps.** The `verify.<domain>` DNS and certificate; the first shared statement, to a real prospect's reviewer if one exists.

### P-4 · GRC push, Vanta first
<!-- pkg status=built wave=W6 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** P-1, C-5. The roadmap's phase 2 item; it waits here only because the packet does.
- **Build.** The hub as an assurance provider that receives summaries and links, never copies: Clearance registers on the hub's evidence API, the customer connects a tenant with an API key (one sender only, because the vendor keeps one live token per application), and each production change becomes an evidence item (at Vanta an evidence item is a custom resource of a private integration, and it counts toward a control only once a custom test is built over it at Vanta) mapped to the hub's control identifiers (origin, tier, approver (a count and kind only: no names and no hash, because an unsalted hash of usernames is reversible), digest, a link to the verifiable record) with a periodic coverage report (change counts, not the three-part telemetry coverage, because the notifier role cannot read that). The signed record stays in Clearance; the hub holds a pointer. Because the vendor sync replaces the whole set, an empty set is never sent, a set below 80% of the last one is refused unless explicitly allowed, a change stays in the set after it is superseded or becomes an exception, and items older than the window (default 90 days) leave the vendor but stay in Clearance. Drata second, behind the same interface (in W6 Drata is the target interface only; no Drata code). Unverified until tried: whether the hubs' evidence APIs accept structured attestations rather than files, and whether a firm signs a receipt from inside the hub's workflow.
- **Done when.** A lab change appears as an evidence item in a Vanta sandbox tenant with a working link back to the record; the coverage report lands on schedule; nothing but hashes, links and summaries leaves the tenant (asserted by a test on the outbound payloads).
- **User steps.** A Vanta sandbox or partner tenant.

### P-5 · The auditor portal and the working-paper push (later)
<!-- pkg status=later -->

- **Repos.** clearance, backstage or a standalone page.
- **Depends on.** P-2, P-3; two firms having accepted a packet (the roadmap's phase 5 trigger).
- **Build.** Scoped, time-boxed, recorded read access for a firm: the packet, the sample call and the verification page behind one firm identity, with the firm's engagements as the unit of scope; a working-paper push to Suralink or AuditBoard as a provider endpoint so the packet never passes through email; the pilot's three measurements captured as records (hours on change-management testing against the firm's prior-year figure, the share of the sample verified without a client request, acceptance of a coverage statement with a blind window). The large firms' own systems when a subscriber brings one.
- **Done when.** One firm accepts a ledger sample in place of a ticket sample on one engagement, with its receipt in the ledger and the three measurements recorded.
- **User steps.** The firm.

## Work packages, I-series: intelligence (later, except I-1) {#work-packages-i}

The opt-in cross-tenant dataset is a second pipeline with its own schema and consent, never a byproduct of the ledger (decided 2026-11-07; the [Intelligence companion](https://claude.ai/artifact/M2rDPgy5WJx8aG7dxsr3xf) has the measurements, the thresholds and the sequence). Only I-1 is near-term, because the operational change class is the cross-tenant comparison axis and belongs in the classifier whether or not anything is ever exported.

### I-1 · The operational change class as versioned data
<!-- pkg status=built wave=W4 -->

- **Repos.** clearance, hangar docs.
- **Depends on.** G-TF-1 (the second subject kind), O-1.
- **Build.** Beside the technical class the classifier already names (resource kinds, paths, Terraform resource types), a mapping shipped as data and versioned like the control mappings: `availability`, `privilege`, `data-integrity`, `security-boundary`, `credential-exposure`, one or more per change, computed from the rendered diff or the plan and stored in the Decision group of every record. The tier stays the customer's policy; the operational class is the only axis a cross-tenant comparison may use, and the packet's Changes section prints both.
- **Done when.** Every lab record carries at least one operational class; a seeded Secret rotation is `credential-exposure`, an IAM policy change is `privilege`, a Deployment image bump is `availability`; the mapping version is in the record.
- **Rollout.** Clearance release.

### I-2 · The intelligence export, the coverage score and the cell rules (later)
<!-- pkg status=later -->

- **Repos.** clearance, hangar docs.
- **Depends on.** I-1, O-5; the data-handling terms with a separate, purpose-limited consent signature (roadmap phase 0 and 4).
- **Build.** A published export schema carrying verified fields and counts only (no approver subjects, no diffs, no intent); an evidence-coverage score per tenant and period on six dimensions (sources covered, actor attribution, authorization observed, execution observed, outcomes observed, reconciliation available); request, decision, approval, execution and outcome exported as separate events; the cell rules enforced in the aggregator (20 tenants, 2,000 changes, no tenant above 25 percent of a cell, fixed cuts, suppression against differencing); give-to-get, so peer benchmarks in Tower are visible only to contributors; withdrawal handling; a `clearance export preview` that shows a tenant exactly what would leave.
- **Done when.** The export of a lab tenant contains no approver subject and no diff (asserted by test); an aggregate over fewer than 20 fake tenants is refused; the preview matches the export byte for byte.

### I-3 · The internal aggregate report (later)
<!-- pkg status=later -->

- **Repos.** clearance.
- **Depends on.** I-2; ten or more opted-in tenants (the roadmap's phase 5 trigger).
- **Build.** The measurement set of the Intelligence companion (AI-originated share by confidence band, human-required share by operational class, denial and refused-attempt rates, rollback rate by cause, out-of-band and break-glass rates beside the health record, monitoring-protection counts, control effectiveness), each printed with its confound and its coverage floor, as an internal report that validates every measurement before any edition is published; the public index is a later, commercial decision and not a package here.
- **Done when.** The report runs over the consenting lab tenants and every measurement has its confound line.

## Build report: W0 and W1 (2026-11-03) {#build-report-w0-and-w1}

Superseded by the W1 report below (the W0 PRs were merged on 2026-11-03). W0 is built and its PRs are green, but nothing is merged. The run stopped at W0's merge gate: the auto-mode classifier refuses the agent's merge of Clearance PRs ("Merge Without Review"), so W1's first package (R-2) cannot start until the user merges clearance#43. No W1 package was started, no tag was cut, no image was built, and nothing on hangar-dev changed. The W1 gate "Installs alone" was not reached.

### Package status

| Package | Status | PRs | Tags and image digests |
| --- | --- | --- | --- |
| R-1 Core API, provider protocol, conformance (R-1a to R-1f) | Built (CI green, not merged, not deployed) | [clearance#43](https://github.com/jfillman/clearance/pull/43) | none: a tag waits on the merge |
| R-6 Evidence record v1 | Built (in the same PR, not merged) | [clearance#43](https://github.com/jfillman/clearance/pull/43), [hangar#109](https://github.com/jfillman/hangar/pull/109) | none |
| R-8 Hygiene, docs, release automation | Built (CI green, not merged) | [clearance#42](https://github.com/jfillman/clearance/pull/42), [autopilot#68](https://github.com/jfillman/autopilot/pull/68), [hangar#108](https://github.com/jfillman/hangar/pull/108) | none; apron needed no change |
| R-1 rollout: boundary decision D21 (amends D16), language decision D22, design.md 0.1 | Built (not merged) | [hangar#110](https://github.com/jfillman/hangar/pull/110) | n/a |
| R-2 Clearance's own image and chart | Proposal (not started: needs R-1 merged) | none | none |
| R-3 The AI gateway moves to Autopilot | Proposal (not started) | none | none |
| R-5 Policy bundles and Hangar vocabulary | Proposal (not started) | none | none |
| R-7 Clearance as its own Apron component | Proposal (not started) | none | none |
| R-4 The cutover on hangar-dev | Proposal (not started) | none | none |

Live on hangar-dev at the stop, unchanged by this run: autopilot-gateway gateway-v0.3.27@sha256:afd540d929c339ffcb85f490ed91608871a47354a24a0386e131e5b908663d0f (clearance v0.26.1) for both the clearance and clearance-api Deployments; clearance-pg 1 instance.

### Live evidence

The W1 gate has no evidence because it was not reached. The W0 checks against live hangar-dev state:

- Chain dump: `select record::text from clearance_evidence order by seq` on clearance-pg-1, database clearance, 612 records (seq 0 to 611), taken 2026-11-02. Python `audit.verify`: `(True, None)`.
- Go verifier on that dump: `clearance chain verify --file live-chain.jsonl` printed `ok 612 head 08cf40674262c1d5e7b7d236dd991c9c6d11cbb4c114f6508bb7058ab1d2a918`, the same head as Python. One byte changed in seq 300 printed `bad seq 300: hash does not match the record` (exit 1).
- Extension: the 612 rows were loaded into a scratch Postgres, then a Go writer opened them, verified from genesis and appended 4 records; Python `audit.verify` on the result printed `ok 616 bdc25f10…3bfd`.
- v0 to v1 boundary (R-6): Python PgAuditLog appended 2 v1 records and a Go pg writer 2 more on the 612 rows. `chain verify --dsn` printed `ok 616 head 3cb43a52d1899d7edf0feccb05ba3a27486bd81b6f286214b897964d8e5b437c`, and Python reopened the database to the same head. Python and Go project all 612 v0 rows byte-identically.
- Record check on real records (docs/evidence.md): seq 0, 3, 16, 139, 141, 236, 335, 336, 397 and 402 to 405. They answer who initiated (principal, agent, session, task\_id verified) and in part whether it was authorized (decision, rule, tier; no policy version, no approver identity). Two findings: seq 405's approver is `app:177375213`, the App, not a person; `clearance register` changes 402 to 405 carry an all-zero tree digest, so they bind only to the commit.
- CI on clearance#43 at 1f6dabd, all green: go (vet, gofmt, `go test -race` with Postgres, govulncheck, every fuzz target), pytest (425 with Postgres), python-client on 3.11 and 3.13.

Budgets, measured locally on an M4 Pro:

| Path | p50 | p99 | Budget |
| --- | --- | --- | --- |
| Decide in process (realistic mix) | 5 µs | 215 µs | 2 ms |
| POST /access/v1/evaluation over HTTP, memory store | 233 µs | 1.19 ms | 20 ms |
| POST /access/v1/evaluation over HTTP, Postgres | 672 µs | 2.31 ms | 20 ms |
| Record append and commit, Postgres | 0.3 to 0.53 ms | 0.73 to 2.8 ms | none |

### R-1 golden corpus and cel-go

No rule evaluated differently under cel-go, so no rule was changed. The corpus has 749 lines recorded from the Python engine over the whole Python test suite plus the fixture agents' calls. The Go engine replays its 735 decision lines with identical decision, rule id, name, message, hint, tier, problems, spend, grant and record fields. That covers 691 records, 380 spends, 293 grants and 35 problem lists. A drift test that changes one word of R006's message makes the replay fail. Every rule id has at least one deny, and every action kind has at least one allow.

| Action | Lines | Allows |
| --- | --- | --- |
| tool.call | 348 | 141 |
| session.open | 295 | 275 |
| model.call | 52 | 10 |
| session.spawn | 35 | 18 |
| altered activation (probes) | 18 | 5 |

The edges probed gave identical results:

- integer overflow at 2^63, 2^64 and 2^63+5, and `est_tokens` of 10^30;
- int, float and bool arguments;
- `in` on lists;
- string functions: a trailing newline against `$`, the lower-case forms of İ and final Σ, and strip;
- YAML equality: 1 against 1.0, yes against true, NaN, merge keys;
- timestamps and null.

The engines differ only on ill-typed contexts that a request cannot carry:

| Altered context | cel-python | cel-go |
| --- | --- | --- |
| `tool.tier = True` | allow (fails open) | R000 |
| `ctx.missing_args = False` | allow (fails open) | R000 |
| `tool.name = 5` | R000 | R006 |
| `effective.tools = "catalog.read"` | R006 | R000 |

The two fail-open cases are cel-python's, not the rule's. They cannot happen through the Go core, whose decoder and typed variables refuse those values. The full list is in `internal/decide/CEL_DIFFERENCES.md`.

### Deviations from the spec

- **One PR for R-1 and R-6.** R-1's six sub-tasks ran as parallel subagents on branches merged into one integration branch, `r1-go-core`. R-6 landed on the same branch because it changes the Go record writer R-1 built. clearance#43 also contains clearance#42, merged in to resolve conflicts in pg.py, README.md and docs/index.md: merge #42 first, then #43.
- **Two packages were added beyond the card.**
  - `internal/profile` ports the agent-definition parser and schema, which the gate and provenance need.
  - `internal/directory/backstage` ports Backstage group and owner lookups. Without it no person could clear a tier-2 or tier-3 change on the Go core.
  - Per the boundary, both belong to Autopilot after R-3; the core keeps a copy for tiering and approvals.
- **The card names `internal/record`; the code uses `internal/store`.** It holds the evidence chain and the gate's rows behind one interface.
- **Two records per allowed tool call.** The decision record carries `result: ok`, and the outcome record (`outcome_of`) carries the effect. Python wrote one. clearance-api counts by tool will see both.
- **New verified field `caller`**, holding provider and principal, on decision and outcome records. The evaluation's `now` must be within 5 minutes of the core's clock, because the record's ts comes from it and is verified.
- **Retries in the clients.** The R-3 card says one retry. The clients retry an outcome, record, clear or deny only when nothing was sent, or when the core answered 503, because a blind retry can write a record twice.
- **Stricter than Python, on purpose:**
  - strict decoding: unknown fields get a 400;
  - Go's `$` does not match before a trailing newline, except in deny globs, so a deny is never loosened;
  - events that jsonb would rewrite are refused (`ErrNotStorable`), where Python broke its own chain on the next start;
  - JWT `exp`, `iat` and `nbf` given as strings are refused, as is any `crit` header;
  - YAML errors and alias bombs, and JWKS and Backstage failures, fail closed instead of raising a 500;
  - `register --paths-from-git` is refused, because the binary does not shell out.
- **Go CI uses Go 1.26.x, not go.mod's 1.25.0,** because govulncheck fails on standard-library vulnerabilities fixed in later patches. tools/fuzz-all.sh retries once a fuzz run that stopped only on the fuzzer's own deadline (golang/go#56238).

### Descoped

- From R-1:
  - The gateway's handler-side checks stay in the Python gateway: launch()'s R004 and R001, run.close's R001, and the inbox HR-\* rules. Corpus lines refused by a handler are not compared for record and spend.
  - `Policy.trace` is not ported.
  - The Postgres-backed Python tests were not in the corpus (no DSN while recording).
  - No route feeds cluster-pinned definitions to the core; the registry loads stored rows at start.
  - The read routes for clearances and the policy stay with clearance-api (R-2).
- From R-6: writers fill the new optional groups (policy, approvals, token, outcome, provenance, destination, intent text) only where R-1d already writes them. The rest waits for C-1, R-5, G-ARGO, G-TF and A-4.
- From R-8, three defects were left alone because fixing them changes live behaviour or needs a decision:
  - `flight_registries` is empty by default. A default would move live image bumps from tier 1 to tier 2.
  - `ChangeRequest.protected` is parsed but unused. Its meaning is a gate-semantics question.
  - `ModelDecision.headers` is never forwarded. Forwarding it would send session and task ids to Anthropic.
- R-8's release workflow builds the wheel and the GitHub Release. Its image and chart jobs are placeholders for R-2.
- autopilot's package version is still 0.1.0.dev0; it releases by image tag.
- The airframe re-vendor had already landed through autopilot #45, #46 and #50.
- The conformance suite does not assert the runtime-records route or deploy.exception. "A fake runtime provider passes conformance" is met with the Go fake. The real gateway can run the suite only after R-3.

### Open questions and recommended changes to W2+ cards

| # | Card | Change | Why |
| --- | --- | --- | --- |
| 1 | C-10, G-TF-2, G-ARGO-5 | Add `GET /v1/clearances/{id}` and a wait route on the core for registered providers | A deployment provider today learns a change's state only by re-POSTing its registration, which takes the gate lock and rewrites the row; clearance-api's read is closed to providers |
| 2 | G-TF-2, C-10 | A change-bound `POST /v1/clearances/{id}/outcome` that checks the applied digest against the cleared one and writes deploy.exception on a mismatch | deploy.outcome through /v1/records is all claimed; only the conformance harness compares digests today |
| 3 | C-1 | Stamp `provider.conformance` from a `CLEARANCE_PROVIDERS` field once a provider passes | The v1 schema reserves it; nothing sets it |
| 4 | R-3, A-series | Name who feeds cluster-pinned definitions to the core after the move (a gateway-to-core route, or the core reading Agent XRs itself) | The Go core has no route for it |
| 5 | R-3 | Say the handler-side checks (R004/R001 on launch and close, HR-\* inbox rules) stay in the gateway; adopt the clients' per-call retry rule | Not ported to the core by design; a blind retry can double-write |
| 6 | R-2 | The Go clearance-api serves records through `evidence.Project`, counts decision and outcome records apart, and fills the release workflow's image and chart jobs | Two records per call; v0 rows need projection |
| 7 | C-5 or a new card | Record the approving person on deploy.\* records, not the App principal | Record check: seq 405 names `app:177375213` |
| 8 | G-TF-1, register | Give `clearance register` changes a real tree digest | seq 402 to 405 carry an all-zero tree |
| 9 | R-5 | The Hangar pack is Go code (context functions for args and cicd scope), not only CEL plus data. Decide whether the bundle carries a pack plugin or Hangar's context moves to the gateway's evaluation request | R-1a ported it as `internal/decide/packs/hangar`; the Hangar names R-1c isolated are listed in its package docs |
| 10 | User | `flight_registries` decided 2026-11-03, option B: product default empty, Hangar sets ghcr.io/riley-roooo/ via CLEARANCE\_FLIGHT\_REGISTRIES, live at the R-4 cutover. Still open: the meaning of `ChangeRequest.protected` | R-8 left both for a decision |
| 11 | none (watch) | Go's `pycompat.ToJSON` writes non-string keys with repr (`True` not `true`), and the YAML `!` tag is not reproduced | Both are known and documented. They matter only if such values reach a record |

### Waiting on the user

1. Merge [clearance#42](https://github.com/jfillman/clearance/pull/42), then [clearance#43](https://github.com/jfillman/clearance/pull/43); then [autopilot#68](https://github.com/jfillman/autopilot/pull/68), [hangar#108](https://github.com/jfillman/hangar/pull/108), [hangar#109](https://github.com/jfillman/hangar/pull/109) and [hangar#110](https://github.com/jfillman/hangar/pull/110). After the merge the managing agent tags v0.27.0 off green main and starts W1 with R-2.
2. Resolve the 14 staged airframe Tier-2 twins and the untracked `lab/` directory with its api-key file in the autopilot checkout.
3. Review the stale worktrees and branches in `/Users/jerf/tech/R8-stale-branches-2026-11-02.md`. It lists worktrees on merged branches: clearance 18, autopilot 14, glidepath 28, airframe 21, apron 26, hangar 9; two are dirty. Nothing was deleted except this run's own ten worktrees and two scratch Postgres containers.

## Build report: W1 complete (2026-11-03) {#build-report-w1-complete}

W1's gate "Installs alone" passed on 2026-11-03, and the run stopped there. No W2 package was started.

- **Chart:** the chart installs alone on a bare kind cluster. It was proven in CI and again on each release from the published image and chart.
- **Cutover:** hangar-dev cut over to the Go core. The evidence chain continues unbroken across it.
- **R-4 live checks:** all pass. One is indirect: the streaming model call (see the live evidence).
- **Merges:** every PR below is merged, with tags and digests recorded. You merged the clearance, autopilot, apron and backstage PRs and gitops-backstage#244; the agent merged the gitops-hangar-dev renders.

### Package status

| Package | Status | PRs | Tags and digests |
| --- | --- | --- | --- |
| R-1, R-6 (W0) | Built, live | [clearance#43](https://github.com/jfillman/clearance/pull/43) | in v0.27.0 |
| R-8 (W0) | Built | [clearance#42](https://github.com/jfillman/clearance/pull/42), [autopilot#68](https://github.com/jfillman/autopilot/pull/68), [hangar#108](https://github.com/jfillman/hangar/pull/108) | — |
| Boundary decisions D21, D22; evidence docs | Built | [hangar#109](https://github.com/jfillman/hangar/pull/109), [hangar#110](https://github.com/jfillman/hangar/pull/110) | — |
| R-2 image, chart, Go `clearance api` | Built, live | [clearance#44](https://github.com/jfillman/clearance/pull/44), [#45](https://github.com/jfillman/clearance/pull/45), [#46](https://github.com/jfillman/clearance/pull/46), [#47](https://github.com/jfillman/clearance/pull/47) | v0.27.0 `sha256:c95c2c59…65f6`; v0.27.1 `sha256:be65dfb6…f4ec` |
| R-3a the gateway's Python moves to autopilot | Built, live | [autopilot#69](https://github.com/jfillman/autopilot/pull/69) | in gateway-v0.4.0 |
| R-3b the gateway calls the core, own DB, outage policy | Built, live | [autopilot#71](https://github.com/jfillman/autopilot/pull/71) | in gateway-v0.4.0 |
| R-3c the gateway's read API; Backstage reads | Built, live | [autopilot#70](https://github.com/jfillman/autopilot/pull/70), [backstage#247](https://github.com/jfillman/backstage/pull/247), [gitops-backstage#244](https://github.com/jfillman/gitops-backstage/pull/244) | backstage 1.0.2-0ffbee2 on hangar-prod |
| R-3e core changes the gateway needs; R-3f gateway adopts them | Built, live | [clearance#48](https://github.com/jfillman/clearance/pull/48), [autopilot#72](https://github.com/jfillman/autopilot/pull/72) | v0.28.0 `sha256:20ba17ae…e274` |
| R-5 policy bundles, Hangar vocabulary out of the core | Built, live | [clearance#49](https://github.com/jfillman/clearance/pull/49), [autopilot#73](https://github.com/jfillman/autopilot/pull/73), [glidepath#228](https://github.com/jfillman/glidepath/pull/228) | v0.29.0 `sha256:afdca0b4…8dd4` (live); gateway-v0.4.0 `sha256:2f48ce0d…8b74` (live) |
| R-3d remove the Python package | Built, not deployed | [clearance#50](https://github.com/jfillman/clearance/pull/50), [autopilot#74](https://github.com/jfillman/autopilot/pull/74) | v0.30.0 `sha256:a0cf63ac…4598` (nothing live runs it; the next apron pin) |
| R-7 Clearance as its own Apron component, plus R-4 | Built, live | [apron#151](https://github.com/jfillman/apron/pull/151), [apron#152](https://github.com/jfillman/apron/pull/152), [gitops-hangar-dev#107](https://github.com/jfillman/gitops-hangar-dev/pull/107), [#108](https://github.com/jfillman/gitops-hangar-dev/pull/108) | chart 0.29.0 `sha256:3da04b68…7a94` |

Live on hangar-dev, all in autopilot-system:

- `clearance-core`: one replica, the only writer of clearance-pg.
- `clearance-api`: the Go `clearance api`, two replicas.
- `clearance`: the Autopilot gateway on gateway-v0.4.0, with its own `autopilot-pg`.
- `autopilot-api`: the gateway's read API, two replicas.

The Hangar bundle is loaded, with Glidepath's contract fetched live from glidepath-api.

### W1 live evidence

Cutover sequence on hangar-dev (2026-11-03, about 19:20 to 19:36Z):

1. **Head recorded.** Chain dump `ok 640 head 272d8d1e…`, verified by the Go binary.
2. **Python gateway stopped.** Auto-sync paused on `hangar-dev-root` and `autopilot-clearance`. The Python gateway and the old clearance-api were scaled to 0, and the old clearance-api Deployment was deleted because its selector is immutable. **The Python gateway's last record: seq 640, head `07e7a9d81dc6f7312dedfd38b4ae5336ff19151b7147fafeea9f122784068191`.**
3. **Go core started.** gitops-hangar-dev#107 merged and the two new Applications were applied. The Go core logged `"clearance store open","records":641,"head":"07e7a9d8…"`: the same head, verified from genesis. It also logged `"policy bundle loaded","bundle":"hangar"` with the glidepath source fetched live.
4. **Runtime state copied.** `autopilot-pg` was created and the runtime tables were copied by an in-cluster Job, so no DSN left the cluster: 24 sessions, 2 human requests, 145 events, 2 results, 1 definition. The temporary Job and NetworkPolicy were deleted.
5. **Auto-sync restored.** gateway-v0.4.0 started on the copied state.
6. **Hotfix: Cilium blocked TokenReview.** A NetworkPolicy ipBlock does not match the API server on Cilium, so every caller got 401 after 10 s. A CiliumNetworkPolicy fixed it (`PUT /v1/definitions` went 401 to 200), first by hand, then through apron#152 and gitops-hangar-dev#108.

R-4's live checks, each with its evidence records (seq):

| Check | Evidence |
| --- | --- |
| Evidence sequence continues across the cutover | `clearance chain verify --file` on a dump: `ok 675 head d296c99d…`, anchored at `641:07e7a9d8…` |
| `GET /v1/evidence/verify` ok | Unverified through the API (auditor-only; no auditor token was used). The chain was verified with the Go verifier over a database dump instead |
| `clearance register` from the scratch repo, and the GitHub App's protection rule | [clearance-deploy-scratch run 41704945379](https://github.com/jfillman/clearance-deploy-scratch/actions/runs/41704945379): register `POST /v1/clearances` 200 as `github:repo:jfillman/clearance-deploy-scratch…`; deploy.request 641 and deploy.answer 642 "approved" |
| A GitHub App check run | 643–646 and 648, `provenance.verify` as `app:177375213`, on autopilot#74, gitops-hangar-dev#108 and gitops-backstage#244 |
| An agent-gates verdict | 647 and 649 as `app-backstage-cicd/pipeline-runner` (the Glidepath gate) on gitops-backstage#244 |
| A clearance-gate change | 641 (deploy.request) through the same deployment-gate core; no Glidepath clearance-gate run happened in the window |
| A human request answered from Tower | 670 human.request, 672 human.answer "answered via" Tower's backend, 673 human.request.get |
| A person control | 666 trigger.hold and 667 trigger.release on nightly-reviewer; 675 and 676 session.end from Tower |
| An AgentRun that finishes with run\_finish | researcher 650–665: session.open "opened to run via" Tower, run.launch, tool decisions with outcomes (`outcome_of`), run.finish "done", run.delete. coding-agent 677–681 the same |
| A streaming model call | 679 model.call for coding-agent (claude-agent-sdk runtime, which always streams) answered 200 through the gateway's model proxy, and the run finished. Indirect: neither the proxy's access log nor the record says "stream" |
| Tower reads both APIs | backstage 1.0.2-0ffbee2 with `AUTOPILOT_API_URL` serves the Autopilot pages (the user's Tower checks above); clearance-api.hangar-dev.local answers through Traefik |

hangar-prod went down at about 20:30Z, unrelated to the cutover: the podman VM was pegged at 700% CPU. A user-approved VM restart recovered it. The laptop's podman-lan-check agent then restarted the VM once more, because a podman machine started over ssh loses its LAN network.

### W1 deviations, descoped work and decisions

Decisions the user took during W1:

- **Trusted registries (Flight), option B.** The product default is empty. Hangar sets `ghcr.io/riley-roooo/`, live from R-4. In v0.29.0 the setting is named `CLEARANCE_TRUSTED_REGISTRIES`.
- **A bundle source that is down at start degrades only that bundle.** Its tools are denied R000 and uncharged, `/readyz` reports `degraded` with a 200, the core retries in the background, and a version mismatch still stops the core.
- **hangar-prod VM restart.** Approved during the outage.

Deviations from the cards:

- **R-3 grew from one card into five packages** (R-3a to R-3f), adding gateway-v0.4.0. It also needed two Clearance releases the card did not foresee: v0.28.0 for record kinds, `via`, the clock-skew flag and `PUT /v1/definitions`, and v0.27.1 for chart hostAliases.
- **Clearance installs in `autopilot-system` on hangar-dev, not `clearance-system`.** That namespace holds clearance-pg, and its Secret can't be read from another namespace. The chart uses `nameOverride: clearance-core`, so its pods do not match the gateway's `app.kubernetes.io/name=clearance` label, which function-agentrun's run-pod egress and the gateway's Service select on.
- **The gateway keeps the name `clearance`:** its Deployment, ServiceAccount and labels are unchanged, so the run-pod contract does not change. Renaming it is follow-up work, with airframe's function-agentrun.
- **Two records per allowed call:** a decision record, plus an outcome record carrying `outcome_of`. Clearance-api counts exclude outcomes by default.
- **The Hangar bundle is vendored into apron** byte for byte from autopilot at the gateway tag (`hack/vendor-clearance-bundle.sh`), so its digest matches.

Descoped or still owed:

- **v0.30.0 is not deployed.** It removes the Python package and changes nothing at runtime; the next apron pin bump picks it up.
- **The gateway image still installs clearance v0.26.1.** autopilot#74 drops it, effective from the next gateway tag.
- **`GET /v1/evidence/verify`** has not been checked through the API with an auditor token.
- **Streaming** is shown indirectly (above).
- **Hangar docs not updated:** `hangar/docs/autopilot/roadmap.md` and decisions.md have no W1 status, and nothing records the trusted-registries and bundle-outage decisions there yet.
- **Leftovers on hangar-dev:**
  - the old runtime tables in clearance-pg, kept until the cutover is accepted;
  - autopilot-api's `GATEWAY_API_TABLES=clearance` option;
  - the `clearance.<domain>/mcp` alias.

### W1 open questions and recommended W2 card changes

These are in addition to the W0 table above. That table's rows 1 to 3 (a wait route and a change-bound outcome route for providers; conformance stamping) and row 7 (the approving person on deploy records) still stand. Rows 4, 5, 6, 9 and 10 were settled in W1.

| # | Card | Change | Why |
| --- | --- | --- | --- |
| 12 | A-series (new, small) | An owner-only `session_close` MCP tool that ends the caller's own session through `end_session` and writes `session.end` | An MCP client cannot close a session it opened. The session stays live until its TTL, and only Tower's End clears it (user finding, 2026-11-03) |
| 13 | A-series | Record whether a model call streamed (a `stream` field on the outcome, or a proxy log line) | The streaming check could only be shown indirectly. Direct proof needs either the record or exec into a run pod, which the auto-mode classifier refuses |
| 14 | Agents | Give coding-agent `repo.file.get`, and give researcher the Argo CD app naming or a catalog annotation (`argocd/app-name`) | Both live runs answered "I can't": coding-agent has no file-read tool; researcher guessed app names and Argo returned not found |
| 15 | Clearance chart | A CNI-neutral way to allow API-server egress, e.g. `networkPolicy.kubeAPIServer.extraPolicies` or documenting Cilium's entity rule | On Cilium an ipBlock never matches the API server; apron carries a CiliumNetworkPolicy today |
| 16 | R-4 cleanup / A-9 | Drop the runtime tables from clearance-pg and the `GATEWAY_API_TABLES=clearance` option; rename the gateway's Deployment and label with airframe's function-agentrun; retire the `clearance.<domain>/mcp` alias | Leftovers from the cutover |
| 17 | Hangar docs | Record the W1 decisions (trusted registries option B, degraded bundle on source outage) in decisions.md and the W1 status in roadmap.md | The spec's done bar wants both; not done in this run |
| 18 | Ops | Restart the hangar-prod podman machine only through Terminal (`podman-lan-restart.command`) or the lan-check agent | Started over ssh, the VM lost its LAN network and the agent restarted it again |

## Build report: W2 complete and live on hangar-dev (2026-11-04) {#build-report-w2-complete-and-live}

**Gate status.** The W2 gate is met on hangar-dev:

- **Signed tokens issued:** core 0.32.0 logs `clearance tokens: signing`, kid `qBscSbdf…`. `GET /v1/keys` serves one P-256 ES256 key. The key is the owner's, from Infisical `clearance-signing-key`, synced by ExternalSecret.
- **Grant feed:** served by clearance-api (C-10) and signed by the core.
- **Both subject kinds registered:** manifest-tree and terraform-plan (G-TF-1, G-TF-2).
- **Argo design pass:** recorded with spike results in clearance#57. The owner accepted D26–D29 (hangar#113).

### What shipped

- **Clearance v0.31.0** (clearance#61):
  - C-1, clearance token: #55
  - C-8, policy group on deploy records: #52
  - C-10, gate API (wait, signed feed, stream, installations, OpenAPI 3.1): #58
  - G-TF-1, terraform-plan subject: #54
  - G-ARGO-1, design pass: #57
  - C-6, state machine, protected environments, outage policy, exceptions, break-glass: #59
  - C-9, Traefik Hub federated decisions: #51
  - G-TF-2, plan hold and outcome: #60
  - A-4, cost counts: #53
- **v0.31.1** (#63): an unprotected plan keeps its 24 h hold (#62).
- **v0.32.0** (#65): AI co-author trailers give a warn-only `unattested` provenance verdict (#64; owner decision 2026-11-04).
- **Autopilot `gateway-v0.4.2`:**
  - A-1, provider conformance, session\_close, model-call stream: #76
  - A-5, trigger durability: #77
  - A-4, flight recorder and cost: #78
  - A-7, runtime and agents: #79
  - runtime re-pin to runtime-v0.1.4, base-python-v0.1.2, langgraph-v0.1.1, claude-agent-sdk-v0.1.1: #80
- **Backstage:** clearance-api contract re-vendored (backstage#248).
- **Glidepath:** policy verdict sent to Clearance (glidepath#229).
- **Decisions:** D25 (owner), D26–D29 accepted, D30 (protected environments; hangar#114).

### Rollout

- apron#155, gitops-hangar-dev#110: signing-key ExternalSecret.
- apron#156, gitops-hangar-dev#111: 0.31.0 pin, `protectedEnvironments: ["hangar-prod/*", "*/prod"]` (`*/prod` keeps clearance-deploy-scratch protected; a deliberate addition to D30), break-glass 4h, chart-owned Cilium policy.
- apron#157, gitops-hangar-dev#112: the go-live. Clearance 0.32.0, gateway-v0.4.2, metrics port and monitoring, OTLP logs, `/healthz`.

### Verified live (06:20Z)

- **Rollout:** gateway, clearance-core, clearance-api and autopilot-api are on the new images, and all clearance and autopilot Argo apps are Synced and Healthy.
- **Core:** `/readyz` ok with the Hangar bundle loaded. The evidence chain is at 730 records.
- **Gateway:** it names itself `autopilot-gateway/gateway-v0.4.2` and published its definitions to the core. That call proves TokenReview works under the chart's Cilium policy.
- **Prometheus:** scrapes the gateway, `up{job="autopilot-system/autopilot-gateway"}` is 1, and the `autopilot-triggers` alert group is loaded.
- **Loki:** has log streams for `service_name` autopilot-gateway and autopilot-api.
- **`/healthz`:** returns 200 through the route.

### Not verified; needs an agent run (owner)

- **A-1:** a run's records name `autopilot-gateway/gateway-v0.4.2`, and a streamed model call has `receipt.stream: true`.
- **A-4:** `GET /v1/evidence/counts?by=cost&task=<id>` equals the session's charged tokens.
- **A-5:** restart the gateway mid-trigger. No event is lost, and the reconcile sweep fills any gap.
- **C-8:** gitops-gate-api commits A and B on `clearance.yaml`, then a release PR. The record shows `ref: clearance.yaml@A` and then `@B`.

### Owner steps left

- gate-reader re-pin in gate-api, which needs gitsign. The staged worktree is `/Users/jerf/tech/gate-api-wt-a7-runtime-v014`. Replace `RUNTIME_V014_INDEX_DIGEST` with `ae7ba756d0a16676e7bc90fbe1d500b0dc5654e4650b82a06f079387e47bb4ae`, commit and push. After it merges, re-pin the Agent XR commit in gitops-hangar-dev-tenants.
- Optional: the hangar-prod spike plan, `docs/spikes/g-argo-1/prod-plan.md`.

### Follow-ups, not in W2

- The Glidepath broker should allow agent tokens for the tenants repo, needed by `xr.request` and A-3.
- Glidepath should map the `unattested` verdict to `person` in clearance-gate before it sends `coauthors`.
- Provenance scans only the head commit; scanning all PR commits is a later change.
- airframe `limits.tools`: commit 02540fe is not pushed; re-vendor the XRD into autopilot in the same change.
- G-TF-5: C-6's provider-report check needs `destination.cluster`, which plan changes lack.
- The grant feed's seq restarts on a database rebuild; G-ARGO-3 adds a feed epoch.
- The core should de-duplicate `POST /v1/records`, since C-9's adapter is at-least-once.
- Unpinned Dockerfiles in airframe and glidepath.
- Backstage ingestor: it should not need the full CRD list, and its mass-removal guard should hold rather than empty a cluster after 3 runs.
- hangar-dev memory pressure: an etcd stall on 11-04 forced a VM restart. The new IP is 192.168.64.132, and `/kind/kubeadm.conf` is now seeded.
- Four duplicate runtime tags (`runtime-v0.1.5`, `-base-python-v0.1.3`, `-langgraph-v0.1.2`, `-claude-agent-sdk-v0.1.2`) point at the same commit as the pinned ones and can be deleted.

## Build report: W3 code complete; keyless signing live on hangar-dev (2026-11-07) {#build-report-w3-code-complete-keyless}

**Status.** Every W3 package is built and merged. Clearance v0.33.0 and v0.34.0 are released, and hangar-dev runs 0.34.0 with keyless attestations on. The W3 gate (G-ARGO-7's exit tests on hangar-prod, plus a Terraform plan cleared, applied and matched) is **not yet passed**. Both halves are owner-run steps.

Subagents ran on Sonnet, per the model rule in section 1.

### Merged

- **G-ARGO-2:** the ClearanceGrant CRD and the native admission policy. The wait-Job exemption is a field allowlist that pins the plugin's exact Job. (clearance#67, apron#158)
- **G-ARGO-3:** the Argo CD agent: grant sync with the feed epoch, outcomes, exceptions. (#68)
- **G-ARGO-4 and G-ARGO-5:** the CMP and the PreSync wait. (#70, apron#159)
- **G-ARGO-6:** the release-record join. Outcomes attach only to a cleared change with a matching destination and app. (#75, glidepath#231)
- **G-TF-3:** hold, release and report. (#66)
- **G-TF-4:** the hangar-infra workflow plus the same-repository fix. (hangar-infra#3, #4; #72, #74; apron#160)
- **G-TF-5:** the drift and untraced-apply detectors. (#73)
- **C-2:** the attestation signer. (#69)
- **C-2a:** trust-root build and verify (#77), Glidepath managed keys (glidepath#232), apron flags (apron#162).
- **Also merged:**
  - glidepath#230: render parity between the Tekton gate and the CMP.
  - \#71: the release workflow builds the gate images.
  - \#78: the stream-test flake was a test bug; no events were lost in the product.

### Keyless cutover (hangar-dev)

- **The ceremony,** run by the owner. The first run used macOS LibreSSL, which wrote explicit EC parameters that Go rejects, so it was redone with OpenSSL 3. The results:
  - Hangar Root CA: P-384, to 2036.
  - Hangar Fulcio hangar-dev: P-256, to 2028.
  - A new Rekor key.
- **Step 1** (gitops-hangar-dev#115): the trusted root is published, with the legacy root and Rekor key valid until 2026-11-10.
- **Step 2** (#116): Fulcio and Rekor take their keys from Infisical. Verified: Fulcio's trust bundle leads with the new intermediate, and Rekor serves the ceremony key.
- **Step 3** (#117): Clearance 0.34.0, with `/readyz` showing `attestation: enabled, backend keyless`.

### Not verified yet

- A new Chains signature chaining to Hangar Root CA, and an old one verifying through the legacy entry. Both need the next Glidepath pipeline run.
- A live change attestation passing `clearance attest verify --trust-root`. This needs a real applied outcome: the Terraform lab run or G-ARGO-7.
- If the legacy window must move past 2026-11-10, rebuild `trusted-root.json`.

### Owner steps left in W3

1. **Terraform exit check:**
   - create the IAM roles and the `lab` environment with the Clearance App as a protection rule;
   - set `LAB_GATE_ENABLED=true`;
   - open one `network/lab` PR.
2. **G-ARGO-7 on hangar-prod:**
   - turn on the Warn-mode gate on a scratch namespace (commands in docs/gate.md);
   - deploy the agent and the CMP;
   - take one real protected release through the six join checks.
3. **Root key:** store it offline and delete the local private keys.

### Follow-ups

- Tower's provenance view should read `hangar-trusted-root`.
- `serviceAccountName` stays unpinned for the wait Job; either pin it or remove the knob.
- The detector has no workflow, image or chart yet.
- CloudTrail Lake for untraced-apply principals.
- Glidepath should map the `unattested` verdict.
- Provenance should scan all commits, not just the head.
- Core de-duplication of `POST /v1/records`.

## Spec revision between W3 and W4 (2026-11-07) {#spec-revision-between-w3-and-w4}

The spec was revised against the day's analysis and the updated Clearance documents before W4 starts; the note under the byline lists what changed and where. For the managing agent entering W4:

- Read sections 15 to 17 (the O, P and I series) once, then the W4 row of section 11 again: O-1 and C-14 join W4 and land before C-5, I-1 may run in W4 as a small package, and R-9 runs alongside as the owner of the W2 and W3 follow-up lists.
- The W3 gate is still open on two owner steps (G-ARGO-7's exit tests on hangar-prod and the Terraform lab run); W4 may start its code-only packages (C-3, C-4, O-1, C-14, I-1, R-9, A-2's evaluation) before the gate passes, as W3 did, but nothing is called done until the gate's evidence is quoted.
- W5's gate is the product roadmap's phase 2 exit gate in its observation form; W6's gate is the first form of the roadmap's phase 3 and 4 clearinghouse tests. Both are listed in section 11 with their evidence.
- The architecture diagram in section 4 and the build-order diagram in section 11 predate this revision and do not show observation or the clearinghouse; the tables beside them are current.

## Build report: W4 gate closed (2026-11-09) {#build-report-w4-gate-closed}

**Status.** The owner **closed the W4 gate on 2026-11-09**, with one check postponed: the 30-day window. A live packet from the hangar-dev database verifies offline against a witnessed checkpoint, both providers pass conformance, and the coverage statement carries the six states and states observation is blind. That packet covers 11 days, because the chain began on 2026-10-29. **Re-run the 30-day packet on 2026-12-09**, when 30 days of records have each been witnessed as they happened. W5 may start. Clearance 0.36.0 is live on hangar-dev, and the 0.36.0 Argo gate is live on hangar-prod in Warn.

### W3 exit

- **Terraform lab run passed:** cleared, applied and matched, with the first keyless attestation at Rekor index 2050.
- **G-ARGO-7 Warn-mode checks passed on hangar-prod.** A release cleared on its PR matched Argo's render with no second hold (`ch-0a29f11f80f20359`, tree `765d2bfc6461`); a tier 2 hold cleared with one owner approval (`ch-212c050629a9d5d7`); an out-of-band ConfigMap was recorded in 37 seconds (seq 1086); the attestation verifies (Rekor 2156).
- **Not done yet:** force-push and `--strategy apply` refusal (these need Deny), ConfigMap-only tiering, the core-outage test, a tier 3 denial, and the week in Warn.

### Merged

- **Clearance 0.35.0 and 0.36.0:** release stamps (a normal image bump can be tier 1), O-1, C-14, C-3, C-5, C-4, I-1, G-TF-6, G-TF-7, G-ARGO-9, grant carry (#91), R-9 (#83, #85).
- **Glidepath:** G-ARGO-8 code (#237, the required flag not yet set), A-6 check (#238), R-9 (#235, #236), Flight-source promotion (#233), clearance-gate observability YAML (#234).
- **Autopilot:** A-9 first slice (#82), A-6 (#83), A-3 (#84), `limits.tools` (#81).
- **Airframe:** version label on workloads only (#139, chart v0.3.173, live on both clusters), `limits.tools` (#140), pinned bases (#141).
- **Backstage:** squash-merged release commits read as deploys (#251), sign-off status switch (#253), ingestor hold (#254).
- **Tower provenance item:** already closed; Tower does no verification of its own.

### Live evidence

- `ledger: checkpoint witnessed`, size 1266, witness `hangarplatform.dev/witness/hangar-prod`; all 1266 records `checkpointed`.
- A tier 3 change on hangar-prod (`ch-1dda08661ae5b7b1`) shows `kind: person` on both approvals, owner and outside.
- The active grant carries the namespace's other live cleared trees.

### Gate evidence: the live packet

- **Built by** a one-off Job on hangar-dev using Clearance 0.36.0 and the API's read-only database role, on 2026-11-09: 1,266 records, 2026-10-29 to 2026-11-09, 4 exceptions.
- **`clearance verify` exits 0** with the log key, witness policy, trust root and signer identity all supplied outside the packet: record hashes and chain, log signature, the hangar-prod witness's countersignature, 1,266 of 1,266 inclusion proofs, and 7 of 7 keyless attestations pinned to the `clearance-core` service account. The trust root was read from the `hangar-trusted-root` ConfigMap, so it is less independent than the two keys.
- **Negative controls:** one altered record fails the manifest, chain and inclusion checks; a wrong witness key fails the witness check.
- **Coverage statement:** all six states are present (1,264 authorized-and-verified, 2 out-of-band-detected, 0 for the other four). `window_verified` is false by design until a collector reports, and the text states observation is blind.
- **Conformance:** `TestArgoConformance` and `TestTerraformConformance` both pass, as do the harness and the `clearance conformance` command.
- **Bug found by the packet:** seq 1261 is the gate's own PreSync wait Job reported as out-of-band, so every release held for people added a false exception. The fix is [clearance#95](https://github.com/jfillman/clearance/pull/95): the scan skips a Job only when it matches admission's field allowlist and the pinned image, core URL and host alias. Records already written stay in the chain, including seq 1261. Deployed 2026-11-09 as agent 0.36.1 on hangar-prod: the agent dropped its exception for the real, still-present wait Job (UID 2312d8f5) on its next scan. A newly held release adding no exception is still to be observed.

### Decisions by the owner

- **A-2 deferred (2026-11-09); `people-dex` stays.** Dex with dexidp/dex#4611 issues an ID-JAG but takes no service-account input, sets no `act`, and is unmerged. Keycloak 26.8.2 passes with gaps: a plain JWT rather than an ID-JAG, and it needs a live human token, so triggered runs get no delegated identity. Revisit when an issuer ships ID-JAG.
- The C-3 log uses Tessera's POSIX driver on a volume (managing agent's choice, stated to the owner), since Tessera has no PostgreSQL driver. The chain stays the source of truth.

### Descoped or not verified

- A-9 can't serve runs yet: the run backend, people and foreign-cluster auth, most backends, and release plumbing remain. Its canary and cutover have not started.
- A-3 and A-6 have not run live. A-3 doesn't open the `gitops-<app>` PR; A-6 needs its gateway URL, delegate and NetworkPolicy wiring.
- C-3: no every-N-records trigger, no `ledger verify` command, the log isn't served over HTTP, the witness chart isn't published (apron renders plain manifests).
- C-4: Rekor's checkpoint signature and consistency between checkpoints are not verified; `MANIFEST.json` is unsigned.
- G-ARGO-8 is not turned on: it needs a gitops resync first (`gitops-backstage` has no check file).
- G-TF-6 is unproven against a real HCP organization.
- The 30-day window is not proven. Re-run the packet on 2026-12-09 against the gate's wording (the job is a one-off; the steps are in the evidence above).
- PR Lens did not review autopilot#81, clearance#86's final head, or backstage#254 (its analysis failed).

### Waiting on the owner

The force-push and `--strategy apply` tests, the core-outage test, accepting Deny after a week in Warn, and DHCP reservations for the Mac and laptop.

### Carried past the gate, for the W5 session

Closing the gate does not finish these W4 packages. They continue alongside W5:

- **2026-12-09:** the 30-day packet re-run. This is the one item the gate itself still owes.
- **G-ARGO-7:** the remaining exit tests above and the Deny flip. O-3 needs this gate live on hangar-prod; it is live in Warn.
- **G-ARGO-8:** resync the gitops repos, then set `clearance-gate` required.
- **A-3 and A-6:** wiring and live runs.
- **A-9:** the rest of the port, then its 7-day canary and cutover.
- **A-2:** deferred by the owner.

## Build report: W5 gate passed (2026-11-11); work closed (2026-11-12) {#build-report-w5-gate-passed-work}

**Gate.** Passed 2026-11-11 on hangar-dev: an admin's `kubectl apply` recorded with its diff, a Secret write with no value, a revert folded to `reverted`; a stopped collector reported blind with its reason; the lab account's console security-group change recorded out-of-band with the SSO identity and diff, and its removal folded to `reverted` (Clearance 0.40.3). Packets saved under `clearance-packets/`. **O-4 has no hangar-prod side**: hangar-prod has no AWS account; the lab scope is healthy on all ten checks incl. `regions-covered` (an earlier "prod AWS apply" note was wrong).

**Releases after the gate (all live on both clusters unless noted).**

- Clearance 0.41.x–0.42.1: platform GitOps attribution on hangar-prod (Argo CD controller writes, cluster-scoped objects, sync hooks, and Kubernetes' cleanup of a hook: TTL delete, garbage-collector delete and finalizer patch); refusals only 401/403/admission/5xx; controller children with verbs; the narrowed garbage-collector scope.
- 0.41.3: a multi-role machine principal resolved per route (Tower's alert poll 403 fixed).
- 0.42.0 + gateway-v0.6.0: the gateway publishes its bundled agents to the core (`PUT /v1/definitions` `bundled`), so a bundled agent's PR passes `agent-scope` (was AS004).
- 0.43.0 + gateway-v0.7.0: the Evidence `coverage` filter; a store write runs detached from its caller's cancellation, bounded (the 16:01:57 writer-lock loss); A-11 a–f, h, i (below).
- 0.44.0 + gateway-v0.8.0 (hangar-dev live 23:51 UTC; hangar-prod PR #42 merged): the `propose` scope and bulk resolutions; Hangar bundle 1.2.0 (Glidepath contract v1 and v2); glidepath#242 contract v2 live.

**Packages closed in W5.** O-3 (k8s observation + platform GitOps), O-4 (AWS), O-5 (Tower: Exceptions tab, banner, alerts, admin resolutions), C-7 (Glidepath `agent-gates-` retired where Clearance's App reports; no rulesets on the free plan, so Glidepath's readers are the enforcement), R-10 j2 (old `autopilot-system` Postgres and volumes deleted). Hangar roadmap entry and business rules OBS-19–30, AI-06–09 merged (hangar#120).

**A-11 (from the owner's parachute test), built 2026-11-12.** a `airframe.capabilities` AppSpec section · b clipped results say so (runtime-v0.1.7) · c apply merges into onboarding-created files · d `repos-ready` waits for the resync PR · e broker/GitHub errors reach the agent · f parachute instructions (one capabilities call, ≤3 plans, ask instead of dropping, resume prompt, wait for merges in the same run; limits 60 min / 80 calls, owner-accepted with progress reporting) · g `propose` (owner: T1, parachute and app-provisioner enabled, bot-merge detection on app and gitops repos; the person-vs-bot limit accepted: enterprise-first, lab is weaker) · h core write context + gateway 1 s timeout · i run warnings. Also fixed: Glidepath `cicd-validate`/`agent-gates` on large PRs ("Argument list too long", glidepath#243).

**Tower.** Exceptions tab (drawer under the row, confirmation, pager, sort, search; Evidence coverage filter) live as Backstage 1.0.2-d74124d. In review: backstage#264 (Clearance and Autopilot tabs to Tower's design system, clearance-react kit + style ratchet, spacing fixes, gate-exception history across scopes, no double submit) and #265 (bulk resolution UI, stacked on #264).

**Owner-only items open.** Ratify the remaining hangar-prod exceptions in Tower (bulk resolution makes this practical once #265 ships); the MCP switch for the autopilot project directory (the tech directory and /etc/hosts are done), then R-10e alias retirement; the Warn-to-Deny flip.

**Carried.** R-10e/f, A-10 Skyport move, G-ARGO-10 (10c–h incl. the load test), C-13/15/16, A-11 k (PaC "pipelinerun start failure" flake + PaC restart loop dropping events; `WatchCircuitOpen`), hangar-dev control-plane stalls (21:45 UTC mass restart; owner: leave for now), Tower re-run for any finished run, the Backstage image's Trivy findings, the hangar-prod Airframe catalog pin drift, the 30-day packet re-run on 2026-12-09.
