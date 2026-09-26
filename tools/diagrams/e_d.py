from libx import *

def w_two_planes():
    b=[]
    b += [zone(24,84,432,336,'durable plane · git · reviewed'), zone(544,84,432,336,'ephemeral plane · claims · ttl')]
    b += [path([(240,292),(240,324)]), vlab(240,292,324,'PULL'),
          path([(760,196),(760,228)]), vlab(760,196,228,'RENDERS'),
          path([(760,292),(760,324)]), vlab(760,292,324,'CREATES'),
          path([(432,164),(568,164)]), hlab(432,568,164,'NARROWS'),
          path([(568,356),(500,356),(500,260),(432,260)],dashed=True), hlab(500,568,356,'PR ONLY')]
    b += [node(48,132,384,64,'Agent definitions and policy','ceilings, tools, network · reviewed commit'),
          node(48,228,384,64,'App, gitops and tenants repos','PRs · xr-requests · platform/envs'),
          node(48,324,384,64,'ArgoCD pulls','per cluster · lower and upper'),
          node(568,132,384,64,'AgentRun claim','namespaced XR · dev clusters only · TTL'),
          node(568,228,384,64,'Crossplane composition','function-agentrun · a pure function'),
          node(568,324,384,64,'Run namespace','sandbox · budget · gone at expiresAt','focal')]
    b.append(callout(24,452,'The ephemeral plane can only narrow what the durable plane grants. It reaches the durable plane only as a PR.'))
    b.append(legend(484,[('focal','Ephemeral sandbox'),('backend','Component'),('muted','Flow'),('muted-dash','Proposal only')]))
    return dict(slug='two-planes', eyebrow='Architecture · 02 of 19 · Two planes',
      title='Durable changes are commits. Ephemeral runs are claims.',
      desc='Architecture with two planes: a durable plane where agent definitions, repos and ArgoCD change only by reviewed git commits, and an ephemeral plane where an AgentRun claim is rendered by a Crossplane function into a sandbox namespace that disappears at its deadline, with durable ceilings narrowing every claim and the ephemeral plane reaching the durable one only through a pull request.',
      lede='Committing every session to git would be slow, noisy, rate-limited and unreviewable. So ephemeral, bounded, disposable things are created as claims, and everything that outlives a run stays a reviewed commit.',
      body=''.join(b), W=1000, H=540, y0=60,
      cards=[('Principle, revised','', P('Every durable mutation is a git commit. An ephemeral one is a declarative claim to an already-privileged control plane (Crossplane), never a direct write. That is still delegate-to-the-audited-system, and still dev-only.')),
             ('The ephemerality test','accent', UL(['It has a hard deadline that needs no Clearance to enforce.','It holds no durable state, and reaches the durable plane only as a PR.','One narrowly scoped identity creates it, in one reserved namespace.','It can only narrow what git grants.','It can be rebuilt from git plus the task spec. Fail any one and it goes through git.'])),
             ('What this costs','link', P('Clearance now holds one Kubernetes permission: create, get, patch and delete AgentRun in autopilot-runs, on dev clusters. That is a real departure from zero write credentials, so it is one kind in one namespace, and the composition, not the caller, decides what gets created.'))])

