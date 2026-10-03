"""The Testing set: pictures for the essay "Why Hangar runs its tests in Testkube" (2026-10-03)."""
from libx import *


def t_how_it_works():
    b = []
    b += [zone(24, 100, 952, 120, 'what starts a run'), zone(24, 260, 952, 160, 'in your cluster · the agent'),
          zone(24, 460, 952, 120, 'where the results go')]
    starts = [('CI pipeline', 'Tekton · Actions · Jenkins'), ('CLI or API', 'testkube run testworkflow'),
              ('A schedule', 'cron, in the workflow'), ('Kubernetes event', 'a TestTrigger on a resource')]
    for i, (n, s) in enumerate(starts):
        x = 48 + i * 240
        cx = x + 92
        if i == 0:
            b.append(path([(cx, 192), (cx, 296)]))
        else:
            b.append(path([(cx, 192), (cx, 240), (232, 240), (232, 296)]))
        b.append(node(x, 136, 184, 56, n, s, 'input'))
    b += [path([(288, 328), (380, 328)], 'accent'), hlab(288, 380, 328, 'RUNS', ACC)]
    b += [node(48, 296, 240, 64, 'TestWorkflow', 'a Kubernetes resource, in git', 'focal'),
          node(380, 296, 240, 64, 'Testkube agent', 'open source · in your cluster')]
    for k, y in enumerate((276, 320, 364)):
        b.append(path([(620, 328), (666, 328), (666, y + 18), (712, y + 18)], marker=True))
        b.append(node(712, y, 240, 36, f'Worker {k + 1} · shard {k + 1} of 3'))
    b.append(lab(832, 266, 'PARALLEL · SHARDS · MATRIX', ACC))
    b += [path([(832, 400), (832, 440), (500, 440), (500, 496)]),
          path([(380, 524), (288, 524)], 'open'), path([(620, 524), (712, 524)], 'open')]
    b += [node(380, 496, 240, 56, 'Results and artifacts', 'logs · reports · step status', 'store'),
          node(48, 496, 240, 56, 'Control plane', 'dashboard · cloud or on-prem', 'optional'),
          node(712, 496, 240, 56, 'Notifications', 'webhooks · CDEvents')]
    b.append(callout(24, 620, 'Your tests, in any framework, declared once and run where your apps run.'))
    b.append(legend(652, [('input', 'Who starts it'), ('focal', 'The declared test'), ('store', 'What it produces'),
                          ('optional', 'Optional, commercial'), ('accent', 'Runs'), ('open', 'Reports')]))
    return dict(slug='how-testkube-works', eyebrow='Testing · 01 of 03 · The model',
      title='How Testkube runs a test',
      desc='Three rows. What starts a run: a CI pipeline (Tekton, GitHub Actions, Jenkins), the CLI or API (testkube run testworkflow), a schedule declared in the workflow, or a Kubernetes event through a TestTrigger. All four start a TestWorkflow, highlighted, which is a Kubernetes resource kept in git. The open source Testkube agent, running in your cluster, runs it, fanning out to three workers, each one shard of three, labelled parallel, shards and matrix. The workers produce results and artifacts: logs, reports and step status. Those go to an optional control plane, a dashboard in the cloud or on-premises, drawn dashed because it is the optional, commercial part, and out as notifications through webhooks and CDEvents.',
      lede='A test is a resource, like a Deployment. The open source agent runs it in your cluster, in whatever framework the test already uses, and the control plane is where you see every run in one place.',
      body=''.join(b), W=1000, H=680, y0=76,
      cards=[('Declared, not scripted', '', P('A TestWorkflow says which image, which steps, which services and which artifacts to keep. It lives in git and gets reviewed like anything else.')),
             ('Bring your framework', 'accent', P('k6, Playwright, Cypress, JMeter, Postman, pytest: if it runs in a container, Testkube can orchestrate it. Nobody rewrites a test suite to adopt it.')),
             ('Free agent, optional pane', 'link', P('The agent is open source and runs standalone. The dashboard that gathers every run lives in the commercial control plane, hosted or on-premises.'))])


