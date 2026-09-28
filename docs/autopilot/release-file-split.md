# Release-file split (D9, AF-5)

Status: **designed and proven live; step 1 and 2 of the migration shipped (2026-09-26); step 3's ApplicationSet mechanics proven live on a scratch copy, `deploy.releaseFile` landed in the schema, and both writer Tasks now read it (2026-09-27, opt-in, not yet merged/deployed or live-exercised); the ApplicationSet change on the live ApplicationSets, the file split, and the directory rename are not done.** See "Progress" at the end.
Written 2026-09-26.

## Problem
One values file per environment mixes two kinds of key with different authors:

| Owner | Keys | Written by |
|---|---|---|
| **human / agent** | everything else: `rollout.replicas`, ports, probes, `env`, `components`, `secrets`, ... | people, the planner, agents |
| **release** (machine) | `rollout.image.*`, `releaseTracking.*` | Glidepath's deploy stage and outcome relay |

An agent that edits the mixed file can overwrite a fresh image tag, or leave stale release data. Path-level
scope (Clearance's `deny_paths`) cannot protect a key inside a file it is allowed to edit. Split by file and it can.

## Layout
```
<app repo>/platform/
  base.yaml                     # optional, shared by every Ground env (human-owned)
  envs/<env>.yaml               # human-owned Ground env config            (generator matches this)
  envs/<env>.release.yaml       # machine-owned: rollout.image, releaseTracking  (generator excludes this)

gitops-<app>/<cluster>/<env>/
  values.yaml                   # human-owned Flight env config
  release.yaml                  # machine-owned
gitops-<app>/<cluster>/base.yaml   # optional, shared by that cluster's Flight envs
```
A release file contains **only** the release keys. Anything else in it is an error (validate rule, below).

## Layering (last wins; Helm deep-merges maps, replaces lists)
`base.yaml` < `<env>.yaml` < `<env>.release.yaml` < the ApplicationSet's own `valuesObject` (appName, cluster,
envName; already beats `valueFiles` in ArgoCD).

Ground ApplicationSet (`lower-envs-applicationset.yaml`) changes:
- generator: `files: [{path: platform/envs/*.yaml}, {path: platform/envs/*.release.yaml, exclude: true}]`
- `valueFiles`: `$appsrc/platform/base.yaml`, `$appsrc/platform/envs/{{.envName}}.yaml`, `$appsrc/platform/envs/{{.envName}}.release.yaml`
- `ignoreMissingValueFiles: true` so an app with no base or no release file yet still syncs.
- `{{.envName}}` must come from the file body (it does today) and must not include `.release`; the exclude guarantees the release file never becomes its own environment.

The Flight ApplicationSets get the same treatment over `values.yaml` and `release.yaml`.

## Who writes what
| Writer | Allowed to write | Enforced by |
|---|---|---|
| Glidepath deploy stage, outcome relay | `*.release.yaml` / `release.yaml` only | its own commit step; a validate rule rejects any other key there |
| Planner, agents, people | the human files, `base.yaml` | Clearance `deny_paths` gains `**/*.release.yaml`, `**/release.yaml` (baseline deny, cannot be removed) |
| `airframe validate` | reads all | rule `AF-OWNER-001`: a human file holding a release key, or a release file holding anything else, fails |

Writers must **preserve strings**. Round-tripping through a YAML library changes an unquoted
`flowStartTime: 2026-09-25T06:14:54.641Z` into a datetime and re-dumps it as `2026-09-25 06:14:54.641000+00:00`
(seen in the proof below). Glidepath must quote such values or write them textually.

## Migration (per app, one PR)
1. Split the existing file: move `rollout.image` and `releaseTracking` into the release file, leave the rest.
2. Land the ApplicationSet change first (with `ignoreMissingValueFiles`), then the file split. Order matters: the
   reverse briefly renders a workload with no image, which the AF-10a chart guard now turns into "no workload"
   (a deploy would look like a delete, so do not do it in the other order).
3. Update Glidepath to write the release file. Until it does, it would keep committing `rollout.image` into the
   human file and the release file would silently win on top; the validate rule flags that.
4. Turn on the `deny_paths` entries.

## Proof so far (offline, 2026-09-26)
Split the four real live files by the two release keys, then compared `helm template` of the single file with
`helm template -f human -f release`. Rendered output is **byte-identical for all four** (Ground: boarding-api
11,505 bytes, flight-api 11,310; Flight prod-cluster staging: boarding-api 25,370, flight-api 18,157 rendered
bytes; the fourth needed the timestamp quoting above). The test asserts non-zero output and real release keys
were moved (`rollout` and `releaseTracking` present in the release files).

