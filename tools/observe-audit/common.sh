# Shared by hangar-dev.sh and hangar-prod.sh. Sourced, not run. The cluster's script sets CLUSTER, NODE_EXEC, NAMESPACES
# and MAX_LOAD. Keys live in $DIR on this machine, outside every repository, and are never printed.
set -euo pipefail

APRON="${APRON:-$HOME/tech/apron}"
CLEARANCE_SRC="${CLEARANCE_SRC:-$HOME/tech/clearance}"
CLEARANCE_REF="v0.38.0"
SERVICE_IP="10.96.200.50"   # free on both clusters and pinned in the chart's webhook.service.clusterIP
DIR="$HOME/.hangar-observe-audit/${CLUSTER}"
TOOL="${APRON}/hack/observe-audit.sh"

[ -x "${TOOL}" ] || { echo "error: ${TOOL} not found. Pull apron main, or set APRON=<checkout>." >&2; exit 1; }

case "${1:-}" in
  prepare)
    # Makes the keys, then the collector's Secret. Run once, before the collector is deployed.
    "${TOOL}" prepare --dir "${DIR}" --service-ip "${SERVICE_IP}" --namespaces "${NAMESPACES}" \
      --clearance-src "${CLEARANCE_SRC}" --clearance-ref "${CLEARANCE_REF}"
    "${TOOL}" secret --context "${CLUSTER}" --dir "${DIR}"
    ;;
  install)
    # Run after the collector is deployed and ready. Shows the change, asks, then restarts the API server.
    "${TOOL}" install --context "${CLUSTER}" --node-exec "${NODE_EXEC}" --dir "${DIR}" --max-load "${MAX_LOAD}" --dry-run
    printf '\nThis restarts the API server on %s. Type the cluster name to continue: ' "${CLUSTER}"
    read -r answer
    [ "${answer}" = "${CLUSTER}" ] || { echo "Not confirmed; nothing changed."; exit 1; }
    "${TOOL}" install --context "${CLUSTER}" --node-exec "${NODE_EXEC}" --dir "${DIR}" --max-load "${MAX_LOAD}"
    ;;
  verify)
    "${TOOL}" verify --context "${CLUSTER}"
    ;;
  rollback)
    "${TOOL}" rollback --context "${CLUSTER}" --node-exec "${NODE_EXEC}"
    ;;
  *)
    echo "usage: $0 prepare|install|verify|rollback" >&2
    exit 2
    ;;
esac
