# Decisions log

Answers to the open decisions in [roadmap.md](roadmap.md), recorded 2026-09-26.

| Id | Decision | Status |
|---|---|---|
| D1 | Sign agent commits with a self-hosted Fulcio. A self-signed root CA for it is acceptable and to be evaluated. | Decided |
| D2 | `AgentRun` is a namespaced Crossplane v2 XR (no Claim, composed by `function-agentrun`). | Decided |
| D3 | Clearance is a standalone component (its own deployment, one Kubernetes permission). | Decided |
| D4 | Agents get their own GitHub App, separate from the platform's. | Decided |
| D5 | Audit object lock: take the recommendation in roadmap.md. | Decided |
| D6 | Model-hub isolation: needs more context. | **Decided 2026-09-26:** hosted providers only for now (option 1); one hub per environment with dedicated accounts (option 2) is the M5 default |
| D7 | Name for the evaluation harness. | **Decided 2026-09-26: Preflight** (replaces the working name Checkride) |
| D8 | A new `autopilot` repo, with Clearance as a package inside it. | Decided |
| D9 | Release-file split: yes; design it fully and prove it out. | Decided; designed and proven live on the dev cluster ([release-file-split.md](release-file-split.md)); Glidepath's writer change still to build |
| D10 | Strictness rollout timing. | **Decided 2026-09-26: option A, enforce now.** Gate built (validator image, `values-check`); becomes required once every gitops repo has the check file. See [briefings-d6-d10.md](briefings-d6-d10.md) |
| D11 | Take the recommendation in roadmap.md. | Decided |
| D12 | Take the recommendation in roadmap.md. | Decided |

All experiments (U1–U12) in the roadmap run on the dev cluster.

## 2026-09-26, substrate review

Accepted: stable agent identity (AP-A4), model version in the record (AP-C1), cost accounting (AP-C2), upstream Agent Sandbox evaluation (U11), resumable state (AP-D1, U12), fixed T0 read set (AF-2b), rejection of a monolithic `AgentWorkspace`. See [industry-context.md](industry-context.md).

## 2026-10-09, before M3

| Id | Decision |
|---|---|
| D1 (detail) | Create a new Hangar root CA for the platform's Fulcio, rather than each cluster's self-generated root. |
| D13 | `cicd.yaml` is agent-editable: an agent allowed to configure an app may configure its CI/CD. It leaves Clearance's `BASELINE_DENY_PATHS` (`.tekton/**` stays). Human-only fields and rules (governance, releaseFile, chart, cloud targets, secrets, environment tier/production/cluster, gitops-image-bump, automatic production releases) are listed in roadmap.md "M3 status". |
| D14 | Holmes stays scaled to 0 on both clusters, on purpose; A5 (Holmes through Clearance) is deferred with it. |
| D15 | The U8 ClusterRole for AgentRun's provider-kubernetes objects is approved (`autopilot/airframe-drafts/rbac/provider-kubernetes-agentrun.yaml`). It ships only together with a ValidatingAdmissionPolicy confining the provider's service account to run namespaces, the agent-sandbox resources in place of Jobs, and a stable service-account binding; see roadmap.md "M3 status". |

kiac-dev enforces NetworkPolicy (Cilium 1.20), verified 2026-10-09; the AP-A1 canary is expected to pass there.

## 2026-10-28, Clearance becomes a product

Sources: the Clearance Brief, Architecture and Roadmap (2026-10-27/28). What they change in Autopilot is in [design.md section 0.1](design.md).

