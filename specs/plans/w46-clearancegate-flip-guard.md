# W-46: a guard on `clearanceGate` flips

Written 2026-11-22. Strip W-46, the owner's follow-up to A-22 (a). A design note only: no code, nothing applied, no gitops
repo changed.

Read at: apron `origin/main` `2c11b7f` (apron#256 merged, head `abe3174`), airframe `origin/main` `e1cbd42` (airframe#151
merged), clearance `origin/main` `297d342`, gitops-hangar-dev `origin/main`, and the Argo CD v3.5.0 module source (the version
argocd-apps runs). The W-43 rehearsal plan is `specs/plans/w43-gated-set-handover-rehearsal.md` (hangar#148). Line numbers
below are v3.5.0.

## 1. The failure mode

Where the pieces live:

- `ApplicationEnvironment` is an Airframe XR (`airframe` `xrds/applicationenvironment.yaml`, `spec.clearanceGate`, boolean,
  default `false`). It lives on the control-plane cluster (hangar-dev), for every target cluster. The `xr-requests`
  ApplicationSet there syncs it from `gitops-hangar-dev-tenants` `tenants/<app>/xr-requests/`; Tower writes it as a PR.
- Its composition (`compositions/applicationenvironment/templates/render-github-resources/tenant-identity-yaml.yaml`) writes
  `clearanceGate: true` into `tenants/<app>/<env>/identity.yaml` in the target cluster's tenants repo, and writes nothing when
  false. It is a provider-github `RepositoryFile` with no `Delete` policy.
- On the target cluster, apron's tenant-onboarding chart renders two ApplicationSets from one template
  (`templates/02-argocd-apps/tenant-onboarding/chart/applicationset.tmpl.yaml`, `templates/render.yaml`, `hack/render.py`
  `tenant_gated_set_flags`). `tenant-onboarding` selects `clearanceGate NotIn ["true"]`. `tenant-onboarding-gated` selects
  `In ["true"]`. `clearance.gate.agent.gatedSetHandover: true` gives both `applicationsSync: create-update`: the window.

The exact sequence, gating an existing environment with the window closed:

1. Environment `E` is in `tenant-onboarding`. Its Application is controlled by that set and carries
   `resources-finalizer.argocd.argoproj.io` from the template.
2. The window is closed: neither set has `applicationsSync`, so the default policy (`sync`) allows deletes.
3. Someone sets `spec.clearanceGate: true` on `E`'s ApplicationEnvironment (Tower, a PR, or kubectl).
4. The composition renders the new file content. provider-github commits `clearanceGate: true` to the tenants repo's `main`.
5. The next `tenant-onboarding` reconcile (3-minute poll, or a refresh) reads the file. The selector drops `E`.
6. `deleteInCluster` lists the Applications the set controls and deletes each one it no longer generates
   (`applicationset_controller.go:859`; it runs because `AllowDelete` is true, `:351`).
7. The Application has the resources finalizer, so Argo CD deletes every resource it manages in `app-<app>-<env>`:
   Deployments, Services, and any managed database (a CNPG `Cluster`, Redis). Data goes with them.
8. `tenant-onboarding-gated` now generates `E`. It creates a new Application (new uid, no finalizer, `protect` annotation).
   It deploys the workload again, empty. The agent switches it.

The reverse flip (removing `clearanceGate`) is quieter but still wrong. The gated set deletes its Application. There is no
finalizer, so the workload stays. `tenant-onboarding` creates a new Application on Helm sources and adopts the workload. The
namespace keeps the agent's `protected` label, so admission refuses the Helm render once the gate enforces. The agent's
state for that Application is lost.

Three more ways into the same deletion, with the window "open" or no XR change at all:

- the flip lands after the window's render but before both sets reconciled under it (W-43 section 1, item 6);
- someone edits `identity.yaml` in the tenants repo by hand (the composition then writes its own value back: two flips);
- an ApplicationEnvironment is deleted and created again with the other value. Its `identity.yaml` was kept (no `Delete`
  policy; airframe `docs/user/decommission-app.md`), and `overwriteOnCreate: true` rewrites it. To admission this is a
  CREATE, not a change.

Today only the W-43 procedure stops any of this.

## 2. Options

Four options. (a), (b) and (c) are the brief's. (d) came out of reading the controller.

### (a) The composition holds the change

The composition already reads the cluster registry (`00-cluster-gate.yaml`, an extra-resources lookup on the hub's
`crossplane-system` ConfigMaps). It would also read a window field there. When the window is closed and `spec.clearanceGate`
differs from what it last wrote (the observed `tenant-identity-yaml` resource's `forProvider.content`), it keeps writing the
old value and reports a `ClearanceGateHeld` condition.

- Lives: Airframe (composition and status template).
- Blast radius: the render of every ApplicationEnvironment. A template error fails every environment's render, and a wrong
  hold flaps `identity.yaml`, the same class as the 2026-09-16 `$clusterOk` flap that deleted Infisical data.
- Fails open when the observed resource is empty: the first render after an XR is created again, so the re-create case is
  missed. Misses hand edits of the file.
- The XR says `true` while the cluster runs `false`. The held change lands by itself when the window opens, with no person
  watching.
- No admission dependency. That is its one advantage, and (b) costs little there.

Not recommended.

### (b) A ValidatingAdmissionPolicy on ApplicationEnvironment (hub)

A built-in VAP on the hub refuses a write that changes the effective `clearanceGate` unless the target cluster's window is
open. It reads the window from a param ConfigMap.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: airframe-clearancegate-window
spec:
  failurePolicy: Fail
  paramKind: {apiVersion: v1, kind: ConfigMap}
  matchConstraints:
    resourceRules:
      - apiGroups: ["catalog.hangar.io"]
        apiVersions: ["*"]
        operations: ["CREATE", "UPDATE"]
        resources: ["applicationenvironments"]      # not /status: Crossplane's status writes never match
  matchConditions:
    # True only for a write that changes the gate. Every field read is has()-guarded: a matchCondition error with
    # failurePolicy Fail would refuse every ApplicationEnvironment write, Crossplane's own included.
    - name: gate-changes
      expression: >-
        request.operation == 'CREATE'
          ? (has(object.spec) && has(object.spec.clearanceGate) && object.spec.clearanceGate == true)
          : (has(object.spec) && has(oldObject.spec) &&
             (has(object.spec.clearanceGate) && object.spec.clearanceGate == true) !=
             (has(oldObject.spec.clearanceGate) && oldObject.spec.clearanceGate == true))
  validations:
    - expression: >-
        has(object.spec.cluster) && has(params.data) && object.spec.cluster in params.data &&
        params.data[object.spec.cluster] == 'open'
      messageExpression: >-
        'clearanceGate on ' + object.metadata.name + ' changes which ApplicationSet owns its Application. That needs the
        handover window of cluster ' + (has(object.spec.cluster) ? object.spec.cluster : '?') + ' open (hangar
        specs/plans/w46-clearancegate-flip-guard.md section 4).'
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: airframe-clearancegate-window
spec:
  policyName: airframe-clearancegate-window
  validationActions: [Audit, Warn]                 # Deny after the audit period (section 5)
  paramRef:
    name: clearance-gate-handover
    namespace: crossplane-system
    parameterNotFoundAction: Deny
```

The param is one ConfigMap, `clearance-gate-handover`, with a key per cluster name and alias whose window is open. The
cluster-registry chart renders it from a new `clusters.yaml` field (`airframe.clearanceGateHandover: true`). A cluster with
no key is closed.

A missing ConfigMap is wider than a closed window. The API server resolves the param before it evaluates the match
conditions (`policy_dispatcher.go`). With `parameterNotFoundAction: Deny`, a missing param refuses **every**
ApplicationEnvironment CREATE and UPDATE, Crossplane's own main-resource writes included (finalizers,
`spec.crossplane.resourceRefs`), not just flips. Status writes go to the subresource and still work. In the audit period
(`[Audit, Warn]`) the refusal is only recorded and warned. So:

- the chart renders `clearance-gate-handover` always, empty when no window is open, so it is never absent in normal operation;
- the binding syncs after it (a later sync wave), and a chart test fails a render without it;
- if it is deleted, ApplicationEnvironment writes stop until `cluster-registry` is synced again. That is loud and quick to
  fix, and it never deletes anything. `Allow` would instead let every flip through silently. Open question 9.

- Lives: Airframe ships the policy next to the XRD and renders the param from `charts/cluster-registry`. Apron installs both
  on the control-plane cluster. Nothing in Clearance.
- Fail-closed is safe here. The match condition confines the policy to writes that flip the gate. A CEL error in a
  validation refuses that flip only. The has() guards keep the match condition itself from erroring.
- The defaulted field: the API server applies the XRD default (`false`) before admission. An absent field and `false` are the
  same, so a re-apply without the field is not a flip.
- A refused write gives the writer the reason at once: Tower shows the error, kubectl prints it, and the `xr-requests`
  Application reports a failed sync.
- Misses: hand edits of `identity.yaml`, and anything that deletes an Application for another reason (a selector bug, an
  identity removed by mistake).
- Its truth is a copy. The real window is the target's ApplicationSets. If the hub flag says open before the target's sets
  drained under `create-update`, a flip is allowed and deletes. (d) removes that risk.
- A refused `xr-requests` sync is retried. The flip lands by itself when the window opens. That is the right order, but the
  operator should expect it (section 4).

### (c) The Clearance agent moves the owner reference

The agent already reads parent ApplicationSets and patches Applications with a `resourceVersion` test
(`providers/argocd/agent/kubeapi.go`). It would do W-43's C.4 and D.4 itself: move an Application's controller reference
from the set that no longer generates it to the one that does.

- It does not remove the delete window on its own. The old set deletes in the same reconcile in which it stops generating
  the Application (`deleteInCluster` runs right after create and update). No agent can move the reference between the git
  commit and that reconcile. So (c) needs both sets never to delete: permanent `create-update`, or (d).
- It needs a signal for "which set generates this Application now". Argo CD has none in the CRD. `status.resources` lists
  what a set owns, not what it generates. What is left is parsing the other set's `ErrorOccurred` message ("already owned by
  another ApplicationSet controller ..."), which is not an API, or calling Argo CD's `applicationsets/generate` endpoint,
  which needs an Argo CD API token in the agent.
- Product separation. It can be stated without Hangar names: "two ApplicationSets labelled as handover peers
  (`clearance.hangar.io/handover-peer: <group>`); when one reports that the other owns an Application it generates, move the
  controller reference with a `resourceVersion` test". The labels go on the two sets in apron. No Airframe or tenant names
  in Clearance.
- Blast radius: the agent gains write access to `metadata.ownerReferences` of every Application in its projects. A wrong
  move leaves an Application with an owner that does not generate it. That set then deletes it, unless (d) is on.

Not now. It automates the manual move once (d) makes a stuck handover safe. See open question 7.

### (d) Refuse the ApplicationSet controller's delete of a tenant Application (target)

A VAP on each target cluster refuses a DELETE of an Application in `argocd-apps` when the requester is the ApplicationSet
controller's ServiceAccount and the Application's controller reference is `tenant-onboarding` or `tenant-onboarding-gated`.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: tenant-onboarding-no-set-delete
spec:
  failurePolicy: Fail
  matchConstraints:
    namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: argocd-apps}}
    resourceRules:
      - apiGroups: ["argoproj.io"]
        apiVersions: ["*"]
        operations: ["DELETE"]
        resources: ["applications"]
  matchConditions:
    # The username first: it is false for every other requester, and a false condition skips the policy even if a
    # later one errors. So a CEL error can only ever refuse the controller's own deletes of Applications.
    - name: by-applicationset-controller
      expression: "request.userInfo.username == 'system:serviceaccount:argocd-apps:@@APPSET_CONTROLLER_SA@@'"
    - name: tenant-set-controlled
      expression: >-
        has(oldObject.metadata.ownerReferences) &&
        oldObject.metadata.ownerReferences.exists(r, has(r.controller) && r.controller == true &&
          r.kind == 'ApplicationSet' && r.name in ['tenant-onboarding', 'tenant-onboarding-gated'])
  validations:
    - expression: "false"
      messageExpression: >-
        'The ApplicationSet controller may not delete tenant Application ' + oldObject.metadata.name + '. If its
        environment changed sets, finish the handover (move the controller reference). If it was removed on purpose,
        delete the Application by hand.'
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: tenant-onboarding-no-set-delete
spec:
  policyName: tenant-onboarding-no-set-delete
  validationActions: [Audit]                        # Deny after the audit period (section 5)
```

What the controller does with the refusal (read in v3.5.0): `deleteInCluster` records the error and returns it
(`:859`-`:869`). `Reconcile` sets `ErrorOccurred` with reason `DeleteApplicationError` and returns (`:351`). Create and update
already ran, so every other tenant Application is still updated. The refresh annotation stays (it is cleared at the end).

So a bare flip becomes a safe stuck state. The old set keeps the Application and cannot delete it. The new set reports
`already owned`. The workload is untouched. With (d) on, the old set cannot clear its refresh annotation either: its
reconcile fails at the refused delete. So the W-43 waits do not work as written in this state, and the recovery has its
own order:

1. Freeze the tenants identities (W-43 section 2).
2. Decide per stuck Application whether the flip is wanted. For one that is not, revert `spec.clearanceGate` on the
   ApplicationEnvironment (not `identity.yaml`: the composition writes its own value back). With (b) in Deny that is a
   gate change too, so open the hub half for it, then close it again. The old set generates the Application again and
   its error clears; nothing moves.
   If stuck Applications go both ways (one flipped in, another flipped back), each set fails on the other's Application
   and neither drain below can finish. Revert one direction's flips first, as above, and recover the other. Redo the
   reverted flips afterwards as a normal handover.
   When every remaining stuck Application goes the same way, record `main` of the tenants repo (`git ls-remote`) as `M`
   and check its identities say what is intended.
3. Open the target half of the window, and check both sets show `create-update`. The move needs no hub half: it changes
   no ApplicationEnvironment.
4. The revision-cache wait. C.3's script does not fit: it waits for `main` to become the flip commit, and later commits may
   have landed. Instead, check `main` is still `M`, sleep the bound from W-43 C.3 (git timeout + expiry, 180 s on
   hangar-dev), and check `main` is still `M`. Any change stops the recovery. `M` was pushed before step 1, so a bound
   timed from now covers it.
4b. Then C.1's wait for **the old set only** (`bash -s -- tenant-onboarding`, or `tenant-onboarding-gated` for a flip
   back). Under `create-update` the old set no longer tries the delete, so its reconcile finishes and clears the
   annotation. The new set keeps failing with `already owned` until the move; that is expected, and why it is left out.
5. The move: C.4 for a flip into the gated set; for a flip back, D.3's opt-out first, then D.4.
6. C.5's second guard (the sleep from the move, C.1's wait for both sets, the owner check). A reconcile that read an older
   identity can put the old owner and source order back after the move; (d) refuses its later delete, not that update.
