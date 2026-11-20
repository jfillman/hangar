# Pipeline trust T4: split `pipeline-runner`

Written 2026-11-20. Strip W-8. Design note only: nothing here is built. Continues
[pipeline-trust-plan.md](pipeline-trust-plan.md) (slice T4; T1-T3 and T3b are done or in flight there). Owner review first.

Read at origin/main of each repo: glidepath `aca3ace`, apron `3e5c583`, clearance `494ff0f`. Citation shorthand:
`GA` = glidepath `charts/glidepath-app/templates`, `GC` = glidepath `charts/glidepath-catalog/templates`,
`GCP` = glidepath `charts/glidepath-control-plane/templates`, `AP` = apron. Every `path:N` is a line in that tree.

## 1. Today

One identity, `pipeline-runner`, runs every catalog task except the few already split out (source-runner, image-pusher,
glidepath-cloud-deployer; `GA/triggers/flow-triggers.yaml:306-327`, `GCP/admission/cicd-run-shape.yaml:177-185`). Repository code no longer reaches it (done in
glidepath#248 and #249), so what is left is the blast radius of a catalog bug: one
flawed task (T2 found a `yq` injection on main) hands over everything below.

### What the runner holds

| # | Permission | Where | Needed by (step) | Verdict |
|---|---|---|---|---|
| R1 | `configmaps`: get, list, create, patch, **delete**, whole namespace | `GA/identity/pipeline-runner.yaml:55-57` | Writes of the release record `release-tracking-<chain>`: `open-release-pr` create/patch/label/supersede (`GC/tasks/open-release-pr.yaml:298-354,384,407,471,583`); `mark-release-merged` (`GC/tasks/mark-release-merged.yaml:58,92`); `itsm-change` (`:91`); `itsm-gate` (`:116`); `comment-pr-check-result` gate ledger, resourceVersion CAS (`:432-445`); `clearance-gate` join of `clearanceId` (`GC/tasks/clearance-gate.yaml:676-690`). Writes of **gate reports** `gate-report-<run>` (not records): `clearance-gate` (`:800-806`), `api-compat-gate` (`:350-355`), `policy-validation-gate` (`:413-418`). Reads: `resolve-release-tracking`, `extract-promoted-image`, `itsm-*`, `release-source.sh`, `clearance-gate:253`. | Writes: split out. Reads: keep. **No catalog step deletes a ConfigMap** (no `kubectl delete` under `GC`); the sweeper does (`GA/identity/release-record-relay.yaml:48-51`). `delete` is unused. |
| R2 | `tekton.dev` pipelineruns, taskruns: get, list, watch | `pipeline-runner.yaml:29-31` | `stage-debrief`, `comment-pr-check-result`, `clearance-gate:800` (owner uid) | keep |
| R3 | pods, pods/log, events, pvcs: get, list, watch | `:32-34` | debrief, log collection | keep |
| R4 | `secrets` get, only `app-secrets`, `dex-check-ride-credentials` | `:41-44` | `run-testworkflow` forwards them (`GC/tasks/run-testworkflow.yaml:339`) | moves to `test-runner` (owner decision 3) |
| R5 | virtual `glidepath.hangar.io/refprotection` get | `:62-64` | first task of every privileged Pipeline (T3) | keep |
| R6 | rollouts get/list/watch in each local env namespace | `GA/env/deploy-rbac.yaml:21-43` | `deploy-manifests:236` | keep |
| R7 | Argo `applications` get, patch in `argocd-apps` (lower envs) and `argocd` (DORA) | `GA/env/argocd-refresh-rbac.yaml:19-42`, `GA/argocd/release-application.yaml:50-75` | `deploy-manifests:216`, `mark-release-pending:94` | keep |
| R8 | policy-config get; cluster-registry get | `GA/governance/policy-config.yaml:43-60`, `GA/clusters/read-registry-rbac.yaml:20-37` | gates, `open-release-pr` | keep |
| R9 | testkube `secrets` get/update/patch for `<app>-app-secrets`, plus the `testkube-testworkflow-runner` role | `GA/testkube/rbac-and-secret.yaml:58-89` | `run-testworkflow:354,394,508` | moves to `test-runner` |

### The token Clearance trusts

- The Task declares a projected token, audience `clearance` (`GC/tasks/clearance-gate.yaml:112-118`; `agentGates.audience`
  at `glidepath charts/glidepath-catalog/values.yaml:246`). Its principal is the **pod's ServiceAccount**, so it is
  `app-<app>-cicd/pipeline-runner`. Four Tasks mount it: `clearance-gate` (`:155,404-406,650-651,713-735`: provenance and
  registration), `agent-gates` (`GC/tasks/agent-gates.yaml:42-44,98-99`: provenance), `agent-definitions`
  (`:37,86-87`: definitions review), `agent-release` (`:43,84`: review and registration).
- Clearance's core authenticates it by TokenReview for the `clearance` audience and yields `<namespace>/<serviceaccount>`
  (`clearance internal/authn/workload.go:91-159`). It is trusted because that string matches a glob in
  `CLEARANCE_VERIFIERS` (`clearance internal/gate/service.go:292`, `internal/gate/outcome.go:479`). It is a **principal
  glob, not a token-audience or SA-name check of its own**: any account named in the list gets it. A verifier named
  `app-<app>-cicd/<sa>` is bound to its own app (`service.go:65,312-316`), for any `<sa>`.
- Apron renders the list as `app-*-cicd/pipeline-runner` plus GitHub workflows (`AP hack/render.py:369`,
  `templates/TOKENS.md:167`), and names the same string as the Map's gate instance (`render.py:853-859`,
  `docs/clearance-map.md:49,52-55`, fixture `tests/run.sh:889`).
