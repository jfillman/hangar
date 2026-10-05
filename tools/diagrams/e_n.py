"""The Expansion set: pictures for the essay "A service catalog that grows with the company" (2026-10-05)."""
from libx import *


def g_many_targets():
    b = []
    b += [zone(24, 100, 952, 100, 'who asks'), zone(24, 232, 952, 112, 'airframe · catalog.hangar.io'),
          zone(24, 376, 952, 112, 'glidepath · build once'), zone(24, 520, 952, 104, 'where it runs')]
    askers = [('Backstage form', 'a scaffolder template'), ('Tower', 'the developer view'),
              ('An agent', 'the same API, typed'), ('A pull request', 'an XR file in git')]
    for i, (n, s) in enumerate(askers):
        x = 48 + i * 232
        b.append(path([(x + 104, 180), (x + 104, 216)], marker=False))
        b.append(node(x, 124, 208, 56, n, s, 'input'))
    b.append(path([(152, 216), (848, 216)], marker=False))
    b += [path([(258, 216), (258, 256)]), path([(742, 216), (742, 256)])]
    b.append(hlab(258, 742, 216, 'ANY CALLER, THE SAME API'))
    b += [node(48, 256, 420, 56, 'Container app APIs', 'python · go · node · spring boot'),
          node(532, 256, 420, 56, 'Function APIs', 'LambdaFunction · AzureFunction', 'focal')]
    b += [path([(258, 312), (258, 400)]), path([(742, 312), (742, 360), (300, 360), (300, 400)])]
    b.append(hlab(300, 742, 360, 'THE SAME BUILD PATH'))
    b += [node(48, 400, 420, 56, 'One build', 'Containerfile to OCI image · signed'),
          path([(468, 428), (532, 428)], 'accent'),
          node(532, 400, 420, 56, 'deploy.target', 'one gate in the deploy stage', 'focal')]
    b += [path([(742, 456), (742, 504)], marker=False), path([(152, 504), (848, 504)], marker=False)]
    targets = [('k8s-rollout', 'an Argo Rollout, in cluster', 'backend'), ('aws-ecs', 'update an ECS service', 'focal'),
               ('aws-lambda', 'copy to ECR, then update', 'focal'), ('azure-container-apps', 'apps and Azure Functions', 'focal')]
    for i, (n, s, k) in enumerate(targets):
        x = 48 + i * 232
        b.append(path([(x + 104, 504), (x + 104, 544)]))
        b.append(node(x, 544, 208, 56, n, s, k))
    b.append(callout(24, 664, 'Kubernetes is where the platform lives, not where every workload has to.'))
    b.append(legend(696, [('input', 'Who asks'), ('backend', 'There before'), ('focal', 'New, Oct 3 and 4, 2026'),
                          ('accent', 'Picks the target')]))
    return dict(slug='one-catalog-many-targets', eyebrow='Expansion · 01 of 03 · The shape',
      title='One catalog, many places to run',
      desc='Four rows. Who asks: a Backstage form (a scaffolder template), Tower, an agent using the same typed API, or a pull request with an XR file in git. Any caller reaches the same API, Airframe\'s catalog.hangar.io group, which holds the container app APIs (Python, Go, Node and Spring Boot) and, highlighted as new, the function APIs, LambdaFunction and AzureFunction. Both take the same build path in Glidepath: one build, from a Containerfile to a signed OCI image, then deploy.target, one gate in the deploy stage, also new. It picks where the service runs: k8s-rollout, an Argo Rollout in the cluster, which was there before, and three new cloud targets: aws-ecs updates an ECS service, aws-lambda copies the image to ECR and then updates the function, and azure-container-apps updates a Container App, which is also how Azure Functions are hosted.',
      lede='A developer asks for a kind of service, never for a cloud. The platform builds it once and the deploy stage decides where it goes, so a new place to run is a new branch at the bottom, not a new platform.',
      body=''.join(b), W=1000, H=724, y0=76,
      cards=[('Same front door', '', P('A form, Tower, an agent and a pull request all create the same kind of resource. Adding a function changed none of them.')),
             ('Same build', 'accent', P('A function is a container image too. It reuses the Containerfile, the signing and the release records every app already had.')),
             ('A new branch, not a fork', 'link', P('Each cloud target is one Task behind one gate. Tower files it by its target and shows the cloud variant of the Deployments tab.'))])


