# Rebuilding the lab with Apron

Rebuild the two lab clusters as **hangar-dev** and **hangar-prod** with `apron`, then stand Skyport back up. Every
step is a command to paste. The names are this rebuild's choice: nothing in Apron, Airframe, Glidepath or Tower
depends on them.

**One name per cluster.** The name given to `apron init --name` is also the cluster's kubectl context, its record in
the fleet's `clusters.yaml`, its Infisical project stem (`glidepath-<name>`, `<app>-<name>`), its issuer
(`https://hangarplatform.dev/oidc/<name>`) and its hostname stem (`<service>.<name>.local`).

## Machines and variables

| | Mac A | Mac B |
|---|---|---|
| Cluster | hangar-dev (kiac): control plane, Infisical | hangar-prod (kind on podman): workloads, Tower |
| Old cluster | kiac `dev`, context `kiac-dev` | kind `prod`, context `kind-prod` |

That split is the lab's hardware, not a requirement. Paste this block into every new shell, on both Macs, after
filling in the four values:

```sh
export OWNER="<github-owner>"
export SRC=~/src                          # where the repos are checked out
export DEV_IP="<Mac A LAN IP>"            # on Mac A: ipconfig getifaddr en0
export PROD_IP="<Mac B LAN IP>"            # on Mac B: ipconfig getifaddr en0
export AWS_ACCOUNT="<12 digits>"          # only for ECS/Lambda targets; the old clusters.yaml has it under aws:
```

**How the clusters reach each other.** The old lab went through `192.168.1.78` and SSH tunnels. This rebuild makes
the paths explicit:

- Mac A forwards ports 80, 6443, 30880 and 31800 to the kiac node (step 2.4). Pods on hangar-prod then reach
  hangar-dev's gateway, API server, release relay and Infisical at `$DEV_IP`.
- Mac B publishes kind's port 80 on its LAN address, so hangar-dev's pods and Mac A's browser reach Tower at
  `$PROD_IP`.
- Apron's two settings that point across: `tower.hostAliasIP=$PROD_IP` on hangar-dev, and
  `fleet.hubAddress=$DEV_IP` on hangar-prod. Each becomes `hostAliases` entries on the pods that need them.

**Tools.** On both Macs: `kubectl`, `gh` (logged in), `jq`, `yq` (mikefarah), `argocd`, `python3` with PyYAML and
`ruamel.yaml`, and `git` with gitsign configured. Mac A also needs `kiac`, `container`, `socat`, `infisical` and
`aws`. Mac B needs `kind` and `podman`, with a rootful machine because it binds port 80:

```sh
brew install socat infisical/get-cli/infisical            # Mac A, if missing
pip3 install pyyaml ruamel.yaml                           # both Macs; ruamel keeps clusters.yaml's comments
podman machine stop; podman machine set --rootful; podman machine start     # Mac B, once
export KIND_EXPERIMENTAL_PROVIDER=podman APRON_CONTAINER_ENGINE=podman        # Mac B, every shell
```

**Checkouts.** On both Macs:

```sh
mkdir -p $SRC && cd $SRC
for r in apron airframe glidepath tower backstage hangar; do [ -d $r ] || gh repo clone $OWNER/$r; done
```

**Sync helper.** The infrastructure Applications have no automated sync on purpose. This syncs them one by one and
waits for each to be healthy (Argo CD core mode, no login):

```sh
sync() { local ctx=$1; shift; kubectl config set-context $ctx --namespace argocd >/dev/null
  for a in "$@"; do argocd app sync $a --core --kube-context $ctx --timeout 900 &&
    argocd app wait $a --core --kube-context $ctx --health --timeout 900 || { echo "stopped at $a"; return 1; }; done; }
```

## 0. Before teardown (old clusters still running)

### 0.1 Back up Infisical

Infisical starts fresh, so the export is the only copy of values that live nowhere else: the GitHub App private
key, the PATs, the Backstage OAuth secret and the Anthropic key. Mac A:

```sh
export OLD_INF=http://infisical.dev.kiac.local/api
infisical login --domain $OLD_INF -i
TOKEN=$(infisical user get token --plain --domain $OLD_INF)
mkdir -p ~/infisical-export && cd ~/infisical-export
curl -fsS -H "Authorization: Bearer $TOKEN" $OLD_INF/v1/workspace \
  | jq -r '.workspaces[] | "\(.id // ._id) \(.slug) \([.environments[]?.slug] | join(","))"' > projects.txt
cat projects.txt                                        # id slug envs; fill in envs by hand if a line has none
while read id slug envs; do for env in ${envs//,/ }; do
  infisical export --domain $OLD_INF --projectId $id --env $env --format yaml --output-file "$slug.$env.yaml"
done; done < projects.txt
ls -l                                                   # one file per project and environment
```

`export` reads the root folder only. If a project uses folders, export each one again with `--path /<folder>`.
Encrypt the export and delete the plaintext:

```sh
cd ~ && tar czf - infisical-export | openssl enc -aes-256-cbc -pbkdf2 -salt -out infisical-export.tgz.enc
rm -rf ~/infisical-export
# later, to read it: openssl enc -d -aes-256-cbc -pbkdf2 -in ~/infisical-export.tgz.enc | tar xzf - -C ~
```

Keep `infisical-export.tgz.enc` offline. Sections 2, 4 and 5 restore from it.

### 0.2 Delete the cloud resources the old clusters own

`smoke-ecs` (`AwsEcsTarget`: VPC, subnets, ECS cluster and service, ECR repository, deploy role), `customs-api`
(`deployTarget: aws-ecs`), `smoke-fn` (`AwsLambdaTarget`, dev and prod) and `smoke-az-fn` (Azure) are real cloud
resources. A teardown first leaves them running and billing, with nothing left to manage them. Their GitHub repos
are safe: no app composition deletes a repo.

