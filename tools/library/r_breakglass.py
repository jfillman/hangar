"""Spec: break-glass debug access to Flight pods from Tower (Oct 10 to 12, 2026), with its test plan."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, vlab, text, callout

P = Page(
    'tower-break-glass', 'Spec', 'Tower · Spec · Break-glass debug access',
    'Looking inside a production pod, without ever handing out exec',
    'The spec for break-glass in Tower: why a debug container beats exec, the two-person flow, the guardrails that live in the cluster rather than the portal, and the plan for testing it with two people.',
    '2026-10-10',
    meta=[('Status', 'phases 1 to 4 built and live on both clusters, Oct 12, 2026'),
          ('Test plan', 'October 12, 2026'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/tower/break-glass/">Tower break-glass guide</a>')],
    lede=('Tower\'s write actions are delegated and reviewed, so pod exec was never going to be a standing feature. But '
          'mid-incident an owner sometimes needs a process list, a DNS lookup from the pod\'s network, or a file the app '
          'wrote, and no log line answers it. This is the spec for doing that safely: short, approved, recorded, and '
          'enforced by the cluster itself.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Built · live on both clusters</span>
  <h2>Never exec on Flight. Two debug modes, a second person, and a recording of every byte.</h2>
  <ul>
    <li><b>Copy mode</b> debugs a copy of the pod that takes no traffic. <b>Live mode</b> adds a debug container to the running pod, for problems a copy can't reproduce.</li>
    <li>On Flight, a second person approves. An admin can "break the glass" alone, and that session is broadcast and owes a review.</li>
    <li>Every guardrail that matters is an admission policy, so it holds even if Tower is wrong.</li>
  </ul>
</div>
""")

# Figure 1: the flow.
W, H = 760, 300
b = zone(24, 24, 712, 116, 'Tower')
steps = [('Request', 'owner, reason', 'propose'), ('Approve', 'another person', 'security'),
         ('Session', 'recorded', 'focal'), ('End', 'pod recycled', 'backend'), ('Review', 'record and hash', 'store')]
for i, (n, s, k) in enumerate(steps):
    x = 40 + i * 140
    b += node(x, 64, 116, 56, n, s, k)
    if i:
        b += path([(x - 24, 92), (x - 4, 92)], 'accent' if i == 2 else 'muted')
b += zone(24, 164, 712, 112, 'The cluster')
b += node(100, 200, 196, 52, 'RoleBinding', 'TTL, deleted at the end', 'backend')
b += node(320, 200, 168, 52, 'Debug container', 'pinned, signed image', 'focal')
b += path([(238, 120), (238, 196)], 'accent') + vlab(238, 140, 176, 'activate', lib.ACC)
b += path([(378, 120), (378, 196)]) + vlab(378, 140, 176, 'attach')
b += path([(296, 226), (316, 226)])
b += text(560, 222, 'Admission policies', 10, 500, lib.MUTED, mono=True)
b += text(560, 238, 'check every step', 10, 400, lib.MUTED, mono=True)
fig1 = P.fig(b, W, H, 'The break-glass flow',
             'An owner requests a session with a reason, a second person approves, Tower creates a time-limited RoleBinding and attaches to a pinned debug container, the session is recorded, the pod is recycled at the end, and the record is reviewed.',
             'Outside an active grant, Tower holds none of the verbs a session needs. The RoleBinding carries a TTL, so it expires even if Tower dies mid-session.')

# Figure 2: guardrail layers.
W2, H2 = 760, 236
c = ''
layers = [('Tower permissions', 'who may request, approve, break the glass, end', 'propose'),
          ('Tower backend', 'requester is never approver; refuses an unrecorded start', 'backend'),
          ('Admission policies', 'binding shape, debug image, no exec on Flight', 'security'),
          ('RBAC with a TTL', 'nothing standing; the grant expires on its own', 'focal')]
