"""Spec: a Glidepath API for people, Tower and agents (Oct 25, 2026)."""
from report import Page, chip
import lib
from lib import node, path, zone, hlab, vlab, text, stopx

P = Page(
    'glidepath-api', 'Spec', 'Glidepath · Tower · Autopilot · Spec · The Glidepath API',
    'A Glidepath API for people, Tower and agents',
    'Give Glidepath the front end Airframe already has: a generated contract, a validator, a small API for runs and '
    'releases, and four tiers of action. Agents edit cicd.yaml through pull requests, limited by field. Tower moves onto the API '
    'side by side, one group of routes at a time.',
    '2026-10-25',
    meta=[('Status', 'proposed Oct 25, 2026; nothing built yet'),
          ('Basis', 'airframe, glidepath, autopilot, tower and backstage, read from the code on Oct 25, 2026; nothing checked live'),
          ('Related', '<a href="https://hangarplatform.dev/library/airframe-crossplane-agent-api/">Airframe as an agent API</a> · '
                      '<a href="https://hangarplatform.dev/library/autopilot-architecture-map/">Autopilot architecture map</a>')],
    lede=('Airframe has a front end an agent can use cold. It has a schema, a contract that says what every kind '
          'returns and how it fails, a validator, a verifier, and a gateway that decides what an agent may touch. Glidepath has '
          'none of that. What it has is about sixty routes inside Tower\'s backend that answer every CI/CD question and take every CI/CD '
          'action, for Tower alone. This spec moves that surface into Glidepath, builds it the way Airframe is built, and lets Tower '
          'and agents share it.'))

P.add(f"""
<div class="verdict info">
  <span class="stamp">Proposed · Oct 25, 2026</span>
  <h2>Glidepath gets a contract, a validator and an API, and Tower becomes one of its clients.</h2>
  <ul>
    <li><b>Durable changes stay git commits.</b> Editing <code>cicd.yaml</code>, promoting, rolling back and pinning all open a pull request. Only short-lived things, such as a re-run or a preview environment, are API calls.</li>
    <li><b>Agents may edit <code>cicd.yaml</code> by pull request, limited by field.</b> The whole-file block goes. Each field is <i>open</i>, <i>tighten only</i> or <i>human only</i>, and both Clearance and CI enforce that.</li>
    <li><b>Four tiers.</b> Read, reversible in Ground, propose for Flight, never. A human merge is the only thing that changes a Flight environment.</li>
    <li><b>Tower moves side by side.</b> Every Tower route stays. Behind each group of routes a switch goes from <i>direct</i> to <i>shadow</i> to <i>api</i>, and flipping it back undoes the move.</li>
    <li><b>Glidepath stays standalone.</b> The API ships in <code>glidepath-control-plane</code> and has no Hangar dependency. Tower and Clearance are only clients.</li>
  </ul>
</div>
""")

# ---------------------------------------------------------------------------------------------------------------
# Figure 1: the Airframe pattern, applied to Glidepath.
W1, H1 = 760, 304
a = zone(24, 24, 712, 116, 'Airframe · today')
a += zone(24, 164, 712, 116, 'Glidepath · this spec')
rows = [
    (64, [('Contract', 'airframe-contract.json', 'store'), ('airframe-validate', 'AF-* rule ids', 'backend'),
          ('XR in git', 'Argo CD applies it', 'backend'), ('airframe-verify', 'closed reason sets', 'backend')]),
    (204, [('Contract', 'glidepath-contract.json', 'propose'), ('glidepath validate', 'GP-* rule ids', 'propose'),
           ('glidepath-api', 'git or a short-lived call', 'focal'), ('explain', 'knownFailures ids', 'propose')]),
]
for y, items in rows:
    for i, (n, s, k) in enumerate(items):
        x = 40 + i * 176
        a += node(x, y, 152, 56, n, s, k)
        if i:
            a += path([(x - 24, y + 28), (x - 4, y + 28)])
fig1 = P.fig(a, W1, H1, 'The Airframe pattern, applied to Glidepath',
             'Airframe has four pieces: a generated contract, a validator with rule ids, a write path through git, and a verifier with closed reason sets. Glidepath gets the same four: a generated contract, glidepath validate, glidepath-api, and explain.',
             'Blue pieces are new. The API is the one piece Airframe doesn\'t need. A run is short-lived and has no desired state for Crossplane to reconcile.')

# Figure 2: architecture.
W2, H2 = 760, 424
b = zone(24, 32, 168, 360, 'Clients')
b += zone(216, 32, 232, 360, 'Dev cluster · control plane', center=True)
b += zone(472, 32, 264, 360, 'What it reads and drives')
callers = [('Tower', 'as tower-actor + user', 'backend'), ('Clearance', 'agents, over MCP', 'backend'),
           ('glidepath CLI', 'people, OIDC token', 'backend'), ('Pipelines', 'their own SA token', 'backend')]
for i, (n, s, k) in enumerate(callers):
    y = 64 + i * 80
    b += node(36, y, 144, 52, n, s, k)
    b += path([(180, y + 26), (204, y + 26)], marker=False)