def g_where_policy_lives():
    b = []
    b += [zone(24, 100, 952, 96, 'who writes the policy'), zone(24, 240, 952, 220, 'policy as code'),
          zone(24, 488, 952, 96, 'what a developer does')]
    b += [node(48, 124, 280, 48, 'Enterprise Architecture', 'standards · approved patterns', 'input'),
          node(360, 124, 280, 48, 'Security', 'controls · data classification', 'input'),
          node(692, 124, 260, 48, 'Platform team', 'turns both into code, in git')]
    b += [path([(188, 172), (188, 212), (760, 212), (760, 172)], 'accent'),
          path([(440, 172), (440, 212)], 'accent', marker=False),
          hlab(188, 440, 212, 'STANDARDS, IN WORDS', ACC)]
    b += [path([(900, 172), (900, 228)], marker=False), path([(180, 228), (900, 228)], marker=False)]
    cols = [
        (('The XRD schema', 'what you can ask for', 'focal'),
         [('Enums and patterns', 'runtime · architecture · region', 'backend'),
          ('CEL rules across fields', 'attach mode needs a broker', 'backend')]),
        (('The Composition', 'what you always get', 'focal'),
         [('Gates and safe defaults', 'dev cluster check · no repo Delete', 'backend'),
          ('Tags, roles, encryption', 'proposal · every cloud resource', 'optional')]),
        (('Admission and CI', 'what nobody gets', 'security'),
         [('Kyverno admission policy', 'a test mounts only its own secret', 'backend'),
          ('airframe-validate in CI', 'release-owned keys stay put', 'backend')]),
    ]
    for i, (head, ex) in enumerate(cols):
        x = 48 + i * 320
        cx = x + 132
        b.append(path([(cx, 228), (cx, 268)]))
        b.append(node(x, 268, 264, 56, *head))
        for j, (n, s, k) in enumerate(ex):
            y = 340 + j * 56
            b.append(node(x, y, 264, 44, n, s, k))
    b += [node(48, 512, 280, 48, 'kind: LambdaFunction', 'a few fields, in plain words', 'focal'),
          path([(328, 536), (368, 536)], 'accent'),
          node(368, 512, 264, 48, 'Airframe applies all three', 'on create and on every change'),
          path([(632, 536), (688, 536)], 'open'),
          node(688, 512, 264, 48, 'A service that already complies', 'the paperwork is done', 'store')]
    b.append(callout(24, 624, 'The policy is written once, by the people who own it, and enforced on every request.'))
    b.append(legend(656, [('input', 'Owns the standard'), ('focal', 'Where it lives'), ('backend', 'Built in Hangar'),
                          ('optional', 'Proposal'), ('security', 'A fence'), ('accent', 'Hands over')]))
    return dict(slug='where-the-policy-lives', eyebrow='Expansion · 02 of 03 · Governance',
      title='Where the policy lives',
      desc='Three rows. Who writes the policy: Enterprise Architecture (standards and approved patterns) and Security (controls and data classification) hand their standards, in words, to the platform team, which turns both into code in git. Policy as code lives in three places. The XRD schema decides what you can ask for; built in Hangar today: enums and patterns for runtime, architecture and region, and CEL rules across fields, such as RabbitMQ attach mode needing a broker. The Composition decides what you always get; built today: gates and safe defaults, like the live dev cluster check and no Delete on repositories; a proposal, drawn dashed: tags, roles and encryption on every cloud resource. Admission and CI, drawn as a fence, decide what nobody gets; built today: a Kyverno admission policy so a test mounts only its own secret, and airframe-validate in CI keeping release-owned keys where they belong. A developer writes kind LambdaFunction with a few fields in plain words, Airframe applies all three on create and on every change, and the result is a service that already complies, with the paperwork done.',
      lede='Architects and security teams own the rules. The platform team owns the code that enforces them. The developer owns a short request, and never has to read either.',
      body=''.join(b), W=1000, H=684, y0=76,
      cards=[('Ask', '', P('The schema is the first policy. A region that is not on the list is not a value the API will take, so it never reaches a review.')),
             ('Always', 'accent', P('The Composition adds what every service gets whether anyone asked or not. Nobody remembers the tags, because nobody has to.')),
             ('Never', 'link', P('Admission policies and CI checks are the fence for anything that slips around the API. They fail loudly, with a rule id a person or an agent can read.'))])


