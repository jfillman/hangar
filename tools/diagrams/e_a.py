from libx import *

def e01():
    b=[]
    for (y,h,l) in [(84,96,'agents and people'),(196,112,'interface and policy'),(324,96,'git · durable write path'),(436,112,'cluster · pull-based')]:
        b.append(zone(24,y,928,h,l,right=True))
    b += [path([(152,172),(152,228)],'link'), vlab(152,172,228,'MCP',LINK),
          path([(400,172),(400,228)]), vlab(400,172,228,'UI'),
          path([(240,260),(312,260)]), hlab(240,312,260,'FEDERATES'),
          path([(152,292),(152,356)],'link'), vlab(152,292,356,'PR',LINK),
          path([(400,292),(400,356)]), vlab(400,292,356,'COMMIT'),
          path([(152,412),(152,468)]), vlab(152,412,468,'CHECKS'),
          path([(240,392),(268,392),(268,448),(356,448),(356,468)]),
          path([(436,412),(436,468)]), vlab(436,412,468,'PULLED'),
          path([(488,500),(560,500)]), hlab(488,560,500,'APPLIES'),
          path([(64,260),(44,260),(44,564),(648,564),(648,532)],'accent',dashed=True), lab(346,572,'AGENTRUN CLAIM · DEV ONLY',ACC)]
    b += [node(64,116,176,56,'Agent workload','any framework · any model','input'),
          node(312,116,176,56,'Engineer','works in Tower','input'),
          node(64,228,176,64,'Clearance','MCP · CEL policy · audit','focal'),
          node(312,228,176,64,'Tower (Backstage)','portal · MCP actions'),
          node(64,356,176,56,'App + gitops repos','PRs · platform/envs'),
          node(312,356,176,56,'Tenants repo','xr-requests/'),
          node(64,468,176,64,'Glidepath','Tekton · PaC · broker'),
          node(312,468,176,64,'ArgoCD ×2','platform · apps'),
          node(560,468,176,64,'Airframe','XRDs · compositions')]
    b.append(callout(24,612,'Durable changes are commits. Ephemeral runs are claims that Crossplane renders.'))
    b.append(legend(644,[('focal','New: Clearance'),('backend','Exists today'),('input','Actor'),('link','Governed call'),('muted','Existing flow')]))
    return dict(slug='hangar-plus-autopilot', eyebrow='Architecture · 01 of 11 · Hangar today',
      title='Hangar as it is, and the one new component beside it',
      desc='Architecture in four planes: agents and people, interface and policy, git as the only write path, and the pull-based cluster, showing the existing Tower, repos, Glidepath, ArgoCD and Airframe, with a single new component, Clearance, added beside Tower.',
      lede='Nothing here replaces a Hangar component. Clearance sits next to Tower and federates its MCP actions. Durable writes are git commits the cluster pulls, like any human commit. Ephemeral agent runs are claims to Crossplane, dev clusters only.',
      body=''.join(b), W=1000, H=692, y0=64,
      cards=C3(P('Durable mutations are git commits (service-catalog-design.md §0). Ephemeral runs are claims to Crossplane, an already-privileged and audited control plane. Each cluster pulls, and holds no other cluster\'s credentials.'),
               UL(['One new service: Clearance (Python), an InfraService like skyport-broker, with a model proxy beside it.','It federates the Backstage MCP actions already in app-config.yaml instead of re-implementing catalog and scaffolder tools.','Airframe gains one XRD, AgentRun, and one Python composition function. Nothing else changes.']),
               P('Checked in the repos today: Tower, the tenants repos, the two ArgoCD instances and Airframe v0.3.90 all exist as drawn. Whether the Backstage mcpActions endpoint is live on a cluster is not verified; check that first.'), 'What is real'))

