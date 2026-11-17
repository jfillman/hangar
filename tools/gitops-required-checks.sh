#!/usr/bin/env bash
# gitops-required-checks.sh: a read-only check of limit (a) in glidepath docs/admin/security.md ("Limits of reading
# pipelines from the default branch"). With gitopsRepoProvenance: default_branch, a gitops repo with no .tekton/ on main
# starts no checks on a PR and nothing fails. The way out is a branch protection rule or ruleset that REQUIRES the gate
# checks (pinned to the Pipelines-as-Code GitHub App). This script shows, per gitops repo, whether that is so.
#
# Usage:
#   tools/gitops-required-checks.sh [--branch main] [--owner jfillman] REPO...
#   tools/gitops-required-checks.sh [--branch main] --tenants DIR
#
#   REPO         a gitops repo as owner/name or just name (the owner then comes from --owner, default jfillman)
#   --tenants DIR  a cluster's tenants repo checkout (gitops-<cluster>-tenants): the repos are the gitopsRepoUrl of every
#                  DIR/tenants/*/identity.yaml. Repo names given as arguments are added to that list.
#
# Per repo it prints:
#   protection   branch protection on the branch: required checks (name, app pin) or none, absent (404), or not available
#                on this plan (403: GitHub needs Pro/Team, or a public repo, for protection on a private repo)
#   rulesets     the same for rules/branches/<branch> (rules of type required_status_checks)
#   .tekton      each PipelineRun on the branch, whether it has a path filter, and whether a gate check requires it
#   verdict      one line: required, NOT REQUIRED, or NOT ENFORCEABLE (protection not available on this plan)
#
# Read-only: only `gh api` GETs. Needs gh (logged in, repo read) and jq. A required check "pinned to an app" has an app id
# (checks[].app_id, or integration_id in a ruleset); any source is shown as "any app".
set -u

branch=main
owner=jfillman
tenants=""
repos=()
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) branch="$2"; shift 2 ;;
    --owner) owner="$2"; shift 2 ;;
    --tenants) tenants="$2"; shift 2 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) repos+=("$1"); shift ;;
  esac
done

if [ -n "$tenants" ]; then
  [ -d "$tenants/tenants" ] || { echo "no $tenants/tenants directory" >&2; exit 2; }
  for f in "$tenants"/tenants/*/identity.yaml; do
    [ -f "$f" ] || continue
    url=$(sed -n 's/^[[:space:]]*gitopsRepoUrl:[[:space:]]*//p' "$f" | head -1 | tr -d '"')
    [ -n "$url" ] && repos+=("$(printf '%s' "$url" | sed -e 's#^https://github.com/##' -e 's#\.git$##')")
  done
