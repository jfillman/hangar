# kind-prod: migrate to the new airframe pin and retire the Infisical operator

Status: **All five phases done** (2026-09-23). Every kind-prod Infisical project is provider-managed and the infisical-secretstore-operator is retired on kind-prod. Remaining follow-ups are listed under Phase 5. Written from live
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

## Phase 3 — Install on kind-prod — DONE

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

**The credential — done.** (Kept below as the record of how it was set up.) The Secret
was created with `--from-file=<path>/provider-infisical.creds` and so its key is
`provider-infisical.creds`, not `credentials`; the `ClusterProviderConfig` reads that key.

**Exit test passed on kind-prod (amd64):** a throwaway `Identity` → `IdentityUniversalAuth`
→ `IdentityUniversalAuthClientSecret` chain went `Ready`, logging in with its credentials
returned HTTP 200 and a token, and it deleted cleanly (no managed resources left).

**Original note on the credential.** The provider is idle until this exists. It is
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

Order: `boarding-api` (done) → `search-api` → `process-api` → `order-api` →
`checkout-api` → `platform-cicd-kind-prod`.

### boarding-api — DONE, adopted in place (2026-09-23)

**Result.** The Infisical project and both environments (`shared`, `staging`) kept their
original ids; nothing was destroyed or recreated. Verified:

- A canary secret written into the `shared` environment before the flip was still there
  after adoption. (boarding-api's project held 0 real secrets, so this was the only data
  test available.)
- ESO read that canary through the store's new credentials — a real ExternalSecret,
  `SecretSynced`, value matched. That closes the "ESO reading through the new store"
  item Phase 2 could not test on kiac-dev.
- After the old operator identity was **deleted**, both ClusterSecretStores stayed
  `Valid` and a second canary read still worked, so the stores can only be on the new
  credentials.
- Both SecretStore XRs `Ready`; the other 13 SecretStores, all 15 ClusterSecretStores
  and the ExternalSecrets are identical to the pre-change baseline.

### search-api, process-api, order-api — DONE, adopted in place (2026-09-23)

Same runbook, run once per app with an identical automated verification. Every check
passed for all three:

- the chain and every SecretStore XR for the app `Ready`;
- project and environment ids unchanged;
- **secret fingerprints identical** — a SHA-256 of every secret value, taken before and
  compared after, so the data is proven byte-identical without displaying any of it
  (search-api 0 secrets, process-api 0, order-api 1 — its `prod` secret);
- an ESO read of a canary through the new store credentials;
- the old operator CRs deleted with the project and fingerprints untouched;
- the old operator identity deleted, then a **second** canary read still working, so the
  stores can only be on the new credentials.

The provider identity had to be `admin` on each project first (granted by hand for these,
confirmed by reading its membership); the fleet — SecretStores, ClusterSecretStores,
ExternalSecrets — matched its baseline after each batch.

### checkout-api — DONE, adopted in place (2026-09-23)

The `prod` app, done last and on its own. Five environments (`shared`, `staging`,
`proofing`, `pre-prod`, `prod`); real secrets in `prod` and `proofing`. Every check passed
— chain and all five SecretStore XRs `Ready`, ids unchanged, **both secrets
byte-identical by fingerprint** before, after the flip and after the old CRs were
deleted, an ESO canary read through the new credentials, the old operator identity
deleted and a second read still working. The running `prod` ExternalSecrets
(`app-secrets`, `platform-outcome-relay-token`, `registry-credentials`) stayed
`SecretSynced` throughout, and the whole fleet matched its pre-change baseline.

Two of the steps drew permission-guard blocks (one was reported as a transient
classifier error); the flip was carried out after explicit authorization and a retry, and
the operator was restored to one replica afterwards.

### platform-cicd — DONE (2026-09-23), and not what the plan assumed

The plan said this was "a raw `InfisicalProject` CR that needs converting to a SecretStore
XR". Reading it live showed a different problem: **the CR was managing the wrong project.**