for i, (n, s, k) in enumerate(layers):
    y = 24 + i * 50
    fill, stroke, dash = lib.KINDS[k]
    d = f' stroke-dasharray="{dash}"' if dash else ''
    c += f'<rect x="24" y="{y}" width="712" height="40" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>'
    c += text(44, y + 25, n, 12, 600, lib.INK)
    c += text(724, y + 25, s, 10, 400, lib.MUTED, anchor='end', mono=True)
fig2 = P.fig(c, W2, H2, 'Four layers of guardrails',
             'Tower permissions, the Tower backend, admission policies in the cluster, and time-limited RBAC.',
             'Each layer assumes the one above it can fail. On Flight the validation runs as built-in admission policy inside the API server, so it\'s never down on its own.')

P.add(f"""
<section>
  <h2>Exec or a debug container?</h2>
  <div class="tbl"><table>
    <thead><tr><th></th><th>exec into the app</th><th>ephemeral debug container</th></tr></thead>
    <tbody>
      <tr><td class="area">Admission control</td><td>allow or deny the whole thing</td><td>the policy sees the full container spec</td></tr>
      <tr><td class="area">What runs</td><td>the app image's tools, as the app's user</td><td>an approved, pinned image as a fixed non-root user</td></tr>
      <tr><td class="area">Writes</td><td>land in the app container</td><td>impossible: read-only root, read-only mounts</td></tr>
      <tr><td class="area">Minimal images</td><td>often no shell at all</td><td>always works</td></tr>
      <tr><td class="area">Trace in the pod</td><td>none</td><td>the container stays in the pod spec</td></tr>
    </tbody>
  </table></div>
  <p class="note">A debug container is safer for these reasons, not inherently. Run as the app's user with a shared process namespace, it reaches the same secrets as exec. So process access is a separate, explicit option that the approver sees.</p>
</section>

<section>
  <h2>The flow</h2>
  {fig1}
</section>

<section>
  <h2>Guardrails that don't trust the portal</h2>
  {fig2}
  <div class="prose"><p>The first build used fail-closed Kyverno policies on Flight too. On the dev cluster they made break-glass unavailable every time Kyverno lost its lease on a busy node, and on Flight that would happen during the incident itself. So Flight validation moved to built-in ValidatingAdmissionPolicy, and a slim Kyverno keeps only the two jobs it's uniquely good at: the cleanup TTL and the debug image's signature check.</p></div>
</section>

<section>
  <h2>How it was tested</h2>
  <div class="prose"><p>The last piece is a plan for walking every feature in a browser with two people, one an admin and one an app owner, on a Skyport app's Ground and Flight environments. It covers the things a harness can't: the approval round trip, the notification deep links, a sensitive recording refused to the wrong person, and a "glass broken" session reviewed by someone else.</p></div>
  <div class="track">
    <div class="row"><h3>Ground: copy, held copy, live with process access</h3>{chip('Plan', 'info')}<p>Non-root, no token, read-only; the recording's hash matches and is anchored in the Rekor transparency log.</p></div>
    <div class="row"><h3>Flight with two people</h3>{chip('Plan', 'info')}<p>Request, approve with "keep the pod", deny, end by the approver, and exec refused.</p></div>
    <div class="row"><h3>Glass broken, then reviewed</h3>{chip('Partly verified Oct 12, 2026', 'ok')}<p>Broadcast to everyone, review due, never self-reviewed, and a fallback reviewer.</p></div>
    <div class="row"><h3>Recordings</h3>{chip('Verified Oct 12, 2026', 'ok')}<p>A locked bucket refuses deletes, and the hash checks against the log without Tower.</p></div>
    <div class="row"><h3>Cluster backstops</h3>{chip('Plan', 'info')}<p>The TTL deletes a binding at fifteen minutes; process access is refused unless the session asked for it.</p></div>
  </div>
</section>

<section>
  <h2>Still open</h2>
  <ul class="plain">
    <li>Is sixty minutes the right maximum, or should an extension need a second approval?</li>
    <li>Should "glass broken" exist at all on a platform with one human? It's useful to exercise the path, and it's the weakest link.</li>
  </ul>
</section>
""")
