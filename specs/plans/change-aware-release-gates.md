---
title: Change-aware release gates
program: Hangar · Clearance, Autopilot, Glidepath
board: https://claude.ai/artifact/7bptZqWD7RdUDxyR4TQ8o9
updated: 2026-11-24
---

Every Glidepath release gate runs on every pull request to a gitops repo's `main`. Each gate decides from the PR's own
diff what kind of change it is judging, and reports one of three things: it ran, it ran as advisory, or it does not
apply to this kind of change. This lets a config-only change merge under a required-checks ruleset without weakening any
gate on an image release, and every other PR still reports every required check. The owner approved the design and
answered every open question on 2026-11-24 (section 13). Building starts with CG-1.

Written 2026-11-23 against glidepath `origin/main` `e5d27d8` (glidepath#299 merged), Tower `origin/main` `d4ad869` and
backstage `origin/main`. Shorthand: `GC` = glidepath `charts/glidepath-catalog/templates`, `GV` =
`charts/glidepath-catalog/values.yaml`, `OT` = `charts/glidepath-app/files/onboarding-templates`, `API` =
`glidepath/api/internal`, `BE` = backstage `packages/backend/src`. A `path:N` is a line in that tree on that commit.
Statements about what runs on a live cluster come from reading main. Where something was checked live, the text says
so. Strips: I-84 (trigger by branch name), I-85 (timeouts).

## 1. The problem {#problem}

gitops-gate-api#96 changes one file, `hangar-prod/staging/values.yaml` (staging replicas 1 to 2), from branch
`release-slack-test`. The branch name starts with `release-`, so every gate ran. Checked live on the PR's head:

| Check | Result | Why |
|---|---|---|
| `values-`, `policy-validation-` | success | they judge the manifests, which is what changed |
| `clearance-gate-` | success after a Slack clear | tier 2 (replicas), held for one owner who is not the author: correct |
| `sast-`, `sbom-`, `image-scan-`, `api-compat-`, `qa-` | failure | `resolve-promoted-image` found no `release.image.repository/tag` in the changed values file (`GC/stepactions/resolve-promoted-image.yaml:118-134`) |
| `provenance-` | failure | no PR commit carries `X-App-Repo`/`X-App-Commit` trailers (`GC/tasks/verify-commit-signature.yaml:168-173`) |
| `itsm-` | failure | no release record, so no `changeRequestId`, and no `glidepath:change-request` marker in the body (`GC/tasks/itsm-gate.yaml:90-106`) |

Two details matter for the design:

- `api-compat` and `qa` are advisory (`GV:414-430`) but still went red. Their advisory copy only covers the check task.
  The first task, `extract-promoted-image`, is hard, and it fails before the copy runs (`GC/pipelines/api-compat-check.yaml:42,64`).
- With a branch not named `release-*`, most of these gates do not run at all. On an enforced ruleset that blocks the
  merge forever: a required check that never reports never passes. Since 2026-09-27, `docs/admin/github-ruleset.md:47-53`
  has recorded this as problem 1. It cannot be solved in the ruleset, because a ruleset cannot condition on the head branch.

Today's triggers, in `OT/gitops-repo/pull-request-*.yaml`:

| Gate | Trigger (`on-cel-expression`) |
|---|---|
| sast, sbom, image-scan, provenance, itsm, qa, api-compat, policy-validation | `source_branch.startsWith("release-") && !startsWith("release-record-")` (e.g. `pull-request-sast.yaml:53`) |
| clearance-gate | glidepath#299: `release-*`, **or** any changed deployable file (`pull-request-clearance-gate.yaml:27`) |
| values | any `values.yaml`, `release.yaml` or `/base.yaml` (`pull-request-values.yaml:18`) |
| agent-gates | every PR to main (`pull-request-agent-gates.yaml:17`) |

So the branch name decides which gates judge a change, not the change itself. A config change on a `release-*`
branch fails seven gates. An image change on any other branch runs almost none of them.

## 2. What exists and is reused {#existing}

- **The registry.** `releaseGuardrails` (`GV:377-487`): each gate has `name`, `status`, `class`
  (`content | integrity | process | approval`), optional `targets`, and `required`. A cluster changes `required` through
  `releaseGuardrailOverrides` (`GV:495`), and one app through `releaseGuardrailOverridesByApp` (`GV:507`). The helper
  `glidepath-catalog.guardrails` (`GC/_helpers.tpl:106-140`) resolves the registry once. Every consumer renders from that
  result: the gate Pipelines, `detect-bypass-merge` (`GC/tasks/detect-bypass-merge.yaml:117`), `release-log-emit`
  (`GC/tasks/release-log-emit.yaml:169`), `wait-for-release-guardrails`, `open-release-pr`'s gate table, and
  `hack/apply-guardrail-ruleset.sh` (`docs/admin/release-guardrails.md:24-33`).
- **Locked gates.** `sast` and `provenance` refuse `required: false`, so the chart fails to render
  (`GC/_helpers.tpl:121-123`). The per-app map refuses them too (`:227-260`).
- **The content-based precedent: ADR-0021 decision 8** (`docs/admin/adr/0021-rollout-facts-and-release-record.md:132-153`).
  On an eligible rollback, the content gates run an `-advisory` copy. `extract-promoted-image`'s `rollback-eligibility`
  step (`GC/tasks/extract-promoted-image.yaml:67-119`) decides eligibility from the image the PR's diff promotes and the
  release records (the last five healthy releases of that app/env/cluster). It never reads the PR's text: "a PR that calls
  itself a rollback but targets anything else gets the full gate set" (`:69-71`). This design generalises that rule.
- **The promotion fan-in** (`docs/admin/registries.md:65-110`, ADR-0025, ADR-0029). Each gate's `finally`
  (`comment-pr-check-result`, step `promotion-ready`) records its verdict as `gate.<sha12>.<gate>` in the release
  record's gate ledger. With `gateLedger.writer: api` it goes through glidepath-api's `gate-verdict` route, which
  derives the verdict from the run's own TaskRuns (`API/gateverdict/gateverdict.go:254-316`). When the last gate
  finishes with every required gate green, it sends `promotion-ready`, and `promote` re-checks under PROM-03
  (`GC/tasks/promote.yaml:137-166`). "With no release record (a PR opened by hand) the check runs alone decide"
  (`registries.md:89`). The fan-in skips "a branch that is not `release-*`" (`registries.md:100`,
  `GC/tasks/comment-pr-check-result.yaml:475`), which is another place the branch name decides.
- **A non-release PR in the Clearance gate.** The proposer is the PR author, provenance is the agent gates' verdict,
  and the tier comes from the rendered diff (`docs/admin/clearance-gate.md:31-35`). The gate already checks out and
  renders **base and head** (`GC/tasks/clearance-gate.yaml:254-285`).
- **itsm** (`docs/admin/change-management.md`): the release record's `changeRequestId` comes first, then the PR body's
  marker. `open-release-pr` creates the change (`GC/tasks/open-release-pr.yaml:234-238`, `release-kind` `promote|rollback`
  at `:100-103`).
- **provenance's two signature paths** (ADR-0027, `docs/admin/commit-signing.md`): gitsign, or a GitHub merge by an
  `allowedMergers` login with optional strict mode and approvals. Both verify the **app** commit that the trailers name,
  not the gitops PR's commits.
- **Protection** (`charts/glidepath-catalog/files/lib/protection.sh`, `clearance-gate.md` "Which environments are
  protected"): Clearance decides where it runs. Without Clearance, `production: true` decides. Unknown counts as protected.
- **Tower's config PR.** The Values form's "Open config PR" (Tower `src/values/ValuesForm.tsx:2636`) posts to the
  Backstage backend's `/config` (`BE/glidepathProvenance.ts:1630`). That calls `submitConfigChange`
  (`BE/glidepathConfig.ts:193-262`), which opens a `config-<env>-…` PR **with no release record and no change request**,
  and refuses image fields (`assertPatchIsSafe`, `:160-170`). It runs in Backstage, not glidepath-api.
- **How Tower shows gates.** The Release Record's "Release gates" grid shows "N/M passed" (Tower
  `src/ReleaseRecordDetail.tsx:677-697`). The count comes from `BE/pullRequests.ts:349`
  (`passedChecks = runs.filter(conclusion === 'success')`).

## 3. Decisions the owner already made {#approved}

1. One check per gate stays. A single aggregate check may be added, but only alongside the per-gate checks (section 11).
2. Every gate runs on every PR to `main`. The owner first set this as "every PR that changes deployable files" (the
   glidepath#299 trigger, extended to all gates), then widened it to every PR on 2026-11-24 (Q1). The deployable-files
   predicate moved into the classifier, where it separates `no-op` from the other kinds.
3. A shared classifier works out the change kind from the PR's diff (and from the render where needed). It never reads the
   branch name, the PR text or commit trailers.
4. A class × kind matrix gives each gate one of run / advisory / not applicable for each kind. "Not applicable" is a
   green check, a PR comment and `n/a` in the ledger. The fan-in counts `n/a` as satisfied. Every reader shows `n/a`
   explicitly, never as a pass.
5. provenance on a config change checks the gitops PR's own signature or reviewed merge, and records the proposer.
6. itsm on a config change stays required for protected environments.
7. A "propose config change" action opens the PR with a release record and change request, as an image release does.
8. The migration covers order, resync, the ruleset and tests.

## 4. The trigger {#trigger}

Every gitops-repo gate template (`OT/gitops-repo/pull-request-<gate>.yaml`) triggers on **every pull request to
`main`** (Q1, decided 2026-11-24) and drops the branch clause:

```
event == "pull_request" && target_branch == "main"
```

- `release-*` is no longer a condition, and nothing about the files changed is either. Every required check reports on
  every PR, so a PR that changes nothing deployable can still merge on an enforced ruleset.
- The deployable-files predicate from glidepath#299 moves into the classifier (section 5.2, step 2). It is the line
  between `no-op` and the other kinds:

  ```
  !f.startsWith(".tekton/") && !f.startsWith("releases/") &&
  (f.matches("(values|release|base|kustomization)[^/]*\\.ya?ml$") || f.endsWith("Kustomization") ||
   f.matches("^[^/]+/[^/]+/.+\\.(ya?ml|json)$"))
  ```

- A PR that changes nothing deployable, such as an onboarding-resync PR (`.tekton/` only), a Release Record PR
  (`releases/` only) or a README edit, classifies as `no-op`, and every gate except `agent-gates` reports `n/a`
  (`agent-gates` judges who opened the PR, so it runs on every PR, section 6). The cost is about 11 small PipelineRuns
  per such PR (section 12.2).
- `release-record-*` PRs need no exclusion: they only add `releases/<app>@<version>.yaml`, so they classify as `no-op`.
- The classifier (section 5) decides what each gate does, so the trigger needs no judgement of its own.
- All gate templates must carry the identical expression. A test asserts it (CG-9).

## 5. The classifier {#classifier}

### 5.1 Kinds

| Kind | When | Precedence |
|---|---|---|
| `image-release` | any image reference in a deployable file changes, whoever wrote the change, and it is not an eligible rollback | 1 (highest) |
| `rollback` | every image change in the PR is the release image of a `<cluster>/<env>` returning to an **eligible** earlier image (ADR-0021: one of the last five healthy releases of that app/env/cluster, `extract-promoted-image.yaml:109-119`, unchanged) | 2 |
| `config` | deployable files change semantically, and no image reference changes | 3 |
| `no-op` | nothing deployable changes semantically (comments, whitespace, key order), or no deployable file changed | 4 |

The PR's kind is the highest kind of any environment it touches. A PR that mixes an image change with a config change
is `image-release`.

**A hand-edited image change is `image-release`, and that is intended.** Every content gate runs. provenance refuses
it, because no PR commit carries the trailers that name the app commit (`verify-commit-signature.yaml:168-173`). qa
refuses an image with no check ride attested on it, and sast refuses one with no build attestation. An image
Glidepath did not build cannot be released by editing a file. Images reach an environment through promote or rollback.
A hand-edited return to an eligible earlier image classifies as `rollback`, so the content gates only advise, but
provenance (integrity) still blocks it for the same trailer reason. Tower's rollback action is the supported path.
This matches ADR-0021 today.

### 5.2 Algorithm

Inputs: repository, PR number, head SHA. Every read goes through the GitHub API with the same per-run installation
token the gates use today. There is no clone.

1. `GET pulls/{n}` gives the base SHA. `GET compare/{base}...{head}` gives the changed files **including removed and
   renamed ones**. Today's resolver drops removed files (`resolve-promoted-image.yaml:109`); the classifier must not,
   because deleting a manifest is a change. The compare is three-dot, so `main` moving on does not change the answer.
2. Keep only the deployable files: the predicate in section 4, plus the template side of an own chart under
   `<cluster>/<env>/` (a `.tpl` helper, anything under `templates/`, `Chart.yaml`, `Chart.lock`, a packaged subchart
   under `charts/`). The predicate matches only YAML and JSON, so without the second half a PR that changes only a
   chart helper would be `no-op` and skip the render backstop. Template-side files are not parsed: they make their
   environment `config` with `renderCheck: required` (step 8). An own chart's values files (any other YAML or JSON in
   it, `values.yaml`, `values-*.yaml`, a subchart's values) are parsed like every values file, so an image change in
   them is `image-release` (section 5.1) and never reaches the backstop as a surprise. If no file is left, the kind is
   `no-op`.
3. Map each file to the environments it feeds. `<cluster>/<env>/…` is one environment. `<cluster>/base.yaml` feeds
   every environment under `<cluster>/`, listed from the head tree. A `kustomization` file feeds the directory it is in.
4. For each file, read it at base and head (an added file has no base, a removed file has no head) and pull out
   **image references**:
   - values, release and base files: `release.image.{repository,tag,digest,source}`, the deprecated `rollout.image.*`,
     and every other map or leaf under a key named `image` or `images` (component images, sidecars);
   - raw manifests (YAML or JSON under `<cluster>/<env>/`): every `image` string anywhere in the document;
   - kustomization files: `images:` entries (`name`, `newName`, `newTag`, `digest`) and image keys in
     `helmCharts[].valuesInline`.
5. For each environment: `imageChanged` is true if the normalised image-reference sets differ (path → `repo[:tag][@digest]`).
   `configChanged` is true if anything else differs after a semantic YAML compare.
6. **Rollback eligibility** applies only when the one changed image reference in that environment is its release image.
   It uses the existing release-record query, unchanged, moved out of `extract-promoted-image` into the classifier.
7. **Fail closed.** If a file does not parse, the compare is truncated (GitHub's 300-file limit) or any read fails, the
   kind is `image-release`. The full gate set then runs and the image gates fail loudly. Nothing gets lighter treatment
   because of a doubt.
8. **Changes only a render can judge.** A chart pin change (`chart.targetRevision`, `repoURL`, an own-chart directory)
   or a remote kustomize base can change images with no image key moving. Such an environment is `config` with
   `renderCheck: required`. The render backstop (section 5.4) compares the rendered images.

The output is versioned JSON:

```json
{"v": 1, "classifier": "<catalog version>", "pr": 96, "base": "<sha>", "head": "<sha>",
 "kind": "config", "reason": "hangar-prod/staging: values changed (rollout.replicas); no image reference changed",
 "renderCheck": "none",
 "envs": [{"cluster": "hangar-prod", "env": "staging", "kind": "config", "protected": true,
           "images": {"base": [], "head": []}, "files": ["hangar-prod/staging/values.yaml"]}]}
```

`protected` is filled by `protection.sh` for itsm (section 8). Not knowing counts as protected.

### 5.3 Computed once per head commit, then shared {#classifier-sharing}

Tekton has no data sharing across PipelineRuns, and every gate is its own PipelineRun. Three options:

| Option | Load | Agreement between gates | Notes |
|---|---|---|---|
| A. Each gate computes it in a StepAction | about 11 × (2 + 2 per file) GitHub reads per head | everything is deterministic except rollback eligibility: a release turning healthy while the gates run can make two gates disagree | no new service dependency |
| **B. glidepath-api computes it, stores it, and serves it** (recommended) | one computation per head; the other gates read a stored answer | one answer, frozen per head SHA | the API already holds the gate ledger (W-8) and ref protection; readers outside a gate's run (promote, detect-bypass-merge, release-log-emit, Tower) need the same answer later |
| C. Store it on the release record | one computation | one answer | a hand PR has no release record, which is exactly the case this design is for |

**B in detail.** `POST /v1/apps/{app}/pulls/{n}/classification` with `head` (tier T0: it reads and stores, and changes
nothing in git or the cluster). The API computes once per `(repo, pr, head)` under singleflight, so the 11 gates that
start together cause one computation. It writes the result into a ConfigMap `change-kind-pr-<n>` in the app's `-cicd`
namespace, one key per `head[:12]`, **write-once**. A head's kind never changes afterwards, so rollback eligibility is
frozen at the first ask. When the PR has a release record, the same JSON is also copied onto it as `changeKind.<sha12>`.
The release-record sweeper removes these ConfigMaps once the PR has been closed for its retention window.
`GET` on the same path serves the stored answer to the later readers.

In each gate, the call is a step (`classify`, StepAction `classify-change`) **inside the gate's existing first Task**,
so it adds no pod: `extract-promoted-image` (sast, image-scan, sbom, api-compat, qa), `fetch` (clearance-gate,
policy-validation), `validate` (values) and `verify-change` (itsm). provenance runs two tasks in parallel, so it gets a
small first task, which is one extra pod. If the API cannot be reached, the step falls back to option A's local
computation and logs that it did. If both fail, the result is `image-release` (fail closed).

### 5.4 The render backstop {#render-backstop}

The file-level classifier can miss an image that only the render shows (step 8, and anything it does not understand).
clearance-gate already renders base and head. Its decide step gains one comparison: the set of container images
(containers, initContainers, ephemeralContainers) per environment, base against head. If they differ and the
classification is `config` or `no-op`, the check fails with "this PR changes images the classifier did not see:
<list>". This runs as a hard task even where clearance-gate itself is advisory (it sits next to the existing
`render-check` task), because it is a statement about classification, not about clearance. This is the right host
(Q4, decided); revisit if clearance-gate ever stops rendering base. It covers only `targets: [k8s-rollout]` apps,
the only ones with environments to render today.

## 6. The class × kind matrix {#matrix}

One table, rendered from the registry (`GV`) by a new helper `glidepath-catalog.applicability`. Class defaults apply.
An entry can override them with `kinds: { <kind>: run|advisory|n/a }`. `required: false`, per cluster or per app,
still composes on top: an advisory gate that "runs" runs its advisory copy.

| Gate | Class | image-release | rollback | config | no-op |
|---|---|---|---|---|---|
| sast | content | run (locked) | advisory | n/a: the image is unchanged and its source was gated when it was released | n/a |
| image-scan | content | run | advisory | n/a (Q5: new CVEs in running images belong to a scheduled re-scan) | n/a |
| sbom | content | run | advisory | n/a | n/a |
| api-compat | content | run (advisory by registry) | advisory | n/a | n/a |
| qa | content | run (advisory by registry) | advisory | n/a | n/a |
| provenance | integrity | run (locked): app commit and SLSA | run: block (ADR-0021) | **run, config variant** (section 7) | n/a |
| values | integrity | run | run | run if a values, release or base file changed, else n/a | n/a |
| policy-validation | integrity | run | run | run | n/a |
| agent-gates | integrity | run | run | run | run (it is about who opened the PR, and already runs on every PR) |
| clearance-gate | process | run | run | run | n/a ("nothing to register" today) |
| itsm | process | run | run | **run for a protected env, n/a otherwise** (section 8) | n/a |
| image-promotion | integrity | run (with `promotion.enabled`) | as today | n/a: nothing to promote | n/a |

`agent-identity` and `agent-scope` are the Clearance App's own checks (`GV:456-471`). They already run on every PR and
are out of scope here.

**Locks**, enforced at render time next to the existing refusals in `glidepath-catalog.guardrails`:

- sast and provenance must be `run` for `image-release`;
- provenance cannot be `n/a` for `rollback` or `config`;
- image-promotion must be `run` for `image-release`;
- no gate may be `n/a` for `image-release`;
- an unknown kind or value fails the render.

The rendered matrix is also published as a ConfigMap `release-guardrails` in `platform-catalog`, like
`release-signing-policy` (`GC/release-signing-policy.yaml`), so glidepath-api and Tower read the same table that the
Pipelines were rendered from.

### 6.1 How a gate Pipeline uses it {#pipeline-shape}

- The `classify` step returns `change-kind`, `applicability` (`run | advisory | n/a`, for this gate) and `reason`.
- The hard tasks get `when: applicability in [run]` and the `-advisory` copies get `when: applicability in [advisory]`.
  This replaces today's `rollback-eligible` `when`s (e.g. `GC/pipelines/sast-check.yaml:59,75`), because rollback is now
  a kind. The `rollback-eligible` result stays one release for old readers.
- With `n/a`, no other DAG task runs. Tasks skipped by a false `when` count as done in the API's verdict
  (`gateverdict.go:259-266`, `doneSkips`), so the run is green with no special case.
- This also fixes the #96 advisory problem: `extract-promoted-image`'s resolve step runs only when the gate applies, so
  an advisory gate can no longer go red on a config PR.

### 6.2 What "not applicable" looks like {#na-surface}

- **The check run is green.** PaC posts it, and PaC sets the title. Checked live on #96: every PaC check is titled
  `Success` or `Failed`, with PaC's own summary. Glidepath posts as the same GitHub App (promote already PATCHes its own
  `image-promotion-` check, `promote.yaml:240`), so it *can* retitle the run to
  `Not applicable: config, <reason>`. But PaC updates the check run again when the PipelineRun finishes, after the
  `finally` that would do the retitling. Two ways (Q2, decided: (a) for v1, and prototype (b)):
  (a) v1 keeps PaC's title. The n/a run's only DAG task is named `not-applicable`, so PaC's task table in the check
  says it, and the comment and every reader say `n/a`.
  (b) A small post-completion updater retitles the check after PaC's last update (the tekton-results relay already sees
  completions). This needs a prototype: does PaC write the check again after completion?
