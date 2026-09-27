"""The Glidepath set: CI/CD, redrawn in the Hangar grammar from glidepath/docs (2026-09-27)."""
from libx import *


def g_overview():
    b = []
    b += [zone(24, 100, 200, 440, 'github'), zone(256, 100, 448, 440, 'dev cluster · glidepath'), zone(736, 100, 240, 440, 'observe')]
    b += [path([(200, 172), (280, 172)]), hlab(200, 280, 172, 'WEBHOOK'),
          path([(376, 204), (376, 244)]), vlab(376, 204, 244, 'STARTS'),
          path([(584, 204), (584, 244)], 'open'), vlab(584, 204, 244, 'RESOLVES'),
          path([(336, 308), (336, 348)], 'link'), vlab(336, 308, 348, 'CDEVENT', LINK, 'l'),
          path([(424, 348), (424, 308)], 'link'), vlab(424, 308, 348, 'NEXT STAGE', LINK),
          path([(472, 380), (488, 380)], 'link'),
          path([(680, 276), (760, 276)], 'link'), hlab(680, 760, 276, 'SPANS', LINK),
          path([(856, 244), (856, 204)], 'open'), vlab(856, 204, 244, 'QUERIES'),
          path([(680, 292), (712, 292), (712, 380), (760, 380)]),
          path([(280, 292), (240, 292), (240, 468), (200, 468)], 'accent'), hlab(200, 240, 468, 'PR', ACC),
          path([(200, 496), (488, 496)]), hlab(200, 488, 496, 'ARGOCD PULLS')]
    b += [node(48, 140, 152, 64, 'App repo', 'cicd.yaml · source', 'input'),
          node(48, 452, 152, 64, 'gitops-<app>', 'release PRs land here', 'store'),
          node(280, 140, 192, 64, 'Pipelines-as-Code', 'GitHub App · checks'),
          node(488, 140, 192, 64, 'Shared catalog', 'Helm · pinned by git tag'),
          node(280, 244, 400, 64, 'Stage PipelineRuns', 'validate · build · test · deploy · release', 'focal'),
          node(280, 348, 192, 64, 'CDEvents broker', 'TokenReview · no minted creds'),
          node(488, 348, 192, 64, 'DORA exporter', 'a consumer of the events'),
          node(488, 452, 192, 64, 'ArgoCD', 'the only writer to a cluster'),
          node(760, 140, 192, 64, 'Grafana', 'pipelines · stages · DORA'),
          node(760, 244, 192, 64, 'Tempo', 'one trace per flow'),
          node(760, 348, 192, 64, 'Tekton Results', 'every run, archived', 'store')]
    b.append(callout(24, 584, 'Two triggers, two trust models: git events belong to Pipelines-as-Code, stage-to-stage chaining to the broker.'))
    b.append(legend(616, [('focal', 'Pipeline runs'), ('input', 'Your repo'), ('store', 'State'), ('link', 'Event or telemetry'), ('accent', 'Release path'), ('open', 'Reads')]))
    return dict(slug='architecture-overview', eyebrow='Architecture · 01 of 07 · System overview',
      title='Glidepath end to end: from a push to a verified release',
      desc='Architecture of Glidepath. An app repo with cicd.yaml sends webhooks to Pipelines-as-Code on the dev cluster, which starts stage PipelineRuns resolved from a shared, git-tag-pinned catalog. Each stage emits a CDEvent to a broker that authenticates callers with TokenReview and starts the next stage; a DORA exporter consumes the same events. Spans go to Tempo, Grafana queries them, and Tekton Results archives every run. The release stage opens a pull request against the gitops repo, and ArgoCD, the only writer to a cluster, pulls from it.',
      lede='Developers write one file and push. Pipelines-as-Code owns everything git-triggered, a broker chains the stages by event, every step is a span in one trace, and nothing reaches a cluster except through a reviewed commit that ArgoCD pulls.',
      body=''.join(b), W=1000, H=664, y0=76,
      cards=[('Built', '', UL(['Tekton plus Pipelines-as-Code on plain Kubernetes (ADR-0001).', 'CDEvents broker with a TokenReview interceptor (ADR-0002).', 'GitOps-only release (ADR-0004); Tekton Results archival (ADR-0016).'])),
             ('Why two triggers', 'accent', P('Git events arrive with a webhook signature that the Pipelines-as-Code GitHub App already validates. A stage finishing is not a git event, so it needs its own path, and that path authenticates the pod itself rather than a credential the platform would have to mint and rotate.')),
             ('Known gaps', 'link', P('Glidepath keeps a public known-gaps list of problems found building real apps, each with evidence: for example, config-only pushes are not validated yet, and required checks assume every PR is a release PR.'))])


