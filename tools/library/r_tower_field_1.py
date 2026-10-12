"""Tower field report I (Sep 14, 2026): Tower judged as an app owner's only console."""
from report import Page, chip
import lib
from panel import panel

P = Page(
    'tower-field-report-1', 'Report', 'Tower · Field report I · The app owner\'s seat',
    'Tower, judged as my only console',
    'Would I give up kubectl, Argo CD and the Tekton dashboard for Tower, for the apps I own? A field report from the app owner\'s seat: four pillars scored, what works, what still sends me elsewhere, and a backlog.',
    '2026-09-14',
    meta=[('Basis', 'a read of the Tower source, its git history and its handoff notes'),
          ('Follow-up', '<a href="https://hangarplatform.dev/library/tower-field-report-2/">Field report II</a>, October 11, 2026')],
    lede=('Tower set out to be the one place an app owner goes. So I sat in that seat and asked a blunt question: '
          'for the apps I own, end to end, would I actually give up kubectl, Argo CD, the Tekton dashboard and a '
          'release tool for this? I scored each one on three things: can I see it, can I change it, and does Tower '
          'give me enough to own the outcome without leaving.'))

P.add("""
<div class="verdict">
  <span class="stamp">Mostly for looking · not yet for acting</span>
  <h2>The visibility problem is solved. The authority problem is next.</h2>
  <p>Tower already answers "where do I go to see what's happening": one URL, one app, nine tabs, real data from Kubernetes, Tekton, Argo CD, GitHub and Prometheus. The acting half is thinner. Promote and Config edits are real, careful write paths, but there's no rollback, no way to unstick Argo CD, no re-run of a failed pipeline, and no restart on a workload. Those are exactly the moments an owner reaches for a console under pressure.</p>
</div>
""")

body, h = panel([
    ('Kubernetes cluster access', 'replaces kubectl and cluster dashboards', 'Partial', ('full', 'none', 'half'), None),
    ('Argo CD', 'replaces the Argo CD UI', 'Partial', ('full', 'half', 'half'), None),
    ('CI/CD', 'replaces the Tekton dashboard', 'Strong', ('full', 'none', 'half'), None),
    ('Release management', 'replaces a release tool', 'Gap', ('full', 'half', 'none'), None),
])
fig = P.fig(body, 760, h + 20, 'Four pillars, scored on see, change and own',
            'Kubernetes access: full visibility, almost no change, half ownership. Argo CD: full, half, half. CI/CD: full, almost none, half. Release management: full, half, almost none.',
            'Every pillar is fully visible. Change is where the gaps are: there was no exec, restart, sync, re-run or rollback anywhere in the module.')

BACKLOG = [
    ('Quick wins', [
        ('Retire or wire up the Overview monitoring placeholder', 'The one visible "not wired up yet" left after the SLOs tab shipped past it.', 'Honest links to each environment\'s Grafana'),
        ('Force sync wherever sync status already shows', 'The delivery timeline already tracks sync state with real care. Add the action Argo CD leads with.', 'Refresh, sync, force sync and terminate'),
        ('Re-run a failed PipelineRun', 'The run list and DAG are there. One Tekton call is missing.', 'Re-run and cancel'),
    ]),
    ('Near-term', [
        ('Rollback, as a mirror of Promote', 'The Release Matrix knows every past release per environment; point Promote at the previous row.', 'Rollback PRs, and pin restore for cloud targets'),
        ('One "everything that changed" timeline per app', 'Fold config PRs and promotions into the release timeline that already exists.', 'Recent Activity covers release, config, rollout, rollback and images'),
        ('Wire SLO burn-rate breaches to a notification', 'The math and the channel both exist; they\'d never been connected.', 'SLO transition notifications, three signals'),
        ('CPU and memory trends beside requests and limits', 'The Prometheus hook and the chart style already exist from SLOs.', 'Per-pod metrics in Topology'),
    ]),
    ('Strategic', [
        ('A real per-app authorization model', 'Anyone signed in could Promote or edit Config. The only gate was GitHub review, which Tower couldn\'t see.', '18 permissions, owners and admins, grant-only Flight actions, audited'),
        ('Pod exec, restart and scale, behind that model', 'The biggest reason an owner still opens a terminal, and the action with the most blast radius.', 'Break-glass debug containers instead of exec, two-person on Flight'),
        ('Attached components (a database, a broker)', 'Left out of the Config tab\'s first version on purpose.', 'A Components sub-tab built from Airframe\'s XRD schemas'),
        ('Secret rotation as an action', 'Config rightly never shows a value, but there\'s no way to rotate one either.', None),
    ]),
]
rows = ''
for tier, items in BACKLOG:
    rows += f'<h3>{tier}</h3><div class="track">'
    for t, why, done in items:
        c = chip('Done by Oct 11, 2026', 'ok') if done else chip('Still open', 'warn')
        res = f' <b>Since:</b> {done}.' if done else ' <b>Since:</b> still Infisical project links only.'
        rows += f'<div class="row"><h3>{t}</h3>{c}<p>{why}{res}</p></div>'
    rows += '</div>'

P.add(f"""
<section>
  <h2>The instrument panel</h2>
  {fig}
</section>

<section>
  <h2>Signal and noise</h2>
  <div class="tbl"><table>
    <thead><tr><th>Genuinely works</th><th>Still sends me elsewhere</th></tr></thead>
    <tbody>
      <tr><td><b>One app, one URL, nine tabs.</b> Overview, PRs, CI/CD, Releases, Topology, Images, SLOs, Notifications and Config, with no plugin-hopping.</td><td><b>No rollback.</b> A bad release only moves forward; reverting means a hand-built PR.</td></tr>
      <tr><td><b>PR context everywhere.</b> State, CI and review status ride on the same button wherever a PR matters.</td><td><b>No exec, port-forward, restart or scale.</b> Every "act on the workload" moment means a terminal.</td></tr>
      <tr><td><b>Config edits are real GitOps.</b> Form fields where they fit, a YAML editor where they don't, and every save checked against the chart's schema before it becomes a PR.</td><td><b>No manual sync or re-run.</b> Both are read-only observation decks.</td></tr>
      <tr><td><b>SLOs are the real thing.</b> Multi-window burn rates from live Prometheus, with a plain-language explainer.</td><td><b>No app-level authorization.</b> Who may promote to prod is whatever branch protection says, invisible to Tower.</td></tr>
      <tr><td><b>Shared plumbing.</b> One cluster-aware fetch backs Topology, logs, events and Tekton polling.</td><td><b>No single audit trail.</b> Config PRs, promotions and deploys each leave their own trace somewhere else.</td></tr>
      <tr><td><b>A fleet view too.</b> The Fleet Grid and Ops Wall answer "how's everything doing".</td><td><b>Secrets, attached infrastructure and cost</b> stay out of scope.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>The backlog, and what happened to it</h2>
  <p class="note">Ordered by how directly each item closed the gap between looking and acting. Every item extended a pattern the code already had. The "since" notes come from <a href="https://hangarplatform.dev/library/tower-field-report-2/">Field report II</a>, four weeks later.</p>
  {rows}
</section>
""")