def w_shapes():
    b=[]
    cols=[(24,172,'SHAPE'),(200,148,'TRIGGER'),(352,132,'LIFETIME'),(488,164,'DURABLE (GIT)'),(656,164,'EPHEMERAL (CLAIM)'),(824,152,'EXAMPLES')]
    for x,w,t in cols: b.append(text(x+8,108,t,8,500,MUTED,mono=True,ls='0.14em'))
    b.append(f'<line x1="24" y1="118" x2="976" y2="118" stroke="{RULE}" stroke-width="0.8"/>')
    rows=[('Task agent','task','human, API, agent','to completion','Agent definition','AgentRun','coding, triage'),
          ('Session agent','session','human in Tower','bounded TTL','Agent definition','AgentRun (interactive)','pairing, review'),
          ('Service agent','service','always on','until removed','Agent + Rollout',None,'chat bot, Holmes'),
          ('Scheduled agent','scheduled','cron in definition','per run','Agent + schedule','AgentRun per tick','nightly review'),
          ('Event agent','event','alert or webhook','per event','Agent + trigger','AgentRun per event','incident triage'),
          ('Agent team','team','a parent run','inside parent','Agent definitions','child AgentRuns','planner + workers')]
    y=128
    for i,(n,k,trig,life,dur,eph,ex) in enumerate(rows):
        team = (k=='team')
        b.append(f'<rect x="24" y="{y}" width="172" height="48" rx="4" fill="#ffffff" stroke="rgba(27,31,36,0.16)" stroke-width="1"/>')
        b.append(text(36,y+21,n,12,600,INK)); b.append(text(36,y+37,'kind: '+k,8,400,MUTED,mono=True))
        for (x,w,_),v in zip(cols[1:3],[trig,life]):
            assert len(v)*6.7<=w-16, v
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="4" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.12)" stroke-width="1"/>')
            b.append(text(x+8,y+29,v,12,400,INK))
        x,w,_=cols[3]
        assert len(dur)*6.7<=w-16, dur
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="1"/>')
        b.append(text(x+8,y+29,dur,12,600,INK))
        x,w,_=cols[4]
        if eph is None:
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="4" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.25)" stroke-width="1" stroke-dasharray="4,3"/>')
            b.append(text(x+8,y+29,'none: not a run',12,400,SOFT))
        else:
            assert len(eph)*6.7<=w-16, eph
            f,st = ('rgba(185,121,31,0.08)',ACC) if team else ('rgba(27,31,36,0.05)',MUTED)
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="4" fill="{f}" stroke="{st}" stroke-width="1"/>')
            b.append(text(x+8,y+29,eph,12,600,INK))
        x,w,_=cols[5]; assert len(ex)*6.7<=w-8, ex
        b.append(text(x+8,y+29,ex,12,400,MUTED))
        y+=56
    b.append(legend(y+12,[('backend','Durable, in git'),('store','Ephemeral claim'),('optional','Not a run'),('focal','Narrowing enforced')]))
    return dict(slug='workload-shapes', eyebrow='Matrix · 04 of 19 · Workload shapes',
      title='Any agent workload is one of six shapes, built from two kinds of thing',
      desc='Matrix of six agent workload shapes, task, session, service, scheduled, event and team, showing for each the trigger, lifetime, the durable git part and the ephemeral AgentRun claim, where a service agent has no ephemeral part because it is an ordinary deployed application.',
      lede='The platform does not care what the agent does or which framework it uses. A definition is durable and reviewed. A run is a disposable instance of it. A long-running service agent is just the durable half, deployed the way any application is.',
      body=''.join(b), W=1000, H=y+12+52, y0=60,
      cards=C3(P('Definition durable, run ephemeral. Service agents reuse the existing application path, so nothing new is invented for them.'),
               UL(['Today: an AgentDefinition YAML in git, schema-validated in CI.','Later: an Agent XRD so Tower generates a New Agent form from it, like every other XRD.','Triggers are part of the definition; each firing becomes an AgentRun.']),
               P('Run one agent of each shape, and one that should be refused (a delegated agent triggered by cron, which Clearance denies). The refusal is the more useful test.')))

def w_definition_to_run():
    b=[]
    b += [zone(16,100,968,124,'durable · git · reviewed',center=True), zone(16,244,968,144,'ephemeral · claims · ttl',center=True)]
    b += [path([(176,164),(424,164)]), hlab(176,424,164,'ON MERGE'),
          path([(576,164),(824,164)]), hlab(576,824,164,'SIGN + SCAN'),
          path([(96,196),(96,260),(296,260),(296,300)]), hlab(96,296,260,'DEFINITION + PROFILE'),
          path([(900,196),(900,300)]), vlab(900,196,300,'IMAGE PULL'),
          path([(168,332),(224,332)]), hlab(168,224,332,'EVENT'),
          path([(368,332),(424,332)],'accent'), hlab(368,424,332,'CLAIM',ACC),
          path([(568,332),(624,332)]), hlab(568,624,332,'RENDERS'),
          path([(768,332),(824,332)]), hlab(768,824,332,'CREATES')]
    b += [node(24,132,152,64,'Agent definition','YAML in git','focal'),
          node(424,132,152,64,'Glidepath','build · scan · sign'),
          node(824,132,152,64,'Signed image','pinned by digest','store'),
          node(24,300,144,64,'Trigger','manual · cron · alert','input'),
          node(224,300,144,64,'Clearance','policy · narrow-only'),
          node(424,300,144,64,'AgentRun claim','ephemeral XR','focal'),
          node(624,300,144,64,'Crossplane','function-agentrun'),
          node(824,300,152,64,'Run namespace','sandbox · TTL')]
    b.append(legend(420,[('focal','New'),('backend','Exists today'),('store','Artifact'),('input','Trigger'),('accent','The claim')]))
    return dict(slug='definition-to-run', eyebrow='Architecture · 05 of 19 · Definition to run',
      title='From a reviewed definition to a disposable run',
      desc='Architecture in two zones: a durable zone where an agent definition merged in git triggers Glidepath to build, scan and sign an image pinned by digest, and an ephemeral zone where a trigger reaches Clearance, which checks policy against the definition and creates an AgentRun claim that Crossplane renders into a run namespace which pulls the signed image.',
      lede='The image is built and signed by the same pipeline as any application, so a run can only execute what was reviewed. The run itself is a claim that Clearance narrows and Crossplane renders.',
      body=''.join(b), W=1000, H=470, y0=76,
      cards=C3(P('Supply chain first: agent code is untrusted code. Images are signed by Glidepath (cosign, self-hosted Fulcio and Rekor) and referenced by digest, never by tag.'),
               UL(['Admission verifies the signature (Kyverno verifyImages is already in the cluster).','Third-party agent images take the same path, and default to the hardened sandbox class where the cluster has one.','A run whose image is not on the signed path is rejected, not warned about.']),
               P('Try to run an unsigned image, and a tag instead of a digest. The XRD schema refuses the tag; admission has to refuse the unsigned image. Test the second one, not just the first.')))

