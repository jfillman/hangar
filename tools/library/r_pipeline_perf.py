"""Glidepath pipeline performance review (Oct 8, 2026, closed Oct 9)."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, text, callout

P = Page(
    'glidepath-pipeline-performance', 'Report', 'Glidepath · Report · Pipeline performance',
    'Where does a Glidepath pipeline spend its time?',
    'Three weeks of Tekton history, measured: where the wall-clock goes in every Glidepath pipeline, nine fixes ranked by gain over effort, and what each one did once it shipped.',
    '2026-10-08',
    meta=[('Evidence', '1,596 PipelineRuns and 7,414 TaskRuns from Tekton Results, Sep 17 to Oct 9, 2026'),
          ('Closed', 'October 9, 2026')],
    lede=('Builds felt slow, and I didn\'t want to guess why. So I pulled every PipelineRun from Tekton Results and '
          'measured where the time went. The answer surprised me: outside the build itself, most of a pipeline\'s '
          'wall-clock was pods starting up to do almost nothing.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">8 of 9 done · closed Oct 9, 2026</span>
  <h2>Most of the time was overhead, not work.</h2>
  <p>The build stage is the only pipeline where most of the wall-clock is real work. In most of the others, more than three quarters of the time went to scheduling pods and starting containers. Eight of the nine recommendations shipped the next day without dropping a single result, event or gate. The ninth, building amd64 images under emulation, is deferred, and it's still the biggest remaining cost.</p>
</div>
""")

# Figure 1: wall-clock p50 per pipeline, split into step work and overhead.
data = [('build', 476, 363), ('test', 176, 76), ('deploy', 116, 27), ('release', 151, 23),
        ('image-scan-check', 122, 36), ('provenance-check', 115, 64), ('sast-check', 94, 21),
        ('sbom-check', 85, 18), ('governance-check', 77, 10), ('image-promotion', 150, 92),
        ('release-notify', 53, 11)]
W, H = 760, 404
X0, SC, Y0, RH = 196, 0.9, 40, 28
b = text(24, 24, 'P50 WALL-CLOCK, SECONDS', 8, 500, lib.MUTED, mono=True, ls='0.14em')
for i, (name, wall, work) in enumerate(data):
    y = Y0 + i * RH
    b += text(X0 - 12, y + 14, name, 11, 400, lib.INK, anchor='end', mono=True)
    b += f'<rect x="{X0}" y="{y + 2}" width="{wall * SC:g}" height="16" rx="2" fill="rgba(27,31,36,0.05)" stroke="rgba(27,31,36,0.16)" stroke-width="0.8"/>'
    b += f'<rect x="{X0}" y="{y + 2}" width="{work * SC:g}" height="16" rx="2" fill="rgba(185,121,31,0.55)"/>'
    b += text(X0 + wall * SC + 8, y + 14, f'{wall}s · {round(100 * work / wall)}% work', 10, 400, lib.MUTED, mono=True)
b += lib.legend(H - 24, [('focal', 'step work'), ('store', 'scheduling and start-up')], W)
fig1 = P.fig(b, W, H, 'Work versus overhead per pipeline',
             'Median wall-clock per Glidepath pipeline, split into step work and overhead. Build is 76 percent work; deploy is 23 percent; release 15; governance-check 13.',
             'Amber is time spent running steps. The rest is pods being scheduled, init containers, result propagation and the reconcile loop.')

# Figure 2: one stage before and after item 3.
W2, H2 = 760, 264
c = zone(24, 24, 712, 96, 'Before · one stage, 13 pods')
for i in range(13):
    kind = 'focal' if i in (5, 6) else 'store'
    c += f'<rect x="{40 + i * 52}" y="60" width="44" height="40" rx="5" fill="{lib.KINDS[kind][0]}" stroke="{lib.KINDS[kind][1]}" stroke-width="1"/>'
