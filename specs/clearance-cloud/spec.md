---
title: Clearance Cloud Build Specification
program: Hangar · Clearance Cloud
board: https://claude.ai/artifact/N9sDgHyHKjF8aMfAcxjr8f
source: https://claude.ai/artifact/XByvsn2wm6xmVcGnA32tJb
updated: 2026-11-24
---

Nov 9, 2026 · @James

This spec builds Clearance Cloud, the hosted product drawn in direction A (Ledger), and runs it on AWS. It also covers the two Backstage changes that go with it. It sits beside the [Clearance & Autopilot Build Specification](https://claude.ai/artifact/BCosjaYXnJzghRF6VZsL5D) and follows its card format, rules and release discipline.

The cloud is mostly hosting and screens on top of code that already exists or is already specified. Clearance v0.47.1 has the record, ledger, packet and offline verifier. The P-series of the main spec defines receipts, sampling, statements and GRC push. This spec adds four things:

- a multi-tenant control plane;
- a hosted record store that the tenant's in-cluster core syncs to;
- the portal;
- the AWS estate that runs them.

The design sources are the [UI design doc](https://claude.ai/artifact/9f8jNFAyjcvVGcRGX5Z2oU) (its Clearance Cloud sections) and the **Clearance Cloud** page of the [UI canvas](https://claude.ai/artifact/9yqroF5srM4U7htTeCkqUj).

Build order in one line: the AWS foundation and tenancy, then record sync and the workspace, then outside parties (statements, sharing, public ledger), then the auditor portal, then intelligence.

Status words follow Hangar: Built, Draft, Proposal, Unverified. Everything in this spec is Proposal unless marked.

## 1. How to use this spec {#how-to-use-this-spec}

This spec is for a managing Claude Code session that builds Clearance Cloud by handing work packages to subagents. Every package in sections 7 to 10 is self-contained. Each card names its repos, dependencies, build, proof on cloud-staging, and the steps only the user can take.

### Roles

| Role | Reads | Owns |
| --- | --- | --- |
| Managing agent | Sections 1 to 6, 11, 12 and 13 in full; each card before delegating it; the main spec's sections 1 and 12 | Sequencing, release tags, image and chart pins, the gitops render for cloud-staging and cloud-prod, Terraform plans, live verification, memory and roadmap status, every hand-off to the user |
| Subagent | Its card, section 12 here and in the main spec, and the README, AGENTS.md and docs the card names | One PR in one repo unless the card says otherwise, with tests and docs. It reports a PR link, what it verified and what it left out |
| User (platform owner) | The spec and PR links | Merges, new repos, AWS account creation and payer settings, every `terraform apply` to a prod account, DNS and domain purchase, the KMS key-policy ceremony, external witness agreements, first real tenants and firms, and any decision a card marks "user" |

### Package card format

Cards use the main spec's fields: **Id and title**, **Repos**, **Depends on**, **Build**, **Done when**, **Rollout** and **User steps**. Four new series:

- **INF-n** is AWS infrastructure, in Terraform.
- **CS-n** is cloud services, in Go.
- **CW-n** is the portal web app, in TypeScript.
- **BK-n** is Backstage plugin changes.

A card that depends on a main-spec package names it by its id (for example P-3 or C-5).

**Model per subagent** follows the main spec (owner decision 2026-11-07). Coding uses Sonnet 5.5 (`sonnet`). Read-only research uses Haiku 5.5 (`haiku`). A design-heavy card such as CS-1 uses `sonnet`, with its research given to `haiku`. The model goes on the brief line.

### Rules every subagent follows

1. Everything in section 12 of the main spec still holds: fresh worktree, `git -C` and `gh --repo` on every call, no force-push, no skipped signing, docs in the same PR, green CI before reporting.
2. Clearance core code lives only in jfillman/clearance. Cloud code imports it as a Go module by tag and never forks or copies it. A change the cloud needs in the core is a Clearance PR first.
3. Nothing in the cloud may weaken an open-core property. `clearance verify`, the verify page and the record schemas stay in the Apache-2.0 repo.
4. Infrastructure changes are Terraform PRs. A subagent may run `terraform plan` against cloud-staging with a read-only role. It never runs `apply`; the managing agent applies to staging, and the user applies to prod.
5. No AWS credential is written to a file, a log or a PR. CI and agents use GitHub OIDC roles only.
6. The final report names what was descoped and why, next to what was done.

### The cloud release chain

Run one step per command, never chained with `;`:

1. The clearance-cloud PR merges (user). Tag `cloud-vX.Y.Z` off main once CI is green. The image workflow builds, signs and pushes to ECR. Record each index digest.
2. The gitops-clearance-cloud PR bumps the digests for cloud-staging only. It touches exactly the expected files.
3. Argo CD syncs cloud-staging. Run the card's live checks there and quote the evidence.
4. The same bump goes to cloud-prod as a second PR. That bump is a Clearance-gated change: Argo CD's gate holds it until the user clears it in production. This is the cloud dogfooding the product.
5. Record the evidence in memory and in clearance-cloud/docs/roadmap.md.

Infrastructure follows the same shape. The clearance-cloud-infra PR runs a plan in HCP Terraform, Clearance's HCP run task gates it, the managing agent applies to staging, and the user applies to prod.

### The done bar

A package is done when all of these hold:

- Its PRs are merged.
- Its tags and pins are live on cloud-staging.
- Its positive test, negative test and tenant-isolation test (section 12) passed against cloud-staging, with the evidence quoted.
- Docs are updated.
- The roadmap status reflects it.

A screen is done only when it renders from live staging data. A mock fixture does not count.

## 2. Context and product boundaries {#context-and-product-boundaries}

The brief's line is "open enforcement, paid assurance", and the cloud is the paid assurance half. The gate, the classifier, the record schema and `clearance verify` stay open and run in the customer's cluster. The cloud sells what a customer cannot easily run alone:

- the hosted recorder and retention;
- witnesses the customer does not run;
- packets and statements;
- outside-party access and acceptance receipts;
- SSO, Slack and GRC surfaces;
- the intelligence add-on.

### Where each piece runs

| Piece | Runs in | Why |
| --- | --- | --- |
| Decision core, gate providers, collectors | Customer cluster and cloud accounts (unchanged) | The decide path has a 20 ms p99 budget in-cluster and must work when the cloud is unreachable |
| Hosted recorder: record store, tenant ledger, retention | Clearance Cloud, one tenant cell per customer | The paid product. Records arrive from the in-cluster core by sync (CS-2) |
| Packets, statements, receipts, grants, access log | Clearance Cloud | Outward-facing, and every read is a ledger record |
| Verify page and public ledger pages | Clearance Cloud, served by the open-source `clearance` binary (P-3) | Verification must be reproducible from open code |
| Portal (workspace, auditor portal) | Clearance Cloud, TypeScript single-page app | The main spec's language table names TypeScript for the portal |
| Witnesses | One in a separate Clearance account, at least one external, optionally the tenant's own | The Architecture's rule: the operator is never its own witness |

A Regulated-tier customer may self-host the whole cloud stack from the same charts and Terraform modules. That is a packaging option, not a separate build; INF modules take an `operator` input for it.

### Repos

| Repo | Visibility | Holds |
| --- | --- | --- |
| jfillman/clearance | Public, Apache 2.0 | Core, CLI, verifier, the verify and public-ledger pages (P-3), the record-sync client (CS-2's client half) |
| jfillman/clearance-cloud (new, user creates) | Private | Go services (`cmd/cloud-api`, `cmd/cloud-worker`, `cmd/cloud-ingest`), the TypeScript portal (`web/`), the `@clearance/cloud-ui` design kit, Helm charts, docs and roadmap |
| jfillman/clearance-cloud-infra (new, user creates) | Private | Terraform: the account vending, network, EKS, data, edge and identity modules, and per-environment roots |
| jfillman/gitops-clearance-cloud (new, user creates) | Private | Rendered manifests and Argo CD Applications for cloud-staging and cloud-prod |
| jfillman/backstage | Private | The BK-series changes to the Clearance plugin |

Apron is not used for the cloud. Apron renders Hangar clusters from cluster.yaml, and the cloud's clusters are rendered from clearance-cloud's charts directly. The same render-and-diff discipline applies.

### Rules the cloud keeps

These come from the UI design doc's "Rules the cloud portal keeps" and the main spec's guardrails. Section 12 turns each one into a test.

1. No score.
2. Exceptions cannot be hidden inside a chosen scope.
3. Blind prints as blind.
4. Issued is immutable: supersede or revoke, never edit.
5. Every outside read is a ledger record.
6. Summaries, never copies, to GRC hubs.
7. Verification is free and needs no account.
8. The public ledger holds hashes only.
9. Verified vs claimed shows on every field.
10. Tenant isolation is absolute: no query, key, bucket prefix or log line crosses tenants, except the opt-in intelligence export under its own consent.

## 3. Current state {#current-state}

Nothing of Clearance Cloud exists yet: no repo, no AWS account, no hosted component. What exists is the core it hosts, released as Clearance v0.36.0 on 2026-11-09, and the Backstage plugins. Main-spec waves W0 to W4 are code complete.

| Piece | State | What the cloud takes from it |
| --- | --- | --- |
| Evidence record `clearance.evidence/v1.1` with observations and health (O-1) | Built | The schema every hosted record follows. `POST /v1/records` already de-duplicates by provider, kind, source and event id, which record sync relies on |
| Evidence ledger (C-3) | Built, off unless configured | A Tessera log on the POSIX driver with witness countersignatures. The cloud needs it on object storage (CS-3) |
| Witness (`cmd/clearance-witness`, `charts/clearance-witness`) | Built | Deployed in the separate witness account as is |
| Packet (C-5) and offline verifier (C-4) | Built | The packet builder runs in cloud workers. Freeze and incident views exist as `--view` |
| Coverage route `GET /v1/coverage` (O-1) | Built | Feeds P1's statement, S1, C4 and the health strips |
| Operational class (I-1), tier 3 approvers are people (C-14) | Built | Printed on statements and the insurer profile |
| HCP run task (G-TF-6), Argo CD gate, conformance (G-TF-7, G-ARGO-9) | Built; HCP run task not live-verified | The cloud's own infra and deploys are gated by them |
| Receipts, sampling, statements and verify page, GRC push (P-1 to P-4) | Proposal (main spec W6) | The outward half of the cloud. This spec hosts them and does not redefine them |
| Auditor portal (P-5), intelligence export (I-2, I-3) | Proposal, later | CW-8 and CW-9 are their screens |
| Backstage Clearance plugin: Clearances, Evidence, Policy | Built (Tower v0.118.0) | BK-1 adds Coverage; BK-2 adds the links out |
| Mockups: 15 cloud boards and C4 | Drawn 2026-11-09, direction A chosen | The visual source of truth for every CW card |

Two facts shape the design. First, the core is Go and stores in Postgres (`internal/store/pg`) with an in-memory store for tests, so a hosted tenant cell is the same binary against a hosted Postgres. Second, the ledger uses Tessera's POSIX driver, which cannot run on several replicas, so the hosted ledger needs Tessera's AWS driver or a single-writer design. CS-3 spikes both.

## 4. Target architecture {#target-architecture}

The cloud has three parts:

- **Tenant cells** hold each customer's evidence.
- **The control plane** knows tenants, people, grants and plans.
- **Public surfaces** let anyone verify.

Records flow one way, from the customer's in-cluster core into its cell. Everything outward is derived from the cell and recorded back into it.

> Diagram: cloud architecture · 1 customer core, ingest, tenant cells, control plane, public surfaces. See the original document.

The customer's core stays authoritative and syncs into its cell. cloud-api and cloud-worker are the only callers of a cell. The public side sees only hashes and signed summaries.

### Components

| Component | Language | Runs as | What it does |
| --- | --- | --- | --- |
| cloud-ingest | Go | Deployment, 3 replicas, behind its own hostname `ingest.<domain>` | Receives record batches and checkpoints from customer cores. Each core authenticates with a per-tenant workload identity: an OIDC token from the customer cluster's issuer, federated per tenant, or an mTLS client certificate on the Regulated tier. Ingest re-verifies each record's hash chain and signature before writing. It never trusts a count |
| Tenant cell | Go, the `clearance` binary in `--mode=hosted-recorder` | One namespace per tenant, holding a Deployment of the recorder, read API and ledger appender | One Postgres database and role, one KMS key, one S3 prefix and one signing identity per tenant (Architecture, data handling). It serves the read side to cloud-api only |
| cloud-api | Go | Deployment, 3 replicas, `api.<domain>` | The portal's only backend. Sessions, RBAC, tenant routing, grants and the access log, statements, packets, integrations registry, settings, plans and the meter. It calls cells with an audience-bound service-account token |
| cloud-worker | Go | Deployment scaled on SQS depth | Async jobs: packet builds, statement issue and monthly insurer statements, GRC push, escrow export, email, the intelligence export (later) |
| Portal | TypeScript, React, Vite | Static files on S3 behind CloudFront, `app.<domain>` | The subscriber workspace (P1, S1 to S7) and the auditor portal (AU1, AU2). No server rendering, no third-party script, a strict Content Security Policy |
| verify-web | Go, the open `clearance` binary (P-3) | Deployment, `verify.<domain>` and `ledger.<domain>` | V1, V2 and L1. Server-rendered and works with JavaScript off. Reads public statement summaries and the public ledger only; V2's recipient detail comes through cloud-api under the recipient's grant |
| Public ledger | Go, Tessera | One appender Deployment; tiles on S3 behind CloudFront | Statement roots, receipts, revocations and tenant-log checkpoints. Hashes only |
| Witnesses | Go, `clearance-witness` | A separate AWS account, plus at least one external operator | Countersign tenant-log and public-ledger checkpoints |
| Identity | Amazon Cognito | One user pool per region | Subscriber SSO (one SAML or OIDC IdP per tenant), MFA, emailed magic links or the recipient's own SSO for recipients and firm users. SCIM 2.0 is served by cloud-api |

### Contracts

- **Sync protocol.** `POST /v1/sync/records` takes a batch of canonical records, each with `prev_hash` and its signature, and returns the highest accepted sequence. `POST /v1/sync/checkpoints` takes the tenant log's signed checkpoint. The protocol is idempotent and resumable by sequence, and is published in jfillman/clearance as `docs/sync.md` with a JSON schema.
- **cloud-api.** An OpenAPI 3.1 document in clearance-cloud generates the TypeScript client the portal uses. No hand-written fetch calls.
- **Cell read API.** The existing clearance-api routes (`/v1/records`, `/v1/coverage`, `/v1/observations`, packets and statements from P-1 to P-3), reached only from cloud-api and cloud-worker.
- **Events.** Cells publish `record.accepted`, `exception.opened`, `health.changed` and `checkpoint.witnessed` to an SNS topic per environment. cloud-api turns them into server-sent events for the portal's live counts.

## 5. AWS deployment infrastructure {#aws-deployment-infrastructure}

The cloud runs on EKS in its own AWS Organization, in us-east-1 with a pilot-light copy in us-west-2. Everything is Terraform in clearance-cloud-infra, applied through HCP Terraform. Workloads deploy through Argo CD from gitops-clearance-cloud. EKS rather than ECS keeps the Hangar toolchain (Helm charts, Argo CD, the Clearance Argo gate, ValidatingAdmissionPolicy) and the existing clearance and witness charts. The witness alone runs on ECS Fargate in its own account, so it shares no cluster or failure domain with what it witnesses.

> Diagram: AWS layout · 4 platform accounts, cloud-prod-us, witness, us-west-2 pilot light. See the original document.

cloud-staging has the same shape as cloud-prod-us, only smaller. The witness account shares nothing with prod but the organization.

### Accounts

| Account | Holds | Who can reach it |
| --- | --- | --- |
| management | Organizations, SCPs, IAM Identity Center, billing | User only |
| security | Delegated admin for GuardDuty, Security Hub, Config, IAM Access Analyzer, Inspector | Operators, read-only |
| log-archive | Organization CloudTrail and Config history, in Object Lock buckets | Nobody writes but the services |
| shared-services | ECR, Route 53 public zone, GitHub OIDC roles for CI, the ops Clearance core that gates the cloud's own changes | CI, operators |
| cloud-staging | The full stack, small | Managing agent (plan and apply), operators |
| cloud-prod-us | The full stack in us-east-1, pilot light in us-west-2 | Argo CD and HCP Terraform only; operators through break-glass |
| witness | `clearance-witness` on ECS Fargate and its key | User only. A later move to a separate payer is recommended |
| cloud-prod-eu (later) | The full stack in eu-central-1 | Not planned: USA only for now (decided 2026-11-09) |

Organization SCPs:

- Deny leaving the organization, and deny any root-user action.
- Allow only the listed regions.
- Deny stopping or deleting CloudTrail, GuardDuty or Config.
- Deny `s3:BypassGovernanceRetention` and Object Lock configuration changes outside the break-glass role.
- Deny `kms:ScheduleKeyDeletion` outside break-glass.

### Network

- One VPC per environment across 3 AZs: public subnets (ALB, NAT), private app subnets (EKS nodes), and isolated data subnets (Aurora) with no route to the internet.
- VPC endpoints for S3 (gateway), ECR, STS, KMS, SQS, SNS, Secrets Manager, CloudWatch Logs and SES, so service traffic to AWS stays private.
- Ingress is only through the ALBs. The app ALB accepts only CloudFront's origin-facing prefix list and a rotating origin header. The ingest ALB is internet-facing with WAF rate limits and ALB mutual TLS in verify mode for Regulated tenants.
- Egress from cells: none. Egress from workers goes to the named GRC, working-paper and email endpoints through AWS Network Firewall with a domain allowlist in prod. Staging uses NAT only.
- Kubernetes NetworkPolicy is default-deny in every namespace, enforced by the VPC CNI's network policy agent. A cell accepts traffic only from cloud-api, cloud-worker and cloud-ingest.

### Compute

- EKS on the current supported Kubernetes minor, private API endpoint, envelope encryption of Secrets with a KMS key, control-plane logs on.
- Karpenter on Graviton (arm64) Bottlerocket nodes, with a 3-node floor in prod. Pod Security Admission is `restricted` in every namespace.
- Add-ons: AWS Load Balancer Controller, EKS Pod Identity Agent, External Secrets Operator (Secrets Manager), ExternalDNS (Route 53), the CloudWatch Observability add-on with ADOT, Argo CD, and the Clearance Argo CD gate pointed at the ops core.
- **IAM per workload through EKS Pod Identity.** One role serves every cell, and ABAC on the `kubernetes-namespace` session tag limits each cell to its own S3 prefix, KMS key and Secrets Manager path. Unverified until INF-3's isolation test passes. Until then, use one role per tenant.

### Data

| Store | Service | Shape |
| --- | --- | --- |
| Control plane and tenant records | Aurora PostgreSQL Serverless v2, Multi-AZ | A `cloud` database, plus one database and one role per tenant. IAM database auth from Pod Identity. Encrypted with the cluster key. 35-day point-in-time recovery |
| Ledger coordination | Aurora MySQL Serverless v2 | Tessera's AWS driver needs Aurora MySQL for write coordination, and stores tiles in S3 (confirmed in the Tessera v1.0.4 `storage/aws` README). One database per tenant log, plus one for the public ledger |
| Evidence objects | S3 `clearance-evidence-<env>-<region>` | Object Lock in compliance mode. Per-object retention set by the cell from the tenant's tier (30 days, 1 year, 7 years); legal hold for Regulated. SSE-KMS with the tenant's key and S3 Bucket Keys. Versioning on. Cross-region replication to us-west-2 with S3 Replication Time Control |
| Ledger tiles | S3 `clearance-ledger-<env>` | Tenant-log tiles private. Public-ledger tiles readable only through CloudFront with origin access control |
| Statement summaries | S3 `clearance-statements-<env>` | Signed public summaries that verify-web renders. Immutable keys; a revocation is a new object |
| Keys | KMS | One customer-managed key per tenant (evidence, its database secrets, its log key), one per platform service. Key policies name the cell's role only. Rotation on |
| Secrets | Secrets Manager | Tenant log signing keys (Ed25519) encrypted under the tenant key. A KMS-held Ed25519 key is preferred if INF-4's spike confirms the region supports it |
| Queues and schedules | SQS with dead-letter queues, SNS, EventBridge Scheduler | Packet builds, statements, monthly insurer statements, nightly escrow export, GRC push |
| Email | SES, dedicated configuration set | Passwordless sign-in, grant and statement notices. DKIM and DMARC on the domain |

### Edge and domains

`<domain>` is `clearance.hangarplatform.dev` (decided 2026-11-09), so the hosts are `app.clearance.hangarplatform.dev`, `verify.clearance.hangarplatform.dev` and so on. Session cookies are host-only with the `__Host-` prefix, so they are never sent to the rest of hangarplatform.dev.

| Host | Served by | Notes |
| --- | --- | --- |
| `app.<domain>` | CloudFront: S3 origin for the SPA; `/api/*` to the app ALB to cloud-api | One origin, no CORS. Strict CSP, HSTS preload, no third-party origins |
| `verify.<domain>`, `ledger.<domain>` | CloudFront to the app ALB to verify-web; `/tiles/*` from S3 | Public. Cached at the edge; statement pages are immutable once issued, so long TTLs are safe |
| `ingest.<domain>` | Ingest ALB directly | Not behind CloudFront, so client certificates reach the ALB |
| `auth.<domain>` | Cognito custom domain | Hosted sign-in for SSO and passwordless email |

AWS WAF on every CloudFront distribution and the ingest ALB:

- AWS managed common, known-bad-inputs and IP-reputation rule groups.
- Rate-based rules per IP on `/api/*`, verify and ingest.
- A tighter rule on the passwordless sign-in path.

Shield Standard is on by default. ACM certificates live in us-east-1 for CloudFront and in-region for the ALBs.

### Identity and access

- **Operators** use IAM Identity Center with three permission sets: ReadOnly, Operator (staging only) and BreakGlass (prod). BreakGlass use pages the user and is recorded as a break-glass record in the ops tenant.
- **CI** uses GitHub Actions OIDC to roles in shared-services (ECR push only). HCP Terraform uses dynamic provider credentials (OIDC) per workspace. There are no long-lived keys anywhere.
- **Customers** sign in through Cognito, one IdP per tenant, with MFA required for owners. cloud-api is a backend-for-frontend: it does the auth-code-with-PKCE exchange and sets an httpOnly, Secure, SameSite=Strict session cookie, so the SPA never holds a token.
- **Customer cores** authenticate to ingest with their cluster's service-account OIDC token, federated per tenant (issuer, audience and subject registered in S6 or its Kubernetes equivalent), or with an mTLS client certificate.
- **Recipients and firm users** sign in with an emailed magic link (single use, 15-minute expiry, through a Cognito custom auth challenge) or with their own organization's SSO (SAML or OIDC, registered on the grant), as P-1 requires (decided 2026-11-09). They never get a Clearance password.

### Delivery and supply chain

- Images are multi-arch, built in GitHub Actions, and signed keyless with an SBOM. They are pushed to ECR with immutable tags, scan on push and Inspector enabled.
- Argo CD runs in each cluster and syncs from gitops-clearance-cloud. cloud-prod is gated by the Clearance Argo CD gate against the ops core: a tier 2 or 3 change to cloud-prod waits for a person to clear it.
- HCP Terraform runs every plan for clearance-cloud-infra with Clearance's HCP run task (G-TF-6). Production applies need a T3 clearance, which means two people. Until there are two operators, the user's single clearance is recorded as an exception.
- The portal bundle is built once per tag, uploaded to S3 under a content-hashed path, and switched by a CloudFront origin-path change. That switch is itself a gated Terraform change.

### Observability and SLOs

- CloudWatch Container Insights and ADOT traces. Application logs are kept 30 days and never contain record bodies, secrets or approver subjects (asserted by a log-scrubbing test in CI).

| Signal | Objective | Alarm |
| --- | --- | --- |
| Ingest accept latency | p99 under 500 ms | p99 over 1 s for 5 min |
| Tenant checkpoint age | New checkpoint every 60 s, witnessed within 5 min | Unwitnessed for 10 min |
| Verify page | Full result p95 under 2 s (P-3's done bar) | p95 over 3 s for 10 min |
| cloud-api | p95 under 300 ms, 99.9% monthly availability | 5xx rate over 1% |
| Jobs | Packet build under 5 min for a 30-day Business tenant | Any message on a dead-letter queue |

Paging goes to PagerDuty through SNS. A status page at `status.<domain>` is hosted outside AWS so it survives a regional outage.

### Backup and disaster recovery

- **RPO.** Evidence: 15 minutes (S3 Replication Time Control); the customer's core also buffers unsent records, so nothing is lost while ingest is down. Control plane: 5 minutes (Aurora point-in-time recovery).
- **RTO.** 4 hours. us-west-2 is pilot light: replicated buckets, AWS Backup snapshot copies in a vault with Vault Lock in compliance mode, Terraform ready to raise EKS and Aurora.
- A restore drill each quarter into a scratch account. The drill's result is a record in the ops tenant.

### Security baseline

- GuardDuty with EKS runtime, S3 and RDS protection.
- Security Hub with AWS Foundational Security Best Practices and CIS.
- Config conformance packs.
- IAM Access Analyzer for external and unused access.
- Inspector for ECR and nodes.
- The organization trail with S3 data events on the evidence buckets.

The cloud is a Clearance tenant of the ops core, observed by its own AWS collector (O-4) through the same S6 onboarding customers use. Every out-of-band change in the cloud's own accounts prints in the ops tenant's packet.

### Initial sizing

| Environment | EKS | Aurora PostgreSQL | Aurora MySQL | Other |
| --- | --- | --- | --- | --- |
| cloud-staging (us-east-1) | 2 AZs, Karpenter, 2 nodes floor | 0.5 to 4 ACU, one writer | 0.5 to 2 ACU | NAT only, single NAT gateway |
| cloud-prod-us (us-east-1) | 3 AZs, Karpenter, 3 nodes floor | 1 to 16 ACU, writer and one reader | 0.5 to 8 ACU | Network Firewall, NAT per AZ |
| DR (us-west-2) | None until failover | Snapshot copies only | Snapshot copies only | Replicated buckets |
| witness | ECS Fargate, 1 task | None | None | Its own KMS key |

INF-9 turns this into a monthly cost model, and the user sets the budget alarms.

## 6. Gap analysis {#gap-analysis}

Each row is a capability the mockups or the companion artifacts require. It shows what exists today and the package that closes the gap.

| Need | Exists today | Package |
| --- | --- | --- |
| AWS organization, accounts, guardrails | Nothing | INF-1 |
| Network, edge, domains, WAF | Nothing | INF-2 |
| EKS cluster with add-ons and per-workload IAM | Nothing | INF-3 |
| Aurora, S3 Object Lock buckets, KMS per tenant | Nothing | INF-4 |
| Customer sign-in, SSO per tenant, passwordless for outsiders | Nothing | INF-5, CS-1 |
| CI, image signing, Argo CD, gated cloud deploys | Hangar patterns only | INF-6 |
| Observability, SLOs, backups, DR drill | Nothing | INF-7 |
| Security baseline and the cloud as its own tenant | Nothing | INF-8 |
| Cost model and per-tenant meter | Nothing | INF-9, CS-9 |
| Tenants, people, roles, plans | Nothing | CS-1 |
| Records reaching the cloud from a customer's core | Records stay in-cluster; de-duplication on `POST /v1/records` (Built) | CS-2 |
| Hosted ledger on object storage, public ledger | Tessera on POSIX (Built) | CS-3 |
| Retention by tier, legal hold, escrow export | Nothing hosted | CS-4 |
| Grants, access register, every read recorded | P-1 deliveries and credentials (Proposal) | CS-5 on top of P-1 |
| Statements, verify page, revoke and supersede | P-3 (Proposal) | P-3 in the core; CS-6 hosts it |
| Packets and the six report types as jobs | `clearance packet` CLI (Built) | CS-7 |
| Integrations registry, AWS onboarding | Collectors in-cluster (O-4, Proposal) | CS-8 |
| Plans, the governed-scope meter, billing | Nothing | CS-9 |
| Insurer statement schedule, benchmarks | Insurer profile in P-3; I-2 later | CS-10 |
| Portal shell, design kit, auth | Mockups only | CW-1 |
| P1 Overview, Changes, Exceptions | Mockups | CW-2 |
| S1 Evidence, Coverage, Ledger | Mockups | CW-3 |
| S3 Reports | Mockups | CW-4 |
| S2 Sharing | Mockups | CW-5 |
| S5 Integrations, S6 Connect AWS | Mockups | CW-6 |
| S7 Settings | Mockups | CW-7 |
| AU1, AU2 Auditor portal | Mockups; P-2, P-5 | CW-8 |
| S4 Intelligence | Mockups; I-2 | CW-9 |
| V1, V2, L1 | Mockups; P-3 | CS-6, rendered by the open binary |
| Backstage Coverage page (C4) | Mockup | BK-1 |
| Backstage links to the cloud | Nothing | BK-2 |

## 7. Work packages, INF-series: AWS infrastructure {#work-packages-inf}

Nine packages build the estate in section 5. All of them are Terraform in jfillman/clearance-cloud-infra:

- reusable modules under `modules/`;
- one root per account and environment under `live/<account>/<region>/`;
- one HCP Terraform workspace per root.

Modules pin provider versions, run `terraform validate`, `tflint` and `checkov` in CI, and have a `terraform test` per module. A subagent writes modules and plans. The managing agent applies to staging, and the user applies to management, witness and prod.

### INF-1 · Organization, accounts and guardrails
<!-- pkg status=verified wave=K0 strip=C-1 -->

- **Repos.** clearance-cloud-infra.
- **Depends on.** The user creating the management account and the two repos.
- **Build.** `modules/org`: the accounts in section 5 through Organizations account vending, organizational units (Security, Infrastructure, Workloads, Witness), the SCPs listed in section 5, IAM Identity Center with the three permission sets, the organization CloudTrail into log-archive (Object Lock, 1 year compliance), delegated admin for the security services, and budgets with alerts per account. HCP Terraform dynamic-credential roles per account.
- **Done when.** Every account exists with its baseline. An SCP test shows a staging role refused when it disables CloudTrail, leaves the region list, or bypasses Object Lock. A plan from HCP Terraform reaches each account with no static key.
- **Rollout.** User applies management. The managing agent applies the rest to staging-equivalent OUs.
- **User steps.** The management account, the payer, MFA on root, the organization's email aliases, and the first apply.
- **Evidence.** [clearance-cloud-infra#1](https://github.com/jfillman/clearance-cloud-infra/pull/1) (phase 1, applied 2026-11-18 after the account quota was raised to 10) and [#2](https://github.com/jfillman/clearance-cloud-infra/pull/2) (phase 2, applied 2026-11-19). Verified 2026-11-19: organization trail logging with digests, delegated admin for Organizations, GuardDuty, Security Hub and Inspector, and the SCP refusal test (three PASS lines).

### INF-2 · Network, edge and domains
<!-- pkg status=verified wave=K0 strip=W-2 -->

- **Repos.** clearance-cloud-infra.
- **Depends on.** INF-1; delegation of clearance.hangarplatform.dev.
- **Build.** `modules/network` (VPC, subnets in three tiers, NAT, endpoints, flow logs to log-archive, Network Firewall with a domain allowlist in prod). `modules/edge`:
  - Route 53 zone and ACM certificates;
  - CloudFront distributions for app, verify and ledger, with origin access control on the S3 origins;
  - the origin-header secret in Secrets Manager with rotation;
  - WAF web ACLs as in section 5;
  - the ingest ALB's trust store for mTLS.
- **Done when.** A request to the app ALB that skips CloudFront is refused. A burst over the rate rule gets 429 from WAF. A pod in a data subnet cannot reach the internet. DNS and certificates resolve for every host in staging.
- **Rollout.** Staging, then prod.
- **User steps.** Add the NS records that delegate clearance.hangarplatform.dev to the new Route 53 zone, at whoever hosts hangarplatform.dev's DNS.
- **Evidence.** Verified in cloud-staging on 2026-11-22. The prod network and edge stay code only until the first tenant (lean-until-first-tenant decision, 2026-11-19).
  - Code: the zone ([clearance-cloud-infra#3](https://github.com/jfillman/clearance-cloud-infra/pull/3)), the network ([#4](https://github.com/jfillman/clearance-cloud-infra/pull/4)), lean staging with an on-demand switch ([#5](https://github.com/jfillman/clearance-cloud-infra/pull/5)), the edge ([#6](https://github.com/jfillman/clearance-cloud-infra/pull/6)), and an optional reserved concurrency for the rotation Lambda, because a new account's 10-execution quota refuses any reservation ([#9](https://github.com/jfillman/clearance-cloud-infra/pull/9)).
  - Done tests, all PASS:
    - The data-subnet egress test found no path out, with a working control path from the app subnet.
    - A request that skips CloudFront is refused at the network layer, three ways; a request through CloudFront reaches the ALB.
    - WAF answered 429 on request 96 of a burst at the sign-in path.
    - DNS and certificates resolve for app, verify, ledger and ingest.
    - Flow logs arrive in log-archive.
    - A manually triggered origin-secret rotation completed, and the plan after it was clean.
  - Not yet proven: mutual TLS at ingest, which needs a test CA.
  - Applied by the local Terraform CLI against HCP state while HCP Terraform runs were failing for Free-tier organizations (HashiCorp incident, 2026-11-22).

### INF-3 · EKS and platform add-ons
<!-- pkg status=built wave=K0 strip=W-4 -->

- **Repos.** clearance-cloud-infra (cluster), clearance-cloud (add-on charts and values), gitops-clearance-cloud.
- **Depends on.** INF-2.
- **Build.**
  - `modules/eks`: private endpoint, KMS envelope encryption, control-plane logs, access entries for Identity Center roles only.
  - Karpenter with a Bottlerocket arm64 node pool.
  - Add-ons: Pod Identity Agent, VPC CNI with network policy on, Load Balancer Controller, External Secrets Operator, ExternalDNS, the CloudWatch Observability add-on, and Argo CD bootstrapped from gitops-clearance-cloud.
  - Pod Security Admission `restricted` and default-deny NetworkPolicy in every namespace.
  - A ValidatingAdmissionPolicy that refuses an image not from the environment's ECR by digest. It follows the main spec's `has()`-guard rule and is tested in Warn first.
  - The ABAC role for cells.
- **Done when.** The tenant-isolation test (section 12) passes: a pod in namespace `tenant-a` with the shared cell role is refused on tenant-b's S3 prefix, KMS key and secret path. If ABAC fails, the card falls back to one role per tenant and says so. A pod from a non-ECR image is refused. Argo CD syncs an empty app.
- **Rollout.** Staging, then prod.
- **Evidence.** Part 1, the cluster module, is merged but not applied: [clearance-cloud-infra#7](https://github.com/jfillman/clearance-cloud-infra/pull/7). It sits behind `cluster_enabled` (off), so nothing runs until we decide to run the cluster. Part 2 (add-ons and Argo CD) is not started.

### INF-4 · Data stores and keys
<!-- pkg status=verified wave=K0 strip=W-5 -->

- **Repos.** clearance-cloud-infra.
- **Depends on.** INF-2.
- **Build.**
  - `modules/data`: Aurora PostgreSQL Serverless v2 (Multi-AZ, IAM auth, 35-day PITR, Performance Insights) and Aurora MySQL Serverless v2 for Tessera.
  - The three S3 buckets with Object Lock in compliance mode, versioning, Block Public Access, CRR to us-west-2 with Replication Time Control, and lifecycle rules that never shorten a retention.
  - SQS queues with dead-letter queues, SNS topics, and EventBridge Scheduler groups.
  - `modules/tenant-keys`: called by CS-1's tenant provisioning, it creates a tenant KMS key with a key policy naming only that tenant's cell role and the break-glass role.
  - A spike on KMS Ed25519 signing support for the log key.
- **Done when.** An object written with 7-year retention cannot be deleted or shortened by the account's admin role (quoted error). The replica exists in us-west-2 with the same retention. A tenant key refuses decrypt from another tenant's role.
- **Rollout.** Staging, then prod. Object Lock retention is permanent, so prod's first apply happens only after staging's test passes.
- **User steps.** Approve the retention defaults per tier, because they cannot be undone on written objects. **Approved 2026-11-22: 30 days for a trial or pilot tenant, 1 year for Team, 7 years for Business, 7 years plus legal hold for Regulated** (values, then the plan mapping on board A-7).
- **Decisions (2026-11-22).**
  - The Object Lock buckets are created by a separate owner-applied root per environment. It runs through the organization access role, the only path the SCP allows besides break-glass.
  - The staging proof uses 1-day COMPLIANCE retention. The 7-year proof runs once in prod with the first real tier.
  - Staging Aurora is lean: a single writer that pauses when idle.
- **Evidence.** Verified in cloud-staging on 2026-11-22. Prod is code only.
  - Code: [clearance-cloud-infra#8](https://github.com/jfillman/clearance-cloud-infra/pull/8) (modules, roots, scripts), [#10](https://github.com/jfillman/clearance-cloud-infra/pull/10) (Aurora versions offered in the region), [#11](https://github.com/jfillman/clearance-cloud-infra/pull/11) (tenant key policy allows alias management), [#12](https://github.com/jfillman/clearance-cloud-infra/pull/12) (replication KMS conditions accept the S3 Bucket Keys context) and [#13](https://github.com/jfillman/clearance-cloud-infra/pull/13) (parameter drift).
  - Done tests, all PASS:
    - The account's admin role is refused when it deletes a locked object, shortens its retention, bypasses governance (also refused by the SCP) or switches it to GOVERNANCE.
    - Replication completes, and the us-west-2 replica carries the same COMPLIANCE retention.
    - A tenant key works for its own role, and refuses decrypt, encrypt and data-key requests from the other tenant's role and from the account's admin role.
    - Both Aurora clusters were confirmed paused at zero capacity.
  - Ed25519 spike: AWS KMS supports `ECC_NIST_EDWARDS25519` with `ED25519_SHA_512` over RAW messages, which suits signed-note checkpoints. A live verification against Go's `crypto/ed25519` is still to run.

### INF-5 · Identity
<!-- pkg status=in-progress wave=K0 strip=W-6 -->

- **Repos.** clearance-cloud-infra.
- **Depends on.** INF-2.
- **Build.** `modules/identity`:
  - a Cognito user pool per region with the custom domain `auth.<domain>`;
  - an app client for cloud-api (confidential, auth code with PKCE);
  - emailed magic links and per-organization SSO federation for recipients and firm users;
  - MFA required for the owner role;
  - advanced security in enforced mode;
  - SES domain identity with DKIM, DMARC and a configuration set;
  - an IdP template that CS-1 instantiates per tenant (SAML or OIDC).
- **Done when.** A test tenant signs in through an Okta developer org over SAML, a recipient signs in once with an emailed link and once through their own SSO, and a used link is refused, and a disabled user is refused. No password sign-in path exists for a tenant that has SSO.
- **User steps.** An Okta or Entra test org, and SES production access.
- **Decision (2026-11-22, A-8).** Owners always sign in through their organization's SSO, whose identity provider supplies the MFA. A tenant without SSO is not onboarded until it has one, so no non-SSO owner path is built.

### INF-6 · Delivery: CI, images, Argo CD and gated deploys
<!-- pkg status=in-progress wave=K0 strip=W-7 -->

- **Repos.** clearance-cloud (workflows), clearance-cloud-infra, gitops-clearance-cloud.
- **Depends on.** INF-3; the main spec's G-TF-6 and the Argo CD gate.
- **Build.**
  - GitHub Actions OIDC roles (ECR push only).
  - The image workflow: multi-arch build, SBOM, keyless signing, push by digest.
  - The portal bundle workflow: build, upload to a content-hashed S3 path, open the origin-path PR.
  - The render-and-diff job for gitops-clearance-cloud.
  - Argo CD Applications per environment.
  - The ops Clearance core in shared-services (the existing chart), with the Argo CD gate installed on cloud-prod against it and the HCP run task registered on every prod workspace.
- **Done when.** A digest bump syncs to staging without a hold. The same bump to prod holds until a person clears it, quoted as the record id. A Terraform plan on a prod workspace shows the run task result. An unsigned image is refused at admission.
- **User steps.** The HCP Terraform organization, and clearing the first prod deploy.
- **Progress (2026-11-24).** Built: GitHub OIDC push roles (immutable subject), the image workflow (multi-arch, SBOM, provenance, keyless signing, push by digest; first release cloud-v0.1.0), the shared-services registry, render-and-diff for gitops, and the staging Argo CD Applications (all Synced and Healthy). The admission policy admits only environment-registry images by digest (verified 5/5, Warn mode). Open: signature verification at admission (an unsigned image is not refused yet), the cloud-api digest bump to staging (waits on CS-1's deploy chart), the portal bundle workflow, the ops core with the Argo CD gate on prod, and the HCP run task on prod workspaces.

### INF-7 · Observability, backups and DR
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud-infra, clearance-cloud (dashboards and alarms as code).
- **Depends on.** INF-3, INF-4.
- **Build.**
  - The SLO alarms and dashboards in section 5.
  - ADOT trace pipeline.
  - Log retention and the log-scrubbing CI test.
  - AWS Backup plans with cross-region copies into a Vault Lock vault.
  - The us-west-2 pilot-light root.
  - A runbook and a drill script that restores Aurora and raises EKS in a scratch account.
  - The external status page.
- **Done when.** A forced ingest stall pages within 5 minutes. A drill restores staging into the scratch account inside 4 hours and replays the restored tenant's chain through `clearance verify` with every record intact.
- **User steps.** The PagerDuty service, and the status page vendor account.

### INF-8 · Security baseline and the cloud as its own tenant
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud-infra.
- **Depends on.** INF-1, INF-6, the main spec's O-4.
- **Build.**
  - GuardDuty (EKS runtime, S3, RDS), Security Hub standards, Config conformance packs, Access Analyzer, Inspector.
  - Findings routed to the operator channel.
  - The ops tenant onboarded with the same S6 module customers use (CS-8), so the cloud's own CloudTrail and Config feed its own collector.
- **Done when.** A console change to a prod security group shows as out of band in the ops tenant's coverage with actor and diff. Security Hub shows no critical finding open in prod.
- **User steps.** None beyond reviewing the first findings.

### INF-9 · Cost model and tenancy metering inputs
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud-infra, clearance-cloud docs.
- **Depends on.** INF-3, INF-4.
- **Build.**
  - Cost allocation tags (`tenant`, `service`, `env`) enforced by a Config rule.
  - Split cost allocation data for EKS so per-namespace cost is visible.
  - A Cost and Usage Report export queried by Athena.
  - `docs/cost-model.md`: fixed cost per environment, marginal cost per tenant by tier, measured on staging with synthetic tenants.
- **Done when.** Staging's per-tenant marginal cost is measured for 1, 10 and 50 synthetic tenants, and the model names the tier where a pooled cell becomes necessary.
- **User steps.** Set budget alarms from the model.

## 8. Work packages, CS-series: cloud services {#work-packages-cs}

Ten packages build the Go services in jfillman/clearance-cloud: `cmd/cloud-api`, `cmd/cloud-ingest` and `cmd/cloud-worker`, sharing `internal/`. They import jfillman/clearance by tag. A change the core needs, such as hosted-recorder mode, the sync client or the S3 ledger driver, is a Clearance PR first and follows the main spec's release chain. The main spec's security and efficiency principles apply unchanged: distroless images, strict decoding, timeouts, fuzz targets on every parser, fail closed.

### CS-1 · Tenancy, people, roles and the cloud-api skeleton
<!-- pkg status=in-progress wave=K0 strip=W-8 -->

- **Repos.** clearance-cloud.
- **Depends on.** INF-3, INF-4, INF-5.
- **Build.**
  - The control-plane schema in the `cloud` database: tenants (plan, region, retention, scopes), people, roles and approver groups, sessions, API keys.
  - Tenant provisioning as one idempotent job. It creates the namespace, database and role, KMS key (cloud-worker calls the AWS APIs directly with the key policy INF-4's tenant-keys module encodes, and a nightly drift check compares the two), Secrets Manager path, the cell's Helm release, and the Cognito IdP.
  - The BFF session flow.
  - RBAC as drawn on board S7: owner, GRC lead, platform admin, approver T2 and T3, viewer.
  - SCIM 2.0 users and groups.
  - OpenAPI 3.1 with the generated TypeScript client.
  - Audit of every control-plane write as a record in the tenant's own chain.
- **Done when.** Provisioning a tenant from nothing to a serving cell takes under 10 minutes and a second run changes nothing. A viewer is refused a share action. A SCIM deprovision ends that person's sessions within 60 seconds. The tenant-isolation suite passes.
- **Rollout.** Cloud release chain.
- **User steps.** None.
- **Progress (2026-11-24).** Code built and merged (CS-1a to CS-1d) with unit tests. Database access uses RDS IAM authentication with a token per connection and verify-full TLS against a pinned CA bundle, so no database password is stored. Staging prerequisites merged in the infra repo behind a flag: Pod Identity roles for cloud-api, cloud-migrate and cloud-worker, an app secret seeded in-VPC (no value in Terraform state), and in-VPC tasks that create the IAM login roles. Next: apply and run those tasks, cut a release with the IAM code, then the gitops chart (Deployment, migrate Job, target group binding, external secret, Postgres egress). The done bar also needs the real cloud-worker adapters (KMS, Secrets Manager, Cognito, Kubernetes, Helm), which are still stubs.

### CS-2 · Record sync from the customer's core
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance (sync client, `docs/sync.md`), clearance-cloud (`cmd/cloud-ingest`).
- **Depends on.** CS-1; the main spec's R-6 schema and the `POST /v1/records` de-duplication (Built).
- **Build.**
  - In the core: a sync client that ships sealed records and checkpoints in sequence, with an outbox table, resumable by sequence, back-off, and a health signal (`sync.lag`) on clearance-api and in the observation-health record.
  - In the cloud: ingest. It authenticates the tenant's workload identity, re-verifies hash links and signatures, rejects gaps and forks, writes to the cell, and returns the highest accepted sequence.
  - A chart value `cloud.enabled` with the tenant id and ingest URL.
- **Done when.**
  - A lab core's 30-day chain syncs to staging, and the cloud's copy verifies with `clearance verify` byte for byte against the in-cluster copy.
  - A record with an altered body is refused and the refusal is recorded.
  - Cutting ingest for an hour leaves the core's decide path unchanged, and the backlog drains when it returns.
  - A token from tenant A cannot write to tenant B.
- **Rollout.** Clearance release, then the cloud release chain.
- **User steps.** Point hangar-dev's core at staging ingest.

### CS-3 · Hosted tenant ledgers and the public ledger
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance (ledger driver option), clearance-cloud.
- **Depends on.** CS-2, INF-4; the main spec's C-3.
- **Build.**
  - A spike comparing Tessera's AWS driver (S3 plus Aurora MySQL) with a single-writer POSIX log on EBS. The recommendation is the AWS driver, because it serves tiles from S3 and survives a pod move.
  - The cell's ledger appender on the chosen driver, checkpointing every 60 seconds and collecting countersignatures from the Clearance witness and one external witness.
  - The public ledger log: statement roots, receipts, revocations and each tenant log's checkpoints, witnessed the same way. Tiles are served at `ledger.<domain>/tiles/`.
- **Done when.**
  - A tenant checkpoint is countersigned by 2 of 3 witnesses within 5 minutes.
  - `clearance verify --ledger https://ledger.<staging-domain> --consistency` passes across a cell restart.
  - Deleting a tile in a scratch copy makes verify fail with the tile named.
- **User steps.** The external witness agreement.

### CS-4 · Evidence store, retention, legal hold and escrow
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud.
- **Depends on.** CS-2, INF-4.
- **Build.**
  - The cell writes each record's original and attachments (diffs, plans, bundles) to the evidence bucket with retention from the tenant's tier, and legal hold on request (Regulated).
  - The S1 search API: scope, path, coverage state, actor, time, record id, hash.
  - The nightly escrow export to a bucket in the tenant's own account through a role the tenant grants. It carries the records, checkpoints, countersignatures and the verifier binary.
  - The "who read what" log.
- **Done when.** An escrow export verifies offline in a fresh container with no network. Retention on a Team tenant's object is 1 year and cannot be shortened. A search for another tenant's record id returns nothing, not an error that leaks its existence.
- **User steps.** None.

### CS-5 · Grants and the access register
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance-cloud; clearance (P-1).
- **Depends on.** The main spec's P-1, CS-1.
- **Build.** The S2 access register over P-1's deliveries:
  - grant kinds: auditor, assessor, statement recipient, insurer profile, examiner export;
  - each grant has a scope, a window, an expiry and a read count;
  - revoke takes effect at once and writes to the public ledger;
  - every read through cloud-api or verify-web becomes a ledger record in the tenant chain, then shows in the access log and in V2's "your access" note;
  - expiry notices go out by email.
- **Done when.** A revoked grant's next read is refused within 5 seconds and the refusal is a record. A read appears in the register within 10 seconds. An expired grant cannot be extended without a new grant record.
- **User steps.** None.

### CS-6 · Hosting statements, the verify page and the ledger explorer
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance (P-3's page and the L1 explorer, server-rendered), clearance-cloud (issue flow, storage), gitops-clearance-cloud.
- **Depends on.** The main spec's P-3, CS-3, CS-5.
- **Build.**
  - cloud-api's statement flow behind S2's composer, with the locked invariants enforced in the core, not the UI.
  - Signed public summaries written to the statements bucket.
  - verify-web deployed from the open binary at `verify.<domain>/s/{id}` (V1).
  - V2's recipient detail behind the recipient's grant.
  - L1 at `ledger.<domain>`: checkpoints, lookup by statement id or hash, revoked statements, witnesses.
- **Done when.** P-3's own done bar passes on staging's public hostname: seven checks in under 2 seconds, revoked and superseded shown, a blind window printed, and the result visible with JavaScript off. L1 shows a revoked statement with both leaves. No page includes a tenant name unless the statement prints it.
- **User steps.** DNS for verify and ledger.

### CS-7 · Reports as jobs
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance-cloud.
- **Depends on.** CS-4; the main spec's C-5.
- **Build.**
  - cloud-worker runs `clearance packet` against the cell for the six report types in S3: audit packet, verification statement (through CS-6), insurer statement, freeze, incident, regulator export.
  - Sealing on a schedule (the 1st of the month).
  - The control graph API (covered, partial, gap, with the missing evidence named).
  - Issued reports listed with their tree root and acceptances.
  - A regulator-export layout per framework, shipped as data.
- **Done when.** A sealed October packet from staging verifies offline. Re-running a seal is refused, not duplicated. A packet for a window with a blind day prints it.
- **User steps.** Which regulator layouts come first.

### CS-8 · Integrations registry and AWS onboarding
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud, clearance-cloud-infra (`modules/customer-aws-reader`, published to a public registry), clearance (O-4 collector in hosted mode).
- **Depends on.** CS-1; the main spec's O-4, G-TF-6, P-4.
- **Build.**
  - The S5 registry: gate providers with conformance results, collectors with health, assurance and GRC connections, identity and alerts.
  - The S6 flow:
    - a read-only reader role per customer account, deployed by StackSet, Terraform module or a console link, with an external id;
    - detection of the organization trail and logging account;
    - an EventBridge rule plus an SQS queue in the customer's logging account;
    - the five checks;
    - the named limits.
  - The hosted AWS collector reads through the role and posts observations into the tenant's cell.
- **Done when.** The ops tenant (INF-8) and one lab customer account onboard end to end. A `StopLogging` call flips the account's health within 5 minutes. Removing the external id breaks the assume-role and the screen says why.
- **User steps.** A lab AWS organization to onboard as a customer.

### CS-9 · Plans, the meter and billing
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance-cloud.
- **Depends on.** CS-1, INF-9.
- **Build.**
  - Plans as data: Team, Business, Regulated, Auditor. Community has no cloud workspace; it is Backstage and the offline verifier (decided 2026-11-09).
  - The meter is governed production scopes, never changes or seats, computed daily from the registry and recorded.
  - Plan limits enforced in cloud-api.
  - AWS Marketplace SaaS listing and a card-payment path behind one billing interface, recommended Stripe for direct sales.
  - Invoices show the meter's record ids.
- **Done when.** A Team tenant adding a second scope is asked to upgrade, not silently billed. The meter recomputes the same number from the records. Auditor and recipient accounts can never be charged.
- **User steps.** The billing provider account, prices, and Marketplace seller registration.

### CS-10 · Insurer statements and the intelligence hooks
<!-- pkg status=proposal wave=K4 -->

- **Repos.** clearance-cloud; clearance (I-2 later).
- **Depends on.** CS-6, CS-7; I-2 for benchmarks.
- **Build.**
  - The monthly insurer statement schedule per carrier, built on P-3's insurer profile.
  - S4's consent record under its own signature, with withdrawal.
  - `clearance export preview` surfaced in S4.
  - When I-2 lands: the aggregator in its own account with the cell rules (20 tenants, 2,000 changes, 25% dominance), and give-to-get gating on benchmarks.
- **Done when.** An insurer statement is issued on schedule and verifies. The benchmark API refuses a cell under the thresholds. The preview matches the export byte for byte. Withdrawal stops the next export.
- **User steps.** The neutrality charter text, and the first carrier.

## 9. Work packages, CW-series: the portal {#work-packages-cw}

Nine packages build the portal in `web/` of jfillman/clearance-cloud. The stack is:

- TypeScript in strict mode, React, Vite and React Router;
- TanStack Query over the generated cloud-api client;
- Vitest for units and Playwright for end-to-end;
- axe accessibility checks in CI.

The visual source is the canvas board named on each card, in direction A. Every screen meets WCAG 2.2 AA, works from 1280 px wide down to a 390 px phone for read-only views, and renders from live staging data before it is called done. Pages that are a Proposal in the product carry the proposal chip, as the Backstage plugins do.

### CW-1 · App shell, design kit and sign-in
<!-- pkg status=proposal wave=K0 strip=W-9 -->

- **Repos.** clearance-cloud.
- **Depends on.** CS-1.
- **Build.**
  - The `@clearance/cloud-ui` package: the paper and ink tokens from the UI doc's "Visual language for the cloud", self-hosted Geist, Geist Mono and Instrument Serif (no font CDN, so the CSP holds), and the components with the Tower kit's names (panel, chip, stat, table, callout, facts, tier, vc, stamp, health strip, KPI band).
  - The left-nav shell from P1: org card, the nav groups, the checkpoint lock line.
  - BFF sign-in, a tenant switcher for people in more than one tenant, error and empty states.
  - A Storybook of the kit, published to the staging bucket.
- **Done when.** The kit's screenshots match the canvas boards within the visual-diff threshold the card sets. Signed out, every route redirects. The CSP report endpoint receives nothing on a full Playwright run.

### CW-2 · Overview, Changes and Exceptions (P1)
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-2, CS-4.
- **Build.**
  - P1's statement header with live counts from `/v1/coverage`.
  - The KPI band and the Needs-you queue: holds, open out-of-band, auditor requests.
  - Observation health strips, By path, and Who has seen it.
  - The Changes list with Clear and Deny for approvers, signed in as the person (the gate's existing clear route through cloud-api).
  - Exceptions with the three resolutions from C4: revert, adopt, accept with a reason.
  - Live counts over server-sent events.
- **Done when.** The header's numbers equal `clearance packet`'s coverage section for the same window. Clearing a held lab change from P1 is a record naming the person. A viewer sees no Clear button and the API refuses one anyway.

### CW-3 · Evidence, Coverage and Ledger (S1)
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-3, CS-4.
- **Build.**
  - S1's search and record detail, with verified or claimed per field, the ledger leaf, the inclusion proof and the verify command.
  - The bundle download, and the retention and hold tab.
  - The Coverage page: scope-by-day health matrix, named limits.
  - The tenant Ledger page: checkpoints, witnesses, consistency.
- **Done when.** A downloaded bundle verifies offline. A claimed field never renders with the verified style (component test over the schema's tags).

### CW-4 · Reports (S3)
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-7.
- **Build.** The six report types, the packet builder form, the control graph, and the issued list with roots and acceptances.
- **Done when.** A packet built from the form equals the CLI's for the same inputs. The control graph shows the named missing evidence for each partial or gap.

### CW-5 · Sharing (S2)
<!-- pkg status=proposal wave=K2 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-5, CS-6.
- **Build.**
  - The statement composer with the locked-rules callout, preview as the recipient, issue and sign.
  - The access register: grant, manage, supersede, revoke.
  - The who-read-what log and GRC hub status.
- **Done when.** The composer cannot produce a request that omits an exception class; the API refuses a crafted one. Revoke from S2 shows on L1 within a minute.

### CW-6 · Integrations and Connect AWS (S5, S6)
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-8.
- **Build.**
  - S5's four groups with health and conformance.
  - S6's five-step flow with the StackSet, Terraform and console options.
  - Live checks as the customer completes each step, and the named-limits summary.
- **Done when.** The lab AWS org onboards through the screen alone, and each failing check names its fix.

### CW-7 · Settings (S7)
<!-- pkg status=proposal wave=K1 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-1, CS-4, CS-9.
- **Build.** Plan and meter, the tier table, retention, witnesses, people and roles (SCIM-managed rows read-only), SSO setup, API keys, and continuity (escrow status, run now).
- **Done when.** Changing retention upward applies to new objects and the screen says existing objects keep theirs. Retention can never be lowered below what is written.

### CW-8 · The auditor portal (AU1, AU2)
<!-- pkg status=proposal wave=K3 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-5; the main spec's P-2 and P-5.
- **Build.**
  - A firm context in the same app: firm home, clients, engagements, grants and receipts.
  - The engagement view: population, the seeded and stratified sample with per-record verify, the receipt form (verdict, per-control notes), signing with the firm key or OIDC identity.
  - Export to Suralink, then AuditBoard.
  - Firm-or-assessor labelling.
- **Done when.** A fake firm draws a 25-record sample, verifies it, and signs a receipt. The next packet carries the receipt. The firm never sees a record outside its grant.
- **User steps.** The first real firm.

### CW-9 · Intelligence (S4)
<!-- pkg status=proposal wave=K4 -->

- **Repos.** clearance-cloud.
- **Depends on.** CW-1, CS-10.
- **Build.** The insurer statement preview and send, the benchmarks table with the cell statement, the contribution and consent panel with withdrawal, and the neutrality charter link.
- **Done when.** A tenant that has not opted in sees no benchmarks and is told why. A withdrawn consent hides the benchmarks at the next refresh.

## 10. Work packages, BK-series: Backstage changes {#work-packages-bk}

Two packages change the Clearance Backstage plugin in jfillman/backstage. The plugin still imports nothing from Tower or Hangar, and it works with no cloud tenant linked.

### BK-1 · The Coverage page (C4)
<!-- pkg status=proposal wave=K0 strip=W-10 -->

- **Repos.** backstage (clearance, clearance-backend, clearance-react).
- **Depends on.** The main spec's O-1 (Built) and C-6. It does not depend on the cloud.
- **Build.**
  - A Coverage route between Evidence and Policy, with an open-exceptions count in the nav.
  - The scope-by-day health matrix from `/v1/observations/health`.
  - Open exceptions, with the Resolve panel's three choices through the delegate write path. Each choice adds a resolution record and never removes the exception.
  - Tabs for not-attributed changes and named limits.
  - T1's needs-you callout links to C4 for a live out-of-band change.
- **Done when.** On hangar-dev, a console change seeded by O-4 shows in C4 with actor and diff. Resolving it as revert links the revert record. A viewer cannot resolve.
- **Rollout.** The backstage PR (user merges), then the Tower release.

### BK-2 · Links into Clearance Cloud
<!-- pkg status=proposal wave=K1 -->

- **Repos.** backstage, clearance (a `cloud` block on clearance-api's `/v1/info`).
- **Depends on.** CS-2, BK-1.
- **Build.**
  - When the core reports a linked tenant, the side nav shows the "Cloud: \<tenant> · open in Clearance Cloud" chip.
  - Evidence, Coverage and Packets deep-link to S1, P1 and S3.
  - "Copy verification link" opens S2's composer.
  - Nothing renders when no tenant is linked.
- **Done when.** hangar-dev, linked to staging, deep-links to the same record id in S1. An unlinked install shows no cloud UI.

## 11. Sequencing {#sequencing}

The foundation goes first because every service needs tenancy, keys and a cluster. The workspace goes second because it proves records arrive and verify. Outside parties wait for the main spec's P-1 and P-3, which are W6 there. Five cloud waves, K0 to K4, run beside the main spec's W5 and W6.

> Diagram: cloud build order · 5 waves, 5 gates, 2 inputs from the main spec. See the original document.

Each diamond is a wave's gate, passed only with the live evidence named in the table below.

### Waves and their entry conditions

| Wave | Packages | Starts when | Gate at the end |
| --- | --- | --- | --- |
| K0 Foundation | INF-1 to INF-6, CS-1, CW-1; BK-1 alongside, since it needs no cloud | The user has created the repos, the management account and the domain | A tenant is provisioned on staging from nothing in under 10 minutes and its owner signs in through SSO. The tenant-isolation suite passes. A prod deploy of an empty app holds at the gate until a person clears it |
| K1 Workspace | CS-2, CS-3, CS-4, CS-8, CW-2, CW-3, CW-6, CW-7, INF-7, INF-8, INF-9, BK-2 | K0 gate passed; CS-8's collector needs the main spec's O-4 | Records arrive and verify. hangar-dev's core syncs 30 days to staging and the copy verifies byte for byte. P1's counts equal the packet's. The ops tenant shows a seeded console change as out of band. The DR drill passes. The ops tenant is live in prod |
| K2 Outside parties | CS-5, CS-6, CS-7, CS-9, CW-4, CW-5 | K1 gate passed, and the main spec's P-1 and P-3 merged | Verifiable by a stranger. A statement issued from S2 verifies on the public verify host with all seven checks and with JavaScript off. A revoke shows on L1. A sealed packet verifies offline. A pilot tenant is on a paid plan |
| K3 Auditor portal | CW-8, plus hosting for the main spec's P-2 and P-5 | K2 gate passed, and P-2 merged | A firm signs in with its own identity, draws and verifies a 25-record sample, and signs a receipt that the next packet carries |
| K4 Intelligence | CS-10, CW-9 | The insurer half after K2. Benchmarks after the main spec's I-2 and ten opted-in tenants | A monthly insurer statement issues on schedule and verifies at the carrier. A cell under the thresholds is refused |

### Parallel tracks

- **Track 1, infrastructure (INF).** One subagent per module. The managing agent applies to staging and the user to prod. INF-1 is the only package that blocks everything.
- **Track 2, services (CS).** CS-1 first. CS-2 and CS-3 can overlap once CS-1's provisioning exists. CS-2's core half is a Clearance PR and follows the main spec's release chain.
- **Track 3, portal (CW).** CW-1's design kit can start on day one from the canvas, before any API exists. Every other CW card waits for its service card.
- **Track 4, Backstage (BK).** BK-1 any time. BK-2 after CS-2.
- **Track 5, core changes in jfillman/clearance.** The sync client, the S3 ledger option, `/v1/info`'s cloud block, and P-3's pages. These go through the main spec's release chain, and the cloud pins the tag.

### The critical path

INF-1 to INF-2 to INF-3 and INF-4 to CS-1 (tenant provisioned) to CS-2 (records arrive) to CS-3 (hosted ledger), then the main spec's P-1 and P-3, to CS-5 and CS-6 to CW-5 (a stranger verifies a statement). Everything else hangs off that line.

With subagents, the constraint is the user's steps: accounts, the domain, repos, prod applies, merges and the first real recipients. Section 13 lists them.

### What the managing agent does at each gate

- Re-checks the next wave's dependencies against what is merged and live, not against this document.
- Runs the gate's tests itself on staging (and prod where named) and records the evidence in memory and in clearance-cloud/docs/roadmap.md.
- Sends the user one message: what passed, what was descoped, and which PRs, applies and decisions wait on them.

## 12. Cross-cutting rules {#cross-cutting-rules}

These apply to every package and are copied into every subagent brief, together with section 12 of the main spec, which still holds in full.

### Versions and releases

- clearance-cloud uses `cloud-vX.Y.Z` tags on main after green CI. The services and the portal bundle share one version.
- clearance-cloud-infra is not tagged. Each root pins module versions by git ref, and HCP Terraform applies the merged main.
- The cloud pins jfillman/clearance by tag in `go.mod`. A cloud PR that needs a new core feature waits for that Clearance tag, mirroring the main spec's #30 and #33 lessons.
- Re-read the current digests in gitops-clearance-cloud before bumping, because another session may have moved them.

### Languages

| Component | Language | Why |
| --- | --- | --- |
| cloud-api, cloud-ingest, cloud-worker | Go | Same libraries as the core (cel-go, Tessera, sigstore-go), one static binary, and the core is imported, not called over a network, where it can be |
| verify-web and L1 | Go, in the open clearance binary | Verification is reproducible from open code (P-3) |
| Portal and design kit | TypeScript, React | The main spec's language table. The browser is the only place it runs |
| Infrastructure | Terraform (HCL) | HCP Terraform with the Clearance run task gates it, and Hangar's Terraform gate already speaks it |
| Provisioning glue | Go, inside cloud-worker | No Lambda-only code paths, so one test suite covers provisioning |

### Tenancy and security guardrails

1. **Tenant isolation is tested, not assumed.** A shared suite runs in CI against kind and against staging after every deploy. Two synthetic tenants try to reach each other's records, objects, keys, secrets, queues, SSE streams and search results through every API, and every attempt must fail without revealing whether the target exists. A failure blocks the release.
2. **One key, one database, one prefix, one signing identity per tenant.** A cross-tenant join is a lint failure. Only the intelligence aggregator (CS-10) reads across tenants, from the export, never from cells.
3. **The rules the cloud keeps (section 2) each have a test.**
   - No score: a snapshot test greps rendered statements for score-like fields.
   - Exceptions cannot be hidden: an API test with a crafted request.
   - Blind prints as blind: a stopped-collector window.
   - Immutability: an update attempt.
   - Every read is recorded: a read followed by a register check.
   - Summaries, never copies: an outbound payload test.
   - Free verification: no auth on verify routes.
   - Hashes only: a schema test on public-ledger entries.
   - Verified vs claimed: the CW-3 component test.
4. **Logs and traces never hold** record bodies, secrets, approver subjects or customer resource names. The scrubbing test runs in CI and on a sample of staging logs each day.
5. **The SPA holds no token.** It uses session cookies only (httpOnly, Secure, SameSite=Strict), with CSRF protection on every write. The CSP has no `unsafe-inline` and no third-party origin, and fonts are self-hosted.
6. **Every public endpoint has a rate limit** in WAF and in the service, and request bodies are size-capped.
7. **Operator access to prod is break-glass only.** Every use is a break-glass record in the ops tenant and is reviewed weekly.
8. **A security review pass before each public surface goes live:** verify, ledger, ingest and sign-in. This is the main spec's P-3 rule, extended. An external penetration test runs before the first paying tenant.
9. **Customer AWS access is read-only and assumed with an external id.** Customers can revoke it unilaterally, and the cloud never stores customer AWS credentials.

### Live verification

- Verify against cloud-staging, not the docs. Quote record ids, ledger leaves, `clearance verify` output, HTTP responses with request ids, and `aws` and `kubectl` output with secrets redacted.
- A passing check whose guardrail is off is not evidence. Confirm WAF rules, SCPs and the gate are enforcing before counting a pass.
- Staging data is synthetic or Hangar lab data. No customer data enters staging.

### Docs and memory

- Docs move with code: clearance-cloud/docs (architecture, runbooks, the sync and API references, cost model), clearance/docs for core changes, and the UI design doc when a screen departs from its board.
- After each package, update clearance-cloud/docs/roadmap.md, the decisions log, and the project memory with PR links and live evidence.

## 13. Open questions and risks {#open-questions-and-risks}

Each question names the package it blocks, the recommendation, and who decides. The managing agent proceeds on the recommendation where the row says agent, and stops where it says user.

| # | Question | Blocks | Recommendation or decision | Decides |
| --- | --- | --- | --- | --- |
| 1 | Which domain hosts app, verify, ledger, ingest and auth? | INF-2 | **Decided:** hangarplatform.dev for now. The subdomain `clearance.hangarplatform.dev` is delegated to a Route 53 zone in shared-services. A dedicated product domain can come later; INF-2 keeps the zone name a single variable so a move is a new certificate and a redirect, not a rebuild | James, 2026-11-09 |
| 2 | Recipient sign-in for V2: email or SSO? | INF-5, CS-5 | **Decided:** both. An emailed magic link for anyone, and the recipient's own SSO (SAML or OIDC) when their organization has one | James, 2026-11-09 |
| 3 | Is an EU region needed? | INF-1 | **Decided:** USA only for now. Terraform roots stay region-parameterised so EU is a new root later | James, 2026-11-09 |
| 4 | Does Community get a cloud workspace? | CS-9 | **Decided:** no. Community is Backstage and the offline verifier only. The cloud starts at Team | James, 2026-11-09 |
| 5 | Cell per tenant, or a pooled cell for Team? | CS-1, INF-9 | Cell per tenant at launch. Revisit when INF-9's model shows the marginal cost of a Team cell exceeds a set share of Team revenue | Agent, then user at the threshold |
| 6 | Tessera AWS driver or single-writer POSIX for hosted ledgers? | CS-3 | AWS driver, after the spike confirms checkpoint latency under 60 s with 50 tenant logs on one Aurora MySQL cluster | Agent |
| 7 | Who runs the external witness? | CS-3 | **Deferred by James, 2026-11-09.** Recommendation stands: a public witness network first, then a willing audit firm, never only Clearance's own. K0 and K1 run with the Clearance witness alone, and statements print "not yet independently witnessed". An external witness is needed before K2's gate | User |
| 8 | Billing provider for direct sales | CS-9 | **Decided:** Stripe for card and invoice, plus AWS Marketplace for customers who buy through AWS | User |
| 9 | Where does the ops core that gates the cloud run? | INF-6 | shared-services, self-hosted from the open chart, syncing to an ops tenant in cloud-prod. It must not depend on the cloud it gates | Agent |
| 10 | Retention defaults per tier | INF-4 | **Decided:** 1 year for Team, 7 years for Business, and 7 years plus legal hold for Regulated. These cannot be shortened once written. **Added 2026-11-22 (A-7):** 30 days for a trial or pilot tenant | User |

### Risks the managing agent watches

- **A cross-tenant leak.** It would end the product. The isolation suite gates every release, and any failure stops the wave.
- **Object Lock is permanent.** A wrong retention on prod objects cannot be undone. INF-4's prod apply waits for the user's retention sign-off and a staging test.
- **The cloud becoming the record.** If customers stop keeping their in-cluster chain, the open-core story weakens. The sync keeps the customer's copy authoritative, and escrow (CS-4) returns it nightly.
- **The main spec slipping.** K2 waits for P-1 and P-3. If W6 slips, K1 still ships a useful workspace with packets from CS-7.
- **Cost of a cell per tenant.** INF-9 measures it before the first Team tenant, not after.
- **One operator.** T3 clearances need two people. Until a second operator exists, prod applies are single-cleared exceptions, printed as such in the ops tenant's packet.

### Waiting on the user before K0 can start

- [ ] Create jfillman/clearance-cloud, jfillman/clearance-cloud-infra and jfillman/gitops-clearance-cloud (private).
- [ ] Create the AWS management account and payer, and an HCP Terraform organization.
- [ ] Delegate clearance.hangarplatform.dev (question 1).
- [ ] Arrange the external witness (question 7) before K2. The setup steps are in Clearance Cloud setup: owner steps.

## 14. Outstanding suggestions and decisions {#outstanding-suggestions-and-decisions}

This is the one Clearance Cloud build spec. It replaces the Claude Doc of the same name, retired on 2026-11-20. This section carries what the doc left open: its pending tracked suggestions, and the decisions still open on the Clearance Cloud Strip Board. Nothing here is applied to the sections above.

### Pending suggestions from the retired doc

Fifteen suggestions were pending in the doc when it was retired, all laid on 2026-11-14 and all unreviewed. They are proposals only: the body above keeps the accepted text. The doc gave no reason with any of them, so the reason column says so. Ids are CSG-n (Cloud SuGgestion) so they do not collide with the CS-series work packages.

| Id | Section it touches | Proposed change | Reason | State |
| --- | --- | --- | --- | --- |
| CSG-1 | 3. Current state, status of "Receipts, sampling, statements and verify page, GRC push (P-1 to P-4)" | Replace "Proposal (main spec W6)" with "Built: main spec W6, merged and released as core 0.48.0 on 2026-11-14; proven against fakes, not deployed" | None given | pending owner |
| CSG-2 | 4. Target architecture, Components, verify-web row | Replace "V2's recipient detail comes through cloud-api under the recipient's grant" with "V2's recipient detail is never served on the public verify route: the open route carries the public summary only, and recipient detail sits behind sign-in" | None given | pending owner |
| CSG-3 | 5. AWS deployment infrastructure, Edge and domains table | Add a row: host `slack.<domain>`, "The clearance-slack link page (a record in the INF-2 zone)", note "Owner decision 2026-11-14: slack.clearance.hangarplatform.dev is a record in the INF-2 zone" | None given (the row quotes an owner decision of 2026-11-14) | pending owner |
| CSG-4 | 5. AWS deployment infrastructure, Identity and access, recipient sign-in paragraph | After "(decided 2026-11-09)" add " (superseded for W6: P-1 builds a registered key only as recipient identity, and OIDC recipient identity is deferred, not built)" | None given | pending owner |
| CSG-5 | 6. Gap analysis, row "P-1 deliveries and credentials" | Replace "Proposal" with "built: core 0.48.0, 2026-11-14, not deployed" | None given | pending owner |
| CSG-6 | 6. Gap analysis, row "P-3" | Replace "Proposal" with "built: core 0.48.0, 2026-11-14, not deployed; the public verify route stays off until its security review is accepted" | None given | pending owner |
| CSG-7 | CS-5 Grants and the access register, Build | After "The S2 access register over P-1's deliveries" add " (the core issues and verifies the recipient credential, scoped and time-boxed, every fetch a record; cloud-api only passes it through and keeps its own grant register)" | None given | pending owner |
| CSG-8 | CS-5 Grants and the access register, Build, revoke | After "revoke takes effect at once and writes to the public ledger" add " (core 0.48.0 has no credential or key revocation; the core's delivery and recipient-key revoke routes merged on 2026-11-14 and are not yet released, so until a release carries them this revoke acts in cloud-api's register only, and after it cloud-api calls the core's delivery revoke as well)" | None given | pending owner |
| CSG-9 | CS-6 Hosting statements, the verify page and the ledger explorer, Build | After "verify-web deployed from the open binary at `verify.<domain>/s/{id}` (V1)" add " as its own process, not inside the core; the public listener ships off by default and stays off until the owner accepts the security review" | None given | pending owner |
| CSG-10 | CS-10 Insurer statements and the intelligence hooks, Build | After "The monthly insurer statement schedule per carrier" add " (P-3 has no built-in scheduler in W6, so cloud-worker calls the issue route on each carrier's schedule)" | None given | pending owner |
| CSG-11 | CW-1 App shell, design kit and sign-in, Build, the `@clearance/cloud-ui` package | Add a sentence: "This kit belongs to the Cloud portal (business-facing, Cognito) and shares no package with the standalone Clearance UI (clearance web and the jfillman/clearance-ui package; operational: clearances, evidence, exceptions, attestations, map, policy)." | None given | pending owner |
| CSG-12 | CW-8 The auditor portal (AU1, AU2), Build, engagement view | Delete " or OIDC identity" after "signing with the firm key" | None given (it matches CSG-4, which defers OIDC recipient identity) | pending owner |
| CSG-13 | 11. Sequencing, Waves and their entry conditions, the "Verifiable by a stranger" gate | After "all seven checks" add " (the page's headline is "VERIFIED, WITNESS INDEPENDENCE DECLARED", never plain VERIFIED, because independence is the issuer's declaration; plain VERIFIED with all seven green is the offline result when the reader names the witness key)" | None given | pending owner |
| CSG-14 | 11. Sequencing, Waves and their entry conditions, same gate | After "and with JavaScript off." add "The main spec's W6 gate is the P-series code proven against fakes; this gate is the hosted proof on verify.clearance.hangarplatform.dev, and the external witness, deferred until now (lab statements print "not yet independently witnessed"), is in place before it, so all seven checks green is proven here." | None given | pending owner |
| CSG-15 | 12. Cross-cutting rules, Tenancy and security guardrails, free verification | After "Free verification: no auth on verify routes" add " (public summary and public ledger only; recipient detail, statement level V2, is never served on the public route and needs sign-in)" | None given | pending owner |

### Open decisions from the Clearance Cloud Strip Board

Source: the Clearance Cloud Strip Board, https://claude.ai/artifact/N9sDgHyHKjF8aMfAcxjr8f, read on 2026-11-22. The board holds the live state; this table is a snapshot.

| Strip | Touches | What is open | Options and recommendation | State |
| --- | --- | --- | --- | --- |
| (none) | | No ask strip is open on 2026-11-22 after A-7 and A-8 were answered | | |

Answered on the board since the last snapshot (owner): A-5 (a), a separate owner-applied root creates the Object Lock buckets; A-6 (a), the staging proof uses 1-day retention; A-7 (a), the retention mapping above; A-8 (a), owners sign in through their own SSO. The owner steps Y-5 to Y-14 are done.
