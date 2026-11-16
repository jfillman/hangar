# W6 P-series work-package cards (Clearinghouse)

Verbatim extract of Clearance spec rev 101 (Claude Doc https://claude.ai/artifact/BCosjaYXnJzghRF6VZsL5D), taken 2026-11-14. Text is copied as the doc holds it; links and bullets are kept, bold labels are shown as **bold**. Nothing here is edited or paraphrased.

Companion docs (not opened for this extract):
- Clearinghouse: https://claude.ai/artifact/3rPgELsmjQJ5rqsz386D9Q
- Verification: https://claude.ai/artifact/UfE1xys4nK9C7D2gNm25Lp
- Underwriting: https://claude.ai/artifact/PaZMadKYhzJSJgTBHxiw6B

---

## Work packages, P-series: the clearinghouse and the outward statements

Five packages build what the packet is for once it exists: the recipients who accept it, the sample an auditor pulls, the statement a subscriber hands a prospect or a carrier, the push into a GRC hub, and, last, the portal (added 2026-11-07; the [Clearinghouse](https://claude.ai/artifact/3rPgELsmjQJ5rqsz386D9Q), [Verification](https://claude.ai/artifact/UfE1xys4nK9C7D2gNm25Lp) and [Underwriting](https://claude.ai/artifact/PaZMadKYhzJSJgTBHxiw6B) companions have the design). Three rules from those documents bind every package: verification, witness operation and acceptance are free and need no account; the subscriber grants access and Clearance records it, Clearance never submits on anyone's behalf and never pays a recipient; and no page ever scores or ranks a subscriber. Everything here is Go in the clearance repo; the public verify page is a small server-rendered page in the same binary, no JavaScript framework.

### P-1 · Assurance providers: acceptance receipts and recipient access

- **Repos.** clearance, hangar docs.
- **Depends on.** C-5 (the packet), C-3 (the ledger the receipt lands in).
- **Build.** The assurance-provider contract from the Architecture's chapter 08 as a registered provider class: `POST /v1/packets/{id}/deliveries` (the subscriber names a recipient, a scope and a window; the delivery is a ledger record), `GET /v1/packets/{id}` for the recipient under a scoped, time-boxed credential (every fetch a record), and `POST /v1/packets/{id}/receipts` where the recipient signs an acceptance receipt with its own key (packet id, engagement, framework and mapping versions, checkpoint, verdict accepted, accepted with notes, questioned or rejected, per-control notes keyed to mapping row ids). The receipt is a ledger record of its own; later packets carry prior receipts in their Acceptances section (C-5) and `clearance verify` checks the recipient's signature against the key it registered. A `clearance receipt sign` subcommand for firms that have no system to sign from. Recipient identities are OIDC or a registered key, never a Clearance account.
- **Done when.** A fake assurance provider pulls a lab packet under a time-boxed credential, signs a receipt, and the next packet's Acceptances section carries it and verifies; an expired credential is refused and the refusal is a record; the roadmap's phase 3 "GRC lead forwards a packet unchanged" test runs through this route.
- **Rollout.** Clearance release.
- **User steps.** The first real recipient's key or OIDC issuer.

### P-2 · The sampling call

- **Repos.** clearance.
- **Depends on.** P-1, C-4.
- **Build.** `GET /v1/packets/{id}/sample?n=&seed=&stratify=` returns a statistically valid sample of cleared records (uniform or stratified by tier and month, seed recorded so the auditor can reproduce it) with an inclusion proof per record against the packet's checkpoint range, and the sampling itself as a record. The population is every change in scope, printed with the sample, so a firm can test the population before the sample (the ChatGPT analysis's point and the auditor pilot's measurement). `clearance verify` checks a sample file offline the same way it checks a packet.
- **Done when.** A 25-record sample of a 30-day lab packet verifies offline; the same seed reproduces the same sample; a record outside the scope cannot be sampled.
- **Rollout.** Clearance release.

### P-3 · The verification statement and the hosted verify page

- **Repos.** clearance, apron (the public route), hangar docs.
- **Depends on.** C-3, C-4, C-5, O-1 (the three-part coverage), C-14 (approver kind), P-1 (receipts to show).
- **Build.** The verification statement as the packet's fourth derived view (Architecture chapter 11): `POST /v1/statements` from a period, a scope and a policy version produces an immutable, signed statement with two levels. The public summary (period, scope as printed, policy version, counts by every coverage state, exceptions by class, the observation-health summary, the verification result, the firms whose receipts are attached, a questionnaire-mapping block shipped as data beside the control mapping with SOC 2 CC8.1 and CC6, ISO 27001 A.8.32, NIST SP 800-53 CM-3 and CM-5 and the SIG change-control and AI topics, worded as evidence for those objectives) and the recipient detail (exception rows with resolutions, record ids, proofs as files), opened by the subscriber to a named recipient and recorded like auditor access. Invariants enforced in the core: totals, every coverage state, exceptions and unreconciled counts can never be omitted; the scope is the only choice; a correction supersedes (`supersedes` on the new statement, `supersededBy` on the old); `POST /v1/statements/{id}/revoke` makes it verify as revoked. The hosted page at `verify.<domain>/s/{id}` runs the seven checks in order (signed by the subscriber's Clearance identity; signature valid; every cited record has an inclusion proof against a checkpoint; checkpoints countersigned by a witness Clearance does not run; counts recompute from the cited records; exceptions and health present and matching; not superseded or revoked), prints one word and one colour at the top with the checks behind a click, and links `clearance verify --statement <url>` for the reader who wants to run it alone. The insurer profile is the same statement with `profile: insurer`: the share of critical changes with two independent approvers (from C-14's `kind: person`), unresolved exceptions each with a disposition, telemetry coverage per scope as a share of the period, the agent share of changes, and a mapping block in carriers' words (privileged change, separation of duties, unauthorized-change detection); monthly cadence by a schedule the subscriber sets. The statement format and the verification rules are published with the verifier (a `docs/statement.md` and a JSON schema), so a reviewer or a trust-center platform verifies without Clearance. The page never scores or ranks.
- **Done when.** A lab statement verifies on the hosted page in under two seconds with all seven checks green and the proofs downloadable; a revoked statement shows revoked; a superseded one points at its successor; a statement with a stopped collector in its window prints the blind window; an insurer-profile statement prints the five figures; `clearance verify --statement` passes offline against the published trusted root; a page load with JavaScript disabled still shows the result.
- **Rollout.** Clearance release, apron render (the public route and its rate limit), hangar docs.
- **User steps.** The `verify.<domain>` DNS and certificate; the first shared statement, to a real prospect's reviewer if one exists.

### P-4 · GRC push, Vanta first

- **Repos.** clearance, hangar docs.
- **Depends on.** P-1, C-5. The roadmap's phase 2 item; it waits here only because the packet does.
- **Build.** The hub as an assurance provider that receives summaries and links, never copies: Clearance registers on the hub's evidence API, the customer connects a tenant with an API key, and each production change becomes an evidence item mapped to the hub's control identifiers (origin, tier, approver, digest, a link to the verifiable record) with a periodic coverage report. The signed record stays in Clearance; the hub holds a pointer. Drata second, behind the same interface. Unverified until tried: whether the hubs' evidence APIs accept structured attestations rather than files, and whether a firm signs a receipt from inside the hub's workflow.
- **Done when.** A lab change appears as an evidence item in a Vanta sandbox tenant with a working link back to the record; the coverage report lands on schedule; nothing but hashes, links and summaries leaves the tenant (asserted by a test on the outbound payloads).
- **User steps.** A Vanta sandbox or partner tenant.

### P-5 · The auditor portal and the working-paper push (later)

- **Repos.** clearance, backstage or a standalone page.
- **Depends on.** P-2, P-3; two firms having accepted a packet (the roadmap's phase 5 trigger).
- **Build.** Scoped, time-boxed, recorded read access for a firm: the packet, the sample call and the verification page behind one firm identity, with the firm's engagements as the unit of scope; a working-paper push to Suralink or AuditBoard as a provider endpoint so the packet never passes through email; the pilot's three measurements captured as records (hours on change-management testing against the firm's prior-year figure, the share of the sample verified without a client request, acceptance of a coverage statement with a blind window). The large firms' own systems when a subscriber brings one.
- **Done when.** One firm accepts a ledger sample in place of a ticket sample on one engagement, with its receipt in the ledger and the three measurements recorded.
- **User steps.** The firm.

---

## Wave table, row W6 (block mvpvtx8f3hm.213328)

| Wave | Packages | Starts when | Gate at the end |
| --- | --- | --- | --- |
| W6 Clearinghouse | P-1, P-2, P-3, P-4 | W5 gate passed (P-1 and P-4 may start after W4, since they need only the packet) | **Accepted and verifiable by a stranger**: a fake assurance provider pulls a packet under a time-boxed credential and signs a receipt that the next packet carries; a 25-record sample verifies offline; a verification statement verifies on the hosted page with all seven checks, shows revoked when revoked, and prints a blind window when there was one; a change appears as an evidence item in a Vanta sandbox with a link back |

## Track 7 bullet (block mvpvtx8f3hm.214319)

- **Track 7, clearinghouse** (P): sequential after the packet; P-3 is the one with a public surface and gets the security-review pass of section 12 before its route is rendered; P-4 can run as soon as C-5 exists and a Vanta sandbox is available.

## Section 12 guardrail (block mvpvtx8f3hm.219951)

- **The hosted verify page is a public surface (added 2026-11-07).** It is the first Clearance route reachable without an identity. Mitigation: a separate route with a rate limit, server-rendered with no JavaScript required, the statement id unguessable, the page reads only published statements and proofs, and the section 12 fuzz targets cover its inputs; the recipient detail level is never on the public route.

Open questions: a search of the open-question table for "clearinghouse", "Vanta", "receipt", "sampl" and "verify page" returned no open-question rows. The only matches outside the P-series are the roadmap rows that list P-1 to P-5 (the gap table and the deferred-portal table), which are not copied here.

---

## Summary

1. P-1 Assurance providers: receipts and recipient access. Depends on C-5, C-3. Done when a fake provider pulls a lab packet under a time-boxed credential, signs a receipt, and the next packet's Acceptances section verifies.
2. P-2 Sampling call. Depends on P-1, C-4. Done when a 25-record sample of a 30-day lab packet verifies offline and the same seed reproduces it.
3. P-3 Verification statement and hosted verify page. Depends on C-3, C-4, C-5, O-1, C-14, P-1. Done when a lab statement verifies on the hosted page in under two seconds with all seven checks green, and a revoked statement shows revoked.
4. P-4 GRC push, Vanta first. Depends on P-1, C-5. Done when a lab change appears as an evidence item in a Vanta sandbox tenant with a working link back, and only hashes, links and summaries leave the tenant.
5. P-5 Auditor portal and working-paper push (later). Depends on P-2, P-3 and two accepting firms. Done when one firm accepts a ledger sample in place of a ticket sample on one engagement.
6. W6 Clearinghouse wave: packages P-1 to P-4; starts after the W5 gate (P-1 and P-4 may start after W4).
7. W6 gate: accepted and verifiable by a stranger (fake provider receipt carried by the next packet; offline 25-record sample; hosted statement with seven checks; Vanta sandbox evidence item with link back).
8. Track 7: sequential after the packet; P-3 needs the section 12 security-review pass before its route is rendered; P-4 can start once C-5 exists and a Vanta sandbox is available.
9. Section 12 guardrail: the hosted verify page is a public surface with a rate limit, unguessable ids, published-data-only reads, and fuzz coverage.
10. No open-question rows in the doc cover the clearinghouse, Vanta, receipts, sampling or the verify page.