def w_run_anatomy():
    b=[]
    b.append(zone(24,100,712,380,'run namespace · agent-r-<id> · pod security restricted'))
    b += [path([(296,152),(776,152)],'link'), hlab(296,776,152,'MCP · RUN TOKEN',LINK),
          path([(296,212),(776,212)],'link'), hlab(296,776,212,'LLM CALLS · SESSION AS CALLER',LINK),
          path([(176,220),(176,252)]), vlab(176,220,252,'LOCALHOST'),
          path([(280,220),(280,380),(256,380)],dashed=True)]
    b += [node(56,132,240,88,'Agent container','any framework · any language','focal'),
          node(56,252,200,64,'MCP sidecars','bundled tools · no credentials','optional'),
          node(56,348,200,64,'Attached components','Postgres · Redis · queue','optional'),
          node(440,252,264,56,'Run identity','projected tokens · aud clearance, model-proxy','security'),
          node(440,324,264,56,'Workspace','emptyDir · scratch and /run/output','store'),
          node(440,396,264,56,'Guard rails','quota · limits · default-deny egress','store'),
          node(776,124,200,56,'Clearance','tools · policy · audit','focal'),
          node(776,200,200,56,'Model proxy','allowlist · budget · caller id')]
    b.append(legend(508,[('focal','Agent and gate'),('security','Identity'),('store','Guard'),('optional','Optional'),('link','Governed call')]))
    return dict(slug='run-anatomy', eyebrow='Architecture · 06 of 19 · Run anatomy',
      title='What a run gets, and the only two ways out',
      desc='Architecture of a run namespace containing an agent container of any framework, optional bundled MCP sidecars, optional attached components, a projected run identity, a scratch workspace and guard rails, with exactly two egress paths, to Clearance for tools and to the model proxy for models, and no provider keys inside.',
      lede='The contract is small on purpose so any framework fits: environment in, a workspace and an output folder, two audience-bound tokens, and two places to send traffic. Nothing inside holds a credential.',
      body=''.join(b), W=1000, H=548, y0=76,
      cards=C3(P('Least privilege by construction. Default-deny egress with two exceptions, no secrets in the namespace (the quota forbids them), a token that names its audience.'),
               UL(['Environment: HANGAR_RUN_ID, TASK_ID, SESSION_ID, EXPIRES_AT, LIMITS, INPUT, CLEARANCE_URL, MODEL_PROXY_URL.','Files: /workspace to work in, /run/output for results, tokens under /var/run/hangar.','On SIGTERM, checkpoint within 30 seconds. Sidecars get the same lockdown and no env.']),
               P('Kubernetes has no pod exec here by policy, so a human cannot shell into a run. Debugging is via output, logs and the audit record. Decide whether that is acceptable before promising it to users.'), 'Consequence'))

