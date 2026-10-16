# Business rules

Every rule Hangar applies to people, releases and clusters, in one place. Each component's own docs explain how a
rule works and why; this page lists every rule, how strongly it holds, and what holds it. If a rule is not on this
page, it is not a rule yet.

Last checked against the code on 2026-10-14: backstage `6689352`, tower `855d8e4` (v0.71.2), glidepath `6d25259`,
airframe `22aad95`, gitops-cluster-dev `22e1fa8`, gitops-cluster-kind-prod `3f26e81`. Cloud credentials (CRED-05,
CRED-07 to CRED-09, POL-10) re-checked on 2026-10-16: glidepath `2579c9f`, airframe `aed778e` (v0.3.144),
gitops-cluster-dev `02bb7f8`.

## How to read it

Each rule has an ID that never changes and is never reused. **Strength** says what happens when someone tries to break
the rule:

| Strength | Meaning |
|---|---|
| **Enforced** | A system refuses the action. |
| **Fails closed** | Enforced, and if the check itself cannot run, the action is refused too. |
| **Soft** | The rule is checked, and breaking it is flagged, announced and recorded, but nothing stops it. |
| **Display** | Shown to help a person decide. Nothing is checked or blocked. |
| **Convention** | Written down. Nothing checks it. |
| **Off here** | Built and documented, but not in effect in this lab (usually the GitHub plan). |

**Source** links to the doc that explains the rule in full, or to the code when no doc does.

## Contents

