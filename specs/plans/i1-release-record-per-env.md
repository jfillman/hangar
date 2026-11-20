# I-1: two release steps in one flow overwrite one release record

Written 2026-11-20. Design note only: nothing here is built. Owner review first. Related: strip W-8
([pipeline-trust-t4-split-runner.md](pipeline-trust-t4-split-runner.md)), glidepath#279 (admission policies) and #281 (task mapping).

Read at glidepath `origin/main` `4b5ebf9`; Tower and backstage at their `origin/main`. Shorthand: `GC` = glidepath
`charts/glidepath-catalog/templates`, `GA` = `charts/glidepath-app/templates`, `GCP` = `charts/glidepath-control-plane/templates`,
`API` = `glidepath/api/internal`, `RELAY` = `glidepath/broker/cmd/glidepath-relay`. Every `path:N` is a line in that tree.
Claims about what runs on a live cluster are NOT verified here: this is a read of main only.

## 1. The bug, confirmed

A release record is named from the flow's chain id alone: `name="release-tracking-${CHAIN_ID}"` (`GC/tasks/open-release-pr.yaml:299`).
The chain id is minted once per flow and passed through every event-chained step (`GC/tasks/stage-preflight.yaml:281-306`,
`GA/triggers/flow-triggers.yaml:183`). Nothing stops a flow having two `release` steps: `validateFlows` requires `env` on a release
step and that it be a Flight environment, and restricts a *git-rooted* release to be the sole step, but says outright that an
event-chained release "has no position restriction" and may repeat (`GA/_helpers.tpl:561-690`, esp. 572, 680-690). The two
steps have different `${ENV}`, so different branches (`release-${ENV}-<sha8>`, `open-release-pr.yaml:677-679`), so two real PRs,
and one record name.

What the second step's `write_release_record` (`open-release-pr.yaml:298-357`) does to the first step's record:

| Field | Effect |
|---|---|
| `exists=1` path, merge patch (`:338-348`) | Overwrites `prUrl`, `prCreatedAt`, `releaseId`, `image`, `imageDigest`, `gitRevision`, `env`, `cluster`, `configJson`, `changeRequest*` with the second env's values (empty values are skipped). It never names `state`/`stateAt`, so the second release **inherits the first's state** (`proposed`, or `merged`/`healthy` once the relay has moved it). |
| `kubectl label ... --overwrite` (`:354-357`) | `hangar.io/env` and `hangar.io/cluster` move to the second env. Every label-selected reader now sees one record, for the wrong env. |
| First env's PR | `mark-release-merged` finds a record by `prUrl` (`GC/tasks/mark-release-merged.yaml:58-59`): the URL is gone, so it logs "nothing to mark" and exits 0. Silent. |
| First env's rollout facts | The relay loads by chain only and then compares env/cluster: `RELAY/facts.go:157,162` returns 400 "record for chain ... is for X/Y, fact says ...". Loud, but the release is untracked. |
| Change management | The first env's `changeRequestId` is replaced; `itsm-close` for the first env closes the second's change. On a retry of the second step, `open-release-pr.yaml:738-742` also *reads* the first env's change id from the shared record. |
| Documented invariant | `docs/admin/release-state.md:173` says "a record is one chain, one environment and one PR". It is not. |

The key fact for every option below: **the release id is already per environment.** `releaseId = <chain>:<cluster>/<env>`
(`open-release-pr.yaml:311,861`; parsed at `RELAY/facts.go:91-103`), rides on the Rollout as `hangar.io/release-id`, and
`env` is unique within a chain because `deploy.environments` maps each env name to one cluster (`GA/_helpers.tpl:680-690`). Only the
ConfigMap name drops it.

## 2. Who reads or writes the name

Split by what each one keys on. "Name" readers are the migration surface; the others need no change under option 1.

### Keyed on the name (chain id only): these break or misread when a chain has two records

