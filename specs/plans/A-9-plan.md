# A-9: the Autopilot gateway in Go — plan for the rest of the port

Written 2026-11-14. Repo: jfillman/autopilot. Reference: `docs/admin/go-gateway.md` (what the first slice carries and
what is left), spec card "A-9 · The gateway in Go".

## Where it stands

- First slice merged 2026-11-09 (autopilot#82): MCP on the Go SDK, decisions/outcomes through Clearance's Go client,
  sessions in the same database, streaming model proxy, `metrics.query` / `logs.query`. Replay, conformance and the
  load-test bar pass. Off by default, no image published.
- Go: ~7.1k lines (with tests). Python gateway: ~12.7k lines (`src/autopilot` 7.7k + `engine/` 5.1k).
- Python has moved since the slice: 1,610 lines added across 50 files (A-11 propose scope, R-10 naming, backend error
  detail, `airframe_apply.py` new). `engine/dispatch.py` alone changed by 228 lines, so the ported hot path is behind.

## Done when (the card)

1. Replay corpus: identical decisions and record fields through the Go gateway.
2. Conformance harness passes.
3. Own p99 overhead per tool call under 5 ms at 200 sessions.
4. A canary agent definition runs on the Go gateway on hangar-dev for 7 days with no divergence in its records.
5. Every definition moves; the Python gateway is removed.

1-3 hold for the first slice and must keep holding as each slice lands. 4-5 need a deployment.

## Slices (code only, one PR each, Python stays the reference until cutover)

| # | Slice | Python source | Unlocks |
|---|---|---|---|
| S0 | Catch-up: bring the ported hot path level with Python as of main | `engine/dispatch.py`, `core.py`, `session.py`, `results.py`, `backends.py`, `server.py` diffs since 366442a | a true baseline; a drift guard so it cannot fall behind silently again |
| S1 | Authentication: people OIDC (Dex), GitHub Actions, foreign-cluster workloads | `engine/auth.py` | people and Tower can reach it |
| S2 | Runs: RunBackend (AgentRun XRs), `run.spawn`/`run.close`, `launch`, `run_finish`, `session_close`, `acting_as`, sweep's run deletion and backstop outcomes, results and artifacts | `kube_runs.py`, `agent_xrs.py`, `xr_request.py`, `engine/results.py`, `runtimes.py`, dispatch run paths | 43 skipped corpus lines; the gateway can serve an agent run |
| S3 | People and triggers: human inbox, person controls (freeze, end, hold, release, `run_agent`), trigger scheduler, event bridge, reconcile sweep, trigger ledger, `open_triggered` | `engine/inbox.py`, `control.py`, `events.py`, `trigger_ledger.py`, `scheduler.py`, `triggers.py`, `event_bridge.py`, `reconcile.py` | 31 skipped corpus lines |
| S4 | Definitions: publish the set to the core (`PUT /v1/definitions`), Agent XR loader, JSON-schema validation | `engine/definitions.py`, `profile.py`, `agent_xrs.py` | the Go gateway can own the definition set |
| S5a | Read backends: `catalog.read`, `argo.app.get`, `app.api.get`, `artifact.*` | `backends.py`, `hangar_tools.py` | |
| S5b | Glidepath and repo tools: `glidepath.*`, `repo.*`, `argo.sync.lower`, `cicd_propose` | `glidepath_api.py`, `glidepath_live.py`, `github_pr.py`, `argo_sync.py`, `cicd_propose.py` | |
| S5c | Airframe tools: `airframe.*`, `xr.request`, plan, apply, preflight | `airframe_*.py`, `preflight.py`, `xr_request.py` | the largest single piece (~2k lines) |
| S6 | `api` subcommand (the read API), Prometheus metrics, OTLP logs | `api_serve.py`, `read_api.py`, `reads.py`, `metrics.py`, `otlp_logs.py` | autopilot-api can be Go too |
| S7 | Release plumbing: image workflow and tag for the Go image, apron switch (off by default), `serve` stops refusing the settings it now carries | workflows, apron `55-autopilot` | a deployable image |
| S8 | Canary: 7 days on a deployed cluster, record comparison | | card item 4 |
| S9 | Cutover: every definition moves, Python gateway and its image workflow removed | | card item 5 |

Order: S0 first. S1 can run beside it. S2 follows S0 (both touch dispatch) and is the critical path: nothing can canary
without runs. S3 and S4 follow S2. S5a/b/c and S6 are independent of each other and can run two at a time.

## How each slice is proven

- Equivalence tests against the Python implementation for the slice's surface (same inputs, same outputs, same record
  fields), in the style of `gateway/internal/replay` and `tests/test_gateway_go.py`.
- The replay's skip list shrinks as S2 and S3 land; skipped lines are never silently dropped.
- An independent security review before merge for S1 (auth), S2 (run identity), S5b/S5c (write paths), S6 (read API).
- PR Lens findings read and applied on every PR.

## Owner decisions, 2026-11-14

1. **Canary placement.** EKS dev, own Deployment and database, if EKS is ready when the canary is. If it is not, there
   is no canary: a hard cutover on hangar-dev (the Go gateway replaces the Python one on the same database). Card item 4
   (7 days, no divergence) is then replaced by: the full replay and conformance run against the release image before the
   switch, a record comparison for the first runs after it, and the Python image kept for rollback.
2. **Drift while porting.** CI guard in place since S0.
3. **autopilot-api.** Port it before cutover (S6).
