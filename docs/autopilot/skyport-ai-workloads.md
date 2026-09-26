# Skyport AI workloads: one agent per workload shape

Skyport already exercises every Airframe stack and component with five services and a broker
(`airframe/docs/user/skyport-demo.md`). This extends it with **six AI workloads, one per shape**, so
every part of Autopilot has a real caller, a visible effect, and a test that can fail.

The definitions are real and tested: `clearance/agents/skyport/*.yaml` (nine files: six workloads and
three team members), with one Checkride case each in `clearance/checkride/cases/skyport-*.yaml`.

Status: definitions and cases **Built**. Everything that would run them is **Proposal** until
Autopilot phase A and B exist (see `roadmap.md`).

## The six workloads

| Shape | Agent | Trigger | What it does | Skyport touchpoints | Checkride verifier |
|---|---|---|---|---|---|
| Task | `flight-briefer` | a person or API asks | Ops brief for one flight from three APIs | reads flight-api, boarding-api, baggage-api | every fact matches the API fixture; no invented flight |
| Session | `gate-copilot` | a gate agent opens a chat in Tower | Answers questions, drafts announcements | reads flight-api; approvals in Tower | scripted chat; a draft is never sent |
| Service | `passenger-assistant` | always on, HTTP | Public flight-status chat | boarding-api, flight-api, Redis | golden Q&A, plus an injected instruction that must not be followed |
| Scheduled | `delay-digest` | every 24 hours | Daily delays and gate-change report | flight-api history; the artifact store | counts equal the event log; a second run changes nothing |
| Event | `disruption-responder` | `flight.*.delayed` on the broker | Drafts rebooking notices, never sends | broker consumer, Clearance | one run per unique event; a redelivery starts none |
| Team | `irregular-ops-team` | spawned by the responder | Planner with researcher, drafter, checker | all three APIs, narrowed | child budgets sum within the root; an over-broad spawn is denied |

Diagram: `diagrams/plan/07-skyport-ai-workloads.html`. The event and team flow:
`diagrams/plan/08-skyport-event-to-team.html`.

### Why these six
They are business-domain agents, so the demo shows agents *operating a system*, not only agents
operating the platform. The platform-facing agents already exist or are planned: HolmesGPT is the
event and service shape for triage (`diagrams/autopilot/17-triage-before-after.html`), and the coding
agent is the delegated task shape for platform work (the parachute test).

### A deliberate rule: nothing here applies a change
No Skyport agent has a write tool. They read, they draft, they store artifacts, they ask a human, and
they spawn narrower runs. Anything consequential goes through `human.request`. A test asserts it:
`test_nothing_in_the_demo_can_apply_a_change_except_by_spawning_narrower_runs`. The demo shows what
"humans on the loop" looks like without the demo being able to break Skyport.

## What each needs that does not exist yet

| Piece | Needed by | Status |
|---|---|---|
| Clearance core, sessions, policy, audit | all | **Built** (255 tests) |
| `AgentRun` XRD, composition function, `provider-kubernetes` grants | task, session, scheduled, event, team | **Draft**, never applied |
| Model proxy (HTTP forwarder), hosted model route, key in Infisical | all | decision core **Built**; forwarder **Proposal** |
| Read tool `app.api.get` (allowlisted service APIs) | all | **Built** (policy and tests); real adapter **Proposal** |
| Artifact tools `artifact.put` and `artifact.get` | task, scheduled, team | **Built**; MinIO adapter **Proposal** |
| Session channel `chat.recv` and `chat.send`, and Tower's chat UI | session | tools **Built**; Tower **Proposal** |
| Trigger runner (interval) | scheduled | logic **Built** (`due`); runner **Proposal** |
| **Trigger bridge** (broker to `open_triggered`) | event | design below; **Proposal** |
| Chart `agent:` block (tokens, egress, contract) | service | **Proposal** (Airframe AF-10) |
| `event` trigger type in the definition schema | event | **Built** |
| Tower Agent tab: runs, audit, approvals | session, event, team | **Proposal** |
| Skyport APIs, broker, `baggage-api`, MongoDB | task, session, service, digest, responder, team | broker, flight-api, boarding-api **Built**; baggage-api and MongoDB next |

## The trigger bridge (event shape)
An ordinary Airframe `PythonApplication` with a RabbitMQ **attach** consumer, so the demo also
exercises the component it depends on. It:

1. binds a queue `ai.disruption` to `flights.events` with `flight.*.delayed` (the definition's `bindingKey`);
2. for each message, derives `task_id = event_task_id(agent, message_id)` so **redelivery maps to the same run** (RabbitMQ is at-least-once);
3. applies the definition's `maxPerHour` as a **storm brake** (a delayed-flights storm must not start a thousand runs);
4. calls Clearance `open_triggered` as its own workload identity, then `launch`;
5. acks only after the audit record exists; malformed messages are rejected and audited, not dropped.

It holds no model key and no repo credential. Its authority is "may start this one definition".
Tested pieces: `amqp_topic_match`, `match_event`, `event_task_id`, `RateLimiter`, idempotent
`open_triggered`. The consumer itself is the build work.

## The session channel (session shape)
Runs have no inbound network by policy, so Tower cannot connect to a `gate-copilot` pod. Instead
Clearance holds a per-session message queue: Tower posts the human's message to Clearance, the agent
calls `chat.recv` (long-poll) and `chat.send`. The sandbox only ever dials out. Those two tools exist
only for `kind: session` (rule R018).

## The service agent (service shape)
`passenger-assistant` is an application: `PythonApplication` plus a Redis component, deployed and
released like `baggage-api`, with the chart's `agent:` block giving its pods the same tokens, egress
policy and labels a run gets. It is the only workload facing the public, so its definition asks for the
**hardened** sandbox.

**That fails closed on the dev cluster, by design.** kind and Apple `container` have no gVisor or Kata
runtime class, so the chart (and `function-agentrun`) reject it rather than run it weaker. To run the
demo on `kiac-dev`, change the definition to `standard` in a reviewed commit and record why. A run can
narrow a definition but never widen it, so lowering isolation is only ever a commit. That moment is
worth a paragraph in the quickstart.

## Safety demonstrations built into the demo

| Demonstration | Where | What it proves |
|---|---|---|
| **Prompt injection** | the passenger-assistant fixture has a flight-remarks field telling the model to reveal credentials and call a forbidden tool | tool output is data; the assistant has no tool that could comply; a tripwire attempt would end the session |
| **Redelivered event** | responder fixture delivers one message twice | idempotent `task_id`, no second run |
| **Event storm** | responder fixture floods `flight.*.delayed` | `maxPerHour` brake |
| **Over-broad spawn** | team fixture instructs a worker to ask for more than its parent has | narrow-only, denied with R007 and audited |
| **Wrong fact** | team fixture puts a wrong gate in a draft | the checker worker catches it against the API |
| **Fail-closed sandbox** | passenger-assistant on kiac-dev | a hardened request is Rejected, never downgraded |
| **Expiry without Clearance** | stop Clearance mid-run | the run still ends at `expiresAt` |

## Quickstart parts (numbered in the order built)

| Part | Adds | Depends on |
|---|---|---|
| 4 | `baggage-api` (Python) + MongoDB, consuming flight events | MongoDB component (born A+) |
| 5 | `skyport-auth` (OAuth) and enforced JWTs | OAuth component (born A+) |
| 6 | **Your first agent: `flight-briefer`** (task) | Autopilot phase A and B, model proxy v0 |
| 7 | **`gate-copilot`** (session) | session channel, Tower Agent tab |
| 8 | **`passenger-assistant`** (service) | chart `agent:` block, the hardened-sandbox moment |
| 9 | **`delay-digest`** (scheduled) | trigger runner, artifact store |
| 10 | **`disruption-responder`** (event) | trigger bridge |
| 11 | **`irregular-ops-team`** (team) | `run.spawn`, approvals |
| 12 | *(optional)* nginx edge | nginx component |

The existing part 3 (broker) is done. Parts 4 and 5 are the existing Skyport phases 3 and 4; the AI
parts slot in after them because the agents read `baggage-api`. Each part follows the house rule:
**walk it live before it is called done**, and the quickstart's verified-state note says exactly what was walked.

## Where the code lives (proposed)
```
airframe/examples/skyport/
  flight-api/  boarding-api/  baggage-api/        # existing and next
  agents/
    flight-briefer/  gate-copilot/  passenger-assistant/  delay-digest/
    disruption-responder/  irregular-ops-team/  ops-researcher/  ops-drafter/  ops-checker/
    trigger-bridge/                               # an ordinary Airframe app
    fixtures/                                     # API fixtures, event streams, the injection text
autopilot/ (new repo; today ~/tech/clearance)
  agents/skyport/*.yaml   checkride/cases/skyport-*.yaml
```
Definitions stay next to Clearance because they are policy, reviewed as policy. The agent *code*
lives with the demo because it is an example, versioned with the Airframe it exercises.

## Cost control
A hosted model is the default. Every run has a token budget (`modelTokens`), the model proxy
enforces it and trips the breaker on overrun, and `delay-digest` and `flight-briefer` are the only
scheduled or on-demand spenders. A Modelplane hub is a later trial (M5), not a demo dependency.

## Acceptance for the whole extension
1. Each agent runs end to end on the dev cluster and its Checkride case passes.
2. Each case's seeded bad run fails (the harness can say no).
3. `kubectl` shows no run namespace older than its `expiresAt`, with Clearance stopped.
4. One `task_id` traces a disruption from broker message to the team's final artifact in the Flight recorder.
5. The scorecard has not regressed.
