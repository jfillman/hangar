"""Overview set (docs/overview/diagrams): five high-level pictures of Hangar. Kit in ov.py."""
from ov import *

def o_change():
    f = Fig('hangar-change')
    W, H = 1000, 404
    A = f.add
    A(zone(588, 68, 392, 264, 'Clusters · dev and prod · built from Apron', href='/docs/apron/', icon='apron'))
    # connectors first
    f.arrow([(144, 132), (176, 132)])
    f.arrow([(144, 252), (176, 252)])
    f.arrow([(336, 132), (408, 132)], 'acc'); A(hlab(336, 408, 132, 'PR', 'acc'))
    f.arrow([(336, 252), (408, 252)]); A(hlab(336, 408, 252, 'scoped PR'))
    f.arrow([(536, 240), (612, 240)], 'acc'); A(hlab(536, 612, 240, 'webhook', 'acc'))
    f.arrow([(612, 268), (536, 268)], dashed=True); A(hlab(536, 612, 268, 'release PR', below=True))
    f.arrow([(472, 288), (472, 316), (896, 316), (896, 284)], 'acc'); A(label(820, 298, 'pull', 'acc'))
    f.arrow([(896, 220), (896, 164)]); A(vlab(896, 164, 220, 'XR'))
    f.arrow([(828, 132), (748, 132)]); A(hlab(748, 828, 132, 'composes'))
    f.arrow([(612, 120), (568, 120), (568, 44), (256, 44), (256, 96)], 'lnk', dashed=True)
    # nodes, in reading order
    A(item(1, 'Step 1: a developer asks Tower for something',
           node(24, 104, 120, 56, 'Developers', 'self-service', 'input')
           + node(176, 96, 160, 72, 'Tower', 'Backstage portal', tag='experience', href='/tower/', icon='tower')
           + badge(336, 96, 1)))
    A(item(2, 'Step 2: Tower opens a pull request; a reviewed, merged commit is the only thing that crosses',
           node(408, 96, 128, 192, 'GitHub', 'reviewed commits', 'focal', tag='boundary', href='/principles/#reviewed-commits')
           + f'<text class="lbl lbl-acc" x="472" y="252" text-anchor="middle">ONLY A MERGED</text>'
           + f'<text class="lbl lbl-acc" x="472" y="264" text-anchor="middle">COMMIT CROSSES</text>'
           + badge(536, 96, 2)))
    A(item(3, 'Step 3: Glidepath builds, tests and signs it on the dev cluster',
           node(612, 220, 136, 64, 'Glidepath', 'build · sign', tag='delivery', href='/cicd/', icon='glidepath') + badge(748, 220, 3)))
    A(item(4, 'Step 4: each cluster\'s ArgoCD pulls the merged change',
           node(828, 220, 136, 64, 'ArgoCD', 'one per cluster · pulls', 'external', href='/stack/') + badge(964, 220, 4)))
    A(item(5, 'Step 5: Airframe turns the XR into real resources',
           node(828, 100, 136, 64, 'Airframe', 'Crossplane', tag='control plane', href='/docs/airframe/', icon='airframe') + badge(964, 100, 5)))
    A(item(5, 'Step 5: the Skyport apps run',
           node(612, 100, 136, 64, 'Skyport apps', 'flight-api · baggage-api', href='/run/')))
    A(item(6, 'Step 6: events, traces and SLOs flow back to Tower',
           label(412, 26, 'events · traces · SLOs', 'link') + badge(484, 32, 6)))
    A(item(7, 'Step 7: AI agents take the same road through Clearance, with less authority',
           node(24, 224, 120, 56, 'AI agents', 'any agent workload', 'input')
           + node(176, 216, 160, 72, 'Autopilot', 'Clearance gateway', tag='ai workloads', href='/autopilot/', icon='autopilot')
           + badge(336, 216, 7)))
    A(drawpath(2, [(336, 132), (408, 132)]))
    A(drawpath(4, [(472, 288), (472, 316), (896, 316), (896, 284)]))
    A(legend(372, [('input', 'People and agents'), ('backend', 'Hangar product'), ('external', 'Third-party tool'),
                   ('focal', 'The only crossing'), ('acc', 'A change'), ('muted-dash', 'Write-back'), ('lnk-dash', 'Events back')]))
    return page(
        n=1, slug='hangar-change', W=W, H=H, mode='reveal', steps=7,
        eyebrow='Hangar · How a change moves', title='One road from intent to production',
        lede='Everything in Hangar meets at one place: a reviewed, merged commit. People ask Tower, agents ask '
             'Autopilot, and from there the same pipeline builds, proves and releases to every cluster.',
        desc='A developer asks Tower for a change, which becomes a pull request on GitHub. A reviewed, merged commit is the '
             'only thing that crosses into the clusters: Glidepath builds and signs it, each cluster\'s ArgoCD pulls it, and '
             'Airframe composes what the Skyport apps need. Events flow back to Tower. AI agents follow the same road through '
             'Autopilot\'s Clearance gateway, with less authority.',
        body=f.svg(),
        hint='Plays once on load. Click any box to open its page; numbered badges give the reading order.',
        notes=[
            ('The idea', '<p>The home page\'s job is the one-breath version of Hangar. This draws the platform as the road a '
                         'change travels, with GitHub as the wall in the middle. It is principle 2 (every change is a reviewed '
                         'commit) made visible, and it is the same story the flight path tells further down the page.</p>'),
            ('Motion and clicks', '<ul><li><b>Reveal</b>, plays once on load (7 steps, about 5 seconds), then stays complete. '
                                  'Replay and step controls underneath.</li><li>Every product box links to its page; the Apron '
                                  'zone label links to the Apron docs.</li><li>Autopilot arrives last, as step 7: '
                                  'present, but no longer the headline.</li></ul>'),
            ('Budget', '<p>9 nodes, 10 connectors, 2 accent elements (the boundary and the change path), 1 zone. Within the '
                       'skill\'s limits with no room to spare, which is about right for a home page.</p>'),
        ])


