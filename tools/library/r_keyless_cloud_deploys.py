"""Spec: keyless cloud deploys - no stored AWS key for Crossplane or Glidepath (Oct 15 to 16, 2026)."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, vlab, text, esc

P = Page(
    'keyless-cloud-deploys', 'Spec', 'Airframe · Glidepath · Spec · Keyless cloud deploys',
    'No stored AWS key for cloud deploys',
    'How Hangar replaced two never-expiring AWS keys with one-hour roles that a pod earns by proving who it is: '
    'what was built, why it was built this way, a bigger hole closed on the way, and the incident the switch caused.',
    '2026-10-16',
    meta=[('Status', 'phases 0 to 4 live for Lambda, Oct 16, 2026; the old keys are deleted by hand; ECS, then Azure, next'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/airframe/admin/cloud-credentials/">Airframe cloud credentials</a> · '
                   '<a href="https://hangarplatform.dev/docs/glidepath/admin/cloud-deploy-identity/">Glidepath cloud deploy identity</a>')],
    lede=('Hangar reached AWS with two access keys: passwords for machines that worked from anywhere until someone '
          'deleted them, one of them shared by every app. I wanted them gone, not rotated. Doing that also turned up '
          'a way for Crossplane to make itself an AWS administrator, and the switch itself deleted a function before '
          'I fixed the composition that allowed it. This page explains all three for someone meeting these ideas for '
          'the first time.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Lambda keyless · Oct 16, 2026</span>
  <h2>Crossplane and Lambda deploys keep no AWS key.</h2>
  <ul>
    <li><b>Earned, not stored.</b> A pod proves who it is with a token Kubernetes signed for it minutes ago, and AWS trades that for one hour of access.</li>
    <li><b>One function, one role.</b> Each Lambda function gets its own deploy role. One app's pipeline can't touch another app's function.</li>
    <li><b>Only the deploy step.</b> Every other pipeline step, including the ones that run the app's own code, has no AWS access at all.</li>
    <li><b>A ceiling on everything Crossplane creates.</b> It can no longer create a role without a permissions boundary attached.</li>
  </ul>
</div>
""")

# ---------------------------------------------------------------------------------------------------------------
# Figure 1: before and after.
W, H = 760, 330
b = zone(24, 24, 712, 120, 'Before · two keys that never expire, copied around')
before = [('Infisical', 'two projects', 'store'), ('Kubernetes Secret', 'app-secrets, provider creds', 'store'),
          ('Pods', 'every pipeline step', 'backend'), ('AWS IAM users', 'keys work from anywhere', 'focal')]
for i, (n, s, k) in enumerate(before):
    x = 40 + i * 176
    b += node(x, 64, 152, 56, n, s, k)
    if i:
        b += path([(x - 24, 92), (x - 4, 92)], dashed=True)
b += zone(24, 168, 712, 140, 'After · nothing stored, nothing that lives past an hour')
b += node(40, 212, 156, 56, 'kiac-dev issuer', 'public keys only', 'store')
b += node(252, 212, 156, 56, 'Deploy pod', 'token from kubelet', 'focal')
b += node(564, 212, 156, 56, 'AWS STS', 'trusts the issuer', 'backend')
b += path([(196, 240), (248, 240)], 'link') + hlab(196, 248, 240, 'signs')
b += path([(408, 240), (560, 240)], 'accent') + hlab(408, 560, 240, '1 hour · one role')
b += text(720, 292, 'role trust: issuer, audience, one ServiceAccount', 10, 400, lib.MUTED, anchor='end', mono=True)
fig1 = P.fig(b, W, H, 'From two stored keys to earned one-hour access',
             'Before, each AWS identity was a key stored in Infisical, copied into a Kubernetes Secret and readable by any pod that mounted it. After, kiac-dev signs a short-lived token for the pod, and AWS STS trades it for one hour of one role.',
             'The workload-identity pattern a managed Kubernetes service gives you for free, built by hand for self-managed clusters.')

