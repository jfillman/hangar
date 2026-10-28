# Autopilot design: running any AI agent workload on Hangar

Autopilot is the sixth Hangar product, beside Tower, Glidepath, Airframe and Apron. This is its design. The plan to build it, and the Airframe work it depends on, are in [roadmap.md](roadmap.md) and [airframe-ai-friendly.md](airframe-ai-friendly.md). Every claim is labelled **Built** (exists and is tested), **Draft** (written, never applied to a cluster), **Proposal** (designed, not written) or **Unverified** (depends on something not checked). Code lives in the [`autopilot` repo](https://github.com/jfillman/autopilot) (decision D8). Clearance's package moves to its own `clearance` repo (section 0.1, D16).

Names, checked against the Hangar Brand System on 2026-09-26. **Autopilot** (a sixth product beside Tower, Glidepath, Airframe and Apron, and the apron component name), **Clearance** (tool gateway and policy; since 2026-10-28 a product of its own, section 0.1) and **Flight recorder** (audit and correlation) are accepted. **Preflight** (evaluation) was decided on 2026-09-26 (D7). Caveat on Flight recorder: "Flight" already means the upper-environment tier in Tower and the Airframe quickstart (Ground and Flight), so define it in the glossary as recording both tiers. Flight recorder is a feature, like Tower's "Ground Control" and "Release Record", so it needs no mark of its own. Clearance, now a product, does.

## 0. Where this stands

| Piece | Status |
|---|---|
| Clearance core: tiers, path and field scope, narrow-only limits, definitions, sessions and the run tree, 23 CEL rules (R000 to R022), hash-chained audit, gateway, model-proxy decisions, triggers, artifacts, the MCP surface | **Built**, 308 tests on `autopilot` main (2026-10-28), no cluster needed |
| `glidepath.*` T0 tools over glidepath-api, with a real HTTP adapter (the first real backend) | **Built** and live-verified on hangar-dev through MCP (autopilot#16, #17) |
| Clearance's deployment gate, evidence record, ledger and packet | **Proposal**, in the Clearance product docs (section 0.1) |
| AppSpec, and the planner that compiles it to a change set (the parachute test: one plain-language request, a new Python app named parachute with four environments, compiled to the exact change set; see [the parachute sentence](airframe-ai-friendly.md)) | **Built** and tested, including against the real XRD schemas, Glidepath's `cicd.schema.json` and a real `helm template` |
| Nine Skyport agent definitions and six Preflight cases | **Built** ([skyport-ai-workloads.md](skyport-ai-workloads.md)) |
| `AgentRun` XRD, composition, `function-agentrun` | **Draft**, never applied |
| Real adapters (GitHub, ArgoCD, Kubernetes, Backstage), authentication, HTTP transports, the model proxy forwarder, the CI gates, the interceptor route | **Proposal** |

## 0.1 Clearance is a product of its own (2026-10-28)

Sources: the Clearance Brief, Clearance Architecture and Clearance Roadmap (published 2026-10-27/28:
[brief](https://claude.ai/artifact/9geoKfKryMxdX7g7pFcxgQ),
[architecture](https://claude.ai/artifact/XuUiKwFagcKiWH5Ag9778R),
[roadmap](https://claude.ai/artifact/XHxJKZTggPve4p7G1KkycN)). Those three are the source for the product. This section records what
they change in Autopilot's design. Where this document and they disagree, they win for Clearance and this document wins for Autopilot.

**What changed.** Clearance is no longer a feature inside Autopilot. It is a standalone Hangar product. Autopilot depends on it and is
its native consumer, and the Hangar lab is its reference deployment. It has two boundaries that write one record:

| Boundary | Question it answers | Status |
|---|---|---|
| Runtime gateway | What may this agent call? Tool tiers T0 to T3, path and field scope, narrow-only limits, CEL policy, hash-chained audit | **Built** (sections 5.3 to 5.5) |
| Deployment gate | May this change land in a protected environment, and can we prove afterwards that it did so under policy? | **Proposal** (Clearance roadmap phases 1 to 2, Dec 2026 to Jan 2027) |

They share one tier vocabulary, one evidence schema, one ledger and the `task_id`, so a packet can show the tool call that drafted a
change beside the clearance that landed it. Runtime tiers T0 to T3 and deployment tiers 0 to 3 share names, not rules: a T2 tool (propose
a PR to an upper environment) produces a change that is tiered again, on its own merits, at the deployment boundary.

**The runtime gateway is a Hangar deliverable whatever happens to the product.** The Clearance roadmap has stop conditions (no budget
owner, an in-house build under two weeks, nobody pays). They decide the deployment-gate business. They do not decide whether Hangar
builds the gateway Autopilot needs: Clearance is Hangar's AI gateway at the very least (owner, 2026-10-28). AP-A2 is built here, not
in a separate lab.

### What it changes in this design

| Area | Before | Now |
|---|---|---|
| Repository | Clearance is a package inside the `autopilot` repo (D8) | Its own `clearance` repo, installable alone (Clearance architecture ch. 1; D16). The split line is proposed below |
| Name and brand | A feature of Autopilot, no mark | A product, like Autopilot; it needs a mark and a glossary entry of its own |
| Audit and Flight recorder | Hash-chained JSON lines, checkpoint anchored "somewhere the writer cannot rewrite" (WORM or Rekor); MinIO object lock (D5) | One **evidence record** schema: every field tagged *verified* (Clearance checked it) or *claimed* (an integration asserted it), a **coverage state** and an **assurance state**. A **ledger of hashes only** in a Tessera log with C2SP checkpoints, countersigned by at least one witness Clearance does not operate, checked by the open `clearance verify`. Content stays on the tenant's storage. Object lock remains for retention, not for integrity. The evidence sink takes every decision unsampled, separate from telemetry |
| Runtime policy | CEL rules evaluated inside Clearance's dispatch loop | The same rules, shaped as an **AuthZEN policy decision point**. The long-term enforcer is Traefik Hub's Sovereign Trust Plane, inline at the request path (open decision, Clearance architecture ch. 13 and 15). Clearance keeps its own gateway until then (see "Runtime boundary on a standard") |
| Agent identity and delegation | Narrow-only limits enforced by Clearance sessions; nothing maps a run pod's service account to the session principal R001 checks | **Taken from a standard (owner, 2026-10-28): ID-JAG** (IETF draft-ietf-oauth-identity-assertion-authz-grant). The run (or Claude Code session) presents its own token to the IdP by RFC 8693 token exchange and receives an ID-JAG: a JWT naming the agent identity (one per AgentDefinition, AP-A4), the human it acts for, and `aud: clearance`. It presents that to Clearance as an RFC 7523 JWT bearer grant. R001's principal is the ID-JAG's subject, not a Clearance-invented mapping. Narrow-only stays Clearance's job at each hop. **Gap, checked 2026-10-28:** Dex has no ID-JAG issuance. dexidp/dex#4611 (issuance on Dex's token exchange, disabled by default) is open and unmerged, and Dex v2.46.1 (2026-10-21) does not ship it. Choosing the issuer is decision D19 |
| Provenance | Not modelled | *Confirmed agent* needs three things: the agents' own GitHub App (D4), a commit signed by an agent Fulcio identity (D1), and agent metadata on the PR. AP-B1 therefore stamps `task_id` and the tool into every agent PR and commit. *Unknown* never resolves to human |
| AgentRun admission | Clearance holds one namespaced Role on `agentruns`; AP-A3's ValidatingAdmissionPolicy (D15) confines provider-kubernetes | Unchanged now, and the one standing exception to "no live write credential" (D3). Later the deployment gate's controller also gates AgentRun claims at admission: the **native entry point**, Clearance roadmap phase 5 (Aug 2027). Until then D15's policy is the containment |
| Deployment-gate policy engine | n/a | Delegates to Kyverno, which Hangar already runs, and stores the rule-set version and verdict with each record. The runtime stays CEL. This agrees with the dead end "OPA or Cedar for the gateway" |
| Preflight | Evaluates agent definitions | Also a classifier input at the deployment boundary: what an agent may propose, decided before the change exists |
| Infisical | Not a tool | A federated gate provider (Clearance phase 2). An agent's call to Infisical's MCP server passes the runtime gateway, which records the intent and stamps its `task_id` into the change request. **Unverified:** whether Infisical's API takes that metadata other than as a comment |
| Consoles | Autopilot plugin (fleet-wide) plus a Tower Agent tab (section 8, 3a) | Unchanged, plus Clearance's own Tower plugin (pending clearances, record search, packet download) in Clearance phase 4 |
| GitHub Apps | One agents' App (D4) | Two Apps with different jobs: the **agents' App** writes PRs as agents (D4, AP-B1); the **Clearance provenance App** reads PRs and commits, posts checks and is a deployment protection rule (checks, pull requests, contents read, deployments; never administration or workflows). Keep them separate: the App that authors a change must not be the one that attests its provenance, and each needs its own rate-limit bucket. The interceptor outer bound (section 5.5) applies to both |

### Repo split (D16, accepted by the owner 2026-10-28)

| `clearance` (the product) | `autopilot` (Hangar's agent runtime) |
|---|---|
| tiers, path and field scope, narrow-only limits, CEL policy rules, sessions and the run tree, dispatch and the gateway, the MCP surface, model-proxy decisions, the audit (becoming the evidence record), later the AuthZEN PDP API and the whole deployment gate | agent definitions and their schema, Preflight cases and harness, the AgentRun XRD, composition and `function-agentrun`, the AppSpec planner (`airframe_plan.py`), the tool backends (`glidepath_api.py`, the coming `airframe.*` tools), triggers and the trigger bridge, the vendored Glidepath and Airframe contracts, `netpol_canary.py`, the smoke tools |

The line: Clearance must install at a customer that runs no Airframe and no Glidepath. Hangar-specific backends would make it a
Hangar component, not a product. Autopilot pins the `clearance` package and registers its tools with it. The tool *policy* (which
tools exist, their tiers, R021 and R022) is Clearance's. The tool *implementations* are Autopilot's.

### Runtime boundary on a standard

Traefik's Sovereign Trust Plane (GA 30 Sep 2026) does at the request path what Clearance's dispatch does in Python: delegation by
token exchange, inline enforcement through an AuthZEN query that returns a structured denial, and a witnessed log of every decision. Hangar's
rule is to adopt leading technology rather than reinvent it. **Verified 2026-10-28:** both clusters run open-source Traefik Proxy
(`docker.io/traefik:v3.7.6`, GatewayClass `traefik`), not Traefik Hub, so STP needs a Hub licence or the feature reaching the open
proxy. Until one of those happens:

- Clearance keeps its own gateway, which is what AP-A2 deploys.
- Dispatch is refactored so the decision is a pure function, from an AuthZEN-shaped request (subject, action, resource, context)
  to a decision with a rule id and a hint. That makes moving behind STP a change of transport, not of policy. Denials already return
  a rule id and a fix hint (section 5.3), which is the structured 403 STP returns.
- The STP evaluation runs against a GA build in the lab (Clearance architecture ch. 14), never early access.

### Timing against the Clearance roadmap

The Clearance roadmap starts in Nov 2026 with two weeks of discovery and no code. The `clearance` repo, the design record and a
**frozen evidence schema** follow by 2026-11-27. Hangar's M3 does not wait for that, with one rule: anything M3 writes that becomes
a record (AP-C1's Flight recorder fields, the session store's audit) is built to the draft evidence schema, because changing the
schema after records exist is the one migration both roadmaps say to avoid.

**Stale numbers in the three sources:** they say 254 tests and 15 deny rules. `autopilot` main on 2026-10-28 has 308 tests and 23
rules, R000 to R022 (R020 field scope, R021 `cicd.yaml` scope, R022 Glidepath app scope were added since).

Three design decisions shaped it, each made with the project owner:
1. **Durable changes are git commits; ephemeral runs are direct requests to Crossplane** (section 1).
2. **It must run any AI agent workload**, not only deploy applications (section 3).
3. **Backend infrastructure is managed the Hangar way, with Modelplane for self-hosted models** (section 6).

## 1. The principle, revised

Hangar already answered the hardest question in this space (`hangar/docs/service-catalog-design.md` §0): no component holds a live Kubernetes write credential, and every mutation is a git commit. That is still right for anything that outlives a run.

It is wrong for a run itself. Committing every session to git would be slow, rate-limited (your GitHub bucket is already shared by four or more tokens and has been exhausted once), noisy in history, and unreviewable, because no human will review a 20-minute sandbox.

So:

> **Durable changes are git commits. Ephemeral runs are direct requests to Crossplane: a namespaced XR, created through the Kubernetes API instead of through git, and reconciled by an already-privileged and already-audited control plane. The requester never touches the underlying resources.**

(Crossplane v2 has no Claims; an `AgentRun` is a namespaced XR like every other Airframe API. What makes it ephemeral is how it is created and when it dies, not its kind.)

That is still your Tower policy (delegate to a system that already audits itself), and still dev-only.

### The ephemerality test

A thing may be created directly through the API instead of as a commit only if **all five** hold. If any fails, it goes through git.

1. It has a **hard deadline** that needs no Clearance to enforce.
2. It **holds no durable state** and reaches the durable plane only as a PR.
3. **One narrowly scoped identity** creates it, in **one reserved namespace**.
4. It can **only narrow** what git grants.
5. It can be **rebuilt** from git plus the task spec.

### What this costs, stated plainly

Clearance now holds one Kubernetes permission: create, get, list, watch, patch and delete `agentruns` in the `autopilot-runs` namespace, on dev clusters. That is a departure from "zero write credentials". It is contained three ways: the permission is one kind in one namespace (a namespaced Role, not a cluster grant), the XRD schema constrains every field, and the composition, not the caller, decides what is created. The caller cannot pass a manifest.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: clearance-agentruns, namespace: autopilot-runs }
rules:
  - apiGroups: ["catalog.hangar.io"]
    resources: ["agentruns"]
    verbs: ["create", "get", "list", "watch", "patch", "delete"]   # patch sets spec.frozen
```

### What stays in git

Agent definitions and policy, profiles and their ceilings, app, gitops and tenants repos, cluster config, the Modelplane hub's inventory (classes, clusters, deployments, services), model routes, the Preflight corpus, gate definitions. Raising authority is always a reviewed commit. Lowering it is immediate and needs no review.

> Industry context: [industry-context.md](industry-context.md) places this design against the emerging "agent substrate" category and records what we adopted from it.

## 2. Principles inherited, and what each forces

| Principle (source) | Consequence |
|---|---|
| Durable writes are commits; ephemeral runs are direct requests (revised, section 1) | Two planes. The ephemeral plane can only narrow the durable one and reaches it only as a PR. |
| Delegated over interactive; lower-only for write RBAC; no pod exec (Tower write-action policy) | The imperative actions are lower-env ArgoCD sync and pipeline re-run, plus creating `AgentRun` XRs. Exec is a tripwire. |
| Never-persisted credentials (token-review-interceptor, ADR-0002) | Repo-scoped GitHub tokens minted per call. Runs get audience-bound projected tokens, never keys. Modelplane's per-caller keys are avoided (section 6). |
| Isolation comes from the TokenReview answer, not a request claim (ADR-0002) | A session's principal is checked server-side; a forged session id is denied (R001, tested). |
| No cluster holds another cluster's credentials; per-cluster repos; lower/upper split (gitops-strategy, ADR-0005) | The write path and runs exist on dev only. The Modelplane hub is a bounded exception (section 6). |
| Cluster-agnostic, generator-driven (ADR-0006) | `components.autopilot` in apron `cluster.yaml`, refused on `type: upper`. New types `hub` and `inference`. |
| Governance stubs are loud (ADR-0003) | `agent-scope` and `agent-identity` start as loud stubs. |
| Bespoke code in Python, no custom controllers | Clearance and `function-agentrun` are Python. The AgentRun composition is a pure function, the same shape as `rolloutwatch`. |
| Test shared compositions via a copy | Nothing shared is edited. AgentRun is a new XRD, first exercised through one XR's `compositionRef`. |
| Live verification; a pass can mean the gate is off | Every phase ends with a negative test. A network-policy canary gates `autopilotReady`. |
| Multi-arch | Clearance and the function build for arm64 and amd64. |

## 3. The workload model

**AgentDefinition (durable, git)** says what an agent is: kind, identity, tier ceiling, tools, repos, models, network reach, compute class, limits, image (by digest), framework, sandbox class, sidecars, triggers. Today it is reviewed YAML validated by `schemas/agent-definition.schema.json`. Later it becomes an `Agent` XRD, so Tower generates a *New Agent* form like every other XRD (Phase C).

**AgentRun (ephemeral, namespaced XR)** is one bounded instance: the definition narrowed by its requested limits, with a deadline.

| Shape | Trigger | Durable part | Ephemeral part |
|---|---|---|---|
| Task | human, API, agent | definition | AgentRun |
| Session | human in Tower | definition | AgentRun (interactive) |
| Service | always on | definition + Rollout | none: it is an ordinary application |
| Scheduled | interval in the definition | definition + schedule | AgentRun per tick |
| Event | alert or webhook | definition + trigger | AgentRun per event |
| Team | a parent run | definitions | child AgentRuns, each narrower than its parent |

Services reuse the existing application path, so nothing new is invented for them. Holmes is already one.

### 3.1 Additions from the substrate review (2026-09-26)

- **Stable agent identity.** An agent has one identity per `AgentDefinition`, independent of any run. Runs inherit it. It is the key for per-agent policy, for "everything this agent ever did" in the audit chain, and for any future memory scope. Task: AP-A4.
- **Model version is part of the record.** Each run records the exact model id/version it used, next to its tools, decisions and Preflight result, so a change in behaviour can be tied to a model change.
- **Cost accounting.** Tokens and compute are recorded per run, per agent and per task tree, and shown in Tower. Task: AP-C2.
- **Optional persistent state (session and team shapes only).** Default stays stateless, so a run's state is its Clearance channel and its artifacts. An agent may opt in to a workspace volume that can be snapshotted and resumed. Guards: size cap, retention TTL, a scan before restore (memory poisoning is the risk), and the volume belongs to the agent identity, never to another agent. Task: AP-D1, gated on U12.
- **Sandbox substrate.** Before building more pod-rendering code, decide whether `function-agentrun` should render the upstream Kubernetes Agent Sandbox object (warm pools, gVisor/Kata, suspend/resume) instead of a raw pod. Answer: U11, before AP-A3.
- **Rejected: a monolithic `AgentWorkspace` resource** that grants cpu, memory, namespaces and tools in one object. It merges what a run may do with what the platform grants, and it would put `kubectl` and `argocd` inside the sandbox. `AgentRun` plus an optional state volume keeps them apart.

### Runtime contract (any framework)

Environment: `HANGAR_RUN_ID`, `_TASK_ID`, `_SESSION_ID`, `_AGENT`, `_EXPIRES_AT`, `_LIMITS`, `_INPUT`, `_OUTPUT_DIR`, `_WORKSPACE`, `CLEARANCE_URL`, `MODEL_PROXY_URL` (each URL only if the network mode allows it). Files: `/workspace`, `/run/output`, tokens under `/var/run/hangar` (audiences `clearance` and `model-proxy`). On SIGTERM, checkpoint within 30 seconds. That is the whole contract, which is why Claude Agent SDK, LangGraph and a hand-rolled agent all fit.

### Sandbox and compute classes

- `standard`: pod security `restricted`, non-root, read-only root filesystem, all capabilities dropped, default-deny egress with only the exceptions the network mode names, a quota that forbids Secrets and Services.
- `hardened`: adds a runtime class (gVisor or Kata). **If the cluster has none, the run is Rejected. It is never silently downgraded.** The home lab's local clusters have none, so `hardened` is a production-cluster feature.
- Compute classes (`small`, `medium`, `large`, `gpu`) are declared per cluster in the function's input; a class the cluster lacks is Rejected. This borrows Modelplane's idea of a platform team publishing hardware classes that workloads request by name.
- Network modes, ordered by reach: `none`, `clearance`, `clearance+model`, `allowlist` (explicit CIDRs, never `/0`).
- Agent images are untrusted code. They are signed by Glidepath, referenced by digest (the XRD schema rejects a tag), and admission verifies the signature.

## 4. Components and repo changes

| Repo / path | Change | Phase | Status |
|---|---|---|---|
| `autopilot/src/clearance`, moving to the `clearance` repo (D16) | Gateway core, policy, audit, sessions, model proxy core, triggers, Preflight, MCP surface (triggers and Preflight stay in `autopilot`, section 0.1) | A to C | **Built** (308 tests) |
| `autopilot/airframe-drafts/xrds/agentrun.yaml` | AgentRun XRD | A | **Draft** |
| `autopilot/airframe-drafts/functions/function-agentrun/` | Pure `compose()` plus a gRPC wrapper on the real SDK | A | **Built** (tests) and **Draft** (never run by Crossplane) |
| `airframe/xrds`, `compositions`, `functions` | Move the drafts in through a worktree | A | Proposal |
| `provider-kubernetes-applied-resources` (gitops-cluster-dev) | Grants for Namespace, ResourceQuota, NetworkPolicy, ServiceAccount, batch/Job | A | Proposal |
| `apron/cluster.yaml.example`, `hack/customize-cluster.sh`, `apron/55-autopilot/` | `components.autopilot`, refused on upper; types `hub` and `inference` | A | Proposal |
| `gitops-cluster-dev` cluster registry | `autopilotReady`, set only after the network-policy canary passes | A | Proposal |
| `glidepath/platform/broker` (token-review-interceptor) | `/agent-installation-token` beside `/github-installation-token` | B | Proposal |
| ArgoCD RBAC | `role:clearance-read`, `role:clearance-lower` | B | Proposal |
| `glidepath` releaseGuardrails | `agent-scope`, `agent-identity` (loud stubs first) | B | Proposal |
| `glidepath/platform/dora-exporter` | `author=agent\|human` label | C | Proposal |
| `backstage` (Tower) | Agent tab: session-type runs and chat, scoped to one app (reuses the Autopilot plugin's backend, the same relationship Tower's Glidepath tab has to Glidepath) | C | Proposal |
| A new **Autopilot** Backstage plugin, standalone-installable beside Tower | Fleet-wide console: every run across every agent, budgets, the breaker, Preflight results, audit | C | Proposal |
| Airframe A+ program (contract bundle, `airframe validate`, ownership split, `airframe.*` tools) | see [airframe-ai-friendly.md](airframe-ai-friendly.md); Autopilot's planner and tools depend on it | M0 to M3 | Proposal; planner **Built** |
| Trigger runner and trigger bridge | interval and broker-event agents | M4 | Logic **Built**; runners Proposal |
| Real backends and auth adapters | GitHub via the interceptor, ArgoCD, the Kubernetes API for `AgentRun` XRs, Backstage MCP federation, Tower and TokenReview auth | A to B | Proposal (interfaces and fakes **Built**) |

## 5. Concrete artifacts

### 5.1 The AgentRun function: expiry and failing closed

`function-agentrun` is one pure function, `compose(xr, observed, now, cfg)`, so it is tested without a cluster. Two properties matter most, and both are tested:

- **Expiry needs no Clearance.** Past `spec.expiresAt` it renders nothing, and Crossplane garbage-collects the namespace. A dead or compromised gateway cannot leave a run alive. The Job's `activeDeadlineSeconds` is anchored to the XR's creation time, so it does not drift between reconciles.
- **It fails closed.** A hardened sandbox on a cluster without a runtime class, a compute class the cluster lacks, a TTL over the cluster's cap, an allowlist of `0.0.0.0/0`, or an input over 4 KiB is `Rejected` and renders nothing.

Lifecycle: `Provisioning`, `Running`, `Succeeded` or `Failed` (drained after a grace period), `Frozen` (egress cut, run kept for forensics for a hold period), `Expired`, `Rejected`.

It composes only `provider-kubernetes` Objects, because Crossplane v2 rejects a namespaced XR composing a cluster-scoped resource, the same reason SecretStore wraps `ClusterSecretStore`. **The run namespace must never carry `hangar.io/ephemeral-env`**: the existing PR-namespace TTL sweep deletes namespaces with that label when no owning ArgoCD Application exists, and would reap live runs. A test asserts the label is absent.

### 5.2 AgentDefinition

See `autopilot/agents/*.yaml` (five shipped: a task agent, a researcher, an orchestrating team, an event-triggered triage agent, a scheduled reviewer). Baseline deny paths (`.tekton/**`, `cicd.yaml`, `CODEOWNERS`, `.github/**`, `**/appproject*.yaml`) apply to every agent and **cannot be removed** by a definition, so an agent can never edit the controls that constrain it.

### 5.3 Policy as CEL

Twenty-two deny rules plus R000, first match wins, each with a stable id and a fix hint that goes back to the agent, so it can retry against a deterministic gate instead of guessing. Any evaluation error is R000 and a deny. The rule id plus hint is already the shape of an AuthZEN structured denial (section 0.1).

| Id | Denies when |
|---|---|
| R001 | the caller is not the session's principal |
| R002 | the tool is a tripwire (exec, secrets, IAM, upper sync); also trips the breaker |
| R003 | unknown tool |
| R004 / R005 | session expired / breaker tripped |
| R006 | tool not in the session's tool set |
| R007 | tier above the ceiling (a propose-only tool needs T1, not more), or requested limits that widen |
| R008 | required arguments missing |
| R009 / R010 / R011 | tool-call, GitHub-call or open-PR budget exhausted |
| R012 | a lower-only tool aimed at an upper environment |
| R013 | a T2 tool that is not propose-only |
| R014 | repo not on the allowlist |
| R015 | the change touches a protected path (traversal-safe) |
| R016 | a spawn refused: depth, children budget |
| R017 | an application API not on the agent's `apis.allow` list |
| R018 | chat tools used outside a session agent |
| R019 | an artifact over 1 MiB |
| R020 | a change to a field outside the definition's field scope, or on `BASELINE_DENY_FIELDS` (`/extraManifests`, `/networkPolicy`, `/httpRoute`, `/release`, `/releaseTracking`, `/rollout/image`) |
| R021 | a `cicd.yaml` change outside Glidepath's field scope (vendored `cicd_scope.py`) |
| R022 | a `glidepath.*` call for an app not in the profile's `glidepath.apps` |

Tools, by tier: **T0** `catalog.read`, `metrics.query`, `logs.query`, `argo.app.get`, `app.api.get`, `artifact.get`, `chat.recv`, `chat.send`. **T1** `repo.pr.open`, `xr.request`, `argo.sync.lower`, `pipeline.rerun`, `artifact.put`, `run.spawn`, `run.close`, `human.request`. **T2 (propose only)** `repo.pr.open_upper`. **T3** never exposed; the names exist only as tripwires. **T0, built:** six `glidepath.*` tools over glidepath-api (`contract`, `runs.list`, `run.get`, `logs.get`, `explain`, `releases.get`). The `airframe.*` tools (capabilities, describe, explain, plan, apply, status, verify) are the M3 deliverable: the read-only half first (AF-8a), `apply` after the agents' GitHub App (AF-8b). The planner behind `plan` is built.

### 5.4 Narrow-only, and teams

Requested limits, or a child run, may only narrow what they inherit: tier, time, each budget, tools, models, network reach, compute. A child starts from what its parent has *left* and reserves its budget from the parent. There is a property test: in 200 random sequences of spawn, spend and close, no session overspends and no tree exceeds what the root was granted. Depth is capped at 3.

### 5.5 Tokens, ArgoCD, audit

- **Interceptor route** `POST /agent-installation-token`, authenticated by TokenReview as Clearance's service account. It enforces an **independent outer bound** (an interceptor-side repo allowlist; permissions limited to `contents`, `pull_requests`, check reads; never `administration` or `workflows`), so a Clearance bug cannot widen it.
- **ArgoCD**: `p, role:clearance-lower, applications, sync, *-lower/*, allow`. Tower's `role:tower-sync` is `*/*` today. **Unverified**: that the glob matches your `<app>-lower` AppProject names.
- **Audit**: hash-chained JSON lines, arguments stored only as a hash. The chain proves consistency, not completeness: truncating the tail leaves a valid chain, so `checkpoint()` must be anchored somewhere the writer cannot rewrite. Tests cover edit, delete, reorder, truncation and rewrite-after-anchor. **Superseded design for the anchor (2026-10-28, section 0.1):** each audit line becomes an evidence record; the Clearance ledger commits only their hashes to a Tessera log; checkpoints are countersigned by a witness Clearance does not operate, which never accepts a smaller tree, so even the key holder cannot truncate and re-sign unseen. `clearance verify` recomputes the hashes from the tenant's own files and names an altered line.

### 5.6 Preflight

A case names deterministic verifiers, a path scope, and denial and token budgets. Two guards against a harness that always says yes: a run that changed nothing cannot pass, and every case must fail a synthetic unfixed run. Seed cases come from your own dead-ends list (liveness probe path, `function-auto-ready`, RabbitMQ 4.1 versus operator 2.23, hand-applied XRD reverted by selfHeal, Trivy-gated Java pins, the broken canary). Two are written (`autopilot/preflight/cases/`); the rest are listed in the diagram. Other agent types get their own suites, graded by deterministic checks such as schema-valid output and no forbidden tool calls.

## 6. Backend infrastructure

### 6.1 Inventory: what backs an agent, and who manages it

| Backend | Managed by | Plane | Exists? |
|---|---|---|---|
| Agent runs | `AgentRun` XR, `function-agentrun` | ephemeral | Draft |
| Clearance and the model proxy | `InfraService` (`gitops-infra-clearance`) | durable | pattern **Built** (`skyport-broker`) |
| State: Postgres, Redis, RabbitMQ | Airframe components, `attach` mode per run | durable | **Built** (CloudNativePG 1.30.1, RabbitMQ operators) |
| Object storage for artifacts | MinIO (already in the observability stack) | durable | **Built** |
| Vector store | pgvector on CloudNativePG | durable | **Unverified** (extension availability in the CNPG image) |
| Provider API keys | Infisical, External Secrets | durable | **Built** (`provider-infisical`) |
| Hosted models | model proxy route to the provider | durable config | Proposal |
| Self-hosted models | **Modelplane** (a separate fleet) | durable inventory, runtime replicas | Proposal |
| Telemetry, DORA | existing otel, Loki, Tempo, Prometheus, dora-exporter | durable | **Built** |

The model proxy's routes are durable git (`autopilot/config/model-routes.example.yaml`): an alias maps to a backend. A run names an alias and never holds a key or a URL.

### 6.2 What Modelplane is

Read from its repo (`b3b3f2f`, 2026-09-25) and docs, not from memory. (`modelplane.io` refused my connection; the project is at [modelplane.ai](https://modelplane.ai/).)

- An open-source control plane for AI inference, **v0.1**, API `modelplane.ai/v1alpha1`, Apache 2.0, from Upbound. It requires Crossplane on a **control cluster** above a fleet of **inference clusters**.
- **Built the way Hangar is**: the entire system is Python composition functions with no custom controllers; the fleet scheduler is "a pure function of observed state" using CEL over typed hardware attributes; two personas share one API.
  - Platform team: `InferenceClass` (a hardware recipe), `InferenceCluster` (provisioned on EKS, GKE, AKS, Nebius or Vultr, or `source: Existing`), `InferenceGateway` (OpenAI and Anthropic APIs).
  - ML team: `ModelDeployment`, `ModelService`, `ModelCache`.
  - Composed: `ModelReplica`, `ModelEndpoint`.
- A `ModelEndpoint` can also point at an external provider, so one `ModelService` can front self-hosted replicas and a hosted provider with weighted traffic and failover.
- The gateway supports per-caller API keys (stamping identity on requests and usage records) and a **"run behind another gateway"** mode that trusts an `x-modelplane-caller` header.
- Requirements on an inference cluster: Kubernetes 1.34.2 or newer with DRA, NVIDIA drivers, a load balancer, a `ReadWriteMany` StorageClass for caches.
- AWS EKS is provisioned natively. **OCI (OKE) is "planned"**, so it works today only by bring-your-own with `source: Existing`.

### 6.3 Recommendation: adopt it, behind one contract, later

Building fleet scheduling, GPU cluster provisioning, weight caching and an inference gateway is exactly what Modelplane is. Hangar should not. But it is v0.1, so:

- **The only thing Hangar depends on is an OpenAI or Anthropic compatible URL.** Hosted providers and Modelplane are interchangeable behind the model proxy. Nothing in phases A to C needs Modelplane, and hosted models come first.
- Pin the version (git-source pinned tag, your standing rule), and treat its `v1alpha1` API as able to change.
- A contract test in Preflight: a completion through the proxy against the inference gateway.

### 6.4 Where it collides with your principles

These are explicit decisions, not details:

1. **It holds credentials for other clusters.** The hub reconciles inference clusters, so it holds their credentials (and, for provisioning, broad cloud credentials; the GKE tutorial needs `projectIamAdmin`). That contradicts "no cluster holds another cluster's credentials". **Containment:** inference is its own fleet class with its own hub *per environment* (a dev hub never holds prod credentials), dedicated cloud accounts, and inference clusters that hold no app data, agent data or Hangar secrets. Prefer `source: Existing` clusters built by Terraform in a controlled account, so the hub holds only a kubeconfig, not cloud admin.
2. **It owns each inference cluster and installs Envoy Gateway.** It assumes exclusive ownership and owns the `GatewayClass`, so it cannot share a cluster with your Hangar clusters, which run Traefik (`GatewayClass traefik`, verified 2026-10-28). Inference clusters are dedicated: registry type `inference`, not `dev` or `upper`.
3. **It needs its own Crossplane packages.** You have been bitten by package dependency-lock corruption on a shared Crossplane. The hub is its own cluster (registry type `hub`), never the Airframe Crossplane.
4. **`source: Existing` takes a kubeconfig Secret**, a persisted credential, against never-persisted. **Unverified:** whether short-lived cloud auth (an exec plugin) works there. If not, this is an accepted, documented exception on a bounded fleet, delivered by External Secrets and never in git.

### 6.5 Managed the Hangar way

- Hub config (`InferenceClass`, `InferenceCluster`, `InferenceGateway`, `ModelDeployment`, `ModelService`) is **durable and lives in git**, in `gitops-cluster-<hub>` from an apron template of type `hub`, with a tenants repo for ML teams' namespaced resources. Modelplane is installed by a pinned ArgoCD Application.
- Replicas and scaling are **runtime**, derived by Modelplane and KEDA. They are not committed.
- Cloud and provider keys come from Infisical through External Secrets. Modelplane's own tutorial has you `kubectl create secret`; here it is an `ExternalSecret`.
- **Budgets stay in the model proxy.** Modelplane advertises no usage caps or token metering. Budgets, model allowlists and per-run caller identity are the proxy's job. Modelplane's usage records carry the caller, so setting `x-modelplane-caller` to the session id lets them be joined to `task_id`. **Unverified:** what those records actually contain.
- GPU metrics and Modelplane's engine metrics feed the same Prometheus.

## 7. Failure modes

| Failure | What happens | Mitigation |
|---|---|---|
| Clearance is down | Agents cannot act. Runs still end on time. People, ArgoCD and git are unaffected | Fail closed; expiry is the composition's job |
| Clearance is compromised | Can create AgentRuns (bounded by schema and composition) and PRs as any definition. Cannot merge upper, exec, or read secrets | Namespaced Role; interceptor outer bound; branch protection; `agent-scope`; hash-chained audit |
| A run is compromised | Reaches only Clearance and the model proxy | Default-deny egress, no secrets in the namespace, hardened class where available |
| Runaway spawn loop | Bounded | Depth 3, children budget, reserved budgets |
| Agent burns GitHub or model budget | Shared bucket starves CI (has happened) | Per-session budgets, a separate GitHub App, the breaker; token overrun trips it |
| Time-driven re-invocation does not fire | Expiry is late | **Unverified**: the function sets a response TTL. Test first; fallback is an independent sweep |
| PR-namespace sweep reaps runs | Live runs killed | Never use `hangar.io/ephemeral-env`; tested |
| NetworkPolicy not enforced on a cluster | Egress claim is false | Canary gates `autopilotReady`. kiac-dev enforces it (Cilium; verified 2026-10-09), so the canary is expected to pass there |
| Hub compromised | Holds inference cluster credentials | Per-environment hubs, dedicated accounts, no app data on those clusters |
| Modelplane API changes (v1alpha1) | Backend breaks | Pinned; the contract is the URL; contract test |
| Prompt injection via logs, PR text, repo content | Agent steered | Tool output is data; T2 is propose-only; T3 is never |
| In-memory sessions lost on restart | Sessions end | Safe direction; single replica for now. AP-A2 adds a durable session store |
| Ledger witness unreachable | Records keep being written but no new checkpoint is published | Each record carries an assurance state (`checkpointed`, `recorded-not-checkpointed`, `not-recorded`); the packet reports the window; deployment tier 3 waits by default (Clearance architecture ch. 6) |
| No pod exec | Humans cannot shell into a run | By policy; debug via output, logs and the audit record. Decide if acceptable |

## 8. Open decisions

1. **Commit signing for agent PRs.** `provenance` verifies human `gitsign` against public Sigstore. Options: sign with the self-hosted Fulcio (workload trust root) and extend the gate, or exempt agent PRs. **Decided (D1): the first**, under a new Hangar root CA. It is also one of the three signals Clearance's provenance detector needs for *confirmed agent* (section 0.1). Never mix the two trust roots.
2. **AgentRun as an XR, a bare Job, or a controller.** **Recommend the XR.** A Job alone loses status, policy and Tower visibility; a custom controller repeats a reflex you already decided against, and Modelplane is evidence it is unnecessary.
3. **Standalone Clearance or a Backstage module.** **Decided (D3): standalone**, federating Backstage's MCP actions. Since 2026-10-28 it is a product with its own repo (D16).
3a. **Where the frontend lives: a new Backstage plugin, or a Tower tab. Decided 2026-09-27: a new, standalone-installable Autopilot plugin beside Tower**, not a tab inside it. Tower's whole chrome (`EnvPicker`, `AppPicker`, the release matrix, promotion order) is built around one app's environments and releases; an `AgentRun` does not live at that coordinate; it can be triggered by an event with no app in the picker, a scheduled task touching several repos, or a team fanning out across them. Forcing that into Tower's app-scoped tabs would mean inventing a fake app context, or a second incompatible navigation model bolted onto Tower's sidebar. The precedent already in this codebase: Glidepath is a standalone-installable CI/CD engine, and Tower's Glidepath tab is a thin reuse of Glidepath's own backend routes, not a reimplementation. Autopilot gets the same relationship: a fleet-wide console (every run, every agent, budgets, the breaker, Preflight results, audit) in its own plugin, and a narrow Tower "Agent" tab for the one case that is genuinely app-scoped and conversational (a session-type agent like `gate-copilot` chatting inside the app a human is already looking at), backed by the Autopilot plugin's own API, exactly like the Glidepath tab is backed by Glidepath's.
4. **A separate GitHub App for agents**, so their rate-limit bucket is their own. **Decided (D4), reconfirmed 2026-10-28.** It is not the Clearance provenance App (section 0.1).
5. **Audit store.** MinIO object lock must be enabled when the bucket is created. **Revised 2026-10-28:** integrity comes from the witnessed ledger; object lock is retention only (D5, section 0.1).
9. **Runtime boundary: Clearance as an AuthZEN PDP behind Traefik Hub, or its own gateway.** Open (Clearance architecture ch. 15). Recommendation: PDP, keeping the own gateway as the fallback. Hangar runs Traefik Proxy, not Hub, so the own gateway is what ships now.
6. **Hub isolation and credentials** (section 6.4). Decide before any hub exists.
7. **When to trial Modelplane.** After phase D, once agents run and their spend is bounded, and on a dedicated kind cluster first (its getting-started guide targets local kind, but it needs a cloud account for GPUs).
8. **Debugging without exec.** Accept it, or build a recorded, time-boxed, approved break-glass as its own initiative, never a normal backlog item (your policy).

## 9. Built versus not

`cd ~/tech/autopilot && ./.venv/bin/python -m pytest -q` runs **308 tests** with no cluster (2026-10-28; at the time of this section, 255): scope and traversal safety, narrow-only limits, definition schema, sessions and the run tree (including the property test), 16 CEL rules one at a time and failing closed, hash-chain tamper detection, the gateway end to end with fakes, the model proxy, triggers, Preflight, the MCP surface on the mcp SDK v2, the AgentRun manifest against the XRD's own schema, and the composition function including its gRPC wrapper on the real SDK.

**Not built:** the real GitHub, ArgoCD, Kubernetes and Backstage adapters; the auth adapters; MCP over HTTP; the model proxy's HTTP forwarder; the interceptor route; the CI gates; the drafts have never been applied or rendered by Crossplane. **Unit tests prove the composition logic, not that provider-kubernetes accepts what it renders.**

## 10. What I did not verify

- Whether the Backstage `mcpActions` endpoint is live on any cluster.
- Whether HolmesGPT can call an MCP server authenticated by a service-account token, and forward a task id.
- Whether Tower's Tier 1 write actions were live-verified after the 2026-09-15 handoff.
- The provenance gate's internals and where the per-app signer allowlist lives.
- The `*-lower/*` ArgoCD glob against your AppProject names.
- Time-driven re-invocation through the function response TTL on your Crossplane version.
- Whether provider-kubernetes Objects for Namespace, ResourceQuota, NetworkPolicy and Job apply cleanly with the grants drafted.
- pgvector in the CloudNativePG image.
- The upstream Kubernetes Agent Sandbox and GKE Agent Substrate: known only from a third-party survey, not read at source (U11).
- Modelplane's usage-record contents, short-lived-credential support for `Existing` clusters, and behaviour on your Kubernetes versions (prod is 1.37; the dev cluster's version I did not check).

## Sources

- [Modelplane](https://modelplane.ai/), the [repository](https://github.com/modelplaneai/modelplane), and [Building Modelplane on Crossplane](https://blog.crossplane.io/building-modelplane/).
- Modelplane docs read from the repository: `overview/how-it-works`, `platform/inference-cluster`, `platform/inference-gateway`, `platform/providers`, `models/model-endpoint`, `getting-started/build-the-platform`.