c += text(736 - 12, 112, 'amber: pods doing the real work', 10, 400, lib.MUTED, anchor='end', mono=True)
c += zone(24, 144, 712, 96, 'After · preflight, the work, debrief')
c += node(40, 176, 148, 48, 'preflight', 'was 4 to 6 pods', 'store')
c += node(212, 176, 148, 48, 'the real work', 'unchanged', 'focal')
c += node(384, 176, 148, 48, 'debrief', 'was 5 to 6 pods', 'store')
c += path([(188, 200), (208, 200)]) + path([(360, 200), (380, 200)])
c += callout(556, 196, '13 pods to 4.')
c += callout(556, 220, '258 to 409s down to 129s.')
fig2 = P.fig(c, W2, H2, 'Collapsing the zero-work pods',
             'Before, a stage ran thirteen pods, most doing under two seconds of work each. After, a preflight task and a debrief task replace eleven of them.',
             'Item 3: every Task result and CDEvent kept its name, so nothing downstream changed. Measured on a real function build.')

ITEMS = [
    ('1', 'Stop building amd64 under emulation when nothing runs it', 'The amd64 leg is cross-built under QEMU and is the slowest step on the platform: p90 664 seconds, worst case 46 minutes.', 'Deferred', 'info', 'Backstage\'s build is still 25 minutes, 11 of them here.'),
    ('2', 'Fix the dependency cache keys', 'npm and Maven caches were keyed on the whole lockfile, so any dependency bump started from empty.', 'Done', 'ok', 'One shared cache directory per tool, also mounted for unit tests.'),
    ('3', 'Collapse the zero-work pods', 'Four to six pods before the work and five to six after, each paying a 14-second start-up tax to do under two seconds of work.', 'Done', 'ok', '13 pods to 4; a function build from 258-409s to 129s.'),
    ('4', 'One vulnerability analysis per image', 'Every scan pulled a 120 MiB database, and each image was analysed three times.', 'Done', 'ok', 'A shared Trivy server: the scan step takes 4 seconds.'),
    ('5', 'Make release gates cheap and reliable', 'Four gates full-cloned a repo to read one file, and one failed 48 percent of the time for a reason unrelated to security.', 'Done', 'ok', '135 of 284 failures were Release Record PRs, now excluded. A stub check retired (ADR-0025).'),
    ('6', 'Turn off the Affinity Assistant on one node', 'A StatefulSet and a placeholder pod per run, buying nothing on a single node.', 'Done', 'ok', '10 to 25 seconds and one StatefulSet less per run.'),
    ('7', 'Shallow clones in the write-side tasks', 'Eight tasks cloned full history to push one commit.', 'Done', 'ok', 'Target resolution reads the file over the API: 1 second.'),
    ('8', 'Tell Argo CD about a dev deploy', 'A pushed deploy sat unseen for up to two minutes waiting for the next poll.', 'Done', 'ok', 'A hard refresh, scoped by an admission policy: picked up in 4 seconds.'),
    ('9', 'Semgrep rule fetch', 'Rules downloaded and metrics posted on every scan.', 'Partly', 'warn', 'Metrics off. The fetch turned out to be under a second, so vendoring was dropped.'),
]
rows = ''.join(f'<div class="row"><h3>{n}. {t}</h3>{chip(st, tone)}<p>{why} <b>Result:</b> {res}</p></div>' for n, t, why, st, tone, res in ITEMS)

P.add(f"""
<section>
  <h2>Where the time goes</h2>
  {fig1}
  <div class="prose"><p>Across all 7,414 TaskRuns, the gap between a TaskRun starting and its first step running was 14 seconds at the median, 40 at p90 and 105 at p99. That tracked node load, not pipeline design: the daily p90 swung from 15 seconds to almost six minutes.</p></div>
</section>

<section>
  <h2>Nine fixes, ranked by gain over effort</h2>
  <p class="note">Each one had to keep every existing feature, result name, event and gate.</p>
  <div class="track">{rows}</div>
</section>

<section>
  <h2>The biggest one, drawn</h2>
  {fig2}
</section>

<section>
  <h2>What caps every number above</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Environment</span><h3>A control plane under pressure</h3><p>The scheduler and controller manager restarted 120 times in 16 days on lease timeouts. Each restart stalls scheduling for the whole cluster.</p></div>
    <div class="card"><span class="eyebrow">Fixed at close</span><h3>Step pods were BestEffort</h3><p>No requests on any Tekton container meant the lowest CPU share under contention. A cluster default now gives every step a small request.</p></div>
    <div class="card"><span class="eyebrow">Found on the way</span><h3>Three bugs nobody had seen</h3><p>Builds skipped when the pushed head was a merge commit, a grant that could have rewritten an Application, and a fallback to defaults on an unknown revision.</p></div>
  </div>
</section>
""")
