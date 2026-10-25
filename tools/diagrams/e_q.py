"""The Paving set: pictures for the essay "Paving the cloud" (2026-10-25)."""
from libx import *


def q_two_roads():
    b = []
    b += [zone(24, 100, 952, 96, 'who asks'), zone(24, 228, 952, 184, 'airframe · one contract · catalog.hangar.io'),
          zone(24, 440, 952, 80, 'reconciled by crossplane'), zone(24, 548, 952, 104, 'where it lands')]
    askers = [('Backstage form', 'a scaffolder template'), ('Tower', 'the developer view'),
              ('An agent', 'the same API, typed'), ('A pull request', 'an XR file in git')]
    for i, (n, s) in enumerate(askers):
        x = 48 + i * 232
        b.append(path([(x + 104, 172), (x + 104, 212)], marker=False))
        b.append(node(x, 124, 208, 48, n, s, 'input'))
    b.append(path([(152, 212), (848, 212)], marker=False))
    b.append(path([(500, 212), (500, 252)]))
    b.append(node(48, 252, 904, 56, 'The same contract for every kind',
                  'a schema · a closed set of status reasons · an entry in the catalog · the policy, as code', 'focal'))
    b += [path([(268, 308), (268, 340)]), path([(732, 308), (732, 340)])]
    b += [node(48, 340, 440, 48, 'Kubernetes resources', 'PythonApplication · PostgreSQL · Redis · RabbitMQ'),
          node(512, 340, 440, 48, 'Cloud resources', 'LambdaFunction · AwsEcsTarget · MessageQueue · ObjectStorage', 'focal')]
    b += [path([(268, 388), (268, 460)]), path([(732, 388), (732, 460)])]
    b.append(node(48, 460, 904, 40, 'Crossplane', 'compositions · providers · drift is put back'))
    b += [path([(268, 500), (268, 536)], marker=False), path([(732, 500), (732, 536)], marker=False)]
    b += [path([(152, 536), (384, 536)], marker=False), path([(616, 536), (848, 536)], marker=False)]
    b += [path([(152, 536), (152, 572)]), path([(384, 536), (384, 572)]), path([(616, 536), (616, 572)]),
          path([(848, 536), (848, 572)])]
    lands = [('App clusters', 'Argo CD · Rollouts', 'backend'), ('In-cluster data', 'CNPG · Redis · RabbitMQ', 'backend'),
             ('AWS', 'Lambda · ECS · SQS · S3 · RDS', 'external'), ('Azure', 'Functions · Container Apps', 'external')]
    for i, (n, s, k) in enumerate(lands):
        x = 48 + i * 232
        b.append(node(x, 572, 208, 56, n, s, k))
    b.append(callout(24, 692, 'Kubernetes is where the contract is kept, not where every road has to end.'))
    b.append(legend(724, [('input', 'Who asks'), ('focal', 'The contract, and its cloud kinds'), ('backend', 'Kubernetes'),
                          ('external', 'A cloud')]))
    return dict(slug='two-roads-one-contract', eyebrow='Paving · 01 of 03 · The shape',
      title='Two kinds of road, one contract',
      desc='Four rows. Who asks: a Backstage form, Tower, an agent using the same typed API, or a pull request with an XR file in git. All of them reach one contract in Airframe\'s catalog.hangar.io group, the same for every kind: a schema, a closed set of status reasons, an entry in the catalog and the policy as code. Under it sit two columns: Kubernetes resources such as PythonApplication, PostgreSQL, Redis and RabbitMQ, and, highlighted, cloud resources such as LambdaFunction, AwsEcsTarget, MessageQueue and ObjectStorage. Crossplane reconciles both, with compositions and providers, and puts drift back. They land in four places: app clusters with Argo CD and Rollouts, in-cluster data with CloudNativePG, Redis and RabbitMQ, AWS (Lambda, ECS, SQS, S3 and RDS) and Azure (Functions and Container Apps).',
      lede='A developer asks for a noun. Whether that noun becomes a pod on a cluster or a managed service in a cloud is the platform\'s business, and the request, the status and the rules look the same either way.',
      body=''.join(b), W=1000, H=764, y0=76,
      cards=[('One front door', '', P('A form, Tower, an agent and a pull request all create the same kind of resource. A new cloud kind changed none of them.')),
             ('One shape', 'accent', P('A queue on RabbitMQ and a queue on SQS answer the same questions: what can I ask for, what do I always get, and how do I know it worked.')),
             ('More than a front end', 'link', P('Kubernetes holds the contract and runs the reconcilers. The resources it describes can live anywhere the providers reach.'))])


