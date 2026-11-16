# Design proposal: using Clearance without Backstage (person CLI, Slack)

Status: proposal, 2026-11-12. No code, no PRs. Evidence base is `origin/main` of clearance and backstage (paths below are
repo-relative; `clearance:` = /Users/jerf/tech/clearance, `backstage:` = /Users/jerf/tech/backstage).

## 0. What exists today (so we reuse it)

| Capability | Where |
|---|---|
| Person reads: evidence, clearances (+counts, one change with token and attestation), attestation bundle, exceptions, observations, coverage, policy + `policy/explain` ("why this tier"), receipts, definitions | `clearance: docs/clearance-api.md` (routes table, "Observations and the coverage statement") |
| Person writes, all on the **core**: `POST /v1/clearances/{id}/clear`, `/deny {reason}`, `POST /v1/observations/{seq}/resolution`, `POST /v1/observations/resolutions` (bulk, 200), `POST /v1/breakglass` | `clearance: docs/core.md` (routes table), `docs/gate.md` ("By people", "Bulk resolution", "Break-glass") |
| Wait on a change (long-poll) and live feed (SSE, resume by `Last-Event-ID`, 8 streams/caller, ends at 10 min) | `clearance: docs/core.md` (`/wait`), `docs/clearance-api.md` ("The stream") |
| Roles: person, `delegate` (names a person in `X-Hangar-On-Behalf-Of`), `auditor`, `feed`, `notifier`, `observer` | `clearance: docs/clearance-api.md` ("Who sees what"); `CLEARANCE_DELEGATES` in `docs/core.md` |
| Approvals record the person **and** the delegate (`"iss": "delegate:<principal>"`, `person`); `DG-PROPOSER`, `DG-TWICE`, `DG-APPROVER-AUTOMATION`, `DG-APPROVER-SAME` (same `sid` or subject counts once) | `clearance: docs/core.md` (~l.292-299), `docs/gate.md` (~l.703-709) |
| People sign-in: people-dex (Dex + GitHub), public client `clearance`, **device flow**, 1 h ID tokens, **no refresh grant**; principal = `user:<preferred_username>`; allowlist `CLEARANCE_OIDC_ALLOWED_USERS`; laptop helper keeps the token in the macOS Keychain | memory `project_people_signin_d19_interim.md`; `tools/hangar_login.py` (autopilot repo); `clearance: docs/core.md` (`CLEARANCE_OIDC_*`) |
| Backstage write proxy: exactly the endpoints above, as delegate, 16 kb bodies, whitelisted fields, `validateResolution` vocabulary (states, causes, note <= 1000) | `backstage: plugins/clearance-backend/src/proxy.ts` (`WRITE_ROUTES`) |
| Alerts: `clearanceAlerts.ts` polls as machine `observer` every 120 s, notifies when a scope turns degraded/blind and on each monitoring-protection exception; off by default; recipients `broadcast` or an entity ref | `backstage: plugins/clearance-backend/config.d.ts` (`alerts`), `plugins/clearance/README.md` |
| The notifier role exists but "no Clearance read is a notifier's" (inbox feed is the gateway's) | `clearance: docs/clearance-api.md` ("Differences", notifier) |
| PR-side signal: the `clearance-gate-` check reports holding/cleared on the PR. `docs/gate.md` ~l.159 lists "Slack/PR comment through the check" as phase-1 intent; **grep of docs finds no built Slack or email code**. `CLEARANCE_GITHUB_APP_COMMENTS` is `off`/`agent-failures` only (agent failures, not holds) | `clearance: docs/gate.md`, `docs/core.md` (env table) |
| Today's CLI is servers, CI steps and verification only | `clearance: cmd/clearance/*.go`, `docs/core.md` (subcommand table) |

Consequence: **every read and write a person needs already has an HTTP endpoint**. The work is a client, an identity story and
a notifier. Gaps are small and listed per phase in section 5.

---

## 1. Person CLI

### 1.1 Binary: `clearance` subcommands, not a separate `clr`

Recommendation: add person-facing subcommands to the existing `clearance` binary (Go, `cli.Register`), under a noun-verb
tree, plus an optional `clr` symlink/alias installed by the release (same binary, `argv[0]` dispatch).

- One artifact to sign, attest and distribute; `clearance attest verify` / `packet` / `chain verify` already live there and
  people reasonably expect `clearance attest download` + verify in one tool.
- Cost: the binary also contains the core. Mitigate with a build tag or `-ldflags` slim variant only if size matters
  (it is a static Go binary; not a security concern since the server subcommands need server env to do anything).
- Share the typed client with the Slack service via a new `internal/personclient` package (no Tower imports, per the
  Clearance repo rule).

### 1.2 Command set (mirrors the Backstage features)

| Command | Endpoint | Notes |
|---|---|---|
| `clearance inbox` | `GET /v1/clearances?state=holding` + "can I clear" | Server-side "what waits on me" filter is a gap (G1) |
| `clearance changes list [--app --env --state --tier --since]` | `GET /v1/clearances` | table/json |
| `clearance changes show <id> [--why] [--diff]` | `GET /v1/clearances/{id}`, `GET /v1/clearance-policy?app&env` | `--why` prints the tier reasons (objects + rules) and approvals needed vs. held |
| `clearance changes clear <id>` / `deny <id> --reason ...` | `POST .../clear`, `.../deny` | reason mandatory for deny, confirmation prompt on tier >= 2 (`--yes` for scripts, refused on tier 3 without a TTY) |
| `clearance changes history <id>` | `GET /v1/evidence?...` filtered to the change's `deploy.*` records | needs a `change=` evidence filter (G2) |
| `clearance changes wait <id>` | `GET .../{id}/wait` | exits 0 on cleared, non-zero on denied/expired: scriptable |
| `clearance attest get <id> [-o bundle.json]` / `attest verify` (exists) | `GET /v1/clearances/{id}/attestation` | `attest verify --change <id>` fetches, then verifies offline with the trust root |
| `clearance exceptions list [--scope --kind --unresolved]` | `GET /v1/exceptions`, `GET /v1/observations?kind=resolution` | |
| `clearance exceptions resolve <seq...> --state ... [--cause ...] [--note ...]` | `POST .../resolution`, bulk `.../resolutions` (chunks of 200) | admin only; same vocabulary as `proxy.ts` `RESOLUTION_STATES/CAUSES`; `--dry-run` lists what would be skipped |
| `clearance coverage [--scope] [--from --to]` | `GET /v1/coverage` | exit code 0 healthy, 1 degraded, 2 blind (usable in scripts and on-call) |
| `clearance evidence list/show/counts` | `GET /v1/evidence[...]` | `--seq` cursor paging |
| `clearance watch [--types clearances,records]` | `GET /v1/stream` | reconnects with `Last-Event-ID`, dedupes by seq, survives the 10 min server cut-off |
| `clearance breakglass open/close` | `POST /v1/breakglass` | admin, always interactive, always shows the reason it will record |
| `clearance login / logout / whoami` | see 1.3 | |

Global: `-o table|json|jsonl|yaml`, `--api`, `--core` (or a context file holding only URLs, never tokens), `--no-color`,
stable exit codes, `NO_COLOR`. JSON output is the API answer verbatim (the contract is OpenAPI 3.1 at `GET /v1/contract`; the
client can be generated from it and a conformance test can diff it, as `contract.test.ts` does for Backstage).

### 1.3 Auth

Requirement: the core must see a real `user:<login>` principal with a verifiable IdP subject and session, because the gate's
approver rules key on it (`DG-APPROVER-SAME` uses `sub`/`sid`; `DG-APPROVER-AUTOMATION` rejects non-people).

**Flow: OIDC device-code against people-dex** (already live, public client `clearance`, issuer in `CLEARANCE_OIDC_ISSUER`).
It works headless/over SSH and needs no loopback listener. Add **PKCE loopback** as an optional second flow only if people-dex
gets a browser-capable client; the device flow is the one proven in the lab. The issuer for production people is the
owner's choice (see decision D1); the CLI is issuer-agnostic via OIDC discovery.

**Direct person token, not a delegate.** The CLI sends the person's ID token (`Authorization: Bearer`) straight to
clearance-api and the core. The principal is the person; no delegate is involved, so the record shows exactly who and from which IdP session (`sid`), and the gate's
approver checks need no extra trust. Delegates are for services that cannot hold the person's token (Backstage backend,
Slack).

