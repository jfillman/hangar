# A-17: Clearance TLS on hangar-dev, rollout plan

Written 2026-11-21. Strip A-17 (owner approved option (a)), with I-43 and I-28. A plan only: no cluster, gitops repo or
release was changed, and nothing here is merged. Read with `specs/plans/i43-clearance-tls.md` (the design) and
`specs/plans/i28-people-dex-tls.md` (people-dex).

Read at: apron `919c83b`, clearance `b41ccd5` (chart and images 0.54.0), gitops-hangar-dev `origin/main` of 2026-11-21.

## 1. Decisions this plan follows (Y-40)

- One shared cluster CA, published by trust-manager. people-dex (I-28) uses the same CA.
- The core and the API serve https on **8443**. Leaf certificates last **90 days** and renew **30 days** early. These are the
  clearance chart's defaults (`tls.certManager.duration: 2160h`, `renewBefore: 720h`).
- Nothing outside the cluster calls the core on 8080. Section 8 lists the one path that still reaches 8080 through the gateway.
- The admission policy change is apron PR `a17-wait-job-ca-volume`. It adds `clearance.gate.waitCAConfigMap`.

## 2. What is on hangar-dev today (read-only kubectl, 2026-11-21)

- **cert-manager is installed**: the Application `cert-manager`, controller `v1.21.1`, in namespace `cert-manager`, 31 days
  old (`components.certManager: true` in the dev profile). It has no ClusterIssuer. The only Issuers are the self-signed ones
  of the OpenTelemetry and RabbitMQ operators.
- **trust-manager is not installed.** There is no `trust-manager` namespace and no `trust.cert-manager.io` CRD.
- The gate is on in Warn mode (`clearance.gate.enabled`, `lowerZone`, `enforce` off). Both policies are live.
- **No wait Job runs on hangar-dev.** None exists now. The one protected namespace, `w40-optin-test`, is cleared as
  environment `dev`, which `protectedEnvironments` does not hold. The README also says the core's NetworkPolicy does not
  admit a wait Job's pod on the core's own cluster. The wait Jobs that call this core run on **hangar-prod**
  (`app-gate-api-prod`). They come through the HTTPRoute `clearance-gate` (`clearance.hangar-dev.local`) to port 8080.

## 3. Work that must land in apron first (not built)

Only the policy change is in a PR. Each step below names the apron change it needs. Each change is off by default and gets
its own PR, with a render diff-check.

