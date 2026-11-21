# W-8: the gate-verdict ledger write as a glidepath-api record service

Written 2026-11-20. Strip W-8, board strip Y-39, owner choice (b). Continues
[pipeline-trust-t4-split-runner.md](pipeline-trust-t4-split-runner.md) (steps 1 to 3 merged and live; #279 in Audit).
Option (a), a `record-gate-verdict` finally task beside `comment-pr` (draft glidepath#282), is not taken.

Read at glidepath origin/main `3fe3051`. `GC` = glidepath `charts/glidepath-catalog/templates`, `GA` =
`charts/glidepath-app/templates`, `GCP` = `charts/glidepath-control-plane/templates`, `API` = `glidepath/api`.

## 1. Why a service

`comment-pr-check-result` writes the gate ledger (`gate.<sha12>.<gate>` in the release record, resourceVersion CAS,
`GC/tasks/comment-pr-check-result.yaml:432-447`) from its `promotion-ready` step, as `pipeline-runner`. It is a finally
task. Tekton finally tasks all start together, take no `runAfter` and cannot read each other's results, so no other
finally task can be handed its verdict, and a DAG task after it is skipped when the gate fails. So the write cannot move to
another task account. Step 6 (drop `pipeline-runner`'s ConfigMap writes) and #279's Deny both wait on it.

A glidepath-api endpoint moves the write out of the pod altogether. The pod asks; glidepath-api works out the verdict
from the cluster's own objects and writes it under its own account. The pod holds no ConfigMap write right at all.

## 2. The endpoint

`POST /v1/apps/{app}/pipelineruns/{name}/gate-verdict`, next to `.../pipelineruns/{name}/rerun` and `cancel`. `{app}`
resolves to the `-cicd` namespace as every `/v1/apps/{app}` route does; `{name}` is the gate's PipelineRun. The body is
ignored (it may be `{}`). `?dryRun=true` derives and answers without writing.

Answer, 200:

```json
{"outcome": "recorded", "gate": "sast", "sha": "<40 hex>", "pullRequest": 12,
 "prUrl": "https://github.com/<owner>/gitops-<app>/pull/12", "verdict": "success",
 "record": "release-tracking-<chain>", "key": "gate.<sha12>.sast",
 "ledger": {"gate.<sha12>.sast": "success", "gate.<sha12>.sbom": "failure"}}
```

`outcome`: `recorded` (written now), `already-recorded` (this run wrote it before: nothing written), `superseded` (a
newer run of this gate on this commit already wrote: nothing written), `deferred` (the run is within 60 s of its tasks
timeout: nothing written, as today), `no-record` (no release record has this PR's URL: nothing written). `ledger` is this
commit's `gate.<sha12>.*` entries after the call, the only part of the record the promotion decision reads.

Errors use the API's existing shapes: 401 (`GP-AUTH-001/002`), 403 (`GP-GV-403`: not the allowed caller), 404 (no such
run), 422 (`GP-GV-422`: the run is not a gate run of a pull request), 503 (not configured), 502 (the API server failed).

## 3. Authentication: who may call

- **Token:** a projected ServiceAccount token with its own audience, `glidepath-gate-verdict`, 600 s, mounted by the
  Task (as `clearance-gate` does for `clearance`). glidepath-api checks it with a TokenReview that names that audience,
  so the pod's default token, a Clearance token or a broker token is refused (401), and this token is good for nothing
  else (the API server and every other service refuse its audience).
- **Principal:** the user must be exactly `system:serviceaccount:<the app's -cicd namespace>:pipeline-runner`. The list
  of account names is a chart value (`api.gateVerdict.serviceAccounts`, default `[pipeline-runner]`) so the task can move
  to another account later without a code change. Another app's runner gets 403.
- **Pod binding:** a projected token is bound to its pod; TokenReview returns
  `authentication.kubernetes.io/pod-name` and `pod-uid`. glidepath-api reads that pod and requires: same uid, labels
  `tekton.dev/pipelineRun=<name>`, `tekton.dev/pipelineTask=comment-pr`, `tekton.dev/task=comment-pr-check-result`,
  `tekton.dev/memberOf=finally`, and a `tekton.dev/taskRun` whose TaskRun is owned by the PipelineRun (uid). So **only
  the comment-pr pod of that same run** can ask for that run's verdict, and a token copied out of another runner pod of
  the app (a compromised `notify-slack`) cannot write a verdict for any run. A token without pod claims is refused.
- No SubjectAccessReview: the virtual-resource grant would only repeat the principal check. No `X-Glidepath-On-Behalf-Of`
  (refused): nobody acts for anyone here. The audit line is the usual one (op `recordGateVerdict`, tier T1, caller, the
  outcome and key).

## 4. Derivation: the body is a trigger, never a source

Everything is read from objects the Tekton controller and Pipelines-as-Code wrote:

| Field | Source |
|---|---|
| Pull request | PipelineRun label `pipelinesascode.tekton.dev/pull-request` (PaC sets it on `pull_request` and on `retest-comment` runs; seen live on `clearance-gate-cmzmv`, 2026-11-19). Missing or not a number: 422, nothing written. |
| Commit | PipelineRun annotation `pipelinesascode.tekton.dev/sha` (40 hex). |
| PR URL | annotation `pipelinesascode.tekton.dev/repo-url` + `/pull/<n>`; must be `https://github.com/<owner>/gitops-<name>`. |
| Gate | the `gate-name` param of the caller's own comment-pr TaskRun (`spec.params`, filled by the controller: a catalog literal, or `governance-check`'s run param, exactly what comment-pr itself uses today). Must match `^[a-z0-9][a-z0-9-]{0,62}$`. |
| Verdict | the DAG tasks of `status.pipelineSpec.tasks` and their TaskRuns (label `tekton.dev/pipelineRun`): `success` when every DAG task is done (TaskRun `Succeeded` True or False, or listed in `status.skippedTasks`) and every failed one is an `-advisory` task (ADR-0021); otherwise `failure`. This is comment-pr's own rule (`$(tasks.status)` Succeeded/Completed, or only `-advisory` failures), read from the TaskRuns instead of a param. |
| Timeout | the same rule as `promotion-ready`: a success past `startTime + timeouts.tasks` (else `timeouts.pipeline`) is `failure`; within 60 s of it, `deferred`. |

The task's `status`, `pr-number`, `revision` and `gate-name` params are not sent and not read.

## 5. Idempotency: one write per PipelineRun

Beside the verdict, the same patch writes `gateRun.<sha12>.<gate>` = `<creationTimestamp> <pipelinerun name>`
(a new key; nothing reads `gate.` keys by a prefix it matches). Before writing, glidepath-api reads it:

- same run: `already-recorded`, nothing written (a retried call, a replay);
- a run created later: `superseded`, nothing written (an old run must not overwrite the verdict of a `/retest` that
  finished first);
- absent (or written by the old direct path, which writes no `gateRun.` key) or older: write both keys.

The write is a merge patch carrying the record's `resourceVersion`, retried up to 5 times on 409, as today, so two
gates finishing together are serialized and each answer's `ledger` holds every verdict that landed before it.

## 6. The ledger write and its RBAC

- glidepath-api's own account (`platform-system/glidepath-api`) does the patch. Today it holds `configmaps get, list`
  cluster-wide and no write anywhere.
- glidepath-app gains a Role `glidepath-api-gate-ledger` in each app's `-cicd` namespace: `configmaps patch` only (no
  create, update, delete), bound to `platform-system/glidepath-api`. The cluster-wide grant stays read-only.
- RBAC cannot narrow a patch to a name pattern or to keys, so a new ValidatingAdmissionPolicy, `gate-ledger-writes`
  (control plane), matches only that account's ConfigMap writes in a `-cicd` namespace and allows only an UPDATE of an
  existing release record (`release-tracking-*`, labelled `hangar.io/subcomponent=release-tracking`) that changes nothing
  but `gate.<sha12>.<gate>` (`success` or `failure`) and `gateRun.<sha12>.<gate>` keys, adds or removes no other key and
  leaves the labels as they were. **Deny from the start** (`cicdRunAdmission.gateLedgerActions`, default `[Deny]`):
  glidepath-api writes no ConfigMap today, so the policy refuses nothing that works now.
- The existing policies are untouched: `release-record-writes` and `gate-report-writes` match the three task accounts
  only, so glidepath-api is outside them.

## 7. Failure handling

- **API down or slow:** the `promotion-ready` step calls with `curl --retry 4 --retry-all-errors --retry-max-time 60`
  (5 attempts, backoff 1, 2, 4, 8 s, 15 s per attempt, at most a minute: inside `timeouts.finally`, 4 m). A 4xx is not
  retried (it will not change). After that it **fails visibly**: it logs `gate ledger: glidepath-api did not record
  <gate> for <sha7> (HTTP <code>)`, carries on as "no record" (below), and exits 1 at the end. The step is
  `onError: continue`, so the gate's verdict and check run are not changed, and the step shows as failed in the run (Tower,
  debrief).
