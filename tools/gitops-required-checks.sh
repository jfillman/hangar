#!/usr/bin/env bash
# gitops-required-checks.sh: a read-only check of limit (a) in glidepath docs/admin/security.md ("Limits of reading
# pipelines from the default branch"). With gitopsRepoProvenance: default_branch, a gitops repo with no .tekton/ on main
# starts no checks on a PR and nothing fails. The way out is a branch protection rule or ruleset that REQUIRES the gate
# checks (pinned to the Pipelines-as-Code GitHub App). This script shows, per gitops repo, whether that is so.
#
# Usage:
#   tools/gitops-required-checks.sh [--branch main] [--owner jfillman] [--app-name Glidepath] REPO...
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
#   .tekton      each PipelineRun on the branch, whether it has a path filter (on-path-change, or a CEL expression that uses files.*), and whether a gate check requires it
#   verdict      one line: gate checks are required; no gate check is required; NOT ENFORCEABLE (both endpoints answer
#                "Upgrade to GitHub Pro"); or UNKNOWN (a request failed: rate limit, missing permission, network)
#
# Read-only: only `gh api` GETs. Needs gh (logged in, repo read), jq and python3 with PyYAML. A gate check is a required context that
# is exactly "<app-name> / <PipelineRun name>". A required check "pinned to an app" has an app id
# (checks[].app_id, or integration_id in a ruleset); any source is shown as "any app".
set -u

branch=main
owner=jfillman
tenants=""
appname=Glidepath
repos=()
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) branch="$2"; shift 2 ;;
    --owner) owner="$2"; shift 2 ;;
    --tenants) tenants="$2"; shift 2 ;;
    --app-name) appname="$2"; shift 2 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) repos+=("$1"); shift ;;
  esac
done

