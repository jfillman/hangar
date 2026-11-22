# W-43: the gated tenant ApplicationSet, hangar-dev rehearsal plan

Written 2026-11-21. Strip W-43; the owner chose option (3) on Y-36: a second ApplicationSet only for gated environments.
Recorded on the Strip Board (strip Y-36, owner note "go with option 3", done 2026-11-22T00:10Z) and in the Y-36 row of
`specs/clearance-autopilot/spec.md` ("owner chose option (3), 2026-11-22").
A plan only: nothing here was applied to any cluster, and no gitops repo was changed. The build is apron PR
`feat/w43-clearance-gate` (apron#256, reworked) and airframe#151.

Read at: apron `feat/w43-clearance-gate` `c1b83ce` (main `2c54708` merged in), clearance `v0.54.0` (the agent's `carrier`), airframe#151 `87882df`, gitops-hangar-dev `origin/main`
`09dcb2a`, gitops-hangar-prod `origin/main` `f01e628`. argocd-apps runs Argo CD **v3.5.0** (apron `versions.argocdChart`
10.3.2, appVersion v3.5.0) on both clusters; the source was also read at v3.4.5 and the behaviour below is the same there.

## 1. What is rehearsed

`clearance.gate.agent.gatedSet: true` makes the tenant-onboarding chart render two ApplicationSets from one template:

| | `tenant-onboarding` | `tenant-onboarding-gated` |
|---|---|---|
| generates | every `tenants/*/*/identity.yaml` without `clearanceGate: true` (selector `clearanceGate NotIn ["true"]`) | exactly those with it (`clearanceGate In ["true"]`) |
| `ignoreApplicationDifferences` | none (it still updates sources) | `jsonPointers: [/spec/source, /spec/sources]`, unconditional |
| `preservedFields.annotations` | none | `[clearance.hangar.io/switched]` |
| template annotation | none | `clearance.hangar.io/protect: "true"` |
| static plugin source (templatePatch) | as before (`tenantPlugin`; `gatedSet` needs it `false`) | never: the agent switches its Applications |
| source order | chart, then `ref: appsrc` (as today) | `ref: appsrc` first, then the chart: the agent's carrier (first git source) is the gitops repository |
| resources finalizer | yes (as today) | **no** (`preserveResourcesOnDeletion: true` and none in the template) |

`clearance.gate.agent.gatedSetHandover: true` opens the handover window: both sets render
`syncPolicy.applicationsSync: create-update`, so neither deletes an Application it stops generating.

Airframe's `ApplicationEnvironment` `spec.clearanceGate: true` (airframe#151) writes `clearanceGate: true` (a YAML boolean)
into `tenants/<app>/<env>/identity.yaml` and writes nothing when false. The git files generator parses it into the
parameters, and the post-selector flattens them with `fmt.Sprintf("%v")`, so the boolean is matched as the string
`"true"` (`applicationset/generators/generator_spec_processor.go` `flattenParameters`, v3.4.5 and v3.5.0, identical). The
selectors are In / NotIn on the same value, so every environment is in exactly one set, whatever the value is.

### Argo CD behaviour the handover rests on (v3.5.0 line numbers; v3.4.5 in brackets)

1. **A set deletes what it owns and no longer generates.** `deleteInCluster` lists the Applications whose controller owner
   reference names the set (field index `.metadata.controller`), and deletes each one not generated
   (`applicationset_controller.go:859` [872]). It runs only when the policy allows deletion (`:351` [355],
   `AllowDelete`: `sync` and `create-delete`). `preserveResourcesOnDeletion` is not consulted there: it only stops the
   controller *adding* the finalizer when the template has none (`applicationset/utils/utils.go:299`).
2. **tenant-onboarding's Applications carry `resources-finalizer.argocd.argoproj.io`** from the template itself, so a
   deletion by (1) cascades to the workload. (Also true when the whole ApplicationSet is deleted: the template's comment
   "deleting or replacing this ApplicationSet must not delete the Flight workloads" is not what the finalizer does. A
   finding, not changed by W-43: the render must stay byte-identical.)
3. **A set never modifies an Application another set controls.** `CreateOrUpdate` runs the mutate function, which ends with
   `controllerutil.SetControllerReference` (`:734` [775]); an Application whose controller reference names another
   ApplicationSet fails with `AlreadyOwnedError` before any patch (`applicationset/utils/createOrUpdate.go:100` mutate,
   `:127` patch). The error is reported as the set's `ErrorOccurred` condition and the reconcile is retried with backoff.
4. **An Application with no controller reference is adopted** by the set that generates it: same object (same uid), the
   set's labels, annotations (plus preserved ones) and finalizers replace the live ones (`:730`, `:732`).
5. **`applicationsSync` is honoured only with the policy override**, which defaults to on when no controller-wide
   `applicationsetcontroller.policy` is set (`applicationset/utils/policy.go` `DefaultPolicy`;
   `cmd/argocd-applicationset-controller/commands/applicationset_controller.go:303` [284]). argocd-apps-install sets none
   (apron tests/run.sh checks the template).
6. **A reconcile acts on the ApplicationSet it read at its start.** `Reconcile` does one `Get` (`:138`) and passes that object
   to `deleteInCluster` under that object's policy (`:351`), so a reconcile that read the set before the window opened can
   still delete after the stored policy says `create-update`. The refresh annotation is the drain signal: it is removed only
   at the very end of a reconcile, past its create, update and delete steps (`:378` `RefreshRequired`; `updateResourcesStatus`
   re-reads the set just before (`:1032`, its `Get` and `DeepCopyInto`), so the remover may be a reconcile that started before the annotation was set),
   and the workqueue never runs two reconciles of one key at once. So once it is gone, no reconcile that read the set
   earlier can still reach its delete step, and every later one reads the set as it is now. It does **not** prove a fresh
   git read: only a reconcile that read the annotation skips the repo-server's revision cache (`generators/git.go:70`
   `noRevisionCache`), and the remover may not be that one. A stale identity read is covered by time instead (C.3, D.2).
   ApplicationSet status has no observedGeneration in v3.5.0. Used at C.1, C.3, C.5, D.1, D.2 and D.4.
7. **The unconditional ignore rule normalises the live and the generated Application the same way**
   (`createOrUpdate.go:110` `applyIgnoreDifferences` on both), so there is no first-transition source deletion of the
   kind the annotation-scoped `select()` rule had (CodeRabbit on apron#256). On create, nothing is ignored: a new gated
   Application starts on its Helm sources and the agent switches it.

All of this is exercised against the **real** controller in apron `tests/appset` (the Argo CD Go module, its own git
generator, an in-memory tenants repo, envtest kube-apiserver 1.36.2): one set per environment; the ignore rule and
`preservedFields` keep an agent switch in the gated set and not in tenant-onboarding; a gated Application's first git source
(the agent's carrier) is its gitops repository, with and without the configMapGenerator source, and tenant-onboarding's
order is unchanged; the handover in (after the refresh-annotation wait, with C.4's `move`), then back, keeps the
Application (same uid); and a bare flip outside the window makes tenant-onboarding delete the Application with its
finalizer on (the failure the window exists for). Run against v3.5.0 in CI and once by hand against v3.4.5: both pass.

## 2. Preconditions (read-only)

Context `hangar-dev` on every command. Nothing below touches hangar-prod.

```
kubectl --context hangar-dev -n argocd-apps get applicationsets.argoproj.io
kubectl --context hangar-dev -n argocd-apps get cm argocd-cmd-params-cm -o jsonpath='{.data.applicationsetcontroller\.policy}{"|"}{.data.applicationsetcontroller\.enable\.policy\.override}{"\n"}'
kubectl --context hangar-dev -n argocd-apps get deploy argocd-apps-applicationset-controller -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
kubectl --context hangar-dev -n clearance-system get deploy clearance-argocd-agent -o jsonpath='{.spec.template.spec.containers[0].args}{"\n"}'
```
Expect: no `tenant-onboarding-gated`; the policy keys print `|` (both empty: override on); image `quay.io/argoproj/argocd:v3.5.0`;
the agent runs with `--optin` (dev's `clearance.gate.agent.optIn: true`, on main since W-40). **Stop** if a controller-wide
policy is set: the window would be ignored and the handover would delete. hangar-dev's `cluster.yaml` has
`clearance.gate.tenantPlugin: false` (apron refuses `gatedSet` without it: an Application on the static plugin would keep
that source through the handover and the agent would refuse it), so no tenant-onboarding Application is on the plugin;
check it (a failed read stops it: `pipefail`, and `jq -e` fails on empty input):
```
bash -s <<'EOF'
set -o pipefail
out=$(kubectl --context hangar-dev -n argocd-apps --request-timeout=20s get applications.argoproj.io -o json | jq -er '[.items[] | select(any(.metadata.ownerReferences[]?; .controller == true and .name == "tenant-onboarding")) | select([(.spec.source // empty), (.spec.sources[]? // empty)] | any(.plugin != null)) | .metadata.name] | join("\n")') \
  || { echo "STOP: the Applications could not be read"; exit 2; }
[ -z "$out" ] || { echo "$out"; echo "STOP: the tenant-onboarding Applications above are on a plugin"; exit 1; }
echo "ok: no tenant-onboarding Application is on a plugin"
EOF
```
Go on only on `ok` and exit 0.

Baseline of every tenant Application (name, uid, generation, owner, finalizers, annotations, sources):
```
W=<an evidence directory>
kubectl --context hangar-dev -n argocd-apps get applications.argoproj.io -o json | jq -S '[.items[] | {name:.metadata.name, uid:.metadata.uid, generation:.metadata.generation, owner:([.metadata.ownerReferences[]? | select(.controller) | .name][0]), finalizers:.metadata.finalizers, annotations:(.metadata.annotations // {} | del(.["argocd.argoproj.io/refresh"])), sources:(.spec.source // .spec.sources)}]' > $W/apps-before.json
```

**Stop if any tenant identity names `clearanceGate` at all.** Step A runs with no handover window, so tenant-onboarding
would delete such an Application (finalizer included) when it starts excluding it. The selector matches the parameter as
the string `"true"`, and more spellings than `true` give it: `"true"`, `True`, and, because the git generator parses with
`sigs.k8s.io/yaml` (YAML 1.1 booleans), `yes` and `on`. Airframe writes the key only when it is true, so before step A no
identity carries it: the scan stops on any mention of the key, whatever its value, and on any error. It reads every file
the generator can read, and more: `find -path 'tenants/*/*/identity.yaml'` with no depth limit (in `-path`, `*` also
matches `/`), so a deeper path such as `tenants/a/b/c/identity.yaml` is read too. argocd-apps renders
`applicationsetcontroller.enable.new.git.file.globbing: "true"`, where the generator's `*` stops at `/` and reads depth 3
only; the legacy mode (`git ls-files`) also reads deeper paths; the scan covers both, and a stop on a deeper file the
generator ignores is a safe stop. `find` fails on a directory it cannot read, where a shell glob would skip it silently.
It does not follow symlinks, and Argo CD does (`util/git/client.go` `LsFiles` resolves them inside the repository and
reads the target, and its glob descends symlinked directories), so **any symlink under `tenants/` is a stop**: an
`identity.yaml` symlink, or a symlinked directory, would hide an identity from the scan. Airframe writes plain files;
neither tenants repo has a symlink today. `set -f` keeps a listed path from being glob-expanded. It stops when there are
no identities (a wrong directory). grep exits 0 on a match, 1 on none, and anything else on an error, including an error
after a match. **Announce the freeze (below) before taking the checkout**, then take `T` as a fresh checkout of the tenants
repo (`gitops-hangar-dev-tenants`, `main`): a gated identity committed before the announcement is then in `T`, and one
committed after it breaks the freeze. The script fetches `origin/main` and stops unless `T`'s HEAD is that commit, so a
checkout taken before a later push is never scanned. In bash:
```
bash -s -- "$T" <<'EOF'
cd "$1" || exit 2
git fetch -q origin main || { echo "STOP: git fetch failed in $1"; exit 2; }
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "STOP: $1 is not at origin/main (HEAD $(git rev-parse --short HEAD), origin/main $(git rev-parse --short origin/main)): take a fresh checkout after the freeze is announced"; exit 2; }
set -f
s=$(find tenants -type l) || { echo "STOP: tenants/ could not be read in full (find failed)"; exit 2; }
[ -z "$s" ] || { echo "$s"; echo "STOP: the symlinks above are under tenants/ (Argo CD reads through them, find does not): read them by hand"; exit 2; }
l=$(find tenants -path 'tenants/*/*/identity.yaml' -type f) || { echo "STOP: tenants/ could not be read in full (find failed)"; exit 2; }
f=($l)
[ ${#f[@]} -gt 0 ] || { echo "STOP: no tenants/*/*/identity.yaml in $1 (wrong checkout?)"; exit 2; }
grep -l -e clearanceGate -- "${f[@]}"; rc=$?
case $rc in
  0) echo "STOP: the identities above name clearanceGate"; exit 1 ;;
  1) echo "none gated: ${#f[@]} identities read, none names clearanceGate" ;;
  *) echo "STOP: the scan failed (grep exit $rc)"; exit 2 ;;
esac
EOF
```
Go on only on `none gated` and exit 0. The freeze below has held since before `T` was taken, and still holds.

**Freeze of gate membership and of the tenant identities.** Nothing in the cluster enforces the order yet (section 6). For
the whole rehearsal, the operator running it is the only one who changes the tenants repo's `tenants/*/*/identity.yaml`
(no `ApplicationEnvironment` or app is created, deleted, renamed or edited by anyone else), and the operator changes only:
the throwaway's identity at B (created), C.2 and D.2 (`clearanceGate`) and E (deleted, after the window is closed). The
C.6 check assumes that no identity changes between it and the close sync; the freeze is what makes that true. Announce
the freeze before taking the checkout `T` for step A's scan (and so before the scan and step A), and lift it after E. On hangar-dev the only writers are the owner and this session; on a shared
cluster the freeze needs an Airframe or admission guard before this is run.

Also in place before step B: airframe#151 merged and its composition live on hangar-dev (the throwaway's identity.yaml must
come from Airframe, as a real one would).

## 3. Steps

### A. Turn the gated set on, no environment gated

gitops-hangar-dev PR (owner merges): `cluster.yaml` `clearance.gate.agent.gatedSet: true`, plus the throwaway's project and
namespace on the agent (`projects: [w40-optin-test, w43-handover]`, `protectedNamespaces: [w40-optin-test, app-w43-handover-dev]`),
rendered with the apron PR. The render changes `02-argocd-apps/tenant-onboarding/chart/applicationset.tmpl.yaml`,
`.../templates/render.yaml`, the agent's values and `cluster.yaml`, nothing else (diff-check it).

Observe after the `tenant-onboarding` Application (namespace `argocd`) syncs:
```
kubectl --context hangar-dev -n argocd-apps get applicationset tenant-onboarding tenant-onboarding-gated -o json | jq '.items[] | {name:.metadata.name, selector:.spec.generators[0].selector, ignore:.spec.ignoreApplicationDifferences, preserved:.spec.preservedFields, sync:.spec.syncPolicy, conditions:[.status.conditions[]? | select(.status=="True") | {type, message}]}'
```
Expect: the two sets as in the table; `tenant-onboarding-gated` generates nothing; neither has an `ErrorOccurred` condition.
Then the blast-radius check: the baseline command again into `apps-after-A.json`, `diff` against `apps-before.json`:
**identical** (no tenant Application changed owner, uid, generation, finalizers, annotations or sources). If any entry
moved, STOP and roll back (section 5).

### B. Create the throwaway environment, ungated

Through Airframe (Tower or a PR to the catalog namespace): app `w43-handover` with an `ApplicationEnvironment` `dev` on
hangar-dev, **without** `clearanceGate`, chart default, `replicaCount: 0` in its values (nothing needs to run; the objects
need to exist). Label its namespace for the agent: `kubectl --context hangar-dev label ns app-w43-handover-dev clearance.hangar.io/environment=dev`.
Wait for `w43-handover-dev` to be Synced, then record:
```
kubectl --context hangar-dev -n argocd-apps get application w43-handover-dev -o json | jq '{uid:.metadata.uid, owner:.metadata.ownerReferences, finalizers:.metadata.finalizers, annotations:.metadata.annotations}' | tee $W/w43-B.json
kubectl --context hangar-dev -n app-w43-handover-dev get deploy,svc,cm -o json | jq '[.items[] | {kind, name:.metadata.name, uid:.metadata.uid}]' | tee $W/workload-B.json
```
Expect: owner `tenant-onboarding` (controller), finalizer `resources-finalizer.argocd.argoproj.io`, no `clearance.hangar.io/*` annotation.

### C. Hand it over into the gated set

1. gitops-hangar-dev PR: `clearance.gate.agent.gatedSetHandover: true`. After the sync, both sets show `applicationsSync: create-update`
   (the jq above). Then wait for a reconcile of each that started after the window opened (section 1, item 6): a reconcile
   that read the set earlier still holds the deleting policy.
   The wait below (used again at C.3, C.5, D.2 and D.4; the sets to wait for are its arguments) stops unless the
   annotation write succeeds on every set named (a set it did not annotate would show no pending annotation with no new
   reconcile), every read succeeds, each kubectl call returns within 20 s, and the sets clear within 5 minutes:
   ```
   bash -s -- tenant-onboarding tenant-onboarding-gated <<'EOF'
   set -o pipefail
   [ $# -gt 0 ] || { echo "STOP: name the ApplicationSets to wait for"; exit 2; }
   k() { kubectl --context hangar-dev -n argocd-apps --request-timeout=20s "$@"; }
   deadline=$((SECONDS + 300))
   k annotate applicationset "$@" argocd.argoproj.io/application-set-refresh=true --overwrite \
     || { echo "STOP: the refresh annotation was not set on every set named"; exit 2; }
   while [ "$SECONDS" -lt "$deadline" ]; do
     n=$(k get applicationset "$@" -o json | jq -er '[(.items // [.])[] | select(.spec.syncPolicy.applicationsSync == "create-update" and ((.metadata.annotations // {}) | has("argocd.argoproj.io/application-set-refresh") | not))] | length') \
       || { echo "STOP: the sets could not be read"; exit 2; }
     [ "$n" = "$#" ] && [ "$SECONDS" -lt "$deadline" ] && { echo "ok: $* reconciled under create-update since the annotation was set"; exit 0; }
     sleep 10
   done
   echo "STOP: not every set cleared the refresh annotation within 5 minutes: read its conditions"; exit 1
   EOF
   ```
   **Do not go on without `ok` and exit 0.** An annotation that stays means that set's reconcile fails before its end:
   stop and read its conditions.
2. Set `spec.clearanceGate: true` on the `ApplicationEnvironment` `w43-handover-dev`. Check the tenants repo commit:
   `tenants/w43-handover/dev/identity.yaml` gains exactly `clearanceGate: true`. Refresh both sets to skip the 3-minute poll:
   `kubectl --context hangar-dev -n argocd-apps annotate applicationset tenant-onboarding tenant-onboarding-gated argocd.argoproj.io/application-set-refresh=true --overwrite`.
3. Observe for 3 minutes: `w43-handover-dev` is **not** deleted (no `deletionTimestamp`), same uid, owner still
   `tenant-onboarding`; `tenant-onboarding-gated` has `ErrorOccurred`: `Object argocd-apps/w43-handover-dev is already owned by
   another ApplicationSet controller tenant-onboarding`. The workload's uids equal `workload-B.json`. A tenant-onboarding
   reconcile that generates from the identities as they were before C.2 still generates the Application, and
   `CreateOrUpdate` writes a merge patch with no resourceVersion precondition (`applicationset/utils/createOrUpdate.go:127`):
   during or after C.4 it would put tenant-onboarding's controller reference and source order back. Two kinds exist: one
   already running, and a later one that resolves `main` from the repo-server's revision cache. So:
   - wait out the revision cache, timed from the push of C.2's commit, not from any later report of it. `getRefs`
     (`util/git/client.go`) writes whatever its `ls-remote` returned into the cache, unconditionally and with a fresh
     expiry (`reposerver/cache/cache.go` `SetGitReferences`: a plain Redis `SET` with a TTL, which no read refreshes), so
     a lookup that read the refs before the push can write the old revision after the gated set has already reported
     the new one. Such a lookup started before the push, and its one HTTP request is cut off by the repo-server's git
     client timeout (`ARGOCD_GIT_REQUEST_TIMEOUT`, default 15s: an `http.Client` timeout, which covers reading the
     response; the tenants repo is https, and over ssh there is no such bound), so its write lands before push + that
     timeout, and the entry is gone one revision cache expiry after that (`--revision-cache-expiration`, default
     `ARGOCD_RECONCILIATION_TIMEOUT`, else 3m). A retry is a new request, bounded the same way. The ApplicationSet
     controller's own call timeout to the repo-server (`--repo-server-timeout-seconds`, 60s) bounds nothing here: the
     repo-server finishes the lookup after its caller gives up. So the bound is push + git timeout + expiry. Read the
     values:
     ```
     kubectl --context hangar-dev -n argocd-apps get deploy argocd-apps-repo-server -o json | jq '.spec.template.spec.containers[0] | {args, env: [(.env // [])[] | select(.name == "ARGOCD_RECONCILIATION_TIMEOUT" or .name == "ARGOCD_GIT_REQUEST_TIMEOUT")]}'
     kubectl --context hangar-dev -n argocd-apps get cm argocd-cm -o jsonpath='{.data.timeout\.reconciliation}{"\n"}'
     kubectl --context hangar-dev -n argocd-apps get cm argocd-cmd-params-cm -o jsonpath='{.data.reposerver\.git\.request\.timeout}{"\n"}'
     ```
     Expect no `--revision-cache-expiration` in the args (it would win), both variables taken from those two keys, and
     the values apron renders for hangar-dev's argocd-apps: `timeout.reconciliation` `120s` (the chart's default; apron
     sets `600s` only with `argocd.light`, which is hangar-prod's) and no git timeout (15s). The wait is 15 s + 120 s =
     2 min 15 s, rounded up to the next whole minute (the round-up covers the Redis write itself): **180 s**. Other values:
     recompute it the same way, and with none set take 3m. The push time is taken as T0, the moment `ls-remote` first
     shows C.2's commit as `main` (at or after the push); the script stops unless `main` is that commit within 5 minutes.
     With `C` the full sha of C.2's tenants commit and `T` the tenants checkout:
     ```
     bash -s -- "$T" "$C" 180 <<'EOF'
     [ $# -eq 3 ] || { echo "STOP: name the tenants checkout, the commit and the wait in seconds"; exit 2; }
     case "$2" in *[!0-9a-f]*|'') echo "STOP: $2 is not a full commit sha"; exit 2 ;; esac
     [ ${#2} -eq 40 ] || { echo "STOP: $2 is not a full commit sha"; exit 2; }
     case "$3" in *[!0-9]*|'') echo "STOP: $3 is not a number of seconds"; exit 2 ;; esac
     deadline=$((SECONDS + 300))
     while :; do
       h=$(git -C "$1" ls-remote origin refs/heads/main) || { echo "STOP: ls-remote failed"; exit 2; }
       [ "${h%%[[:space:]]*}" = "$2" ] && break
       [ "$SECONDS" -lt "$deadline" ] || { echo "STOP: main is not $2 after 5 minutes (main is ${h%%[[:space:]]*}): read it by hand"; exit 2; }
       sleep 5
     done
     echo "T0 $(date -u '+%Y-%m-%dT%H:%M:%SZ'): main is $2; waiting $3 s"
     sleep "$3"
     echo "ok: $3 s since main was first seen at $2 ($(date -u '+%Y-%m-%dT%H:%M:%SZ'))"
     EOF
     ```
     Go on only on `ok` and exit 0;
   - then C.1's wait for `tenant-onboarding` only (`bash -s -- tenant-onboarding`; the gated set's reconcile now fails at
     that error before it clears the annotation).
   **Do not do C.4 before both.** After them, every tenant-onboarding reconcile still to come resolves the new commit, and
   none that started earlier is still running.
4. Move the controller reference, guarded by the uid of tenant-onboarding (one owner reference is expected; check first),
   and in the same atomic patch put the `ref: appsrc` source first (the gated set's order). The gated set's ignore rule keeps
   the live sources when it adopts the Application, so without the move the agent would carry its plugin source on the
   chart repository at its pinned tag (apron README "Gated environments"):
   ```
   kubectl --context hangar-dev -n argocd-apps get application w43-handover-dev -o jsonpath='{.metadata.ownerReferences}{"\n"}{.spec.sources[*].repoURL}{"\n"}'
   U=$(kubectl --context hangar-dev -n argocd-apps get applicationset tenant-onboarding -o jsonpath='{.metadata.uid}')
   kubectl --context hangar-dev -n argocd-apps patch application w43-handover-dev --type json -p "[{\"op\":\"test\",\"path\":\"/metadata/ownerReferences/0/uid\",\"value\":\"$U\"},{\"op\":\"test\",\"path\":\"/spec/sources/1/ref\",\"value\":\"appsrc\"},{\"op\":\"move\",\"from\":\"/spec/sources/1\",\"path\":\"/spec/sources/0\"},{\"op\":\"remove\",\"path\":\"/metadata/ownerReferences/0\"}]"
   kubectl --context hangar-dev -n argocd-apps annotate applicationset tenant-onboarding-gated argocd.argoproj.io/application-set-refresh=true --overwrite
   ```
5. The second guard: `sleep 180` from C.4's patch (C.3's wait again, now timed from the move), then C.1's wait for both
   sets, then re-check the owner. If an old-revision entry outlived C.3's wait (a value read wrong), it has expired by
   the end of the sleep, and every tenant-onboarding reconcile that could have used it has finished by the end of C.1's
   wait; a controller reference it put back is then visible. The check fails closed, and the window is still open, so a
   failure deletes nothing. With `W` the evidence directory:
   ```
   bash -s -- w43-handover-dev tenant-onboarding-gated "$(jq -r .uid "$W/w43-B.json")" <<'EOF'
   set -o pipefail
   [ $# -eq 3 ] || { echo "STOP: name the Application, the ApplicationSet that must control it and the Application's uid"; exit 2; }
   k() { kubectl --context hangar-dev -n argocd-apps --request-timeout=20s "$@"; }
   su=$(k get applicationset "$2" -o jsonpath='{.metadata.uid}') && [ -n "$su" ] || { echo "STOP: cannot read ApplicationSet $2"; exit 2; }
   r=$(k get application "$1" -o json | jq -er --arg su "$su" --arg au "$3" '
     [.metadata.ownerReferences[]? | select(.controller == true)] as $c
     | if .metadata.uid != $au then "its uid is \(.metadata.uid), not \($au)"
       elif .metadata.deletionTimestamp != null then "it is being deleted"
       elif ($c | length) != 1 then "it has \($c | length) controller references"
       elif $c[0].uid != $su then "its controller is \($c[0].name) (uid \($c[0].uid))"
       else "ok" end') || { echo "STOP: cannot read Application $1"; exit 2; }
   [ "$r" = ok ] || { echo "STOP: $1: $r, not $2 (uid $su): keep the window open"; exit 1; }
   echo "ok: $1 (uid $3) is controlled by $2 (uid $su)"
   EOF
   ```
   **Do not go on without `ok` and exit 0.** On `STOP`, leave the window open and read the Application and both sets'
   conditions; a controller reference back on tenant-onboarding means C.3's wait did not hold: find out why, then redo
   C.3 and C.4. Then expect: owner `tenant-onboarding-gated` (controller), same uid, the gitops repository
   as the carrier (not yet switched: `spec.sources[0]` is the `ref: appsrc` source; already switched: the one plugin
   source's `repoURL` is the gitops repository and its `sources` parameter starts with the `ref: appsrc` source), annotation `clearance.hangar.io/protect: "true"`, no resources finalizer, the gated set's condition cleared. Then the agent (log `kubectl --context hangar-dev -n clearance-system logs deploy/clearance-argocd-agent --since=5m`):
   pair `w43-handover/dev` reported, `Application switched to the plugin ... shape=sources`; the Application now has one plugin
   source, on the app's gitops repository at `main` (not the chart repository), and `clearance.hangar.io/switched: sources`; watch 5 minutes that the gated set does not revert either (W-40's check,
   now on a tenant Application). Clear the change if it holds, and the merged grant and namespace label follow as in W-40 step 3.
6. Close the window: PR removing `gatedSetHandover`. Before merging it, check ownership both ways (the condition check alone
   misses a set that has not reconciled yet). From the Applications: every Application whose controller is
   `tenant-onboarding` or `tenant-onboarding-gated` must be one that set generates from a current identity; an `ORPHAN`
   (its identity removed or renamed) is what the closed window would delete. From the identities: each one's Application
   must be controlled by the set its `clearanceGate` puts it in (`MISMATCH`, including no Application at all). Also no
   Application without a controller (`UNOWNED`). An identity whose `clearanceGate` is anything but absent, `false` or `true`
   (an explicit `null` included)
   (a quoted string, `yes`, `True`: the generator's YAML 1.1 reading and yq's YAML 1.2 one can differ) stops the check.
   Every read that fails stops it, and so does any symlink under `tenants/`; it lists the identities as step A's scan
   does (no depth limit). In bash, with `T` a fresh checkout of the tenants repo at `main` (the freeze means it is
   what the sets last read; the script fetches `origin/main` and stops unless `T`'s HEAD is that commit, so a checkout taken before
   the last push is refused) and `W` the evidence directory:
   ```
   bash -s -- "$T" "$W" <<'EOF'
   cd "$1" || exit 2; W=$2
   git fetch -q origin main || { echo "STOP: git fetch failed in $1"; exit 2; }
   [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "STOP: $1 is not at origin/main (HEAD $(git rev-parse --short HEAD), origin/main $(git rev-parse --short origin/main)): take a fresh checkout after the freeze is announced"; exit 2; }
   set -f
   s=$(find tenants -type l) || { echo "STOP: tenants/ could not be read in full (find failed)"; exit 2; }
   [ -z "$s" ] || { echo "$s"; echo "STOP: the symlinks above are under tenants/ (Argo CD reads through them, find does not): read them by hand"; exit 2; }
   l=$(find tenants -path 'tenants/*/*/identity.yaml' -type f) || { echo "STOP: tenants/ could not be read in full (find failed)"; exit 2; }
   f=($l)
   [ ${#f[@]} -gt 0 ] || { echo "STOP: no tenants/*/*/identity.yaml in $1"; exit 2; }
   : > "$W/want.tsv" || exit 2
   for i in "${f[@]}"; do
     a=$(yq -e '.appName' "$i") && e=$(yq -e '.env' "$i") && g=$(yq '(has("clearanceGate") | to_string) + ":" + (.clearanceGate | tag) + ":" + (.clearanceGate | to_string)' "$i") \
       || { echo "STOP: cannot read $i"; exit 2; }
     case "$g" in
       'false::'|'true:!!bool:false') s=tenant-onboarding ;;
       'true:!!bool:true') s=tenant-onboarding-gated ;;
       *) echo "STOP: $i says clearanceGate $g (Airframe writes true or nothing: read it by hand)"; exit 2 ;;
     esac
     printf '%s\t%s\n' "$a-$e" "$s" >> "$W/want.tsv" || exit 2
   done
   d=$(cut -f1 "$W/want.tsv" | sort | uniq -d); [ -z "$d" ] || { echo "STOP: more than one identity makes $d"; exit 2; }
   kubectl --context hangar-dev -n argocd-apps get applications.argoproj.io -o json > "$W/apps-C6.json" || { echo "STOP: cannot list the Applications"; exit 2; }
   r=$(jq -r --rawfile want "$W/want.tsv" '
     ($want | split("\n") | map(select(length > 0) | split("\t") | {key: .[0], value: .[1]}) | from_entries) as $w
     | [.items[] | {n: .metadata.name, o: ([.metadata.ownerReferences[]? | select(.controller == true) | .name][0] // "")}] as $a
     | ($a | map({key: .n, value: .o}) | from_entries) as $by
     | ($a[] | select(.o == "tenant-onboarding" or .o == "tenant-onboarding-gated") | select($w[.n] == null)
         | "ORPHAN \(.n): controlled by \(.o), and no identity generates it"),
       ($w | to_entries[] | select($by[.key] != .value)
         | "MISMATCH \(.key): controlled by \(if $by[.key] == null then "nothing (no Application)" elif $by[.key] == "" then "nothing" else $by[.key] end), its identity puts it in \(.value)"),
       ($a[] | select(.o == "") | "UNOWNED \(.n)")' "$W/apps-C6.json") || { echo "STOP: jq failed"; exit 2; }
   if [ -n "$r" ]; then echo "$r"; echo "STOP: do not merge the close PR"; exit 1; fi
   echo "ok: $(wc -l < "$W/want.tsv" | tr -d ' ') identities; every Application either set controls is one that set generates"
   EOF
   kubectl --context hangar-dev -n argocd-apps get applicationsets tenant-onboarding tenant-onboarding-gated -o json | jq '.items[] | {name:.metadata.name, error:[.status.conditions[]? | select(.type=="ErrorOccurred" and .status=="True") | .message]}'
   ```
   Merge only when the script prints `ok` and exits 0, and neither set has an error. The freeze (section 2) holds until the
   close sync is done, so no identity can change between this check and the sync.
   After the sync: `w43-handover-dev` unchanged, workload uids equal `workload-B.json`, and the baseline
   diff of every other Application still identical.

### D. Hand it back to tenant-onboarding

1. Open the window again (as C.1, including the wait for a reconcile after it opened).
2. Remove `spec.clearanceGate` from the `ApplicationEnvironment`; refresh both sets. Expect: the gated set keeps the Application
   (owner unchanged, same uid, still switched); `tenant-onboarding` reports `already owned by another ApplicationSet controller
   tenant-onboarding-gated`. Then C.3's wait, timed from the push (its script, with `C` the tenants commit that removed
   `clearanceGate`), and C.1's wait for `tenant-onboarding-gated` only: a gated-set reconcile that generates from the identities as they were would put the
   `protect` annotation back after D.3. **Do not do D.3 before both.**
3. Opt out by hand (nothing reconciles the Application now, so it sticks):
   `kubectl --context hangar-dev -n argocd-apps annotate application w43-handover-dev clearance.hangar.io/protect-`.
   Expect in the agent log, in order: removal reported, label off, `Application put back to its original sources`, merged grant
   gone. The Application has its two Helm sources again and no `switched` annotation; the namespace has no `protected` label.
   **Do not go on while it is still on the plugin**: tenant-onboarding would overwrite the plugin source and the agent could no
   longer restore or unlabel it (gate.md "The marker has two halves"), leaving a labelled namespace whose Helm render admission
   refuses once enforced.
4. Move the controller reference to tenant-onboarding (C.4's uid test and remove, with the gated set's uid; no `move`:
   tenant-onboarding rewrites the sources), refresh `tenant-onboarding`, then C.5's second guard the other way: `sleep 180`
   from the patch, C.1's wait for both sets, and C.5's owner check with `tenant-onboarding`
   (`bash -s -- w43-handover-dev tenant-onboarding "$(jq -r .uid "$W/w43-B.json")"`; a stale gated-set reconcile would
   have taken it back). Do not go on without `ok` and exit 0. Expect: owner `tenant-onboarding`, same uid, the
   chart source first again, resources finalizer back, no `clearance.hangar.io/*` annotation, Synced.
5. Close the window (C.6's check first). Then the full baseline diff: every Application identical to `apps-before.json` except
   `w43-handover-dev` (new since the baseline) and the workload uids equal `workload-B.json`.

### E. Cleanup

Delete the throwaway through Airframe (its `ApplicationEnvironment`, then the app). It is back in tenant-onboarding, so its
Application is deleted with its finalizer and the workload goes with it, as for any tenant environment. Turning
`gatedSet` off afterwards is optional: with no gated environment, remove the key, render, and delete the now unmanaged
`tenant-onboarding-gated` ApplicationSet by hand (the tenant-onboarding Application does not prune); it owns nothing, so
nothing is deleted with it. Check: `kubectl --context hangar-dev -n argocd-apps get applications.argoproj.io -o json | jq '[.items[] | select(.metadata.ownerReferences[0].name=="tenant-onboarding-gated")] | length'` is `0` first.

## 4. What is NOT rehearsed live

The bare flip (C.2 without C.1) deletes the workload by design of Argo CD (section 1, items 1 and 2). It is shown in
apron `tests/appset` (`a bare flip outside the window deletes the Application`), never on a cluster.

## 5. Failure modes and rollback

| Failure | What happens | Prevention / recovery |
|---|---|---|
| `clearanceGate` flipped with the window closed | the set that stops generating the Application deletes it; from tenant-onboarding the resources finalizer deletes the workload; the gated set then creates a new Application (new uid) that deploys it again. From the gated set (handover back) the Application is deleted but the workload stays (no finalizer) and tenant-onboarding recreates and adopts it | the window first, always; the README and this plan say so. Today nothing in the cluster enforces the order (an Airframe or admission guard is a follow-up: section 6). On hangar-dev recovery is a re-sync of the recreated Application |
| a controller-wide `applicationsetcontroller.policy` set without the override | `applicationsSync` is ignored: the window does nothing, the flip deletes | precondition check in section 2; apron's test fails if argocd-apps-install sets it |
| the window closed while an Application is still owned by a set that no longer generates it (C.4 or D.4 skipped, or its identity removed or renamed) | that set deletes it on its next reconcile (a tenant-onboarding one with the finalizer: the workload goes) | C.6 / D.5 check: no `ORPHAN`, `MISMATCH` or `UNOWNED`, no `ErrorOccurred` on either set; the identity freeze |
| `clearanceGate` flipped right after the window's render, before the sets reconciled under it | a reconcile that read the set before the window still holds `sync` and deletes the Application its generator stops returning | C.1's refresh-annotation wait (section 1, item 6) |
| C.4 while a tenant-onboarding reconcile that read the identities before C.2 is still running | its merge patch (no resourceVersion precondition) puts tenant-onboarding's controller reference back after the move; closing the window would then delete the Application | C.3's revision-cache wait timed from the push and its wait on tenant-onboarding before C.4; C.5's second wait from the move and its fail-closed owner check, with the window still open; the same at D.2 and D.4 |
| C.4 without the `move` | the gated set keeps the chart source first (ignore rule); the agent carries the plugin source on the chart repository at its tag: the plugin refuses the gitops repository (not on `CLEARANCE_CHART_REPOS`), or a release commit does not re-render | the `move` in C.4's patch; C.5 checks the plugin source's repository. To repair: opt out (remove `protect`), wait for the restore, move the source by hand, put `protect` back |
| a cluster with `tenantPlugin` on | an Application on the static plugin keeps that source through the handover and the agent refuses it | apron refuses `gatedSet` unless `tenantPlugin: false`; section 2 checks no tenant Application is on a plugin |
| owner reference removed before the flip | tenant-onboarding still generates the Application and re-adopts it (SetControllerReference on an unowned object): nothing moves | do C.4 after C.2, as written |
| the JSON patch `test` fails | nothing is changed (the patch is atomic) | re-read the owner references; never remove one without the uid test |
| both sets generate the same name (a selector bug) | each reports `already owned` for the other's Application; nothing is deleted while the error stands (the reconcile returns before its delete step) | tests/appset checks exactly-one; on a cluster, revert the apron render |
| the agent is down at C.5 | the Application stays on its Helm sources, annotated, owned by the gated set: protection is not enforced yet, nothing else breaks | scale the agent back; it switches on its next pass |
| D.3 opt-out cannot complete (core unreachable) | the agent keeps the Application on the plugin and the namespace labelled (gate.md "Who can set the annotation") | wait for the core; do not do D.4 until the restore is seen |
| the gated Application's sources go stale | the ignore rule stops the gated set updating `/spec/source(s)` after creation: a new default chart revision or identity.yaml `chart` does not reach it | known cost of option (3); the agent's plugin parameters carry the chart pins it switched with. A follow-up for the agent (re-switch on a template change) or a handover back and forth |

**Rollback of the whole change**: with no environment gated, revert the gitops PR of step A (the render goes back to one
ApplicationSet) and delete `tenant-onboarding-gated` by hand as in E. With an environment gated, hand it back first (D).

## 6. Open points

- **Order is enforced by process only.** A flip outside the window is the one destructive path. Options for later: an
  Airframe-side gate (the composition writes `clearanceGate` for an existing environment only while the cluster registry says
  its window is open), or the Clearance agent taking over C.4/D.4 (it already patches Applications with a resourceVersion test).
  Neither is built.
- **tenant-onboarding's resources finalizer** contradicts its `preserveResourcesOnDeletion: true` comment (section 1, item 2).
  Out of W-43's scope (the render stays byte-identical); worth its own decision.
- **W-42 (the gate rule, `specs/plans/gate-rule-design.md` section 3).** A rule-gated tenant Application needs the same parent
  entries as an annotated one (the ignore rule and `preservedFields`). Option (3) gives the rule one place where those entries
  exist: an environment the rule gates must be in `tenant-onboarding-gated`, or the agent blocks it ("does not ignore
  /spec/source"), which is safe but not protected. The rule needs no annotation, so the gated set's `protect` annotation is
  redundant for it but harmless. The set membership (identity.yaml `clearanceGate`) and the rule must agree; the simplest
  is that whatever writes the rule also sets `clearanceGate` for the environments it names, or that the gated set later
  selects on a key derived from the rule. A rule that newly gates an existing tenant environment still needs this handover.
