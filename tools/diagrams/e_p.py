"""The Portability set: pictures for the plan "Any forge, any registry" (2026-10-15), about running Hangar on
GitLab and Bitbucket as well as GitHub, and on any OCI registry as well as GHCR."""
from libx import *


def q_coupling():
    b = []
    cols = [('airframe', ('81 GitHub MR templates', '88 live · Repository · File', 'focal'),
                         ('Owner is a literal', 'jfillman in 10 templates', 'backend'), 'MRS + URLS'),
            ('glidepath', ('15 places call GitHub', 'PRs · comments · checks · files', 'backend'),
                          ('GitHub App broker', 'one-repo tokens, 1 hour', 'security'), 'REST + APP'),
            ('tower + backstage', ('App id = GitHub slug', 'github.com/project-slug', 'focal'),
                                  ('GHCR-only image client', 'other registries refused', 'backend'), 'REST + OAUTH'),
            ('apron + argo cd', ('Repo creds by URL', 'App creds · github.com/jfillman', 'security'),
                                ('Ruleset is the gate', 'PaC app integration_id', 'backend'), 'GIT + APP')]
    for i, (zn, n1, n2, lb) in enumerate(cols):
        x = 24 + i * 242
        cx = x + 113
        b.append(path([(cx, 272), (cx, 336)]))
        b.append(vlab(cx, 272, 336, lb))
    for i, (zn, n1, n2, lb) in enumerate(cols):
        x = 24 + i * 242
        b.append(zone(x, 100, 226, 172, zn))
        b.append(node(x + 12, 128, 202, 56, *n1))
        b.append(node(x + 12, 200, 202, 56, *n2))
    b.append(node(48, 336, 904, 56, 'GitHub.com and GHCR', 'one vendor · one rate-limit bucket · one identity · one plan tier', 'external'))
    b.append(callout(24, 436, 'Tekton, Argo CD, ESO and cosign were never the problem. Three things are.'))
    b.append(legend(468, [('focal', 'Load-bearing'), ('security', 'A credential path'), ('backend', 'A literal or a driver'),
                          ('external', 'The vendor'), ('muted', 'Calls')]))
    return dict(slug='where-github-is-load-bearing', eyebrow='Portability · 01 of 06 · Today',
      title='Where GitHub is load-bearing today',
      desc='Four product zones, each calling GitHub.com and GHCR. Airframe composes 81 provider-upjet-github managed-resource templates, Repository and RepositoryFile, 88 of them live, highlighted as load-bearing, and has the owner jfillman as a literal in ten templates. Glidepath has fifteen places, thirteen catalog Tasks, a StepAction and a notify Job, calling the GitHub REST API for pull requests, comments, check runs and file contents, and a broker that mints one-repo GitHub App tokens valid for an hour. Tower and Backstage identify an app by its github.com/project-slug annotation, highlighted as load-bearing, and have an image client that refuses any registry but GHCR. Apron and Argo CD hold repository credentials as GitHub App credentials matched by the github.com/jfillman URL prefix, and the merge gate is a GitHub ruleset that trusts only the Pipelines as Code app integration id. All four share one vendor, one rate-limit bucket, one identity and one plan tier.',
      lede='GitHub is mostly an accident of where Hangar was built: a literal here, a curl there. In three places it is part of the design: the Crossplane resources that write to repositories, the GitHub App that mints CI tokens, and the annotation Tower uses to decide who owns an app.',
      body=''.join(b), W=1000, H=520, y0=76,
      cards=[('Load-bearing', 'accent', UL(['RepositoryFile: 70 templates, 64 live, the source of the 2026-09 data loss and rate-limit storms.',
                                             'github.com/project-slug: Tower authorization (ACC-05), approvers, catalog apps.',
                                             'GitHub App tokens: the never-persisted credential the platform is built on.'])),
             ('Mechanical', '', P('The owner literal, ghcr.io in onboarding, hardcoded links, the Images tab and the prune call. Each is config or one driver, and none needs a design decision.')),
             ('Already neutral', 'link', P('Tekton, Pipelines as Code (it speaks GitLab and Bitbucket), Argo CD, ESO, the dockerconfigjson pull secret, cosign and Rekor. They stay as they are.'))])