| Id | Decision |
|---|---|
| D4 (reconfirmed) | Agents get their own GitHub App. It is a different App from Clearance's provenance App: the one that writes agent PRs must not be the one that attests their provenance. |
| D5 (revised) | Audit integrity comes from the Clearance ledger: record hashes in a Tessera log, with checkpoints countersigned by at least one witness Clearance does not operate. MinIO object lock remains for retention only. |
| D16 | Clearance is a standalone Hangar product with its own `clearance` repo. This supersedes D8 for the package (the `autopilot` repo stays). The proposed split: policy, scope, sessions, gateway, audit and the deployment gate go to `clearance`; definitions, Preflight, AgentRun, the planner and the Hangar tool backends stay in `autopilot`. The owner accepted this split on 2026-10-28. |
| D17 | **Open:** the runtime boundary as an AuthZEN PDP behind Traefik Hub's Sovereign Trust Plane, or Clearance's own gateway. Hangar runs Traefik Proxy (not Hub), so the own gateway ships now, with the decision refactored into a pure, AuthZEN-shaped function. |
| D18 | AF-8a, the read-only `airframe.*` tools, is built before AP-A3. |
| Agent identity | Taken from a standard: ID-JAG (RFC 8693 token exchange at the IdP, then an RFC 7523 JWT bearer to Clearance). The issuer is open (D19 in roadmap.md): Dex has no ID-JAG issuance yet. |
| AP-A2 | Built in this plan, not in a separate lab. Clearance is Hangar's AI gateway whatever the product's go/stop gates decide. |

## 2026-10-29, after the AP-A3 copy-test

| Id | Decision |
|---|---|
| D20 | Finished AgentRuns are deleted, in two layers. Clearance (AP-A2) deletes a run once it has recorded the run's evidence. A backstop CronJob (cluster repo `55-autopilot/agentrun-reaper/`, no Clearance and no function needed) deletes every AgentRun whose deadline, `min(spec.expiresAt, creation + max TTL)`, passed more than 60 minutes ago, judged from those immutable fields alone, never from status. Deleting the XR cascades through owner references to Objects Crossplane lost track of, the copy-test's open finding (an untracked run namespace and endless Sandbox re-creation after etcd timeouts). The backstop's one permission is list and delete on agentruns in `autopilot-runs`. Crossplane Operations can't delete resources (v2 alpha), so it is a CronJob. Clearance must record evidence within the 60 minutes; a run the backstop reaps keeps only its CronJob log line. |

## 2026-11-02, the Clearance and Autopilot boundary

Source: the Clearance Architecture's decision of 2026-11-02 (ch. 01 and 13) and the Clearance and Autopilot build spec ("Hangar context and product boundaries", "Languages"). What it changes in Autopilot's design is in [design.md section 0.1](design.md#repo-split-d16-accepted-by-the-owner-2026-10-28-amended-by-d21-2026-11-02).

| Id | Decision |
|---|---|
| D21 | **Amends D16.** Autopilot owns the AI gateway: the MCP surface agents connect to; sessions, the run tree, budgets, the breaker and requested limits (limits and budgets); the tool registry (which tools exist, their tier and arguments) and dispatch to every backend; the model proxy; agent definitions, their schema and the cluster pin loader; the human inbox, person controls (freeze, end, hold), run results, artifacts and trigger history; the runtime catalog and images; the trigger bridge and scheduler, AgentRun, Preflight and the planner; the vendored Glidepath and Airframe contracts; the gateway's serve entrypoint and image. Clearance decides and records, and owns the gates and the ledger: the decision service (CEL deny rules, the tier vocabulary, path, repo and field scope, narrow-only), answered as an AuthZEN-shaped evaluation the gateway calls for every tool call, model call, session open and spawn; the clearance token; the evidence record schema, the recorder and its store; the ledger, `clearance verify` and the packet; the deployment gate with its classifier, `clearance.yaml`, grants and approvals; the gate providers (Argo CD, Terraform, the GitHub App's protection rule, `clearance register`); provenance verification from receipts; tiering of agent-definition changes; clearance-api; approver identity. The gateway enforces and Clearance decides and records: the gateway reaches Clearance only through its API, and Clearance's code imports nothing from Hangar or Autopilot. Clearance is not a gateway; the runtime boundary is a feeder, kept thin. D16 put sessions, dispatch, the gateway and the MCP surface in the `clearance` repo, which is where that code sits today; it moves to `autopilot` in R-3. |
| D22 | Each component's language is chosen for security and efficiency on its own path. Clearance and every gate component are Go: the core (decision service, token, recorder, ledger, clearance-api, GitHub App, deployment gate) and the `clearance` CLI are one Go module and one static binary; the Argo CD and Terraform gate pieces are Go. cel-go is the reference CEL implementation and the one Kubernetes runs for ValidatingAdmissionPolicy, so a rule means the same at decision time and at admission; the supply-chain libraries (Tessera, sigstore-go, in-toto-golang, DSSE) are Go; the decide path has a 20 ms p99 budget. The Autopilot gateway moves in Python (R-3) and is then ported to Go (A-9). Agent runtimes and Crossplane composition functions stay Python; policy is CEL; the portal is TypeScript. Rust was weighed for the core and not taken: the libraries this work needs are Go-first, and Go is memory-safe at the boundary that matters. |

