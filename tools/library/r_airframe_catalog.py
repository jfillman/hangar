"""Spec: the Airframe service catalog as it stood on Sep 20, 2026."""
from report import Page, chip, tick, esc
import lib
from lib import node, path, zone, hlab, vlab, lab, text, callout, legend

P = Page(
    'airframe-service-catalog', 'Architecture', 'Airframe · Architecture · Service catalog',
    'Airframe, the service catalog under Hangar',
    'A snapshot of Airframe on September 20, 2026: how a commit becomes a running service, the eleven XRDs and how they compose, the three tiers, what each Composition calls, and what was not yet live.',
    '2026-09-20',
    meta=[('Snapshot', 'September 20, 2026'),
          ('Living doc', '<a href="https://hangarplatform.dev/docs/hangar/service-catalog-design/">Service catalog design</a>')],
    lede=('Airframe is the Crossplane-based service catalog behind Hangar. Eleven XRDs turn a git commit into a running '
          'service that is onboarded to CI/CD and has its secrets, without any cluster ever holding credentials for another '
          'cluster\'s API. I drew this on September 20, 2026 to see the wiring underneath: what each catalog object takes in '
          'and gives back, how the pieces compose, and what actually moves when someone asks for a service. It\'s a snapshot. '
          'The design doc is the living version, and it has moved on since.'))

P.add("""
<div class="verdict info">
  <span class="stamp">Snapshot · Sep 20, 2026</span>
  <h2>Everything routes through git.</h2>
  <ul>
    <li>Airframe has no API server and no webhook receiver. A request to the catalog is a commit: a manifest written into a tenant's <code>xr-requests/</code> folder.</li>
    <li>Argo CD is the only thing watching that commit, and Crossplane is the only thing allowed to act on what Argo CD syncs. Repos, CI/CD onboarding, secrets and the running workload are all side effects of that one XR existing on a cluster.</li>
    <li>The engine stays on one dev cluster, because its only two levers, provider-upjet-github and a GitOps commit, never need a credential to any other cluster's API.</li>
  </ul>
</div>
""")

# Figure 1: the request architecture.
W, H = 760, 400
b = node(24, 60, 136, 56, 'Developer', 'Tower · Backstage', 'input')
b += node(224, 60, 160, 56, 'GitHub', 'tenants · gitops · src', 'store')
b += node(440, 60, 128, 56, 'Argo CD', 'platform + apps', 'backend')
b += node(616, 60, 120, 56, 'Target cluster', 'Rollout · Service', 'backend')
b += node(224, 220, 160, 56, 'Tekton CI/CD', 'Glidepath · PaC', 'backend')
b += node(440, 220, 128, 56, 'Airframe engine', 'XRDs, Compositions', 'focal')
b += node(620, 220, 116, 56, 'Infisical', 'provider · ESO', 'external')
b += path([(160, 88), (220, 88)]) + hlab(160, 220, 88, 'commit XR')
b += path([(384, 80), (436, 80)]) + hlab(384, 436, 80, 'sync')
b += path([(568, 80), (612, 80)], 'accent') + hlab(568, 612, 80, 'deploy', lib.ACC)
b += path([(536, 116), (536, 216)]) + vlab(536, 116, 216, 'apply')
b += path([(460, 216), (460, 140), (360, 140), (360, 120)], 'link') + hlab(360, 460, 140, 'write', lib.LINK)
b += path([(568, 248), (616, 248)], 'link') + hlab(568, 620, 248, 'secrets', lib.LINK)
b += path([(320, 116), (320, 216)], 'link') + vlab(320, 116, 216, 'onboard', lib.LINK)
b += path([(256, 220), (256, 120)], dashed=True) + vlab(256, 120, 220, 'image PR', side='l')
b += path([(678, 216), (678, 120)], dashed=True) + vlab(678, 120, 216, 'inject', side='l')
b += callout(24, 324, 'No call ever reaches a second cluster\'s API. Cross-cluster effects are commits.')
b += legend(360, [('focal', 'engine'), ('backend', 'control plane'), ('store', 'git'), ('external', 'external'),
                  ('input', 'human'), ('link', 'GitHub call'), ('accent', 'deploy'), ('muted-dash', 'async')], W)