def g_pipeline():
    b = []
    b += [zone(24, 100, 176, 300, 'you'), zone(224, 100, 752, 300, 'glidepath · the platform owns all of this')]
    xs = [248, 364, 480, 596, 712, 828]
    names = [('PaC', 'reads .tekton/'), ('validate', 'fails fast'), ('build', 'kaniko · signed'), ('test', 'Testkube'), ('deploy', 'lower envs'), ('release', 'gitops PR')]
    for i in range(len(xs) - 1):
        b.append(path([(xs[i] + 96, 168), (xs[i + 1], 168)]))
    b += [path([(176, 168), (248, 168)]), hlab(176, 248, 168, 'WEBHOOK'),
          path([(176, 264), (412, 264), (412, 196)], 'accent'), hlab(176, 412, 264, 'READ FRESH, EVERY RUN', ACC),
          path([(528, 196), (528, 316)], 'link', dashed=True), vlab(528, 196, 316, 'SPANS', LINK),
          path([(760, 196), (760, 316)], 'link'), vlab(760, 196, 316, 'CDEVENTS', LINK)]
    b += [node(48, 140, 128, 56, 'git push', 'any branch rule', 'input'),
          node(48, 236, 128, 56, 'cicd.yaml', 'the one file', 'focal')]
    for (x, (n, s)) in zip(xs, names):
        b.append(node(x, 140, 96, 56, n, s))
    b += [node(248, 316, 332, 56, 'One trace per flow', 'otel-cli span per step · Tempo', 'store'),
          node(596, 316, 328, 56, 'Stage events', 'broker chains stages · DORA', 'store')]
    b.append(callout(24, 444, 'A fixed superset of stages, switched on by config. Not an arbitrary graph compiled per app.'))
    b.append(legend(476, [('focal', 'What you edit'), ('input', 'Your action'), ('backend', 'Platform stage'), ('store', 'Record'), ('accent', 'Config read'), ('link', 'Telemetry')]))
    return dict(slug='pipeline-flow', eyebrow='Flowchart · 02 of 07 · What you change',
      title='What you change, and what the platform owns',
      desc='Flowchart. On the left, the developer does two things: pushes to git and edits cicd.yaml. On the right, the platform owns the rest: Pipelines-as-Code reads platform-generated .tekton files and runs validate, build, test, deploy and release in order. Validate reads cicd.yaml fresh from the triggering commit. Every step emits a span into one trace per flow, and every stage emits a CDEvent that the broker uses to chain the next stage and that DORA metrics consume.',
      lede='The developer\'s surface is a push and one file. Everything in the larger box is the platform\'s: generated boilerplate, a shared catalog, the stage order, the telemetry and the events.',
      body=''.join(b), W=1000, H=524, y0=76,
      cards=C3(P('Platform as a product: a small, stable contract for developers, and the engineering on the platform side.'),
               UL(['.tekton/ files are generated at onboarding and never hand-edited.', 'cicd.yaml has no sync step and no second copy: it is read from the commit.', 'An undeclared stage never runs.']),
               P('A bad cicd.yaml fails in validate, with a readable schema error, before any build starts.'), 'Fails fast'))


