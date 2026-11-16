# Owner digest, 2026-11-14

Everything from today's updates that you need to know or act on, in one place. Detail for the Go
port's security findings is in the review page: https://claude.ai/artifact/81NmvD3YkijvUQNxgT1fRM

## 1. On your plate

### Decisions

Still open: the spec suggestions (36 main, 16 Cloud). You are reviewing them.

Decided 2026-11-14:

| # | Decision | Your answer | State |
|---|---|---|---|
| 2 | A-9 canary placement | EKS dev if it is ready when the canary is; otherwise a hard cutover on hangar-dev | In the A-9 plan |
| 3 | Port autopilot-api to Go before cutover (S6) | Yes | Planned |
| 4 | A revoked signing key is revoked for statements too | Keep | Merged |
| 5 | Earliest allowed back-date for a recipient key | Add a registration record later | Not started |
| 6 | W6 calls | Keep | Released in 0.48.0 |
| 7 | G-ARGO-10c calls | Keep | Merged |
| 8 | Cap the Slack clear tier | Cap it: 0 to 2, tier 3 can never be turned on | Merged (clearance#176, 98dc042), not released |
| 9 | Mirror W6 status into the Cloud spec | Yes, as a suggestion | Done: four of my existing Cloud suggestions updated |

### Things only you can do

- Done by you 2026-11-14: branch `a9-s3-people-triggers` deleted; leftover Postgres containers removed.
- **W6 gate inputs:** a Vanta sandbox, a first real recipient key, sign-off on the verify page's security review, and the EKS environments.
- **Carried from earlier waves:** G-ARGO-7 exit tests and the Warn to Deny flip; G-ARGO-8 (make `clearance-gate` required); O-4 AWS apply; ratify the hangar-prod exceptions; Slack wiring (Infisical keys, DNS record); delete branches `clearance-slack` and `web-2-package`.
- **Dated:** the 30-day packet re-run is due 2026-12-09.

## 2. What shipped today

| Item | State |
|---|---|
| Clearance 0.48.0 (W6: P-1 to P-4) | Released. Not deployed anywhere. `grc.*` and `verifyPage.enabled` are off. |
| Backstage `1.0.2-f60b9fe` (clearance-ui v0.1.1) | Live on hangar-prod. |
| Glidepath BuildKit retry fix (#246) | Live on hangar-dev. |
| G-ARGO-10c annotation opt-in (clearance#175) | Merged to main. Not released. Off by default. Never run on a cluster. |
| A-9 S0, S1, S2, S5a (autopilot #104, #103, #105, #106) | Merged. Go gateway is off by default; no image published. |
| A-9 S3 (autopilot#108) | Open. Two findings in the trigger fires-once logic being fixed. |
| Revocation (clearance#174) | Merged to main (947a5da). Not released. |

## 3. Things to know, by area

### Clearance 0.48.0 (W6)
- Nothing is proven on a cluster. The W6 gate needs EKS, a Vanta sandbox and the verify page sign-off.
- OIDC recipients are not built; recipients are key-only.

### Revocation (merged, not released)
- Revokes a delivery, a recipient key, or a retired signing key. The key in use cannot be revoked without rotating first.
- A verifier that caches the key set trusts a revoked signing key for up to 5 minutes.
- A read already streaming when the revoke lands may finish.
- A packet cut before a key revocation does not know about it. The remedy is a new packet.
- A careful forger who strips a revocation and rewrites the packet's figures is not caught unless the reader holds the original packet id. Reasoned, not tested.
- A receipt submitted with a stolen key before anyone revokes it cannot be told from an honest one.
- For the first seconds after a restart, delivery and recipient-key revokes answer 503.
- One new nullable database column: `clearance_signing_keys.revoked_at`.

### G-ARGO-10c
- To use it: apply the CRD first, then the agent, then turn the opt-in on; add the ignore entry on the parent Application or ApplicationSet; list and label destination namespaces; add a `protection` entry for the agent on the core.
- While an Application is opted in, edits to its source in the parent's git are ignored and the parent shows Synced. Remove the annotation, edit, annotate again.
- Per-object expiry is enforced by the agent only (every 30 seconds, and only while it runs). Admission has no clock.
- A namespace whose clearances all expire refuses every write until a new clearance arrives.
- Anyone who can edit an Application's annotations can opt it out. That is recorded, not refused.
- The parent check is a guard against fighting the app-of-apps, not a security boundary.
- With the opt-in off, two things still change: exception scanning can report fewer out-of-band exceptions, and the core's decision for an environment outside the static list reads the store and treats a failed read as protected.

### A-9 Go gateway
- The Go gateway can serve a run end to end in code: sign-in, sessions, spawn, run identity, results, expiry, read tools. Missing: triggers and the inbox (S3, open), definitions (S4), write tools (S5b, S5c), the read API (S6), a published image (S7).
- Run identity requires the pod name `agent`. That is unverified on a cluster. If wrong, every call from a run is refused.
- Run identity also assumes nobody but the gateway and Crossplane can create a namespace named `agent-<run>`.
- The 5 ms load-test bar is not confirmed. Quiet runs read 0.6 to 2 ms; runs under load are not evidence. I owe a clean measurement.
- Two settings the lab render must turn on, both off by default: `AUTOPILOT_JWKS_ALLOW_HTTP`, `GLIDEPATH_API_ALLOW_HTTP`.
- Owner groups resolve to nobody until S6, so only a session's own person and admins can use person controls.
- Go differs from Python on purpose in eight places (listed in the review page). The canary comparison must allow for them.
- A rollback to Python in the middle of a trigger could open a second session: Python does not read what Go records on a claim.
- CI drift guard: a change to a ported Python file fails CI until the Go side is updated or the change is confirmed irrelevant.

### How the work is run
- Every slice gets an independent security review. A fix round that rewrites locking or state gets a second one. Each such round so far introduced a new defect that the next review caught.
- Builders must reproduce a finding before fixing it.
- Today's parallel builders hit the account's 5-hour usage limit at about 14:10 Pacific; two were cut off mid-task with their work saved. I will run fewer at once.
- PR Lens does not re-run on later pushes in these repos. I ask it to with a comment and read the result before merging.

## 4. Not started, could start (code only)

- OIDC recipient identity for P-1.
- G-ARGO-10d (several Argo CD instances) and 10h (cluster-scoped grants).
- C-15 warm-standby core; C-16 bring your own gateway and CI.

## 5. Blocked on a cluster or on you

- G-ARGO-10e, f, g (load test and platform rollout on hangar-prod).
- A-3, A-6 wiring and live runs; A-10 Skyport agents on the cluster.
- A-9 canary (S8) and cutover (S9).
- W6 gate run.
- A-2 is deferred by you.

## 6. Evening update (2026-11-14, late)

### Waiting on you
- **Backstage prod release:** https://github.com/jfillman/gitops-backstage/pull/303 (clearance-ui 0.1.2, all UI fixes). `itsm-` approval, the Clearance hold and the merge are yours. First deploy that should show an outcome and attestation for Backstage.
- **Pipeline hardening, how to proceed:** planned work package (my recommendation), merge glidepath#248/#249 now, or park.
- **Second approver identity for the lab:** needed once the proposer/people rules ship (you are author, promoter and only owner).
- **PR Lens free trial ended** on your account: private-repo PRs (backstage) are no longer reviewed.

### Shipped since the first digest
| Item | State |
|---|---|
| Clearance 0.49.0 (Map fix, G-ARGO-10c, revocation, Slack cap 0-2) | Released. hangar-dev roll-out PRs being prepared. |
| clearance-ui 0.1.2 (panel width, Objects columns, Tier popup, Tool rules, Map gate names and popups) | Released; backstage#283 merged; prod release PR #303 open. |
| Backstage prod namespace enrolled with Clearance | Live: gitops-hangar-prod#44 merged, label applied. Admission is warn-and-audit. |
| autopilot#106 (S5a) | Was already on main; PR record closed. |

### Open PRs, none merged
| PR | What | State |
|---|---|---|
| autopilot#108 (S3) | Inbox, person controls, triggers | Round five: a real crash-injection test first, then five fixes |
| autopilot#109 (S5b) | Write tools | Third round: file-under-protected-file, trailer forgery, tests restored |
| clearance#178 | People behind a deploy cannot clear it | Last round after three reviews |
| glidepath#247 | Proposer from the source PR, not the release bot | Held until #178 and the hardening land |
| glidepath#248, #249 | Pipeline least privilege | Three rounds; four structural holes still open |

### Things to know
- **Found today in the platform as it runs:** an app's build/test scripts run with the pipeline's token. Proven read-only on hangar-dev: they can write the pipeline's release records and start a task that gets a token Clearance trusts as registrar. Not exploited, not yet fixed on any cluster.
- **Still open after the hardening PRs:** registry push credential readable from a Containerfile `RUN` (push to other apps' images); release/test pipelines startable by pushing a `v*` tag or unprotected `main`; chart rendering in a credentialed step; `pipeline-runner` still writes release records and holds the Clearance token.
- **Rules that will change who can clear, once shipped:** everyone who proposed, wrote, merged or promoted a deploy is excluded from clearing it; a rollback to an old version may leave a small team with nobody eligible (break-glass, 4 h).
- **Direct push to main:** decided, owner-declared baseline; not built.
- **Usage limit hit twice today** (14:10 and about 19:00 Pacific) with four agents running. I am holding to two at a time.
- **Render drift on hangar-prod:** a full Apron render would also move Clearance providers 0.46.0 to 0.47.0 and drop three Crossplane provider lines. Left out of #44; needs its own look.
