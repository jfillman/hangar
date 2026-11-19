# One switch for Clearance's Argo CD gate

Written 2026-11-18. Strip W-35, owner decision Y-27 ("implement part 1"). Status: design note, nothing applied.
Facts below were read from apron, clearance, airframe and gitops-hangar-prod at origin/main on 2026-11-18, plus one
read of hangar-prod's namespaces. Line numbers are at that state.

## The goal

Turning the Argo CD gate on or off for one app and environment should be one platform-owned edit, not four lists and a
regex. The fact must not be settable from a tenant's own repo, must fail closed, and must leave a record when it is
turned off.

## What the work found first (this changes the plan)

The strip assumed admission, the agent and the observer each select protected namespaces from a list. They do not.

1. **Admission already selects by label.** `clearance-protected-writes` matches `namespaceSelector: clearance.hangar.io/protected=true`
   (apron `templates/56-clearance-gate/admission.yaml:18-20`). No list is involved. Nothing to change.
2. **The agent already finds protected namespaces by label** (`providers/argocd/agent/kubeapi.go:157-172`, selector
   `clearance.hangar.io/protected=true`). Its `protectedNamespaces` list is something else: the set of namespaces it holds
   RBAC for. The chart renders one Role per entry and a Namespace `get`/`patch` limited by `resourceNames`
   (`charts/clearance-argocd-agent/templates/rbac.yaml:30,94`). RBAC cannot select on labels.
3. **The observer's list is names the API server needs.** `protectedNamespaces` feeds per-namespace watch Roles
   (`charts/clearance-observe-k8s/templates/_helpers.tpl:19`, `rbac.yaml:73`) and the kube-apiserver audit policy
   (`providers/observe-k8s/auditpolicy/policy.go:88,103`). An audit policy rule matches namespace names only, and it is a
   file on the control-plane node. It cannot select on labels either.
4. **Nothing in any repo puts the label on a namespace.** I found `clearance.hangar.io/protected` only in
   `admission.yaml` in gitops-hangar-prod. On hangar-prod now, `app-gate-api-prod` has it with managers
   `kubectl-label`, `argocd-controller` and `external-secrets`; `app-backstage-prod` has it too. Neither has the agent's
   `protected-by` marker. So today the label is set by hand, once per namespace, and that hand step is a fifth place that
   must agree with the four lists. The agent can label namespaces itself, but only through the annotation opt-in
   (G-ARGO-10c, `docs/gate.md:2106`), which apron does not turn on (`optIn` is not in
   `templates/56-clearance-gate/agent/application.yaml`).

So "make the consumers select by label, in addition to the lists" would be a no-op for admission and would need wider
RBAC for the agent and observer (see Options below). The real cost is that apron takes four inputs and one hand step for
what is one decision. The design fixes that at the source.

## Today's flow

Per app and environment, the gate is turned on by:

| # | Where | What it holds | Consumer |
|---|---|---|---|
| 1 | `cluster.yaml` `clearance.gate.apps` (gitops-hangar-prod `cluster.yaml:46`) | app names | `hack/render.py:492,511` renders `CLEARANCE_GATE_APP_REGEX`; ApplicationSet `templatePatch` (`applicationset.tmpl.yaml:193-194`) swaps the Helm source for the `clearance` plugin source when app regex and env regex both match |
| 2 | `clearance.protectedEnvironments` (`cluster.yaml:41`) | `<cluster>/<env>` globs | `render.py:465-466` renders `CLEARANCE_GATE_ENV_REGEX`; the same `templatePatch` line; also the Map publisher (`render.py:781`) |
| 3 | `clearance.gate.agent.projects` (`cluster.yaml:49`) | Argo CD project names (= app names) | agent chart `argocd.projects` (`agent/application.yaml:31`, `render.py:518`) |
| 4 | `clearance.gate.agent.protectedNamespaces` (`cluster.yaml:50`) | `app-<app>-<env>` | agent chart RBAC and opt-in scope (`agent/application.yaml:32`, `render.py:519`); Map target gates (`render.py:768,785`) |
| 5 | `clearance.observe.protectedNamespaces` (`cluster.yaml:54`) | `app-<app>-<env>` | observer chart (`57-clearance-observe/application.yaml:28,55`), audit policy, Map observers (`render.py:613,767`) |
| 6 | the namespace label, by hand | `clearance.hangar.io/protected=true` | admission |