def t_in_hangar():
    b = []
    b += [zone(24, 100, 280, 236, 'the app repo'), zone(328, 100, 320, 236, 'glidepath · run-testworkflow'),
          zone(672, 100, 304, 236, 'testkube namespace · shared'), zone(24, 372, 952, 116, 'where people see it')]
    b += [node(48, 144, 232, 56, 'cicd.yaml', 'test: enabled · name: integration', 'input'),
          node(48, 232, 232, 56, 'platform/integration.yaml', 'a TestWorkflow the team owns', 'input')]
    steps = ['1  Copy app secrets into testkube', '2  Rewrite the name, then apply',
             '3  Run with the testkube CLI, poll', '4  Blank the secret again']
    for i, s in enumerate(steps):
        y = 128 + i * 52
        b.append(node(344, y, 288, 36, s))
        if i < 3:
            b.append(path([(488, y + 36), (488, y + 52)]))
    b += [path([(280, 172), (320, 172), (320, 146), (344, 146)]),
          path([(280, 260), (328, 260), (328, 198), (344, 198)])]
    b += [path([(632, 198), (664, 198), (664, 152), (696, 152)], 'accent'),
          path([(824, 176), (824, 196)], 'accent'), path([(824, 244), (824, 264)]),
          path([(632, 250), (680, 250), (680, 288), (696, 288)], 'link')]
    b += [node(696, 128, 256, 48, 'Kyverno admission', 'your own secret, or denied', 'security'),
          node(696, 196, 256, 48, 'TestWorkflow', 'name: <app>-integration', 'focal'),
          node(696, 264, 256, 48, 'Agent runs the pods', 'Testkube CE · no control plane')]
    b += [path([(488, 320), (488, 360), (188, 360), (188, 408)]),
          path([(328, 436), (360, 436)], 'open'),
          path([(600, 320), (600, 380), (812, 380), (812, 408)])]
    b += [node(48, 408, 280, 56, 'Task results', 'outcome · one line per step', 'store'),
          node(360, 408, 280, 56, 'Release Record', 'in Tower, beside the build', 'focal'),
          node(672, 408, 280, 56, 'Stage span and notify', 'OTel trace · CDEvent · Slack')]
    b.append(callout(24, 528, 'The team owns the test. The platform owns the fence around it.'))
    b.append(legend(560, [('input', 'Written by the team'), ('backend', 'Platform step'), ('security', 'Policy'),
                          ('focal', 'What matters most'), ('accent', 'Apply'), ('link', 'Run'), ('open', 'Shown in')]))
    return dict(slug='a-test-run-in-hangar', eyebrow='Testing · 02 of 03 · In Hangar',
      title='One test run in Hangar',
      desc='Four zones. The app repo holds cicd.yaml, which turns the test stage on and names the test (integration), and platform/integration.yaml, a TestWorkflow the team owns. Glidepath\'s run-testworkflow Task takes four steps: copy the app\'s secrets into the shared testkube namespace, rewrite the workflow\'s name and apply it, run it with the testkube CLI and poll, and blank the secret again. In the shared testkube namespace, a Kyverno admission policy, drawn as a security boundary, only lets the workflow reference the app\'s own secret, or denies it. The admitted TestWorkflow is named after the app and the test, and Testkube CE, with no control plane, runs the pods. Below, where people see it: the Task\'s results (an outcome and one line per step) are shown in the Release Record in Tower, beside the build, and the stage emits an OpenTelemetry span, a CDEvent and a Slack notification.',
      lede='The app team writes one file. Glidepath does the rest: it moves the secrets in for the length of the run, applies the workflow through a policy gate, and puts the result where people already look.',
      body=''.join(b), W=1000, H=588, y0=76,
      cards=[('Self-service', '', P('A new test is a file in the app repo, next to cicd.yaml. No ticket, no operator, and the name can\'t collide with another app\'s.')),
             ('Fenced', 'accent', P('Kyverno checks every TestWorkflow at admission, while the caller\'s real identity is still visible. One app\'s tests can\'t mount another app\'s secrets.')),
             ('Not only tests', 'link', P('A TestWorkflow is anything that runs and reports pass or fail. Warming a cache before a release fits just as well as a Playwright suite.'))])