- The CR provisioned `platform-cicd-kind-prod-v2`, a fresh project created after the
  original became unreachable (its own header explains why). It was **empty** and nothing
  read it.
- `platform-secret-store` — which feeds ~27 ExternalSecrets cluster-wide (GitHub App keys,
  registry credentials, the Anthropic key, Backstage tokens) — has always read the
  **original** `platform-cicd-kind-prod`, 14 secrets, with credentials for an older
  operator-made identity that no CR any longer owned. The two had drifted apart; the store
  file's own header says they "must carry the same projectSlug", and they did not.

So the target was the original project, not `-v2`. What was done, in order (each its own
commit, so a half-applied state could not collide):

1. ConfigMap entry `platform-cicd-kind-prod` adopting the original project and its
   `shared` environment by id — synced and confirmed live **before** anything else. Without
   it the Composition would have rendered the operator CR, whose name would have collided
   with the raw CR.
2. A SecretStore XR (`platform-secrets/platform-cicd-kind-prod`; slug
   `<appRef.name>-<cluster>` is exactly the original slug). The provider adopted the
   project and environment under their original ids and minted a new identity; the raw CR
   was left untouched.
3. Verified before repointing anything: project and environment ids unchanged, **all 14
   secrets byte-identical by fingerprint**, and the new identity able to read all 14.
4. `platform-secret-store` repointed at the new credentials Secret. Forcing every
   dependent ExternalSecret to re-read left **all 27 `SecretSynced`**.
5. The old identity deleted, then the same forced re-read again — still all 27 synced and
   the store `Valid`, so nothing depends on the old credentials.
6. The dead `platform-cicd-infisical-creds` Secret deleted, and the raw CR removed from
   git. ArgoCD pruned it and the operator's own delete handler removed only the empty
   `-v2` project and its identity (ids confirmed as `-v2`'s beforehand); the real project
   is untouched and the 14 fingerprints still match.

**Result:** zero `InfisicalProject`/`InfisicalEnvironment` objects on kind-prod; every
project is provider-managed; the whole fleet matches its baseline apart from the new
platform-cicd store. Two smaller findings: the same store-vs-CR drift may exist elsewhere
(worth a look at any other hand-authored CR); and the Composition always renders an
unused ClusterSecretStore `platform-cicd-kind-prod` scoped to `^app-platform-cicd-.*$`
(matches no namespace — harmless).

**The runbook, as it actually had to be done** (each step was needed):

1. **Baseline** — record SecretStore / ClusterSecretStore / ExternalSecret state for the
   whole cluster, and secret counts per environment for the app (read-only, using the
   operator's admin token from `infisical-bootstrap-secret`, read inside the command and
   never printed). Get the project id and environment ids from the operator CRs'
   `status`; the `shared` environment id is *not* in the CR and comes from
   `GET /api/v1/projects/<id>`.
2. **Pause the operator** (`scale --replicas=0`) so it cannot act while CRs are edited.
3. **Detach the credentials Secret from its owner.** The operator sets an
   `ownerReference` to the CR on `<slug>-infisical-creds`; deleting the CR would garbage-
   collect it. Remove it with a JSON patch first.
4. **Strip the CRs' kopf finalizers** (`InfisicalProject` and each `InfisicalEnvironment`
   for the app). Deleting a CR with the finalizer would run the operator's `on_delete`,
   which **deletes the Infisical project and identity**.
5. **Commit the ConfigMap entry** (`secretstore-provisioner.yaml`, in
   `gitops-cluster-kind-prod/10-crds-operators/crossplane/`) with `projectId`,
   `sharedEnvId` and `envIds`. crossplane-packages syncs it.