The regexes in 1 and 2 are a product, not a pair: app `a` is gated in every environment the env regex matches.
gitops-hangar-prod PR 50 ("Take flight-api out of the Clearance Argo gate") shows the cost of one app: a `cluster.yaml`
edit in three places and a render that changed three more files (`applicationset.tmpl.yaml`, `agent/application.yaml`,
`59-clearance-targets/publisher.yaml`). It deliberately left list 5 alone, which is why the audit collector still watches
a namespace the gate has let go.

How the pieces meet at runtime:

- The tenant-onboarding ApplicationSet reads `tenants/*/*/identity.yaml` (`applicationset.tmpl.yaml:100`), written by
  Airframe's `ApplicationEnvironment` composition (`tenant-identity-yaml.yaml:63-79`: `appName`, `gitopsRepoUrl`,
  `githubOwner`, `env`, `type`, `runtime`, `configMapGenerator`, and `chart` from the app's `cicd.yaml`). Every value comes
  from tenant-controlled input.
- The destination namespace is `__DESTINATION_NAMESPACE__` (`applicationset.tmpl.yaml:172`), `app-<app>-<env>`. It is
  created by the chart's own Namespace object (airframe `charts/airframe-application/templates/namespace/namespace.yaml`,
  labels from `namespace.labels`), with `CreateNamespace=true` (`:190-191`) as a fallback. The platform injects
  `namespace.labels` through the Helm `valuesObject` (`:122-125`) and, for the plugin source, `valuesJson` (`:219`), which
  wins over the tenant's value files.
- The per-app AppProject is generated from the coarser `tenants/<app>/identity.yaml`
  (`tenant-appprojects/applicationset.yaml:2-8`) and is shared by all of an app's environments.
- Clearance already has a tenant-side opt-in: the Application annotation `clearance.hangar.io/protect: "true"` (G-ARGO-10c,
  built, not deployed). Anyone who can edit the Application can opt out (`docs/gate.md:2165`); the opt-out is reported to the
  core before it takes effect, and a pair the core's `CLEARANCE_PROTECTED_ENVIRONMENTS` lists stays protected.
- The core keeps its own floor: `CLEARANCE_PROTECTED_ENVIRONMENTS`, rendered from `clearance.protectedEnvironments`.

## Target

One fact per app and environment: **protected**. It is a pair in one platform list, and everything else is derived from it:

```yaml
# cluster.yaml (platform gitops repo, rendered by apron)
clearance:
  gate:
    protect:            # replaces gate.apps, gate.agent.projects, gate.agent.protectedNamespaces
      - {app: gate-api,  env: prod}
      - {app: backstage, env: prod}
```

apron derives from it, by the namespace pattern it already uses (`APP_NAMESPACE`, `render.py:700`):

- the ApplicationSet condition, as a pair test instead of two regexes: `has (printf "%s/%s" .appName .env) (list ...)`;
- the agent's projects and protected namespaces;
- the observer's namespaces (plus a separate `observe.extraNamespaces` for namespaces watched but not gated, so PR 50's
  "collector still watches flight-api" stays expressible);
- the Map targets' `g-argo` gate.

And it stamps two labels:

- `clearance.hangar.io/gate: enabled` on the generated Application and on the destination namespace. It means "the platform
  asks for this to be gated". The Application label comes from the ApplicationSet template. The namespace label comes from
  `namespace.labels` in `valuesObject`/`valuesJson` (airframe-application charts), and from `managedNamespaceMetadata` for a
  chart that renders no Namespace.
- `clearance.hangar.io/protected: "true"` stays what enforces. It is not stamped by apron: admission refuses every matched
  write in a labelled namespace with no active grant, so the label must follow the grant (`docs/gate.md:464`,
  `protect.go:26-28`). The agent sets it once the namespace's grant is active, which replaces the hand `kubectl label`.

Two labels are needed because one cannot be both a request and an enforcement state. With a single label stamped at
namespace creation, a new protected namespace would refuse the first sync's own writes in Deny mode.

## Where the fact lives: options

**A. `identity.yaml`, written by Airframe.** Add `gate: true` to `tenants/<app>/<env>/identity.yaml`. The ApplicationSet
already reads the file, so the template change is small and the fact is per app and per environment.
Against: every field in that file derives from tenant input through the `ApplicationEnvironment` XR, and the tenants repo
is written by Crossplane's GitHub provider and is pushable by whoever holds that token or the repo. To be platform-owned the
composition would have to read an Airframe-side platform setting, not the XR, and gating is a per-cluster fact that Airframe
does not otherwise know. A change spans airframe, a release, and a hand backfill of every existing identity.yaml in the
tenants repos. A tenant who can edit the file turns their own gate off. This is the option the strip's target warns against.

