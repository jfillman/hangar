"""Spec: Tower Airspace (Oct 24, 2026), ported from the claude.ai artifact."""
from report import Page

CSS = r'''.airspace{--bg:var(--ground);--surface:var(--paper);--sunk:var(--code-bg);--fg:var(--ink);--muted:var(--ink-2);--line:var(--rule);--sky:var(--accent);--sky-soft:var(--accent-soft);--ok-soft:var(--ok-bg);--amber-soft:rgba(185,121,31,0.12);--font-display:var(--serif);--font-body:var(--sans);--font-mono:var(--mono);display:flex;flex-direction:column;gap:48px}
:root[data-theme="dark"] .airspace{--amber-soft:rgba(232,163,61,0.14)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .airspace{--amber-soft:rgba(232,163,61,0.14)}}
.airspace h2,.airspace h3{font-weight:400}
.airspace h2,.airspace h3{font-family: var(--font-display); text-wrap: balance; margin: 0; letter-spacing: 0.005em;}
.airspace h2{font-size: clamp(26px, 3.6vw, 34px); font-weight: 600; line-height: 1.15;}
.airspace h3{font-size: 20px; font-weight: 600;}
.airspace p{margin: 0; max-width: 68ch;}
.airspace a{color: var(--sky);}
.airspace code,.airspace .mono{font-family: var(--font-mono); font-size: 0.88em;}
.airspace code{background: var(--sunk); padding: 1px 6px; border-radius: 4px;}
.airspace .eyebrow{font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--sky);}
.airspace section{display: flex; flex-direction: column; gap: 18px;}
.airspace .lede{font-size: 19px; color: var(--muted); max-width: 62ch;}
.airspace .hero{display: flex; flex-direction: column; gap: 18px; padding-bottom: 8px; border-bottom: 1px solid var(--line);}
.airspace .hero-row{display: flex; align-items: center; gap: 14px;}
.airspace .hero svg{flex: none;}
.airspace .chips{display: flex; flex-wrap: wrap; gap: 8px;}
.airspace .chip{font-family: var(--font-mono); font-size: 12px; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); background: var(--surface);}
.airspace .grid3{display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;}
.airspace .panel{background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px; min-width: 0;}
.airspace .panel h3{font-size: 18px;}
.airspace .panel p{color: var(--muted); font-size: 15px;}
.airspace .panel .mono{color: var(--sky); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;}
.airspace figure{margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; display: flex; flex-direction: column;}
.airspace figure .scope{overflow-x: auto; padding: 20px;}
.airspace figure svg{display: block; min-width: 760px; width: 100%; height: auto;}
.airspace figcaption{border-top: 1px solid var(--line); padding: 12px 20px; font-size: 14px; color: var(--muted);}
.airspace figcaption b{color: var(--fg); font-weight: 600;}
.airspace .d-box{fill: var(--sunk); stroke: var(--line); stroke-width: 1.2;}
.airspace .d-box-sky{fill: var(--sky-soft); stroke: var(--sky); stroke-width: 1.2;}
.airspace .d-box-amber{fill: var(--amber-soft); stroke: var(--amber); stroke-width: 1.2;}
.airspace .d-box-ok{fill: var(--ok-soft); stroke: var(--ok); stroke-width: 1.2;}
.airspace .d-surface{fill: var(--surface); stroke: var(--line); stroke-width: 1.2;}
.airspace .d-t{fill: var(--fg); font-family: var(--font-mono); font-size: 13px;}
.airspace .d-s{fill: var(--muted); font-family: var(--font-body); font-size: 12px;}
.airspace .d-h{fill: var(--sky); font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.12em;}
.airspace .d-ha{fill: var(--amber); font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.12em;}
.airspace .d-e{fill: none; stroke: var(--muted); stroke-width: 1.4;}
.airspace .d-e-sky{fill: none; stroke: var(--sky); stroke-width: 1.6;}
.airspace .d-e-amber{fill: none; stroke: var(--amber); stroke-width: 1.6; stroke-dasharray: 6 5;}
.airspace .d-arrow{fill: var(--muted);}
.airspace .d-arrow-sky{fill: var(--sky);}
.airspace .d-arrow-amber{fill: var(--amber);}
.airspace .d-lane{fill: none; stroke: var(--line); stroke-dasharray: 3 5;}
.airspace table{border-collapse: collapse; width: 100%; font-size: 15px;}
.airspace .tablebox{overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 6px;}
.airspace th,.airspace td{text-align: left; padding: 11px 16px; border-bottom: 1px solid var(--line); vertical-align: top;}
.airspace th{font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); font-weight: 500;}
.airspace tr:last-child td{border-bottom: none;}
.airspace td:first-child{white-space: nowrap;}
.airspace .pill{display: inline-block; font-family: var(--font-mono); font-size: 12px; padding: 2px 9px; border-radius: 999px; border: 1px solid; white-space: nowrap;}
.airspace .p-ok{color: var(--ok); border-color: var(--ok); background: var(--ok-soft);}
.airspace .p-sky{color: var(--sky); border-color: var(--sky); background: var(--sky-soft);}
.airspace .p-amber{color: var(--amber); border-color: var(--amber); background: var(--amber-soft);}
.airspace .p-bad{color: var(--bad); border-color: var(--bad);}
.airspace .p-mute{color: var(--muted); border-color: var(--line);}
.airspace .guard{display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px;}
.airspace .guard div{background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0;}
.airspace .guard b{font-family: var(--font-display); font-size: 17px; font-weight: 600;}
.airspace .guard span{color: var(--muted); font-size: 15px;}
.airspace pre{margin: 0; background: var(--sunk); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; overflow-x: auto; font: 13px/1.6 var(--font-mono); color: var(--fg);}
.airspace pre .c{color: var(--muted);}
.airspace pre .k{color: var(--sky);}
.airspace .two{display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;}
.airspace .two > div{display: flex; flex-direction: column; gap: 10px; min-width: 0;}
.airspace .note{font-size: 14px; color: var(--muted);}
.airspace ol.steps{margin: 0; padding-left: 22px; display: flex; flex-direction: column; gap: 8px; max-width: 72ch;}
.airspace ol.steps li::marker{font-family: var(--font-mono); color: var(--sky);}
.airspace footer{border-top: 1px solid var(--line); padding-top: 18px; font-size: 14px; color: var(--muted);}
@media (prefers-reduced-motion: no-preference){.airspace a{transition: color .15s;}}'''

