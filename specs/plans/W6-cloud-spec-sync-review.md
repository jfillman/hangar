# W6 vs Clearance Cloud Build Specification: sync review

Status: research only. Nothing was edited, commented on, or applied. No Clearance Cloud doc was changed.
Date of evidence: memory notes dated 2026-11-13 and 2026-11-14.

## 0. Sources and read coverage

Read from the Claude Docs project `XByvsn2wm6xmVcGnA32tJb` ("Clearance Cloud Build Specification", rev 36, tab `a02c7263-c88e`, prose node `b4f8ac64-40bd`). Block ids below are `m0mwfjdhaqa.<n>` unless noted.

Read in full: §1 How to use (.1194, .1218), Roles table (.1502), §2 Where each piece runs (.5790), Repos (.6971), §3 Current state (.8865), §4 Components (.11187), §5 Accounts (.14968), Edge hosts (.19778), Data (.17964), Identity (.20703), INF-2..INF-9 cards (.28767 to .35300), CS-1..CS-10 cards (.36517 to .45134), CW-1, CW-3, CW-5, CW-8 cards (.46556, .48203, .49089, .50369), BK-1, BK-2 (.51643, .52496), §11 wave table (.53333), §12 tenancy rules (.57982) and live verification (.60089), §6 gap table (.25165), §13 open questions (.64687), risks (.62978), waiting-on-user (.63872), domain decision (.66694), and the INF-1 card (.27728).

Not read (blocks not opened): CW-2, CW-4, CW-6, CW-7, CW-9 cards; §5 Network, Compute, WAF, Delivery, Observability, Backup, Security, sizing sub-blocks (.16228, .17157, .20396, .21774, .22600, .23393, .24437; .23898 security list was read); §4 Contracts (.13511); §11 parallel tracks; §12 docs-and-memory (.60504); §13 intro (.60873).

Companion doc read: `LBzQN4AninX9aKUbL7p5sv`, "Clearance hosted App with a subscriber-hosted core" (rev 11). Read: Summary, the "Three deployment modes" table, and the decision sentence. Not read: Architecture, Flows, Failure modes, Threat model, Tenancy, Open questions, Build plan.

Local comparison sources: `/Users/jerf/tech/clearance-packets/W6-P-series-cards.md` (P-1..P-5, W6 gate, §12 guardrail); `/Users/jerf/tech/clearance-packets/design-clearance-cli-slack.md` (CLI and Slack design, owner decisions 2026-11-13); clearance origin/main `docs/web.md`, `docs/slack.md`, `docs/clearance-api.md` (Map, targets, attestations, whoami); memory `project_clearance_map_build.md`, `project_clearance_w6_build.md`, `project_clearance_cloud_k0.md`.

Not checked: the code. Statements about "built" are taken from the docs and memory notes, not from running code.

## A. What the Cloud spec is