LAYERS = [  # top to bottom
    ('exp', 'L5', 'Experience', 'Tower', 'Backstage · Tower plugin · TechDocs', 'One place to look. Every change becomes a PR.',
     '/tower/', 'backend', None,
     'People should look in one place, and every change they make there should become a pull request.',
     [('Backstage', 'built'), ('Tower', 'built'), ('TechDocs', 'built')]),
    ('ai', 'L4', 'AI workloads', 'Autopilot', 'Clearance · CEL policy · Preflight · AgentRun',
     'Same road, less authority, every call on record.', '/autopilot/', 'backend', 'early',
     'An agent is just another workload, with less authority by default and every call on the record.',
     [('Clearance', 'built'), ('CEL policy', 'built'), ('Preflight', 'built'), ('MCP', 'proposed'), ('AgentRun XR', 'proposed')]),
    ('del', 'L3', 'Delivery', 'Glidepath', 'Tekton · Chains · Sigstore · ArgoCD · Rollouts',
     'One small file in; a signed, verified release out.', '/cicd/', 'backend', None,
     'One small file for developers; a fixed, platform-owned path from a merged commit to a verified release. ArgoCD is the only thing that writes to a cluster, and each cluster has its own.',
     [('Tekton', 'built'), ('Pipelines-as-Code', 'built'), ('CDEvents broker', 'built'), ('Tekton Chains', 'built'), ('Conforma', 'built'), ('ArgoCD', 'built'), ('Argo Rollouts', 'built')]),
    ('cp', 'L2', 'Control plane', 'Airframe', 'Crossplane · XRDs · Functions · CloudNativePG',
     'The platform is an API that keeps itself true.', '/docs/airframe/', 'focal', None,
     'The platform is an API. An XR says what you want; reconciliation keeps it true afterwards.',
     [('Crossplane', 'built'), ('Airframe XRDs', 'built'), ('Composition Functions', 'built'), ('provider-github', 'built'), ('CloudNativePG', 'built')]),
    ('gr', 'L1', 'Ground', 'Apron', 'Kubernetes · Calico · Gateway API · cert-manager',
     'Every cluster starts from the same template.', '/docs/apron/', 'backend', None,
     'Every cluster starts from the same template and the same bootstrap order, with its own trust roots. Two today: dev and prod.',
     [('Kubernetes', 'built'), ('Calico', 'built'), ('Contour + Gateway API', 'built'), ('cert-manager', 'built'), ('Apron template', 'built')]),
]
RAILS = [
    ('sec', 768, ['Secrets,', 'identity,', 'policy'], ['Infisical', 'External Secrets', 'TokenReview', 'Kyverno'], '/sdlc/secure/',
     'Identity comes from the platform, not from secrets the platform has to guard. Policy runs at admission and at release.',
     [('Infisical', 'built'), ('External Secrets', 'built'), ('provider-infisical', 'built'), ('TokenReview', 'built'), ('Kyverno', 'built')]),
    ('obs', 880, ['Observability'], ['OpenTelemetry', 'Prometheus', 'Loki · Tempo', 'Sloth SLOs', 'DORA'], '/sdlc/operate/',
     'One trace per change, from commit to canary, and SLOs and DORA metrics that Tower shows next to every release.',
     [('OpenTelemetry', 'built'), ('Prometheus + Thanos', 'built'), ('Loki + Tempo', 'built'), ('Sloth', 'built'), ('DORA exporter', 'built')]),
]

