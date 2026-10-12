"""Crossplane v2 vocabulary review (Oct 5, 2026): why "claim" left Hangar's writing."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, text, callout

P = Page(
    'crossplane-v2-vocabulary', 'Review', 'Hangar · Review · Crossplane v2 vocabulary',
    'Is "claim" the right word in a Crossplane v2 world?',
    'A review of ChatGPT\'s analysis of the word "claim" across Hangar\'s site and docs, what I changed, and what I left alone.',
    '2026-10-05',
    meta=[('Scope', 'the site, Hangar docs, Autopilot code and docs, Airframe docs'),
          ('Acted on in', 'hangar#32, hangar#33, autopilot#5, airframe#50')],
    lede=('I use Crossplane v2 exclusively, and one word kept rubbing me the wrong way: "Ephemeral runs are claims to '
          'Crossplane." I asked ChatGPT to analyse it, then had Claude check that analysis against the v2 docs and '
          'every repo. This is what held up, what didn\'t, and what changed.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Done · all four PRs merged Oct 5, 2026</span>
  <h2>"Claim" was the wrong word. "Direct request" says what's actually different.</h2>
  <p class="prose">Crossplane v2 removed Claims: namespaced XRs don't need them, and only <code>LegacyCluster</code> XRs from v1 XRDs still support them. So a Crossplane reader who sees "AgentRun claim" assumes v1 indirection that Hangar never used. The fix was mostly words, because nothing in Hangar was ever built on Claims.</p>
  <ul>
    <li><b>Principle, now:</b> Durable changes are git commits. Ephemeral runs are direct requests to Crossplane.</li>
    <li><b>Any Crossplane object</b> is an XR (a namespaced composite resource), never a claim.</li>
    <li><b>Autopilot's narrow-only request</b> is called <i>requested limits</i> (<code>LimitRequest</code> in code, passed as <code>limits</code>).</li>
  </ul>
</div>
""")

# Figure 1: v1 versus v2. Figures are drawn at 760 wide, the page's column, so text is 1:1.
W, H = 760, 280
b = zone(24, 24, 346, 228, 'Crossplane v1')
b += node(40, 72, 92, 56, 'Claim', 'namespaced', 'input')
b += node(150, 72, 92, 56, 'XR', 'cluster-scoped', 'backend')
b += node(260, 72, 92, 56, 'Resources', 'composed', 'store')
b += path([(132, 100), (146, 100)]) + path([(242, 100), (256, 100)])
b += text(40, 168, 'A Claim let a namespaced team ask for a', 11, fill=lib.MUTED)
b += text(40, 186, 'cluster-scoped XR without cluster access.', 11, fill=lib.MUTED)
b += callout(40, 228, 'The indirection the word implies.')
b += zone(390, 24, 346, 228, 'Crossplane v2 · what Hangar uses')
b += node(406, 72, 120, 56, 'XR', 'namespaced', 'focal')
b += node(606, 72, 114, 56, 'Resources', 'composed', 'store')
b += path([(526, 100), (602, 100)], 'accent') + hlab(526, 602, 100, 'composes')
b += node(406, 156, 120, 44, 'Claim', None, 'optional')
b += lib.stopx(500, 178, lib.MUTED)
b += text(542, 174, 'Removed. Only LegacyCluster', 11, fill=lib.MUTED)
b += text(542, 192, 'XRs from v1 XRDs keep it.', 11, fill=lib.MUTED)
b += callout(406, 236, 'All 17 Airframe XRDs are v2 and namespaced.')
fig1 = P.fig(b, W, H, 'Crossplane v1 and v2 resource paths',
             'In v1 a namespaced Claim pointed at a cluster-scoped XR, which composed resources. In v2 a namespaced XR composes resources directly, and Claims are gone.',
             'v1 needed a Claim in front of a cluster-scoped XR. v2 makes the XR itself namespaced, so the Claim has nothing left to do.')

# Figure 2: the two planes.
W2, H2 = 760, 320
c = ''
for y, label, row in ((24, 'Durable · reviewed and replayable',
                       [('Person or agent', 'proposes', 'propose', None), ('Reviewed commit', 'git', 'focal', 'only path'),
                        ('Argo CD', 'applies', 'backend', None), ('App XR', 'Airframe, lives in git', 'backend', None)]),
                      (164, 'Ephemeral · bounded and audited',
                       [('Agent', 'asks to run', 'propose', None), ('Clearance', 'policy gate', 'security', None),
                        ('K8s API', 'direct request', 'backend', None), ('AgentRun XR', 'deadline, then gone', 'backend', None)])):
    c += zone(24, y, 712, 116, label)
    xs, ws = (40, 212, 400, 556), (120, 136, 104, 176)
    for (name, sub, kind, tag), x, w in zip(row, xs, ws):
        c += node(x, y + 40, w, 56, name, sub, kind, tag=tag)
    m = y + 68
    c += path([(160, m), (208, m)], 'link') + path([(348, m), (396, m)], 'accent') + path([(504, m), (552, m)])
