# I-43: TLS for the Clearance core and API

Written 2026-11-20. Strip I-43. Design note plus the Clearance product PR it describes. Nothing here is merged, tagged or
applied; apron, gitops and every cluster are untouched. Read with `specs/plans/i28-people-dex-tls.md` (PR #138), which solves
the same CA-distribution question for people-dex; section 4 keeps the two consistent.

Read at origin/main of clearance `494ff0f`.

## 1. Problem

The gate clients send a projected service-account token (audience `clearance`, one hour) as a bearer token to
`clearance-core` and `clearance-api` over plain http on port 8080. The clients are the Argo CD plugin sidecar (`CLEARANCE_URL`),
the PreSync wait Job (`CLEARANCE_URL`, injected by the plugin), the Argo CD agent (`--core-url`, `--api-url`) and observe-aws.
Anything that can watch pod traffic can replay a token for up to an hour against the core: record a change, clear one it may
not, or read the API.

## 2. What the Clearance repo does today (findings)

- Both servers are one `http.Server` on `CLEARANCE_LISTEN` (default `:8080`): `internal/core/core.go` `Run`,
  `internal/api/config.go` `Run`. No TLS code anywhere; the chart's probes, Services, NetworkPolicies and HTTPRoutes all name
  8080 / the `http` port.
- The Go client (`client.New`) already accepts an `https` BaseURL but only trusts the system roots. The wait binary, the agent's
  feed reader (`providers/argocd/agent/http.go`) and observe-aws' evidence reader are plain `http.Client`s with no trust setting.
- The wait Job is **pinned**: the plugin renders it (`cmp/job.go`), the agent's scan recognises it field by field
  (`agent/waitjob.go`), and the admission policy exempts exactly that shape (`crd/admission.yaml`, rendered by apron). It has two
  env vars and one volume. Anything added to it must be added in all three.
- cert-manager is not a dependency of the chart today; the chart must install without it.
- No trust-manager and no cluster CA exist in apron (I-28 section 2).

## 3. Approach

1. **A second, https listener beside 8080.** `CLEARANCE_TLS_LISTEN` (`:8443`), `CLEARANCE_TLS_CERT_FILE`,
   `CLEARANCE_TLS_KEY_FILE` on both the core and the API; all three or none. The same handler serves both, so nothing about
   authentication changes. TLS 1.2 or later. An unreadable pair stops the start. The certificate is **hot-reloaded**: a
   `GetCertificate` callback compares the files' mtimes at most every 10 seconds and loads a changed pair; a failed reload keeps
   the last good certificate. cert-manager renewal needs no restart (this removes the "restart people-dex yearly" gap I-28 lists).
   `CLEARANCE_LISTEN=off` drops the plain listener (refused unless the https one is on).
2. **Chart: `tls.*`, default off, byte-identical render when off** (checked against origin/main for every ci values file).
   On: container port and Service port `https`/8443, the key pair mounted from a Secret (`tls.crt`, `tls.key` only) at
   `/etc/clearance/tls`, the env above, NetworkPolicy ingress for 8443. `tls.plainHttp: false` sets `CLEARANCE_LISTEN=off`,
   removes the Service's http port and moves the probes to `scheme: HTTPS` (the kubelet does not verify).
3. **cert-manager, no hand-made Secret.** `tls.certManager.enabled` (default on with TLS) renders Certificates `<release>-core-tls`
   and `<release>-api-tls` (ECDSA P-256, 90 days, renew 30 days before; SANs: the Service's four names plus `tls.dnsNames`).
   Issuer: by default the chart builds its own namespaced CA (self-signed Issuer, CA Certificate, CA Issuer), so **Clearance installs
   on its own with only cert-manager present**; or `tls.certManager.issuerRef` names an existing Issuer or ClusterIssuer (a shared
   cluster CA, which is what apron would supply). `tls.certManager.enabled: false` takes `tls.existingSecrets`. apron only
   sets values; it is not referenced anywhere in the chart.
4. **Clients verify, with an optional CA file.** One setting, `CLEARANCE_CA_FILE` (`--ca-file`; Go `client.Options.CAFile`):
   a PEM file added to the system roots for that client's connections only (not `SSL_CERT_FILE`, which replaces roots process-wide;
   the same choice I-28 made for `AUTOPILOT_JWKS_CA_FILE`). No skip-verify setting exists. A bad file stops the client. Wired into
   the plugin sidecar (and its `doctor`), the wait binary (also defaults to `/etc/clearance-ca/ca.crt` when mounted), the agent
   (both the core client and the feed reader) and observe-aws. The URL is the existing `CLEARANCE_URL` / `--core-url` /
   `--api-url`, now `https://...:8443`.
5. **The wait Job's CA.** Optional `CLEARANCE_WAIT_CA_CONFIGMAP` on the plugin (and `--wait-ca-configmap` on the agent): the
   plugin adds a read-only ConfigMap volume (key `ca.crt`) mounted at `/etc/clearance-ca`; no env var changes, so the existing
   two-variable pin stays. The agent's validator (`WaitPin.CAConfigMap`) accepts exactly that one extra volume and mount.
   **The admission policy's CEL must get the same optional volume and mount, in apron's template** (section 8): not done here.
6. **Agent chart.** `tls.caConfigMap` mounts the CA and sets `CLEARANCE_CA_FILE`; `waitJob.caConfigMap` is the pin above.

## 4. CA distribution, and consistency with I-28

I-28 keeps the trust bundle inside one namespace (a Secret's `ca.crt`, no trust-manager), because every consumer was in
`autopilot-system`, and recommends trust-manager once for the cross-namespace consumers, naming Clearance's namespaces. This is that
case. Clearance's callers are in other namespaces (the plugin in Argo CD's, the wait Job in every destination namespace, the agent in
`clearance-system`, observe-aws wherever it runs), so a Secret mounted in place does not work.

- **Recommended: trust-manager, one shared cluster CA.** A cluster `ClusterIssuer` (CA) in the cert-manager namespace signs people-dex's
  certificate (I-28), the core's and the API's; one trust-manager `Bundle` publishes its certificate as a ConfigMap `ca.crt` in the
  namespaces that ask. One source for both notes; the I-28 apron PR's in-namespace CA then becomes an `issuerRef`. A Bundle can read
  a Secret source only from the trust namespace, which is why the CA Secret must be the cluster CA's, not the chart's own.
- **What Clearance supports either way**: any ConfigMap or file with the CA certificate. The chart takes `tls.certManager.issuerRef` (so it
  signs with the shared CA) and the clients take a CA file path; none of them knows about trust-manager. Without a shared CA the chart's
  own CA works for in-release callers, and the CA certificate (public, never the key) can be copied to a ConfigMap by the operator.
- **Why not a CA-bundle value only**: committing the certificate to gitops breaks when cert-manager re-issues the CA (I-28 section 10
  says the same); a Bundle follows it.
- **CA replacement (overlap).** The Bundle publishes what its source holds, so a replacement is staged, never swapped: (1) make the
  Bundle publish **both** CA certificates (old and new) and wait until every client namespace's ConfigMap holds both; (2) **restart the clients that
  read `ca.crt` only at start** (they still trust the old CA alone, and would reject a new-CA leaf), and wait for them to be Ready, after first checking that each client's mounted `ca.crt` already holds both certificates (a client that restarts before the ConfigMap update reaches its mount loads the old certificate and keeps it), and confirm each startup-only client loaded the new one (the startup log line that names the loaded CA; the mount alone proves only what the file holds, not what the process read); (3) only then re-issue
  the leaves (core, API, people-dex) under the new CA and restart the servers that read them at start; (4) once every served leaf verifies against the **new CA alone** (the old and new CA can share a subject name, so an issuer-name check proves
  nothing: verify each server's presented leaf with `openssl verify -no-CApath -no-CAstore -trusted <new ca.crt> leaf.pem` (`-trusted` alone, so no default trust store that still holds the old CA can accept it) or a client given only the new CA), remove the old CA from the
  Bundle; (5) restart the clients once more if they must stop trusting the old CA, with the same check first (the mount holds only the new CA before the restart; confirm after).
  Set the CA's `privateKey.rotationPolicy: Never` where a re-issue should keep the same key: leaves still verify, but a startup-only client holds the old CA
  *certificate* and Go rejects the chain once that certificate expires, so such a renewal still needs the clients restarted (or reloaded) with the renewed
  `ca.crt` **before the old certificate's `notAfter`**; only the overlap of two CAs is skipped.
  The CA must never be replaced by one that drops the old certificate while any server still presents an old-CA leaf.
- **Mismatch to avoid**: do not have two different CAs per namespace pair. If the owner takes I-28 as written (in-namespace CA) first and
  trust-manager later, only the `issuerRef` changes; the file path and env names do not.

## 5. Exact files (Clearance PR)

| File | Change |
|---|---|
| `internal/tlsutil/` (new) | reloading server certificate, listener env parsing, client CA pool |
| `internal/core/core.go`, `internal/api/config.go` | the optional https listener, `CLEARANCE_LISTEN=off` |
| `client/client.go` | `Options.CAFile`, `NewHTTPClient` |
| `providers/argocd/{cmp,wait,agent}`, `providers/observe-aws/cmd` | `CLEARANCE_CA_FILE`; wait Job CA mount and its validator |
| `charts/clearance/templates/{tls,core,api,networkpolicy,_helpers}`, `values.yaml`, `ci/tls*.yaml` | the `tls.*` values |
| `charts/clearance-argocd-agent` | `tls.caConfigMap`, `waitJob.caConfigMap` |
| `docs/tls.md`, `docs/core.md`, `docs/clearance-api.md`, `CHANGELOG.md` | docs |

## 6. Migration order (no running gate breaks)

The plain listener is never removed until step 6, so a client that has not moved keeps working.

1. Merge and release the Clearance PR. No behavior change while `tls.enabled` is false. **Never point a client at https with an older
   binary**: an old client has no CA setting and fails verification, and the gate fails closed.
2. gitops/apron (owner): bump Clearance to the release. Diff-check the apron render: the only difference must be the image tag.
3. Turn on server TLS beside plain: `tls.enabled: true` (plus `tls.certManager.issuerRef` if the shared CA exists). The core restarts once
   (Recreate; the verify page and gate calls see a short outage, as on any core upgrade); the API rolls. Check the Certificates are Ready.
4. Publish the CA to the namespaces that need it (trust-manager Bundle, or a ConfigMap).
5. Move clients one at a time, each a separate PR, checking after each: the agent (`tls.caConfigMap`, https URLs); the plugin sidecar
   (`CLEARANCE_URL`, `CLEARANCE_CA_FILE`), **with the wait URL kept on http**: the plugin injects the wait Job with `CLEARANCE_URL`, so
   this step sets the wait URL explicitly to the http one (or the plugin does not derive it) and no new wait Job gets an https URL
   before its CA mount exists; then, together and in this order, the admission policy's optional CA volume (apron), the plugin's
   `CLEARANCE_WAIT_CA_CONFIGMAP`, the agent's `waitJob.caConfigMap`, and only last the wait URL to https. An in-flight wait Job keeps
   its old http URL and finishes; its next injection uses https. Last, observe-aws.
6. When the NetworkPolicy flow logs (or the pods' access logs) show nothing on 8080 from clients, set `tls.plainHttp: false`.
   Not supported yet while the web UI, clearance-slack, clearance-grc or an HTTPRoute is on (they call over plain http and have no CA
   setting; the chart refuses it). NetworkPolicy rules for plain 8080 stay until then.

## 7. Rollback

- Before step 6: set a client's URL back to `http://...:8080`; nothing else is needed (the CA setting is ignored by http).
- After step 6: set `tls.plainHttp: true`; the core restarts, the Service gets its http port back.
- To remove TLS: `tls.enabled: false` after every client is back on http. The Certificates and the Secrets can stay or be pruned.
- A wait Job already rendered with the CA mount needs the ConfigMap to exist; if it is removed first the Job pod waits in
  ContainerCreating and the sync stays held. Unset `CLEARANCE_WAIT_CA_CONFIGMAP` first, then wait until every existing
  wait Job that uses the CA mount has finished or been removed (`kubectl get jobs` for the wait Jobs, per destination namespace), and only
  then delete the ConfigMap or the Bundle that publishes it: unsetting the variable changes only Jobs rendered afterwards.

## 8. Out of scope, follow-ups, owner decisions

- **apron: the admission policy's wait-Job exemption** must allow the optional second volume and mount (the CEL in `admission.yaml`
  is rendered by apron). Until that lands the wait Job cannot use a private CA, so step 5's last item and step 6 wait for it. It
  needs an envtest run (`providers/argocd/crd/test_admission.py`), which was not available here, so the CEL was deliberately not edited.
- web UI, clearance-slack, clearance-grc call the core and API over plain http; each needs the same CA setting before step 6.
- The people-dex and glidepath consumers are I-28's.
- A BackendTLSPolicy for HTTPRoutes to the https port is not rendered.

Owner decisions:
1. **Shared cluster CA plus trust-manager** (recommended, matches I-28's recommendation) or the chart's own CA and an operator-copied ConfigMap?
2. Port **8443** and a 90-day leaf with 30-day renewal: OK?
3. Is anything outside the cluster (a route, another cluster's gate clients) calling the core on 8080? It would need the route to keep a plain backend.
4. Approve the apron follow-up for the admission exemption, and who tags the Clearance release.

Owner steps (none done): tag the release; the gitops PRs in section 6; the live check (Certificates Ready; `curl --cacert` succeeds
and a call without the CA fails; a held change clears end to end through an https wait Job; `/readyz` through https). No secrets are
created by hand at any step.

## 9. Tests

Clearance PR: `internal/tlsutil` (a TLS server with a private CA is accepted with the CA file and refused without it or with another
CA; hot reload; env parsing), `client` (the same against `client.New`), core and API config parsing, the wait Job pin with and without the
CA mount, the plugin's wait Job render, and the chart render tests (off render unchanged, on render, refusals). Counts are in the PR.