- **PR comment.** `comment-pr-check-result` gains `change-kind`, `applicability` and `reason` params. The n/a gates
  share one "Change classification" comment, upserted by a marker (Q3, decided), instead of one comment each. It
  names the kind and the reason once, then lists the n/a gates: "**Not applicable** (config): sast, image-scan, sbom,
  api-compat, qa. This PR changes no image; hangar-prod/staging changes `rollout.replicas`." A gate that runs keeps
  its own comment.
- **Ledger.** The verdict `n/a` goes in beside `success` and `failure`. The `gate-verdict` route does **not** take the
  run's word for it. It reads the `classify` TaskRun's results and checks them against its own stored classification
  and the `release-guardrails` matrix. If they agree, the route records `n/a`. If not, it records `failure` with
  "classification mismatch". Without this check, a run could claim n/a for a gate that applies. The `kubectl` ledger
  writer (`comment-pr-check-result.yaml:527-545`) applies the same rule through a `GET` to the API.
- **Fan-in.** `n/a` counts as satisfied. The skip "a branch that is not `release-*`"
  (`comment-pr-check-result.yaml:475`) becomes "a kind that is not `image-release` or `rollback`". A config change
  promotes nothing.

### 6.3 Readers that must show n/a, never a pass {#readers}

Each reader gets the PR head's classification from the API (`GET`) and the matrix from `release-guardrails`. It shows
a green check for a gate that is n/a for that kind as `n/a`:

| Reader | Today | Change |
|---|---|---|
| `promote` PROM-03 (`promote.yaml:137-166`) | `gate=success` | `gate=n/a` in its log and in the promotion attestation's `gates` snapshot (e.g. `values=n/a` on an image release that changes only `release.yaml`) |
| `detect-bypass-merge` (`detect-bypass-merge.yaml:117-132`) | every required gate must be `success`. Read from the code: a merged hand config PR today reads every release-only gate as `missing` and reports **BYPASS DETECTED** (not checked live) | a gate that is n/a for the merged head's kind is skipped and listed as `n/a`. A **missing** check for a gate that applies is still a bypass |
| `release-log-emit` (`release-log-emit.yaml:157-181`) | conclusion per gate, `bypass` from the required ones | conclusion `n/a`, plus a `changeKind` field on the log record; `n/a` never sets `bypass` |
| `wait-for-release-guardrails` | waits for `success` | n/a is satisfied (no shape-B gate uses it today) |
| `open-release-pr` gate table | "real, advisory" etc. | one column per kind, filled for the record's kind |
| Tower Release Record (`ReleaseRecordDetail.tsx:677-697`) and `BE/pullRequests.ts:349` | "N/M passed" | "N passed · K n/a of M". A grey `n/a` chip with the reason, never counted as passed |

