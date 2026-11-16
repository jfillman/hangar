# Specs and plans

Build specifications and working plans for the Hangar program, kept here so they are versioned.

| Path | What |
|---|---|
| `clearance-autopilot/spec.md` | Clearance & Autopilot Build Specification |
| `clearance-cloud/spec.md` | Clearance Cloud Build Specification |
| `argo-rollouts-1-11/spec.md` | Argo Rollouts 1.11 Upgrade and Follow-ons: Build Specification |
| `plans/` | Plans, package cards, reviews and design notes written during the build |

Each `spec.md` is a Spec Sheet source. Build the page with the kit in [`tools/spec-kit/`](../tools/spec-kit/):

    python3 tools/spec-kit/build_spec.py specs/<name>/spec.md <out.html>

The format is described in [`tools/spec-kit/SPEC-FORMAT.md`](../tools/spec-kit/SPEC-FORMAT.md). Built HTML is
published, not committed. This directory sits outside `docs/` on purpose: it is not part of the documentation site.

Evidence packets are not kept here. This repository is public: no account ids, bucket names or other real
identifiers in these files.