c += hlab(348, 396, 232, 'limits')
c += text(40, 304, 'Both planes end in an XR. What differs is the path, so the principle names the path.', 11, fill=lib.MUTED)
fig2 = P.fig(c, W2, H2, 'Hangar\'s two planes',
             'Durable changes go from a person or agent through a reviewed git commit and Argo CD to an Airframe XR. Ephemeral runs go from an agent through the Clearance policy gate as a direct request to the Kubernetes API, creating an AgentRun XR with a deadline.',
             'Why "Ephemeral runs are Crossplane XRs" doesn\'t work: durable apps are XRs too. A run is different because it skips the commit, so it\'s a direct request.')

P.add(f"""
<section>
  <h2>What changed in v2</h2>
  <div class="prose"><p>The whole reason for a Claim was that v1 XRs were cluster-scoped. Namespaced XRs remove that reason, and v2 removes Claims with it. Every Airframe XRD and the draft <code>AgentRun</code> XRD are <code>apiextensions.crossplane.io/v2</code>, <code>scope: Namespaced</code>, with no <code>claimNames</code>.</p></div>
  {fig1}
</section>

<section>
  <h2>Where the analysis was right, and where it slipped</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Right</span><h3>The core point</h3><p>"Claim" signals v1 to anyone who knows Crossplane. The v2 docs say it plainly: namespaced XRs don't support claims.</p></div>
    <div class="card"><span class="eyebrow">Overstated</span><h3>It's prose, not the model</h3><p>Nothing in Hangar was built on Claims. "Kubernetes API for AgentRun claims" in a README is wording, not an implementation choice.</p></div>
    <div class="card"><span class="eyebrow">Missed</span><h3>Its favourite fix</h3><p>"Ephemeral runs are Crossplane XRs" doesn't separate the planes, because durable apps are XRs too. The difference is the path.</p></div>
    <div class="card"><span class="eyebrow">Missed</span><h3>How far it went</h3><p>The word was all over the site: the glossary, the stack page, the cost essay's rule of thumb and the overview diagrams.</p></div>
    <div class="card"><span class="eyebrow">Missed</span><h3>Two meanings in Autopilot</h3><p>One was the <code>AgentRun</code>. The other was the narrow-only request in code, which also applies to local sessions and child spawns. It needed its own name.</p></div>
  </div>
</section>

<section>
  <h2>The two planes, named by their path</h2>
  {fig2}
</section>

<section>
  <h2>What changed</h2>
  <div class="tbl"><table>
    <thead><tr><th>Before</th><th>After</th></tr></thead>
    <tbody>
      <tr><td>Ephemeral runs are claims to Crossplane.</td><td>Ephemeral runs are direct requests to Crossplane.</td></tr>
      <tr><td>AgentRun claim</td><td>AgentRun XR, or just AgentRun</td></tr>
      <tr><td>Glossary: Claim</td><td>Glossary: XR, with a note that v1 put a Claim in front of it</td></tr>
      <tr><td>A claim says what you want; reconciliation keeps it true.</td><td>An XR says what you want; reconciliation keeps it true.</td></tr>
      <tr><td>If you'd be upset that it changed back, it's a claim.</td><td>If you'd be upset that it changed back, it's an XR.</td></tr>
      <tr><td><code>Claim</code> and <code>claim=</code> in Autopilot's code</td><td><code>LimitRequest</code> and <code>limits=</code>, called requested limits in prose</td></tr>
      <tr><td>Diagram labels CLAIM and "claims · ttl"</td><td>API and "XRs · ttl"</td></tr>
    </tbody>
  </table></div>
  <p class="note">Left alone, because the word is plain English there: "every claim is labelled Built", the SLO compare-and-set claim, token and OIDC claims, <code>SandboxClaim</code> (a real agent-sandbox kind), and the dated Sep 27, 2026 architecture review, which is a point-in-time record.</p>
</section>

<section>
  <h2>Tracking</h2>
  <div class="track">
    <div class="row"><h3>Site and Hangar docs</h3>{chip('Merged · hangar#32', 'ok')}<p>Principle, glossary, stack page, cost essay, overview diagrams.</p></div>
    <div class="row"><h3>Autopilot code and docs</h3>{chip('Merged · autopilot#5', 'ok')}<p>AgentRun is an XR; <code>Claim</code> renamed <code>LimitRequest</code>, passed as <code>limits</code> on <code>session_open</code> and <code>run.spawn</code>.</p></div>
    <div class="row"><h3>Airframe docs</h3>{chip('Merged · airframe#50', 'ok')}<p>The Skyport demo walkthrough, plus a chart CI fix that rode along.</p></div>
    <div class="row"><h3>Glossary note</h3>{chip('Merged · hangar#33', 'ok')}<p>Why the code once said <code>claim</code>.</p></div>
  </div>
</section>
""")
