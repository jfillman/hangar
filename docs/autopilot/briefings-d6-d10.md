# Briefings for D6 and D10

Plain-language context so you can decide. Each has options and a recommendation. Written 2026-09-26.

---

## D10: When does the strict schema start rejecting typos?

### What is being decided
Today the chart's `values.schema.json` accepts unknown keys. Write `rolout:` or `replcas: 3` and the chart
ignores it, silently. For an AI agent that is the worst failure: the change looks accepted and does nothing.
`airframe validate` (built in M0, `airframe/tools/airframe-validate`) closes every object that lists its
properties, so those typos fail with a hint (`did you mean 'rollout'?`). The question is only **when a
failure becomes blocking** rather than a warning.

### What we measured (2026-09-26)
- The strict schema closes 46 objects. Passthrough objects (`podSpec`, `extraManifests` items) stay open.
- Every live file passes it: both Ground env files (`boarding-api`, `flight-api`) and both Flight values files
  (`boarding-api` and `flight-api` on kind-prod staging). **Zero violations, so the fleet sweep is already clean.**
- It catches the three test typos: `rolout:`, `replcas:`, and `size: gigantic` on a component (the last needs the
  XRD schema, which validate now reads).

### Options
| Option | What happens | Risk |
|---|---|---|
| **A. Enforce now** | `airframe validate` is a required check on PRs to env files from day one | Almost none today (0 violations). A future legitimate key the schema forgot would block a PR until the schema is fixed, which is a small, visible fix. |
| **B. Warn through M1, enforce at the end of M1** (the roadmap default, about 2026-10-23) | Failures are reported but do not block for about four weeks | New apps (baggage-api, MongoDB and OAuth components) can pick up typos in the meantime, which is the thing we are trying to prevent. |
| **C. Enforce only on agent-authored PRs** | Agents are held to the strict schema; humans get warnings | Two standards, and the human path stays typo-prone. |

### Recommendation: A for the agent path and new files, B's warning for nothing else
Because the sweep is clean and there are only four live files, the reason to warn (a surprise breaking an
existing environment) mostly does not exist. Enforce now. If a real environment is ever broken by it, the escape
hatch is a one-line schema change, not a rollback. Choose B only if you expect other people's apps to land in the
next month.

**Decision needed:** A, B or C.

---

## D6: Where does the model hub live, and how isolated is it?

### What is being decided
Autopilot can send agent model calls to hosted providers (works today in design) or, later, to models you run
yourself through **Modelplane** (a Crossplane-native system that manages inference clusters). Modelplane's
"hub" is a control cluster that creates and reconciles those inference clusters, so it **holds their
credentials**, and to provision them it may need broad cloud permissions. That breaks a Hangar rule: no cluster
holds another cluster's credentials.

This does not need answering until M5. Nothing in M0 to M4 depends on it.

### Options
| Option | What it means | Trade-off |
|---|---|---|
| **1. Hosted providers only, no hub** | Skip self-hosting. Model calls go through Clearance's model proxy to a hosted API. | Nothing new to secure; no self-hosted models. |
| **2. One hub per environment, dedicated accounts** (the current design) | A dev hub never holds prod credentials. Inference clusters are dedicated, hold no app data, agent data or Hangar secrets, and the hub prefers pre-built clusters so it only holds a kubeconfig, not cloud admin. | Most isolated; more clusters to run; a persisted kubeconfig Secret remains (delivered by External Secrets, never in git). |
| **3. One shared hub for all environments** | One hub reconciles every inference cluster. | Simplest; one compromise reaches every environment's inference credentials. |

### Recommendation
Decide **option 1 now** (it is already the plan: "hosted providers first") and revisit option 2 when M5 starts
and you know whether self-hosted models are worth a second cluster. Avoid option 3. Two things to check before
choosing option 2, both listed in `roadmap.md` as U10: whether Modelplane's short-lived cloud auth works for
pre-built clusters (which would remove the persisted kubeconfig), and what its usage records contain.

**Decision needed:** confirm option 1 for now, with option 2 as the M5 default.