def g_mapping():
    b = []
    b += [zone(24, 100, 360, 420, 'cicd.yaml · the one file you edit'), zone(440, 100, 536, 420, 'what the platform runs')]
    rows = [
        (140, ['build:', '  agent: nodejs-22', '  script: ./build.sh'], 'build', 'validate · unit test · kaniko image · Chains signature'),
        (220, ['test:', '  name: integration'], 'test', 'Testkube TestWorkflow in the shared namespace'),
        (300, ['deploy:', '  lowerEnvironments: [dev]', '  upperEnvironments: [prod]'], 'deploy + release', 'commit the dev env file · open a PR per upper env'),
        (380, ['governance:', '  sast: true', '  imageScan: true'], 'governance gates', 'Semgrep · Trivy · SBOM · provenance'),
        (460, ['pipelines:', '  ci: { event: push, branch: main }'], 'triggers and order', 'Pipelines-as-Code · a fixed stage DAG'),
    ]
    for (y, lines, name, sub) in rows:
        for i, ln in enumerate(lines):
            indent = (len(ln) - len(ln.lstrip(' '))) // 2
            b.append(text(48 + indent * 16, y + 4 + i * 16, ln.strip(), 11, 500 if i == 0 else 400, INK if i == 0 else MUTED, mono=True))
        b.append(path([(360, y + 12), (464, y + 12)]))
        b.append(node(464, y - 16, 488, 56, name, sub, 'focal' if name == 'build' else 'backend'))
    b.append(callout(24, 564, 'A block you leave out is a stage that never runs. Everything on the right is the platform\'s job.'))
    b.append(legend(596, [('focal', 'The one required block'), ('backend', 'Platform stage')]))
    return dict(slug='cicd-yaml-mapping', eyebrow='Mapping · 03 of 07 · The contract',
      title='cicd.yaml, and what actually runs',
      desc='Mapping from cicd.yaml blocks to what the platform runs. The build block (agent and optional script) drives validate, unit tests, a kaniko image build and a Chains signature. The test block names a Testkube TestWorkflow. The deploy block lists lower environments, which get a committed env file, and upper environments, which get a release pull request. The governance block switches on Semgrep, Trivy, SBOM and provenance gates. The pipelines block sets triggers and order through Pipelines-as-Code over a fixed stage DAG.',
      lede='Five blocks, each driving one part of the pipeline. Only build is required, and only its agent field inside it. The file is validated against a JSON Schema on every run.',
      body=''.join(b), W=1000, H=644, y0=76,
      cards=[('Scaffolded, not hand-written', '', P('Airframe commits a minimal, build-only cicd.yaml when an app is onboarded, so the first push already runs a pipeline (ADR-0017).')),
             ('What it cannot say', 'accent', P('Identity (app name, gitops repo, owner) lives in an operator-reviewed identity file, never in cicd.yaml. The schema rejects it, so a developer\'s commit can never change where a release goes.')),
             ('Honest toggles', 'link', P('governance.sast runs a real Semgrep scan; each gate says whether it is real or a stub, and a stub never reports as a pass.'))])


