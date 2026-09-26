from lib import *

def P(s): return f'<p>{esc(s)}</p>'
def UL(items): return '<ul>'+''.join(f'<li>{esc(i)}</li>' for i in items)+'</ul>'

def d1():
    b = []
    b.append(zone(568,100,232,308,'ephemeral namespace · per session'))
    b += [path([(144,224),(200,224)]), hlab(144,200,224,'TASK'),
          path([(328,224),(384,224)]), hlab(328,384,224,'CLAIM'),
          path([(512,224),(568,224)]), hlab(512,568,224,'CREATES'),
          path([(512,360),(568,360)],dashed=True), hlab(512,568,360,'DELETES'),
          path([(776,172),(840,172)],'link'), hlab(806,834,172,'MCP',LINK),
          path([(908,204),(908,236)],'link'), vlab(908,204,236,'EVERY CALL')]
    b += [node(24,196,120,56,'Agent request','task · repo · scope','input'),
          node(200,196,128,56,'Agent broker','authz · quota · TTL'),
          node(384,196,128,56,'AgentSession XR','Crossplane claim'),
          node(384,332,128,56,'TTL reaper','deletes namespace','optional'),
          node(592,140,184,64,'Sandbox pod','gVisor · read-only rootfs','focal'),
          node(592,236,184,64,'Session identity','projected SA · 30 min TTL','security'),
          node(592,332,184,56,'Egress policy + quota','default-deny NetworkPolicy','store'),
          node(840,140,136,64,'MCP gateway','only permitted egress'),
          node(840,236,136,56,'Audit log','append-only','store')]
    b.append(callout(568,436,'The agent holds an identity, not a credential.'))
    b.append(legend(472,[('focal','Isolation unit'),('security','Identity'),('store','Policy · log'),('optional','Lifecycle'),('link','Governed call'),('muted','Provisioning')]))
    return dict(slug='agent-substrate', eyebrow='Architecture · 01 of 11 · Agent substrate',
      title='Agent execution substrate: sandboxed, scoped, disposable',
      desc='Architecture showing an agent task becoming a per-session Crossplane claim that provisions an ephemeral namespace with a sandbox pod, a short-lived identity and default-deny egress, whose only route out is the MCP gateway, with a reaper deleting the namespace on TTL expiry.',
      lede='Every agent task gets its own disposable environment. The broker decides scope, the claim creates it, and the only way out of the sandbox is the governed gateway.',
      body=''.join(b), W=1000, H=512, y0=76,
      cards=[('Requirement','', P('Design and run the execution environments agents work in: sandboxed, reproducible, permissioned, disposable.')),
             ('Design choices','accent', UL(['Identity per session, not per agent type: 30 minute TTL, scope derived from the task.','No route out except the gateway; no standing secrets inside the sandbox.','Namespace carries a TTL and finalizer; rebuildable from an image digest plus the task spec.'])),
             ('Evidence and gap','link', P('Built in Hangar: the claim-a-thing, get-a-governed-environment pattern (Crossplane XRs) and the Tower policy of no standing pod exec. Proposal only: gVisor or Kata runtime and per-session identity minting.'))])

def d2():
    b = []
    b += [zone(24,100,192,136,'untrusted'), zone(296,100,376,244,'governed · gateway'), zone(752,100,224,244,'protected')]
    # forbidden routes first
    b += [path([(160,140),(160,72),(864,72),(864,96)],'accent',dashed=True,marker=False), stopx(864,100),
          hlab(160,864,72,'direct to infra · denied',ACC),
          path([(160,204),(160,392),(864,392),(864,348)],'accent',dashed=True,marker=False), stopx(864,344),
          lab(530,400,'direct to secrets · denied',ACC)]
    b += [path([(184,172),(312,172)],'link'), lab(256,154,'MCP call',LINK),
          path([(456,172),(512,172)]), hlab(456,512,172,'AUTHZ?'),
          path([(584,204),(584,264)]), vlab(584,204,264,'ALLOW'),
          path([(384,204),(384,264)]), vlab(384,204,264,'EVERY CALL'),
          path([(656,284),(712,284),(712,172),(784,172)],'link'), vlab(712,172,284,'SCOPED TOKEN',LINK),
          path([(656,308),(784,308)]), hlab(656,784,308,'FETCH')]
    b += [node(40,140,144,64,'Coding agent','Claude Code · Cursor','input'),
          node(312,140,144,64,'Tool gateway','MCP · schema-validated','focal'),
          node(512,140,144,64,'Policy decision','OPA / Cedar'),
          node(312,264,144,56,'Audit log','append-only · WORM','store'),
          node(512,264,144,56,'Credential broker','per-call, short-lived','security'),
          node(784,140,176,64,'Infra APIs','k8s · ArgoCD · Git · cloud'),
          node(784,264,176,56,'Secrets store','never reaches the agent','store')]
    b.append(callout(296,440,'One privileged gate. Everything else is a route to it.'))
    b.append(legend(472,[('focal','Privileged gate'),('security','Credential mint'),('store','Record'),('link','Governed call'),('muted','Internal'),('accent-dash','Denied route')]))
    return dict(slug='tool-gateway', eyebrow='Secure paved road · 02 of 11 · Tool gateway',
      title='MCP tool gateway: the only road to infrastructure',
      desc='Architecture with three trust zones: an untrusted agent sandbox, a governed gateway zone containing policy decision, audit and credential broker, and protected infrastructure and secrets, showing permitted MCP calls through the gateway and two direct routes that are denied at the boundary.',
      lede='Agents never hold infrastructure credentials. The gateway validates the call, asks policy, mints a scoped token for that one call, and records it. Direct routes stop at the boundary.',
      body=''.join(b), W=1000, H=512, y0=40,
      cards=[('Requirement','', P('Stand up and own the MCP and tool-gateway layer so agents reach infrastructure through governed interfaces instead of ad hoc credentials.')),
             ('Risk tiers, enforced here','accent', UL(['T0 read-only: auto-approved.','T1 reversible writes (PRs, dev sync): auto-approved, audited.','T2 prod-affecting: human approval or pre-approved runbook.','T3 (secret reads, IAM, pod exec): never exposed.'])),
             ('Evidence and gap','link', P('Built in Hangar: Tower write-action policy (delegated vs interactive, lower-env only, authz required for prod RBAC) and never-persisted credentials. Proposal only: a general MCP gateway with OPA or Cedar policy.'))])

