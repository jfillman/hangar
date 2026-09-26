from libx import *

def wrap(s, n):
    words, lines, cur = s.split(), [], ''
    for w in words:
        if len(cur)+len(w)+(1 if cur else 0) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur+' '+w).strip()
    if cur: lines.append(cur)
    return lines

def p_family():
    b=[]
    b.append(zone(24,100,752,384,'hangar · the platform'))
    b += [path([(296,164),(152,164),(152,252)]), hlab(152,296,164,'FORMS'),
          path([(400,196),(400,252)]), vlab(400,196,252,'AGENT TAB'),
          path([(504,164),(648,164),(648,252)]), hlab(504,648,164,'RELEASES'),
          path([(296,288),(256,288)]), hlab(256,296,288,'TOOLS'),
          path([(504,288),(544,288)]), hlab(504,544,288,'GATES'),
          path([(296,420),(152,420),(152,324)]), hlab(152,296,420,'CLUSTERS'),
          path([(752,288),(808,288)]), hlab(752,808,288,'DEPLOYS'),
          path([(440,324),(440,356),(892,356),(892,388)],'link'), hlab(440,892,356,'MODEL PROXY',LINK)]
    b += [node(296,132,208,64,'Tower','command console · Backstage'),
          node(48,252,208,72,'Airframe','XRDs · chart · contract'),
          node(296,252,208,72,'Autopilot','Clearance · AgentRun · proxy','focal'),
          node(544,252,208,72,'Glidepath','CI/CD · guardrails · releases'),
          node(296,388,208,64,'Apron','cluster template · ground','store'),
          node(808,252,168,72,'Skyport','demo apps + agents','input'),
          node(808,388,168,64,'Modelplane','self-hosted models','external')]
    b.append(callout(24,516,'Autopilot is the sixth product. It drives the Airframe A+ program and Skyport gains six AI workloads.'))
    b.append(legend(548,[('focal','New: Autopilot'),('backend','Exists today'),('store','Ground infrastructure'),('input','Reference system'),('external','Outside Hangar')]))
    return dict(slug='hangar-family', eyebrow='Architecture · 01 of 08 · The family',
      title='Hangar with Autopilot: six products and one reference system',
      desc='Architecture of the Hangar platform: Tower as the command console, Airframe, Autopilot and Glidepath as the middle layer, Apron as ground infrastructure, with Skyport as the reference system deployed by Glidepath and Modelplane as an outside model backend reached through Autopilot\'s model proxy.',
      lede='Autopilot sits beside Airframe and Glidepath, not above them. It uses Airframe\'s contract through tools, uses Glidepath\'s guardrails as gates, and shows up in Tower as an Agent tab.',
      body=''.join(b), W=1000, H=580, y0=60,
      cards=C3(P('One vocabulary, six products: Hangar, Apron, Airframe, Glidepath, Tower, Autopilot. Clearance and Flight recorder are features of Autopilot, like Tower\'s Ground Control.'),
               UL(['Airframe gains a machine-readable contract (the A+ program).','Autopilot adds Clearance, the AgentRun claim and a model proxy.','Skyport gains six AI workloads, one per workload shape.']),
               P('Each product keeps its own repo and its own install. Autopilot needs Airframe and Glidepath; it does not need Tower to run, only to be seen.'), 'Independence'))

