# I-28: TLS for people-dex's in-cluster key listener

Written 2026-11-20. Strip I-28. Design note plus the two PRs it describes. Owner review first: this touches people sign-in
(the D19 interim). Nothing here is merged or applied.

Read at origin/main of each repo: apron `6e9a9a3`, autopilot `91c802e`. PRs: apron `i28-people-dex-tls`, autopilot
`i28-people-dex-tls` (links in the PR description of this note).

## 1. Problem

The Go gateway and the read API fetch people-dex's signing keys from `http://people-dex.autopilot-system.svc:5556/dex/keys`.
Plain http is allowed only because `autopilot.gateway.go.plainHttp.jwks: true` renders `AUTOPILOT_JWKS_ALLOW_HTTP=1`. Anything
that can intercept pod traffic can answer that request with its own keys and mint a token the gateway accepts for any
`autopilot.people` login, including the admins.

Three more consumers read the same URL and are **not** fixed by this change (section 8): the Clearance core
(`templates/55-clearance/clearance/application.yaml:105`), glidepath-api (`templates/50-glidepath/glidepath-control-plane/values.yaml:143`)
and the Python gateway and read API (`gateway.yaml:135`, `autopilot-api.yaml:108`). They live in other namespaces or run an
image with no CA setting.

## 2. What apron does today (findings)

- people-dex is `templates/55-identity/people-dex/dex.yaml` (ConfigMap, PVC, Deployment, Service), rendered into
  `autopilot-system` by the Argo Application `autopilot-people-dex`. Dex `v2.46.0`, config `web.http: 0.0.0.0:5556`.
- The issuer is the **public** URL, `@@GATEWAY_SCHEME@@://dex.@@CLUSTER_DOMAIN@@/dex`. It is what tokens carry as `iss`, what
  browsers are redirected to, and what the gateway checks. The keys URL is only where the gateway fetches the key set; it
  is a separate env var (`AUTOPILOT_OIDC_JWKS_URL`) from the issuer on every consumer.
- In-cluster TLS pattern: cert-manager is a component (`components.certManager`, `templates/10-crds-operators/cert-manager`,
  chart v1.21.1, on in the dev, prod and platform profiles). The only apron-authored use is `clearance-config/slack-tls.yaml`:
  a namespaced `Issuer` plus a `Certificate`, wave annotations, `SkipDryRunOnMissingResource=true`, Secret filled by cert-manager.
  The rabbitmq operators use a self-signed `Issuer` for webhook certificates. **There is no cluster CA, no ClusterIssuer and
  no trust-manager.** So there is no existing way to hand a CA to another namespace; the design below therefore keeps the
  trust bundle inside `autopilot-system`, where people-dex, the Go gateway and the Go read API all run.
- `plainHttp.jwks` is checked by `hack/check.py` (required whenever `autopilot.people` and `components.gatewayRoutes`).

## 3. Approach

1. **Keep the issuer. Add an internal https listener.** Dex accepts `web.http` and `web.https` together. Set
   `web.https: 0.0.0.0:5557` with `tlsCert` and `tlsKey` beside the existing `web.http: 0.0.0.0:5556`. Both listeners serve the
   same paths (`/dex/keys`, discovery, token). The issuer stays `<scheme>://dex.<domain>/dex`, so existing ID tokens, the
   `iss` check, browser redirects and the device flow are untouched. Nothing about the public route changes
   (`routes.yaml` still sends dex.<domain> to 5556).
2. **cert-manager, in `autopilot-system`, no hand-made Secret.** New `55-identity/people-dex/tls.yaml`: a self-signed bootstrap
   `Issuer` signs a CA `Certificate` (`people-dex-ca`, ECDSA P-256, 10 years), a CA `Issuer` is built on that Secret, and it signs
   the serving `Certificate` `people-dex-tls` (SANs: `people-dex`, `.autopilot-system`, `.svc`, `.svc.cluster.local`; 1 year,
   renew 60 days before). Secret `people-dex-tls` holds `tls.crt`, `tls.key`, `ca.crt`.
3. **Trust bundle = that Secret's `ca.crt`.** The gateway and read API mount only `ca.crt` (Secret `items`), never the key,
   at `/etc/people-dex-ca/ca.crt`. Same namespace, so no trust-manager and no copy.
