"""Review and roadmap: Apron's next shape, built on kubara (Oct 16, 2026), ported from the claude.ai artifact."""
from report import Page

CSS = r'''.apron{--amber-soft:#f4e6c9;display:flex;flex-direction:column;gap:44px}
:root[data-theme="dark"] .apron{--amber-soft:#3a2c15}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .apron{--amber-soft:#3a2c15}}
.apron h2,.apron h3{font-family:var(--serif);font-weight:400;letter-spacing:-.01em;line-height:1.15;text-wrap:balance;margin:0}
.apron h2{font-size:1.9rem;padding-bottom:8px;border-bottom:1px solid var(--rule)}
.apron h3{font-size:1.3rem}
.apron p{margin:0}
.apron section{display:flex;flex-direction:column;gap:16px}
.apron .prose{max-width:68ch;display:flex;flex-direction:column;gap:12px}
.apron .prose ul,.apron .prose ol{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:6px}
.apron .eyebrow{font-family:var(--mono);font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--amber)}
.apron code{font-family:var(--mono);font-size:.85em;background:var(--code-bg);padding:1px 5px;border-radius:3px;overflow-wrap:anywhere}
.apron a{color:var(--accent)}
.apron a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.apron .meta{display:flex;flex-wrap:wrap;gap:6px 20px;font-size:.85rem;color:var(--ink-2)}
.apron .meta b{color:var(--ink);font-weight:500}
.apron .verdict{background:var(--paper);border:1px solid var(--rule);border-top:4px solid var(--accent);border-radius:6px;padding:24px;display:flex;flex-direction:column;gap:14px}
.apron .verdict .stamp{display:inline-flex;align-self:flex-start;font-family:var(--mono);font-size:.78rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);background:var(--accent-soft);padding:4px 10px;border-radius:3px}
.apron .verdict h2{border:0;padding:0;font-size:1.75rem}
.apron .verdict ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:8px}
.apron .callout{background:var(--amber-soft);border-radius:6px;padding:16px 18px;display:flex;flex-direction:column;gap:8px;max-width:72ch}
.apron .callout b.lbl{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--warn)}
.apron .tbl{overflow-x:auto;background:var(--paper);border:1px solid var(--rule);border-radius:6px}
.apron table{border-collapse:collapse;width:100%;font-size:.88rem;min-width:720px}
.apron th,.apron td{text-align:left;vertical-align:top;padding:10px 14px;border-bottom:1px solid var(--rule)}
.apron th{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);font-weight:500;background:var(--ground)}
.apron tr:last-child td{border-bottom:0}
.apron td.area{font-weight:600;white-space:nowrap}
.apron tr.us td{background:var(--accent-soft)}
.apron .chip{display:inline-block;font-family:var(--mono);font-size:.7rem;font-weight:500;letter-spacing:.04em;padding:2px 8px;border-radius:3px;white-space:nowrap}
.apron .c-ok{color:var(--ok);background:var(--ok-bg)}
.apron .c-warn{color:var(--warn);background:var(--warn-bg)}
.apron .c-bad{color:var(--bad);background:var(--bad-bg)}
.apron .c-info{color:var(--info);background:var(--info-bg)}
.apron .finding{background:var(--paper);border:1px solid var(--rule);border-left:4px solid var(--rule);border-radius:4px;padding:16px 18px;display:flex;flex-direction:column;gap:8px}
.apron .finding.sev-high{border-left-color:var(--bad)}
.apron .finding.sev-med{border-left-color:var(--warn)}
.apron .finding.sev-low{border-left-color:var(--info)}
.apron .finding .top{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 12px}
.apron .finding .id{font-family:var(--mono);font-size:.75rem;color:var(--ink-2)}
.apron .finding h3{font-family:var(--sans);font-size:1rem;font-weight:600}
.apron .finding p{font-size:.93rem;color:var(--ink-2);max-width:72ch}
.apron .findings{display:flex;flex-direction:column;gap:10px}
.apron .fig{margin:0;background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:18px;display:flex;flex-direction:column;gap:12px}
.apron .fig .scroll{overflow-x:auto}
.apron .fig svg{display:block;width:100%;height:auto}
.apron .fig figcaption{font-size:.86rem;color:var(--ink-2)}
.apron .fig figcaption b{font-family:var(--mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);margin-right:8px;font-weight:500}
.apron svg text{font-family:var(--sans);fill:var(--ink)}
.apron svg .t-mono{font-family:var(--mono);font-size:11px;fill:var(--ink-2)}
.apron svg .t-lbl{font-size:13px;font-weight:600}
.apron svg .t-sm{font-size:11.5px;fill:var(--ink-2)}
.apron svg .t-eyebrow{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;fill:var(--amber)}
.apron svg .box{fill:var(--paper);stroke:var(--rule);stroke-width:1}
.apron svg .band{fill:var(--ground);stroke:var(--rule)}
.apron svg .us{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.5}
.apron svg .warnb{fill:var(--warn-bg);stroke:var(--warn);stroke-width:1}
.apron svg .okb{fill:var(--ok-bg);stroke:var(--ok);stroke-width:1}
.apron svg .badb{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1}
.apron svg .edge{stroke:var(--ink-2);stroke-width:1.3;fill:none}
.apron svg .edge-a{stroke:var(--accent);stroke-width:1.6;fill:none}
.apron svg .edge-bad{stroke:var(--bad);stroke-width:1.3;fill:none;stroke-dasharray:4 3}
.apron svg .dash{stroke:var(--rule);stroke-dasharray:3 4;fill:none;stroke-width:1.2}
.apron svg .ah{fill:var(--ink-2)}
.apron svg .ah-a{fill:var(--accent)}
.apron pre{margin:0;background:var(--code-bg);border-radius:6px;padding:14px 16px;overflow-x:auto;font-family:var(--mono);font-size:.8rem;line-height:1.55}
.apron pre .c{color:var(--ink-2)}
.apron .pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.apron .pair>div{min-width:0;display:flex;flex-direction:column;gap:6px}
.apron .pair .cap{font-family:var(--mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.apron .purpose{font-family:var(--serif);font-size:clamp(1.5rem,3.6vw,2rem);line-height:1.25;max-width:30ch;text-wrap:balance}
.apron .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.apron .col{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:16px;display:flex;flex-direction:column;gap:8px;min-width:0}
.apron .col h3{font-family:var(--mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;font-weight:500}
.apron .col.is h3{color:var(--ok)}
.apron .col.isnt h3{color:var(--bad)}
.apron .col ul{margin:0;padding-left:18px;font-size:.92rem;display:flex;flex-direction:column;gap:5px}
.apron .phases{display:flex;flex-direction:column;gap:0;border-left:2px solid var(--rule);margin-left:8px}
.apron .phase{position:relative;padding:0 0 22px 24px;display:flex;flex-direction:column;gap:6px}
.apron .phase::before{content:"";position:absolute;left:-8px;top:6px;width:14px;height:14px;border-radius:50%;background:var(--paper);border:2px solid var(--ink-2)}
.apron .phase.now::before{background:var(--ok);border-color:var(--ok)}
.apron .phase.next::before{background:var(--accent);border-color:var(--accent)}
.apron .phase .ph{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:baseline}
.apron .phase .v{font-family:var(--mono);font-size:.8rem;color:var(--amber)}
.apron .phase h3{font-size:1.25rem}
.apron .phase ul{margin:0;padding-left:20px;font-size:.93rem;color:var(--ink-2);display:flex;flex-direction:column;gap:4px;max-width:72ch}
.apron .phase .exit{font-size:.88rem;max-width:72ch}
.apron .phase .exit b{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);font-weight:500;margin-right:6px}
.apron .sources{font-size:.85rem;color:var(--ink-2)}
.apron .sources ul{margin:6px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:3px}
@media (prefers-reduced-motion: reduce){}'''

P = Page(
    'apron-next-shape', 'Review', 'Apron · Review and roadmap · kubara',
    "Apron's next shape: self-contained, built on kubara",
    'Apron and kubara, an open-source GitOps platform framework, solve the same problem. This review compares the two and records '
    'the October 16, 2026 decision: Apron keeps its services in one kubara catalog, uses kubara as its only renderer, and stays installable on its own.',
    '2026-10-16',
    meta=[('Decision', 'October 16, 2026'),
          ('Status', 'decided; v0.5 (the apron CLI and the lab rebuild) built Oct 16 and 17, 2026; the kubara port not started'),
          ('Read', '<code>jfillman/apron</code> · <code>jfillman/hangar</code> · <code>kubara-io/kubara</code> · <code>kubara-io/catalogs</code>')],
    lede=('Apron deploys Hangar onto a Kubernetes cluster: it onboards a cluster you already have, or creates a local one first. When this was '
          'written it did that by copying a template repo and rewriting it with one script. kubara, an open-source GitOps platform framework from '
          'STACKIT, does the same job with a CLI, versioned catalogs and generated Helm values. This review compares the two and records the decision '
          'taken on October 16: Apron keeps its services in one kubara catalog, uses kubara as its only renderer, and lets DIY users install kubara\'s '
          'plain output without kubara.'),
    css=CSS)