| Reader | Line | How it finds the record | Needs |
|---|---|---|---|
| `open-release-pr` itself | `:235,298-299,369,396,471,530,583,610,618,730-752` | `release-tracking-${CHAIN_ID}` / `${reissue_of}` / `${ROLLBACK_OF%%:*}` | writer and every self-read use the new name; rollback and reissue targets resolved from a release id / record key, not a bare chain |
| `resolve-release-tracking` | `GC/tasks/resolve-release-tracking.yaml:64-72` | `release-tracking-${CHAIN_ID}`; the Task has only a `chain-id` param | an `env` (and `cluster`) param; the outcome trigger already has both (`GA/triggers/release-outcome-trigger.yaml:25-26`) and `release-outcome-notify.yaml:83-88` calls the Task with `chain-id` only |
| `release-log-emit` | `GC/tasks/release-log-emit.yaml:211-212` | `release-tracking-${CHAIN_ID}` | same: an env |
| `itsm-change` | `GC/tasks/itsm-change.yaml:85-87` (`record_by_chain`; callers `:107,124,128`) | `release-tracking-$1` | the chain callers (`:107,124`) have the run's env; `:128` resolves a rollback's original from `rollback_of%%:*`, and the release id it came from also carries cluster/env |
| glidepath-api `Get` | `API/releases/releases.go:139-151` (`Prefix+chain`), used by `server.go:570` (`GET /releases/{chainId}`), `server/release_run.go:37` (run -> record), `environments/reissue.go:337` | `Prefix + chain` | see section 4 |
| glidepath-api reissue | `API/environments/reissue.go:53` (`chainOf` = `TrimPrefix(name, Prefix)`), `:109` (`uuidRE.MatchString(chain)`) | derives the chain from the *name* | derive from `data.releaseId`, not the name; a suffixed name would fail the UUID check at `:109` and every record would read as "not a release chain id" |
| relay reducer | `RELAY/facts.go:157,302` (`loadRecord`, `recordPrefix+chain`), `:434` (`markRolledBack`, chain from the rollback's release id) | `recordPrefix + chain` | name from the fact's own release id (chain, cluster, env are all in it) |
| relay Argo failure facts | `RELAY/argocd_facts.go:107` (`ChainID: TrimPrefix(pick.Name, recordPrefix)`) | label list, then derives chain from the name | derive from `data.releaseId` |
| Tower | `src/PipelineRunList.tsx:391-392` (`releases.find(r => r.chainId === chain)`), `src/reissue/ReissueRelease.tsx:49,101-114` (`entry.chainId` as React key and reissue argument), `src/reissue/reissue.ts:67-73` | a run's chain id -> one release; chain id as the reissue handle | match on chain **and** env; key and reissue by record key. `fleet/releaseRecords.ts:2` only documents the name. Tower's remaining `release-tracking` references are comments or label reads. |
| backstage | no `release-tracking-` name use in `packages/*/src` or `plugins/*/src` on `origin/main` | none | none (checked by grep only) |

### Keyed on labels, the record's data or the PR URL: name-agnostic

`release-source.sh:60-63` (label + `prUrl`; note it fails closed if more than one record names a PR, which matters to migration),
`extract-promoted-image.yaml:110` (labels app/env/cluster, sorts on `healthyAt`), `mark-release-merged.yaml:58`,
`itsm-gate.yaml:91`, `record-gate-verdict.yaml:66`, `join-release.yaml:56`, `clearance-gate.yaml:682`,
`comment-pr-check-result.yaml:440` (all by `prUrl`), the relay's `supersedeOlder` (`RELAY/facts.go:392-421`, labels),
`close_stale_proposals` (`open-release-pr.yaml:364-390`, labels, skips its own name at `:369`), the sweeper
(`GCP/broker/release-record-sweeper-cronjob.yaml:110-135`, labels, deletes by `.metadata.name`), glidepath-api `List`,
`ListFrom`, `ListEnv`, `ListAll` (`API/releases/releases.go:95-135,165`), and `GET /fleet/releases` / events (`server.go:521-556`).
RBAC is namespace-wide on configmaps (cannot be `resourceNames`-restricted: `GA/identity/pipeline-runner.yaml:48-51`;
`GA/identity/release-record-relay.yaml:14-17`), so a new name needs no grant.

One more place the name is public: the OpenAPI document and contract say `release-tracking-<chainId>` for `Release.name`,
`getRelease`'s summary and the event's `recordName` (`api/openapi.yaml:445,1463,1520,1530`; `contract/glidepath-contract.json:1526`),
and `docs/admin/api.md:49,396,465,514,568`, `release-state.md:19-22,233`, `AGENTS.md:50`.

## 3. Options

### Option 1: one record per environment, `release-tracking-<chain>-<env>`

Writer: `name="release-tracking-${CHAIN_ID}-${ENV}"` at `open-release-pr.yaml:299`, and the same expression at the other eight
self-reads. The suffix is added for every new record (not only when a flow has two release steps, which the writer cannot know).
The chain id is a fixed-width UUID in everything the pipeline mints (`open-release-pr.yaml:283,536`), so a name parses
deterministically: `release-tracking-` + 36 characters is a chain, with an optional `-<env>`. Readers should still prefer
`data.releaseId` and the labels over parsing a name.

- **Migration of existing records.** No rename and no copy: a ConfigMap cannot be renamed, and a copy-then-delete leaves two records
  naming one PR for a while, which `release-source.sh:63-67` treats as "none is trusted" (a gate fails closed). Leave every legacy
  record where it is. Its name is exactly `release-tracking-<chain>`; each carries `env`, `cluster` and `releaseId` in data, so a reader
  that looks up the new name first and the legacy name second, then checks `data.env`/`data.cluster` against the release id
  (the relay already does, `facts.go:162`), reads every legacy record correctly. Legacy records age out through the sweeper
  (`RECORD_TTL_DAYS` is 14, `release-record-sweeper-cronjob.yaml:93-94`, plus the newest five healthy per env kept for rollback
  eligibility). Nothing is orphaned: the sweeper and `List*` are label-based. **Records already clobbered by this bug cannot be repaired**:
  the first env's data is gone from the record (the gitops release file and PR still say what shipped). Not detectable from the cluster;
  list them as "known damaged, flows with two release steps, before the fix" and let them age out.
- **Mixed versions.** The pieces ship separately (catalog Tasks, glidepath-api, relay, Tower). Order: readers first (dual-name lookup
  in API, relay, `resolve-release-tracking`, `release-log-emit`, `itsm-change`, `open-release-pr`'s self-reads, Tower), writer last.
  A reader that only knows the old name and meets a new record is the only unsafe pairing, so the writer flip must wait for every
  reader to be on a version that knows both.
- **API compatibility** (section 4): additive. One behaviour changes, for a case that was silently wrong before.
- **#279 (W-8 step 5).** The policy matches `variables.name.startsWith('release-tracking-')` (`release-record-writes` template, diff
  line 99 of the PR) and the immutable keys `prUrl, releaseId, image, imageDigest, gitRevision, kind` (diff line 114). A suffixed name
  still starts with the prefix: no change to the policy. This is the policy's main reason to fix I-1 first: **today the second release
  step's merge patch changes `prUrl`, `releaseId` and `image` of an existing record, which is exactly what the immutability rule
  refuses.** In Audit it is only a log line; once `recordWritesActions` is `Deny`, the second step's write is refused, the step fails
  after its PR is already open (`open-release-pr.yaml:980`, `finish_after_pr ... || exit 1`), and the PR is left without a record.
  So I-1 must land before #279 is switched to Deny. The immutable-key rule is the *right* behaviour once names are per env.
- **#281 (step 3 mapping).** Mapping is by Pipeline task name (`release` -> `release-record-writer`), not record name, so it does not
  interact. `join-release`, `mark-release-merged`, `itsm-*` find records by `prUrl`/labels. The existing task tests use arbitrary
  record names (`tests/carve_out_tasks_test.sh:39-52,95-107`), which is the name-agnostic behaviour wanted. No change.
- **Sweeper.** Deletes by `.metadata.name` over a label-selected list and groups the keep-window by the three labels
  (`:115-116`), so each env's record ages and is kept independently. No change. (Stall alerts label each record, `:158`:
  per record, so per env, which is correct.)