def q_contracts():
    b = []
    callers = [('Airframe compositions', 'repos · seed files · hooks'), ('Glidepath tasks', 'PRs · statuses · image push'),
               ('Tower backend', 'PRs · links · images · prune')]
    for i, (n, s) in enumerate(callers):
        x = 48 + i * 312
        b.append(path([(x + 140, 172), (x + 140, 236)]))
    b.append(vlab(500, 172, 236, 'CONTRACT ONLY'))
    b += [path([(268, 316), (268, 372)]), path([(732, 316), (732, 372)])]
    b += [zone(24, 100, 952, 96, 'who calls'), zone(24, 236, 952, 104, 'hangar contracts')]
    for i, (n, s) in enumerate(callers):
        b.append(node(48 + i * 312, 124, 280, 48, n, s, 'input'))
    b += [node(48, 260, 440, 56, 'SCM contract', 'repos · files · hooks · merge gate · PRs · statuses · tokens', 'focal'),
          node(512, 260, 440, 56, 'Registry contract', 'OCI push · pull · digest · referrers · list · delete', 'focal')]
    b.append(depnode(48, 372, 440, 160, 'forge', 'Forge drivers',
                     [('GitHub', 'built today · driver 1', False), ('GitLab · .com and self-managed', 'phase 3', True),
                      ('Bitbucket Cloud', 'phase 4', True), ('Bitbucket Data Center', 'phase 4', True)]))
    b.append(depnode(512, 372, 440, 160, 'registry', 'Registry drivers',
                     [('GHCR', 'built today', False), ('GitLab Container Registry', 'phase 1', True),
                      ('Harbor', 'phase 1 · neutral default', True), ('ECR · ACR · Artifactory', 'by demand', True)]))
    b.append(callout(24, 576, 'Two choices, made separately. A Bitbucket shop still needs a registry.'))
    b.append(legend(608, [('input', 'Caller'), ('focal', 'Hangar-owned contract'), ('backend', 'Driver set'),
                          ('security', 'Planned driver')]))
    return dict(slug='two-contracts-many-drivers', eyebrow='Portability · 02 of 06 · The shape',
      title='Two contracts, many drivers',
      desc='Three callers, Airframe compositions (repositories, seed files and webhooks), Glidepath tasks (pull requests, statuses and image pushes) and the Tower backend (pull requests, links, images and pruning), call Hangar contracts, never a vendor API. The SCM contract covers repositories, files, hooks, the merge gate, pull requests, statuses and tokens; the registry contract covers OCI push, pull, digest, referrers, list and delete. Each contract has a set of drivers. Forge drivers: GitHub, built today, then GitLab for gitlab.com and self-managed in phase 3, and Bitbucket Cloud and Bitbucket Data Center in phase 4. Registry drivers: GHCR, built today, then the GitLab Container Registry and Harbor, the neutral default, in phase 1, and ECR, ACR and Artifactory on demand.',
      lede='The forge and the registry are two independent choices, and today they are welded together: the image path is ghcr.io/<GitHub owner>/<app> and the pull credential is a GitHub token. Hangar owns the two contracts; each vendor is a driver behind one of them.',
      body=''.join(b), W=1000, H=660, y0=76,
      cards=[('SCM contract', 'accent', UL(['Declarative: Repository, RepositoryFile, Webhook, MergeGate, as scm.hangar.io resources.',
                                             'Imperative: pr open, find, comment, status, contents, compare, token.',
                                             'One Go library behind the provider, the scm CLI and the broker.'])),
             ('Registry contract', 'link', P('Push, pull, digest and cosign already speak plain OCI. Only listing with dates and deleting are vendor APIs, so only those need drivers.')),
             ('Capability, not the lowest common denominator', '', P('A driver declares what it can enforce, such as a required check from one named app. Tower shows the level each app actually has.'))])


