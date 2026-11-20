# Where an SLO requested through xr.request should live

Written 2026-11-19. Strip W-44. Status: design note, no code, nothing applied. The owner picks an option later.

Facts were read from three repos at `origin/main` as of the last fetch on this machine: autopilot `09158e1`, apron
`d4e9487`, airframe `dc5ffa6`. The local checkouts of apron and airframe were behind, so every citation below is to
`origin/main`, not to the working tree. Nothing was run against a cluster. Where this note could not confirm something,
it says "To confirm".

## Terms used below

- **The gateway.** The Autopilot gateway's Go service, which serves the `xr.request` tool.
- **xr.request.** The tool that turns an agent's request into an XR file committed under
  `tenants/<app>/xr-requests/` in the tenants repo, as a pull request.
- **The xr-requests ApplicationSet.** apron's `xr-requests` ApplicationSet. It makes one Argo CD Application per app
  directory and applies the XR files from the tenants repo.
- **cicd namespace.** `app-<app>-cicd`, the app's control-plane namespace. (The suffix is `cicd` on the control plane
  and `xrs` elsewhere: `templates/TOKENS.md:101`.)
- **Environment namespace.** `app-<app>-<env>`, where the app's workload and, from the chart, its SLOs live.
- **The SLO composition.** Airframe's Crossplane composition for the `SLO` kind (`compositions/slo/`), which renders a
  Sloth `PrometheusServiceLevel`.
- **Tenant scope.** The rule that an SLO may read only its own namespace's metrics.

## The problem

Three facts that do not fit together.

1. **xr.request writes every XR for the app's cicd namespace.** The gateway stamps `namespace: app-<app>-cicd` on the
   XRs it builds (`gateway/internal/airframe/plan.go:504` and `:511`), and for an XR with no namespace the ApplicationSet
   supplies the same one (`airframe/capabilities.go:99`). The ApplicationSet's destination is
   `<type>-<app>-<suffix>` (`templates/02-argocd-apps/xr-requests/applicationset.yaml:127`), and an XR file that sets its
   own `metadata.namespace` wins over it (`:125`).
2. **The SLO composition scopes its queries to the XR's own namespace.** It reads `metadata.namespace`
   (`compositions/slo/templates/prometheusservicelevel.yaml:51`), requires it to be a valid namespace name (`:69`),
   refuses any `namespace` or `__name__` matcher from the tenant (`:86`), and forces `namespace="<that namespace>"` into
   every selector (`:91`, used at `:97-:101`). The comment on the rule says the namespace is "an environment namespace,
   app-NAME-ENV, where the chart puts it and where the tenant's RBAC ends" (`:68`). The chart does put it there: the
   `slos:` template sets `namespace` to the release namespace (`charts/airframe-application/templates/attached/slos.yaml:9`,
   `_helpers.tpl:5-7`).
3. **So an SLO from xr.request would read nothing.** Its series carry `namespace="app-<app>-<env>"`, and the query would
   demand `namespace="app-<app>-cicd"`. Autopilot PR #118 therefore refuses kind `SLO`: `xrrequest.go:348-350`, with the
   message at `:925` and the hint at `:926-928` that points users to `slos:` in
   `gitops-<app>/<cluster>/<env>/values.yaml`. The matcher checks for SLOs are kept behind `sloRequestsOpen = false`
   (`xrrequest.go:915-922`; documented at `docs/admin/go-gateway.md:980`).

A fourth fact the refusal text does not mention: **the xr-requests Argo CD project does not allow SLOs at all.** Its
`namespaceResourceWhitelist` lists the catalog kinds explicitly (`appproject.yaml:66-125`) and the header says the
Attached-tier kinds, SLO among them, "are deliberately NOT meant to go through xr-requests/"
(`appproject.yaml:50-53`). The project's destinations are only `app-*-cicd` and `infra-*-cicd`
(`appproject.yaml:40-43`). So even a correctly namespaced SLO XR would be refused at sync today. Any option that lets
xr.request place SLOs has to touch apron.