7. C.6's check, close the window, lift the freeze.

Rehearse this on the throwaway in section 5, step 2, and write it into the W-43 plan as its own section (slice S6).

- Lives: apron (the tenant-onboarding chart, next to the two ApplicationSets it names). It is plain Argo CD and Kubernetes:
  nothing in Clearance or Airframe.
- Blast radius: only DELETE requests by one ServiceAccount, on Applications two named sets control. People, the Argo CD
  application controller and the garbage collector are not matched.
- Fail-closed is safe. Any error refuses the controller's delete of an Application, the safe direction.
- Covers every path in section 1: XR flips, re-creates, hand edits, a selector bug, a bad tenants-repo commit that removes
  identities. It also covers the stale-reconcile races in W-43 C.3 to C.5: a set that took the reference back can no longer
  delete.
- Not covered: deleting a whole ApplicationSet (the garbage collector deletes its Applications, and the tenant-onboarding
  finalizer cascades: W-43 section 6, a separate decision).
- Cost: removing an environment on purpose needs one more step. Today it is already by hand (the identity is deleted in the
  tenants repo: decommission-app.md). With (d), the operator also deletes the Application. Until then `tenant-onboarding`
  shows `ErrorOccurred`.
- If the policy is missing, or names the wrong ServiceAccount, it does nothing and we are back to today. Tests and a live
  check catch the wrong name (section 6).

