"""The Crossplane set: pictures for the "Building Airframe" essay series (2026-09-30)."""
from libx import *


def x_secretstore():
    b = []
    b += [zone(24, 100, 432, 440, 'the poc i planned · never built'), zone(488, 100, 488, 440, 'what airframe built · live since 2026-08-17')]
    # Left: the proof of concept that never happened.
    b += [path([(240, 204), (240, 244)], dashed=True), vlab(240, 204, 244, 'COMPOSES'),
          path([(190, 308), (190, 328), (140, 328), (140, 348)], dashed=True),
          path([(290, 308), (290, 328), (340, 328), (340, 348)], dashed=True),
          path([(248, 380), (232, 380)], 'open', dashed=True),
          path([(340, 412), (340, 452)], dashed=True), vlab(340, 412, 452, 'SYNCS')]
    b += [node(140, 140, 200, 64, 'SecretStore XR', 'app · env', 'optional'),
          node(140, 244, 200, 64, 'Composition', 'one template, two outputs', 'optional'),
          node(48, 348, 184, 64, 'Azure Key Vault', 'one per app', 'optional'),
          node(248, 348, 184, 64, 'ESO SecretStore', 'points at the vault', 'optional'),
          node(248, 452, 184, 64, 'App Secrets', 'pulled by ESO', 'optional')]
    # Right: what exists today.
    b += [path([(732, 204), (732, 244)]), vlab(732, 204, 244, 'COMPOSES'),
          path([(682, 308), (682, 328), (612, 328), (612, 348)]),
          path([(782, 308), (782, 328), (856, 328), (856, 348)]),
          path([(612, 412), (612, 452)], 'accent'), vlab(612, 412, 452, 'PROJECT · IDENTITY', ACC, 'l'),
          path([(856, 412), (856, 452)]), vlab(856, 412, 452, 'STORE', side='l'),
          path([(760, 484), (712, 484)], 'open'), hlab(712, 760, 484, 'PULLS')]
    b += [node(632, 140, 200, 64, 'SecretStore XR', 'app · cluster · env', 'input'),
          node(632, 244, 200, 64, 'Composition', 'go-templating pipeline', 'focal'),
          node(512, 348, 200, 64, 'provider-infisical', 'my own Upjet provider'),
          node(760, 348, 192, 64, 'provider-kubernetes', 'Object wraps the store'),
          node(512, 452, 200, 64, 'Infisical', 'project never deleted', 'store'),
          node(760, 452, 192, 64, 'External Secrets', 'ClusterSecretStore', 'store')]
    b.append(callout(24, 584, 'The idea survived. The backend changed, and the first real API I shipped was the one I had wanted to prototype.'))
    b.append(legend(616, [('optional', 'Planned, never built'), ('input', 'The request'), ('focal', 'Composition'), ('store', 'State'), ('accent', 'Creates'), ('open', 'Reads')]))
    return dict(slug='secretstore-then-and-now', eyebrow='Crossplane · 01 of 04 · Where it started',
      title='The SecretStore I planned, and the one I built',
      desc='Two panels. Left, drawn dashed because it was never built: a proof of concept in which a SecretStore XR is composed into an Azure Key Vault and an External Secrets SecretStore pointing at it, which syncs app secrets. Right, what Airframe runs today: a SecretStore XR with app, cluster and environment, composed by a go-templating pipeline into provider-infisical resources (a project and an identity in Infisical, the project never deleted with the XR) and a provider-kubernetes Object that wraps a ClusterSecretStore for External Secrets, which pulls values from Infisical.',
      lede='In my previous role I wanted to try Crossplane on one small, well-understood resource: a secret store. That proof of concept never happened. In Hangar the same idea became Airframe\'s first real cross-cluster API.',
      body=''.join(b), W=1000, H=644, y0=76,
      cards=[('Planned, never built', '', P('One XR, two outputs: an Azure Key Vault and an External Secrets SecretStore pointing at it. Small enough to learn on, useful enough to matter.')),
             ('Built', 'accent', UL(['First live on 2026-08-17 behind a small operator of my own.', 'Since September, provider-infisical (my own Upjet provider) does the provisioning, and the operator is retired.', 'A per-environment store narrows a secret to exactly one namespace.'])),
             ('What it taught me', 'link', P('A namespaced XR can\'t compose a cluster-scoped resource in Crossplane v2, so the ClusterSecretStore rides inside a provider-kubernetes Object. And a secret store must never be deleted just because its request was.'))])


