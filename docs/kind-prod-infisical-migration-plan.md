# kind-prod: migrate to the new airframe pin and retire the Infisical operator

Status: **Phases 1-2 done; Phase 3 done except the credential** (2026-09-23); Phases 4-5 not started. Written from live
inspection of kind-prod, the airframe tags, and the upstream Terraform provider.

## The short version

Bumping kind-prod's airframe pin does **not** retire the operator. Every SecretStore
on kind-prod uses **universal auth** (it isn't the cluster that hosts Infisical), and at
v0.3.77 that branch still renders the *old* `InfisicalProject` CR on purpose. The new
provider-infisical chain only exists for the kubernetes-auth branch (kiac-dev).

The reason was a failure in `IdentityUniversalAuthClientSecret`'s Observe. **The
first diagnosis in this plan was wrong**, corrected after reproducing it live:
it is not an upstream SDK bug. Infisical's GET-by-id endpoint returns a single object
(checked in the server source); only the LIST endpoint returns an array. Before Create,
this resource's external name is empty, and upjet seeds the Terraform state with
`id = <external name>` and refreshes anyway. The Terraform provider's Read then calls
`.../client-secrets/` with an empty id, which *is* the LIST endpoint, and fails
unmarshalling the array. Reproduced on kiac-dev with a throwaway chain (error text in
the commit message).

**Fixed in our own provider, no fork.** `GetIDFn` seeds a well-formed id that cannot
exist (the nil UUID) whenever the external name is empty, so Read hits the by-id
endpoint, gets a 404 and reports "not found". Only the pre-Create state is affected;
the real id replaces it on Create. `provider-infisical` commit `b220ec2`, published as
`v0.0.0-7.gb220ec2` (multi-arch index: amd64 + arm64), running on kiac-dev.

So the work is four things in order: ~~fix the provider~~ (done), write the universal-auth branch
of the SecretStore Composition, install the provider on kind-prod, then cut apps over
one at a time.

## What is on kind-prod today

| | Count | Notes |
|---|---|---|
| `InfisicalProject` CRs | 6 | boarding-api, checkout-api, order-api, process-api, search-api, and `platform-cicd-kind-prod` (project `platform-cicd-kind-prod-v2`, in `platform-secrets`) |
| `InfisicalEnvironment` CRs | 9 | checkout-api ×4 (`staging`, `pre-prod`, `prod`, `proofing`), order-api ×2, boarding-api `staging`, process-api and search-api `prod` |
| `ClusterSecretStore`s | 15 | all `Valid`, `Ready` |
| Operator | 1 pod | `infisical-secretstore-operator`, reads `INFISICAL_ADMIN_TOKEN` from `infisical-bootstrap-secret`, talks to `dev.kiac.local:31800` |
| Crossplane packages | provider-kubernetes, provider-helm; 3 functions | **no provider-infisical** |
| Catalog pin | `idp-service-catalog` at v0.3.69 (SLO, SecretStore, RolloutWatch) | Redis added separately at v0.3.77 this session |

Architectures: kind-prod is **amd64**; the provider package must be multi-arch (it is;
the Dockerfile picks the upstream Terraform provider zip by `TARGETARCH`).

## Phase 0 — Before touching anything

1. **Verify the backups yourself, per project.** You said backup projects exist. Before
   each cutover, compare secret counts, paths and key names, live project vs its backup
   (the same check kiac-dev used), and take a local export as well. A backup nobody has
   diffed is a hope.
2. **Confirm what a lost secret would mean.** ESO copies values into ordinary Kubernetes
   Secrets, so running pods should survive a period where Infisical or a store is broken.
   That is expected behaviour, **not yet verified on this cluster** — check one
   ExternalSecret's `deletionPolicy` (default `Retain`) before relying on it.
3. **Pick a window.** checkout-api runs `prod`, `pre-prod`, `proofing` and `staging`
   here. It goes last.

## Phase 1 — Fix the provider — DONE

Verified live on kiac-dev, 2026-09-23:

- Reproduced the Observe failure with a throwaway `Identity` → `IdentityUniversalAuth`
  → `IdentityUniversalAuthClientSecret` chain.
- Shipped the `GetIDFn` fix (with a unit test that the override survives provider
  setup), published, bumped the pin in `gitops-cluster-dev`.
- Same chain after the upgrade: all three `Synced` and `Ready`.
- The credential authenticates: a universal-auth login with the produced client id and
  secret returns HTTP 200 and an access token.
- The chain deletes cleanly (namespace and all three resources gone).
- The provider restart left all 10 existing Infisical `Project`s Ready and Synced.

**What the Composition must know** (from the live result): the client secret is in the
managed resource's connection secret under the key **`attribute.client_secret`**; the
**client id is not** — it is in `IdentityUniversalAuthClientSecret`'s
`status.atProvider.clientId`. The credentials Secret has to be assembled from both.

**Not yet proven:** the amd64 build (kiac-dev is arm64). The published package index
contains both, and Phase 3 is where amd64 actually runs.

**Upstream:** the fix turned out to be ours, so there is nothing to send to
`terraform-provider-infisical` for *this* problem. If you want a defensive upstream
change anyway (Read treating an empty id as not found), say so and I'll draft it; I
won't post it without your say.

## Phase 2 — Composition (airframe) — DONE

Shipped as airframe **v0.3.79** (`70a3385`, on main); kiac-dev's catalog pin is bumped
to it.

**What it does.** On a universal-auth cluster the SecretStore Composition renders the
provider chain — `Project`, `ProjectEnvironment`, `Identity`, `IdentityUniversalAuth`,
`IdentityUniversalAuthClientSecret`, `ProjectIdentity` — plus the same
`<slug>-infisical-creds` Secret (`clientId`, `clientSecret`) the operator writes, so the
ClusterSecretStores are unchanged. The client id is read from the client-secret
resource's `status.atProvider.clientId`; the secret from its connection Secret
(`<slug>-ua-conn`, key `attribute.client_secret`).

**How the opt-in works** (a change from the design sketched earlier): not an XRD field.
kind-prod's SecretStore XRs are files the ApplicationEnvironment Composition re-commits
with `Update` in its policies, so a hand-added field would be reverted. Instead the
Composition reads an optional ConfigMap, `crossplane-system/secretstore-provisioner`,
one key per project slug:

```yaml
data:
  boarding-api-kind-prod: |
    provisioner: provider
    projectId: <existing project uuid>        # optional: adopt in place
    sharedEnvId: <existing shared env uuid>   # optional
    envIds: {staging: <existing env uuid>}    # optional
```

No ConfigMap, or no key for a slug, keeps the operator. The three id fields set
`crossplane.io/external-name` so the provider observes the existing object rather
than creating a colliding one. Adoption is **untried against a real project** — Phase 4
proves it on boarding-api. The Infisical host cluster (kiac-dev) always uses the
provider, no entry needed.

**Verified**
- Offline render with Go's real `text/template`, six scenarios: kiac-dev renders the
  same resource set as before; a universal cluster with no entry renders only the
  operator CR; an opted-in one renders the full chain; the credentials Secret appears
  only once *both* the client id and secret exist; adoption ids appear as external
  names; the per-env XR follows the same switch.
- Live on kiac-dev, throwaway XR for a non-host cluster, opted in: every resource
  `Ready`, the XR `Ready`, the credentials Secret has both keys, and **logging in with
  the Composition-assembled credentials returns HTTP 200 and a token**.
- Teardown: XR, all six managed resources, the ClusterSecretStore and the credentials
  Secret all removed.
- Regression: the 10 real SecretStores on kiac-dev unchanged and `Ready` after the bump.

**Not verified**
- ESO actually reading a secret through the new store. The throwaway's
  ClusterSecretStore could not be exercised: ESO on kiac-dev cannot resolve
  `dev.kiac.local` (the known pod-DNS gap; kind-prod's existing stores resolve it and
  are `Valid`). ESO did read the assembled Secret and attempted the universal-auth login
  against the right path. The real end-to-end read happens on kind-prod in Phase 4.
- Crossplane logged `WatchCircuitOpen` ("too many watch events") on the throwaway during
  its first build, then went `Ready`. Watch whether it recurs on a real XR.

Exit gate met: tagged release; renders the universal chain for a throwaway XR on
kiac-dev; still renders the operator CR for everything else.

**Still to do in this area** (Phase 5): `platform-cicd-kind-prod`. It is a raw
`InfisicalProject` CR in `gitops-cluster-kind-prod/10-crds-operators/external-secrets/`,
not a SecretStore XR, so it needs converting to one before the operator can go.

## Phase 3 — Install on kind-prod — DONE, except the credential

**Installed and verified (2026-09-23)**

- `provider-infisical` v0.0.0-7.gb220ec2 is **Healthy on kind-prod's amd64 node** — the
  first time this package has run on amd64. Own `DeploymentRuntimeConfig`, with the same
  `dev.kiac.local` → `192.168.1.78` `hostAliases` the operator and ESO already carry
  (bump all three together if that LAN address changes). `ClusterProviderConfig` present,
  applied through a sync-wave after the Provider installs (as provider-helm's was).
- **Reachability:** a kind-prod pod with that alias gets HTTP 200 from
  `http://dev.kiac.local:31800/api/status` in ~70 ms.
- **RBAC:** checked with `auth can-i`, nothing to add. provider-kubernetes can manage
  Secrets in app namespaces; Crossplane can read them (needed for the two ExtraResources
  lookups).
- **Catalog pin** moved v0.3.69 → v0.3.79, with Redis folded into the same Application
  (the temporary `idp-service-catalog-redis` Application is gone; its XRD and Composition
  survived and are now tracked by the main one). The tenant ApplicationSet pins were
  **not** moved: the `airframe-application` chart is byte-identical from v0.3.76 to
  v0.3.79, so there is nothing to take.
- **Default behaviour proven unchanged**, two ways. Offline: v0.3.69's and v0.3.79's
  SecretStore templates rendered against kind-prod-shaped XRs (shared and per-env) give
  identical resources once comments and the new lookups are set aside. Live, after the
  sync: all 14 SecretStores, 15 ClusterSecretStores and 28 ExternalSecrets show
  identical state; all 15 operator CRs are the same objects (none recreated); no
  provider-infisical resource exists yet.

**The one open item — the credential.** The provider is idle until this exists. It is
created by hand, on purpose: kiac-dev delivers its copy through an ExternalSecret out of
an Infisical project, but on kind-prod the only candidate project is
`platform-cicd-kind-prod-v2` — one this provider will itself recreate or adopt. A
credential stored inside a project its own consumer is about to change is a lockout.

The operator's `infisical-bootstrap-secret` will **not** work: it holds a raw admin
`token`, and the provider needs a universal-auth machine identity. So:

1. In Infisical, create a machine identity for kind-prod (suggested name
   `provider-infisical-kind-prod`, so it can be revoked independently of kiac-dev's),
   with universal auth, the same organization role as kiac-dev's provider identity (it
   must be able to create projects, identities and memberships), and a client secret.
2. Create the Secret yourself. Do not paste it in chat or commit it:

   `kubectl --context kind-prod -n crossplane-system create secret generic provider-infisical-creds --from-file=credentials=<file>`

   where the file holds `{"host": "http://dev.kiac.local:31800", "client_id": "...",
   "client_secret": "..."}`. (`host` differs from kiac-dev's, which uses the in-cluster
   Service.) Delete the file afterwards.

Exit test once it exists: a throwaway `Identity` → `IdentityUniversalAuth` →
`IdentityUniversalAuthClientSecret` chain on kind-prod reaches `Ready` and logs in, then
deletes cleanly — the Phase 1 test, this time on amd64 against the real path.

## Phase 4 — Cut over, one app at a time

Order: `boarding-api` (newest, one staging env, fewest secrets) → `search-api` →
`process-api` → `order-api` → `checkout-api` → `platform-cicd-kind-prod`.

Per app: re-verify the backup → flip that XR to `provider` → let the chain go
`Ready` → repoint stores → verify ExternalSecrets refresh and pods are healthy →
verify secrets key-for-key against the backup → only then remove the old CR.

**Decision needed — how the project survives:**

| | Destroy and restore | Adopt in place |
|---|---|---|
| How | Delete the old CR (the operator's `on_delete` deletes the Infisical project), new chain recreates the slug, restore from backup | Scale the operator to zero, strip the CR finalizer so the project is left alone, give the new `Project` the existing project id as its external-name |
| Proven | Yes — kiac-dev, 8 projects, zero loss | **No** — untried; Terraform import of a project is supported but not exercised here |
| Risk | Secrets are briefly gone; relies entirely on the backup | Identity name collisions; a mistake in the finalizer step can still delete the project |
| Recommendation | Fallback | Try on `boarding-api` first; keep destroy-and-restore if it misbehaves |

Whichever you pick: the old operator's identities/credentials are replaced either way,
so a new client secret is issued per app. Crossplane will **not** garbage-collect the
old object for you — delete it by hand, one resource at a time (kiac-dev lesson 3).
If a managed resource sticks, annotate it with a new value to force a requeue instead
of restarting the provider (which re-Observes everything at once).

## Phase 5 — Retire the operator on kind-prod

Only when `kubectl get infisicalprojects,infisicalenvironments -A` is empty and every
store is `Ready` via the new chain:

1. Remove the `infisical-secretstore-operator` Application from
   `gitops-cluster-kind-prod` (its CRDs, RBAC, Deployment).
2. Retire `infisical-bootstrap-secret` in favour of the provider's credential.
3. Delete the two CRDs; confirm nothing else referenced them.
4. Later, in airframe, delete the operator-CR branch of the Composition and the
   `operators/infisical-secretstore-operator/` source.

The shared items the kiac-dev migration had to split out first (token reviewer,
NodePort) belong to kiac-dev's Infisical, not kind-prod's operator, so this phase has
no equivalent.

## Rollback

- **Phases 1–3** are additive: remove the provider and Application; nothing depended
  on them.
- **Phase 4** is per-app: flip the XR back to `operator`, restore the project from its
  backup. This is why the backup diff comes first and why apps go one at a time.
- **Phase 5** is not reversible without redeploying the operator; don't start it until
  every app has been stable through a full release cycle.

## Open questions

1. ~~Fork and patch~~ — not needed; fixed in our provider config.
2. **Adopt in place, or destroy and restore?** Decided: try adopt in place on
   `boarding-api`, fall back to destroy and restore.
3. ~~Backups~~ — verified by you.
4. **`kiac-man` and kind-man's separate operator copy** — both are gone per the current
   cluster list, so their repos need no migration; confirm.
5. **Timing.** checkout-api runs a real `prod` environment on this cluster.