def o_layers():
    W, H = 1000, 456
    out = []
    top, lh, gap = 40, 64, 8
    # direction indicator
    out.append(f'<text class="zt" x="56" y="56" text-anchor="middle">PEOPLE</text>')
    out.append(f'<text class="zt" x="56" y="388" text-anchor="middle">CLUSTERS</text>')
    out.append(f'<path class="a thin" d="M56,218 L56,70" marker-end="url(#hangar-layers-arrow)"/>')
    out.append(f'<path class="a thin" d="M56,218 L56,370" marker-end="url(#hangar-layers-arrow)"/>')
    items = []
    for i, (key, idx, name, prod, tools, why, href, kind, tag, *_rest) in enumerate(LAYERS):
        y = top + i * (lh + gap)
        tone = 'acc' if kind == 'focal' else 'ink'
        s = f'<rect class="mask" x="96" y="{y}" width="648" height="{lh}" rx="6"/>'
        s += f'<rect class="k k-{kind}" x="96" y="{y}" width="648" height="{lh}" rx="6"/>'
        s += f'<text class="lbl" x="112" y="{y + 36}">{idx}</text>'
        s += icon_svg(prod.lower(), 136, y + 14, 36)
        s += f'<text class="nm-l" x="184" y="{y + 30}">{esc(name)}</text>'
        pw = up4(len(prod) * 5.6 + 8)
        s += (f'<rect class="tagb t-{tone}" x="184" y="{y + 38}" width="{pw}" height="12" rx="2"/>'
              f'<text class="tagt t-{tone}" x="{184 + pw / 2:g}" y="{y + 47}" text-anchor="middle">{prod.upper()}</text>')
        if tag:
            tw = up4(len(tag) * 5.6 + 8)
            s += (f'<rect class="tagb t-link" x="{188 + pw}" y="{y + 38}" width="{tw}" height="12" rx="2"/>'
                  f'<text class="tagt t-link" x="{188 + pw + tw / 2:g}" y="{y + 47}" text-anchor="middle">{tag.upper()}</text>')
        assert len(tools) * 5.6 < 400, tools
        s += f'<text class="sub-l" x="728" y="{y + 28}" text-anchor="end">{esc(tools)}</text>'
        s += f'<text class="why" x="728" y="{y + 46}" text-anchor="end">{esc(why)}</text>'
        s += f'<text class="go" x="736" y="{y + 13}" text-anchor="end" aria-hidden="true">↗</text>'
        s = f'<a id="l-{key}" href="{SITE}{href}" target="_top" aria-label="{esc(name)}, {esc(prod)}: open its page">{s}</a>'
        items.append((5 - i, f'Layer {idx[1]}: {name}, built by {prod}', s))
    for step, aria, s in sorted(items):
        out.append(item(step, aria, s))
    rh = 5 * lh + 4 * gap
    for key, x, names, tools, href, *_ in RAILS:
        s = f'<rect class="mask" x="{x}" y="{top}" width="96" height="{rh}" rx="6"/>'
        s += f'<rect class="k k-store" x="{x}" y="{top}" width="96" height="{rh}" rx="6"/>'
        s += f'<text class="tagt t-ink" x="{x + 48}" y="{top + 18}" text-anchor="middle">RUNS THROUGH</text>'
        for j, n in enumerate(names):
            s += f'<text class="nm" x="{x + 48}" y="{top + 44 + j * 16}" text-anchor="middle">{esc(n)}</text>'
        for j, t in enumerate(tools):
            s += f'<text class="sub" x="{x + 48}" y="{top + 120 + j * 18}" text-anchor="middle">{esc(t)}</text>'
        s += f'<text class="go" x="{x + 88}" y="{top + rh - 8}" text-anchor="end" aria-hidden="true">↗</text>'
        s = f'<a id="l-{key}" href="{SITE}{href}" target="_top" aria-label="{esc(" ".join(names))}: open its page">{s}</a>'
        out.append(item(6, f'Cross-cutting: {" ".join(names)}', s))
    out.append(legend(424, [('backend', 'Hangar layer'), ('focal', 'The API everything drives'),
                            ('store', 'Runs through every layer')]))

    peeks = ['<div data-p="intro"><p class="eyebrow">Five layers, two rails</p><p>Point at a layer (or tab to it) to see '
             'what is in it and why. Click to open its page.</p></div>']
    css = []
    status = lambda st: f'<span class="st {st}">{st}</span>'
    for key, idx, name, prod, tools, why, href, kind, tag, long, tl in LAYERS:
        peeks.append(f'<div data-p="{key}"><p class="eyebrow">{idx} · {esc(name)} · {esc(prod)}</p><p>{esc(long)}</p>'
                     f'<p class="tl">{" ".join(f"<span>{esc(t)} {status(st)}</span>" for t, st in tl)}</p></div>')
    for key, x, names, tools, href, long, tl in RAILS:
        peeks.append(f'<div data-p="{key}"><p class="eyebrow">Runs through every layer · {esc(" ".join(names))}</p><p>{esc(long)}</p>'
                     f'<p class="tl">{" ".join(f"<span>{esc(t)} {status(st)}</span>" for t, st in tl)}</p></div>')
    for key in [l[0] for l in LAYERS] + [r[0] for r in RAILS]:
        sel = f'main:has(#l-{key}:hover), main:has(#l-{key}:focus-visible)'
        css.append(f'{sel.replace(")", ") .peek>[data-p=intro]")}{{display:none}}'.replace('main:has(#l-' + key + ':hover) .peek>[data-p=intro], main:has(#l-' + key + ':focus-visible) .peek>[data-p=intro]',
                   f'main:has(#l-{key}:hover) .peek>[data-p=intro], main:has(#l-{key}:focus-visible) .peek>[data-p=intro]'))
        css.append(f'main:has(#l-{key}:hover) .peek>[data-p={key}], main:has(#l-{key}:focus-visible) .peek>[data-p={key}]{{display:block}}')
    extra_css = '''
.peek{margin-top:.75rem;min-height:7.2rem;background:var(--card);border:1px solid var(--rule);border-radius:var(--r);padding:.8rem 1rem}
.peek>div{display:none}.peek>[data-p=intro]{display:block}
.peek p{margin:0 0 .45rem;font-size:.86rem;line-height:1.5;max-width:80ch}
.peek .tl{display:flex;flex-wrap:wrap;gap:.35rem .9rem;font:400 11px/1.4 var(--font-mono);color:var(--muted)}
.st{font-size:9px;letter-spacing:.08em;text-transform:uppercase;padding:0 .3rem;border:1px solid currentColor;border-radius:2px}
.st.built{color:var(--muted)} .st.proposed{color:var(--link)}
''' + '\n'.join(css)
    return page(
        n=2, slug='hangar-layers', W=W, H=H, mode='reveal', steps=6,
        eyebrow='Hangar · The stack', title='Five layers, one platform',
        lede='Hangar from the ground up: clusters from one template, an API that keeps itself true, a guarded road to '
             'production, agents with less authority, and one place for people to look.',
        desc='Hangar as a layer stack, from the clusters up: Ground (Apron), Control plane (Airframe), Delivery (Glidepath), '
             'AI workloads (Autopilot, early) and Experience (Tower). Secrets, identity and policy, and observability run '
             'through every layer.',
        body='\n'.join(out), after_svg='<div class="peek" aria-live="polite">' + ''.join(peeks) + '</div>',
        hint='Builds from the ground up on load. Point at a layer to preview it below; click to open its page.',
        extra_css=extra_css,
        notes=[
            ('The idea', '<p>The stack the site already describes on /stack/, compressed to five layers and two rails. It '
                         'answers "what is Hangar made of" rather than "how does a change move". Autopilot is one layer of '
                         'five, honestly tagged as early.</p>'),
            ('Motion and clicks', '<ul><li><b>Reveal</b>, bottom-up, so the platform is literally built from the ground '
                                  '(6 steps).</li><li>Two levels of detail with no script: hovering or tabbing to a layer '
                                  'fills the panel below with its tools and their status; clicking opens the page.</li></ul>'),
            ('Trade-off', '<p>It reads more like a table of contents than an architecture: no arrows, so it does not '
                          'show the GitOps boundary. It overlaps with the flight path lower down the home page.</p>'),
        ])