## 3. Recommendation

Build **(d) first, then (b)**. Not (a). Not (c) yet.

- (d) is the floor. It stops the deletion itself, on the cluster where it happens, whatever caused it. It needs no copy of
  the window. Small, and all in apron.
- (b) is the guard the brief asks for. It refuses the flip at the source, with a clear message, so an app owner cannot start
  a handover no operator is ready for. With (d) on, a wrong window flag costs a stuck handover, not a workload.
- Keep `gatedSetHandover` (`create-update`) as it is. It is a second layer, and the W-43 steps stay valid.

What each side owns:

| Piece | Side |
|---|---|
| (d) VAP and binding, the ServiceAccount name, the two set names | apron (Hangar) |
| (b) VAP and binding | Airframe (ships with the XRD); apron installs it on the control-plane cluster |
| (b) param ConfigMap `clearance-gate-handover` and `airframe.clearanceGateHandover` | Airframe `charts/cluster-registry`, from the fleet's `clusters.yaml` |
| Window procedure, rehearsal | hangar `specs/plans` (this note, W-43) |
| Clearance | nothing. If (c) is built later, only the generic handover-peer contract in section 2 |

## 4. The window: who opens and closes it

The window has two halves. The target half is what Argo CD obeys. The hub half is what (b) reads.