# Figure 2: the token exchange (sequence).
W2, H2 = 760, 420
xs = [88, 236, 384, 532, 680]
c = ''
for x in xs:
    c += f'<line x1="{x}" y1="76" x2="{x}" y2="396" stroke="rgba(27,31,36,0.20)" stroke-width="1" stroke-dasharray="3,3"/>'
c += path([(xs[1] - 4, 120), (xs[0] + 4, 120)]) + hlab(xs[0], xs[1], 120, 'signed token')
c += path([(xs[0] + 4, 168), (xs[3] - 4, 168)], 'link') + hlab(xs[0], xs[3], 168, 'token + role', lib.LINK)
c += path([(xs[3] - 4, 212), (xs[2] + 4, 212)], 'link') + hlab(xs[2], xs[3], 212, 'get keys', lib.LINK)
c += path([(xs[2] + 4, 248), (xs[3] - 4, 248)], dashed=True) + hlab(xs[2], xs[3], 248, 'public keys')
c += path([(xs[3] + 4, 284), (xs[3] + 40, 284), (xs[3] + 40, 312), (xs[3] + 8, 312)]) + vlab(xs[3] + 40, 284, 312, 'check claims')
c += path([(xs[3] - 4, 352), (xs[0] + 4, 352)], 'accent') + hlab(xs[0], xs[3], 352, '1-hour session', lib.ACC)
c += path([(xs[0] + 4, 388), (xs[4] - 4, 388)], 'link') + hlab(xs[0], xs[4], 388, 'update code', lib.LINK)
actors = [('Deploy pod', 'glidepath-cloud-deployer', 'backend'), ('kiac-dev', 'the issuer', 'backend'),
          ('Published keys', 'hangarplatform.dev', 'external'), ('AWS STS', 'sts.amazonaws.com', 'focal'),
          ('Lambda + ECR', 'this function only', 'external')]
for x, (n, s, k) in zip(xs, actors):
    c += node(x - 68, 24, 136, 52, n, s, k)
fig2 = P.fig(c, W2, H2, 'Trading a ServiceAccount token for AWS access',
             'The deploy pod gets a signed token from kiac-dev, sends it to AWS STS with the role it wants, STS checks it against the published public keys and the role\'s rules, returns a one-hour session, and the pod updates its own function.',
             'The pod never holds anything that outlives it. AWS caches the public keys, so they aren\'t fetched on every request.')

# Figure 3: the trust chain.
W3, H3 = 760, 404
d = zone(24, 24, 208, 352, 'kiac-dev cluster')
d += zone(248, 24, 152, 352, 'Public web')
d += zone(416, 24, 320, 352, 'AWS account')
d += (f'<rect x="424" y="264" width="304" height="104" rx="8" fill="rgba(185,121,31,0.05)" '
      f'stroke="rgba(185,121,31,0.50)" stroke-width="1" stroke-dasharray="4,4"/>')