**Token handling (owner preference: never-persisted, mint-per-call over cached):**

| Option | Persisted? | Verdict |
|---|---|---|
| A. In-memory only, device login per invocation | no | strictest; unusable for repeated commands, but right for CI-ish `--token-from-stdin` and for `changes clear` in step-up (below) |
| B. OS keychain, ID token only, **no refresh token** (people-dex issues none), expiry <= 1 h | short-lived, OS-protected | **recommended default**; matches `hangar_login.py` (service `hangar-clearance`); after 1 h the user re-runs `login` |
| C. Refresh token on disk | long-lived | rejected; also Dex here has no refresh grant |
| D. Agent daemon holding the token in memory (ssh-agent style) | no disk | optional later (P2+) if re-login friction hurts; adds a daemon to secure |

Rules: the token never goes in a config file, env var by default, or shell history; `CLEARANCE_TOKEN` env is allowed only for
automation and warns when set on a TTY; the CLI never logs `Authorization`, never prints a token (the repo's own redaction
bar); Linux without a keyring falls back to **A** (re-login), not to a file. Writes with a token older than 15 minutes
re-prompt (a "fresh login" rule enforced client-side now; server-side via `auth_time`/`amr` check is gap G3 and is what makes tier 3 trustworthy from any surface).

**Attribution:** the clear/deny record names the person (`cleared_by`, approval `sub`, `person`) and, for a direct token, no
delegate. Add a `client` hint (`cli/<version>`) recorded beside it (gap G4) so audits can distinguish surfaces; it is
unverified metadata and is labelled so.