One more constraint on the request itself: xr.request takes an `env` and accepts only lower environments, `dev`,
`pr-*` and `agent-*` (`xrrequest.go:337-340`). So the gateway already knows which environment an SLO is for.

Also worth knowing: the XR's `environmentRef` is, in the XRD's words, "Labeling/audit only - not a live lookup"
(`xrds/slo.yaml:75-88`). Nothing in the composition reads it for scope today.

## Option 1. Place the SLO XR in the environment namespace

### What changes

There are two ways to do it, and the owner may want only the first.

**1a. Same ApplicationSet, XR names its own namespace.** The ApplicationSet already lets an XR's `metadata.namespace`
win over its default (`applicationset.yaml:125`). So:

- autopilot: for kind `SLO`, stamp `namespace: app-<app>-<env>` (the gateway has `app` and `env`), flip
  `sloRequestsOpen` on, update the refusal docs and tests.
- apron: add `SLO` to the project's `namespaceResourceWhitelist` and add destinations for the environment namespaces
  (`appproject.yaml`). The rule to keep: these destinations never reach a staging or production namespace, for any
  permitted app name. Globs such as `app-*-pr-*` do not keep it on their own, because `*` can span hyphens: an app
  named `x-pr` with environment `prod` lives in `app-x-pr-prod`, which `app-*-pr-*` matches. So either the
  destinations are exact names written per app and environment (rendered from the tenant list), or a stated naming
  rule, enforced at tenant onboarding, stops app names from containing an environment token (`-pr`, `-agent`,
  `-dev`, `-staging`, `-prod`). Until one of those exists, use exact names. The ApplicationSet itself does not change.
- airframe: nothing is needed for the composition, which already expects this placement. A small contract note (which
  namespace an SLO request is placed in) would keep the gateway's vendored contract honest. To confirm whether the
  contract has a field for it.

**1b. A per-environment path and Application.** Files go under `tenants/<app>/xr-requests/<env>/` and a second
ApplicationSet (or a matrix of app and env) renders each into `app-<app>-<env>`. The current source only includes
`xr-requests/*.yaml` (`applicationset.yaml:117-120`), so a subfolder needs a new include and a new generator. It sets the
Application's default destination from the path; an XR's own `metadata.namespace` still overrides it (see below). The cost is a second ApplicationSet to keep in step with the first, and
an Application per environment.

### Tenant isolation and security

The tenant-scope rule does not change: the SLO is still scoped to its own namespace, the one thing a tenant cannot
choose from inside the SLO spec. The new exposure is the destination widening in the AppProject. That project already
holds cluster-scoped Namespace rights and the Crossplane kinds, and its cicd destinations are already globs over every
app (`appproject.yaml:40-43`). Widening to `app-*-dev` and friends lets an XR file in one app's directory name another
app's dev namespace. I found nothing in apron that checks that a file's `metadata.namespace` matches its directory; the
control is review of the tenants-repo pull request. To confirm whether any admission check (Kyverno or Argo) ties them.
The invariant needed is: a file in one tenant's directory can never land in a namespace of another app. 1b alone
does not establish it. The ApplicationSet lets an XR's own `metadata.namespace` win (`applicationset.yaml:125`), so a
file under `<app>/xr-requests/dev/` can still name another app's namespace, and the shared AppProject's globs would
let it through. 1b closes the gap only with an enforcing control: per-app AppProjects whose destinations are that
app's own namespaces (Argo CD refuses the sync; this stops cross-app placement but not a file naming
another environment of the same app), or an admission or CI check that rejects a file whose namespace does
not match its path. Neither exists today. Until one does, the gap stays open under 1a and 1b alike, and PR review is
the only control.

The namespace must exist when the sync runs. `CreateNamespace=true` (`applicationset.yaml:149`) creates only the
destination namespace, and a missing XR namespace failed a sync before (`applicationset.yaml:51-54`, the skyport-auth
case). Who creates `app-<app>-<env>` and when is not something I confirmed. To confirm; if environment namespaces come from
tenant onboarding, a request for an environment that is not yet onboarded fails its sync, which is the right outcome.

### Effect on clusters already deployed