- **Cost.** About a dozen touch points, all enumerated above. No schema change in a record. Reissue gets one real change: `reissueOf` is
  a chain id today (`open-release-pr.yaml:283`); for a chain with two records it must name the record (see decision 3).

### Option 2: one record per chain, per-env sub-entries (`<env>.prUrl`, `<env>.state`, ...)

Rejected. Reasons, each from the code:

- **Labels.** The record carries one `hangar.io/env` and one `hangar.io/cluster`. Every label-selected reader above
  (`ListEnv`, `supersedeOlder`, `close_stale_proposals`, `extract-promoted-image`, the sweeper's keep-window `group_by`) selects on
  those. One record cannot carry two env labels; all of them would be rewritten to select on key prefixes, which Kubernetes cannot do.
- **Every key moves.** Flat keys (`prUrl`, `state`, `healthyAt`, `mergedAt`, ...) are read and written by `open-release-pr`, the relay's
  reducer and its `state_test.go`, `mark-release-merged`, five itsm/gate Tasks, the sweeper and the API's `Record.Data` map, which Tower
  shows as-is. A `data` shape change is a breaking change to `GET /releases` and Tower.
- **#279 would silently stop protecting.** The immutable-key list is the literal names `prUrl, releaseId, image, ...`; `staging.prUrl`
  is not in it. The policy has to be rewritten to match by key suffix, and until it is, the identity fields are unguarded with no
  error. Worst failure mode of the three.
- **Sweeper and alerts.** One `stateAt` anchors retention and one `hangar.io/stall-alerted` label carries the alert state, so one
  env's terminal state would age or alert the other. ConfigMaps are also capped at 1 MiB, and each env carries its own `configJson`.
- **Migration** is a data rewrite of every record, with the copy-window failure described under option 1.

### Option 3: refuse two release steps in one flow, at validation

In `validateFlows` (`GA/_helpers.tpl:~665`, the per-step loop) fail when a flow has more than one `release` step, or (narrower) two
release steps for the same `env`.

- **Migration, API, #279, #281, sweeper:** none. No record changes shape or name; nothing to migrate or version.
- **What it costs.** It removes a shape the chart documents as supported ("Event-chained release has no position restriction",
  `_helpers.tpl:571-572`; "release -> test", `release.yaml:50`). It breaks any live `cicd.yaml` with two release steps, and **the repo
  cannot tell us whether one exists**: examples 04, 05, 06 and 10 each have one release step (`docs/user/examples/`); the
  `cicd-flow-test-app` that once had two release *flows* (`docs/admin/multi-cluster.md:144`) had two flows, hence two chains.
  A fleet scan of every onboarded app's `cicd.yaml` is needed first.
- **The honest argument for it.** `docs/admin/chaining.md:124` says `change.created` (emitted by `release`) fires "whatever's next".
  If that is at PR-open rather than at merge, a second release step in the same flow opens the prod PR immediately, without waiting
  for the staging release to merge or go healthy; the governed way to promote is Tower's Promote or the `promote-release` template, which
  starts its own flow with its own chain and its own record (`GA/triggers/promote-release-template.yaml:3-4`; `docs/admin/api.md:465`).
  So the multi-release flow may be of little value. Confirm on hangar-dev before relying on it.
- **Not sufficient alone if any live flow has two releases:** validation only stops new renders; the damage on flows already running
  needs a decision on those flows anyway.

### Narrow variant worth doing with option 1

Even with per-env names, two release steps for the *same* env in one flow still collide (same branch name `:677-679`, same
record name). Refuse that in `validateFlows` regardless of which option is picked. This is cheap, never legitimate (the second step has
nothing different to release), and stops the residual case.

## 4. glidepath-api compatibility (option 1)

glidepath-api is the CI/CD interface, so every change is additive and the document is checked by `oasdiff`
(`hack/ci/api_compat_test.sh`; not run here, it needs the tool).

- `GET /v1/apps/{app}/releases/{chainId}`: the path parameter keeps its pattern `^[a-z0-9][a-z0-9-]{0,200}$`
  (`openapi.yaml:~450`), which already admits `<uuid>-<env>`. It becomes a **record key**: exactly the `name` minus the prefix.
  `Get` tries `Prefix+key` as today, which finds both a legacy record (`<chain>`) and a new one (`<chain>-<env>`).
  No existing call changes its answer. For a chain id on its own against a chain that now has only suffixed records, `Get` returns the
  one record if there is one, and **409 with the record keys listed** if there are several (new response code for a case that returned
  one wrong record before; document it). An optional `?env=` query parameter picks one. Both additive.
- `Release` response: add `chainId`, `releaseId`, `env`, `cluster`, `key` (derived from `data`, not from the name). Existing `name` and
  `data` are unchanged; `name` stays the ConfigMap name. Update the `name` description from `release-tracking-<chain-id>` to
  `release-tracking-<chain-id>[-<env>]`. `recordName` on events is the same.
- Reissue list (`API/environments/reissue.go:370`, `chainId` field) keeps `chainId` as the true chain and adds `key`; `POST
  .../{chainId}/reissue` takes a key. `chainOf` (`:53`) and the UUID check (`:109`) read `data.releaseId`.
- Run -> record join (`server/release_run.go:37`): a release run knows its env (`PipelineRun` param); pass it so the record is the
  right one when a chain has several. Falls back to the chain-only path when it does not.
- Versioning: nothing here is a `/v2`. If the owner wants one hard-versioned signal, it is a `X-Glidepath-Record-Naming` response
  header, not a path. Not recommended: the additive fields suffice.

## 5. Recommendation

1. **Option 1**, named `release-tracking-<chain>-<env>` for every new record, with dual-name readers, writer flipped last.
2. **Plus the narrow guard** (refuse two release steps for one env in a flow) in `validateFlows`, in the same change.
3. **Before #279 goes to Deny**, so a flow with two release steps never meets the immutability rule.
4. Treat option 3 (refuse all multi-release flows) as the fallback if the fleet scan shows no live use *and* the owner prefers it:
   it is one validation rule and no migration, but it removes a documented shape. It does not conflict with option 1; it can be
   added later if the shape proves unwanted.
5. Do not do option 2.

Sequence: (a) fleet scan of `cicd.yaml` for flows with two release steps, and of records for any whose `releaseId` chain appears in
two PRs' release files (damaged ones); (b) readers: API, relay, the four Tasks, Tower; (c) writer; (d) docs
(`release-state.md:19-22,173,233`, `api.md`, `AGENTS.md:50`, OpenAPI and the contract file) and CHANGELOG; (e) #279 to Deny.

Tests the change needs: a two-release-step flow fixture in the catalog tests (the existing `release_record_survives_test.py:26,338,499-515`
and `release_reissue_test.py` use a single `RECORD`); a relay test for a fact whose release id names a legacy record and a new one
(`facts_test.go`, `state_test.go`); an `API/releases` test with both name forms and a two-record chain (409); a `validateFlows`
test for the guard; and the #279 policy test (`record_policies_test.py`) with a suffixed name.

## 6. Owner decisions

1. **Option.** Option 1 plus the same-env guard (recommended), option 3 alone (after a fleet scan), or something else.
2. **Fleet scan first?** Is a scan of the onboarded apps' `cicd.yaml` for flows with two or more release steps wanted before
   anything ships? It decides whether option 3 is even possible and how many damaged records exist.
3. **Reissue of a chain with two records.** `reissueOf`/`reissuedBy` carry a chain id today. Keep chain id and add env (a new key),
   or switch both to the record key. The second is simpler for readers and changes what is written to new records only.
4. **Interim guard.** Add the validation refusal (all multi-release flows, or only same-env) now, ahead of the option 1 work, to stop
   new silent corruption? It could break a live flow; the scan answers that.
5. **Damaged records.** Accept that records already clobbered cannot be repaired (let them age out in 14 days), or hand-repair any the
   scan finds from the gitops release files?
6. **Order against #279.** Agree that #279 stays Audit until the writer change is live, and that I-1 is the item that gates it.
7. **409 on an ambiguous chain.** Accept a new 409 on `GET /releases/{chainId}` when a chain has several records, or return a list.
