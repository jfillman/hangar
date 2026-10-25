"""Tower field report II (Oct 11, 2026): the same question, 27 days and every Hangar repo later."""
from report import Page, chip, tick, BAD
import lib
from lib import node, zone, text, callout, stopx
from panel import panel

P = Page(
    'tower-field-report-2', 'Report', 'Tower · Field report II · The app owner\'s seat, 27 days on',
    'Tower, judged again as my only console',
    'The same question as the first field report, with a wider lens: across every Hangar repo, would I give up my other tools for Tower, and would I trust it to carry production?',
    '2026-10-11',
    meta=[('Basis', 'main branch of nine repos, plus the docs'),
          ('Previous', '<a href="https://hangarplatform.dev/library/tower-field-report-1/">Field report I</a>, September 14, 2026')],
    lede=('Four weeks after the first report I sat in the same seat and asked the same question. The answer moved a '
          'long way. What\'s left isn\'t a missing button any more. It\'s the ground the console stands on.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Yes for looking · now yes for acting</span>
  <h2>The console is finished enough. The platform under it is the next report.</h2>
  <ul>
    <li>Every gap in the first report but one is closed, and closed the hard way: Tower still holds no Kubernetes write access of its own. Every write goes through Argo CD or a reviewed PR, behind 18 per-app permissions, and every action is audited, refusals included.</li>
    <li>Rollback, Rollout controls, force sync, terminate, pod restart, image cleanup and a two-person break-glass debug container all exist, and I tested them in a browser this week.</li>
    <li>What still sends me elsewhere is underneath: the prod cluster has no metrics, prod leans on the dev cluster, gates can't block a merge on GitHub's free plan, and nothing is backed up.</li>
  </ul>
</div>
""")

OLD = {'k8s': ('full', 'none', 'half'), 'argo': ('full', 'half', 'half'), 'ci': ('full', 'none', 'half'), 'rel': ('full', 'half', 'none')}
body, h = panel([
    ('Kubernetes cluster access', 'restart, rollout restart, debug', 'Strong', ('full', 'most', 'most'), OLD['k8s']),
    ('Argo CD', 'refresh, sync, force sync, terminate', 'Strong', ('full', 'full', 'most'), OLD['argo']),
    ('CI/CD', 're-run and cancel; gates advise', 'Strong', ('full', 'most', 'half'), OLD['ci']),
    ('Release management', 'rollback, release records', 'Strong', ('full', 'full', 'most'), OLD['rel']),
    ('Onboarding and environments', 'new this time', 'Strong', ('full', 'most', 'half'), None),
    ('Observability and SLOs', 'new this time', 'Partial', ('half', 'most', 'half'), None),
    ('Identity and security', 'new this time', 'Partial', ('most', 'most', 'half'), None),
    ('Platform resilience', 'new this time', 'Gap', ('half', 'none', 'none'), None),
])
body += text(24, h + 22, 'The dark tick on each of the first four bars marks where it stood on September 14, 2026.', 10, 400, lib.MUTED, mono=True)
fig1 = P.fig(body, 760, h + 40, 'Eight pillars, then and now',
             'The four original pillars all moved to Strong, with ticks showing their September positions. Four new pillars: onboarding is Strong, observability and identity are Partial, platform resilience is a Gap.',
             'Release management moved furthest, from a gap to strong. The four new pillars are the ones that now decide the answer.')

# Figure 2: the floor under the console.
W, H = 760, 300
b = zone(24, 24, 712, 76, 'The console')
b += node(40, 48, 680, 40, 'Tower', 'delegated writes only · 18 permissions · every action audited', 'focal')
b += zone(24, 124, 712, 132, 'The floor under it, on October 11, 2026')
floor = [('Prod metrics', 'Prometheus at zero', 'x'), ('Prod on dev', 'secrets, bootstrap', 'x'),
         ('Gates', 'advise, can\'t block', 'x'), ('Backups', 'none at all', 'x'),
         ('Cluster token', 'closed Oct 12, 2026', 'ok')]
for i, (n, s, m) in enumerate(floor):
    x = 40 + i * 136
    b += node(x, 160, 120, 52, n, s, 'backend' if m == 'ok' else 'store')
    b += tick(x + 60, 232) if m == 'ok' else stopx(x + 60, 232, BAD)
b += callout(24, 286, 'None of this is Tower\'s code. Tower is just where I\'d find out.')
fig2 = P.fig(b, W, H, 'The floor under the console',
             'Tower on top. Underneath: prod has no metrics, prod depends on the dev cluster, gates advise but cannot block, and there are no backups. The over-powered cluster token was closed the day after this report.',
             'Four of these are platform work, and they\'re now the backlog. The fifth, the cluster token, was closed the next day by the credentials spec.')

def tier(name, items):
    out = f'<h3>{name}</h3><div class="track">'
    for t, why, st in items:
        c = chip('Done ' + (st[5:] or 'Oct 12, 2026'), 'ok') if st.startswith('done') else chip('Open', 'warn')
        out += f'<div class="row"><h3>{t}</h3>{c}<p>{why}</p></div>'
    return out + '</div>'

backlog = tier('Quick wins', [
    ('Close the Kubernetes proxy hole first', 'The read token behind the portal could do far more than read, and any signed-in user could reach it through a generic proxy. Phase 0 of the credentials spec closed it.', 'done'),
    ('Give Flight environments a Prometheus to read', 'Until then SLOs, pod metrics and canary analysis are empty for exactly the environments an owner cares about.', 'open'),
    ('Decide on scale, then close the question', 'Durable scale already exists as a values PR. My recommendation: no runtime scale, and say so.', 'open'),
    ('Finish break-glass hygiene on Flight', 'A signed debug image, an image policy scoped to debug containers, and a cleanup backstop in the cluster.', 'open'),
    ('Confirm the image cleanup token really synced', 'If it never did, the Images tab\'s one write action is dead on prod.', 'open'),
    ('Show test results where releases are judged', 'Testkube results belong on the Release Record and the pipeline row. Tower v0.79 and v0.80 put every attested test run on the image, a Tests view on Pipelines, and the test evidence on the Release Record.', 'done Oct 19, 2026'),
]) + tier('Near-term', [
    ('Short-lived cluster credentials for Tower', 'Replace the never-expiring token with federated ten-minute tokens and split reads from writes.', 'done'),
    ('Verify image signatures at admission', 'If a merge can\'t be blocked, admission is the only place an unsigned image can be refused.', 'open'),
    ('Platform health on the Ops Wall', 'The webhook relay, the tunnels and each cluster\'s reachability, before an app looks wrong.', 'open'),
    ('Decommission a Flight environment from Tower', 'Ground removal is a confirmed PR. Flight removal is still a manual XR delete with a data-loss history.', 'open'),
    ('Break-glass phase 4', 'Self grants, review-due tracking, an in-Tower recording player and retention.', 'done'),
]) + tier('Strategic: the review\'s remaining production gates', [
    ('A management cluster', 'Move bootstrap Crossplane, the secrets store and Backstage off the dev cluster so prod stops sharing its fate.', 'open'),
    ('A GitHub organization, Apps and SSO', 'Retire the personal token, generate rulesets so gates block for real, and put sign-in in front of everything.', 'open'),
    ('Backup, restore, and a drill', 'Cluster state, databases, the audit bucket and the secrets store\'s root key. One drill a quarter.', 'open'),
    ('A production-readiness scorecard', 'The Airframe scorecard climbed because it was measured every week. Give SSO, DR and platform SLOs the same treatment.', 'open'),
    ('Cloud targets to parity, or labelled preview', 'One live Lambda smoke test; the other targets are render-tested only.', 'open'),
])

P.add(f"""
<section>
  <h2>The original four, then and now</h2>
  {fig1}
  <div class="prose"><p>The biggest move is release management. Roll back opens a rollback release PR against a healthy earlier release, where integrity gates block and content gates only advise, and I tested abort and retry live on a Skyport app's staging. Release state is now built from the Rollout's own facts (ADR-0021) instead of hook Jobs. And the plain-language troubleshooting banner on Deployments is the single best reason I no longer open the Argo CD UI for an app I own.</p></div>
</section>

<section>
  <h2>The floor under the console</h2>
  {fig2}
</section>

<section>
  <h2>Signal and noise</h2>
  <div class="tbl"><table>
    <thead><tr><th>Genuinely works</th><th>Still sends me elsewhere</th></tr></thead>
    <tbody>
      <tr><td><b>Delegated authority.</b> Every runtime action is an Argo CD call through one account with three narrow roles; every durable change is a PR.</td><td><b>Prod has no metrics.</b> The prod cluster's Prometheus is scaled to zero for capacity, which empties three tabs for Flight.</td></tr>
      <tr><td><b>Break-glass done better than exec.</b> A debug container, a copy of the pod by default, cluster guardrails, a recording, and two people on Flight.</td><td><b>Prod depends on the dev cluster.</b> Secrets, bootstrap Crossplane and part of Tower's read path live there.</td></tr>
      <tr><td><b>Troubleshooting in sentences.</b> An ordered rule table turns Argo CD, Rollout, pod and event signals into one line and a first thing to try.</td><td><b>Gates can't block.</b> On GitHub's free plan the platform audits a bypass; it can't prevent one.</td></tr>
      <tr><td><b>Environments as one model.</b> Tower stages edits and opens exactly the PRs needed, in order.</td><td><b>Identity is one person.</b> The authorization model is ready for teams; the identity layer under it isn't.</td></tr>
      <tr><td><b>Honesty as a feature.</b> Published known-gaps lists, 25 ADRs, and docs that say "verified" or "not verified".</td><td><b>No backup or restore.</b> The architecture review called it, and nothing has moved.</td></tr>
      <tr><td><b>Tests exist now.</b> The review found none; Tower now has 62 test files and the backend 33.</td><td><b>Not built yet:</b> runtime scale, Flight removal, two cloud targets, DORA on the Ops Wall, and the Autopilot tab.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>The backlog, ordered by what unblocks trusting prod</h2>
  <p class="note">The first report's backlog was about adding levers. This one is about the floor under them. Three items were done the day after it was written.</p>
  {backlog}
</section>
""")