def q_tokens():
    b = [zone(312, 116, 344, 228, 'platform-system', right=True)]
    b += [path([(256, 176), (336, 176)], 'link'), hlab(256, 336, 176, 'REQUEST'),
          path([(632, 176), (712, 176)], 'accent'), hlab(632, 712, 176, 'MINTS'),
          path([(484, 264), (484, 204)]), vlab(484, 204, 264, 'SIGNS WITH'),
          path([(376, 204), (376, 228), (152, 228), (152, 264)], dashed=True), hlab(152, 376, 228, 'ROTATES DAILY')]
    b += [node(48, 148, 208, 56, 'Pipeline pod', 'projected SA token, aud scm', 'input'),
          node(336, 148, 296, 56, 'scm broker', 'TokenReview + Repository CR check', 'focal'),
          node(336, 264, 296, 56, 'Forge credential', 'App key · group token · OAuth secret', 'security'),
          node(48, 264, 208, 56, 'PaC provider secret', 'GitLab and Bitbucket only', 'security')]
    b.append(depnode(712, 124, 264, 160, 'per forge', 'What comes back',
                     [('GitHub', 'installation · 1h · one repo', False), ('GitLab', 'project token · 1 day', True),
                      ('Bitbucket Cloud', 'OAuth · 2h · workspace', True), ('Bitbucket DC', 'HTTP token · 1 day', True)]))
    b.append(callout(24, 392, 'The weakest forge sets the floor. Write the difference down, never hide it.'))
    b.append(legend(424, [('input', 'Caller'), ('focal', 'Broker'), ('security', 'Credential'),
                          ('accent', 'Short-lived token'), ('muted-dash', 'Rotation')]))
    return dict(slug='a-token-on-every-forge', eyebrow='Portability · 03 of 06 · Credentials',
      title='A short-lived token on every forge',
      desc='A pipeline pod sends its projected ServiceAccount token, audience scm, to the scm broker in platform-system, which checks it with a TokenReview and checks the caller owns a Repository CR for the repo. The broker signs with a forge credential that never leaves platform-system: a GitHub App key, a GitLab group token or a Bitbucket OAuth secret. It mints a short-lived token, which differs per forge: a GitHub installation token for one repo for an hour, built today; planned, a GitLab project access token for one day, a Bitbucket Cloud OAuth token for two hours that covers the whole workspace, and a Bitbucket Data Center HTTP token for one repo for a day. The broker also rotates, daily, the provider secret Pipelines as Code needs on GitLab and Bitbucket.',
      lede='Hangar\'s rule is that a pipeline never holds a standing credential: it proves who it is and gets a token for one repository. The broker keeps that rule on every forge. What it cannot keep is the lifetime and the scope, and those differ.',
      body=''.join(b), W=1000, H=476, y0=76,
      cards=[('Same front door', '', P('The broker\'s caller check does not change: a Repository CR in your namespace, proved with TokenReview. Only the minting step is per forge.')),
             ('Two weaker spots', 'accent', UL(['GitLab tokens expire by date, so a token can live up to a day. The broker revokes it when the run ends.',
                                                 'Bitbucket Cloud OAuth tokens cover the whole workspace. Use one workspace per trust boundary.'])),
             ('One new standing secret', 'link', P('Pipelines as Code on GitLab and Bitbucket reads a token from a Secret named by the Repository CR. The broker rotates it daily and Tower shows its age.'))])