def o_clusters():
    f = Fig('hangar-clusters')
    W, H = 1000, 476
    A = f.add
    A(zone(24, 144, 456, 248, 'Dev cluster · built from Apron', align='right', href='/docs/apron/', icon='apron'))
    A(zone(520, 144, 456, 248, 'Prod cluster · built from Apron', align='right', href='/docs/apron/', icon='apron'))
    # connectors
    f.arrow([(816, 60), (640, 60), (640, 184)]); A(hlab(640, 816, 60, 'self-service'))
    f.arrow([(604, 184), (604, 76), (560, 76)], 'acc'); A(vlab(604, 76, 184, 'PR', 'acc', side='l'))
    f.arrow([(400, 56), (96, 56), (96, 184)], 'acc'); A(hlab(96, 400, 56, 'webhook', 'acc'))
    f.arrow([(120, 184), (120, 80), (400, 80)], dashed=True); A(hlab(120, 400, 80, 'release PR', below=True))
    f.arrow([(492, 96), (492, 348), (456, 348)], 'acc')
    f.arrow([(508, 96), (508, 348), (544, 348)], 'acc')
    f.arrow([(392, 320), (392, 256)]); A(vlab(392, 256, 320, 'deploys'))
    f.arrow([(252, 320), (252, 256)], dashed=True); A(vlab(252, 256, 320, 'agent run'))
    f.arrow([(824, 320), (824, 256)]); A(vlab(824, 256, 320, 'deploys'))
    # nodes
    A(node(400, 40, 160, 56, 'GitHub', 'reviewed, merged commits', 'focal', href='/principles/#reviewed-commits'))
    A(node(816, 40, 136, 56, 'Developers', 'self-service', 'input'))
    A(node(48, 184, 128, 72, 'Glidepath', 'build · sign', href='/cicd/', icon='glidepath'))
    A(node(188, 184, 128, 72, 'Autopilot', 'agent sandbox', 'propose', href='/autopilot/', icon='autopilot'))
    A(node(328, 184, 128, 72, 'Skyport apps', 'dev · test', href='/run/'))
    A(node(544, 184, 128, 72, 'Tower', 'Backstage', href='/tower/', icon='tower'))
    A(node(696, 184, 256, 72, 'Skyport apps', 'flight-api · baggage-api · canary', href='/run/'))
    A(node(48, 320, 408, 56, 'ArgoCD + Airframe', 'pulls from git · composes XRs', href='/docs/airframe/', icon='airframe'))
    A(node(544, 320, 408, 56, 'ArgoCD + Airframe', 'pulls from git · composes XRs', href='/docs/airframe/', icon='airframe'))
    A(item(1, 'No cluster holds credentials for another; each one pulls',
           '<text class="callout" x="500" y="420" text-anchor="middle">No cluster holds credentials for another. Each one pulls.</text>'))
    A('<g data-motion-item data-step="1" data-motion-decorative aria-hidden="true" focusable="false">'
      '<circle class="flow-token" cx="604" cy="184" r="5"/></g>')
    A(legend(444, [('input', 'People'), ('backend', 'Hangar product'), ('propose', 'Proposed runtime'),
                   ('focal', 'The only crossing'), ('acc', 'A change'), ('muted-dash', 'Write-back')]))
    css = '''
.flow-token{fill:var(--accent);opacity:0}
[data-motion-mode="loop"] .flow-token{animation:token-route 4.8s linear infinite}
:root:has(#pause:checked) .flow-token{animation-play-state:paused}
.pause{display:inline-flex;gap:.35rem;align-items:center;margin-top:.5rem;font:400 11px/1.4 var(--font-mono);color:var(--muted);cursor:pointer}
@media (prefers-reduced-motion: reduce){.pause{display:none}}
@keyframes token-route{
 0%{transform:translate(0,0);opacity:0} 4%{opacity:1}
 21.3%{transform:translate(0,-108px)} 40.2%{transform:translate(-96px,-108px)}
 92.6%{transform:translate(-96px,164px);opacity:1} 100%{transform:translate(-60px,164px);opacity:0}}
'''
    return page(
        n=3, slug='hangar-clusters', W=W, H=H, mode='loop', steps=1,
        eyebrow='Hangar · Where it runs', title='Two clusters, one source of truth',
        lede='Hangar as it actually runs today: a dev cluster that builds and proves, a prod cluster that runs Tower '
             'and the apps, and GitHub between them as the only thing either one trusts.',
        desc='Two Kubernetes clusters, dev and prod, each built from the Apron template and each running ArgoCD and Airframe. '
             'The dev cluster runs Glidepath, an Autopilot agent sandbox and dev copies of the Skyport apps; the prod cluster '
             'runs Tower and the production Skyport apps. Developers use Tower, which opens pull requests on GitHub; '
             'GitHub triggers Glidepath, and each cluster\'s ArgoCD pulls merged changes. No cluster holds credentials for another.',
        body=f.svg(), extra_css=css,
        after_svg='<label class="pause"><input type="checkbox" id="pause"> Pause the moving dot</label>',
        hint='A token follows one change from Tower to prod, on a quiet loop (CSS only, hidden for reduced motion). Click any box to open its page.',
        notes=[
            ('The idea', '<p>A deployment view: where each part of Hangar physically lives in the home lab. It is the most '
                         'honest picture (two clusters, Backstage on prod, agents sandboxed on dev) and the one that best '
                         'shows the "no cluster reaches into another" rule.</p>'),
            ('Motion and clicks', '<ul><li><b>Loop</b>: one decorative token traces a change from Tower, through GitHub, '
                                  'into prod. No controls needed; a pause toggle is here for the mockup.</li><li>Every product '
                                  'box and both Apron zone labels click through.</li></ul>'),
            ('Trade-off', '<p>It is about infrastructure more than the product family, so Tower, Glidepath and Airframe '
                          'read as tenants rather than as the platform. It would date quickly if the lab grows a third '
                          'cluster.</p>'),
        ])


