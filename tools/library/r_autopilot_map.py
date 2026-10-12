"""Spec: Autopilot drawn as Kubernetes resources, checked against the code on Oct 7, 2026."""
from report import Page, chip, tick, esc
import lib
from lib import node, path, zone, hlab, vlab, lab, text, legend

P = Page(
    'autopilot-architecture-map', 'Architecture', 'Autopilot · Architecture map',
    'Autopilot, drawn as Kubernetes resources',
    'Autopilot as built and drafted on October 7, 2026: Clearance, the AgentRun XR, the run namespace, the five-document contract chain, the parachute acceptance test, the flight recorder, and six gaps found while drawing it.',
    '2026-10-07',
    meta=[('Snapshot', 'checked against the code on Oct 7, 2026'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/hangar/autopilot/design/">Autopilot design</a>')],
    lede=('I kept describing Autopilot in words, and the words kept drifting away from the code. So I drew it the way '
          'the cluster would see it, as Kubernetes resources, and checked every box against the code on October 7, 2026. '
          'This page is that drawing. It\'s a snapshot, so some of what it calls a draft may have moved since, and drawing '
          'it turned up six things the code says that the docs didn\'t.'))

P.add("""
<div class="verdict info">
  <span class="stamp">Snapshot · Oct 7, 2026 · core built, runtime drafted</span>
  <h2>One Deployment, three jobs, and a grant it never hands out.</h2>
  <ul>
    <li><b>Clearance</b> is the MCP server agents talk to, the policy engine that decides every call, and the keeper of each session's grant.</li>
    <li>It never hands out a signed contract. It keeps the grant itself and re-checks it on every call.</li>
    <li>To run an agent in the cluster it creates one <b>AgentRun XR</b>, and Crossplane turns that into a locked-down namespace whose pod can reach only Clearance and the model proxy.</li>
    <li>On the day: Clearance's core was built and tested but not deployed. Most of the cluster side was a draft, written and unit-tested, never applied.</li>
  </ul>
</div>
""")

# The six questions.
QA = [
    ('Is Clearance an MCP server?', 'yes', 'Three MCP tools, the rest are arguments',
     '<code>tools_list</code>, <code>session_open</code>, <code>call</code>. Hangar tools such as <code>repo.pr.open</code> or '
     '<code>run.spawn</code> are names passed to <code>call</code>, so one gate sees everything. Built on stdio; the HTTP transport isn\'t built.'),
    ('A policy engine?', 'yes', '21 CEL deny rules, fail closed',
     'R000 to R020, first match wins, and any evaluation error is R000 and a deny. Tiers T0 to T3, path and field scope, repo and API '
     'allowlists, budgets. A denial returns the rule id and a fix hint to the agent.'),
    ('A contract issuer and validator?', 'partly', 'Issues a session, keeps it, checks every call',
     'There is no signed token a run carries. The grant lives in Clearance\'s memory, keyed by session id. Knowing a session id '
     'gives nothing: R001 checks the caller\'s identity against the session\'s principal.'),
    ('Does it create the AI workload?', 'yes', 'By creating an AgentRun, not an Agent',
     '<code>launch</code> (top level) or <code>run.spawn</code> (a child) creates the XR. Its one Kubernetes permission is a Role on '
     'agentruns in <code>autopilot-runs</code>. Agent is the planned XRD form of the AgentDefinition (Phase C).'),
    ('Does the workload talk back to Clearance?', 'yes', 'It\'s the only thing it can talk to',
     'NetworkPolicy allows DNS, Clearance and the model proxy, nothing else. The pod has two projected tokens, one per audience, '
     'valid for an hour, and no other credential.'),
    ('Can outside clients use it?', 'yes', 'And many never get a run pod',
     'Claude Code or a Tower user opens a session and calls tools with its own loop, so there is no AgentRun at all. Task, '
     'scheduled, event and team agents get one. Service agents are ordinary apps.'),
]
cards = ''.join(
    f'<div class="card"><span class="eyebrow">{esc(q)}</span><h3>{esc(h)}</h3>'
    f'<div>{chip(a, "ok" if a == "yes" else "warn")}</div><p>{body}</p></div>'
    for q, a, h, body in QA)

A = lib.ACC
STATE = [('backend', 'built and tested'), ('propose', 'draft, never applied'),
         ('optional', 'proposal'), ('external', 'exists today'), ('accent', 'request path')]

# Figure 1: one request, through the resources it touches.
W, H = 760, 720
b = zone(44, 24, 672, 88, 'Who talks to Clearance')
for i, (n, s, k) in enumerate([('A person in Tower', 'or the Autopilot plugin', 'optional'),
                               ('Claude Code', 'any MCP client, no run', 'optional'),
                               ('HolmesGPT', 'SA token, TokenReview', 'optional'),
                               ('Trigger bridge', 'and the interval runner', 'backend')]):
    b += node(60 + i * 164, 48, 148, 48, n, s, k)
b += zone(44, 144, 672, 188, 'autopilot-system')
b += zone(52, 168, 496, 148, 'clearance · Deployment', right=True)
cl = [[('MCP server', 'stdio · 3 tools', 'backend'), ('Authenticate', 'OAuth, TokenReview', 'optional'),
       ('Policy engine', '21 CEL deny rules', 'backend'), ('Session store', 'the grant, memory', 'backend')],
      [('Run launcher', 'AgentRun, fake k8s', 'backend'), ('Gateway', 'audit, spend, call', 'backend'),
       ('Airframe tools', 'airframe.* planner', 'backend'), ('Record writer', 'hash-chained JSONL', 'backend')]]
for r, row in enumerate(cl):
    for i, (n, s, k) in enumerate(row):
        b += node(68 + i * 118, 192 + r * 60, 110, 48, n, s, k)
b += node(564, 200, 136, 56, 'model-proxy', 'allowlist · budget', 'backend')
b += text(632, 274, 'forwarder not built', 9, 400, lib.MUTED, anchor='middle', mono=True)
# 1: callers to Clearance.
b += path([(241, 112), (241, 188)], 'accent') + vlab(241, 112, 144, 'session_open · call') + lab(241, 150, '1', A)
# 3: Clearance creates the AgentRun.
b += zone(44, 356, 208, 96, 'autopilot-runs', right=True)
b += node(60, 384, 176, 52, 'AgentRun', 'catalog.hangar.io XR', 'propose')
b += path([(123, 300), (123, 380)], 'accent') + lab(123, 334, '3', A)
b += zone(268, 356, 448, 96, 'crossplane-system')
b += node(284, 384, 184, 52, 'function-agentrun', 'one Pipeline step, tested', 'propose')
b += node(500, 384, 200, 52, 'provider-kubernetes', '6 Objects, never secrets', 'propose')
b += path([(236, 410), (280, 410)], 'accent') + lab(258, 392, '4', A)
b += path([(468, 410), (496, 410)], 'accent')
# The run namespace.
b += zone(44, 480, 672, 172, 'agent-r-<id> · one per run')
objs = [('Namespace', 'restricted PSS'), ('ResourceQuota', 'secrets 0 · jobs 1'),
        ('NetworkPolicy ×2', 'Clearance + proxy only'), ('ServiceAccount', 'no token automount'),
        ('Job', 'backoffLimit 0')]
for i, (n, s) in enumerate(objs):
    b += node(60 + i * 129, 508, 124, 48, n, s, 'propose')
b += path([(600, 436), (600, 476)], 'accent') + vlab(600, 436, 480, 'applies', A, side='l')
b += path([(638, 556), (638, 584)])
b += node(300, 588, 360, 48, 'Run pod', 'image by digest · non-root · read-only root · 2 tokens', 'propose')
# 5 and 6: the pod can reach only Clearance and the model proxy.
b += path([(300, 612), (30, 612), (30, 216), (64, 216)], 'accent') + lab(30, 400, '5', A)
b += path([(660, 612), (730, 612), (730, 228), (704, 228)], 'accent') + lab(730, 400, '6', A)
b += hlab(30, 300, 612, 'tools, clearance token')
b += hlab(660, 730, 612, 'models')
b += legend(684, STATE, W)
fig1 = P.fig(b, W, H, 'One request, through every resource it touches',
             'Callers open sessions on Clearance in autopilot-system. Clearance creates an AgentRun XR in autopilot-runs; function-agentrun and provider-kubernetes compose a namespace agent-r-<id> with a quota, two network policies, a service account and a Job. The run pod can reach only Clearance and the model proxy.',
             'Everything here lives in the dev cluster: runs and agent writes exist only there, and the component is refused on an upper cluster. Box borders show build state; the amber numbers match the steps below. The pod holds no Secrets, no provider keys and no kubectl.')

# Figure 2: what Clearance reaches, and where every decision lands.
W2, H2 = 760, 590
c = node(40, 40, 128, 480, 'Clearance', 'gateway · adapters', 'focal')
c += zone(200, 24, 536, 152, 'Services Clearance calls')
svc = [[('TokenReview', 'who is this pod?', 'external'), ('Token interceptor', 'repo-scoped GitHub token', 'optional'),
        ('Argo CD', 'role:clearance-lower', 'optional')],
       [('Backstage', 'MCP actions, partly built', 'backend'), ('Prometheus · Loki', 'metrics, logs, app APIs', 'external'),
        ('Model backends', 'only the proxy holds keys', 'optional')]]
for r, row in enumerate(svc):
    for i, (n, s, k) in enumerate(row):
        c += node(216 + i * 172, 52 + r * 60, 160, 48, n, s, k)
c += path([(168, 76), (212, 76)], 'accent') + lab(190, 58, '7', A)
c += zone(200, 200, 536, 152, 'Git · reviewed, pulled by Argo CD')
git = [[('autopilot repo', 'AgentDefinitions: the ceiling', 'backend'), ('gitops-cluster-dev', 'XRD, Composition, RBAC: not applied', 'propose')],
       [('<app> repos', 'Ground PRs, may auto-merge (T1)', 'external'), ('gitops-<app> · tenants', 'Flight PRs, propose only (T2)', 'external')]]
for r, row in enumerate(git):
    for i, (n, s, k) in enumerate(row):
        c += node(216 + i * 264, 228 + r * 60, 248, 48, n, s, k)
c += path([(212, 252), (172, 252)], dashed=True) + lab(190, 234, 'loads')
c += path([(168, 312), (212, 312)], 'accent') + lab(190, 294, '8', A)
c += zone(200, 376, 536, 152, 'Flight recorder · one task_id on every record')
rec = [[('Audit chain', 'JSONL · prev_hash · hash', 'backend'), ('Object-lock bucket', 'WORM copy, in MinIO', 'optional'),
        ('Rekor anchor', 'anchors count and head', 'optional')],
       [('OTel spans', 'tool and LLM spans, tokens', 'optional'), ('task_id stamps', 'commit, PR label, app', 'optional'),
        ('Readers', 'plugin, Agent tab, record', 'optional')]]
for r, row in enumerate(rec):
    for i, (n, s, k) in enumerate(row):
        c += node(216 + i * 172, 404 + r * 60, 160, 48, n, s, k)
c += path([(168, 428), (212, 428)], 'accent') + lab(190, 410, '9', A)
c += legend(560, STATE[:4], W2)
fig2 = P.fig(c, W2, H2, 'What Clearance reaches, and where every decision lands',
             'Clearance calls TokenReview, a token interceptor, Argo CD, Backstage, Prometheus, Loki and app APIs through adapters. It loads AgentDefinitions from the autopilot repo and writes only PRs to app and gitops repos. Every decision lands in a hash-chained audit chain, with an object-locked copy, a Rekor anchor, OpenTelemetry spans and task_id stamps proposed around it.',
             'The adapters were interfaces and fakes on Oct 7, 2026. Model backends sit outside the cluster and only the model proxy talks to them. In the recorder only the chain itself was built; the bucket was decided (D5) but not created.')

STEPS = [
    ('A caller opens a session with <code>session_open(agent, claim)</code>.', 'A workload definition must be called by its own service account; a delegated one must be called by a person.'),
    ('Clearance computes the grant.', 'The AgentDefinition\'s limits, narrowed by the caller\'s request and, for a child, by what the parent has left. Any widening is denied (R007). The reply carries the session id, task_id, deadline and effective limits.'),
    ('For an in-cluster run, Clearance creates one AgentRun in <code>autopilot-runs</code>.', 'Afterwards it can only patch <code>spec.frozen</code> (the breaker) or delete it (<code>run.close</code>).'),
    ('Crossplane calls function-agentrun, which renders six provider-kubernetes Objects.', 'provider-kubernetes applies them into <code>agent-r-&lt;id&gt;</code>. A bad request is Rejected and renders nothing.'),
    ('The agent calls tools at <code>CLEARANCE_URL</code> with its clearance-audience token.', 'Each call goes through authenticate, rules, audit, spend, adapter, audit.'),
    ('Model calls go to <code>MODEL_PROXY_URL</code>.', 'The proxy checks the model allowlist and <code>model_tokens</code> on the same session, then forwards with a key only it holds.'),
    ('Allowed calls reach real services through adapters.', 'TokenReview, the interceptor, Argo CD (lower environments only), Backstage, Prometheus, Loki, app APIs. The adapters are interfaces and fakes today.'),
    ('Writes leave only as PRs.', 'The interceptor mints a GitHub token scoped to one repo for one call. Ground PRs may auto-merge; Flight PRs are propose-only and a person merges them.'),
    ('Every decision, allowed or denied, becomes one hash-chained record with the task_id.', ''),
]
gates = ''.join(f'<div class="gate"><span class="n">{i}</span><div><p>{t}</p>'
                + (f'<p class="when">{w}</p>' if w else '') + '</div></div>'
                for i, (t, w) in enumerate(STEPS, 1))
gates += ('<div class="gate"><span class="n">∎</span><div><p>At <code>expiresAt</code> the function renders nothing and Crossplane deletes the namespace, with or without Clearance alive.</p>'
          '<p class="when">A tripped breaker cuts egress and holds the run 15 minutes for forensics, then it expires.</p></div></div>')

# Figure 3: the contract narrows.
W3, H3 = 760, 290
d = ''
chain = [('AgentDefinition', 'git · ttlMinutes 10 · modelTokens 120000 · the ceiling', 'backend'),
         ('The caller\'s request', 'ttl_minutes 5 · model_tokens 60000', 'input'),
         ('Session (the grant)', 'enforced on every call', 'focal'),
         ('AgentRun spec', '3 of 6 budgets · deadline enforced', 'store'),
         ('Runtime env', 'information only', 'external')]
for i, (n, s, k) in enumerate(chain):
    y, w = 24 + i * 48, 712 - i * 72
    fill, stroke, dash = lib.KINDS[k]
    da = f' stroke-dasharray="{dash}"' if dash else ''
    d += f'<rect x="24" y="{y}" width="{w}" height="38" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"{da}/>'
    d += text(40, y + 24, n, 12, 600, lib.INK)
    d += text(24 + w - 16, y + 24, s, 10, 400, lib.MUTED, anchor='end', mono=True)
d += tick(430, 140)
d += text(24, 274, 'Each copy can only narrow the one above it. Only the session is checked on each call.', 11, 400, lib.MUTED)
fig3 = P.fig(d, W3, H3, 'Five documents, each narrower than the last',
             'The AgentDefinition in git is the ceiling. The caller\'s request narrows it, Clearance\'s session holds the result and enforces it, and the AgentRun spec and runtime env carry shrinking copies for information.',
             'The flight-briefer example from the code: the definition allows 10 minutes and 120000 model tokens, the request asks for 5 and 60000, and that is what the session enforces.')

TRACK = [
    ('The parachute plan is denied by Clearance\'s own baseline.', 'Blocks M3 exit.',
     'The planner\'s app-repo step patches <code>cicd.yaml</code>. <code>BASELINE_DENY_PATHS</code> puts <code>cicd.yaml</code> off-limits to every agent, and '
     '<code>test_dispatch.py</code> asserts that exact denial (R015). Run end to end, the sentence stops at step 3. This needs a decision: a field-level '
     'allow for <code>/deploy/environments</code> using the AF-9a machinery, or hand that step to a person through Tower\'s existing <code>cicd.yaml</code> PR flow.'),
    ('The planner is stale against the environments overhaul.', '1 test failing.',
     '234 of 235 tests pass. The failure: the planner emits <code>deploy.lowerEnvironments</code>, <code>upperEnvironments</code> and <code>promotionOrder</code>, '
     'and Glidepath\'s schema now accepts only <code>deploy.environments</code> (ADR-0019). It also writes <code>platform/envs/*.yaml</code>, while apps now use <code>glidepath/envs/</code>.'),
    ('A run pod can\'t pass R001 yet.', 'Design gap.',
     'R001 compares the caller with <code>session.principal</code>, which is the person or the definition\'s service account. A run pod authenticates as '
     '<code>system:serviceaccount:agent-r-&lt;id&gt;:run</code>. Nothing maps one to the other. The unbuilt auth adapter has to, for example by finding the '
     'AgentRun that owns that namespace and taking its <code>sessionId</code>.'),
    ('The recorder can\'t reconstruct what a run was allowed to do.', 'Audit gap.',
     'The <code>session.open</code> record stores the caller\'s request only as a hash and doesn\'t store the effective limits, and sessions live only in memory. '
     'After a restart the grant is gone. The limits hold no secrets, so recording them in that record costs nothing.'),
    ('The drafts still used the old API group.', 'Drift.',
     '<code>manifests.py</code> and the AgentRun XRD said <code>catalog.idp.io</code>; the Tier 2 rename had moved everything to <code>catalog.hangar.io</code>, '
     'and <code>design.md</code>\'s Role already used the new group.'),
    ('The counts in the docs were out of date.', 'Docs.',
     'The docs said 19 CEL rules and 255 tests. The code had 21 rules (R000 to R020, with R020 for field scope added by AF-9a) and 235 tests.'),
]
track = ''.join(f'<div class="row"><h3>{esc(t)}</h3>{chip("Found Oct 7, 2026", "warn")}<p><b>{tag}</b> {body}</p></div>'
                for t, tag, body in TRACK)

PRE = 'margin:0;padding:14px 16px;font-family:var(--mono);font-size:.8rem;line-height:1.5'

P.add(f"""
<section>
  <h2>Six questions, answered from the code</h2>
  <div class="cards">{cards}</div>
</section>

<section>
  <h2>The map</h2>
  <div class="prose"><p>One request, through every resource it touches. Box borders show build state. Most of the cluster side was a draft on October 7, 2026: written and unit-tested, never applied. The amber numbers are the order things happen in.</p></div>
  {fig1}
  {fig2}
</section>

<section>
  <h2>The request, step by step</h2>
  <div class="gates">{gates}</div>
</section>

<section>
  <h2>The contract, in practice</h2>
  <div class="prose"><p>What gets called "the contract" is a chain of five documents. The AgentDefinition in git is the ceiling. Every later copy can only narrow it, and only the session inside Clearance is checked on each call. The copies in the AgentRun and the pod are for information, except the deadline, network mode, compute and sandbox, which the composition enforces on its own.</p></div>
  {fig3}
  <div class="tbl"><table>
    <thead><tr><th>Document</th><th>Who writes it</th><th>Where it lives</th><th>Who can see it</th><th>What's in it</th><th>Enforced by</th></tr></thead>
    <tbody>
      <tr><td class="area">AgentDefinition</td><td>A person, in a reviewed PR</td><td><code>agents/*.yaml</code> in the autopilot repo; Clearance loads it</td><td>Anyone who can read the repo</td><td>Identity, tier ceiling, tools, repos, APIs, models, network, compute, all budgets and TTL, image digest, triggers</td><td>It is the ceiling</td></tr>
      <tr><td class="area">The caller's request</td><td>The caller: a person, a trigger, or a parent run</td><td>The <code>claim</code> argument of <code>session_open</code> or <code>run.spawn</code></td><td>Clearance. The audit keeps only its hash</td><td>Optional lower values for any limit</td><td>R007 if anything widens</td></tr>
      <tr><td class="area">Session (the grant)</td><td>Clearance, by <code>narrow()</code></td><td>Clearance memory only</td><td>Clearance. The caller gets one copy of the limits in the reply</td><td>Effective limits, used and reserved counters, deadline, breaker, parent and children</td><td>Clearance, on every call</td></tr>
      <tr><td class="area">AgentRun spec</td><td>Clearance (<code>agentrun_manifest</code>)</td><td>etcd, namespace <code>autopilot-runs</code></td><td>Whoever RBAC lets read agentruns there</td><td>Agent, image digest, sandbox, compute, network, deadline, ids, 3 of the 6 budgets</td><td>Composition: deadline, network, compute, sandbox</td></tr>
      <tr><td class="area">Runtime env</td><td>function-agentrun</td><td>The pod spec</td><td>The agent process</td><td><code>HANGAR_*</code> ids, deadline, limits JSON, two URLs, token paths</td><td>Nothing: information</td></tr>
    </tbody>
  </table></div>
  <div class="verdict ok">
    <span class="stamp">Does it hold the budget? Yes</span>
    <p>The session holds six limits: the TTL plus five counters (<code>tool_calls</code>, <code>github_calls</code>, <code>open_prs</code>, <code>model_tokens</code>, <code>children</code>), and spends them as calls happen. A child run reserves its budget out of the parent's remainder when it starts, and its real usage rolls up when it closes, so a team can never spend more than its root was granted. A 200-sequence property test covers this.</p>
    <p>Five denied calls, a tripwire, or a token overrun trips the breaker. The counters exist only in Clearance's memory: a restart ends every session, which is the safe direction, and the runs still stop on time.</p>
  </div>
</section>

<section>
  <h2>The acceptance test: the parachute sentence</h2>
  <p class="quote">"Provision a new python application named parachute. Give it a dev and test ground environment, a staging and prod flight environment, and configure it with one 100% weight canary step and a URL=http://myendpoint.io env var."</p>
  <ul class="plain">
    <li>A person says it to a coding agent, in Tower chat or in Claude Code (step 1). The session gets <code>repo.pr.open</code>, <code>xr.request</code>, <code>repo.pr.open_upper</code> and the <code>airframe.*</code> tools.</li>
    <li>The agent writes the AppSpec below and calls <code>airframe.plan</code>. The planner, inside Clearance, compiles it into an ordered ChangeSet with no network and no clock, so the same input gives the same plan.</li>
    <li><code>airframe.apply</code> walks the plan as PRs (steps 7 and 8). Each step's tier decides the gate: Ground and tenants work is T1, Flight values are T2 propose-only.</li>
    <li>A person merges the Flight PRs. Argo CD and Glidepath do the rest, and <code>airframe.verify</code> checks the result.</li>
    <li>Every step is on the record under one task_id, so a killed session can resume from the PR labels and the log.</li>
  </ul>
  <div class="tbl"><pre style="{PRE}">apiVersion: airframe/v1
kind: AppSpec
app: parachute
stack: python
environments:
  ground: [dev, test]
  flight:
    - {{ name: staging }}
    - {{ name: prod }}
config:
  rollout:
    strategy: canary
    steps: [{{ setWeight: 100 }}]
  env:
    - {{ name: URL, value: "http://myendpoint.io" }}</pre></div>
  <div class="tbl"><table>
    <thead><tr><th>Plan step (real output)</th><th>Repo</th><th>Gate</th><th>Files</th></tr></thead>
    <tbody>
      <tr><td class="area">tenants</td><td>gitops-cluster-dev-tenants</td><td>human merge</td><td>A PythonApplication XR plus two ApplicationEnvironment XRs (staging and prod, on the prod cluster)</td></tr>
      <tr><td class="area">repos-ready</td><td>gitops-cluster-dev-tenants</td><td>wait</td><td>Crossplane creates the app and gitops repos</td></tr>
      <tr><td class="area">app-repo</td><td>the parachute app repo</td><td>auto-merge</td><td><code>cicd.yaml</code> patch, <code>platform/envs/dev.yaml</code>, <code>test.yaml</code></td></tr>
      <tr><td class="area">tekton-resync</td><td>the parachute app repo</td><td>auto-merge</td><td>Glidepath regenerates <code>.tekton/</code></td></tr>
      <tr><td class="area">gitops</td><td>gitops-parachute</td><td>human merge</td><td><code>&lt;cluster&gt;/staging/values.yaml</code>, <code>&lt;cluster&gt;/prod/values.yaml</code></td></tr>
      <tr><td class="area">verify</td><td>none</td><td>verify</td><td>XRs Ready and CicdOnboarded, the dev namespace's Application Synced</td></tr>
    </tbody>
  </table></div>
  <p class="note">The planner raises two warnings on its own: the environment name <code>test</code> collides with the pipeline stage name, and a single 100% step promotes at once with no ramp. The app-repo row is where the plan broke on October 7, 2026; see the first two gaps below.</p>
</section>

<section>
  <h2>The flight recorder</h2>
  <div class="prose"><p>Clearance writes one record per decision, allowed or denied, chained to the one before. Arguments are kept only as a hash, so a secret that slips into a call never lands in the log. The chain proves nobody edited, deleted or reordered records. It can't prove nobody cut off the tail, which is why the checkpoint gets anchored in Rekor and copied to an object-locked bucket.</p></div>
  <p class="note">A denial the agent can fix:</p>
  <div class="tbl"><pre style="{PRE}">{{"seq": 43, "ts": "2026-10-07T13:56:20Z",
 "task_id": "t-3f9a1c2b7d10",
 "session": "s-3f9a1c2b7d10", "parent": null,
 "principal": "user:james",
 "agent": "flight-briefer",
 "tool": "app.api.get", "tier": 0,
 "decision": "deny", "rule": "R017",
 "args_sha256": "51aa…",
 "result": "that application API is not on this agent's allowlist",
 "prev_hash": "d17a…", "hash": "0b3f…"}}</pre></div>
</section>

<section>
  <h2>Found while drawing this</h2>
  <div class="prose"><p>Six things the code said that the docs didn't. Each was checked against the autopilot repo on October 7, 2026, not taken from the docs. I haven't rechecked them for this page, so treat each as found on that day.</p></div>
  <div class="track">{track}</div>
  <p class="note">Sources: the autopilot repo's <code>src/clearance/</code> (dispatch, session, limits, policy, audit, modelproxy, manifests, server, airframe_plan), <code>airframe-drafts/</code> (XRD, composition, function-agentrun, RBAC) and <code>agents/</code>, plus the Hangar docs: the Autopilot design, roadmap, glossary and decisions. Example ids and timestamps are illustrative; field names and shapes are the code's.</p>
</section>
""")
