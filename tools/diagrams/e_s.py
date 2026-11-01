"""The API set: pictures for the essay "A CI/CD engine you can call" (2026-11-01)."""
from libx import *


def zonex(x, y, w, h, label, lx):
    """A zone whose label sits at lx, between the connectors that cross its top edge."""
    lw = up4(len(label) * 5.6 + 16)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.16)" stroke-width="0.8"/>'
            f'<rect x="{lx}" y="{y+4}" width="{lw}" height="12" rx="2" fill="{PAPER}"/>'
            f'<text x="{lx+lw/2}" y="{y+13}" fill="{MUTED}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing="0.14em">{esc(label.upper())}</text>')


def s_front_door():
    b = []
    b += [zone(24, 100, 952, 96, 'who calls'), zone(24, 228, 952, 88, 'how they reach it'),
          zonex(24, 344, 952, 96, 'glidepath · one api', 176), zonex(24, 468, 952, 104, 'reads and starts', 136)]
    callers = [('Tower', 'the developer portal', 'input'), ('Clearance', 'MCP tools for agents', 'input'),
               ('A script or pipeline', 'a ServiceAccount token', 'input'), ('A person', 'a people-dex ID token', 'input')]
    for i, (n, s, k) in enumerate(callers):
        x = 48 + i * 232
        b.append(path([(x + 104, 172), (x + 104, 252)], 'link'))
    b.append(path([(152, 300), (152, 368)], 'link'))
    b.append(path([(500, 300), (500, 368)], 'link'))
    b.append(path([(848, 300), (848, 368)], 'link'))
    for i, (n, s, k) in enumerate(callers):
        b.append(node(48 + i * 232, 124, 208, 48, n, s, k))
    b.append(node(48, 252, 208, 48, 'API server proxy', 'from the other cluster', 'external'))
    b.append(node(280, 252, 440, 48, 'The Service, in the cluster', 'glidepath-api.platform-system:8080'))
    b.append(node(744, 252, 208, 48, 'Gateway route', '/v1 only · since Nov 1', 'propose'))
    b.append(node(48, 368, 904, 48, 'glidepath-api',
                  '2 replicas · 30 operations · TokenReview + SubjectAccessReview · audit, metrics, traces', 'focal'))
    b.append(path([(500, 416), (500, 452)], marker=False))
    b.append(path([(118, 452), (878, 452)], marker=False))
    srcs = [('Tekton Results', '30 days of runs, logs'), ('Live Tekton', 'runs in flight, pod logs'),
            ('Testkube', 'test runs, JUnit'), ('Sigstore + GHCR', 'signatures, re-verified'),
            ('GitHub, read', 'a token per request'), ('CDEvents broker', 'events, re-verified')]
    for i in range(6):
        cx = 118 + i * 152
        b.append(path([(cx, 452), (cx, 492)]))
    for i, (n, s) in enumerate(srcs):
        b.append(node(48 + i * 152, 492, 140, 56, n, s, 'store' if i < 3 else 'external'))
    b.append(callout(24, 612, 'Every caller gets the same answers, decided the same way, in the same place.'))
    b.append(legend(644, [('input', 'Who calls'), ('propose', 'The new route'), ('focal', 'The API'),
                          ('store', 'Platform data'), ('external', 'Outside the API'), ('link', 'HTTP')]))
    return dict(slug='one-front-door', eyebrow='API · 01 of 03 · The shape',
      title='One front door for CI/CD',
      desc='Four callers, Tower, Clearance with its MCP tools for agents, a script or pipeline with a ServiceAccount token, and a person with a people-dex ID token, reach glidepath-api three ways: through the API server proxy from the other cluster, through the Service inside the cluster, or over the new Gateway route that serves only /v1. glidepath-api runs two replicas with 30 operations, decides each call with a TokenReview and a SubjectAccessReview, and records an audit line, metrics and a trace. It reads Tekton Results, live Tekton runs and pod logs, Testkube, Sigstore and GHCR, GitHub with a read token minted per request, and the CDEvents broker.',
      lede='Tower, agents, scripts and people all ask the same API. How they get to it differs; what they are allowed to do, and what gets written down, does not.',
      body=''.join(b), W=1000, H=684, y0=76,
      cards=[('One contract', '', P('30 operations in one OpenAPI file, each with a tier. A test fails if the server and the spec ever differ.')),
             ('Three ways in', 'link', P('The API server proxy for the other cluster, the Service inside it, and since November 1 a Gateway route for people.')),
             ('Sources stay behind it', 'accent', P('No caller reads Tekton Results, Testkube or Rekor itself any more, or holds a GitHub token.'))])