def p_roadmap():
    b=[]
    GX0=248; PITCH=24; NW=28
    phases=[('M0 · stabilize and baseline · score 35',[('Chart guard + CI + baseline',1,2,0),('baggage-api, dogfood validate',1,3,0)]),
            ('M1 · contract · score 60',[('Strict schema + validate',3,6,0),('Outputs + MongoDB (born A+)',4,7,0)]),
            ('M2 · safe write · score 75',[('Base layer + owner split',7,10,0),('OAuth + walkthroughs',8,10,0)]),
            ('M3 · autopilot core · score 88',[('Clearance + AgentRun',11,16,0),('airframe tools + planner',13,18,1)]),
            ('M4 · skyport ai workloads · score 93',[('Task, session, service',19,21,0),('Scheduled, event, team',22,24,0)]),
            ('M5 · evidence and widen · score 97',[('Eval gate + autonomy ladder',25,28,0),('Modelplane trial + edge',25,28,0)])]
    for w in range(NW):
        b.append(text(GX0+w*PITCH+PITCH/2,56,f'{w+1}',8,400,SOFT,'middle',mono=True))
    b.append(text(GX0-8,56,'WEEK',8,500,MUTED,'end',mono=True,ls='0.14em'))
    b.append(f'<line x1="{GX0}" y1="64" x2="{GX0+NW*PITCH}" y2="64" stroke="{RULE}" stroke-width="0.8"/>')
    cur=76; zones=[]; bars=[]; labels=[]
    for pn,tasks in phases:
        zh = 20+len(tasks)*40+8
        zones.append(f'<rect x="24" y="{cur}" width="952" height="{zh}" rx="8" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.10)" stroke-width="0.8"/>')
        labels.append(text(36,cur+14,pn.upper(),8,500,MUTED,mono=True,ls='0.14em'))
        for i,(nm,s,e,foc) in enumerate(tasks):
            ry = cur+20+i*40
            assert len(nm)*6.7<=200, nm
            labels.append(text(36,ry+25,nm,12,600,INK))
            bx = GX0+(s-1)*PITCH; bw=(e-s+1)*PITCH
            f,st = ('rgba(185,121,31,0.12)',ACC) if foc else ('rgba(91,101,112,0.15)',MUTED)
            bars.append(f'<rect x="{bx}" y="{ry+8}" width="{bw}" height="24" rx="4" fill="{f}" stroke="{st}" stroke-width="1"/>')
        cur += zh + 12
    b += zones
    for wk,lbl in [(2,'M0'),(6,'M1'),(10,'M2'),(18,'M3'),(24,'M4'),(28,'M5')]:
        xx = GX0+wk*PITCH
        b.append(f'<line x1="{xx}" y1="64" x2="{xx}" y2="{cur-12}" stroke="{MUTED}" stroke-width="0.8" stroke-dasharray="4,3"/>')
        b.append(text(xx,40,lbl,8,500,ACC if lbl=='M3' else MUTED,'middle',mono=True,ls='0.14em'))
    b += bars + labels
    b.append(legend(cur+16,[('focal','Acceptance: the parachute sentence'),('input','Task'),('muted-dash','Milestone exit, verified live')]))
    return dict(slug='roadmap', eyebrow='Gantt · 02 of 08 · Roadmap',
      title='Twenty-eight weeks, six milestones, one score to move',
      desc='Gantt chart of twelve workstreams across six milestones over twenty-eight weeks: stabilize and baseline, contract, safe write, autopilot core with the airframe tools and planner as the acceptance test, Skyport AI workloads, and evidence and widening, with the Airframe scorecard target at the end of each milestone.',
      lede='Durations are estimates for one person; the order is the point. The contract comes before the next components, ownership comes before agent write tools, and the planner (the parachute sentence) is the acceptance test that everything before it exists to enable.',
      body=''.join(b), W=1000, H=cur+16+52, y0=24,
      cards=[('M0 to M2, before any agent writes','', UL(['Chart guard, strict schema, validate, outputs.','MongoDB and OAuth built already A+.','Ownership split and a base layer.'])),
             ('M3, the acceptance test','accent', UL(['Clearance, AgentRun, model proxy, real adapters.','airframe.* tools and the planner.','The parachute sentence passes live; a seeded bad run fails; killing Clearance still ends every run.'])),
             ('M4 and M5, proof','link', UL(['Six agents, six Checkride cases, six seeded bad runs.','Regression gate, autonomy ladder, Modelplane trial.','Scorecard at 14 of 14 and at least 97.']))])