4. **Autopilot gateway change (separate PR).** The Go JWKS client only used the system roots. New Go-only setting
   `AUTOPILOT_JWKS_CA_FILE` adds a PEM file to the system roots for the key-set client only. `SSL_CERT_FILE` was rejected: it
   replaces the roots for every https client in the process (model provider, OTLP, catalog). A bad or empty file refuses to start.
5. **One switch, off by default.** `autopilot.peopleTls: true` (cluster.yaml). Off, every template renders byte for byte as
   before. On: people-dex gets the listener, certificate and Service port 5557; the Go gateway and read API get
   `AUTOPILOT_OIDC_JWKS_URL=https://people-dex.autopilot-system.svc:5557/dex/keys`, `AUTOPILOT_JWKS_CA_FILE`, the CA mount, and
   the gateway egress policy gains TCP 5557 to the people-dex pods. `hack/check.py` requires `autopilot.people`,
   `components.gatewayRoutes`, `components.certManager` and `autopilot.gateway.implementation: go` with it, and stops requiring
   `plainHttp.jwks` when it is on.

## 4. Why no issuer change

Changing the issuer to an https cluster URL would invalidate every issued token (`iss` mismatch), break the GitHub callback
(`redirectURI`), the static clients' device-flow redirect URIs, Clearance's and glidepath-api's issuer settings, and
`hangar-login`. Serving a second internal listener has none of those effects. If anyone later wants the issuer itself on
https it is `gateway.scheme: https` (already the EKS runtime default), a separate change.

## 5. Exact files

| Repo | File | Change |
|---|---|---|
| autopilot | `gateway/internal/auth/jwks.go` | `(*JWKS).TrustCAFile` |
| autopilot | `gateway/cmd/autopilot-gateway/authconfig.go` | read `AUTOPILOT_JWKS_CA_FILE`, apply to both key sets |
| autopilot | `gateway/envtable.json`, `docs/admin/go-gateway.md`, `docs/admin/go-gateway-env.md`, `CHANGELOG.md` | document the setting |
| autopilot | `gateway/internal/auth/jwks_ca_test.go`, `authconfig_test.go` | tests |
| apron | `templates/55-identity/people-dex/tls.yaml` (new) | Issuer, CA, CA Issuer, serving Certificate |
| apron | `templates/55-identity/people-dex/dex.yaml` | `web.https`, `tlsCert`, `tlsKey`, port, mount, Secret volume, Service port 5557 |
| apron | `templates/55-autopilot/gateway/gateway-go.yaml`, `autopilot-api-go.yaml` | https keys URL, CA env, CA mount |
| apron | `templates/55-autopilot/gateway/gateway-go-egress.yaml` | TCP 5557 to people-dex, both policies |
| apron | `templates/MANIFEST`, `hack/check.py`, `tests/run.sh`, `README.md` | gating, validation, tests, docs |
| gitops (later, owner) | the cluster's `cluster.yaml` | `autopilot.peopleTls: true`, a newer `go.tag` and `go.digest`; later `plainHttp.jwks` off |

## 6. Migration order (no sign-in outage)

The http listener on 5556 never goes away in this change, so people-dex is reachable the old way throughout, and the Go
Deployments roll with the default rolling update (the old pod serves until the new one is ready).

1. Merge and tag the autopilot PR; the manager cuts a `gateway-go-v*` release. The image must contain `AUTOPILOT_JWKS_CA_FILE`.
   **An older image ignores the variable and then fails the TLS verification, and a failed first key fetch is only a warning,
   so readiness stays green while sign-in breaks. Never turn `peopleTls` on with an older image.**
2. Merge the apron PR (no behavior change while the switch is off). Re-render the cluster and diff: the only difference must
   be the new tag and digest and nothing about people-dex (diff-check, as for every apron render).
3. In gitops, one PR: bump `go.tag` and `go.digest` to the release from step 1. Let it sync. Leave `peopleTls` off. Confirm
   sign-in still works.
