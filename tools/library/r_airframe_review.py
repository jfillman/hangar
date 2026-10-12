"""Airframe review: Crossplane usage and the agent-facing API (Oct 8, 2026), with its outcome."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, text, callout

P = Page(
    'airframe-crossplane-agent-api', 'Review', 'Airframe · Review · Crossplane and the agent API',
    'How well does Airframe use Crossplane, and can an agent drive it?',
    'A review of Airframe\'s Crossplane layer and its agent-facing API: twenty findings, ranked, and what happened to each one in the two days after.',
    '2026-10-08',
    meta=[('Scope', 'airframe, with autopilot and hangar for context; both clusters checked read-only'),
          ('Follows', 'the Sep 27, 2026 architecture review'),
          ('Acted on', 'Oct 8 and 9, 2026')],
    lede=('Two weeks after the architecture review I asked for a narrower one: just Airframe, my service catalog, '
          'read the way an agent would read it. Is the Crossplane layer built well, and could an agent discover, '
          'change and verify things through it without a human translating? Twenty findings came back. Fifteen '
          'were fixed and live within two days.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">15 of 20 fixed and live · Oct 9, 2026</span>
  <h2>A healthy fleet with structural debt, and an agent API that was half built.</h2>
  <p>Every catalog XR on both clusters was Synced and Ready, and the compositions in git matched their templates. The problems were structural: six near-identical app compositions with no tests, credentials passing through the function pipeline, readiness decided by hand in every template, and one-shot scaffolding reconciled forever.</p>
  <p>On the agent side, the contract half was ahead of most platforms: a strict schema, rule ids with fix hints, and closed reason sets. The runtime half was missing. Verify steps were English sentences, the planner wrote an API group that no longer existed, and a typo in an XR was silently dropped.</p>
</div>
""")

# Figure 1: the findings board, coloured by outcome.
FIX, PART, LATER, OPEN = 'ok', 'warn', 'info', 'bad'
crossplane = [('C1', 'High', FIX), ('C2', 'High', FIX), ('C3', 'High', FIX), ('C4', 'High', FIX), ('C5', 'Med', FIX),
              ('C6', 'Med', FIX), ('C7', 'Med', FIX), ('C8', 'Med', FIX), ('C9', 'Med', PART), ('C10', 'Low', FIX),
              ('C11', 'Low', FIX), ('C12', 'Low', FIX), ('C13', 'Low', FIX)]
agent = [('A1', 'High', FIX), ('A2', 'High', FIX), ('A3', 'High', PART), ('A4', 'Med', OPEN), ('A5', 'Med', LATER),
         ('A6', 'Med', OPEN), ('A7', 'Low', FIX)]
KIND = {FIX: 'focal', PART: 'propose', LATER: 'optional', OPEN: 'external'}
W, H = 760, 300
b = zone(24, 24, 712, 116, 'Part 1 · Crossplane · 13 findings')
for i, (fid, sev, st) in enumerate(crossplane):
    b += node(40 + i * 52, 64, 44, 52, fid, sev.lower(), KIND[st])
b += zone(24, 160, 712, 116, 'Part 2 · the agent-facing API · 7 findings')
for i, (fid, sev, st) in enumerate(agent):
    b += node(40 + i * 52, 200, 44, 52, fid, sev.lower(), KIND[st])
b += callout(420, 236, 'Fixed in two days: 15 of 20.')
b += lib.legend(296, [('focal', 'fixed, live'), ('propose', 'partly done'), ('optional', 'deferred'), ('external', 'open')], W)
fig1 = P.fig(b, W, 324, 'Twenty findings and their outcome',
             'Thirteen Crossplane findings and seven agent API findings. Fifteen are fixed and live, two are partly done (C9 and A3), one is deferred (A5), and two are open (A4 and A6).',
             'Every finding, coloured by what happened to it. The four still not done are about governance and vocabulary, not correctness.')

# Figure 2: the XR write path after A2.
W2, H2 = 760, 236
c = zone(24, 24, 712, 140, 'An XR request, from commit to cluster')
c += node(40, 72, 120, 56, 'XR in git', 'tenants repo', 'propose')
c += node(204, 72, 136, 56, 'validate --xr', 'pre-merge CI', 'security', tag='new')
c += node(384, 72, 136, 56, 'Argo CD', 'server-side apply', 'backend', tag='new')
c += node(564, 72, 156, 56, 'API server', 'rejects unknown fields', 'focal')
c += path([(160, 100), (200, 100)], 'link') + path([(340, 100), (380, 100)]) + path([(520, 100), (560, 100)], 'accent')
c += text(40, 196, 'Before: client-side apply let the API server prune a misspelled field, and the XR reported healthy.', 11, fill=lib.MUTED)
c += text(40, 214, 'After: the typo fails twice, once in the PR with a did-you-mean hint, and again at sync.', 11, fill=lib.MUTED)
fig2 = P.fig(c, W2, H2, 'Closing the XR typo hole',
             'An XR committed to git is validated against the XRD schema in pre-merge CI, then Argo CD applies it with server-side apply, so the API server rejects any field the schema does not declare.',
             'A2: a scratch XR with a misspelled field failed its sync and created nothing. The same mistake is now caught before merge.')