def s_decided():
    b = []
    b += [zone(24, 100, 952, 140, 'every call, in order'), zonex(24, 268, 952, 88, 'refused, with a rule', 160),
          zone(24, 384, 952, 80, 'written down, either way')]
    steps = [('Who are you?', 'TokenReview, or an ID token', 'authenticate', 'backend'),
             ('Acting for whom?', 'On-Behalf-Of: delegates only', 'delegate', 'backend'),
             ('May you?', 'SubjectAccessReview, app ns', 'authorize', 'focal'),
             ('Do it', 'read · re-run · propose', 'act', 'backend'),
             ('Answer', 'JSON, a stable rule id', 'respond', 'backend')]
    for i in range(4):
        x = 48 + i * 184
        b.append(path([(x + 168, 172), (x + 184, 172)], 'accent' if i == 2 else 'muted'))
    refusals = [('GP-AUTH-001 / 002', 'no token, or not accepted'), ('GP-AUTH-003 / 004', 'not a delegate · no person'),
                ('GP-AUTHZ-001', '404 only if you could read'), ('GP-API-422', 'shape lock or plan said no')]
    for i in range(4):
        cx = 48 + i * 184 + 84
        b.append(path([(cx, 212), (cx, 292)], dashed=True))
    b.append(path([(868, 212), (868, 408)]))
    for i, (n, s, t, k) in enumerate(steps):
        b.append(node(48 + i * 184, 132, 168, 80, n, s, k, tag=t))
    for i, (n, s) in enumerate(refusals):
        b.append(node(48 + i * 184, 292, 168, 48, n, s, 'optional'))
    b.append(node(48, 408, 904, 40, 'One audit line, one metric, one span',
                  'op · tier · app · caller · onBehalfOf · decision · status · ms · traceId', 'store'))
    b.append(callout(24, 508, 'The cluster already knows who you are. RBAC only needs the strings.'))
    b.append(legend(540, [('focal', 'The decision'), ('backend', 'A step'), ('optional', 'A refusal'),
                          ('store', 'The record'), ('muted-dash', 'Refused')]))
    return dict(slug='how-a-call-is-decided', eyebrow='API · 02 of 03 · Auth',
      title='How glidepath-api decides a call',
      desc='Five steps in order. Who are you: a TokenReview by the cluster, or a people-dex ID token glidepath-api verifies itself. Acting for whom: only a listed delegate such as Tower may name a person with On-Behalf-Of. May you: a SubjectAccessReview in the app\'s cicd namespace on the virtual group glidepath.hangar.io, the focal step. Do it: a read, a re-run or cancel, or a proposal. Answer: JSON with a stable rule id. Each of the first four can refuse with a stable rule: GP-AUTH-001 or 002, GP-AUTH-003 or 004, GP-AUTHZ-001 (an app answers 404 only to someone who could read it), and GP-API-422 when the cluster\'s shape lock or the release plan says no. Every call, allowed or refused, writes one audit line, one metric and one span with the operation, tier, app, caller, on-behalf-of, decision, status, time and trace id.',
      lede='Authentication is the cluster\'s TokenReview. Authorization is ordinary RBAC on a group nothing serves. Every refusal has a name an agent can branch on, and nothing goes unrecorded.',
      body=''.join(b), W=1000, H=580, y0=76,
      cards=[('Who', '', P('Anything the cluster trusts works: an in-cluster ServiceAccount, a federated identity from the other cluster, or since November 1 a person signed in with people-dex.')),
             ('What', 'accent', P('runs, runs/logs, releases, evidence, tests, environments, events and cicd: strings in a ClusterRole. Three roles, reader, operator and releaser, and all of them empty on a fresh install.')),
             ('For whom', 'link', P('Tower writes as tower-actor and names the person. The API authorizes Tower and records the person; Tower checks ownership before it calls.'))])


