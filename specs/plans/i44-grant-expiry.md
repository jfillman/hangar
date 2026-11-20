# I-44: an expired ClearanceGrant can still let a write through

Written 2026-11-20. Design note only: nothing here is built, and no cluster was touched. Owner review first.
Read at clearance `494ff0f` (origin/main). Paths are in that repo. Kubernetes facts were read from the
`k8s.io/apiserver` v0.37.2 source (the version the repo's CEL cost spike already uses); anything that needs a live
API server is marked **Unverified**.

## 1. The defect

Admission policy `clearance-protected-writes` (`providers/argocd/crd/admission.yaml`) admits Argo CD's controller
only when the namespace's one active grant has `status.valid == true` and lists the object at its `rendered` hash,
in its own `objects` or in a `carried[]` entry. It never reads `spec.expiresAt`, `objects[].expiresAt` or
`carried[].expiresAt` (the CRD says so in each description). Expiry reaches admission only because the agent
(`providers/argocd/agent/grants.go`, `expireGrants`, every 30 s) flips `status.valid` to false, removes the active
label, and drops expired `carried` entries and merged-grant objects.

So the gate is correct only while the agent is alive and writing. If the agent crashes, is evicted, loses its
RBAC, hits a bug in the pass, or the API server rejects its writes after it marked a grant valid, every write the
grant covers keeps passing, indefinitely, after expiry. Today both bindings are `[Warn, Audit]`, so nothing is
blocked; this matters when `clearance.gate.enforce` flips to Deny.

## 2. Is there any clock CEL can see? (rigorous)

The environment a VAP expression gets (`pkg/admission/plugin/cel/compile.go`, `BuildRequestType`): `request`
(kind, resource, subResource, name, namespace, operation, userInfo, dryRun, options), `object`, `oldObject`,
`params`, `namespaceObject`, `variables`, `authorizer`. No timestamp field, and the CEL libraries in
`pkg/cel/library` (authz, cidr, ip, jsonpatch, lists, quantity, regex, semver, urls, format) have no `now()`.
Each candidate proxy:

| Candidate | Verdict |
| --- | --- |
| `object.metadata.creationTimestamp` | **Real clock, CREATE only.** `Store.create` calls `rest.BeforeCreate` (which runs `FillObjectMetaSystemFields`, `meta.SetCreationTimestamp(metav1.Now())`, always overwriting what the client sent) and only then `createValidation`, which is where the VAP runs (`pkg/registry/generic/registry/store.go:569-575`). So on CREATE, `timestamp(object.metadata.creationTimestamp) < timestamp(params.spec.expiresAt)` is a sound expiry check. On UPDATE (and every Argo re-sync is a PATCH, so an UPDATE) the field is the original creation time and says nothing about now. Covers the minority of writes only. |
| `managedFields[].time` | Not usable. The writer picks the manager name, the time moves only when the managed field set changes (a no-op re-apply keeps the old one), and it is a CEL-visible field only by accident of the object schema. Unsound. |
| `params` (a grant, ConfigMap or lease the agent refreshes) | Admission reads it as stored. A refreshed `observedAt`, `validUntil` or "time bucket" is data the same dead agent stops refreshing, and CEL has nothing to compare it to. A heartbeat is only checkable against a clock; without one it is the same as `status.valid`. |
| A time-bucket label and `paramRef.selector` | The binding selects params by label, so a label like `window=2026-11-20T10` looks like a clock. The binding is static, and something must rewrite the label each window: the agent again. |
| `authorizer.check(...)` | Asks the SubjectAccessReview chain. RBAC and node authorizers are time-free; only a webhook authorizer has a clock, which is option 1 with extra steps. |
| `request.userInfo` / token expiry | The API server does enforce token expiry on its clock, but nothing ties Argo's token to the grant's `expiresAt`; the projected-token minimum (10 min) and rotation make it unfit. |
| TTL-after-finished (Jobs), owner-reference GC | Built-in clock-driven deletion exists only for Jobs and needs kube-controller-manager plus a Job per grant. A VAP `paramKind` cannot be a Job; abuse for no gain. Rejected. |

Conclusion: **no CEL-visible clock exists for UPDATE.** Anything that enforces expiry on an UPDATE needs either an
actor that changes stored state at expiry (today's agent, with the stall defect), or a component that has a clock
at request time (a webhook). A purely in-VAP fix cannot be complete.

## 3. Options

| # | Option | Closes I-44? | New fail-closed dependency | Blast radius | Cost | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Status quo plus HA agent (2 replicas, leader lease, PDB) and an alert on `status.checkedAt` age | Narrows (needs both replicas to fail), does not close | No | None | Low | Do as hardening, not as the fix |
| 1a | Purpose-built expiry webhook, separate small Deployment, informer on grants, compares each matching entry's expiry to its own clock | **Yes**, every operation | Yes: the webhook for protected-namespace Argo writes | Argo controller's CREATE/UPDATE in `protected=true` namespaces only | Medium: Go service, chart, TLS | **Recommended** |
| 1b | Same check in the agent's own process | Yes | Yes, and it makes the agent's up-time a deploy dependency, the same agent whose stall is the bug | Same | Low | Rejected: couples the check to the thing that fails, and adds a listener to a credential-holding pod |
| 1c | Kyverno ValidatingPolicy with `time.now()` (the spike `docs/spikes/g-argo-1/prod/31-kyverno.yaml` already does `time.now() < timestamp(...expiresAt)`) | Yes | Yes: Kyverno | Fine-grained webhook, but dev saw 16 of 30 calls refused when Kyverno's admission controller was down (restarts on dev and prod) | Low | Rejected: `docs/gate.md` already decides "a Kyverno outage must not decide whether a protected sync can land" |
| 2 | Agent-written `status.validUntil` window, compared in CEL | No: nothing to compare to (section 2) | No | None | Low | Not sound |
| 2' | CREATE-only clock in the VAP: `timestamp(object.metadata.creationTimestamp) < timestamp(params.spec.expiresAt)` | Partial: CREATE only | No | None | Tiny | Optional defence in depth; **Unverified** live (a dry-run create with a past `expiresAt` would show it). **Intentionally stricter than section 4:** it tests only the grant's own `spec.expiresAt`, so it also refuses a CREATE that a still-unexpired matching `carried[]` entry would allow once the grant itself has expired (the grant is then due for expiry by the agent anyway, and the webhook, not this row, is the exact check) |
| 3 | Heartbeat or Lease checked by admission | No (same as 2) | No | None | Low | Not sound |
| 4 | Params, authorizer, token expiry, TTL GC | No (section 2) | n/a | n/a | n/a | Rejected |

## 4. Recommendation: 1a, a narrow clock gate beside the VAP

Keep the VAP exactly as is (state, hashes, one active grant: in-process, 1 ms, no new availability dependency).
Add one **ValidatingWebhookConfiguration** `clearance-grant-expiry` served by a new tiny Deployment
(`clearance-grant-expiry`, 2 replicas, PDB `minAvailable: 1`, topology spread) whose only job is the clock:

- Decision: for the admitted object's key `<group>/<kind>/<name>` and `rendered` stamp, find the namespace's active
  grant (informer cache, labels `clearance.hangar.io/active=true`). Allow only if some entry that **lists the key at
  that hash** is unexpired: the grant's own `objects[key]` (and, on a merged grant, its `objects[key].expiresAt`) when
  `spec.expiresAt` and that object expiry are in the future, or a `carried[]` entry that lists the key at the hash with
  its `expiresAt` in the future. It must mirror the VAP's matching, otherwise an expired matching entry would be
  rescued by an unexpired non-matching one. It never grants anything: it can only refuse, and both it and the VAP must
  pass.
- Fail closed on the narrowest scope the API allows. `failurePolicy: Fail`, `timeoutSeconds: 3`,
  `sideEffects: None`, `matchPolicy: Equivalent`, `namespaceSelector: clearance.hangar.io/protected=true`,
  operations CREATE and UPDATE, `scope: Namespaced`. A `ValidatingWebhookConfiguration` has no `excludeResourceRules`
  (that field belongs to the policy's `matchResources`), so the VAP's exclusions (clearancegrants, events, endpoints,
  endpointslices, leases) are expressed as `matchConditions` instead, so the agent can bootstrap and the control plane keeps
  writing: `!(request.resource.group == 'clearance.hangar.io' && request.resource.resource == 'clearancegrants')`,
  and the same for `events`, `endpoints`, `endpointslices` and `leases` with their own groups, each `has()`-guarded. A test
  per exclusion proves the webhook is not called for it, and that a normal resource is. The other `matchConditions` copy the VAP's, every expression `has()`-guarded:
  `has(request.userInfo) && has(request.userInfo.username) && request.userInfo.username == '<argocd controller>' &&
  (!has(request.subResource) || request.subResource == '')`. A CEL error in a match condition is a cluster-wide
  refusal under `Fail` (hangar's 2026-10-29 lesson), so each has() guard gets a unit test with objects missing the
  field. Net blast radius: Argo's controller writing to a protected namespace; nobody else, no other namespace.
- Audit-safe rollout, mirroring `validationActions`: an `--mode=audit|enforce` flag. In audit the webhook always
  allows, returns a warning and an audit annotation (`clearance.hangar.io/expired-grant`), and the configuration is
  `failurePolicy: Ignore`. Apron renders `mode` and `failurePolicy` from one switch, `clearance.grantExpiry.enforce`
  (default off: the webhook configuration is not rendered unless `clearance.grantExpiry.enabled`).
  **The VAP's Deny may only follow it.** `failurePolicy: Fail` refuses only an unreachable webhook, not a successful allow,
  so an audit-mode pod that is still serving would let an expired grant through after the VAP went to Deny. Ordering
  that closes it: (1) the Deployment rolls to `--mode=enforce` and every replica is Ready, its readiness reporting the
  mode it runs (a pod still in audit is not Ready in the enforce rollout); (2) only then the configuration becomes `Fail`
  (the Deployment sits in an earlier Argo wave than the configuration, and the configuration in an earlier wave than the VAP binding; a
  later wave starts only after the earlier wave is healthy, so `Fail` takes effect only once the pods are Ready); (3) only then `clearance.gate.enforce` turns the VAP to Deny. The Clearance chart owns this rule (a template `fail`; it installs on its own), and Apron's `hack/check.py` mirrors it: both refuse
  `clearance.gate.enforce: true` unless `clearance.grantExpiry.enforce: true` and `enabled: true`, which also stops an enforce flip
  with the webhook off (otherwise the VAP would deny other invalid writes yet still admit writes covered by an expired
  grant). The one exception is an explicit, recorded override, `clearance.grantExpiry.acceptResidualRisk: true`, that the
  owner sets knowingly; without it the render fails.
  **Leaving enforce runs in the reverse order**, and the check enforces it: `clearance.gate.enforce` goes back to Warn first (the VAP
  stops denying), and only in a later change may `clearance.grantExpiry.enforce` go to false (the webhook returns to audit and
  `Ignore`). The check refuses a render where the webhook is not in enforce while the VAP is, and the Argo waves apply the
  webhook's change after the VAP binding's on the way down, so no moment has the webhook in audit with expired grants passing
  under a still-Deny VAP.
- Why this fixes the stall: expiry no longer depends on any process having written anything. A dead agent leaves
  the VAP's stored state stale but the webhook still compares each entry to the clock and refuses. A dead webhook
  closes the gate for protected namespaces (the intended direction), which is also what "no active grant" already
  does under Deny, so it adds no new kind of outage to those namespaces.
- Keep: the agent's `expireGrants` unchanged. The webhook is a backstop; the agent still keeps the grant, label and
  display state tidy and `status.valid` honest.
- Optional, cheap: option 2' in the VAP for CREATE (defence in depth, no dependency). Verify live before relying on it.

Tests the build slice would carry (Go, table-driven): own-object expired / unexpired, merged-grant per-object expiry,
carried entry expired while an unexpired non-matching entry exists, grant expired with a valid `status.valid: true`
(the I-44 case), no active grant, two active grants, missing `expiresAt` or unparsable time (refuse), skew
(`--skew` default 0), audit mode allows with a warning, every match-condition guard with the field absent, plus an
envtest-free replay of `test_admission.py` cases against the webhook handler.

## 5. Owner decisions

1. **Accept a new fail-closed dependency** for Argo writes in protected namespaces at enforce time, or accept the
   residual and rely on option 0 (HA agent plus a staleness alert). This is the blocker: it is why no Clearance PR
   accompanies this note. Recommended: accept, 2 replicas.
2. **Host**: separate Deployment (recommended), inside the agent (1b), or Kyverno (1c; contradicts the standing gate
   decision). 
3. **TLS for the webhook**: cert-manager `Certificate` plus CA injection, or a self-managed CA rendered by Apron. This
   overlaps I-43 (TLS), which another session is working; the webhook should reuse whatever I-43 settles and must
   not invent a second scheme. Clearance must install on its own (no Apron or Hangar dependency in the product
   feature), so the chart needs a built-in path, with Apron only supplying values.
4. **Enforce-time failurePolicy and timeout**: `Fail` with 3 s (recommended; `Ignore` reopens I-44 whenever the
   webhook is down) and whether `timeoutSeconds` may be 10 like Kyverno's.
5. **Gate on the Deny flip**: make "I-44 closed or explicitly accepted" a precondition of `gate.enforce: true` on
   hangar-prod.
6. **Clock skew allowance** (default none; entries expire on the webhook pod's clock, same as the agent's today).
7. Whether to ship option 2' now (decision-free, but only CREATE).

## 6. Not verified

No live cluster was used. Unverified: that option 2' behaves as the source read says on a real API server; the
webhook's latency under Argo's sync bursts (budget: Kyverno averaged 0.5 to 1.2 s, a Go informer lookup should be
milliseconds); that Apron can render the second configuration from the one `enforce` switch.
