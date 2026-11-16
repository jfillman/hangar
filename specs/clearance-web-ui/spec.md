---
title: Clearance standalone web UI: spec
program: Hangar · Clearance web UI
board: https://claude.ai/artifact/7bptZqWD7RdUDxyR4TQ8o9
source: https://claude.ai/artifact/Pwcu1AUxEAiLeokrrs4498
updated: 2026-11-16
---

Nov 13, 2026 · James

## Summary and schedule {#summary}

Clearance gets its own web UI, `clearance-web`, that runs in `clearance-system` and shows the same views as the Backstage plugin, so an organization without Backstage can still use Clearance. One UI codebase serves both hosts; nothing is forked.

- **Goal:** every person-facing Clearance view (Clearances, Evidence, Exceptions, Policy, Map, Attestations) available in a browser with only Clearance installed.
- **Non-goals:** no new policy or decisions in the web tier; no Tower-only views (the per-app Tower tab, the catalog); no replacement for the CLI or Slack (they share the same API).
- **Schedule:** starts when the Backstage plugin updates in flight are merged and released: the tier legend (backstage#267, merged), the Map tab and environment detail, and the change detail with attestations (boards C5-C13). Estimate: about 1.5 to 2 weeks.
- **Why after:** the plugin's views are still changing; extracting them now means moving a target. The first work package (the transport interface) is small and can be pulled forward if the Map UI has not started.

## Today: the Backstage plugin barely touches Backstage {#today}

The plugin was built standalone-ready (no Tower imports), so the Backstage coupling sits in four places.

| Package | Backstage use | Standalone answer |
| --- | --- | --- |
| `plugins/clearance-react` (the kit) | `read.ts` and `write.ts` take `discoveryApiRef` + `fetchApiRef` to reach `/api/clearance` | a transport interface set by a React context |
| `plugins/clearance` (views, about 4.9k lines with the kit) | `useEntity` in `EntityClearanceContent` (the Tower tab); plugin and route registration | the tab stays Backstage-only; the pages mount in a shell |
| Theme | MUI v4 under Backstage's theme, Tower tokens via the kit | a MUI ThemeProvider with the same tokens |
| `plugins/clearance-backend` | the person from the Backstage session; proxy to clearance-api, the core and the gateway; scope discovery; the alerts poller | the Go backend-for-frontend; alerts move to `clearance-slack` (CLI/Slack P3) |

The views call only Clearance's HTTP API, so their data needs nothing new.

## Design {#design}

The views move into one package that both hosts mount; the web host adds a small Go server that only signs people in and forwards their requests.

> Diagram: clearance-web architecture · one UI package, two hosts. See the original document.

1. **Shared UI package.** `plugins/clearance-react` and the views of `plugins/clearance` move to the Clearance repo as `@jfillman/clearance-ui`, tagged with Clearance releases. Backstage pins it by git tag, as it does Tower. The kit's `read.ts`/`write.ts` call a `ClearanceTransport` (`get(path)`, `post(path, body)`, `stream(path)`) from a React context; Backstage supplies discovery + fetch, the web shell supplies same-origin fetch.
2. **Shell app.** A Vite build of the same pages with a top nav, client-side routing, an app picker in place of the catalog, and a MUI ThemeProvider carrying the Tower tokens (dark and light).
3. **Go server (`clearance web`, a subcommand of the one binary).** Serves the bundle from `embed.FS`; signs people in with OIDC authorization code + PKCE; holds sessions in memory only (lost on restart = sign in again); forwards `/api/read/*` to clearance-api and `/api/write/*` to the core (and the gateway for agent controls) with the person's own ID token as the bearer. No delegate, no policy, no caching of answers.
4. **Deployment.** In the Clearance Helm chart behind `web.enabled` (off by default); one Deployment, Service and HTTPRoute (`clearance.<domain>/`), a NetworkPolicy allowing egress only to the IdP, clearance-api, the core and the gateway. Apron turns it on per cluster.
5. **Alerts.** The Backstage alerts poller has no equivalent here; alerts go out through `clearance-slack` (CLI/Slack phase 3). The web UI shows the same banners from live reads.

## Security model and guardrails {#security}

The web tier adds no authority: Clearance decides and records every action exactly as it does for the CLI, with the person as the caller.

- **Identity:** the person's own ID token from the people IdP is the bearer on every forwarded call; Clearance's existing OIDC allowlist, roles and the gate's who-may-clear rules apply unchanged. No delegate principal and no Clearance credential held for people.
- **Sessions:** server memory only, never written to disk or a database; token lifetime capped at 1 h (the CLI's rule); sign-out clears it. Restart = sign in again.
- **Cookies and requests:** `__Host-` cookie, HttpOnly, Secure, SameSite=Strict; CSRF token on every write; strict CSP (self only, no inline script), `frame-ancestors 'none'`.
- **Step-up:** writes that need a fresh login (tier 3 clear, break-glass) rely on the core's server-side freshness check (CLI/Slack decision 7); the web tier sends the person through a fresh login when the core asks. This page also serves Slack's link-out for those actions.
- **Records:** person writes carry `via: web` (CLI/Slack decision 8).
- **Network:** egress only to the IdP, clearance-api, the core and the gateway; no other outbound call.
- **Off by default:** `web.enabled: false` in the chart; a cluster opts in through apron.

## Work packages {#work-packages}

Five packages in order; each ends in a merged PR with its checks green.

### WEB-1 · Transport interface in the kit; Backstage supplies discovery + fetch

**Repo.** backstage

**Done when.** every view reads and writes through `ClearanceTransport`; plugin behaviour unchanged (tests, tsc, a Tower smoke check)

**Est.** 1-2 d

### WEB-2 · Move the kit + views to the Clearance repo as `@jfillman/clearance-ui`; Backstage pins it by tag

**Repo.** clearance, backstage

**Done when.** Backstage builds from the tag; no copy of the views left in backstage; the package has no Backstage import outside an adapter

**Est.** 2 d

### WEB-3 · Shell app: Vite build, router, nav, app picker, ThemeProvider with Tower tokens

**Repo.** clearance

**Done when.** every page renders against a fake transport; light and dark; phone width

**Est.** 2 d

### WEB-4 · `clearance web` Go server: embed, OIDC code + PKCE, in-memory sessions, forwarding, CSRF, CSP

**Repo.** clearance

**Done when.** sign-in, a read and a clear work end to end against a test core; a session never touches disk; fuzz and race tests pass

**Est.** 3 d

### WEB-5 · Chart (`web.enabled`), HTTPRoute, NetworkPolicy; apron toggle; hangar-dev rollout

**Repo.** clearance, apron

**Done when.** the web UI serves on hangar-dev; a person clears a change there; the record shows `via: web`

**Est.** 1-2 d

Prerequisites: the Backstage plugin work (tier legend, Map, change detail and attestations) merged and released; CLI/Slack phase 2's freshness check (G3) and `via` field (G4) for the step-up and audit rows.

## Owner steps, risks, open decisions {#owner-risks-decisions}

- **Owner steps:** create a confidential OIDC client for `clearance-web` in people-dex and put its secret in Infisical (one-time); approve the hangar-dev rollout.
- **Risk, two hosts drift:** a Backstage-only change slips back into the views. Guard: WEB-2's rule that only the adapter imports Backstage, checked by a lint rule.
- **Risk, sessions lost on restart:** accepted (in-memory by design); one replica, or sticky sessions if scaled.
- **Open decision 1:** host path. Recommend `clearance.<domain>/` for the UI with the API paths unchanged.
- **Open decision 2:** whether the web server also polls for alerts when `clearance-slack` is off. Recommend no; banners on the pages cover it.
