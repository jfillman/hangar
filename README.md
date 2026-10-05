<div align="center">
  <img src="docs/brand/hangar-tile.svg" width="88" height="88" alt="Hangar mark" />
  <h1>Hangar</h1>
  <p><i>Home base for building, releasing, and watching every service you run.</i></p>
</div>

An API-centric, event-driven Internal Developer Platform: Crossplane as the custom
control plane, ArgoCD/GitOps for delivery, Backstage as the single pane of glass,
Glidepath (`../glidepath`) as the CI/CD component underneath it. AI-assisted at
two levels — API clients driving self-service provisioning, and workflows embedded at
the control-plane layer for things like automated triage of a degraded deployment.

## Status

Design resolved (`docs/gitops-strategy.md`, `docs/service-catalog-design.md`), build
started 2026-08-12/13.

### 2026-09-27: Architecture review

A staff-architect review of the whole platform: **conditional approval**. The architecture is approved and a pilot
is worth funding; production waits on five gates (prod independent of the dev cluster, a GitHub organization and
SSO, authorization on Tower's write actions, a tested restore, admission-time signature checks). Rich page:
[`docs/reviews/2026-09-27-architecture-review.html`](docs/reviews/2026-09-27-architecture-review.html), also at
`/review/` on the site.

### 2026-09-26: Autopilot, the Airframe A+ program, and Skyport AI workloads

Hangar gains a sixth product, **Autopilot**: it runs any AI agent workload (task, session, service,
scheduled, event, team), bounded and audited, and it drives a program to make Airframe operable by
agents (measured by [`tools/airframe-scorecard`](tools/airframe-scorecard/): baseline 27/100, A+ needs
97 and 14 of 14 checks). Skyport gains six AI workloads, one per shape. The design principle:
**durable changes are git commits; ephemeral runs are direct requests to Crossplane.** Start at
[`docs/autopilot/README.md`](docs/autopilot/README.md); the plan is [`docs/autopilot/roadmap.md`](docs/autopilot/roadmap.md).
Built so far, with 255 passing tests and no cluster: the Clearance core, the AppSpec planner (the
"parachute" acceptance test: one plain-language request to provision a Python app named parachute, end to end), nine Skyport agent definitions and six Preflight cases. Drafted, never
applied: the `AgentRun` XRD and its composition function. Nothing is committed yet.

## Repos

```
hangar                      this repo — docs + running status (was "idp")
glidepath                   the CI/CD engine (was "platform-cicd")
tower                       the Backstage plugin that handles release orchestration and operational intelligence
airframe                    Crossplane XRDs/Compositions + the airframe-application chart, tagged v0.1.0, pinned+synced via ArgoCD (was "idp-service-catalog")
apron                       gold-standard template for provisioning a new cluster repo - docs/cluster-provisioning.md (was "gitops-cluster-template")
autopilot                   AI agent workloads: Clearance, AgentRun, planner (proposed repo; code is ~/tech/autopilot today) - docs/autopilot/
```

## Repo layout (so far)

```
docs/   design docs, written as decisions land — same convention as glidepath/docs/
web/    the website (hangarplatform.dev): Astro, built from docs/ and brand/ — see web/README.md
```

## Design language

Shares Glidepath's conventions rather than inventing new ones: `hangar.io/*`
label namespace, `<type>-<app-name>-<env>` namespace pattern,
kebab-case docs, the "never a live cross-cluster API call, only a git commit" credential
posture. Deviations get called out explicitly where they happen, not silently.

The deeper design docs below (`gitops-strategy.md`, `service-catalog-design.md`,
`backstage-design.md`, `cluster-provisioning.md`, `local-clusters.md`) are dated design
narrative and still refer to components by their pre-rebrand names (`platform-cicd`,
`idp-service-catalog`, `gitops-cluster-template`) throughout — that's intentional, not
stale: they're a historical record of decisions as they were made, and a global rename
would misdate them. Renaming those references is in scope for the later docs
reorg/rebrand pass, not this one.
