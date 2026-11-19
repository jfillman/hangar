# Hangar on AWS: install plan

Written 2026-11-18. The owner is moving dev and test from the lab (hangar-dev, hangar-prod) to AWS.
Repos: jfillman/hangar-infra (Terraform and the command-by-command runbook, `docs/install.md`), jfillman/apron
(`--runtime eks`), plus Glidepath, Airframe, Clearance, Autopilot and Backstage/Tower as Apron renders them.

This plan is the order, the gates and the decisions. `hangar-infra/docs/install.md` has the commands for every step it
names; this file doesn't repeat them.

## Where things stand (read live, 2026-11-18)

- **AWS**: the Organization has the management account and the lab's `hangar` account only. None of the five
  capstone accounts exist yet. The state bucket exists, but it was made by hand, not by `00-state`. Its only state is
  `observe/logging` (Clearance's observe-aws for the lab). Nothing from `10-org` onward has been applied.
- **Code**: everything the capstone needs is merged:
  - hangar-infra#1: the stacks
  - apron#150: the eks runtime and the platform profile
  - glidepath#227: universal auth off the Infisical host
  - hangar-infra#11: the gVisor node group
  - apron#221: lab-only networking off EKS

## The review

Each of these is checked against `main` as of today.

| Area | Result |
|---|---|
| Terraform | `fmt` and `validate` pass on every stack, and on `40-clusters` for all three workspaces. Nothing has been planned against AWS yet (the admin SSO session had expired). |
| Apron renders | I ran hangar-infra's `apron_init` command for eks-dev, eks-prod and eks-man (fake AWS ids), plus the lab's fleet settings on eks-dev. All three pass `apron check` and render. |
| Lab leaks | None in the three renders. The only `.local` names are in-cluster `svc.cluster.local` names, and the only `hostAliases` are CRD schemas. `apron check` now refuses `tower.hostAliasIP` and the other lab-networking keys on `eks` (apron#221). |
| https | Every URL Apron builds on a cluster domain is https on eks: people-dex, the Autopilot gateway and MCP, and Clearance. Routes exist for every host Tower calls (autopilot, autopilot-api, clearance, clearance-api, glidepath-api, argocd-apps, rekor, minio). |
| Tower's identity | Clearance's, the Autopilot gateway's and glidepath-api's delegate lists name `eks-man/app-backstage-prod/backstage-ingestor`, derived from `tower.cluster`. No manual step. |
| gVisor | `40-clusters` gives eks-dev a tainted `sandbox` group, and `apron_init` adds `autopilot.hardenedRuntime=gvisor`. Apron then renders the RuntimeClass. |

### Fixed in this review

- **[hangar-infra#12](https://github.com/jfillman/hangar-infra/pull/12)** has three fixes:
  - **The state bucket is adopted.** The runbook's step 1 would have created a bucket that already exists, and then
    migrated state into it. `00-state` now has the backend on from the start and `import` blocks for the bucket and
    its three settings.
  - **No hand-made Secrets.** The runbook had you `kubectl create` two Secrets per cluster: Argo CD's repo
    credential and provider-infisical's identity. Owner rule (2026-11-16): no secret is created by hand in a GitOps
    cluster. Now:
    - A new stack, `35-bootstrap-secrets`, creates a Secrets Manager secret for each, in the cluster's own account.
      They outlive the clusters, so a teardown between sessions keeps the values.
    - You put the value in once.
    - Listing the cluster in `bootstrap_secrets` writes both Kubernetes Secrets. Terraform reads the values as ephemeral values and
      writes them through write-only arguments, so they never reach state.
    - `apron up` then runs straight through.
  - **The runbook is current.** The fleet settings to carry from the lab (and which to leave for later), Tower's values
    with the five Clearance and Autopilot URLs the old table lacked, and the backstage CI LAN address (below).
- **[apron#251](https://github.com/jfillman/apron/pull/251)**: on `eks`, `apron up` no longer prints `kubectl create`
  for the two bootstrap Secrets. It points at the Terraform step, and a test holds it there.

## Decisions for the owner

1. **Cut over or run side by side.** The lab and AWS share the GitHub Apps. Pipelines-as-Code and Clearance each have
   one webhook URL, and people-dex's and Tower's OAuth Apps have one callback each.

   **Recommendation: cut over.** Point them at AWS in phase 4 and leave the lab running with no CI events. That
   matches "dev and test move to AWS". Running both needs a second PaC App and two new OAuth Apps.
2. **Tower and eks-prod.** Backstage's `app-config.yaml` still has one remote cluster (the control plane), so Tower on
   eks-man can't see eks-prod's workloads. The AWS side is ready: eks-prod's RBAC, OIDC trust and API allow-list are in
   place.

   **Recommendation:** build the second remote cluster in backstage while phases 1-3 run. Phase 5 then proves it
   instead of listing it as a gap. Without it, the fleet still works; Tower just shows eks-dev and eks-man.
3. **Clearance's lab features** (ledger and witness, Kubernetes observe, observe-aws, targets, backup) stay off on the
   first install, because each names lab hosts or principals. Phase 7 brings them back with AWS wiring. Say if any
   must be there from day one.

## Phases and gates

Do not start a phase until the previous gate passes. Each gate is a check from `docs/install.md`.

| Phase | install.md steps | What happens | Gate |
|---|---|---|---|
| 0. Ready | What you need | Merge hangar-infra#12 and apron#251. `aws sso login --profile admin`. Tools installed. | `aws sts get-caller-identity` shows the management account |
| 1. Foundation | 1-5 | State bucket adopted, Organization (five accounts, SCPs, Identity Center), four VPCs, the `aws` zone delegated from Cloudflare (a manual NS step), backup vault | `dig NS aws.hangarplatform.dev` returns Route 53; SSO profiles work for the four new accounts |
| 2. Infisical | 6-7 | Infisical on Fargate (about 25 minutes), ENCRYPTION_KEY backed up, first-run admin, sign-ups off, three provider identities | two healthy targets; the org and the three identities exist |
| 3. Clusters | 8 | `35-bootstrap-secrets`, then eks-man, eks-dev and eks-prod (about 20 minutes each) | nodes Ready (eks-dev: 3 general plus the gVisor node), `gp3` default, Infisical's `/api/status` reachable from a pod over PrivateLink, `runsc` on the sandbox node |
| 4. Hub | 9-13 | Bootstrap values into Secrets Manager, then `bootstrap_secrets = ["eks-dev"]`, `apron up` on eks-dev, import the lab's `glidepath-hangar-dev` project, fleet file, gateway DNS, GitHub App URLs (decision 1) | every ExternalSecret Synced; `https://argocd.eks-dev...` answers from your address only; a PaC delivery returns 200 |
| 5. Prod, platform, Tower | 14-15 | The same for eks-prod and eks-man; Tower registered on the AWS fleet with the lab's XRs paused; Tower's values per the step 15 table | Tower signs you in; eks-dev's API server logs Tower's federated user; with decision 2 built, Tower lists an app's eks-prod workloads and eks-prod's API server logs the same federated user. Without it, record "eks-prod not visible in Tower" as an accepted gap here |
| 6. Prove it | 16 | A new app end to end; G1 (scale eks-dev to zero, prod keeps serving); a 30-minute Infisical outage; G4 restore from the backup vault; RDS failover | the times written down |
| 7. Clearance on AWS | (new runbook section, to write) | observe-aws for the hangar-dev/prod accounts (an `observe/<account>` stack per account, using the cluster's EKS issuer); Kubernetes audit from EKS control-plane logs; the ledger witness on eks-man; targets and backup; then the Go gateway | each feature's own verification, as on the lab |

## What blocks before it hurts

- **Backstage's CI** pins `backstage.hangar-prod.local` to a lab LAN address (backstage#250, `.tekton/flow-ci.yaml`).
  It must go before Backstage builds on eks-dev, or its smoke step calls the lab. It is a lab accommodation in product
  code; remove it rather than make it conditional.
- **Kubernetes audit collection** on the lab comes from an API server audit webhook (`hack/observe-audit.sh`).
  EKS takes no API server flags. Phase 7 needs a CloudWatch-based source (the control-plane `audit` log is already on
  in `40-clusters`). Keep `clearance.observe` off until then.
- **First apply, untested.** Nothing past the state bucket has run against AWS. Watch for:
  - the five account emails
  - the EKS OIDC identity provider association (10-20 minutes)
  - the AWS Load Balancer Controller v3 annotations on Traefik's Service
  - the bumped Infisical image (v0.167.5) on Fargate
  - the ephemeral Secrets Manager read for a cluster listed in `bootstrap_secrets`, which errors if a secret has no
    value yet: put the values first, then list the cluster

## Cost and pace

About $2.5-3 an hour with everything up. Phases 1-2 cost little: NAT gateways, RDS and the Fargate tasks. The clusters
are the expensive part.

Run phases 1-3 in one session, leave the secrets account up, and do phases 4-6 in a second. Tear the clusters down
between sessions (install.md, Teardown). Each recreate gives a cluster a new OIDC issuer: re-print the `apron_init`
command and update `issuer` and `tower.issuer`.

## Still not built

These are carried from install.md's Known gaps, and they don't block the install:

- Infisical AWS Auth for machine identities (they still use universal auth with a client secret)
- Infisical SSO
- ECR (images stay on GHCR)
- AWS cloud targets on eks-dev
- eks-prod's trace metrics to Thanos Receive
- Verified Access in front of the gateways
- a lifetime cap on Tower's EKS-OIDC tokens
- plan and apply in CI