- Clearance's source names `pipeline-runner` nowhere (only a historical note, `docs/gate.md:1517`). A move needs **config only**, no
  Clearance code.

### Where the RBAC is rendered

Apron does **not** render the runner's Role or ServiceAccount: they are in the glidepath-app chart
(`GA/identity/pipeline-runner.yaml`, one release per app). Apron renders the control-plane admission values
(`AP templates/50-glidepath/glidepath-control-plane/values.yaml:187-192`), the Kyverno mirror of the run rules for
glidepath-api reruns (`AP templates/30-policy/kyverno-policies/tower-identity-writes.yaml:108-142`) and the task lists
pinned in `versions.glidepathRunTasks` (`AP docs/glidepath-run-policies.md:33,92`, `hack/glidepath_tasks.py`). So T4 is a
Glidepath release plus an Apron pin and Clearance-trust change.

## 2. Target

Four task accounts replace the one (owner decision 3 adds `test-runner`). None may create runs (the same invariant as today).

| Identity | Holds | Runs |
|---|---|---|
| `pipeline-runner` (read-mostly) | R2, R3, R5, R6, R7, R8, and configmaps **get, list** only. No create, patch, delete. No Secret. No `clearance` audience. | Every catalog task not named below. |
| `test-runner` | R4 (`app-secrets`, `dex-check-ride-credentials` get), R9 (testkube secrets and the `testkube-testworkflow-runner` role), R2 and R3 for its own logs. No ConfigMap write, no `clearance` audience. | `run-testworkflow` only. |
| `release-record-writer` | configmaps get, list, create, patch (no delete, no update) in the app's `-cicd` namespace; enforced to release records by the admission policy below. Read-only R8 grant for the cluster-registry (`open-release-pr` reads it, `GC/tasks/open-release-pr.yaml:846`; the policy-config is not referenced there, so not granted). No Secret, no `clearance` audience. | `open-release-pr`; `mark-release-merged`; `itsm-change`; `itsm-gate`; and two **new small Tasks** carved out of tasks that must stay runner: `record-gate-verdict` (the ledger write from `comment-pr-check-result:432-447`) and `join-release` (from `clearance-gate:676-690`). |
| `clearance-gate` | get pipelineruns; get configmaps; create, patch configmaps (gate reports only, enforced by the policy below); the `clearance` audience. No record write, no Secret. | `clearance-gate`, `agent-gates`, `agent-definitions`, `agent-release` (the four Tasks that present the token). |