d += text(576, 360, 'PERMISSIONS BOUNDARY', 8, 500, lib.ACC, anchor='middle', mono=True, ls='0.14em')
d += path([(216, 84), (260, 84)], dashed=True) + hlab(216, 260, 84, 'keys')
d += path([(384, 84), (428, 84)], 'link', dashed=True) + hlab(384, 428, 84, 'read', lib.LINK)
d += path([(508, 112), (508, 168)]) + vlab(508, 112, 168, 'verifies')
d += path([(216, 196), (428, 196)], 'link') + hlab(216, 428, 196, 'assume role', lib.LINK)
d += path([(216, 308), (428, 308)], 'accent') + hlab(216, 428, 308, 'assume role', lib.ACC)
d += path([(508, 224), (508, 276)]) + vlab(508, 224, 276, 'creates')
d += path([(640, 196), (664, 196), (664, 276)]) + vlab(664, 216, 256, 'creates')
d += node(40, 56, 176, 56, 'kiac-dev API server', 'signs SA tokens', 'backend')
d += node(40, 168, 176, 56, 'Crossplane providers', 'SA provider-aws-*', 'backend')
d += node(40, 280, 176, 56, 'Deploy step · Job', 'SA glidepath-cloud-deployer', 'backend')
d += node(264, 56, 120, 56, 'Published keys', '/oidc/kiac-dev', 'external')
d += node(432, 56, 152, 56, 'Identity provider', 'trusts the issuer', 'external')
d += node(432, 168, 208, 56, 'hangar-crossplane-kiac-dev', 'builds the infrastructure', 'backend')
d += node(432, 280, 164, 56, 'glidepath-deploy-<fn>', 'this repo · this function', 'focal')
d += node(608, 280, 112, 56, '<fn>-exec', 'runs the function', 'store')
fig3 = P.fig(d, W3, H3, 'The trust chain behind keyless deploys',
             'kiac-dev publishes its public signing keys; an AWS identity provider trusts them; Crossplane assumes its own role and creates each function\'s deploy and execution roles inside a permissions boundary; the deploy step assumes its function\'s deploy role.',
             'Two kinds of workload, each with its own role. Everything Crossplane creates sits inside the boundary.')

# Figure 4: six guardrails.
W4, H4 = 760, 356
rows = [('01', 'Admission policy', 'who may run as glidepath-cloud-deployer', False),
        ('02', 'Short-lived token', '1 hour · audience sts.amazonaws.com', False),
        ('03', 'Trust policy', 'this issuer · this audience · this ServiceAccount', False),
        ('04', 'Role policy', 'this repository · this function · no deletes', False),
        ('05', 'Permissions boundary', 'the most any created role can ever do', True),
        ('06', "Crossplane's own policy", "can't create a role without the boundary", False)]
x0, wl, rh, y0 = 136, 600, 48, 24
e = f'<rect x="{x0}" y="{y0}" width="{wl}" height="{rh * 6}" rx="6" fill="{lib.PAPER}" stroke="{lib.MUTED}" stroke-width="1"/>'
for i, (idx, name, note, focal) in enumerate(rows):
    y = y0 + rh * i
    if focal:
        e += f'<rect x="{x0}" y="{y}" width="{wl}" height="{rh}" fill="rgba(185,121,31,0.08)" stroke="{lib.ACC}" stroke-width="1"/>'
    elif i:
        e += f'<line x1="{x0}" y1="{y}" x2="{x0 + wl}" y2="{y}" stroke="{lib.RULE}" stroke-width="1"/>'
    e += text(x0 + 16, y + 28, idx, 9, 500, lib.ACC if focal else lib.MUTED, mono=True, ls='0.18em')
    e += text(x0 + 52, y + 29, name, 13, 600, lib.INK)
    e += text(x0 + wl - 16, y + 28, note, 9, 400, lib.MUTED, anchor='end', mono=True)
for (ya, yb, label) in ((y0 + 6, y0 + rh * 2 - 6, 'KUBERNETES'), (y0 + rh * 2 + 6, y0 + rh * 6 - 6, 'AWS IAM')):
    e += (f'<line x1="120" y1="{ya}" x2="120" y2="{yb}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
          f'<line x1="116" y1="{ya}" x2="120" y2="{ya}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
          f'<line x1="116" y1="{yb}" x2="120" y2="{yb}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>')
    e += text(108, (ya + yb) / 2 + 3, label, 8, 500, lib.MUTED, anchor='end', mono=True, ls='0.14em')
e += path([(x0 + 16, y0 + rh * 6 + 16), (x0 + 16, y0 + rh * 6 + 40)])
e += text(x0 + 32, y0 + rh * 6 + 32, 'A DEPLOY PASSES EVERY LAYER', 8, 500, lib.MUTED, mono=True, ls='0.14em')
fig4 = P.fig(e, W4, H4, 'Six guardrails around a keyless deploy',
             'Six independent checks: the admission policy and the short-lived token in Kubernetes, then the trust policy, the role policy, the permissions boundary and Crossplane\'s own policy in AWS.',
             'The boundary (05) was added because scoping this work showed Crossplane could create an administrator.')