def q_road_parts():
    b = []
    b += [zone(24, 100, 304, 384, 'the request'), zone(352, 100, 624, 384, 'what the platform adds'),
          zone(24, 512, 952, 96, 'what the app gets')]
    b.append('<rect x="48" y="132" width="256" height="148" rx="6" fill="#ffffff" stroke="' + ACC + '" stroke-width="1"/>')
    lines = ['kind: ManagedPostgreSQL', 'name: baggage-db', 'size: small', 'version: "17"',
             'allowedCidrs: [203.0.113.0/24]', 'protect: true']
    for i, s in enumerate(lines):
        b.append(text(64, 160 + i * 20, s, 11, 400, INK if i else ACC, mono=True))
    b.append(text(48, 312, 'Six lines in the app\'s xr-requests/.', 11, 400, MUTED))
    b.append(text(48, 332, 'No VPC, no subnet, no security group,', 11, 400, MUTED))
    b.append(text(48, 352, 'no parameter group, no IAM.', 11, 400, MUTED))
    parts = [('The contract', 'what you can ask for: a size, a version, storage, networks', 'focal'),
             ('Defaults with no field', 'encrypted · TLS only · no network until you list one', 'backend'),
             ('Identity', 'a password the provider generates, in a Secret · never in git', 'backend'),
             ('An answer', 'DependencyReady: Ready, Provisioning or Failing, and why', 'backend'),
             ('A way out', 'delete the file and every piece goes · protect keeps a snapshot', 'backend')]
    b.append(path([(304, 206), (336, 206), (336, 144 + 4 * 68), (368, 144 + 4 * 68)], 'accent', marker=False))
    for i, (n, s, k) in enumerate(parts):
        y = 124 + i * 68
        b.append(path([(336, y + 20), (376, y + 20)], 'accent'))
        b.append(node(376, y, 576, 48, n, s, k))
    outs = [('baggage-db-connection', 'ConfigMap · host, port, sslmode', 'store'),
            ('baggage-db-credentials', 'Secret · written by the provider', 'store'),
            ('RDS for PostgreSQL 17', 'its own VPC · encrypted at rest', 'external')]
    for i, (n, s, k) in enumerate(outs):
        x = 48 + i * 312
        b.append(node(x, 536, 280, 48, n, s, k))
    b.append(callout(24, 648, 'The road is everything the request doesn\'t have to say.'))
    b.append(legend(680, [('focal', 'The request and its contract'), ('backend', 'Built in, every time'),
                          ('store', 'What the app reads'), ('external', 'The cloud resource')]))
    return dict(slug='what-a-road-is-made-of', eyebrow='Paving · 02 of 03 · Anatomy',
      title='What a paved road to a cloud database is made of',
      desc='Left, the request: six lines in the app\'s xr-requests folder, kind ManagedPostgreSQL, name baggage-db, size small, version 17, allowedCidrs 203.0.113.0/24 and protect true, with no VPC, subnet, security group, parameter group or IAM. Right, what the platform adds, five layers: the contract (what you can ask for: a size, a version, storage and networks); defaults with no field (encrypted, TLS only, no network until you list one); identity (a password the provider generates, kept in a Secret, never in git); an answer (DependencyReady, with Ready, Provisioning or Failing and why); and a way out (delete the file and every piece goes, while protect keeps a snapshot). Bottom, what the app gets: the ConfigMap baggage-db-connection with host, port and sslmode, the Secret baggage-db-credentials written by the provider, and RDS for PostgreSQL 17 in its own VPC, encrypted at rest.',
      lede='The request is short on purpose. Everything a team would otherwise have to know, decide and remember about running a database in the cloud is in the five layers on the right, and none of them is optional.',
      body=''.join(b), W=1000, H=720, y0=76,
      cards=[('Asked', '', P('The schema is the first guardrail. A field that does not exist cannot be set wrong, and a value outside the list never reaches a review.')),
             ('Always', 'accent', P('Encryption, TLS and a closed network are not settings. They are how this kind of database is built.')),
             ('Answered', 'link', P('A fixed set of reasons means a person, a script and an agent all read the same status and know what to do next.'))])