def d3():
    b = []
    X = {'agent':140,'cat':380,'plat':620,'ver':860}
    top, bot = 84, 508
    for k,x in X.items():
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="rgba(27,31,36,0.22)" stroke-width="1" stroke-dasharray="3,3"/>')
    # alt frame
    fy, fh = 336, 168
    b.append(f'<rect x="100" y="{fy}" width="800" height="{fh}" rx="4" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.22)" stroke-width="1"/>')
    b.append(f'<line x1="108" y1="{fy+84}" x2="892" y2="{fy+84}" stroke="rgba(27,31,36,0.20)" stroke-width="1" stroke-dasharray="4,3"/>')
    b.append(f'<rect x="100" y="{fy}" width="40" height="16" rx="2" fill="{PAPER}" stroke="rgba(27,31,36,0.22)" stroke-width="1"/>')
    b.append(text(120,fy+12,'ALT',8,400,MUTED,'middle',mono=True,ls='0.12em'))
    b.append(text(112,fy+36,'[gate fails · retry ≤ 3]',8,400,MUTED,mono=True))
    b.append(text(112,fy+108,'[all gates pass]',8,400,MUTED,mono=True))
    def msg(x1,x2,y,label,cx,color='link',dashed=False,lc=SOFT):
        return path([(x1,y),(x2,y)],color,dashed) + lab(cx,y-18,label,lc)
    b += [msg(140,380,124,'discover',260),
          msg(380,140,160,'schema + verify contract',260,'muted',True),
          msg(140,620,208,'invoke · typed inputs',260),
          msg(620,140,244,'run id',260,'muted',True),
          msg(140,860,292,'verify(run id)',260),
          msg(860,140,fy+56,'rule id + fix hint',740,'muted',True),
          msg(140,620,fy+76,'re-invoke with fix',260),
          msg(860,140,fy+132,'pass + signed evidence',740,'accent',False,ACC)]
    b.append(node(60,24,160,56,'Coding agent','Claude Code · Cursor','input'))
    b.append(node(300,24,160,56,'Golden-path catalog','typed XRD schemas'))
    b.append(node(540,24,160,56,'Platform API','XRs · ArgoCD'))
    b.append(node(780,24,160,56,'Verifier','deterministic gates','focal'))
    b.append(legend(540,[('link','Call'),('muted-dash','Return'),('accent','Headline success'),('focal','Judge of record')]))
    return dict(slug='golden-path-contract', eyebrow='Sequence · 03 of 11 · Golden path contract',
      title='Golden path as a contract: discover, invoke, verify',
      desc='Sequence diagram of an agent discovering a golden path in the catalog, invoking it with typed inputs on the platform API, then calling the verifier, which either returns a rule id and fix hint for a retry or returns signed evidence of success.',
      lede='The agent never grades its own work. The path ships its own verifier, and a failure comes back as a rule id and a fix hint the agent can act on.',
      body=''.join(b), W=1000, H=580,
      cards=[('Requirement','', P('Golden paths become machine-executable contracts, not wiki pages. An agent has to be able to discover them, invoke them, and verify the result.')),
             ('Design choices','accent', UL(['One catalog feeds Backstage for humans and MCP for agents.','Every path declares preconditions and a verify contract: XR Ready, Argo Healthy, signature checks out, SLO burn under threshold.','Retry budget of three, then a human is paged with the evidence.'])),
             ('Evidence and gap','link', P('Built in Hangar: typed airframe XRDs, the Backstage scaffolder, release verification with cosign and Rekor. Proposal only: an MCP discovery endpoint over the same catalog.'))])