## 2026-11-03, during W1 of the Clearance and Autopilot build

Both decided by the owner on 2026-11-03, while R-2 and R-5 were being built. Where they stand is in [roadmap.md](roadmap.md), "Clearance and Autopilot build: W0 and W1".

| Id | Decision |
|---|---|
| D23 | **Trusted registries, option B.** The deployment gate's trusted-registry prefix (its Flight prefix) is configuration. Clearance's product default is empty: any registry. Hangar sets `ghcr.io/riley-roooo/` (with the trailing slash, since the core's check is a prefix test) through apron's `clearance.trustedRegistries`, whose default is derived from `registries.flight`. It took effect at the R-4 cutover on hangar-dev. The core reads it from `CLEARANCE_TRUSTED_REGISTRIES` (clearance v0.29.0; before v0.29.0 the variable was `CLEARANCE_FLIGHT_REGISTRIES`). **Consequence, accepted:** an image bump from any other registry is tier 2 and waits for one owner. That includes the third-party images Kyverno allows on hangar-prod (CNPG, the OTel auto-instrumentation images, `bitnamilegacy`). |
| D24 | **A policy bundle whose source cannot be read at start is degraded, not fatal.** The core starts. The bundle's tools, and calls carrying a file one of its documents checks with that source's rules, are denied R000 ("policy bundle ... is unavailable"), with no charge and no breaker trip; every other call decides as usual, and records, the deployment gate, provenance, the GitHub App and clearance-api stay up. `/readyz` stays 200 and lists the bundle under `degraded`, because the core is one `Recreate` replica that also serves the gate and the webhook. A background loader retries (2 s, doubling to 60 s) and swaps the compiled policy in when the source answers. A contract version the bundle does not list stays a hard refusal at start: that is a configuration error. This applies to Hangar's bundle, which reads Glidepath's scope from glidepath-api's `GET /v1/contract` (clearance v0.29.0, clearance#49). |

## 2026-11-03, the Argo CD gate design pass (G-ARGO-1)

D25 was decided by the owner on 2026-11-03. D26 to D29 are the shapes the design pass chose, each from a spike on
hangar-dev in Warn mode; the owner accepted all four on 2026-11-03. The
evidence, the card changes they imply and the two hangar-prod measurements prepared for the owner are in clearance
`docs/gate.md`, "Phase 2 design pass", and `docs/spikes/g-argo-1/prod-plan.md`.

| Id | Decision | Status |
|---|---|---|
| D25 | **Clearance's signed record is the authority; Glidepath's release record cross-references it by `releaseId` and the change id.** Clearance's change and `deploy.request`, `deploy.outcome` records carry `release.id` (the release's `<chainId>:<cluster>/<env>`), which the CMP reads from the rendered tree (`hangar.io/release-id` on the Rollout) so it is bound by the tree digest; the attestation predicate copies it. Glidepath's release-tracking ConfigMap and glidepath-api's release record carry `clearanceId`, the tree digest and the `deploy.request` record's seq and hash, written by the `clearance-gate` task when the core answers; Tower writes a `clearance:` block (id, tree, state, request and outcome seq and hash, attestation digest and Rekor index) into the release log with the final outcome. `release.yaml`'s `releaseTracking` gains nothing: it is inside the tree, and a change id there would change the tree it names. A verifier follows the link both ways and a pointer that does not round-trip is a finding; the release record never outranks the chain. Clearance stays installable without Glidepath: `release` is an optional opaque id. | **Decided 2026-11-03** by the owner |
| D26 | **The Config Management Plugin replaces the tenant Application's Helm source.** On a protected Application the one generating source is the plugin on `gitops-<app>`; the plugin fetches the airframe chart at the tag the tenant-onboarding template pins (recording the peeled commit) and renders it with that repo's values, release name = the Application, namespace = the destination, set on every object before hashing. A plugin source cannot read a `ref` source: with the chart as the plugin source and `$appsrc` value files, the spike rendered the chart's defaults without an error. No other generating source on a protected app (its objects would carry no stamp). The CMP finds a cleared change by app, environment and tree digest, because Argo syncs the merge commit, not the PR head. | Accepted 2026-11-03 (G-ARGO-1) |
| D27 | **Admission is a native ValidatingAdmissionPolicy that matches the CMP's stamp, not Kyverno and not spec equality.** `paramKind: ClearanceGrant`, one binding, `paramRef` by selector `clearance.hangar.io/active=true` in the object's own namespace, exactly one active grant per protected namespace listing every object of its tree as a map keyed `<group>/<kind>/<name>` to the `clearance.hangar.io/rendered` hash; matched only for argocd-apps' application-controller, CREATE and UPDATE, main resources, protected namespaces, every `matchConditions` expression `has()`-guarded. Expiry is the agent's (`status.valid`), since admission CEL has no clock. Warn runs with `parameterNotFoundAction: Allow` (Deny refuses even in Warn) and the flip to Deny changes both fields. Why: on hangar-dev the stamp survived Argo, a mutating policy and API-server defaulting while the live spec never equalled the render; the VAP costs about 1 ms and 52 CEL units for any grant size (4,647 for a 200-object list); Kyverno's webhook, with its admission controller crash-looping, refused Argo's writes in Audit/Warn mode and kept its webhook for minutes after the policy was deleted. Kyverno stays Hangar's Flight-registry engine. | Accepted 2026-11-03 (G-ARGO-1); prod measurement P1 optional |
| D28 | **The Argo CD agent watches Application status for outcomes; Argo CD Notifications are not used.** The watch saw every operation within a second and catches up after a restart; Notifications gave up after 4 attempts in 8 s with the receiver down for one sync and marked the outcome sent, back-filled old operations on first start, and would need a core credential in the notifications controller. The agent keys each outcome by the operation and the Application, and reposts the last one on restart (the core answers idempotently). | Accepted 2026-11-03 (G-ARGO-1) |
| D29 | **The CMP and the agent reach the core as two more hangar-prod foreign workloads**, on the path Tower's backend uses (hangar-prod's public issuer, Traefik on `clearance.hangar-dev.local`, a hostAlias). The core already accepts a list of `<namespace>/<sa>` globs for one foreign cluster: add `argocd-apps/argocd-apps-repo-server` (the CMP; its `clearance` token mounted in the sidecar only) and the agent's account to `CLEARANCE_FOREIGN_SERVICE_ACCOUNTS` on clearance-core, the agent's to clearance-api's, the CMP's principal to `CLEARANCE_VERIFIERS`, both to `CLEARANCE_PROVIDERS`; add `Exact /v1/records` to the route and a grant-feed reader role on clearance-api (C-10). A second protected cluster needs several foreign issuers, a later code change. The hop is plain HTTP on the lab LAN, as Tower's is; accepted for the lab only. | Accepted 2026-11-03 (G-ARGO-1); prod measurement P2 optional |

## 2026-11-03, protected environments (C-6)

| Id | Decision | Status |
|---|---|---|
| D30 | **Clearance decides which environments are protected, from its own configuration; the caller's `protected` flag decides nothing.** The list is `CLEARANCE_PROTECTED_ENVIRONMENTS` (chart `gate.protectedEnvironments`), `<cluster glob>/<env glob>` entries. A change to an unlisted environment is cleared at tier 0 with reason `unprotected`, recorded, and gets a token. Two choices made in the build: an empty list protects every environment (fail closed), and a request saying `protected: false` is refused with `DG-PROTECTED` (`true` decides nothing; Glidepath sends `true`). Hangar sets `["hangar-prod/*"]`, so hangar-dev changes are tier 0. | Decided by the owner 2026-11-03 (unlisted = tier 0); the empty default and the `false` refusal are C-6 build choices (clearance#59), open to amendment |
