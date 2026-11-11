# Industry context: the "agent substrate"

Reviewed 2026-09-26 against a third-party survey ("Agent substrate", kept outside the repo). The survey's own sources were not read; treat the vendor and project claims as leads to verify.

## The claim

Platforms are moving from "an LLM behind an app" to "give an agent a secure, persistent, observable computer plus governed tools". Kubernetes is gaining agent-specific primitives (the SIG Agent Sandbox and Google's Agent Substrate are named), and internal developer platforms are becoming platforms for humans and agents alike, with MCP as the agent-facing interface.

## Update 2026-11-10: Google's stack moves to the CNCF

Read first-hand ([The New Stack, 2026-11-06](https://thenewstack.io/gvisor-cncf-kubernetes-open-source/)): Google is donating gVisor, Agent Substrate and OpenRL to the CNCF. Agent Substrate 1.0 is GA on GKE.

| Project | What it is | For Autopilot |
|---|---|---|
| gVisor | user-space kernel that intercepts a sandboxed pod's syscalls; used by Anthropic and OpenAI for untrusted code | **adopted** as the `hardened` runtime class (eks-dev `sandbox` node group, Apron `autopilot.hardenedRuntime`; [design.md](design.md) section 3). Neutral governance removes the single-vendor risk. Caveat from the article: Google's I/O patches are not in mainline Linux, so off-GKE gVisor is slower on I/O-heavy work. Measure before defaulting to it |
| Agent Substrate | a runtime layer on Kubernetes that suspends idle agents and resumes them without new pods, state kept apart from compute; gVisor is one isolation option | **watch**. The upstream Agent Sandbox (kubernetes-sigs, v1.0.8, already pinned) covers what U11 measured: suspend/resume, warm pools, a hard deadline. Substrate is GKE-only GA and Hangar targets EKS. Revisit once it is in the CNCF and runs off GKE |
| OpenRL | reinforcement-learning fine-tuning on your own Kubernetes | out of scope |

The article also cites models in a July OpenAI cyber evaluation escaping their environment and reaching Hugging Face's production infrastructure. That is the case for `hardened`: Clearance governs every call a run makes, but only the runtime contains a kernel exploit.

## Where Autopilot already matches

| Survey layer | Autopilot |
|---|---|
| Platform API for agents (`createApplication`, `deploy`, `getLogs`) | Airframe A+ contract, AppSpec, planner, `airframe.*` tools |
| Registry | `AgentDefinition` and its schema |
| Runtime and sandbox | `AgentRun` XR, `function-agentrun`, Agent Sandbox controller, hardened profile on gVisor |
| Identity | separate GitHub App (D4), Fulcio-signed commits (D1) |
| Permissions and policy | Clearance tiers, 19 CEL rules, narrow-only |
| Scheduler | scheduled and event shapes, trigger bridge |
| Agent-to-agent | team shape, run tree |
| Evaluation | Preflight |
| Observability, execution ledger | Flight recorder, hash-chained audit |

## Adopted from the survey

Stable agent identity, model version in the record, cost accounting, an evaluation of the upstream Agent Sandbox, optional resumable state, and a fixed T0 read set. See [design.md](design.md) 3.1 and the tasks AP-A4, AP-C1, AP-C2, AP-D1 and AF-2b in [roadmap.md](roadmap.md).

## Rejected, and why

- One large `AgentWorkspace` resource: widens authority by default and invites shell-level platform access from inside the sandbox.
- "Git is the agent context store" and "GitOps audits agent actions": true only for durable changes; reads, model calls and denied attempts never reach git, which is why the ephemeral plane and the audit chain exist.
- Agent memory as plain infrastructure: no treatment of poisoning or retention, so state is opt-in and guarded.
- The survey has no failure model (prompt injection, spend runaway, spawn storms); ours is [design.md](design.md) section 7.