## 7. provenance on a config change {#provenance-config}

There is no new image, so the SLSA half is `n/a`. The commit half judges the **gitops PR itself**, under the same
admin-owned policy (`releaseSigning`, ADR-0027 decision 3). New task `verify-gitops-change`:

1. **gitsign**: every commit on the PR is gitsign-signed by a signer allowed for the app. Pass, with path `gitsign`.
2. **reviewed merge**, only where the app's policy enables the GitHub-merge path. A merge cannot be checked before it
   happens, so this half has two steps:
   - At PR time, in the gate: the final head has at least `requiredApprovals` approvals from `allowedMergers` logins other
     than the author, the same rule as `verify-commit-signature.yaml:416-430`. In `strict` mode every commit must also be
     gitsign-signed.
   - After the merge, in `bypass-merge-check`: the merge commit is signed with GitHub's pinned web-flow key and
     `merged_by` is in `allowedMergers`. If not, it is announced as a bypass. That is today's rule for any merge past a
     red gate (GATE-04), and the sync-time Clearance gate still applies.
3. Neither path holds: the check fails and names the commits and the policy.

**The proposer is recorded.** The PR author's login, and its kind from the agent gates' verdict (`POST /v1/provenance`,
the same call clearance-gate's fetch makes, `clearance-gate.md:37-46`). A PR opened by the config-change action
(section 9) records the action's `On-Behalf-Of` initiator instead of the App's login. The proposer goes into the task's
results, into the `<!-- glidepath:signature {...} -->` line with `path: gitops-pr`, and onto the release record when
there is one.

**Consequence accepted (Q6, decided).** On a cluster whose policy leaves the GitHub-merge path off, a config PR written
in GitHub's web editor (web-flow signed, not gitsign) fails provenance. That is the rule as written for image releases
too, but config PRs are much more often hand-written. The path stays off by default; an admin turns it on per app where
people edit in the web UI.

## 8. itsm on a config change {#itsm-config}

- A **protected** environment (from `protection.sh`, where unknown counts as protected) needs a change request, exactly
  as a release does. A prod config change needs a change request.
- An **unprotected** environment is `n/a`: "hangar-dev/dev is not a protected environment".
- Where the change request comes from: the release record (the config-change action creates one through `itsm_create`
  with `release-kind: config`), else the PR body's marker (`itsm-gate.yaml:98-106`). A hand-edited PR with neither gets
  today's "no change request linked" message, as the owner intended.
- **Hardening (also outside this design).** Today the marker is trusted as given: any approved change id in a PR body
  passes. The gate should also check the change's `correlation_id` or app/env against the PR's environment and refuse a
  change for a different release.

## 9. The config-change path {#config-change-action}

**glidepath-api `POST /v1/apps/{app}/environments/{env}/config-change`** (tier T2, "propose"). It has the same shape
as `promote` and `rollback` (`api/openapi.yaml:724-792`): `On-Behalf-Of`, `Idempotency-Key`, `dryRun`, and the open
PR returned if one already exists.

- **Body**: `patch` (the Config top-level fields) or `raw` (the whole file, for an environment on its own chart), and
  `summary[]`. The checks move from `BE/glidepathConfig.ts:160-170` into the API: only editable fields, never an image
  (the image belongs to promote).
- **What it does**: creates a PipelineRun from a `config-release` TriggerTemplate that runs `open-release-pr` with
  `release-kind: config`. One writer of release records stays one writer (the I-1 single-writer rule). It opens the PR
  through the platform's GitHub App, writes a release record (`kind: config`, the environment's current image, a new
  chain id) and a change request when a provider is set, and fills in the gate table for the `config` column. It also
  stamps a new `releaseTracking.releaseId` into the release file, so the relay's outcome facts land on this record and
  not on the last image release. Q7, checked 2026-11-24: airframe-application puts `hangar.io/release-id` (and the
  `hangar.io/release-tracked` label) on the Rollout's own metadata, never on its pod template
  (`charts/airframe-application/templates/workload/rollout.yaml:56-75` on airframe `e1cbd42`; the pod template at
  `:90-123` carries nothing release-specific but the image tag in `app.kubernetes.io/version`). open-release-pr writes
  only `release.image.*` and `releaseTracking.{cluster,appNamespace,releaseId}` (`GC/tasks/open-release-pr.yaml:854-865`
  on glidepath `25ad6ea`). So stamping a new id never restarts pods, and the action **always** stamps one: every config
  release gets its outcome facts under its own id. Open for CG-7: a change that rolls no pods (replicas only) produces
  no new revision, so the Rollouts notifications may report nothing for it, and the sweeper's stall alert ("merged,
  no rollout fact") would fire. CG-7 decides how such a record reaches a terminal state (for example, healthy from the
  first heartbeat fact under its id).