def w_lifecycle():
    b=[]
    b.append(f'<circle cx="32" cy="232" r="6" fill="{INK}"/>')
    b += [path([(38,232),(56,232)]),
          path([(192,232),(256,232)]), hlab(192,256,232,'ADMITTED'),
          path([(392,232),(456,232)]), hlab(392,456,232,'READY'),
          path([(592,232),(656,232)]), hlab(592,656,232,'ENDED'),
          path([(792,232),(890,232)]), hlab(792,890,232,'DELETED'),
          path([(524,264),(524,344)],'accent'), vlab(524,264,344,'BREAKER',ACC),
          path([(592,376),(724,376),(724,264)],'accent',dashed=True), hlab(592,724,376,'HOLD ENDS',ACC),
          path([(324,264),(324,448),(760,448),(760,264)],dashed=True), lab(542,456,'never ready · 2 min')]
    b.append(f'<circle cx="900" cy="232" r="8" fill="none" stroke="{INK}" stroke-width="1.2"/><circle cx="900" cy="232" r="5" fill="{INK}"/>')
    b += [node(56,200,136,64,'Requested','claim created',rx=8),
          node(256,200,136,64,'Provisioning','namespace + policy',rx=8),
          node(456,200,136,64,'Running','agent executes','focal',rx=8),
          node(656,200,136,64,'Draining','ttl · done · budget',rx=8),
          node(456,344,136,64,'Frozen','egress cut · logs kept','security',rx=8)]
    b.append(callout(56,496,'Expiry needs no Clearance: past expiresAt the composition renders nothing and Crossplane removes the namespace.'))
    b.append(legend(528,[('focal','Working state'),('security','Held for forensics'),('backend','Transition state'),('accent','Breaker'),('muted-dash','Fail closed')]))
    return dict(slug='run-lifecycle', eyebrow='State machine · 07 of 19 · Run lifecycle',
      title='A run always ends, whether or not anyone is watching',
      desc='State machine of an agent run: requested, provisioning, running, draining and deleted, with a frozen state entered when the session breaker trips that cuts egress but keeps the logs for a hold period, and a fail-closed path that drains a run that never became ready.',
      lede='Every path ends in deletion. The deadline is enforced by the composition, not by the gateway, so a dead or compromised Clearance cannot leave a run alive. A tripped breaker freezes a run for review instead of destroying the evidence.',
      body=''.join(b), W=1000, H=576, y0=170,
      cards=C3(P('Fail closed, and never depend on one component being alive. This mirrors the existing PR-namespace pattern: primary cleanup plus an independent backstop.'),
               UL(['Primary: expiresAt reached, so the function renders nothing and Crossplane garbage-collects.','Backstop: a sweep for agent-run namespaces with no live AgentRun. It must NOT reuse hangar.io/ephemeral-env, or the existing PR sweep will reap live runs.','Freeze holds 15 minutes by default, then drains.']),
               P('Stop Clearance and confirm a run still ends on time. Then kill the function pod mid-run. Time-driven re-invocation via the response TTL is unverified on your Crossplane version, so this is the first thing to test.'), 'Verify first'))

def w_team():
    b=[]
    b += [path([(460,124),(460,162),(300,162),(300,200)]), path([(540,124),(540,162),(700,162),(700,200)]),
          path([(660,264),(660,302),(600,302),(600,340)]),
          path([(740,264),(740,302),(840,302),(840,324)],'accent',dashed=True,marker=False), stopx(840,328)]
    b += [node(400,60,200,64,'Orchestrator','T1 · 60 min · 300 calls','input'),
          node(200,200,200,64,'Researcher','T0 · 20 min · 100 calls'),
          node(600,200,200,64,'Coder','T1 · 30 min · 150 calls','focal'),
          node(500,340,200,64,'Test runner','T0 · 10 min · 40 calls'),
          node(740,340,200,64,'Deployer','asks T2 · 10 min','optional')]
    b.append(text(840,424,'denied: above the parent ceiling',8,400,ACC,'middle',mono=True))
    b.append(callout(24,464,'A child gets at most what its parent has left: ceiling, time, calls and tokens are reserved from the parent.'))
    b.append(legend(496,[('input','Root run'),('focal','Child'),('backend','Grandchild'),('optional','Refused'),('accent-dash','Denied spawn')]))
    return dict(slug='agent-teams', eyebrow='Tree · 08 of 19 · Agent teams',
      title='Agent teams: every child is narrower than its parent',
      desc='Tree of an orchestrator run that spawns a researcher and a coder, where the coder spawns a test runner, each with a lower or equal tier, shorter time and smaller budget than its parent, and a fourth spawn, a deployer asking for tier two, is denied for exceeding the parent ceiling.',
      lede='Delegation is narrowing. A planner can hand work to workers without any of them being able to do more than the planner could. The reservation makes it arithmetic: the children cannot collectively spend more than the root was granted.',
      body=''.join(b), W=1000, H=544, y0=40,
      cards=C3(P('Least privilege and bounded blast radius, applied to delegation. The same narrow-only rule that applies to a claim applies to a child.'),
               UL(['One task_id across the whole tree, so the flight recorder shows a team as one story.','Depth is capped at 3 and children at a per-definition limit, so a runaway spawn loop stops.','Closing a parent closes the tree; tripping a parent freezes it.']),
               P('This is tested as a property: in 200 random sequences of spawn, spend and close, no session ever overspends and no tree ever exceeds what the root was granted. That test is in the repository.'), 'Proved in code'))
