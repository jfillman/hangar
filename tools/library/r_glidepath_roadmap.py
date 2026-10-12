"""Spec: Glidepath production roadmap (Oct 12, 2026), the companion to the SDLC review."""
from report import Page, chip, tick, GOOD
import lib
from lib import node, path, zone, hlab, vlab, lab, text, callout

P = Page(
    'glidepath-production-roadmap', 'Spec', 'Glidepath · Spec · Production roadmap',
    'Glidepath, from the lab to production',
    'The companion to the Glidepath SDLC review: every weakness it found sorted by cause, then nine items in three lanes, each with a test that says when it is done, and a short list of what to defer.',
    '2026-10-12',
    meta=[('Companion', '<a href="https://hangarplatform.dev/library/glidepath-sdlc-review/">Glidepath SDLC review</a>'),
          ('Effort', 'single-engineer estimates: S is days, M is one to three weeks, L is one to two months')],
    lede=('The SDLC review told me where Glidepath falls short. Reading it back, I realized some of those gaps were '
          'my lab, not the design. So this sorts every weakness the review found by cause, then orders the work in '
          'three lanes, so a production install is never blocked on a feature it doesn\'t need.'))

P.add("""
<div class="verdict info">
  <span class="stamp">Nine items · three lanes · now, next, later</span>
  <h2>Some gaps are the lab, not the design. Finish the architecture first, then build what it lacks.</h2>
  <ul>
    <li><b>T1</b> is the only item that blocks a production install, and it is small.</li>
    <li><b>T1, P1 and P2</b> complete the architecture that already exists. The other six are new design.</li>
    <li>Each lane can move on its own. Within a lane, order matters.</li>
  </ul>
</div>

<div class="verdict">
  <span class="stamp">Correction to the review</span>
  <h2>Approvals and change management: Partial, not Not enforced.</h2>
  <p>The review rated approvals and change management as not enforced. That was the lab, not the architecture. Glidepath's install requires a GitHub ruleset on every gitops repo, generated from <code>releaseGuardrails</code>, with two approvals and every gate as a required check. In an organization, one ruleset covers <code>gitops-*</code>. The lab runs on GitHub Free, where private-repo rulesets exist but are not applied.</p>
  <p>Revised rating: <b>Partial</b>. The ruleset would block, but three of its required checks always pass, and the September 27, 2026 audit found that non-release PRs and bot commits would be stuck the day it is switched on. Item T1 fixes that.</p>
</div>
""")

KIND = {'lab': ('Lab-bound', 'info'), 'fix': ('Fix before enforcing', 'warn'), 'design': ('Design gap', 'bad')}


def kchip(k):
    return chip(*KIND[k])


GAPS = [
    ('Approvals and required checks don\'t block a merge', 'lab', 'P1 · T1'),
    ('NetworkPolicy is a no-op on the dev CNI', 'lab', 'P1'),
    ('Prod reads secrets from a dev-hosted store over a NodePort', 'lab', 'P1 · P2'),
    ('Webhook arrives through a tunnel and port-forward', 'lab', 'P1'),
    ('No Prometheus on the upper cluster', 'lab', 'P1 · T3'),
    ('Required checks never report on non-release PRs', 'fix', 'T1'),
    ('Bot bootstrap commits would be refused by the ruleset', 'fix', 'T1'),
    ('<code>/retest &lt;gate&gt;</code> re-runs nothing', 'fix', 'T1'),
    ('Bypass alert not yet proven against a real bypass', 'fix', 'T1'),
    ('ITSM, QA and policy gates always pass', 'design', 'T2'),
    ('A scan that never ran counts as a pass', 'design', 'T2'),
    ('No signature check at admission', 'design', 'T2'),
    ('No secret, dependency or license scanning', 'design', 'T2'),
    ('Test secrets copied into the shared Testkube namespace', 'design', 'T2'),
    ('Extra <code>.tekton</code> files run unchecked', 'design', 'T2'),
    ('Inert canary; analysis passes on no data', 'design', 'T3'),
    ('Next environment starts when the PR opens', 'design', 'T3'),
    ('DORA has no environment, skips Ground and cloud', 'design', 'T3'),
    ('Chained stages never report to the PR; no test reports', 'design', 'D1'),
    ('Missing test file reports success', 'design', 'D1'),
    ('Push branch globs never match; no cron or manual runs', 'design', 'D2'),
    ('No build secrets or build args; cache misses Python and Go', 'design', 'D2'),
    ('Closed stage graph, fixed agents, no monorepo', 'design', 'D3'),
    ('Control plane shares a cluster with Ground', 'design', 'P2'),
    ('Kaniko archived; amd64 Go builds crash under QEMU', 'design', 'P3'),
    ('Hardcoded to GHCR and GitHub; cloud targets unverified', 'design', 'P3'),
    ('No migration or feature-flag story', 'design', 'P3'),
]
gap_rows = ''.join(f'<tr><td>{w}</td><td>{kchip(k)}</td><td class="area">{item}</td></tr>' for w, k, item in GAPS)
counts = {k: sum(1 for _, kk, _ in GAPS if kk == k) for k in KIND}