### How the narrow record writer is reached

Recommended: **a separate Task per write, with its own ServiceAccount**, selected per task in `taskRunSpecs`. This is the
mechanism already used for source-runner, image-pusher and the cloud deployer: `taskRunSpecs` in the Trigger and
onboarding templates (`GA/triggers/flow-triggers.yaml:310-325`, `pull-request-clearance-gate.yaml:45-49`), an allowlist per
Pipeline in `cicdRunAdmission` (`GCP/values.yaml:68-85`; the check at `cicd-run-shape.yaml:177-185` gains two branches) and
a chart test that derives the lists from the catalog. Tekton fixes the account per pod, so a step cannot change it.
`open-release-pr` and `mark-release-merged` move whole (they are catalog code, already trusted with the GitHub token);
only the ledger write and the join are carved out, passing their inputs by Task result (the ledger is a handful of
`gate.<sha12>.<gate>` keys; the 4 KiB result limit is a check in step 3).

RBAC cannot narrow `create` by name, and a ConfigMap write cannot be limited to keys. So two ValidatingAdmissionPolicies
in the control plane do that part (the repo already stages policies Warn, Audit, Deny: `GCP/admission/cicd-run-shape.yaml:223-226`):
- **`release-record-writes`**: a request from `pipeline-runner` or `clearance-gate` may not create, update or delete a
  ConfigMap whose name starts `release-tracking-` or that carries `hangar.io/subcomponent=release-tracking`, nor add that
  label. A request from `release-record-writer` may touch only such ConfigMaps (and no `gate-report-*`), and may not change
  the immutable keys (`prUrl`, `releaseId`, image, sha, `kind`) after create (compare `object` and `oldObject`).
- **`gate-report-writes`**: `clearance-gate` and `pipeline-runner` may create or patch only `gate-report-<run>` with an
  owner reference to a PipelineRun of this namespace.

Considered and not chosen now: a **small service** (a glidepath-api endpoint family, called with a projected token and
authorized by SubjectAccessReview exactly like `/v1/apps/{app}/ref-protection`, `glidepath api/openapi.yaml:781-786`).
It would also enforce per-key and state-transition rules server side, which RBAC and policy cannot, and it matches
"glidepath-api is THE CI/CD interface". It costs a new availability dependency in the release path and a larger build.
Recommendation: ship the per-Task accounts now (it closes the stated gap), and treat the service as a follow-up only if the
owner wants key-level rules.

### How Clearance trust moves

1. Core `verifiers` gains `app-*-cicd/clearance-gate` **beside** `app-*-cicd/pipeline-runner` (`AP render.py:369` reads
   `clearance.verifiers`, so no render change is strictly needed to add it; a change is needed to drop the old one).
2. Glidepath releases with the four Tasks on `clearance-gate`. Nothing else changes in Clearance: the app binding
   (`service.go:65,312`) already applies to any `<sa>`.
3. Apron's gate instance changes to `app-<app>-cicd/clearance-gate` (`render.py:859`, `docs/clearance-map.md:49`, `tests/run.sh:889`).
   During the overlap it declares both, so the Map does not show `silent` for either (`internal/api/map.go:482-485`).
4. Drop `app-*-cicd/pipeline-runner` from the render (`render.py:369`). From then on a pod that is still `pipeline-runner`
   and presents a `clearance` token gets 403 (`NotVerifier`): **fail closed**.

## 3. Blast radius