**B. A label on the AppProject.** Argo CD scopes projects and the agent already filters on projects.
Against: the AppProject is per app, not per environment, and is generated from the coarser `tenants/<app>/identity.yaml`
(same tenant-influenced source as A). dev and prod of one app cannot differ. It also cannot carry the namespace label.

**C. A platform-side list keyed by app and environment that renders to labels (recommended).** The `protect` list above, in
`cluster.yaml`, which only the owner changes (prod gitops PRs are merged by the owner). It is already where the four lists
live, it is per cluster (right, since gating is a per-cluster fact), and apron's render already fans one input out to several
files. No tenants-repo change, no Airframe change, nothing tenant-controlled.
Against: it is still a list that someone edits per app, and it is not the data an ApplicationSet generator reads, so the
ApplicationSet carries the pair list inside its `templatePatch` (rendered at apron time, as the regex is now). It is a single
list and the render is checked, which is what the owner asked for. "Never a hand edit of a generated Application" holds: the
Application is generated from the template and the pair list in it.

Recommendation: C.

## Who may change it, and how that is enforced

- **Who:** the platform owner, by a reviewed change to `cluster.yaml` in the cluster's gitops repo, then an apron render.
- **Not from the tenant:** the tenant's repos hold no input to it. identity.yaml keys named `gate`/`protected` are ignored by the
  template (the condition reads the rendered list, never `.gate`). `valuesObject`/`valuesJson` win over tenant value files, so a
  tenant values file cannot set `namespace.labels` over the platform's. `apron check` refuses a `protect` entry that is not a
  DNS-label app and env, and refuses a cluster with the old keys and `protect` both set.
