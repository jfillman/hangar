from libx import *

def e09():
    b=[]
    b += [zone(24,100,440,448,'today · live-verified 2026-08-13'), zone(536,100,440,448,'with clearance · proposed')]
    b += [path([(244,192),(244,244)]), vlab(244,192,244,'RENDERS'),
          path([(244,296),(244,348)]), vlab(244,296,348,'POST /API/CHAT'),
          path([(244,400),(244,452)],'accent',dashed=True), vlab(244,400,452,'STANDING PAT',ACC),
          path([(756,184),(756,212)]), vlab(756,184,212,'RENDERS'),
          path([(756,264),(756,292)]), vlab(756,264,292,'CHAT + TASK ID'),
          path([(756,344),(756,372)],'link'), vlab(756,344,372,'MCP · SA TOKEN',LINK),
          path([(756,424),(756,452)],'link'), vlab(756,424,452,'PR · INSTALL TOKEN',LINK)]
    b += [node(124,140,240,52,'Rollout degraded','RolloutWatch XR'),
          node(124,244,240,52,'Dispatch Job','zero RBAC · one HTTP call'),
          node(124,348,240,52,'HolmesGPT','model key · PAT · cluster RBAC'),
          node(124,452,240,52,'GitHub PR','e.g. idp#8, 2026-08-13'),
          node(636,132,240,52,'Rollout degraded','RolloutWatch XR'),
          node(636,212,240,52,'Dispatch Job','SA token · aud clearance'),
          node(636,292,240,52,'HolmesGPT','model key · cluster read'),
          node(636,372,240,52,'Clearance','profile: triage · budgets','focal'),
          node(636,452,240,52,'GitHub PR','signed · task id trailer')]
    b.append(legend(580,[('focal','New'),('backend','Exists today'),('accent-dash','Standing credential'),('link','Governed call')]))
    return dict(slug='triage-before-after', eyebrow='Architecture · 09 of 11 · AI triage',
      title='AI triage: move Holmes\'s GitHub access behind Clearance',
      desc='Two-panel architecture comparing the current AI triage flow, where a degraded rollout renders a dispatch job that calls HolmesGPT, which holds a standing GitHub token and cluster RBAC and opens a fix pull request, with the proposed flow where Holmes calls Clearance with a service-account token and Clearance opens the pull request using a per-call installation token under a budget.',
      lede='This is the first real consumer, and it already works: a broken canary produced a real diagnosis and a real fix PR. The change is small and removes a standing credential, which also takes pressure off a GitHub rate limit that four or more shared tokens have already hit.',
      body=''.join(b), W=1000, H=620, y0=76,
      cards=C3(P('Never-persisted credentials, and one GitHub App per consumer as the durable fix for the shared rate-limit bucket (documented in the rate-limit investigation).'),
               UL(['Holmes\'s GitHub MCP toolset is pointed at Clearance instead of holding github-mcp-token.','Clearance enforces a per-session GitHub API budget; the hot-loop that made ~16k calls an hour is the exact failure this bounds.','The dispatch Job stays exactly as it is: zero RBAC, one HTTP call.']),
               P('Unverified: whether Holmes can call an MCP server that authenticates with a projected service-account token, and forward a task id per request. Check Holmes\'s MCP config before committing to this design. Its cluster read RBAC stays a documented exception.'), 'Open questions'))