6. **Grant the provider identity `admin` on the existing project** — *the step the design
   missed.* Adoption fails with 403 on every read until this is done: the provider's
   identity has org-level rights but is not a member of a project it did not create
   (a project it creates makes it a member automatically). API:
   `POST /api/v1/projects/<id>/memberships/identities/<providerIdentityId>` with
   `{"role":"admin"}`. The provider's identity id is the `identityId` claim in its own
   access token. Then annotate the stuck managed resources to retry immediately.
7. **Verify** (secrets preserved, project unchanged, ESO read).
8. **Delete the old CRs** (finalizers already stripped, so nothing reaches Infisical), and
   confirm the project is untouched.
9. **Delete the old operator identity** (`secretstore-<slug>`) through the Infisical API —
   it still holds a valid client secret and viewer access, so it must not be left behind.
   Check its name (nested under `identity.identity.name`) and that delete protection is
   off first.
10. **Prove it after step 9**, then **scale the operator back to 1** and diff the fleet
    against the baseline.

**For apps that hold real secrets** (all the rest): take the per-environment secret count
in step 1 and compare after step 7 — the canary only proves the mechanism, the counts
prove the data. checkout-api has four environments including `prod`; treat it as its own
window.

**Open design point.** An adopted project has `Delete` in its management policies, so
deleting the SecretStore XR would delete the Infisical project **and its secrets**. That
matches kiac-dev, but for a production project consider excluding `Delete`. Not changed
yet.

**Decision made:** adopt in place is now proven for a project with a shared and one
per-env environment. Destroy-and-restore remains the fallback and was not needed.

## Phase 5 — Retire the operator on kind-prod — DONE (2026-09-23)

**The ordering that mattered.** Deleting the operator's CRDs first would have broken the
next newly-onboarded app: the SecretStore Composition still defaulted to the operator for
any app without a ConfigMap entry, so it would have rendered an `InfisicalProject` with no
CRD behind it. So:

1. **Composition made provider-only** (airframe **v0.3.81**): both operator branches
   removed; the ConfigMap is now only for *adopting* an existing project (a slug with no
   entry gets a fresh one; the old `provisioner:` key is ignored). Offline render: all
   four already-opted-in scenarios identical to v0.3.80; the two no-entry scenarios now
   render the provider chain instead of an operator CR.
2. **Rolled out** to kiac-dev and kind-prod. Fleet regression after each sync:
   kiac-dev's 10 SecretStores unchanged; kind-prod's 15 SecretStores, 16
   ClusterSecretStores, 28 ExternalSecrets and 12 managed resources identical.
3. **Operator removed**: the Application, Deployment, ServiceAccount, ClusterRole and
   binding, both CRDs (`infisicalprojects` / `infisicalenvironments.secrets.idp.io`, with
   zero objects) and Crossplane's stale RBAC for that API group. The `infisical` namespace
   stays — ESO places `registry-credentials` in it.
4. **`infisical-bootstrap-secret` deleted** from the cluster (nothing else referenced it).
5. **Final verification** after removal: fleet identical to the pre-Phase-5 baseline, all 28
   ExternalSecrets synced, platform-cicd's 14 and checkout-api's 2 recorded secret
   fingerprints still identical.

**Things that behaved unexpectedly**
- The root Application does not prune, so removing files from git left the operator's
  Application (and resources) in place; they were deleted by hand. Root then briefly
  **re-created the Application from a revision cached before the commit**; it had no
  source and created nothing, and was deleted again once root reached the new commit.
- Main had moved between tags: v0.3.80 was already cut at the merge of your scaffold PR, so
  the provider-only change is v0.3.81, built on top of it.

**`Delete` protection (airframe v0.3.82) — DONE.** Adopted projects had `Delete` in their
management policies, so deleting a SecretStore XR — or ArgoCD pruning its file, which for
platform-cicd sits in an auto-prune Application — would have deleted the Infisical project
and every secret in it. The Composition now renders `Project` and `ProjectEnvironment` with
`managementPolicies: [Create, Observe, Update, LateInitialize]`. The Kubernetes objects go;
the Infisical project and its secrets stay. Identities, their auth config and client
secrets keep `Delete`, so credentials are still revoked.