1. [People and roles](#1-people-and-roles)
2. [Access in the portal](#2-access-in-the-portal)
3. [Environments and promotion](#3-environments-and-promotion)
4. [Release gates](#4-release-gates)
5. [Release records, modes and sign-off](#5-release-records-modes-and-sign-off)
6. [Rollback](#6-rollback)
7. [Supply chain](#7-supply-chain)
8. [Live operations from Tower](#8-live-operations-from-tower)
9. [Break-glass debug sessions](#9-break-glass-debug-sessions)
10. [Images and retention](#10-images-and-retention)
11. [Service catalog (Airframe)](#11-service-catalog-airframe)
12. [Cluster admission policies](#12-cluster-admission-policies)
13. [Credentials and secrets](#13-credentials-and-secrets)
14. [Notifications](#14-notifications)
15. [AI agents](#15-ai-agents)
16. [Rules that are not enforced yet](#16-rules-that-are-not-enforced-yet)
17. [Keeping this page true](#17-keeping-this-page-true)

## 1. People and roles

| ID | Rule | Strength | Held by |
|---|---|---|---|
| PPL-01 | You sign in with GitHub, and only if the catalog has a User whose name is your GitHub login. Guest sign-in works only in local development. | Enforced | Backstage auth (`usernameMatchingUserEntityName`); the guest provider refuses outside `NODE_ENV=development` |
| PPL-02 | Groups and memberships come from the catalog (`examples/org.yaml`, each User's `memberOf`). Nothing syncs them from GitHub: a personal account has no org to sync from. | Convention | [backstage `examples/org.yaml`](https://github.com/jfillman/backstage/blob/main/examples/org.yaml) |
| PPL-03 | An app's **owners** are its catalog Component's `spec.owner`, which comes from the XR's `terasky.backstage.io/owner` annotation. You own an app if you, or a group you belong to, are its owner. | Enforced | the catalog's `isEntityOwner` rule |
| PPL-04 | **Admins** are the members of `group:default/admins`. Admin is a grant, and some actions need it whoever owns the app (ACC-04). | Enforced | [`permissionPolicy.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/permissionPolicy.ts) |
| PPL-05 | **Break-glass reviewers** (`group:default/breakglass-reviewers`) may review a glass-broken session. They get nothing else from that group. | Enforced | Tower's break-glass routes |
| PPL-06 | Tower's write routes accept only a signed-in user. A service token is refused. | Enforced | [`towerAuthz.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/towerAuthz.ts) |

Today's groups are `admins`, `team-passenger`, `team-flight-ops`, `team-skyport`, `team-platform` and
`breakglass-reviewers`.

## 2. Access in the portal

| ID | Rule | Strength | Held by |
|---|---|---|---|
| ACC-01 | Anyone signed in can read everything: the catalog, every app's Tower tabs, TechDocs, release records, sign-off states and the release calendar. | Enforced | permission policy (every read allowed) |
| ACC-02 | Only admins can delete catalog entities, register or delete catalog locations, run software templates (create a scaffolder task, run an action) or manage templates. | Enforced | `permissionPolicy.ts` `WRITE_PERMISSIONS` |
| ACC-03 | Every Tower write needs the app's owners or an admin. The route finds the app's catalog entity and asks the permission framework for that user and that app. | Enforced | `towerPermissions.ts`, `towerAuthz.ts` |
| ACC-04 | Some writes need an admin even from an owner: changing an app's release mode, syncing or force-syncing a Flight environment, ending someone else's break-glass session, and breaking the glass. | Enforced | `towerGrantOnlyPermissions` |
| ACC-05 | A request can only act on the repository the catalog names for that app. The GitHub owner in the request must match the entity's `github.com/project-slug`. | Enforced | `towerAppFromEntity` |
| ACC-06 | The Kubernetes proxy is read-only. Anything but GET, HEAD or OPTIONS is refused, and so is a WebSocket upgrade (exec or attach). Every write goes through an owner-checked route. | Enforced | [`kubernetesProxyGuard.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/kubernetesProxyGuard.ts) |
| ACC-07 | Tower greys out the actions you may not take and says why. That is a courtesy: every route checks again. | Display | Tower `/argo/capabilities` |
| ACC-08 | Every Tower write is audited (`tower-write`), refusals included. Severity is medium by default, high for Flight permissions, rollback, force sync and image pruning, and critical for a Flight analysis bypass or a broken glass. | Enforced | Backstage auditor |

Full action-by-action table: [Tower security model](https://github.com/jfillman/tower/blob/main/docs/security.md#who-may-do-what).

## 3. Environments and promotion

| ID | Rule | Strength | Held by |
|---|---|---|---|
| ENV-01 | Every environment is **Ground** (lower, on the dev cluster) or **Flight** (upper clusters). The tier comes from the app's `cicd.yaml`, read on the server, never from a request. An environment that can't be placed counts as Flight. | Enforced | Backstage routes; Glidepath |
| ENV-02 | Ground is self-service: a deploy is a direct commit to the app repo's `glidepath/envs/<env>.yaml` by the deploy bot. No release gates run on Ground. | Enforced | Glidepath `deploy-manifests` |
| ENV-03 | Flight changes only through a release PR to `gitops-<app>`. The release pipeline can open a PR but cannot touch a cluster; Argo CD syncing the merged PR is the only way in. | Enforced | [Glidepath ADR-0004](https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0004-gitops-only-release.md) |
| ENV-04 | A promotion carries forward only what already runs in the source environment. The image and commit are read from the source environment's file on the server, never from the request, and never rebuilt. | Enforced | `glidepathPromote.ts` `resolveSource` |
| ENV-05 | No workload, no release. An environment whose values turn the service off (`rollout.enabled: false`) gets no release: Glidepath refuses before any PR or commit, Tower refuses Promote, and the chart refuses to render a tracked release with nothing to run. | Enforced | [Glidepath release.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/release.md#an-environment-that-runs-no-workload-is-refused-2026-10-10) |
| ENV-06 | Every environment's Argo CD Application syncs automatically, heals drift and prunes what the chart no longer renders. Argo CD refuses a sync that would delete everything, and deleting a generator never deletes a running environment. | Enforced | Argo CD (`selfHeal`, `prune`, `allowEmpty: false`, `preserveResourcesOnDeletion`) |
| ENV-07 | No cluster holds a credential for another cluster's API. A Flight environment is created by a commit the target cluster's own Argo CD acts on. Separate lower and upper AppProjects keep an app's Ground identity away from Flight destinations. | Enforced | [Glidepath security.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/security.md#multi-cluster-no-credential-ever-crosses-the-boundary) |
| ENV-08 | Each app environment has its own namespace (`<type>-<app>-<env>`), and pipelines run in the app's `-cicd` namespace. RBAC never spans them. | Enforced | Glidepath, Airframe |
| ENV-09 | A PR preview environment lives as long as its PR. Its namespace is deleted with its Application, and a sweep every 30 minutes deletes any preview namespace whose Application is gone. | Enforced | [Glidepath ephemeral-environments.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/ephemeral-environments.md) |
| ENV-10 | A Flight destination must be a registered upper cluster marked `crossplaneReady`. A dev cluster is refused. | Enforced | Airframe `ApplicationEnvironment` schema and cluster registry |

## 4. Release gates

| ID | Rule | Strength | Held by |
|---|---|---|---|
| GATE-01 | Every release PR to a gitops repo runs every registered gate: `sast`, `image-scan`, `provenance`, `sbom` and `values` are real; `itsm`, `qa` and `policy-validation` are stubs. | Enforced (they run) | [Glidepath release-guardrails.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/release-guardrails.md) |
| GATE-02 | A stub never reports a pass. It logs that no check exists, returns `stub`, and shows as a grey STUB everywhere. | Enforced | [Glidepath governance-stubs.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/governance-stubs.md), ADR-0003 |
| GATE-03 | A gate stops a merge only through the gitops repo's GitHub ruleset: every gate a required check from the Pipelines as Code app, 2 approvals, no bypass actors. | **Off here** | [Glidepath github-ruleset.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/github-ruleset.md). Private repos on GitHub Free cannot enforce rulesets, so anyone with write access can merge past a red gate. |
| GATE-04 | Merging past a failed or missing gate is a break-glass bypass. It is detected after the merge and alerted (not subject to notification settings), and the PR keeps its failed checks. | Soft | `bypass-check` (`detect-bypass-merge`) |
| GATE-05 | The commit being released must be gitsign-signed (public Sigstore) by an address on the app's `allowed-commit-signers` list (`<app>-policy-config`). | Enforced | `provenance` gate; [Glidepath commit-signing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md) |
| GATE-06 | Land app changes by fast-forwarding a signed commit, never with GitHub's merge button. All three button options make a new commit nobody signed, so its build fails GATE-05. | Convention (GATE-05 catches it) | [commit-signing.md: merge strategy](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md#merge-strategy-matters-a-github-clicked-merge-is-never-signed) |
| GATE-07 | The image must carry a valid SLSA provenance attestation from the platform's own Fulcio (the Tekton Chains identity), and the attestation must pass the Conforma policy. | Enforced | `provenance` gate; [Glidepath provenance-policy.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/provenance-policy.md) |
| GATE-08 | Every changed `values.yaml` passes `airframe-validate`: no secret-looking literal (`AF-SECRET-001`), no release-owned key in a human file or the reverse (`AF-OWNER-001`), and no unknown component or output (`AF-COMP-001/002`). | Enforced (subject to GATE-03) | `values` gate |
| GATE-09 | A Release Record PR (`release-record-*` branch) is not a release, and the gates skip it. | Enforced | gate triggers |
| GATE-10 | `/retest` re-runs a gate. It never skips one. | Enforced | Pipelines as Code |
| GATE-11 | A new or removed gate goes in the `releaseGuardrails` registry, and the ruleset is regenerated from it in the same change. | Convention | `hack/apply-guardrail-ruleset.sh` |

## 5. Release records, modes and sign-off

| ID | Rule | Strength | Held by |
|---|---|---|---|
| REL-01 | Each app has a release mode in `gitops-cluster-dev-tenants/release-modes.yaml`: **Assisted** (the default) or **Hand-flown**. **Autoland** has a name but isn't available. Only an admin can change a mode, and only through a PR. | Enforced | `tower.release.mode` (admins only) |
| REL-02 | The **sign-off environment** is the one `cicd.yaml` marks `production: true`, else the last Flight environment. | Enforced | `releaseFlow.ts` |
| REL-03 | For a Hand-flown app, a release PR to the sign-off environment needs a sign-off. | Soft | the `hangar/release-signoff` commit status; GitHub Free can't make it required |
| REL-04 | A sign-off counts only if it is the reviewer's latest review, it is an approval, and it came before the merge. The reviewer must not be the person who merged or opened the PR, and must be in the app's owning team or an admin (GitHub login matched to a catalog User). If the catalog can't be read, no approval counts. | Fails closed | [`releaseApprovers.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/releaseApprovers.ts), `releaseFlow.ts` |
| REL-05 | A release that merges without a sign-off that counts is announced at high severity. Its record says **shipped without** or **self-approved**, and keeps saying so. | Soft | `release-signoff-poll` |
| REL-06 | Assisted apps record who merged and who reviewed. They get no status and no alert. | Enforced | `release-signoff-poll` |
| REL-07 | The next release's draft (notes, summary, owner, risk, target date, milestone, GitHub Release opt-in) is `glidepath/releases/next.yaml` in the app repo. Owners and admins save it as a direct commit that names them and builds nothing. Unknown fields are dropped, and text is capped at 50 lines of 300 characters per list and 2,000 characters per field. | Enforced | `tower.release-record.edit`; `sanitizeDraft` |
| REL-08 | When a release is first healthy in a Flight environment, the backend opens the record PR (`releases/<app>@<tag>.yaml` in `gitops-<app>`) with the draft sealed into it, and clears `next.yaml`, within a few minutes. Nothing merges it. A record is history once a person merges it. | Enforced | `release-record-seal-poll` (2 min), `release-record-poll` (hourly) |
| REL-09 | Release names are tree names given in order (ASPEN, BIRCH, CEDAR...), skipping U, V and X, with numerals after the last (ASPEN II). A name is the release's place in the app's committed records, so it never changes. | Enforced | `releaseNames.ts` (Tower and backend, kept identical) |
| REL-10 | A release's scope is the PRs merged after the previous release's commit landed on main, up to its own. A PR is never in two releases. | Enforced | Tower |
| REL-11 | **Readiness** checks the leading candidate: changes merged, running on Ground, 24 hours on Ground, build and scans passed, signed and attested, version bumped, and a healthy previous release to roll back to. A target date and closed planned issues are added when the draft has them. | **Display** | Tower `nextRelease.ts`. Nothing is blocked. |
| REL-12 | The suggested version is the last version plus the bump the merged PRs call for: breaking means major (minor before 1.0), a feature means minor, anything else patch. The real version is the image's tag. | Display | Tower |
| REL-13 | A release's outcome is decided in the sign-off environment. **Clean** means healthy, then replaced or healthy through the 7-day bake. **Rolled back**, **replaced before healthy** and **stopped before production** are the other outcomes. It is written back once, by PR. | Enforced | `releaseOutcome.ts` (`BAKE_DAYS = 7`) |
| REL-14 | A GitHub Release is opt-in per release, published only once the release is healthy in production, and tagged `v<version>` at the image's commit. An existing tag is reused only at that commit, and a tag is never moved or replaced. | Enforced | `releaseOutcome.ts` |
| REL-15 | Everyone hears when a release PR to production opens ("ready for prod") and when it merges ("released"). After a restart, nothing is announced twice. | Enforced | `release-signoff-poll` |
| REL-16 | The backend writes only PRs, commit statuses, GitHub Releases and the draft commit. It never merges. | Enforced | [Tower security.md: release records](https://github.com/jfillman/tower/blob/main/docs/security.md#release-records-what-the-backend-does-on-its-own) |

Full detail: [Tower release records](https://github.com/jfillman/tower/blob/main/docs/release-records/index.md).

## 6. Rollback

| ID | Rule | Strength | Held by |
|---|---|---|---|
| RB-01 | A rollback is an ordinary release of an earlier image: a PR, the gates and a merge. Owners start it (`tower.release.rollback`, audited high). It applies to Kubernetes Flight environments; a cloud target rolls back by a release pin PR (`tower.release.pin`, ADR-0020). | Enforced | Glidepath `rollback-release`; Tower |
| RB-02 | The target must be one of the five newest releases of that app, environment and cluster that reached healthy. The gates work this out from the release records, never from the PR's text. | Enforced | `extract-promoted-image` `rollback-eligibility` |
| RB-03 | On an eligible rollback, `sast`, `image-scan` and `sbom` are advisory, because that image already ran there. Provenance, values, commit signing and approvals still apply. | Enforced | [Glidepath release-state.md: rollback](https://github.com/jfillman/glidepath/blob/main/docs/admin/release-state.md#rollback-adr-0021-phase-4) |

## 7. Supply chain

| ID | Rule | Strength | Held by |
|---|---|---|---|
| SC-01 | Builds run rootless under Pod Security `restricted` (kaniko): not privileged, no host namespaces. | Enforced | [Glidepath rootless-builds.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/rootless-builds.md) |
| SC-02 | Tekton Chains signs every image and its provenance with a short-lived certificate from the build cluster's own Fulcio (its own trust root, never the public one), and logs the signatures in the platform's Rekor. Rekor's signing key persists, is never replaced, and is never in git, Infisical or a terminal. | Enforced | [Glidepath image-signing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/image-signing.md) |
| SC-03 | Tower colours a supply-chain step by its verification. **Green**: verified. **Amber**: present but unverified, for a reason that isn't tampering. **Red**: contradicted, so don't promote it. **Grey**: missing. A signature with no Rekor entry counts as unsigned. | Display | [Tower supply-chain.md](https://github.com/jfillman/tower/blob/main/docs/supply-chain.md) |
| SC-04 | Readiness's "Signed and attested" passes only on a verified attestation, never on one that is merely present. | Display | Tower `isSignedAndAttested` |
| SC-05 | Image signatures are checked at release (GATE-07), not when a cluster admits an image. The exception is the Tower debug image (BG-04). | Enforced at release only | see [section 16](#16-rules-that-are-not-enforced-yet) |

## 8. Live operations from Tower

| ID | Rule | Strength | Held by |
|---|---|---|---|
| OPS-01 | Tower has no standing write access to any cluster. Sync, force sync, terminate, Rollout actions and pod restarts run through one Argo CD account, which can act only on app projects: deny rules cover the platform projects. | Enforced | Argo CD RBAC |
| OPS-02 | Through Argo CD, Tower deletes nothing but a single pod. It never rolls back to an Argo CD revision and never edits an Application's spec. | Enforced | Argo CD role `tower-pod` (`delete//Pod/*` only) |
| OPS-03 | Sync and force sync: owners on Ground, admins only on Flight. | Enforced | ACC-04 |
| OPS-04 | Restarting a pod never takes the last ready pod of a Flight ReplicaSet. On Ground it needs an explicit "accept downtime". | Enforced | [`podRestart.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/podRestart.ts) |
| OPS-05 | Skipping canary analysis on Flight (promote full, skip step) is allowed to owners as a **bypass**: audited critical and announced to everyone. Every Rollout action is announced. | Soft | `tower.rollout.bypass` |
| OPS-06 | Re-running and cancelling a PipelineRun is for owners. The cluster admits only Glidepath's own run shape in an app's `-cicd` namespace, and on an existing run only a cancel. | Enforced | `tower-pipelinerun-shape` policy |
| OPS-07 | Configuration changes (values, env XR, ConfigMap files, `cicd.yaml`) are PRs, never direct edits. | Enforced | `tower.config.edit` |

## 9. Break-glass debug sessions

| ID | Rule | Strength | Held by |
|---|---|---|---|
| BG-01 | Only the app's owners can ask for a session. On Ground it starts at once. On Flight a second person approves first: an owner who isn't the requester, or an admin. | Fails closed | Tower routes, and the cluster refuses a grant whose approver is the requester |
| BG-02 | An admin may **break the glass**: a Flight session with no second person. It is audited critical, announced to everyone, and must be reviewed afterwards by someone other than the requester (an owner, an admin or a break-glass reviewer). | Soft (the review) | `tower.breakglass.self` |
| BG-03 | A session lasts 15, 30 or 60 minutes, with one 15-minute extension. It ends after 10 minutes idle or 2 minutes disconnected. Each person may have one open session. | Enforced | backend timers; expiry labels the cluster acts on |
| BG-04 | Never exec. A session is a separate debug container: the signed, digest-pinned Tower debug image, non-root, read-only, all capabilities dropped. On Flight the cluster refuses `kubectl exec` into app namespaces for everyone but operators. | Fails closed | `tower-breakglass-*` admission policies |
| BG-05 | Backstage has no standing debug rights. For each session it binds one of two debug roles to itself, in one namespace, with an expiry. | Fails closed | `tower-breakglass-rolebinding` |
| BG-06 | Every byte is recorded. A session that can't be recorded never starts. Recordings are object-locked for 365 days, their hashes anchored in Rekor, and the app's owners can read them. | Fails closed | [Tower break-glass guardrails](https://github.com/jfillman/tower/blob/main/docs/break-glass/guardrails.md) |
| BG-07 | Admins can end anyone's session, and on Flight so can the session's approver. Anyone can end their own. | Enforced | `tower.breakglass.terminate` |

## 10. Images and retention

| ID | Rule | Strength | Held by |
|---|---|---|---|
| IMG-01 | Owners can prune only their app's own packages (`<app>`, `<app>-pr`, `<app>/cache`). Platform packages are refused whatever the app is called. | Enforced | `imagePrunePlan.ts` `PLATFORM_PACKAGE` |
| IMG-02 | A prune shows its plan first and deletes only that plan. If anything changed, it refuses and shows the new plan. At most 300 versions go per run, audited high and announced. | Enforced | `imagePrune.ts` |
| IMG-03 | Always kept: anything running or that a ReplicaSet can scale back to; anything named in git (default branch or an open PR); each environment's last five healthy releases; anything in flight; an open PR's head image; anything under 14 days old; the 10 newest builds. For the cache: the 20 newest layers and anything under 14 days. A release is deleted whole or not at all. | Enforced | `imagePrunePlan.ts` |
| RET-01 | Release-tracking records on the dev cluster are deleted after 14 days. Never deleted: a merged or progressing release, or the five newest healthy releases per app, environment and cluster. Outcomes are copied into the git record before the 14 days are up. | Enforced | `release-record-sweeper` |
| RET-02 | A release that is merged or progressing with no new fact for 45 minutes raises `ReleaseStalled`, once per state. | Enforced | `release-record-sweeper` |
| RET-03 | A pipeline stage that hasn't started its next stage 10 minutes after finishing is reported as stalled. | Enforced | [stalled pipeline detector](https://github.com/jfillman/glidepath/blob/main/docs/admin/stalled-pipeline-detector.md) |

## 11. Service catalog (Airframe)

Airframe is where policy turns into code. Its own register is the authority on these rules:
[Airframe governance: what is enforced today](https://github.com/jfillman/airframe/blob/main/docs/admin/governance.md#what-is-enforced-today).
In short:

| ID | Rule | Strength | Held by |
|---|---|---|---|
| AF-01 | You can ask only for the kinds and fields the XRDs offer, within their enums, bounds and cross-field rules. There is no "raw VM" kind, on purpose. | Enforced | XRD schema and CEL at admission |
| AF-02 | Composed resources get least-privilege roles, the baseline NetworkPolicy, dedicated data stores per environment, and `hangar.io/*` tags and labels. | Enforced | compositions |
| AF-03 | Removing a Kubernetes object never deletes developer data: scaffolded repo files and Infisical projects. Scaffold files and the deploy surfaces Glidepath owns are never overwritten. | Enforced | management policies |
| AF-04 | Upper-environment and catalog changes are PRs a person merges. A catalog change ships as a tag, pinned per cluster, dev first. | Enforced | GitOps; Argo CD self-heal reverts hand edits |
| AF-05 | Only control-plane clusters can be marked `autopilotReady`. | Enforced | cluster registry chart |
| AF-06 | `extraManifests`, `networkPolicy` and `httpRoute` changes need a person. | Convention | `AGENTS.md` |
| AF-07 | A security reviewer approves changes to XRDs and compositions. | Convention | not enforced |

## 12. Cluster admission policies

Rules the API servers themselves enforce, so a bug in Backstage, or a compromised Backstage, can't get around them.
Every one is native ValidatingAdmissionPolicy that fails closed, and each is scoped to its own objects. The exceptions
are the debug-image signature check and `glidepath-cloud-deployer-pods`, which run in Kyverno's webhook (also fail
closed).

| ID | Policy | Cluster | Rule |
|---|---|---|---|
| POL-01 | `tower-pipelinerun-shape` | kiac-dev | Backstage's PipelineRuns have Glidepath's shape only (OPS-06). |
| POL-02 | `tower-rolebinding-delete` | kiac-dev | Backstage may delete only `tower-breakglass-*` RoleBindings. |
| POL-03 | `tower-breakglass-rolebinding` | both | The only grant Backstage may create. On Flight it must name an approver other than the requester, or carry the glass-broken mark. |
| POL-04 | `tower-breakglass-debug-container`, `-debug-image` | both | The exact debug image digest and its cosign signature, hardened settings, and process access only for the approved session. |
| POL-05 | `tower-breakglass-pod-delete`, `-pod-annotate` | both | Backstage deletes only debug or copy pods, and patches only the process-access annotation. |
| POL-06 | `tower-breakglass-no-exec` | kind-prod | No exec into app pods for anyone but operators. Attach only to a debug container. |
| POL-07 | `no-long-lived-sa-tokens` | kiac-dev | No long-lived ServiceAccount token Secrets in `backstage-system`. |
| POL-08 | `testkube-secret-usage` | kiac-dev | A tenant's TestWorkflow may reference only that tenant's own Secrets in the shared `testkube` namespace. |
| POL-10 | `glidepath-cloud-deployer-pods`, `-taskruns`, `-pipelineruns`, `-jobs` | kiac-dev | Only a cloud deploy may run as `glidepath-cloud-deployer`, the one identity AWS deploy roles trust. Decided by who created the object, never by labels: pods only from Tekton's controller or the Job controller, TaskRuns only from Tekton, Jobs only from Crossplane, and only they may change a TaskRun's or Job's spec later (others may add metadata, as Chains, Results and the garbage collector do), and a PipelineRun may give it only to the catalog `deploy` Pipeline's `deploy-aws-lambda`, not run-wide, with no pod-template `env` or volumes. |
| POL-09 | (how policies are written) | both | Every optional field is guarded with `has()`, and every policy is scoped by match conditions, so a CEL error can only refuse its own objects. A policy change widens before it narrows. |

Full detail: [Tower break-glass admission policies](https://github.com/jfillman/tower/blob/main/docs/break-glass/admin/policies.md).

## 13. Credentials and secrets

| ID | Rule | Strength | Held by |
|---|---|---|---|
| CRED-01 | Secrets are references to Infisical, never values in git or an XR. | Enforced on gitops repos (GATE-08), convention elsewhere | `AF-SECRET-001` |
| CRED-02 | People create credential material themselves, in Infisical. It is never pasted into a chat, a terminal transcript or a repo. | Convention | [Glidepath secrets-management.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/secrets-management.md) |
| CRED-03 | Tower holds no long-lived cluster credential. Reads use the pod's projected token (600 s). Writes on kiac-dev use a `tower-actor` token minted for each action. | Enforced | [Tower credentials](https://github.com/jfillman/tower/blob/main/docs/credentials/index.md); POL-07 |
| CRED-04 | The GitHub App's private key never leaves `platform-system`. A release gets an installation token for its own gitops repo only. | Enforced | `token-review-interceptor` |
| CRED-05 | The platform has one identity per external system (GitHub, Infisical, AWS, Azure), in `crossplane-system`. Apps never hold one. Each app reads only its own Infisical project. On AWS that identity is an IAM role assumed with a projected ServiceAccount token; nothing is stored (since 2026-10-16). | Enforced | Airframe provider configs, External Secrets; [Airframe cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md#how-keyless-aws-access-works) |
| CRED-07 | A Lambda deploy reaches AWS as `glidepath-deploy-<functionName>`, a role made for that one function: push to its repository and update its code, nothing else. It is assumed with a one-hour token for `glidepath-cloud-deployer`; no other pipeline step has AWS access. | Enforced; the stored-key fallback remains until phase 4 (section 16) | [Glidepath cloud-deploy-identity.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/cloud-deploy-identity.md); POL-10 |
| CRED-08 | Every IAM role a cloud-target composition creates carries the permissions boundary `HangarCloudTargetBoundary`. The Crossplane identity can't create a role, or add rules to one, without it, and nothing may remove it. | Enforced (IAM) | `HangarCrossplaneCloudTargets` v3; [Airframe cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md) |
| CRED-09 | A composition never removes something that already exists because a condition it was created under stopped holding. Conditions gate creation only; deleting the XR is the only way to delete its cloud resources. | Enforced (render tests) | Airframe v0.3.144; incident 2026-10-16 in [cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md#a-rule-for-composition-authors-never-gate-what-already-exists) |
| CRED-06 | The image-prune token can only read and delete packages. The backend holds it, never the browser. | Enforced | IMG-01 |

## 14. Notifications

| ID | Rule | Strength | Held by |
|---|---|---|---|
| NOT-01 | SLO alerts go to the app's owners, or to everyone if the app has no owner. **Budget exhausted** fires above a burn of 1.0 and clears below 0.9. **Burning fast** fires when both 5-minute and 1-hour burn exceed 14.4x, and clears below 12.96x. **No data** fires after 15 empty polls (about 30 minutes); a failed query doesn't count. | Enforced | [Hangar SLO docs](../slo/README.md), `sloTransitionPoll.ts` |
| NOT-02 | Release announcements, Rollout actions, analysis bypasses, broken glass, Flight pod restarts and image prunes go to everyone. | Enforced | Backstage notifications |
| NOT-03 | A bypass merge (GATE-04) is alerted however notifications are set. | Enforced | `detect-bypass-merge` |

## 15. AI agents

| ID | Rule | Strength | Held by |
|---|---|---|---|
| AI-01 | An agent passes the same pre-merge checks a person does, and works within `AGENTS.md`. | Enforced (the checks), convention (`AGENTS.md`) | Airframe |
| AI-02 | Agent runs go only to clusters marked `autopilotReady` (AF-05). | Enforced | AgentRun composition |
| AI-03 | Per-agent tool tiers, budgets and field allow/deny lists (Clearance) are built but not deployed. | Off here | [Autopilot design](../autopilot/design.md) |

## 16. Rules that are not enforced yet

Every place where a rule above is weaker than it reads, in one list:

| Gap | Rules | What it means today |
|---|---|---|
| GitHub Free can't enforce rulesets or required checks on private repos. | GATE-03, REL-03 | Gates and sign-off report but don't block. A bypass is detected and announced (GATE-04, REL-05). |
| GitHub's merge button can't keep a gitsign signature. | GATE-05, GATE-06 | A PR merged on GitHub builds an image whose provenance gate fails. Proposed: accept a GitHub web-flow merge when GitHub's own signature verifies and every commit in the PR is signed by an allowed signer. **Open decision.** |
| The ruleset assumes every PR is a release PR. | GATE-03 | Once enforced, non-release PRs would wait forever for gates that never run. Fix before enabling GATE-03 ([ruleset audit](https://github.com/jfillman/glidepath/blob/main/docs/admin/github-ruleset.md#problems-found-in-the-audit-2026-09-27)). |
| App repos aren't gated. | ENV-02 | By design: Ground is self-service. Only gitops repos get gates. |
| Three gates are stubs. | GATE-01 | `itsm`, `qa` and `policy-validation` say so, never pass. |
| Production SLO burn isn't measured. | REL-13 | kind-prod's Prometheus is off, so "clean" can't yet mean "no SLO burn during bake". |
| Image signatures aren't checked at admission. | SC-05 | An unsigned image could run if it got into git. GATE-07 is the only check. |
| `airframe-validate` doesn't run on app repos or the tenants repo. | GATE-08, CRED-01 | Airframe roadmap AF-4b. |
| Agent and security-review limits are convention. | AF-06, AF-07, AI-03 | Clearance isn't deployed, and no rule requires a security reviewer. |
| Lambda deploys can still fall back to the shared deploy key, and ECS and Azure deploys use stored keys. | CRED-07 | A deploy that can't assume its function's role uses the app's `app-secrets` key. Phase 4 removes the fallback, the scaffold's AWS secrets and the `glidepath-deployer` user; ECS and Azure follow ([Glidepath known gap 43](https://github.com/jfillman/glidepath/blob/main/docs/admin/known-gaps.md)). |
| Only admins can run software templates. | ACC-02 | App teams can't scaffold a new service themselves. Intentional for the lab; revisit before onboarding other teams. |

## 17. Keeping this page true

- A change that adds, changes or removes a rule updates this page in the same change: here when the change is in
  this repo, or with a linked Hangar PR when it isn't. The component's own docs keep the detail.
- A rule that exists only in code is a bug in this page. Add it with the next free ID in its section.
- A retired rule keeps its row, struck through, with the date and the reason. Its ID is never reused.
- The commit list at the top says what this page was last checked against. Re-check it after any release of Tower,
  Glidepath, Airframe or Backstage that touches permissions, gates, release records or admission policies.