if [ -n "$tenants" ]; then
  [ -d "$tenants/tenants" ] || { echo "no $tenants/tenants directory" >&2; exit 2; }
  for f in "$tenants"/tenants/*/identity.yaml; do
    [ -f "$f" ] || continue
    # the file is read as YAML, so quotes and comments around the scalar are handled
    url=$(python3 -c 'import sys, yaml
d = yaml.safe_load(open(sys.argv[1])) or {}
print(((d.get("platformIdentity") or d).get("gitopsRepoUrl")) or "")' "$f") || { echo "cannot parse $f" >&2; exit 2; }
    [ -n "$url" ] && repos+=("$(printf '%s' "$url" | sed -e 's#^https://github.com/##' -e 's#\.git$##' -e 's#/$##')")
  done
fi
[ ${#repos[@]} -gt 0 ] || { echo "no repos: give names or --tenants DIR" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq is needed" >&2; exit 2; }
python3 -c 'import yaml' 2>/dev/null || { echo "python3 with PyYAML is needed" >&2; exit 2; }

# api [--paginate] PATH: sets API_BODY and API_CODE without failing the script. API_CODE is 200, 404, plan (a 403 whose
# message is GitHub's "Upgrade to GitHub Pro" plan restriction), 403 (any other 403: a rate limit or a token without
# Administration: read) or err (anything else, such as a network error). Only plan means the plan lacks the feature.
api() {
  API_BODY=$(gh api "$@" 2>&1); local rc=$?
  if [ $rc -eq 0 ]; then API_CODE=200
  elif printf '%s' "$API_BODY" | grep -q 'HTTP 403' && printf '%s' "$API_BODY" | grep -qi 'upgrade to github pro'; then API_CODE=plan
  elif printf '%s' "$API_BODY" | grep -q 'HTTP 403'; then API_CODE=403
  elif printf '%s' "$API_BODY" | grep -q 'HTTP 404'; then API_CODE=404
  else API_CODE=err; fi
}

# Pipelines-as-Code names a check "<Repository application name> / <PipelineRun name>" (generateName as written, trailing dash
# included); Glidepath's application name is "Glidepath". A check is a gate check when its context starts with that.
is_gate() { case "$1" in "$appname / "*) return 0 ;; esac; return 1; }

# pr_info: reads one .tekton file on stdin, prints "<metadata.name or generateName><TAB><filter>" per PipelineRun document.
# filter: "path filter" (on-path-change, on-path-change-ignore, or an on-cel-expression that uses files.*),
# "branch filter" (on-target-branch other than [main], or an on-cel-expression on source_branch or target_branch other than
# target_branch == "main"), "event filter" (on-event other than [pull_request], or a CEL event other than pull_request),
# "CEL without path or branch reference" (any other on-cel-expression), or "no path filter". The CEL text is normalised
# first (whitespace dropped, single quotes read as double), so target_branch=="main" and target_branch == 'main' are alike.
pr_info() {
  python3 -c '
import re, sys, yaml
def items(v):
    return [x.strip().strip("\"\x27") for x in str(v).strip().strip("[]").split(",") if x.strip()]
for d in yaml.safe_load_all(sys.stdin):
    if not isinstance(d, dict) or d.get("kind") != "PipelineRun":
        continue
    m = d.get("metadata") or {}
    a = m.get("annotations") or {}
    p = "pipelinesascode.tekton.dev/"
    cel = re.sub(r"\s+", "", str(a.get(p + "on-cel-expression") or "")).replace("\x27", "\"")
    rest = cel.replace("target_branch==\"main\"", "")
    events = re.findall(r"event==\"(\w+)\"", cel)
    if p + "on-path-change" in a or p + "on-path-change-ignore" in a or "files." in cel:
        f = "path filter"
    elif "source_branch" in rest or "target_branch" in rest or (p + "on-target-branch" in a and items(a[p + "on-target-branch"]) != ["main"]):
        f = "branch filter"
    elif any(e != "pull_request" for e in events) or (p + "on-event" in a and items(a[p + "on-event"]) != ["pull_request"]):
        f = "event filter"
    elif cel:
        f = "CEL without path or branch reference"
    else:
        f = "no path filter"
    print("%s\t%s" % (m.get("name") or m.get("generateName") or "", f))
'
}

for r in "${repos[@]}"; do
  case "$r" in */*) slug="$r" ;; *) slug="$owner/$r" ;; esac
  echo "== $slug ($branch)"
  # required checks as lines "context<TAB>app" from both sources
  req=""
  plan=0   # endpoints answering with the plan restriction
  errs=0   # endpoints that failed for another reason (rate limit, permission, network)

  api "repos/$slug/branches/$branch/protection"
  case $API_CODE in
    200)
      p=$(printf '%s' "$API_BODY" | jq -r '(.required_status_checks.checks // [])[] | "\(.context)\t\(if .app_id == null or .app_id == -1 then "any app" else "app " + (.app_id|tostring) end)"')
      if [ -n "$p" ]; then echo "  protection: required checks"; printf '%s\n' "$p" | sed 's/^/    /'; req="$req$p"$'\n'
      else echo "  protection: present, no required status checks"; fi ;;
    404) echo "  protection: absent (404, the branch is not protected)" ;;
    plan) echo "  protection: not available on this plan (403)"; plan=$((plan+1)) ;;
    *) echo "  protection: could not be read ($API_CODE): $(printf '%s' "$API_BODY" | head -1)"; errs=$((errs+1)) ;;
  esac

  api --paginate "repos/$slug/rules/branches/$branch"
  case $API_CODE in
    200)
      p=$(printf '%s' "$API_BODY" | jq -r '.[] | select(.type=="required_status_checks") | (.parameters.required_status_checks // [])[] | "\(.context)\t\(if .integration_id == null then "any app" else "app " + (.integration_id|tostring) end)"')
      if [ -n "$p" ]; then echo "  rulesets: required checks"; printf '%s\n' "$p" | sed 's/^/    /'; req="$req$p"$'\n'
      else echo "  rulesets: none require status checks"; fi ;;
    404) echo "  rulesets: none (404)" ;;
    plan) echo "  rulesets: not available on this plan (403)"; plan=$((plan+1)) ;;
    *) echo "  rulesets: could not be read ($API_CODE): $(printf '%s' "$API_BODY" | head -1)"; errs=$((errs+1)) ;;
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
      info=$(printf '%s\n' "$body" | pr_info) || { echo "  .tekton: $path: not valid YAML"; continue; }
      while IFS=$'\t' read -r nm filt; do
        [ -z "$filt" ] && continue
        # the check's context is exactly "<app> / <name>"; compare the whole string
        if printf '%s\n' "$req" | cut -f1 | grep -Fxq -- "$appname / $nm"; then rq="required"
        elif [ $errs -gt 0 ]; then rq="UNKNOWN (required checks could not be read)"
        else rq="not required"; fi
        echo "  .tekton: $path ($nm): $filt, $rq"
        if [ "$filt" != "path filter" ] && [ "$filt" != "branch filter" ] && [ "$filt" != "event filter" ] && [ "$rq" = "not required" ]; then unfiltered="$unfiltered$nm "; fi
      done <<EOI
$info
EOI
    done
  elif [ "$API_CODE" = 404 ]; then
    echo "  .tekton: none on $branch (a PR starts no checks, and nothing fails)"
  else
    echo "  .tekton: could not be read ($(printf '%s' "$API_BODY" | head -1))"
  fi
  [ -n "$unfiltered" ] && echo "  not conditional (no path, branch or event filter) and not required: $unfiltered"

  if [ -n "$gates" ]; then echo "  verdict: gate checks are required"
  elif [ $errs -gt 0 ]; then echo "  verdict: UNKNOWN: a request failed (see above), so required checks could not be determined"
  elif [ $plan -eq 2 ]; then echo "  verdict: NOT ENFORCEABLE: protection and rulesets are not available on this plan (403), so a check cannot be required"
  else echo "  verdict: no gate check is required"; fi
done
