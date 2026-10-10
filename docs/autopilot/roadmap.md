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
3. **The planner is the acceptance test.** The parachute sentence (the one-line
   request to an agent in [airframe-ai-friendly.md](airframe-ai-friendly.md): a new Python app named
   parachute, with dev, test, staging and prod environments, a canary step and one env var) needs AF-1 to AF-6 and the Autopilot
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
| **DX-0** decide and create the `autopilot` repo | move `~/tech/autopilot` there; pytest as CI |

**Exit:** the guard is live on dev; `airframe validate` catches an injected typo on a real PR; `baggage-api` runs on dev; every item this milestone's own packet actually asks for (U1, U5, U6, U7, U11 - see task 1 above) has an answer. (U2, U3, U8, U9, U10 are follow-on experiments that de-risk M2/M3/M5, not M0 gates - the packet was written that way; this line originally over-promised "every item in section 5" and is corrected to match.)

**M0 status (2026-09-27): 100% done against its own exit bar; scorecard 27.3 -> 41.3 (target 35).**
- Done: AF-10a guard (Airframe v0.3.91, pinned on the dev and prod clusters; all 7 live env files render byte-identically before and after); AF-10b chart tests and CI (the scorecard job needs a `FLEET_READ_TOKEN` secret); AF-1a `AGENTS.md`; AF-4a `airframe validate` v0; DX-0 `autopilot` repo (public, github.com/jfillman/autopilot); planner flipped (`Features.rollout_guard` defaults to True, the canary test retired); D7 decided (Preflight); D6 and D10 briefed ([briefings-d6-d10.md](briefings-d6-d10.md)); D10 rollout itself now live too (the `values` release-guardrail is mandatory on all 3 candidate gitops repos, not just briefed); release-file split designed and proven on the dev cluster ([release-file-split.md](release-file-split.md)), and its D9/AF-5 continuation (schema field, both writer Tasks, the 3-`valueFiles` ApplicationSet change) shipped and live-verified on both clusters 2026-09-27 (see that doc's own Progress table - this runs past M0, not gated by it).
- Exit criterion **"`airframe validate` catches an injected typo on a real PR"** demonstrated live 2026-09-27: a fixture PR against `gitops-baggage-api` (`m0-typo-proof`, closed after) with `rolout:` injected into `kind-prod/staging/values.yaml` made the `values` release-guardrail Check fail for real, not just offline.
- U1, U5, U6, U7, U11, U12 answered and U3 partly (section 5); **U4 also now answered** (2026-09-27: Tower's Re-run/Cancel confirmed against a real failed PipelineRun on `baggage-api`). Still open, not required for M0: U2 (function TTL re-invoke), U8 (needs the `AgentRun` composition applied via a copy), U9/U10 (deferred by the user's own choice, M2/M5).
- `baggage-api`: fully working end to end, dev and kind-prod staging both `Synced`/`Healthy`, broker-connected, image `0.1.0-ae82839` (Python versioning fix live). The first two image scans failed (Debian base: 44 unfixed HIGH CVEs; then a stale setuptools), which is a scorecard item for the Python scaffold.

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

**M1 status (2026-09-27): AF-2/AF-3/AF-4b/AF-1b (#6-#10) all merged, tagged v0.3.95, live-verified on
both clusters and on a real PipelineRun.** Airframe `v0.3.95` tagged; `glidepath-catalog`'s
`valuesValidatorImage`/`chartVersion` bumped (pushed direct to `glidepath` main, its own convention).
`gitops-cluster-dev`'s `idp-service-catalog` Application had a real live-cluster risk found and fixed
before the pin moved: its `xrds/*.yaml` include glob was a wildcard that would have caught AF-3's new
`xrds/*.meta.yaml` sidecar files as invalid manifests - narrowed to an explicit 13-file list (verified
by simulating the glob against the real tag: exactly 13 XRDs + 13 compositions, zero `.meta.yaml`).
`gitops-cluster-kind-prod`'s equivalent already used an explicit list, so only needed the bump. Both
synced `Synced`/`Healthy` with the expected resource counts; the live Redis XRD carries its new
`hangar.io/agent-summary`. A real fixture PR against `gitops-baggage-api` (closed after) confirmed the
`values` guardrail catches `AF-SECRET-001` (a GitHub-token-shaped literal) and warns `AF-COMP-003` on
baggage-api's own real unmigrated component references, on a live PipelineRun with a `fail`-reporting
GitHub Check - both brand new in this batch, not a repeat of the M0 typo check.
- **AF-2, merged.** `values.schema.json` is the single hand-authored source (additionalProperties:false
  baked in everywhere except the documented passthroughs; descriptions 5% -> 100%); `values.yaml` is
  generated from it, CI-gated. `tools/airframe-validate` runs one pass against a compiled schema
  (`tools/airframe_schema.py`) with a discriminated `components[].type` union spliced in from the real
  XRDs. Found and fixed a real latent gap: `cronJobs[]`/`jobs[]` were missing several fields the strict
  form would have wrongly rejected. 48/48 injected mutations rejected on the real fleet. A follow-on fix
  (`jfillman/airframe#7`, also open) bakes the new `airframe_schema.py` module into the validate image -
  #6 alone would have shipped a broken image.
- **AF-3 (`jfillman/airframe#8`), component outputs and `fromComponent`.** Redis/PostgreSQL/RabbitMQ each
  declare their real outputs in `xrds/<type>.meta.yaml`, verified against their actual Compositions.
  `env: [{name, fromComponent: {name, output}}]` resolves to a real valueFrom, with `AF-COMP-002` lint
  rejecting a bad reference. A real migration PR against `boarding-api` (branch
  `af3-fromcomponent-migration`, staged, needs a user-signed commit - gitsign/Sigstore needs an
  interactive browser login this session couldn't complete) replaces its hand-written `cache-master`/
  `board-mq-connection`/`board-mq-user-credentials` literals, dropping a manually-Infisical-synced
  Redis password in the process.
- **AF-4b (`jfillman/airframe#9`), partial.** Five dead-end rules (`AF-CLUSTER-001`, `AF-ENV-001`,
  `AF-COMP-001`, `AF-SECRET-001`, and `AF-COMP-003` - an advisory that fires exactly on the fleet's
  remaining hand-written component references) plus `--format json`. **Not done:** L3 kubeconform
  conformance, SARIF output, AF-ENV-002/AF-PROBE-001/AF-ARCH-001/AF-RABBIT-001 (need cluster/build
  context this session didn't reach), and widening the required check from gitops-only to app + tenants
  repos (Tekton/CI wiring, not an `airframe-validate` change).
- **AF-1b (`jfillman/airframe#10`), done, stacked on #9.** `hangar.io/agent-summary` on all 13 XRDs;
  `contract/airframe-contract.json` (generated from the same sources the chart/validator use);
  `tools/airframe-capabilities` (a CLI answering component/XRD/field/output questions from the bundle
  alone); `llms.txt`. `tools/test_capabilities_coldstart.py` proves 10 real capability questions
  answered correctly from the bundle, cross-checked against source. **Not done:** the
  `add-to-catalog` Backstage-template review (a real product decision, left for the user) and wiring
  the 10-question proof into the separate `autopilot` repo's own Preflight harness.
- **AF-6a (`jfillman/airframe#11`), done, stacked on #9.** Redis/PostgreSQL/RabbitMQ each set a custom
  `ComponentReady` condition (deliberately not named `Ready` - that's Crossplane's own core-managed
  type) with a closed reason set, computed from the composed child resource's own real status. Live
  copy-composition-verified for every branch on all 3 components, both RabbitMQ modes - including a
  real transient `PostgreSQLDegraded` state caught mid-bootstrap, not simulated.
- **SP-3 (`jfillman/airframe#12`), the MongoDB component built and live-verified, born A+ - stacked on
  #11.** DEDICATED mode, wrapping MongoDB Controllers for Kubernetes' `MongoDBCommunity` CRD (the
  design's originally-named operator is archived; its unified successor preserves the same CRD,
  verified against the real repo, not memory). Outputs, verify checks, sidecar meta and a
  `ComponentReady` condition all shipped in the same PR, not retrofitted. Getting one real replica set
  running on kiac-dev surfaced three non-obvious cluster-infra gaps in `gitops-cluster-dev`, each fixed
  with the user's explicit confirmation before the more sensitive RBAC grants: the operator needed
  `watchNamespace: "*"` (app namespaces, not its own), its database pods needed two ServiceAccounts +
  a narrow Role/RoleBinding replicated per app namespace (the chart only creates them in its own
  namespace), and Crossplane itself needed two new RBAC grants for that - the second
  (`pods: get/patch/delete` cluster-wide) required by Kubernetes' own RBAC-escalation check before
  Crossplane could delegate that permission via the Role it creates. End-to-end proof: a real replica
  set reached phase `Running`, the pod went `2/2 Running`, and the output Secret's credentials were
  read and confirmed correct, not just checked for existence. **Not done:** migrating `baggage-api`'s
  own application code onto it (real Node.js changes in a separate repo, replacing its current
  single-replica in-memory state) - the component itself is the whole scope of this PR; the app
  migration is real follow-on work, not started.
- XRD-level descriptions/CEL rules are still at the M0 baseline in most XRDs (AF-1b's own summaries
  don't count as the per-field description sweep AF-2 originally scoped there).
- **`boarding-api`'s `fromComponent` migration merged** (`jfillman/boarding-api#9`). Merging it exposed
  a real gap: the chart's `lower-envs`/`tenant-onboarding`/`tenant-identity` ApplicationSet pins - a
  **third**, easy-to-miss pin location for `airframe-application` beyond Glidepath's `chartVersion` and
  each cluster's `idp-service-catalog` sync pin - were still at `v0.3.94` (dev)/`v0.3.92` (kind-prod),
  predating `fromComponent`. The live `boarding-api-dev` pod crash-looped (`REDIS_URL="<nil>"`) within
  seconds of the merge syncing; caught immediately by watching the Rollout, fixed within minutes
  (`gitops-cluster-dev` `f5d15b3`, `gitops-cluster-kind-prod` `da0f5cf` preventively), confirmed by the
  actual pod going healthy and its logs showing it consuming events normally. See
  [[feedback_airframe_chart_three_pin_locations]] (memory) and the handoff's live-incident block for
  the full timeline - this is now a standing checklist item for the next chart-behavior release.
- **Immediate next steps:** merge `#11` and `#12` (each stacked on the last); decide on `add-to-catalog`
  for the 7 newly-annotated XRDs (a real product decision, not blocking); migrate `baggage-api` onto
  the new MongoDB component (real app-code work, not started); M1's remaining item after that is just
  the XRD-level description/CEL sweep.

### M2 Safe write (weeks 7-10), target 75
| Task | Notes |
|---|---|
| **AF-5** base layer and release-file split | migrate dev first, then prod, each via a scratch app; coordinate airframe, glidepath's `open-release-pr` and deploy stage, and Tower's Config tab |
| **AF-5b** ownership gate, risk classes, comment-preserving patch engine | |
| **AF-9a** field-level `agent-scope` specified and tested | Clearance policy grows a JSON-pointer allow and deny |
| **SP-4** OAuth component, `skyport-auth`, enforced JWTs (part 5) | born A+ |
| **AF-7a** walkthrough runner; convert quickstart parts 1 to 3 | each step: command, expected result, verify |

**Exit:** no live file mixes owners; a release PR and a config PR never conflict (property test); part 1 replays green from a walkthrough.

**M2 status (2026-09-29): all five workstreams done. Exit bar met - M2 is closed.**
- **AF-5**, done for the 3 pre-existing live apps (`baggage-api`, `boarding-api`, `flight-api`): dev-env split merged (`baggage-api#4`, `boarding-api#10`, `flight-api#10`); staging split (`gitops-baggage-api#16`, `gitops-boarding-api#17`, `gitops-flight-api#10`) built directly rather than waiting for each app's next real release, since the ApplicationSet mechanism was already live. `skyport-broker` has no image to split (`rollout: null`), so it's out of scope. `platform/` → `airframe/` (step 4, the directory rename) is deliberately **not** part of this - scoped separately, see below.
- **AF-5b**, the doc-backed half done, two PRs: `airframe#15` promotes `AF-OWNER-001` from warning to error now that the split is real fleet-wide (a release key in a human file, or anything else in a release file, both fail); `autopilot#3` adds the matching Clearance-side guarantee - `release.yaml`/`*.release.yaml` join `BASELINE_DENY_PATHS`, un-removable by any agent definition. The roadmap row's other two items ("risk classes", "comment-preserving patch engine") have no design anywhere in this repo - not attempted rather than improvised.
- **AF-9a**, done, `autopilot#3` (same PR as AF-5b's Clearance half). `clearance/scope.py` gained `diff_pointers` (RFC-6901 JSON pointers for whatever changed between two parsed file contents), `field_violations`/`field_outside_allow` (glob matching reusing the existing path-glob engine, extended to also match a whole matched subtree). `AgentDefinition` grows `field_allow`/`field_deny` (schema: `repos.fieldAllow`/`repos.fieldDeny`), with a `BASELINE_DENY_FIELDS` an agent can never remove (`extraManifests`, `networkPolicy`, `httpRoute`, `release`, `releaseTracking`, `rollout.image` - the same fields AGENTS.md already named by convention). Wired into `policy.py` as a new rule `R020`, given a file's `before` and proposed `content` in the `repo.pr.open`/`open_upper` tool args - a file with no `before` (a new file) is exempt, since there's nothing to diff against. 235/235 tests pass, including 5 new end-to-end R020 cases and 8 new `scope.py` unit tests.
- **AF-7a**, done, `airframe` (branch `af7a-walkthrough-runner`). `docs/walkthroughs/*.yaml` (schema in that directory's own `README.md`): each step has a `command` (documentation), an `expected` result (prose), and a `verify` (a real, idempotent shell command against the live clusters - exit 0 = still true). `tools/walkthrough-runner` replays a walkthrough's `verify` steps and reports PASS/FAIL, or `--render`s the command/expected text to markdown. Converted all 3 quickstarts (`boarding-api`, `flight-api`, `skyport-broker`) - **all three replay green for real against kiac-dev/kind-prod right now** (7/7, 4/4, 3/3 steps), satisfying this milestone's own exit line. Found and fixed a real, unrelated bug along the way: `hangar/tools/airframe-scorecard/scorecard.py`'s XRD glob matched `*.meta.yaml` sidecar files too (added by AF-3), crashing the whole scorecard with a `KeyError` since SP-3 added `mongodb.meta.yaml` - nobody had run it successfully since. Fixed; scorecard now runs clean (57.9/100, "Docs for agents" 100/A+, walkthroughs check passing).
- **SP-4** (OAuth component, `skyport-auth`), done and **live-verified end to end**, `airframe#17`/`#19`-`#22`. Dex (`dexidp/dex`) chosen over Authentik (lighter footprint, already running in-cluster as ArgoCD's own SSO). `mode: attach` registers a client via Dex's real gRPC Admin API (`CreateClient`) through a new custom Crossplane Function, `function-dex` - this catalog's second hand-written Function, after `function-rollout-watcher`. Real, live proof, not offline: the real `skyport-auth` server (running on kiac-dev, kept as the permanent component, not torn down) issued a real `client_credentials` access token to a real registered client, and the JWT's signature was validated against the real JWKS endpoint with PyJWT.
  - **Solved multi-arch for real** using the `container` CLI (no docker/podman machine) + `skopeo` for image-format conversion; `crossplane xpkg push -f a.xpkg,b.xpkg TAG` genuinely combines two single-arch builds into one real multi-platform manifest - confirmed via `skopeo inspect --raw`. Full recipe in `functions/function-dex/README.md`.
  - **Known, accepted tradeoff**: `client_credentials` isn't in any stable Dex release yet (confirmed absent from v2.45.1, the latest as of 2026-09-29) - only on Dex's unreleased `master` branch. Pinned to `ghcr.io/dexidp/dex:master` (a floating tag, no version stability), user-confirmed given there's no alternative with the feature at all. Revisit once a stable release ships it. **Resolved 2026-10-09:** Dex v2.46.0 ships the grant (enabled by listing it in `oauth2.grantTypes`, which the config already does); function-dex v0.1.7 pins it (airframe#79), live on kiac-dev with a token verified against JWKS.
  - Three real bugs found and fixed live before this worked (Dex refuses to start with zero connectors; a wrong healthz probe path; four resource kinds with no `status.conditions` for `function-auto-ready`'s generic detection), plus a Crossplane RBAC gap (`PersistentVolumeClaim`, user-confirmed) and a Dockerfile portability fix (`container` CLI doesn't support BuildKit's `RUN --mount=target=.`). Full writeup: `project_sp4_oauth_dex_investigation.md` (session memory).
- **The `platform/` → `airframe/` rename** (AF-5's own step 4) is scoped as a separate follow-on, not part of M2's AF-5 line item above - it touches every live app's file layout, both clusters' ApplicationSets, ~10 Glidepath Tasks, Tower's Config tab, and every scaffold template, and the design doc's own plan is a dual-path migration window, not a drop-in rename.

### M3 Autopilot core (weeks 11-18), target 88
| Task | Notes |
|---|---|
| **AP-A1** apron `components.autopilot` toggle, registry `autopilotReady`, network-policy canary | refused on `type: upper`; the canary must pass before `autopilotReady` flips (kiac-dev enforces NetworkPolicy: Cilium, verified 2026-10-09) |
| **AP-A2** Clearance as an InfraService; T0 tools with real adapters | Backstage MCP, ArgoCD read-only account |
| **AP-A3** `AgentRun` XRD, `function-agentrun`, `provider-kubernetes` grants, namespaced Role | copy-tested; expiry proven with Clearance stopped and with the function pod killed |
| **AP-B1** interceptor `/agent-installation-token`, separate GitHub App, ArgoCD accounts | commit-signing decision executed |
| **AP-B2** T1 tools with real adapters; `agent-scope` and `agent-identity` gates, stub then real | field-aware, from AF-9a |
| **AP-B3** model proxy v0 (HTTP forwarder), hosted model route, key via Infisical | |
| **AF-8** `airframe.*` tools, planner adapters | **the parachute sentence passes live**, with a seeded bad run and a resume test |
| **AF-6b** `describe` and verify contracts; **AF-10c** chart `agent:` block | |
| **AP-C1** Flight recorder: `task_id` everywhere, audit chain anchor; each run records the pinned model version and its Preflight result | ledger fields from [industry-context.md](industry-context.md) |
| **AP-A4** stable agent identity, separate from a run (per-agent policy, history, memory scope) | one identity per AgentDefinition; runs inherit it |
| **AP-C2** cost accounting: tokens and compute per run, per agent, per task tree, in the recorder and the Tower tab | from budgets already enforced |
| **AF-2b** fix the T0 read set (`getLogs`, `getMetrics`, `getRelease`, `getDeploymentStatus`) and put it in the contract bundle | read tools taught by example |

**Exit:** the parachute sentence works end to end on dev (a human merges the flight PRs); killing Clearance mid-run still ends every run on time; the seeded bad run scores as failed.

**M3 status (2026-10-09): not started.** Nothing of it exists on a cluster: no `AgentRun` or agent-sandbox CRD on
kiac-dev, no Clearance deployment, no `components.autopilot` in apron. What moved between M2 and here:
- The Tier 2 rename finished on 2026-10-01: `catalog.hangar.io` is the only catalog group, and the autopilot drafts
  emit it.
- The 2026-10-08 architecture review closed on 2026-10-09 (airframe v0.3.137 on both clusters). It leaves A4
  (condition vocabulary, `observedGeneration`) and A6 (XR rule ids) to the `airframe.*` tools (AF-8), and A5
  (Holmes through Clearance) to AP-A2.
- The planner follows ADR-0019 (`deploy.environments`, `glidepath/envs/`, the tenants repo from the registry;
  autopilot#6). autopilot `main`: 240 tests pass.
- The AppSpec schema now lives in Airframe's contract bundle (`contract/appspec.schema.json`, airframe#80). Autopilot
  vendors it and its CI fails on drift (autopilot#7).
- apron's cluster template is on airframe v0.3.137 with what that catalog needs (apron#20). AP-A1 builds on it.
- Scorecard 86.6, 11 of 14 checks (`baseline-2026-10-09b.json`) against this milestone's 88. The lowest dimension is
  the interaction surface (54.5), which waits on the `airframe.*` tools (AF-8).

**Decisions before M3 code (answered 2026-10-09 unless marked open):**
1. **`cicd.yaml` is agent-editable.** The CI/CD config is part of the app, so an agent allowed to configure the app
   may configure it. `cicd.yaml` leaves `BASELINE_DENY_PATHS`; `.tekton/**` stays denied. These stay human-only
   (decided 2026-10-09):
   - Field-level deny (AF-9a `BASELINE_DENY_FIELDS` for `cicd.yaml`): `/governance` (the scan gates; an agent adding
     itself to `allowedCommitSigners` would approve its own release), `/deploy/releaseFile`, `/deploy/chart` (another
     chart renders anything, past the schema and chart guards), `/deploy/target` with `/deploy/ecs`, `/deploy/lambda`,
     `/deploy/azureContainerApps` and the same blocks on each environment (they point the cloud deployer elsewhere),
     and `/secrets` (with `build.script` editable, an entry is a path to exfiltrate any key in the app's store).
   - A new Clearance rule matching environments by name, because the pointer diff collapses a list-length change to
     the whole list: an existing environment's `tier`, `production` and `cluster` cannot change, and flight
     environments cannot be removed or reordered (the order is the promotion order). Adding environments stays allowed.
   - Pipeline steps: no `gitops-image-bump` step (its `gitopsRepo`/`manifestPath` reach any repo); no `release` step
     to a `production` environment in a flow with an automatic (push or event) trigger. Other release steps stay
     allowed, since the planner adds one for the first flight environment.
   - Allowed, with notes: `build.script`/`containerfile`/`unitTest.command` (check the build step holds no
     credential the unit-test step lacks, such as registry push), `ephemeralEnvironments` (cap the TTL),
     `notifications`, triggers.
2. **kiac-dev enforces NetworkPolicy.** It runs Cilium 1.20 with Kubernetes NetworkPolicy on; a scratch test showed
   ingress and egress deny-all enforced and a pod-selector allow restoring traffic. The AP-A1 canary is expected to
   pass there; the earlier "fails by design" premise was never tested.
3. **The U8 ClusterRole is approved** (`autopilot/airframe-drafts/rbac/provider-kubernetes-agentrun.yaml`,
   2026-10-09). Review notes for AP-A3: the grant lands on provider-kubernetes's shared service account, so it covers
   every provider-kubernetes `Object`, not only function-agentrun's; Job and ServiceAccount create in any namespace
   can run a pod as any existing service account; namespace patch can drop pod-security labels or add the PR-sweep
   label anywhere. Approved to ship together with it (2026-10-09): a ValidatingAdmissionPolicy matched on the provider's
   service account that confines these kinds to `agent-r-*` run namespaces carrying the run label, never touches
   `pod-security.*` labels or adds the PR-sweep label, and allows only `serviceAccountName: run`; the `batch/jobs` rule
   swapped for the agent-sandbox resources (U11); a binding through a stable service account name. A test proves the
   policy rejects a Job in `default` and a label patch on `kube-system`.
4. **Holmes stays at 0 replicas**, on purpose. A5 (Holmes through Clearance) waits until Holmes is wanted again.
5. **D1: a new Hangar root CA for the platform's Fulcio.** Agent commits (and the platform's other keyless signing)
   chain to a Hangar-owned root rather than a per-cluster self-generated one. Design and rollout are not started.

**Gaps in the existing code that M3 closes:** nothing maps a run pod's identity
(`system:serviceaccount:agent-r-<id>:run`) to the session principal R001 compares against (AP-A4); sessions are held
in memory and their audit entry stores the requested limits only as a hash, so a Clearance restart loses the grant
(AP-A2 needs a durable session store).

**Build order:** AP-A1 -> AP-A3 (render an agent-sandbox `Sandbox`, per U11; hard expiry from its `shutdownTime`, per
U2) -> AP-A2 with AF-2b -> AP-A4 -> AP-B1 -> AP-B2 -> AP-B3 -> AF-8 with AF-6b and AF-10c (the parachute run) -> AP-C1
and AP-C2.

### M4 Skyport AI workloads (weeks 19-24), target 93
Parts 6 to 11, in shape order: task, session, service, scheduled, event, team. Each is walked live, has
a Preflight case with a seeded bad run, and updates its quickstart's verified-state note.

| Task | Notes |
|---|---|
| Part 6 `flight-briefer` | first agent; proves the whole path |
| Part 7 `gate-copilot` | session channel and Tower's chat and approvals |
| Part 8 `passenger-assistant` | the hardened-sandbox fail-closed moment; injection test |
| Part 9 `delay-digest` | trigger runner; artifact store |
| Part 10 `disruption-responder` | trigger bridge; redelivery and storm demos |
| Part 11 `irregular-ops-team` | narrow-only, a denied spawn, a checker catching a wrong fact |
| A new, standalone Autopilot Backstage plugin (fleet-wide console: runs, budgets, the breaker, Preflight, audit) and a narrow Tower Agent tab for app-scoped session chat, reusing the plugin's backend the way Tower's Glidepath tab reuses Glidepath's (decided 2026-09-27, design.md section 8 item 3a); `Agent` XRD and two templates; Holmes via Clearance (drop `github-mcp-token`) | |

**Exit:** six Preflight cases pass and their seeded bad runs fail; one `task_id` traces a disruption from broker message to final artifact.

### M5 Evidence and widen (weeks 25-28), target 97 and 14 of 14
- Preflight as a regression gate on the Autopilot repo: profile, model and policy changes are PRs that must pass.
- Autonomy tracker for one alert class (shadow, then approve, then auto), with the breaker.
- Modelplane hub trial on a dedicated kind cluster, behind the OpenAI-compatible contract.
- **AP-D1** opt-in persistent, resumable state for session and team shapes: size cap, retention TTL, scan before restore (needs U12; design in design.md 3.1).
- Part 12: the nginx edge (optional), born A+.
- Conformance on prod: upper clusters get no runs, and a run cannot be created there.
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
| D6 | Hub isolation for Modelplane | **Decided 2026-09-26:** hosted providers only for now (option 1); per-environment hub with dedicated accounts (option 2) is the M5 default | before M5 |
| D7 | **Preflight's name** | Airworthiness (open; the user likes Autopilot, Clearance, Flight recorder) | before AP-B2 |
| D8 | A new `autopilot` repo | yes; `clearance/` becomes a package in it | M0 |
| D9 | Release-file split and the ArgoCD `exclude` | prove on a scratch app first | M2 |
| D10 | Strictness rollout dates | **Decided 2026-09-26: option A, enforce now** (the fleet sweep is clean). `airframe validate` becomes a required check on gitops PRs. **Built 2026-09-26, not yet required:** Airframe publishes `ghcr.io/jfillman/airframe-validate` (multi-arch, on release tags; contract `validate-values`), Glidepath has the generic `validate-values` Task, `values-check` Pipeline and a gitops onboarding template. Rollout: resync PRs deliver `.tekton/pull-request-values.yaml` to each gitops repo (baggage-api's is #3; boarding-api, flight-api and skyport-broker were triggered), then register `values-validation` in `releaseGuardrails` to make it required. Ground (app repo) env edits are not gated yet: direct commits to main have no PR to block | M1 |
| D11 | Debugging a run without pod exec | accept: debug via output, logs and audit | M3 |
| D12 | Where agent code lives | `airframe/examples/skyport/agents/` | M4 |

## 5. Unverified: answer these in M0
| # | Question | How to check |
|---|---|---|
| U1 | Does ArgoCD apply XRs so that unknown fields are rejected, or pruned silently? | apply an XR with a bogus field to the dev cluster via a scratch Application |
| U2 | Does the function response TTL re-invoke `function-agentrun` near expiry? | a toy composition on a scratch namespace; the expiry test in M3 depends on it |
| U3 | Is Backstage's `mcpActions` endpoint live on a cluster? | request it from the Tower backend |
| U4 | Were Tower's Tier 1 write actions ever live-verified? | click Refresh, Sync and Re-run against a genuinely stuck app |
| U5 | Does the ArgoCD glob `*-lower/*` match `<app>-lower` AppProject names? | `argocd proj list` against the policy |
| U6 | Does Helm ignore unknown `x-hangar-*` keywords in `values.schema.json`? | `helm lint` on a schema with the keys |
| U7 | Can the ArgoCD git files generator exclude `*.release.yaml`? | a scratch ApplicationSet |
| U8 | Does provider-kubernetes accept the rendered Namespace, Quota, NetworkPolicy, ServiceAccount and Job? | `crossplane render` is not possible without Docker; use a scratch XR on the dev cluster |
| U9 | Is pgvector available in the CloudNativePG image? | only if a vector store is wanted |
| U10 | What do Modelplane's usage records contain, and does short-lived auth work for `Existing` clusters? | read a real record, in the M5 trial |
| U11 | Is the upstream Kubernetes SIG Agent Sandbox real and mature enough (warm pools, gVisor/Kata, suspend/resume)? Could `function-agentrun` render its Sandbox object instead of a raw pod? | read the project and its CRDs, then install it on the dev cluster and render one run through it; answer before AP-A3 is built. Its current maturity is second-hand knowledge (see [industry-context.md](industry-context.md)) |
| U12 | Can a run's workspace be snapshotted and restored (volume snapshot on the dev cluster's storage class), and what does restore cost in seconds? | scratch PVC plus VolumeSnapshot on the dev cluster; needed for AP-D1 |

All U-experiments run on the dev cluster (decision 2026-09-26).

### Answers (2026-09-26)
| # | Answer |
|---|---|
| U1 | **Pruned silently, by default.** ArgoCD synced a Redis XR with `persistance: true` and `bogusField: 1`, reported success, and the stored spec had neither. A server-side dry-run with `--validate=strict` rejects them (`strict decoding error: unknown field`), `warn` prints a warning, `ignore` accepts. Enum values (`size: gigantic`) are rejected by the XRD schema either way. So typos in an XR file look accepted and do nothing: `airframe validate` must cover XR files too. |
| U5 | **Yes.** `argocd admin settings rbac can` with `p, role:clearance-lower, applications, sync, *-lower/*, allow`: `flight-api-lower/...` and `backstage-lower/...` allowed; `flight-api/...` (upper) and `app-flight-api-cicd-pr/...` denied. |
| U6 | **Yes.** `helm lint` and `helm template` accept unknown `x-hangar-*` keys at the root and on a property; type enforcement still works (`appName=5` fails). |
| U7 | **Yes, with the real name.** A git files generator with `path: .../*.release.yaml, exclude: true` generated exactly the `dev` and `test` apps and none for `dev.release.yaml` (live, scratch ApplicationSet on the dev cluster). |
| U2 | **No, not on our Crossplane.** A function's response TTL only takes effect when Crossplane's beta realtime-compositions flag is on (it is off: the args are `core start`); otherwise the XR is requeued at the poll interval, default 1 minute, and the per-XR `crossplane.io/poll-interval` annotation cannot go below `--min-poll-interval`, default 1 minute. Measured: a composition that renders the current time re-rendered every 60 s whether the TTL annotation or a 10 s poll-interval annotation was set. Also: installed `function-go-templating` v0.12.3 has no TTL support at all, and installing a second package from the same repo under another name collides in the package lock (health flapped for about a minute, then recovered; nothing was left behind). **Consequence:** expiry cannot be driven by re-invocation faster than about a minute. Use the Sandbox `shutdownTime` (U11: enforced within a second) or the Job's `activeDeadlineSeconds` for hard expiry, and treat Crossplane's poll as the status refresh only. |
| U8 | **Yes, once granted RBAC; today it is denied.** Rendered the six `AgentRun` objects with `function-agentrun`'s own `compose()` (docker.io alpine pinned by digest) and applied them as provider-kubernetes `Object`s on the dev cluster. Before any grant every one failed to observe with `forbidden` (provider-kubernetes has no rights on namespaces, resourcequotas, serviceaccounts, networkpolicies or jobs). With a scratch ClusterRole for exactly those kinds, all six synced and went Ready, the Job **completed** under `pod-security: restricted`, and deleting the Objects removed the run namespace. The narrow role is drafted in `autopilot/airframe-drafts/rbac/`; it must be reviewed as a privilege grant (namespace create/delete cluster-wide) before it ships. Not tested: NetworkPolicy enforcement (believed then not to be enforced on the dev cluster; it is, see "M3 status"), the Modelplane path, or the composition running under a real XR (the function image is not built). |
| U3 | **Partly.** On the prod cluster, Backstage serves `/api/mcp-actions` (401 "Missing credentials", where a made-up path returns 404), so the plugin is mounted and behind auth. Not verified: that it lists Tower/catalog actions with a real token. |
| U4 | **Yes, live-verified 2026-09-27.** `baggage-api` PR #2 (branch `u4-failing-run`) produced a real failed PipelineRun; Tower's Re-run and Cancel were exercised against it and confirmed working before the PR was closed and the branch deleted. |
| U12 | **Not with VolumeSnapshot on the dev cluster today.** The cluster has no snapshot CRDs and its only storage class is `rancher.io/local-path`. Workspace persistence for AP-D1 needs either a snapshot-capable CSI driver or an archive-to-object-store approach (tar the workspace, scan it, store it); restore cost is not measured. |
| U11 | **Real and usable; adopt behind the `AgentRun` contract.** kubernetes-sigs/agent-sandbox v1.0.4 (2026-09-24, weekly releases, API `v1beta1`): `Sandbox`, `SandboxTemplate`, `SandboxClaim`, `SandboxWarmPool`. Installed on the dev cluster (arm64 image works) and measured: a cold sandbox Ready in 2 s (image cached), suspend and resume in about 1 s, a claim served from a warm pool Ready in 89 ms, and a Sandbox with `shutdownTime` and `shutdownPolicy: Delete` was deleted by the controller within a second of expiry. `SandboxTemplate` carries `networkPolicy`/`networkPolicyManagement` and an env-injection policy, which overlap what `function-agentrun` renders. Not tested: gVisor/Kata, snapshot restore, and NetworkPolicy enforcement (believed then not to be enforced on the dev cluster; it is, see "M3 status"). Removed again after the trial. Decision for AP-A3: render a `Sandbox` (or claim) instead of a raw pod, and treat the controller as a pinned dependency. |

## 6. Risks
- **One person, many repos.** airframe, glidepath, backstage, apron, the tenants repos and a new repo all change. Keep every change small, behind a gate, and reversible. Use worktrees.
- **Retrofit cost** if the contract slips behind the next components. Hence the ordering.
- **NetworkPolicy enforcement is per cluster.** kiac-dev enforces it (Cilium; ingress and egress verified 2026-10-09; an earlier version of this list said it did not, which was never tested). `autopilotReady` is still gated on a canary, so runs are never trusted on an assumption.
- **The prod cluster is resource-limited** (observability scaled to 0). Runs are dev-only; prod gets none.
- **Hosted model cost.** Token budgets and the breaker; two on-demand or scheduled spenders in the demo.
- **Upstream churn.** Modelplane is v0.1 and the mcp SDK is v2; both sit behind contracts and pins.
- **Strictness breaks an environment.** Warn first, sweep the fleet, then enforce.

## 7. First ten actions
1. Read `HANDOFF-hangar-autopilot-airframe-a-plus.md` and check each repo's branch and status.
2. Decide D8 (the `autopilot` repo) and D7 (Preflight's name).
3. Answer U1, U5, U6 and U7 (quick, no cluster changes).
4. Write the chart guard in an Airframe worktree with a fixture test; run it through a scratch app.
5. Wire the scorecard and chart tests into CI.
6. Commit `AGENTS.md` for Airframe.
7. Build `airframe validate` v0 (schema plus `helm template`).
8. Provision `baggage-api` through the current flow and log each stumble.
9. Put `airframe validate` on `baggage-api`'s PRs.
10. Re-run the scorecard and update this file's status.
