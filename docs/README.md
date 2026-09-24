<div align="center">
  <img src="brand/hangar-tile.svg" width="88" height="88" alt="Hangar mark" />
  <h1>Hangar</h1>
  <p><i>Home base for building, releasing, and watching every service you run.</i></p>
</div>

# Documentation

The table of contents for the whole Hangar platform — Hangar itself, Airframe
(the service catalog), Glidepath (CI/CD), Tower (the Backstage UI), and Apron
(the cluster template). Available two ways: browsable here across each repo's own
`docs/`, and through **Tower's TechDocs tab** once a component's `catalog-info.yaml`
is registered in the catalog (Airframe and Glidepath are wired as of 2026-09-21;
Tower/backstage and Apron are not yet — see [Open items](#open-items)).

**Convention going forward:** every new illustrated doc/artifact this project
produces gets a line added to the relevant section below, at the time it's
created — not batched up later.

## Start here

| Doc | Read this when... |
|---|---|
| [service-catalog-design.md](service-catalog-design.md) | You want the full design history and open decisions behind Airframe — the running log, not the as-built summary. |
| [gitops-strategy.md](gitops-strategy.md) | You want the repo topology, ArgoCD instance split, and the lower/upper env security boundary. |
| [cluster-provisioning.md](cluster-provisioning.md) | You're standing up a new cluster. |
| [kind-prod-infisical-migration-plan.md](kind-prod-infisical-migration-plan.md) | You're moving kind-prod onto the new airframe pin and retiring the Infisical operator (plan, not yet executed). |
| [local-clusters.md](local-clusters.md) | You're running clusters locally and need the real operational notes. |
| [backstage-design.md](backstage-design.md) | You want Tower's own design rationale — self-service flows, the terasky ingestor, catalog structure. |

## Airframe — the service catalog

Developer- and admin-facing docs live in the `airframe` repo itself.

| Doc | Read this when... |
|---|---|
| [airframe/docs/user/README.md](https://github.com/jfillman/airframe/blob/main/docs/user/README.md) | You're creating a service, adding ground/flight environments, or attaching a component. |
| [airframe/docs/user/quickstart.md](https://github.com/jfillman/airframe/blob/main/docs/user/quickstart.md) | You want the full worked example — `boarding-api` (NodeJS): pull in the code, both env tiers, a Redis cache, a canary. |
| [airframe/docs/user/skyport-demo.md](https://github.com/jfillman/airframe/blob/main/docs/user/skyport-demo.md) | You want the plan for the five-service Skyport demo system that exercises every stack and component, and where its code lives. |
| [airframe/docs/user/decommission-app.md](https://github.com/jfillman/airframe/blob/main/docs/user/decommission-app.md) | You need to delete/decommission an app: what gets destroyed (both GitHub repos), the git-driven order of operations, and the ArgoCD ordering bug. Proven once on boarding-api. |
| [airframe/docs/admin/architecture.md](https://github.com/jfillman/airframe/blob/main/docs/admin/architecture.md) | You want the as-built reference — every XRD's inputs/outputs, the composition graph, the plumbing. |

*(Local checkout note: since this repo and `airframe` are cloned as siblings on
this machine, `../../airframe/docs/...` also resolves locally — the links above
use full GitHub URLs instead because this page is also built by TechDocs, which
renders each repo's docs in isolation and can't follow a relative link across a
repo boundary.)*

**Illustrated / interactive:**

| Doc | Status | Read this when... |
|---|---|---|
| [Airframe Service Catalog](https://claude.ai/artifact/TBhiiN1TPjAbiwTTcctnK2) | current | You want the architecture reference with real diagrams — same content as `admin/architecture.md`. |
| [Airframe Quickstart](https://claude.ai/artifact/WDPmWSD9BMBGurFzqATDWG) | **stale, 2026-09-23** | The illustrated walkthrough still follows the earlier Go version of `boarding-api`; `quickstart.md` now uses NodeJS and adds code pull-in and a canary. Trust the markdown until this is republished. |
| [Hangar Service Catalog](https://claude.ai/artifact/8tS9SWXGVVNL4hZCemzAMp) | vision, 2026-09-17 | You want the original ELI10 pitch and roadmap for components not yet built (Postgres, RabbitMQ, MongoDB, OAuth, nginx). **Its "dedicated vs. shared" diagram describes a `mode: create\|attach` field that was never built for Redis** — see `admin/architecture.md` for what actually shipped. |

## Glidepath — CI/CD

Full user and admin documentation already lives in the `glidepath` repo; this is
the on-ramp, not a duplicate.

| Doc | Read this when... |
|---|---|
| [glidepath/docs/user/README.md](https://github.com/jfillman/glidepath/blob/main/docs/user/README.md) | You're onboarding an app or maintaining its `cicd.yaml`. |
| [glidepath/docs/admin/README.md](https://github.com/jfillman/glidepath/blob/main/docs/admin/README.md) | You're running the platform — architecture, security model, ADRs, operations. |

**Illustrated / interactive:**

| Doc | Read this when... |
|---|---|
| [Glidepath](https://claude.ai/artifact/93Hd5ukJ1oBQHryiyGe7FR) | You want the illustrated platform overview. |
| [Pipeline Atlas · platform-cicd catalog](https://claude.ai/artifact/WdNLAQxo856YTrZtWsKdzW) | You want the pre-rename catalog reference (platform-cicd → Glidepath). |
| [Sigstore Ecosystem](https://claude.ai/artifact/AiYyTaNPaYmuH5nFicCujz) | You want the keyless-signing (Fulcio/Rekor/cosign) reference behind `admin/image-signing.md`. |
| [RHDH Plugin Manifest](https://claude.ai/artifact/Ggz7pP9i3ep67Mc6bX3jQL) | You're evaluating a Backstage/RHDH plugin for Tower. |
| [Upstream Candidates](https://claude.ai/artifact/HHPKtuLBhQX52SK1KEv7Wy) | You want the roadmap of upstream tools being evaluated. |

## Tower — the Backstage UI

Tower has no dedicated `docs/user/` or `docs/admin/` split yet (see
[Open items](#open-items)) — its documentation today is the illustrated set
below, plus `backstage-design.md` above.

| Doc | Read this when... |
|---|---|
| [Tower Field Report](https://claude.ai/artifact/TTrEDDnEPPGncw3QKqdjKa) | You want the current-state evaluation: what's live, what's thin. |
| [Tower Dashboard Mockups](https://claude.ai/artifact/WdYsSwHbUvhUFLfdB3BGSi) | You want the Fleet Grid / Ops Wall dashboard concepts. |
| [Tower Recent Activity](https://claude.ai/artifact/6CXUTUiuAtXBwHsPELfzeS) | You want the activity-feed design. |
| [Tower Release Matrix](https://claude.ai/artifact/X94edN1D3JYFYrybRjFfkn) | You want the release-matrix design (Releases tab + Overview pill). |
| [Tower Releases Revamp](https://claude.ai/artifact/6SSenGmF4Ugr45Skqv7hRb) | You want the Releases tab redesign. |
| [Tower Deployments Tab Concepts](https://claude.ai/artifact/9vDBTjpwHdm9rqnr8Cx5pv) | You want the Deployments tab concepts. |
| [Tower Rollout Mockups](https://claude.ai/artifact/9TeUHsDsv5H6mDmdof2XyS) | You want the rollout-visualization concepts. |
| [Tower CI/CD Mockups](https://claude.ai/artifact/TYWEd5zDCngEX467yxGiQ4) | You want the CI/CD tab ("Ground Control") concepts. |
| [Release Gates Mockup](https://claude.ai/artifact/JYEeEHHV6kvc9LBuzW5N54) | You want the release-gates UI concept. |
| [Release Flow Concepts](https://claude.ai/artifact/RjyB5Po7n1syUdMAXrd87U) | You want release-flow visualization concepts. |
| [Release Thread Patterns](https://claude.ai/artifact/EZHPaZ9vXPHjMRuPapujjJ) | You want the release-thread (activity-log) pattern language. |
| [Active Delivery Redesign](https://claude.ai/artifact/2acZTPZhFMU9ySjW2TFHGQ) | You want the write-action/RBAC UI redesign. |

## Brand & design system

| Doc | Read this when... |
|---|---|
| [Hangar Brand System](https://claude.ai/artifact/URP9Sz9zMCmWdUbcXANNs3) | You're designing anything Hangar-branded — palette, type, the amber/sky accent rule. |
| [Hangar Logo Concepts](https://claude.ai/artifact/EhCgYuDQXApnxUnxdnTU7f) | You want the logo design history — Concept A is final. |

## Kubernetes fundamentals (general reference, not Hangar-specific)

Not part of the Hangar product — background reading that happens to live in the
same artifact list. Not linked from Tower.

- [Kubernetes Cluster Architecture](https://claude.ai/artifact/7827igGT2ocrdWofphJoHS)
- [Pod Instantiation: From kubectl apply to Running](https://claude.ai/artifact/3YiDoTXc9r9a58CWhgqe28)
- [Worker Node Internals: From kubelet to Kernel](https://claude.ai/artifact/GmN7u8PULue9cnXGjtiMVH)
- [Pod Termination & the SIGTERM Race](https://claude.ai/artifact/5C3ZZBxAxRYeePvD5zG9ec)
- [Request Path: Client to Pod](https://claude.ai/artifact/Wpjw9UXmNh917C14sGkH5p)
- [CPU Requests vs Limits](https://claude.ai/artifact/EdYBvF185ACrkVqHJ8vMnp)
- [Crossing Cluster Boundaries](https://claude.ai/artifact/QYHTG3qH5aFFNWtW4P5CNH)

## Open items

- **This index was curated by title and publish date, not by re-reading every
  linked artifact.** The Airframe and Glidepath sections above are verified
  against real source (`xrds/`, `compositions/`, the actual `docs/` trees); the
  Tower and brand sections are placed by title alone — flag anything
  miscategorized or stale.
- **Tower/backstage and Apron have no `catalog-info.yaml`/`mkdocs.yml` yet** —
  their docs don't appear in TechDocs until that's added. Airframe and Glidepath
  do (2026-09-21).
- **Tower has no `docs/user/`/`docs/admin/` split** — worth doing once its
  illustrated mockups above settle into an as-built state, the same distinction
  Airframe and Glidepath already draw.
- **`kind-dev Radar` and `Podman Sleep Instability`** are live-status/incident
  artifacts, not curated docs — deliberately left out of this index.