- **Tower**: the Values form's "Open config PR" and the flight-base and ConfigMap-files editors
  (`BE/glidepathConfig.ts:487-582`) call this route through the Backstage proxy instead of writing to GitHub
  themselves. That fits the standing rule that glidepath-api is the CI/CD interface.
- **Hand-edited PRs still work.** They classify the same way. Without a record or a marker they get "no change request
  linked" on a protected environment, and with no record the check runs alone decide, as today.

## 10. Migration {#migration}

Order matters: each step works with what the previous step left in place.

1. **glidepath-api first**: the classification route and store, `n/a` in `gate-verdict`, and the `config-change` route
   (dark until Tower calls it). An older catalog never calls the new routes.
2. **Catalog**: the `classify-change` StepAction, the registry `kinds` field and helper, the `release-guardrails`
   ConfigMap, the gate Pipelines (classify plus `when`), comment-pr's n/a wording, the fan-in keyed by kind, and the
   readers in section 6.3. Pipelines resolve from the cluster, so this applies at once to the **existing** triggers. That
   is safe: those triggers fire only on `release-*` branches, where release PRs classify as `image-release` and run
   unchanged. Hand PRs on `release-*` branches, like #96, get the right answer straight away.
3. **Templates**: the new CEL in every `OT/gitops-repo/pull-request-<gate>.yaml` (section 4), and the I-85 timeout rule
   (section 12.2), in the same template change.