def q_since_october():
    b = []
    b += [zone(24, 100, 448, 336, 'wished for · october 5, 2026'), zone(504, 100, 472, 336, 'where it stands · october 24, 2026'),
          zone(24, 464, 952, 96, 'next, and written down')]
    rows = [('The XR makes the function', 'not bring your own', 'Built · Oct 8, 2026', 'Lambda, ECS and Container Apps targets', 'focal'),
            ('An approval for cloud prod', 'a reviewed release, like k8s', 'Built · Oct 7, 2026', 'ADR-0020: a release pin PR', 'focal'),
            ('Least privilege, a boundary', 'roles nobody can widen', 'Built · Oct 16, 2026', 'one-hour roles · no stored AWS key', 'focal'),
            ('A queue, a bucket, maybe more', 'the next nouns on the menu', 'Built · Oct 24, 2026', 'MessageQueue · ObjectStorage · ManagedPostgreSQL', 'focal'),
            ('Live cloud health in Tower', 'not just what was deployed', 'Still open', 'Tower shows history, not health', 'optional')]
    for i, (n, s, n2, s2, k) in enumerate(rows):
        y = 128 + i * 60
        b.append(node(48, y, 400, 44, n, s, 'input'))
        b.append(path([(448, y + 22), (528, y + 22)], 'accent' if k == 'focal' else 'muted', dashed=k != 'focal'))
        b.append(node(528, y, 424, 44, n2, s2, k))
    gaps = [('Gap 8 · more consumers', 'ECS task roles · Kubernetes identity'),
            ('Gap 9 · a private database', 'Lambda inside the VPC · an app role'),
            ('Gap 10 · Azure, for real', 'install the providers · run each once')]
    for i, (n, s) in enumerate(gaps):
        x = 48 + i * 312
        b.append(node(x, 488, 280, 48, n, s, 'propose'))
    b.append(callout(24, 600, 'Four of five crossed off in three weeks, and the new gaps are on the page.'))
    b.append(legend(632, [('input', 'The wish'), ('focal', 'Built'), ('optional', 'Still open'), ('propose', 'Known gap, planned')]))
    return dict(slug='three-weeks-of-the-wish-list', eyebrow='Paving · 03 of 03 · Honest notes',
      title='Three weeks of the wish list',
      desc='Two columns. Left, wished for on October 5, 2026, in the essay A service catalog that grows with the company: the XR makes the function instead of bring your own; an approval for cloud production, a reviewed release like Kubernetes apps have; least privilege inside a boundary, roles nobody can widen; a queue, a bucket, maybe more, the next nouns on the menu; and live cloud health in Tower. Right, where each stands on October 24, 2026: built October 8, the Lambda, ECS and Container Apps targets; built October 7, ADR-0020\'s release pin PR; built October 16, one-hour roles and no stored AWS key; built October 24, MessageQueue, ObjectStorage and ManagedPostgreSQL; still open, Tower shows history, not health. Bottom, next and written down: gap 8, more consumers (ECS task roles and Kubernetes identity); gap 9, a private database (Lambda inside the VPC and an app role); gap 10, Azure for real (install the providers and run each kind once).',
      lede='The last essay ended with a list of what I wanted next. Most of it is built now, and building it turned up three new gaps, which is how a road gets longer.',
      body=''.join(b), W=1000, H=672, y0=76,
      cards=[('Composed, not borrowed', '', P('Cloud targets stopped being bring your own on October 8, so the rules finally had somewhere to live.')),
             ('Keys gone', 'accent', P('Crossplane, Lambda and ECS deploys earn one-hour roles. Every role Crossplane creates sits inside one permissions boundary.')),
             ('Gaps named', 'link', P('Gaps 8 to 10 are in Airframe\'s known gaps with a proposed fix each, not discovered by the next person.'))])
