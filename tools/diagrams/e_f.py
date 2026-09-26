from libx import *

def w_placement():
    b=[]
    b += [zone(24,84,952,152,'kiac-dev · type: dev · arm64'), zone(24,256,952,144,'github.com'), zone(24,420,952,144,'kind-prod · type: upper · amd64')]
    b += [path([(320,170),(368,170)]), hlab(320,368,170,'BROKER'),
          path([(648,170),(696,170)]), hlab(648,696,170,'CLAIM',ACC),
          path([(180,216),(180,272),(400,272),(400,292)],'link'), lab(290,254,'HTTPS · CHECKS',LINK),
          path([(508,216),(508,292)],'link'), vlab(508,216,292,'HTTPS · PR',LINK),
          path([(836,216),(836,338),(648,338)],'link'), hlab(648,836,338,'PULL',LINK),
          path([(500,456),(500,384)],'link'), vlab(500,384,456,'PULL AFTER HUMAN MERGE',LINK)]
    b += [depnode(40,124,280,92,'POD','glidepath · broker',[('/agent-token route','planned',True),('agent-scope gate','planned',True)]),
          depnode(368,124,280,92,'POD','clearance',[('MCP + policy + audit','planned',True),('model proxy','planned',True)],'focal'),
          depnode(696,124,280,92,'POD','argocd · crossplane',[('airframe','v0.3.90',False),('agentrun composition','planned',True)]),
          depnode(352,292,296,92,'MANAGED','GitHub App + repos',[('required checks','existing',False)]),
          depnode(352,456,296,92,'POD','argocd-apps',[('airframe','v0.3.90',False),('agent write path','none',False)])]
    b.append(text(676,494,'No Clearance and no runs on upper clusters:',12,600,INK))
    b.append(text(676,510,'agents reach them only as a PR that a human merges.',8,400,MUTED,mono=True))
    b.append(legend(590,[('focal','New service'),('backend','Exists today'),('link','Crosses a boundary'),('muted','Inside a cluster'),('accent','The claim')]))
    return dict(slug='fleet-placement', eyebrow='Deployment · 18 of 19 · Fleet placement',
      title='Where it runs: dev gets the write path and the runs, upper gets none',
      desc='Deployment diagram with three zones: the dev cluster hosting the planned clearance service with its model proxy, a glidepath and broker pod with a planned agent-token route and agent-scope gate, and ArgoCD with Crossplane and a planned agentrun composition; GitHub with required checks; and the upper cluster with ArgoCD only and no agent write path.',
      lede='This follows the cluster registry\'s dev and upper types. Bootstrap-tier mutations are already dev-only, and agent runs are the same shape, so a production cluster holds no agent credential and runs no agent.',
      body=''.join(b), W=1000, H=620, y0=64,
      cards=C3(P('Cluster-agnostic and generator-driven (ADR-0006). A cluster gets the feature by a toggle in cluster.yaml, and customize-cluster.sh refuses the invalid combination.'),
               UL(['apron/cluster.yaml: components.autopilot, refused on type: upper like providerGithub and platformCicd. New types hub and inference for the model fleet.','New group apron/55-autopilot/, and provider-kubernetes grants for the kinds a run renders.','Registry ConfigMap gains autopilotReady, set only after the network-policy canary passes.']),
               P('kiac-dev\'s CNI does not enforce NetworkPolicy; kind-prod\'s Calico does. Do not set autopilotReady on a claim. Run a canary pod that must fail to reach a blocked service, and gate the flag on that result.')))