- **At the cluster:** add a ValidatingAdmissionPolicy on Namespace UPDATE that refuses any change to `clearance.hangar.io/gate`
  and `/protected` unless the user is the agent's service account, or the platform Argo CD that applies the gitops repo.
  The tenant Argo CD instance (argocd-apps) applies the tenant's own Namespace, so it is the one writer this must stop. This is
  clearance work (an addition to `providers/argocd/crd/admission.yaml`, kept in step with apron's render).
- **Recorded:** the agent reports the protected pair set to the core already (`PUT /v1/protection/{cluster}`,
  `protect.go:20-28`) and the core records a removal as `protection.report`. Today that runs only for annotation opt-ins. It
  must also run for pairs the agent sees from the `gate=enabled` label, so that dropping a pair from `protect` produces a
  record naming the pair and the reason (the label left). The label is removed only after the core took the report
  (`protect.go:296-303`); if the core is unreachable the namespace stays protected.

## How each consumer selects

| Consumer | Selects on | Change |
|---|---|---|
| Admission | `protected=true` namespace label (as now) | none |
| ApplicationSet `templatePatch` | the pair list rendered into the condition (replaces `CLEARANCE_GATE_APP_REGEX` and `_ENV_REGEX`) | apron |
| Agent, finding work | `gate=enabled` namespaces, within its RBAC ceiling; sets `protected=true` after the grant | clearance |
| Agent, RBAC ceiling | derived from `protect` by apron (still names; RBAC cannot select on labels) | apron |
| Observer, scope | derived from `protect` plus `observe.extraNamespaces` (still names: audit policy and Roles) | apron |
| Observer, check | lists namespaces by `gate=enabled`, compares with its configured set, posts an exception on a difference | clearance |
| Map publisher | derived from `protect` | apron |

Selecting by label for the RBAC ceiling and the audit policy would require the agent to hold `patch` on every Namespace and
the observer to list and watch workloads cluster-wide, and the audit policy would have to record everything. That widens
what a compromise of either component reaches, for the sake of one fewer derived list. This note does not recommend it
(open decision 1).

## Failure modes

- **Plugin source removed, namespace still `protected=true`:** the platform Argo CD applies unstamped objects, admission
  refuses them (Deny), or warns (Warn, which is the mode hangar-prod runs today). Fail-closed already holds in Deny. This
  is why the label, not the ApplicationSet, is the enforcement point.
- **`gate=enabled` but no `protected=true` yet:** a window of up to the agent's pass (30 s) after a new namespace and its
  grant exist. Not enforced in it. The observer check flags a namespace that stays in this state past a bound.
- **`protected=true` but no `gate=enabled`:** a hand label, or a pair dropped from `protect`. The agent leaves a label it
  has no marker for (`protect.go:346`), so the hand labels already on prod survive. The observer check posts it as drift.
- **Core unreachable when a pair is dropped:** the removal waits, the namespace stays protected, the agent says so in its
  status.
- **Chart renders its own Namespace without the label:** the platform's `valuesObject` label covers airframe-application;
  for another chart the `managedNamespaceMetadata` path and the Namespace-label policy above are the backstop. The
  observer check also catches it.
- **App in the list but not in the agent's RBAC:** impossible by construction, both come from `protect`. A chart/version
  mismatch (new apron, old agent chart) is caught by `apron check`, which already ties `gate.agent` to the pins.
- **Map and Argo disagree:** both derive from `protect`, so they cannot.

## Migration with no gap in protection

The rule: the new input produces exactly the old output before anything is removed, and additive labels come before any
reader depends on them.

1. **apron PR 1 (additive).** Add `clearance.gate.protect`. When present it is the source; when absent the old keys apply
   unchanged. When both are set, `apron check` requires that they derive the same sets. Stamp `gate=enabled` on the
   Application and the namespace. Tests: the render of the old keys and of the equivalent `protect` are byte-identical
   apart from the new labels. No cluster change until a cluster adopts the key.
2. **clearance PR (additive, after 1).** The agent labels `protected=true` from `gate=enabled` once the grant is active, and
   reports the pair set from the label so a removal is recorded; the observer check; the Namespace-label policy; docs. Off
   by a chart flag, so it is deployed before it is used. Needs the clearance release and the new image digest pinned in
   apron, which is a separate apron change.
3. **gitops-hangar-dev, then gitops-hangar-prod (owner).** Replace the four keys with `protect`, render, and require
   the diff to be only the two new labels. Merge. Then the owner sets the agent flag on and confirms the agent labelled
   (or adopted) each namespace. The existing hand labels have no marker, so the agent keeps them.
4. **apron PR 2.** Remove the old keys: `apron check` refuses them with a message pointing at `protect`. Only after
   both clusters have moved.
5. **Airframe, tenants repos:** no change under option C. If the owner picks A later, they come first (compose, release,
   backfill), then the rest.

No step lowers protection: the old and new inputs derive the same namespaces, the label is added before it is read, and the
agent never removes a label it did not apply.

## What the owner does by hand

- Merge the apron PRs, and the gitops-hangar-dev and gitops-hangar-prod pull requests (prod: owner only).
- Pin the new Clearance image digest and chart version in `cluster.yaml` once released.
- On hangar-prod, check after the cutover that `app-gate-api-prod` and `app-backstage-prod` carry both labels. The
  hand labels stay until the owner decides to let the agent own them (the agent needs the marker, which a label it did not
  apply lacks; removing the label and letting the agent re-add it makes it the owner).
- Nothing in the tenants repos or Airframe under option C.

## Open decisions for the owner

1. Keep the RBAC ceiling and audit-policy names as derived lists (recommended), or widen the agent and observer to
   cluster-wide reads so they can select by label (not recommended).
2. Two labels (`gate` as the request, `protected` as the enforcement), recommended, or one.
3. Pair semantics: `protect` as explicit app+env pairs (recommended), or keep an app list times an environment list.
4. Where `clearance.protectedEnvironments` (the core's floor and the Map's enforce/flag) and `protect` meet. Today a pair
   in `protect` for an environment the floor does not list is protected only by the agent's report. Recommend `apron check`
   refuses `protect` entries outside `protectedEnvironments`, or derives the floor.
5. The annotation opt-in (G-ARGO-10c) and apron's template switch are two ways to put an Application on the plugin. This
   design uses the template for ApplicationSet-made Applications and leaves the annotation for Applications not made by
   ApplicationSet. Say if you want one of them retired.

## First PR, and why it is not in clearance

The suggested first PR was a clearance change to select by label in addition to the lists. Admission already does. The agent
and observer could not follow it without the RBAC and audit-policy widening in decision 1, which is the owner's call. So
there is no clearance PR yet. The smallest safe first PR is apron PR 1 above (additive key and labels, byte-identical
render), which touches the prod render path and the apron repo's checks; it was not part of this task. Clearance's part
(agent labelling and removal records, step 2) follows once decisions 1 and 2 are made.
