"""The Service catalog set: pictures for the essay "Why Airframe" (2026-09-30)."""
from libx import *


def c_one_api():
    b = []
    b += [zone(24, 100, 952, 120, 'who asks'), zone(24, 260, 952, 120, 'one contract · every write is a commit'),
          zone(24, 420, 952, 120, 'what runs')]
    b += [path([(184, 192), (184, 240), (420, 240), (420, 296)]),
          path([(500, 192), (500, 296)]),
          path([(816, 192), (816, 240), (580, 240), (580, 296)], 'link', dashed=True)]
    b += [node(64, 136, 240, 56, 'Developer', 'Tower · Backstage templates', 'input'),
          node(380, 136, 240, 56, 'Pipeline', 'Glidepath · a git commit', 'input'),
          node(696, 136, 240, 56, 'AI agent', 'Autopilot · through Clearance', 'propose')]
    b += [path([(500, 360), (500, 456)], 'accent'), vlab(500, 372, 404, 'CROSSPLANE COMPOSES', ACC),
          path([(420, 360), (420, 408), (184, 408), (184, 456)], 'accent'),
          path([(580, 360), (580, 408), (816, 408), (816, 456)], 'accent'),
          path([(900, 456), (900, 360)], 'open'), vlab(900, 392, 424, 'REPORTS', side='r'),
          path([(300, 328), (256, 328)], 'open')]
    b += [node(48, 296, 208, 64, 'Backstage catalog', 'inventory, generated from CRDs', 'store'),
          node(300, 296, 400, 64, 'Airframe', 'XRDs · contract bundle · llms.txt', 'focal'),
          node(744, 296, 208, 64, 'Status and reasons', 'ComponentReady · verify checks', 'store')]
    b += [node(64, 456, 240, 64, 'Apps and environments', 'NodeJS · Python · Go · Spring'),
          node(380, 456, 240, 64, 'Components', 'PostgreSQL · Redis · RabbitMQ'),
          node(696, 456, 240, 64, 'Secrets and identity', 'SecretStore · Dex')]
    b.append(callout(24, 584, 'Three kinds of caller, one front door. The catalog is the API they all agree on.'))
    b.append(legend(616, [('input', 'People and pipelines'), ('propose', 'Agents, runtime proposed'), ('focal', 'The contract'), ('store', 'Generated or observed'), ('accent', 'Creates'), ('open', 'Reads')]))
    return dict(slug='one-api-many-callers', eyebrow='Service catalog · 01 of 05 · The front door',
      title='One API, three kinds of caller',
      desc='Three rows. Who asks: a developer through Tower and Backstage templates, a pipeline through Glidepath as a git commit, and an AI agent through Autopilot and its Clearance gateway, drawn dashed because the agent runtime is proposed. All three converge on one contract, Airframe, with its XRDs, contract bundle and llms.txt, and every write is a git commit. Airframe feeds the Backstage catalog, an inventory generated from its CRDs. Crossplane composes what runs: apps and environments (NodeJS, Python, Go, Spring Boot), components (PostgreSQL, Redis, RabbitMQ) and secrets and identity (SecretStore, Dex). What runs reports back as status and reasons: ComponentReady and verify checks.',
      lede='A developer at a portal, a pipeline making a commit, and an agent acting on someone\'s behalf all ask for the same things. If they each had their own way in, you\'d have three platforms to keep honest.',
      body=''.join(b), W=1000, H=644, y0=76,
      cards=[('Built', '', UL(['Fifteen APIs in Airframe, reconciled by Crossplane.', 'Backstage holds no Kubernetes credentials; its templates make git commits.', 'A generated contract bundle and llms.txt, checked in CI.'])),
             ('Proposed', 'link', P('Autopilot\'s runtime: agents reach the same APIs through Clearance, with narrow, audited authority. The Clearance core is built and tested; the real backends are not.')),
             ('Why one door', 'accent', P('Policy, audit and naming live in one place. A new kind of caller, even one we haven\'t thought of yet, inherits all of it for free.'))])