def w_tiers():
    b=[]
    cols=[(308,'Task agent','in-cluster'),(452,'Delegated agent','human-driven'),(596,'Service agent','always on')]
    for x,n,s in cols:
        b.append(text(x+68,104,n,12,600,INK,'middle')); b.append(text(x+68,120,s,8,400,MUTED,'middle',mono=True))
    b.append(text(748,112,'DELEGATED TO',8,500,MUTED,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="132" x2="976" y2="132" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('Read: catalog, metrics, logs','T0',['allow','allow','allow'],'Backstage MCP, Prometheus, Loki (read)'),
          ('Read: ArgoCD app and diff','T0',['allow','allow','allow'],'ArgoCD API, read-only account'),
          ('Open a PR on an app repo','T1',['rev','rev','rev'],'Repo-scoped token, minted per call'),
          ('Request a lower env','T1',['never','rev','never'],'Commit to the tenants repo (GitOps)'),
          ('Sync or refresh a lower env','T1',['never','rev','never'],'ArgoCD role:clearance-lower'),
          ('Re-run a failed pipeline','T1',['never','rev','never'],"Tower's delegated re-run"),
          ('Start a child run','T1',['rev','rev','rev'],'AgentRun claim, narrower than parent'),
          ('PR to an upper gitops repo','T2',['prop','prop','prop'],'PR only; human merge, CODEOWNERS'),
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
    return dict(slug='tool-tiers', eyebrow='Access matrix · 12 of 19 · Tool tiers',
      title='What each kind of agent may do, and who really does it',
      desc='Access matrix of nine tool groups against three agent kinds, task agent, human-delegated agent and service agent, showing allow, allow but reversible in git, propose only, or never, with the delegated backing system for each tool.',
      lede='Write access is mostly a pull request, which a human can revert. The few imperative actions are delegated to systems that already audit themselves. The last row is not exposed to any identity, including Clearance itself.',
      body=''.join(b), W=1000, H=y+16+52, y0=64,
      cards=C3(P('Delegated over interactive. Every write action must state which category it falls in and the exact API it needs, before it is built (Tower write-action policy).'),
               UL(['Definitions are YAML in gitops-infra-clearance, reviewed like any change, and schema-validated in CI.','For delegated agents the ceiling is the intersection with the human\'s own Tower permissions.','Starting a child run is a claim, and a claim can only narrow: see Agent teams.']),
               P('As of the last handoff (2026-09-15), Tower Tier 1 write actions were built but not live-verified. Verify those first: Clearance would be delegating to something not yet proven against a genuinely stuck app.'), 'Caution'))

def w_authority():
    b=[]
    ins=[(132,'AgentDefinition','in git · reviewed','backend','TIER CEILING'),(212,'Human delegation','Tower permission policy','backend','USER RIGHTS'),
         (292,'Run claim','narrow-only, per run','backend','NARROWED TO'),(372,'Parent run','what the parent has left','backend','PARENT LEFT'),
         (452,'Runtime breaker','reduce-only state','security','TRIPPED?')]
    for y,n,s,k,l in ins:
        b.append(path([(264,y+28),(400,y+28)])); b.append(hlab(264,400,y+28,l))
    b += [path([(600,220),(680,220)]), hlab(600,680,220,'T0 · T1'),
          path([(600,316),(680,316)]), hlab(600,680,316,'RULE ID'),
          path([(600,412),(680,412)]), hlab(600,680,412,'T2')]
    for y,n,s,k,l in ins: b.append(node(32,y,232,56,n,s,k))
    b.append(node(400,108,200,456,'Policy decision','CEL over all five inputs','focal'))
    b += [node(680,188,224,64,'Allow','audit row written'),
          node(680,284,224,64,'Deny','rule id back to the agent'),
          node(680,380,224,64,'Propose only','PR opened, human merges','input')]
    b.append(callout(32,604,'Raising authority is a reviewed commit. Lowering it is immediate and needs no review.'))
    b.append(legend(636,[('focal','Decision'),('security','Reduce-only'),('backend','Input'),('input','Outcome: propose')]))
    return dict(slug='effective-authority', eyebrow='Architecture · 13 of 19 · Authority',
      title='Effective authority is the minimum of five inputs, and runtime can only lower it',
      desc='Architecture showing five inputs, the git-managed agent definition, the human\'s delegated permissions, the narrow-only run claim, the parent run\'s remaining budget, and a reduce-only runtime breaker, feeding one CEL policy decision that yields allow with an audit row, deny with a rule id, or propose only for a pull request that a human merges.',
      lede='Any of the five can say no; none can say yes on behalf of another. The claim and the parent can only narrow what the definition grants, and the breaker can only take authority away, so a compromised run cannot widen its own reach.',
      body=''.join(b), W=1000, H=676, y0=72,
      cards=C3(P('Least privilege, fail toward less. Runtime state may only reduce authority; raising it is a git commit, like every other durable change.'),
               UL(['Definitions live in gitops-infra-clearance/agents/*.yaml, schema-validated like cicd.yaml is.','The breaker is state inside Clearance only; a tripped run is also frozen by setting one field on its AgentRun.','Sessions live in memory on one replica for now. A restart ends them, which is the safe direction.']),
               P('Fifteen CEL rules, each with an id and a hint, are tested one at a time: each input alone must force a deny, and the whole policy must fail closed if evaluation errors. That table is in the repository.'), 'Proved in code'))

def w_rollout():
    b=[]
    GX0=248; PITCH=44; NW=16
    phases=[('A · read-only and claims, dev only',[
               ('apron: autopilot toggle',1,2,0),('Clearance as InfraService',1,4,0),('T0 read tools',3,4,0),('AgentRun + expiry test',2,6,0)]),
            ('B · governed writes, lower only',[
               ('Interceptor agent-token route',5,6,1),('Model proxy v0',5,8,0),('T1 tools + run.spawn',6,9,0),('Gates: scope + identity',7,10,0)]),
            ('C · evidence and any agent',[
               ('Agent XRD + two templates',9,13,0),('Recorder + GenAI traces',9,12,0),('Checkride v0',10,14,0)]),
            ('D · widen',[
               ('Triggers + Holmes routing',13,16,0)])]
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
    for wk,lbl in [(6,'VERIFY A'),(10,'VERIFY B'),(14,'VERIFY C')]:
        xx = GX0+wk*PITCH
        b.append(f'<line x1="{xx}" y1="64" x2="{xx}" y2="{cur-12}" stroke="{MUTED}" stroke-width="0.8" stroke-dasharray="4,3"/>')
        b.append(text(xx,40,lbl,8,500,MUTED,'middle',mono=True,ls='0.14em'))
    b += bars + labels
    b.append(legend(cur+16,[('focal','Credential boundary'),('input','Task'),('muted-dash','Live-verify gate before the next phase')]))
    return dict(slug='rollout-plan', eyebrow='Gantt · 19 of 19 · Rollout',
      title='Rollout: four phases, each closed by a live check before the next begins',
      desc='Gantt chart of twelve tasks over sixteen weeks in four phases: read-only and claims on dev, governed writes on lower environments, evidence and any-agent support, then triggers and routing Holmes through Clearance, with live-verify checkpoints after weeks six, ten and fourteen.',
      lede='Each phase ends with a check against real state, not a checklist. Durations are estimates for one person working alone, which is how Hangar has been built. A Modelplane hub trial and a second cloud come after this, once agents run and their spend is bounded.',
      body=''.join(b), W=1000, H=cur+16+52, y0=24,
      cards=[('Verify A · end of week 6','', UL(['A T0 call works end to end and leaves an audit row.','A run ends on time with Clearance stopped, and again with the function pod killed.','The network-policy canary fails on kiac-dev (reported honestly) and passes on kind-prod.','customize-cluster.sh refuses autopilot on a type: upper cluster.'])),
             ('Verify B · end of week 10','accent', UL(['A repo-scoped token cannot open a PR on any other repo.','Upper sync and any kubectl write are refused with the agent token.','A PR that edits .tekton/ turns agent-scope red and cannot merge.','A model call for a model off the allowlist is denied and audited.'])),
             ('Verify C · end of week 14','link', UL(['One task_id runs from audit row to Argo annotation to a Loki line.','Checkride scores the seed cases, and a seeded bad run fails.','A new agent scaffolded from a template runs end to end with no platform change.']))])
