from libx import *

def diamond(cx,cy,hw,hh,name,kind='backend'):
    fill,stroke,dash = KINDS[kind]
    pts = f'{cx-hw},{cy} {cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh}'
    return (f'<polygon points="{pts}" fill="{PAPER}"/><polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            + text(cx,cy+4,name,12,600,INK,'middle'))

def e05():
    b=[]
    cols=[(308,'Triage agent','in-cluster'),(452,'Coding agent','human-delegated'),(596,'Preflight runner','sandbox only')]
    for x,n,s in cols:
        b.append(text(x+68,104,n,12,600,INK,'middle')); b.append(text(x+68,120,s,8,400,MUTED,'middle',mono=True))
    b.append(text(748,112,'DELEGATED TO',8,500,MUTED,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="132" x2="976" y2="132" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('Read: catalog, metrics, logs','T0',['allow','allow','allow'],'Backstage MCP, Prometheus, Loki (read)'),
          ('Read: ArgoCD app and diff','T0',['allow','allow','allow'],'ArgoCD API, read-only account'),
          ('Open a PR on an app repo','T1',['rev','rev','rev'],'Repo-scoped token, minted per call'),
          ('Request a lower env','T1',['never','rev','rev'],'Commit to the tenants repo (GitOps)'),
          ('Sync or refresh a lower env','T1',['never','rev','rev'],'ArgoCD role:clearance-lower'),
          ('Re-run a failed pipeline','T1',['never','rev','rev'],"Tower's delegated re-run"),
          ('PR to an upper gitops repo','T2',['prop','prop','never'],'PR only; human merge, CODEOWNERS'),
          ('Secrets, exec, upper sync, IAM','T3',['never','never','never'],'Not exposed to any identity')]
    sty={'allow':('allow','#ffffff',INK,None,INK),'rev':('allow · reversible','rgba(27,31,36,0.05)',MUTED,None,INK),
         'prop':('propose only','rgba(46,123,166,0.10)',LINK,None,INK),'never':('never','rgba(27,31,36,0.02)','rgba(27,31,36,0.25)','4,3',SOFT)}
    y=140
    for i,(tool,tier,cells,dele) in enumerate(rows):
        last = (i==len(rows)-1)
        b.append(f'<rect x="24" y="{y}" width="276" height="44" rx="4" fill="{"rgba(185,121,31,0.08)" if last else "#ffffff"}" stroke="{ACC if last else "rgba(27,31,36,0.16)"}" stroke-width="1"/>')
        b.append(f'<rect x="32" y="{y+16}" width="24" height="12" rx="2" fill="transparent" stroke="{MUTED}" stroke-opacity="0.6" stroke-width="0.8"/>')
        b.append(text(44,y+25,tier,8,500,MUTED,'middle',mono=True))
        b.append(text(64,y+26,tool,12,600,INK))
        for (x,_,_),c in zip(cols,cells):
            lbl,fill,st,da,tc = sty[c]
            d = f' stroke-dasharray="{da}"' if da else ''
            b.append(f'<rect x="{x}" y="{y}" width="136" height="44" rx="4" fill="{fill}" stroke="{st}" stroke-width="1"{d}/>')
            b.append(text(x+68,y+26,lbl,12,600 if c!='never' else 400,tc,'middle'))
        b.append(text(748,y+26,dele,8,400,MUTED,mono=True))
        y += 52
    b.append(legend(y+16,[('backend','Allow'),('store','Allow, reversible in git'),('propose','Propose only'),('optional','Never')]))
    return dict(slug='tool-tiers', eyebrow='Access matrix · 05 of 11 · Tool tiers',
      title='What each agent identity may do, and who really does it',
      desc='Access matrix of eight tool groups against three agent profiles, triage agent, human-delegated coding agent and preflight runner, showing allow, allow but reversible in git, propose only, or never, with the delegated backing system for each tool.',
      lede='Write access is mostly a pull request, which a human can revert. The few imperative actions are delegated to systems that already audit themselves. The last row is not exposed to any identity, including Clearance itself.',
      body=''.join(b), W=1000, H=y+16+52, y0=64,
      cards=C3(P('Delegated over interactive. Every write action must state which category it falls in and the exact API it needs, before it is built (Tower write-action policy).'),
               UL(['Profiles are YAML in gitops-infra-clearance, reviewed like any change, and schema-validated in CI.','Tool ceilings apply on top of the human\'s own Tower permissions for delegated agents (the intersection).','Pipeline re-run and lower sync reuse the actions Tower Tier 1 already built and RBAC-scoped.']),
               P('As of the last handoff (2026-09-15), Tower Tier 1 write actions were built but not live-verified. Verify those first: Clearance would be delegating to something not yet proven against a genuinely stuck app.'), 'Caution'))

def e06():
    b=[]
    b += [path([(440,68),(440,96),(216,96),(216,128)]), path([(480,68),(480,128)]), path([(520,68),(520,96),(744,96),(744,128)]),
          path([(216,192),(216,232),(476,232)],marker=False), path([(744,192),(744,232),(484,232)],marker=False), path([(480,192),(480,228)],marker=False),
          path([(480,236),(480,264)]),
          path([(580,300),(660,300)],dashed=True), hlab(580,660,300,'ANY RED'),
          path([(880,300),(920,300),(920,46),(580,46)],dashed=True), vlab(920,46,300,'RETRY ≤ 3'),
          path([(480,336),(480,372)]), vlab(480,336,372,'ALL GREEN'),
          path([(380,408),(336,408)]), hlab(336,380,408,'LOWER'),
          path([(580,408),(624,408)]), hlab(580,624,408,'UPPER')]
    b.append('<circle cx="480" cy="232" r="4" fill="%s"/>'%INK)
    b += [node(380,24,200,44,'Agent PR opened',None,'input',rx=22),
          node(96,128,240,64,'Existing guardrails','provenance (real) · registry'),
          node(376,128,208,64,'agent-scope','paths within allowlist','focal'),
          node(624,128,240,64,'agent-identity','signer + task id vs audit','focal'),
          diamond(480,300,100,36,'Checks green?'),
          node(660,272,220,56,'Structured failure','rule id · path · fix hint'),
          diamond(480,408,100,36,'Target env?'),
          node(96,380,240,56,'Auto-merge','lower env · then ArgoCD pulls'),
          node(624,380,240,56,'Human review','upper · CODEOWNERS · then pull')]
    b.append(legend(480,[('focal','New gate'),('backend','Exists today'),('input','Start'),('muted-dash','Retry / fail')]))
    return dict(slug='pr-guardrails', eyebrow='Flowchart · 06 of 11 · Agent PR guardrails',
      title='An agent PR goes through the same gates, plus two that are about agents',
      desc='Flowchart of an agent-opened pull request passing the existing release guardrails and two new gates, agent-scope and agent-identity, in parallel; any failure returns a structured rule id and fix hint for up to three retries, while a pass routes to auto-merge for lower environments or human review for upper ones.',
      lede='Agents get no shortcut. Their PRs hit the same required checks as anyone\'s, and two new gates catch the failure modes that only agents have: editing their own controls, and acting under an identity that does not match the audit record.',
      body=''.join(b), W=1000, H=528,
      cards=C3(P('Governance stubs are structurally loud, never a silent pass (ADR-0003). One file adds a gate to the releaseGuardrails registry.'),
               UL(['agent-scope: changed paths must sit inside the profile allowlist, and never touch .tekton/, cicd.yaml guardrails, CODEOWNERS or AppProject files. An agent cannot edit its own gates.','agent-identity: the commit signer is an allowlisted workload identity, and the task id trailer exists in Clearance\'s audit log.','Both start as loud stubs and graduate to real, one at a time.']),
               P('For each new gate, open a PR that should fail it (edits .tekton/, or carries a forged task id) and confirm the required check goes red and blocks merge. Branch protection is a manual GitHub setting, so check it is actually required.')))

def e07():
    b=[]
    b.append(callout(32,100,'One task_id on every record.'))
    b += [path([(216,152),(592,152)],'accent'), hlab(216,592,152,'hash-chained',ACC),
          path([(216,168),(260,168),(260,232),(304,232)]),
          path([(216,248),(304,248)]),
          path([(488,248),(592,248)]), hlab(488,592,248,'OTLP'),
          path([(216,344),(304,344)]), hlab(216,304,344,'annotation'),
          path([(760,248),(808,248)]),
          path([(488,344),(808,344)]), hlab(488,808,344,'query'),
          path([(216,440),(880,440),(880,376)]), hlab(216,880,440,'PR labels + trailers')]
    b += [node(32,120,184,64,'Clearance + proxy','tool and LLM audit','focal'),
          node(32,216,184,64,'Glidepath','CDEvents · OTel spans'),
          node(32,312,184,64,'ArgoCD','Application annotations'),
          node(32,408,184,64,'Git','trailer + PR label'),
          node(304,216,184,64,'otel-collector','exists today'),
          node(304,312,184,64,'Prometheus','dora-exporter · author'),
          node(592,120,168,64,'WORM + Rekor','tamper-evident','focal'),
          node(592,216,168,64,'Loki · Tempo','logs · traces'),
          node(808,216,160,160,'Tower','Release Record · Agent tab')]
    b.append(legend(504,[('focal','New'),('backend','Exists today'),('accent','Evidence chain'),('muted','Telemetry')]))
    return dict(slug='flight-recorder', eyebrow='Data flow · 07 of 11 · Flight recorder',
      title='Flight recorder: reuse the telemetry, add one tamper-evident chain',
      desc='Data flow from four sources, Clearance audit, Glidepath, ArgoCD and git, through the existing otel-collector into Loki, Tempo and Prometheus with the dora-exporter, and into Tower, while Clearance audit events are also hash-chained into WORM storage and anchored in the self-hosted Rekor.',
      lede='Almost all of this already exists. The additions are one field, task_id, carried on every record from every agent type, and one chain for the audit events that is tamper-evident, not just searchable. Model calls are audited with the same id as tool calls.',
      body=''.join(b), W=1000, H=548, y0=76,
      cards=C3(P('Live-verified reuse over new mechanism. The dora-exporter already correlates by annotations rather than CDEvents, because CDEvents cannot confirm a deploy happened.'),
               UL(['hangar.io/task on commits (trailer), PRs (label) and Application annotations, alongside the hangar.io/* labels every component already propagates.','dora-exporter emits its four metrics with an author=agent|human label, so agent change failure rate reads against a human baseline.','Audit events hash-chain; periodic checkpoints go to WORM storage and to the self-hosted Rekor (ADR-0014).']),
               P('Proposal, not built: MinIO object lock needs enabling when the bucket is created, so decide before creating the audit bucket. Loki alone is searchable but not tamper-evident, which is why the second chain exists.'), 'Decide first'))

def e08():
    b=[]
    b.append(zone(216,96,544,148,'glidepath pipelinerun · one per case'))
    b += [path([(176,172),(232,172)]), hlab(176,232,172,'case'),
          path([(368,172),(408,172)]), lab(388,154,'TASK'),
          path([(544,172),(584,172)]), lab(564,154,'DIFF'),
          path([(744,172),(792,172)],'link'), hlab(744,792,172,'score',LINK),
          path([(884,204),(884,236)]), vlab(884,204,236,'BASELINE')]
    b += [node(24,140,152,64,'Seed corpus','documented dead ends','store'),
          node(232,140,136,64,'Broken fixture','AgentRun · TTL','optional'),
          node(408,140,136,64,'Agent under test','profile: preflight','input'),
          node(584,140,160,64,'Verifier','deterministic checks','focal'),
          node(792,140,184,64,'Scorecard','Prometheus · Tower','store'),
          node(792,236,184,56,'Regression gate','blocks profile · model · policy')]
    b.append(text(24,272,'SEED CORPUS · GROUND TRUTH FROM DOCUMENTED DEAD ENDS',8,500,MUTED,mono=True,ls='0.14em'))
    hdr=[(32,'CASE'),(256,'KNOWN ROOT CAUSE'),(500,'DETERMINISTIC VERIFIER')]
    for x,t in hdr: b.append(text(x,300,t,8,500,SOFT,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="308" x2="760" y2="308" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('Canary broken by image tag','bad image tag in gitops values','AnalysisRun passes; diff limited to values.yaml'),
          ('Liveness probe never Ready','probe path pointed at /readiness','pod Ready; probe is /actuator/health/liveness'),
          ('RabbitMQ broker never Ready','RabbitMQ 4.1 with operator 2.23','RabbitmqCluster Ready; broker is 4.2.x'),
          ('Composite never goes Ready','auto-ready: no Ready condition on CR','XR Ready; composition sets ready annotation'),
          ('XRD change silently reverted','hand-apply reverted by ArgoCD selfHeal','fix lands as a commit; no kubectl apply logged'),
          ('Image scan fails the build','transitive CVE in Java dependencies','image-scan gate green; pom diff is pins only')]
    y=312
    for i,(c,r,v) in enumerate(rows):
        if i%2==0: b.append(f'<rect x="24" y="{y}" width="736" height="28" fill="rgba(27,31,36,0.03)"/>')
        b.append(text(32,y+18,c,12,600,INK)); b.append(text(256,y+17,r,8,400,MUTED,mono=True)); b.append(text(500,y+17,v,8,400,MUTED,mono=True))
        y+=28
    b.append(callout(24,y+32,'Real incidents with a known cause and a known-good fix, so no judge model is needed. Other agent types get their own suites.'))
    b.append(legend(y+64,[('focal','Judge of record'),('input','Under test'),('optional','Disposable'),('store','History'),('link','Score')]))
    return dict(slug='preflight', eyebrow='Process · 08 of 11 · Preflight',
      title='Preflight: score every agent change against incidents you have already solved',
      desc='Process diagram of an evaluation harness in which a seed corpus of documented incidents is applied as a broken fixture in a disposable namespace inside a Glidepath PipelineRun, the agent under test works through Clearance, a deterministic verifier scores the result, and a regression gate blocks profile, model or policy changes that score worse than the baseline; a table lists six seed cases with their known root causes and verifiers.',
      lede='Hangar\'s own dead-ends list is the corpus: each case has a documented cause and a known fix, so the verifier is a deterministic check and not another model. Any change to a profile, a model or a policy has to score no worse than the last one.',
      body=''.join(b), W=1000, H=y+64+52, y0=76,
      cards=C3(P('Live verification: prove against real state, and never trust a pass that could mean the gate is off. Each case also has a seeded negative run that must fail.'),
               UL(['Runs as a Glidepath pipeline, so it inherits provenance, signing and results archival.','Scored on outcome, blast radius (paths touched vs allowlist), Clearance denials, retries and cost.','Gate lives on the Clearance repo itself: profile, model and policy changes are PRs that must pass Preflight.']),
               P('Proposal, not built. Start with two cases (the probe path and the auto-ready bug), because they are one-file fixes with unambiguous verifiers, and add the rest once the harness is trusted.'), 'Start small'))