- **Scope.** A hosted product, "Clearance Cloud", drawn in direction A (Ledger), run on AWS, plus two Backstage changes (§0 intro, .56; "The cloud is mostly hosting and screens on top of code that already exists or is already specified", .338). It states the P-series of the main spec "defines receipts, sampling, statements and GRC push" and that the cloud hosts them and "does not redefine them" (.10033).
- **Repos** (§2 Repos table .6971): `jfillman/clearance` (public, Apache 2.0; core, CLI, verifier, verify and public-ledger pages P-3, record-sync client CS-2 client half); `jfillman/clearance-cloud` (private, new: Go services `cmd/cloud-api`, `cmd/cloud-worker`, `cmd/cloud-ingest`, the TypeScript portal `web/`, `@clearance/cloud-ui` kit, Helm charts); `jfillman/clearance-cloud-infra` (private, new: Terraform); `jfillman/gitops-clearance-cloud` (private, new: rendered manifests and Argo CD apps for cloud-staging and cloud-prod); `jfillman/backstage` (BK-series). The user creates the three new repos (W-table, §13 waiting-on-user .63872). Note: `jfillman/clearance-ui` (the standalone UI package in docs/web.md) is not in this table.
- **Components** (§4 table .11187): cloud-ingest (Go, Deployment, `ingest.<domain>`, per-tenant workload identity, re-verifies hash chain and signatures); tenant cell (the `clearance` binary in `--mode=hosted-recorder`, one namespace per tenant); cloud-api (Go, `api.<domain>`, portal's only backend, sessions, RBAC, grants, statements, packets, integrations registry, plans, meter); cloud-worker (Go, SQS-scaled: packet builds, statement issue, insurer statements, GRC push, escrow export, email, intelligence later); portal (TypeScript, React, Vite, S3 + CloudFront, `app.<domain>`, workspace P1/S1-S7 and auditor AU1/AU2); verify-web (Go, the open `clearance` binary P-3, `verify.<domain>` and `ledger.<domain>`, server-rendered, works with JavaScript off, V1/V2/L1); public ledger (Go, Tessera); witnesses (Go, `clearance-witness`, separate AWS account plus at least one external operator).
- **Accounts** (§5 table .14968): management (User only); security (delegated admin; operators read-only); log-archive (org CloudTrail and Config, Object Lock); shared-services (ECR, Route 53 public zone, GitHub OIDC roles, the ops Clearance core that gates the cloud's own changes); cloud-staging (full stack, small); cloud-prod-us (full stack in us-east-1, pilot light us-west-2); witness (`clearance-witness` on ECS Fargate; user only); cloud-prod-eu (later, "Not planned: USA only for now", decided 2026-11-09).
- **Environments.** Staging and prod. Lab data only in staging ("Staging data is synthetic or Hangar lab data", §12 live verification .60408).
- **Waves** (§11 wave table .53333; the Cloud's own K-series, distinct from the main spec's W-series):
  - K0 Foundation: INF-1..INF-6, CS-1, CW-1, BK-1 alongside. Gate: a tenant provisioned on staging from nothing in under 10 minutes, owner signs in through SSO, tenant-isolation suite passes, prod empty app holds at the gate.
  - K1 Workspace: CS-2, CS-3, CS-4, CS-8, CW-2, CW-3, CW-6, CW-7, INF-7, INF-8, INF-9, BK-2. Starts when K0 passes. Gate: records arrive and verify; hangar-dev's core syncs 30 days to staging and the copy verifies byte for byte; ops tenant live in prod.
  - K2 Outside parties: CS-5, CS-6, CS-7, CS-9, CW-4, CW-5. Starts when K1 passes "and the main spec's P-1 and P-3 merged" (.54211). Gate: "Verifiable by a stranger. A statement issued from S2 verifies on the public verify host with all seven checks and with JavaScript off."
  - K3 Auditor portal: CW-8, plus hosting for the main spec's P-2 and P-5. Starts when K2 passes and P-2 merged. Gate: a firm draws and verifies a 25-record sample and signs a receipt the next packet carries.
  - K4 Intelligence: CS-10, CW-9. After K2 and the main spec's I-2.
- **Packages** (cards, §7 to §10): INF-1..INF-9 (Terraform, clearance-cloud-infra); CS-1..CS-10 (Go, clearance-cloud, plus client half in clearance); CW-1..CW-9 (portal, `web/`); BK-1, BK-2 (backstage). Each card has Repos, Depends on, Build, Done when, Rollout, User steps.
- **DNS and hostnames.**
  - Zone: `clearance.hangarplatform.dev` is decided and delegated to a Route 53 zone in shared-services (§13 Q1 .64816, decided by James 2026-11-09; INF-2 .28799 and user steps .29549 require the NS delegation "at whoever hosts hangarplatform.dev's DNS").
  - Hosts (§5 Edge table .19778 and the `<domain>` decision .66694): `app.` (CloudFront to S3 SPA, `/api/*` to cloud-api ALB); `verify.` and `ledger.` (CloudFront to app ALB to verify-web; `/tiles/*` from S3; public, cached); `ingest.` (ingest ALB directly, not behind CloudFront, for mTLS); `auth.` (Cognito custom domain); `api.` (cloud-api); `status.` (hosted paging, §5 Observability .23237). No `slack.` host appears in the rows read.
  - Account owning the zone: shared-services (§5 accounts table, §INF-2 build).
  - Account owning the account-level DNS parent: `hangarplatform.dev` itself (Cloudflare per memory; the NS delegation is a user step).
- **Identity** (§5 Identity .20703): operators via IAM Identity Center (three permission sets); CI via GitHub OIDC; customers via Cognito, one IdP per tenant (SAML or OIDC), MFA for owners; cloud-api is a BFF with auth-code-with-PKCE and httpOnly cookies; recipients and firm users get an emailed magic link (Cognito custom auth challenge, 15-minute single use) or their own org SSO, "decided 2026-11-09".

## B. Coverage map: portal, sign-in, verify page, receipts, sampling, statements, GRC, Slack, CLI

| Surface | Cloud spec | Built or planned (local) | Where it should live and run |
|---|---|---|---|
| Subscriber portal / hosted UI | Yes. CW-1..CW-7 and the portal row (.12459). TypeScript SPA, `web/` in clearance-cloud, S3 + CloudFront at `app.<domain>`, backend is cloud-api (BFF). Kit `@clearance/cloud-ui` (CW-1 .46616). | `clearance web`: Go BFF inside the clearance binary, in-memory sessions, forwards the person's own ID token (docs/web.md; WEB-4 built per memory). UI package `jfillman/clearance-ui`, Vite shell, pinned into the image via `web-ui.lock` (WEB-2, held for owner, separate repo recommended). | Two different products. The Cloud portal is multi-tenant, Cognito, cloud-api. `clearance web` is single-core and people-IdP. See C7. |
| Sign-in (IdP) | Cognito per region; per-tenant SSO (SAML/OIDC); recipients by magic link or own SSO (.20703, §13 Q2 decided). | people-dex + GitHub in the lab (D19 interim memory); `clearance web` uses `CLEARANCE_WEB_ISSUER` generic OIDC (docs/web.md). Owner decision 3 (CLI design): people-dex in lab, enterprise IdP via the same OIDC config. | The Cloud's Cognito is an OIDC issuer, so the core's OIDC config can accept it. But the core has a single-tenant allowlist. See C9 and C15. |
| Verify page (`verify.`) | Yes. verify-web = the open `clearance` binary (P-3), server-rendered, JS off, V1 statement, V2 recipient detail, L1 ledger explorer (.12698, .41553). | P-3 in W6 card: the hosted page at `verify.<domain>/s/{id}`, rendered in apron's public route with a rate limit (W6 P-3 Repos and Rollout). | Cloud spec: hosted by cloud on EKS. W6 card: apron public route. See C2, C4. |
| Receipts (assurance providers, recipients) | Cloud CS-5 "grants register on top of P-1" (.40805); K2 gate. The gap table lists "P-1 deliveries and credentials (Proposal)" (.26146). | W6 P-1: deliveries, scoped time-boxed recipient credential, signed receipts, `clearance receipt sign`. Core owns the endpoints. | Cloud hosts and records; the core defines the credential. See C1. |
| Sampling (P-2) | K3 hosting (.54511). Cloud CW-8 is its screen (.50369). | W6 P-2 in clearance repo (`GET /v1/packets/{id}/sample`). | Core defines; Cloud hosts at K3. No conflict in placement. |
| Statements | Cloud S2 composer in portal; cloud-worker issues; statement summaries in S3 `clearance-statements-<env>` (.18996). "Locked invariants enforced in the core, not the UI" (.41741). | P-3 statement `POST /v1/statements` in the core (W6 P-3). | Core enforces invariants; Cloud issues. Consistent, but the Cloud says "the core" and K2 is a cloud deliverable. See C5. |
| GRC push (Vanta) | cloud-worker job (.12321, .19552); S2 "GRC hub status" (.49310). | W6 P-4 in clearance repo; provider interface; Vanta sandbox gate. | Core owns the provider; cloud-worker runs it in hosted mode. See C10. |
| Slack | Not covered. The outline and read blocks contain no Slack term. | `clearance-slack`: separate Go binary in clearance repo (owner decision 4); public URL `https://slack.clearance.hangarplatform.dev` planned (memory 2026-11-13); lab first (Gateway LAN IP plus cert-manager DNS-01 Route 53). | Not covered. Needs an owner decision on where it runs (C6, C14). |
| Person CLI | Not covered as a surface. The Cloud's CLI-facing API is cloud-api. | `clearance` person commands: device-code login, keychain ID token <=1h (CLI design; P1 started 2026-11-13, P2 merged overnight). | Runs against the core (and clearance-api). Cloud spec silent on CLI; it does mention `clearance verify` and `clearance packet` (CS-2 .38435, CS-7 .42605). |
| Map / target registry, attestations | Not in the §3 current-state table as read. §3 lists evidence record, ledger, packet, coverage route as Built. | clearance#153 (Map, `PUT /v1/targets/{source}`), #154 (attestations), #155 (names-only), all merged 2026-11-13. Apron targets publisher live on dev and prod. | Core-owned. The Cloud's CS-8 and CW-7 imply a registry; the Cloud spec does not name the Map. See C17. |
| Public ledger (`ledger.`) | Yes: CS-3 (.39353), L1 at `ledger.<domain>` (.42038). Tessera on S3, Aurora MySQL coordination. | Tessera POSIX built; AWS driver is a spike (CS-3 .38991). | Cloud. Consistent. |
| Hybrid (vendor GitHub App + relay, subscriber-hosted core) | Not covered. The Cloud spec has no relay component. | Companion doc `LBzQN4...` "Clearance hosted App with a subscriber-hosted core": a third mode between self-hosted and fully hosted; the core runs on subscriber network with one outbound connection to a vendor relay. | Not covered by Cloud. See C13. |

## C. Conflicts and overlaps

Severity key: **BLOCKS W6** = W6 cannot pass its gate or merge as written until decided; **NEEDS DECISION** = a decision is needed before the named package is built or merged; **INFO** = informational, record it.

**C1. Recipient credential authority. NEEDS DECISION before P-1 merge.**
- W6 P-1 puts `GET /v1/packets/{id}` and the scoped, time-boxed credential in the core, every fetch a record.
- Cloud CS-5 (.40805, .41011 to .41075) makes "grants" a cloud-api register with "every read through cloud-api or verify-web becomes a ledger record in the tenant chain". Its Repos and Depends on name P-1 as input.
- Cloud §6 gap table row "Grants, access register, every read recorded" lists "P-1 deliveries and credentials (Proposal)" as the existing piece (.26146). So both specs think P-1 owns the credential.
- Without a decision, cloud-api could mint a second credential type. Recommended resolution in D1.

**C2. Recipient detail on the public verify host. NEEDS DECISION (security, blocks P-3 route rendering).**
- Cloud verify-web row (.12799): "V2's recipient detail comes through cloud-api under the recipient's grant", served on `verify.<domain>` (host table .19996).
- W6 §12 guardrail (W6 cards, "The hosted verify page is a public surface"): "the recipient detail level is never on the public route."
- Cloud §12 test list (.58952): "Free verification: no auth on verify routes." V2 needs a grant, so the Cloud spec contradicts itself on the verify routes.
- Resolution (D2): keep V2 recipient detail off the public host, or put V2 on an authenticated host.

**C3. External witness before the W6 gate. BLOCKS W6 gate as written.**
- W6 P-3 done bar: "checkpoints countersigned by a witness Clearance does not run" is check 4 of the seven; the W6 gate says "a verification statement verifies on the hosted page with all seven checks".
- Cloud §13 Q7 (.66046): "Deferred by James, 2026-11-09. ... K0 and K1 run with the Clearance witness alone, and statements print 'not yet independently witnessed'. An external witness is needed before K2's gate."
- Cloud K2 gate needs a passing verify host. So the W6 gate cannot be fully green until an external witness exists, unless the lab run prints the "not yet independently witnessed" line and the gate is worded to accept it.
- Resolution (D2 and E3): owner decides whether the W6 gate accepts the printed limitation for lab, or an external witness is brought forward.

**C4. Where the verify page runs (two deployment targets for one hostname). NEEDS DECISION.**
- W6 P-3 rollout: "Clearance release, apron render (the public route and its rate limit)". W6 memory: "deploy + run the gate only on EKS".
- Cloud: verify-web in clearance-cloud EKS, behind CloudFront and the app ALB (.12698, .19996). The Cloud's K2 gate, not W6, is where it goes public.
- Two live sources for `verify.clearance.hangarplatform.dev` would collide. Resolution in D2.

**C5. Gate and wave sequencing. NEEDS DECISION.**
- W6 gate and Cloud K2 gate are close to the same outcome: "verifiable by a stranger" (W6, §11 wave table row W6) versus "Verifiable by a stranger ... on the public verify host with all seven checks and with JavaScript off" (Cloud K2).
- Cloud K2 starts only after K1 gate and "the main spec's P-1 and P-3 merged" (.54211). Cloud K3 needs P-2 merged (.54565).
- W6 memory: W6 is "code-only until the AWS environments exist". Cloud K0 is blocked by the org account quota (memory, Phase 1 apply errored 2026-11-10; support case open). So W6's EKS gate depends on K0, and K0 is blocked.
- Resolution in D2 and E6: W6 gate = code plus lab proof against fakes; K2 gate = hosted proof.

**C6. Hostname and zone for Slack versus the Cloud estate's DNS. NEEDS DECISION (blocks Slack lab step).**
- Cloud INF-2 (.28767, decision Q1 .64816): `clearance.hangarplatform.dev` delegates to a Route 53 zone in shared-services. INF-2 creates it; INF-2 depends on INF-1, which is quota-blocked.
- Slack plan (memory 2026-11-13; CLI/Slack design in clearance-packets): `publicUrl https://slack.clearance.hangarplatform.dev`, owner delegates `clearance.hangarplatform.dev` to Route 53, "lab first: record -> lab Gateway LAN IP, cert-manager DNS-01 (Route 53)".
- Collision: the lab step needs a writable zone before INF-1/INF-2 exist; if the Slack lab zone is created separately, there are two authoritative zones for one delegated name. If it is created inside the Cloud zone, the Cloud estate now owns a host it does not list.
- The Cloud host table (.19778) has no `slack.` row. Cloud is silent on Slack.
- Severity: NEEDS DECISION. Blocks the Slack public URL, not the Slack code.

**C7. Two UIs, two BFFs, two design kits. NEEDS DECISION before WEB-2.**
- Cloud portal (CW-1 .46556): TypeScript React/Vite SPA in clearance-cloud `web/`; `@clearance/cloud-ui` kit in clearance-cloud; BFF is cloud-api (INF-5 .32073 "cloud-api is a backend-for-frontend"); Cognito; sessions and RBAC in cloud-api.
- `clearance web` (docs/web.md): Go BFF in clearance binary; in-memory sessions; people IdP; UI package in `jfillman/clearance-ui`; WEB-2 (package location) held for owner, separate repo recommended (memory overnight 2026-11-13).
- Overlap: both are the subscriber UI. Two design kits (`@clearance/cloud-ui` and `clearance-ui`) would drift. Both claim the Tower kit names and the Clearance visual language.
- Severity: NEEDS DECISION. Recommended resolution in D4.

**C8. Own-doc inconsistency on the standalone UI. INFO.**
- design-clearance-cli-slack.md §3: "Standalone web page (`clearance-web`) ... Not worth a new product now."; decision 10 "no clearance-web now (standalone UI under separate consideration)".
- Memory: WEB-1..5 scheduled; WEB BFF merged as clearance#161 overnight 2026-11-13. Record the decision explicitly.

**C9. Recipient identity wording. NEEDS DECISION (wording).**
- W6 P-1: "Recipient identities are OIDC or a registered key, never a Clearance account."
- Cloud §5 Identity (.21577, decided 2026-11-09) and INF-5 (.32236): recipients sign in with an emailed magic link through a Cognito custom auth challenge, or their org SSO. That is a Cognito user record, which is an account in practice. "They never get a Clearance password" (.21710) is consistent with W6, but "never a Clearance account" is not defined.
- Resolution: define "Clearance account" as a Clearance role or permission record; a Cognito recipient is an IdP identity.

**C10. GRC push host. INFO.**
- W6 P-4 implements the provider in clearance; Cloud runs GRC push as a cloud-worker SQS job (.12321, .19552).
- Consistent with the "summaries, never copies" rule (Cloud §12 .58900; W6 P-4 done bar). Choose the host per mode; no change to the outbound-payload test.

**C11. P-2 hosting timing. INFO.**
- W6 builds P-2 now in core. Cloud hosts it at K3 (.54511), after K2. No conflict; the Cloud spec's CW-8 screen depends on it.

**C12. Cloud spec version and status are stale. INFO.**
- §0 intro .338 says "Clearance v0.36.0 has the record, ledger, packet and offline verifier". Memory: clearance is at 0.47.0 (2026-11-13). The P-series rows are still labelled "Proposal (main spec W6)" (.10006, .26146, .26256) though W6 started 2026-11-14.
- Update the baseline when the owner next edits the doc (not done here).

**C13. Hybrid mode not in the Cloud spec. NEEDS DECISION (informational for W6).**
- The companion doc `LBzQN4...` defines a hybrid mode: subscriber-run core, vendor-run public GitHub App, outbound relay, "every record stays in the subscriber's chain." Its table: fully-hosted "Vendor, one logical core per tenant"; hybrid "Subscriber's network."
- Cloud spec §4 and §2 describe only the fully hosted cell and the self-hosted core; no relay component (§4 components table .11187).
- Open: who hosts the verify page and the P-3 statement when the core is hybrid. Not covered by either spec as read.

**C14. Slack and CLI absent from the Cloud spec. INFO (or NEEDS DECISION if Slack is to be Cloud-hosted).**
- No `clearance-slack` or person CLI in the Cloud outline as read. Owner decision 4 (CLI/Slack design): standalone `clearance-slack` in the clearance repo, separate binary.
- Cloud spec should either list it as out of scope or add it to the Cloud's integrations registry (CS-8 .26384 mentions integrations, not Slack).

**C15. Multi-tenant assumptions the core lacks. INFO for W6; NEEDS DECISION for K1.**
- Cloud requires: one tenant cell per tenant; "one key, one database, one prefix, one signing identity per tenant" (§12 .58346); tenant isolation suite gating every release (.58025); SCIM 2.0 (CS-1 .37145); RBAC in cloud-api.
- Core (docs/web.md, docs/clearance-api.md): single deployment identity; `CLEARANCE_OIDC_ALLOWED_USERS`, `CLEARANCE_ADMINS` are deployment-wide; one signing identity per deployment. `--mode=hosted-recorder` appears in Cloud (.11707); I did not check whether it exists in code.
- Not a W6 blocker. It is a K1 blocker if the core is reused for hosted tenants.

**C16. Map/target registry and attestations not in the Cloud spec. INFO.**
- Core has `PUT /v1/targets/{source}`, `GET /v1/map`, attestation routes (clearance-api.md .58-.64 and §"coverage Map" .146). Apron publishes targets. Cloud §3 current-state table lists neither. The Cloud's CW-7 settings and CS-8 integrations registry would need them.

**C17. Operators' IdP differs from people's IdP. INFO.**
- Cloud operators: IAM Identity Center (§5 .20704). Lab people: people-dex. Different identities by design; the spec says "User (platform owner)" holds management. No conflict, but record it.

**C18. Verify routes and rate limiting. INFO.**
- W6 P-3: app-level rate limit plus unguessable ids. Cloud: "Every public endpoint has a rate limit in WAF and in the service" (§12 .59480). Aligned. Cloud's security review pass before each public surface (.59705) matches W6 P-3 "security-review pass before its route is rendered". Aligned.

## D. Recommended adjustments

**D1. W6 P-1 (being built now).**
- Proceed. Keep the three routes and the receipt format.
- Record in the P-1 contract: the core issues and verifies the recipient credential (audience-bound, time-boxed, each fetch a record). cloud-api only proxies it in hosted mode and records its own grant register as a ledger view. This matches Cloud "Hosts them and does not redefine them" (.10033) and resolves C1.
- Change "never a Clearance account" to define the term (C9) before the first recipient is onboarded. Code can go ahead.
- Severity: needs decision before P-1 merge (C1, C9). No change to sequencing.

**D2. P-2..P-4 order and placement.**
- P-2: no change. Build in the core; K3 hosts it.
- P-3: build the statement and verify route in the open binary as the card says. Keep recipient detail (V2) off the public route (W6 §12 rule, C2); ask the Cloud spec author to correct V2 and the §12 "no auth on verify routes" test. Do not render the hosted page from apron for the lab on the production hostname (C4). For the W6 gate, state that check 4 needs an external witness, or accept "not yet independently witnessed" in the gate wording (C3).
- P-4: no change in placement; provider in clearance, runs as cloud-worker in hosted mode (C10). Keep the Vanta sandbox gate.
- Gate sequencing: W6 gate = code plus lab proof against fakes; K2 gate = hosted proof on `verify.` (C5).

**D3. Slack public URL and DNS plan.**
- Do not create `slack.clearance.hangarplatform.dev` in the Cloud zone until INF-2 exists and the owner confirms the zone (C6).
- Options for the owner: (a) add `slack.` to the INF-2 host table and create it in the shared-services zone once it exists; (b) for the lab only, use a lab-only hostname on the lab Gateway and move to the Cloud zone later.
- Socket Mode needs no inbound; the https link page and Sign in with Slack need a public hostname. Keep the lab-only option until (a) is decided.

**D4. Standalone web UI.**
- No change to WEB-1..5 for the self-hosted (subscriber core) case.
- Add an explicit boundary: the Cloud portal (CW-1..CW-7, cloud-api BFF, Cognito) is the hosted product; `clearance web` is the self-hosted single-tenant UI. Do not build the Cloud portal on `clearance web` (C7).
- WEB-2: resolve the package location with one design kit. Recommend `jfillman/clearance-ui` as the single package, consumed by both `clearance web` and the Cloud portal, with `@clearance/cloud-ui` retired or made a consumer. Owner decision.
- Start no new UI package until WEB-2 is decided.

## E. Open questions for the owner

1. Is the core the sole authority for recipient credentials, with cloud-api only proxying and recording (C1, D1)? Yes/no.
2. Does V2 recipient detail stay off the public verify host (W6 §12 rule), or move to an authenticated host (C2)?
3. Does the W6 gate accept the printed "not yet independently witnessed" limitation for the lab run, or is an external witness brought forward (C3)?
4. Which deployment hosts `verify.clearance.hangarplatform.dev`: EKS Cloud (K2) or apron (W6)? Both cannot (C4).
5. Is the W6 gate code-plus-lab, with the hosted gate left to K2 (C5, D2)?
6. Who creates the Slack lab DNS record, and in which zone? Is `slack.` added to the Cloud host table (C6, D3)?
7. Is `clearance-ui` the single UI package for both the self-hosted UI and the Cloud portal (C7, D4)?
8. Should "recipient identity is never a Clearance account" be reworded to define a Cognito recipient as an IdP identity (C9)?
9. Is Slack in scope for Cloud (hosted), or stays in the customer's cluster (C14)?
10. Is hybrid mode (LBzQN4) in scope for the Cloud build, and who hosts its verify page (C13)?
11. Update the Cloud spec's version baseline and P-series status labels now, or at the next edit (C12)?

## Summary for the caller (C, D, E in 15 lines)

1. BLOCKS W6: external witness. W6 check 4 and the gate need a countersigned checkpoint Clearance does not run; the Cloud defers the external witness (§13 Q7), so the gate needs wording or an earlier witness (C3).
2. NEEDS DECISION before P-1 merge: recipient credential authority. Core (W6) or cloud-api (Cloud CS-5)? Recommend core (C1, D1).
3. NEEDS DECISION (security): Cloud puts recipient detail (V2) on the public verify host and has a test saying verify routes need no auth; W6 says recipient detail never on the public route (C2, D2).
4. NEEDS DECISION: verify host has two deployment targets (apron for W6, EKS for Cloud K2) (C4).
5. NEEDS DECISION: W6 gate and Cloud K2 gate describe the same "verifiable by a stranger" outcome; K2 also needs P-1 and P-3 merged (C5).
6. NEEDS DECISION (blocks Slack lab step): `clearance.hangarplatform.dev` is delegated to a shared-services zone that INF-1/INF-2 create; the Slack lab record needs a zone now; Cloud host table has no `slack.` (C6, D3).
7. NEEDS DECISION before WEB-2: two UIs and two BFFs (cloud-api/Cognito vs `clearance web`/people-IdP) and two design kits (C7, D4).
8. NEEDS DECISION (wording): "recipient never a Clearance account" vs Cognito magic-link recipients (C9).
9. NEEDS DECISION: hybrid mode (LBzQN4) and its verify host are not in the Cloud spec (C13).
10. INFO: Cloud spec is silent on Slack, CLI, and the Map/targets/attestations (C14, C16).
11. INFO: Cloud spec cites clearance v0.36.0 and labels P-series "Proposal"; now 0.47.0 and W6 started (C12).
12. INFO: Cloud multi-tenant assumptions (one key, database, prefix, identity per tenant) are not met by the single-deployment core; K1 issue, not W6 (C15).
13. INFO: GRC push host (cloud-worker vs core) and P-2 hosting at K3 are consistent with the "hosts, does not redefine" rule (C10, C11).
14. D: proceed with P-1 under a core-authoritative credential; P-2 no change; P-3 keep V2 off public route, do not deploy to the production hostname from apron, state witness limit; P-4 no change; Slack DNS waits on zone decision; one UI package (`clearance-ui`) before WEB-2.
15. E: 11 open questions in §E; the owner must answer 1-4 before P-1 merges and P-3 routes render.
