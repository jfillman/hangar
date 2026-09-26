# Release-file split (D9, AF-5)

Status: **designed; offline proof done; live ArgoCD proof pending** (needs a scratch app on kiac-dev).
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
11,505 bytes, flight-api 11,310; Flight kind-prod staging: boarding-api 25,370, flight-api 18,157 rendered
bytes; the fourth needed the timestamp quoting above). The test asserts non-zero output and real release keys
were moved (`rollout` and `releaseTracking` present in the release files).

Also proven: an ApplicationSet git files generator excludes files by glob (U7: nine files, three excluded,
six generated), so `*.release.yaml` cannot become an environment.

## Still to prove (needs kiac-dev, a cluster write)
1. A scratch app with the new ApplicationSet: three `valueFiles`, one missing, syncs and renders identically to today.
2. Changing only the release file (an image tag) rolls the app and touches no human file.
3. The exclude with the real `*.release.yaml` name (U7 used a stand-in glob).
4. Glidepath's deploy stage writing only the release file, with strings preserved.
Test through a copy of the ApplicationSet under another name, not by editing the live one (ArgoCD self-heal).

## Revisions after review (2026-09-26)

Two questions were raised on this design. Both change it; the layout above still says `platform/` and
`rollout.image` until the work is scheduled.

### 1. The directory name: rename `platform/` to `airframe/`
In the Hangar brand system "the platform" is Hangar itself. `platform/` in an app repo is a leftover from
`platform-cicd` (the deprecated predecessor of Glidepath; `cicd.yaml` still says `apiVersion: platform/v1`). The
files in it are exactly the values for the Airframe chart, so the directory should be named for the product
that owns the contract, as the other pieces already are (`.tekton/` for Pipelines-as-Code, gitops repos for Flight).

- **Recommended:** `airframe/` (`airframe/base.yaml`, `airframe/envs/<env>.yaml`, `airframe/envs/<env>.release.yaml`,
  `airframe/pr-env.yaml`). Runner-up: `hangar/` (umbrella name, matches the `hangar.io` label domain, but says
  less about what is inside). Rejected: `ground/` (base and release files are not Ground-specific ideas and the
  PR-environment file lives there too).
- **Cost, measured by grep:** the `platform/envs` path is read by the lower-envs ApplicationSet (apron and
  gitops-cluster-dev, plus their `applicationset.yaml` and `Chart.yaml`), about eight Glidepath files
  (`deploy-manifests`, `deliver-onboarding-files`, `open-release-pr`, `deploy` pipeline, `run-testworkflow`,
  `ephemeral-envs`, `deploy-rbac`, `appproject`, the PR-preview notify job, the PaC config-only-push exemption),
  Tower's `GlidepathTab` and `PromoteDialog`, and every app repo and scaffold.
- **Migration shape:** do it inside the split migration, since every app repo is touched anyway. The files
  generator can list both paths for a window (`platform/envs/*.yaml` and `airframe/envs/*.yaml`; an `envName`
  must not appear in both), writers move first, then the old path is dropped.
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
2. Glidepath and the `ApplicationEnvironment` composition write `release.image` into a release file; Tower reads both.
3. ApplicationSet change (three `valueFiles`, `ignoreMissingValueFiles`, exclude), then split each app's files.
4. Directory rename with a dual-path window; then remove the old path and the `rollout.image` fallback.
