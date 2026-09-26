# Autopilot design: running any AI agent workload on Hangar

Autopilot is the sixth Hangar product, beside Tower, Glidepath, Airframe and Apron. This is its design. The plan to build it, and the Airframe work it depends on, are in [roadmap.md](roadmap.md) and [airframe-ai-friendly.md](airframe-ai-friendly.md). Every claim is labelled **Built** (exists and is tested), **Draft** (written, never applied to a cluster), **Proposal** (designed, not written) or **Unverified** (depends on something not checked). Code lives in `~/tech/clearance` today and moves to a new `autopilot` repo (decision D8).

Names, checked against the Hangar Brand System on 2026-09-26. **Autopilot** (a sixth product beside Tower, Glidepath, Airframe and Apron, and the apron component name), **Clearance** (tool gateway and policy) and **Flight recorder** (audit and correlation) are accepted. **Checkride** (evaluation) is still open (Airworthiness is the recommended alternative; decision D7). Caveat on Flight recorder: "Flight" already means the upper-environment tier in Tower and the Airframe quickstart (Ground and Flight), so define it in the glossary as recording both tiers. Clearance and Flight recorder are features inside Autopilot, like Tower's "Ground Control" and "Release Record", so they need no mark of their own.

## 0. Where this stands

| Piece | Status |
|---|---|
| Clearance core: tiers, path scope, narrow-only limits, definitions, sessions and the run tree, 19 CEL rules, hash-chained audit, gateway, model-proxy decisions, triggers, artifacts, the MCP surface | **Built**, 255 tests, no cluster needed |
| AppSpec, and the planner that compiles it to a change set (the parachute test) | **Built** and tested, including against the real XRD schemas, Glidepath's `cicd.schema.json` and a real `helm template` |
| Nine Skyport agent definitions and six Checkride cases | **Built** ([skyport-ai-workloads.md](skyport-ai-workloads.md)) |
| `AgentRun` XRD, composition, `function-agentrun` | **Draft**, never applied |
| Real adapters (GitHub, ArgoCD, Kubernetes, Backstage), authentication, HTTP transports, the model proxy forwarder, the CI gates, the interceptor route | **Proposal** |

Three design decisions shaped it, each made with the project owner:
1. **Durable changes are git commits; ephemeral runs are claims to Crossplane** (section 1).
2. **It must run any AI agent workload**, not only deploy applications (section 3).
3. **Backend infrastructure is managed the Hangar way, with Modelplane for self-hosted models** (section 6).

## 1. The principle, revised

Hangar already answered the hardest question in this space (`hangar/docs/service-catalog-design.md` §0): no component holds a live Kubernetes write credential, and every mutation is a git commit. That is still right for anything that outlives a run.

It is wrong for a run itself. Committing every session to git would be slow, rate-limited (your GitHub bucket is already shared by four or more tokens and has been exhausted once), noisy in history, and unreviewable, because no human will review a 20-minute sandbox.

So:

> **Durable changes are git commits. Ephemeral runs are declarative claims to Crossplane, an already-privileged and already-audited control plane. The requester never touches the underlying resources.**

That is still your Tower policy (delegate to a system that already audits itself), and still dev-only.

### The ephemerality test

A thing may be created as a claim instead of a commit only if **all five** hold. If any fails, it goes through git.

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
  - apiGroups: ["catalog.idp.io"]
    resources: ["agentruns"]
    verbs: ["create", "get", "list", "watch", "patch", "delete"]   # patch sets spec.frozen