Also proven: an ApplicationSet git files generator excludes files by glob (U7: nine files, three excluded,
six generated), so `*.release.yaml` cannot become an environment.

## Proven live (2026-09-27)
A standalone `ApplicationSet` (`baggage-api-scratch-releasefile-test`, applied directly to `kiac-dev`'s
`argocd-apps` namespace, not tracked by any Application - same "copy under another name" pattern as testing a
shared composition, never touching the live `lower-envs-applicationset.yaml`) proved items 1-3 of what this
section used to list as "still to prove":
1. **Three `valueFiles`, one missing, syncs and renders identically.** `platform/scratch/base.yaml` never
   existed at all; `ignoreMissingValueFiles: true` still synced cleanly against `platform/scratch/envs/
   scratchtest.yaml` + `scratchtest.release.yaml`. Rendered `Rollout`/`RolloutWatch` matched a local `helm
   template` of the same two files exactly.
2. **Changing only the release file rolls the app and touches no human file.** Bumped `release.image.tag` alone
   (git commit touched exactly one file); ArgoCD's git generator picked it up within its normal poll window and
   the live `Rollout`'s image updated - `replicas` and `ports` (the human file's only other fields) were
   byte-identical before and after.
3. **The exclude works with the real `*.release.yaml` name**, not U7's stand-in glob: the generator produced
   exactly one Application (from `scratchtest.yaml`), never a second bogus one from `scratchtest.release.yaml`.

Health stayed `Progressing` (`ImagePullBackOff`) throughout, because this scratch namespace had no
`registry-credentials` Secret - copying one from a live namespace was refused by the auto-mode classifier
(reasonable: cross-namespace Secret duplication is exactly the kind of action that should ask a human first) and
not worked around. Irrelevant to what this proof was checking (`Synced` status and the rendered manifest content,
not whether the image can actually be pulled) - not re-attempted.

Scratch `ApplicationSet`, its generated Application, and the `app-baggage-api-scratch` namespace were all deleted
after the proof; the `scratch/release-file-split-proof` branch stays on `baggage-api` (never merged, never
opens a PR) as a record, per this doc's own migration-order caution.

