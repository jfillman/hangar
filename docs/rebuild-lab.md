# Rebuilding the lab with Apron

One ordered checklist for rebuilding the two lab clusters as **hangar-dev** and **hangar-prod** with the new
`apron` tool, then standing Skyport back up. The names are this rebuild's choice; nothing in Apron, Airframe,
Glidepath or Tower depends on them.

**One name per cluster.** The name you give `apron init --name` is also the cluster's kubectl context, its entry in
the fleet `clusters.yaml`, its Infisical project stem (`glidepath-<name>`, `<app>-<name>`), its issuer path
(`https://hangarplatform.dev/oidc/<name>`) and its hostname stem (`<service>.<name>.local`).

In the commands below, `<owner>` is your GitHub owner. The lab puts hangar-dev on kiac (this Mac) and hangar-prod on
kind (the second MacBook); that is a hardware choice, not a requirement.

## 0. Before teardown

1. **Back up Infisical.** Export every project and environment (`infisical export --projectId … --env …`, or the
   UI), store the exports encrypted and offline. Infisical starts fresh; the export is the only source for values
   that live nowhere else: the GitHub App private key, the classic PAT, the Backstage OAuth client secret, the
   MinIO break-glass keys and the anchor key. Key list: section 3 below.
2. **Accept what is thrown away:** the Rekor transparency log and Fulcio root (old image signatures and receipts stop
   verifying), Tekton Results history, MinIO/Thanos/Loki/Tempo data, Backstage's Postgres, Prometheus data.
3. **Merge and tag, in this order** (each is a branch, already pushed):
   1. airframe: `no-hardcoded-cluster-names`, then `backstage-on-airframe` (rebased on it), then
      `skyport-walkthroughs`. Cut the next tag.
   2. glidepath: `no-hardcoded-cluster-names`. Apron pins Glidepath to `main`; tag it if you prefer a pin.
   3. tower: `no-hardcoded-cluster-names`; release per `RELEASING.md`.
   4. apron: `apron-up` (`apron-cli` is already merged in; 101 + 17 tests passing).
   5. apps, on `dex-tokens`: **boarding-api first**, then flight-api (run its `./test.sh`; it was never compiled
      here), then baggage-api.
   6. backstage: `airframe-app`.
4. **Bump Apron's pins** in `versions.yaml` (`airframe.*` to the new Airframe tag) before `apron init`.
5. **Make `ghcr.io/<owner>/function-dex` public** (the prod cluster pulls it without credentials).

## 1. Teardown (point of no return)

```sh
kiac delete cluster --name dev                    # this Mac: the old kiac-dev
kind delete cluster --name prod                   # the second MacBook: the old kind-prod (check `kind get clusters`)
```

Archive the old cluster and tenants repos on GitHub; leave them in place.

## 2. hangar-dev (control plane, hosts Infisical)

```sh
./apron init dev --name hangar-dev --runtime kiac --out ../gitops-hangar-dev \
  --repo-url https://github.com/<owner>/gitops-hangar-dev.git --scm-owner <owner> \
  --tower-cluster hangar-prod --create-repos --push
./apron fleet add --from ../gitops-hangar-dev --fleet ../gitops-hangar-dev/clusters.yaml
./apron up --out ../gitops-hangar-dev            # stops to ask for the hand-planted Secrets
```

1. Run the `kubectl create secret` commands `apron up` prints (repo creds; `infisical-secrets` and
   `infisical-bootstrap-credentials`), then `./apron up --out ../gitops-hangar-dev` again.
2. Add `/etc/hosts` lines for `*.hangar-dev.local` and the bare `hangar-dev.local` (Infisical's NodePort address
   for the other cluster); `./apron resume --out ../gitops-hangar-dev` prints them.
3. Infisical first run: open `http://infisical.hangar-dev.local`, note the org id, then
   `./apron fleet set-infisical --fleet ../gitops-hangar-dev/clusters.yaml --org-id <id> --url http://hangar-dev.local:31800/api`
   and push the cluster repo.
4. Re-plant secrets from your export (section 3) and create the universal-auth identity hangar-prod will use.
5. Manual syncs in the order `apron up` prints (`docs/after-up.md` in Apron).
6. Cluster identity: `./apron identity --out ../gitops-hangar-dev`, then publish the keys to this repo's
   `web/public/oidc/hangar-dev` (`hack/cluster-identity.sh publish`, see Apron `docs/cluster-identity.md`), merge,
   and wait until `https://hangarplatform.dev/oidc/hangar-dev/jwks.json` serves them.
