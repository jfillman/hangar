"""Build every diagram page for hangar/docs/autopilot/diagrams/.

    python3 build_hangar.py [OUT_DIR]

Three sets: plan (8), autopilot (19), reference (10); plus Glidepath (7), Crossplane (4), Service catalog (5) and SLO (4) beside them. Needs only the Python standard library.
"""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
import e_a, e_b, e_c, e_d, e_e, e_f, e_g, e_h, e_i, e_j, e_k, d123, d456, d789, d1011

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '../../docs/autopilot/diagrams')
# The Glidepath set lives beside it, in docs/glidepath/diagrams (a sibling of OUT's parent).
OUT_GLIDEPATH = os.path.join(OUT, '../../glidepath/diagrams')
# The Crossplane set (pictures for the Building Airframe essays) lives in docs/crossplane/diagrams.
OUT_CROSSPLANE = os.path.join(OUT, '../../crossplane/diagrams')
# The Service catalog set (pictures for the Why Airframe essay) lives in docs/catalog/diagrams.
OUT_CATALOG = os.path.join(OUT, '../../catalog/diagrams')
# The SLO set (pictures for the SLO feature doc) lives in docs/slo/diagrams.
OUT_SLO = os.path.join(OUT, '../../slo/diagrams')

PLAN = [e_g.p_family, e_g.p_roadmap, e_g.p_deps, e_g.p_scorecard, e_g.p_contract, e_g.p_plan_seq, e_g.p_skyport_matrix, e_g.p_skyport_seq]
AUTOPILOT = [
    e_a.e01, e_d.w_two_planes, e_a.e02,
    e_d.w_shapes, e_d.w_definition_to_run, e_d.w_run_anatomy, e_d.w_lifecycle, e_d.w_team,
    e_e.w_fleets, e_e.w_egress,
    e_a.e03, e_f.w_tiers, e_f.w_authority, e_b.e06, e_b.e07, e_b.e08, e_c.e09,
    e_f.w_placement, e_f.w_rollout,
]
# The reference set: the general architecture.
# Glidepath (CI/CD), redrawn from glidepath/docs in this grammar.
GLIDEPATH = [e_h.g_overview, e_h.g_pipeline, e_h.g_mapping, e_h.g_onboarding, e_h.g_chaining, e_h.g_deploy_release, e_h.g_multicluster]
CROSSPLANE = [e_i.x_secretstore, e_i.x_readiness, e_i.x_budget, e_i.x_timeline]
CATALOG = [e_j.c_one_api, e_j.c_menu_inventory, e_j.c_anatomy, e_j.c_discovery, e_j.c_roadmap]
SLO = [e_k.s_pipeline, e_k.s_thresholds, e_k.s_state, e_k.s_tick]
REFERENCE = [d123.d1, d123.d2, d123.d3, d456.d4, d456.d5, d456.d6, d789.d7, d789.d8, d789.d9, d1011.d10]


def build(group, fns, subdir, footer, root=None):
    lib.FOOTER = footer
    d = os.path.join(root or OUT, subdir)
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, '[0-9][0-9]-*.html')):
        os.remove(f)
    n = len(fns)
    rows = []
    for i, fn in enumerate(fns, 1):
        r = fn()
        eb = re.sub(r'\d\d of \d\d', f'{i:02d} of {n:02d}', r['eyebrow'])
        html = lib.page(r['slug'], eb, r['title'], r['desc'], r['body'], r['W'], r['H'], r.get('lede', ''), r.get('cards', ()), '', r.get('y0', 0))
        name = f'{i:02d}-{r["slug"]}.html'
        open(os.path.join(d, name), 'w').write(html)
        rows.append((f'{subdir}/{name}', eb, r['title'], r.get('lede', '')))
    print(group, n, 'pages')
    return rows

plan = build('plan', PLAN, 'plan', 'Hangar · Autopilot · plan')
auto = build('autopilot', AUTOPILOT, 'autopilot', 'Hangar · Autopilot')
ref = build('reference', REFERENCE, 'reference', 'Hangar · reference architecture')
glide = build('glidepath', GLIDEPATH, '.', 'Hangar · Glidepath', root=OUT_GLIDEPATH)
xp = build('crossplane', CROSSPLANE, '.', 'Hangar · Airframe · Crossplane', root=OUT_CROSSPLANE)
cat = build('catalog', CATALOG, '.', 'Hangar · Airframe · Service catalog', root=OUT_CATALOG)
slo = build('slo', SLO, '.', 'Hangar · SLOs', root=OUT_SLO)

def tiles(rows):
    return ''.join(f'<a class="tile" href="{h}"><p class="eb">{e}</p><h2>{t}</h2><p>{l}</p></a>' for h, e, t, l in rows)

css = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--paper:#f2efe9;--ink:#1b1f24;--muted:#5b6570;--soft:#838b93;--accent:#b9791f;--link:#2e7ba6;--rule:rgba(27,31,36,0.12)}
body{font-family:'Geist',system-ui,sans-serif;background:var(--paper);color:var(--ink);padding:2.5rem 2rem}
.frame{max-width:1120px;margin:0 auto}
.eyebrow{font-family:'Geist Mono',monospace;font-size:.66rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}
h1{font-family:'Instrument Serif',serif;font-size:2.25rem;font-weight:400;letter-spacing:-.02em;line-height:1.1;margin-bottom:.6rem}
h3{font-family:'Geist Mono',monospace;font-size:.66rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin:1.75rem 0 .6rem}
.lede{color:var(--muted);font-size:.95rem;line-height:1.55;max-width:74ch;margin-bottom:.5rem}
.grid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:.75rem}
.tile{display:block;background:#fff;border:1px solid var(--rule);border-radius:6px;padding:1rem 1.1rem;text-decoration:none;color:inherit}
.tile:hover{border-color:var(--accent)}
.tile .eb{font-family:'Geist Mono',monospace;font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:.4rem}
.tile h2{font-family:'Instrument Serif',serif;font-size:1.25rem;font-weight:400;line-height:1.2;margin-bottom:.4rem}
.tile p:last-child{font-size:.78rem;line-height:1.5;color:var(--muted)}
.foot{font-family:'Geist Mono',monospace;font-size:.62rem;letter-spacing:.06em;color:var(--soft);border-top:1px solid var(--rule);margin-top:1.5rem;padding-top:.6rem}
@media (max-width:900px){.grid{grid-template-columns:1fr}}"""
index = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Autopilot diagrams</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style></head><body><div class="frame">
<p class="eyebrow">Hangar · Autopilot · diagrams</p>
<h1>Autopilot diagrams: {len(plan)+len(auto)+len(ref)} one-page pictures</h1>
<p class="lede">Every page separates what is built from what is proposed. Start with the plan set, then the Autopilot design, then the general reference architecture.</p>
<h3>Plan: family, roadmap, contract, Skyport AI ({len(plan)})</h3><div class="grid">{tiles(plan)}</div>
<h3>Autopilot design ({len(auto)})</h3><div class="grid">{tiles(auto)}</div>
<h3>Reference architecture ({len(ref)})</h3><div class="grid">{tiles(ref)}</div>
<div class="foot">Generated by hangar/tools/diagrams/build_hangar.py with the diagram-design skill (Hangar profile)</div>
</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w').write(index)
print('index written')