BODY = r'''
<div class="apron">
<p class="note"><b>Since then.</b> v0.5 is built: the <code>apron</code> CLI (<code>init</code>, <code>render</code>, <code>up</code>, <code>fleet</code>, <code>identity</code>, <code>verify</code>, <code>resume</code>, <code>down</code>) replaced the script on October 16, 2026, with templates harvested from the live clusters, profiles independent of runtimes and Traefik on every cluster, and both lab clusters were rebuilt with it the next day. Tower now deploys as an Airframe app. The kubara port (v1) has not started. This page is the review and decision as written.</p>
<div class="verdict">
  <span class="stamp">Verdict · adopt kubara, build on it, give back</span>
  <h2>kubara and Apron solve the same problem. Adopt kubara, and move Apron's best ideas into it.</h2>
  <ul>
    <li><b>Same layer, same shape.</b> Both take one config file and produce the Argo CD state that installs a cluster's baseline. kubara regenerates on every change and versions its add-ons as OCI catalogs. Apron copies a repo once and rewrites it with <code>sed</code>, so it can't upgrade a fleet.</li>
    <li><b>Apron becomes a thin kubara catalog.</b> It keeps only what is Hangar's: the service catalog, platform CI/CD, Autopilot, Backstage, the second Argo CD. cert-manager, External Secrets, Kyverno, Prometheus, Loki and Crossplane come from kubara's general catalog today.</li>
    <li><b>Generic pieces go upstream, not into Apron.</b> Argo Rollouts, Sloth, Thanos, Tempo and an Infisical secret store are useful to every kubara user. Contribute them to kubara's general catalog, and ship them from Apron only until they land.</li>
    <li><b>The script stays, as <code>apron check</code>, and points the way for kubara.</b> kubara validates each service's settings on its own, but can't say "an upper cluster can't run the CI/CD control plane". <code>apron check</code> enforces those rules now; proposing catalog-level rules to kubara is how it becomes unnecessary.</li>
    <li><b>One catalog, one renderer, DIY from the output.</b> Apron's services are a kubara catalog (kubara's word for what you might call a profile), rendered only by kubara. What kubara writes to Git is plain Helm charts, values and Argo CD ApplicationSets, so a DIY user installs that with Helm and Argo CD and never runs kubara.</li>
    <li><b>Apron stays self-contained, and you name the cluster.</b> One script, <code>apron up dev --name dev</code> or <code>apron up prod --name prod</code>, onboards Hangar onto an existing cluster, or creates a local one on kiac or kind first, then generates, bootstraps and verifies it. kubara is a pinned tool the script drives, like kind or Helm; the apron catalog ships inside the repo, and nothing else in Hangar has to exist first.</li>
    <li><b>Every Hangar cluster is its own kubara hub.</b> kubara's default is one hub that holds every spoke's kubeconfig. That's the setup ADR-0005 rejected, and kubara supports the alternative natively.</li>
  </ul>
</div>

<section>
  <h2>What kubara is</h2>
  <div class="prose">
    <p>kubara is a single Go binary, Apache-2.0, that started inside STACKIT and was open-sourced in 2026. You describe clusters and the services each one runs in <code>config.yaml</code>. <code>kubara generate</code> merges that with one or more <b>catalogs</b> and writes reviewable files to Git: reusable charts under <code>platform-components/</code>, per-cluster values under <code>platform-configs/&lt;cluster&gt;/</code>. <code>kubara bootstrap</code> installs Argo CD and a few CRDs once. From then on Argo CD reconciles, and kubara isn't running.</p>
    <p>A catalog is to a platform what a Helm chart is to an app. It holds a <code>Catalog.yaml</code> with a plain semver version, one <code>ServiceDefinition</code> per service, the charts, and Go templates (<code>.tplt</code>, with Sprig) for each cluster's values. Catalogs are published as OCI artifacts and listed per cluster, in order. kubara ships two: <code>bootstrap</code> (Argo CD, CRDs) and <code>general</code> (17 services, from cert-manager to Velero).</p>
    <p>On each cluster, the bootstrap catalog's Argo CD chart creates one ApplicationSet per service. Each selects clusters labelled <code>&lt;service&gt;: enabled</code> and layers values in a fixed order: chart defaults, then <code>values.generated.yaml</code>, then <code>additional-values.yaml</code>, then any <code>values-*.yaml</code> you add. Generated files are never hand-edited; your changes live in the last two.</p>
  </div>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 360" role="img" aria-label="config.yaml and three catalogs (bootstrap, general, apron) feed apron check then kubara generate, which writes platform-components and platform-configs to Git; each cluster's Argo CD reconciles from Git.">
      <defs>
        <marker id="g1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker>
        <marker id="g1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah-a"/></marker>
      </defs>
      <text x="20" y="22" class="t-eyebrow">INPUTS</text>
      <rect x="20" y="36" width="170" height="58" rx="5" class="box"/><text x="34" y="60" class="t-lbl">config.yaml</text><text x="34" y="78" class="t-mono">clusters, services</text>
      <rect x="20" y="108" width="170" height="44" rx="5" class="box"/><text x="34" y="128" class="t-lbl">bootstrap catalog</text><text x="34" y="143" class="t-mono">argo-cd, crds</text>
      <rect x="20" y="162" width="170" height="44" rx="5" class="box"/><text x="34" y="182" class="t-lbl">general catalog</text><text x="34" y="197" class="t-mono">17 services</text>
      <rect x="20" y="216" width="170" height="54" rx="5" class="us"/><text x="34" y="238" class="t-lbl">apron catalog</text><text x="34" y="256" class="t-mono">Hangar services</text>
      <text x="20" y="296" class="t-sm">OCI, pinned per cluster,</text>
      <text x="20" y="312" class="t-sm">merged in listed order</text>

      <rect x="232" y="110" width="128" height="74" rx="5" class="us"/><text x="246" y="134" class="t-lbl">apron check</text><text x="246" y="152" class="t-mono">zone/role rules</text><text x="246" y="167" class="t-mono">secrets, fleet record</text>
      <rect x="392" y="110" width="128" height="74" rx="5" class="box"/><text x="406" y="134" class="t-lbl">kubara generate</text><text x="406" y="152" class="t-mono">.tplt → values</text><text x="406" y="167" class="t-mono">schema per cluster</text>
      <path d="M190 66 L230 130" class="edge" marker-end="url(#g1)"/>
      <path d="M190 130 L230 142" class="edge" marker-end="url(#g1)"/>
      <path d="M190 184 L230 160" class="edge" marker-end="url(#g1)"/>
      <path d="M190 240 L230 172" class="edge-a" marker-end="url(#g1a)"/>
      <path d="M360 147 L390 147" class="edge" marker-end="url(#g1)"/>

      <text x="560" y="22" class="t-eyebrow">GIT · REVIEWED</text>
      <rect x="560" y="36" width="200" height="66" rx="5" class="box"/><text x="574" y="60" class="t-lbl">platform-components/</text><text x="574" y="78" class="t-mono">helm/&lt;service&gt;/ charts</text><text x="574" y="93" class="t-mono">regenerated</text>
      <rect x="560" y="112" width="200" height="88" rx="5" class="box"/><text x="574" y="136" class="t-lbl">platform-configs/</text><text x="574" y="154" class="t-mono">&lt;cluster&gt;/helm/&lt;svc&gt;/</text><text x="574" y="170" class="t-mono">values.generated.yaml</text><text x="574" y="186" class="t-mono">values-*.yaml (yours)</text>
      <path d="M520 140 L558 80" class="edge" marker-end="url(#g1)"/>
      <path d="M520 152 L558 156" class="edge" marker-end="url(#g1)"/>
      <rect x="560" y="236" width="200" height="74" rx="5" class="okb"/><text x="574" y="260" class="t-lbl">Argo CD on each cluster</text><text x="574" y="278" class="t-mono">one ApplicationSet</text><text x="574" y="293" class="t-mono">per enabled service</text>
      <path d="M660 202 L660 234" class="edge" marker-end="url(#g1)"/>
      <text x="232" y="232" class="t-sm">kubara runs at generate time only.</text>
      <text x="232" y="248" class="t-sm">Re-running it after a catalog bump is</text>
      <text x="232" y="264" class="t-sm">the fleet upgrade: the diff is the PR.</text>
    </svg>
    </div>
    <figcaption><b>Figure 1</b>The proposed flow. kubara's pieces are grey; Apron's are blue. Apron becomes one catalog plus a check that runs before generation.</figcaption>
  </figure>
</section>

<section>
  <h2>Apron and kubara, side by side</h2>
  <div class="prose"><p>The two tools started from the same pain: hand-maintained cluster repos that drift apart. kubara solved generation and upgrades. Apron solved fleet safety rules and Hangar's specific stack.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Concern</th><th>Apron today</th><th>kubara</th><th>Better</th></tr></thead>
    <tbody>
      <tr><td class="area">Input</td><td><code>cluster.yaml</code>, deleted after one run</td><td><code>config.yaml</code>, committed, all clusters in one file</td><td><span class="chip c-ok">kubara</span></td></tr>
      <tr><td class="area">Rendering</td><td>Literal <code>sed</code> over a copy of a live cluster; macOS only</td><td>Go templates with Sprig, reading the cluster, its services and the catalog</td><td><span class="chip c-ok">kubara</span></td></tr>
      <tr><td class="area">Re-runnable</td><td>No; run once on a fresh clone</td><td>Yes; generated files are rewritten, yours are left alone</td><td><span class="chip c-ok">kubara</span></td></tr>
      <tr><td class="area">Versioning</td><td>None; each cluster repo is a fork</td><td>OCI catalogs, immutable semver, pinned per cluster</td><td><span class="chip c-ok">kubara</span></td></tr>
      <tr><td class="area">Per-service validation</td><td>Field presence in the script</td><td><code>configSchema</code> per service; <code>kubara schema</code> for editors</td><td><span class="chip c-ok">kubara</span></td></tr>
      <tr><td class="area">Cross-cluster rules</td><td>Zone and role invariants, refused before writing</td><td>Only hub vs spoke per service</td><td><span class="chip c-ok">Apron</span></td></tr>
      <tr><td class="area">Topology</td><td>Every cluster runs and pulls with its own Argo CD</td><td>Default: hub holds spoke kubeconfigs. A hub with no spokes works too</td><td><span class="chip c-info">compatible</span></td></tr>
      <tr><td class="area">Secrets</td><td>Infisical via ESO; fresh passwords per cluster</td><td>ESO with a backend you choose; OpenBao locally, Bitwarden in examples</td><td><span class="chip c-info">compatible</span></td></tr>
      <tr><td class="area">Stack opinions</td><td>Traefik, Thanos, Tempo, Rollouts, Sloth, Crossplane, Tekton</td><td>Traefik, oauth2-proxy, Homer, Velero, Longhorn, MetalLB</td><td><span class="chip c-info">overlap on Traefik</span></td></tr>
      <tr><td class="area">Provisioning</td><td>None (kind config only)</td><td>Optional Terraform for STACKIT and T Cloud; <code>--local</code> kind for evaluation</td><td><span class="chip c-info">neither for Hangar</span></td></tr>
      <tr><td class="area">Maturity</td><td>Built for two live clusters</td><td>Young: config schema <code>v1alpha5</code>, releases every two weeks, migrations in the CLI</td><td><span class="chip c-warn">pin it</span></td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>What the Apron code shows today</h2>
  <div class="prose"><p>These are the reasons to move, and which ones kubara fixes on its own.</p></div>
  <div class="findings">
    <div class="finding sev-high"><div class="top"><span class="chip c-bad">high</span><span class="id">AP-1</span><h3>Every cluster repo is a fork, so upgrades go back to hand diffs</h3><span class="chip c-ok">kubara fixes</span></div>
      <p>The script deletes <code>cluster.yaml</code> and isn't safe to re-run. Each cluster keeps its own copy of 38 Applications and about 62,000 lines of vendored installs. Bumping cert-manager across the fleet is N pull requests on N diverging copies, the drift Apron was built to stop. It only stops it on day 0.</p></div>
    <div class="finding sev-med"><div class="top"><span class="chip c-warn">medium</span><span class="id">AP-2</span><h3>The substitution only runs on macOS</h3><span class="chip c-ok">kubara fixes</span></div>
      <p><code>substitute()</code> calls <code>sed -i '' "s|…|…|g"</code>, which is BSD syntax. GNU sed reads <code>''</code> as the script, so the run fails on Linux and in CI. Templating replaces <code>sed</code> entirely.</p></div>
    <div class="finding sev-med"><div class="top"><span class="chip c-warn">medium</span><span class="id">AP-3</span><h3>Install order is a folder-name convention</h3><span class="chip c-warn">still open</span></div>
      <p>The <code>00-</code> to <code>60-</code> prefixes read as an order, but every Application starts at once; one manifest in the repo has a sync wave. kubara has the same property: one ApplicationSet per service, all in parallel, with a retry limit of 5 and a 5-minute maximum backoff. Crossplane packages before the XRs that need them is the case to test.</p></div>
    <div class="finding sev-low"><div class="top"><span class="chip c-info">low</span><span class="id">AP-4</span><h3>The template is a curated copy of a live cluster</h3><span class="chip c-ok">kubara fixes</span></div>
      <p>Substitution targets are real names from <code>the old dev cluster</code> and <code>the prod cluster</code>, which is why the script must skip <code>hack/</code> and order rules longest-first. Templates with parameters remove this class of bug.</p></div>
    <div class="finding sev-low"><div class="top"><span class="chip c-info">low</span><span class="id">AP-5</span><h3>Housekeeping</h3></div>
      <p>Two <code>.DS_Store</code> files are committed. AI triage has no <code>components.aiTriage</code> toggle yet, as the README notes.</p></div>
  </div>
</section>

<section>
  <h2>Apron as a kubara catalog</h2>
  <div class="prose">
    <p>Each of today's <code>components.*</code> toggles becomes a <code>ServiceDefinition</code>. Where kubara's general catalog already ships the same service, Hangar uses kubara's and supplies its own values in <code>values-hangar.yaml</code>. Where it doesn't, the <code>apron</code> catalog ships the chart. Name collisions fail by default in kubara, so Apron never redefines a general service by accident.</p>
  </div>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 330" role="img" aria-label="Which catalog provides each service: bootstrap provides Argo CD and CRDs; general provides cert-manager, external-secrets, kyverno, kube-prometheus-stack, loki, crossplane, metrics-server; apron provides the rest; traefik, homer, velero, longhorn, metallb disabled.">
      <rect x="10" y="10" width="760" height="56" rx="6" class="band"/>
      <text x="24" y="32" class="t-eyebrow">BOOTSTRAP · kubara</text>
      <text x="24" y="52" class="t-sm">installed by kubara bootstrap</text>
      <rect x="250" y="20" width="120" height="36" rx="4" class="box"/><text x="262" y="43" class="t-lbl">argo-cd</text>
      <rect x="380" y="20" width="120" height="36" rx="4" class="box"/><text x="392" y="43" class="t-lbl">bootstrap-crds</text>
      <rect x="10" y="76" width="760" height="100" rx="6" class="band"/>
      <text x="24" y="98" class="t-eyebrow">GENERAL · kubara</text>
      <text x="24" y="118" class="t-sm">used with Hangar values</text>
      <rect x="250" y="86" width="120" height="36" rx="4" class="okb"/><text x="262" y="109" class="t-lbl">cert-manager</text>
      <rect x="380" y="86" width="120" height="36" rx="4" class="okb"/><text x="392" y="109" class="t-lbl">external-secrets</text>
      <rect x="510" y="86" width="120" height="36" rx="4" class="okb"/><text x="522" y="109" class="t-lbl">kyverno</text>
      <rect x="640" y="86" width="120" height="36" rx="4" class="okb"/><text x="652" y="109" class="t-lbl">crossplane</text>
      <rect x="250" y="130" width="120" height="36" rx="4" class="okb"/><text x="262" y="153" class="t-lbl">kube-prom-stack</text>
      <rect x="380" y="130" width="120" height="36" rx="4" class="okb"/><text x="392" y="153" class="t-lbl">loki</text>
      <rect x="510" y="130" width="120" height="36" rx="4" class="okb"/><text x="522" y="153" class="t-lbl">metrics-server</text>
      <rect x="640" y="130" width="120" height="36" rx="4" class="box"/><text x="652" y="148" class="t-sm">traefik on; homer,</text><text x="652" y="161" class="t-sm">velero… off</text>
      <rect x="10" y="186" width="760" height="134" rx="6" class="band"/>
      <text x="24" y="208" class="t-eyebrow">APRON · Hangar</text>
      <text x="24" y="228" class="t-sm">ships the chart</text>
      <text x="24" y="296" class="t-mono">ghcr.io/jfillman/</text><text x="24" y="310" class="t-mono">catalogs/apron</text>
      <rect x="250" y="196" width="120" height="36" rx="4" class="us"/><text x="262" y="219" class="t-lbl">infisical</text>
      <rect x="380" y="196" width="120" height="36" rx="4" class="us"/><text x="392" y="219" class="t-lbl">gateway routes</text>
      <rect x="510" y="196" width="120" height="36" rx="4" class="us"/><text x="522" y="219" class="t-lbl">argo-rollouts</text>
      <rect x="640" y="196" width="120" height="36" rx="4" class="us"/><text x="652" y="219" class="t-lbl">sloth</text>
      <rect x="250" y="240" width="120" height="36" rx="4" class="us"/><text x="262" y="263" class="t-lbl">thanos · tempo</text>
      <rect x="380" y="240" width="120" height="36" rx="4" class="us"/><text x="392" y="263" class="t-lbl">service-catalog</text>
      <rect x="510" y="240" width="120" height="36" rx="4" class="us"/><text x="522" y="263" class="t-lbl">argocd-apps</text>
      <rect x="640" y="240" width="120" height="36" rx="4" class="us"/><text x="652" y="263" class="t-lbl">cluster-registry</text>
      <rect x="250" y="282" width="120" height="30" rx="4" class="warnb"/><text x="262" y="302" class="t-lbl">platform-cicd</text>
      <rect x="380" y="282" width="120" height="30" rx="4" class="warnb"/><text x="392" y="302" class="t-lbl">autopilot</text>
      <rect x="510" y="282" width="120" height="30" rx="4" class="warnb"/><text x="522" y="302" class="t-lbl">backstage</text>
      <rect x="640" y="282" width="120" height="30" rx="4" class="box"/><text x="652" y="302" class="t-sm">+ otel, minio, …</text>
    </svg>
    </div>
    <figcaption><b>Figure 2</b>Where each service comes from at first. Infisical, Rollouts, Sloth, Thanos and Tempo in the Apron band are generic and should move up into kubara's general catalog. Amber services are role-gated: <code>apron check</code> refuses them on any cluster without the control-plane role.</figcaption>
  </figure>
  <div class="pair">
    <div><span class="cap">apron catalog repo</span>
<pre>apron/
  Catalog.yaml          <span class="c"># spec.version: 1.0.0</span>
  services/
    hangar.yaml         <span class="c"># zone + roles live here</span>
    infisical.yaml
    argocd-apps.yaml    <span class="c"># second Argo CD</span>
    platform-cicd.yaml
    autopilot.yaml
    …
  platform-components/helm/
    argocd-apps/ platform-cicd/ …
                        <span class="c"># today's Applications,</span>
                        <span class="c"># as charts</span>
  platform-configs/helm/
    argocd-apps/values.generated.yaml.tplt
    …
  hack/
    apron-check         <span class="c"># was customize-cluster.sh</span>
    cluster-identity.sh <span class="c"># unchanged</span></pre></div>
    <div><span class="cap">kubara config.yaml, one Hangar cluster</span>
<pre>version: v1alpha5
clusters:
  - name: kind-staging
    stage: upper
    type: hub             <span class="c"># its own Argo CD</span>
    dnsName: staging.hangar.example
    ingressClassName: traefik
    argocd:
      selfManaged: enabled
      repo: { … }
    catalogs:
      - oci://ghcr.io/kubara-io/catalogs/general:2026.42.1
      - oci://ghcr.io/jfillman/catalogs/apron:1.0.0
    services:
      hangar:
        status: enabled
        config: { zone: upper, roles: [workloads] }
      traefik:       { status: enabled }   <span class="c"># Hangar's gateway too</span>
      platform-cicd: { status: disabled }</pre></div>
  </div>
  <div class="prose">
    <p><b>Where zone and roles live.</b> kubara's cluster record has a free-form <code>stage</code> and a <code>type</code> of hub or spoke, nothing richer. An always-on <code>hangar</code> service carries <code>zone</code> and <code>roles</code> in its <code>configSchema</code>, so kubara types and checks them, and every template can read them through <code>.cluster.services.hangar.config</code>.</p>
  </div>
<pre><span class="c"># services/platform-cicd.yaml</span>
apiVersion: kubara.io/v1alpha1
kind: ServiceDefinition
metadata:
  name: platform-cicd
  annotations: { kubara.io/category: delivery }
spec:
  chartPath: platform-cicd
  status: disabled          <span class="c"># opt-in, control-plane only</span>
  clusterTypes: [hub]
  configSchema:
    type: object
    properties:
      cicdReady: { type: boolean, default: false }</pre>
  <div class="prose">
    <p><b>What <code>apron check</code> keeps doing.</b> Everything kubara can't express. It reads <code>config.yaml</code>, refuses the same combinations the script refuses today (an upper zone with <code>platform-cicd</code>, <code>provider-github</code>, <code>autopilot</code> or a full service catalog; a control-plane cluster outside the lower zone; Autopilot without the full catalog), generates the Infisical and Rekor passwords, renders cluster identity, and prints the <code>clusters.yaml</code> record. It runs before <code>kubara generate</code> locally and as a required CI check. What it drops: copying, directory deletion, and the whole <code>sed</code> table.</p>
    <p><b>How it goes upstream.</b> Rules that span services are a gap any multi-cluster kubara user hits. Propose a small addition to kubara: rules in <code>Catalog.yaml</code>, checked during <code>generate</code> and <code>schema</code>, for example "service <code>platform-cicd</code> requires <code>hangar.config.zone == lower</code>". Open it as an ADR in kubara's own format, with <code>apron check</code> as the working reference. Once it lands, Apron's rules move into its catalog and the check script retires.</p>
  </div>
</section>



<section>
  <h2>Decision: how Apron installs</h2>
  <div class="verdict" style="border-top-color:var(--ok)">
    <span class="stamp" style="color:var(--ok);background:var(--ok-bg)">Decided · October 16, 2026</span>
    <ul>
      <li><b>Catalog format:</b> kubara's, <code>Catalog.yaml</code> plus one <code>ServiceDefinition</code> per service. An open format already in use, not a Hangar invention.</li>
      <li><b>Renderer:</b> kubara only, pinned in <code>apron.lock</code> and installed by the <code>apron</code> script like kind or Helm.</li>
      <li><b>DIY:</b> supported through kubara's output. The rendered charts, values and ApplicationSets are committed to Git; anyone can install them with Helm and Argo CD alone.</li>
      <li><b>Profile and runtime are independent:</b> a profile (dev or prod) says what the cluster runs; the runtime (kiac, kind, or an existing cluster) says where. v1 supports existing clusters, kiac and kind, and any profile runs on any runtime.</li>
      <li><b>One name per cluster, chosen by you:</b> the name passed to <code>apron up --name</code> is the kubectl context, the fleet registry entry, the Infisical project stem, the issuer path and the hostname stem. It is recorded once, in the cluster's config; no tool, chart, template or script contains a cluster name.</li>
      <li><b>Gateway:</b> Traefik on every runtime, installed by Apron. <b>Argo CD:</b> two instances per cluster, both installed by Apron.</li>
      <li><b>Sequence:</b> for the October lab rebuild, Apron renders its own templates (name-free, tested against today's clusters). The kubara catalog port follows the rebuild.</li>
      <li><b>Not now:</b> a second, Helm-only renderer (two engines to keep equal); Sveltos (a hub pushing into clusters, ruled out by ADR-0005); vCluster and existing clusters (later runtimes).</li>
    </ul>
  </div>
  <div class="prose">
    <p><b>Naming.</b> kubara calls its packaged unit a <i>catalog</i>, and a cluster's entry in <code>config.yaml</code> its cluster profile. Apron uses <i>catalog</i> for its service set, to match, and <i>profile</i> for a named cluster shape: dev, prod or baseline.</p>
  </div>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 250" role="img" aria-label="The apron catalog and a profile go through kubara generate into Git as plain Helm and Argo CD output. Three ways to install it: apron up, kubara bootstrap, or DIY with helm and argocd.">
      <defs><marker id="d1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>
      <rect x="20" y="30" width="170" height="70" rx="5" class="us"/><text x="34" y="54" class="t-lbl">apron catalog</text><text x="34" y="72" class="t-mono">+ profile: dev · prod</text><text x="34" y="87" class="t-mono">  · baseline</text>
      <rect x="226" y="30" width="150" height="70" rx="5" class="box"/><text x="240" y="54" class="t-lbl">kubara generate</text><text x="240" y="72" class="t-mono">the only renderer</text><text x="240" y="87" class="t-mono">after apron check</text>
      <rect x="412" y="20" width="348" height="90" rx="5" class="okb"/><text x="426" y="44" class="t-lbl">Git: plain output</text><text x="426" y="62" class="t-mono">platform-components/helm/*  (charts)</text><text x="426" y="77" class="t-mono">platform-configs/&lt;cluster&gt;/  (values)</text><text x="426" y="92" class="t-mono">Argo CD ApplicationSets</text>
      <path d="M190 65 L224 65" class="edge" marker-end="url(#d1)"/>
      <path d="M376 65 L410 65" class="edge" marker-end="url(#d1)"/>
      <text x="20" y="150" class="t-eyebrow">THREE WAYS TO INSTALL THE SAME OUTPUT</text>
      <rect x="20" y="166" width="230" height="70" rx="5" class="box"/><text x="34" y="190" class="t-lbl">apron up</text><text x="34" y="208" class="t-mono">creates the cluster too</text><text x="34" y="223" class="t-mono">any runtime</text>
      <rect x="275" y="166" width="230" height="70" rx="5" class="box"/><text x="289" y="190" class="t-lbl">kubara bootstrap</text><text x="289" y="208" class="t-mono">existing cluster,</text><text x="289" y="223" class="t-mono">kubara users</text>
      <rect x="530" y="166" width="230" height="70" rx="5" class="box"/><text x="544" y="190" class="t-lbl">DIY</text><text x="544" y="208" class="t-mono">helm install argo-cd,</text><text x="544" y="223" class="t-mono">apply the ApplicationSets</text>
      <path d="M520 112 L135 164" class="edge" marker-end="url(#d1)"/>
      <path d="M560 112 L390 164" class="edge" marker-end="url(#d1)"/>
      <path d="M600 112 L645 164" class="edge" marker-end="url(#d1)"/>
    </svg>
    </div>
    <figcaption><b>Figure 3</b>One renderer, three ways in. DIY needs only Helm and Argo CD because what reaches Git is ordinary charts and manifests.</figcaption>
  </figure>
  <div class="prose">
    <p><b>Technology Apron should build on</b>, so Hangar doesn't end up imitating it:</p>
    <ul>
      <li><b>Gateway API</b> for every UI route. Both lab clusters already serve their UIs through a Gateway; the catalog ships <code>HTTPRoute</code>s, not Ingress.</li>
      <li><b>Renovate</b> to bump everything in <code>apron.lock</code> (kubara, catalog versions, chart pins) as reviewed PRs. kubara and its catalogs already use it.</li>
      <li><b>OCI artifacts</b> for publishing the apron catalog, as kubara publishes its own.</li>
      <li><b>Argo CD Agent</b>, later, for one view over many clusters without a hub that holds their credentials.</li>
      <li><b>vCluster</b> and <b>Cluster API</b>, later, as runtimes for per-PR clusters and real infrastructure.</li>
    </ul>
  </div>
</section>

<section>
  <h2>Installing Apron on its own</h2>
  <div class="prose">
    <p>Every Hangar component installs by itself. For Apron that means a person with a laptop and this one repo gets a working cluster without reading kubara's docs or cloning another Hangar repo. kubara changes what the script calls inside, not what the user runs. The tagline holds: one config file, one script, a known order.</p>
    <p>Apron's main job is onboarding: point it at a Kubernetes cluster and it deploys Hangar there. Local runtimes are a convenience that creates the cluster first and then runs exactly the same onboarding. Two choices describe a cluster. The <b>profile</b> says what it runs: <b>dev</b> is the lower-zone control plane that also hosts Infisical; <b>prod</b> is the upper-zone workloads cluster. The <b>runtime</b> says where it runs: kiac (one Apple <code>container</code> VM per node, with Cilium and a Gateway built in), kind (Docker or Podman, with Calico), or an existing cluster you already run, such as EKS or AKS. Any profile runs on any runtime; runtime-specific pieces such as the CNI or the gateway's ports follow the runtime, not the profile. You also give each cluster its name. The lab's rebuild happens to put <code>dev</code> on kiac and <code>prod</code> on kind, because that's the best use of its two machines.</p>
  </div>
<pre>./apron init prod --name my-cluster --runtime existing --context my-cluster --out ../gitops-my-cluster
./apron up --out ../gitops-my-cluster      <span class="c"># onboard Hangar onto a cluster you already have</span>

<span class="c"># the lab: create local clusters first, then the same onboarding</span>
./apron init dev  --name dev  --runtime kiac --out ../gitops-dev
./apron up --out ../gitops-dev      <span class="c"># lower zone, control plane, hosts Infisical</span>
./apron init prod --name prod --runtime kind --out ../gitops-prod
./apron up --out ../gitops-prod     <span class="c"># upper zone, workloads</span>
./apron up prod --runtime kind --baseline-only
                                   <span class="c"># Apron alone: no Airframe, Glidepath or Autopilot</span>
./apron resume --out ../gitops-dev   <span class="c"># runtime's own resume (e.g. kiac resume) + refresh hosts</span>
./apron verify --out ../gitops-dev   <span class="c"># runtime health check, then every Argo CD app healthy</span>
./apron down dev</pre>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 300" role="img" aria-label="apron up: check prerequisites and pin kubara, create the cluster on the chosen runtime from recorded flags, apron check, kubara generate with the bundled catalog, push, plant secrets, kubara bootstrap, verify and print URLs.">
      <defs><marker id="u1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>
      <text x="20" y="22" class="t-eyebrow">APRON UP · ONE RUN, IN ORDER</text>
      <rect x="20" y="40" width="130" height="80" rx="5" class="box"/><text x="32" y="62" class="t-mono">1 · tools</text><text x="32" y="82" class="t-lbl">Prerequisites</text><text x="32" y="99" class="t-sm">pin kubara into</text><text x="32" y="113" class="t-sm">./.bin</text>
      <rect x="172" y="34" width="130" height="44" rx="5" class="us"/><text x="184" y="54" class="t-lbl">kiac create</text><text x="184" y="70" class="t-mono">cilium · gateway</text>
      <rect x="172" y="86" width="130" height="44" rx="5" class="us"/><text x="184" y="106" class="t-lbl">kind create</text><text x="184" y="122" class="t-mono">+ calico v3.29.1</text>
      <text x="172" y="148" class="t-mono">2 · runtimes/*.yaml</text>
      <rect x="324" y="40" width="130" height="80" rx="5" class="box"/><text x="336" y="62" class="t-mono">3 · config</text><text x="336" y="82" class="t-lbl">Profile → entry</text><text x="336" y="99" class="t-sm">apron check</text><text x="336" y="113" class="t-sm">refuses bad combos</text>
      <rect x="476" y="40" width="130" height="80" rx="5" class="box"/><text x="488" y="62" class="t-mono">4 · render</text><text x="488" y="82" class="t-lbl">kubara generate</text><text x="488" y="99" class="t-sm">--catalog ./catalog</text><text x="488" y="113" class="t-sm">diff, then push</text>
      <rect x="628" y="40" width="132" height="80" rx="5" class="box"/><text x="640" y="62" class="t-mono">5 · secrets</text><text x="640" y="82" class="t-lbl">Plant per cluster</text><text x="640" y="99" class="t-sm">generated, never</text><text x="640" y="113" class="t-sm">committed</text>
      <path d="M150 80 L170 58" class="edge" marker-end="url(#u1)"/>
      <path d="M150 80 L170 108" class="edge" marker-end="url(#u1)"/>
      <path d="M302 58 L322 76" class="edge" marker-end="url(#u1)"/>
      <path d="M302 108 L322 86" class="edge" marker-end="url(#u1)"/>
      <path d="M454 80 L474 80" class="edge" marker-end="url(#u1)"/>
      <path d="M606 80 L626 80" class="edge" marker-end="url(#u1)"/>
      <path d="M694 122 L694 168" class="edge" marker-end="url(#u1)"/>
      <rect x="476" y="170" width="284" height="74" rx="5" class="box"/><text x="488" y="192" class="t-mono">6 · bootstrap</text><text x="488" y="212" class="t-lbl">kubara bootstrap</text><text x="488" y="230" class="t-sm">Argo CD, ESO CRDs, ClusterSecretStore</text>
      <path d="M474 207 L456 207" class="edge" marker-end="url(#u1)"/>
      <rect x="172" y="170" width="282" height="74" rx="5" class="okb"/><text x="184" y="192" class="t-mono">7 · verify</text><text x="184" y="212" class="t-lbl">Wait for every app healthy</text><text x="184" y="230" class="t-sm">write /etc/hosts block, print URLs</text>
      <text x="20" y="190" class="t-sm">Recorded flags only:</text>
      <text x="20" y="206" class="t-sm">the --cp-memory</text>
      <text x="20" y="222" class="t-sm">incident can't recur.</text>
      <text x="20" y="276" class="t-sm">Steps 3 to 7 are the same on both runtimes. Only step 2 differs, and it reads from a file, never from typed flags.</text>
    </svg>
    </div>
    <figcaption><b>Figure 4</b>What <code>apron up</code> does. Blue is the only runtime-specific step. kubara appears in steps 4 and 6 as a tool the script runs.</figcaption>
  </figure>
  <div class="tbl"><table>
    <thead><tr><th>Profile</th><th>Replaces in the lab</th><th>Zone · roles</th><th>Runtime</th><th>Turns on</th></tr></thead>
    <tbody>
      <tr><td class="area">dev</td><td><code>the dev cluster</code></td><td>lower · control-plane, workloads</td><td>any</td><td>Infisical host, platform CI/CD, full service catalog, Autopilot, observability</td></tr>
      <tr><td class="area">prod</td><td><code>the prod cluster</code></td><td>upper · workloads</td><td>any</td><td>Attached-tier catalog, Rollouts, Tower's cluster access (Tower itself deploys as an app); Infisical as a remote consumer</td></tr>
      <tr><td class="area">--baseline-only</td><td>none</td><td>either</td><td>any</td><td>Argo CD, cert-manager, ESO, Kyverno, Prometheus, Loki, Traefik. No other Hangar repo referenced</td></tr>
    </tbody>
  </table></div>
  <div class="prose">
    <p><b>Self-contained, concretely.</b> The apron catalog is a directory in the repo, passed to kubara as <code>--catalog ./catalog</code>, so no registry is needed; publishing it as OCI is for other users, not a requirement. The kubara binary and the general catalog version are pinned in <code>apron.lock</code>. Runtime flags live in the cluster's own config, recorded at <code>init</code>, which also fixes the lab's open gap: the old prod cluster's recreate steps were never written down.</p>
    <p><b>What still needs Git.</b> Argo CD reconciles from a repository, so <code>up</code> shows the generated diff and pushes only when told to. That is the one external dependency, the same as today.</p>
  </div>
</section>

<section>
  <h2>Keeping one Argo CD per cluster</h2>
  <div class="prose">
    <p>kubara's documented model is a hub that runs Argo CD and registers spokes, reading each spoke's kubeconfig from the secret backend. Glidepath ADR-0005 rejected exactly that: a hub holding every cluster's credentials is a path from dev to prod. kubara still fits, because nothing requires spokes. Declare every Hangar cluster as <code>type: hub</code> with <code>argocd.selfManaged: enabled</code> and it bootstraps and reconciles only itself, as Apron's clusters do now. kubara's own <code>--local</code> mode runs exactly this way.</p>
    <p>The zone line maps onto repos. Keep one kubara repo per zone, or per cluster as today. Upper clusters pin <code>argocd.repo.components.targetRevision</code> to a tag, so a catalog bump reaches them only through a reviewed merge.</p>
  </div>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 250" role="img" aria-label="Left: kubara default, hub Argo CD holds kubeconfigs for spokes. Right: Hangar, each cluster is its own hub pulling from Git, no shared credentials.">
      <defs>
        <marker id="t1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker>
        <marker id="t1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah-a"/></marker>
      </defs>
      <text x="20" y="22" class="t-eyebrow">KUBARA DEFAULT · HUB AND SPOKE</text>
      <rect x="110" y="40" width="160" height="62" rx="5" class="badb"/><text x="124" y="64" class="t-lbl">hub Argo CD</text><text x="124" y="82" class="t-mono">holds spoke kubeconfigs</text>
      <rect x="30" y="160" width="110" height="50" rx="5" class="box"/><text x="44" y="190" class="t-lbl">spoke: dev</text>
      <rect x="240" y="160" width="110" height="50" rx="5" class="box"/><text x="254" y="190" class="t-lbl">spoke: prod</text>
      <path d="M160 104 L100 158" class="edge-bad"/><path d="M100 158 L94 150" class="edge-bad"/>
      <path d="M220 104 L290 158" class="edge-bad"/>
      <text x="30" y="236" class="t-sm">One compromise reaches every spoke.</text>
      <line x1="390" y1="16" x2="390" y2="240" class="dash"/>
      <text x="410" y="22" class="t-eyebrow">HANGAR · EVERY CLUSTER A HUB</text>
      <rect x="510" y="40" width="170" height="62" rx="5" class="box"/><text x="524" y="64" class="t-lbl">Git (per zone)</text><text x="524" y="82" class="t-mono">generated + reviewed</text>
      <rect x="410" y="160" width="110" height="50" rx="5" class="okb"/><text x="422" y="182" class="t-lbl">dev</text><text x="422" y="198" class="t-mono">hub · lower</text>
      <rect x="540" y="160" width="110" height="50" rx="5" class="okb"/><text x="552" y="182" class="t-lbl">staging</text><text x="552" y="198" class="t-mono">hub · upper</text>
      <rect x="660" y="160" width="110" height="50" rx="5" class="okb"/><text x="672" y="182" class="t-lbl">prod</text><text x="672" y="198" class="t-mono">hub · upper</text>
      <path d="M465 158 L560 104" class="edge-a" marker-end="url(#t1a)"/>
      <path d="M595 158 L595 104" class="edge-a" marker-end="url(#t1a)"/>
      <path d="M715 158 L640 104" class="edge-a" marker-end="url(#t1a)"/>
      <text x="410" y="236" class="t-sm">Each pulls its own config. No cluster holds another's credentials.</text>
    </svg>
    </div>
    <figcaption><b>Figure 5</b>The same kubara output in two topologies. Arrows on the right point from each cluster to Git because each cluster pulls.</figcaption>
  </figure>
  <div class="callout">
    <b class="lbl">Worth a later look</b>
    <p>kubara's examples include an Argo CD Agent lab in which spokes pull manifests over outbound mTLS, with no hub kubeconfigs. That gives Tower one place to see every cluster while still honouring ADR-0005's reason. It's a candidate for revisiting that ADR, not a v1 dependency.</p>
  </div>
</section>

<section>
  <h2>Hangar on AWS and Azure</h2>
  <div class="prose">
    <p>Hangar will install on EKS and AKS through a Terraform module. Terraform builds the cloud: network, cluster, DNS, workload identity and the cluster's Infisical identity. Apron takes over inside the cluster, exactly as it does on a local runtime. The home-lab rebuild doesn't use any of this; it's the path for clusters that live in a cloud account.</p>
    <p>Three rules carry over from the lab. You name the cluster once, as <code>cluster_name</code>, and every resource takes its name from it. Terraform stops at Argo CD, so it never fights Argo CD over drift. Infisical is the only secrets backend: there is no AWS Secrets Manager or Azure Key Vault option.</p>
  </div>
<pre>terraform-hangar/
  modules/
    aws-cluster/        <span class="c"># VPC, EKS, node groups, EKS Pod Identity agent, Route 53 zone</span>
    azure-cluster/      <span class="c"># VNet, AKS with OIDC issuer + workload identity, Azure DNS zone</span>
    infisical-cluster/  <span class="c"># Infisical project, machine identity and its auth, project access</span>
    apron-bootstrap/    <span class="c"># cloud-agnostic: Argo CD, repo creds, Infisical creds, root app</span>
  hangar-aws/           <span class="c"># root: aws-cluster + infisical-cluster + apron-bootstrap</span>
  hangar-azure/         <span class="c"># root: azure-cluster + infisical-cluster + apron-bootstrap</span>
  examples/
    aws-prod/  azure-prod/</pre>
  <figure class="fig">
    <div class="scroll">
    <svg viewBox="0 0 780 400" role="img" aria-label="A root module hangar-aws or hangar-azure calls a cloud cluster module, infisical-cluster and apron-bootstrap. The cloud module creates the network, cluster and DNS; infisical-cluster creates the project and identity in Infisical; apron-bootstrap installs Argo CD and the root app, which pulls the Apron-rendered cluster repo from Git. In the cluster, External Secrets and provider-infisical read from Infisical with the identity.">
      <defs>
        <marker id="w1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker>
        <marker id="w1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah-a"/></marker>
      </defs>
      <text x="20" y="22" class="t-eyebrow">TERRAFORM · ONE APPLY</text>
      <rect x="20" y="36" width="160" height="72" rx="5" class="us"/><text x="34" y="60" class="t-lbl">hangar-aws</text><text x="34" y="78" class="t-mono">or hangar-azure</text><text x="34" y="96" class="t-mono">cluster_name = …</text>
      <rect x="220" y="30" width="170" height="54" rx="5" class="box"/><text x="234" y="52" class="t-lbl">aws-cluster</text><text x="234" y="70" class="t-mono">or azure-cluster</text>
      <rect x="220" y="96" width="170" height="54" rx="5" class="box"/><text x="234" y="118" class="t-lbl">infisical-cluster</text><text x="234" y="136" class="t-mono">infisical provider</text>
      <rect x="220" y="162" width="170" height="54" rx="5" class="box"/><text x="234" y="184" class="t-lbl">apron-bootstrap</text><text x="234" y="202" class="t-mono">helm + kubernetes</text>
      <path d="M180 62 L218 57" class="edge" marker-end="url(#w1)"/>
      <path d="M180 76 L218 120" class="edge" marker-end="url(#w1)"/>
      <path d="M180 92 L218 184" class="edge" marker-end="url(#w1)"/>

      <text x="430" y="22" class="t-eyebrow">WHAT EACH CREATES</text>
      <rect x="430" y="30" width="330" height="54" rx="5" class="band"/><text x="444" y="52" class="t-lbl">Cloud account</text><text x="444" y="70" class="t-mono">network · EKS/AKS · DNS zone · OIDC issuer</text>
      <rect x="430" y="96" width="330" height="54" rx="5" class="warnb"/><text x="444" y="118" class="t-lbl">Infisical (Cloud or self-hosted)</text><text x="444" y="136" class="t-mono">project &lt;cluster_name&gt; · machine identity</text>
      <path d="M390 57 L428 57" class="edge" marker-end="url(#w1)"/>
      <path d="M390 123 L428 123" class="edge" marker-end="url(#w1)"/>

      <rect x="220" y="250" width="540" height="130" rx="6" class="band"/>
      <text x="234" y="272" class="t-eyebrow">INSIDE THE NEW CLUSTER</text>
      <rect x="234" y="284" width="150" height="80" rx="5" class="okb"/><text x="248" y="308" class="t-lbl">Argo CD</text><text x="248" y="326" class="t-mono">root app</text><text x="248" y="341" class="t-mono">Terraform stops here</text>
      <rect x="404" y="284" width="160" height="80" rx="5" class="box"/><text x="418" y="308" class="t-lbl">Apron baseline</text><text x="418" y="326" class="t-mono">rendered cluster repo</text><text x="418" y="341" class="t-mono">prod profile</text>
      <rect x="584" y="284" width="164" height="80" rx="5" class="box"/><text x="598" y="308" class="t-lbl">ESO · provider-</text><text x="598" y="324" class="t-lbl">infisical</text><text x="598" y="342" class="t-mono">read secrets</text>
      <path d="M305 218 L305 282" class="edge" marker-end="url(#w1)"/>
      <path d="M384 324 L402 324" class="edge-a" marker-end="url(#w1a)"/>
      <path d="M564 324 L582 324" class="edge" marker-end="url(#w1)"/>
      <path d="M666 282 L640 152" class="edge-a" marker-end="url(#w1a)"/>
      <text x="20" y="300" class="t-sm">apron-bootstrap writes</text>
      <text x="20" y="316" class="t-sm">the identity's creds to</text>
      <text x="20" y="332" class="t-sm">a Secret; the cluster</text>
      <text x="20" y="348" class="t-sm">then pulls everything.</text>
    </svg>
    </div>
    <figcaption><b>Figure 6</b>Terraform builds the cloud and the Infisical identity, then installs Argo CD and Apron's root app. Everything after that is GitOps, the same as on the lab clusters. Blue arrows are pulls.</figcaption>
  </figure>
  <div class="tbl"><table>
    <thead><tr><th>Module</th><th>Creates</th><th>Key inputs</th><th>Outputs</th></tr></thead>
    <tbody>
      <tr><td class="area">aws-cluster</td><td>VPC, EKS, managed node groups, EKS Pod Identity agent, Route 53 zone</td><td><code>cluster_name</code>, region, Kubernetes version, node sizes</td><td>endpoint, CA, OIDC issuer URL, zone id</td></tr>
      <tr><td class="area">azure-cluster</td><td>VNet, AKS with OIDC issuer and workload identity on, Azure DNS zone</td><td><code>cluster_name</code>, location, Kubernetes version, node sizes</td><td>endpoint, CA, OIDC issuer URL, zone id</td></tr>
      <tr><td class="area">infisical-cluster</td><td><code>infisical_project</code>, <code>infisical_identity</code>, its auth method, <code>infisical_project_identity</code></td><td><code>cluster_name</code>, Infisical URL and org</td><td>identity credentials for the cluster</td></tr>
      <tr><td class="area">apron-bootstrap</td><td>argocd namespace, Argo CD, repo creds, Infisical creds Secret, root Application</td><td>kubeconfig parts, cluster repo URL, profile</td><td>the cluster's fleet record</td></tr>
    </tbody>
  </table></div>
  <div class="prose">
    <p><b>apron-bootstrap is <code>apron up</code> for a cluster that already exists.</b> It runs the same steps from Argo CD onward, and the cluster repo it points at is rendered by Apron from the same cluster config, with <code>runtime: existing</code>. The issuer comes from the cloud: EKS and AKS publish their own OIDC issuers, so cloud clusters skip the lab's publish-to-hangarplatform.dev step, and the fleet record carries the provider's issuer URL.</p>
    <p><b>Infisical, concretely.</b> The infisical-cluster module uses Infisical's own Terraform provider. Version 1 uses Universal Auth, the method Hangar's provider-infisical already uses, so its client secret passes from Terraform to a Kubernetes Secret. That puts it in Terraform state, so state lives in an encrypted remote backend (S3 with KMS, or an Azure Storage account). Infisical also offers AWS Auth and Azure Auth, and the provider has resources for both. They would remove the stored secret, which matches Hangar's keyless direction, once External Secrets and provider-infisical are confirmed to support them.</p>
  </div>
  <div class="callout">
    <b class="lbl">Decide before the first cloud cluster</b>
    <p>A cloud cluster must reach Infisical. The lab's Infisical runs on the dev cluster behind a home network, so AWS and Azure can't reach it. Pick one: Infisical Cloud, or a self-hosted Infisical with a public URL (for example a cloud cluster built with the dev profile, which hosts Infisical). The module takes the URL as an input either way.</p>
  </div>
  <div class="prose">
    <p><b>Moving it forward upstream.</b> kubara ships Terraform only for STACKIT and T Cloud, and its provider list is fixed in the CLI. The aws-cluster and azure-cluster modules are written as ordinary reusable modules first, then offered to kubara as AWS and Azure providers.</p>
  </div>
</section>

<section>
  <h2>Gaps settled, and what's left</h2>
  <div class="findings">
    <div class="finding sev-low"><div class="top"><span class="chip c-ok">decided</span><h3>Two Argo CD instances per cluster stay</h3></div>
      <p>Hangar keeps <code>argocd-platform</code> for the cluster's own baseline and <code>argocd-apps</code> for tenant apps (gitops-strategy §2). Apron installs both on every profile. kubara's bootstrap installs one Argo CD, so after the kubara port the second becomes an <code>argocd-apps</code> service in the apron catalog, together with tenant onboarding and the AppProject charts.</p></div>
    <div class="finding sev-low"><div class="top"><span class="chip c-ok">decided</span><h3>Traefik is the gateway on every runtime</h3></div>
      <p>Apron installs and owns Traefik, the Gateway API CRDs and the Gateway on every cluster, the way the prod cluster already does, and every UI is an <code>HTTPRoute</code> on it. The runtime only decides how traffic reaches it: port mappings on kind, a NodePort on kiac (kiac's own <code>--gateway</code> Traefik is no longer used), and a <code>LoadBalancer</code> Service, so an NLB or Azure load balancer, on EKS and AKS. kubara's general catalog also ships Traefik, so this choice carries straight into the port. Because routes are Gateway API, a cloud cluster can later swap to its native controller without touching apps.</p></div>
    <div class="finding sev-med"><div class="top"><span class="chip c-warn">for the port</span><h3>kubara's secret names differ from Hangar's</h3></div>
      <p>kubara's bootstrap Argo CD chart creates its own ExternalSecrets (the image pull secret and spoke credentials) and assumes a store named <code>&lt;cluster&gt;-&lt;stage&gt;</code> with keys at paths like <code>&lt;cluster&gt;/&lt;stage&gt;/cluster_secrets/docker_config</code>. Hangar uses one ClusterSecretStore, <code>platform-secret-store</code>, backed by Infisical projects named <code>platform-cicd-&lt;cluster&gt;</code> with flat keys such as <code>registry-credentials-dockerconfigjson</code>. Left alone, kubara's ExternalSecrets would look for a store and keys that don't exist and never sync. kubara lets later <code>values-*.yaml</code> files override its generated values, so Hangar points those references at its own store and keys; the lasting fix is a small upstream PR making the store name and key prefix configurable. Apron's own templates already use Hangar's names, so the rebuild isn't affected.</p></div>
    <div class="finding sev-low"><div class="top"><span class="chip c-info">check</span><h3>A young dependency</h3></div>
      <p>Config is at <code>v1alpha5</code> and the CLI carries migrations between versions; releases come every two weeks. Pin the kubara binary and both catalog versions in CI, and upgrade on purpose.</p></div>
  </div>
</section>

<section>
  <h2>Apron's purpose</h2>
  <p class="purpose">Apron deploys Hangar onto a Kubernetes cluster, under the name you choose, and keeps it there. It onboards a cluster you already run, or creates a local one on kiac or kind first. Anything another platform could use goes upstream.</p>
  <div class="cols">
    <div class="col is"><h3>Apron owns</h3><ul>
      <li>Onboarding any Kubernetes cluster to Hangar: the <code>apron</code> CLI's <code>init</code>, <code>up</code>, <code>verify</code>, <code>check</code></li>
      <li>Local runtimes as a convenience: kiac and kind recipes with recorded flags, plus <code>resume</code> and <code>down</code></li>
      <li>The dev, prod and baseline profiles</li>
      <li>Keeping the rendered output installable without kubara (the DIY path)</li>
      <li>The <code>apron</code> catalog: Hangar-only services, charts and value templates</li>
      <li>Hangar's upstream work on kubara: services, rules, providers</li>
      <li>Hangar values for kubara's general services</li>
      <li>Zone and role rules, enforced by <code>apron check</code> in CI</li>
      <li>Per-cluster secrets, cluster identity, and the fleet's <code>clusters.yaml</code></li>
      <li>Which kubara and catalog versions the fleet runs</li>
    </ul></div>
    <div class="col isnt"><h3>kubara and others own</h3><ul>
      <li>Generation, schema, bootstrap of Argo CD (kubara)</li>
      <li>Generic add-ons like cert-manager or Kyverno (kubara general)</li>
      <li>The clusters themselves: kiac and kind locally; EKS, AKS or Cluster API elsewhere (the Terraform modules build cloud clusters, then hand them to Apron)</li>
      <li>Delivering and promoting apps (Glidepath, Tower)</li>
    </ul></div>
  </div>
</section>

<section>
  <h2>Roadmap</h2>
  <div class="phases">
    <div class="phase now"><div class="ph"><span class="v">v0 · built Aug 19</span><h3>Template and script</h3><span class="chip c-ok">retired</span></div>
      <ul><li>One config, one script, folder-ordered bootstrap. Solves day 0 and the dev/prod drift that prompted it.</li></ul></div>
    <div class="phase next"><div class="ph"><span class="v">v0.5 · Oct 17</span><h3>Name-free Apron and the lab rebuild</h3><span class="chip c-ok">built</span></div>
      <ul>
        <li>Replace <code>customize-cluster.sh</code> with the <code>apron</code> CLI: <code>init</code> records the cluster's name, profile, runtime and repos; <code>up</code> runs a runtime phase (create on kiac or kind, or check an existing cluster) and then one onboarding phase for every runtime; <code>check</code> keeps today's rules; <code>fleet</code>, <code>identity</code> and <code>down</code> cover the rest. No <code>sed</code>, no cluster name or GitHub owner in any template.</li>
        <li>Templates harvested from what the dev and prod clusters run today, with a parity test proving they reproduce both clusters; profiles independent of runtimes; Traefik and both Argo CD instances on every cluster; Dex on prod.</li>
        <li>New cluster and tenants repos per cluster, created by <code>apron init --create-repos</code> or by hand; the old repos are left untouched.</li>
        <li>Tower moves out of the cluster baseline and deploys as an Airframe app with its own Postgres.</li>
      </ul>
      <p class="exit"><b>Done when</b>dev and prod are rebuilt with <code>apron up</code> and every Skyport walkthrough replays green.</p></div>
    <div class="phase"><div class="ph"><span class="v">v1</span><h3>Adopt kubara, start contributing</h3><span class="chip c-info">next</span></div>
      <ul>
        <li>Run <code>kubara bootstrap --local</code> with only the general catalog to learn its conventions on kind. Join the kubara Slack channel and introduce Hangar's use case.</li>
        <li>Port Apron's templates to a kubara catalog (<code>kubara catalog create apron</code>), keeping the <code>apron</code> CLI as the entry point; port Infisical, Rollouts, Sloth and the second Argo CD first, written to kubara's own chart and changelog conventions so they can be upstreamed unchanged.</li>
        <li>Point kubara's own ExternalSecrets at Hangar's store and keys through <code>values-*.yaml</code> overrides.</li>
        <li>In CI on every Apron PR, run <code>apron up prod --baseline-only</code> on kind (the runtime CI can run), then install the same rendered output a second time by the DIY path to prove it needs no kubara. File kubara gaps as kubara issues, not Apron workarounds.</li>
      </ul>
      <p class="exit"><b>Done when</b>the kubara-rendered output matches what v0.5 renders for both profiles, from a fresh clone of Apron alone, with no hand edits under <code>platform-components/</code>.</p></div>
    <div class="phase"><div class="ph"><span class="v">v2</span><h3>Upstream the generic, migrate the fleet</h3><span class="chip c-info">planned</span></div>
      <ul>
        <li>Open pull requests to <code>kubara-io/catalogs</code> for Argo Rollouts, Sloth, Thanos, Tempo and an Infisical secret store. Remove each from Apron as it ships in a general release.</li>
        <li>Propose cross-service catalog rules as a kubara ADR, with <code>apron check</code> as the reference implementation.</li>
        <li>Port the Hangar-only services: platform CI/CD, Autopilot, Backstage, the service catalog, the second Argo CD. Publish <code>ghcr.io/jfillman/catalogs/apron</code> as OCI.</li>
        <li>Migrate the prod cluster, then dev, by diffing rendered manifests against the live repos until empty. After that, recreating either is <code>apron down</code> then <code>apron up</code>.</li>
      </ul>
      <p class="exit"><b>Done when</b>a cert-manager bump is one change to a pinned catalog version, regenerated for every cluster and reviewed as one diff, and at least one Hangar service ships in kubara's general catalog.</p></div>
    <div class="phase"><div class="ph"><span class="v">v3</span><h3>Fleet view and promotion</h3><span class="chip c-warn">decide</span></div>
      <ul>
        <li>Publish each cluster's catalog versions to the cluster registry so Tower shows who's behind.</li>
        <li>Move catalog versions lower to upper with a PR at the zone line, by hand or as a Tower action.</li>
        <li>Evaluate Argo CD Agent against ADR-0005, and share the result with the kubara maintainers either way.</li>
        <li>Add a <code>vcluster</code> runtime; per-PR clusters inside dev become <code>apron up pr-N --runtime vcluster</code>.</li>
      </ul>
      <p class="exit"><b>Done when</b>a new apron version reaches the dev cluster first and waits as a PR on every upper cluster.</p></div>
    <div class="phase"><div class="ph"><span class="v">v4</span><h3>Apron as small as it can be</h3><span class="chip c-warn">explore</span></div>
      <ul>
        <li>With catalog rules upstream, move Apron's rules into <code>Catalog.yaml</code>; <code>apron check</code> becomes a thin call to kubara. The rest of the script stays, because the lab lifecycle is Apron's job.</li>
        <li>kubara's local mode only knows kind. Offer kiac as a second local runtime upstream, using Apron's recipe.</li>
        <li>Ship <code>hangar-aws</code> and <code>hangar-azure</code> Terraform modules on top of <code>apron-bootstrap</code>, with Infisical as the only secrets backend.</li>
        <li>Add a Cluster API runtime through ClusterClass, so a real cluster is one more <code>--runtime</code>.</li>
        <li>kubara's Terraform provider list is fixed in the CLI (STACKIT, T Cloud). Contribute a provider for wherever Hangar runs next, such as EKS, rather than building one inside Apron.</li>
      </ul>
      <p class="exit"><b>Done when</b>the apron catalog contains only Hangar's own services, every rule runs inside kubara, and <code>apron up</code> still works from Apron alone.</p></div>
  </div>
</section>

<section class="sources">
  <h3 style="font-family:var(--sans);font-size:.9rem;font-weight:600">Sources</h3>
  <ul>
    <li><a href="https://github.com/jfillman/apron" target="_blank" rel="noopener">jfillman/apron</a> README, <code>cluster.yaml.example</code>, <code>hack/customize-cluster.sh</code></li>
    <li><a href="https://github.com/jfillman/hangar" target="_blank" rel="noopener">jfillman/hangar</a> <code>docs/cluster-provisioning.md</code>, <code>docs/gitops-strategy.md</code>, <code>docs/local-clusters.md</code></li>
    <li><a href="https://github.com/kubara-io/kubara" target="_blank" rel="noopener">kubara-io/kubara</a> (also on <a href="https://codeberg.org/kubara-io/kubara" target="_blank" rel="noopener">Codeberg</a>): docs on catalogs, templating, ADR-0003, kind local mode, hub and spoke</li>
    <li><a href="https://github.com/kubara-io/catalogs" target="_blank" rel="noopener">kubara-io/catalogs</a>: bootstrap and general catalogs, Argo CD ApplicationSet chart</li>
        <li><a href="https://docs.kubara.io/latest-stable/" target="_blank" rel="noopener">kubara documentation</a></li>
    <li>Artem Lajko, <a href="https://itnext.io/what-is-kubara-a-gitops-first-approach-to-reusable-kubernetes-platforms-3f91a060b39c" target="_blank" rel="noopener">What is kubara?</a> and <a href="https://itnext.io/kubara-an-open-source-kubernetes-platform-framework-built-on-gitops-8990b8a635b3" target="_blank" rel="noopener">kubara: an open source Kubernetes platform framework</a>, ITNEXT</li>
  </ul>
</section>
</div>
'''

P.add(BODY)
