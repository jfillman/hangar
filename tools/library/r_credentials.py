"""Spec: short-lived cluster credentials for Tower (Oct 10 to 12, 2026)."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, vlab, text, callout

P = Page(
    'tower-cluster-credentials', 'Spec', 'Tower · Spec · Short-lived cluster credentials',
    'No long-lived Kubernetes credential for Tower, anywhere',
    'The spec that replaced Tower\'s never-expiring cluster token with federated tokens that live ten minutes, split its reads from its writes, and closed a bigger hole found on the way.',
    '2026-10-10',
    meta=[('Status', 'phases 0 to 4 done and live, Oct 12, 2026; phase 5 not started'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/tower/credentials/">Tower cluster credentials</a>')],
    lede=('Tower reached the dev cluster with a ServiceAccount token that never expired, copied into four places. '
          'I wanted it gone, not rotated. The spec ended up doing more than that: checking what the token could '
          'really do turned up a path to far more power than a "read-only" identity should have, and that had to '
          'close first.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Phases 0 to 4 live · Oct 12, 2026</span>
  <h2>Tower now holds no long-lived Kubernetes credential.</h2>
  <ul>
    <li><b>Federated, not stored.</b> The dev cluster trusts the prod cluster's ServiceAccount issuer, so Tower presents a token the kubelet minted minutes ago.</li>
    <li><b>Ten minutes at most.</b> The trust rule refuses any token that lives longer.</li>
    <li><b>Reads and writes are different identities.</b> The credential in the pod can't write. A writer token is minted per action and kept only in memory.</li>
    <li><b>A kill switch in seconds.</b> Remove one entry from the trust file and every federated token stops working.</li>
  </ul>
</div>
""")

# Figure 1: before and after.
W, H = 760, 330
b = zone(24, 24, 712, 120, 'Before · one token that never expires, in four places')
copies = [('Dev cluster', 'token Secret'), ('Secrets store', 'planted by hand'), ('Prod cluster', 'synced Secret'), ('Tower', 'process env')]
for i, (n, s) in enumerate(copies):
    x = 40 + i * 176
    b += node(x, 64, 152, 56, n, s, 'external')
    if i:
        b += path([(x - 24, 92), (x - 4, 92)], dashed=True)
b += zone(24, 168, 712, 140, 'After · nothing stored, nothing that lives past ten minutes')
b += node(40, 212, 156, 56, 'Prod issuer', 'public keys only', 'store')
b += node(252, 212, 156, 56, 'Tower pod', 'token from kubelet', 'focal')
b += node(564, 212, 156, 56, 'Dev cluster', 'trusts the issuer', 'backend')
b += path([(196, 240), (248, 240)], 'link') + hlab(196, 248, 240, 'signs')
b += path([(408, 240), (560, 240)], 'accent') + hlab(408, 560, 240, '10 min · audience dev')
b += text(720, 292, 'CEL rules: namespace, two names, lifetime', 10, 400, lib.MUTED, anchor='end', mono=True)
fig1 = P.fig(b, W, H, 'From one stored token to federated tokens',
             'Before, a never-expiring token lived in the dev cluster, a secrets store, the prod cluster and Tower\'s environment. After, the prod cluster signs short-lived tokens, Tower reads one from its pod, and the dev cluster trusts the prod issuer with rules on namespace, identity and lifetime.',
             'The same pattern a managed cloud uses for workload identity, built by hand on two self-managed clusters.')

# Figure 2: the phases.
W2, H2 = 760, 180
c = ''
phases = [('0', 'Close the hole', 'focal'), ('1', 'Verify TLS', 'focal'), ('2', 'Federate reads', 'focal'),
          ('3', 'Split writer', 'focal'), ('4', 'Delete token', 'focal'), ('5', 'Per-user', 'optional')]
for i, (n, t, k) in enumerate(phases):
    x = 24 + i * 120
    c += node(x, 40, 112, 64, t, f'phase {n}', k)
    if i:
        c += path([(x - 8, 72), (x - 1, 72)], 'accent' if k == 'focal' else 'muted', marker=False)
c += text(24, 140, 'Phases 0 to 4 built and live on Oct 12, 2026.', 11, fill=lib.MUTED)
c += text(24, 158, 'Phase 5 carries each person\'s own identity into a write, so RBAC applies per team. It\'s its own spec.', 11, fill=lib.MUTED)
fig2 = P.fig(c, W2, H2, 'Six phases', 'Phase 0 closed the hole, then TLS, federated reads, a split writer identity and deleting the old token. Phase 5, per-user writes, is not started.',
             'Phase 0 didn\'t depend on the rest and closed the larger risk, so it shipped first.')

P.add(f"""
<section>
  <h2>What checking the token turned up</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Finding 0.1</span><h3>"Read-only" wasn't</h3><p>The token could create PipelineRuns in any namespace, and nothing constrained their shape. Chained with a privileged ServiceAccount elsewhere, that was a path to cluster-admin. Worked out from RBAC and config, never exercised.</p></div>
    <div class="card"><span class="eyebrow">Finding 0.2</span><h3>Anyone signed in could use it</h3><p>Re-run and Cancel went from the browser through Backstage's generic Kubernetes proxy, which every signed-in user could reach. That bypassed Tower's ownership check entirely.</p></div>
    <div class="card"><span class="eyebrow">Phase 0</span><h3>Closed first</h3><p>An admission policy pins the exact PipelineRun shape Tower sends. Re-run and Cancel moved to owner-gated backend routes, and the proxy now refuses anything but reads.</p></div>
  </div>
</section>

<section>
  <h2>From a stored token to a federated one</h2>
  {fig1}
</section>

<section>
  <h2>Options considered</h2>
  <div class="tbl"><table>
    <thead><tr><th>Option</th><th>Verdict</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td class="area">Native federation</td><td>{chip('Chosen', 'ok')}</td><td>Nothing stored, nothing new in the request path, the trust file reloads by itself, and claims are checked with CEL.</td></tr>
      <tr><td class="area">Secrets-store dynamic secret</td><td>{chip('Fallback', 'info')}</td><td>Short leases, but the store keeps a standing credential, and every Tower read depends on it being up.</td></tr>
      <tr><td class="area">Pinniped Concierge</td><td>{chip('Fallback', 'info')}</td><td>Same trust model, plus a component with CA-key-level privilege. For clusters whose API server flags can't change.</td></tr>
      <tr><td class="area">A token "minter"</td><td>{chip('Rejected', 'bad')}</td><td>Its bootstrap credential can mint the full-power token, so the risk stays the same.</td></tr>
      <tr><td class="area">Short-lived client certificates</td><td>{chip('Rejected', 'bad')}</td><td>Submitting a request needs a credential first, and certificates can't be revoked.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>It has to work beyond a home lab</h2>
  <div class="prose"><p>The trust model is portable; the mechanism isn't. Managed control planes don't expose API server flags, so Tower picks how it gets a credential cluster by cluster. On the big clouds it's an exchange: the same projected token, traded for a cloud identity with a trust policy on its subject and audience. The reader and writer split carries over as two roles or two federated credentials. What gets coarser is the claim checking, and revocation is slower behind an exchange, because tokens already issued live until they expire.</p></div>
</section>

<section>
  <h2>The phases</h2>
  {fig2}
  <p class="note">One regression on the way, about 21 minutes long: a Backstage proxy quirk sent dev-cluster reads to the prod cluster once the stored token was removed. The local harness never runs in a cluster, so it couldn't have caught it. A small guard fixed it, and a cleaner fix is noted for later.</p>
</section>
""")