# Figure 1: three lanes by now, next, later.
W, H = 760, 412
b = ''
for i, h in enumerate(['Now', 'Next', 'Later']):
    b += text(144 + i * 236, 28, h.upper(), 8, 500, lib.MUTED, anchor='middle', mono=True, ls='0.14em')
LANES = [
    ('Trust · governance that blocks', [('Ready the ruleset to enforce', 'T1 · effort S', 'focal'),
                                        ('Make every gate real', 'T2 · effort M–L', 'propose'),
                                        ('Release on health', 'T3 · effort L', 'propose')]),
    ('Developer · the inner loop', [('Feedback on the PR', 'D1 · effort M', 'propose'),
                                    ('Triggers and build inputs', 'D2 · effort M', 'propose'),
                                    ('An extensible pipeline', 'D3 · effort L', 'propose')]),
    ('Platform · the production profile', [('Write the production profile', 'P1 · effort S', 'backend'),
                                           ('Separate the control plane', 'P2 · effort L', 'backend'),
                                           ('Portable builds and targets', 'P3 · effort L', 'propose')]),
]
for li, (name, items) in enumerate(LANES):
    y = 40 + li * 100
    b += zone(24, y, 712, 88, name)
    for i, (n, s, k) in enumerate(items):
        x = 40 + i * 236
        b += node(x, y + 28, 208, 48, n, s, k)
        if i:
            b += path([(x - 28, y + 52), (x - 1, y + 52)])
b += callout(24, 362, 'Finish the architecture first, then build what it lacks. Each lane can move on its own.')
b += lib.legend(390, [('focal', 'Blocks a production install'), ('backend', 'Completes the architecture'),
                      ('propose', 'New design')], W)
fig1 = P.fig(b, W, H, 'The roadmap at a glance',
             'Roadmap in three lanes and three horizons. Trust lane: T1 ready the ruleset to enforce now, T2 make every gate real next, T3 release on health later. Developer lane: D1 feedback on the PR now, D2 triggers and build inputs next, D3 an extensible pipeline later. Platform lane: P1 write the production profile now, P2 separate the control plane next, P3 portable builds and targets later. T1 blocks a production install; T1, P1 and P2 complete the existing architecture; the rest is new design.',
             'Nine items in three lanes. Effort is a rough single-engineer estimate: S is days, M is one to three weeks, L is one to two months.')

# Figure 2: the target production topology.
W2, H2 = 760, 536
LINK, SOFT = lib.LINK, lib.SOFT
c = zone(24, 24, 712, 96, 'GitHub organization')
c += node(40, 48, 136, 44, 'App repos', 'Ground config', 'external')
c += node(300, 48, 136, 44, 'Gitops repos', 'one per app', 'external')
c += node(460, 48, 176, 44, 'Org ruleset', '2 approvals · required checks', 'focal')
c += path([(460, 70), (439, 70)], 'accent')
c += text(460, 109, 'LAB: FREE PLAN, NOT ENFORCED', 8, 400, SOFT, mono=True, ls='0.06em')

