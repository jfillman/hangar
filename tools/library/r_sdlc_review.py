"""Review: Glidepath against the everyday software lifecycle (Oct 12, 2026)."""
from report import Page, chip, tick, GOOD
import lib
from lib import node, path, zone, hlab, vlab, lab, text, callout, stopx

P = Page(
    'glidepath-sdlc-review', 'Review', 'Glidepath · Review · The software lifecycle',
    'Glidepath against the everyday software lifecycle',
    'A CI/CD review of Glidepath against what teams expect from GitHub Actions, GitLab CI or a commercial delivery platform: the change road as built, fifteen workflows rated, strengths, weaknesses, and five things to do next, in order.',
    '2026-10-12',
    meta=[('Basis', 'code, ADRs and docs of glidepath, tower, airframe, apron and hangar'),
          ('Scale', 'in build since Aug 12, 2026 · 1 engineer · 2 clusters · 25 ADRs · 42 logged gaps'),
          ('Companion', '<a href="https://hangarplatform.dev/library/glidepath-production-roadmap/">Glidepath production roadmap</a>')],
    lede=('I wanted to know how Glidepath holds up against the delivery tools most teams already use, so I read it '
          'the way a reviewer would: the code, the ADRs and the docs, across every repo it touches. Each finding below '
          'says whether it holds today, so a design that is built is never mistaken for one that is enforced.'))

P.add("""
<div class="verdict">
  <span class="stamp">Strong merge to prod · governance advises</span>
  <h2>Strong on the road from merge to production, by design. Thin on the developer's inner loop. Most of its governance advises today rather than enforces.</h2>
  <ul>
    <li>The pull-only boundary between clusters is sound: nothing on dev holds prod credentials, and prod only changes from a merged commit.</li>
    <li>Gates, approvals and test results exist on paper, but on GitHub Free nothing stops a change that skips or fails them.</li>
    <li>Everything that makes delivery observable and governable runs on one dev cluster.</li>
  </ul>
</div>
""")

# Figure 1: the change road, as built.
W, H = 760, 516
ACC = lib.ACC


def mark(x, y, lines, ok=False):
    """A tick or an amber X, with one or two lines of mono text beside it."""
    s = tick(x, y) if ok else stopx(x, y)
    for i, ln in enumerate(lines):
        s += text(x + 10, y + 3 + i * 12, ln.upper(), 8, 500, GOOD if ok else ACC, mono=True, ls='0.06em')
    return s


b = zone(24, 24, 712, 128, 'Inner loop · app repo · each stage starts on the last one\'s CDEvent')
row = [('Push or PR', 'PaC webhook', 'external'), ('build', 'kaniko · two arches', 'input'),
       ('test', 'Testkube, 10 min cap', 'input'), ('deploy', 'bot commit to main', 'input'),
       ('Running in dev', 'Argo Rollout', 'backend')]
for i, (n, s, k) in enumerate(row):
    x = 40 + i * 140
    b += node(x, 48, 116, 52, n, s, k)
    if i:
        b += path([(x - 24, 74), (x - 1, 74)])
b += mark(186, 120, ['PR check posts here'], ok=True)
b += mark(326, 120, ['No PR check, no reports'])
b += mark(326, 136, ['No test file = pass'])
b += mark(606, 120, ['Canary: one 100% step'])

b += path([(520, 100), (520, 172), (100, 172), (100, 212)])
b += hlab(100, 520, 172, 'service.deployed')

b += zone(24, 188, 712, 232, 'Release · gitops repo · one PR per upper environment', right=True)
rel = [('release', 'opens the PR', 'input'), ('Gitops PR', 'same image digest', 'backend'),
       ('Real gates', 'sast scan prov sbom', 'backend'), ('Human review', '2 approvals asked', 'backend'),
       ('Upper Argo CD', 'pulls merged commit', 'backend')]
for i, (n, s, k) in enumerate(rel):
    x = 40 + i * 140
    b += node(x, 212, 116, 52, n, s, k)
    if i:
        b += path([(x - 24, 238), (x - 1, 238)])
b += node(180, 316, 116, 48, 'Next env PR', 'starts at once', 'input')
b += node(320, 316, 116, 48, 'Stub gates', 'itsm · qa · policy', 'optional')
b += node(460, 316, 116, 48, 'Bypass alert', 'Slack, after merge', 'backend')
# change.created starts the next environment as soon as the PR opens.
b += path([(240, 264), (240, 312)], 'accent', dashed=True) + vlab(240, 264, 312, 'change.created', ACC, side='l')
# Stub gates run as checks beside the real ones; the bypass alert fires after merge.
b += path([(308, 238), (308, 340), (318, 340)], dashed=True)
b += path([(436, 340), (448, 340), (448, 248), (457, 248)], dashed=True)
b += path([(588, 238), (588, 340), (578, 340)], dashed=True)
b += mark(466, 282, ['Not enforced on', 'GitHub Free'])
b += mark(606, 282, ['Pull-only boundary', 'holds'], ok=True)
b += mark(186, 382, ['Not tied to', 'staging health'])
b += mark(326, 382, ['Always pass'])