fig1 = P.fig(b, W, H, 'Everything routes through git',
             'A developer commit lands in GitHub, Argo CD syncs it to the Crossplane-based Airframe engine, which writes back to GitHub and provisions Infisical secrets. GitHub onboarding triggers Tekton CI/CD, and Argo CD deploys the resulting release to the target cluster.',
             'Every cluster runs two Argo CD instances: argocd-platform, cluster-admin, which installs the catalog itself, and argocd-apps, app-owner facing, with one AppProject per app. Their watched repos never overlap.')

# Figure 2: the catalog entity graph.
W2, H2 = 760, 330
c = text(24, 44, 'DevClusterReady · CicdOnboarded', 9, 400, lib.MUTED, mono=True)
c += node(24, 52, 240, 56, 'App stack (5 XRDs)', 'NodeJS · Spring · Go · Python · Infra', 'focal')
c += text(344, 44, 'ClusterReady · WorkloadDeployed', 9, 400, lib.MUTED, mono=True)
c += node(344, 52, 200, 56, 'ApplicationEnvironment', 'appName · cluster · env', 'backend')
c += node(24, 188, 240, 56, 'TektonCICD', 'composed only; GitHub API', 'backend')
c += text(24, 262, 'CicdOnboarded', 9, 400, lib.MUTED, mono=True)
c += node(344, 188, 200, 56, 'SecretStore', 'per env, or shared', 'backend')
c += text(344, 262, 'Ready', 9, 400, lib.MUTED, mono=True)
for i, (n, s) in enumerate([('Redis', 'size, persistence'), ('SLO', 'objective, indicator'), ('RolloutWatch', 'rolloutPhase')]):
    y = 36 + i * 60
    c += node(616, y, 120, 44, n, s, 'backend')
    c += path([(544, 80), (588, 80), (588, y + 22), (612, y + 22)])
c += lab(676, 208, 'attaches · 1:N')
c += path([(264, 80), (340, 80)]) + hlab(264, 340, 80, 'has envs')
c += text(270, 96, '1', 9, 400, lib.MUTED, mono=True) + text(330, 96, 'N', 9, 400, lib.MUTED, mono=True)
c += path([(144, 108), (144, 184)], 'accent') + vlab(144, 108, 184, 'composes · 1:1', lib.ACC)
c += path([(232, 108), (232, 128), (400, 128), (400, 184)], 'link', dashed=True) + hlab(232, 400, 128, 'commits', lib.LINK)
c += path([(480, 108), (480, 184)], 'link', dashed=True) + vlab(480, 108, 184, 'commits', lib.LINK)
c += legend(300, [('focal', 'aggregate root'), ('backend', 'XRD'), ('accent', 'direct composition'),
                  ('link-dash', 'indirect: xr-requests commit')], W2)
fig2 = P.fig(c, W2, H2, 'Eleven XRDs, one composition graph',
             'An app stack XRD composes a TektonCICD child directly and requests a SecretStore indirectly. An ApplicationEnvironment belongs to an app, also requests its own SecretStore, and is where Redis, SLO and RolloutWatch attach.',
             'The small mono text above or below a box is its published status. Anything that has to land on a different cluster\'s API is requested by a commit, never composed directly.')

# Figure 3: request to running service.
W3, H3 = 760, 520
cols = [('Developer', 'input'), ('GitHub', 'store'), ('Airframe', 'focal'), ('Argo CD', 'backend'), ('Target cluster', 'backend')]
X = [92, 236, 380, 524, 668]
d = ''
for (n, k), x in zip(cols, X):
    d += path([(x, 60), (x, 470)], dashed=True, marker=False, w=0.8)
    d += node(x - 60, 24, 120, 36, n, None, k)