# Figure 5: the deploy step's decision.
W5, H5 = 760, 400


def diamond(cx, cy, l1, l2, hw=110, hh=40):
    pts = f'{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}'
    return (f'<polygon points="{pts}" fill="{lib.PAPER}"/><polygon points="{pts}" fill="#ffffff" stroke="{lib.INK}" stroke-width="1"/>'
            + text(cx, cy - 3, l1, 11, 600, lib.INK, anchor='middle') + text(cx, cy + 12, l2, 11, 600, lib.INK, anchor='middle'))


def oval(x, y, w, h, name, sub=None):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{lib.PAPER}"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#ffffff" stroke="{lib.INK}" stroke-width="1"/>')
    s += text(x + w / 2, y + h / 2 + (4 if not sub else -2), name, 12, 600, lib.INK, anchor='middle')
    if sub:
        s += text(x + w / 2, y + h / 2 + 12, sub, 8, 400, lib.MUTED, anchor='middle', mono=True)
    return s


f = path([(380, 56), (380, 80)])
f += path([(380, 164), (380, 192)]) + vlab(380, 164, 192, 'yes')
f += path([(380, 276), (380, 300)]) + vlab(380, 276, 300, 'yes')
f += path([(490, 344), (552, 344)], 'accent') + hlab(490, 552, 344, 'yes', lib.ACC)
f += path([(270, 124), (214, 124)]) + hlab(214, 270, 124, 'no')
f += path([(256, 236), (214, 236)]) + hlab(214, 256, 236, 'no')
f += path([(270, 344), (214, 344)]) + hlab(214, 270, 344, 'no')
f += oval(300, 20, 160, 36, 'Deploy step starts')
f += diamond(380, 124, 'Account ConfigMap', 'in the namespace?')
f += diamond(380, 236, 'Token belongs to', 'glidepath-cloud-deployer?', hw=124)
f += diamond(380, 344, 'STS accepts', 'the role?')
f += node(556, 316, 180, 56, 'Assume the role', 'glidepath-deploy-<fn>', 'focal')
f += oval(30, 102, 180, 44, 'Deploy fails', 'names clusters.yaml')
f += oval(30, 214, 180, 44, 'Deploy fails', 'names taskRunSpecs')
f += oval(30, 322, 180, 44, 'Deploy fails', 'names the deploy Role')
fig5 = P.fig(f, W5, H5, 'How the deploy step gets its AWS access',
             'The deploy step checks that the namespace has the account ConfigMap, that the pod\'s token belongs to glidepath-cloud-deployer and that STS accepts the function\'s role. If all three hold it assumes the role; if one fails the deploy stops with an error naming that piece. There is no stored key to fall back to.',
             'Until phase 4 a failed check fell back to the app\'s stored key. That covered the minutes between switching an app over and Crossplane creating its role, and was removed once every app had moved.')

# Figure 6: the incident.
W6, H6 = 760, 232
x0, x1 = 48, 712
px = lambda m: x0 + m * (x1 - x0) / 35
base = 132
g = f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{lib.INK}" stroke-width="1"/>'
for m in range(0, 36, 5):
    x = px(m)
    g += f'<line x1="{x:g}" y1="{base - 4}" x2="{x:g}" y2="{base + 4}" stroke="{lib.INK}" stroke-width="1"/>'
    g += text(round(x, 1), base + 18, f'17:{m:02d}', 8, 400, lib.SOFT, anchor='middle', mono=True)
events = [(5 + 22 / 60, True, False, '17:05 · switch merged', 'registry names the account'),
          (16.5, False, True, '17:16 · function deleted', 'with its URL and permission'),
          (22.75, True, False, '17:22 · function back', 'placeholder image, new URL'),
          (27.5, False, True, '17:27 · fix merged', 'never drop what exists')]