def x_readiness():
    b = []
    b += [zone(24, 100, 680, 160, 'composition pipeline · every reconcile'), zone(736, 100, 240, 160, 'what you see')]
    b += [zone(24, 300, 952, 160, 'composed resources · observed state')]
    b += [path([(232, 180), (264, 180)]), path([(464, 180), (496, 180)]),
          path([(680, 180), (756, 180)], 'accent'), hlab(680, 756, 180, 'READY', ACC),
          path([(152, 348), (152, 284), (340, 284), (340, 212)], 'open'),
          path([(384, 348), (384, 212)], 'open'), vlab(384, 250, 290, 'OBSERVED'),
          path([(616, 348), (616, 212)], 'open', dashed=True), stopx(616, 292),
          path([(848, 348), (848, 296), (660, 296), (660, 212)], 'open')]
    b += [node(48, 148, 184, 64, 'Render', 'function-go-templating'),
          node(264, 148, 200, 64, 'ComponentReady', 'closed reason codes', 'focal'),
          node(496, 148, 184, 64, 'Auto-ready', 'function-auto-ready'),
          node(756, 148, 196, 64, 'XR status', 'Ready · Synced · ComponentReady', 'store'),
          node(48, 348, 208, 64, 'CNPG Cluster', 'has a Ready condition'),
          node(280, 348, 208, 64, 'RabbitmqCluster', 'ClusterAvailable, no Ready'),
          node(512, 348, 208, 64, 'Service · PVC', 'no conditions at all', 'security'),
          node(744, 348, 208, 64, 'RepositoryFile', 'the provider decides Ready')]
    b.append(callout(24, 504, 'Ready should mean someone could use it now. Every layer underneath has its own idea of what that means.'))
    b.append(legend(536, [('focal', 'My condition'), ('store', 'Status'), ('security', 'Blind spot'), ('open', 'Observes'), ('accent', 'Rolls up')]))
    return dict(slug='readiness', eyebrow='Crossplane · 02 of 04 · Readiness',
      title='Three layers, three ideas of "ready"',
      desc='Top row: a composition pipeline runs every reconcile. A render step (function-go-templating) feeds a ComponentReady step with closed reason codes, which feeds function-auto-ready, which rolls Ready up to the XR status, showing Ready, Synced and ComponentReady. Bottom row: composed resources whose observed state is read. A CloudNativePG Cluster has a Ready condition; a RabbitmqCluster has ClusterAvailable but no Ready; a Service or PVC has no conditions at all, a blind spot for auto-ready; a RepositoryFile has a Ready decided by its provider.',
      lede='Crossplane owns Ready and Synced. Each composed resource reports health its own way, or not at all. Getting an honest answer to "is my database ready?" meant building a condition of my own on top.',
      body=''.join(b), W=1000, H=572, y0=76,
      cards=[('Don\'t call it Ready', '', P('function-go-templating reserves Ready, Healthy and Synced and errors if you set them. My own condition is ComponentReady, with a closed list of reasons such as PostgreSQLDegraded or RedisReleaseFailed, so it never races Crossplane\'s.')),
             ('Mark what can\'t report', 'accent', P('A Service, a PVC or a ConfigMap has no status conditions, so auto-ready waits for them forever. The Dex component sat at "Creating" with its pod running until the function marked those resources ready itself.')),
             ('Provider bugs look like readiness bugs', 'link', P('A RepositoryFile interrupted mid-create stayed Ready: False forever. The fix was in the provider, not the composition: a deterministic external name, patched in my fork.'))])