rows = [  # (from, to, label, colour, dashed)
    (0, 1, 'commit xr-requests/*', 'link', False),
    (1, 3, 'sync detects XR', 'muted', False),
    (3, 2, 'apply XR', 'muted', False),
    None,  # compose TektonCICD child
    (2, 1, 'write repos and files', 'link', False),
    'status1',
    (1, 3, 'sync release', 'muted', False),
    (3, 4, 'apply Rollout · Service', 'accent', False),
    (1, 3, 'image PR merged, later', 'open', True),
    (3, 4, 're-sync image', 'accent', True),
    'status2',
]
for i, r in enumerate(rows):
    y = 100 + i * 34
    if r is None:
        d += path([(380, y - 6), (412, y - 6), (412, y + 8), (384, y + 8)], 'accent')
        d += lab(492, y - 5, 'compose TektonCICD child')
    elif r == 'status1':
        d += f'<rect x="394" y="{y - 8}" width="196" height="16" fill="{lib.PAPER}"/>' + tick(388, y) + text(398, y + 4, 'DevClusterReady · CicdOnboarded', 10, 500, lib.INK, mono=True)
    elif r == 'status2':
        d += tick(676, y) + text(660, y + 4, 'WorkloadDeployed', 10, 500, lib.INK, anchor='end', mono=True)
    else:
        a, z, t, col, da = r
        x1, x2 = X[a], X[z]
        x2e = x2 - 4 if x2 > x1 else x2 + 4
        d += path([(x1, y), (x2e, y)], col, dashed=da) + hlab(x1, x2, y, t, lib.LINK if col == 'link' else (lib.ACC if col == 'accent' else lib.SOFT))
d += legend(496, [('link', 'GitHub write or commit'), ('muted', 'sync or apply'), ('accent', 'deploy'),
                  ('muted-dash', 'async, later')], W3)
fig3 = P.fig(d, W3, H3, 'From request to running service',
             'A developer commits an XR to GitHub; Argo CD applies it to the Airframe engine, which composes TektonCICD, writes repos and files back to GitHub and marks itself ready. Argo CD syncs the release to the target cluster, and once a later image PR merges, the workload is marked deployed.',
             'Four status conditions gate the handoff, DevClusterReady, CicdOnboarded, ClusterReady and WorkloadDeployed, and each turns True only once its real precondition is met, not on a timer.')

KINDS = [
    ('NodeJSApplication', 'app stack', 'Bootstrap', 'devCluster *, description, nodeVersion (18|20|22), packageManager (npm|pnpm|yarn), port, visibility', 'DevClusterReady, CicdOnboarded, Ready', 'TektonCICD (direct) · SecretStore shared (xr-requests)'),
    ('SpringBootApplication', 'app stack', 'Bootstrap', 'devCluster *, description, javaVersion (17|21), buildTool (maven|gradle), groupId, port, visibility', 'DevClusterReady, CicdOnboarded, Ready', 'TektonCICD (direct) · SecretStore shared'),
    ('GoApplication', 'app stack', 'Bootstrap', 'devCluster *, description, goVersion (1.22 to 1.24), port, visibility (module path derived, not typed)', 'DevClusterReady, CicdOnboarded, Ready', 'TektonCICD (direct) · SecretStore shared'),
    ('PythonApplication', 'app stack', 'Bootstrap', 'devCluster *, description, pythonVersion (3.11 to 3.13), packageManager (pip|poetry|uv), port, visibility', 'DevClusterReady, CicdOnboarded, Ready', 'TektonCICD (direct) · SecretStore shared'),
    ('InfraService', 'app stack', 'Bootstrap', 'devCluster *, description, visibility. NodeJSApplication without the src repo and boilerplate, for shared infra with no app code', 'DevClusterReady, CicdOnboarded, Ready', 'TektonCICD type: infra · SecretStore shared'),
    ('ApplicationEnvironment', '', 'Bootstrap', 'appName *, cluster * (live-gated: type=upper, crossplaneReady), env *, configMapGenerator', 'ClusterReady, WorkloadDeployed, Ready', 'SecretStore per env · a Usage blocks parent deletion'),
    ('TektonCICD', '', 'Bootstrap-adjacent', 'appName *, type (app|infra), registerPipelinesAsCode, gitopsRepoUrl *, appRepoUrl *, devCluster *', 'DevClusterReady, CicdOnboarded', 'Composed only, never created by a developer directly'),
    ('SecretStore', '', 'Attached (auto)', 'appRef.name *, cluster *, environmentSlug (default shared)', 'Ready', 'Requested only, via xr-requests, never created by a developer directly'),
    ('Redis', '', 'Attached', 'environmentRef.name * (auto-stamped), size (small|medium|large), persistence', 'Ready', 'Rendered by the airframe-application chart from a components: block'),
    ('SLO', '', 'Attached', 'environmentRef.name *, service *, objective * (0 to 100), indicator * (availability|latency)', 'Ready', 'Rendered from a slos: block; wraps Sloth'),
    ('RolloutWatch', '', 'Attached', 'environmentRef.name *, appName *, cluster *, env *, notifications.slack', 'rolloutPhase, lastDiagnosisRevision, lastDiagnosisJob, lastDiagnosisTime', 'Rendered alongside any release with a rollout: block'),
]
krows = ''.join(f'<tr><td class="area">{esc(k)}' + (f'<br><span class="note">{esc(s)}</span>' if s else '')
                + f'</td><td>{esc(t)}</td><td>{esc(f)}</td><td>{esc(o)}</td><td>{esc(c_)}</td></tr>'
                for k, s, t, f, o, c_ in KINDS)