def g_onboarding():
    b = []
    b += [zone(24, 104, 952, 116, 'tower and airframe · self-service'), zone(24, 256, 952, 116, 'argocd and glidepath · automatic')]
    top = [(48, '1 · you', 'Pick a stack in Tower', 'Node · Go · Java · Python'),
           (360, '2 · airframe', 'Repos scaffolded', 'src · Dockerfile · cicd.yaml'),
           (672, '3 · airframe', 'Identity committed', 'tenants/<app>/identity.yaml')]
    bot = [(48, '4 · argocd', 'Tenant rendered', 'namespaces · RBAC · PaC · Triggers'),
           (360, '5 · glidepath', '.tekton delivered', 'boilerplate, never hand-edited'),
           (672, '6 · you', 'First push runs', 'build · test · deploy to dev')]
    for (x, tag, n, s) in top:
        b.append(node(x, 128, 280, 72, n, s, 'focal' if x == 48 else 'backend', tag=tag))
    for (x, tag, n, s) in bot:
        b.append(node(x, 280, 280, 72, n, s, 'focal' if x == 672 else 'backend', tag=tag))
    b += [path([(328, 164), (360, 164)]), path([(640, 164), (672, 164)]),
          path([(812, 200), (812, 236), (188, 236), (188, 280)]), hlab(188, 812, 236, 'APPLICATIONSET READS IT'),
          path([(328, 316), (360, 316)]), path([(640, 316), (672, 316)]),
          path([(500, 428), (500, 352)], dashed=True), vlab(500, 352, 428, 'NEEDED FOR 5')]
    b.append(node(380, 428, 240, 56, 'Install the GitHub App', 'the one manual step', 'optional'))
    b.append(callout(24, 528, 'No command to run and no pipeline YAML to write. Every step is a commit someone can review.'))
    b.append(legend(560, [('focal', 'You'), ('backend', 'Automatic'), ('optional', 'Manual, one time')]))
    return dict(slug='onboarding-sequence', eyebrow='Process · 04 of 07 · Onboarding',
      title='Getting a new app onto the platform',
      desc='Six-step process. The developer picks an app stack in Tower. Airframe scaffolds the source repo, Dockerfile and a starter cicd.yaml, then commits the app\'s identity file. ArgoCD\'s tenant-onboarding ApplicationSet reads it and renders the tenant: namespaces, RBAC, the Pipelines-as-Code Repository and the chaining Triggers. Glidepath delivers the generated .tekton boilerplate, and the developer\'s first push runs build, test and deploy to dev. Installing the platform GitHub App on the repo is the one manual, one-time step.',
      lede='Onboarding is where a platform shows whether it is a product. Here, the developer makes one choice, and each following step is a reviewed commit the platform makes on their behalf.',
      body=''.join(b), W=1000, H=604, y0=80,
      cards=C3(P('Backstage holds no Kubernetes credentials. Even creating a new app is a git commit, not an API call.'),
               UL(['The identity file is written by the platform, never by the app repo, so a developer\'s commit cannot redirect a release.', 'The execution namespace is computed as <type>-<app>-cicd, so it cannot drift.']),
               P('A private gitops repo needs the GitHub App installed on it too, or delivery to it fails: found live, and now in the docs.'), 'Found in use'))


def g_chaining():
    b = []
    lanes = [(92, 'build PipelineRun', 'finally: emit'), (254, 'CDEvents broker', 'shared · stateless'),
             (416, 'Interceptor', 'ClusterInterceptor'), (578, 'Kubernetes API', 'TokenReview'),
             (740, 'Tenant Trigger', 'tenant SA · namespaced'), (902, 'test PipelineRun', 'runs as tenant SA')]
    for (cx, n, s) in lanes:
        b.append(f'<line x1="{cx}" y1="156" x2="{cx}" y2="512" stroke="{RULE}" stroke-width="1" stroke-dasharray="3,4"/>')
    for (cx, n, s) in lanes:
        kind = 'focal' if n == 'CDEvents broker' else ('input' if 'PipelineRun' in n else 'backend')
        b.append(node(cx - 68, 100, 136, 56, n, s, kind))
    steps = [(92, 254, 196, '1 · CDEVENT + OWN SA TOKEN', 'link', False),
             (254, 416, 244, '2 · INTERCEPT', 'muted', False),
             (416, 578, 292, '3 · TOKENREVIEW', 'muted', False),
             (578, 416, 340, '4 · VALID · WHICH SA', 'muted', True),
             (254, 740, 400, '5 · ROUTE TO THIS TENANT', 'link', False),
             (740, 902, 460, '6 · CREATES', 'accent', False)]
    for (x1, x2, y, label, col, dash) in steps:
        b.append(path([(x1, y), (x2, y)], col, dashed=dash))
        b.append(hlab(x1, x2, y, label, {'link': LINK, 'accent': ACC}.get(col, SOFT)))
    b.append(callout(24, 556, 'No key material anywhere: the broker never mints or stores a credential, it only asks Kubernetes who is calling.'))
    b.append(legend(588, [('focal', 'Shared broker'), ('input', 'Pipeline run'), ('link', 'Event'), ('muted-dash', 'Response'), ('accent', 'Runs as tenant')]))
    return dict(slug='chaining-sequence', eyebrow='Sequence · 05 of 07 · Chaining',
      title='How test gets started when build finishes',
      desc='Sequence across six participants. The build PipelineRun\'s finally block posts a CDEvent with its own projected service-account token to the shared CDEvents broker. The broker\'s ClusterInterceptor calls the Kubernetes TokenReview API, which confirms the token and says which service account it belongs to. The broker routes the event to that tenant\'s own Trigger, which creates the test PipelineRun under the tenant\'s least-privilege service account.',
      lede='Stages are separate PipelineRuns chained by events. The interesting part is identity: each hop is authenticated by Kubernetes itself, and the next stage runs as the tenant, never as the broker.',
      body=''.join(b), W=1000, H=632, y0=76,
      cards=C3(P('Workload identity over minted secrets: the pod\'s own audience-bound token is the credential, verified by the API server.'),
               UL(['One shared EventListener with 2 to 3 replicas, not a listener per tenant.', 'Each tenant has its own Trigger object, scoped to its own service account.', 'The same events feed DORA metrics.']),
               P('A tenant cannot trigger another tenant\'s pipeline: routing follows the identity TokenReview returns, not anything in the payload.'), 'Why it holds'))