| # | apron change | Used in |
|---|---|---|
| P1 | `clearance.gate.waitCAConfigMap`: the policy admits the wait Job's optional CA volume (the A-17 PR) | step 5a |
| P2 | `components.trustManager`: jetstack's trust-manager chart, trust namespace `cert-manager` | step 1 |
| P3 | the cluster CA: a self-signed bootstrap ClusterIssuer, a CA Certificate `hangar-cluster-ca` in `cert-manager`, a CA ClusterIssuer `hangar-cluster-ca`, and a Bundle `hangar-cluster-ca` (source: that Secret's `ca.crt`; target: a ConfigMap, key `ca.crt`) | step 2 |
| P4 | `clearance.tls.*`: passes the chart's `tls.enabled`, `tls.plainHttp` and `tls.certManager.issuerRef` (ClusterIssuer `hangar-cluster-ca`), plus a NetworkPolicy for 8443 from the same peers as 8080 | steps 3, 7 |
| P5 | the gate clients' CA: `CLEARANCE_CA_FILE` and the Bundle ConfigMap mount on the repo-server sidecar; `tls.caConfigMap` on the agent and the observe collectors; `CLEARANCE_WAIT_CA_CONFIGMAP` on the sidecar and `waitJob.caConfigMap` on the agent, set from `waitCAConfigMap` | steps 4, 5b |
| P6 | `autopilot.peopleTls` with the cluster CA: people-dex's Certificate takes `issuerRef` ClusterIssuer `hangar-cluster-ca`, and its clients mount the Bundle ConfigMap instead of the Secret's `ca.crt` | step 6 |

Before step 3, bump `versions.clearance.cmpImage`, `waitImage` and `argocdAgentImage` to the 0.54.0 digests. Older clients
have no CA setting, so they fail verification and the gate fails closed. I did not check which release the current
`waitImage` digest comes from. Do that first. Never point a client at https while it runs an older binary.

## 4. Steps on hangar-dev

Each step is its own gitops PR. Merge it, sync it, and check it before you start the next one.

### Step 1. trust-manager

- Change: `components.trustManager: true` (P2). Pin the chart and the version on the PR. Check that the Bundle API
  (`trust.cert-manager.io/v1alpha1` `Bundle`, or its newer replacement) matches the pinned version.
- Check: the trust-manager Deployment is Ready, and its webhook answers (a dry-run Bundle is accepted).
- Rollback: set `components.trustManager: false`. Nothing depends on it yet.

### Step 2. The cluster CA and the Bundle

- Change: P3. Make the CA ECDSA P-256 with a 10-year life and `privateKey.rotationPolicy: Never`. The Bundle targets every
  namespace. The CA certificate is public, so publishing it everywhere costs nothing, and a new protected namespace has
  it before its first wait Job. `useDefaultCAs: false`, so the ConfigMap holds only the cluster CA.
- Check: `kubectl get certificate -n cert-manager hangar-cluster-ca` is Ready. `kubectl get clusterissuer hangar-cluster-ca`
  is Ready. `configmap/hangar-cluster-ca` exists in `clearance-system`, `argocd-apps`, `autopilot-system` and
  `w40-optin-test`, and its `ca.crt` matches the CA Secret's `ca.crt` (compare fingerprints, never print the key).
- Rollback: remove P3. Nothing uses it yet. Delete the Bundle before the CA, so no ConfigMap points at a missing source.

### Step 3. Core and API TLS on 8443, plain http still on

- Change: `clearance.tls.enabled: true` with `plainHttp: true` and the `hangar-cluster-ca` issuer (P4). The core restarts
  once (Recreate), so the gate and the verify page see a short outage, as they do on any core upgrade. The API rolls.
- Check:
  - The Certificates `clearance-core-tls` and `clearance-api-tls` are Ready, each with a 90-day life.
  - From a pod in `clearance-system`, `curl --cacert ca.crt https://clearance-core.clearance-system.svc:8443/readyz`
    returns 200. The same call without `--cacert` fails verification.
  - Plain `http://...:8080/readyz` still answers.
  - The leaf verifies against the new CA alone:
    `openssl verify -no-CApath -no-CAstore -trusted ca.crt leaf.pem`.
- Rollback: `clearance.tls.enabled: false`. No client uses https yet.

### Step 4. In-cluster clients to https, except the wait Job

- Change (P5), one client per PR:
  1. The agent: `tls.caConfigMap: hangar-cluster-ca`, with the core and API URLs on https.
  2. observe-k8s and observe-aws: the same settings.
  3. The repo-server sidecar: `CLEARANCE_CA_FILE` and the mount.
- The sidecar's own `CLEARANCE_URL` and the wait Job's URL are both `clearance.gate.url`, so that key stays http in this
  step. If the sidecar needs to move first, that is a separate P5 setting.
- Check: each client's calls succeed. Where a client logs the CA it loaded at start, that CA is the cluster CA. The agent's grant feed keeps updating. Run
  `clearance-cmp doctor` in the sidecar: `core-tls` must pass for an https URL.
- Rollback: set the client's URL back to `http://...:8080`. An http URL ignores the CA setting.

### Step 5. Wait Jobs to https

The policy pins one core URL and one shape, so the order matters.

- **5a. Policy first.** Set `clearance.gate.waitCAConfigMap: hangar-cluster-ca` (P1). This only widens the policy. A wait
  Job with or without the CA volume is admitted. Check: the live `clearance-protected-writes` contains
  `configMap.name == 'hangar-cluster-ca'`, and the render diff touches only `56-clearance-gate/admission.yaml`.
  Rollback: unset the key, after step 5b is rolled back.
- **5b. The plugin mounts the CA.** Set the sidecar's `CLEARANCE_WAIT_CA_CONFIGMAP` and the agent's `waitJob.caConfigMap`
  together (P5). The agent's pin then expects the CA volume, and the policy already admits it. Check: render a held change
  (use a scratch protected namespace whose environment is protected, section 7). The injected Job has volume and mount
  `clearance-ca` at `/etc/clearance-ca`, and the agent does not report it as out-of-band. Rollback: unset both. Wait until
  no wait Job that uses the CA mount is still running, then go on.
- **5c. The URL.** Set `clearance.gate.url: https://clearance-core.clearance-system.svc:8443`. One render moves the sidecar,
  the wait Job, the policy's pinned URL and the agent's pin together. Check: a held change clears end to end through an
  https wait Job (section 7). Rollback: set the http URL again.
- **Caveat for an enforcing cluster.** hangar-dev runs Warn, so in 5c an in-flight wait Job or a cached manifest that still
  carries the http URL only warns. On a cluster with `enforce: true` it would be refused. Before you repeat 5c on such a
  cluster, add a one-release `previousURL` to the policy, the same way `previousWaitImage` works. That is not built.

### Step 6. people-dex on the same CA (I-28)

- Change: `autopilot.peopleTls: true` with P6, and with `plainHttp.jwks` still on. Follow I-28 section 6, steps 3 to 5:
  1. Bump the Go gateway image to one that has `AUTOPILOT_JWKS_CA_FILE`.
  2. Sync `autopilot-people-dex` first, and wait until the Deployment is Ready.
  3. Run `curl --cacert ... https://people-dex.autopilot-system.svc:5557/dex/keys`.
  4. Only then sync the gateway and read-API Applications.
  5. In a later PR, turn `plainHttp.jwks` off.
- Dex reads its certificate once, at start, so restart people-dex after each renewal. That is a few seconds of sign-in
  outage. With the cluster CA, the leaf's life follows P6's Certificate (I-28 used 1 year with 60 days' renewal). Keep
  that life, or move to 90/30 and accept a restart every 60 days.
- Check: I-28 section 7.
- Rollback: I-28 section 9, staged. Sync the clients back to http 5556 first, then people-dex.

### Step 7. Verify, then turn plain http off

- **Verify before you turn it off:**
  - Every in-cluster client's URL is https in the live render.
  - The NetworkPolicy flow logs, or the core's access log, show no client on 8080 for a full day.
  - `clearance-cmp doctor` reports no `core-tls` warning.
- Change: `clearance.tls.plainHttp: false` (P4). The core restarts. The Service loses its http port, and the probes move to
  `scheme: HTTPS`.
- **Blocked today.** The chart refuses `plainHttp: false` while an HTTPRoute, the web UI, clearance-slack or clearance-grc
  is on. hangar-dev has HTTPRoutes `clearance-gate`, `clearance-api` and `clearance-github-webhook` to port 8080. hangar-prod's
  gate (`clearance.gate.url: http://clearance.hangar-dev.local`) and agent (`apiURL: http://clearance-api.hangar-dev.local`)
  use the first two, and GitHub's webhook uses the third. Each route needs an https backend first (a BackendTLSPolicy, which
  apron does not render) or has to go. This needs an owner decision (section 8).
- Rollback: `clearance.tls.plainHttp: true`. The core restarts and the http port comes back.

## 5. CA replacement and renewal

Follow I-43 section 4. Make the Bundle publish the old and the new CA. Restart the clients that read `ca.crt` only at start,
and check the CA each one loaded. Re-issue the leaves. Check each leaf against the new CA alone. Only then remove the old CA.
The clearance core and API reload a renewed leaf without a restart. people-dex does not.

## 6. Rollback order, overall

Go back down the steps in reverse: 7, then 6, then 5c, 5b and 5a, then 4, 3, 2 and 1. Never delete the Bundle or its
ConfigMap while a wait Job that mounts it can still be injected or is still running. A pod that mounts a missing ConfigMap
sits in ContainerCreating, and the sync stays held.

## 7. Verification gap on hangar-dev

hangar-dev cannot run a wait Job today (section 2). To prove step 5 end to end there, the owner has to pick one:

- (a) A scratch protected namespace, cleared as an environment that `protectedEnvironments` holds, plus a core
  NetworkPolicy rule that admits its pods on 8443. This is test-only, so remove it afterwards.
- (b) Prove step 5 on hangar-prod's own path instead, which first needs the route decision in section 8.

Until then, step 5 is proven on hangar-dev by the policy (apron envtest), the plugin's render (clearance `job_ca_test.go`)
and the agent's pin, not by a live wait Job.

## 8. Open questions for the owner

1. **Cross-cluster callers.** hangar-prod's wait Jobs and agent reach this core and API over plain http through the gateway
   (port 80 to backend 8080). Should step 7 wait until those routes terminate TLS at the gateway and re-encrypt to 8443
   (a BackendTLSPolicy, new apron work)? Or do the routes stay on plain http, with step 7 dropped for hangar-dev?
2. **Bundle scope.** All namespaces (recommended: the CA certificate is public) or a label selector?
3. **people-dex leaf life.** Keep I-28's 1 year with 60 days' renewal (a restart per year) or the core's 90/30 (a restart
   every 60 days)?
4. **Enforcing clusters.** Build the one-release `previousURL` for step 5c before any enforcing cluster moves to https?