b += path([(204, 90), (204, 330)], marker=False)
b += path([(204, 212), (240, 212)], 'link') + hlab(204, 240, 212, 'https', lib.LINK)
b += node(244, 64, 176, 52, 'Authn', 'TokenReview · OIDC', 'security')
b += node(244, 180, 176, 64, 'glidepath-api', 'v1 · OpenAPI · audited', 'focal')
b += node(244, 312, 176, 52, 'Authz', 'SubjectAccessReview', 'security')
b += path([(332, 116), (332, 176)]) + vlab(332, 116, 176, 'who')
b += path([(332, 244), (332, 308)]) + vlab(332, 244, 308, 'may they')
sources = [('Tekton + Results', 'runs, logs, 30-day archive'), ('Release records', 'state per release-id'),
           ('Testkube', 'test runs and reports'), ('Chains + Rekor', 'provenance, SBOM'),
           ('GitHub', 'PRs, statuses, merges'), ('CDEvents broker', 'the event stream')]
for i, (n, s) in enumerate(sources):
    y = 52 + i * 56
    b += node(496, y, 224, 44, n, s, 'store')
    b += path([(460, y + 22), (492, y + 22)], 'link')
b += path([(420, 212), (460, 212)], marker=False)
b += path([(460, 74), (460, 354)], marker=False)
fig2 = P.fig(b, W2, H2, 'Where glidepath-api sits',
             'Four clients, Tower, Clearance, the glidepath CLI and pipelines, call glidepath-api on the dev cluster over https. It checks who the caller is with TokenReview or an OIDC token, checks what they may do with a SubjectAccessReview, and reads and drives Tekton and Tekton Results, the release records, Testkube, Chains and Rekor, GitHub, and the CDEvents broker.',
             'Nothing here reaches a Flight cluster. A release is still a pull request on gitops-&lt;app&gt; that Argo CD syncs (ADR-0004).')

# Figure 3: the four tiers.
W3, H3 = 760, 300
tiers = [('T0', 'Read', 'flows · logs · gates · releases · evidence · explain', False, False),
         ('T1', 'Reversible, Ground only', 're-run · cancel · build a branch · preview env · cicd.yaml PR', False, False),
         ('T2', 'Propose for Flight', 'promote · roll back · pin: a PR a human merges', True, False),
         ('T3', 'Never offered', 'bypass a gate · edit signing policy · merge · approve', False, True)]
x0, wl, rh, y0 = 136, 600, 56, 24
e = f'<rect x="{x0}" y="{y0}" width="{wl}" height="{rh * 4}" rx="6" fill="{lib.PAPER}" stroke="{lib.MUTED}" stroke-width="1"/>'
for i, (idx, name, note, focal, never) in enumerate(tiers):
    y = y0 + rh * i
    if focal:
        e += f'<rect x="{x0}" y="{y}" width="{wl}" height="{rh}" fill="rgba(185,121,31,0.08)" stroke="{lib.ACC}" stroke-width="1"/>'
    elif i:
        e += f'<line x1="{x0}" y1="{y}" x2="{x0 + wl}" y2="{y}" stroke="{lib.RULE}" stroke-width="1"/>'
    e += text(x0 + 16, y + 32, idx, 10, 500, lib.ACC if focal else lib.MUTED, mono=True, ls='0.18em')
    e += text(x0 + 56, y + 25, name, 13, 600, lib.INK)
    e += text(x0 + 56, y + 42, note, 9, 400, lib.MUTED, mono=True)
    if never:
        e += stopx(x0 + wl - 24, y + rh / 2)
for (ya, yb, label) in ((y0 + 6, y0 + rh * 2 - 6, 'API CALL'), (y0 + rh * 2 + 6, y0 + rh * 3 - 6, 'GIT PR'),
                        (y0 + rh * 3 + 6, y0 + rh * 4 - 6, 'NONE')):
    e += (f'<line x1="120" y1="{ya}" x2="120" y2="{yb}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
          f'<line x1="116" y1="{ya}" x2="120" y2="{ya}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
          f'<line x1="116" y1="{yb}" x2="120" y2="{yb}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>')
    e += text(108, (ya + yb) / 2 + 3, label, 8, 500, lib.MUTED, anchor='end', mono=True, ls='0.14em')
e += text(x0, y0 + rh * 4 + 32, 'T1 and T2 accept dryRun: true and return the plan without acting.', 10, 400, lib.MUTED, mono=True)
fig3 = P.fig(e, W3, H3, 'The four tiers of a Glidepath action',
             'T0 reads. T1 makes reversible changes in Ground only, such as a re-run or a preview environment. T2 proposes a Flight change as a pull request that a human merges. T3 is never offered to any identity.',
             'The same tiers Clearance already uses. T2 is the line that matters: past it, nothing applies until a human merges.')