7. Flip readiness flags in `clusters.yaml` once each is true (`cicdReady` after a pipeline runs; `autopilotReady`
   after autopilot's `tools/netpol_canary.py` passes), push, sync the cluster registry.
8. Re-point the cloudflared tunnel for the PaC webhook at the new node IP (NodePort 30860). The GitHub App's
   webhook URL stays the same.

## 3. Infisical keys to re-plant

Platform project **`glidepath-hangar-dev`**, env `shared`: `github-application-id`, `github-installation-id`,
`github-private-key`, `github-webhook-secret`, `provider-github-creds`, `provider-azure-creds` (optional),
`registry-credentials-dockerconfigjson`, `backstage-notify-token`, `anthropic-api-key`, `github-mcp-token`,
`provider-infisical-creds` (new identity), `relay-token-hangar-prod` (generate; must equal prod's relay token).

Platform project **`glidepath-hangar-prod`**, env `shared`: `github-application-id`, `github-installation-id`,
`github-private-key`, `registry-credentials-dockerconfigjson`, `anthropic-api-key`, `github-mcp-token`,
`platform-outcome-relay-token` (same value as dev's relay token).

Tower, project **`backstage-hangar-prod`**, env `prod`: the ten keys listed in the backstage repo's
`deploy/airframe/README.md` (OAuth id/secret, GitHub token, both Argo CD tokens minted fresh, notify token, GHCR
prune token, three break-glass keys).

App projects (`<app>-hangar-dev`, `<app>-hangar-prod`): re-plant from each app project's export as the walkthroughs
create them.

## 4. hangar-prod (workloads, Tower)

On the second MacBook, with the Apron checkout:

```sh
./apron init prod --name hangar-prod --runtime kind --out ../gitops-hangar-prod \
  --repo-url https://github.com/<owner>/gitops-hangar-prod.git --scm-owner <owner> \
  --fleet-hub hangar-dev --fleet-repo-url https://github.com/<owner>/gitops-hangar-dev.git \
  --tower-cluster hangar-prod --create-repos --push
./apron fleet add --from ../gitops-hangar-prod --fleet ../gitops-hangar-dev/clusters.yaml   # then push hangar-dev's repo
./apron up --out ../gitops-hangar-prod
```

1. Plant the repo creds and `crossplane-system/provider-infisical-creds` (the universal-auth identity from step 2.4),
   re-run `apron up`.
2. `/etc/hosts` for `*.hangar-prod.local`; manual syncs; `./apron identity --out ../gitops-hangar-prod --node-exec
   "docker exec -i <node>"` (or podman), publish to `web/public/oidc/hangar-prod`, merge; set `crossplaneReady`.
3. Cross-cluster wiring that lives outside Git: hangar-prod must reach `hangar-dev.local:31800` (Infisical) and the
   relay port; check the LAN IP and any port forwards on this Mac.

## 5. Tower as an app

Follow the backstage repo's `deploy/airframe/README.md`: onboard the `backstage` app by PR to hangar-dev's tenants
repo, commit the prod values, PR the ApplicationEnvironment, plant its Infisical keys, release. Before its first
start, set the GitHub OAuth App's homepage to `http://backstage.hangar-prod.local` and its callback to
`http://backstage.hangar-prod.local/api/auth/github/handler/frame`. Fill the three placeholders in the prod values
(`<hangar-dev-node-ip>`, `<hangar-dev-ca-data>`, `<hangar-dev-tenants-repo>`).

## 6. Outside Git (cloud targets only)

If you use AWS cloud targets: add IAM OIDC providers for the two new issuer URLs and update the Crossplane role's
trust (Airframe `docs/admin/cloud-credentials.md`).

## 7. Skyport

Airframe `docs/user/skyport-runbook.md`: configure the owner and cluster names once, clean up leftovers from the old
lab, then walk parts 1 to 7 (gate-api first as a smoke test). Replay every check with
`tools/walkthrough-runner --all --clusters ../gitops-hangar-dev/clusters.yaml`.

## Deferred until after the rebuild

- Namespaces `platform-catalog` and `platform-system`, and API groups `catalog.idp.io` / `secrets.idp.io`: Glidepath
  and Airframe depend on them; rename across repos later.
- Port Apron's templates to a kubara catalog (Apron roadmap v1).