- **No entry:** promotion keeps today's behaviour when there is no record: this gate decides from its own verdict and the
  other gates' check runs. A missing ledger only loses the "two gates finishing together" tie-break; the next `/retest`
  asks again, and `promote` re-checks every rule itself (PROM-03).
- **Verdict skew:** when the API answered, the step uses the API's verdict for its own promotion decision too, and logs
  it when it differs from the comment step's, so the ledger and the decision never disagree.
- **Old API:** a 404 from an API older than the catalog is logged as such ("upgrade glidepath-api first").

## 8. How promotion reads it

Unchanged readers. The ledger is read only by `promotion-ready` (the fan-in in every gate's finally): its own entry is
its own verdict, the others come from `ledger` (now the API's answer instead of the record it patched) and, when absent,
from the check runs (`newest`). The `promote` Pipeline does not read the ledger; it re-checks the check runs. Tower and
glidepath-api's release reads see two more keys per gate (`gateRun.*`).

## 9. Migration

Every step is a normal PR; each is safe to merge alone (glidepath main deploys to hangar-dev).

| Step | Change | Safe alone because |
|---|---|---|
| 1 | **Add the service** (glidepath): the endpoint, the `glidepath-api-gate-ledger` Role, the `gate-ledger-writes` policy, the task's API path behind catalog `promotion.gateLedger.writer` (`direct` default, `api`). | `direct` renders the task exactly as today; the endpoint has no caller. |
| 2 | **Switch comment-pr-check-result to call it:** `promotion.gateLedger.writer: api` (glidepath default, after the API image with the endpoint is live; the image bump lands after the merge). Watch one release of each gate kind: `gate ledger: recorded` in each `promotion-ready` log, `gateRun.*` keys in the record. | The runner keeps its RBAC; rolling back is the value. |
| 3 | **W-8 step 6:** remove `create, patch, delete` on configmaps from `pipeline-runner` (keep get, list). | No runner task writes a ConfigMap after step 2 and the step-3 mapping (gate reports moved with `clearance-gate`; check `api-compat-gate` and `policy-validation-gate`, which still write `gate-report-*` as runner: they need the same move or an exception before this step). |
| 4 | **#279 to Deny,** its own step: `recordWritesActions` and `gateReportActions` to `[Deny]`, hangar-dev first, prod on the owner's OK. | Audit has shown no runner record write since step 2. |

Rollback: step 2 is the value; step 3 re-adds the verbs; step 4 goes back to Audit.

Draft glidepath#282 stays open, unmerged. The step-2 `record-gate-verdict` Task has no caller either way; removing it is a
follow-up.

## 10. Tests

- **Go (API, `go test -race`):** the handler end to end with a fake cluster: the audience is passed to TokenReview; wrong
  account, wrong namespace, another app's runner, no pod claims, a pod of another run or of another pipeline task, a
  TaskRun owned by another run: refused. Derivation: success, failure, skipped tasks, only `-advisory` failed, a DAG task
  not done, past the timeout, within 60 s (`deferred`), no PR label (422), the body ignored (a body saying `success` on a
  failed run records `failure`). Idempotency: same run twice writes once; an older run after a newer one is
  `superseded`; a key from the old direct path is overwritten. CAS: a 409 is retried and the second gate's answer holds
  both verdicts. `dryRun` writes nothing. No record: `no-record`.
- **Policy (cel-python, `record_policies_test.py`):** `gate-ledger-writes` allows a ledger-only patch; refuses a create,
  a delete, a non-record ConfigMap, a change to `prUrl` or any other key, a removed key, a label change, a verdict other
  than `success`/`failure`; does not match other accounts.
- **Chart:** the least-privilege test admits the new Role and its binding to `platform-system/glidepath-api` with patch
  only; renders with `promotion.gateLedger.writer` `direct` (byte-identical step) and `api` (token volume, no
  `kubectl patch`).
- **Task (`promotion_fan_in_test.sh`):** with `api`, the step calls the endpoint with the projected token, never patches
  a ConfigMap, reads the other gates from the answer, retries a 503 and gives up within the bound, exits 1 visibly while
  still deciding from check runs, and does not retry a 4xx.
- **Live (after step 2, hangar-dev):** a release PR's gates write `gateRun.*`; `kubectl auth can-i patch configmaps
  --as=system:serviceaccount:platform-system:glidepath-api -n app-<app>-cicd` yes, `create` no; a hand-made token-less
  call gets 401.

## 11. Decisions the owner may want to change

1. Path under `/v1/apps/{app}/pipelineruns/{name}` (not `/v1/runs/{ns}/...`), to match rerun and cancel.
2. A dedicated audience plus pod binding, instead of the pod's default token plus a SubjectAccessReview (what
   ref-protection uses).
3. `gateRun.<sha12>.<gate>` as a second key for idempotency and ordering, instead of changing the verdict value.
4. `gate-ledger-writes` in Deny from day one, not staged through Audit.
5. A catalog switch (`promotion.gateLedger.writer`) rather than a fallback from the API to the direct write: once
   switched, a failed call never falls back to a runner write.
6. On API failure the step fails visibly but the gate does not (`onError: continue`, as today).