b += callout(24, 448, 'The release path is designed right. Today the pull-only boundary')
b += callout(24, 468, 'enforces it, and the checks only advise.')
ly = 494
b += lib.legend(ly, [('input', 'Stage'), ('backend', 'Check or system'), ('optional', 'Stub, always passes'),
                     ('muted-dash', 'After the fact')], W)
b += stopx(551, ly + 6) + text(562, ly + 9, 'Does not hold', 8, 400, lib.MUTED, mono=True)
b += tick(648, ly + 6) + text(658, ly + 9, 'Holds today', 8, 400, lib.MUTED, mono=True)
fig1 = P.fig(b, W, H, 'The change road, as built',
             'In the app repo, a push or PR starts build, test and deploy to dev, each stage chained by CDEvents. Only the build stage posts a PR check; test results never reach the PR and a missing test passes; the dev canary is a single 100 percent step. A service.deployed event starts the release stage, which opens a PR on the gitops repo with the same image digest. Real gates and stub gates that always pass run as checks, then a human review that GitHub Free does not enforce; a bypass alert fires only after merge. change.created starts the next environment as soon as the PR opens. The pull-only boundary, Argo CD on the upper cluster pulling the merged commit, holds.',
             'Where each guarantee holds. Amber marks the places where a check exists on paper but nothing stops a change that skips or fails it.')

# Figure 2: where the control plane lives.
W2, H2 = 760, 472
c = node(500, 24, 140, 48, 'GitHub', 'app + gitops repos', 'external')
c += zone(24, 116, 436, 240, 'The dev cluster · lower zone · control plane', right=True)
c += zone(476, 116, 260, 240, 'The prod cluster · upper zone', right=True)
c += node(40, 176, 124, 48, 'Tekton + PaC', 'every pipeline run')
c += node(180, 176, 124, 48, 'Broker + relay', 'CDEvents, facts')
c += node(320, 176, 124, 48, 'Argo CD · dev', 'Ground environments')
c += node(180, 260, 124, 48, 'Records + DORA', 'ConfigMaps, exporter')
c += node(320, 260, 124, 48, 'Infisical', 'secrets for dev + prod')
c += node(492, 176, 124, 48, 'Argo CD · prod', 'own instance')
c += node(492, 260, 124, 48, 'Staging + prod', 'Argo Rollouts')
c += node(628, 260, 92, 48, 'ESO', 'secret sync')
c += path([(500, 48), (102, 48), (102, 172)], 'accent', dashed=True) + hlab(102, 500, 48, 'webhook via tunnel', ACC)
c += path([(520, 72), (520, 172)])
c += tick(534, 94) + lab(602, 88, 'pulls merged commit', GOOD)
c += path([(554, 224), (554, 256)])
c += path([(492, 200), (468, 200), (468, 156), (242, 156), (242, 172)], dashed=True) + hlab(242, 468, 156, 'rollout facts')
c += path([(242, 224), (242, 256)])
c += path([(674, 308), (674, 336), (382, 336), (382, 312)], 'accent') + hlab(382, 674, 336, 'plain HTTP NodePort', ACC)
c += callout(24, 390, 'One dev cluster runs every control-plane job. Prod keeps serving without it,')
c += callout(24, 412, 'but loses release feedback, records, metrics and secret refresh.')
c += lib.legend(444, [('backend', 'Component'), ('external', 'External'), ('accent', 'Fragile link'),
                      ('muted', 'Pull, sound'), ('muted-dash', 'Feedback')], W2)
fig2 = P.fig(c, W2, H2, 'Where the control plane lives',
             'The dev cluster runs Tekton and Pipelines-as-Code, the broker and relay, Argo CD for Ground environments, release records and DORA, and Infisical, which also serves prod secrets. GitHub webhooks reach Tekton through a temporary tunnel. The prod cluster runs its own Argo CD, which pulls merged commits from GitHub, the staging and prod workloads, and External Secrets, which fetches secrets from Infisical on the dev cluster over a plain-HTTP NodePort. Rollout facts flow back from prod Argo CD to the relay on dev.',
             'The dev cluster as a single point of failure. The webhook tunnel once died for about 19 hours with no alert (known gap 8).')