def e02():
    b=[]
    b += [zone(24,100,184,136,'untrusted'), zone(248,100,296,260,'privileged'), zone(568,100,416,344,'delivery')]
    b += [path([(112,140),(112,72),(928,72),(928,96)],'accent',dashed=True,marker=False), stopx(928,100),
          hlab(112,928,72,'direct sync of an upper env · denied',ACC),
          path([(112,204),(112,484),(928,484),(928,448)],'accent',dashed=True,marker=False), stopx(928,444),
          lab(520,492,'kubectl or apiserver write · denied',ACC)]
    b += [path([(184,172),(272,172)],'link'), lab(228,154,'MCP',LINK),
          path([(504,172),(632,172)],'link',dashed=True), lab(600,154,'SYNC',LINK),
          path([(504,196),(548,196),(548,284),(632,284)],'link'), hlab(548,632,284,'PR',LINK),
          path([(388,204),(388,268)]), vlab(388,204,268,'MINT'),
          path([(732,204),(732,252)]), vlab(732,204,252,'PULL'),
          path([(732,364),(732,316)]), vlab(732,316,364,'PULL AFTER HUMAN MERGE')]
    b += [node(40,140,144,64,'Agent','any framework','input'),
          node(272,140,232,64,'Clearance','MCP · CEL · audit','focal'),
          node(272,268,232,64,'token-review-interceptor','app key stays here','security'),
          node(632,140,200,64,'ArgoCD · lower','AppProject *-lower'),
          node(632,252,200,64,'GitHub repos','branch protection + checks'),
          node(632,364,200,64,'ArgoCD · upper','human merge only')]
    b.append(callout(248,536,'Agents can propose to upper environments. Only a human merge lets ArgoCD pull the change.'))
    b.append(legend(568,[('focal','Privileged gate'),('security','Credential mint'),('link','Governed call'),('link-dash','Delegated, lower only'),('accent-dash','Denied route')]))
    return dict(slug='write-path-spine', eyebrow='Secure paved road · 02 of 11 · The write path',
      title='The durable path: an agent\'s write is a git write',
      desc='Architecture with three trust zones showing that an agent reaches Clearance over MCP, Clearance mints a repo-scoped token through the token-review-interceptor, opens pull requests on GitHub behind branch protection, and may only sync lower environments in ArgoCD, while direct upper-environment sync and direct cluster writes are denied at the boundary.',
      lede='This is the spine for anything that outlives a run. Agents hold no cluster credential. They propose changes as pull requests, ArgoCD pulls what has been merged, and the one imperative action, syncing a lower environment, is delegated to ArgoCD under its own narrow account. Ephemeral runs are the other plane.',
      body=''.join(b), W=1000, H=612, y0=40,
      cards=C3(P('Delegated over interactive: call an API that already holds write authority and already audits itself (Tower write-action policy). No pod exec, ever; lower-only for any write RBAC; authz required before prod.'),
               UL(['New ArgoCD account role:clearance-lower, sync on *-lower/* projects only (Tower\'s role:tower-sync today is */*).','Clearance never holds the GitHub App key; the interceptor does, as it already does for Backstage.','A separate GitHub App for agents, so agent traffic cannot starve CI release PRs of API budget.']),
               P('Prove the two denials, not just the happy path: with the agent\'s token, an upper-project sync must return 403, and a kubectl write must be refused by the apiserver. A passing happy path can mean a gate is off.')))