def t_free_tier():
    b = []
    b += [zone(24, 100, 300, 340, 'what I expected'), zone(340, 100, 300, 340, 'what the cluster said'),
          zone(656, 100, 320, 340, 'what shipped')]
    rows = [
        (('Tests in each app namespace', 'executionNamespaces, per the docs'),
         ('Pro only, in the source', 'api-server exits in standalone mode'),
         ('One shared namespace', 'ADR-0007 · secrets in, then blanked'), 'backend'),
        (('A secret per run', 'config sensitive: true'),
         ('Not in this CE build', 'execution aborted, no secret made'),
         ('A Kyverno admission policy', 'ADR-0008 · your own secret only'), 'focal'),
        (('A plain pass or fail', 'result.status'),
         ('Passing runs said aborted', 'a race with the Job controller'),
         ('Trust the steps', 'every step passed means passed'), 'backend'),
        (('The default MongoDB', "the chart's own backend"),
         ("Won't start on this kernel", 'an upstream MongoDB gate'),
         ('PostgreSQL instead', 'a first-class chart option'), 'backend'),
    ]
    for i, (a, c, d, k) in enumerate(rows):
        y = 136 + i * 76
        b += [path([(300, y + 28), (364, y + 28)], 'open'), path([(616, y + 28), (680, y + 28)])]
        b += [node(48, y, 252, 56, *a, kind='input'), node(364, y, 252, 56, *c, kind='store'),
              node(680, y, 272, 56, *d, kind=k)]
    b.append(callout(24, 480, 'Read the source when the docs disagree, and write down what you find.'))
    b.append(legend(512, [('input', 'The plan'), ('store', 'Found on a live cluster'), ('backend', 'Shipped'),
                          ('focal', 'The policy fix'), ('open', 'Tried'), ('muted', 'Led to')]))
    return dict(slug='what-the-free-tier-taught-me', eyebrow='Testing · 03 of 03 · Honest notes',
      title='What running the free tier taught me',
      desc='Three columns: what I expected, what the cluster said, and what shipped, over four rows, all from August 24, 2026 onward on the dev cluster. One: tests in each app\'s own namespace through executionNamespaces, as the docs described; the source gates it to the paid editions and the api-server exits in standalone mode; so one shared namespace shipped, ADR-0007, with secrets moved in and blanked after each run. Two, highlighted: a secret per run through config sensitive true; not delivered in this CE build, the execution aborted and no secret was made; so a Kyverno admission policy shipped, ADR-0008, allowing only the app\'s own secret. Three: a plain pass or fail from result.status; passing runs reported aborted, a race with the Kubernetes Job controller; so the platform trusts the steps, and every step passed means passed. Four: the chart\'s default MongoDB backend would not start on this kernel, an upstream MongoDB gate; PostgreSQL, a first-class chart option, is used instead.',
      lede='Hangar runs the open source agent with no control plane, on purpose. These are the four places where that floor was lower than the docs suggested, and what I built on top of it.',
      body=''.join(b), W=1000, H=540, y0=76,
      cards=[('Fair trade', '', P('Open core means the paid features are paid. I\'d rather know exactly where the line is than guess, so I read the source.')),
             ('Policy fills the gap', 'accent', P('RBAC decides who can edit a Secret, not which Secret a pod may mount. An admission policy closes that, at the one point where the caller is still known.')),
             ('Reversible', 'link', P('With a control plane connection, per-namespace runs come back and the shared namespace and its policy simply have nothing left to do.'))])