def e10():
    b=[]
    ins=[(132,'AgentProfile','in git · reviewed','backend','TIER CEILING'),(220,'Human delegation','Tower permission policy','backend','USER RIGHTS'),
         (308,'Session budget','calls · API · minutes','backend','REMAINING'),(396,'Runtime breaker','reduce-only state','security','TRIPPED?')]
    for y,n,s,k,l in ins:
        b.append(path([(264,y+28),(400,y+28)])); b.append(hlab(264,400,y+28,l))
    b += [path([(600,200),(680,200)]), hlab(600,680,200,'T0 · T1'),
          path([(600,296),(680,296)]), hlab(600,680,296,'RULE ID'),
          path([(600,392),(680,392)]), hlab(600,680,392,'T2')]
    for y,n,s,k,l in ins: b.append(node(32,y,232,56,n,s,k))
    b.append(node(400,108,200,352,'Policy decision','CEL over all four inputs','focal'))
    b += [node(680,168,224,64,'Allow','audit row written'),
          node(680,264,224,64,'Deny','rule id back to the agent'),
          node(680,360,224,64,'Propose only','PR opened, human merges','input')]
    b.append(callout(32,500,'Raising authority is a reviewed commit. Lowering it is immediate and needs no review.'))
    b.append(legend(532,[('focal','Decision'),('security','Reduce-only'),('backend','Input'),('input','Outcome: propose')]))
    return dict(slug='effective-authority', eyebrow='Architecture · 10 of 11 · Authority',
      title='Effective authority is the minimum of four inputs, and runtime can only lower it',
      desc='Architecture showing four inputs, the git-managed agent profile, the human\'s delegated permissions, the remaining session budget, and a reduce-only runtime breaker, feeding one CEL policy decision that yields allow with an audit row, deny with a rule id, or propose only for a pull request that a human merges.',
      lede='Any of the four can say no; none can say yes on behalf of another. The breaker is the only input that changes at runtime, and it can only take authority away, so a compromised session cannot widen its own reach.',
      body=''.join(b), W=1000, H=580, y0=72,
      cards=C3(P('Least privilege, fail toward less. Runtime state may only reduce authority; raising it is a git commit, like every other change here.'),
               UL(['Profiles live in gitops-infra-clearance/agents/*.yaml, schema-validated like cicd.yaml is.','The breaker is state inside Clearance only; it needs no Kubernetes write credential.','Sessions live in memory on one replica for now. A restart ends them, which is the safe direction.']),
               P('A CEL policy is testable as a table: for each (profile, user, tool, budget, breaker) row, an expected decision. Run that table in CI, and include rows where each input alone should force a deny.'), 'Test it as a table'))

def e11():
    b=[]
    GX0=248; PITCH=44; NW=16
    phases=[('A · read-only, dev only',[
               ('apron: autopilot toggle',1,2,0),('Clearance as InfraService',1,4,0),('T0 read tools',3,4,0),('Netpol conformance canary',2,3,0)]),
            ('B · governed writes, lower only',[
               ('Interceptor agent-token route',5,6,1),('T1 write tools, lower only',6,8,0),('Gates: scope + identity',5,9,0)]),
            ('C · evidence and evaluation',[
               ('Flight recorder task_id',8,11,0),('Checkride v0, 2 then 6 cases',8,12,0),('Holmes via Clearance',10,12,0)]),
            ('D · widen',[
               ('Autonomy tracker, shadow',12,15,0),('Conformance on EKS or OKE',13,16,0)])]
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
    for wk,lbl in [(4,'VERIFY A'),(9,'VERIFY B'),(12,'VERIFY C')]:
        xx = GX0+wk*PITCH
        b.append(f'<line x1="{xx}" y1="64" x2="{xx}" y2="{cur-12}" stroke="{MUTED}" stroke-width="0.8" stroke-dasharray="4,3"/>')
        b.append(text(xx,40,lbl,8,500,MUTED,'middle',mono=True,ls='0.14em'))
    b += bars + labels
    b.append(legend(cur+16,[('focal','Credential boundary'),('input','Task'),('muted-dash','Live-verify gate before the next phase')]))
    return dict(slug='rollout-plan', eyebrow='Gantt · 11 of 11 · Rollout',
      title='Rollout: four phases, each closed by a live check before the next begins',
      desc='Gantt chart of eleven tasks over sixteen weeks in four phases: read-only on dev, governed writes on lower environments, evidence and evaluation, then widening to autonomy tracking and a second cloud, with live-verify checkpoints after weeks four, nine and twelve.',
      lede='Each phase ends with a check against real state, not a checklist. Durations are estimates for one person working alone, which is how Hangar has been built; treat them as ordering, not a promise.',
      body=''.join(b), W=1000, H=cur+16+52, y0=24,
      cards=[('Verify A · end of week 4','', UL(['A T0 read call works end to end, and an audit row exists for it.','The network-policy canary fails as it should on kind-prod and is reported honestly on kiac-dev.','customize-cluster.sh refuses components.autopilot on a type: upper cluster.'])),
             ('Verify B · end of week 9','accent', UL(['An agent PR opens with a repo-scoped token, and the token cannot open a PR on any other repo.','Upper-env sync and any kubectl write are refused with the agent token.','A PR that edits .tekton/ turns agent-scope red and cannot merge.'])),
             ('Verify C · end of week 12','link', UL(['Every record of one agent task shares a task_id, from audit row to Argo annotation.','Checkride scores the two seed cases, and a seeded bad run scores as failed.','Holmes opens a PR through Clearance; github-mcp-token is deleted.']))])