fi
[ ${#repos[@]} -gt 0 ] || { echo "no repos: give names or --tenants DIR" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq is needed" >&2; exit 2; }

# api PATH: sets API_BODY and API_CODE (200, 403, 404 or other) without failing the script.
api() {
  API_BODY=$(gh api "$1" 2>&1); local rc=$?
  if [ $rc -eq 0 ]; then API_CODE=200
  elif printf '%s' "$API_BODY" | grep -q 'HTTP 403'; then API_CODE=403
  elif printf '%s' "$API_BODY" | grep -q 'HTTP 404'; then API_CODE=404
  else API_CODE=err; fi
}

# Pipelines-as-Code names a check "<Repository application name> / <PipelineRun name>"; Glidepath's application name is "Glidepath".
is_gate() { case "$1" in "Glidepath / "*) return 0 ;; esac; return 1; }

for r in "${repos[@]}"; do
  case "$r" in */*) slug="$r" ;; *) slug="$owner/$r" ;; esac
  echo "== $slug ($branch)"
  # required checks as lines "context<TAB>app" from both sources
  req=""
  unavailable=0

  api "repos/$slug/branches/$branch/protection"
  case $API_CODE in
    200)
      p=$(printf '%s' "$API_BODY" | jq -r '(.required_status_checks.checks // [])[] | "\(.context)\t\(if .app_id == null or .app_id == -1 then "any app" else "app " + (.app_id|tostring) end)"')
      if [ -n "$p" ]; then echo "  protection: required checks"; printf '%s\n' "$p" | sed 's/^/    /'; req="$req$p"$'\n'
      else echo "  protection: present, no required status checks"; fi ;;
    404) echo "  protection: absent (404, the branch is not protected)" ;;
    403) echo "  protection: not available on this plan (403)"; unavailable=1 ;;
    *) echo "  protection: error: $(printf '%s' "$API_BODY" | head -1)"; unavailable=1 ;;
  esac

  api "repos/$slug/rules/branches/$branch"
  case $API_CODE in
    200)
      p=$(printf '%s' "$API_BODY" | jq -r '.[] | select(.type=="required_status_checks") | (.parameters.required_status_checks // [])[] | "\(.context)\t\(if .integration_id == null then "any app" else "app " + (.integration_id|tostring) end)"')
      if [ -n "$p" ]; then echo "  rulesets: required checks"; printf '%s\n' "$p" | sed 's/^/    /'; req="$req$p"$'\n'
      else echo "  rulesets: none require status checks"; fi ;;
    404) echo "  rulesets: none (404)" ;;
    403) echo "  rulesets: not available on this plan (403)"; unavailable=1 ;;
    *) echo "  rulesets: error: $(printf '%s' "$API_BODY" | head -1)"; unavailable=1 ;;
  esac

  gates=""
  while IFS=$'\t' read -r ctx app; do
    [ -z "$ctx" ] && continue
    if is_gate "$ctx"; then gates="$gates$ctx ($app); "; fi
  done <<EOF
$req
EOF
  if [ -n "$gates" ]; then echo "  gate checks required: $gates"; else echo "  gate checks required: none"; fi
  if [ -n "$req" ] && [ -n "$gates" ] && printf '%s' "$gates" | grep -q '(any app)'; then
    echo "  note: a gate check is not pinned to the Pipelines-as-Code App, any app can report it"
  fi

  # the PipelineRuns on the branch
  api "repos/$slug/contents/.tekton?ref=$branch"
  unfiltered=""
  if [ "$API_CODE" = 200 ]; then
    names=$(printf '%s' "$API_BODY" | jq -r '.[] | select(.type=="file") | select(.name|test("\\.ya?ml$")) | .path')
    if [ -z "$names" ]; then echo "  .tekton: directory on $branch has no YAML files (a PR starts no checks)"; fi
    for path in $names; do
      body=$(gh api -H "Accept: application/vnd.github.raw" "repos/$slug/contents/$path?ref=$branch" 2>/dev/null)
      [ -z "$body" ] && { echo "  .tekton: $path: could not be read"; continue; }
      # the PipelineRun's name: metadata name or generateName (documents of other kinds are skipped)
      printf '%s\n' "$body" | grep -q '^kind:[[:space:]]*PipelineRun' || continue
      nm=$(printf '%s\n' "$body" | sed -n -e 's/^  name:[[:space:]]*//p' -e 's/^  generateName:[[:space:]]*//p' | head -1 | tr -d '"'"'")
      nm=${nm%-}
      if printf '%s\n' "$body" | grep -Eq 'pipelinesascode.tekton.dev/on-(path-change|path-change-ignore|cel-expression)'; then
        filt="path filter"
      else
        filt="no path filter"
      fi
      if [ -n "$nm" ] && printf '%s\n' "$req" | cut -f1 | grep -Fq -- "$nm"; then rq="required"; else rq="not required"; fi
      echo "  .tekton: $path ($nm): $filt, $rq"
      if [ "$filt" = "no path filter" ] && [ "$rq" = "not required" ]; then unfiltered="$unfiltered$nm "; fi
    done
  elif [ "$API_CODE" = 404 ]; then
    echo "  .tekton: none on $branch (a PR starts no checks, and nothing fails)"
  else
    echo "  .tekton: could not be read ($(printf '%s' "$API_BODY" | head -1))"
  fi
  [ -n "$unfiltered" ] && echo "  always-running but not required: $unfiltered"

  if [ -n "$gates" ]; then echo "  verdict: gate checks are required"
  elif [ $unavailable -eq 1 ]; then echo "  verdict: NOT ENFORCEABLE: protection and rulesets are not available on this plan (403), so a missing check cannot block a merge"
  else echo "  verdict: NOT REQUIRED: no gate check is required, a PR with no checks can merge"; fi
done