---

## 2. Slack

### 2.1 Architecture: a small Go service `clearance-slack`, as a delegate, in the Clearance repo

| | A. Standalone `clearance-slack` (Go) | B. Inside Autopilot's gateway |
|---|---|---|
| Trust | Own principal; listed in `CLEARANCE_DELEGATES`, `CLEARANCE_API_OBSERVATION_READERS`; blast radius = one small process | Gateway already holds runtime powers (sessions, tools); adds a human-approval path next to agent powers |
| Boundary | Clearance owns person controls; Slack is a surface on Clearance | Contradicts "Clearance is in the path; MCP/sessions/dispatch/model proxy are Autopilot's": approvals are Clearance's |
| Reuse | Same `internal/personclient` as the CLI; same alert semantics as `clearanceAlerts.ts` | Reuses gateway's inbox feed, but that feed is agent human-requests, not gate changes |
| Ops | One more Deployment | none extra, but couples release trains |

**Recommendation: A**, in the Clearance repo (Go: security + efficiency, per standing guidance), deployed by Autopilot/apron like clearance-api. It
holds no signing keys and no database writes of its own beyond a small state table (see 2.5), and it acts only by calling the
core as a delegate.

Delegate pattern (same as Backstage): the pod's projected ServiceAccount token (read per call, never cached, same as
`ClearanceReadClient`) + `X-Hangar-On-Behalf-Of: user:<login>` resolved from the **verified Slack identity link**. Principal
`autopilot-system/clearance-slack` goes in `CLEARANCE_DELEGATES`; for reads that need no person (alerts) it is an `observer`
(and `notifier`-style reads for changes, gap G5).

### 2.2 Notifications

Source of truth is the API, never Slack. Two feeds, both machine-readable already:

- `GET /v1/stream` (SSE, resumable) for change state (`event: clearance`) and records; reconnect every 10 min with `Last-Event-ID`. Caveat: stream scoping is per viewer (a delegate sees only what the named person may see). The service needs an **all-changes machine view** (G5): a `notifier` (or `observer`) role reading `clearance` events for every change, redacted like a person. Without G5 it can poll per linked person, which is O(users); not recommended.
- Coverage/exception polling every 120 s exactly as `backstage: packages/backend/src/clearanceAlerts.ts` does (`/v1/coverage`, `/v1/exceptions`) with the same dedupe semantics (alert on transition to degraded/blind and on each monitoring-protection exception; one "recovered" message).

| Event | Trigger | Default destination |
|---|---|---|
| Hold waiting on you | change `holding`, you qualify as approver (owner group, or outside group) | DM to each qualifying person, plus owner-group channel (one thread per change, updated in place) |
| Tier 3 waiting on an outsider | holding tier 3, owner approval present, outside approval missing for > N min | outside group's channel (`#platform-leads`/security); DM to members |
| Exception / break-glass | `deploy.exception`, `breakglass.open/close`, `attempted-refused` | owner-group channel for the scope; `#clearance-security` for break-glass and monitoring-protection (always) |
| Coverage degraded/blind | `/v1/coverage` state transition | scope's owner channel + `#clearance-security` |
| Attestation signing stuck | cleared change, `deploy.outcome` reported, `attestation: null` after T | `#clearance-ops`; needs a "stuck" signal (G6: an attestation-pending age on the change, or the evidence record for it) |
| Expiring hold | holding past 75 % of TTL | DM to qualifying people |