def q_release_on_gitlab():
    b = []
    X = {'dev': 110, 'gl': 300, 'gp': 500, 'rg': 700, 'ar': 890}
    top, bot = 84, 556
    for x in X.values():
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="rgba(27,31,36,0.22)" stroke-width="1" stroke-dasharray="3,3"/>')

    def msg(a, c, y, label, color='link', dashed=False, lc=SOFT):
        x1, x2 = X[a], X[c]
        cx = (x1 + x2) / 2
        return path([(x1, y), (x2, y)], color, dashed) + lab(cx, y - 18, label, lc)
    b += [msg('dev', 'gl', 124, 'PUSH + MR'),
          msg('gl', 'gp', 160, 'WEBHOOK'),
          msg('gp', 'rg', 196, 'IMAGE + SIG'),
          msg('gp', 'gl', 232, 'STATUS', 'muted', True),
          msg('dev', 'gl', 268, 'MERGE'),
          msg('gl', 'gp', 304, 'TAG EVENT'),
          msg('gp', 'gl', 340, 'RELEASE MR'),
          msg('gl', 'gp', 376, 'MR EVENT'),
          msg('gp', 'gl', 412, 'GATE STATUSES', 'muted', True),
          msg('dev', 'gl', 448, 'APPROVE + MERGE', 'accent', False, ACC),
          path([(890, 484), (300, 484)], 'muted', True), lab(595, 466, 'PULL GITOPS REPO'),
          msg('ar', 'rg', 520, 'PULL BY DIGEST', 'muted')]
    b += [node(30, 24, 160, 56, 'Developer', 'signed commits', 'input'),
          node(220, 24, 160, 56, 'GitLab', 'app + gitops-<app>', 'external'),
          node(420, 24, 160, 56, 'Glidepath', 'PaC + Tekton + broker', 'focal'),
          node(620, 24, 160, 56, 'Registry', 'GitLab CR or Harbor', 'store'),
          node(810, 24, 160, 56, 'Argo CD', 'the target cluster', 'backend')]
    b.append(legend(588, [('link', 'Event or call'), ('muted-dash', 'Status or pull'), ('accent', 'The merge gate'),
                          ('focal', 'Unchanged engine')]))
    return dict(slug='a-release-on-gitlab', eyebrow='Portability · 04 of 06 · The proof',
      title='One release, start to finish, on GitLab',
      desc='Sequence diagram across five lifelines: developer, GitLab, Glidepath, registry and Argo CD. The developer pushes and opens a merge request; GitLab sends a project webhook to Glidepath; Glidepath pushes the image and its signature to the registry and posts a commit status back. The developer merges; GitLab sends a tag event; Glidepath opens a release merge request on the gitops repo; GitLab sends the merge request event and Glidepath posts a status per gate. The developer approves and merges through the protected branch, the merge gate, highlighted. Argo CD pulls the gitops repo and pulls the image by digest from the registry.',
      lede='This is the acceptance test for phase 3: a new Skyport service, scaffolded from Tower, built, signed, released to a Flight environment and rolled back, with no GitHub anywhere in the path. Every step already exists on GitHub; the only new parts are the drivers.',
      body=''.join(b), W=1000, H=636,
      cards=C3(P('Glidepath\'s engine does not change. Pipelines as Code already accepts GitLab webhooks and reports commit statuses, and Argo CD already pulls from any git host.'),
               UL(['The webhook is per project, so onboarding creates it as an scm.hangar.io Webhook.',
                   'The merge gate is a protected branch with required approvals and "pipelines must succeed".',
                   'Release MR, comments and statuses go through the scm CLI.']),
               P('Not run yet. The lab has no GitLab group. Phase 3 is done when this sequence has run live, end to end, including a rollback, and the merge gate refused a merge with a red gate.'), 'Done when'))