Existing apps and their chart-made SLOs are untouched: no existing XR moves. The AppProject change reaches every cluster
that renders the apron template, and the header says prod carries "a narrower copy of this file"
(`appproject.yaml:62-65` area), so each cluster's copy needs the change on its own schedule. A cluster that does not
take it simply keeps refusing: the gateway would open a pull request whose sync Argo rejects. So the gateway change
should wait until the dev cluster has the project change, or check for it.

### Effort

1a: small. A gateway change with tests, one AppProject edit, a live rehearsal on dev (request an SLO for a test app,
see it Ready, see the query return data). About one to two days. 1b: add roughly two more days for the
ApplicationSet, its generators, and tests for rename and delete behaviour (the existing one has a documented deletion
deadlock history, `applicationset.yaml:160-179`).

## Option 2. The composition scopes by environmentRef

### What changes

The SLO would stay in the cicd namespace and the composition would derive the scope from `environmentRef.name` instead
of `metadata.namespace`.

- airframe: rewrite the scope block (`prometheusservicelevel.yaml:68-91`). `environmentRef` is only a name today
  (`xrds/slo.yaml:75-88`), and an ApplicationEnvironment XR sits in the cicd namespace (xr.request writes those files
  into `xr-requests/`, `plan.go:910-913`), so a bare name does not carry the environment namespace. The composition would
  have to look the ApplicationEnvironment up (a required-resource lookup plus the RBAC for it) and compute `app-<app>-<env>`
  from it. The `<xrName>_<namespace>` Sloth name and the dashboard queries (`composition.yaml:133-169`, and
  Tower's `selectorFor`, named in the comment at `prometheusservicelevel.yaml:166-169`) also key on the XR's namespace
  and would need the environment instead, or two environments' SLOs in one cicd namespace collide.
- apron: still needed. The whitelist still lacks `SLO` (`appproject.yaml:50-53`), so this option is not Airframe-only.
- autopilot: flip `sloRequestsOpen`, update docs.

### Tenant isolation and security read

This is the option that changes the rule, and the question asked was whether a tenant can then reach another tenant's
or another environment's metrics. Answer: not safely as stated, and only with extra checks.

- **Today's rule is unforgeable from inside the XR.** The namespace is metadata Kubernetes and Argo CD control, not a
  field the tenant types. `environmentRef.name` is a tenant-typed string with no check. If the composition trusted it,
  an SLO could name another app's ApplicationEnvironment and read that app's series. The composition would have to
  verify that the referenced environment belongs to the same app as the XR's own namespace. The cicd namespace carries no
  `hangar.io/app` label, but the mapping from app to `app-<app>-cicd` is injective, so the app can be read from the
  name (`gateway/internal/airframe/state.go:136-138`). That check is doable, but it is new security-critical logic in a
  Go template, in a path where known gap 11 already lists weaknesses (`docs/admin/known-gaps.md:14`).
- **Another environment of the same app.** The cicd namespace holds XRs for every environment of the app. Any tenant
  who can write an SLO for the app can then point it at any of the app's environments, including ones whose RBAC they
  lack today (the chart-made SLO is bound to one environment namespace and its RBAC). xr.request only does lower
  environments, but nothing in the XRD stops a hand-written `environmentRef` naming `prod`. The lookup would need to
  refuse that, which duplicates a rule xr.request enforces only in the gateway (`xrrequest.go:337-340`).
- **It works against the recommended hardening.** Known gap 11 says to set `enforcedNamespaceLabel` on the Prometheus
  resource so prometheus-operator injects the rule's own namespace into every expression
  (`known-gaps.md:14`). With the rule living in the cicd namespace and the series in an environment namespace, that
  injection would make every such SLO read nothing. Option 2 and the planned fix cannot both be true.
- **The cicd namespace has different guards.** It gets `managed-secrets` and Pod Security `baseline`
  (`applicationset.yaml:138-146`); the PrometheusServiceLevel and PrometheusRule objects would land there, mixed with
  CI resources.

### Effect on clusters already deployed

The composition ships to every cluster. Every existing SLO, made by the chart in an environment namespace, would be
re-rendered by the new scope logic. If it computes anything other than the same namespace, every existing SLO's
queries change at once. It needs a rollout that proves no query text changes for existing SLOs, per cluster.

### Effort

The largest: composition rewrite with a lookup, RBAC, new tests in `compositions/slo/example/cases.yaml`, Tower and
dashboard changes, the apron whitelist, a security review, and a live check on dev. Roughly four to six days, and it
leaves the Prometheus-level hardening blocked.

## Option 3. Keep SLOs chart-only

### What changes

Nothing in code. Keep the refusal, keep `slos:` in `gitops-<app>/<cluster>/<env>/values.yaml` as the only way
(`xrrequest.go:926-928`). Optionally delete the dead matcher code behind `sloRequestsOpen`, or leave it for later.

### Tenant isolation and security

None changed. Tenant scope stays as written at `prometheusservicelevel.yaml:68-91`, and the AppProject keeps SLO out on
purpose (`appproject.yaml:50-53`). This is the only option that adds no new way to reach metrics.

### Effect on clusters already deployed

None.

### Effort

Hours, for docs and a clearer refusal hint. The cost is not code: an agent cannot create an SLO in one step. It has to
open a pull request on the app's gitops repo, which is not the tenants repo the gateway writes to. Whether the
agent has a tool for that repo is not something I checked. To confirm.

## Comparison

| | Tenant scope rule | Repos touched | Existing clusters | Effort |
|---|---|---|---|---|
| 1a. XR names the environment namespace | unchanged | autopilot, apron | AppProject change per cluster; no SLO moves | 1 to 2 days |
| 1b. per-environment path | unchanged; path sets the destination only with a namespace check | autopilot, apron | same, plus a second ApplicationSet | 3 to 4 days |
| 2. scope by environmentRef | weakened; needs a same-app check | airframe, apron, autopilot | every SLO re-rendered | 4 to 6 days |
| 3. chart-only | unchanged | none | none | hours |

## Recommendation

Choose option 1a, with the AppProject destinations kept to exact lower-environment names (or patterns backed by an
enforced naming rule), and keep option 3 as the
behaviour until the dev cluster has the project change. It leaves the tenant-scope rule alone and works with the
`enforcedNamespaceLabel` hardening that known gap 11 recommends, where option 2 does not. Move to 1b only if the owner wants
the destination derived from the path, and then only together with a control that rejects a file whose namespace does
not match its path (an admission or CI check). Per-app AppProjects would confine a file to its own app's namespaces
but not to the environment its path names; this depends on the answer to question 1.
Option 2 is the one to avoid: it trades a rule the platform enforces for a string the tenant types.

## Open questions for the owner

1. **Who may name a namespace in an XR file?** Under 1a an XR file in one app's directory can name another app's
   `app-*-dev` namespace, and only pull request review stops it. Is that acceptable, or do you want a control that enforces it (per-app AppProjects, or an admission or CI check that
   ties the namespace to the path), with or without 1b?
2. **Which environments?** xr.request is lower-environments-only. Should SLOs be requestable in `dev`, `pr-*` and
   `agent-*`, or in `dev` only? It sets the AppProject destination list.
3. **Do you want agent-made SLOs to survive their environment?** An `agent-*` or `pr-*` environment is ephemeral. Its
   SLO XR would be pruned with it. Is that wanted, or should SLOs there be refused?
4. **Option 2 at all?** If you want it anyway, should the composition refuse any `environmentRef` that is not a lower
   environment of the same app, and are you willing to give up `enforcedNamespaceLabel`?
5. **Interim.** Until a change ships, is the refusal text enough, or should the gateway tell the agent which tool opens a
   pull request on the gitops repo? (Needs the answer to the "to confirm" under option 3.)
6. **Cluster rollout.** Prod carries a narrower copy of the AppProject. Should prod take the SLO change at all, or stay
   chart-only?

## What the owner does by hand

- Choose an option and answer the questions above.
- If option 1: review and merge the autopilot and apron pull requests, and the gitops change that brings the AppProject
  to each cluster (prod: owner only).
- Nothing in the tenants repos, and nothing on any cluster, was changed by this note.