# Figure 4: cicd.yaml field scope.
W4, H4 = 760, 336
cols = [('Open · agent PR', 'propose', ['/build/**', '/test/**', '/ephemeralEnvironments/**', '/notifications/**',
                                        '/deploy/strategy', '/deploy/environments', '  (Ground entries only)', '/pipelines/**']),
        ('Tighten only', 'focal', ['/governance/sast', '/governance/imageScan', '/governance/policyCheck', '/governance/sbom',
                                   '/governance/githubMerge', '', 'may turn on or narrow,', 'never turn off or widen']),
        ('Human only', 'security', ['/secrets', '/governance/allowedCommitSigners', '/deploy/target', '/deploy/lambda',
                                    '/deploy/ecs', '/deploy/azureContainerApps', '/deploy/releaseFile', '/deploy/chart'])]
f = ''
for i, (title, kind, fields) in enumerate(cols):
    x = 24 + i * 240
    fill, stroke, dash = lib.KINDS[kind]
    d = f' stroke-dasharray="{dash}"' if dash else ''
    f += (f'<rect x="{x}" y="24" width="224" height="264" rx="8" fill="{lib.PAPER}"/>'
          f'<rect x="{x}" y="24" width="224" height="264" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>')
    f += text(x + 16, 48, title.upper(), 9, 500, stroke if kind != 'propose' else lib.LINK, mono=True, ls='0.14em')
    f += f'<line x1="{x + 16}" y1="60" x2="{x + 208}" y2="60" stroke="{lib.RULE}" stroke-width="1"/>'
    for j, fld in enumerate(fields):
        note = not fld.startswith('/')
        f += text(x + 16, 84 + j * 24, fld.strip(), 10, 400, lib.MUTED if note else lib.INK, mono=True, italic=note)
f += text(24, 316, 'Every agent PR still needs a human merge. .tekton/** stays file-denied: Glidepath regenerates it.', 10, 400, lib.MUTED, mono=True)
fig4 = P.fig(f, W4, H4, 'Which cicd.yaml fields an agent may change',
             'Open fields an agent may change in a pull request: build, test, ephemeral environments, notifications, deploy strategy, Ground environment entries and pipelines. Governance gates may only be tightened. Secrets, signers, the deploy target and its cloud blocks, the release file and the chart are human only.',
             'Replaces the whole-file deny on cicd.yaml. The rule that stays: an agent never edits a control that constrains it.')

# Figure 5: Tower side by side.
W5, H5 = 760, 472
t = zone(24, 24, 712, 168, 'Today · Tower holds the CI/CD logic')
t += node(40, 76, 128, 52, 'Browser', 'Tower UI', 'input')
t += node(216, 56, 176, 52, 'Tower backend', '/api/glidepath · 60', 'backend')
t += node(216, 124, 176, 52, 'Kubernetes proxy', 'read-only guard', 'backend')
t += node(472, 56, 248, 52, 'Tekton · Results · Testkube', 'records · GitHub · Rekor', 'store')
t += node(472, 124, 248, 52, 'PipelineRuns direct', 'runs, TaskRun logs, fleet', 'store')
t += path([(168, 92), (192, 92), (192, 82), (212, 82)])
t += path([(168, 112), (192, 112), (192, 150), (212, 150)])
t += path([(392, 82), (468, 82)]) + hlab(392, 468, 82, 'tower-actor')
t += path([(392, 150), (468, 150)]) + hlab(392, 468, 150, 'ingestor')
t += zone(24, 216, 712, 232, 'Side by side · a switch per group of routes')
t += node(40, 300, 128, 52, 'Browser', 'unchanged', 'input')
t += node(216, 300, 176, 52, 'Tower backend', 'same routes, a client', 'backend')
t += node(472, 256, 248, 52, 'glidepath-api', 'groups switched to api', 'focal')
t += node(472, 340, 248, 52, 'Direct, as today', 'groups still direct', 'store')
t += path([(168, 326), (212, 326)])
t += path([(392, 316), (432, 316), (432, 282), (468, 282)], 'accent') + vlab(432, 282, 316, 'api', lib.ACC, side='l')
t += path([(392, 336), (432, 336), (432, 366), (468, 366)]) + vlab(432, 336, 366, 'direct', side='l')
t += path([(596, 312), (596, 336)], 'link', dashed=True, marker=False)
t += text(608, 328, 'shadow: both, then diff', 9, 400, lib.LINK, mono=True)
t += text(40, 424, 'Tower-only routes (Argo CD, Config, break-glass, Release Record) stay direct for good.', 10, 400, lib.MUTED, mono=True)
fig5 = P.fig(t, W5, H5, 'Tower before and during the move',
             'Today the browser calls Tower\'s backend, which reads and drives Tekton, Results, Testkube, the release records, GitHub and Rekor itself, and the browser also reads PipelineRuns through the read-only Kubernetes proxy. Side by side, the browser is unchanged and Tower\'s backend keeps its routes; each group of routes is switched to glidepath-api or kept direct, and in shadow mode it calls both and records any difference.',
             'Nothing changes for someone using Tower. What changes is where each answer comes from, and the move is undone by changing config.')