def p_deps():
    b=[]
    b += [path([(232,236),(256,236),(256,176),(280,176)]), path([(232,260),(268,260),(268,336),(280,336)]),
          path([(488,176),(516,176),(516,236),(544,236)]), path([(488,336),(516,336),(516,260),(544,260)]),
          path([(768,236),(788,236),(788,176),(808,176)]), path([(768,260),(800,260),(800,336),(808,336)])]
    b += [node(40,212,192,72,'Contract foundation','guard · strict schema · validate'),
          node(280,140,208,72,'Outputs + new components','Mongo, OAuth: born A+'),
          node(280,300,208,72,'Ownership split','base layer · release file'),
          node(544,212,224,72,'Autopilot core + planner','Clearance · AgentRun · tools','focal'),
          node(808,140,168,72,'Skyport AI workloads','six shapes'),
          node(808,300,168,72,'Eval gate + autonomy','regression, ladder')]
    b.append(text(40,132,'RANK 1',8,500,SOFT,mono=True,ls='0.14em')); b.append(text(280,124,'RANK 2',8,500,SOFT,mono=True,ls='0.14em'))
    b.append(text(544,196,'RANK 3',8,500,SOFT,mono=True,ls='0.14em')); b.append(text(808,124,'RANK 4',8,500,SOFT,mono=True,ls='0.14em'))
    b.append(callout(24,428,'Nothing on the right can start until everything it points from is done and verified.'))
    b.append(legend(460,[('focal','The acceptance test lives here'),('backend','Milestone workstream'),('muted','Depends on')]))
    return dict(slug='dependencies', eyebrow='Dependency graph · 03 of 08 · Order',
      title='What blocks what: the critical path in six boxes',
      desc='Dependency graph in four ranks: the contract foundation feeds both the outputs and new born-A+ components and the ownership split; both feed the Autopilot core with the planner; and that feeds both the Skyport AI workloads and the evaluation gate.',
      lede='Skyport\'s remaining components join the contract stream instead of waiting behind it, so each is built once. Ownership must be split before agents get write tools, which is why it sits on the path to the Autopilot core.',
      body=''.join(b), W=1000, H=492, y0=100,
      cards=C3(P('Never retrofit. A component built before the contract needs a second pass; one built after is born with outputs, verify checks and full descriptions.'),
               UL(['Parallel and safe: docs and walkthroughs, the Autopilot repo setup, Modelplane reading.','Not parallel: the ownership split and Clearance write tools.','Skyport parts 4 and 5 (Mongo, OAuth) ride rank 2.']),
               P('The Skyport AI workloads also read baggage-api, so baggage-api and MongoDB must exist by rank 4, which the plan guarantees.'), 'Also'))