**Item 4 (Glidepath's deploy stage writing only the release file) is not a cluster-proof item** - it needs real
code in `deploy-manifests`/`open-release-pr` to read `deploy.releaseFile` and write through it, which is
"Migration" step 3 below, not built yet. Test through a copy of the ApplicationSet under another name, not by
editing the live one (ArgoCD self-heal) - as done here.

## Revisions after review (2026-09-26)

Two questions were raised on this design. Both change it; the layout above still says `platform/` and
`rollout.image` until the work is scheduled.

### 1. Who owns the folder, and therefore its name: Airframe, so `airframe/`
The test is compartmentalization: each product must be installable without the others. Applied to the files:

| File | What it is | Owner | Why |
|---|---|---|---|
| `airframe/base.yaml`, `airframe/envs/<env>.yaml`, `airframe/pr-env.yaml` | what to run and how: scaling, ports, env vars, components, secrets | **Airframe** | Airframe defines the schema, the validator, the chart that consumes it and the Tower Config tab that edits it. Glidepath standalone has no use for it. |
| the **release file** (`release.image`, `releaseTracking`) | the record of what was released | **content: Glidepath** (it is Glidepath's output); **format: Airframe** (the chart consumes it) | The two products meet here, so this is a contract, not a shared folder. |
| `cicd.yaml`, `.tekton/` | pipeline definition and its generated files | **Glidepath** (and Pipelines-as-Code) | Not touched by this rename. |

**Today the boundary is broken:** Glidepath hardcodes `platform/envs/<env>.yaml` in `deploy-manifests` (the
`yq` write into an Airframe-shaped file) and writes `rollout.image` into the gitops repo's `values.yaml` in
`open-release-pr`. A standalone Glidepath would write an Airframe values file that nothing reads.

**Design:** the folder belongs to Airframe and is named for it. Glidepath is a *writer* of the release file, and
where it writes is configuration, not code: a new `cicd.yaml` field `deploy.releaseFile`, a path template such as
`airframe/envs/{env}.release.yaml`. Its schema default (no Airframe present) is a Glidepath-owned location
(`glidepath/releases/{env}.yaml`). The Airframe scaffolds that create `cicd.yaml` set it to the Airframe path.
So Glidepath alone works and writes a plain record; Airframe alone works (a person or any other CI writes the
release file); together they meet through one documented file shape. Airframe's ApplicationSet layers whatever
`airframe/envs/<env>.release.yaml` it finds. `airframe/pr-env.yaml` moves with the rest: it is Airframe values
for PR environments, which Glidepath's ephemeral-env ApplicationSet merely references.

- **Name:** `airframe/`. Runner-up `hangar/` (umbrella name, says less about the contents). Rejected: `ground/`.
- **Cost, measured by grep:** the `platform/envs` path is read by the lower-envs ApplicationSet (apron and
  gitops-cluster-dev, plus their `applicationset.yaml` and `Chart.yaml`), about ten Glidepath files
  (`deploy-manifests`, `deliver-onboarding-files`, `open-release-pr`, `deploy` pipeline, `run-testworkflow`,
  `ephemeral-envs`, `deploy-rbac`, `appproject`, the PR-preview notify job, the PaC config-only-push exemption),
  Tower's `GlidepathTab` and `PromoteDialog`, and every app repo and scaffold. Making the Glidepath side
  configurable (`deploy.releaseFile`) is what removes most of the Glidepath hardcoding for good.
- **Migration shape:** inside the split migration, since every app repo is touched anyway. The files generator can
  list both paths for a window (`platform/envs/*.yaml` and `airframe/envs/*.yaml`; an `envName` must not appear
  in both); writers move first, then the old path is dropped.
- **Not part of this rename:** `cicd.yaml` and its `platform/v1` apiVersion (Glidepath's own schema, baked into
  the toolbox image). Worth a separate decision.

### 2. Split the image out of `rollout`: a top-level `release:` object
The ArgoCD/Helm precedence approach works and is proven (Helm deep-merges maps; later `valueFiles` win; the
files here never conflict on a key). The reasons to go further are not about precedence:

1. **The image is not a rollout setting.** It is the release artifact. The chart already uses `rollout.image` as the
   fallback image for `jobs:` and `cronJobs:` (`_helpers.tpl`), so a Job's image is configured through the
   Rollout's object. Naming it `release.image` says what it is.
2. **Ownership becomes a fact about a top-level key.** With disjoint top-level keys (`release` and
   `releaseTracking` versus everything else) `x-hangar-owner: release` sits on whole objects, and the validate
   rule is one line: a human file may not contain `release`/`releaseTracking`, a release file may contain
   nothing else. Today the rule has to say "`rollout.image` but not the rest of `rollout`", which is exactly the
   nested-key ownership that path-level scope cannot express.
3. **Merge hazards disappear.** Lists replace wholesale in Helm, and any tool that treats `rollout` as one object
   (a planner merge-patch, the Config tab writing `rollout`, `yq` replacing it) can drop or resurrect an image
   if both authors write under `rollout`. Disjoint keys cannot collide.
4. **`rollout: null` stops being a trick.** Today "no workload" and "no image yet" both go through `rollout`.

- **Cost, measured by grep:** the chart (`_helpers.tpl`, `rollout.yaml`, `values.yaml`, README), the
  `ApplicationEnvironment` composition (three templates), four Glidepath tasks (`extract-promoted-image`,
  `open-release-pr`, `deploy-manifests`, `verify-image-provenance`) plus `ephemeral-envs`, and Tower/Backstage
  (`GlidepathTab`, `GlidepathSummaryPanel`, three backend config readers), plus every existing env file.
- **Compatibility:** the chart reads `release.image` first and falls back to `rollout.image` for a deprecation
  window, so this is a non-breaking chart release. `airframe validate` warns on `rollout.image` in a human file,
  then errors once the writers have moved.
- **Keep `releaseTracking` as it is** (already top-level and machine-owned; Tower's Release Record reads it).
  Folding it under `release.tracking` is possible later but not needed.

### Order of work (each step ships on its own, none breaks a live app)
1. Chart: accept `release.image` (fallback to `rollout.image`); guard and helpers read the new key first.
2. Glidepath and the `ApplicationEnvironment` composition write `release.image` (Glidepath to the path named by the new `deploy.releaseFile`); Tower reads both.
3. ApplicationSet change (three `valueFiles`, `ignoreMissingValueFiles`, exclude), then split each app's files.
4. Directory rename with a dual-path window; then remove the old path and the `rollout.image` fallback.

## Progress (2026-09-26)
| Step | State |
|---|---|
| 1. Chart accepts `release.image`, falls back to `rollout.image` | **Shipped** in Airframe v0.3.92, pinned on the dev and prod clusters. All 7 live env files render byte-identically before and after. The values schema has a strict `release` object; `airframe-validate` warns on `rollout.image`, `release` and `releaseTracking` in a human file (AF-OWNER-001). |
| 2. Writers write `release.image`; readers read both | **Shipped** in Glidepath (`deploy-manifests`, `open-release-pr`, `extract-promoted-image`, `verify-image-provenance`, `ephemeral-envs`). Live-verified on `baggage-api`: the Ground deploy wrote `release.image`, the rollout followed it; the Flight release PR carries `release.image`, and the `image-scan`, `sbom` and `provenance` (image-verification step) gates read it. A writer also drops a bootstrap `rollout: null`, because with a real image the chart needs its rollout defaults. Tower needs no change: it is whitelist-based, so `release` is already outside what it reads or writes. The `ApplicationEnvironment` composition still seeds Flight files with `rollout: null`; that is now unnecessary (the guard covers it) but is left alone because that file was once wiped by a composition change. |
| 3. ApplicationSet with three `valueFiles`, then split each app's files | **Mechanics proven live 2026-09-27** on a scratch copy (see "Proven live" above). `deploy.releaseFile` landed in `cicd.schema.json` 2026-09-27 (`jfillman/glidepath` `a246430`), schema-only: an optional string, one `{env}` placeholder required, default `glidepath/releases/{env}.yaml`. Live-verified: the rebuilt+pushed `platform-cicd-toolbox:2026-09-27-release-file-schema` (multi-arch, schema baked in) is synced on `kiac-dev`'s `validate-cicd-config` Task; a real `cicd.yaml` accepts a conforming value and rejects one missing `{env}` (checked with the same `yajsv`-against-`cicd.schema.json` mechanism the live Task uses, not just an offline `helm template`). **Both writer Tasks now read `deploy.releaseFile` (2026-09-27, not yet merged/deployed):** `deploy-manifests.yaml` reads it off the app repo's own `cicd.yaml` (already clones that repo); when unset it falls all the way back to writing `release.image` into `platform/envs/<env>.yaml` exactly as before - deliberately, since no live app's `cicd.yaml` sets the field yet and the lower-envs ApplicationSet still only reads that one file. `open-release-pr.yaml` reads it off the already-forwarded `config-json` param (no second clone); when unset it keeps writing `release.image`+`releaseTracking` into `<cluster>/<env>/values.yaml`; when set it writes both into a sibling `<cluster>/<env>/release.yaml` (fixed name, not `{env}`-templated - that path segment is already cluster+env) and leaves `values.yaml` untouched. Both branches offline-tested against real `yq`/`jq` (fixture files, not just `helm template`); `helm template` + extracting the rendered `.spec.steps[].script` and `bash -n`-checking it, matching this project's own verification convention. **Not yet live-verified**: no cicd.yaml has `deploy.releaseFile` set, so the opt-in branch has never run inside a real PipelineRun. Still to build: the 3-`valueFiles` change on `lower-envs-applicationset.yaml` and the Flight ApplicationSets, then each live app's file split (which is what will actually set `deploy.releaseFile` and exercise this branch for real). |
| 4. Rename `platform/` to `airframe/` with a dual-path window | Not done. |

**Finding:** an unsigned commit fails the `provenance` gate on an upper-environment release (`baggage-api`'s commits made by Claude Code carry no gitsign signature). That is decision D1 (agent commits signed through a self-hosted Fulcio) showing up early; until it is built, a release of an app whose latest commit came from an agent needs a signed commit from a person.

## First real runs (2026-09-27/28)
Two new apps (`gate-api`, `checkin-api`) were taken from nothing to a Flight release with `deploy.releaseFile` set by default. The opt-in branch now runs for real, and the end-to-end path found three gaps the per-step checks had missed, all fixed and in Glidepath's known gaps:

- **#18** `extract-promoted-image` and `verify-image-provenance` only diffed `*/values.yaml`, so `sast`, `image-scan`, `sbom` and `provenance` failed on every `release.yaml`-only release PR. Fixed: prefer `*/release.yaml`, fall back to `*/values.yaml` (glidepath `85a1c07`).
- **#19** The `values` gate only triggered on `values.yaml`, so `image-promotion` waited forever for it. Fixed: it also triggers on `release.yaml` and passes with a note (glidepath `effceac`); existing gitops repos pick it up at their next onboarding resync.
- **#22** The `tenant-identity` ApplicationSet only read `values.yaml`, so `airframe-identity` never saw `releaseTracking` and never rendered `platform-outcome-hook`; release syncs hung at PreSync. Fixed: it reads `release.yaml` too, in the prod cluster's repo and the Apron template.

The same runs also fixed the long-parked `relayHostAliasIP` bug (Glidepath known-gaps #12): the cluster registry now carries a per-cluster address. Verified live on `checkin-api` staging, 2026-09-28: PreSync and PostSync hooks both completed first time and reported back to dev.