- **Proven twice before it mattered.** First with raw managed resources on kiac-dev
  (deleted them: the Infisical project, its environment and a canary secret remained), then
  through the real Composition on kind-prod with a throwaway XR: deleting the XR removed
  every Kubernetes object, the project and canary survived, and the identity returned 404.
  Throwaway projects were removed through the API afterwards.
- **Rolled out** to kiac-dev (20 Project/Environment resources protected, 10 identities
  unchanged) then kind-prod (all 21 protected, none can still delete; 6 identities
  unchanged). Fleet identical to baseline both times, and the platform-cicd (14) and
  checkout-api (2) fingerprints still match.
- **The cost, by design:** decommissioning an app leaves its project behind, holding its
  slug. Reusing that slug means adopting the leftover through the
  `secretstore-provisioner` ConfigMap, or deleting the project in Infisical by hand.

**Operator source removed (2026-09-23).** Deleted `operators/infisical-secretstore-operator/`
(source, Dockerfile, both CRD files, README) and its CI workflow from airframe - the
workflow would otherwise have kept publishing an image nothing runs - and the operator's
directory plus its `InfisicalProject` CR file from `gitops-cluster-kind-man` (that cluster
no longer exists). The source stays in git history at tag v0.3.81 and earlier, and
kiac-dev/kind-prod pins to those tags are unaffected. Also dropped the dead operator block
from `refresh-kiac-hosts.sh` (with a note: kind-prod's `dev.kiac.local` aliases now use the
laptop LAN address, so that script's VM-IP logic is wrong for it), and corrected glidepath's
secrets-management doc. Left alone as history: comments in the Composition templates,
gitops-cluster-dev, and this doc set.

**Deliberately NOT removed - needs its own piece of work:**
- **`apron`** (the live cluster template) still ships the operator. New clusters built from it
  would install the retired operator: `hack/customize-cluster.sh` has operator-specific
  prune/rename logic; the operator directory also holds the Infisical NodePort and
  token-reviewer manifests that any Infisical-host cluster needs (those must move, not
  vanish); and its `external-secrets/infisical-project.yaml` is still an operator CR, so a
  new cluster's platform project would fail with no CRD. Fixing it means redesigning how a
  template cluster gets its platform project (a SecretStore XR plus a hand-created
  `provider-infisical-creds`), which cannot be verified without building a cluster.
- **`gitops-cluster-template`** is the deprecated predecessor of apron; not touched.
- **The published image** `ghcr.io/jfillman/infisical-secretstore-operator` is still on GHCR.
  Deleting a package version is outward-facing and irreversible, so it is left for you.

**Follow-ups, not done**
- **Revoke the old admin token in Infisical.** Deleting the cluster Secret removed kind-prod's
  copy, not the token. It is the **`Instance Admin Identity`** - the only `token-auth`
  identity in the org, role `admin`, created by Infisical's own autoBootstrap Job (the
  `infisical-bootstrap-secret` name comes from that job). Revoke its token(s) under
  *Organization -> Access Control -> Identities -> Instance Admin Identity -> Token Auth*.
  Before doing so: kiac-dev still holds a leftover copy of the same token
  (`infisical/infisical-bootstrap-secret`, plus `infisical-bootstrap-credentials`) that
  no workload references, so revoking is safe for it too, but the Infisical chart's
  autoBootstrap may recreate them on a redeploy. Deleting the *identity* rather than just its
  token is a larger step that is not needed.
- **Store shape.** Nothing in the catalog produces a cluster-wide platform store;
  `platform-secret-store` is still hand-authored, and the XR's composed
  `platform-cicd-kind-prod` store matches no namespace.
- The `WatchCircuitOpen` warning seen on first build of new XRs was not investigated.

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