STAGES = [  # slug, name, sub, short (from web/src/data/sdlc.ts), spoke
    ('design', 'Plan and design', 'ADRs · contracts', 'Contracts first, decisions in writing', True),
    ('onboard', 'Onboard and code', 'Tower · one cicd.yaml', 'One file, scaffolded for you', True),
    ('build', 'Build and test', 'Glidepath · Tekton', 'Rootless builds, pinned catalogs, real tests', False),
    ('secure', 'Secure and govern', 'Sigstore · Kyverno', 'Honest gates, workload identity, no stored keys', False),
    ('release', 'Release and deploy', 'ArgoCD · Rollouts', 'Only a merged commit crosses a boundary', True),
    ('operate', 'Operate and observe', 'Tower · OTel · SLOs', 'One trace per change, one pane of glass', False),
    ('improve', 'Measure and improve', 'DORA · scorecard', 'Scorecards, evals and written-down gaps', True),
]
LONG = {
    'design': 'Every decision that shapes the platform is written down as an ADR, and every service starts as a contract (an Airframe XR) before it is code.',
    'onboard': 'A new service is one form in Tower. It becomes a pull request with a single cicd.yaml; nobody hand-writes pipelines.',
    'build': 'Glidepath builds on Tekton with rootless Kaniko, pinned task catalogs, and real tests through Testkube.',
    'secure': 'Keyless signing, provenance that says what the build really did, and policy that checks both before release.',
    'release': 'Promotion is a pull request. Each cluster\'s ArgoCD pulls what merged, and Argo Rollouts runs the canary.',
    'operate': 'One OpenTelemetry trace per change from commit to canary, with SLOs and release records side by side in Tower.',
    'improve': 'DORA metrics, the Airframe scorecard and agent evals turn every pass into the next round of work.',
}