def x_budget():
    b = []
    zs = [(24, 'background polling · 09-07'), (348, 'annotation fight · 09-23'), (672, 'retry loop · 09-22')]
    for zx, t in zs:
        b.append(zone(zx, 100, 304, 280, t))
        b.append(path([(zx + 152, 196), (zx + 152, 220)]))
    rows = [
        (24, ('provider-github polls', 'default --poll=10m, every Repository'), ('Background drain', 'forever, changed or not'), ('Poll hourly, cap the rate', 'fix · 09-07'), 'r'),
        (348, ('Renders repo:file:', 'the name the template computes'), ('Provider writes repo:file:main', 'its own id, every ~2s'), ('Render the observed name', 'fix · 09-23'), 'r'),
        (672, ('Template default changes', 'Dockerfile to Containerfile'), ('Retries at 60s backoff', 'force-replace field; --poll ignored'), ('Pin file and name', 'fix · 09-23'), 'l'),
    ]
    for zx, a, bb, fx, side in rows:
        b.append(node(zx + 24, 140, 256, 56, *a))
        b.append(node(zx + 24, 220, 256, 56, *bb, kind='focal' if zx == 348 else 'backend'))
        fxx = zx + 72 if side == 'r' else zx + 24
        b.append(node(fxx, 308, 208, 48, fx[0], kind='backend', tag=fx[1]))
    # The fight is a loop: each rewrite triggers the next.
    b.append(path([(628, 248), (640, 248), (640, 168), (628, 168)], 'accent'))
    b += [path([(68, 276), (68, 464), (300, 464)], 'accent'), vlab(68, 392, 420, 'ALWAYS ON', ACC),
          path([(392, 276), (392, 432)], 'accent'), vlab(392, 392, 420, '~280 A MINUTE', ACC),
          path([(932, 276), (932, 464), (700, 464)], 'accent'), vlab(932, 392, 420, '~16,000 AN HOUR', ACC, 'l')]
    b.append(node(300, 432, 400, 64, 'GitHub API budget', '5,000 calls an hour per account, shared with Backstage', 'store'))
    b.append(callout(24, 544, 'None of these was a Crossplane bug. Each was me not yet knowing what a reconcile costs.'))
    b.append(legend(576, [('focal', 'The loop'), ('backend', 'Cause or fix'), ('store', 'Shared budget'), ('accent', 'Spends calls')]))
    return dict(slug='rate-limit-budget', eyebrow='Crossplane · 03 of 04 · Pollers and loops',
      title='Three ways to empty a 5,000-call bucket',
      desc='Three panels drain one shared GitHub API budget of 5,000 calls an hour per account, shared with Backstage. Background polling (2026-09-07): provider-github polls every Repository on a ten-minute default, forever; fixed by polling hourly and capping the reconcile rate. Annotation fight (2026-09-23): the composition renders the external name repo:file: while the provider rewrites it to repo:file:main every two seconds, a loop costing about 280 calls a minute; fixed by rendering the observed name. Retry loop (2026-09-22): a template default change from Dockerfile to Containerfile hits a force-replace field, and the provider retries at a sixty-second backoff that ignores the poll interval, about 16,000 calls an hour from seven objects; fixed by pinning the file and name to what the provider observed.',
      lede='Every reconcile spends someone\'s API budget. On GitHub mine was 5,000 calls an hour, shared with Backstage, and I emptied it three different ways before I learned to count.',
      body=''.join(b), W=1000, H=612, y0=76,
      cards=[('Polling is a cost', '', P('The provider\'s default poll is ten minutes, per managed resource, forever. Every new cluster from the Apron template now starts with --poll=1h and --max-reconcile-rate=50.')),
             ('Never fight the provider', 'accent', P('If the provider owns a field, like the external name it assigns, render back exactly what it wrote. Two writers with different spellings of one name is a loop, not a disagreement.')),
             ('The worst one', 'link', P('The provider release I ran read a rate-limit 403 as "this file was deleted" and re-created it, overwriting real values.yaml content. An upstream fix already existed but hadn\'t been released, so I built and published my fork\'s main.'))])