NOT_LIVE = [
    '<b>OAuthServer, Database (postgresql), Queue (rabbitmq), mongodb, nginx.</b> Zero XRDs existed.',
    '<b>BranchProtection.</b> Deliberately deferred; it needs real CI status-check names.',
    '<b>Platform default canary steps.</b> The chart shipped an inert single-step placeholder.',
    '<b>A ClusterAnalysisTemplate golden-path library.</b> It belongs in the cluster baseline repo and wasn\'t built there.',
    '<b>A second real dev cluster.</b> The registry gate existed; nothing had exercised it.',
    '<b>The environment deletion and Argo CD prune deadlock.</b> Downgraded to monitor-only, not proven resolved.',
]

P.add(f"""
<section>
  <h2>The shape of a request</h2>
  {fig1}
  <div class="cards">
    <div class="card"><span class="eyebrow">The trust boundary</span><h3>Git-only, on purpose</h3><p>Airframe holds exactly one live credential class: a GitHub personal access token for provider-upjet-github and, for secrets, an Infisical identity. It never authenticates to a second cluster's Kubernetes API. Every cross-cluster effect happens by committing a file into that cluster's own tenants repo and letting its own Argo CD pick it up.</p></div>
    <div class="card"><span class="eyebrow">Every cluster</span><h3>Two Argo CD instances</h3><p><code>argocd-platform</code> is cluster-admin and installs the catalog itself. <code>argocd-apps</code> faces app owners, with one AppProject per app. The sets of repos they watch never overlap.</p></div>
    <div class="card"><span class="eyebrow">The loop</span><h3>Why the write loops back</h3><p>The engine's own Composition writes the very manifests Argo CD will later sync: <code>identity.yaml</code>, the release <code>values.yaml</code>, a SecretStore request. It closes the loop through git instead of calling any API directly.</p></div>
  </div>
</section>

<section>
  <h2>The catalog: eleven XRDs, one composition graph</h2>
  <div class="prose"><p>An app is created from one of five Bootstrap-tier stacks. Every stack composes a TektonCICD child directly. That's a normal in-process composition, and it's safe because TektonCICD only ever calls the GitHub API. Everything that has to land on a different cluster's API, namely SecretStore, is requested the indirect way: a commit into that cluster's own <code>xr-requests/</code>, never a direct composition.</p></div>
  {fig2}
</section>

<section>
  <h2>Every input, every output</h2>
  <div class="prose"><p>The graph shows shape; this is the full inventory. All eleven kinds share one API group and are namespaced. Only RolloutWatch publishes a real <code>status.properties</code> schema. Every other kind relies on custom conditions layered onto the standard Ready and Synced pair.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Kind</th><th>Tier</th><th>Key spec fields (inputs)</th><th>Status outputs</th><th>Composes or requests</th></tr></thead>
    <tbody>{krows}</tbody>
  </table></div>
  <p class="note">* marks a required field. All kinds: group <code>catalog.hangar.io</code>, scope Namespaced, <code>apiextensions.crossplane.io/v2</code>. This snapshot predates the rename: on September 20, 2026 the group was still <code>catalog.idp.io</code>.</p>
</section>

<section>
  <h2>Three tiers, three lifecycles</h2>
  <div class="prose"><p>The tier isn't a UI grouping. It's the mechanism. Bootstrap-tier XRs are created by a git commit and never touch a live cluster API, which is exactly why the engine can stay on one dev cluster however big the fleet gets. Attached-tier XRs compose real in-cluster resources directly, so they only mean something where Crossplane is actually running, and they have to be created per cluster.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Tier</th><th>Members</th><th>Mechanism</th><th>Lifecycle</th></tr></thead>
    <tbody>
      <tr><td class="area">Bootstrap</td><td>NodeJS, SpringBoot, Go, Python and InfraService stacks, ApplicationEnvironment. TektonCICD is Bootstrap-adjacent: composed, not created by a developer.</td><td>A commit into <code>xr-requests/</code>, reconciled by provider-github. No live API call, no Kubernetes credential.</td><td>Creates a new addressable git location: a repo, or a <code>&lt;cluster&gt;/&lt;env&gt;/values.yaml</code></td></tr>
      <tr><td class="area">Attached</td><td>SLO, Redis, RolloutWatch, and SecretStore (provisioned automatically, never chosen by a developer). Planned and unbuilt: OAuthServer, Database, Queue, mongodb, nginx.</td><td>A <code>components:</code> or <code>slos:</code> block inside that environment's own <code>values.yaml</code>, rendered into an XR in the app's namespace</td><td>Its own provisioning lifecycle, but only expressible inside an existing environment's file</td></tr>
      <tr><td class="area">Embedded</td><td>Config maps, secrets, HPA, PodDisruptionBudget, AnalysisTemplate, resource limits, volumes, networkPolicy</td><td>Plain fields on the same <code>values.yaml</code>, rendered directly, with no XR at all</td><td>One to one with the single workload (an Argo Rollout) the release owns</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>From request to running service</h2>
  <div class="prose"><p>One trace, start to finish: a developer asks for an app and an environment, the engine writes the git state that makes both real, and the target cluster ends up running a workload.</p></div>
  {fig3}
</section>

<section>
  <h2>What each Composition actually calls</h2>
  <div class="prose"><p>Every Composition in the catalog is a function-go-templating pipeline with inline source, plus a function-auto-ready step. The source stays inline because a second registered Function package once corrupted Crossplane's shared dependency-lock graph across the whole cluster. Below that shared shape, each XRD reaches a different real system.</p></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">GitHub</span><h3>provider-upjet-github</h3><p>The namespaced managed-resource family (<code>repo.github.m.upbound.io</code>), with a personal access token, because a GitHub App can't create repos under a personal account. It creates Repository and RepositoryFile resources: the src repo, its boilerplate, the empty <code>gitops-&lt;app&gt;</code> repo, <code>identity.yaml</code> and the release <code>values.yaml</code>. As of Sep 21, 2026 the boilerplate includes a real, build-only <code>cicd.yaml</code>, which closed the one hand-written step in an otherwise self-service flow.</p></div>
    <div class="card"><span class="eyebrow">Secrets</span><h3>provider-infisical and ESO</h3><p>Project, ProjectEnvironment, Identity and ProjectIdentity managed resources, wrapped through provider-kubernetes into a real ESO ClusterSecretStore. Crossplane v2 forces the wrap, since a namespaced XR can't compose a cluster-scoped resource directly. Kubernetes Auth on the cluster that hosts Infisical, Universal Auth everywhere else.</p></div>
    <div class="card"><span class="eyebrow">Compute</span><h3>provider-helm</h3><p>Redis composes a Release of a Bitnami-derived chart. It was the only component XRD with a real workload behind it. Every other planned component (Postgres, RabbitMQ, MongoDB, OAuthServer, nginx) was unbuilt.</p></div>
    <div class="card"><span class="eyebrow">Observability</span><h3>Sloth and HolmesGPT</h3><p>SLO renders a Sloth PrometheusServiceLevel, which Sloth's own controller turns into a real PrometheusRule. RolloutWatch finds the live Rollout through a Crossplane extra-resources lookup and, when it goes Degraded, sends a diagnosis Job to that cluster's HolmesGPT service, which can open a fix PR back into the GitOps repo.</p></div>
  </div>
</section>

<section>
  <p class="quote">"No cluster ever holds credentials for another cluster's API."</p>
  <div class="prose"><p>That one rule explains every indirection on this page: why SecretStore goes through a GitOps commit instead of a direct composition, why the Bootstrap engine can stay on one dev cluster for good, and why each cluster's own <code>argocd-apps</code> is the only thing that ever touches that cluster's workloads.</p></div>
</section>

<section>
  <h2>Not yet live on September 20, 2026</h2>
  <p class="note">Don't read these as built. Check the living design doc for where each one stands now.</p>
  <ul class="plain">{''.join(f'<li>{x}</li>' for x in NOT_LIVE)}</ul>
  <p class="note">Sources: the Hangar service catalog design and GitOps strategy docs, and the Airframe XRDs, as of September 20, 2026.</p>
</section>
""")
