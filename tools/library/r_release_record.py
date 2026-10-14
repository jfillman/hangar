"""Proposal: the Release Record lifecycle in Tower (Oct 13, 2026). Start the record when the last release ships."""
from report import Page, chip
import lib
from lib import node, path, zone, lab, vlab, text, callout

P = Page(
    'tower-release-record-lifecycle', 'Proposal', 'Tower · Proposal · Release record lifecycle',
    'Start the next release record when the last one ships',
    'A proposal to open Tower\'s Release Record as a live draft the moment the previous release ships, move sign-off before the Flight merge, and keep the record open through a bake window, while it stays a sealed, git-backed receipt at the end.',
    '2026-10-13',
    meta=[('Status', 'proposed; R1 approved to ship on its own, October 13, 2026'),
          ('Grounded in', 'Tower v0.66.0 and Glidepath main, October 13, 2026'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/tower/">Tower docs</a>')],
    lede=('Today a Release Record is a receipt: Tower writes it after an image is already healthy in a Flight '
          'environment. But most release work happens before that point. Someone gathers scope, writes notes, '
          'picks a candidate and makes the go or no-go call. The record should exist for all of it, and still be '
          'a sealed, git-backed receipt at the end.'))

P.add("""
<div class="verdict info">
  <span class="stamp">Proposed · R1 approved to ship alone</span>
  <h2>The record shows up after every decision it could have informed has already been made.</h2>
  <ul>
    <li>The next release's <b>draft</b> opens as soon as the previous one ships, before any PR exists. Open PRs show as incoming, and merged PRs are its scope.</li>
    <li>Sign-off moves <b>before</b> the Flight merge, onto the release PR.</li>
    <li>The record stays open through a bake window, then records the outcome.</li>
    <li>The git seal, the layout, export, compare and the confidence score all stay as they are.</li>
  </ul>
</div>
""")

# Figure 1: when the record exists, today and proposed.
W, H = 760, 324
EV = [('Last release', 'prod @ previous'), ('PRs merge', 'main · 1..n'), ('Image built', 'signed'),
      ('Ground soak', 'dev · test'), ('Release PR', 'proposed'), ('Gates, merge', 'guardrails'),
      ('Canary', 'progressing'), ('Healthy', 'healthy'), ('Bake', '+24h · +7d')]
X = [64 + i * 79 for i in range(len(EV))]
b = ''
for x in X:
    b += f'<line x1="{x}" y1="92" x2="{x}" y2="270" stroke="{lib.RULE}" stroke-dasharray="2,4" stroke-width="1"/>'
b += f'<line x1="40" y1="84" x2="736" y2="84" stroke="{lib.SOFT}" stroke-width="1.2"/>'
for x, (n, s) in zip(X, EV):
    b += text(x, 50, n, 10, 600, lib.INK, anchor='middle')
    b += text(x, 66, s, 8, 400, lib.MUTED, anchor='middle', mono=True)
    b += f'<circle cx="{x}" cy="84" r="4" fill="#ffffff" stroke="{lib.INK}" stroke-width="1.2"/>'


def bar(x, y, w, kind):
    fill, stroke, dash = lib.KINDS[kind]
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="4" fill="{lib.PAPER}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>')


def row(y, s):
    return text(24, y, s, 8, 500, lib.MUTED, mono=True, ls='0.14em')


b += row(114, 'TOWER RECORD · TODAY')
b += bar(48, 120, 576, 'optional')
b += text(336, 138, 'no record · scope, notes and sign-off have nowhere to live', 9, 400, lib.MUTED, anchor='middle', mono=True)
b += bar(632, 120, 104, 'backend') + text(684, 138, 'sealed in git', 10, 600, lib.INK, anchor='middle')
b += row(172, 'GLIDEPATH TRACKING CONFIGMAP')
b += bar(372, 178, 364, 'store')
b += text(554, 196, 'proposed → healthy · dev cluster · swept at 14 days', 9, 400, lib.MUTED, anchor='middle', mono=True)
b += row(230, 'PROPOSED RECORD')
b += bar(48, 236, 688, 'focal')
for x in (X[2], X[4], X[5], X[7]):
    b += f'<line x1="{x}" y1="236" x2="{x}" y2="264" stroke="{lib.ACC}" stroke-opacity="0.55" stroke-width="1"/>'
for cx, n in [((48 + X[2]) / 2, 'Draft'), ((X[2] + X[4]) / 2, 'Candidate'), ((X[4] + X[5]) / 2, 'Ready'),
              ((X[5] + X[7]) / 2, 'Rolling out'), ((X[7] + 736) / 2, 'Released · bake')]:
    b += text(cx, 254, n, 10.5, 600, lib.INK, anchor='middle')
b += callout(24, 304, 'Opens when the previous release ships. Seals into git at Healthy. Ends when the next one supersedes it.')
fig1 = P.fig(b, W, H, 'When the release record exists',
             'A release timeline from the last Flight release to the bake window. Today Tower\'s record appears only after Healthy. Glidepath\'s tracking ConfigMap starts at the release PR, lives on the dev cluster and is swept after 14 days. The proposed record runs the whole way through Draft, Candidate, Ready, Rolling out and Released.',
             'One release, from the last Flight release to the bake window. Columns are events, not equal time. The dashed bar is where no Tower record exists today.')

# Figure 2: branches, merges and the draft.
W2, H2 = 760, 300
INKC, MUT = lib.INK, lib.MUTED


def dot(x, y, r=4, fill='#ffffff', stroke=INKC):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'


c = path([(120, 150), (120, 88), (290, 88), (290, 144)])
c += path([(150, 150), (150, 214), (430, 214), (430, 157)])
c += path([(470, 150), (470, 88), (560, 88)], dashed=True, marker=False)
c += f'<line x1="40" y1="150" x2="720" y2="150" stroke="{INKC}" stroke-width="1.4"/>'
c += text(720, 140, 'main', 8, 400, MUT, anchor='end', mono=True)
c += dot(190, 88) + dot(250, 88) + dot(250, 214) + dot(370, 214)
c += dot(520, 88, stroke=MUT) + dot(560, 88, stroke=MUT)
c += dot(80, 150, 6, INKC) + dot(290, 150, 6, INKC) + dot(430, 150, 7, lib.ACC, lib.ACC)
c += text(128, 78, 'feature/bag-reprint · dev 1', 10, 600, INKC)
c += text(158, 234, 'feature/read-pref · dev 2', 10, 600, INKC)
c += text(478, 78, 'feature/tz-cutoff · PR #221 open', 10, 600, INKC)
c += text(570, 92, 'not merged · incoming, not scope', 8, 400, MUT, mono=True)
c += text(80, 176, 'BIRCH · on prod', 10, 600, INKC, anchor='middle')
c += text(80, 189, '1.8.2-6f1c0aa', 8, 400, MUT, anchor='middle', mono=True)
c += text(298, 174, 'quiet-heron', 10, 600, INKC)
c += text(298, 187, '1.8.2-4c1e9a0', 8, 400, MUT, mono=True)
c += text(438, 174, 'amber-finch', 10, 600, INKC)
c += text(438, 187, '1.9.0-a41f9c2 · promote →', 8, 400, MUT, mono=True)
c += f'<path d="M92 246 V254 H720 V246" fill="none" stroke="{lib.ACC}" stroke-width="1.5"/>'
c += text(92, 272, 'NEXT RELEASE · CEDAR · DRAFT', 8, 500, lib.ACC, mono=True, ls='0.14em')
c += text(92, 288, 'Opens when BIRCH ships. Scope is main after BIRCH. Promoting amber-finch ships both features.', 10, 400, MUT)
fig2 = P.fig(c, W2, H2, 'Branches, merges and the draft',
             'Main carries the previous release, BIRCH. Two developers\' feature branches merge into main, and each merge builds a candidate image: quiet-heron, then amber-finch. A third branch is still an open PR, so it is incoming, not scope. The draft, CEDAR, spans everything on main after BIRCH.',
             'Each dot on main is a merge, and each merge builds an image with its own slug. quiet-heron still says 1.8.2 because nobody had bumped the version yet.')

# Figure 3: the lifecycle.
W3, H3 = 760, 384
d = zone(16, 28, 728, 96, 'Detours') + zone(16, 268, 728, 88, 'Endings')
PH = [('Draft', 'opens at last ship', 'backend'), ('Candidate', 'soaking on Ground', 'backend'),
      ('Ready', 'release PR, sign-off', 'focal'), ('Rolling out', 'merged · canary', 'backend'),
      ('Released', 'healthy, baking', 'backend')]
PX = [24 + i * 148 for i in range(5)]
for i, (x, (n, s, k)) in enumerate(zip(PX, PH)):
    d += node(x, 170, 116, 56, n, s, k)
    if i:
        d += path([(x - 32, 198), (x - 3, 198)], 'accent' if i == 3 else 'muted')
for i, t in enumerate(['build', 'promote', 'merge', 'healthy']):
    d += lab(PX[i] + 116 + 16, 232, t, lib.ACC if t == 'merge' else lib.SOFT)
d += node(210, 52, 170, 56, 'Rework', 'candidate rejected', 'optional')
d += path([(370, 170), (370, 112)], dashed=True) + vlab(370, 112, 170, 'no-go')
d += path([(240, 108), (240, 166)], dashed=True) + vlab(240, 108, 170, 'rebuild')
d += node(520, 52, 170, 56, 'Aborted', 'canary paused or failed', 'optional')
d += path([(536, 170), (536, 112)], dashed=True) + vlab(536, 112, 170, 'abort', side='l')
d += path([(572, 108), (572, 166)], dashed=True) + vlab(572, 108, 170, 'retry')
d += node(456, 292, 140, 52, 'Rolled back', 'from rollout or released', 'store')
d += path([(526, 226), (526, 288)]) + vlab(526, 248, 280, 'rollback', side='l')
d += node(616, 292, 116, 52, 'Superseded', 'next release healthy', 'store')
d += path([(674, 226), (674, 288)]) + vlab(674, 248, 280, 'next live')
d += callout(24, 376, 'Ready is the new step: the release PR is open, gates run, and sign-off happens here.')
fig3 = P.fig(d, W3, H3, 'Release record lifecycle',
             'Main phases Draft, Candidate, Ready, Rolling out and Released. Detours: Rework from Ready back to Candidate, and Aborted from Rolling out with a retry. Endings: Rolled back from Rolling out, and Superseded from Released when the next release is healthy.',
             'Nine states and ten transitions. Ready and the merge out of it are highlighted, because that is the new decision point.')

MOCK = """
<style>
.tw{background:#0b0d10;color:#e9ecef;border:1px solid #232830;border-radius:10px;padding:16px;font-size:13px;min-width:700px}
.tw .tabs{display:flex;gap:18px;font-weight:600;color:#96a2ac;border-bottom:1px solid rgba(233,236,239,.1);padding-bottom:8px;margin-bottom:14px}
.tw .tabs .on{color:#e9ecef;box-shadow:inset 0 -2px 0 #e8a33d;padding-bottom:8px;margin-bottom:-9px}
.tw .card{background:#171b21;border:1px solid rgba(233,236,239,.1);border-radius:6px;padding:12px 14px;margin-bottom:10px}
.tw .card.draft{border:1px dashed rgba(232,163,61,.55)}
.tw .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.tw .ver{font-weight:600;font-size:16px;letter-spacing:.06em}
.tw .m{font-family:var(--mono);font-size:11.5px;white-space:nowrap}
.tw .d{color:#96a2ac}
.tw .sp{flex:1}
.tw .ch{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:3px;border:1px solid currentColor}
.tw .amb{color:#e8a33d} .tw .sky{color:#6fb2d9} .tw .grn{color:#6cc08a}
.tw .slug{font-family:var(--mono);font-size:11px;color:#6fb2d9;background:rgba(111,178,217,.1);border-radius:10px;padding:1px 8px;white-space:nowrap}
.tw .grid{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:10px;margin-top:12px}
.tw .col{background:#0b0d10;border:1px solid rgba(233,236,239,.1);border-radius:5px;padding:10px 12px}
.tw .col h4{margin:0 0 8px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#96a2ac;font-weight:600}
.tw .col ul{list-style:none;margin:0;padding:0}
.tw .col li{display:flex;gap:8px;align-items:baseline;padding:3px 0;font-size:12.5px}
.tw .btn{font-size:12px;background:#1f242c;border:1px solid rgba(233,236,239,.1);border-radius:4px;padding:5px 10px}
.tw .btn.p{color:#0b0d10;background:#e8a33d;border-color:#e8a33d}
.tw .meter{height:6px;background:#1f242c;border-radius:3px;overflow:hidden;margin:4px 0 6px}
.tw .meter i{display:block;height:100%;width:75%;background:#e8a33d}
pre.schema{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;overflow-x:auto;font-family:var(--mono);font-size:.78rem;line-height:1.6;margin:0}
pre.schema .c{color:var(--ink-2)} pre.schema .n{color:var(--amber)}
</style>
<div class="tbl" style="background:transparent;border:0" role="img" aria-label="Sketch of Tower's Record sub-tab with a Next release draft card above the sealed records">
<div class="tw">
  <div class="tabs"><span>Matrix</span><span>Log</span><span>Lead time</span><span>Preview</span><span class="on">Record</span></div>
  <div class="card draft">
    <div class="row"><span class="ch amb">Next release · draft</span><span class="ver">CEDAR</span><span class="d m">v1.9.0 suggested · 3 feat / 4 fix</span><span class="sp"></span><span class="d">Owner</span><span>@jfillman</span></div>
    <div class="grid">
      <div class="col"><h4>Scope · 7 PRs since v1.8.2</h4><ul>
        <li><span class="ch sky">feat</span><span>Bag-tag reprint endpoint <span class="d m">#212</span></span></li>
        <li><span class="ch sky">feat</span><span>Read preference per route <span class="d m">#215</span></span></li>
        <li><span class="ch d">fix</span><span>Timezone on transfer cutoff <span class="d m">#217</span></span></li>
        <li class="d">+ 4 more · 2 linked issues still open</li>
        <li class="d" style="border-top:1px solid rgba(233,236,239,.1);margin-top:6px;padding-top:6px">Incoming · 2 open PRs <span class="m">#221 #224</span></li>
      </ul></div>
      <div class="col"><h4>Candidates</h4><ul>
        <li><span class="grn">●</span><span class="m">1.9.0-a41f9c2</span><span class="slug">amber-finch</span><span class="d">test · 26h</span></li>
        <li><span class="amb">!</span><span class="m">1.8.2-4c1e9a0</span><span class="slug">quiet-heron</span><span class="d">version not bumped</span></li>
      </ul><div class="d" style="margin-top:8px;font-size:12px">amber-finch: build, test and scan passed · provenance verified · SBOM +2 packages.</div></div>
      <div class="col"><h4>Readiness · 6 of 8</h4><div class="meter"><i></i></div><ul>
        <li><span class="grn">✓</span>Version bumped since BIRCH</li>
        <li><span class="grn">✓</span>Ground soak ≥ 24h</li>
        <li><span class="grn">✓</span>Rollback target eligible</li>
        <li><span class="amb">!</span>Release notes drafted</li>
        <li><span class="amb">!</span>Sign-off on release PR</li>
      </ul></div>
    </div>
    <div class="row" style="margin-top:12px"><span class="d" style="font-size:12px">Draft written from merged PRs · nothing saved until you edit</span><span class="sp"></span><span class="btn">Edit notes</span><span class="btn">Compare candidates</span><span class="btn p">Promote amber-finch →</span></div>
  </div>
  <div class="card"><div class="row"><span class="ch grn">Released · bake day 2 of 7</span><span class="ver">BIRCH</span><span class="d m">v1.8.2</span><span class="slug">north-tern</span><span class="d">prod · 2 days ago</span><span class="sp"></span><span class="d">Readiness</span><span class="m grn">92</span><span class="d">Outcome</span><span class="m d">pending</span></div></div>
  <div class="card" style="opacity:.75"><div class="row"><span class="ch d">Superseded</span><span class="ver">ASTER</span><span class="d m">v1.8.1</span><span class="slug">calm-plover</span><span class="d">prod · 9 days ago</span><span class="sp"></span><span class="d">Readiness</span><span class="m">88</span><span class="d">Outcome</span><span class="m grn">clean</span></div></div>
</div>
</div>
"""

IMP = [
    ('01', 'R1', '"Next release" live draft',
     'A card at the top of the Record list from the moment the previous release ships: nickname, suggested version, PRs merged since then sorted by the existing <code>classifyPr</code>, incoming open PRs, linked GitHub issues, candidate images and a notes preview.',
     'Mostly frontend, built from data Tower already fetches. No PRs and no files. Linked issues probably need GitHub\'s closing-issue references on each PR.'),
    ('02', 'R1', 'Candidates inside a release',
     'Every image built since the last release, side by side: slug, Ground environments, time on Ground, gate results, provenance, and SBOM diff against the last release. Promote acts on a candidate.',
     'Reuses Tekton Results pipeline runs, deploy history and provenance. Kargo calls this Freight.'),
    ('03', 'R2', 'Sign-off before the Flight merge',
     'In Ready, an approval is a review on the gitops release PR from someone other than the author. Approvals after release are still allowed but labelled <i>acknowledged</i>, and only pre-merge ones earn score.',
     'DORA\'s peer-review finding. Decided October 13, 2026: sign-off is recorded, never blocking, for now.'),
    ('04', 'R2', 'Readiness checklist, go or no-go',
     'At most eight items, most filled in by the system: guardrails green, provenance verified, minimum Ground soak, rollback target eligible, no open release-blocker issues. A person confirms notes, data risk and sign-off.',
     'Runway\'s checklists. Rollback eligibility already exists in Glidepath.'),
    ('05', 'R2', 'Release notes with two audiences',
     'Keep a Changelog categories, an internal changelog and user-facing notes with Known issues. Sealing writes a GitHub Release and feeds a per-app Changelog view.',
     'Replaces the blank Summary field with a pre-filled draft.'),
    ('06', 'R2', 'A named release owner',
     'An owner on the draft, defaulting to whoever promotes, with an optional rotation in <code>cicd.yaml</code>. The owner makes the call; others add evidence.',
     'Runway\'s release pilot. The existing <code>authoredBy</code> field covers part of it.'),
    ('07', 'R3', 'Outcome loop and a two-part score',
     'Today\'s confidence score becomes <b>Readiness</b>, minus the constant "+5, no incidents". A new <b>Outcome</b> score: clean, degraded, aborted then recovered, or rolled back, plus SLO checks at +1h, +24h and +7d.',
     'Glidepath already emits rolled-back and superseded. SLO checks need the prod cluster\'s Prometheus running again.'),
    ('08', 'R3', 'Risk signals filled in automatically',
     'Batch size, migration files, Flight config changes, dependency changes from the SBOM diff and a changed rollout strategy suggest low, medium or high, which a person confirms.',
     'The existing risk fields. Batch size is the factor DORA links to change failure rate.'),
    ('09', 'R4', 'Scheduled releases, optional',
     'A target date and planned scope from a GitHub milestone, then Jira keys. Scope can freeze, and open items move to the next release when this one seals.',
     'Linear\'s scheduled pipelines and Jira fix versions. Continuous mode stays the default.'),
    ('10', 'R4', 'Fleet calendar and notifications',
     'An Ops Wall panel of each app\'s draft, ready and baking releases, messages at Ready and Released, and a signed read-only link for stakeholders.',
     'The Phase 3 distribution items, now with something worth sending before release.'),
]
imp = '<div class="track">' + ''.join(
    f'<div class="row"><h3>{n} · {t}</h3>{chip(r, "warn" if r == "R1" else "info")}<p>{what}</p><p class="note">{fits}</p></div>'
    for n, r, t, what, fits in IMP) + '</div>'

P.add(f"""
<section>
  <h2>Where it stands</h2>
  <div class="prose"><p>Release management is the part of Tower I trust most. The October 11 field report rated it Strong. So this isn't a rescue. It's about timing.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Piece</th><th>What it does today</th><th>State</th></tr></thead>
    <tbody>
      <tr><td class="area">Record sub-tab</td><td>List and detail views: what changed, what was built, what happened, then human context and a verification strip.</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Export and compare</td><td>A self-contained HTML document that prints to PDF, and a diff of two records of the same app.</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Saved to git</td><td>When a release goes Healthy in a Flight environment, a poller opens a PR adding <code>releases/&lt;app&gt;@&lt;tag&gt;.yaml</code> to the app's gitops repo. Cloud apps write theirs from the merged pin PR.</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Human context</td><td>Summary, risk, notes, tags and approvals stamped with the signed-in identity. Every edit is a PR.</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Build evidence</td><td>Archived pipeline runs, tests, scans, provenance, SBOM and the guardrail ledger, kept in the record so they outlive live data.</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Confidence score</td><td>Starts at 50, with points for guardrails, provenance, approvals and "no incidents".</td><td>{chip('Shipped', 'ok')}</td></tr>
      <tr><td class="area">Outcome tracking</td><td>Status can only be healthy, degraded or superseded, and incidents can't be recorded, so every release gets the "no incidents" points. Glidepath knows about rollbacks; the record doesn't.</td><td>{chip('Gap', 'bad')}</td></tr>
      <tr><td class="area">Post-release SLO watch</td><td>Checks at +24h and +7d, blocked while the prod cluster's Prometheus is scaled to zero.</td><td>{chip('Not started', 'info')}</td></tr>
      <tr><td class="area">Approval gate</td><td>Block promotion without approvals, for apps that opt in.</td><td>{chip('Parked', 'info')}</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>How teams run releases now</h2>
  <div class="prose"><p>One idea runs through every tool I looked at: <b>a release is an object with a lifecycle, and a deploy is one event in it.</b> The tools that track releases well create the object early and attach work to it as it happens. The record is a byproduct.</p></div>
  <div class="cards">
    <div class="card"><h3>Linear Releases</h3><p>Releases are continuous or scheduled, and CI attaches issues as commits land. Make the release first and attach work at merge time.</p></div>
    <div class="card"><h3>Jira and Keep a Changelog</h3><p>"Unreleased" is a state teams already use. Tower can show it with no extra input.</p></div>
    <div class="card"><h3>Octopus, Kargo, GitLab</h3><p>The thing that moves between environments has one identity. Each image is a candidate for a release.</p></div>
    <div class="card"><h3>Runway</h3><p>A release has a kickoff, one named pilot and a short checklist, mostly evidence the system already has.</p></div>
    <div class="card"><h3>DORA and ServiceNow</h3><p>External approvals slow delivery and don't lower the change failure rate. Use a light peer sign-off backed by evidence, not a change board.</p></div>
    <div class="card"><h3>LaunchDarkly</h3><p>Deploy and release are separate. The record isn't finished at Healthy: rollbacks and degradation have to flow back in, or the score can't be trusted.</p></div>
  </div>
</section>

<section>
  <h2>Most of a release happens before Tower makes a record</h2>
  {fig1}
  <div class="prose">
    <p><b>Approvals currently come after the fact.</b> An approval added once a release is already healthy in production is really an acknowledgement. Moving sign-off onto the release PR, while gates run, makes it a real decision.</p>
    <p><b>Notes get written as work merges.</b> If the draft builds up from merged PRs, the notes are mostly written by release day.</p>
    <p><b>Picking a candidate needs context.</b> A draft can show every image built since the last release, how long each has run on Ground, and its gate results, side by side.</p>
    <p><b>The draft needs no storage.</b> Everything it shows comes from data Tower already fetches. A file is needed only for what people type, and only once they type it.</p>
    <p><b>Not everything gets a record.</b> The unit is still a release to Flight. It just starts earlier. Every image is a candidate inside a release, not a release of its own.</p>
  </div>
</section>

<section>
  <h2>One branch, one next release</h2>
  <div class="prose"><p>Each Skyport app builds Flight releases from <code>main</code>, with no release branches. Every merge builds an image tagged <code>&lt;version&gt;-&lt;sha&gt;</code> and deploys it to Ground, so every merge produces a candidate. A release is the candidate you choose to promote, plus everything merged before it. Work attaches to the draft at three levels: <b>planned</b> issues on a milestone (optional), <b>incoming</b> open PRs, and <b>scope</b>, the PRs merged since the last release.</p></div>
  {fig2}
  <div class="prose">
    <p><b>Two developers, two features.</b> Both feed the same release. Because main is a single line, you can't ship the later feature without the earlier one. To hold one back, keep its PR open or merge it behind a feature flag, and the record notes the flag.</p>
    <p><b>A nickname, and a version that settles later.</b> Each release gets a name when its draft opens, handed out alphabetically per app the way hurricanes are named: ASTER, BIRCH, CEDAR. It comes from a different word family than image slugs like <code>amber-finch</code>, so people say "CEDAR, shipped as amber-finch". The version is a label, not an identity. The Skyport apps' sealed records show both habits: gate-api bumped its version every release, while baggage-api and boarding-api each shipped the same version twice. So the draft suggests a version from the merged PRs, readiness flags one that hasn't moved, and the seal records the real one.</p>
    <p class="note">A side finding: image slugs come from only four hex characters and a noun list with duplicates, about 1,600 combinations, so slugs will repeat across an app's history. Sequential release names never do.</p>
  </div>
</section>

<section>
  <h2>Five phases on one record</h2>
  {fig3}
  <div class="cards">
    <div class="card"><h3>Glidepath's states, folded in</h3><p>Ready is Glidepath's <code>proposed</code>. Rolling out covers merged, progressing and sync-failed. Aborted covers aborted and degraded. Released, Superseded and Rolled back keep their names.</p></div>
    <div class="card"><h3>One identity across phases</h3><p>A record keyed on <code>app@imageTag</code> can't exist before the image does, so it becomes <code>baggage-api@CEDAR</code>. Existing records keep their file names and get nicknames in date order.</p></div>
    <div class="card"><h3>Where state lives</h3><p>Draft and Candidate are computed. Typed fields go in a draft file once someone writes something. At Healthy the poller seals the record as it does today, and the outcome is added once, when the bake window ends.</p></div>
  </div>
</section>

<section>
  <h2>What it looks like in Tower</h2>
  <div class="prose"><p>Sealed records keep their list and detail views. Above them goes one live card for the release in progress. This sketch uses illustrative values, not real data.</p></div>
  {MOCK}
</section>

<section>
  <h2>Ten changes, in priority order</h2>
  {imp}
</section>

<section>
  <h2>Schema v2 adds to v1</h2>
  <div class="prose"><p>Every v1 field stays. A v1 file reads as a release with one candidate and no draft history.</p></div>
<pre class="schema"><span class="c"># gitops-&lt;app&gt;/releases/&lt;app&gt;@&lt;release&gt;.yaml  (sealed at Healthy, as today)</span>
schemaVersion: <span class="n">2</span>
id: baggage-api@CEDAR             <span class="c"># assigned when the draft opens, never changes</span>
version: {{ suggested: 1.9.0, shipped: 1.9.0 }}
phase: released                   <span class="c"># draft | candidate | ready | rolling-out | released | superseded | rolled-back</span>
base:       {{ branch: main, commit: 6f1c0aa }}   <span class="c"># scope = merged on main after this</span>
scope:      {{ prs: [212, 215, 217, …], issues: ["#198", "#203"] }}
candidates:
  - {{ tag: 1.9.0-a41f9c2, slug: amber-finch, groundSoak: 26h, chosen: true }}
  - {{ tag: 1.8.2-4c1e9a0, slug: quiet-heron, chosen: false }}
readiness:  {{ items: [{{ id: guardrails, ok: true, auto: true }}, …], score: 92 }}
signoffs:   [{{ role: qa, via: "gitops PR review", before: merge }}]
notes:      {{ internal: …, public: …, knownIssues: […] }}
risk:       {{ suggested: medium, confirmed: low, rollbackTo: v1.8.2 }}
outcome:    {{ state: clean, slo24h: met, slo7d: met }}
<span class="c"># + every v1 field: deployments, promotionChain, guardrails, pipelineRuns, testResults, humanContext …</span></pre>
  <p class="note">The draft file lives at <code>glidepath/releases/next.yaml</code> in the source repo, created only when someone edits the draft. Pushes that touch only <code>glidepath/</code> already skip builds. One thing to check first: the lower-environments ApplicationSet must not treat <code>releases/</code> as an environment folder.</p>
</section>

<section>
  <h2>Four stages, cheapest and most valuable first</h2>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(190px,1fr))">
    <div class="card"><h3>R1 · Show the release before it ships</h3><p>The draft card with its nickname, scope, incoming PRs, suggested version, candidates and soak time, a display-only checklist and linked issues. Approved to ship alone, with no new storage.</p></div>
    <div class="card"><h3>R2 · Sign off before merging</h3><p>Sign-off from PR reviews, an owner, a notes editor and draft file, and a seal that copies the draft in as schema v2.</p></div>
    <div class="card"><h3>R3 · Record the outcome</h3><p>Rollbacks written back, Readiness and Outcome scores, bake-window SLO checks, and GitHub Releases with a Changelog view.</p></div>
    <div class="card"><h3>R4 · For teams that plan</h3><p>Scheduled releases, Jira keys, a fleet calendar and messages at Ready and Released. The sign-off gate stays parked.</p></div>
  </div>
</section>

<section>
  <h2>What not to build, and what's decided</h2>
  <div class="tbl"><table>
    <thead><tr><th>Not building</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td class="area">An issue tracker</td><td>Link to GitHub Issues, Jira or Linear, and read keys from PR text. The backlog doesn't live in Tower.</td></tr>
      <tr><td class="area">A change advisory board</td><td>One peer sign-off, backed by evidence.</td></tr>
      <tr><td class="area">A record per Ground deploy</td><td>An image is a candidate. A release is what reaches Flight.</td></tr>
      <tr><td class="area">A PR for every draft edit</td><td>Drafts are computed or committed straight to a build-exempt folder. PRs are for sealing and outcome only, which avoids the gate trouble record branches caused in glidepath#83.</td></tr>
    </tbody>
  </table></div>
  <h3>Decided October 13, 2026</h3>
  <ul class="plain">
    <li><b>Naming.</b> Every release gets an alphabetical nickname per app; the version is suggested at draft time and taken from the promoted image at seal. The word list is still to be curated.</li>
    <li><b>Blocking sign-off.</b> No, for now. Sign-off is recorded only.</li>
    <li><b>Issue trackers.</b> GitHub Issues first through closing references in R1, Jira keys in R4.</li>
    <li><b>Ship R1 alone first.</b> Yes: a read-only draft card, with no schema change and no new files.</li>
  </ul>
</section>

<section>
  <h2>Sources</h2>
  <ul class="plain note">
    <li><a href="https://linear.app/docs/releases">Linear: Releases</a></li>
    <li><a href="https://www.atlassian.com/agile/tutorials/versions">Atlassian: Versions in Jira</a> · <a href="https://keepachangelog.com/">Keep a Changelog</a></li>
    <li><a href="https://docs.gitlab.com/ee/user/project/releases/index.html">GitLab: Releases and release evidence</a> · <a href="https://octopus.com/docs/releases/lifecycles">Octopus Deploy: Lifecycles</a> · <a href="https://docs.kargo.io/user-guide/core-concepts/">Kargo: Core concepts</a></li>
    <li><a href="https://docs.runway.team/using-runway/checklists">Runway: Checklists</a></li>
    <li><a href="https://dora.dev/capabilities/streamlining-change-approval/">DORA: Streamlining change approval</a></li>
    <li><a href="https://launchdarkly.com/docs/home/releases/release-pipelines">LaunchDarkly: Release pipelines</a></li>
    <li><a href="https://slsa.dev/spec/v1.1/verification_summary">SLSA: Verification summary attestation</a></li>
  </ul>
</section>
""")
