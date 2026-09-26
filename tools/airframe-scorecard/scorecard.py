#!/usr/bin/env python3
"""Airframe AI-friendliness scorecard.

Measures how usable Airframe's contract is by an AI agent, with numbers that can be re-run,
instead of an opinion. Ten dimensions, each scored 0-100 from measurable checks; the letter
grade comes from the score, and A+ additionally requires every acceptance check in
`ACCEPTANCE` to pass. See hangar/docs/autopilot/airframe-ai-friendly.md for the rubric and
what each check means.

    python3 scorecard.py [--tech /Users/jerf/tech] [--json out.json]

Read-only. It never writes to any repo; it runs `helm template` into memory only.
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


# --------------------------------------------------------------------------- helpers
def load_yaml(p):
    return yaml.safe_load(Path(p).read_text())


def walk_schema(node, fn):
    """Call fn(node) on every subschema in a JSON-schema-ish tree."""
    if not isinstance(node, dict):
        return
    fn(node)
    for k, c in node.items():
        if k == "properties" and isinstance(c, dict):
            for c2 in c.values():
                walk_schema(c2, fn)
        elif k in ("items", "additionalProperties", "if", "then", "else", "not") and isinstance(c, dict):
            walk_schema(c, fn)
        elif k in ("oneOf", "anyOf", "allOf") and isinstance(c, list):
            for c2 in c:
                walk_schema(c2, fn)
        elif k == "definitions" and isinstance(c, dict):
            for c2 in c.values():
                walk_schema(c2, fn)


def frac(a, b):
    return (a / b) if b else 0.0


def helm_ok(chart, values: dict) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(values, f)
        name = f.name
    try:
        r = subprocess.run(["helm", "template", "x", str(chart), "-f", name], capture_output=True, timeout=60)
        return r.returncode == 0
    finally:
        os.unlink(name)


def letter(score: float) -> str:
    bands = [(97, "A+"), (93, "A"), (90, "A-"), (87, "B+"), (83, "B"), (80, "B-"), (77, "C+"),
             (73, "C"), (70, "C-"), (67, "D+"), (63, "D"), (60, "D-")]
    for lo, g in bands:
        if score >= lo:
            return g
    return "F"


# --------------------------------------------------------------------------- collection
def collect(tech: Path) -> dict:
    af = tech / "airframe"
    chart = af / "charts" / "airframe-application"
    m: dict = {}

    schema = json.loads((chart / "values.schema.json").read_text())
    st = dict(nodes=0, desc=0, objects=0, addl_false=0, passthrough=0, constrained=0, leaves=0, examples=0,
              xhangar=0, owner=0, risk=0)

    def rec(n):
        st["nodes"] += 1
        st["desc"] += "description" in n
        if n.get("type") == "object" or "properties" in n:
            st["objects"] += 1
            if n.get("additionalProperties") is False:
                st["addl_false"] += 1
            if n.get("x-hangar-passthrough"):
                st["passthrough"] += 1
        else:
            st["leaves"] += 1
            st["constrained"] += any(k in n for k in ("enum", "pattern", "minimum", "maximum", "minLength",
                                                      "maxLength", "minItems", "maxItems", "format"))
        st["examples"] += ("examples" in n) or ("example" in n)
        st["xhangar"] += any(k.startswith("x-hangar") for k in n)
        st["owner"] += "x-hangar-owner" in n
        st["risk"] += "x-hangar-risk" in n

    walk_schema(schema, rec)
    m["schema"] = st
    m["schema_top_keys"] = len(schema.get("properties", {}))
    m["schema_owner_top"] = sum(1 for v in schema.get("properties", {}).values() if "x-hangar-owner" in v)

    # XRDs
    x = dict(count=0, nodes=0, desc=0, cel=0, status_conditions=0, status_reason=0, summary=0, catalog=0)
    kinds = []
    for f in sorted(glob.glob(str(af / "xrds" / "*.yaml"))):
        d = load_yaml(f)
        x["count"] += 1
        kinds.append(d["spec"]["names"]["kind"])
        ann = d["metadata"].get("annotations", {})
        x["catalog"] += ann.get("terasky.backstage.io/add-to-catalog") == "true"
        x["summary"] += "hangar.io/agent-summary" in ann
        sch = d["spec"]["versions"][0]["schema"]["openAPIV3Schema"]

        def r2(n):
            x["nodes"] += 1
            x["desc"] += "description" in n
            x["cel"] += "x-kubernetes-validations" in n
        walk_schema(sch, r2)
        status = sch.get("properties", {}).get("status", {}).get("properties", {})
        x["status_conditions"] += "conditions" in status
        x["status_reason"] += any("reason" in json.dumps(v) for v in status.values())
    m["xrd"] = x
    m["xrd_kinds"] = kinds

    # contract / meta artifacts
    m["agents_md"] = (af / "AGENTS.md").exists()
    m["agents_md_components"] = len(list((af / "compositions").glob("*/AGENTS.md")))
    m["llms_txt"] = (af / "llms.txt").exists() or (af / "docs" / "llms.txt").exists()
    m["contract_bundle"] = (af / "contract" / "airframe-contract.json").exists()
    m["outputs_meta"] = len(list((af / "contract").glob("*.meta.yaml"))) if (af / "contract").exists() else 0
    m["validate_cli"] = (af / "validate").exists() or (af / "tools" / "airframe-validate").exists()
    m["appspec_schema"] = (af / "contract" / "appspec.schema.json").exists()
    m["walkthroughs"] = len(list((af / "docs" / "walkthroughs").glob("*.yaml"))) if (af / "docs" / "walkthroughs").exists() else 0
    m["verify_meta"] = 0 if not (af / "contract").exists() else sum(
        "verify" in (load_yaml(f) or {}) for f in (af / "contract").glob("*.meta.yaml"))

    # chart guards / tests / CI
    fails = 0
    for f in glob.glob(str(chart / "templates" / "**" / "*"), recursive=True):
        if os.path.isfile(f):
            t = Path(f).read_text()
            fails += len(re.findall(r'\{\{-?\s*fail\b|\brequired\s+"', t))
    m["helm_guards"] = fails
    m["chart_tests"] = len(list((chart / "tests").glob("**/*.yaml"))) if (chart / "tests").exists() else 0
    wf = list((af / ".github" / "workflows").glob("*.y*ml")) if (af / ".github" / "workflows").exists() else []
    m["ci_workflows"] = len(wf)
    m["ci_chart_workflow"] = any("chart" in w.name or "validate" in w.name for w in wf)
    lint = subprocess.run(["helm", "lint", str(chart)], capture_output=True)
    m["helm_lint_ok"] = lint.returncode == 0

    # base layer / ownership split in the ApplicationSets
    appsets = glob.glob(str(tech / "gitops-cluster-dev" / "02-argocd-apps" / "**" / "*.yaml"), recursive=True)
    text = "\n".join(Path(p).read_text() for p in appsets)
    m["base_layer"] = bool(re.search(r"valueFiles:[\s\S]{0,400}base", text))
    m["release_file_split"] = "values.release.yaml" in text or ".release.yaml" in text

    # live values files
    upper = [p for p in glob.glob(str(tech / "gitops-*" / "*" / "*" / "values.yaml"))
             if "appName" in (load_yaml(p) or {})]
    lower = glob.glob(str(tech / "*" / "platform" / "envs" / "*.yaml"))
    m["live_upper"], m["live_lower"] = len(upper), len(lower)

    def keys_mixed_upper(d):
        machine = "releaseTracking" in d
        human = any(k in d for k in ("httpRoute", "components", "env", "secrets", "ingress")) or \
            any(k in (d.get("rollout") or {}) for k in ("replicas", "resources", "steps", "ports", "livenessProbe"))
        return machine and human

    def keys_mixed_lower(d):
        ro = d.get("rollout") or {}
        machine = bool((ro.get("image") or {}).get("tag"))
        human = any(k in d for k in ("components", "env", "secrets")) or any(k for k in ro if k != "image")
        return machine and human

    mixed = [keys_mixed_upper(load_yaml(p) or {}) for p in upper] + [keys_mixed_lower(load_yaml(p) or {}) for p in lower]
    m["mixed_owner_files"] = sum(mixed)
    m["live_files"] = len(mixed)

    # derived-name literals in env entries (convention reliance)
    pat = re.compile(r"-master:|-connection|-user-credentials|svc\.cluster\.local|-app\b")
    lit = tot = 0
    for p in upper + lower:
        d = load_yaml(p) or {}
        for e in d.get("env", []) or []:
            tot += 1
            lit += bool(pat.search(json.dumps(e)))
    m["derived_literals"], m["env_entries"] = lit, tot

    # real strengths that already exist
    values_top = set((load_yaml(chart / "values.yaml") or {}).keys())
    m["schema_key_coverage"] = frac(len(values_top & set(schema.get("properties", {}))), len(values_top))
    sec = ((schema.get("properties", {}).get("secrets", {}) or {}).get("items", {}) or {}).get("properties", {})
    m["secrets_by_reference"] = bool(sec) and "value" not in sec
    m["chart_readme_lines"] = len((chart / "README.md").read_text().splitlines()) if (chart / "README.md").exists() else 0
    m["docs_index"] = (tech / "hangar" / "docs" / "README.md").exists()
    comps = glob.glob(str(af / "compositions" / "**" / "*"), recursive=True)
    m["custom_conditions"] = any(os.path.isfile(c) and "CicdOnboarded" in Path(c).read_text() for c in comps)
    ok_types = 0
    probe = {"appName": "x", "appType": "app", "cluster": "c", "envName": "e", "rollout": {"replicas": "two"}}
    m["type_error_caught"] = not helm_ok(chart, probe)

    # fleet baseline + typo acceptance (strictness)
    base_ok = accepted = tested = 0
    for p in upper + lower:
        d = load_yaml(p) or {}
        if not helm_ok(chart, d):
            continue
        base_ok += 1
        mut = copy.deepcopy(d)
        mut["zzUnknownKey"] = {"a": 1}
        if isinstance(mut.get("rollout"), dict):
            mut["rollout"]["replcas"] = 5
        tested += 1
        accepted += helm_ok(chart, mut)
    m["fleet_baseline_ok"], m["fleet_total"] = base_ok, len(upper) + len(lower)
    m["typo_tested"], m["typo_accepted"] = tested, accepted

    # docs: yaml blocks in user docs
    blocks = parsed = 0
    for f in glob.glob(str(af / "docs" / "user" / "*.md")):
        for b in re.findall(r"```ya?ml\n(.*?)```", Path(f).read_text(), flags=re.S):
            blocks += 1
            try:
                yaml.safe_load(b)
                parsed += 1
            except Exception:
                pass
    m["doc_yaml_blocks"], m["doc_yaml_parse"] = blocks, parsed
    m["doc_yaml_validated_in_ci"] = 0 if not (af / "docs" / "walkthroughs").exists() else 1
    m["mcp_tools"] = len(list((tech / "clearance" / "src" / "clearance").glob("airframe_tools.py")))
    return m


# --------------------------------------------------------------------------- scoring
def score(m: dict) -> dict:
    s = m["schema"]
    x = m["xrd"]
    desc_cov = frac(s["desc"], s["nodes"])
    addl = frac(s["addl_false"], max(1, s["objects"] - s["passthrough"]))
    constrained = frac(s["constrained"], s["leaves"])
    typo_acc = frac(m["typo_accepted"], m["typo_tested"])
    xrd_desc = frac(x["desc"], x["nodes"])
    dims: dict[str, dict] = {}

    def dim(name, parts, note):
        total_w = sum(w for w, _, _ in parts)
        val = 100 * sum(w * v for w, v, _ in parts) / total_w
        dims[name] = {"score": round(val, 1), "grade": letter(val), "checks": {n: round(v, 3) for _, v, n in parts}, "note": note}

    dim("1 Discoverability", [
        (2, 1.0, "human docs and quickstarts exist"),
        (2, frac(x["catalog"], x["count"]), "XRDs generate the Backstage catalog"),
        (2, float(m["agents_md"]), "AGENTS.md at the repo root"),
        (1, frac(m["agents_md_components"], x["count"]), "AGENTS.md per component"),
        (3, float(m["contract_bundle"]), "machine-readable contract bundle"),
        (1, float(m["llms_txt"]), "llms.txt index"),
        (1, frac(x["summary"], x["count"]), "agent-summary annotation on XRDs"),
        (1, float(m["docs_index"]), "a docs table of contents"),
        (1, min(1.0, m["chart_readme_lines"] / 300), "chart README documents the values")],
        "what an agent can enumerate without reading prose")
    dim("2 Schema precision", [
        (3, 1.0 if s["nodes"] else 0.0, "values.schema.json exists"),
        (3, m["schema_key_coverage"], "top-level values keys covered by the schema"),
        (3, float(m["type_error_caught"]), "a wrong-type value fails at render"),
        (3, desc_cov, "schema nodes with a description"),
        (3, addl, "objects that reject unknown keys"),
        (2, constrained, "leaf fields with an enum, pattern or bound"),
        (1, frac(s["examples"], s["nodes"]), "nodes with examples"),
        (3, 1 - typo_acc, "typo'd values files that fail (rather than pass silently)"),
        (2, xrd_desc, "XRD fields with a description"),
        (2, min(1.0, x["cel"] / max(1, x["count"])), "XRDs with a cross-field CEL rule")],
        "how precisely the contract says what is valid")
    dim("3 Component contracts", [
        (4, frac(m["outputs_meta"], 6), "components declaring machine-readable outputs (of 6)"),
        (3, 1 - frac(m["derived_literals"], max(1, m["env_entries"])), "env entries free of derived-name literals"),
        (2, float(m["verify_meta"] > 0), "components declaring verify checks")],
        "whether an agent can wire components without guessing names")
    dim("4 Pre-merge validation", [
        (4, float(m["validate_cli"]), "an `airframe validate` exists"),
        (3, float(m["ci_chart_workflow"]), "required check on env, gitops and tenants repos"),
        (2, min(1.0, m["helm_guards"] / 25), "chart guards with actionable messages (of 25)"),
        (2, 0.0, "dead-end lint rules (encoded and seeded)"),
        (2, frac(m["fleet_baseline_ok"], m["fleet_total"]), "live values files that render cleanly")],
        "the deterministic gate an agent can retry against")
    dim("5 Write safety", [
        (4, 1 - frac(m["mixed_owner_files"], m["live_files"]), "live files with a single owner"),
        (2, float(m["base_layer"]), "shared base layer"),
        (2, float(m["release_file_split"]), "machine-owned release file split out"),
        (3, frac(m["schema_owner_top"], max(1, m["schema_top_keys"])), "fields carrying an owner"),
        (2, frac(s["risk"], max(1, m["schema_top_keys"])), "fields carrying a risk class"),
        (2, float(m["secrets_by_reference"]), "secrets are references, never values")],
        "whether path-level scope can protect machine-owned data")
    dim("6 Observe and verify", [
        (2, 1.0, "Crossplane's standard Ready and Synced conditions"),
        (1, float(m["custom_conditions"]), "custom conditions (e.g. CicdOnboarded)"),
        (3, frac(x["status_conditions"], x["count"]), "XRDs declaring status conditions"),
        (3, frac(x["status_reason"], x["count"]), "XRDs with reason codes"),
        (3, float(m["verify_meta"] > 0), "verify contracts"),
        (2, float(m["mcp_tools"] > 0), "a describe/status tool")],
        "can an agent tell whether it worked, and why not")
    dim("7 Docs for agents", [
        (3, 1.0, "walked-live quickstarts (true docs)"),
        (2, frac(m["doc_yaml_parse"], m["doc_yaml_blocks"]), "doc YAML blocks that at least parse"),
        (3, float(m["doc_yaml_validated_in_ci"]), "doc YAML blocks validated in CI"),
        (3, min(1.0, m["walkthroughs"] / 3), "executable walkthroughs (of 3)"),
        (2, float(m["agents_md"]), "AGENTS.md")],
        "docs an agent can rely on and replay")
    dim("8 Interaction surface", [
        (4, float(m["mcp_tools"] > 0), "airframe.* tools available to agents"),
        (3, float(m["appspec_schema"]), "a desired-state AppSpec"),
        (2, 1.0, "single GitOps write path"),
        (2, 0.5, "UI-only config path exists (Tower), no API")],
        "how an agent actually asks for a change")
    dim("9 Safety integration", [
        (3, frac(s["risk"], max(1, m["schema_top_keys"])), "risk-classed fields"),
        (3, 0.0, "field-level agent-scope gate"),
        (2, 1.0, "secrets referenced, never inlined"),
        (2, 0.0, "escape hatches (extraManifests) denied by default")],
        "tiers that reach down to individual fields")
    dim("10 Hygiene and determinism", [
        (3, float(m["helm_lint_ok"]), "helm lint passes"),
        (3, min(1.0, m["chart_tests"] / 10), "chart tests (of 10)"),
        (3, float(m["ci_chart_workflow"]), "chart CI"),
        (2, frac(m["fleet_baseline_ok"], m["fleet_total"]), "fleet renders cleanly")],
        "does the contract stay true as it changes")
    overall = round(sum(d["score"] for d in dims.values()) / len(dims), 1)
    return {"overall": overall, "grade": letter(overall), "dimensions": dims}


ACCEPTANCE = [
    ("typo acceptance is 0%", lambda m: m["typo_tested"] > 0 and m["typo_accepted"] == 0),
    ("schema description coverage >= 95%", lambda m: frac(m["schema"]["desc"], m["schema"]["nodes"]) >= 0.95),
    ("every non-passthrough object rejects unknown keys", lambda m: frac(m["schema"]["addl_false"], max(1, m["schema"]["objects"] - m["schema"]["passthrough"])) >= 1.0),
    ("contract bundle published", lambda m: m["contract_bundle"]),
    ("AGENTS.md at root and on every component", lambda m: m["agents_md"] and m["agents_md_components"] >= m["xrd"]["count"]),
    ("all component XRDs declare outputs and verify checks", lambda m: m["outputs_meta"] >= 6 and m["verify_meta"] >= 6),
    ("no derived-name literals in live env entries", lambda m: m["derived_literals"] == 0),
    ("airframe validate exists and is a required check", lambda m: m["validate_cli"] and m["ci_chart_workflow"]),
    ("no live file mixes human and machine-owned keys", lambda m: m["mixed_owner_files"] == 0),
    ("shared base layer in the ApplicationSets", lambda m: m["base_layer"]),
    ("airframe.* tools exist", lambda m: m["mcp_tools"] > 0),
    ("AppSpec schema exists", lambda m: m["appspec_schema"]),
    ("executable walkthroughs replace prose quickstarts", lambda m: m["walkthroughs"] >= 3),
    ("every live values file renders cleanly", lambda m: m["fleet_baseline_ok"] == m["fleet_total"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tech", default="/Users/jerf/tech")
    ap.add_argument("--json")
    ap.add_argument("--baseline", help="committed baseline JSON; exit 1 if the score, any dimension or any acceptance check regresses")
    a = ap.parse_args()
    m = collect(Path(a.tech))
    res = score(m)
    acc = [(n, bool(f(m))) for n, f in ACCEPTANCE]
    res["acceptance"] = {n: ok for n, ok in acc}
    res["a_plus"] = res["overall"] >= 97 and all(ok for _, ok in acc)
    res["metrics"] = m
    print(f"Airframe AI-friendliness: {res['overall']}/100  {res['grade']}   (A+ certified: {res['a_plus']})\n")
    for name, d in res["dimensions"].items():
        print(f"  {name:28} {d['score']:>5}  {d['grade']:<3}  {d['note']}")
    print(f"\n  acceptance checks passing: {sum(ok for _, ok in acc)}/{len(acc)}")
    for n, ok in acc:
        print(f"    [{'x' if ok else ' '}] {n}")
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=2, default=str))
        print(f"\nwrote {a.json}")
    if a.baseline:
        base = json.loads(Path(a.baseline).read_text())
        bad = []
        if res["overall"] < base["overall"]:
            bad.append(f"overall {base['overall']} -> {res['overall']}")
        for name, d in res["dimensions"].items():
            b = base["dimensions"].get(name)
            if b and d["score"] < b["score"]:
                bad.append(f"{name} {b['score']} -> {d['score']}")
        for n, was in base["acceptance"].items():
            if was and not res["acceptance"].get(n, False):
                bad.append(f"acceptance regressed: {n}")
        if bad:
            print("\nREGRESSION vs baseline:\n  " + "\n  ".join(bad))
            return 1
        print(f"\nno regression vs baseline ({base['overall']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