def c_menu_inventory():
    b = []
    b += [zone(24, 100, 464, 300, 'the inventory · what exists'), zone(512, 100, 464, 300, 'the menu · what you can ask for')]
    b += [path([(256, 196), (256, 236)], 'open'), path([(744, 196), (744, 236)], 'open'),
          path([(256, 292), (256, 332)], 'open'), path([(744, 292), (744, 332)], 'open'),
          path([(536, 356), (464, 356)], 'accent'), hlab(464, 536, 356, 'FEEDS', ACC)]
    b += [node(48, 140, 416, 56, 'Who owns checkout-api?', 'what is running, and whose is it', 'input'),
          node(48, 236, 128, 56, 'Component', 'a running service'),
          node(192, 236, 128, 56, 'Owner', 'team · on-call'),
          node(336, 236, 128, 56, 'Docs', 'TechDocs · APIs'),
          node(48, 332, 416, 48, 'Backstage catalog', 'generated from what the control plane reports', 'store')]
    b += [node(536, 140, 416, 56, 'Can I have a database?', 'what can I ask for, and what do I get', 'input'),
          node(536, 236, 128, 56, 'PostgreSQL', 'size · instances'),
          node(680, 236, 128, 56, 'Redis', 'a cache per env'),
          node(824, 236, 128, 56, 'SecretStore', 'app · cluster'),
          node(536, 332, 416, 48, 'Airframe', 'XRDs with outputs, conditions and reasons', 'focal')]
    b += [path([(400, 440), (400, 380)], 'open'), path([(600, 440), (600, 380)], 'open')]
    b.append(node(300, 440, 400, 56, 'An agent, or a new hire', 'needs both answers before acting', 'propose'))
    b.append(callout(24, 540, 'Most catalogs only answer the question on the left, and go stale answering it.'))
    b.append(legend(572, [('input', 'The question'), ('focal', 'The menu'), ('store', 'The inventory'), ('propose', 'The reader'), ('accent', 'Generates'), ('open', 'Answers')]))
    return dict(slug='menu-and-inventory', eyebrow='Service catalog · 02 of 05 · Two catalogs',
      title='The menu and the inventory',
      desc='Two panels. The inventory answers "who owns checkout-api?": what is running and whose it is, through components, owners with team and on-call, and docs, collected in the Backstage catalog, which is generated from what the control plane reports. The menu answers "can I have a database?": what you can ask for and what you get, through APIs such as PostgreSQL, Redis and SecretStore, defined in Airframe as XRDs with outputs, conditions and reasons. Airframe feeds the Backstage catalog. Below, an agent or a new hire reads both and needs both answers before acting.',
      lede='"Service catalog" means two different things. One is a list of what exists. The other is a list of what you\'re allowed to ask for. A platform needs both, and it works best when the first is generated from the second.',
      body=''.join(b), W=1000, H=600, y0=76,
      cards=[('The inventory', '', P('Ownership, docs and dependencies for everything that runs. Useful, and famously hard to keep true when people maintain it by hand.')),
             ('The menu', 'accent', P('Typed APIs with a schema, defaults, outputs and an honest status. This is the part that defines the platform, and the part I built first.')),
             ('Generated, not typed', 'link', P('In Hangar, Backstage\'s entities and its templates are both generated from Airframe\'s live XRDs and XRs, so the inventory stays true to what the menu created. Today that\'s on the management cluster; dev and prod are next.'))])