for m, above, major, title, sub in events:
    x = round(px(m), 1)
    r = 6 if major else 4
    col = lib.ACC if major else lib.INK
    if above:
        g += f'<line x1="{x}" y1="{base - r}" x2="{x}" y2="{base - 40}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
        ty = base - 72
    else:
        g += f'<line x1="{x}" y1="{base + r}" x2="{x}" y2="{base + 40}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
        ty = base + 58
    g += f'<circle cx="{x}" cy="{base}" r="{r}" fill="{col}"/>'
    g += text(x, ty, title, 12, 600, lib.INK, anchor='middle') + text(x, ty + 16, sub, 9, 400, lib.MUTED, anchor='middle', mono=True)
fig6 = P.fig(g, W6, H6, 'Incident: smoke-fn\'s function deleted and re-created',
             'On October 16, 2026 (UTC) the switch merged at 17:05, the function, its URL and its permission were deleted at 17:16, the function came back from the placeholder at 17:22, and the fix merged at 17:27.',
             'Spaced to scale. The function was gone from 17:16:32 to 17:22:45.')

# ---------------------------------------------------------------------------------------------------------------
P.add(f"""
<section>
  <h2>Why: two keys that never expired</h2>
  <div class="prose">
    <p>Hangar uses AWS in two ways. <b>Crossplane</b> builds what an app needs there: an image registry, a Lambda
    function, a public web address for it. <b>Glidepath</b>, the delivery pipeline, then ships each new version of the
    app's code into that function. Each needed an AWS identity, and each got an <b>access key</b>: a username and
    password for a machine.</p>
    <p>A key like that has three problems. It never expires, so a leaked copy works until someone notices. It works
    from anywhere, so a copy on a laptop is as good as the original. And the deploy key was shared by every app, so a
    leak from one app's pipeline reached every other app's functions. Rotating keys shortens the window; it doesn't
    close it.</p>
  </div>
  {fig1}
</section>

<section>
  <h2>How it works, in plain terms</h2>
  <div class="prose">
    <p>Think of a building with a front desk. The old way handed each contractor a master key to keep. The new way
    gives them nothing to keep. They arrive with a badge their employer printed that morning, the desk checks it
    against the employer's published sample, and hands back a visitor pass for one floor that expires in an hour.</p>
    <p>The employer is the cluster: Kubernetes gives every pod a signed identity card, a <b>ServiceAccount token</b>.
    The published sample is kiac-dev's public signing keys, at <code>hangarplatform.dev/oidc/kiac-dev</code>: anyone
    can check a signature with them, nobody can make one. The front desk is <b>AWS STS</b>, which checks the token
    against an <b>IAM role</b>'s rules about who may use it, and returns credentials that last an hour. The industry
    name is web identity federation; on Amazon's own Kubernetes service it's called IRSA.</p>
  </div>
  {fig2}
</section>

<section>
  <h2>What was built</h2>
  {fig3}
  <div class="tbl"><table>
    <thead><tr><th>Who</th><th>Runs as</th><th>Assumes</th><th>Can do</th></tr></thead>
    <tbody>
      <tr><td class="area">Crossplane's AWS providers</td><td><code>provider-aws-*</code></td><td><code>hangar-crossplane-kiac-dev</code></td><td>create, observe and delete what the compositions describe</td></tr>
      <tr><td class="area">Glidepath's deploy step</td><td><code>glidepath-cloud-deployer</code></td><td><code>glidepath-deploy-&lt;fn&gt;</code></td><td>push to this function's registry, update this function's code</td></tr>
      <tr><td class="area">The target's bootstrap Job</td><td><code>glidepath-cloud-deployer</code></td><td><code>glidepath-deploy-&lt;fn&gt;</code></td><td>the same, once, to seed the first image</td></tr>
      <tr><td class="area">Every other pipeline step</td><td><code>pipeline-runner</code></td><td>nothing</td><td>no AWS access</td></tr>
    </tbody>
  </table></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">Decision</span><h3>The target creates each deploy role</h3><p>The Lambda target already creates the function, its registry and its execution role, so it creates the deploy role beside them and deletes it with them. A new app needs no IAM step at all.</p></div>
    <div class="card"><span class="eyebrow">Decision</span><h3>A dedicated ServiceAccount</h3><p>Every pipeline step runs as <code>pipeline-runner</code>, including tests that run the app's own code. Only the deploy step and the bootstrap Job run as <code>glidepath-cloud-deployer</code>, the one subject the role trusts.</p></div>
    <div class="card"><span class="eyebrow">Decision</span><h3>The account, stated once</h3><p>The AWS account lives in the fleet's <code>clusters.yaml</code>. The compositions and every app's chart read it from there; no app repeats it in <code>cicd.yaml</code>.</p></div>
  </div>
</section>

<section>
  <h2>Options considered</h2>
  <div class="tbl"><table>
    <thead><tr><th>Option</th><th>Verdict</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td class="area">Web identity federation</td><td>{chip('Chosen', 'ok')}</td><td>Nothing stored, nothing new in the request path, one role per function, and the same pattern every managed Kubernetes uses.</td></tr>
      <tr><td class="area">Rotate the keys</td><td>{chip('Rejected', 'bad')}</td><td>Shortens the window but keeps it, adds a process someone must run, and keeps one key for every app.</td></tr>
      <tr><td class="area">Short-lived keys from a secrets store</td><td>{chip('Fallback', 'info')}</td><td>Real leases, but the store keeps a standing credential that can mint them, and every deploy depends on it being up.</td></tr>
      <tr><td class="area">IAM Roles Anywhere</td><td>{chip('Rejected', 'bad')}</td><td>Trusts X.509 certificates instead of tokens: a certificate authority to run and certificates to hand out, for the same result.</td></tr>
      <tr><td class="area">Trust <code>pipeline-runner</code></td><td>{chip('Rejected', 'bad')}</td><td>Simpler, but any step that runs the app's code could reach AWS.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>What checking the permissions turned up</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Finding 0.1</span><h3>Crossplane could mint an administrator</h3><p>Its policy let it create any role ending in <code>-exec</code>, decide who may use it and attach any rules. Together that's a way to create a full administrator. Apps couldn't reach it, but a bug in a composition could.</p></div>
    <div class="card"><span class="eyebrow">Phase 0</span><h3>A ceiling on every created role</h3><p>A permissions boundary caps a role whatever its own rules say. Crossplane's policy now refuses to create a role, or add rules to one, unless the boundary is attached, and nothing may remove it.</p></div>
    <div class="card"><span class="eyebrow">Finding 0.2</span><h3>Labels could be forged</h3><p>Kubernetes lets any pod use any ServiceAccount in its namespace, and labels on a pipeline run are copied onto its pods. So the admission policies decide by who created the pod, which Kubernetes records and a client can't fake.</p></div>
  </div>
  {fig4}
</section>

<section>
  <h2>The migration</h2>
  <div class="prose"><p>Switching every app at once would break any deploy that runs before its role exists, so for the
  switch the deploy step kept the old key as a fallback and logged which path it took. Once every app had deployed
  through its role and no cluster held an AWS key any more, the fallback was removed (phase 4). Now a deploy either
  assumes its role or stops and says what is missing.</p></div>
  {fig5}
  <div class="track">
    <div class="row"><h3>Phase 0 · close the hole</h3>{chip('Live', 'ok')}<p>Permissions boundary and Crossplane policy v3; every composed role carries the boundary.</p></div>
    <div class="row"><h3>Phase 1 · a deploy role per function</h3>{chip('Live', 'ok')}<p>The Lambda target creates <code>glidepath-deploy-&lt;fn&gt;</code>; its bootstrap Job uses it.</p></div>
    <div class="row"><h3>Phase 2 · Glidepath assumes it</h3>{chip('Live', 'ok')}<p>The ServiceAccount, the account ConfigMap, the deploy step and promote flows.</p></div>
    <div class="row"><h3>Phase 3 · who may use it</h3>{chip('Live', 'ok')}<p>Four admission policies, 16 of 16 live cases. The first real deploy showed they also refused Tekton's signing and history services, which only add a note to a run; fixed the same day.</p></div>
    <div class="row"><h3>Phase 4 · retire the key</h3>{chip('Live', 'ok')}<p>The fallback and the scaffold's AWS secrets are gone, and a test fails the build if the deploy step ever reads a stored key again. The old Infisical keys and IAM users are deleted by hand.</p></div>
    <div class="row"><h3>ECS, then Azure</h3>{chip('Planned', 'info')}<p>The same deploy role for ECS after its first live deploy; Azure through workload identity federation.</p></div>
  </div>
</section>

<section>
  <h2>The incident: the switch deleted a function</h2>
  {fig6}
  <div class="prose">
    <p>Crossplane works by comparison: each time it looks at an app, it lists what should exist and deletes anything
    no longer on the list. Phase 1 made the bootstrap Job wait for the new deploy role. For one pass the role didn't
    exist, so the finished Job dropped off the list and was deleted. An older rule said the function exists only once
    the Job has succeeded, so on the next pass the function, its URL and its permission dropped off too, and were
    deleted in AWS. They came back six minutes later from the placeholder image, with a new web address.</p>
    <p>The fix keeps anything that already exists on the list, whatever happens to the conditions it was created
    under. Two new tests replay both steps; run against the old composition, they fail the way production did.</p>
  </div>
  <p class="quote">A condition may decide when to create something. It must never decide whether to keep it.</p>
</section>

<section>
  <h2>How I know it works</h2>
  <div class="tbl"><table>
    <thead><tr><th>Check</th><th>Result</th></tr></thead>
    <tbody>
      <tr><td class="area">Crossplane's role</td><td>Assumed from a real provider token; the default ServiceAccount, a wrong audience and the Azure provider were refused.</td></tr>
      <tr><td class="area">A real create and delete</td><td>An empty registry created, Ready and deleted through the role; AWS confirmed it gone.</td></tr>
      <tr><td class="area">Permissions boundary</td><td>Added to the existing execution role and on both new deploy roles, which policy v3 only allows with the boundary.</td></tr>
      <tr><td class="area">Bootstrap Job</td><td>Ran as <code>glidepath-cloud-deployer</code> and logged in to the registry through the deploy role, with no key mounted.</td></tr>
      <tr><td class="area">Admission policies</td><td>16 of 16 live cases, 12 for creating objects and 4 for changing them, each test object checked to contain what its case claims.</td></tr>
      <tr><td class="area">A real deploy</td><td>smoke-fn promoted to production (<code>promote-prod-0-deploy-cc5kj</code>): the deploy step ran as <code>glidepath-cloud-deployer</code>, logged <code>credentials: assuming …/glidepath-deploy-glidepath-smoke-fn-prod (web identity, no stored key)</code> and updated the function.</td></tr>
      <tr><td class="area">With no key path at all</td><td>After phase 4, the same promotion re-run (<code>promote-prod-0-deploy-t4n84</code>): the deploy step had no <code>app-secrets</code> volume, assumed the role, updated the function, and was signed and recorded.</td></tr>
    </tbody>
  </table></div>
  <p class="note">The page's numbers are from kiac-dev and AWS account 700017004810 on October 16, 2026. Pull requests: hangar#55, glidepath#114 to #116, airframe#87 to #90, gitops-cluster-dev#96 to #108, apron#30 and #31, and for phase 4 glidepath#118 and airframe#92 and #93; documentation in airframe#91, glidepath#117 and hangar#56.</p>
</section>
""")