Their requests are already gone from `gitops-cluster-dev-tenants` (2026-10-17, "deleting aws apps", "deleting azure
function"). Onboarding then re-added a `secretstore.yaml` for all four, though, which means their XRs were still on
the cluster at that point. The xr-requests ApplicationSet doesn't prune. The commands below find what is left and
finish the job.

Mac A. First stop both Argo CD instances so they don't recreate what you delete:

```sh
kubectl --context kiac-dev -n argocd scale statefulset --all --replicas=0
kubectl --context kiac-dev -n argocd-apps scale statefulset --all --replicas=0
kubectl --context kiac-dev get awsecstarget,awslambdatarget,azurecontainerapptarget -A -o json | jq -r '.items[] |
  "\(.metadata.namespace)  \(.kind)/\(.metadata.name)  parent: \((.metadata.ownerReferences // [])[0] | if . then "\(.kind)/\(.name)" else "none" end)"'
# a target with a parent is recomposed by it, so delete the parent too (here: GoApplication customs-api, AzureFunction smoke-az-fn)
xdel() { kubectl --context kiac-dev -n "$(kubectl --context kiac-dev get $1 -A -o json | jq -r --arg n $2 '.items[]|select(.metadata.name==$n)|.metadata.namespace')" delete $1 $2 --wait=false; }
xdel goapplication customs-api; xdel azurefunction smoke-az-fn
kubectl --context kiac-dev delete awsecstarget,awslambdatarget,azurecontainerapptarget --all -A --wait=false
watch -n 15 "kubectl --context kiac-dev get managed 2>/dev/null | grep -Ei 'ecs|ec2|ecr|lambda|iam|azure|resourcegroup'"
```

When the watch shows nothing, check AWS directly:

```sh
aws resourcegroupstaggingapi get-resources --tag-filters Key=crossplane-kind --query 'ResourceTagMappingList[].ResourceARN'
aws iam list-roles --query "Roles[?starts_with(RoleName,'glidepath-deploy')].RoleName"
aws ecs list-clusters
```

All three should come back empty, except a resource you created by hand. On Azure, check the target's resource
group in the portal.

### 0.3 Merge and tag, in order

Every branch is pushed and rebased onto main as of 2026-10-17. Mac A, from `$SRC`. For each PR, wait for green and
then merge:

```sh
pr() { gh pr view -R $OWNER/$1 $2 >/dev/null 2>&1 ||
    { gh pr create -R $OWNER/$1 --base main --head $2 --title "$2" --body "Lab rebuild (hangar docs/rebuild-lab.md)." && sleep 30; } || return 1
  { gh pr checks -R $OWNER/$1 $2 --watch || { read -p "$1/$2: checks not green, or none. Merge anyway? [y/N] " a; [ "$a" = y ]; }; } &&
  gh pr merge -R $OWNER/$1 $2 --merge; }
```

1. **airframe**, three PRs in this order:

   ```sh
   pr airframe no-hardcoded-cluster-names        # already PR #99
   pr airframe backstage-on-airframe
   pr airframe skyport-walkthroughs
   cd $SRC/airframe && git switch main && git pull --ff-only
   git tag -a v0.3.154 -m "No hardcoded cluster names; Tower on Airframe; Skyport walkthroughs" && git push origin v0.3.154
   ```

   v0.3.153 is the last tag as of 2026-10-17; use the next free one if v0.3.154 is taken by then.
2. **glidepath:** `pr glidepath no-hardcoded-cluster-names`. Apron pins Glidepath to `main`, so no tag is needed.
3. **tower**, then release it (`RELEASING.md`):

   ```sh
   pr tower no-hardcoded-cluster-names
   cd $SRC/tower && git switch main && git pull --ff-only
   npm pkg set version=0.73.3 && yarn install && yarn tsc && yarn build      # tsc writes dist-types/, which build packages
   git add package.json dist && git commit -m "release: v0.73.3 (cluster names from app-config)"
   git tag v0.73.3 && git push origin main --tags
   ```

4. **backstage:** bump Tower on the branch, then merge it:

   ```sh
   cd $SRC/backstage && git switch airframe-app && git pull --ff-only
   sed -i '' 's|"@jfillman/tower": "jfillman/tower#v[0-9.]*"|"@jfillman/tower": "jfillman/tower#v0.73.3"|' packages/app/package.json
   yarn install && git commit -am "Bump Tower to v0.73.3" && git push
   cd $SRC && pr backstage airframe-app
   ```

5. **apps**, on `dex-tokens`. Merge boarding-api first, and run flight-api's tests first: it was never compiled here.

   ```sh
   pr boarding-api dex-tokens
   gh repo clone $OWNER/flight-api /tmp/flight-api -- -b dex-tokens && (cd /tmp/flight-api && ./test.sh) && pr flight-api dex-tokens
   pr baggage-api dex-tokens
   ```

6. **apron:** pin the new Airframe tag on the branch, then merge it:

   ```sh
   cd $SRC/apron && git switch apron-up && git pull --ff-only
   yq -i '.versions.airframe.catalog = "v0.3.154" | .versions.airframe.clusterRegistry = "v0.3.154" | .versions.airframe.defaultChart = "v0.3.154"' versions.yaml
   bash tests/run.sh && bash tests/cli/test_cli.sh && git commit -am "Pin Airframe v0.3.154" && git push
   cd $SRC && pr apron apron-up
   cd $SRC/apron && git switch main && git pull --ff-only
   ```

7. **hangar:** `pr hangar rebuild-runbook`.

Then pull `main` of apron, airframe and hangar on Mac B too:

```sh
for r in apron airframe hangar; do git -C $SRC/$r switch main && git -C $SRC/$r pull --ff-only; done
```

### 0.4 Make function-dex public

hangar-prod pulls `ghcr.io/$OWNER/function-dex` without credentials. Open
`https://github.com/users/$OWNER/packages/container/function-dex/settings`, then Danger Zone, Change visibility,
Public. Check it:

```sh
curl -fsS "https://ghcr.io/token?scope=repository:$OWNER/function-dex:pull" | jq -r .token | \
  xargs -I{} curl -fsS -H "Authorization: Bearer {}" https://ghcr.io/v2/$OWNER/function-dex/tags/list | jq .
```

## 1. Teardown (point of no return)

```sh
kiac delete cluster --name dev                         # Mac A
kind get clusters && kind delete cluster --name prod   # Mac B (podman provider exported)
```

Archive the old cluster and tenants repos. Archived repos stay readable:

```sh
for r in gitops-cluster-dev gitops-cluster-dev-tenants gitops-cluster-kind-prod gitops-cluster-kind-prod-tenants; do
  gh repo archive $OWNER/$r --yes; done
kubectl config delete-context kiac-dev; kubectl config delete-context kind-prod      # on whichever Mac has each
```

## 2. hangar-dev (Mac A)

### 2.1 Init: renders the repo and creates both GitHub repos

```sh
cd $SRC/apron
./apron init dev --name hangar-dev --runtime kiac --out $SRC/gitops-hangar-dev \
  --repo-url https://github.com/$OWNER/gitops-hangar-dev.git --scm-owner $OWNER \
  --tower-cluster hangar-prod --set tower.hostAliasIP=$PROD_IP \
  --set components.cloudTargets=true --set "aws.accountId=\"$AWS_ACCOUNT\"" \
  --create-repos --push
```

Without ECS or Lambda targets, drop the two `cloudTargets`/`aws` flags. The tenants repo is
`gitops-hangar-dev-tenants`.

### 2.2 The fleet file

```sh
./apron fleet add --from $SRC/gitops-hangar-dev --fleet $SRC/gitops-hangar-dev/clusters.yaml
```

For cloud targets, add the account block. `fleet add` doesn't write it, and without it every `AwsEcsTarget` and
`AwsLambdaTarget` waits:

```sh
yq -i ".aws = {\"accountId\": \"$AWS_ACCOUNT\", \"permissionsBoundaryPolicy\": \"HangarCloudTargetBoundary\"}" $SRC/gitops-hangar-dev/clusters.yaml
yq -i '.aws.accountId style="double"' $SRC/gitops-hangar-dev/clusters.yaml
git -C $SRC/gitops-hangar-dev add clusters.yaml && git -C $SRC/gitops-hangar-dev commit -m "Fleet: hangar-dev" && git -C $SRC/gitops-hangar-dev push
```

### 2.3 Up, plant the bootstrap Secrets, up again

```sh
./apron up --out $SRC/gitops-hangar-dev --yes
```

It creates the cluster (`kiac create cluster --name hangar-dev --workers 0 --cni cilium --kernel full --cpus 10
--cp-memory 32G`), renames the context to `hangar-dev`, installs Argo CD, then stops at three missing Secrets. Run
the three commands it prints, typing the values yourself:

- `argocd-repo-creds-$OWNER`: username `$OWNER`, password a PAT that can read the private repos.
- `infisical-secrets`: generate the values as the command says (`openssl rand -hex 16`, `openssl rand -base64 32`).
  **Losing `ENCRYPTION_KEY` loses every secret**, so save it in your password manager.
- `infisical-bootstrap-credentials`: the first admin's email and a generated password. This is your Infisical login.

Then continue:

```sh
./apron up --out $SRC/gitops-hangar-dev --yes          # applies the root app-of-apps
```

### 2.3a Pod limit (kiac)

kiac has no kubelet setting, so its node starts at the kubelet default of 110 pods. The dev stack needs more than
that, and past the limit new pods sit in `Pending` with `Too many pods`. `apron up` and `apron resume` raise it to
`runtime.kiac.maxPods` (250) from Apron's `kiac-max-pods` change on. On a cluster built before that, or to check:

```sh
DEV_NODE=$(kubectl --context hangar-dev get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl --context hangar-dev get node $DEV_NODE -o jsonpath='{.status.capacity.pods}{"\n"}'      # want 250
container exec -i $DEV_NODE sh -c "f=/var/lib/kubelet/config.yaml; if grep -q '^maxPods:' \$f; then sed -i 's/^maxPods:.*/maxPods: 250/' \$f; else echo 'maxPods: 250' >>\$f; fi; systemctl restart kubelet"
sleep 20; kubectl --context hangar-dev get node $DEV_NODE -o jsonpath='{.status.capacity.pods}{"\n"}'
```

Recheck after every `kiac resume` until you've seen the value survive one.

### 2.4 Reach the cluster from Mac A and the LAN

kiac's node IP changes on every VM boot. Traefik listens on NodePort 30080 because Apron never uses kiac's own
gateway, so port 80 is forwarded explicitly:

```sh
NODE_IP=$(kubectl --context hangar-dev get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
DEV_NODE=$(kubectl --context hangar-dev get nodes -o jsonpath='{.items[0].metadata.name}'); echo $NODE_IP $DEV_NODE
sudo pkill -f 'socat TCP-LISTEN' ; for p in 80:30080 443:30443 6443:6443 30880:30880 31800:31800; do
  sudo nohup socat TCP-LISTEN:${p%%:*},fork,reuseaddr TCP:$NODE_IP:${p##*:} >/dev/null 2>&1 &
done
sudo sh -c "sed -i '' '/# hangar-lab/d' /etc/hosts; cat >> /etc/hosts" <<EOF
127.0.0.1 argocd.hangar-dev.local argocd-apps.hangar-dev.local infisical.hangar-dev.local tekton.hangar-dev.local rekor.hangar-dev.local grafana.hangar-dev.local minio-console.hangar-dev.local minio.hangar-dev.local hangar-dev.local # hangar-lab
$PROD_IP argocd.hangar-prod.local argocd-apps.hangar-prod.local backstage.hangar-prod.local # hangar-lab
EOF
curl -sI http://argocd.hangar-dev.local | head -1      # HTTP/1.1 200 or 307 once Argo CD's route is synced
```

After any `kiac resume` (or `./apron resume --out $SRC/gitops-hangar-dev`), rerun the first four lines: the node IP
has probably changed. Note `$DEV_NODE` for section 5. Kubernetes puts it in the API server certificate.

### 2.5 First syncs

```sh
sync hangar-dev crossplane external-secrets infisical cert-manager argo-rollouts cloudnative-pg \
  mongodb-kubernetes rabbitmq-operators sloth
kubectl --context hangar-dev -n infisical rollout status deploy --timeout=10m
curl -fsS http://infisical.hangar-dev.local/api/status | jq .
```

### 2.6 Infisical first run

1. Log in at `http://infisical.hangar-dev.local` with the bootstrap admin from 2.3. Organization `hangar` already
   exists. Copy its ID from Organization Settings.
2. Record it in the fleet file:

   ```sh
   cd $SRC/apron
   ./apron fleet set-infisical --fleet $SRC/gitops-hangar-dev/clusters.yaml --org-id <org-id> \
     --url http://hangar-dev.local:31800/api \
     --in-cluster-url http://infisical-infisical-standalone-infisical.infisical.svc.cluster.local:8080/api
   git -C $SRC/gitops-hangar-dev commit -am "Fleet: Infisical org" && git -C $SRC/gitops-hangar-dev push
   ```

3. Create two machine identities, under Organization, Access Control, Identities, Create. Give both the org role
   **Admin** and Authentication **Universal Auth**, then Create Client Secret:
   - `hangar-dev-crossplane`, for provider-infisical on hangar-dev;
   - `hangar-prod-crossplane`, for provider-infisical on hangar-prod (section 4).
4. hangar-dev's Crossplane needs its credential before it can create the project it would normally read the
   credential from, so plant the first copy by hand:

   ```sh
   umask 077; cat > /tmp/pic.json        # type, then Ctrl-D:
   {"host": "http://infisical-infisical-standalone-infisical.infisical.svc.cluster.local:8080", "client_id": "<hangar-dev-crossplane id>", "client_secret": "<its secret>"}
   kubectl --context hangar-dev create namespace crossplane-system --dry-run=client -o yaml | kubectl --context hangar-dev apply -f -
   kubectl --context hangar-dev -n crossplane-system create secret generic provider-infisical-creds --from-file=credentials=/tmp/pic.json
   ```

   Keep `/tmp/pic.json` until 2.7; it is planted in Infisical there.

### 2.7 Plant hangar-dev's platform keys

Glidepath's control plane creates the project `glidepath-hangar-dev` (environment `shared`) once Crossplane has the
credential. Wait for it:

```sh
export INF=http://infisical.hangar-dev.local/api
infisical login --domain $INF -i
until kubectl --context hangar-dev get secretstores.catalog.hangar.io -A 2>/dev/null | grep -q 'glidepath-hangar-dev.*True'; do sleep 20; done
TOKEN=$(infisical user get token --plain --domain $INF)
pid() { curl -fsS -H "Authorization: Bearer $TOKEN" $INF/v1/workspace | jq -r --arg s $1 '.workspaces[]|select(.slug==$s)|.id // ._id'; }
DEV_PID=$(pid glidepath-hangar-dev); echo $DEV_PID
```

Restore the keys that carry over from the old `platform-cicd-kind-dev` project, then add the new ones:

```sh
openssl enc -d -aes-256-cbc -pbkdf2 -in ~/infisical-export.tgz.enc | tar xzf - -C ~
cd ~/infisical-export
yq 'with_entries(select(.key | test("^(github-application-id|github-installation-id|github-private-key|github-webhook-secret|provider-github-creds|provider-azure-creds|registry-credentials-dockerconfigjson|backstage-notify-token|anthropic-api-key|github-mcp-token)$")))' \
  platform-cicd-kind-dev.shared.yaml > dev-shared.yaml
yq 'keys' dev-shared.yaml                              # names only; expect up to 10
infisical secrets set --domain $INF --projectId $DEV_PID --env shared --file dev-shared.yaml
RELAY=$(openssl rand -hex 32)
infisical secrets set --domain $INF --projectId $DEV_PID --env shared "relay-token-hangar-prod=$RELAY" \
  "provider-infisical-creds=$(cat /tmp/pic.json)" >/dev/null
echo "$RELAY" > ~/.relay-token-hangar-prod && chmod 600 ~/.relay-token-hangar-prod; rm /tmp/pic.json
infisical secrets get github-private-key --domain $INF --projectId $DEV_PID --env shared --plain | head -1   # -----BEGIN ... KEY-----
infisical secrets get github-private-key --domain $INF --projectId $DEV_PID --env shared --plain | wc -l     # more than 1
```

If the key came back as one line with literal `\n`s (the export escapes newlines for multi-line-encoded secrets), set
it again from a file:

```sh
yq -r '.["github-private-key"]' dev-shared.yaml | perl -pe 's/\\n/\n/g' > /tmp/k.pem
infisical secrets set --domain $INF --projectId $DEV_PID --env shared github-private-key=@/tmp/k.pem >/dev/null; rm /tmp/k.pem
```

If `kubectl --context hangar-dev -n crossplane-system get externalsecret provider-infisical-creds` reports an
ownership error rather than `SecretSynced`, delete the hand-made Secret and External Secrets recreates it from
Infisical: `kubectl --context hangar-dev -n crossplane-system delete secret provider-infisical-creds`.

### 2.8 The rest of the syncs

```sh
sync hangar-dev argocd-platform-repo-creds cluster-registry minio-secrets minio kube-prometheus-stack loki tempo \
  thanos otel-collector holmesgpt-creds holmesgpt
argocd app list --core --kube-context hangar-dev | grep -v 'Synced  *Healthy'     # what is still not green
```

### 2.9 Cluster identity: issuer, then published keys

```sh
cd $SRC/apron && ./apron identity --out $SRC/gitops-hangar-dev            # restarts the API server once (~1 min)
cd $SRC/hangar && git switch -c oidc-hangar-dev origin/main
bash $SRC/apron/hack/cluster-identity.sh publish --context hangar-dev \
  --issuer https://hangarplatform.dev/oidc/hangar-dev --out web/public/oidc/hangar-dev
git rm -rq web/public/oidc/kiac-dev web/public/oidc/kind-prod
git add web/public/oidc && git commit -m "OIDC: hangar-dev issuer; drop the old clusters'" && git push -u origin oidc-hangar-dev
cd $SRC && pr hangar oidc-hangar-dev
until curl -fsS https://hangarplatform.dev/oidc/hangar-dev/.well-known/openid-configuration | jq -e '.issuer=="https://hangarplatform.dev/oidc/hangar-dev"'; do sleep 30; done
```

Update the table in `web/public/oidc/README.md` to name hangar-dev and hangar-prod in the same PR.

### 2.10 Webhook tunnel

Point the cloudflared tunnel for `pac-webhook.hangarplatform.dev` at the new node. Pipelines-as-Code listens on
NodePort 30860:

```sh
sed -i '' -E "s#service: http://[0-9.]+:30860#service: http://$NODE_IP:30860#" ~/.cloudflared/config.yml
grep 30860 ~/.cloudflared/config.yml
sudo launchctl kickstart -k system/com.cloudflare.cloudflared 2>/dev/null || cloudflared tunnel run   # however you run it
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://pac-webhook.hangarplatform.dev    # anything but 502/530
```

The GitHub App's webhook URL stays the same. Check that its webhook secret is the restored `github-webhook-secret`.

### 2.11 Readiness flags

Glidepath builds images with rootless BuildKit (ADR-0026), which needs three things from the dev cluster. Apron sets
up all three, so these only confirm them before `cicdReady` lets apps onboard:

```sh
kubectl --context hangar-dev -n kube-system rollout status ds/binfmt --timeout=5m
container exec -i $DEV_NODE ls /proc/sys/fs/binfmt_misc/ | grep -c qemu          # handlers registered (amd64 builds on arm64)
container exec -i $DEV_NODE grep -i seccompDefault /var/lib/kubelet/config.yaml   # no output, or false
```

`-cicd` namespaces get Pod Security `baseline` from Glidepath's tenant-onboarding ApplicationSet. `restricted`
would break rootlesskit, and `seccompDefault: true` would need a Localhost seccomp profile on the build step
(Glidepath `docs/admin/rootless-builds.md`). The first real build is Tower's (5.7).

Set each flag only after checking it live:

```sh
argocd app list --core --kube-context hangar-dev | grep -i glidepath           # all Synced/Healthy -> cicdReady
F=$SRC/gitops-hangar-dev/clusters.yaml
yq -i '(.clusters[] | select(.name=="hangar-dev")).airframe.cicdReady = true' $F
yq -i '(.clusters[] | select(.name=="hangar-dev")).airframe.crossplaneReady = true' $F   # providers Healthy: kubectl --context hangar-dev get providers
git -C $SRC/gitops-hangar-dev commit -am "hangar-dev: cicdReady, crossplaneReady" && git -C $SRC/gitops-hangar-dev push
sync hangar-dev cluster-registry
kubectl --context hangar-dev -n crossplane-system get configmap hangar-dev -o jsonpath='{.data}' | jq .
```

`autopilotReady` waits for autopilot's `tools/netpol_canary.py`. Skyport doesn't need it.

### 2.12 AWS (cloud targets only)

The IAM role and OIDC provider are per cluster name, so hangar-dev gets new ones. The permission policy and boundary
already exist in the account:

```sh
ISSUER=hangarplatform.dev/oidc/hangar-dev
aws iam create-open-id-connect-provider --url "https://$ISSUER" --client-id-list sts.amazonaws.com
cat > /tmp/trust.json <<EOF
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Federated":"arn:aws:iam::$AWS_ACCOUNT:oidc-provider/$ISSUER"},
 "Action":"sts:AssumeRoleWithWebIdentity",
 "Condition":{"StringEquals":{"$ISSUER:aud":"sts.amazonaws.com"},
              "StringLike":{"$ISSUER:sub":"system:serviceaccount:crossplane-system:provider-aws-*"}}}]}
EOF
aws iam create-role --role-name hangar-crossplane-hangar-dev --assume-role-policy-document file:///tmp/trust.json \
  --tags Key=hangar.io/component,Value=hangar-crossplane
aws iam attach-role-policy --role-name hangar-crossplane-hangar-dev \
  --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/HangarCrossplaneCloudTargets
SA=$(kubectl --context hangar-dev -n crossplane-system get sa -o name | grep provider-aws-ecr | cut -d/ -f2)
aws sts assume-role-with-web-identity --no-sign-request --region us-east-1 \
  --role-arn arn:aws:iam::$AWS_ACCOUNT:role/hangar-crossplane-hangar-dev --role-session-name check \
  --web-identity-token "$(kubectl --context hangar-dev -n crossplane-system create token $SA --audience sts.amazonaws.com --duration 10m)" \
  --query AssumedRoleUser.Arn --output text
```

Once nothing uses them, delete the old cluster's role and provider:
`aws iam list-open-id-connect-providers`, then `aws iam delete-open-id-connect-provider --open-id-connect-provider-arn <kiac-dev's>`.
For the role, `aws iam detach-role-policy --role-name hangar-crossplane-kiac-dev --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/HangarCrossplaneCloudTargets && aws iam delete-role --role-name hangar-crossplane-kiac-dev`.

## 3. Infisical keys at a glance

| Project, env | Key | Source |
|---|---|---|
| `glidepath-hangar-dev`, `shared` | `github-application-id`, `github-installation-id`, `github-private-key`, `github-webhook-secret`, `provider-github-creds`, `provider-azure-creds` (optional), `registry-credentials-dockerconfigjson`, `backstage-notify-token`, `anthropic-api-key`, `github-mcp-token` | export of `platform-cicd-kind-dev` (2.7) |
| | `provider-infisical-creds` | identity `hangar-dev-crossplane` (2.6) |
| | `relay-token-hangar-prod` | generated (2.7) |
| `glidepath-hangar-prod`, `shared` | `github-application-id`, `github-installation-id`, `github-private-key`, `registry-credentials-dockerconfigjson`, `anthropic-api-key`, `github-mcp-token` | export of `platform-cicd-kind-prod` (4.4) |
| | `platform-outcome-relay-token` | the same value as `relay-token-hangar-prod` (4.4) |
| `backstage-hangar-prod`, `prod` | ten keys | section 5.6 |
| `<app>-hangar-dev`, `<app>-hangar-prod` | per app | that app's export, when its walkthrough creates the project. Include `customs-api` and `smoke-ecs` if you recreate them |

## 4. hangar-prod (Mac B)

### 4.1 Init and fleet

```sh
cd $SRC/apron && gh repo clone $OWNER/gitops-hangar-dev $SRC/gitops-hangar-dev 2>/dev/null; git -C $SRC/gitops-hangar-dev pull --ff-only
./apron init prod --name hangar-prod --runtime kind --out $SRC/gitops-hangar-prod \
  --repo-url https://github.com/$OWNER/gitops-hangar-prod.git --scm-owner $OWNER \
  --fleet-hub hangar-dev --fleet-repo-url https://github.com/$OWNER/gitops-hangar-dev.git \
  --tower-cluster hangar-prod --set fleet.hubAddress=$DEV_IP --create-repos --push
./apron fleet add --from $SRC/gitops-hangar-prod --fleet $SRC/gitops-hangar-dev/clusters.yaml
git -C $SRC/gitops-hangar-dev commit -am "Fleet: hangar-prod" && git -C $SRC/gitops-hangar-dev push
```

The record gets `glidepath.relaySecretName: cluster-hangar-prod-relay-token`. Back on Mac A, sync it so the release
relay knows hangar-prod: `git -C $SRC/gitops-hangar-dev pull --ff-only && sync hangar-dev cluster-registry`.

### 4.2 Up

Check the cross-machine paths first. Both should answer:

```sh
curl -fsS http://$DEV_IP:31800/api/status | jq -r .message      # Infisical on hangar-dev, through Mac A's forward
curl -s -o /dev/null -w '%{http_code}\n' http://$DEV_IP:30880/   # the release relay (any HTTP code is fine)
cd $SRC/apron && ./apron up --out $SRC/gitops-hangar-prod --yes
```

It creates the kind cluster with Calico v3.29.1 and stops at two Secrets. Run the printed commands:

- `argocd-repo-creds-$OWNER`: same as on hangar-dev.
- `crossplane-system/provider-infisical-creds`: the `hangar-prod-crossplane` identity, with
  `{"host": "http://hangar-dev.local:31800", "client_id": "...", "client_secret": "..."}`. hangar-prod's pods
  resolve `hangar-dev.local` to `$DEV_IP` through the hostAliases from `fleet.hubAddress`.

```sh
./apron up --out $SRC/gitops-hangar-prod --yes
sudo sh -c "sed -i '' '/# hangar-lab/d' /etc/hosts; cat >> /etc/hosts" <<EOF
127.0.0.1 argocd.hangar-prod.local argocd-apps.hangar-prod.local backstage.hangar-prod.local # hangar-lab
$DEV_IP hangar-dev.local argocd.hangar-dev.local argocd-apps.hangar-dev.local infisical.hangar-dev.local # hangar-lab
EOF
```

### 4.3 Syncs

```sh
sync hangar-prod crossplane external-secrets cert-manager argo-rollouts cloudnative-pg mongodb-kubernetes \
  rabbitmq-operators sloth airframe-service-catalog
```

### 4.4 Plant hangar-prod's platform keys (Mac A)

hangar-prod's SecretStore XR creates `glidepath-hangar-prod` in the hub's Infisical. In a new shell on Mac A, rerun
the `export INF`, `TOKEN=` and `pid()` lines from 2.7 first.

```sh
until kubectl --context hangar-prod -n glidepath-secrets get secretstores.catalog.hangar.io glidepath-hangar-prod 2>/dev/null | grep -q True; do sleep 20; done   # on Mac B
# Mac A:
PROD_PID=$(pid glidepath-hangar-prod); echo $PROD_PID
cd ~/infisical-export
yq 'with_entries(select(.key | test("^(github-application-id|github-installation-id|github-private-key|registry-credentials-dockerconfigjson|anthropic-api-key|github-mcp-token)$")))' \
  platform-cicd-kind-prod.shared.yaml > prod-shared.yaml
infisical secrets set --domain $INF --projectId $PROD_PID --env shared --file prod-shared.yaml
infisical secrets set --domain $INF --projectId $PROD_PID --env shared "platform-outcome-relay-token=$(cat ~/.relay-token-hangar-prod)" >/dev/null
infisical secrets get github-private-key --domain $INF --projectId $PROD_PID --env shared --plain | wc -l     # more than 1, as in 2.7
```

Then on Mac B:

```sh
sync hangar-prod argocd-platform-repo-creds cluster-registry kube-prometheus-stack holmesgpt-creds holmesgpt
argocd app list --core --kube-context hangar-prod | grep -v 'Synced  *Healthy'
```

### 4.5 Identity, and the hub's trust in it

On Mac B:

```sh
cd $SRC/apron && ./apron identity --out $SRC/gitops-hangar-prod --node-exec "podman exec -i hangar-prod-control-plane"
cd $SRC/hangar && git switch -c oidc-hangar-prod origin/main
bash $SRC/apron/hack/cluster-identity.sh publish --context hangar-prod \
  --issuer https://hangarplatform.dev/oidc/hangar-prod --out web/public/oidc/hangar-prod
git add web/public/oidc && git commit -m "OIDC: hangar-prod issuer" && git push -u origin oidc-hangar-prod
cd $SRC && pr hangar oidc-hangar-prod
until curl -fsS https://hangarplatform.dev/oidc/hangar-prod/.well-known/openid-configuration | jq -e .issuer; do sleep 30; done
```

On Mac A, make hangar-dev's API server trust hangar-prod's issuer, which Tower reads and writes through:

```sh
git -C $SRC/gitops-hangar-dev pull --ff-only
bash $SRC/apron/hack/cluster-identity.sh trust --context hangar-dev --node-exec "container exec -i $DEV_NODE" \
  --authn-config $SRC/gitops-hangar-dev/00-bootstrap/cluster-identity/authentication-config.yaml
```

### 4.6 crossplaneReady

```sh
kubectl --context hangar-prod get providers,xrd | grep -v 'True.*True'        # nothing unhealthy
F=$SRC/gitops-hangar-dev/clusters.yaml       # Mac A
yq -i '(.clusters[] | select(.name=="hangar-prod")).airframe.crossplaneReady = true' $F
git -C $SRC/gitops-hangar-dev commit -am "hangar-prod: crossplaneReady" && git -C $SRC/gitops-hangar-dev push
sync hangar-dev cluster-registry                                       # Mac A
sync hangar-prod cluster-registry                                      # Mac B
```

## 5. Tower as an app (Mac A unless noted)

This follows the backstage repo's `deploy/airframe/README.md`, with the commands spelled out.

### 5.1 GitHub OAuth App

Under `https://github.com/settings/developers`, OAuth Apps, Tower's app: set the Homepage URL to
`http://backstage.hangar-prod.local` and the callback to
`http://backstage.hangar-prod.local/api/auth/github/handler/frame`. Mac A's browser reaches it on `$PROD_IP:80`, so
no port appears in either URL.

### 5.2 Onboard the app (hangar-dev's tenants repo)

```sh
gh repo clone $OWNER/gitops-hangar-dev-tenants $SRC/gitops-hangar-dev-tenants && cd $SRC/gitops-hangar-dev-tenants
git switch -c onboard-backstage
mkdir -p tenants/backstage/xr-requests
cp $SRC/backstage/deploy/airframe/tenants/backstage/xr-requests/backstage.yaml tenants/backstage/xr-requests/
$SRC/airframe/tools/airframe-validate --xr tenants/backstage/xr-requests/backstage.yaml
git add tenants && git commit -m "Onboard backstage (Tower)" && git push -u origin onboard-backstage
cd $SRC && pr gitops-hangar-dev-tenants onboard-backstage
kubectl --context hangar-dev -n app-backstage-cicd wait nodejsapplication/backstage --for=condition=DevClusterReady --timeout=30m
kubectl --context hangar-dev -n app-backstage-cicd wait nodejsapplication/backstage --for=condition=CicdOnboarded --timeout=30m
gh pr list -R $OWNER/backstage; gh pr list -R $OWNER/gitops-backstage     # merge the .tekton onboarding-resync PRs
gh api repos/$OWNER/backstage/contents/cicd.yaml --jq .content | base64 -d | head -20   # still Tower's cicd.yaml, not the starter
```

### 5.3 Seed the prod values

```sh
CA=$(kubectl config view --raw --minify --context hangar-dev -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')
gh repo clone $OWNER/gitops-backstage $SRC/gitops-backstage 2>/dev/null; cd $SRC/gitops-backstage && git pull --ff-only
git switch -c hangar-prod-values && mkdir -p hangar-prod/prod
sed -e "s|<hangar-dev-node-ip>|$DEV_IP|" -e "s|<hangar-dev-ca-data>|$CA|" -e "s|<hangar-dev-tenants-repo>|gitops-hangar-dev-tenants|" \
  -e "s|hangar-dev-control-plane|$DEV_NODE|g" \
  $SRC/backstage/deploy/airframe/gitops-backstage/hangar-prod/prod/values.yaml > hangar-prod/prod/values.yaml
grep -n '<' hangar-prod/prod/values.yaml | grep -v '^[0-9]*:\s*#'      # no placeholders left
$SRC/airframe/tools/airframe-validate --cluster hangar-prod hangar-prod/prod/values.yaml
git add hangar-prod && git commit -m "Tower: prod values on hangar-prod" && git push -u origin hangar-prod-values
cd $SRC && pr gitops-backstage hangar-prod-values
```

The `$DEV_NODE` substitution matters only if kiac named the node something other than `hangar-dev-control-plane`.
The API server's certificate carries the node's real name.

### 5.4 Create the environment

```sh
cd $SRC/gitops-hangar-dev-tenants && git switch main && git pull --ff-only && git switch -c backstage-prod-env
cp $SRC/backstage/deploy/airframe/tenants/backstage/xr-requests/backstage-hangar-prod-prod.yaml tenants/backstage/xr-requests/
$SRC/airframe/tools/airframe-validate --xr tenants/backstage/xr-requests/backstage-hangar-prod-prod.yaml
git add tenants && git commit -m "Tower: prod environment on hangar-prod" && git push -u origin backstage-prod-env
cd $SRC && pr gitops-hangar-dev-tenants backstage-prod-env
for c in ClusterReady AppResolved; do
  kubectl --context hangar-dev -n app-backstage-cicd wait applicationenvironment/backstage-hangar-prod-prod --for=condition=$c --timeout=30m; done
until [ -n "$(pid backstage-hangar-prod)" ]; do sleep 20; done; TOWER_PID=$(pid backstage-hangar-prod)
```

### 5.5 Mint the tokens that can't be restored

```sh
argocd login argocd-apps.hangar-dev.local --plaintext --grpc-web --username admin \
  --password "$(kubectl --context hangar-dev -n argocd-apps get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
DEV_ARGO=$(argocd account generate-token --account backstage --grpc-web)
argocd login argocd-apps.hangar-prod.local --plaintext --grpc-web --username admin \
  --password "$(kubectl --context hangar-prod -n argocd-apps get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
PROD_ARGO=$(argocd account generate-token --account backstage --grpc-web)
cat > /tmp/bg-policy.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:PutObject","s3:GetObject","s3:GetObjectVersion"],"Resource":["arn:aws:s3:::tower-breakglass/*","arn:aws:s3:::tower-breakglass-v2/*"]}]}
EOF
kubectl --context hangar-dev -n observability run mc-breakglass --rm -i --restart=Never \
  --image=quay.io/minio/minio:RELEASE.2024-12-18T13-15-44Z --command -- sh -c \
  "cat > /tmp/p.json; mc alias set m http://minio:9000 admin minioadmin123 >/dev/null && mc admin user svcacct add m admin --policy /tmp/p.json --json" \
  < /tmp/bg-policy.json > /tmp/bg-key.json
MINIO_AK=$(jq -r .accessKey /tmp/bg-key.json); MINIO_SK=$(jq -r .secretKey /tmp/bg-key.json); rm /tmp/bg-key.json /tmp/bg-policy.json
ANCHOR=$(openssl ecparam -name prime256v1 -genkey -noout | openssl pkcs8 -topk8 -nocrypt)
```

`argocd-apps.hangar-prod.local` resolves on Mac A through the hosts entry from 2.4. If the argocd-apps chart named
its admin Secret differently, `kubectl -n argocd-apps get secret` shows it.

### 5.6 Plant Tower's ten keys

`backstage-github-oauth-client-id` and `-secret`, `backstage-github-token` and `ghcr-prune-token` come from the old
Tower project's export, found by key name below. The notify token must equal hangar-dev's `backstage-notify-token`:

```sh
OLD=$(grep -l '^backstage-github-oauth-client-id:' ~/infisical-export/*.yaml | head -1); echo "$OLD"
NOTIFY=$(yq -r '.["backstage-notify-token"]' ~/infisical-export/dev-shared.yaml)
infisical secrets set --domain $INF --projectId $TOWER_PID --env prod \
  "backstage-github-oauth-client-id=$(yq -r '.["backstage-github-oauth-client-id"]' $OLD)" \
  "backstage-github-oauth-client-secret=$(yq -r '.["backstage-github-oauth-client-secret"]' $OLD)" \
  "backstage-github-token=$(yq -r '.["backstage-github-token"]' $OLD)" \
  "ghcr-prune-token=$(yq -r '.["ghcr-prune-token"]' $OLD)" \
  "backstage-argocd-dev-apps-token=$DEV_ARGO" "backstage-argocd-prod-apps-token=$PROD_ARGO" \
  "glidepath-backstage-notify=$NOTIFY" \
  "tower-breakglass-minio-access-key=$MINIO_AK" "tower-breakglass-minio-secret-key=$MINIO_SK" \
  "tower-breakglass-anchor-key=$ANCHOR" >/dev/null
infisical export --domain $INF --projectId $TOWER_PID --env prod --format yaml | yq 'keys'   # ten names
unset DEV_ARGO PROD_ARGO MINIO_AK MINIO_SK ANCHOR NOTIFY
```

If a key is missing from the export, its row in the backstage README says where to get a new one.

### 5.7 Build, release, verify

```sh
git -C $SRC/backstage switch main && git -C $SRC/backstage pull --ff-only
git -C $SRC/backstage commit --allow-empty -m "Build Tower on hangar-prod" && git -C $SRC/backstage push   # triggers build and release
until B=$(gh pr list -R $OWNER/gitops-backstage --json headRefName,files \
  -q '[.[] | select(any(.files[]; .path=="hangar-prod/prod/release.yaml"))][0].headRefName') && [ -n "$B" ] && [ "$B" != null ]; do sleep 30; done
echo "release PR branch: $B"
cd $SRC/gitops-backstage && git switch main && git pull --ff-only
git fetch origin "$B" && git merge --ff-only FETCH_HEAD && git push origin main      # keeps the signed commit
```

This is the new cluster's first BuildKit build. Check that it ran under `baseline`:

```sh
kubectl --context hangar-dev get ns app-backstage-cicd -o jsonpath='{.metadata.labels}' | jq 'with_entries(select(.key|startswith("pod-security")))'
```

A first build that logs `failed to configure registry cache importer ... not found` is expected: the
`ghcr.io/$OWNER/backstage-buildcache` package doesn't exist yet. If the build step fails inside rootlesskit, see
Glidepath `docs/admin/rootless-builds.md`, "Checking a cluster".

Merge release PRs by fast-forward, never with GitHub's button: all three button strategies make an unsigned commit
and `provenance` fails. Then, on Mac B:

```sh
kubectl --context hangar-prod -n app-backstage-prod get rollout,cluster.postgresql.cnpg.io,pods -w   # Ctrl-C once the pod is Ready
$SRC/airframe/tools/airframe-verify postgresql app-backstage-prod/backstage-db --context hangar-prod
curl -fsS http://backstage.hangar-prod.local/healthcheck
```

Sign in with GitHub at `http://backstage.hangar-prod.local` from Mac A. From here on Tower manages itself.

## 6. Skyport

Airframe's `docs/user/skyport-runbook.md` has the per-part commands. To set it up, on Mac A:

```sh
cd $SRC/airframe && cat > .walkthrough.env <<EOF
HANGAR_GITHUB_OWNER=$OWNER
HANGAR_CLUSTERS_FILE=$SRC/gitops-hangar-dev/clusters.yaml
EOF
tools/walkthrough-runner docs/walkthroughs/part6-gate-api.yaml --render /tmp/check.md && grep -m3 context /tmp/check.md
for r in boarding-api flight-api baggage-api gate-api checkin-api; do
  gh repo view $OWNER/$r --json name -q .name 2>/dev/null && echo "still exists: $r"
  gh repo view $OWNER/gitops-$r --json name -q .name 2>/dev/null && echo "still exists: gitops-$r"
done
```

Clear what that lists (the runbook's leftovers table), then walk parts 1 to 7, gate-api first as a smoke test.
Replay every check at the end:

```sh
tools/walkthrough-runner --all --clusters $SRC/gitops-hangar-dev/clusters.yaml
```

## Deferred until after the rebuild

- Rename the namespaces `platform-catalog` and `platform-system`, and the API groups `catalog.idp.io` and
  `secrets.idp.io`, across repos.
- Glidepath known gap #27 (the Loki `service_name` label), and Airframe comments that still say `platform-cicd`.
- Port Apron's templates to a kubara catalog (Apron roadmap v1).