def q_migration():
    b = []
    steps = [('step 1', 'Freeze the old', 'Observe · Orphan', 'backend'), ('step 2', 'Adopt by name', 'same external-name', 'focal'),
             ('step 3', 'Canary one app', 'copied Composition', 'focal'), ('step 4', 'Cut over', 'flip apiVersion, pin', 'backend'),
             ('step 5', 'Retire the old', 'remove the provider', 'backend')]
    for i in range(4):
        x = 48 + i * 184 + 160
        b.append(path([(x, 188), (x + 24, 188)], 'accent' if i in (1, 2) else 'muted'))
    for i, (t, n, s, k) in enumerate(steps):
        b.append(node(48 + i * 184, 152, 160, 72, n, s, k, tag=t))
    b.append(zone(24, 264, 952, 120, 'what must stay true, measured'))
    b += [node(48, 300, 432, 56, 'Zero commits to any repository', 'diff every repo across steps 1 to 3', 'security'),
          node(520, 300, 432, 56, 'API calls at or below today', 'sample /rate_limit every 30 seconds', 'security')]
    b.append(callout(24, 428, 'Adopt, never recreate. A cluster can be rebuilt; a repository\'s history cannot.'))
    b.append(legend(460, [('focal', 'Where it can go wrong'), ('backend', 'Mechanical'), ('security', 'Exit check')]))
    return dict(slug='moving-without-recreating', eyebrow='Portability · 05 of 06 · Migration',
      title='Moving 88 live resources without recreating a repo',
      desc='Five steps in a row. Step 1, freeze the old: every provider-upjet-github managed resource goes to Observe-only with an Orphan deletion policy. Step 2, adopt by name, highlighted: a new scm.hangar.io resource with the same external-name observes the existing repository or file. Step 3, canary one app, highlighted: one application moves to a copied Composition. Step 4, cut over: flip the apiVersion in every composition, tag and pin. Step 5, retire the old: delete the orphaned resources and remove the provider. Two exit checks are measured throughout: zero commits to any repository across steps 1 to 3, checked by diffing every repo, and GitHub API calls at or below today, sampled from the rate-limit endpoint every 30 seconds.',
      lede='The GitHub path has to move onto the new contract before GitLab can use it, and the old provider has already destroyed real files twice. So the move is adoption by name, one app first, and every step is measured against the repositories themselves.',
      body=''.join(b), W=1000, H=512, y0=96,
      cards=[('Lessons already paid for', 'accent', UL(['A Delete policy on a file destroyed cicd.yaml in five repos.',
                                                         'A changed identity field re-identified every live file.',
                                                         'An external-name fight burned 16,000 calls an hour.'])),
             ('So, by construction', '', P('The new RepositoryFile treats only a 404 as gone, never writes on adopt, never deletes, and keeps whatever external-name it observed.')),
             ('Order', 'link', P('Flip the apiVersion only after every caller is ready, test on a copied Composition first (Argo CD self-heal reverts hand edits), and canary on a Skyport app before the fleet.'))])


