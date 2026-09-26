from lib import *
from d123 import P, UL

def diamond(cx,cy,hw,hh,name,kind='backend'):
    fill,stroke,dash = KINDS[kind]
    pts = f'{cx-hw},{cy} {cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh}'
    return (f'<polygon points="{pts}" fill="{PAPER}"/>'
            f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            + text(cx,cy+4,name,12,600,INK,'middle'))

def d4():
    b=[]
    # arrows first
    b += [path([(340,68),(340,100)]), path([(340,156),(340,188)]), path([(340,244),(340,284)]),
          path([(340,356),(340,400)],'accent'), vlab(340,356,400,'YES',ACC),
          path([(440,320),(560,320)],dashed=True), hlab(440,560,320,'NO'),
          path([(660,296),(660,46),(440,46)],dashed=True), vlab(660,46,296,'RETRY ≤ 3'),
          path([(240,436),(176,436)]), hlab(176,240,436,'T1'),
          path([(440,436),(504,436)]), hlab(440,504,436,'T2'),
          path([(100,464),(100,562),(240,562)]),
          path([(592,464),(592,562),(440,562)])]
    b += [node(240,24,200,44,'Agent opens PR',None,'input',rx=22),
          node(240,100,200,56,'Static gates','schema · policy · tests · sign'),
          node(240,188,200,56,'Ephemeral env','deploy + verify contract'),
          diamond(340,320,100,36,'Gates pass?','focal'),
          node(560,292,200,56,'Structured failure','rule id · file · fix hint','backend'),
          diamond(340,436,100,36,'Risk tier?'),
          node(24,408,152,56,'Auto-merge','T1 · reversible · audited'),
          node(504,408,176,56,'Human approval','T2 · prod-affecting'),
          node(240,540,200,44,'Rollout + auto-rollback',None,'input',rx=22)]
    b.append(callout(720,100,'Fast, deterministic,'))
    b.append(callout(720,124,'and machine-readable.'))
    b.append(legend(616,[('focal','Decision gate'),('backend','Step'),('input','Start · end'),('muted-dash','Retry / fail'),('accent','Pass')]))
    return dict(slug='validation-loop', eyebrow='Flowchart · 04 of 11 · CI/CD validation loop',
      title='CI/CD as a validation loop the agent can retry against',
      desc='Flowchart of an agent-authored pull request passing static and supply-chain gates and an ephemeral environment verify step; a failure returns a structured rule id and fix hint for up to three retries, while a pass routes by risk tier to auto-merge or human approval, then to a progressive rollout with automatic rollback.',
      lede='Every probabilistic step has a deterministic gate behind it. The gates are fast and return structured failures, so the agent can converge without a human, and humans sit on the loop at the risk tiers that need them.',
      body=''.join(b), W=1000, H=656,
      cards=[('Requirement','', P('Turn CI/CD into a validation loop: fast deterministic gates an agent can retry against until it passes, with humans on the loop rather than in it.')),
             ('Design choices','accent', UL(['Failures are structured (rule id, file, line, fix hint), never a log wall.','Retry budget of three, then a page with the evidence attached.','Promotion is tier-aware; provenance is checked at admission, not only in CI.'])),
             ('Evidence and gap','link', P('Built in Hangar: Tekton and Pipelines-as-Code, a releaseGuardrails registry, tier-aware promotion in Glidepath, cosign plus Rekor verification. Real bugs found: a fail-open sast check and an index-lag race. Proposal only: the agent-facing failure schema.'))])