Y = 168  # top of the three cluster zones
c += zone(24, Y, 200, 256, 'Control plane · lower', right=True)
c += zone(236, Y, 200, 256, 'Lower workloads · gap 39')
c += zone(448, Y, 288, 256, 'Upper zone', right=True)
r1, r2, r3 = Y + 32, Y + 104, Y + 176
c += node(36, r1, 176, 48, 'Tekton + PaC', 'pipelines only, no apps')
c += node(36, r2, 176, 48, 'Broker + relay', 'CDEvents, rollout facts')
c += node(36, r3, 176, 48, 'Records + DORA', 'backed up, env-labeled', 'propose')
c += node(248, r1, 176, 48, 'Argo CD · dev', 'moves off the control plane', 'propose')
c += node(248, r2, 176, 48, 'Ground environments', 'dev, previews', 'propose')
c += node(460, r1, 136, 48, 'Argo CD · prod', 'own instance')
c += node(460, r2, 136, 48, 'Admission', 'verifies signatures', 'propose')
c += node(460, r3, 136, 48, 'Staging + prod', 'canary + analysis')
c += node(612, r1, 112, 48, 'Zone store', 'secrets', 'propose')
c += node(612, r2, 112, 48, 'ESO', 'secret sync')
c += path([(336, r1 + 48), (336, r2 - 4)])
c += path([(528, r1 + 48), (528, r2 - 4)]) + path([(528, r2 + 48), (528, r3 - 4)])
c += path([(668, r2), (668, r1 + 52)])
c += path([(60, 92), (60, r1 - 4)], 'link', dashed=True) + vlab(60, 92, r1, 'webhook · ingress', LINK)
c += path([(212, r1 + 24), (230, r1 + 24), (230, 144), (330, 144), (330, 96)]) + hlab(230, 330, 144, 'release PR')
c += path([(400, 92), (400, 156), (528, 156), (528, r1 - 4)])
c += tick(414, 144) + lab(480, 138, 'pulls merged commit', GOOD)
c += path([(460, r1 + 24), (442, r1 + 24), (442, 408), (230, 408), (230, r2 + 24), (215, r2 + 24)], 'link', dashed=True)
c += hlab(230, 442, 408, 'facts · TLS ingress', LINK)
c += text(36, 440, 'LAB: SHARES A CLUSTER WITH GROUND', 8, 400, SOFT, mono=True, ls='0.06em')
c += text(248, 440, 'LAB: NOT BUILT YET', 8, 400, SOFT, mono=True, ls='0.06em')
c += text(460, 440, 'LAB: STORE OVER NODEPORT, NO PROMETHEUS', 8, 400, SOFT, mono=True, ls='0.06em')
c += callout(24, 476, 'The production profile keeps the pull-only boundary and gives every other link a real endpoint.')
c += lib.legend(508, [('backend', 'In the architecture'), ('focal', 'Org ruleset'), ('propose', 'Proposed here'),
                      ('external', 'External'), ('link-dash', 'Proposed link')], W2)
fig2 = P.fig(c, W2, H2, 'Where it lands: the target production topology',
             'A GitHub organization holds app repos, gitops repos and an org ruleset that requires two approvals and the gate checks before a gitops merge; in the lab the free plan does not enforce it. A control-plane cluster runs Tekton and Pipelines-as-Code, the broker and relay, and backed-up release records and DORA, and no apps. A separate lower workloads cluster, not built yet (gap 39), runs Argo CD for dev and the Ground environments. The upper cluster runs its own Argo CD pulling merged commits, an admission policy that verifies signatures, staging and prod with canary analysis, and External Secrets reading a secret store in its own zone. GitHub webhooks and rollout facts travel over TLS ingress instead of the lab tunnel and node ports.',
             'The target topology. Blue outlines are proposed by this roadmap; solid outlines exist in the architecture today. Grey notes under each zone say what the lab uses instead.')