# Figure 6: roadmap.
W6, H6 = 760, 268
x0, x1, base = 96, 664, 120
g = f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{lib.INK}" stroke-width="1"/>'
phases = [('P0', 'Contract', 'validate · field scope', True), ('P1', 'Read API', 'Tower in shadow', False),
          ('P2', 'Read cut-over', 'agent T0 tools', False), ('P3', 'T1 actions', 're-run · cicd PR', False),
          ('P4', 'T2 propose', 'promote · rollback', True), ('P5', 'Events', 'triage on failure', False),
          ('P6', 'Retire', 'Tower loses writes', False)]
step = (x1 - x0) / (len(phases) - 1)
for i, (pid, name, sub, major) in enumerate(phases):
    x = round(x0 + i * step, 1)
    r = 6 if major else 4
    col = lib.ACC if major else lib.INK
    above = i % 2 == 0
    if above:
        g += f'<line x1="{x}" y1="{base - r}" x2="{x}" y2="{base - 36}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
        ty = base - 80
    else:
        g += f'<line x1="{x}" y1="{base + r}" x2="{x}" y2="{base + 36}" stroke="rgba(27,31,36,0.30)" stroke-width="1"/>'
        ty = base + 52
    g += f'<circle cx="{x}" cy="{base}" r="{r}" fill="{col}"/>'
    g += text(x, ty, pid, 9, 500, lib.ACC if major else lib.MUTED, anchor='middle', mono=True, ls='0.14em')
    g += text(x, ty + 16, name, 12, 600, lib.INK, anchor='middle') + text(x, ty + 31, sub, 9, 400, lib.MUTED, anchor='middle', mono=True)
g += text(24, 252,'Each phase ends with a live check. Order is fixed; dates are not.', 10, 400, lib.MUTED, mono=True)
fig6 = P.fig(g, W6, H6, 'Roadmap: seven phases',
             'P0 contract, validator and field scope. P1 read API with Tower in shadow. P2 read cut-over and agent read tools. P3 T1 actions. P4 T2 propose actions. P5 event subscriptions. P6 retire Tower\'s duplicate paths and its write access to Tekton.',
             'P0 and P4 are amber: P0 is what agents need first, and P4 is the first point an agent can start a Flight change.')