Routing: owner group to channel via a small mapping in the service config (`group:default/<x>` -> channel id), kept in the
deployment's catalog sync rather than hand-edited when the Directory is reachable (G7: a read of group membership; the
Backstage people-dex "Directory" the inbox uses). DM vs channel is a per-user setting (`/clearance prefs`), defaults: DM for
"waiting on you", channel for everything else. Messages carry id, app, env, tier, why-this-tier (first 3 reasons), proposer,
age and a link to Tower/web; **never** secret-bearing values (use the API's redacted view only).

### 2.3 Actions from Slack

Buttons: **Clear**, **Deny...** (opens a modal that requires a reason), **Resolve exception...** (modal: state, cause when
reverted, note; the same vocabulary as `proxy.ts`).

**Identity linking (Slack user -> IdP identity).** Do not trust display names, profile emails or `/clearance as <name>`.
- One-time **link flow**: user runs `/clearance link` -> the service replies ephemerally with a one-time URL `https://clearance-slack/.../link?state=<nonce>` -> the page does the **IdP OIDC login** (people-dex today) and **Sign in with Slack** (OIDC, `openid` scope; returns Slack `sub` = team id + user id) in the same browser session, then stores the pair `(slack team_id, slack user_id) <-> (iss, sub, preferred_username)` after verifying both ID tokens (signature, nonce, audience). Link is bound to `team_id` as well as user id (so a user id from another workspace/Enterprise Grid org cannot match).
- Stored in a small table (Postgres or the cluster's existing store; no secrets, just ids). Unlink on `/clearance unlink`, on Slack user deactivation (`user_change`/`team_access` events), and re-verified every 30 days. Re-link requires the IdP login again.
- The principal sent in `X-Hangar-On-Behalf-Of` is always the **IdP-verified** login from the link, never from the Slack payload. A Slack user with no link gets "link your account" and nothing else.

**Request authenticity.** Events API/interactivity: verify `X-Slack-Signature` (HMAC-SHA256 over `v0:<ts>:<body>` with the
signing secret, constant-time compare), reject if `|now - ts| > 5 min` (replay), and keep a short LRU of seen
`(ts, signature)`/`trigger_id` to refuse exact replays within the window. Socket Mode delivers over an authenticated websocket and has no inbound HTTP
signature, but the same envelope-ID de-dupe and `acknowledge` rules apply. Idempotency: the action's `change_id` + approver
means a double click is a harmless `DG-TWICE`/`DG-STATE` from the core; the service also disables the button on first press.

**Which tiers may be cleared from Slack** (the gate's guarantees stay; this only narrows the surface):

| Tier / action | From Slack | Why |
|---|---|---|
| 0, 1 | nothing to clear (policy) | |
| 2 (one owner, not proposer) | **Clear + Deny** in place, modal confirm showing the diff summary and head sha | owner-group person, linked identity |
| 3 (two people incl. outside) | **Deny in place; Clear = link-out** to Tower/web/CLI for a fresh IdP login (step-up) | the second approver must be a verified person with a fresh session; `DG-APPROVER-SAME` relies on `sid`, which a long-lived Slack link cannot supply |
| Break-glass open/close | **link-out only** | rare, high blast radius, wants a deliberate step-up |
| Resolve exception (one) | in place if the person is an admin | append-only, newest wins, recorded |
| Bulk resolve | link-out / CLI | |

Default can be loosened per deployment (`slack.clearTiers`), but "tier >= 3 and break-glass clear" stays link-out in the product default.

**Audit: `via: slack`.** Today the record shows the delegate principal, which already identifies the surface
(`delegate:autopilot-system/clearance-slack`, `docs/core.md` approvals example), but not whether the person had a fresh login. Proposal (gap G4): the core accepts an optional
`X-Clearance-Via: slack|cli|web` from a delegate or direct caller and records it as unverified `via` next to `person`
and `delegate`, with the Slack message permalink and workspace/team id in a `surface_ref` string field. For tier-2 clears, also
record `identity_link: {linked_at, verified_by}` so an auditor sees how the person was bound.

### 2.4 Socket Mode vs Events API

| | Socket Mode | Events/Interactivity API (HTTPS) |
|---|---|---|
| Public ingress | **none** (outbound websocket) | needs a public HTTPS endpoint + signature checks |
| Slack App Directory | not allowed for distributed apps (fine: internal app) | required for distribution |
| Reliability | one websocket per connection; reconnect + `envelope_id` ack | stateless HTTP, easy to scale |
| Fit | **Off here / lab**: hangar-dev has no public ingress (laptop relays, `.local` hosts), so Socket Mode is the only option that works; also good enterprise default for private clusters | Production with an ingress and a WAF; supports multiple replicas behind a LB |

Recommendation: implement behind one interface, **Socket Mode first** (works in the lab, zero inbound surface), Events API as
the second transport for deployments with ingress. The identity-link page is the exception: it needs a reachable HTTPS URL
for the browser (user-facing, not Slack-facing); in the lab it can be the same `*.hangar-dev.local` gateway route the Dex
login already uses ("Off here": no public TLS, so the Slack OIDC redirect URL must be an `https` URL Slack accepts; lab can
use a tunnel, enterprise uses its ingress. Note this is a hard Slack requirement for Sign in with Slack and may need a real
hostname even in the lab).

### 2.5 Secrets the owner creates (Infisical; we never create them)

| Secret | Used for |
|---|---|
| `clearance-slack-signing-secret` | Events/interactivity HMAC (Events transport only) |
| `clearance-slack-bot-token` (`xoxb-`) | post messages, open modals, DMs |
| `clearance-slack-app-token` (`xapp-`, `connections:write`) | Socket Mode |
| `clearance-slack-oidc-client-id` / `-secret` | Sign in with Slack (identity link) |
| IdP client for the link page (people-dex static client, public) | link flow login |
| DB DSN for the link/preference table (if not reusing an existing store) | links, prefs, message ts |

Never-persisted spirit: the bot token is service state by necessity (Slack has no mint-per-call); it is read from the mounted
secret on each use, never logged, rotated by the owner in Slack + Infisical. Clearance auth stays mint-per-call (projected SA
token).

---

## 3. Other surfaces (brief)

| Surface | State | Take |
|---|---|---|
| PR comment/check | The `clearance-gate-` check exists and shows holding/cleared with "who may clear". A hold-comment is documented as intent (`docs/gate.md` ~159) but `CLEARANCE_GITHUB_APP_COMMENTS` today covers agent failures only | Cheap: extend the GitHub App to post/update one comment "tier N, holding for <group>, link" per change. No actions in the comment. Do in P3 alongside Slack |
| Email digest | none | Low value vs. Slack; offer a daily digest of holding > 24 h and exceptions via the same notifier core (`clearance-slack` becomes `clearance-notify` with transports). Defer; SMTP creds are the owner's |
| Standalone web page (`clearance-web`) | the Clearance plugin is standalone-ready (`backstage: plugins/clearance`, `clearance-react`) but needs a Backstage host | **Not worth a new product now.** clearance-api is read-only and holds no sessions, so it should not serve a UI. If a non-Backstage UI is needed, host the existing React plugin in a minimal app shell (Backstage-free Vite app + OIDC PKCE direct to the core). The CLI + Slack link-outs cover step-up; the link-out target in non-Backstage deployments is then `clearance changes show --web` or this shell. Revisit after P4 |

---

## 4. Risks

| Risk | Mitigation |
|---|---|
| Slack becomes a weak approver path | Tier policy table (2.3), link-out step-up, `DG-*` still enforced by the core, `via` audit, identity re-verification, per-person revoke |
| Linked identity drift (person leaves, Slack account hijacked) | Link bound to team+user; unlink on deactivation events; 30-day re-verify; allowlist (`CLEARANCE_OIDC_ALLOWED_USERS`) still enforced at the core on the delegate-named person (to be confirmed: does the core apply the allowlist to a delegate-named user? G8) |
| Delegate is a confused deputy | Delegate only after a verified link; sends the IdP login, never a Slack-supplied string; per-call SA token; rate limits per user; no free-text principal |
| Token UX (1 h, no refresh) frustrates CLI users | Device flow is quick; optional agent daemon (D); longer-lived IdP session is the IdP's setting, not ours |
| Secrets in Slack messages | Only redacted views; never tool args (API never returns them anyway: `docs/clearance-api.md` ~l.374) |
| Slack outage = unseen holds | Slack is a surface, never a dependency: Tower/CLI/`clearance inbox` unchanged; stuck-hold digest at the 75 % TTL mark |
| Notification volume | Per-change threads, dedupe, transition-based alerts (same as `clearanceAlerts.ts`) |
| Lab constraints ("Off here") | No public ingress: Socket Mode; link page needs an https hostname (noted, not designed around); no Slack Enterprise Grid features assumed |

---

## 5. Phasing and API gaps

| Phase | Scope | Existing endpoints suffice? | Gaps (each a small Clearance change) |
|---|---|---|---|
| **P1: CLI read + auth** | `login/logout/whoami`, `changes list/show/history/wait`, `inbox`, `attest get/verify --change`, `exceptions list`, `coverage`, `evidence`, `watch`, table/json | Yes, except: | **G1** `GET /v1/clearances?awaiting=me` (server-side "can I clear", qualifies against the requirement); **G2** a `change=<id>` filter on `/v1/evidence` for history; **G9** CLI-friendly `GET /v1/whoami` (principal, roles, admin?) |
| **P2: CLI writes** | `changes clear/deny`, `exceptions resolve` (+bulk), `breakglass`, fresh-login rule | Yes (core routes) | **G3** server-side freshness: accept/require `auth_time`/`amr` and a max token age on tier >= 2 clears (also gives tier-3 step-up its real meaning); **G4** `via`/`client` field recorded on `deploy.clear/deny`, resolution, breakglass |
| **P3: Slack notify** | service, Socket Mode, per-change threads, DMs/channels, PR comment, coverage + exception alerts | Mostly (stream, coverage, exceptions) | **G5** machine reader of all `clearance` stream events/changes (extend `notifier`/`observer` to changes, redacted); **G6** attestation-stuck signal; **G7** group membership read for "who qualifies" and channel routing |
| **P4: Slack actions** | link flow, Clear/Deny/Resolve, tier policy, `via: slack` audit | Core routes yes | **G4** (above) + **G8** confirm the core applies `CLEARANCE_OIDC_ALLOWED_USERS` and admin checks to the delegate-named person (the Backstage path relies on it) |

Sizing, rough: P1 about a week, P2 about 3 days plus G3/G4, P3 about a week, P4 about a week. Each ships as a clearance
minor release then an Autopilot version bump (per the Clearance/Autopilot split).

---

## 6. Decisions for the owner

1. **One binary or two?** Recommend: **`clearance` subcommands** (+ `clr` alias); one signed artifact.
2. **CLI token storage.** Recommend: **OS keychain, ID token only, no refresh token, <= 1 h**; strict in-memory (`--token-stdin`) for automation; no disk files ever.
3. **IdP for people in production.** Recommend: keep **people-dex** for the lab; production uses the enterprise IdP (OIDC discovery, device-code enabled) behind the same `CLEARANCE_OIDC_*` config; no CLI change.
4. **Slack architecture.** Recommend: standalone **`clearance-slack` (Go, Clearance repo, delegate + observer)**, not in Autopilot's gateway.
5. **Transport.** Recommend: **Socket Mode first** (lab has no public ingress), Events API as second transport.
6. **Tier policy from Slack.** Recommend: **clear tier 2 and deny any tier in place; tier 3 clear and break-glass are link-out step-up**; loosening is per-deployment config.
7. **Server-side freshness (G3) before P4.** Recommend: **yes**, otherwise "step-up" is a client convention only.
8. **Audit field.** Recommend: add unverified **`via` + `surface_ref`** on person writes (G4), recorded as claimed, in the next evidence schema minor.
9. **Identity link store and Slack OIDC app.** Recommend: **Postgres table in the existing cluster DB** (ids only) and a **Sign in with Slack** app owned by you; you create the app and the Infisical secrets in 2.5.
10. **Email, PR comments, clearance-web.** Recommend: **PR comment in P3; email digest deferred; no clearance-web now** (revisit after P4 if non-Backstage deployments appear).

## 7. Owner decisions (2026-11-13)

Approved all, as recommended: 1 one binary (`clearance` + `clr`); 2 OS keychain, ID token only, no refresh token, <= 1 h, `--token-stdin` for automation; 3 people-dex in the lab, enterprise IdP via the same config; 4 standalone Go `clearance-slack` in the Clearance repo; 5 Socket Mode first; 6 Slack clears tier 2 and denies any tier in place, tier 3 clear and break-glass link out; 7 server-side freshness (G3) before P4; 8 `via` + `surface_ref` on person writes; 9 link store in the cluster Postgres, Sign in with Slack app owned by the owner; 10 PR comment in P3, email deferred, no clearance-web now (standalone UI under separate consideration).

Work package started: P1 (CLI read + auth; G1 awaiting-me filter, G9 whoami; change history uses `GET /v1/clearances/{id}/records` from the attestation API PR instead of G2).
