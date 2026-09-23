# kind-prod: migrate to the new airframe pin and retire the Infisical operator

Status: **plan, nothing executed** (2026-09-23). Written from live read-only
inspection of kind-prod, the airframe tags, and the upstream Terraform provider.

## The short version

Bumping kind-prod's airframe pin does **not** retire the operator. Every SecretStore
on kind-prod uses **universal auth** (it isn't the cluster that hosts Infisical), and at
v0.3.77 that branch still renders the *old* `InfisicalProject` CR on purpose. The new
provider-infisical chain only exists for the kubernetes-auth branch (kiac-dev).

The reason is a bug in `terraform-provider-infisical`: `GetIdentityUniversalAuthClientSecretResponse`
declares `ClientSecretData` as a single struct, but the API returns an array, so the
resource's Observe path fails before Create runs. **Still present in v0.19.33
(2026-09-21)** — checked in the upstream source, not just the release notes.

We own `provider-infisical`, so this is fixable — but the bug is one layer *below* our
code. `provider-infisical` is upjet-generated and its Dockerfile downloads the upstream
Terraform provider as a prebuilt release zip
(`TERRAFORM_PROVIDER_DOWNLOAD_URL_PREFIX`). The fix is a patched fork of the Terraform
provider, built for both architectures, and a URL/version change in our Makefile. No
change to our generated Go code.

So the work is four things in order: fix the provider, write the universal-auth branch
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

Architectures: kind-prod is **amd64**; the provider image must be multi-arch, and so
must the patched Terraform provider zips (the Dockerfile picks by `TARGETARCH`).

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

## Phase 1 — Fix the provider (no kind-prod impact)

1. Reproduce against our live Infisical: call the client-secret GET endpoint with a
   throwaway identity and look at the actual response shape. Don't assume the array —
   confirm it, and confirm what the LIST endpoint returns too.
2. Fork `Infisical/terraform-provider-infisical` at v0.19.33. Patch the response type
   (a small `UnmarshalJSON` accepting object *or* array, or select by
   `clientSecretId`). Add a test with both shapes.
3. Build `linux_arm64` and `linux_amd64` zips named the way the Dockerfile expects
   (`terraform-provider-infisical_<ver>_<os>_<arch>.zip`, binary
   `terraform-provider-infisical_v<ver>`), publish them as a release on the fork.
4. In `provider-infisical`: point `TERRAFORM_PROVIDER_DOWNLOAD_URL_PREFIX`, `_VERSION`
   and `_NATIVE_PROVIDER_BINARY` at the fork; rebuild the multi-arch image and xpkg,
   publish, tag.
5. Prove it on **kiac-dev with a throwaway app**: `Identity` → `IdentityUniversalAuth`
   → `IdentityUniversalAuthClientSecret` reaches `Ready`, its connection Secret carries
   `clientId`/`clientSecret`, and an `ExternalSecret` reads a real value through it.
   Also prove delete cleans up.
6. **Upstream PR: only if you say so.** Standing instruction on this project is to ask
   before pushing anything to someone else's repo.

Exit gate: the throwaway universal-auth chain is green on both architectures.

## Phase 2 — Composition (airframe)

The universal branch of `compositions/secretstore/` needs writing on the new provider:
`Project`, `ProjectEnvironment` (shared plus one per env), `Identity`,
`IdentityUniversalAuth`, `IdentityUniversalAuthClientSecret`, `ProjectIdentity`, then a
credentials Secret from the connection details and a `ClusterSecretStore` using
`universalAuthCredentials` (client id and secret both referenced, unlike the
kubernetes branch which references only an identity id).

Two design points:

- **No blanket flip.** The kiac-dev playbook is explicit that merging a Composition
  which re-renders every existing XR is how you destroy real projects. Add an opt-in
  (for example `spec.provisioner: operator | provider`, default `operator`) so merging
  changes nothing, and each XR is flipped deliberately.
- **Reuse the fixes already found**: `data` + `b64enc`, never `stringData`, on any
  `provider-kubernetes`-managed Secret; keep comments free of the template delimiter
  pair; offline-parse the template with a tiny Go program before it ships.

Also decide `platform-cicd-kind-prod`. On kiac-dev its project is rendered from inside
the chart as a `SecretStore` XR. On kind-prod it is a raw `InfisicalProject` CR in
`gitops-cluster-kind-prod/10-crds-operators/external-secrets/`; it should become a
`SecretStore` XR the same way.

Exit gate: a tagged airframe release; the Composition renders the universal chain for
a throwaway XR on kiac-dev *and* still renders the operator CR for everything else.

## Phase 3 — Install on kind-prod

1. **Provider.** `provider-infisical` (amd64 confirmed by it going Healthy), its own
   `DeploymentRuntimeConfig` (never the shared default — that broke every Function
   once), `ClusterProviderConfig`, and RBAC. Use the sync-wave and
   `SkipDryRunOnMissingResource` pattern this session needed for provider-helm.
2. **Credential.** The provider needs an Infisical admin credential on kind-prod. The
   operator already holds one (`infisical-bootstrap-secret`), so the exposure is the
   same, not larger. Seed it by hand; **never paste it into a repo or chat.**
3. **Reachability.** The provider pod must reach `dev.kiac.local:31800`, exactly as the
   operator does today. Confirm from inside the pod.
4. **Pins.** Move `idp-service-catalog` to the new tag, fold the temporary
   `idp-service-catalog-redis` Application back into it, and align the two tenant
   ApplicationSets (`tenant-onboarding`, `tenant-identity`, currently v0.3.76).

Exit gate: everything Healthy and **every existing SecretStore, ClusterSecretStore and
ExternalSecret unchanged** (compare before and after). Provider present, zero XRs
flipped.

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

1. **Fork and patch the Terraform provider ourselves?** It's the only route that
   retires the operator. Say whether to also offer the fix upstream.
2. **Adopt in place, or destroy and restore?** (Above.)
3. **Who diffs the backups?** I can, given a credential to read them; I won't be
   handed one in chat.
4. **`kiac-man` and kind-man's separate operator copy** — both are gone per the current
   cluster list, so their repos need no migration; confirm.
5. **Timing.** checkout-api runs a real `prod` environment on this cluster.
