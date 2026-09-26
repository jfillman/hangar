from lib import *
from d123 import P, UL

def d10():
    b=[]
    top=140; bot=300
    b += [path([(164,172),(228,172)]), hlab(164,228,172,'replay'),
          path([(368,172),(432,172)]), hlab(368,432,172,'run'),
          path([(572,172),(636,172)]), hlab(572,636,172,'trace'),
          path([(776,172),(840,172)]), hlab(776,840,172,'score'),
          path([(706,204),(706,300)]), vlab(706,204,300,'record'),
          path([(910,204),(910,300)]), vlab(910,204,300,'verdict'),
          path([(502,300),(502,204)],'link'), vlab(502,204,300,'new version',LINK),
          path([(930,356),(930,396),(502,396),(502,356)],dashed=True), lab(716,404,'blocked: revise and resubmit')]
    b += [node(24,top,140,64,'Task corpus','replayable · versioned','store'),
          node(228,top,140,64,'Disposable sandbox','fresh per run'),
          node(432,top,140,64,'Agent under test','model · prompt · tools','input'),
          node(636,top,140,64,'Verifier scorer','outcome · blast radius','focal'),
          node(840,top,140,64,'Regression gate','no worse than base'),
          node(636,bot,140,56,'Scorecard history','per version','store'),
          node(840,bot,140,56,'Ship or block','the change'),
          node(432,bot,140,56,'Proposed change','model · prompt · tool','input')]
    b.append(callout(24,252,'Same corpus for every change,'))
    b.append(callout(24,276,'scored by verifiers, not by another model.'))
    b.append(legend(452,[('focal','Judge of record'),('input','Thing under change'),('store','History'),('link','Change enters loop'),('muted-dash','Feedback')]))
    return dict(slug='agent-eval-harness', eyebrow='Process · 10 of 11 · Evaluating infrastructure agents',
      title='Evaluating infrastructure agents: a regression suite, not a vibe',
      desc='Process diagram of an evaluation loop: a versioned corpus of replayable incidents and tasks runs an agent under test in a fresh sandbox, a deterministic scorer records outcome, blast radius, policy violations and cost, a regression gate ships or blocks the model, prompt or tool change, and blocked changes loop back for revision.',
      lede='Every model, prompt or tool change is replayed against the same corpus in disposable sandboxes and scored by the same verifiers that gate production. If it is worse than the baseline, it does not ship.',
      body=''.join(b), W=1000, H=496, y0=112,
      cards=[('Requirement','', P('Opinions about how to evaluate infrastructure agents. Almost nobody has these yet.')),
             ('Design choices','accent', UL(['Corpus: past incidents and golden-path tasks, replayable against a fresh sandbox.','Scored on outcome, blast radius, policy violations, retries and cost, all by deterministic verifiers.','Scorecard history makes model and prompt regressions visible per version.'])),
             ('Evidence and gap','link', P('Built in Hangar: the verifier side (gate checks, verify contracts, release records). Proposal only: the replay corpus and harness. Say plainly that this is the design you would build first, not something you have run.'))])

def d11():
    b=[]
    GX0=248; PITCH=52; NW=13
    phases=[('days 1–30 · learn and land',[
               ('Map estate, owners, pipelines',1,3,0),('Baseline DORA and toil',1,4,0),
               ('Shadow on-call, read history',2,4,0),('AWS and OCI fluency lab',1,4,0)]),
            ('days 31–60 · one thin slice',[
               ('Agent sandbox v0, one team',5,8,0),('MCP gateway v0: reads',5,8,1),('CI loop: structured failures',6,9,0)]),
            ('days 61–90 · extend and measure',[
               ('T1 writes + policy engine',9,12,0),('Triage agent, shadow mode',9,13,0),('Eval harness v0',8,12,0),
               ('Metrics + lasting docs',10,13,0),('Drift inventory, converge',9,13,0)])]
    # axis
    for w in range(NW):
        b.append(text(GX0+w*PITCH+PITCH/2,56,f'W{w+1}',8,400,SOFT,'middle',mono=True))
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
    for wk,lbl in [(4,'D30'),(8,'D60'),(13,'D90')]:
        xx = GX0+wk*PITCH
        b.append(f'<line x1="{xx}" y1="64" x2="{xx}" y2="{cur-12}" stroke="{MUTED}" stroke-width="0.8" stroke-dasharray="4,3"/>')
        b.append(text(xx,40,lbl,8,500,ACC if wk==13 else MUTED,'middle',mono=True,ls='0.14em'))
    b += bars + labels
    b.append(legend(cur+16,[('focal','First thing that ships'),('input','Task'),('muted-dash','Day-30 / 60 / 90 checkpoints')]))
    return dict(slug='plan-30-60-90', eyebrow='Gantt · 11 of 11 · First 90 days',
      title='First 90 days: learn, land a thin slice, then extend and measure',
      desc='Gantt chart of twelve tasks over thirteen weeks in three phases: learn and land in days one to thirty, one thin slice of sandbox, MCP gateway and CI loop in days thirty-one to sixty, then write tools, triage agent, evaluation harness, metrics and convergence work in days sixty-one to ninety.',
      lede='Read the estate before touching it, ship one thin governed slice for one team, then widen it with numbers to prove it is working.',
      body=''.join(b), W=1000, H=cur+16+52, y0=24,
      cards=[('Day 30 · exit criteria','', UL(['I can explain every deploy path and who owns it.','Baseline for deploy frequency, lead time, change failure rate, MTTR and hands-off share is published.','I have run one real workload on the cloud I have less time on.'])),
             ('Day 60 · exit criteria','accent', UL(['One agent, one team, one environment, working end to end.','Read-only MCP tools behind the gateway with a complete audit trail.','A CI loop where failures come back structured.'])),
             ('Day 90 · exit criteria','link', UL(['Write tools at T1 behind policy; triage agent running in shadow mode on one alert class.','Eval harness scoring it against replayed incidents.','First quarter-over-quarter deltas on the numbers.']))])