# ---------------------------------------------------------------------------------------------------------------
P.add(f"""
<section>
  <h2>Why: Glidepath answers to Tower, and only to Tower</h2>
  <div class="prose">
    <p>Airframe's API is its schema. Twenty kinds in <code>catalog.hangar.io/v1alpha1</code>, a versioning policy, and a
    sidecar per kind that lists what the kind returns, the conditions it reports with a fixed set of reasons, how to verify it
    and how it is known to fail. All of that is generated into one contract file. An agent asks <code>airframe-capabilities</code>
    what it can do, runs <code>airframe-validate</code> before it opens a pull request, and runs <code>airframe-verify</code>
    afterwards. Clearance decides which of those writes the agent may make at all.</p>
    <p>Glidepath has the schema half: <code>cicd.yaml</code> and <code>cicd.schema.json</code>. Everything an agent needs at
    run time is spread over six stores: PipelineRuns, Tekton Results, the release records, Testkube, Chains and Rekor, and
    GitHub. The only thing that joins them is Tower's backend: <code>glidepathProvenance.ts</code> alone is 2,994 lines with
    60 routes, and four browser hooks read Tekton directly through the Kubernetes proxy. Some of that is CI/CD logic, such as
    working out a flow's chain slug or which releases a rollback may target, and it lives in a Backstage plugin. Clearance
    offers agents exactly one CI/CD tool, <code>pipeline.rerun</code>.</p>
    <p>That has three costs. An agent can't ask Glidepath why a flow failed. Glidepath, which has to stay installable on its own,
    can't be operated without Tower. And every rule about who may promote or roll back is written in Tower's code, not in
    Glidepath's.</p>
  </div>
  {fig1}
</section>

<section>
  <h2>Layer 1: the contract</h2>
  <div class="prose">
    <p>A new sidecar, <code>schemas/cicd.meta.yaml</code>, does for <code>cicd.yaml</code> what <code>xrds/&lt;kind&gt;.meta.yaml</code>
    does for an XRD. A generator folds it, the schema, the gate registry and Glidepath's state vocabularies into
    <code>contract/glidepath-contract.json</code>. CI runs the generator with <code>--check</code>, the same way Airframe's does.</p>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Section</th><th>What it says</th><th>Where it comes from</th></tr></thead>
    <tbody>
      <tr><td class="area">fields</td><td>Every <code>cicd.yaml</code> field with its type, description, owner (team or admin), risk and <b>agent scope</b>: open, tighten or human</td><td><code>cicd.schema.json</code> + <code>cicd.meta.yaml</code></td></tr>
      <tr><td class="area">gates</td><td>Each governance gate: what it verifies, whether it is <code>required</code>, which status check it posts</td><td>the gate registry</td></tr>
      <tr><td class="area">states</td><td>Fixed sets of stage, gate and release states with their meanings. The release set already exists: proposed, merged, progressing, healthy, superseded, rolled-back</td><td>ADR-0021, ADR-0022</td></tr>
      <tr><td class="area">knownFailures</td><td>Stable ids with a match and a hint, e.g. <code>SourceVolumeFull</code> (raise <code>build.sourceVolume.size</code>), <code>ProvenanceSignerNotAllowed</code>, <code>ItsmChangeNotApproved</code>, <code>BuildKitOOM</code></td><td>known-gaps.md and incidents, curated</td></tr>
      <tr><td class="area">actions</td><td>Every API action with its tier, arguments, effects and dry-run output</td><td>the OpenAPI spec</td></tr>
    </tbody>
  </table></div>
  <div class="prose">
    <p><code>glidepath validate</code> checks a <code>cicd.yaml</code> in one pass: the schema, then GP-* rules for what a schema
    can't say (an environment named after a stage, a Flight environment with no release stage). With <code>--base &lt;ref&gt;</code>
    it also checks the GP-SCOPE rules on what changed, so the field scope below holds in CI even for a pull request that never
    went through Clearance. Glidepath gets an <code>AGENTS.md</code> and an <code>llms.txt</code>, as Airframe has.</p>
  </div>
</section>

<section>
  <h2>Layer 2: the API</h2>
  {fig2}
  <div class="prose">
    <p>One service, <code>glidepath-api</code>, deployed by <code>glidepath-control-plane</code> on the dev cluster where the
    pipelines already run. Its nouns use identities Glidepath already has: a <b>flow</b> is one <code>chain-id</code> (and one
    Tempo trace), a <b>release</b> is one <code>releaseId</code> (<code>&lt;chain-id&gt;:&lt;cluster&gt;/&lt;env&gt;</code>), and
    an <b>image</b> is a digest. Custom verbs follow the <code>resource:verb</code> style.</p>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Call</th><th>Tier</th><th>What it does</th></tr></thead>
    <tbody>
      <tr><td><code>GET /v1/contract</code></td><td>T0</td><td>The contract, so a client never hard-codes a field or a state</td></tr>
      <tr><td><code>GET /v1/apps/{{app}}/flows</code></td><td>T0</td><td>Flows by state and time, live and archived (Results)</td></tr>
      <tr><td><code>GET /v1/flows/{{chainId}}</code></td><td>T0</td><td>Stages, gates, runs, the trace link</td></tr>
      <tr><td><code>GET /v1/runs/{{run}}/logs</code></td><td>T0</td><td>Step logs, live or archived</td></tr>
      <tr><td><code>GET /v1/flows/{{chainId}}:explain</code></td><td>T0</td><td>The failing step classified against knownFailures, with the hint and the field to change</td></tr>
      <tr><td><code>GET /v1/apps/{{app}}/releases</code>, <code>/v1/releases/{{releaseId}}</code></td><td>T0</td><td>Release state, PR, change request, rollback eligibility</td></tr>
      <tr><td><code>GET /v1/images/{{digest}}/evidence</code></td><td>T0</td><td>Provenance, SBOM, test evidence, signer</td></tr>
      <tr><td><code>POST /v1/apps/{{app}}/cicd:validate</code></td><td>T0</td><td><code>glidepath validate</code> as a call</td></tr>
      <tr><td><code>POST /v1/apps/{{app}}/cicd:propose</code></td><td>T1</td><td>Opens a pull request to <code>cicd.yaml</code>, after the scope check</td></tr>
      <tr><td><code>POST /v1/runs/{{run}}:rerun</code>, <code>:cancel</code></td><td>T1</td><td>What Tower's Re-run and Cancel do today</td></tr>
      <tr><td><code>POST /v1/apps/{{app}}/builds</code></td><td>T1</td><td>Builds a branch</td></tr>
      <tr><td><code>POST|DELETE /v1/apps/{{app}}/previews</code></td><td>T1</td><td>Creates, extends or deletes an ephemeral environment</td></tr>
      <tr><td><code>POST /v1/apps/{{app}}/environments/{{env}}:promote</code></td><td>T1 Ground · T2 Flight</td><td>Ground: the deploy commit. Flight: runs the app's release pipeline, which opens the gitops PR</td></tr>
      <tr><td><code>POST …/environments/{{env}}:rollback</code>, <code>:pin</code></td><td>T2</td><td>A release of an eligible earlier image, or a cloud pin PR</td></tr>
      <tr><td><code>GET /v1/events</code></td><td>T0</td><td>The CDEvents stream, filtered by app (server-sent events; AMQP topics for Autopilot)</td></tr>
    </tbody>
  </table></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">Identity</span><h3>Reuse what verifies</h3><p>Pipelines and agents present a ServiceAccount token, checked with TokenReview the way the broker checks them (ADR-0002). People present an OIDC token. Tower presents <code>tower-actor</code>'s minted token and names the user it acts for; only that subject may name someone else.</p></div>
    <div class="card"><span class="eyebrow">Authorization</span><h3>The app's namespace is the boundary</h3><p>Each call is a SubjectAccessReview against <code>app-&lt;name&gt;-cicd</code> on a virtual resource (<code>glidepath.hangar.io</code> flows, releases, environments) with verbs such as <code>rerun</code> or <code>promote</code>. <code>glidepath-app</code> renders the RoleBindings from the app's owners. No second permission model.</p></div>
    <div class="card"><span class="eyebrow">Every write</span><h3>Plan first, once, on the record</h3><p>Every write takes <code>dryRun</code> and an idempotency key, and records an audit event with the caller, who it acts for, the tier and the decision. A denial returns a rule id and a hint, in the shape Clearance's decisions already use.</p></div>
  </div>
</section>

<section>
  <h2>Layer 3: tiers, and where agents come in</h2>
  {fig3}
  <div class="prose">
    <p>Agents don't get a second MCP server. Clearance registers <code>glidepath.*</code> tools that call the API and keeps doing
    what it does for every tool: profile limits, CEL rules and its hash-chained audit. The API checks permissions again itself,
    so a tool that bypasses Clearance is refused there too.</p>
    <p>One rule is specific to CI/CD: <b>an agent never satisfies a gate on its own change</b>. A Flight change is always a pull
    request; the human who merges it is also who satisfies the GitHub-merge provenance check (ADR-0027). The signing policy is
    admin-owned and never reachable from an agent.</p>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>New Clearance tool</th><th>Tier</th><th>Calls</th></tr></thead>
    <tbody>
      <tr><td><code>glidepath.flows.list</code>, <code>.flow.get</code>, <code>.logs.get</code>, <code>.explain</code></td><td>T0</td><td>flows, runs, logs, explain</td></tr>
      <tr><td><code>glidepath.releases.get</code>, <code>.evidence.get</code>, <code>.contract</code></td><td>T0</td><td>releases, evidence, contract</td></tr>
      <tr><td><code>glidepath.run.rerun</code>, <code>.run.cancel</code>, <code>.build</code>, <code>.preview</code></td><td>T1</td><td>replaces today's <code>pipeline.rerun</code></td></tr>
      <tr><td><code>glidepath.cicd.propose</code></td><td>T1</td><td><code>cicd:propose</code>, after the field-scope check</td></tr>
      <tr><td><code>glidepath.promote</code>, <code>.rollback</code>, <code>.pin</code></td><td>T2</td><td>propose only; T2 tools aren't capped by the tier ceiling</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>Agents and cicd.yaml: pull requests, limited by field</h2>
  <div class="prose">
    <p>Today Clearance's <code>BASELINE_DENY_PATHS</code> denies <code>cicd.yaml</code> for every agent. That keeps agents out
    of their own controls, but it also stops an agent from turning on a build cache, adding a Ground environment or fixing the
    source volume size it was just told is too small. Even Autopilot's own planner patches <code>cicd.yaml</code>. The
    file-level deny goes. In its place is the field-level scope Clearance already uses for values files (AF-9a), with each
    field's class read from the contract.</p>
  </div>
  {fig4}
  <div class="tbl"><table>
    <thead><tr><th>Change</th><th>Where</th></tr></thead>
    <tbody>
      <tr><td>Drop <code>cicd.yaml</code> and <code>**/cicd.yaml</code> from <code>BASELINE_DENY_PATHS</code>; keep <code>.tekton/**</code></td><td>autopilot <code>profile.py</code></td></tr>
      <tr><td>Make the baseline field denies file-qualified (<code>cicd.yaml#/secrets</code>), since <code>/release</code> means something else in a values file</td><td>autopilot <code>profile.py</code>, <code>scope.py</code></td></tr>
      <tr><td>Generate the human-only list from the contract instead of hard-coding it; tighten-only fields need a before and after comparison, not a glob</td><td>autopilot, from <code>glidepath-contract.json</code></td></tr>
      <tr><td>GP-SCOPE-001 human-only field changed, GP-SCOPE-002 a gate loosened, GP-SCOPE-003 a Flight environment added or retiered</td><td>glidepath <code>glidepath validate --base</code>, in each app's PR checks</td></tr>
      <tr><td>Agent PRs need a human approval and a human merge</td><td>the app repo's ruleset, unchanged</td></tr>
    </tbody>
  </table></div>
  <p class="note">The rule the old deny protected still holds: an agent never edits a control that constrains it. Secrets, signers,
  cloud deploy identity and the gates are those controls. A build flag isn't.</p>
</section>
""")