def q_roadmap():
    b = []
    GX0 = 264; PITCH = 28; NW = 24
    phases = [('P0 · seams, github only', [('Config, not jfillman', 1, 2, 0), ('scm CLI replaces curl', 2, 4, 0), ('Tower ScmClient, new annotation', 2, 4, 0)]),
              ('P1 · registry independence', [('Image repo from config', 4, 5, 0), ('Harbor or GitLab CR lane', 5, 6, 0)]),
              ('P2 · provider-hangar-scm', [('Provider, GitHub driver', 6, 8, 0), ('Adopt 88 MRs, drop upjet', 8, 10, 1)]),
              ('P3 · gitlab end to end', [('GitLab drivers + broker', 10, 12, 0), ('PaC, Argo, Backstage, Dex', 11, 14, 0), ('Skyport app on GitLab', 14, 15, 1)]),
              ('P4 · bitbucket', [('Bitbucket Cloud', 16, 19, 0), ('Bitbucket Data Center', 19, 21, 0)]),
              ('P5 · mixed fleet', [('Per-app forge, rate budgets', 21, 23, 0), ('Docs, rules, scorecard', 22, 24, 0)])]
    for w in range(NW):
        b.append(text(GX0 + w * PITCH + PITCH / 2, 56, f'{w + 1}', 8, 400, SOFT, 'middle', mono=True))
    b.append(text(GX0 - 8, 56, 'WEEK', 8, 500, MUTED, 'end', mono=True, ls='0.14em'))
    b.append(f'<line x1="{GX0}" y1="64" x2="{GX0 + NW * PITCH}" y2="64" stroke="{RULE}" stroke-width="0.8"/>')
    cur = 76; zones = []; bars = []; labels = []
    for pn, tasks in phases:
        zh = 20 + len(tasks) * 40 + 8
        zones.append(f'<rect x="24" y="{cur}" width="952" height="{zh}" rx="8" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.10)" stroke-width="0.8"/>')
        labels.append(text(36, cur + 14, pn.upper(), 8, 500, MUTED, mono=True, ls='0.14em'))
        for i, (nm, s, e, foc) in enumerate(tasks):
            ry = cur + 20 + i * 40
            assert len(nm) * 6.7 <= 216, nm
            labels.append(text(36, ry + 25, nm, 12, 600, INK))
            bx = GX0 + (s - 1) * PITCH; bw = (e - s + 1) * PITCH
            f, st = ('rgba(185,121,31,0.12)', ACC) if foc else ('rgba(91,101,112,0.15)', MUTED)
            bars.append(f'<rect x="{bx}" y="{ry + 8}" width="{bw}" height="24" rx="4" fill="{f}" stroke="{st}" stroke-width="1"/>')
        cur += zh + 12
    b += zones
    for wk, lbl in [(4, 'P0'), (6, 'P1'), (10, 'P2'), (15, 'P3'), (21, 'P4'), (24, 'P5')]:
        xx = GX0 + wk * PITCH
        b.append(f'<line x1="{xx}" y1="64" x2="{xx}" y2="{cur - 12}" stroke="{MUTED}" stroke-width="0.8" stroke-dasharray="4,3"/>')
        b.append(text(xx, 40, lbl, 8, 500, ACC if lbl in ('P2', 'P3') else MUTED, 'middle', mono=True, ls='0.14em'))
    b += bars + labels
    b.append(legend(cur + 16, [('focal', 'Exit test, verified live'), ('input', 'Workstream'), ('muted-dash', 'Phase exit')]))
    return dict(slug='roadmap', eyebrow='Portability · 06 of 06 · Roadmap',
      title='Twenty-four weeks, GitHub first, then GitLab, then Bitbucket',
      desc='Gantt chart of six phases over twenty-four weeks. P0, weeks 1 to 4, seams on GitHub only: config instead of the jfillman literal, the scm CLI replacing inline curl, and Tower\'s ScmClient with a new identity annotation. P1, weeks 4 to 6, registry independence: the image repository from config and a Harbor or GitLab Container Registry lane. P2, weeks 6 to 10, provider-hangar-scm: the provider with its GitHub driver, then adopting all 88 live managed resources and dropping the upjet provider, an exit test. P3, weeks 10 to 15, GitLab end to end: drivers and broker, then Pipelines as Code, Argo CD, Backstage and Dex, then a Skyport app on GitLab, an exit test. P4, weeks 16 to 21, Bitbucket Cloud then Bitbucket Data Center. P5, weeks 21 to 24, mixed fleet: per-app forge choice, rate budgets, docs, business rules and the scorecard.',
      lede='Durations are estimates for one person; the order is the point. Nothing reaches GitLab until the GitHub path runs on the new contracts with no change anyone can see, so the risky migration happens on the forge where Hangar already has live traffic to measure.',
      body=''.join(b), W=1000, H=cur + 16 + 52, y0=24,
      cards=[('P0 to P2: no new forge', '', UL(['Every GitHub call goes through a contract; a CI check keeps it that way.',
                                                 'A second registry proves the image path is not ghcr.io.',
                                                 'The RepositoryFile bug class is gone, on GitHub.'])),
             ('P3: the proof', 'accent', UL(['A Skyport service on GitLab: scaffold, build, sign, release to Flight, roll back.',
                                              'The merge gate refuses a merge with a red gate.'])),
             ('P4 and P5: breadth', 'link', UL(['Bitbucket Cloud, then Data Center, on the same drivers.',
                                                 'One fleet, more than one forge, chosen per app.']))])