def g_deploy_release():
    b = []
    b += [zone(24, 100, 952, 124, 'deploy · fast inner loop'), zone(24, 256, 952, 236, 'release · governed promotion')]
    b += [node(48, 132, 200, 64, 'deploy stage', 'lower environments only', 'input'),
          node(288, 132, 200, 64, 'Commit env file', 'platform/envs/dev.yaml'),
          node(528, 132, 200, 64, 'ArgoCD · dev', 'syncs on commit'),
          node(768, 132, 184, 64, 'Running in dev', 'Argo Rollout · canary'),
          path([(248, 164), (288, 164)]), path([(488, 164), (528, 164)]), path([(728, 164), (768, 164)])]
    b += [node(48, 300, 200, 64, 'release stage', 'one PR per upper env', 'input'),
          node(288, 300, 200, 64, 'PR to gitops-<app>', 'same digest · not rebuilt', 'focal'),
          node(528, 304, 200, 56, 'Real gates', 'sast · scan · provenance · sbom'),
          node(528, 376, 200, 56, 'Stub gates', 'itsm · qa · policy · promote', 'optional'),
          node(768, 300, 184, 64, 'Human review', 'branch protection'),
          node(768, 412, 184, 56, 'ArgoCD · upper', 'the only writer', 'focal'),
          path([(248, 332), (288, 332)]),
          path([(488, 332), (528, 332)], 'accent'),
          path([(508, 332), (508, 404), (528, 404)], 'accent', dashed=True),
          path([(728, 332), (768, 332)]),
          path([(728, 404), (748, 404), (748, 340), (768, 340)], dashed=True, marker=False),
          path([(860, 364), (860, 412)]), vlab(860, 364, 412, 'MERGE')]
    b.append(callout(24, 536, 'Deploy asks whether a change works at all. Release asks whether it should run in front of customers.'))
    b.append(legend(568, [('input', 'Pipeline stage'), ('focal', 'The change'), ('backend', 'Check or system'), ('optional', 'Stub, says so'), ('accent', 'Required checks')]))
    return dict(slug='deploy-vs-release', eyebrow='Swimlane · 06 of 07 · Deploy and release',
      title='Deploy and release: different questions, different rigor',
      desc='Two swimlanes. Deploy, the fast inner loop: the deploy stage commits the lower environment file, ArgoCD on the dev cluster syncs it, and the app runs in dev as an Argo Rollout. Release, governed promotion: the release stage opens a pull request against the app\'s gitops repo carrying the digest that already passed, never rebuilt; real gates (SAST, image scan, provenance, SBOM, values) and clearly marked stub gates run as required checks; a human reviews under branch protection; after merge, the upper cluster\'s own ArgoCD is the only thing that changes it.',
      lede='Deploy is optimised for speed and has no reviewers. Release is optimised for trust: the same artifact, independent required checks, a human, and a cluster that only ever changes by pulling a merged commit.',
      body=''.join(b), W=1000, H=612, y0=76,
      cards=[('The same bytes', '', P('A release carries the exact image digest that passed test and deploy. Nothing is rebuilt for production, so what was tested is what ships.')),
             ('Gates that say what they are', 'accent', P('Five gates are real today (sast, image-scan, provenance, sbom, values). Four are stubs, and they are labelled as stubs everywhere they appear, because a gate that silently passes is worse than none.')),
             ('Built', 'link', UL(['GitOps-only release (ADR-0004).', 'Provenance validates the attestation, plus the commit signature (ADR-0015).', 'Gates enforced as required checks by a GitHub ruleset.']))])