# ---------------------------------------------------------------------------------------------------------------
P.add(f"""
<section>
  <h2>What changes in Tower</h2>
  <div class="prose">
    <p>Tower keeps every route, every screen and every URL. What changes is where its backend gets each answer. Tower's
    backend plugin <code>glidepath</code> (<code>/api/glidepath/*</code>) gains one client for <code>glidepath-api</code>, and
    each group of routes gets a switch in config:</p>
  </div>
  <div class="gates">
    <div class="gate"><span class="n">1</span><div><p><b>direct</b>: today's code path, unchanged. The default for every group.</p></div></div>
    <div class="gate"><span class="n">2</span><div><p><b>shadow</b>: Tower serves the direct answer, calls the API in the background and records any difference as a metric (<code>tower_glidepath_api_shadow_mismatch_total{{group}}</code>) and a log line. Writes are never run twice. A shadowed write calls the API with <code>dryRun</code> and compares the plan with what Tower is about to do. This is the same live and shadow approach <code>glidepath-relay</code> used for ADR-0021.</p></div></div>
    <div class="gate"><span class="n">3</span><div><p><b>api</b>: the route calls the API and the direct code becomes the fallback. Going back is a config change.</p></div></div>
  </div>
  {fig5}
  <div class="tbl"><table>
    <thead><tr><th>Group</th><th>Tower today</th><th>After</th><th>Phase</th></tr></thead>
    <tbody>
      <tr><td class="area">Runs and logs</td><td><code>/pipeline-history</code>, <code>/runs</code>, <code>/run</code>, <code>/log</code>; browser hooks <code>useTektonPipelineRuns</code>, <code>useTaskRunLogs</code>, <code>useFleetPipelineRuns</code>, <code>useFleetPipelineHistory</code> through the proxy; chain slugs worked out in <code>chainSlug.ts</code></td><td>flows, runs and logs from the API. Hooks call Tower's backend, not the proxy. The chain slug comes with the flow</td><td>P1 shadow · P2 api</td></tr>
      <tr><td class="area">Supply chain and tests</td><td><code>/provenance</code>, <code>/head</code>, <code>/images</code>, <code>/tests</code>, <code>/tests/report</code> (Rekor, GHCR, Testkube through the service proxy)</td><td><code>/v1/images/{{digest}}/evidence</code></td><td>P1 shadow · P2 api</td></tr>
      <tr><td class="area">Release state</td><td><code>/release-records</code> and the record reads behind <code>/release-run</code> and <code>/deploy-history</code> (release-tracking ConfigMaps, read as the ingestor)</td><td><code>/v1/apps/{{app}}/releases</code></td><td>P1 shadow · P2 api</td></tr>
      <tr><td class="area">Run control</td><td><code>/tekton/rerun</code>, <code>/tekton/cancel</code> as <code>tower-actor</code>, held to shape by the <code>tower-pipelinerun-shape</code> policy</td><td><code>runs:rerun</code>, <code>:cancel</code></td><td>P3</td></tr>
      <tr><td class="area">cicd.yaml editor</td><td><code>/config/cicd</code>, <code>/config/cicd/schema</code>: Tower checks the patch and opens the PR</td><td><code>cicd:validate</code>, <code>cicd:propose</code>; the editor shows each field's owner and scope from the contract</td><td>P3</td></tr>
      <tr><td class="area">Promote, roll back, pin</td><td><code>/promote</code>, <code>/release/rollback-plan</code>, <code>/release/rollback</code>, <code>/pin</code>; eligibility worked out in Tower</td><td><code>environments:promote</code>, <code>:rollback</code>, <code>:pin</code>; eligibility from the API</td><td>P4</td></tr>
    </tbody>
  </table></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">Stays in Tower</span><h3>Not Glidepath's</h3><p>Argo CD actions (<code>/argo/*</code>, a delegated system). Config and values (<code>/config</code>, flight-base, env-xr, components, chart, platform-env: Airframe's contract). Break-glass, the cluster registry, pull requests, agent definitions.</p></div>
    <div class="card"><span class="eyebrow">Stays in Tower</span><h3>Tower's own products</h3><p>The Release Record and the release flow (<code>/release-record*</code>, <code>/release-draft</code>, <code>/release-mode</code>, <code>/release-planned</code>, <code>/release-calendar</code>, <code>/release-signoff</code>). They read release state from the API but are written by Tower. Image prune stays and reads "in use" from the API later.</p></div>
    <div class="card"><span class="eyebrow">Goes away in P6</span><h3>Tower loses write access to Tekton</h3><p><code>tower-actor</code>'s PipelineRun create and patch bindings on the dev cluster, the <code>tower-pipelinerun-shape</code> policy, the ingestor's Testkube service-proxy grant, Tower's Results cache, and the four proxy hooks. Tower then writes nothing on the dev cluster except break-glass.</p></div>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Risk</th><th>Answer</th></tr></thead>
    <tbody>
      <tr><td class="area">The API is down</td><td>Until P6 every group falls back to direct. After P6 Tower's CI/CD views depend on the API, the way they depend on Tekton Results today. The API runs two replicas and has its own readiness alert.</td></tr>
      <tr><td class="area">The two authorization checks disagree</td><td>Tower's owner check (<code>towerAuthz.ts</code>) keeps running in front of the API. Shadow mode also compares the API's decision with Tower's, and a mismatch blocks the cut-over for that group.</td></tr>
      <tr><td class="area">An extra hop is slower</td><td>The Results cache Tower built in <code>pipelineHistory.ts</code> moves into the API: a finished run never changes. Shadow mode records how long each side takes.</td></tr>
      <tr><td class="area">Two copies drift during the move</td><td>Each group is shadowed and then cut over on its own. Only groups that are switched to api are frozen in Tower; the rest keep shipping as usual.</td></tr>
    </tbody>
  </table></div>
</section>
""")