P = Page(
    'tower-airspace', 'Spec', 'Tower · Airspace',
    'Airspace: who a change will reach, before it ships',
    'Tower\'s Airspace shows every service\'s real connections from OpenTelemetry traces, compares them with what each environment declares, '
    'and keeps the API spec signed onto each image, so the api-compat release check can say who a breaking change would reach.',
    '2026-10-24',
    meta=[('Status', 'built and live in Tower v0.99.0 to v0.102.0, Oct 23 and 24, 2026'),
          ('Builds on', 'Airframe service kinds, Apron\'s observability stack, Glidepath\'s signed API specs and api-compat check'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/tower/airspace/">Tower Airspace</a>')],
    lede=('Every service in Hangar talks to other services, databases and brokers, and serves an API someone else depends on. Airspace shows '
          'those connections as they really are, and keeps track of the API contract each deployed version carries, so you know who a change '
          'will reach before it ships.'),
    css=CSS)

BODY = r'''
<div class="airspace">
<section>
  <span class="eyebrow">What you get</span>
  <h2>Three places to look</h2>
  <div class="grid3">
    <div class="panel">
      <span class="mono">Per service</span>
      <h3>Airspace tab</h3>
      <p>Who calls this service, what it calls, and the databases and brokers it owns, per environment. A row view for scanning, with a radar graph one toggle away.</p>
    </div>
    <div class="panel">
      <span class="mono">Fleet</span>
      <h3>Map, Contracts, Drift</h3>
      <p>The whole fleet's connections, every API with the spec each environment runs and a diff between them, and every connection that disagrees with what was declared.</p>
    </div>
    <div class="panel">
      <span class="mono">Release</span>
      <h3>API compatibility</h3>
      <p>Each release PR gets an api-compat check. Its verdict, the breaking changes and whether anyone uses them land on the Release Record and the Ops Wall.</p>
    </div>
  </div>
</section>

<section>
  <span class="eyebrow">The big picture</span>
  <h2>Three sources, one view</h2>
  <p>Airspace never asks you to draw a diagram by hand. It reads three things Hangar already produces: traffic the platform observes, what your environment's configuration declares and owns, and the API spec signed onto each image.</p>
  <figure>
    <div class="scope">
      <svg viewBox="0 0 980 360" role="img" aria-label="Three data sources feeding Tower Airspace: observed traffic, declared and composed configuration, and signed API specs">
        <defs>
          <marker id="a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow"/></marker>
          <marker id="a1s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow-sky"/></marker>
        </defs>
        <text x="20" y="28" class="d-h">OBSERVED</text>
        <rect x="20" y="40" width="160" height="58" rx="5" class="d-box"/><text x="34" y="64" class="d-t">service pod</text><text x="34" y="84" class="d-s">agent injected at start</text>
        <rect x="220" y="40" width="160" height="58" rx="5" class="d-box"/><text x="234" y="64" class="d-t">OTel collector</text><text x="234" y="84" class="d-s">one OTLP endpoint</text>
        <rect x="420" y="40" width="160" height="58" rx="5" class="d-box"/><text x="434" y="64" class="d-t">Tempo</text><text x="434" y="84" class="d-s">builds the service graph</text>
        <rect x="620" y="40" width="160" height="58" rx="5" class="d-box"/><text x="634" y="64" class="d-t">Prometheus</text><text x="634" y="84" class="d-s">edges, rates, latency</text>
        <path d="M180 69H218" class="d-e" marker-end="url(#a1)"/><path d="M380 69H418" class="d-e" marker-end="url(#a1)"/><path d="M580 69H618" class="d-e" marker-end="url(#a1)"/>
        <path d="M20 122H780" class="d-lane"/>
        <text x="20" y="150" class="d-h">DECLARED · COMPOSED</text>
        <rect x="20" y="162" width="360" height="58" rx="5" class="d-box"/><text x="34" y="186" class="d-t">environment values file</text><text x="34" y="206" class="d-s">networkPolicy peers (declared) · components[] (owned)</text>
        <rect x="420" y="162" width="360" height="58" rx="5" class="d-box"/><text x="434" y="186" class="d-t">Airframe / Crossplane</text><text x="434" y="206" class="d-s">the databases, caches and brokers each service owns</text>
        <path d="M20 244H780" class="d-lane"/>
        <text x="20" y="272" class="d-h">SPECS</text>
        <rect x="20" y="284" width="160" height="58" rx="5" class="d-box"/><text x="34" y="308" class="d-t">openapi.yaml</text><text x="34" y="328" class="d-s">in the service repo</text>
        <rect x="220" y="284" width="160" height="58" rx="5" class="d-box"/><text x="234" y="308" class="d-t">Glidepath build</text><text x="234" y="328" class="d-s">signs it onto the image</text>
        <rect x="420" y="284" width="160" height="58" rx="5" class="d-box"/><text x="434" y="308" class="d-t">image digest</text><text x="434" y="328" class="d-s">spec travels with it</text>
        <rect x="620" y="284" width="160" height="58" rx="5" class="d-box-amber"/><text x="634" y="308" class="d-t">api-compat</text><text x="634" y="328" class="d-s">release PR check</text>
        <path d="M180 313H218" class="d-e" marker-end="url(#a1)"/><path d="M380 313H418" class="d-e" marker-end="url(#a1)"/><path d="M580 313H618" class="d-e" marker-end="url(#a1)"/>
        <rect x="830" y="40" width="130" height="302" rx="6" class="d-box-sky"/>
        <text x="846" y="68" class="d-h">TOWER</text>
        <text x="846" y="92" class="d-t">Airspace</text>
        <text x="846" y="130" class="d-s">Strips · Radar</text>
        <text x="846" y="152" class="d-s">Fleet map</text>
        <text x="846" y="174" class="d-s">Contracts</text>
        <text x="846" y="196" class="d-s">Drift</text>
        <text x="846" y="236" class="d-s">Release Record</text>
        <text x="846" y="258" class="d-s">Ops Wall</text>
        <path d="M780 69H828" class="d-e-sky" marker-end="url(#a1s)"/>
        <path d="M780 191H828" class="d-e-sky" marker-end="url(#a1s)"/>
        <path d="M780 313H828" class="d-e-sky" marker-end="url(#a1s)"/>
      </svg>
    </div>
    <figcaption><b>Each source answers one question.</b> Observed: who actually talks to whom. Declared and composed: who is allowed to, and what each service owns. Specs: what contract each running version offers.</figcaption>
  </figure>
</section>

<section>
  <span class="eyebrow">Observed traffic</span>
  <h2>Instrumented without touching your code</h2>
  <p>Hangar already knows what kind of service you run: a Node.js, Spring Boot, Python or Go application is a different Airframe kind. That kind becomes a runtime, the runtime travels with each environment to the Helm chart, and the chart asks the OpenTelemetry Operator to inject the matching agent when the pod starts.</p>
  <figure>
    <div class="scope">
      <svg viewBox="0 0 980 300" role="img" aria-label="How a service's runtime flows from its Airframe kind to an injected OpenTelemetry agent and on to the service graph">
        <defs>
          <marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow"/></marker>
        </defs>
        <text x="20" y="26" class="d-h">CONFIGURATION · DECIDED ONCE</text>
        <rect x="20" y="40" width="200" height="70" rx="5" class="d-box"/><text x="34" y="66" class="d-t">PythonApplication</text><text x="34" y="88" class="d-s">the service's Airframe kind</text>
        <rect x="260" y="40" width="200" height="70" rx="5" class="d-box"/><text x="274" y="66" class="d-t">runtime: python</text><text x="274" y="88" class="d-s">written to its identity file</text>
        <rect x="500" y="40" width="200" height="70" rx="5" class="d-box"/><text x="514" y="66" class="d-t">environment</text><text x="514" y="88" class="d-s">+ the cluster's observability</text>
        <rect x="740" y="40" width="220" height="70" rx="5" class="d-box"/><text x="754" y="66" class="d-t">chart: pod annotation</text><text x="754" y="88" class="d-s">inject-python: observability/hangar</text>
        <path d="M220 75H258" class="d-e" marker-end="url(#a2)"/><path d="M460 75H498" class="d-e" marker-end="url(#a2)"/><path d="M700 75H738" class="d-e" marker-end="url(#a2)"/>
        <path d="M850 110V150H130V188" class="d-e" marker-end="url(#a2)"/>
        <text x="20" y="176" class="d-h">RUNTIME · EVERY POD</text>
        <rect x="20" y="190" width="220" height="70" rx="5" class="d-box-sky"/><text x="34" y="216" class="d-t">Operator webhook</text><text x="34" y="238" class="d-s">adds the agent; fail-open</text>
        <rect x="280" y="190" width="200" height="70" rx="5" class="d-box"/><text x="294" y="216" class="d-t">service + agent</text><text x="294" y="238" class="d-s">spans over OTLP/HTTP</text>
        <rect x="520" y="190" width="200" height="70" rx="5" class="d-box"/><text x="534" y="216" class="d-t">collector → Tempo</text><text x="534" y="238" class="d-s">client/server pairs</text>
        <rect x="760" y="190" width="200" height="70" rx="5" class="d-box"/><text x="774" y="216" class="d-t">service graph</text><text x="774" y="238" class="d-s">in Prometheus</text>
        <path d="M240 225H278" class="d-e" marker-end="url(#a2)"/><path d="M480 225H518" class="d-e" marker-end="url(#a2)"/><path d="M720 225H758" class="d-e" marker-end="url(#a2)"/>
      </svg>
    </div>
    <figcaption><b>Nobody edits a values file to get this.</b> The runtime comes from the kind, the cluster's observability settings come from the cluster, and both reach every Ground, Flight and preview environment that uses the platform's default chart.</figcaption>
  </figure>
  <div class="two">
    <div>
      <h3>What the graph contains</h3>
      <p>Calls between services, calls into databases and caches, and messages through a broker, each with a rate, a p95 latency and an error count. Traffic arriving from outside appears as <code>user</code>. Services are named <code>&lt;service&gt;-&lt;environment&gt;</code>, so dev and prod never blur together.</p>
    </div>
    <div>
      <h3>What gets instrumented</h3>
      <p>Node.js, Java and Python services get an agent automatically. Go services are recognised but not injected, because the Go agent needs a privileged sidecar; they can still send traces with the OpenTelemetry SDK. Every trace is kept, so a quiet connection still shows up.</p>
    </div>
  </div>
</section>

<section>
  <span class="eyebrow">Declared and owned</span>
  <h2>What each connection's state means</h2>
  <p>Observed traffic is compared with what your environment declares. Peers listed in the NetworkPolicy settings count as declared. Components your service owns, such as its PostgreSQL or Redis, come from <code>components[]</code> and need no declaration at all.</p>
  <div class="tablebox">
    <table>
      <thead><tr><th>State</th><th>Meaning</th><th>What to do</th></tr></thead>
      <tbody>
        <tr><td><span class="pill p-ok">Declared · seen</span></td><td>Declared, and traffic flows.</td><td>Nothing.</td></tr>
        <tr><td><span class="pill p-amber">Seen, not declared</span></td><td>Traffic flows, but nothing declares it.</td><td>Declare the peer, or remove the call. A NetworkPolicy built from declarations would block it.</td></tr>
        <tr><td><span class="pill p-mute">Declared · no traffic</span></td><td>Declared, but silent in the window.</td><td>Check whether the caller still exists. In a quiet environment this can be normal.</td></tr>
        <tr><td><span class="pill p-sky">Via broker</span></td><td>Messages pass through a broker such as RabbitMQ.</td><td>Nothing. Shown as a direct publisher-to-consumer edge.</td></tr>
        <tr><td><span class="pill p-mute">Owned</span></td><td>A component the service's own resources create.</td><td>Nothing. Known from Crossplane.</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section>
  <span class="eyebrow">API specs</span>
  <h2>The spec travels with the image</h2>
  <p>Backstage-style API catalogs read a spec from the main branch, which says what the code will do someday. Hangar signs the spec onto the image at build time instead. Each environment then carries the exact contract of the version it is running, and dev and prod can be compared directly.</p>
  <figure>
    <div class="scope">
      <svg viewBox="0 0 980 290" role="img" aria-label="An API spec signed onto the image at build time and read per environment by Tower">
        <defs>
          <marker id="a3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow"/></marker>
          <marker id="a3s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow-sky"/></marker>
        </defs>
        <text x="20" y="26" class="d-h">BUILD</text>
        <rect x="20" y="40" width="170" height="66" rx="5" class="d-box"/><text x="34" y="66" class="d-t">openapi.yaml</text><text x="34" y="88" class="d-s">cicd.yaml api.spec</text>
        <rect x="230" y="40" width="190" height="66" rx="5" class="d-box"/><text x="244" y="66" class="d-t">attest-api-spec</text><text x="244" y="88" class="d-s">YAML → JSON, hash, sign</text>
        <rect x="460" y="40" width="210" height="66" rx="5" class="d-box-sky"/><text x="474" y="66" class="d-t">signed attestation</text><text x="474" y="88" class="d-s">Fulcio cert · Rekor entry</text>
        <path d="M190 73H228" class="d-e" marker-end="url(#a3)"/><path d="M420 73H458" class="d-e" marker-end="url(#a3)"/>
        <rect x="710" y="40" width="250" height="66" rx="5" class="d-surface"/><text x="724" y="66" class="d-t">image @ sha256:…</text><text x="724" y="88" class="d-s">attestation bound to the digest</text>
        <path d="M670 73H708" class="d-e" marker-end="url(#a3)"/>
        <text x="20" y="150" class="d-h">DEPLOY · EACH ENVIRONMENT RUNS ONE DIGEST</text>
        <rect x="20" y="166" width="200" height="66" rx="5" class="d-box"/><text x="34" y="192" class="d-t">dev</text><text x="34" y="214" class="d-s">digest B · spec 1.1.0</text>
        <rect x="260" y="166" width="200" height="66" rx="5" class="d-box"/><text x="274" y="192" class="d-t">prod</text><text x="274" y="214" class="d-s">digest A · spec 1.0.0</text>
        <path d="M835 106V136H120V164" class="d-e" marker-end="url(#a3)"/>
        <path d="M360 136V164" class="d-e" marker-end="url(#a3)"/>
        <rect x="560" y="166" width="400" height="98" rx="6" class="d-box-sky"/>
        <text x="576" y="192" class="d-h">TOWER · CONTRACTS</text>
        <text x="576" y="218" class="d-t">fetch by digest → verify → show</text>
        <text x="576" y="242" class="d-s">per-environment spec, and a diff dev → prod</text>
        <path d="M220 199H558" class="d-e-sky" marker-end="url(#a3s)"/>
      </svg>
    </div>
    <figcaption><b>Optional by design.</b> No file at <code>api.spec</code> means the service publishes no API. A malformed file or a signing problem is reported, and the build still passes.</figcaption>
  </figure>
  <div class="two">
    <div>
      <h3>Turning it on</h3>
      <p>Put an OpenAPI or AsyncAPI file at the repo root as <code>openapi.yaml</code>. That is the default, so nothing else is needed. Name another path in <code>cicd.yaml</code> if you keep it elsewhere.</p>
<pre><span class="k">api:</span>
  <span class="k">spec:</span> openapi.yaml   <span class="c"># default; YAML or JSON</span>
  <span class="k">type:</span> openapi        <span class="c"># openapi | asyncapi</span></pre>
    </div>
    <div>
      <h3>What is signed</h3>
      <p>The spec as JSON, its file hash, its <code>info.title</code> and <code>info.version</code>, and the format version, under the predicate type <code>https://hangar.io/attestations/api-spec/v1</code>. Rebuilding the same image never attaches a second copy. Tower verifies the signature the same way it verifies build provenance and SBOMs, and labels an unverified spec as unverified.</p>
    </div>
  </div>
</section>

<section>
  <span class="eyebrow">Release check</span>
  <h2>api-compat: who a change will break</h2>
  <p>When Glidepath opens a release PR, the api-compat check compares the candidate image's spec with the spec of the image already running in the target environment, not with the previous build. Skipped versions are compared correctly. It verifies both signatures, diffs the two with oasdiff, and looks up which operations are in use there.</p>
  <figure>
    <div class="scope">
      <svg viewBox="0 0 980 440" role="img" aria-label="Decision flow of the api-compat check, from spec lookup to the verdict">
        <defs>
          <marker id="a4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10Z" class="d-arrow"/></marker>
        </defs>
        <rect x="20" y="20" width="190" height="56" rx="5" class="d-box"/><text x="34" y="44" class="d-t">release PR</text><text x="34" y="64" class="d-s">candidate vs. running</text>
        <path d="M210 48H258" class="d-e" marker-end="url(#a4)"/>
        <path d="M330 18 400 48 330 78 260 48Z" class="d-surface"/><text x="296" y="52" class="d-t">spec on</text>
        <text x="282" y="96" class="d-s">candidate?</text>
        <path d="M400 48H448" class="d-e" marker-end="url(#a4)"/><text x="410" y="40" class="d-s">yes</text>
        <path d="M520 18 590 48 520 78 450 48Z" class="d-surface"/><text x="486" y="52" class="d-t">spec on</text>
        <text x="472" y="96" class="d-s">baseline?</text>
        <path d="M590 48H638" class="d-e" marker-end="url(#a4)"/><text x="600" y="40" class="d-s">yes</text>
        <path d="M710 18 780 48 710 78 640 48Z" class="d-surface"/><text x="682" y="52" class="d-t">breaking?</text>
        <path d="M330 78V136" class="d-e" marker-end="url(#a4)"/><text x="338" y="122" class="d-s">no</text>
        <rect x="270" y="138" width="120" height="34" rx="17" class="d-box"/><text x="290" y="160" class="d-t">no-spec</text>
        <path d="M520 78V136" class="d-e" marker-end="url(#a4)"/><text x="528" y="122" class="d-s">no</text>
        <rect x="450" y="138" width="140" height="34" rx="17" class="d-box"/><text x="468" y="160" class="d-t">no-baseline</text>
        <path d="M780 48H838" class="d-e" marker-end="url(#a4)"/><text x="790" y="40" class="d-s">no</text>
        <rect x="840" y="31" width="110" height="34" rx="17" class="d-box-ok"/><text x="872" y="53" class="d-t">pass</text>
        <path d="M710 78V188" class="d-e" marker-end="url(#a4)"/><text x="718" y="140" class="d-s">yes</text>
        <path d="M710 190 800 226 710 262 620 226Z" class="d-surface"/><text x="660" y="222" class="d-t">blocking</text><text x="676" y="240" class="d-t">on?</text>
        <path d="M800 226H838" class="d-e" marker-end="url(#a4)"/><text x="806" y="218" class="d-s">no</text>
        <rect x="840" y="209" width="110" height="34" rx="17" class="d-box-amber"/><text x="874" y="231" class="d-t">warn</text>
        <path d="M710 262V318" class="d-e" marker-end="url(#a4)"/><text x="718" y="296" class="d-s">yes</text>
        <path d="M710 320 800 356 710 392 620 356Z" class="d-surface"/><text x="664" y="352" class="d-t">operation</text><text x="672" y="370" class="d-t">in use?</text>
        <path d="M800 356H838" class="d-e" marker-end="url(#a4)"/><text x="804" y="348" class="d-s">no / unknown</text>
        <rect x="840" y="339" width="110" height="34" rx="17" class="d-box-amber"/><text x="874" y="361" class="d-t">warn</text>
        <path d="M620 356H530" class="d-e" marker-end="url(#a4)"/><text x="572" y="348" class="d-s">yes</text>
        <path d="M450 320 528 356 450 392 372 356Z" class="d-surface"/><text x="414" y="352" class="d-t">owner</text><text x="406" y="370" class="d-t">accepted?</text>
        <path d="M372 356H262" class="d-e" marker-end="url(#a4)"/><text x="312" y="348" class="d-s">no</text>
        <rect x="140" y="339" width="120" height="34" rx="17" class="d-surface" style="stroke: var(--bad)"/><text x="176" y="361" class="d-t">block</text>
        <path d="M450 392V418H262" class="d-e" marker-end="url(#a4)"/><text x="458" y="412" class="d-s">yes</text>
        <rect x="120" y="402" width="140" height="34" rx="17" class="d-box-ok"/><text x="140" y="424" class="d-t">overridden</text>
      </svg>
    </div>
    <figcaption><b>Blocking ships switched off.</b> Until a cluster turns it on, every breaking change is a warning. Even when it is on, a change blocks only if the operation it breaks is seen in use, and the service's owners can accept it.</figcaption>
  </figure>
  <div class="tablebox">
    <table>
      <thead><tr><th>Verdict</th><th>When</th><th>Blocks the merge?</th></tr></thead>
      <tbody>
        <tr><td><span class="pill p-ok">pass</span></td><td>No breaking change between the running spec and the candidate.</td><td>No</td></tr>
        <tr><td><span class="pill p-amber">warn</span></td><td>Breaking changes found, reported only.</td><td>No</td></tr>
        <tr><td><span class="pill p-bad">block</span></td><td>A breaking change to an operation seen in use, with blocking switched on and no owner override.</td><td>Yes, when the check is required</td></tr>
        <tr><td><span class="pill p-ok">overridden</span></td><td>An owner accepted the breaking change. Who, when and why are recorded.</td><td>No</td></tr>
        <tr><td><span class="pill p-mute">no-spec</span></td><td>The candidate image carries no spec.</td><td>No</td></tr>
        <tr><td><span class="pill p-mute">no-baseline</span></td><td>First release, or the running image has no spec yet.</td><td>No</td></tr>
        <tr><td><span class="pill p-mute">unsupported</span></td><td>AsyncAPI, which is not diffed yet.</td><td>No</td></tr>
      </tbody>
    </table>
  </div>
  <div class="two">
    <div>
      <h3>Accepting a breaking change</h3>
      <ol class="steps">
        <li>An admin or maintainer of the service's repository comments <code>/api-break-ok &lt;reason&gt;</code> on the release PR.</li>
        <li>They comment <code>/retest api-compat-</code>.</li>
        <li>The check confirms their permission on GitHub again, records the override and passes. A comment from anyone else is listed as ignored.</li>
      </ol>
    </div>
    <div>
      <h3>Where the verdict shows up</h3>
      <p>On the release PR as a comment with the full report. On the Release Record as an API compatibility section. In Airspace as a "breaking change pending" item. On the Ops Wall as a Needs-Attention entry while the PR is open with a warn or block.</p>
    </div>
  </div>
</section>

<section>
  <span class="eyebrow">Guardrails</span>
  <h2>Built to fail safe</h2>
  <div class="guard">
    <div><b>Pods always start</b><span>The agent is added by a fail-open webhook that only looks at application namespaces. If the operator is down, pods start uninstrumented and nothing else waits.</span></div>
    <div><b>Builds never fail on a spec</b><span>A missing, malformed or unsigned spec is reported. The build passes.</span></div>
    <div><b>Only verified specs count</b><span>The release check verifies both attestations before diffing. Tower shows an unverified spec as unverified, never as trusted.</span></div>
    <div><b>Verdicts can't be forged</b><span>Tower reads the machine-readable verdict only from the platform's own comment. A person posting a lookalike comment changes nothing.</span></div>
    <div><b>Unknown never blocks</b><span>If usage in the target environment can't be read, the verdict stays a warning.</span></div>
    <div><b>Owners decide</b><span>The override is limited to people who can already change the service's code, checked on every run, never cached.</span></div>
  </div>
</section>

<section>
  <span class="eyebrow">Know the limits</span>
  <h2>What Airspace can't tell you</h2>
  <div class="grid3">
    <div class="panel"><span class="mono">Operations, not fields</span><p>Traces show which operation a caller uses, not which response fields it reads. Field-level certainty needs consumer contract tests.</p></div>
    <div class="panel"><span class="mono">Quiet means unknown</span><p>A connection with no traffic in the window may be idle, not gone. Low-traffic environments produce more "no traffic" rows.</p></div>
    <div class="panel"><span class="mono">The spec is a promise</span><p>Nothing yet checks the spec against the routes a service really serves. Keep the file in step with the code.</p></div>
  </div>
  <p class="note">Tower's own diff between environments uses a small rule set. The release check's oasdiff report is the authoritative one, and Tower shows it whenever a release PR has run the check.</p>
</section>

<section>
  <span class="eyebrow">Configuration</span>
  <h2>Who sets what</h2>
  <div class="tablebox">
    <table>
      <thead><tr><th>Setting</th><th>Where</th><th>Owner</th></tr></thead>
      <tbody>
        <tr><td><code>api.spec</code>, <code>api.type</code></td><td><code>cicd.yaml</code> in the service repo</td><td>Service team</td></tr>
        <tr><td><code>observability.namespace</code>, <code>.instrumentation</code></td><td>The cluster's <code>cluster-defaults.yaml</code>, rendered by Apron</td><td>Platform team</td></tr>
        <tr><td><code>observability.runtime</code></td><td>Derived from the service's Airframe kind</td><td>Automatic</td></tr>
        <tr><td><code>apiCompat.blockWhenInUse</code></td><td>Glidepath catalog values, per cluster</td><td>Platform team</td></tr>
        <tr><td><code>apiCompat.usage.&lt;cluster&gt;.url</code></td><td>Glidepath catalog values: where the check reads usage</td><td>Platform team</td></tr>
        <tr><td><code>api-compat</code> required</td><td>The release guardrail registry</td><td>Platform team</td></tr>
      </tbody>
    </table>
  </div>
</section>
</div>
'''

P.add(BODY)