ITEMS = {
    'Trust': ('governance that blocks', [
        ('T1', 'Now', 'S', 'fix', 'Ready the ruleset to enforce', [
            'Run every gate on every PR to <code>main</code>, passing at once when the head is not a <code>release-*</code> branch.',
            'Make the Crossplane GitHub App a bypass actor, scoped to the bootstrap files it writes.',
            'Match the retest comment event in each gate\'s CEL.',
            'Prove <code>detect-bypass-merge</code> against a real bypass merge in the lab.',
            'Already built: <code>hack/apply-guardrail-ruleset.sh</code> generates the ruleset from <code>releaseGuardrails</code>.'],
         'On an org with rulesets enforced, a release PR merges green, a resync PR and a Tower Config PR merge with no bypass, a bot bootstrap commit lands, and a failing gate blocks.',
         'github-ruleset.md audit 1 to 3 · gaps 15, 16, 20'),
        ('T2', 'Next', 'M–L', 'design', 'Make every gate real', [
            'ITSM: open a change from <code>change.created</code> and pass on approval. QA: read the test stage\'s recorded outcome for the digest. Policy: Conforma or Kyverno CLI over the rendered manifests.',
            'For any <code>production: true</code> environment, a missing scan fails instead of passing.',
            'Verify signatures at admission on upper clusters against the cluster\'s own Fulcio root.',
            'Add secret, dependency and license scanning to the build.',
            'Stop copying app secrets into the shared Testkube namespace; run tests where the secret already lives.',
            'Reject <code>.tekton</code> files the platform did not generate.'],
         'No entry in <code>releaseGuardrails</code> is a stub, and an unsigned image is refused by the upper cluster.',
         'governance-gate-stub.yaml · verify-sast-attestation.yaml · run-testworkflow.yaml'),
        ('T3', 'Later', 'L', 'design', 'Release on health', [
            'Scrape ingress metrics wherever canaries run, and make an analysis with no data fail.',
            'Ship a default multi-step canary with an error-rate analysis.',
            'Start the next environment from the release record\'s Healthy fact instead of <code>change.created</code>.',
            'On a failed analysis, abort and open the rollback PR automatically. It stays gated.',
            'Label DORA by environment, count Ground and cloud deploys, and start lead time at the first commit.'],
         'A bad image in staging aborts itself and the prod release PR never opens.',
         'airframe/analysis · rollout.yaml · dora-exporter'),
    ]),
    'Developer': ('the inner loop', [
        ('D1', 'Now', 'M', 'design', 'Feedback on the PR', [
            'Post every chained stage as a check run on the app commit, using the broker\'s per-repo token.',
            'Parse JUnit and coverage from unit tests and Testkube into the check summary.',
            'A test step with no test file fails, or reports neutral, instead of passing.',
            'Run PR pipelines on <code>opened</code> when the label is already there, and give each preview an ingress URL.'],
         'A PR shows build, test and preview checks with test counts and a link to the running preview.',
         'gap 7 · run-tests.yaml · ephemeral-envs.yaml'),
        ('D2', 'Next', 'M', 'design', 'Triggers and build inputs', [
            'Glob matching for push branches, reusing the regex builder <code>branch.created</code> already has.',
            'Cron and manual runs: a PaC incoming webhook, and a Run button in Tower.',
            'Path filters on PR and tag events.',
            'Build secrets and build args from the app\'s own secrets.',
            'Dependency cache for Python and Go; pin agent images by digest.'],
         'A <code>release/*</code> branch flow, a nightly job and a build against a private package registry all work from <code>cicd.yaml</code>.',
         'deliver-onboarding-files.yaml:498 · build-source.yaml'),
        ('D3', 'Later', 'L', 'design', 'An extensible pipeline', [
            'Named extension points (pre-build, post-test, pre-release) that run a team\'s container under a fixed contract and the stage\'s identity.',
            'Bring-your-own agent image from an allow-listed, signed registry.',
            'Monorepo support: app path, build context and image per app.',
            'Matrix test runs and a retry budget.'],
         'A team adds a custom step with no platform change, and two apps build from one repo.',
         'ADR-0017 · stage-preflight.yaml'),
    ]),
    'Platform': ('the production profile', [
        ('P1', 'Now', 'S', 'lab', 'Write the production profile', [
            'An ADR naming each lab substitution and what production requires: an enforced org ruleset with two approvals, an enforcing CNI, a routable secret store per zone, TLS ingress for the relay and webhooks, Prometheus on upper clusters.',
            'An alert when no PaC event has arrived in N hours.',
            'A conformance check, as a script or a Tower page, that reports which profile a cluster meets.'],
         'An installer can tell a lab install from a production one by running one check.',
         'security.md "Known, accepted gaps" · infisical-nodeport.yaml · gap 8'),
        ('P2', 'Next', 'L', 'lab', 'Separate the control plane', [
            'Ground environments on a lower workloads cluster, so the control-plane cluster runs no apps.',
            'Upper clusters read secrets from a store in their own zone, never from dev.',
            'Back up release records, or move them off 14-day ConfigMaps.'],
         'Losing the dev workloads cluster leaves pipelines, release records and prod secrets untouched.',
         'ADR-0024 "Future" · gap 39'),
        ('P3', 'Later', 'L', 'design', 'Portable builds and targets', [
            'Replace kaniko with rootless BuildKit or Buildah, and cross-compile natively instead of under QEMU.',
            'Take the registry and git host from config, not from <code>ghcr.io</code> and <code>api.github.com</code> in Task scripts.',
            'Verify ECS, Lambda and Container Apps live, with OIDC federation instead of static keys, and give them release records.',
            'Document expand/contract migrations as a gated Job, and add an OpenFeature integration.'],
         'The same app builds to a non-GHCR registry and releases to ECS with a release record.',
         'gaps 33, 36 to 38 · build-image.yaml'),
    ]),
}
work = ''
for lane, (sub, items) in ITEMS.items():
    work += f'<h3>{lane} <span class="eyebrow">· {sub}</span></h3><div class="cards">'
    for iid, when, effort, k, title, bullets, done, refs in items:
        work += (f'<div class="card"><span class="eyebrow">{iid} · {when} · effort {effort}</span><h3>{title}</h3>'
                 f'<p>{kchip(k)}</p><ul class="plain">' + ''.join(f'<li>{x}</li>' for x in bullets) + '</ul>'
                 f'<p class="ev"><b>Done when</b>{done}</p><p class="note">{refs}</p></div>')
    work += '</div>'