| Half | Where | Field |
|---|---|---|
| target | the target cluster's gitops repo, `cluster.yaml` | `clearance.gate.agent.gatedSetHandover: true` |
| hub | the fleet's `clusters.yaml` (gitops-hangar-dev) | `airframe.clearanceGateHandover: true` on that cluster's record |

The owner opens and closes it on both clusters. Both halves are owner-merged PRs. The `cluster-registry` Application is
manual sync by design ("a registry change is attested by a person"), so opening the hub half is a deliberate act. The app
owner asks for the flip, and makes it in Tower or a PR, only while it is open.

Open, in this order:

1. Target: merge `gatedSetHandover: true`, sync, run W-43 C.1's drain wait (`ok`, exit 0).
2. Check for refused flips waiting to land: any `xr-requests` Application with a failed sync naming this policy. They land
   in step 3.
3. Hub: merge `airframe.clearanceGateHandover: true`, sync `cluster-registry` by hand.
4. The app owner flips. The operator follows W-43 C.2 to C.5.

Close, in reverse:

1. Hub: remove the field, sync `cluster-registry`. No new flips from here.
2. W-43 C.6's ownership check (`ok`, exit 0, no `ErrorOccurred`).
3. Target: remove `gatedSetHandover`.

With (d) in Deny, getting the order wrong is not destructive: the worst case is a stuck handover that C.4 finishes. Without
(d), step 1 before step 3 is what keeps a flip from deleting, as W-43 says today.

