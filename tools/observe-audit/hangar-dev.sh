#!/usr/bin/env bash
# The API server audit webhook on hangar-dev, the rehearsal for hangar-prod. Order: prepare, (collector deployed),
# install, verify. hangar-dev's node is a kiac VM under Apple's container runtime.
CLUSTER="hangar-dev"
NODE_EXEC="container exec -i kiac-hangar-dev-control-plane"
NAMESPACES="observe-rehearsal,argocd"
MAX_LOAD="20"
source "$(dirname "$0")/common.sh"