def g_today_and_next():
    b = []
    b += [zone(24, 100, 464, 440, 'built · october 3, 2026'), zone(512, 100, 464, 440, 'proposal · next')]
    b.append(node(48, 128, 416, 56, 'LambdaFunction XR', 'runtime · architecture · region', 'focal'))
    left = [('Source repo', 'handler · Containerfile · cicd.yaml'), ('Glidepath CI/CD', 'builds one architecture, deploys'),
            ('Catalog entry', 'service-class: function')]
    b.append(path([(64, 184), (64, 368)], marker=False))
    for i, (n, s) in enumerate(left):
        y = 216 + i * 64
        b += [path([(64, y + 24), (88, y + 24)]), node(88, y, 376, 48, n, s)]
    b += [lab(256, 416, 'BRING YOUR OWN, TODAY'),
          node(48, 440, 416, 56, 'Function, role and ECR repo', 'created by hand, before onboarding', 'input'),
          path([(464, 304), (476, 304), (476, 468), (464, 468)], 'link')]
    b.append(node(536, 128, 416, 56, 'LambdaFunction XR', 'the same few fields', 'focal'))
    right = [('Repo, CI/CD and catalog entry', 'the same as today', 'backend'),
             ('Lambda function', 'approved region · tags · log retention', 'propose'),
             ('Execution role', 'least privilege · permission boundary', 'propose'),
             ('ECR repository', 'scan on push · encrypted', 'propose'),
             ('Release pin PR', 'ADR-0020 · approval for Flight', 'propose')]
    b.append(path([(552, 184), (552, 496)], marker=False))
    for i, (n, s, k) in enumerate(right):
        y = 216 + i * 64
        b += [path([(552, y + 24), (576, y + 24)]), node(576, y, 376, 48, n, s, k)]
    b.append(callout(24, 580, 'Same request, same few fields. The difference is how much the platform does for you.'))
    b.append(legend(612, [('focal', 'The request'), ('backend', 'Composed today'), ('input', 'Made by hand'),
                          ('propose', 'Proposal'), ('link', 'Deploys into')]))
    return dict(slug='a-lambda-today-and-next', eyebrow='Expansion · 03 of 03 · Honest notes',
      title='A LambdaFunction, today and next',
      desc='Two columns. Left, built on October 3, 2026: a LambdaFunction XR with runtime, architecture and region composes a source repo (handler, Containerfile and cicd.yaml), Glidepath CI/CD that builds one architecture and deploys, and a catalog entry with service-class function. Below, labelled bring your own, today: the function, its execution role and its ECR repository are created by hand before onboarding, and Glidepath\'s CI/CD only updates them. Right, a proposal: the same LambdaFunction XR with the same few fields also composes the repo, CI/CD and catalog entry as today, plus, drawn as proposals, the Lambda function itself in an approved region with tags and log retention, an execution role with least privilege and a permission boundary, an ECR repository with scan on push and encryption, and a release pin pull request from ADR-0020 that gives cloud services an approval step for Flight environments.',
      lede='Today the XR wires up everything around the function and trusts you to have made the function. Next, the XR makes the function too, and that is where the architects\' and security team\'s rules get to live.',
      body=''.join(b), W=1000, H=640, y0=76,
      cards=[('Shipped small', '', P('Bring your own function let the first cloud targets land in two days, with no cloud credentials held by the control plane.')),
             ('The gap is named', 'accent', P('Nothing composes the cloud resource yet, and the Lambda and Azure targets have not deployed for real yet. Both are written down, not hidden.')),
             ('Same contract', 'link', P('When the XR starts composing the function, the request does not change. That is the point of putting an API in front.'))])