RATINGS = [
    ('Trunk-based: push to main, deploy to dev', 'Good', 'ok', 'Path filters, multi-arch builds, unit tests, then a dev deploy that waits until the Rollout is healthy.'),
    ('Tag-driven release', 'Good', 'ok', '<code>tagPattern</code> regex; the version comes from the tag.'),
    ('PR validation', 'Partial', 'warn', 'The PR build gets a native check. Test, deploy and scan results never reach the PR. Unit tests return pass or fail only: no JUnit, no coverage.'),
    ('PR preview environments', 'Partial', 'warn', 'A real ApplicationSet with a TTL sweep. Needs a label, skips <code>opened</code>, has no URL (port-forward only).'),
    ('Promotion dev to staging to prod', 'Partial', 'warn', 'Gated PR per environment, but the next one starts when the PR opens, not when staging is healthy.'),
    ('Rollback', 'Partial', 'warn', 'A gated PR to one of the last five healthy releases. Manual, minutes to tens of minutes; live verification still pending.'),
    ('DORA and delivery insight', 'Partial', 'warn', 'No environment label, Ground and cloud deploys not counted, lead time starts at build. MTTR is marked experimental.'),
    ('Integration and e2e tests', 'Weak', 'warn', 'Testkube with a 10 minute cap. No matrix, no retries, no environment URL passed in. A missing test reports success.'),
    ('Release branches and GitFlow', 'Weak', 'warn', 'A push trigger matches the branch exactly, so <code>branch: release/*</code> on push never fires.'),
    ('Non-Kubernetes targets', 'Experimental', 'info', 'ECS, Lambda and Azure Container Apps are render-tested. The one live ECS run failed.'),
    ('Approvals and change management', 'Not enforced', 'bad', 'GitHub Free does not enforce rulesets on private repos. The bypass alert fires after merge. ITSM, QA and policy gates always pass.'),
    ('Progressive delivery, auto-rollback', 'Missing', 'bad', 'Default canary is one <code>setWeight: 100</code> step. Analysis needs metrics nobody scrapes, and a query with no data passes.'),
    ('Hotfix track, freezes, scheduled releases', 'Missing', 'bad', 'Nothing in the schema or the catalog.'),
    ('Monorepo', 'Missing', 'bad', 'Repo name must equal app name, build context is the repo root, one image per app.'),
    ('Cron, manual dispatch, ChatOps', 'Missing', 'bad', 'No triggers for them. <code>/retest &lt;gate&gt;</code> re-runs nothing (gap 20).'),
    ('Feature flags and DB migrations', 'Missing', 'bad', 'No flag system. Migrations are Helm pre-upgrade Jobs with no gating and no rollback path.'),
]
rating_rows = ''.join(f'<tr><td class="area">{w}</td><td>{chip(r, t)}</td><td>{why}</td></tr>' for w, r, t, why in RATINGS)

STRENGTHS = [
    ('ADR-0017 · cicd.schema.json', 'A real paved road', 'One validated file, scaffolded rather than hand-written. Developers never write Tekton, and <code>preflight</code> rejects a bad config before anything runs.'),
    ('image-signing.md', 'Supply chain beyond the norm', 'Tekton Chains signs keylessly through a self-hosted Fulcio and Rekor, Conforma checks the provenance, SBOMs are cosign attestations, and Semgrep fails closed when on.'),
    ('ADR-0005 · ADR-0004', 'Sound GitOps trust', 'Each upper cluster runs its own Argo CD and pulls. The GitHub App key stays in one namespace, and a broker mints tokens for one repo at a time.'),
    ('glidepath-relay', 'Observable by design', 'One OTel trace per flow across separate PipelineRuns, CDEvents throughout, a release state machine fed by Rollout facts, and stall detectors.'),
    ('tower/docs/deployments.md', 'Day-2 tooling in Tower', 'Plain-language deployment diagnosis, Rollout controls, rollback as a PR, config edits as PRs, and a recorded break-glass shell anchored in Rekor.'),
    ('known-gaps.md', 'A candid engineering record', '25 ADRs, a known-gaps log with evidence for each entry, stubs labelled as stubs, and live runs kept apart from render-only checks.'),
]
strengths = ''.join(f'<div class="card"><span class="eyebrow">Holds · {src}</span><h3>{t}</h3><p>{body}</p></div>' for src, t, body in STRENGTHS)