def c_discovery():
    b = []
    cols = [(24, 'what we heard'), (264, 'the job to be done'), (504, 'the noun'), (744, 'the api')]
    for zx, t in cols:
        b.append(zone(zx, 100, 232, 360, t))
    rows = [
        (('"Three weeks for a DB"', 'backend developer'), ('Get a database today', 'self-service, same day'),
         ('Database', 'size · environment'), ('PostgreSQL', 'one per environment')),
        (('"I copy the last repo"', 'new team lead'), ('Start a service right', 'with a repo and CI'),
         ('Application', 'language · version'), ('NodeJSApplication', 'and Python, Go, Spring')),
        (('"Where does the key go?"', 'frontend developer'), ('Keep secrets out of git', 'never in a values file'),
         ('Secret store', 'app · cluster'), ('SecretStore', 'one per app and cluster')),
        (('"Is staging even up?"', 'QA engineer'), ('Trust what green means', 'before a release'),
         ('Health', 'ready · degraded · why'), ('ComponentReady', 'on every component')),
    ]
    kinds = ['input', 'backend', 'backend', 'focal']
    for i, row in enumerate(rows):
        y = 136 + i * 80
        for j, (zx, _) in enumerate(cols):
            b.append(node(zx + 16, y, 200, 56, *row[j], kind=kinds[j]))
            if j < 3:
                b.append(path([(zx + 216, y + 28), (zx + 256, y + 28)]))
    b += [path([(844, 432), (844, 500), (124, 500), (124, 432)], 'accent'),
          hlab(124, 844, 500, 'SHOW IT BACK TO THE PEOPLE WHO SAID IT', ACC)]
    b.append(callout(24, 548, 'Developers don\'t ask for XRDs. They tell you what hurts. The API is our translation.'))
    b.append(legend(580, [('input', 'What a developer said'), ('backend', 'Our reading of it'), ('focal', 'The API in Airframe'), ('accent', 'Review loop')]))
    return dict(slug='from-interview-to-api', eyebrow='Service catalog · 04 of 05 · Discovery',
      title='From an interview to an API',
      desc='Four columns: what we heard, the job to be done, the noun, and the API. Four example rows. "Three weeks for a DB" from a backend developer becomes the job get a database today, the noun database (size and environment), and the PostgreSQL API, one per environment. "I copy the last repo" from a new team lead becomes start a service right with a repo and CI, the noun application, and NodeJSApplication plus Python, Go and Spring Boot. "Where does the key go?" from a frontend developer becomes keep secrets out of git, the noun secret store, and the SecretStore API, one per app and cluster. "Is staging even up?" from a QA engineer becomes trust what green means, the noun health, and ComponentReady, a condition on every component. A loop runs from the API column back to the first: show it back to the people who said it.',
      lede='The quotes are illustrative; everything on the right is real in Airframe. Each one started as a sentence like these, even when the person saying it was me.',
      body=''.join(b), W=1000, H=608, y0=76,
      cards=[('Listen for verbs', '', P('People describe waiting, copying and guessing. Each of those is a job the platform could do for them, and the job is what you design around.')),
             ('Find the noun', 'accent', P('A good API is a noun a developer already uses: a database, an application, a secret store. If you have to explain the name, it isn\'t one yet.')),
             ('Close the loop', 'link', P('Take the draft schema back to the person who asked. "Would this have saved you the three weeks?" is the cheapest review you\'ll ever run.'))])


def c_anatomy():
    b = []
    b.append(zone(24, 96, 952, 456, 'one catalog entry · postgresql'))
    facets_l = [
        ('ask', 'What you ask for', [('environmentRef', 'required', False), ('size', 'small · medium · large', False), ('instances', '1 to 3', False)], 'backend'),
        ('get', 'What you get back', [('Secret {name}-app', 'cnpg managed', False), ('host · port · username', 'secret key', False), ('password · uri · jdbcUri', 'secret key', False)], 'backend'),
        ('know', 'How you know', [('PostgreSQLReady', 'true', False), ('PostgreSQLProvisioning', 'false', False), ('PostgreSQLDegraded', 'false', False)], 'focal'),
    ]
    facets_r = [
        ('check', 'How it is verified', [('xr-ready', 'condition', False), ('secret-exists', 'password key', False), ('reachable', 'tcp :5432', False)], 'backend'),
        ('agents', 'Said for agents', [('agent-summary', 'one line', False), ('contract bundle', 'generated', False), ('llms.txt', 'repo root', False)], 'backend'),
        ('rules', 'Who may change it', [('owner', 'human', False), ('write path', 'a git commit', False), ('drift', 'fails ci', False)], 'backend'),
    ]
    ys = [124, 264, 404]
    for y, (tag, name, chips, kind) in zip(ys, facets_l):
        b.append(path([(400, 328), (364, 328), (364, y + 64), (328, y + 64)], marker=False))
        b.append(depnode(48, y, 280, 128, tag, name, chips, kind))
    for y, (tag, name, chips, kind) in zip(ys, facets_r):
        b.append(path([(600, 328), (636, 328), (636, y + 64), (672, y + 64)], marker=False))
        b.append(depnode(672, y, 280, 128, tag, name, chips, kind))
    b.append(node(400, 292, 200, 72, 'PostgreSQL', 'postgresqls.catalog.hangar.io', 'focal'))
    b.append(callout(24, 596, 'A name and a form is a wish list. The contract is what makes it an API.'))
    b.append(legend(628, [('backend', 'Part of the contract'), ('focal', 'What an agent switches on')]))
    return dict(slug='anatomy-of-an-entry', eyebrow='Service catalog · 03 of 05 · The contract',
      title='What one catalog entry has to carry',
      desc='The PostgreSQL API, postgresqls.catalog.hangar.io, at the centre of six facets, all taken from Airframe. What you ask for: environmentRef (required), size (small, medium or large) and instances (1 to 3). What you get back: the CloudNativePG-managed Secret named after the database with host, port, username, password, uri and jdbcUri keys. How you know, highlighted: the ComponentReady reasons PostgreSQLReady (true), PostgreSQLProvisioning and PostgreSQLDegraded (false). How it is verified: xr-ready, secret-exists and reachable on TCP 5432. Said for agents: a one-line agent summary, the generated contract bundle and llms.txt at the repo root. Who may change it: the owner is a human, the write path is a git commit, and drift between the contract and its source fails CI.',
      lede='This is Airframe\'s real PostgreSQL entry, read from its XRD and its sidecar meta file. The form a developer fills in is the smallest part of it.',
      body=''.join(b), W=1000, H=656, y0=76,
      cards=[('For people', '', P('The ask is a handful of fields, and only the environment has no default. Everything a developer needs to connect is named in advance, so nobody guesses a Secret name.')),
             ('For machines', 'accent', P('A closed list of reasons, and checks that say what "working" means. An agent can act on PostgreSQLDegraded. It can\'t act on "something\'s off".')),
             ('For the platform team', 'link', P('The contract is generated and checked in CI, so the entry can\'t quietly drift from what the composition does.'))])