CEL has no clock, so a window cannot expire by itself. See open question 6.

## 5. Rollout (audit first)

1. (d) on hangar-dev with `validationActions: [Audit]`, about a week. Expect no audit events: in normal operation the
   controller never deletes a tenant Application. Any event is a real deletion (Audit does not refuse): read it.
2. (d) to `[Deny]` on hangar-dev. Live check on the W-43 throwaway: a bare flip with the window closed. Expect the
   Application kept (same uid, no `deletionTimestamp`), `tenant-onboarding` `ErrorOccurred` `DeleteApplicationError`, the
   workload uids unchanged. Finish with C.4. This is the flip W-43 section 4 could not rehearse; with (d) it is safe to.
3. (d) on hangar-prod: Audit, then Deny, the same way. hangar-prod has no gated environment yet.
4. (b) on hangar-dev with `[Audit, Warn]`. A flip with the window closed gets a warning and still goes through, so try it
   only once (d) is in Deny. Check the warning reaches Tower and the `xr-requests` sync.
5. (b) to `[Deny]`. Live check: a flip with the hub half closed is refused, with the message; with it open, allowed.
6. Docs as each step lands (slice S6).

Rollback of either: set the binding back to `[Audit]`, or delete the binding. Nothing else depends on them.

## 6. Tests

(d), apron `tests/appset` (the real controller on envtest, kube-apiserver 1.36.2; envtest runs VAPs). The test's controller
user stands in for the ServiceAccount (the username is a render parameter):

- a bare flip outside the window: the Application is kept (same uid, no `deletionTimestamp`, finalizer still on); the set has
  `ErrorOccurred` `DeleteApplicationError`; the other environments are still updated;
- the reverse bare flip: the same, from the gated set;
- the W-43 handover (window, C.4 move) still passes, and so does the handover back (D.3, D.4);
- an identity removed: refused for the controller; a delete by another user succeeds;
- an Application controlled by another ApplicationSet: its delete is allowed;
- an Application with no `ownerReferences`, or one with no `controller` field: not matched, no CEL error.

(d), apron `tests/run.sh`: the policy renders with `gatedSet` (and always, if open question 2 says so); the ServiceAccount is
the one argocd-apps-install renders; every match condition field is has()-guarded (the breakglass lint).

(b), Airframe CI, server-side dry runs against an API server with the XRD, the policy and the param:

- UPDATE `false` to `true` and back, window closed: refused; window open: allowed;
- the cluster missing from the param, and the param missing: refused;
- an alias name: follows its record;
- CREATE with `true`, window closed: refused (if open question 3 says so); CREATE with `false` or no field: allowed;
- writes that do not flip: allowed. A label, a finalizer, `spec.crossplane`, a `chart` change, a re-apply without the field
  (the default makes it `false`);
- the status subresource: never matched.

`airframe` `tools/test_xr_validate.py` already lints the field type; no change there.

Live: the checks in section 5, steps 2 and 5.

## 7. Work slices