def d5():
    b=[]
    X0, W0, H0, Y0 = 112, 848, 72, 76
    layers = [
      ('L5','Business lines','Mogo lending · Carta payments · Intelligent Investing',['Mogo','Carta','Intelligent Investing'],'backend'),
      ('L4','Golden-path API','one typed abstraction per capability',['Application','PostgreSQL','Queue','Secrets'],'backend'),
      ('L3','Compositions','cloud specifics live here and nowhere else',['AWS','OCI'],'focal'),
      ('L2','GitOps delivery','per-cluster repos · lower/upper AppProject boundary',['ArgoCD','Kyverno','per-cluster repo'],'backend'),
      ('L1','Foundations','accounts · networks · clusters · IAM roots',['Terraform','EKS','OKE'],'store'),
    ]
    for i,(idx,name,sub,chips,kind) in enumerate(layers):
        y = Y0 + i*H0
        fill,stroke,_ = KINDS[kind]
        b.append(f'<rect x="{X0}" y="{y}" width="{W0}" height="{H0}" fill="{PAPER}"/>')
        b.append(f'<rect x="{X0}" y="{y}" width="{W0}" height="{H0}" fill="{fill if kind!="backend" else "#ffffff"}" stroke="{stroke if kind!="backend" else "rgba(27,31,36,0.30)"}" stroke-width="1"/>')
        b.append(text(X0+16,y+28,idx,8,500,MUTED,mono=True,ls='0.14em'))
        b.append(text(X0+56,y+32,name,16,600,INK))
        b.append(text(X0+56,y+52,sub,8,400,MUTED,mono=True))
        # chips right-aligned
        x = X0+W0-16
        for c in reversed(chips):
            cw = up4(len(c)*5.6+20)
            x -= cw
            b.append(f'<rect x="{x}" y="{y+28}" width="{cw}" height="16" rx="3" fill="{PAPER}" stroke="{stroke if kind!="backend" else MUTED}" stroke-opacity="0.6" stroke-width="0.8"/>')
            b.append(text(x+cw/2,y+39,c,8,400,INK,'middle',mono=True))
            x -= 8
    # Terraform / Crossplane boundary
    by = Y0 + 4*H0
    b.append(f'<line x1="{X0}" y1="{by}" x2="{X0+W0}" y2="{by}" stroke="{ACC}" stroke-width="1.2" stroke-dasharray="5,4"/>')
    b.append(lab(X0+W0/2, by-6, 'terraform below · crossplane + argocd above', ACC))
    # direction indicator
    b.append(f'<line x1="64" y1="{Y0+4*H0-16}" x2="64" y2="{Y0+16}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    b.append(text(24,Y0-8,'ABSTRACT',8,500,MUTED,mono=True,ls='0.14em'))
    b.append(text(24,Y0+5*H0+16,'CONCRETE',8,500,MUTED,mono=True,ls='0.14em'))
    b.append(legend(Y0+5*H0+52,[('focal','Where clouds differ'),('backend','Shared across clouds'),('store','Provisioned once'),('accent-dash','Tooling boundary')]))
    return dict(slug='multicloud-gitops', eyebrow='Layer stack · 05 of 11 · Multi-cloud platform',
      title='One platform surface across AWS and OCI',
      desc='Layer stack from foundations at the bottom through GitOps delivery, cloud-specific Crossplane compositions, the golden-path API and business lines at the top, marking Terraform below and Crossplane plus ArgoCD above, with cloud differences confined to the compositions layer.',
      lede='Teams claim a capability once. Only the compositions layer knows whether that is AWS or OCI, so business lines converge on one surface and differ only where regulation or workload genuinely requires it.',
      body=''.join(b), W=1000, H=Y0+5*H0+52+40, y0=40,
      cards=[('Requirement','', P('Multi-cloud Kubernetes, IaC, GitOps. Serve every product line without a separate platform for each one; converge where they drifted for no reason.')),
             ('Design choices','accent', UL(['Terraform for foundations; Crossplane and Argo for everything above the cluster. State the boundary out loud.','PostgreSQL becomes RDS on AWS or OCI Database with the same claim.','Convergence is a queue: inventory drift, score justified vs accidental, converge the accidental.'])),
             ('Evidence and gap','link', P('Built in Hangar: the per-cluster repo decision, two ArgoCD instances per cluster, lower/upper AppProject boundary, generator-driven cluster bootstrap, a PostgreSQL component on CNPG. Honest gap: Hangar ran on kind and Apple container, not AWS or OCI. Say so, then give the 30/60/90.'))])

def d6():
    b=[]
    rings = [
      (24,24,952,392,'L1 · organization','Organization guardrails','SCPs · admission policy · audit retention'),
      (56,72,888,316,'L2 · business line','Business line: lending (Mogo)','own accounts · own policy set · no cross-line reach'),
      (88,120,824,240,'L3 · environment','Environment: lending-dev','namespace RBAC · quota · network segmentation'),
      (120,168,760,164,'L4 · agent session','Agent session','identity TTL 30 min · task-scoped role · token budget'),
    ]
    for i,(x,y,w,h,lbl,cap,ctl) in enumerate(rings):
        so = [0.30,0.45,0.60,0.80][i]
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(27,31,36,{0.015+0.01*i})" stroke="rgba(27,31,36,{so})" stroke-width="1"/>')
        lw = up4(len(lbl)*5.6+16)
        b.append(f'<rect x="{x+12}" y="{y-6}" width="{lw}" height="12" rx="2" fill="{PAPER}"/>')
        b.append(text(x+12+lw/2,y+3,lbl.upper(),8,500,MUTED,'middle',mono=True,ls='0.14em'))
        b.append(text(x+16,y+32,cap,12,600,INK))
        b.append(text(x+w-16,y+32,ctl,8,400,MUTED,'end',mono=True))
    b.append(node(152,216,696,88,'One tool call','one short-lived token · one verb · one resource · one audit row','focal'))
    b.append(callout(24,456,'A compromised agent reaches exactly what its session was scoped to, and nothing in another business line.'))
    b.append(legend(488,[('focal','Unit of authority'),('external','Scope ring (each narrower than the last)')]))
    return dict(slug='identity-blast-radius', eyebrow='Nested · 06 of 11 · Agent identity',
      title='Agents are identities: each ring narrows the blast radius',
      desc='Nested containment from organization guardrails through a business line, an environment and an agent session down to a single tool call, where each ring narrows what an agent identity can reach.',
      lede='Authority only narrows as it moves inward. The unit an agent actually holds is one token, for one verb, on one resource, and that is also the unit that gets audited.',
      body=''.join(b), W=1000, H=536, y0=8,
      cards=[('Requirement','', P('Agents are identities. They need scoped credentials, bounded blast radius, and audit trails that hold up across lending, payments, and securities regulation.')),
             ('Design choices','accent', UL(['Workload identity first (IRSA on EKS, the OCI equivalent); secrets only where federation cannot reach.','Dynamic, short-lived database credentials delivered by External Secrets.','Cross-line reach is denied by policy, not by convention.'])),
             ('Evidence and gap','link', P('Built in Hangar: provider-infisical with declarative, Delete-protected projects adopted in place, ESO delivery, and a standing preference for never-persisted credentials. Honest gap: IRSA and the OCI equivalent were not exercised in Hangar.'))])