def c_roadmap():
    b = []
    b.append(zone(24, 96, 952, 244, 'building the catalog · a first six months'))
    phases = [
        ('weeks 1-4', 'Discovery', 'talk to developers', 'focal',
         ['Interview 15 to 20 devs', 'Shadow two onboardings', 'Inventory what runs', 'Rank the top journeys']),
        ('weeks 4-6', 'Name the nouns', 'jobs into resources', 'backend',
         ['Draft three to five APIs', 'Review schemas with', 'the people who asked', 'Say what we won\'t build']),
        ('weeks 6-12', 'First slice', 'one api, one team', 'backend',
         ['Ship the top journey', 'Git is the only way in', 'Pair with a pilot team']),
        ('weeks 10-16', 'Make it readable', 'contract and status', 'backend',
         ['Outputs and conditions', 'Generated portal pages', 'Drift fails CI']),
        ('weeks 14-20', 'Open to agents', 'same api, bounded', 'backend',
         ['The contract over MCP', 'Narrow, audited access', 'Writes are pull requests']),
        ('ongoing', 'Measure and grow', 'close the loop', 'backend',
         ['Time to first deploy', 'Adoption per API', 'Retire what\'s unused', 'Back to discovery']),
    ]
    b += [path([(884, 144), (884, 124), (104, 124), (104, 144)], 'accent'),
          lab(494, 112, 'WHAT WE LEARN GOES BACK INTO DISCOVERY', ACC)]
    for i, (wk, name, sub, kind, lines) in enumerate(phases):
        x = 32 + i * 156
        b.append(node(x, 144, 144, 72, name, sub, kind, tag=wk))
        if i < 5:
            b.append(path([(x + 144, 180), (x + 156, 180)]))
        for k, s in enumerate(lines):
            b.append(text(x + 4, 248 + k * 20, s, 10.5, 400, MUTED))
    b.append(callout(24, 380, 'Discovery comes first and comes back. The first catalog you ship is a draft of the second one.'))
    b.append(legend(412, [('focal', 'Start here'), ('backend', 'Later phases, overlapping'), ('accent', 'The loop')]))
    return dict(slug='roadmap-discovery-first', eyebrow='Service catalog · 05 of 05 · The approach',
      title='How I\'d build a company\'s service catalog',
      desc='Six overlapping phases over a first six months. Weeks 1 to 4, highlighted, discovery: interview 15 to 20 developers, shadow two onboardings, inventory what runs, rank the top journeys. Weeks 4 to 6, name the nouns: draft three to five APIs, review the schemas with the people who asked, and say what won\'t be built. Weeks 6 to 12, first slice: ship the top journey with one pilot team, with git as the only way in. Weeks 10 to 16, make it readable: outputs and conditions, generated portal pages, drift fails CI. Weeks 14 to 20, open to agents: the contract over MCP, narrow audited access, writes as pull requests. Ongoing, measure and grow: time to first deploy, adoption per API, retire what is unused, and go back to discovery. A loop runs from the last phase back to the first.',
      lede='A proposal, not a record: this is the plan I\'d bring to a platform team on day one. The weeks overlap on purpose, and the numbers are starting points, not promises.',
      body=''.join(b), W=1000, H=440, y0=76,
      cards=[('Discovery is the product work', '', P('Before any YAML: who are our developers, what do they wait on, and what do they copy from the last project? The answers become the first APIs.')),
             ('Small, then readable, then open', 'accent', P('One API that one team loves beats fifteen nobody asked for. Make it explain itself before you let an agent near it.')),
             ('Measure people, not YAML', 'link', P('Take a baseline during discovery, then count time to first deploy and which APIs teams actually use. An API nobody calls is a cost, and retiring it is part of the job.'))])
