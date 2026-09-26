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