P.add(f"""
<section>
  <h2>Three kinds of gap</h2>
  <div class="prose"><p>Each weakness from the review falls into one of three groups, and each group needs different work.</p></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">{counts['lab']} weaknesses</span><h3>Lab-bound</h3><p>Specified in the architecture; the lab substitutes something weaker. The work is to write it down and verify it.</p></div>
    <div class="card"><span class="eyebrow">{counts['fix']} weaknesses</span><h3>Fix before enforcing</h3><p>In the architecture, but would break the day the ruleset is enforced.</p></div>
    <div class="card"><span class="eyebrow">{counts['design']} weaknesses</span><h3>Design gap</h3><p>Missing whatever the environment. Needs new design.</p></div>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Weakness from the review</th><th>Kind</th><th>Roadmap item</th></tr></thead>
    <tbody>{gap_rows}</tbody>
  </table></div>
</section>

<section>
  <h2>The roadmap at a glance</h2>
  <div class="prose"><p>Three lanes that can move independently, each with three horizons. Within a lane, order matters: T2 adds required checks, so T1 must first make sure every check reports. Across lanes, P1 writes down the profile that T1 and P2 verify against.</p></div>
  {fig1}
</section>

<section>
  <h2>The work, item by item</h2>
  <p class="note">Each item names the review findings it closes and a test that says when it is done.</p>
  {work}
</section>

<section>
  <h2>Where it lands</h2>
  <div class="prose"><p>The production profile keeps what the review found sound, Argo CD on each upper cluster pulling merged commits, and replaces each lab shortcut with a real endpoint.</p></div>
  {fig2}
</section>

<section>
  <h2>What to defer</h2>
  <div class="prose"><p>Hangar's own cost essay warns that operating 47 tools is the platform's real limit. For one engineer, these can wait until a second team asks:</p></div>
  <ul class="plain">
    <li><b>D3 extension points and monorepo support.</b> They widen the contract every future change has to keep. Build them for a real team's need, not ahead of it.</li>
    <li><b>A second git host.</b> Take the registry from config in P3, but keep GitHub until there is a reason to leave it.</li>
    <li><b>Azure Container Apps.</b> Verify ECS first. A second cloud target doubles the untested surface.</li>
    <li><b>A real ITSM integration</b> beyond a thin adapter, until a team's change process needs one. Until then, mark the gate optional instead of always-pass.</li>
  </ul>
  <p class="note">Sources: the <a href="https://hangarplatform.dev/library/glidepath-sdlc-review/">Glidepath SDLC review</a>, <code>glidepath/docs/admin/github-ruleset.md</code> (the September 27, 2026 audit), the <code>security.md</code> known gaps, <code>known-gaps.md</code>, ADR-0024, and Apron's Infisical NodePort notes. Effort estimates are judgement, not measurement. The lab-bound items come from what the architecture already specifies; nothing here was verified on an enforcing GitHub plan.</p>
</section>
""")