def p_scorecard():
    b=[]
    for x,w,t in [(24,196,'DIMENSION'),(228,84,'SCORE'),(320,300,'WHAT THE MEASUREMENT FOUND'),(628,348,'WHAT A+ CHANGES')]:
        b.append(text(x+8,108,t,8,500,MUTED,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="118" x2="976" y2="118" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('1 Discoverability',35,'no AGENTS.md or contract bundle; 6 of 13 XRDs cataloged','AGENTS.md, a generated contract bundle, a capabilities tool'),
          ('2 Schema precision',45,'12/234 nodes described; 0/68 objects strict; typos pass','schema-first, strict, 95% described, discriminated components'),
          ('3 Component contracts',4,'22 of 25 env entries hard-code a derived name','declared outputs, fromComponent, verify checks'),
          ('4 Pre-merge validation',22,'no validate; ground envs commit straight to main','airframe validate, six layers, required checks, dead-end rules'),
          ('5 Write safety',13,'4 of 4 live files mix human and machine-owned keys','one file one owner, a base layer, field risk classes'),
          ('6 Observe and verify',21,'Ready and Synced only; no reason codes or verify','a closed reason list, verify contracts, describe'),
          ('7 Docs for agents',39,'true quickstarts; none validated or executable','executable walkthroughs, YAML validated in CI'),
          ('8 Interaction surface',27,'Tower UI only; no plan, apply or verify API','AppSpec, planner, airframe tools, resumable'),
          ('9 Safety integration',20,'tiers reach paths, not fields; extraManifests is open','field-level scope; escape hatches denied by default'),
          ('10 Hygiene',46,'lint passes; no chart tests, no chart CI','chart tests, CI, a scorecard gate, a compatibility matrix')]
    y=128
    for name,sc,ev,ch in rows:
        assert len(ev)*4.8<=300-16 and len(ch)*4.8<=348-16, (ev,ch)
        b.append(f'<rect x="24" y="{y}" width="196" height="40" rx="4" fill="#ffffff" stroke="rgba(27,31,36,0.16)" stroke-width="1"/>')
        b.append(text(36,y+25,name,12,600,INK))
        b.append(f'<rect x="228" y="{y}" width="84" height="40" rx="4" fill="rgba(27,31,36,0.03)" stroke="rgba(27,31,36,0.12)" stroke-width="1"/>')
        b.append(text(238,y+25,str(sc),12,600,INK))
        b.append(f'<rect x="264" y="{y+17}" width="40" height="6" rx="3" fill="rgba(27,31,36,0.10)"/><rect x="264" y="{y+17}" width="{max(2,round(40*sc/100))}" height="6" rx="3" fill="{MUTED}"/>')
        b.append(f'<line x1="{264+round(40*0.97)}" y1="{y+13}" x2="{264+round(40*0.97)}" y2="{y+27}" stroke="{ACC}" stroke-width="1.2"/>')
        b.append(f'<rect x="320" y="{y}" width="300" height="40" rx="4" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.12)" stroke-width="1"/>')
        b.append(text(328,y+25,ev,8,400,MUTED,mono=True))
        b.append(f'<rect x="628" y="{y}" width="348" height="40" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="1"/>')
        b.append(text(636,y+25,ch,8,400,INK,mono=True))
        y+=44
    b.append(f'<rect x="24" y="{y+4}" width="952" height="40" rx="4" fill="rgba(185,121,31,0.08)" stroke="{ACC}" stroke-width="1"/>')
    b.append(text(36,y+29,'Overall 27 / 100 · 1 of 14 acceptance checks · A+ needs 97 and 14 of 14',12,600,INK))
    b.append(legend(y+72,[('focal','Overall'),('backend','Target state'),('store','Measured today')]))
    return dict(slug='scorecard', eyebrow='Matrix · 04 of 08 · Scorecard',
      title='The Airframe scorecard: ten dimensions, measured today',
      desc='Matrix of ten Airframe AI-friendliness dimensions with the measured baseline score, what the measurement found, and what an A+ requires, with an overall baseline of twenty-seven out of one hundred and one of fourteen acceptance checks passing.',
      lede='Re-runnable: hangar/tools/airframe-scorecard/scorecard.py. It measures readiness against the full contract, so most of the gap is artifacts that do not exist yet, not things that are broken. The amber tick on each bar is the A+ line at 97.',
      body=''.join(b), W=1000, H=y+72+52, y0=64,
      cards=C3(P('Measured, not felt. Every check is automated, so "A+" is a result the scorecard prints, not an opinion.'),
               UL(['The biggest gaps are also the cheapest: AGENTS.md, a contract bundle, validate, outputs.','Two real bugs found by running the chart: typos pass silently, and configuring before an image renders image ":".','Baseline committed: tools/airframe-scorecard/baseline-2026-09-26.json.']),
               P('The scorecard cannot judge whether an agent would actually succeed; the parachute sentence, run as a Checkride case, does. Use both.'), 'Limits'))

def p_contract():
    b=[]
    b += [path([(232,164),(296,164)]), path([(232,284),(296,284)]), path([(232,404),(296,404)]),
          path([(456,284),(520,284)],'accent'), hlab(456,520,284,'TAG',ACC),
          path([(680,168),(744,168)]), path([(680,248),(744,248)]), path([(680,328),(744,328)]), path([(680,408),(744,408)])]
    b += [node(32,132,200,64,'XRDs + chart schema','OpenAPI · values.schema.json'),
          node(32,252,200,64,'Sidecar meta','owner · risk · outputs · verify'),
          node(32,372,200,64,'Dead-end rules','AF ids + failing fixtures'),
          node(296,132,160,304,'Contract generator','CI, on each tag','focal'),
          node(520,132,160,304,'Contract bundle','airframe-contract.json','focal'),
          node(744,140,232,56,'airframe validate','CI check + agent tool'),
          node(744,220,232,56,'Tower','forms · validator'),
          node(744,300,232,56,'airframe.* tools','Clearance · MCP'),
          node(744,380,232,56,'Docs','AGENTS.md · reference')]
    b.append(callout(32,476,'One source, generated artifacts: nothing is written twice, so nothing can drift.'))
    b.append(legend(508,[('focal','Generated'),('backend','Source of truth or consumer'),('accent','Versioned with each tag'),('muted','Reads')]))
    return dict(slug='contract-architecture', eyebrow='Architecture · 05 of 08 · The contract',
      title='The contract: one source, generated artifacts, four consumers',
      desc='Architecture in which three sources of truth, the XRDs and chart schema, the sidecar meta and the dead-end rules, feed a contract generator that runs in CI on each tag and emits one versioned contract bundle, consumed by airframe validate, Tower, the airframe tools and the generated documentation.',
      lede='Everything an agent needs to know about Airframe comes out of one bundle. Validate, Tower\'s forms, the agent tools and the docs all read it, so they can never disagree.',
      body=''.join(b), W=1000, H=560, y0=100,
      cards=C3(P('Single source of truth. Today the same rules live in values.yaml comments, the schema, Tower\'s TypeScript and the quickstarts, and they drift.'),
               UL(['A CRD structural schema rejects unknown x- keys, so owners, risks, outputs and verify checks live in sidecar meta files.','Schema-first: values.yaml and the reference docs are generated from the schema, not the other way round.','The bundle is versioned with each Airframe tag, so a tool can ask "what was true at v0.3.90".']),
               P('Unverified: that Helm ignores unknown x-hangar keywords inside values.schema.json. Check with helm lint before relying on it; if not, keep them in the sidecar too.'), 'Check first'))

def p_plan_seq():
    b=[]
    X={'cl':110,'cs':310,'pl':510,'gh':710,'hu':890}
    top,bot=84,548
    for x in X.values():
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="rgba(27,31,36,0.22)" stroke-width="1" stroke-dasharray="3,3"/>')
    def msg(x1,x2,y,label,cx,color='link',dashed=False,lc=SOFT):
        return path([(x1,y),(x2,y)],color,dashed)+lab(cx,y-18,label,lc)
    ms=[msg(110,310,124,'airframe.capabilities',210),
        msg(310,110,160,'stacks · schema · registry',210,'muted',True),
        msg(110,310,196,'plan(appspec)',210),
        msg(310,510,232,'compile(spec, registry)',410),
        msg(510,310,268,'change set · 5 steps',410,'muted',True),
        msg(310,110,304,'plan + assumptions + warnings',210,'muted',True),
        msg(110,310,340,'apply(change set)',210),
        msg(310,710,376,'pr 1: tenants (app + 2 envs)',410),
        msg(890,710,412,'merge',800,'muted'),
        msg(710,310,448,'repos ready · cicdonboarded',410,'muted',True),
        msg(310,710,484,'pr 2 app repo · pr 3 gitops',410),
        msg(310,110,520,'verify: 4 envs configured',210,'accent',False,ACC)]
    b+=ms
    b += [node(30,24,160,56,'Claude Code','the user\'s session','input'),
          node(230,24,160,56,'Clearance','airframe.* tools','focal'),
          node(430,24,160,56,'Planner','pure function'),
          node(630,24,160,56,'GitHub + Argo','repos · sync','external'),
          node(810,24,160,56,'Human','merges flight PRs','input')]
    b.append(legend(580,[('link','Call'),('muted-dash','Return'),('accent','Verified'),('focal','Governed gate')]))
    return dict(slug='plan-apply-sequence', eyebrow='Sequence · 06 of 08 · One sentence',
      title='The parachute sentence, end to end',
      desc='Sequence diagram of an agent handling the request to provision a Python application named parachute: the agent asks for capabilities, sends an app spec to plan, Clearance calls the planner and returns a change set with assumptions, the agent applies it, Clearance opens a tenants PR that a human merges, waits for the repos, opens the app and gitops PRs, then returns a verified result.',
      lede='The agent never edits a file. It describes what it wants, reviews a plan with the assumptions stated, and applies it. Clearance opens PRs, humans merge the flight ones, and verify is a check against the running system, not a green pipeline.',
      body=''.join(b), W=1000, H=612,
      cards=C3(P('Plan before apply, and ambiguity is a question, not a guess: with two upper clusters and no choice, plan returns a question instead of picking one.'),
               UL(['plan is idempotent: the same spec gives the same change set, and a converged app is a no-op.','State lives on the task_id, PR labels and the audit log, so a session can end and resume.','Human gates: the tenants PR and the gitops PR. Ground changes auto-merge.']),
               P('Built and tested: the planner and 26 tests, including the generated XRs against the real XRD schemas, cicd.yaml against Glidepath\'s schema, and a real helm template. Not built: the adapters that open the PRs.'), 'What is built'))

def p_skyport_matrix():
    b=[]
    cols=[(24,208,'AGENT AND SHAPE'),(236,148,'TRIGGER'),(388,236,'WHAT IT DOES'),(628,176,'SKYPORT TOUCHPOINTS'),(808,168,'CHECKRIDE VERIFIER')]
    for x,w,t in cols: b.append(text(x+8,108,t,8,500,MUTED,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="118" x2="976" y2="118" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('flight-briefer','task','a person or an API asks','Ops brief for one flight from three APIs','flight, boarding, baggage APIs (read)','every fact matches the fixture'),
          ('gate-copilot','session','a gate agent opens a chat in Tower','Answers questions, drafts announcements, never sends','flight API; approvals in Tower','drafts never sent; scripted chat'),
          ('passenger-assistant','service','always on, public HTTP','Flight-status chat for passengers','boarding and flight APIs, Redis','golden Q&A; injection ignored'),
          ('delay-digest','scheduled','every 24 hours','Daily delays and gate-change report','flight API history; artifact store','counts match; second run is a no-op'),
          ('disruption-responder','event','flight.*.delayed on the broker','Drafts rebooking notices; hands major ones to the team','broker consumer; Clearance','one run per unique event'),
          ('irregular-ops-team','team','spawned by the responder','Planner with researcher, drafter and checker','all three APIs, narrowed','budgets conserved; bad spawn denied')]
    y=128
    for name,kind,trig,what,touch,ver in rows:
        h=56
        b.append(f'<rect x="24" y="{y}" width="208" height="{h}" rx="4" fill="#ffffff" stroke="rgba(27,31,36,0.16)" stroke-width="1"/>')
        b.append(text(36,y+24,name,12,600,INK)); b.append(text(36,y+42,'shape: '+kind,8,500,ACC if kind=='team' else MUTED,mono=True))
        for (x,w,_),v,fill,st in zip(cols[1:],[trig,what,touch,ver],['rgba(27,31,36,0.02)','#ffffff','rgba(27,31,36,0.05)','rgba(185,121,31,0.06)'],['rgba(27,31,36,0.12)',INK,MUTED,ACC]):
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{st}" stroke-width="1"/>')
            for i,ln in enumerate(wrap(v,int((w-16)/4.8))[:3]):
                b.append(text(x+8,y+22+i*13,ln,8,400,INK if x==388 else MUTED,mono=True))
        y+=60
    b.append(legend(y+12,[('backend','What it does'),('store','Touchpoints'),('focal','How it is proved')]))
    return dict(slug='skyport-ai-workloads', eyebrow='Matrix · 07 of 08 · Skyport AI',
      title='Skyport gains six AI workloads, one per shape',
      desc='Matrix of six Skyport AI agents, flight-briefer as a task, gate-copilot as a session, passenger-assistant as a service, delay-digest as scheduled, disruption-responder as event-driven and irregular-ops-team as a team, with each one\'s trigger, purpose, Skyport touchpoints and the Checkride verifier that proves it.',
      lede='Business-domain agents operating a system, plus the platform agents that already exist. None can apply a change: they read, draft, store artifacts, ask a human and spawn narrower runs. That is what "humans on the loop" looks like without the demo being able to break Skyport.',
      body=''.join(b), W=1000, H=y+12+52, y0=64,
      cards=C3(P('One workload per shape, so every part of Autopilot has a real caller and a test that can fail.'),
               UL(['Definitions and cases are built: 9 YAML files and 6 Checkride cases, all tested.','Built in order: task, session, service, scheduled, event, team.','Each part is walked live before it is called done.']),
               P('The service agent asks for the hardened sandbox. kind and Apple container have no runtime class, so it is Rejected on the dev cluster by design; running it there takes a reviewed commit that lowers isolation.'), 'A deliberate failure'))

def p_skyport_seq():
    b=[]
    X={'br':110,'bg':310,'cl':510,'rn':710,'tw':890}
    top,bot=84,548
    for x in X.values():
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="rgba(27,31,36,0.22)" stroke-width="1" stroke-dasharray="3,3"/>')
    def msg(x1,x2,y,label,cx,color='link',dashed=False,lc=SOFT):
        return path([(x1,y),(x2,y)],color,dashed)+lab(cx,y-18,label,lc)
    b += [msg(110,310,124,'delayed · msg m-42',210,'open',True),
          msg(310,510,160,'open_triggered(responder)',410),
          msg(510,310,196,'session s-1 (deduped)',410,'muted',True),
          msg(310,110,232,'ack',210,'muted',True),
          msg(510,710,268,'launch: agentrun claim',610),
          msg(710,510,304,'run.spawn(team, narrower)',610),
          msg(510,710,340,'child ok · budget reserved',610,'muted',True),
          msg(710,510,376,'run.spawn(worker, wider)',610),
          msg(510,710,412,'denied r007 · audited',610,'muted',True),
          msg(710,510,448,'human.request(draft notices)',610),
          msg(510,890,484,'approval request',700),
          msg(890,510,520,'approved',700,'accent',False,ACC)]
    b += [node(30,24,160,56,'skyport-broker','flights.events','external'),
          node(230,24,160,56,'Trigger bridge','an Airframe app'),
          node(430,24,160,56,'Clearance','policy · audit','focal'),
          node(630,24,160,56,'Responder run','then the team','input'),
          node(810,24,160,56,'Tower','approvals','input')]
    b.append(legend(580,[('link','Call'),('muted-dash','Return'),('open','Async message'),('accent','Human approval'),('focal','Governed gate')]))
    return dict(slug='skyport-event-to-team', eyebrow='Sequence · 08 of 08 · Event to team',
      title='A delayed flight becomes one draft, and a team, and a human decision',
      desc='Sequence of a delayed-flight event on the Skyport broker: the trigger bridge starts exactly one responder run through Clearance, using a task id derived from the message so a redelivery is deduplicated; the responder spawns a narrower team, a spawn asking for more than its parent has is denied and audited, and the drafts go to a human for approval in Tower.',
      lede='Three things are proved here: at-least-once delivery does not start two runs, delegation only narrows, and consequential output waits for a person. Every step carries the same task id, so the Flight recorder shows one story.',
      body=''.join(b), W=1000, H=612,
      cards=C3(P('At-least-once delivery needs an idempotent consumer: task_id is a hash of (agent, message id), and the trigger bridge acks only after the audit record exists.'),
               UL(['A storm brake (maxPerHour) bounds a flood of delayed events.','The denied spawn is a fixture, and the Checkride case asserts it was denied and audited.','Nothing is sent to a passenger: drafts wait for approval.']),
               P('Built and tested: topic matching, the dedupe key, the rate limiter, idempotent open_triggered, the narrow-only spawn and its denial. Not built: the bridge consumer and Tower\'s approvals.'), 'What is built'))