| Slice | What | Repo | Size |
|---|---|---|---|
| S1 | W-43 checkout completeness check (section 8) | hangar (this PR) | XS, done here |
| S2 | (d): VAP and binding in the tenant-onboarding chart, ServiceAccount from the argocd-apps render, `tests/appset` and `tests/run.sh` cases | apron | S |
| S3 | (d) rollout on hangar-dev, then hangar-prod: Audit, Deny, the live bare-flip check | gitops-hangar-dev, -prod | S |
| S4 | `airframe.clearanceGateHandover` in `charts/cluster-registry` (field, the `clearance-gate-handover` ConfigMap, chart tests) | airframe | S |
| S5 | (b): VAP and binding, CI dry-run tests; apron installs it on the control-plane cluster | airframe, apron | M |
| S6 | Docs: apron README "Gated environments"; airframe `clearanceGate` description and `decommission-app.md` (delete the Application by hand); the W-43 plan (what (d) makes safe) | apron, airframe, hangar | S |
| S7 | (b) rollout: Warn, then Deny, live check | gitops-hangar-dev | XS |
| later | (c): agent moves the controller reference between handover peers | clearance, apron | M to L |

Order: S1, S2, S3, then S4, S5, S7. S6 rides with each.

## 8. Folded in: the tenants checkout must be complete (hangar#148, CodeRabbit Minor)

Both W-43 scripts that read the tenants checkout `T` (step A's scan, C.6's ownership check) checked the commit but not the
working tree. A sparse checkout, or an index entry marked skip-worktree, hides identities from `find`. The scan would then
say `none gated` for what it can see, and step A could delete a hidden gated identity's Application.

Both scripts now stop, right after the HEAD check, when:

- `core.sparseCheckout` is true (a config read that fails, other than "unset", also stops);
- `git ls-files -v` lists any entry not tagged `H`: skip-worktree (`S`), and any lowercase tag (assume-unchanged, where an
  edited file shows clean to `git status`), among others;
- `git status --porcelain` is not empty (a tracked identity deleted in the working tree would also be missed).

The W-43 plan carries the exact lines. They were run against five scratch clones (full, sparse, one skip-worktree
entry, one assume-unchanged entry edited in place, one identity deleted in the working tree): `ok` and exit 0 on the full clone, `STOP` and exit 2 on each of the others.

## 9. Open questions for the owner

1. **Accept (d), which changes how an environment is removed?** After deleting its identity, an operator also deletes its
   Application by hand. Until then `tenant-onboarding` shows `ErrorOccurred`. *Recommendation: yes. Removal is already by
   hand, and an unattended delete with a cascading finalizer is the risk we are closing.*
2. **(d) only on clusters with `gatedSet`, or on every tenant-onboarding?** *Recommendation: every cluster, always. It also
   stops a bad tenants-repo commit from deleting many workloads at once. It needs no gate to be on.*
3. **Should (b) refuse a CREATE with `clearanceGate: true` while the window is closed?** It catches the re-create case (a kept
   `identity.yaml`). It also makes a brand-new gated environment wait for a window. *Recommendation: yes. Gated environments
   are few, and (b) cannot tell a new environment from a re-created one.*
4. **Where does the hub half live?** A field in `clusters.yaml`, rendered by the cluster-registry chart, or a hand-made
   ConfigMap. *Recommendation: `clusters.yaml`. It is person-attested and manual-sync already, and it stays in gitops (no
   hand-made objects).*
5. **Keep `gatedSetHandover` once (d) is in Deny?** *Recommendation: keep it. It costs nothing, and it is the layer that
   still holds if the policy is removed.*
6. **A window left open.** CEL has no clock, so it cannot expire. *Recommendation: none in v1. Later, an Ops Wall check that
   flags a hub half open for more than 24 hours.*
7. **(c), the agent moving the reference?** *Recommendation: not now. Revisit after two real handovers with (d) on. If built,
   use the generic handover-peer contract (section 2), with no Hangar names in Clearance.*
8. **Tower.** Should the `clearanceGate` toggle be disabled while the target's hub half is closed? *Recommendation: yes,
   later (a read of the param ConfigMap). The VAP message is the floor until then.*
9. **(b) with its param missing: refuse every ApplicationEnvironment write, or allow every flip?** The API server resolves the
   param before the match conditions, so there is no "refuse flips only". *Recommendation: refuse (`Deny`), with the param
   always rendered. A missing param is then a visible, quickly fixed write stop that deletes nothing. `Allow` fails open
   without a sign; with (d) on it would still not delete, but (b) would guard nothing.*
