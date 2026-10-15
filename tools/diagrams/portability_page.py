"""Build docs/library/2026-10-15-forge-registry-portability.html, the Library page for the illustrated forge and registry portability plan.

    python3 portability_page.py [ARTIFACT_OUT]

Inlines the six Portability diagrams (e_p.py) into one page that uses the architecture review's styles
(docs/reviews/), so it stands alone. With ARTIFACT_OUT it also writes the same page without the document
skeleton, for publishing as an Artifact. Run build_hangar.py first only if you also want the one-page diagrams.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
import e_p

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '../..')
REVIEW = os.path.join(ROOT, 'docs/reviews/2026-09-27-architecture-review.html')
# A Library paper: sync-assets copies docs/library/ to public/papers/, shown at /library/forge-registry-portability/.
OUT = os.path.join(ROOT, 'docs/library/2026-10-15-forge-registry-portability.html')

FIGS = [e_p.q_coupling, e_p.q_contracts, e_p.q_tokens, e_p.q_release_on_gitlab, e_p.q_migration, e_p.q_roadmap]


def figure(n, fn):
    r = fn()
    slug = f'p{n}-{r["slug"]}'
    y0, W, H = r.get('y0', 0), r['W'], r['H']
    svg = (f'<svg viewBox="0 {y0} {W} {H - y0}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-labelledby="{slug}-title {slug}-desc" style="min-width:{W}px">'
           f'<title id="{slug}-title">{lib.esc(r["title"])}</title><desc id="{slug}-desc">{lib.esc(r["desc"])}</desc>'
           f'<defs>{lib.defs()}</defs><rect width="100%" height="100%" fill="{lib.PAPER}"/>{r["body"]}</svg>')
    # Six inline SVGs share one document, so each gets its own marker ids.
    svg = re.sub(r'id="(arrow[a-z-]*)"', rf'id="d{n}-\1"', svg)
    svg = re.sub(r'url\(#(arrow[a-z-]*)\)', rf'url(#d{n}-\1)', svg)
    cap = f'<figcaption><span class="eyebrow">Figure {n} · {lib.esc(r["eyebrow"].split("·")[-1].strip())}</span> {lib.esc(r["lede"])}</figcaption>'
    return svg, f'<figure class="dia" id="fig-{n}"><h3>{lib.esc(r["title"])}</h3><div class="fig">{svg}</div>{cap}</figure>'


def dark_rules(svgs):
    rules = sorted({f'svg [{a}="{v}"]{{{a}:{lib.dark_colour(v)}}}'
                    for a, v in re.findall(r'\b(fill|stroke)="([^"]+)"', ''.join(svgs)) if lib.dark_colour(v)})
    return ('@media (prefers-color-scheme:dark){\n' + '\n'.join(f':root:not([data-theme="light"]) {r}' for r in rules) + '}\n'
            + '\n'.join(f':root[data-theme="dark"] {r}' for r in rules) + '\n')


EXTRA_CSS = """
.wrap{max-width:1032px}
.wrap>*,section>*,header>*,figure.dia,figure.dia>*{min-width:0;max-width:100%}
.prose,.verdict,.cards,.tbl,.gates,.recs,.dlist{max-width:100%}
figure.dia{margin:0;display:flex;flex-direction:column;gap:10px}
figure.dia h3{font-size:1.35rem}
figure.dia .fig{overflow-x:auto;background:var(--paper);border:1px solid var(--rule);border-radius:6px}
figure.dia svg{display:block;width:100%}
figcaption{font-size:.9rem;color:var(--ink-2);max-width:78ch}
figcaption .eyebrow{margin-right:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.kpi{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:14px 16px;display:flex;flex-direction:column;gap:2px;min-width:0}
.kpi .v{font-family:var(--serif);font-size:2.1rem;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi .l{font-size:.84rem;color:var(--ink-2)}
td code,li code{white-space:nowrap}
td{min-width:0}
.dlist{display:flex;flex-direction:column;gap:0;background:var(--paper);border:1px solid var(--rule);border-radius:6px}
.d{display:grid;grid-template-columns:52px 1fr;gap:12px;padding:14px 16px;border-bottom:1px solid var(--rule)}
.d:last-child{border-bottom:0}
.d .n{font-family:var(--mono);font-size:.8rem;color:var(--amber);border:1px solid var(--amber);border-radius:4px;height:28px;display:flex;align-items:center;justify-content:center}
.d h3{font-family:var(--sans);font-size:1rem;font-weight:600}
.d p{font-size:.93rem}
.d .rec{display:block;background:none;border:0;padding:0;font-size:.9rem;color:var(--ink-2)}
.d .rec b{color:var(--ink)}
"""

BODY = """
<header>
  <p class="eyebrow">Hangar · Portability plan · October 15, 2026 · Proposal, nothing built</p>
  <h1>Any forge, any registry</h1>
  <p class="prose" style="font-size:1.05rem">A plan to run Hangar on GitLab and Bitbucket as well as GitHub, and to publish images to any OCI
  registry as well as GHCR, without changing what Hangar is.</p>
  <div class="meta"><span>Scope: Airframe, Glidepath, Tower and Backstage, Apron, Autopilot</span><span>Basis: origin/main of every repo, the live dev cluster</span><span>Status: proposal, for decision</span></div>
</header>

<section class="verdict">
  <span class="stamp">Feasible · 6 phases · about 24 weeks</span>
  <h2>The engine is already neutral. Three things are not.</h2>
  <div class="prose">
    <p>Tekton, Pipelines as Code, Argo CD, External Secrets, Crossplane and cosign all work with GitLab and Bitbucket today.
    GitHub is wired into Hangar in about a hundred small places (a literal owner, a <code>curl</code> to
    <code>api.github.com</code>, a hardcoded link), and in three places it is part of the design:</p>
  </div>
  <ul>
    <li><b>The control plane writes to repositories through provider-upjet-github.</b> 81 templates in 9 compositions, 88 live
    resources on the dev cluster. The GitLab provider has no file resource and no maintained Bitbucket Cloud provider exists, and this
    provider caused the September data loss and rate-limit storms.</li>
    <li><b>CI tokens are GitHub App installation tokens.</b> The never-persisted credential model is built on a GitHub feature
    that GitLab and Bitbucket do not have in the same form.</li>
    <li><b>An app is identified by <code>github.com/project-slug</code>.</b> Tower authorization (ACC-05), release approvers and
    the catalog app list all key on it, and it assumes a one-segment owner that GitLab subgroups break.</li>
  </ul>
  <div class="prose">
    <p><b>Recommendation.</b> Introduce two Hangar-owned contracts, one for the forge and one for the registry, with each vendor as a
    driver behind one of them. Move the existing GitHub path onto the contracts first, with no visible change (phases 0 to 2,
    which also removes the RepositoryFile bug class on GitHub). Then add GitLab as the proof (phase 3) and Bitbucket after it
    (phase 4). The forge and the registry become separate choices, because a Bitbucket shop has no registry of its own.</p>
  </div>
</section>

<section>
  <div class="kpis">
    <div class="kpi"><span class="v">81</span><span class="l">GitHub resource templates in Airframe compositions</span></div>
    <div class="kpi"><span class="v">88</span><span class="l">of them live on the dev cluster today (24 repos, 64 files)</span></div>
    <div class="kpi"><span class="v">15</span><span class="l">Glidepath call sites with inline GitHub REST</span></div>
    <div class="kpi"><span class="v">24</span><span class="l">Backstage backend files calling the GitHub API</span></div>
    <div class="kpi"><span class="v">10</span><span class="l">places the owner <code>jfillman</code> is a literal</span></div>
  </div>
</section>

<section>
  <h2>What is coupled today</h2>
  {FIG1}
  <div class="tbl"><table>
    <thead><tr><th>Where</th><th>Coupling</th><th>Evidence</th><th>Kind</th></tr></thead>
    <tbody>
      <tr><td class="area">Airframe</td><td>Repos and files are <code>repo.github.m.upbound.io</code> Repository and RepositoryFile resources</td><td><code>compositions/*/templates/render-github-resources/</code>, 9 compositions</td><td><span class="chip c-bad">load-bearing</span></td></tr>
      <tr><td class="area">Airframe</td><td>Owner literal; repo URLs and the Go module path built as <code>github.com/&lt;owner&gt;/&lt;app&gt;</code></td><td><code>$platformOwner := "jfillman"</code>, <code>_shared/render-github-resources/tekton-cicd-child.yaml</code>, <code>goapplication</code></td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Airframe</td><td>Container App registry defaults to <code>ghcr.io</code></td><td><code>xrds/azurecontainerapptarget.yaml</code></td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Glidepath</td><td>13 Tasks, 1 StepAction and the preview notify Job call <code>api.github.com</code> with <code>curl</code>: pulls, issue comments, check runs, contents, compare, commit to PR, update-branch, reviews</td><td><code>open-release-pr</code>, <code>comment-pr-check-result</code>, <code>deliver-onboarding-files</code>, <code>verify-commit-signature</code> and 11 more</td><td><span class="chip c-info">mechanical, wide</span></td></tr>
      <tr><td class="area">Glidepath</td><td>Broker mints GitHub App installation tokens for one repo</td><td><code>token-review-interceptor</code> <code>/github-installation-token</code>, <code>catalog/lib/github-app.sh</code></td><td><span class="chip c-bad">load-bearing</span></td></tr>
      <tr><td class="area">Glidepath</td><td>Image path derived from the GitHub owner</td><td><code>deliver-onboarding-files.yaml</code>: <code>image_repo="ghcr.io/${GITHUB_OWNER}/${APP_NAME}"</code>; previews <code>ghcr.io/&lt;owner&gt;/&lt;app&gt;-pr</code></td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Glidepath</td><td>Merge gate is a GitHub ruleset that trusts checks from the PaC app (<code>integration_id</code> 4461953)</td><td><code>docs/admin/github-ruleset.md</code>, <code>hack/apply-guardrail-ruleset.sh</code></td><td><span class="chip c-warn">policy</span></td></tr>
      <tr><td class="area">Tower</td><td>App identity is <code>github.com/project-slug</code>, parsed with <code>split('/')</code></td><td><code>towerAuthz.ts</code>, <code>releaseApprovers.ts</code>, <code>catalogApps.ts</code>, <code>TowerPage.tsx</code></td><td><span class="chip c-bad">load-bearing</span></td></tr>
      <tr><td class="area">Tower</td><td>Image client accepts only GHCR; prune and the Images tab use the GitHub Packages API</td><td><code>ghcr.ts</code> ("only ghcr.io images are supported"), <code>imagePrune.ts</code>, <code>classifyGhcrVersion</code></td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Tower</td><td>Commit, author and file links hardcoded to <code>https://github.com/</code></td><td><code>activityRowRenderers.tsx</code>, <code>useEnvLifecycle.ts</code>, <code>ownChart.ts</code> and 5 more</td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Backstage</td><td>GitHub OAuth sign-in; only <code>integrations.github</code>; ingestor <code>publishPhase.target: github</code></td><td><code>app-config.production.yaml</code>, <code>app-config.yaml</code></td><td><span class="chip c-warn">policy</span></td></tr>
      <tr><td class="area">Apron</td><td>Argo CD repo creds are GitHub App creds for the <code>https://github.com/jfillman</code> prefix; ApplicationSet allows only <code>https://api.github.com</code></td><td><code>01-argocd-platform/repo-creds/</code>, <code>argocd-apps-install/application.yaml</code></td><td><span class="chip c-info">mechanical</span></td></tr>
      <tr><td class="area">Autopilot</td><td>Agent images on <code>ghcr.io/jfillman</code></td><td><code>agents/*.yaml</code></td><td><span class="chip c-info">mechanical</span></td></tr>
    </tbody>
  </table></div>
  <p class="note">Already neutral and staying as is: Tekton and Pipelines as Code (GitLab, Bitbucket Cloud and Data Center are supported
  providers), Argo CD (any git host; PR generators for GitLab and Bitbucket), the <code>registry-credentials</code>
  ClusterExternalSecret (a plain dockerconfigjson), cosign and Rekor, Apron's <code>scm.host</code> and <code>scm.owner</code>
  in <code>cluster.yaml</code>, and the terasky ingestor, whose publish step already supports <code>gitlab</code>,
  <code>bitbucket</code> and <code>bitbucketcloud</code> targets.</p>
</section>

<section>
  <h2>Principles</h2>
  <div class="cards">
    <div class="card"><h3>Separate the forge from the registry</h3><p>Choose them independently. The image path comes from registry config, never from the forge owner.</p></div>
    <div class="card"><h3>Hangar names things</h3><p><code>scm.hangar.io</code> resources, <code>hangar.io/app</code> identity, an <code>scm</code> CLI. Vendors are drivers.</p></div>
    <div class="card"><h3>GitHub moves first</h3><p>Nothing reaches GitLab until the GitHub path runs on the contracts with no change a user can see.</p></div>
    <div class="card"><h3>Capabilities, not the lowest common denominator</h3><p>A driver declares what it can enforce. Tower shows the real level per app.</p></div>
    <div class="card"><h3>Write the credential delta down</h3><p>Every forge gets a row in the credentials table. Weaker is allowed; silent is not.</p></div>
    <div class="card"><h3>Adopt, never recreate</h3><p>Every migration step observes existing repos by name. No step may commit or delete.</p></div>
  </div>
</section>

<section>
  <h2>Target architecture</h2>
  {FIG2}
  <div class="prose">
    <p><b>The SCM contract</b> has two faces over one Go library:</p>
  </div>
  <ul class="plain">
    <li><b>Declarative</b>: <code>provider-hangar-scm</code>, a native Crossplane provider serving <code>scm.hangar.io/v1alpha1</code>
    <code>Repository</code>, <code>RepositoryFile</code>, <code>Webhook</code> and <code>MergeGate</code>. A ProviderConfig per forge instance
    (<code>github</code>, <code>gitlab</code>) picks the driver, so each composition keeps one shape and only its
    <code>providerConfigRef</code> changes. <code>RepositoryFile.spec.mode</code> is <code>seed</code> (create once if absent, never
    update or delete: today's scaffold rule, written into the API instead of into management policies) or <code>managed</code> (the
    platform-owned identity files in tenants repos).</li>
    <li><b>Imperative</b>: an <code>scm</code> CLI in the Glidepath toolbox image (<code>scm pr open|find|comment</code>, <code>scm status</code>,
    <code>scm contents get</code>, <code>scm compare</code>, <code>scm pr-for-commit</code>, <code>scm gate apply</code>) that replaces the inline
    <code>curl</code>, and a broker endpoint <code>/scm-token</code> beside today's <code>/github-installation-token</code>.</li>
    <li><b>Tower</b> gets a TypeScript <code>ScmClient</code> and <code>RegistryClient</code> in the Backstage backend, with drivers built on
    <code>@backstage/integration</code>, which already resolves credentials for GitLab, Bitbucket Cloud and Bitbucket Server. It runs the
    same recorded conformance fixtures as the Go library.</li>
  </ul>
  <div class="prose">
    <p><b>The registry contract</b> is mostly plain OCI. Push, pull, digest, tags, referrers and cosign signatures work against any
    compliant registry with the standard bearer-token challenge, so the GHCR-specific token exchange in <code>ghcr.ts</code> goes. Only
    listing versions with dates and deleting them are vendor APIs, so only those need drivers. Config is
    <code>registry.host</code> and <code>registry.namespace</code>; the image path is <code>&lt;host&gt;/&lt;namespace&gt;/&lt;app&gt;</code>
    and previews add <code>-pr</code>.</p>
    <p><b>Identity.</b> Add <code>hangar.io/app</code> (the app's Hangar name), <code>hangar.io/forge</code> and
    <code>hangar.io/source-location</code>. Tower authorization reads <code>hangar.io/app</code>; GitHub apps keep
    <code>github.com/project-slug</code> for stock Backstage plugins. A repo's namespace may have several segments (GitLab subgroups,
    a Bitbucket workspace and project).</p>
    <p><b>Sign-in.</b> Move Backstage from GitHub OAuth to OIDC through Dex, which already runs in the cluster and has GitHub, GitLab
    and Bitbucket Cloud connectors (LDAP or SAML for Data Center shops). Users still match catalog Users. This also moves the
    architecture review's SSO gate forward.</p>
  </div>
</section>

<section>
  <h2>Decision: how the control plane writes to a forge</h2>
  <div class="tbl"><table>
    <thead><tr><th>Option</th><th>For</th><th>Against</th></tr></thead>
    <tbody>
      <tr><td class="area">A. A vendor provider per forge</td><td>No new code to own for GitHub and GitLab.</td><td>provider-gitlab has Project, Hook, ProtectedBranch and AccessToken but no file resource. No maintained Bitbucket Cloud provider. Three composition variants per app type. Keeps the known RepositoryFile bugs.</td></tr>
      <tr><td class="area">B. Move file writes into Glidepath</td><td>No reconciler writing to repos at all.</td><td>Loses continuous reconcile for the tenants-repo identity files (Create and Update today), and Airframe would need Glidepath to exist before it can scaffold.</td></tr>
      <tr><td class="area"><span class="chip c-ok">recommended</span><br>C. provider-hangar-scm</td><td>One behaviour on every forge. Compositions change only the apiVersion and providerConfigRef. Treats only a 404 as gone, keeps the observed external-name, never writes on adopt: the three provider bugs, fixed by design.</td><td>Hangar owns a provider (Go, crossplane-runtime), about 4 weeks with the GitHub driver and tests. Offset by retiring provider-upjet-github, whose upstream fixes are still unpublished.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>The SCM contract, operation by operation</h2>
  <div class="tbl"><table>
    <thead><tr><th>Operation</th><th>Caller</th><th>GitHub</th><th>GitLab</th><th>Bitbucket Cloud</th><th>Bitbucket DC</th></tr></thead>
    <tbody>
      <tr><td class="area">Repository</td><td>Airframe</td><td>repos</td><td>projects</td><td>repositories</td><td>projects/repos</td></tr>
      <tr><td class="area">Seed or manage a file</td><td>Airframe</td><td>contents PUT</td><td>commits with actions</td><td>src POST</td><td>browse PUT</td></tr>
      <tr><td class="area">Webhook</td><td>Airframe</td><td>none (app-level)</td><td>project hook</td><td>repo webhook</td><td>repo webhook</td></tr>
      <tr><td class="area">Merge gate</td><td>Apron, Glidepath</td><td>ruleset, checks by app</td><td>protected branch, pipelines must succeed, approval rules</td><td>branch restrictions, merge checks</td><td>branch permissions, required builds</td></tr>
      <tr><td class="area">Open, find, update PR</td><td>Glidepath, Tower</td><td>pulls</td><td>merge_requests</td><td>pullrequests</td><td>pull-requests</td></tr>
      <tr><td class="area">Upsert a comment</td><td>Glidepath</td><td>issue comments</td><td>MR notes</td><td>PR comments</td><td>PR comments</td></tr>
      <tr><td class="area">Status per gate</td><td>PaC, Glidepath</td><td>check runs</td><td>commit statuses</td><td>build statuses</td><td>build statuses</td></tr>
      <tr><td class="area">Read a file at a ref</td><td>Glidepath, Tower</td><td>contents</td><td>files raw</td><td>src</td><td>raw</td></tr>
      <tr><td class="area">Compare, PR for a commit</td><td>Glidepath, Tower</td><td>compare, commits/pulls</td><td>compare, commits/merge_requests</td><td>diffstat, commit/pullrequests</td><td>compare</td></tr>
      <tr><td class="area">Short-lived token</td><td>Broker</td><td>App installation, 1 h</td><td>project access token, by date</td><td>OAuth client credentials, 2 h</td><td>repo HTTP token, by days</td></tr>
    </tbody>
  </table></div>
  <p class="note">Resource names are the shape to build against. Check each endpoint against the vendor's API reference when its driver is written; the Bitbucket Data Center column in particular is unverified.</p>
</section>

<section>
  <h2>The registry contract</h2>
  <div class="tbl"><table>
    <thead><tr><th>Capability</th><th>Standard</th><th>GHCR</th><th>GitLab CR</th><th>Harbor</th><th>ECR</th></tr></thead>
    <tbody>
      <tr><td class="area">Push, pull, digest, tags</td><td>OCI Distribution</td><td colspan="4">same code, every registry</td></tr>
      <tr><td class="area">Auth</td><td>bearer challenge</td><td>PAT for a token</td><td>deploy or CI token for a JWT</td><td>robot account</td><td>12 h login token</td></tr>
      <tr><td class="area">cosign signatures</td><td>tag or referrers</td><td>tag</td><td>tag</td><td>tag and referrers</td><td>tag and referrers</td></tr>
      <tr><td class="area">List versions with dates</td><td>vendor</td><td>GitHub Packages API</td><td>registry API</td><td>Harbor API</td><td>DescribeImages</td></tr>
      <tr><td class="area">Delete</td><td>vendor</td><td>Packages API, classic PAT</td><td>registry API</td><td>Harbor API</td><td>BatchDeleteImage</td></tr>
      <tr><td class="area">Retention</td><td>vendor</td><td>none; Tower prunes</td><td>cleanup policies</td><td>retention rules</td><td>lifecycle policies</td></tr>
    </tbody>
  </table></div>
  <p class="note">Bitbucket has no container registry, so a Bitbucket fleet must pick one. Harbor is the recommended neutral default:
  self-hosted, robot accounts, cosign and referrers, replication, and Trivy, the scanner Glidepath already runs.</p>
</section>

<section>
  <h2>Credentials, forge by forge</h2>
  {FIG3}
  <div class="tbl"><table>
    <thead><tr><th>Path</th><th>GitHub</th><th>GitLab</th><th>Bitbucket Cloud</th><th>Bitbucket DC</th></tr></thead>
    <tbody>
      <tr><td class="area">CI write token</td><td>App installation, 1 h, one repo</td><td>project access token, expires next day, one project, revoked when the run ends</td><td>OAuth client credentials, 2 h, <b>whole workspace</b></td><td>repo HTTP token, 1 day, one repo</td></tr>
      <tr><td class="area">PaC trigger and status</td><td>GitHub App, nothing stored</td><td colspan="3">webhook secret plus a token in a Secret named by the Repository CR; the broker rotates it daily and Tower shows its age</td></tr>
      <tr><td class="area">Control plane</td><td>GitHub App (ends the shared PAT bucket)</td><td>group access token</td><td>workspace access token</td><td>project HTTP token</td></tr>
      <tr><td class="area">Argo CD, read only</td><td>GitHub App repo creds</td><td>group deploy token</td><td>workspace access token</td><td>project HTTP token, read</td></tr>
      <tr><td class="area">Tower backend</td><td>GitHub App (a PAT today)</td><td>group access token</td><td>workspace access token</td><td>HTTP token</td></tr>
    </tbody>
  </table></div>
  <p class="note">Bitbucket Cloud removed app passwords on July 28, 2026; use API tokens or access tokens. Plan tiers change what can be
  enforced (GitLab approval rules and group webhooks, Bitbucket Cloud merge-check enforcement); check current vendor pricing before
  you choose a plan for the lab.</p>
</section>

<section>
  <h2>The proof: one release on GitLab</h2>
  {FIG4}
</section>

<section>
  <h2>What changes, product by product</h2>
  <div class="recs">
    <div class="rec"><h3>Airframe</h3><ol>
      <li>Every <code>repo.github.m.upbound.io</code> template becomes <code>scm.hangar.io</code>; the symlinked <code>_shared</code> partials keep the diff small.</li>
      <li>Owner, host and registry come from the cluster registry entry (already read through ExtraResources), never a literal.</li>
      <li>Optional <code>spec.source</code> (forge, namespace) on app XRDs, defaulted from platform config; CEL checks the namespace shape per forge.</li>
      <li>A <code>Webhook</code> per repo on forges without app-level webhooks; the Go module path follows the source host.</li>
    </ol></div>
    <div class="rec"><h3>Glidepath</h3><ol>
      <li>The <code>scm</code> CLI replaces <code>curl</code>, one Task per PR, each with fixtures. ADR-0026: the SCM contract.</li>
      <li><code>platformIdentity.githubOwner</code> becomes <code>platformIdentity.source</code>; <code>image-repo</code> comes from registry config.</li>
      <li>The broker gains <code>/scm-token</code> and the PaC secret rotator; PaC Repository CRs gain <code>git_provider</code> off GitHub.</li>
      <li><code>github-ruleset.md</code> becomes <code>merge-gate.md</code>; <code>scm gate apply</code> renders it from <code>releaseGuardrails</code>.</li>
    </ol></div>
    <div class="rec"><h3>Tower and Backstage</h3><ol>
      <li><code>ScmClient</code> and <code>RegistryClient</code>; today's GitHub code becomes the first driver, unchanged.</li>
      <li>Authorization and approvers read <code>hangar.io/app</code>; links come from <code>hangar.io/source-location</code>.</li>
      <li>Integrations, scaffolder publish actions and the ingestor publish target per forge; sign-in through Dex.</li>
      <li>Each app shows its forge and the merge-gate level the driver reports.</li>
    </ol></div>
    <div class="rec"><h3>Apron, Autopilot, Hangar</h3><ol>
      <li><code>cluster.yaml</code> gains <code>scm.forge</code>, <code>scm.namespace</code> and <code>registry.*</code>; the script renders repo creds, the PaC secret and the allowed SCM providers per forge.</li>
      <li>provider-github is removed after phase 2.</li>
      <li>Agent images come from registry config.</li>
      <li>Business rules PPL-01, PPL-02, ACC-05, GATE-03 and GATE-06 are reworded per forge when each lands (<code>docs/policy/business-rules.md</code>).</li>
    </ol></div>
  </div>
</section>

<section>
  <h2>Moving the GitHub fleet first</h2>
  {FIG5}
</section>

<section>
  <h2>Roadmap</h2>
  {FIG6}
  <div class="gates">
    <div class="gate"><span class="n">P0</span><div><p><b>Seams, GitHub only.</b> No <code>api.github.com</code> or <code>ghcr.io</code> literal outside a driver, enforced by a CI ratchet; no owner literal in compositions; Tower reads <code>hangar.io/app</code>.</p><p class="when">Exit, live: a Skyport release and rollback behave exactly as before; GitHub calls per hour at or below the baseline.</p></div></div>
    <div class="gate"><span class="n">P1</span><div><p><b>Registry independence.</b> Image path from config; a second registry lane.</p><p class="when">Exit, live: one Skyport app builds, signs, passes the provenance gate, deploys, lists and prunes from a non-GHCR registry.</p></div></div>
    <div class="gate"><span class="n">P2</span><div><p><b>provider-hangar-scm.</b> GitHub driver, then adopt all 88 live resources and uninstall provider-upjet-github.</p><p class="when">Exit, live: zero commits during adoption; an injected 403 rate limit neither deletes nor rewrites a file.</p></div></div>
    <div class="gate"><span class="n">P3</span><div><p><b>GitLab end to end.</b> Drivers, broker, PaC, Argo CD, Backstage, Dex.</p><p class="when">Exit, live: figure 4 runs with a rollback; the merge gate refuses a red gate; broker tokens are revoked after each run.</p></div></div>
    <div class="gate"><span class="n">P4</span><div><p><b>Bitbucket.</b> Cloud first, then Data Center, with Harbor.</p><p class="when">Exit, live: the phase 3 test on Bitbucket Cloud.</p></div></div>
    <div class="gate"><span class="n">P5</span><div><p><b>Mixed fleet.</b> Per-app forge, rate budgets per forge in Grafana, docs, business rules, scorecard.</p><p class="when">Exit, live: one fleet with apps on two forges.</p></div></div>
  </div>
</section>

<section>
  <h2>Decisions for you</h2>
  <div class="dlist">
    <div class="d"><span class="n">D1</span><div><h3>How the control plane writes to a forge</h3><p class="rec"><b>Recommend option C</b>, provider-hangar-scm, in Go. The Python preference for composition functions does not apply to a provider.</p></div></div>
    <div class="d"><span class="n">D2</span><div><h3>Order of forges</h3><p class="rec"><b>GitLab, then Bitbucket Cloud, then Data Center.</b> GitLab has the closest feature set and its own registry; Data Center needs a licensed server for the lab.</p></div></div>
    <div class="d"><span class="n">D3</span><div><h3>Where the GitLab lab lives</h3><p class="rec"><b>A gitlab.com Free group.</b> The prod cluster has no CPU to spare for self-managed GitLab. Free has no required approvals, so the two-person rule stays "Off here", as on GitHub Free today.</p></div></div>
    <div class="d"><span class="n">D4</span><div><h3>The second registry</h3><p class="rec"><b>GitLab Container Registry for the GitLab lane</b> (no infrastructure), Harbor as the documented neutral default, run in CI.</p></div></div>
    <div class="d"><span class="n">D5</span><div><h3>Accept the credential differences</h3><p class="rec"><b>Accept, with revoke-at-end and daily rotation</b>, and Tower showing token age. Bitbucket Cloud's workspace-wide token is the one to watch.</p></div></div>
    <div class="d"><span class="n">D6</span><div><h3>One forge per fleet, or per app</h3><p class="rec"><b>Fleet default through phase 4</b>; the per-app field is in the schema from phase 0 but enabled in phase 5.</p></div></div>
    <div class="d"><span class="n">D7</span><div><h3>A name for the SCM component</h3><p class="rec">Yours to choose, in the aviation vocabulary. Working name: <code>hangar-scm</code>.</p></div></div>
  </div>
</section>

<section>
  <h2>Risks</h2>
  <ul class="plain">
    <li><b>Rate limits.</b> Bitbucket Cloud's hourly API budget is far smaller than GitHub's, and the old fleet once burned 16,000 calls an hour in a loop. Seed files are never re-read after the scaffold ledger marks them done; every driver uses conditional reads where the forge supports them; a per-forge budget metric trips a breaker.</li>
    <li><b>Nested namespaces</b> break every <code>owner/repo</code> parse: Tower's <code>split('/')</code>, the broker's name match in <code>verifyAppOwnsRepo</code>, Glidepath's <code>git-url</code> handling. Phase 0 fixes them on GitHub.</li>
    <li><b>Webhooks per repo</b> mean more objects and more secrets; each is an <code>scm.hangar.io</code> Webhook with its own rotated secret.</li>
    <li><b>Test matrix.</b> Four forges and four registries. Recorded conformance fixtures run on every PR; one live lane per forge runs nightly.</li>
    <li><b>Plan tiers</b> change what is enforced. Tower reports the level the driver measured, never an assumed one.</li>
    <li><b>Owning a provider</b> is code to maintain, set against retiring one that needed a fleet-wide pause.</li>
  </ul>
</section>

<section>
  <h2>What I checked</h2>
  <ul class="plain">
    <li>origin/main of airframe, glidepath, tower, backstage, apron and hangar, and autopilot's main; counts from <code>git grep</code> over deployable files (compositions, not their example output).</li>
    <li>The live dev cluster, read only: 24 Repository and 64 RepositoryFile resources from provider-upjet-github, none paused; none on the prod cluster.</li>
    <li>The installed terasky ingestor source: its publish step handles <code>github</code>, <code>gitlab</code>, <code>bitbucket</code> (Server) and <code>bitbucketcloud</code>.</li>
    <li>Vendor sources: Pipelines as Code providers (Tekton announcement, March 2026), the PaC GitLab token Secret (Red Hat OpenShift Pipelines 1.20), provider-gitlab's resource list (no file resource), Bitbucket Cloud's app password removal (Atlassian).</li>
    <li>Not verified: plan-tier features per vendor, Bitbucket rate limits and Data Center endpoints, GitLab conditional-read coverage. Nothing was built or changed on any cluster.</li>
  </ul>
</section>

<footer>Hangar · Portability · generated by <code>tools/diagrams/portability_page.py</code> with the diagram-design skill (Hangar profile). One-page diagrams: <code>docs/portability/diagrams/</code>.</footer>
"""


def main():
    review = open(REVIEW).read()
    css = review[review.index('<style>') + 7:review.index('</style>')]
    svgs, figs = [], {}
    for n, fn in enumerate(FIGS, 1):
        svg, fig = figure(n, fn)
        svgs.append(svg)
        figs[f'{{FIG{n}}}'] = fig
    body = BODY
    for k, v in figs.items():
        body = body.replace(k, v)
    style = f'<style>{css}{EXTRA_CSS}{dark_rules(svgs)}</style>'
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">')
    title = '<title>Any Forge, Any Registry</title>'
    main_html = f'<main class="wrap">{body}</main>'
    full = (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'{title}\n<meta name="description" content="A plan to run Hangar on GitLab and Bitbucket as well as GitHub, and on any OCI registry as well as GHCR.">\n'
            f'{fonts}\n{style}\n</head>\n<body>\n{main_html}\n</body>\n</html>\n')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w').write(full)
    print('wrote', os.path.relpath(OUT, ROOT))
    if len(sys.argv) > 1:
        open(sys.argv[1], 'w').write(f'{title}\n{fonts}\n{style}\n{main_html}\n')
        print('wrote', sys.argv[1])


main()