def x_timeline():
    b = []
    b.append(zone(24, 100, 952, 300, 'airframe · 2026-08-12 to 2026-09-29'))
    stations = [
        ('08-13', 'First XRDs', 'Ready is reserved; use your own', 'backend'),
        ('08-17', 'SecretStore goes live', 'cluster-scoped needs an Object', 'backend'),
        ('08-25', 'TektonCICD split out', 'an XR can compose another XR', 'backend'),
        ('09-07', 'The polling budget', 'poll hourly, cap reconcile rate', 'backend'),
        ('09-16', 'A file vanished', 'rendering nothing is a delete', 'focal'),
        ('09-17', 'Forking the provider', 'a 403 is not a 404', 'backend'),
        ('09-23', 'Two API storms', 'render what the provider observed', 'backend'),
        ('09-27', 'ComponentReady', 'reasons an agent can read', 'backend'),
    ]
    ax = 250
    b.append(f'<line x1="56" y1="{ax}" x2="944" y2="{ax}" stroke="{MUTED}" stroke-width="1.2"/>')
    for i, (d, name, sub, kind) in enumerate(stations):
        x = 140 + i * 103
        above = i % 2 == 0
        by = 140 if above else 300
        b.append(f'<line x1="{x}" y1="{by + 56 if above else ax}" x2="{x}" y2="{ax if above else by}" stroke="{RULE}" stroke-width="1"/>')
        b.append(node(x - 96, by, 192, 56, name, sub, kind))
        col = ACC if kind == 'focal' else INK
        b.append(f'<circle cx="{x}" cy="{ax}" r="{6 if kind == "focal" else 4}" fill="{col}"/>')
        b.append(text(x, ax + 22 if above else ax - 14, d, 9, 500, MUTED, 'middle', mono=True, ls='0.08em'))
    b.append(callout(24, 444, 'Almost every lesson here was found on a running cluster, not in a render.'))
    b.append(legend(476, [('backend', 'A lesson'), ('focal', 'The one that cost data'), ('dot', 'When it landed')]))
    return dict(slug='six-weeks-of-lessons', eyebrow='Crossplane · 04 of 04 · The journey so far',
      title='Six weeks building Airframe, one lesson at a time',
      desc='A timeline from August 12 to September 29, 2026 with eight lessons. August 13, first XRDs: Ready is reserved, use your own condition. August 17, SecretStore goes live: composing a cluster-scoped resource needs an Object wrapper. August 25, TektonCICD split out: an XR can compose another XR. September 7, the polling budget: poll hourly and cap the reconcile rate. September 16, highlighted, a file vanished: rendering nothing is a delete. September 17, forking the provider: a 403 is not a 404. September 23, two API storms: render what the provider observed. September 27, ComponentReady: reasons an agent can read.',
      lede='Not to scale. Each stop is a real commit in Airframe, Apron or my fork of the GitHub provider, and each left a rule behind.',
      body=''.join(b), W=1000, H=508, y0=76,
      cards=[('Built', '', P('Fifteen APIs, from app stacks and environments to PostgreSQL, Redis, RabbitMQ, MongoDB and Dex, plus three Composition Functions.')),
             ('The one that hurt', 'accent', P('A transient false in a template gate rendered a file away. Crossplane deleted it, ArgoCD pruned the SecretStore it described, and two apps lost their Infisical projects and secrets.')),
             ('Next in the series', 'link', P('Moving every API to the catalog.hangar.io group, scaffolding repos as a one-time action instead of a reconciled resource, and the rest of the A+ scorecard.'))])
