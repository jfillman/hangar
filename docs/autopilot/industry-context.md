# Industry context: the "agent substrate"

Reviewed 2026-09-26 against a third-party survey ("Agent substrate", kept outside the repo). The survey's own sources were not read; treat the vendor and project claims as leads to verify.

## The claim

Platforms are moving from "an LLM behind an app" to "give an agent a secure, persistent, observable computer plus governed tools". Kubernetes is gaining agent-specific primitives (the SIG Agent Sandbox and Google's Agent Substrate are named), and internal developer platforms are becoming platforms for humans and agents alike, with MCP as the agent-facing interface.

## Where Autopilot already matches

| Survey layer | Autopilot |
|---|---|
| Platform API for agents (`createApplication`, `deploy`, `getLogs`) | Airframe A+ contract, AppSpec, planner, `airframe.*` tools |
| Registry | `AgentDefinition` and its schema |
| Runtime and sandbox | `AgentRun` XR, `function-agentrun`, hardened sandbox profile |
| Identity | separate GitHub App (D4), Fulcio-signed commits (D1) |
| Permissions and policy | Clearance tiers, 19 CEL rules, narrow-only |
| Scheduler | scheduled and event shapes, trigger bridge |
| Agent-to-agent | team shape, run tree |
| Evaluation | Checkride |
| Observability, execution ledger | Flight recorder, hash-chained audit |

## Adopted from the survey

Stable agent identity, model version in the record, cost accounting, an evaluation of the upstream Agent Sandbox, optional resumable state, and a fixed T0 read set. See [design.md](design.md) 3.1 and the tasks AP-A4, AP-C1, AP-C2, AP-D1 and AF-2b in [roadmap.md](roadmap.md).

## Rejected, and why

- One large `AgentWorkspace` resource: widens authority by default and invites shell-level platform access from inside the sandbox.
- "Git is the agent context store" and "GitOps audits agent actions": true only for durable changes; reads, model calls and denied attempts never reach git, which is why the ephemeral plane and the audit chain exist.
- Agent memory as plain infrastructure: no treatment of poisoning or retention, so state is opt-in and guarded.
- The survey has no failure model (prompt injection, spend runaway, spawn storms); ours is [design.md](design.md) section 7.
