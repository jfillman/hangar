# Pipeline trust: finishing the Glidepath hardening

Written 2026-11-14. Owner decision the same day: merge glidepath#248 and #249, then finish what is still open.
Repo: jfillman/glidepath. Background and findings: memory `project_gate_source_identity_hardening`.

## Threat

A developer who can open a pull request in an app repo (and, separately, one who can push to it) runs code inside the
pipeline. That code must not be able to act as the platform: no Kubernetes token, no release-record writes, no secrets
beyond its own build, no pushes to other apps' images, no token Clearance trusts.

## Done by #248 and #249

- Repo code (build, unit test, integration script, image build) runs as `source-runner`: no rights, no token.
- `pipeline-runner` cannot create runs, so repo code cannot mint a Clearance-audience token.
- A `.tekton` file may start only allowlisted Pipelines with checked parameters; run identity is bound to what
  Pipelines-as-Code recorded.
- Image push target bound to the app's repository; onboarding-resync target derived; per-task service accounts.

## Slices still open (one PR each, one independent security review each)

| # | Slice | Closes | Notes |
|---|---|---|---|
| T1 | Split `build-image`: build to an OCI layout in a credential-less step/pod, push from a separate trusted step | Registry push credential readable from a Containerfile `RUN` (a PR author pushing to another app's images) | First: it reaches other apps and prod. Also establish the credential's real scope and propose per-app scoping. |
| T2 | Token-less rendering: `helm template` and any chart/kustomize render run in a task with no token and no secrets; gates consume the output as data | Token in a developer-readable log through a chosen chart | Touches `clearance-gate.yaml` and `policy-validation-gate.yaml`: coordinate with #247. |
| T3 | Verified protection: a trusted check (glidepath-api endpoint) asks the git host whether the pushed ref is protected by a ruleset or branch protection that requires review; privileged Pipelines refuse otherwise. Required by default; an explicit setting records "Off here" for a host plan without rulesets | Release, deploy and test Pipelines started by pushing a `v*` tag or an unprotected `main` | The lab is GitHub Free: the setting is off there and the docs say what that leaves open. |
| T4 | Split `pipeline-runner`: a release-record writer (only `open-release-pr`, `mark-release-merged` and the tasks that legitimately write records), a `clearance-gate` account (only the gate task gets the Clearance audience), and a read-mostly runner | Any remaining path to release records or the registrar token | Needs Clearance to trust `app-*-cicd/clearance-gate` beside the old principal, then drop the old one: a Clearance settings change in the cluster render, staged. |
| T5 | glidepath-api rerun policy in the cluster repos allows `taskRunSpecs` for `source-runner` | Reruns of build runs refused once the policies are in Deny | Apron template change plus render. |
| T6 | Roll-out: Glidepath release; control plane in Warn and Audit; resync each app's `.tekton/`; hostile-file check (a `.tekton` that pre-sets Pipelines-as-Code annotations); switch to Deny | The whole change live | hangar-dev first. Prod only with the owner's OK. |

Order: T1, T2 and T3 are independent (two at a time). T4 after T1 and T2. T5 before T6. T6 last.

## After that

- glidepath#247 (proposer from the source PR) gets its final review and merges: its trust in the release record holds
  only once T4 is live.
- Owner-declared baseline for a commit with no merged PR (decided 2026-11-14): built on #247.
- Glidepath sends `source` (authors, mergers, promoter) to Clearance once clearance#178 is released.

## Status, 2026-11-15

| Slice | State |
|---|---|
| T1 build/push split | Merged (glidepath#250). Never run with real BuildKit/oras: first-live-run checklist in the upgrade note. |
| T2 token-less render | glidepath#253 open, third fix round (token in fetch failure logs; workspace template rule; name rule too broad). Also closed a yq program injection that existed on main. |
| T3 ref protection | Merged (glidepath#252): configuration check. Superseded as the basis for `protected` by T3b. |
| T3b per-commit review evidence | Owner decision 2026-11-15: yes. Not started. |
| T4 split pipeline-runner | Not started. |
| T5 rerun policy (apron) | In progress. |
| T6 roll-out | Last. Lab sets `refProtection.mode: off`; glidepath-api before the catalog. |

## T3b: per-commit review evidence (owner decision 2026-11-15)

`protected` no longer rests on reading ruleset bypass lists (which needs the App to hold repository Administration:
write). It rests on evidence that every commit being released was reviewed:

- For the ref and sha of a privileged run, take the commits between the last verified release of that app and
  environment and this sha (first release: the sha alone).
- Each commit must belong to a pull request merged into the protected branch of the source repository (base ref and
  base repository checked; squash and merge commits resolved through `merge_commit_sha`).
- That pull request must carry an approving review from someone other than its author and other than any author of its
  commits, submitted on the pull request's final head (no push after the last approval).
- A commit with no such pull request (direct push, admin bypass, force push) makes the verdict `unreviewed`: refused
  under `required`. The owner-declared baseline (decided 2026-11-14) is the only way past it.
- Read-only App permissions only (contents, pull requests, metadata). `githubRead.refProtectionPermissions` and the
  elevated-token path are removed.
- The ruleset and branch-protection reads stay as an informational note in the result.
- Same resolution logic as glidepath#247 (source proposer): one library, used by both.