def g_multicluster():
    b = []
    b += [zone(24, 100, 420, 380, 'dev cluster · one'), zone(476, 100, 168, 380, 'git'), zone(676, 100, 300, 380, 'upper cluster · one of n')]
    b += [node(48, 140, 176, 64, 'release stage', 'opens the PR', 'input'),
          node(48, 252, 176, 64, 'CDEvents broker', 'TokenReview'),
          node(48, 364, 176, 64, 'DORA exporter', 'cluster-mapped'),
          node(248, 252, 176, 64, 'Outcome relay', 'checks cluster id', 'focal'),
          node(248, 364, 176, 64, 'ArgoCD · dev', 'dev manifests only'),
          node(492, 140, 136, 64, 'gitops-<app>', 'PR · review · merge', 'store'),
          node(700, 140, 252, 64, 'ArgoCD · this cluster', 'watches the same repo'),
          node(700, 252, 252, 64, 'App namespaces', '<type>-<app>-<env>'),
          node(700, 364, 252, 64, 'Sync hooks', 'PostSync · SyncFail Jobs', 'focal')]
    b += [path([(224, 172), (492, 172)], 'accent'), hlab(224, 492, 172, 'RELEASE PR', ACC),
          path([(628, 172), (700, 172)]), hlab(628, 700, 172, 'PULL'),
          path([(826, 204), (826, 252)]), vlab(826, 204, 252, 'SYNC'),
          path([(826, 316), (826, 364)]), vlab(826, 316, 364, 'ON CONVERGE'),
          path([(700, 396), (460, 396), (460, 284), (424, 284)], 'link'), hlab(460, 700, 396, 'CDEVENT · PER-CLUSTER SECRET', LINK),
          path([(248, 284), (224, 284)], 'link'),
          path([(136, 316), (136, 364)], 'link'), vlab(136, 316, 364, 'CONSUMES', LINK),
          path([(336, 428), (336, 456), (826, 456), (826, 428)], 'accent', dashed=True, marker=False),
          stopx(580, 456), hlab(460, 700, 456, 'NO REMOTE-CLUSTER CREDENTIAL', ACC)]
    b.append(callout(24, 524, 'Every cluster runs its own ArgoCD. Outcomes come back as events, and only when a release really converges.'))
    b.append(legend(556, [('focal', 'Outcome path'), ('store', 'Git'), ('accent', 'Release'), ('link', 'Event back'), ('accent-dash', 'Denied')]))
    return dict(slug='multi-cluster-topology', eyebrow='Deployment · 07 of 07 · Multi-cluster',
      title='One dev control plane, and an ArgoCD in every cluster',
      desc='Deployment topology. The dev cluster runs the release stage, the CDEvents broker, the DORA exporter, an outcome relay and its own ArgoCD, which syncs dev manifests only. The release stage opens a pull request against the gitops repo. Each upper cluster, one of many, runs its own ArgoCD that pulls the same repo and syncs the app namespaces. When a sync converges, PostSync or SyncFail hook Jobs post a CDEvent with a per-cluster secret to the outcome relay, which checks the claimed cluster and forwards it to the broker; DORA consumes it. No cluster holds a credential for another cluster.',
      lede='A single ArgoCD holding credentials for every cluster is a path from dev into prod. So each cluster pulls for itself, and results travel back the other way as events.',
      body=''.join(b), W=1000, H=600, y0=76,
      cards=C3(P('The only thing that crosses a cluster boundary is a reviewed, merged commit. Outcomes flow back as events, not API calls.'),
               UL(['The relay rejects an event whose claimed cluster does not match the secret it authenticated with.', 'PostSync fires only once health converges, not just when manifests apply.']),
               P('ArgoCD Notifications was tried first and dropped: live testing showed it fired on drift correction too, reporting releases that never happened.'), 'Found in use'))