ROWS = [
    ('C1', 'High', 'A Dex client secret the server doesn\'t hold', 'If an app\'s Secret was deleted, the function wrote a fresh secret that Dex never accepted, and still reported Ready. Now it adopts the existing one; proved by deleting a Secret and watching it come back identical within a second.', 'Fixed', 'ok'),
    ('C2', 'High', 'Credentials rendered into managed-resource specs', 'Two credentials travelled through the function pipeline into plain specs in etcd. The provider now takes a secret reference, and the copies happen server side, so no credential value enters a composed manifest.', 'Fixed', 'ok'),
    ('C3', 'High', 'Six cloned compositions, zero composition tests', 'One build script with a check in CI regenerates every composition from shared templates, and a render harness compares 77 cases against committed expectations. Two renderers agree.', 'Fixed', 'ok'),
    ('C4', 'High', 'Reconcile forever for one-shot scaffolds', '"Scaffold once, reconcile never" became a ledger on the XR\'s status. GitHub file resources fell from 161 to 60, and every scaffolded file kept the same content, checked file by file.', 'Fixed', 'ok'),
    ('C5, C6', 'Med', 'A condition that was always False, and a silent default', '<code>WorkloadDeployed</code> could never be True from where it was computed; it\'s gone. A misspelled app name now says <code>AppNotFound</code> instead of quietly pointing at a NodeJS app.', 'Fixed', 'ok'),
    ('C7', 'Med', 'Readiness decided by hand in every template', 'Readiness rules are declared once, as CEL per resource kind, and the per-template annotations are gone. One of them had been wrong the other way.', 'Fixed', 'ok'),
    ('C8', 'Med', 'Operator webhooks flipping every XR', 'The root cause was leader-election loss on single-replica operators. Two replicas, budgets and longer leases took webhook failures from one per restart to zero in 444 applies.', 'Fixed', 'ok'),
    ('C9', 'Med', 'Security hygiene', 'Endpoints and the org id moved out of templates into the cluster registry. TLS on two internal links is skipped for now, by decision.', 'Partly', 'warn'),
    ('C10 to C13', 'Low', 'Event churn, a probe timeout, version pins, XRD API hygiene', 'All four done: events only on change, one version pinned everywhere, default compositions, name-length bounds and printer columns on all twenty XRDs.', 'Fixed', 'ok'),
    ('A1', 'High', 'The planner was stale on both outputs', 'Autopilot\'s planner wrote a retired API group and a <code>cicd.yaml</code> shape Glidepath no longer accepted, so the parachute sentence could not pass. Fixed, with a test against the live fleet file.', 'Fixed', 'ok'),
    ('A2', 'High', 'The XR write path accepted typos silently', 'Server-side apply at sync, and a pre-merge <code>--xr</code> validator with did-you-mean hints. See figure 2.', 'Fixed', 'ok'),
    ('A3', 'High', 'The observe and verify half was prose', 'Verify steps are now structured checks that <code>airframe-verify</code> runs read-only, and every XRD has a machine-readable sidecar tested in CI. Status outputs on the XR wait until something needs them.', 'Partly', 'warn'),
    ('A4, A6', 'Med', 'Conditions and errors aren\'t one vocabulary', 'Values-file errors come back with a rule id and a hint; XR-side failures still come back as template strings.', 'Open', 'bad'),
    ('A5', 'Med', 'AI triage bypasses governance', 'Routing HolmesGPT\'s fix PRs through Clearance needs Clearance to be running, and it exists only as code today. Triage is switched off meanwhile.', 'Deferred', 'info'),
    ('A7', 'Low', 'Discoverability', 'An AGENTS.md for every kind, generated from the sidecars, and every chart field carries an owner and a risk class. The scorecard moved from 74 to 82.', 'Fixed', 'ok'),
]
rows = ''.join(f'<div class="row"><h3>{fid} · {title}</h3>{chip(st, tone)}<p>{p}</p></div>' for fid, sev, title, p, st, tone in ROWS)

P.add(f"""
<section>
  <h2>Twenty findings, two days later</h2>
  {fig1}
</section>

<section>
  <h2>What it found, and what happened</h2>
  <div class="track">{rows}</div>
</section>

<section>
  <h2>One fix, drawn</h2>
  {fig2}
</section>

<section>
  <h2>What I took from it</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Lesson</span><h3>Every bug was found live</h3><p>Before this, every readiness, naming and policy bug in the git history was found on a cluster. The render harness is the change that moves them to a pull request.</p></div>
    <div class="card"><span class="eyebrow">Lesson</span><h3>Root cause before the fix</h3><p>The webhook outages looked like an Airframe problem. They were operators losing leadership on a busy node, and the fix was in the cluster, not the catalog.</p></div>
    <div class="card"><span class="eyebrow">Lesson</span><h3>A contract isn't an API</h3><p>A strict schema tells an agent what it may write. It also needs to know what happened afterwards, in a form it can check. That's the half still being built.</p></div>
  </div>
</section>
""")