4. **Rollout**: the template change reaches each app's onboarding ConfigMap on the app's next helm upgrade.
   `deliver-onboarding-files` then delivers it on a resync and opens an `onboarding-resync` PR on the gitops repo.
   A resync today needs a push to the app repo's `main` that touches `cicd.yaml` (`docs/admin/onboarding-mechanics.md:174-185`).
   Use the PR-based trigger instead (section 12.1, CG-10). Merge one resync PR per gitops repo.
   With `pipelinesAsCode.gitopsRepoProvenance: default_branch` a release PR opened before the resync is judged by the
   new files after `/retest`. Without it, close and re-promote (`onboarding-mechanics.md:187-194`).
5. **Tower and Backstage**: n/a display, then switch "Open config PR" to the API route.
6. **Ruleset, last**: once every gitops repo's resync has merged, re-run `hack/apply-guardrail-ruleset.sh -f <cluster
   values>`. Before that, a repo with the old files would have required checks that its config PRs never get.
   Implications:
   - non-deployable PRs (resync, Release Record, docs) report every required check as `n/a`, so they merge on an
     enforced ruleset (Q1);
   - the Crossplane App's direct commits still need the bypass actor (`github-ruleset.md:58-61`);
   - on GitHub Free the ruleset is still not enforced, so `detect-bypass-merge` (now n/a-aware) stays the only control.

## 11. A single aggregate check (optional, additive) {#aggregate-check}

`Glidepath / release-gates`: posted by the last gate's `finally`, the way `promote` posts `image-promotion-`. It shows
the kind and one line per gate (`run ✓`, `advisory ✗`, `n/a`), and it would give Tower and reviewers one place to look.
It must not replace a per-gate check, and it should not be required at first: it would be a second source of truth for
the same verdicts. Worth building only if Tower wants it.

## 12. Related findings {#related}

### 12.1 I-84 follow-on: resync without pushing to app-repo main {#resync-trigger}

The I-84 rollout triggered each resync by pushing a `# resync` line straight to the app repo's `main`, as
`onboarding-mechanics.md:181` tells admins to do. Clearance counts a direct push as unvouched, which may raise that
app's next release to tier 3. Proposal: **glidepath-api `POST /v1/apps/{app}/onboarding/resync`** (T2, platform-admin
verb), with a fleet form for after a platform upgrade:

- **(a) PR-based (the owner's ask).** The API opens a PR on the app repo that bumps one stamp line in `cicd.yaml`
  (`# glidepath-resync: <catalog version>`). A person merges it, the existing push trigger fires
  (`OT/app-repo/onboarding-resync.yaml:29`), and the commit is a reviewed merge that Clearance can vouch for.
- **(b) Direct.** The API creates the `onboarding-resync` PipelineRun itself through a TriggerTemplate, as promote does.
  This makes no commit at all, but gives the API one more privileged Pipeline to start.

Recommend (a) for its audit trail, with (b) noted. Update `onboarding-mechanics.md:174-185` either way.

### 12.2 I-85: finally counts against `tasks`, applied to every template {#timeouts}

Tekton counts `finally` against `timeouts.tasks` (`docs/admin/release-guardrails.md:124-132`, found 2026-10-29). The
rule: `tasks` = what the check needs + `finally` + headroom, and `pipeline` = `tasks + finally`. An audit of every
onboarding template on `e5d27d8` finds the gitops gates at 12m to 19m `tasks`, which fit. These four leave about one
minute for the check:

| Template | tasks / finally / pipeline |
|---|---|
| `OT/app-repo/pull-request-cicd-validate.yaml` | 5m / 4m / 10m (I-85: went red when comment-pr took 3m21s) |
| `OT/app-repo/pull-request-agent-definitions.yaml` | 5m / 4m / 10m |
| `OT/app-repo/pull-request-agent-gates.yaml` | 5m / 4m / 10m |
| `OT/gitops-repo/pull-request-agent-gates.yaml` | 5m / 4m / 10m |

A builder is already fixing I-85. This design adds a catalog CI test that parses every template with a `finally` and
fails unless `tasks >= finally + <declared check budget>` and `pipeline >= tasks + finally`. Running every gate on
every PR (Q1) adds `finally` load on hangar-dev, which is exactly when a slow comment step pushes a green run into a
timeout. The n/a path is light (one step and the comment), but about 11 runs × 2 pods per config or no-op PR is real,
and the gates queue under `pipelinesAsCode.concurrencyLimit` (`docs/admin/pipeline-performance.md`).

### 12.3 Found while reading (not part of this change) {#found}

- **provenance trusts trailers to choose which app commit to verify** (`verify-commit-signature.yaml:153-175`). Not
  checked here: whether the SLSA half ties the image's build source commit to that `X-App-Commit`. If it does not, an
  image-release PR could name a well-signed but unrelated app commit. Worth a look under the same "never from PR text"
  rule.
- **The image gates read only the first changed manifest** (`resolve-promoted-image.yaml:118-120`). A PR that changes
  the image in two environments gates one of them. The classifier lists every image change. Decided (Q8): in v1 the
  content gates refuse a PR that changes more than one distinct image, and name the images.

## 13. Decided 2026-11-24 {#questions}

The owner accepted every recommendation. The sections above now read as decided.

- **Q1 · Trigger.** Every PR to `main`, not only PRs that change deployable files. A non-deployable PR classifies as
  `no-op` and every gate but `agent-gates` is `n/a`. This was needed before the ruleset is enforced (section 4).
- **Q2 · n/a check title.** v1 keeps PaC's `Success` title with a `not-applicable` task. Prototype a
  post-completion retitler (section 6.2).
- **Q3 · n/a comments.** One shared "Change classification" comment, upserted by a marker, not one per gate (section 6.2).
- **Q4 · Render backstop.** It lives in clearance-gate's render, as a hard task even where that gate is advisory.
  Revisit if clearance-gate ever stops rendering base (section 5.4).
- **Q5 · image-scan on a config change.** `n/a`. A scheduled re-scan of running images is the home for new CVEs.
- **Q6 · Hand config PRs where the GitHub-merge path is off.** Accept that they fail provenance. Turn the path on per
  app where people edit in the web UI (section 7).
- **Q7 · `releaseId` stamp.** Check where the chart writes `hangar.io/release-id` before building CG-7; if it is on the
  pod template, stamp only when the change already rolls pods. Checked 2026-11-24: it is on the Rollout's metadata, so
  the config-change action always stamps a new id (section 9).
- **Q8 · Several images in one PR.** Refuse more than one distinct image per PR in v1 (section 12.3).
- **Q9 · Cloud release pins.** Not in v1. Pins keep today's gates, and the classifier learns pins later.
- **Q10 · Agent PRs.** Intended as written: an agent's config PR is `config` (agent-scope bounds its paths; provenance
  needs a person's approval under reviewed merge), and an agent's image edit is `image-release` and fails provenance.

## 14. Risks {#risks}

- **Partial renders.** The file-level classifier can be wrong about images that only a render shows. The backstop
  catches it for k8s-rollout apps. Elsewhere, doubt means `image-release`.
- **A PR touching several environments of different kinds** takes the highest kind. A prod config change riding along
  with a staging image release gets the full image gate set, plus itsm for the protected environment. That is stricter,
  never weaker.
- **Classification as a single point.** If glidepath-api is down, gates compute locally, so there is no outage. A wrong
  stored classification would be wrong everywhere at once. It is write-once per head and checked by the ledger route,
  and the fixtures in CG-9 guard the code.
- **Load on hangar-dev.** More PipelineRuns per config PR (section 12.2).
- **Old `.tekton` files** keep the branch rule until each repo's resync merges. Mixed fleets are expected during step 4.

## Work packages {#packages}

### CG-1 · Classifier and its store in glidepath-api
<!-- pkg status=proposal strip=I-84 -->

**Goal.** One classification per PR head: computed from the diff, stored write-once, served to every gate and reader.

**Scope.** `POST`/`GET /v1/apps/{app}/pulls/{n}/classification`, the algorithm in section 5.2 (with the deployable-files
predicate of section 4 as the `no-op` line), singleflight, the
`change-kind-pr-<n>` ConfigMap, the copy onto the release record, the sweeper. Rollback eligibility moves here, with
its logic unchanged. OpenAPI, contract and `docs/admin/api.md`.

**Done when.** The fixtures for every kind pass (CG-9). Two concurrent asks for one head compute once. A second ask after
a release turns healthy returns the frozen answer.

### CG-2 · Registry `kinds`, the matrix helper, the `release-guardrails` ConfigMap
<!-- pkg status=proposal depends=CG-1 -->

**Goal.** The class × kind matrix of section 6 as data, with locks enforced at render time.

**Scope.** `GV` `kinds` per entry, `glidepath-catalog.applicability`, the refusals, the ConfigMap, and
`gate_required_test.sh` cases. `docs/admin/release-guardrails.md` gains a "Change kinds" section.

### CG-3 · Gate Pipelines: classify, `when`, n/a
<!-- pkg status=proposal depends=CG-1,CG-2 -->

**Goal.** Each gate runs, advises or is n/a from the classification.

**Scope.** The `classify-change` StepAction in each gate's first task (and a small first task for provenance), the
`when`s that replace `rollback-eligible`, comment-pr's n/a params and the shared "Change classification" comment
(Q3), the `not-applicable` task name, and the content gates' refusal of more than one distinct image per PR (Q8).
A prototype of the post-completion retitler (Q2) rides along, not wired in.

### CG-4 · Ledger, fan-in and readers show n/a
<!-- pkg status=proposal depends=CG-3 -->

**Scope.** `gate-verdict` n/a with the classification check, the kubectl writer, the fan-in keyed by kind
(`comment-pr-check-result.yaml:475`), PROM-03 and the attestation snapshot, `detect-bypass-merge`, `release-log-emit`,
`wait-for-release-guardrails`, and the gate table. `docs/admin/registries.md` fan-in section.

### CG-5 · provenance config variant
<!-- pkg status=proposal depends=CG-3 -->

**Scope.** `verify-gitops-change` (gitsign, or approvals before the merge), the post-merge check in
`bypass-merge-check`, the proposer in results, the signature line and the record. `docs/admin/commit-signing.md`.

### CG-6 · itsm config variant
<!-- pkg status=proposal depends=CG-3 -->

**Scope.** Protected → required, unprotected → n/a, through `protection.sh`; `release-kind: config` in `itsm_create`;
the marker correlation check. `docs/admin/change-management.md`.

### CG-7 · Propose config change (glidepath-api, open-release-pr, Tower)
<!-- pkg status=proposal depends=CG-2,CG-6 -->

**Scope.** The `config-change` route, the `config-release` TriggerTemplate, `open-release-pr` `release-kind: config`,
Tower's Values, flight-base and ConfigMap editors moved off `BE/glidepathConfig.ts`, and n/a display in Tower and
`BE/pullRequests.ts`.

### CG-8 · Triggers and rollout
<!-- pkg status=proposal depends=CG-3,CG-4 strip=I-84 -->

**Scope.** The every-PR-to-`main` CEL in every gitops gate template (with the I-85 timeouts), the resync of every gitops repo through
CG-10, then the ruleset re-run. The order in section 10.

### CG-9 · Tests
<!-- pkg status=proposal -->

**Scope.**

- CEL: `hack/ci/build-exemption-cel` covers every gate template, asserts they share one expression, and asserts that
  every PR to `main` fires every gate, including `.tekton/`-only, `releases/`-only and docs-only PRs (which the
  classifier fixtures then show as `no-op`).
- Classifier fixtures, one per kind and edge:
  - `release.image.tag` bumped (image-release);
  - a hand image edit (image-release);
  - an eligible return (rollback) and an ineligible one (image-release);
  - replicas changed (config);
  - a raw manifest `image:` changed (image-release);
  - a kustomization `images:` changed (image-release);
  - `base.yaml` image changed (image-release for every environment on that cluster);
  - comment-only and key-reorder changes (no-op);
  - `.tekton/`-only, `releases/`-only and docs-only PRs (no-op);
  - a removed or renamed manifest (config);
  - unparseable YAML (image-release);
  - more than 300 files (image-release);
  - a chart pin bump (config with a render check);
  - a mixed PR (image-release);
  - two environments of different kinds.
- Chart tests: matrix locks, and n/a in `promotion_fan_in_test.sh`, `promote_test.sh` and `detect_bypass_merge_test.sh`.
- Go: `gateverdict` n/a when the run and the store agree, and when they do not.
- The I-85 template timeout lint.
- Live, on one test gitops repo, one PR per kind:
  - a #96-style replicas change, from a branch not named `release-*` and from a `release-*` branch;
  - a Tower promote;
  - a hand image edit (provenance and qa red, as intended);
  - a Tower rollback;
  - a comment-only edit;
  - a mixed PR;
  - a config-change action PR to a protected environment, with its change request.

### CG-10 · Resync through a PR, not a push to main
<!-- pkg status=proposal strip=I-84 -->

**Scope.** `POST /v1/apps/{app}/onboarding/resync` and its fleet form (option (a) in section 12.1), and the
`onboarding-mechanics.md` update.