| A compromised step of ... | Before | After |
|---|---|---|
| Any runner task (e.g. `notify-slack`, `deploy-manifests`) | Create, change or delete any release record (forges what `extract-promoted-image` and the gates read; `docs/admin/security.md:155,689`); read `app-secrets`; patch its Argo Applications. | Read the records, read `app-secrets` (unchanged, R4), patch its Argo Applications (unchanged, R7). Cannot write or delete a record: RBAC and the policy both refuse. |
| `clearance-gate`, `agent-*` (the token pods) | All of the above **and** register or attest a change as the pipeline for its own app (the registrar). | Register for its own app (this is the Task's job; unchanged) and write gate reports. No record write, no `app-secrets`. |
| `open-release-pr` and the other writer tasks | Both of the above. | Write or alter release records within the immutable-key rules; cannot register with Clearance, read a Secret or patch an Application. |

What does **not** change: a catalog task that holds the Clearance token can still register for its app, and the GitHub
installation token is projected per Task, not an RBAC matter. T4 shrinks which steps hold each power; it does not remove
the powers. The record is still not trusted on its own contents (`security.md:155-160`).

## 4. Migration order (no downtime, no hand-made Secrets)

Every step is a normal reviewed PR; the lab does not need to hold merges for downtime. All three accounts are
ServiceAccounts in the glidepath-app chart, and every token is a **projected, audience-bound SA token** requested by the
Task (as `GC/tasks/clearance-gate.yaml:112-118` already does). No Secret is created by hand; none is created at all.

| Step | Change | Owner step? |
|---|---|---|
| 1 | Clearance trust, additive: add `app-*-cicd/clearance-gate` to `clearance.verifiers` and declare the second gate instance (apron). Harmless while nothing uses it. | Apron render PR is the agent's; **the cluster render and Argo sync is the owner's call** for prod (hangar-dev first). |
| 2 | Glidepath chart: add the `release-record-writer`, `clearance-gate` and `test-runner` accounts, Roles and RoleBindings (`test-runner` gets R4, R9, R2, R3; it must exist before step 3 maps `run-testworkflow`); keep the runner's R1, R4 and R9 as is. Add `cicdRunAdmission.recordWriterTasks`, `clearanceTasks` and `testRunnerTasks` and the three new branches in `cicd-run-shape` (default Warn). Add the carve-out Tasks `record-gate-verdict` and `join-release`. A chart test (extend `tests/pipeline_least_privilege_test.py`) fails if anything binds a Role beyond the table. | no |
| 3 | Move the tasks: add `taskRunSpecs` to the Trigger templates (`promote-release-template.yaml:67`, rollback, outcome) and to the onboarding templates (`pull-request-merged`, `pull-request-clearance-gate`, `pull-request-agent-*`, `push-agent-release`). Tasks run on the new accounts; the runner still has its old rights, so a missed mapping still works. | Apps' `.tekton/` files regenerate through onboarding-resync (T6); **the merge of those gitops PRs is a person's** (review rule). |
| 4 | Apron: pin the new Glidepath, update `versions.glidepathRunTasks`, mirror the two lists in `tower-identity-writes.yaml:108-142`. | Commits to repos that need a person's gitsign signature: **owner step if signing blocks** |
| 5 | Turn the admission policies to Audit, then Deny (`release-record-writes`, `gate-report-writes`, the SA allowlists). Watch Audit for one release of every kind: promote, rollback, bypass-merge, itsm, every gate. **Gate for Deny: every app has merged its onboarding-resync and no active run still uses the old `pipeline-runner` mapping** (list TaskRuns by SA per app). | Choosing Deny is the owner's call (T6 rule: prod only with OK) |
| 6 | Remove R1's `create, patch, delete` from `pipeline-runner` (keep get, list). Remove `app-secrets` read from the runner only if open question 3 is answered yes. | no (after Audit is clean) |
| 7 | Clearance, subtractive: drop `app-*-cicd/pipeline-runner` from `verifiers` and the old gate instance. | Cluster render sync is the owner's; only after step 5 is clean |

Rollback: steps 6 and 7 remove a right. Reverting step 6 means re-adding the RBAC **and** setting the admission policies (`release-record-writes`, `gate-report-writes`) back to Audit or narrowing them, since RBAC alone would still be refused by the policy. Step 7 reverts by re-adding the verifier line. Steps 1-5 only add.

No key material is involved: nothing here mints or stores a long-lived credential, so Infisical is not touched.

## 5. Risks, verification, open questions

| Risk | Step | Check |
|---|---|---|
| An app not yet resynced still runs `clearance-gate` as the runner and fails at step 7 | 7 | Before 7, list each app's last gate run and the SA on its TaskRun (`kubectl get taskrun -o jsonpath` per app on hangar-dev); require all on `clearance-gate`. Fail-closed is the safe direction. |
| Ledger or join passed by Task result exceeds Tekton's 4 KiB result limit, or loses the resourceVersion CAS | 2-3 | Unit test with a 20-gate ledger; keep the CAS inside `record-gate-verdict`, so the result is only the verdict list. Extend `tests/release_record_survives_test.py`. |
| The policies refuse a legitimate write (a record label or key written by the relay or sweeper) | 5 | The control-plane accounts (`glidepath-relay`, `release-record-sweeper`, `GA/identity/release-record-relay.yaml`) are exempt by name; Audit run first; the test fixtures from `GCP/tests/cicd_run_admission_test.py`. |
| Missing `taskRunSpecs` on a platform-triggered run (a Trigger template, not PaC; `cicd-run-shape` only covers PaC runs, `:65-68`) | 3 | The chart test renders every Trigger and asserts the writer and gate tasks are mapped; a glidepath-api rerun keeps them (extends the T5 rule). |
| New `clearance-gate` account widens Clearance trust to any `app-*-cicd/clearance-gate` | 1 | The app binding already limits it to its own app (`service.go:312`); the account has no run creation and the admission lists name its tasks. |
| Gate Map goes `silent` when the instance changes | 1, 7 | `tests/run.sh` fixture updated; check the live Map after 1 and 7. |
| Live check | all | Per step, run a real promote, rollback and gate on hangar-dev and read the Role with `kubectl auth can-i --as=system:serviceaccount:app-<app>-cicd:<sa>` for each right in the table: runner `create configmaps` and `get secrets` must be `no` after step 6; writer `get secrets` `no`; `clearance-gate` `create pipelineruns` `no`. |

### Owner decisions (2026-11-20)

1. **Per-Task accounts now; the glidepath-api record service is a later follow-up.**
2. **One `clearance-gate` account for all four Clearance-token Tasks.** A separate account for `agent-release` would not
   narrow the `agent-pin` token: the broker accepts any caller whose TokenReview namespace is the app's `-cicd` namespace
   and does not check the SA (`glidepath/broker/cmd/token-review-interceptor/agentpin.go:10,43,232-239`). Which token a pod
   holds is fixed by its Task's projected volume, and no task account can create pods or TaskRuns or request tokens.
   Follow-up (not in this slice): the broker checks the SA as well, so `agent-pin` is bound to `clearance-gate`.
3. **`run-testworkflow` moves to its own `test-runner` account in this slice** (R4 and R9 leave `pipeline-runner`, which then
   reads no Secret). Step 3 maps it, step 5's allowlists name it, step 6 removes R4 and R9 from the runner, and the live
   check adds `pipeline-runner get secrets` = `no`.
4. **Gate reports stay ConfigMaps, limited by `gate-report-writes`.** A gate report is a display and debrief artifact; the
   Clearance record is the authority, so a forged report cannot change a verdict. A new object kind would add a CRD and
   a migration for little gain. Reports move with the record service if that is built.
5. **The overlap is bounded, and old records keep `pipeline-runner`.** `CLEARANCE_VERIFIERS` is checked when a call is made
   (`internal/core/core.go:13`), so dropping the principal does not invalidate stored records, and history is append-only.
   The one tie to the registrant is the exact-registrant rule for a later call on the same change
   (`internal/gate/outcome.go:261`). So step 7 waits until no open change registered by `app-*-cicd/pipeline-runner`
   remains (closed, or past its policy TTL, `internal/gate/change.go:234`), and at most two weeks after prod Deny. The Map
   shows both gate instances until then.
6. **hangar-dev runs Deny at step 5 first; prod only after the owner's OK.**