```

### What stays in git

Agent definitions and policy, profiles and their ceilings, app, gitops and tenants repos, cluster config, the Modelplane hub's inventory (classes, clusters, deployments, services), model routes, the Checkride corpus, gate definitions. Raising authority is always a reviewed commit. Lowering it is immediate and needs no review.

> Industry context: [industry-context.md](industry-context.md) places this design against the emerging "agent substrate" category and records what we adopted from it.

## 2. Principles inherited, and what each forces

| Principle (source) | Consequence |
|---|---|
| Durable writes are commits; ephemeral runs are claims (revised, section 1) | Two planes. The ephemeral plane can only narrow the durable one and reaches it only as a PR. |
| Delegated over interactive; lower-only for write RBAC; no pod exec (Tower write-action policy) | The imperative actions are lower-env ArgoCD sync and pipeline re-run, plus AgentRun claims. Exec is a tripwire. |
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

**AgentRun (ephemeral, claim)** is one bounded instance: the definition narrowed by a claim, with a deadline.

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
- **Model version is part of the record.** Each run records the exact model id/version it used, next to its tools, decisions and Checkride result, so a change in behaviour can be tied to a model change.
- **Cost accounting.** Tokens and compute are recorded per run, per agent and per task tree, and shown in Tower. Task: AP-C2.
- **Optional persistent state (session and team shapes only).** Default stays stateless, so a run's state is its Clearance channel and its artifacts. An agent may opt in to a workspace volume that can be snapshotted and resumed. Guards: size cap, retention TTL, a scan before restore (memory poisoning is the risk), and the volume belongs to the agent identity, never to another agent. Task: AP-D1, gated on U12.
- **Sandbox substrate.** Before building more pod-rendering code, decide whether `function-agentrun` should render the upstream Kubernetes Agent Sandbox object (warm pools, gVisor/Kata, suspend/resume) instead of a raw pod. Answer: U11, before AP-A3.
- **Rejected: a monolithic `AgentWorkspace` resource** that grants cpu, memory, namespaces and tools in one object. It merges what a run may do with what the platform grants, and it would put `kubectl` and `argocd` inside the sandbox. `AgentRun` plus an optional state volume keeps them apart.

### Runtime contract (any framework)

Environment: `HANGAR_RUN_ID`, `_TASK_ID`, `_SESSION_ID`, `_AGENT`, `_EXPIRES_AT`, `_LIMITS`, `_INPUT`, `_OUTPUT_DIR`, `_WORKSPACE`, `CLEARANCE_URL`, `MODEL_PROXY_URL` (each URL only if the network mode allows it). Files: `/workspace`, `/run/output`, tokens under `/var/run/hangar` (audiences `clearance` and `model-proxy`). On SIGTERM, checkpoint within 30 seconds. That is the whole contract, which is why Claude Agent SDK, LangGraph and a hand-rolled agent all fit.

### Sandbox and compute classes

- `standard`: pod security `restricted`, non-root, read-only root filesystem, all capabilities dropped, default-deny egress with only the exceptions the network mode names, a quota that forbids Secrets and Services.
- `hardened`: adds a runtime class (gVisor or Kata). **If the cluster has none, the run is Rejected. It is never silently downgraded.** kind and Apple `container` clusters have none, so `hardened` is a production-cluster feature.
- Compute classes (`small`, `medium`, `large`, `gpu`) are declared per cluster in the function's input; a class the cluster lacks is Rejected. This borrows Modelplane's idea of a platform team publishing hardware classes that workloads request by name.
- Network modes, ordered by reach: `none`, `clearance`, `clearance+model`, `allowlist` (explicit CIDRs, never `/0`).
- Agent images are untrusted code. They are signed by Glidepath, referenced by digest (the XRD schema rejects a tag), and admission verifies the signature.

## 4. Components and repo changes

| Repo / path | Change | Phase | Status |
|---|---|---|---|
| `/Users/jerf/tech/clearance` (new) | Gateway core, policy, audit, sessions, model proxy core, triggers, Checkride, MCP surface | A to C | **Built** (255 tests) |
| `clearance/airframe-drafts/xrds/agentrun.yaml` | AgentRun XRD | A | **Draft** |
| `clearance/airframe-drafts/functions/function-agentrun/` | Pure `compose()` plus a gRPC wrapper on the real SDK | A | **Built** (tests) and **Draft** (never run by Crossplane) |
| `airframe/xrds`, `compositions`, `functions` | Move the drafts in through a worktree | A | Proposal |
| `provider-kubernetes-applied-resources` (gitops-cluster-dev) | Grants for Namespace, ResourceQuota, NetworkPolicy, ServiceAccount, batch/Job | A | Proposal |
| `apron/cluster.yaml.example`, `hack/customize-cluster.sh`, `apron/55-autopilot/` | `components.autopilot`, refused on upper; types `hub` and `inference` | A | Proposal |
| `gitops-cluster-dev` cluster registry | `autopilotReady`, set only after the network-policy canary passes | A | Proposal |
| `glidepath/platform/broker` (token-review-interceptor) | `/agent-installation-token` beside `/github-installation-token` | B | Proposal |
| ArgoCD RBAC | `role:clearance-read`, `role:clearance-lower` | B | Proposal |
| `glidepath` releaseGuardrails | `agent-scope`, `agent-identity` (loud stubs first) | B | Proposal |
| `glidepath/platform/dora-exporter` | `author=agent\|human` label | C | Proposal |
| `backstage` (Tower) | Agent tab: runs, audit, denials | C | Proposal |
| Airframe A+ program (contract bundle, `airframe validate`, ownership split, `airframe.*` tools) | see [airframe-ai-friendly.md](airframe-ai-friendly.md); Autopilot's planner and tools depend on it | M0 to M3 | Proposal; planner **Built** |
| Trigger runner and trigger bridge | interval and broker-event agents | M4 | Logic **Built**; runners Proposal |
| Real backends and auth adapters | GitHub via the interceptor, ArgoCD, Kubernetes claims, Backstage MCP federation, Tower and TokenReview auth | A to B | Proposal (interfaces and fakes **Built**) |

## 5. Concrete artifacts

### 5.1 The AgentRun function: expiry and failing closed

`function-agentrun` is one pure function, `compose(xr, observed, now, cfg)`, so it is tested without a cluster. Two properties matter most, and both are tested:

- **Expiry needs no Clearance.** Past `spec.expiresAt` it renders nothing, and Crossplane garbage-collects the namespace. A dead or compromised gateway cannot leave a run alive. The Job's `activeDeadlineSeconds` is anchored to the XR's creation time, so it does not drift between reconciles.
- **It fails closed.** A hardened sandbox on a cluster without a runtime class, a compute class the cluster lacks, a TTL over the cluster's cap, an allowlist of `0.0.0.0/0`, or an input over 4 KiB is `Rejected` and renders nothing.

Lifecycle: `Provisioning`, `Running`, `Succeeded` or `Failed` (drained after a grace period), `Frozen` (egress cut, run kept for forensics for a hold period), `Expired`, `Rejected`.

It composes only `provider-kubernetes` Objects, because Crossplane v2 rejects a namespaced XR composing a cluster-scoped resource, the same reason SecretStore wraps `ClusterSecretStore`. **The run namespace must never carry `hangar.io/ephemeral-env`**: the existing PR-namespace TTL sweep deletes namespaces with that label when no owning ArgoCD Application exists, and would reap live runs. A test asserts the label is absent.

### 5.2 AgentDefinition

See `clearance/agents/*.yaml` (five shipped: a task agent, a researcher, an orchestrating team, an event-triggered triage agent, a scheduled reviewer). Baseline deny paths (`.tekton/**`, `cicd.yaml`, `CODEOWNERS`, `.github/**`, `**/appproject*.yaml`) apply to every agent and **cannot be removed** by a definition, so an agent can never edit the controls that constrain it.

### 5.3 Policy as CEL

Nineteen rules, first match wins, each with a stable id and a fix hint that goes back to the agent, so it can retry against a deterministic gate instead of guessing. Any evaluation error is R000 and a deny.

| Id | Denies when |
|---|---|
| R001 | the caller is not the session's principal |
| R002 | the tool is a tripwire (exec, secrets, IAM, upper sync); also trips the breaker |
| R003 | unknown tool |
| R004 / R005 | session expired / breaker tripped |
| R006 | tool not in the session's tool set |
| R007 | tier above the ceiling (a propose-only tool needs T1, not more), or a claim that widens |
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

Tools, by tier: **T0** `catalog.read`, `metrics.query`, `logs.query`, `argo.app.get`, `app.api.get`, `artifact.get`, `chat.recv`, `chat.send`. **T1** `repo.pr.open`, `xr.request`, `argo.sync.lower`, `pipeline.rerun`, `artifact.put`, `run.spawn`, `run.close`, `human.request`. **T2 (propose only)** `repo.pr.open_upper`. **T3** never exposed; the names exist only as tripwires. The `airframe.*` tools (capabilities, describe, explain, plan, apply, status, verify) are the M3 deliverable; the planner behind `plan` is built.

### 5.4 Narrow-only, and teams

A claim or a child may only narrow what it inherits: tier, time, each budget, tools, models, network reach, compute. A child starts from what its parent has *left* and reserves its budget from the parent. There is a property test: in 200 random sequences of spawn, spend and close, no session overspends and no tree exceeds what the root was granted. Depth is capped at 3.

### 5.5 Tokens, ArgoCD, audit

- **Interceptor route** `POST /agent-installation-token`, authenticated by TokenReview as Clearance's service account. It enforces an **independent outer bound** (an interceptor-side repo allowlist; permissions limited to `contents`, `pull_requests`, check reads; never `administration` or `workflows`), so a Clearance bug cannot widen it.
- **ArgoCD**: `p, role:clearance-lower, applications, sync, *-lower/*, allow`. Tower's `role:tower-sync` is `*/*` today. **Unverified**: that the glob matches your `<app>-lower` AppProject names.
- **Audit**: hash-chained JSON lines, arguments stored only as a hash. The chain proves consistency, not completeness: truncating the tail leaves a valid chain, so `checkpoint()` must be anchored somewhere the writer cannot rewrite (WORM storage, your self-hosted Rekor). Tests cover edit, delete, reorder, truncation and rewrite-after-anchor.

### 5.6 Checkride

A case names deterministic verifiers, a path scope, and denial and token budgets. Two guards against a harness that always says yes: a run that changed nothing cannot pass, and every case must fail a synthetic unfixed run. Seed cases come from your own dead-ends list (liveness probe path, `function-auto-ready`, RabbitMQ 4.1 versus operator 2.23, hand-applied XRD reverted by selfHeal, Trivy-gated Java pins, the broken canary). Two are written (`clearance/checkride/cases/`); the rest are listed in the diagram. Other agent types get their own suites, graded by deterministic checks such as schema-valid output and no forbidden tool calls.

## 6. Backend infrastructure

### 6.1 Inventory: what backs an agent, and who manages it

| Backend | Managed by | Plane | Exists? |
|---|---|---|---|
| Agent runs | `AgentRun` claim, `function-agentrun` | ephemeral | Draft |
| Clearance and the model proxy | `InfraService` (`gitops-infra-clearance`) | durable | pattern **Built** (`skyport-broker`) |
| State: Postgres, Redis, RabbitMQ | Airframe components, `attach` mode per run | durable | **Built** (CloudNativePG 1.30.1, RabbitMQ operators) |
| Object storage for artifacts | MinIO (already in the observability stack) | durable | **Built** |
| Vector store | pgvector on CloudNativePG | durable | **Unverified** (extension availability in the CNPG image) |
| Provider API keys | Infisical, External Secrets | durable | **Built** (`provider-infisical`) |
| Hosted models | model proxy route to the provider | durable config | Proposal |
| Self-hosted models | **Modelplane** (a separate fleet) | durable inventory, runtime replicas | Proposal |
| Telemetry, DORA | existing otel, Loki, Tempo, Prometheus, dora-exporter | durable | **Built** |

The model proxy's routes are durable git (`clearance/config/model-routes.example.yaml`): an alias maps to a backend. A run names an alias and never holds a key or a URL.

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
- A contract test in Checkride: a completion through the proxy against the inference gateway.

### 6.4 Where it collides with your principles

These are explicit decisions, not details:

1. **It holds credentials for other clusters.** The hub reconciles inference clusters, so it holds their credentials (and, for provisioning, broad cloud credentials; the GKE tutorial needs `projectIamAdmin`). That contradicts "no cluster holds another cluster's credentials". **Containment:** inference is its own fleet class with its own hub *per environment* (a dev hub never holds prod credentials), dedicated cloud accounts, and inference clusters that hold no app data, agent data or Hangar secrets. Prefer `source: Existing` clusters built by Terraform in a controlled account, so the hub holds only a kubeconfig, not cloud admin.
2. **It owns each inference cluster and installs Envoy Gateway.** It assumes exclusive ownership and owns the `GatewayClass`, so it cannot share a cluster with your Contour-based Hangar clusters. Inference clusters are dedicated: registry type `inference`, not `dev` or `upper`.
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
| NetworkPolicy not enforced (kiac-dev) | Egress claim is false | Canary gates `autopilotReady` |
| Hub compromised | Holds inference cluster credentials | Per-environment hubs, dedicated accounts, no app data on those clusters |
| Modelplane API changes (v1alpha1) | Backend breaks | Pinned; the contract is the URL; contract test |
| Prompt injection via logs, PR text, repo content | Agent steered | Tool output is data; T2 is propose-only; T3 is never |
| In-memory sessions lost on restart | Sessions end | Safe direction; single replica for now |
| No pod exec | Humans cannot shell into a run | By policy; debug via output, logs and the audit record. Decide if acceptable |

## 8. Open decisions

1. **Commit signing for agent PRs.** `provenance` verifies human `gitsign` against public Sigstore. Options: sign with the self-hosted Fulcio (workload trust root) and extend the gate, or exempt agent PRs. **Recommend the first**; exempting weakens a gate that is real today. Never mix the two trust roots.
2. **AgentRun as an XR, a bare Job, or a controller.** **Recommend the XR.** A Job alone loses status, policy and Tower visibility; a custom controller repeats a reflex you already decided against, and Modelplane is evidence it is unnecessary.
3. **Standalone Clearance or a Backstage module.** **Recommend standalone**, federating Backstage's MCP actions.
4. **A separate GitHub App for agents**, so their rate-limit bucket is their own. **Recommend yes.**
5. **Audit store.** MinIO object lock must be enabled when the bucket is created. Decide before creating it.
6. **Hub isolation and credentials** (section 6.4). Decide before any hub exists.
7. **When to trial Modelplane.** After phase D, once agents run and their spend is bounded, and on a dedicated kind cluster first (its getting-started guide targets local kind, but it needs a cloud account for GPUs).
8. **Debugging without exec.** Accept it, or build a recorded, time-boxed, approved break-glass as its own initiative, never a normal backlog item (your policy).

## 9. Built versus not

`cd /Users/jerf/tech/clearance && ./.venv/bin/python -m pytest -q` runs **255 tests** with no cluster: scope and traversal safety, narrow-only limits, definition schema, sessions and the run tree (including the property test), 16 CEL rules one at a time and failing closed, hash-chain tamper detection, the gateway end to end with fakes, the model proxy, triggers, Checkride, the MCP surface on the mcp SDK v2, the AgentRun manifest against the XRD's own schema, and the composition function including its gRPC wrapper on the real SDK.

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
- Modelplane's usage-record contents, short-lived-credential support for `Existing` clusters, and behaviour on your Kubernetes versions (kind-prod is 1.37; kiac-dev's version I did not check).

## Sources

- [Modelplane](https://modelplane.ai/), the [repository](https://github.com/modelplaneai/modelplane), and [Building Modelplane on Crossplane](https://blog.crossplane.io/building-modelplane/).
- Modelplane docs read from the repository: `overview/how-it-works`, `platform/inference-cluster`, `platform/inference-gateway`, `platform/providers`, `models/model-endpoint`, `getting-started/build-the-platform`.