def s_one_call():
    b = []
    b += [zone(24, 100, 952, 120, 'one call, across two clusters'), zonex(24, 248, 952, 88, 'what the call leaves', 212),
          zone(24, 364, 952, 88, 'what people look at')]
    chain = [('Tower', 'span, on the prod cluster', 'input'), ('API server proxy', 'traceparent passes', 'external'),
             ('glidepath-api', 'span named for the op', 'focal'), ('Child spans', 'Results · broker · GitHub', 'backend')]
    for i in range(3):
        x = 48 + i * 240
        b.append(path([(x + 184, 164), (x + 240, 164)], 'link'))
    b.append(path([(620, 192), (620, 228)], marker=False))
    b.append(path([(188, 228), (812, 228)], marker=False))
    for cx in (188, 500, 812):
        b.append(path([(cx, 228), (cx, 272)]))
    b.append(path([(452, 320), (452, 348), (264, 348), (264, 388)]))
    b.append(path([(548, 320), (548, 348), (680, 348), (680, 388)], 'accent'))
    b.append(path([(812, 320), (812, 388)]))
    for i, (n, s, k) in enumerate(chain):
        b.append(node(48 + i * 240, 136, 184, 56, n, s, k))
    outs = [('Audit line', 'JSON on stdout, with traceId'), ('Metrics on :9090', 'requests · duration · streams'),
            ('Trace in Tempo', 'X-Glidepath-Trace-Id')]
    for i, (n, s) in enumerate(outs):
        b.append(node(48 + i * 312, 272, 280, 48, n, s, 'store'))
    b.append(node(48, 388, 432, 48, 'Sloth SLOs and alerts', '99.5% available · 95% within 2.5 s'))
    b.append(node(520, 388, 432, 48, 'Grafana: Glidepath API', "Tower's latency beside the API's own", 'focal'))
    b.append(callout(24, 496, 'The gap between Tower\'s number and the API\'s is the network between clusters.'))
    b.append(legend(528, [('input', 'The caller'), ('focal', 'The API, and its dashboard'), ('store', 'Signals'),
                          ('link', 'HTTP, traced')]))
    return dict(slug='one-call-three-signals', eyebrow='API · 03 of 03 · Observability',
      title='One call, seen three ways',
      desc='A call starts as a span in Tower on the prod cluster, passes the API server proxy with its traceparent unchanged, becomes a span in glidepath-api named for the operation, and has child spans for what the API reads: Tekton Results, the broker, GitHub. It leaves three signals: an audit line on stdout with the trace id, Prometheus metrics on port 9090 (requests, duration, streams), and a trace in Tempo whose id comes back in X-Glidepath-Trace-Id. Sloth turns the metrics into two SLOs, 99.5% availability and 95% of calls within 2.5 seconds, with burn-rate alerts. The Glidepath API dashboard in Grafana shows Tower\'s latency beside the API\'s own.',
      lede='The audit line, the metric and the trace carry the same operation name and the same trace id, so one slow click in Tower can be followed to the source that made it slow.',
      body=''.join(b), W=1000, H=568, y0=76,
      cards=[('Measured where it is felt', '', P('Tower\'s own span metrics, read from the prod cluster through Thanos, sit next to the API\'s numbers on one dashboard.')),
             ('An SLO that stays honest', 'accent', P('The latency SLO burned at about 1.8 on the dev cluster from day one, from slow TaskRun lists. The objective was left alone.')),
             ('Errors name their trace', 'link', P('Tower ends an error message with (trace <id>), so a screenshot is enough to find the call.'))])