def o_wheel():
    W, H = 720, 604
    cx, cy, R, sw, sh = 360, 300, 230, 168, 64
    hw, hh = 200, 104
    N = len(STAGES)
    out = []
    boxes = []
    for k in range(N):
        th = math.radians(-90 + k * 360 / N)
        px, py = cx + R * math.cos(th), cy + R * math.sin(th)
        bx, by = up4(px - sw / 2) if px > cx else round((px - sw / 2) / 4) * 4, round((py - sh / 2) / 4) * 4
        boxes.append((bx, by))
    # mirror pairs for symmetry
    for k in range(1, N):
        j = N - k
        if j > k:
            bx, by = boxes[k]; boxes[j] = (2 * cx - bx - sw, by)
    boxes[0] = (cx - sw // 2, boxes[0][1])

    def hits(k):
        x, y = boxes[k]; pts = []
        for xe in (x, x + sw):
            d = R * R - (xe - cx) ** 2
            if d >= 0:
                for s in (1, -1):
                    yy = cy + s * math.sqrt(d)
                    if y <= yy <= y + sh: pts.append((xe, yy))
        for ye in (y, y + sh):
            d = R * R - (ye - cy) ** 2
            if d >= 0:
                for s in (1, -1):
                    xx = cx + s * math.sqrt(d)
                    if x <= xx <= x + sw: pts.append((xx, ye))
        ang = lambda p: math.atan2(p[1] - cy, p[0] - cx)
        c = math.atan2(y + sh / 2 - cy, x + sw / 2 - cx)
        rel = lambda p: (ang(p) - c + math.pi) % (2 * math.pi) - math.pi
        pts.sort(key=rel)
        return pts[0], pts[-1]  # entry (counter-clockwise side), exit (clockwise side)

    arcs = []
    for k in range(N):
        j = (k + 1) % N
        _, ex = hits(k); en, _ = hits(j)
        phi = math.atan2(en[1] - cy, en[0] - cx) - 1.2 / R
        q = (cx + R * math.cos(phi), cy + R * math.sin(phi))
        tone = 'acc' if STAGES[j][0] == 'release' else ''
        cls = 'a acc' if tone else 'a'
        mk = 'arrow-acc' if tone else 'arrow'
        arcs.append(f'<path class="{cls}" d="M{ex[0]:.3f},{ex[1]:.3f} A{R},{R} 0 0 1 {q[0]:.3f},{q[1]:.3f}" marker-end="url(#hangar-wheel-{mk})"/>')
    out += arcs
    # dashed write-back spokes
    for k, st in enumerate(STAGES):
        if not st[4]: continue
        x, y = boxes[k]; pcx, pcy = x + sw / 2, y + sh / 2
        ux, uy = pcx - cx, pcy - cy; L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        bd = lambda a, b: min(a / abs(ux) if ux else 1e9, b / abs(uy) if uy else 1e9)
        s0 = (pcx - bd(sw / 2, sh / 2) * ux, pcy - bd(sw / 2, sh / 2) * uy)
        e = bd(hw / 2, hh / 2) + 6
        s1 = (cx + e * ux, cy + e * uy)
        out.append(f'<path class="a dash thin" d="M{s0[0]:.2f},{s0[1]:.2f} L{s1[0]:.2f},{s1[1]:.2f}" marker-end="url(#hangar-wheel-arrow)"/>')
    hub = (node(cx - hw // 2, cy - hh // 2, hw, hh, 'Hangar', 'one record of every pass', 'store', tag='git · releases',
                href='/platform/', icon='hangar', isz=36))
    for k, (slug, name, sub, short, spoke) in enumerate(STAGES):
        x, y = boxes[k]
        kind = 'focal' if slug == 'release' else 'backend'
        s = node(x, y, sw, sh, name, sub, kind, href=f'/sdlc/{slug}/') + badge(x + 4, y + 4, k + 1)
        s = s.replace('<a href=', f'<a id="s-{slug}" href=', 1)
        body = s if k else hub.replace('<a href=', '<a id="s-hub" href=', 1) + s
        out.append(item(k + 1, f'Stage {k + 1}: {name}. {short}', body))
    out.append(legend(572, [('backend', 'Stage'), ('focal', 'The boundary'), ('store', 'The record'),
                            ('muted-dash', 'Writes back')], W=W))

    peeks = ['<div data-p="intro"><p class="eyebrow">The whole SDLC</p><p>Seven stages, clockwise from the top, and every '
             'pass leaves something in the record at the centre. Point at a stage for the short version; click it for '
             'the full page.</p></div>',
             '<div data-p="hub"><p class="eyebrow">The centre · Hangar</p><p>Git history, ADRs, release records and DORA '
             'numbers: the platform remembers every pass, so the next one starts better informed.</p></div>']
    css = []
    for k, (slug, name, sub, short, _) in enumerate(STAGES):
        peeks.append(f'<div data-p="{slug}"><p class="eyebrow">Stage {k + 1} · {esc(name)}</p>'
                     f'<p class="big">{esc(short)}.</p><p>{esc(LONG[slug])}</p></div>')
    for key in [s[0] for s in STAGES] + ['hub']:
        css.append(f'main:has(#s-{key}:hover) .peek>[data-p=intro], main:has(#s-{key}:focus-visible) .peek>[data-p=intro]{{display:none}}')
        css.append(f'main:has(#s-{key}:hover) .peek>[data-p={key}], main:has(#s-{key}:focus-visible) .peek>[data-p={key}]{{display:block}}')
    extra_css = '''
.wheel{display:grid;grid-template-columns:minmax(0,720px) minmax(220px,1fr);gap:1rem;align-items:center}
@media (max-width:900px){.wheel{grid-template-columns:1fr}}
.peek{background:var(--card);border:1px solid var(--rule);border-radius:var(--r);padding:1rem 1.1rem;min-height:12rem}
.peek>div{display:none}.peek>[data-p=intro]{display:block}
.peek p{margin:0 0 .5rem;font-size:.86rem;line-height:1.5}
.peek .big{font-family:var(--font-serif);font-size:1.35rem;line-height:1.2}
''' + '\n'.join(css)
    html_ = page(
        n=4, slug='hangar-wheel', W=W, H=H, mode='step', steps=7,
        eyebrow='Hangar · The lifecycle', title='Every pass leaves the platform better',
        lede='The software lifecycle as Hangar runs it: seven stages in a loop, each owned by part of the platform, '
             'and every pass written back to one shared record.',
        desc='A loop of seven lifecycle stages: plan and design, onboard and code, build and test, secure and govern, release and '
             'deploy, operate and observe, and measure and improve, which feeds back into planning. Release and deploy is the '
             'boundary where only a merged commit crosses. Four stages write back to the hub, Hangar\'s single record of git '
             'history, decisions and release records.',
        body='\n'.join(out), extra_css=extra_css,
        hint='Press Play or use ←/→ to walk the stages. Point at a stage to preview it; click to open its SDLC page.',
        notes=[
            ('The idea', '<p>The SDLC rail that already sits on the home page, turned into a loop with Hangar in the '
                         'middle. It sells the "whole SDLC" story James asked the site to cover, and links straight into '
                         'the seven /sdlc/ pages that already exist.</p>'),
            ('Motion and clicks', '<ul><li><b>Step</b> mode: nothing moves until the reader presses Play or Next, then '
                                  'one stage at a time.</li><li>Hover preview in the side panel, click through to each stage '
                                  'page. The hub links to /platform/.</li></ul>'),
            ('Trade-off', '<p>It is a process, not an architecture: you learn how Hangar works, not what it is made of. '
                          'And it repeats the stage rail already on the home page.</p>'),
        ])
    # put the svg and the peek side by side
    html_ = html_.replace('<div class="diagram-container">', '<div class="wheel"><div class="diagram-container">', 1)
    html_ = html_.replace('</svg>\n  </div>\n  ', '</svg>\n  </div>\n  <div class="peek" aria-live="polite">' + ''.join(peeks) + '</div></div>\n  ', 1)
    return html_


def o_family():
    f = Fig('hangar-family')
    W, H = 1000, 512
    A = f.add
    A(zone(184, 52, 808, 404, 'Hangar · the platform', href='/platform/', icon='hangar'))
    f.arrow([(152, 96), (200, 96)])
    f.arrow([(588, 144), (588, 184)], 'acc'); A(vlab(588, 144, 184, 'pull requests', 'acc'))
    f.arrow([(320, 224), (320, 264)], 'acc'); A(vlab(320, 224, 264, 'webhook', 'acc'))
    f.arrow([(588, 224), (588, 264)], 'acc'); A(vlab(588, 224, 264, 'XRs', 'acc'))
    f.arrow([(856, 224), (856, 264)]); A(vlab(856, 224, 264, 'agent defs'))
    f.arrow([(200, 312), (164, 312), (164, 128), (200, 128)], 'lnk', dashed=True); A(vlab(164, 128, 312, 'events', 'link', side='l'))
    A(item(1, 'Step 1: Apron, the ground every cluster starts from',
           node(200, 384, 776, 56, 'Apron', 'every cluster from one template · dev and prod today', 'store', tag='ground',
                href='/docs/apron/', icon='apron')))
    A(item(2, 'Step 2: Airframe, the control plane: what a compliant service is, defined once',
           node(468, 264, 240, 80, 'Airframe', 'Crossplane XRDs · one chart', tag='control plane', href='/docs/airframe/', icon='airframe')))
    A(item(2, 'Step 2: Glidepath, the guarded road from a merged commit to a verified release',
           node(200, 264, 240, 80, 'Glidepath', 'CI/CD · signing · releases', tag='delivery', href='/cicd/', icon='glidepath')))
    A(item(3, 'Step 3: Autopilot, any AI agent workload, bounded and audited (early)',
           node(736, 264, 240, 80, 'Autopilot', 'agent workloads · early', tag='ai workloads', href='/autopilot/', icon='autopilot')))
    A(item(4, 'Step 4: GitHub, where every change is a reviewed, merged commit',
           node(200, 184, 776, 40, 'GitHub · every change is a reviewed, merged commit', None, 'focal', href='/principles/#reviewed-commits')))
    A(item(5, 'Step 5: Tower, the one place people look, on Backstage',
           node(200, 72, 776, 72, 'Tower', 'Backstage plugin · releases, SLOs and fleet views · self-service', tag='experience',
                href='/tower/', icon='tower', big=True)))
    A(item(5, 'Step 5: developers use Tower', node(24, 72, 128, 56, 'Developers', 'self-service', 'input')))
    A(drawpath(4, [(588, 224), (588, 264)]))
    A(legend(480, [('input', 'People'), ('backend', 'Hangar product'), ('store', 'Ground'), ('focal', 'The only crossing'),
                   ('acc', 'A change'), ('lnk-dash', 'Events back')]))
    return page(
        n=5, slug='hangar-family', W=W, H=H, mode='reveal', steps=5,
        eyebrow='Hangar · The product family', title='Five products, one platform',
        lede='Hangar is five products that each do one job: ground to stand on, an API that defines a service, a road to '
             'production, a safe place for agents, and one front door for people.',
        desc='The Hangar product family. Apron is the ground every cluster starts from. Glidepath, Airframe and Autopilot sit on '
             'it side by side: delivery, the control plane, and AI agent workloads. GitHub sits above them, where every change '
             'is a reviewed, merged commit, and Tower sits on top as the front door people use. Events from Glidepath flow back '
             'to Tower.',
        body=f.svg(),
        hint='Builds from the ground up, once, on load. Click any product to open its page.',
        notes=[
            ('The idea', '<p>The like-for-like replacement for today\'s family diagram. Same job (here are the products and '
                         'how they fit), but Autopilot is one of three equal peers instead of the "New" headline, and '
                         'GitHub runs across the middle as the boundary every product respects.</p>'),
            ('Motion and clicks', '<ul><li><b>Reveal</b>, bottom-up (5 steps, under 4 seconds).</li><li>Every product '
                                  'links to its page; the Hangar zone label links to /platform/.</li><li>The product icons do '
                                  'most of the visual work.</li></ul>'),
            ('Trade-off', '<p>The calmest of the five and the easiest to read in a glance, but the least surprising. It '
                          'says what the products are more than how a change moves through them.</p>'),
        ])