# ---------------------------------------------------------------------------------------------------------------
P.add(f"""
<section>
  <h2>Roadmap</h2>
  {fig6}
  <div class="track">
    <div class="row"><h3>P0 · Contract, validator, field scope</h3>{chip('Glidepath + Autopilot', 'info')}<p><code>cicd.meta.yaml</code>, the contract generator, <code>glidepath validate</code> with GP-* and GP-SCOPE rules, AGENTS.md and llms.txt. Clearance swaps the <code>cicd.yaml</code> file deny for field scope from the contract. No service yet. <b>Done when:</b> an agent PR that turns on <code>build.cache</code> passes, and one that turns off <code>governance.sast</code> or touches <code>secrets</code> is refused by Clearance and fails CI.</p></div>
    <div class="row"><h3>P1 · Read API, Tower in shadow</h3>{chip('Glidepath + Tower', 'info')}<p><code>glidepath-api</code> with flows, runs, logs, releases and evidence, its OpenAPI spec, authentication and SubjectAccessReview. Tower's runs, supply chain and release-state groups go to shadow. <b>Done when:</b> seven days with no shadow mismatches on every app on the dev cluster.</p></div>
    <div class="row"><h3>P2 · Read cut-over, agent reads</h3>{chip('Tower + Autopilot', 'info')}<p>Those three groups switch to api. Clearance gets the T0 <code>glidepath.*</code> tools. <code>explain</code> ships with the first knownFailures. <b>Done when:</b> an agent starting cold names the right failure id for a seeded failed flow, using only MCP.</p></div>
    <div class="row"><h3>P3 · T1 actions</h3>{chip('Glidepath + Tower', 'info')}<p>Re-run, cancel, build a branch, previews, <code>cicd:propose</code>. Tower's run-control and cicd-editor groups go through dry-run shadow, then api. <code>pipeline.rerun</code> is retired. <b>Done when:</b> a re-run from Tower and one from an agent each create exactly one PipelineRun, and each is audited with both identities.</p></div>
    <div class="row"><h3>P4 · T2 propose</h3>{chip('Glidepath + Tower', 'info')}<p>Promote, roll back and pin, each opened by Glidepath's release pipeline as today. Tower's promote group moves. <b>Done when:</b> an agent proposes a staging promotion, a human merges it, the release record reaches healthy, and the agent had no way to merge it.</p></div>
    <div class="row"><h3>P5 · Events</h3>{chip('Glidepath + Autopilot', 'info')}<p><code>/v1/events</code> and AMQP topics. An Autopilot event agent triages a failed flow and opens a <code>cicd.yaml</code> or code PR. <b>Done when:</b> a seeded failure produces a correct triage PR without anyone stepping in.</p></div>
    <div class="row"><h3>P6 · Retire the duplicates</h3>{chip('Tower + clusters', 'info')}<p>Remove Tower's direct paths, the proxy hooks, <code>tower-actor</code>'s Tekton bindings and the shape policy. <b>Done when:</b> <code>kubectl auth can-i</code> shows Tower's identities can't create or patch a PipelineRun.</p></div>
  </div>
</section>

<section>
  <h2>Open decisions</h2>
  <div class="prose">
    <p><b>Which GitHub identity opens an agent's pull request.</b> This only matters for the content an agent writes, which is
    <code>cicd.yaml</code> and code. Promote, rollback and pin PRs are opened by Glidepath's release pipeline, as they are today.</p>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Option</th><th>Verdict</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td class="area">A separate GitHub App for agents</td><td>{chip('Leaning', 'ok')}</td><td>The PR author shows it was an agent. It is installed only on the repos it needs, with contents and pull requests and never checks. Each call mints a one-hour installation token, so nothing is stored. It isn't on any ruleset bypass list, so it can't merge. This is Autopilot's D4.</td></tr>
      <tr><td class="area">Glidepath's existing bot or the Pipelines-as-Code app</td><td>{chip('No', 'bad')}</td><td>Blurs who wrote the change, and the Pipelines-as-Code app can write status checks, so an agent holding it could post a passing gate.</td></tr>
      <tr><td class="area">The person's own token</td><td>{chip('No', 'bad')}</td><td>Correct attribution, but the agent inherits that person's merge rights and their token has to be held somewhere.</td></tr>
    </tbody>
  </table></div>
  <ul class="plain">
    <li><b>People's OIDC issuer for the CLI.</b> Dex is already deployed. Tower doesn't need it, since it presents <code>tower-actor</code>.</li>
    <li><b>Group membership for SubjectAccessReview.</b> Tower knows a user's teams from the catalog. Glidepath standalone needs them from the token. The RoleBindings name groups either way.</li>
    <li><b>API versioning.</b> Proposed: copy Airframe's v1alpha1 rules. Additions are free; any tightening is a breaking change.</li>
  </ul>
</section>

<section>
  <h2>Not in scope</h2>
  <ul class="plain">
    <li>Argo CD control and app configuration. Those belong to Argo CD and Airframe, and Tower keeps them.</li>
    <li>Any write to a Flight cluster. A release stays a gitops pull request that Argo CD syncs.</li>
    <li>Replacing Pipelines-as-Code ChatOps. <code>/retest</code> on a PR keeps working, and the API is a second way to do the same thing.</li>
  </ul>
</section>
""")