def e03():
    b=[]
    X = {'ag':110,'cl':310,'tw':510,'ic':710,'gh':890}
    top, bot = 84, 572
    for x in X.values():
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" stroke="rgba(27,31,36,0.22)" stroke-width="1" stroke-dasharray="3,3"/>')
    fy, fh = 288, 272
    b.append(f'<rect x="70" y="{fy}" width="860" height="{fh}" rx="4" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.22)" stroke-width="1"/>')
    div = fy+84
    b.append(f'<line x1="78" y1="{div}" x2="922" y2="{div}" stroke="rgba(27,31,36,0.20)" stroke-width="1" stroke-dasharray="4,3"/>')
    b.append(f'<rect x="70" y="{fy}" width="40" height="16" rx="2" fill="{PAPER}" stroke="rgba(27,31,36,0.22)" stroke-width="1"/>')
    b.append(text(90,fy+12,'ALT',8,400,MUTED,'middle',mono=True,ls='0.12em'))
    b.append(text(82,fy+36,'[policy denies]',8,400,MUTED,mono=True))
    b.append(text(82,div+20,'[policy allows]',8,400,MUTED,mono=True))
    def msg(x1,x2,y,label,cx,color='link',dashed=False,lc=SOFT):
        return path([(x1,y),(x2,y)],color,dashed) + lab(cx,y-18,label,lc)
    b += [msg(110,310,124,'session.open · oauth token',210),
          msg(310,510,156,'introspect token',410),
          msg(510,310,188,'user + groups',410,'muted',True),
          msg(110,310,220,'call: pr.open(repo, branch)',210)]
    # self message
    b.append(f'<path d="M310,248 H336 Q344,248 344,256 V264 Q344,272 336,272 H318" fill="none" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    b.append(text(356,264,'CEL: profile, user rights, tier ceiling',8,400,MUTED,mono=True,ls='0.04em'))
    b += [msg(310,110,fy+56,'denied · rule id',210,'muted',True),
          msg(310,710,div+48,'mint(repo, perms) · sa token',410),
          msg(710,310,div+80,'repo-scoped token',610,'muted',True),
          msg(310,890,div+112,'signed commit · open pr',410),
          msg(890,310,div+144,'pr + checks queued',800,'muted',True),
          msg(310,110,div+176,'pr url + audit id',210,'accent',False,ACC)]
    b.append(node(30,24,160,56,'Agent','delegated by a human','input'))
    b.append(node(230,24,160,56,'Clearance','session · policy · audit','focal'))
    b.append(node(430,24,160,56,'Tower auth','Backstage OAuth'))
    b.append(node(630,24,160,56,'Interceptor','TokenReview + app key','security'))
    b.append(node(810,24,160,56,'GitHub','App installation','external'))
    b.append(legend(600,[('link','Call'),('muted-dash','Return'),('accent','Headline success'),('focal','Policy gate'),('security','Credential mint')]))
    return dict(slug='identity-and-token', eyebrow='Sequence · 03 of 11 · Identity and credentials',
      title='One call, end to end: identity in, scoped token out, nothing kept',
      desc='Sequence diagram of a delegated agent opening a session, Clearance validating the human through Tower auth, evaluating a CEL policy, then either denying with a rule id or asking the token-review-interceptor for a repo-scoped GitHub token, making a signed commit and pull request, and returning the pull request URL with an audit id.',
      lede='The agent never sees a GitHub token. Clearance derives who is acting from Tower\'s login, decides in CEL, and gets a token scoped to one repository for that one call. The audit id in the reply is the record the rest of the platform correlates on.',
      body=''.join(b), W=1000, H=640,
      cards=C3(P('Never-persisted credentials: mint per call, not cache and refresh. Isolation comes from the TokenReview answer, never from a claim in the request body.'),
               UL(['New interceptor route beside /github-installation-token: it checks the caller is Clearance and the repo is in the session\'s profile.','Workload agents (Holmes, Checkride) authenticate with a projected service-account token, audience clearance.','Open decision: commits must satisfy the provenance gate. Sign with the self-hosted Fulcio (workload trust root) and extend the gate, or exempt agent PRs. Prefer the first.']),
               P('Add a test that forges a session id in the request body and confirms the decision still comes from the TokenReview namespace, as ADR-0002 does for CDEvents.')))

def e04():
    b=[]
    b += [zone(24,84,952,152,'kiac-dev · type: dev · arm64'), zone(24,256,952,144,'github.com'), zone(24,420,952,144,'kind-prod · type: upper · amd64')]
    b += [path([(252,180),(276,180)]),
          path([(144,216),(144,272),(364,272),(364,292)],'link'), lab(250,254,'HTTPS · PR',LINK),
          path([(382,216),(382,292)],'link'),
          path([(618,216),(618,292)],'link'), vlab(618,216,292,'HTTPS · CHECKS',LINK),
          path([(854,216),(854,338),(648,338)],'link'), hlab(648,854,338,'PULL',LINK),
          path([(500,456),(500,384)],'link'), vlab(500,384,456,'PULL AFTER HUMAN MERGE',LINK)]
    b += [depnode(40,124,212,92,'POD','clearance',[('MCP + policy + audit','planned',True)],'focal'),
          depnode(276,124,212,92,'POD','token-review-interceptor',[('/agent-token route','planned',True)]),
          depnode(512,124,212,92,'POD','glidepath',[('agent-scope gate','planned',True),('release guardrails','existing',False)]),
          depnode(748,124,212,92,'POD','argocd · crossplane',[('airframe','v0.3.90',False)]),
          depnode(352,292,296,92,'MANAGED','GitHub App + repos',[('branch protection','existing',False),('required checks','existing',False)]),
          depnode(352,456,296,92,'POD','argocd-apps',[('airframe','v0.3.90',False),('agent write path','none',False)])]
    b.append(text(676,494,'No Clearance on upper clusters:',12,600,INK))
    b.append(text(676,510,'agents reach them only as a PR that a human merges.',8,400,MUTED,mono=True))
    b.append(legend(590,[('focal','New service'),('backend','Exists today'),('link','Crosses a boundary'),('muted','Inside a cluster')]))
    return dict(slug='fleet-placement', eyebrow='Deployment · 04 of 11 · Fleet placement',
      title='Where it runs: dev gets the write path, upper gets none',
      desc='Deployment diagram with three zones: the dev cluster hosting the planned clearance service, the extended token-review-interceptor, Glidepath with a planned agent-scope gate and ArgoCD with Crossplane; GitHub with branch protection and required checks; and the upper cluster with ArgoCD only and no agent write path.',
      lede='This follows the cluster registry\'s dev and upper types. Bootstrap-tier mutations are already dev-only; the agent write path is the same shape, so a production cluster holds no agent credential at all.',
      body=''.join(b), W=1000, H=620, y0=64,
      cards=C3(P('Cluster-agnostic and generator-driven (ADR-0006). A cluster gets the feature by a toggle in cluster.yaml, and customize-cluster.sh refuses the invalid combination.'),
               UL(['apron/cluster.yaml: new components.autopilot, refused on type: upper like providerGithub and platformCicd.','New group apron/55-autopilot/ (after 50-platform-cicd, before 60-backstage).','Registry ConfigMap gains autopilotReady, set only after the network-policy canary passes.']),
               P('kiac-dev\'s CNI does not enforce NetworkPolicy; kind-prod\'s Calico does. Do not set autopilotReady on a claim. Run a canary pod that must fail to reach a blocked service, and gate the flag on that result.')))