4. In gitops, a second PR: `autopilot.peopleTls: true`, with `plainHttp.jwks` still on. Argo syncs people-dex first
   (`autopilot-people-dex`: Issuers and Certificates in wave 0, the Deployment in wave 1 once `people-dex-tls` exists; Dex
   restarts, a few seconds, `Recreate` on the PVC). The gateway and read API Applications are separate; if one syncs before
   the Secret exists its new pod waits in ContainerCreating on the mount while the old pod keeps serving. Sync
   `autopilot-people-dex` first if both are out of sync.
5. Live check (section 7). Only then, in gitops, a third PR: `plainHttp.jwks` off. The render drops `AUTOPILOT_JWKS_ALLOW_HTTP`; the
   gateway refuses plain http for the key set from then on, so a regression to http would fail loudly at start.

## 7. Live verification (owner or a session with cluster access, not done here)

- `kubectl -n autopilot-system get certificate` shows `people-dex-ca` and `people-dex-tls` Ready.
- From the gateway pod's namespace: `curl --cacert <ca.crt> https://people-dex.autopilot-system.svc:5557/dex/keys` returns a key set; without the
  CA it fails verification (that is the point). `curl http://...:5556/dex/keys` still works (Clearance depends on it).
- Gateway log at start: no "fetched over plain http" warning for the OIDC key set; sign in with `hangar-login`, call the gateway
  and the read API with the token, both accept it. A token whose `kid` is unknown triggers a refetch: sign in again after a Dex
  key rotation to see it succeed over https.
- Confirm Dex really serves both listeners and the `iss` claim is unchanged (decode a fresh token's payload, do not print the token).

## 8. Out of scope, still plain http after this

- **Clearance core, glidepath-api, Python gateway.** They keep `http://...:5556`. Closing that needs the CA in their namespaces
  (`clearance-system`, glidepath's), which is the trust-manager question below, plus a CA setting in glidepath-api and the
  Clearance core. Until then the 5556 listener stays, so the I-28 exposure is reduced to those consumers, not removed. A
  NetworkPolicy ingress rule limiting 5556 to those namespaces is a cheap next step.
- Rotation. Dex reads `tlsCert` and `tlsKey` at start (verify against v2.46.0 in the live check). After cert-manager renews the
  leaf (day ~305 of 365) people-dex must be restarted, and the gateway reads the CA file once at start, which matters only if the CA is
  ever re-issued (renews year 9). If an operator forgets, the old certificate expires at 365 days and the gateway's key fetches fail. Mitigations:
  a calendar reminder (cheap), or a reloader (new dependency).

## 9. Rollback

- Before step 5: set `autopilot.peopleTls: false`. The URLs go back to http 5556, the https listener, certificate and mounts are
  removed, nothing else changed. Dex restarts once. Tokens, the issuer and sign-in are unaffected throughout.
- After step 5: also set `plainHttp.jwks: true` in the same PR (the check refuses one without the other).
- The new gateway image is compatible with the old config (the setting is opt-in), so the image bump never needs rolling back for this.
- Cert-manager objects can stay or be pruned; they do nothing without the listener.

## 10. Owner decisions and steps

Decisions:
1. **Switch name and default.** `autopilot.peopleTls`, default off, applies to the Go gateway only. OK, or tie it to `implementation: go`?
2. **Trust distribution.** In-namespace Secret now (this PR). To also fix Clearance and glidepath-api the CA must reach their
   namespaces: trust-manager (new dependency; a `Bundle` publishes the CA as a ConfigMap to chosen namespaces, and a shared
   cluster CA could serve all in-cluster TLS) or committing the CA certificate (public material, never the key) to gitops as a
   ConfigMap, which cert-manager re-issuing would break. My recommendation: trust-manager, once.
3. **Rotation.** Accept a manual people-dex restart yearly, or add a reloader?
4. **Python gateway** is left on http. It is the default implementation; is any cluster still on it? If so a Python CA setting is a third PR.

Owner steps (all in gitops, none done here): tag the autopilot release (manager), then the three gitops PRs in section 6 and
the live check in section 7. No secrets are created by hand at any step.

## 11. Tests

apron `tests/run.sh` and `hack/check.py` (counts in the PR); autopilot `go test ./...` in `gateway/`. The render tests prove the
off render is unchanged, that the on render has both listeners, the https URL, the CA mount of `ca.crt` only, the egress port, no
hand-made Secret and an unchanged issuer, and that `check` accepts `peopleTls` without `plainHttp.jwks` and still requires it without.