WEAK = [
    ('Enforcement', ['Required checks and approvals do not block a merge on GitHub Free.',
                     'Security gates are opt-in and default off. The release SAST gate treats a scan that never ran as a pass.',
                     'No secret, dependency or license scanning.']),
    ('CI flexibility', ['A fixed four-stage graph: no custom steps, no matrix, no conditional jobs.',
                        'Build images limited to Node, Java, Python and Go, on floating tags.',
                        'No build secrets or custom build args, so private package registries are out.',
                        'The dependency cache covers npm, yarn and Maven only.']),
    ('Feedback', ['Chained stage results go to Slack, Backstage and Tempo, never to the PR.',
                  'No test reports, no coverage, no flaky-test handling.']),
    ('Lock-in and drift', ['Hardcoded to GitHub, GHCR and a <code>main</code> default branch.',
                           'The build relies on kaniko, whose upstream project is archived. amd64 Go builds crash under emulation.',
                           'The guardrail list, the ruleset and the toolbox schema are kept in sync by hand (gap 35 broke every <code>deploy.target</code> user).']),
    ('Isolation', ['Test runs copy the app\'s secrets into the shared <code>testkube</code> namespace, next to developer-written TestWorkflow YAML.',
                   'Extra <code>.tekton/*.yaml</code> files in an app repo would run as the pipeline identity, outside the platform\'s control.']),
    ('Operations', ['The dev cluster carries Tekton, the broker, release records, DORA and prod\'s secrets (Figure 2).',
                    'Tower\'s per-action authorization is two weeks old and lives in a separate repo.']),
]
weak = ''.join(f'<div class="card"><span class="eyebrow">Gap</span><h3>{t}</h3><ul class="plain">'
               + ''.join(f'<li>{li}</li>' for li in items) + '</ul></div>' for t, items in WEAK)

NEXT = [
    ('Make the gates real before adding features', 'Move to a GitHub plan that enforces rulesets, or add a pre-merge admission check or merge bot. Generate the ruleset from <code>releaseGuardrails</code>. Fail Flight releases when gate evidence is missing.'),
    ('Close the loop on the PR', 'Post every chained stage as a GitHub check, parse JUnit and coverage, and fail the test stage when no test exists.'),
    ('Turn on progressive delivery', 'Scrape ingress metrics, make an analysis with no data fail, ship a default multi-step canary, and start production on staging health instead of PR open.'),
    ('Fill the everyday CI gaps', 'Glob matching on push, cron and manual triggers, PR path filters, build secrets and args, monorepo support, and a sanctioned custom-step hook.'),
    ('De-risk the platform itself', 'Split the control plane from the dev workload cluster, give prod its own secrets path, add a CI check that the schema matches the toolbox image, and plan a BuildKit or Buildah replacement for kaniko.'),
]
nxt = ''.join(f'<div class="row"><h3>{i}. {t}</h3><p>{body}</p></div>' for i, (t, body) in enumerate(NEXT, 1))

P.add(f"""
<section>
  <h2>The change road, as built</h2>
  <div class="prose"><p>A developer writes one <code>cicd.yaml</code>. Pipelines-as-Code starts the first stage from a GitHub webhook, and every later stage starts on the previous stage's CDEvent through a broker that authenticates with the pod's own ServiceAccount token. Ground environments get a direct bot commit. Flight environments only change when a PR on <code>gitops-&lt;app&gt;</code> merges and that cluster's Argo CD pulls it.</p></div>
  {fig1}
</section>

<section>
  <h2>Typical workflows, rated</h2>
  <p class="note">Against what teams usually expect from GitHub Actions, GitLab CI or a commercial delivery platform.</p>
  <div class="tbl"><table>
    <thead><tr><th>Workflow</th><th>Support</th><th>Why</th></tr></thead>
    <tbody>{rating_rows}</tbody>
  </table></div>
  <p class="note">Revised the same day: the <a href="https://hangarplatform.dev/library/glidepath-production-roadmap/">production roadmap</a> moved approvals and change management from Not enforced to Partial. The install already requires a ruleset on every gitops repo; it's the lab's GitHub Free plan that leaves it unenforced.</p>
</section>

<section>
  <h2>Where the control plane lives</h2>
  <div class="prose"><p>The pull model between clusters is sound: nothing on dev holds prod credentials, and prod only changes from a merged commit. Everything else that makes delivery observable and governable runs on the dev cluster.</p></div>
  {fig2}
</section>

<section>
  <h2>Strengths</h2>
  <div class="cards">{strengths}</div>
</section>

<section>
  <h2>Weaknesses</h2>
  <div class="cards">{weak}</div>
</section>

<section>
  <h2>What to do next, in order</h2>
  <div class="track">{nxt}</div>
</section>

<section>
  <h2>How this was read</h2>
  <div class="prose"><p>I read code, ADRs and docs across <code>glidepath</code>, <code>tower</code>, <code>airframe</code>, <code>apron</code> and <code>hangar</code>. The highest-impact findings (push-branch matching, Testkube secret copying, the always-pass gates, the inert canary, the DORA labels) were checked directly in source. Nothing was run against a cluster; live behaviour comes from the repos' own verification notes.</p>
  <p>Glidepath is about two months old, and its September 27, 2026 architecture review withholds production approval. So read the gaps as a roadmap, not a verdict on the design.</p></div>
</section>
""")
