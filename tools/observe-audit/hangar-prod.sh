#!/usr/bin/env bash
# The API server audit webhook on hangar-prod. Run hangar-dev.sh through verify first. Order: prepare, (collector
# deployed), install, verify. hangar-prod's node is a kind container under podman on the laptop; run this from the
# workstation, it goes through `ssh laptop`.
#
# MAX_LOAD: the laptop's load has spiralled after restarts before, so install refuses to start above it.
CLUSTER="hangar-prod"
NODE_EXEC="ssh -o BatchMode=yes laptop /opt/podman/bin/podman exec -i hangar-prod-control-plane"
NAMESPACES="app-gate-api-prod,argocd,argocd-apps"
MAX_LOAD="8"
source "$(dirname "$0")/common.sh"
