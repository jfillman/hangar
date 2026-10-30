# Business rules

Every rule Hangar applies to people, releases and clusters, in one place. Each component's own docs explain how a
rule works and why; this page lists every rule, how strongly it holds, and what holds it. If a rule is not on this
page, it is not a rule yet.

Last checked against the code on 2026-10-19: backstage `e40008f` (+ branch tests-route), tower `2228fbc` (v0.80.0), glidepath `0e66378`,
airframe `4b3cde1` (v0.3.157), gitops-hangar-dev `6a6f055`, gitops-hangar-prod `d751f6e`, check-rides `193afc2`.
REL-17 and REL-18 (commit proof on the Release Record and in the score) added 2026-10-20 with Tower v0.83.0 and
glidepath `36eb223`. GATE-05, GATE-06 and GATE-15 to GATE-17 (release-signing policy, GitHub-merge path) re-checked on 2026-10-20: glidepath
`9c42d81` (ADR-0027), tower `be8111b` (v0.82.0), backstage `61634fb`, gitops-hangar-dev `0d48da0`, apron `24d23d0`,
airframe `8aea2f6`.
GATE-01 and GATE-18 (`policy-validation` real) checked on 2026-10-27 against glidepath `22cd9ff` (ADR-0028).
PROM-01 to PROM-11, POL-11 and the SC-05 change (Ground and Flight registries, ADR-0029) added 2026-10-30, checked
against glidepath `983d2e0`, apron `2493b02`, gitops-hangar-dev `52b1223`, gitops-hangar-prod `fd9082a`, and live on
both clusters.
OPS-06, POL-01 and TEST-10 changed 2026-10-30 with Glidepath API P6 (Tower on glidepath-api, no Tekton writes), checked
against gitops-hangar-dev `52b1223` and live (`kubectl auth can-i`).
CRED-07 to CRED-09, POL-10) re-checked on 2026-10-17: glidepath `1ad8dae`, airframe `0710485` (v0.3.148),
gitops-cluster-dev #108.

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
5. [Testing and the check ride](#5-testing-and-the-check-ride)
6. [Change management (itsm)](#6-change-management-itsm)
7. [Release records, modes and sign-off](#7-release-records-modes-and-sign-off)
8. [Rollback](#8-rollback)
9. [Supply chain](#9-supply-chain)
10. [Live operations from Tower](#10-live-operations-from-tower)
11. [Break-glass debug sessions](#11-break-glass-debug-sessions)
12. [Images and retention](#12-images-and-retention)
13. [Service catalog (Airframe)](#13-service-catalog-airframe)
14. [Cluster admission policies](#14-cluster-admission-policies)
15. [Credentials and secrets](#15-credentials-and-secrets)
16. [Notifications](#16-notifications)
17. [AI agents](#17-ai-agents)
18. [Rules that are not enforced yet](#18-rules-that-are-not-enforced-yet)
19. [Keeping this page true](#19-keeping-this-page-true)

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

### Ground and Flight registries (PROM)

Builds push to **Ground** (`ghcr.io/jfillman`); upper clusters run only what was promoted to **Flight**
(`ghcr.io/riley-roooo`), copied by digest before the release merges. Detail:
[Glidepath registries.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/registries.md), [ADR-0029](https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0029-ground-and-flight-registries.md).

| ID | Rule | Strength | Held by |
|---|---|---|---|
| PROM-01 | A Flight environment's release file pins the Flight repository **and a digest** (`release.image.digest`), with the Ground repository it came from as `source`, from the moment the release PR opens. A release that pins Ground, or no digest, is never promoted. | Enforced | `open-release-pr`; `promote` refuses |
| PROM-02 | Only the promoter writes Flight: the `promote` workflow in `riley-roooo/flight-promoter`, whose own short-lived `GITHUB_TOKEN` is the only credential with write access. Builds, clusters and Glidepath cannot write it; Glidepath can only start the workflow (the `hangar-flight-promoter` App, `actions: write` on that one repo, minted per call by the broker for the `glidepath-promoter` ServiceAccount only). | Enforced | GHCR package permissions; broker `/promoter-token` |
| PROM-03 | Promotion starts only when every required gate is green on the release PR's current head commit. The last gate to finish starts it (an event, not a polling pod), exactly once; `promote` re-checks every gate itself and refuses a red or missing one. `image-promotion` is then a required check on the PR, and it cannot be made advisory. | Enforced | `comment-pr-check-result` fan-in; `promote` |
| PROM-04 | The copy keeps every digest: the image index, every platform manifest, the `.sig`/`.att` tags and the OCI 1.1 referrers. Nothing is re-signed, so Rekor entries and the check ride's age stay valid. The copy is verified in Flight with a read-only credential before the check goes green: digest, `.sig`, `.att`, and a promotion attestation naming this request. | Enforced | `promote` workflow; `promote-image` StepAction |
| PROM-05 | Upper clusters run tenant images only from Flight, each with a promotion attestation (`https://hangar.io/attestations/promotion/v1`) signed by the promote workflow's GitHub Actions identity on public Sigstore and verified offline. Third-party images no build produces (CloudNativePG, OTel auto-instrumentation, `bitnamilegacy`) are allow-listed by prefix. Tenant pods pull with a read-only Flight credential; the Ground credential is not on the cluster. In force on hangar-prod since 2026-10-30 (Audit from 2026-10-29). | Fails closed | Kyverno `flight-only-images` (ValidatingPolicy) and `flight-images` (ImageValidatingPolicy), Deny, `failurePolicy: Fail`, rendered by Apron `admission.flight` (POL-11) |
| PROM-06 | Only the app's own Ground repository is promotable: never a PR preview build (`<app>-pr`) or another app's image. | Enforced | `promote` |
| PROM-07 | Promoting a digest already in Flight (a rollback, a second environment) copies nothing new and adds a new promotion attestation for that release. | Enforced (not yet exercised by a live rollback) | `promote` workflow (digest copy is idempotent) |
| PROM-08 | A release merged before its promotion is a bypass and is never promoted afterwards: the merged pin names a Flight digest that does not exist, so the new pods cannot start and the previous ReplicaSet keeps serving; the missing `image-promotion` check is reported as a bypass. | Enforced (`promote` refuses a merged PR); the bypass alert is Soft | `promote`; `detect-bypass-merge` (GATE-04) |
| PROM-09 | Flight retention never deletes a release that a release file pins, a Release Record names, or an open release PR pins, nor the 10 newest releases of a package, nor one younger than 30 days. The platform plans, and only the promote repo's `prune` workflow deletes. A package without a readable gitops repo is never pruned. | **Off here** (Flight only grows: `promotion.retention.enabled` is false; the `prune` workflow is in the promoter repo since 2026-10-30 but has not run) | Glidepath `flight-prune` CronJob; `prune` workflow |
| PROM-10 | With promotion on, a cloud target (`aws-ecs`, `aws-lambda`, `azure-container-apps`) in a Flight environment is refused before it deploys: a cloud deploy copies from Ground, so nothing promoted it. Ground environments of the same app are not affected. | Enforced | `resolve-deploy-target` |
| PROM-11 | The registries and promotion settings are admin-owned: the catalog's `registries` and `promotion` values and the cluster's `admission.flight`, never `cicd.yaml` or Tower. | Enforced | Glidepath catalog values; Apron `cluster.yaml` |

## 4. Release gates

| ID | Rule | Strength | Held by |
|---|---|---|---|
| GATE-01 | Every release PR to a gitops repo runs every registered gate: `sast`, `image-scan`, `provenance`, `sbom`, `values`, `qa` and `policy-validation` are real; `itsm` is real once the catalog names a change tool (`itsm.provider`) and a stub until then. | Enforced (they run) | [Glidepath release-guardrails.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/release-guardrails.md) |
| GATE-02 | A stub never reports a pass. It logs that no check exists, returns `stub`, and shows as a grey STUB everywhere. | Enforced | [Glidepath governance-stubs.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/governance-stubs.md), ADR-0003 |
| GATE-03 | A gate stops a merge only through the gitops repo's GitHub ruleset: every gate a required check from the Pipelines as Code app, 2 approvals, no bypass actors. | **Off here** | [Glidepath github-ruleset.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/github-ruleset.md). Private repos on GitHub Free cannot enforce rulesets, so anyone with write access can merge past a red gate. |
| GATE-04 | Merging past a failed or missing gate is a break-glass bypass. It is detected after the merge and alerted (not subject to notification settings), and the PR keeps its failed checks. | Soft | `bypass-check` (`detect-bypass-merge`) |
| GATE-05 | The commit being released must be proven one of two ways: gitsign-signed (public Sigstore) by an address in the app's `allowedCommitSigners` from the admin-owned release-signing policy (GATE-16), or a GitHub PR merge that passes GATE-15. A gitsign signature is judged by gitsign alone; failing it never falls through to GATE-15. An empty signer list fails closed. Changed 2026-10-20: the list was the app's own `cicd.yaml`. | Fails closed | `provenance` gate (`verify-commit-signature`); [Glidepath commit-signing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md) |
| GATE-06 | For an app without the GitHub-merge path, land app changes by fast-forwarding a gitsign-signed commit, never with GitHub's merge button: all three button options make a new commit GitHub signs, which fails GATE-05. With the path on, the merge button is fine when an allowed login presses it. The web editor, the contents API, GitHub Apps and "Update branch" never count. | Convention (GATE-05 and GATE-15 catch it) | [commit-signing.md: merge strategy](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md#merge-strategy-what-each-way-of-landing-code-gives-you) |
| GATE-07 | The image must carry a valid SLSA provenance attestation from the platform's own Fulcio (the Tekton Chains identity), and the attestation must pass the Conforma policy. | Enforced | `provenance` gate; [Glidepath provenance-policy.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/provenance-policy.md) |
| GATE-08 | Every changed `values.yaml` passes `airframe-validate`: no secret-looking literal (`AF-SECRET-001`), no release-owned key in a human file or the reverse (`AF-OWNER-001`), and no unknown component or output (`AF-COMP-001/002`). | Enforced (subject to GATE-03) | `values` gate |
| GATE-09 | A Release Record PR (`release-record-*` branch) is not a release, and the gates skip it. | Enforced | gate triggers |
| GATE-10 | `/retest` re-runs a gate. It never skips one. | Enforced | Pipelines as Code |
| GATE-11 | A new or removed gate goes in the `releaseGuardrails` registry, and the ruleset is regenerated from it in the same change. | Convention | `hack/apply-guardrail-ruleset.sh` |
| GATE-12 | `qa` passes only when the promoted image's own test provenance (TEST-06) carries a **check ride** that is verified, `passed`, with `tests-failed: 0`, from the shared check-rides Application (`workflow-source: argocd:check-rides`), and younger than `qa.maxAge` (72h). It names what was missing otherwise. An eligible rollback is advisory. | Enforced as a check; **Soft** today (advisory, GATE-13) | `qa-gate`; [Glidepath testing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/testing.md) |
| GATE-13 | Every registry entry has `required` (default `true`). A gate with `required: false` is **advisory**: it runs and posts what it found, its check stays green, a merge past it is not a bypass, and the ruleset leaves it out. Only a glidepath PR (the chart default) or a cluster's catalog values (`releaseGuardrailOverrides`) change it: never `cicd.yaml`, never Tower, never per release. On hangar-dev `qa` is advisory until every app has a check ride. | Enforced | `glidepath-catalog.guardrails`; [release-guardrails.md: Required and advisory gates](https://github.com/jfillman/glidepath/blob/main/docs/admin/release-guardrails.md#required-and-advisory-gates-required-2026-10-19) |
| GATE-14 | `sast` and `provenance` cannot be made advisory: a catalog that sets either to `required: false` fails to render. | Enforced | `glidepath-catalog` chart render |
| GATE-15 | **GitHub-merge path** (2026-10-20, off unless the policy turns it on for the app). A commit signed with GitHub's web-flow key passes GATE-05 only when every check holds: the key is one of GitHub's pinned keys (GATE-17); the committer is GitHub; it is the `merge_commit_sha` of a PR merged into the default branch; it is on that branch, and a merge commit's second parent is the PR's head; `merged_by` is in `allowedMergers` (an empty list fails closed). `mode: strict` also requires every PR commit gitsign-signed by an allowed signer. `requiredApprovals: N` requires N approvals of the PR's final head by other allowed mergers. Defaults when on: `merger` mode, 0 approvals. The PR comment and the gate's results say which path verified the commit. Applies to tag-triggered releases too. | Fails closed | `verify-commit-signature`; [commit-signing.md: the GitHub-merge path](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md#the-github-merge-path), ADR-0027 |
| GATE-16 | The release-signing policy is admin-owned: signers, whether the GitHub-merge path is on, its mode, `allowedMergers` and the minimum approvals are set only in the catalog's `releaseSigning` values (a glidepath PR, or a cluster's `50-glidepath/glidepath-catalog` values), never in `cicd.yaml` or Tower. A product owner asks for a change; a platform admin merges it. An app's `cicd.yaml` can only tighten it (`governance.githubMerge.mode: strict`, a higher `requiredApprovals`); `governance.allowedCommitSigners` there is ignored. | Enforced (the gate reads only the catalog's ConfigMap; the schema refuses `enabled`/`allowedMergers` in `cicd.yaml`) | `release-signing-policy` ConfigMap; [commit-signing.md: who sets the policy](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md#who-sets-the-policy) |
| GATE-17 | GitHub's web-flow keys are pinned: checked in, baked into the toolbox image with a fingerprint assert, and pinned again in the gate. A signature by any other key, including a new GitHub key not yet pinned, fails closed; the retired 2017 key counts only for signatures made before 2024-01-16. The gate never fetches a key while verifying. A weekly workflow warns when GitHub publishes a different key set. | Fails closed | toolbox image, `verify-commit-signature`, `web-flow-key-check` workflow |
| GATE-18 | `policy-validation` renders every environment the release PR changes and evaluates it offline (Kyverno CLI) against the **target cluster's own** admission policies, `30-policy/` on `main` of its `gitops-<cluster>` repo. Only a Deny/Enforce failure fails the check; Audit/Warn findings are warnings. A render failure or an unreadable policy source fails it (fail closed). The policies are fetched by the token broker (`POST /policy-bundle`) with a read-only token the pipeline never sees. | Enforced | [Glidepath policy-validation.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/policy-validation.md) ([ADR-0028](https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0028-policy-validation-offline-against-target-cluster-policies.md)) |

## 5. Testing and the check ride

The test stage, the shared check ride and the evidence a release carries: [Glidepath testing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/testing.md), the check-rides repository's README, and the library paper *A test contract for Glidepath, and a QA gate that reads it*.

| ID | Rule | Strength | Held by |
|---|---|---|---|
| TEST-01 | A `test` step runs the TestWorkflow it names with the platform's context as config (`app`, `env`, `image`, `url`, `revision`, `gitUrl`, `chain`, for the keys the workflow declares) and as execution tags. A workflow never hardcodes its target. | Enforced | `run-testworkflow` |
| TEST-02 | A `test` or `execute` step whose workflow does not exist fails, naming the file. Only `test.enabled: false` skips, and it says `skipped`. | Enforced | `run-testworkflow` |
| TEST-03 | A `check-ride` step runs `<app>-check-ride` exactly as Argo CD synced it from the check-rides repository, never a file from the app repo: it refuses a workflow without the sync annotation or with another app's `hangar.io/app` label. A flow has at most one, it takes no `testName`, and it is always required. | Enforced | `run-testworkflow`, `validateFlows` |
| TEST-04 | The standard (`templates/`) is owned by SDETs **and** product owners; an app's ride (`apps/<app>/`) by its team **and** an SDET. The repo's own check requires the name, the label, a template from `templates/`, the declared config and only the app's own Secret. | Convention (code owners on a private repo on GitHub Free); Enforced with the ruleset | check-rides `CODEOWNERS`, `tools/check.py` |
| TEST-05 | In the shared `testkube` namespace a tenant pipeline may reference only its own `<app>-app-secrets`, and a workflow synced by Argo CD only `<hangar.io/app label>-app-secrets`, in container env and `content.git.tokenFrom`. | Enforced | Kyverno `testkube-secret-usage` ([ADR-0008](https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0008-kyverno-testkube-secret-policy.md)) |
| TEST-06 | Every completed test PipelineRun's SLSA provenance is signed by Tekton Chains onto the tested image's digest, carrying the run's results (`outcome`, `role`, test counts, `workflow-source`, `workflow-digest`, `execution-id`). Failed runs are attested too, so a reader selects by task name and reads the outcome, never presence. | Enforced | Chains; `test.yaml` type hints |
| TEST-07 | The environment's NetworkPolicy admits same-namespace pods only; an app lets the `testkube` namespace in through its own `glidepath/base.yaml` (`networkPolicy.allowIngressFrom`). | Convention | airframe-application |
| TEST-08 | Tower shows every attested test run on an image (the Tests step), the check ride first, each downloadable; the build provenance is the one whose pipeline ran `build-image`. | Display | Tower v0.79.0 `supplyChain.ts` |
| TEST-09 | A release record carries the check ride the qa gate read (outcome, counts, source, execution, verdict, how many runs were attested) frozen in when the record is sealed; before that Tower reads it live from provenance. The run shown is the newest verified pass, else the newest check ride, else the newest run of any role, so a failure is never hidden behind an older pass and "the team's tests ran, no check ride" reads differently from "nothing ran". | Enforced (record) / Display (live) | backend `testEvidence.ts`; Tower v0.80.0 `findReleaseTestRun` |
| TEST-10 | The Pipelines tab's Tests view lists every Testkube execution tagged with the app and downloads its JUnit report, read from glidepath-api (`listTests`, `getTestReport`) as Tower's read identity. An execution Testkube marked aborted although every step passed is shown as passed, with the note. Changed 2026-10-30: Tower read Testkube itself through the control plane's service proxy; that grant is gone. | Display | backend `/tests`, `/tests/report`; glidepath-api |

## 6. Change management (`itsm`)

The `itsm` gate wraps the company's change tool (ServiceNow first, a webhook adapter for any other): [Glidepath change-management.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/change-management.md). Every rule below applies once the catalog names a provider; with none the gate is a loud stub and the hooks are no-ops. This lab runs the webhook provider against a mock change tool.

| ID | Rule | Strength | Held by |
|---|---|---|---|
| CHG-01 | Every release PR creates a change request, or links one the caller or the PR body already names: a `normal` change for a promote, an `emergency` change for a rollback whose `parent` is the change it rolls back. The PR body and the release record carry it. | Enforced | `open-release-pr` |
| CHG-02 | The `itsm` gate passes only when the change exists and is approved or scheduled, and fails naming the change, its state and its approval. | Enforced (subject to GATE-03 and GATE-13) | `itsm-gate` |
| CHG-03 | The change follows the release: implementing on merge, closed successful when the release is healthy, closed unsuccessful when it is rolled back, with the rollback's emergency change related. A later rollback re-closes a successful change. | Enforced | `bypass-merge-check`, `release-outcome-notify`, `release-rollback-notify` |
| CHG-04 | A change tool that is down stops a release PR from opening and fails the gate; the later hooks tolerate it visibly (a red TaskRun, the release flow continues). | Enforced | `onError: continue` on the hooks |
| CHG-05 | Change-tool credentials come from a platform Secret in each `-cicd` namespace, fanned out from the platform's Infisical project; never a value. | Enforced | `itsm.credentials` ClusterExternalSecret |
| CHG-06 | Glidepath never approves, creates or moves a change on the gate's behalf. A release is held by leaving its change unapproved; a merge past an unapproved change is a bypass (GATE-04). | Enforced | `itsm-gate` |
| CHG-07 | A release record carries its change request (id, number, URL, state, approval, and the change that rolled it back), frozen in when sealed and read from the newest promote tracking record for the image before that; Tower shows it on the record and as a state chip in the list. | Display | backend `changeRequestOf`; Tower v0.80.0 `ReleaseRecordEvidence.tsx` |

## 7. Release records, modes and sign-off

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
| REL-11 | **Readiness** checks the leading candidate: changes merged, running on Ground, 24 hours on Ground, build and scans passed, signed and attested, check ride passed (a verified, passed ride from the shared repository attested on the image: what the qa gate reads), version bumped, and a healthy previous release to roll back to. A target date and closed planned issues are added when the draft has them. | **Display** | Tower `nextRelease.ts`. Nothing is blocked. |
| REL-12 | The suggested version is the last version plus the bump the merged PRs call for: breaking means major (minor before 1.0), a feature means minor, anything else patch. The real version is the image's tag. | Display | Tower |
| REL-13 | A release's outcome is decided in the sign-off environment. **Clean** means healthy, then replaced or healthy through the 7-day bake. **Rolled back**, **replaced before healthy** and **stopped before production** are the other outcomes. It is written back once, by PR. | Enforced | `releaseOutcome.ts` (`BAKE_DAYS = 7`) |
| REL-14 | A GitHub Release is opt-in per release, published only once the release is healthy in production, and tagged `v<version>` at the image's commit. An existing tag is reused only at that commit, and a tag is never moved or replaced. | Enforced | `releaseOutcome.ts` |
| REL-15 | Everyone hears when a release PR to production opens ("ready for prod") and when it merges ("released"). After a restart, nothing is announced twice. | Enforced | `release-signoff-poll` |
| REL-16 | The backend writes only PRs, commit statuses, GitHub Releases and the draft commit. It never merges. | Enforced | [Tower security.md: release records](https://github.com/jfillman/tower/blob/main/docs/security.md#release-records-what-the-backend-does-on-its-own) |
| REL-17 | The Release Record names how the released commit was proven: the gitsign signer, or the GitHub merge (PR, merger, web-flow key, approvers). It is shown green for every passing path, with a hint on a merge that the proof is GitHub's key and record, not a personal key, and frozen into the record when it is sealed. It is read only from the provenance gate's own PR comment posted by the platform's GitHub App (`glidepath.gateCommentApps`); a person's comment is never trusted for it. Records sealed before 2026-10-20 say "not recorded" (no backfill). The same proof shows on the record rows, the release cards, the pending-promotion task and the Release matrix. | Display | Tower `commitProof.ts`; backend `parseGateComments`; [Glidepath commit-signing.md: Evidence](https://github.com/jfillman/glidepath/blob/main/docs/admin/commit-signing.md#evidence-how-a-releases-commit-was-proven-2026-10-20-phase-3) |
| REL-18 | The readiness score's **Commit proof** line weighs how the commit was proven: gitsign 6, GitHub merge strict 4, GitHub merge 2, nothing when not recorded or not required (cloud targets). It only adds points; no older record's score moves. | Display | Tower `computeConfidence` / `confidenceBreakdown` |

Full detail: [Tower release records](https://github.com/jfillman/tower/blob/main/docs/release-records/index.md).

## 8. Rollback

| ID | Rule | Strength | Held by |
|---|---|---|---|
| RB-01 | A rollback is an ordinary release of an earlier image: a PR, the gates and a merge. Owners start it (`tower.release.rollback`, audited high). It applies to Kubernetes Flight environments; a cloud target rolls back by a release pin PR (`tower.release.pin`, ADR-0020). | Enforced | Glidepath `rollback-release`; Tower |
| RB-02 | The target must be one of the five newest releases of that app, environment and cluster that reached healthy. The gates work this out from the release records, never from the PR's text. | Enforced | `extract-promoted-image` `rollback-eligibility` |
| RB-03 | On an eligible rollback, `sast`, `image-scan` and `sbom` are advisory, because that image already ran there. Provenance, values, commit signing and approvals still apply. | Enforced | [Glidepath release-state.md: rollback](https://github.com/jfillman/glidepath/blob/main/docs/admin/release-state.md#rollback-adr-0021-phase-4) |

## 9. Supply chain

| ID | Rule | Strength | Held by |
|---|---|---|---|
| SC-01 | Every pod in an app's `-cicd` namespace, image builds included, meets Pod Security `baseline`: not privileged, no added capabilities, no host namespaces or mounts, no `Unconfined` seccomp/AppArmor. Builds run rootless BuildKit as UID 1000; they can't meet `restricted` because the builder needs a user namespace. Each `-cicd` namespace carries `pod-security.kubernetes.io/enforce: baseline`, so a pod that breaks it is refused at admission (since 2026-10-17). Until then this rule said `restricted` (kaniko), which never held: kaniko ran as root. | Enforced | Pod Security admission, labels set by Glidepath's tenant-onboarding ApplicationSet; [security.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/security.md#build-isolation), [rootless-builds.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/rootless-builds.md), [ADR-0026](https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0026-buildkit-image-builds.md) |
| SC-02 | Tekton Chains signs every image and its provenance with a short-lived certificate from the build cluster's own Fulcio (its own trust root, never the public one), and logs the signatures in the platform's Rekor. Rekor's signing key persists, is never replaced, and is never in git, Infisical or a terminal. | Enforced | [Glidepath image-signing.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/image-signing.md) |
| SC-03 | Tower colours a supply-chain step by its verification. **Green**: verified. **Amber**: present but unverified, for a reason that isn't tampering. **Red**: contradicted, so don't promote it. **Grey**: missing. A signature with no Rekor entry counts as unsigned. | Display | [Tower supply-chain.md](https://github.com/jfillman/tower/blob/main/docs/supply-chain.md) |
| SC-04 | Readiness's "Signed and attested" passes only on a verified attestation, never on one that is merely present. | Display | Tower `isSignedAndAttested` |
| SC-05 | Build signatures and provenance are checked at release (GATE-07), not when a cluster admits an image. Since 2026-10-30 hangar-prod admits tenant images only with a promotion attestation (PROM-05), which records that the image went through the promoter after the gates; the Chains provenance itself is not re-checked at admission (it carries no Rekor inclusion proof, and the build cluster's Rekor is unreachable from prod). The Tower debug image is checked at admission too (BG-04). hangar-dev checks nothing at admission. | Enforced at release; at admission on hangar-prod through PROM-05 | see [section 18](#18-rules-that-are-not-enforced-yet) |

## 10. Live operations from Tower

| ID | Rule | Strength | Held by |
|---|---|---|---|
| OPS-01 | Tower has no standing write access to any cluster. Sync, force sync, terminate, Rollout actions and pod restarts run through one Argo CD account, which can act only on app projects: deny rules cover the platform projects. | Enforced | Argo CD RBAC |
| OPS-02 | Through Argo CD, Tower deletes nothing but a single pod. It never rolls back to an Argo CD revision and never edits an Application's spec. | Enforced | Argo CD role `tower-pod` (`delete//Pod/*` only) |
| OPS-03 | Sync and force sync: owners on Ground, admins only on Flight. | Enforced | ACC-04 |
| OPS-04 | Restarting a pod never takes the last ready pod of a Flight ReplicaSet. On Ground it needs an explicit "accept downtime". | Enforced | [`podRestart.ts`](https://github.com/jfillman/backstage/blob/main/packages/backend/src/podRestart.ts) |
| OPS-05 | Skipping canary analysis on Flight (promote full, skip step) is allowed to owners as a **bypass**: audited critical and announced to everyone. Every Rollout action is announced. | Soft | `tower.rollout.bypass` |
| OPS-06 | Re-running and cancelling a PipelineRun is for owners, and Tower does both through glidepath-api, never by writing the PipelineRun itself. The cluster refuses any PipelineRun write from `tower-actor`, and admits from glidepath-api only Glidepath's own run shape in an app's or InfraService's `-cicd` namespace, and on an existing run only a cancel. Changed 2026-10-30: `tower-actor` wrote the runs itself, held to the shape by `tower-pipelinerun-shape`. | Enforced | `glidepath-api-pipelinerun-shape` policy (POL-01) |
| OPS-07 | Configuration changes (values, env XR, ConfigMap files, `cicd.yaml`) are PRs, never direct edits. | Enforced | `tower.config.edit` |

## 11. Break-glass debug sessions

| ID | Rule | Strength | Held by |
|---|---|---|---|
| BG-01 | Only the app's owners can ask for a session. On Ground it starts at once. On Flight a second person approves first: an owner who isn't the requester, or an admin. | Fails closed | Tower routes, and the cluster refuses a grant whose approver is the requester |
| BG-02 | An admin may **break the glass**: a Flight session with no second person. It is audited critical, announced to everyone, and must be reviewed afterwards by someone other than the requester (an owner, an admin or a break-glass reviewer). | Soft (the review) | `tower.breakglass.self` |
| BG-03 | A session lasts 15, 30 or 60 minutes, with one 15-minute extension. It ends after 10 minutes idle or 2 minutes disconnected. Each person may have one open session. | Enforced | backend timers; expiry labels the cluster acts on |
| BG-04 | Never exec. A session is a separate debug container: the signed, digest-pinned Tower debug image, non-root, read-only, all capabilities dropped. On Flight the cluster refuses `kubectl exec` into app namespaces for everyone but operators. | Fails closed | `tower-breakglass-*` admission policies |
| BG-05 | Backstage has no standing debug rights. For each session it binds one of two debug roles to itself, in one namespace, with an expiry. | Fails closed | `tower-breakglass-rolebinding` |
| BG-06 | Every byte is recorded. A session that can't be recorded never starts. Recordings are object-locked for 365 days, their hashes anchored in Rekor, and the app's owners can read them. | Fails closed | [Tower break-glass guardrails](https://github.com/jfillman/tower/blob/main/docs/break-glass/guardrails.md) |
| BG-07 | Admins can end anyone's session, and on Flight so can the session's approver. Anyone can end their own. | Enforced | `tower.breakglass.terminate` |

## 12. Images and retention

| ID | Rule | Strength | Held by |
|---|---|---|---|
| IMG-01 | Owners can prune only their app's own packages (`<app>`, `<app>-pr`, `<app>/cache`). Platform packages are refused whatever the app is called. | Enforced | `imagePrunePlan.ts` `PLATFORM_PACKAGE` |
| IMG-02 | A prune shows its plan first and deletes only that plan. If anything changed, it refuses and shows the new plan. At most 300 versions go per run, audited high and announced. | Enforced | `imagePrune.ts` |
| IMG-03 | Always kept: anything running or that a ReplicaSet can scale back to; anything named in git (default branch or an open PR); each environment's last five healthy releases; anything in flight; an open PR's head image; anything under 14 days old; the 10 newest builds. For the cache: the 20 newest layers and anything under 14 days. A release is deleted whole or not at all. | Enforced | `imagePrunePlan.ts` |
| RET-01 | Release-tracking records on the dev cluster are deleted after 14 days. Never deleted: a merged or progressing release, or the five newest healthy releases per app, environment and cluster. Outcomes are copied into the git record before the 14 days are up. | Enforced | `release-record-sweeper` |
| RET-02 | A release that is merged or progressing with no new fact for 45 minutes raises `ReleaseStalled`, once per state. | Enforced | `release-record-sweeper` |
| RET-03 | A pipeline stage that hasn't started its next stage 10 minutes after finishing is reported as stalled. | Enforced | [stalled pipeline detector](https://github.com/jfillman/glidepath/blob/main/docs/admin/stalled-pipeline-detector.md) |

## 13. Service catalog (Airframe)

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

## 14. Cluster admission policies

Rules the API servers themselves enforce, so a bug in Backstage, or a compromised Backstage, can't get around them.
Every one is native ValidatingAdmissionPolicy that fails closed, and each is scoped to its own objects. The exceptions
are the debug-image signature check and `glidepath-cloud-deployer-pods`, which run in Kyverno's webhook (also fail
closed).

| ID | Policy | Cluster | Rule |
|---|---|---|---|
| POL-01 | `glidepath-api-pipelinerun-shape` | kiac-dev | Backstage (`tower-actor`) may not create or patch a PipelineRun; glidepath-api's have Glidepath's shape only (OPS-06). Kyverno ValidatingPolicy. Was `tower-pipelinerun-shape` until 2026-10-30, which held Backstage's own PipelineRuns to that shape. |
| POL-02 | `tower-rolebinding-delete` | kiac-dev | Backstage may delete only `tower-breakglass-*` RoleBindings. |
| POL-03 | `tower-breakglass-rolebinding` | both | The only grant Backstage may create. On Flight it must name an approver other than the requester, or carry the glass-broken mark. |
| POL-04 | `tower-breakglass-debug-container`, `-debug-image` | both | The exact debug image digest and its cosign signature, hardened settings, and process access only for the approved session. |
| POL-05 | `tower-breakglass-pod-delete`, `-pod-annotate` | both | Backstage deletes only debug or copy pods, and patches only the process-access annotation. |
| POL-06 | `tower-breakglass-no-exec` | kind-prod | No exec into app pods for anyone but operators. Attach only to a debug container. |
| POL-07 | `no-long-lived-sa-tokens` | kiac-dev | No long-lived ServiceAccount token Secrets in `backstage-system`. |
| POL-08 | `testkube-secret-usage` | kiac-dev | A tenant's TestWorkflow may reference only that tenant's own Secrets in the shared `testkube` namespace. |
| POL-10 | `glidepath-cloud-deployer-pods`, `-taskruns`, `-pipelineruns`, `-jobs` | kiac-dev | Only a cloud deploy may run as `glidepath-cloud-deployer`, the one identity AWS deploy roles trust. Decided by who created the object, never by labels: pods only from Tekton's controller or the Job controller, TaskRuns only from Tekton, Jobs only from Crossplane, and only they may change a TaskRun's or Job's spec later (others may add metadata, as Chains, Results and the garbage collector do), and a PipelineRun may give it only to the catalog `deploy` Pipeline's `deploy-aws-lambda` and `deploy-aws-ecs`, not run-wide, with no pod-template `env` or volumes. |
| POL-11 | `flight-only-images`, `flight-images` | hangar-prod | Tenant pods run only Flight images with a promotion attestation, or an allow-listed third-party prefix (PROM-05). Scoped to namespaces labelled `hangar.io/managed-secrets`. Kyverno, Deny, fails closed. |
| POL-09 | (how policies are written) | both | Every optional field is guarded with `has()`, and every policy is scoped by match conditions, so a CEL error can only refuse its own objects. A policy change widens before it narrows. |

Full detail: [Tower break-glass admission policies](https://github.com/jfillman/tower/blob/main/docs/break-glass/admin/policies.md).

## 15. Credentials and secrets

| ID | Rule | Strength | Held by |
|---|---|---|---|
| CRED-01 | Secrets are references to Infisical, never values in git or an XR. | Enforced on gitops repos (GATE-08), convention elsewhere | `AF-SECRET-001` |
| CRED-02 | People create credential material themselves, in Infisical. It is never pasted into a chat, a terminal transcript or a repo. | Convention | [Glidepath secrets-management.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/secrets-management.md) |
| CRED-03 | Tower holds no long-lived cluster credential. Reads use the pod's projected token (600 s). Writes on kiac-dev use a `tower-actor` token minted for each action. | Enforced | [Tower credentials](https://github.com/jfillman/tower/blob/main/docs/credentials/index.md); POL-07 |
| CRED-04 | The GitHub App's private key never leaves `platform-system`. A release gets an installation token for its own gitops repo only. | Enforced | `token-review-interceptor` |
| CRED-05 | The platform has one identity per external system (GitHub, Infisical, AWS, Azure), in `crossplane-system`. Apps never hold one. Each app reads only its own Infisical project. On AWS that identity is an IAM role assumed with a projected ServiceAccount token; nothing is stored (since 2026-10-16). | Enforced | Airframe provider configs, External Secrets; [Airframe cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md#how-keyless-aws-access-works) |
| CRED-07 | A Lambda deploy reaches AWS as `glidepath-deploy-<functionName>`, a role made for that one function: push to its repository and update its code, nothing else. An ECS deploy reaches AWS as `glidepath-deploy-ecs-<service>`, made for that one service: push to its ECR repository, register task definitions, update that service and pass its execution role to ECS, nothing else. It is assumed with a one-hour token for `glidepath-cloud-deployer`; no other pipeline step has AWS access, and there is no stored-key path: a deploy that can't assume the role fails. The target's bootstrap Job uses the same role; an `AwsLambdaTarget` has no access-key mode, and on a cluster without web identity it stops at `AwsLambdaTargetNeedsWebIdentity` (`AwsEcsTargetNeedsWebIdentity` for ECS). | Enforced (Lambda since phase 4, 2026-10-16; ECS since 2026-10-17, glidepath#119 and airframe#95; `aws_credentials_test.sh` in catalog-ci; Airframe `no-web-identity` render cases) | [Glidepath cloud-deploy-identity.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/cloud-deploy-identity.md); POL-10 |
| CRED-08 | Every IAM role a cloud-target composition creates carries the permissions boundary `HangarCloudTargetBoundary`. The Crossplane identity can't create a role, or add rules to one, without it, and nothing may remove it. | Enforced (IAM) | `HangarCrossplaneCloudTargets` v3; [Airframe cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md) |
| CRED-09 | A composition never removes something that already exists because a condition it was created under stopped holding, or because an observed value it was rendered from is missing for a reconcile. Conditions gate creation only; deleting the XR is the only way to delete its cloud resources. | Enforced (render tests) | Airframe v0.3.144 and v0.3.145; incident 2026-10-16 in [cloud-credentials.md](https://github.com/jfillman/airframe/blob/main/docs/admin/cloud-credentials.md#a-rule-for-composition-authors-never-gate-what-already-exists) |
| CRED-06 | The image-prune token can only read and delete packages. The backend holds it, never the browser. | Enforced | IMG-01 |

## 16. Notifications

| ID | Rule | Strength | Held by |
|---|---|---|---|
| NOT-01 | SLO alerts go to the app's owners, or to everyone if the app has no owner. **Budget exhausted** fires above a burn of 1.0 and clears below 0.9. **Burning fast** fires when both 5-minute and 1-hour burn exceed 14.4x, and clears below 12.96x. **No data** fires after 15 empty polls (about 30 minutes); a failed query doesn't count. | Enforced | [Hangar SLO docs](../slo/README.md), `sloTransitionPoll.ts` |
| NOT-02 | Release announcements, Rollout actions, analysis bypasses, broken glass, Flight pod restarts and image prunes go to everyone. | Enforced | Backstage notifications |
| NOT-03 | A bypass merge (GATE-04) is alerted however notifications are set. | Enforced | `detect-bypass-merge` |

## 17. AI agents

| ID | Rule | Strength | Held by |
|---|---|---|---|
| AI-01 | An agent passes the same pre-merge checks a person does, and works within `AGENTS.md`. | Enforced (the checks), convention (`AGENTS.md`) | Airframe |
| AI-02 | Agent runs go only to clusters marked `autopilotReady` (AF-05). | Enforced | AgentRun composition |
| AI-03 | Per-agent tool tiers, budgets and field allow/deny lists (Clearance) are built but not deployed. | Off here | [Autopilot design](../autopilot/design.md) |

## 18. Rules that are not enforced yet

Every place where a rule above is weaker than it reads, in one list:

| Gap | Rules | What it means today |
|---|---|---|
| GitHub Free can't enforce rulesets or required checks on private repos. | GATE-03, REL-03 | Gates and sign-off report but don't block. A bypass is detected and announced (GATE-04, REL-05). |
| A GitHub-merged release rests on a GitHub session. | GATE-15 | Decided 2026-10-20 (ADR-0027): an allowed merger's GitHub session is enough to release a PR's code, and in `merger` mode nobody gitsign-signed that code. On hangar-dev the path is on for every onboarded app (backstage, boarding-api, flight-api, gate-api), in `merger` mode with 0 approvals (one person merges). Raise `requiredApprovals` once a second real person merges; use `strict` where every author can run gitsign. |
| The ruleset assumes every PR is a release PR. | GATE-03 | Once enforced, non-release PRs would wait forever for gates that never run. Fix before enabling GATE-03 ([ruleset audit](https://github.com/jfillman/glidepath/blob/main/docs/admin/github-ruleset.md#problems-found-in-the-audit-2026-09-27)). |
| App repos aren't gated. | ENV-02 | By design: Ground is self-service. Only gitops repos get gates. |
| `itsm` is real only with a provider. | GATE-01 | This lab points it at a mock change tool (CHG-01 to CHG-06 hold against the mock). |
| `policy-validation` checks only validating policies. | GATE-18 | ImageValidatingPolicy, mutating policies, parameterised ValidatingAdmissionPolicies and Pod Security Admission labels are not evaluated; admission still enforces them at sync. Every policy on hangar-prod today is a break-glass rule, so every current release passes until app-facing policies land in `30-policy/`. |
| `qa` is advisory on hangar-dev. | GATE-12, GATE-13 | `required: false` until every app with a Flight environment has a check ride (boarding-api has one). The check runs and reports; a missing ride does not fail it. |
| The check-rides repository's owners are not enforced. | TEST-04 | A private repo on GitHub Free: code-owner review is convention. The repo holds no secrets and can be made public. |
| An app opens its NetworkPolicy to tests by hand. | TEST-07 | A platform default for the `testkube` namespace is on the test framework roadmap. |
| Production SLO burn isn't read during the bake. | REL-13 | Production's Prometheus is on and canary analysis uses it, but the outcome is still decided from the rollout alone, so "clean" can't yet mean "no SLO burn during bake". |
| Build signatures aren't checked at admission. | SC-05 | hangar-prod checks the promotion attestation (PROM-05), not the Chains provenance; hangar-dev checks nothing, so an unsigned image could run there if it got into git. |
| The promote workflow trusts whoever starts it. | PROM-02, PROM-03, PROM-05 | The workflow checks its input's shape, not the gates. Anyone who can start it (the promoter App through the broker, or `riley-roooo`, who owns the repo) gets a valid promotion attestation for any Ground digest, and PROM-05 would admit it. Glidepath only starts it after PROM-03. |
| Flight admission depends on Kyverno being up. | PROM-05 | `failurePolicy: Fail`: while hangar-prod's Kyverno admission controller is down, new pods in tenant namespaces are refused. It restarted 354 times between 2026-10-18 and 2026-10-30. |
| Flight retention is off. | PROM-09 | Flight keeps every promoted image until `promotion.retention.enabled` is turned on (dry run first: neither the package listing with the read credential nor deletion with the workflow's token has been tried). |
| Cloud environments can't be Flight while promotion is on. | PROM-10 | Refused rather than promoted. No app has a cloud Flight environment today; cloud promotion is a recorded Glidepath follow-up. |
| `airframe-validate` doesn't run on app repos or the tenants repo. | GATE-08, CRED-01 | Airframe roadmap AF-4b. |
| Agent and security-review limits are convention. | AF-06, AF-07, AI-03 | Clearance isn't deployed, and no rule requires a security reviewer. |
| Azure deploys use a stored secret. | CRED-07 | Lambda and ECS deploys are keyless (2026-10-16/17). Azure Container Apps still logs in with a stored service principal secret; next is workload identity federation ([Glidepath known gap 43](https://github.com/jfillman/glidepath/blob/main/docs/admin/known-gaps.md)). |
| Only admins can run software templates. | ACC-02 | App teams can't scaffold a new service themselves. Intentional for the lab; revisit before onboarding other teams. |

## 19. Keeping this page true

- A change that adds, changes or removes a rule updates this page in the same change: here when the change is in
  this repo, or with a linked Hangar PR when it isn't. The component's own docs keep the detail.
- A rule that exists only in code is a bug in this page. Add it with the next free ID in its section.
- A retired rule keeps its row, struck through, with the date and the reason. Its ID is never reused.
- The commit list at the top says what this page was last checked against. Re-check it after any release of Tower,
  Glidepath, Airframe or Backstage that touches permissions, gates, release records or admission policies.
