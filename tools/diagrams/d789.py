from lib import *
from d123 import P, UL

def d7():
    b=[]
    x = lambda m: 80+84*m
    # task_id bracket
    b.append(f'<path d="M{x(0)},112 V104 H{x(9.5)} V112" fill="none" stroke="{MUTED}" stroke-width="1"/>')
    b.append(lab((x(0)+x(9.5))/2, 98, 'task_id = t-7f3a · carried by every event', MUTED))
    # axis
    b.append(f'<line x1="64" y1="260" x2="936" y2="260" stroke="{INK}" stroke-width="1"/>')
    for m in range(0,11):
        b.append(f'<line x1="{x(m)}" y1="256" x2="{x(m)}" y2="264" stroke="{MUTED}" stroke-width="1"/>')
        b.append(text(x(m),280,f'{m}m',8,400,SOFT,'middle',mono=True))
    b.append(text(936,248,'MINUTES SINCE TASK START',8,400,SOFT,'end',mono=True,ls='0.06em'))
    ev = [(0,'a','Intent recorded','gateway audit'),
          (0.5,'b','Read logs via MCP','gateway audit'),
          (2,'a','PR opened','git · task_id label'),
          (3.5,'b','Gate fails: rule 4','ci · structured failure'),
          (5,'a','Gates pass','ci · verify contract'),
          (6.5,'b','Merged (T1)','git · policy decision'),
          (7.5,'a','Argo sync','argocd · annotation'),
          (9.5,'b','SLO check ok','slo · burn rate')]
    for m,side,name,src in ev:
        xx = x(m); focal = (name=='SLO check ok')
        col = ACC if focal else MUTED
        if side=='a':
            b.append(f'<line x1="{xx}" y1="176" x2="{xx}" y2="254" stroke="{col}" stroke-width="0.8"/>')
            b.append(text(xx,152,name,12,600,ACC if focal else INK,'middle')); b.append(text(xx,168,src,8,400,MUTED,'middle',mono=True))
        else:
            b.append(f'<line x1="{xx}" y1="266" x2="{xx}" y2="324" stroke="{col}" stroke-width="0.8"/>')
            b.append(text(xx,344,name,12,600,ACC if focal else INK,'middle')); b.append(text(xx,360,src,8,400,MUTED,'middle',mono=True))
        b.append(f'<circle cx="{xx}" cy="260" r="{6 if focal else 4}" fill="{ACC if focal else INK}"/>')
    b.append(legend(408,[('dot','Event'),('dot-accent','Outcome check'),('muted','Same task_id on every record')]))
    return dict(slug='agent-observability', eyebrow='Timeline · 07 of 11 · Observability',
      title='Did the agent do the right thing, and how do we know?',
      desc='Timeline of one agent task over ten minutes, from recorded intent through tool calls, a pull request, a failed and a passing gate, merge, sync, and a final SLO check, with one task_id carried by every record.',
      lede='One task_id is stamped on the intent, the tool calls, the commits, the pipeline runs and the deploy. The last event is not a green build: it is the service confirming the change did what it was meant to.',
      body=''.join(b), W=1000, H=456, y0=88,
      cards=[('Requirement','', P('Observability has to answer a new question. Not just "is the service healthy" but "did the agent do the right thing, and how do we know."')),
             ('Design choices','accent', UL(['task_id propagates through commits, PR labels, gateway audit rows, Argo annotations and traces.','Outcome metrics: first-attempt gate pass rate, retries per task, human override rate, rollback rate against a human baseline.','The closing event is a service-level check, not a pipeline status.'])),
             ('Evidence and gap','link', P('Built in Hangar: release-outcome-span tracing, the Tower Release Record with compare view, and a HolmesGPT triage prototype. Proposal only: task_id as a first-class field across the gateway and Argo.'))])

def d8():
    b=[]
    Y=200; H=72
    xs = {'s0':72,'s1':312,'s2':552,'fz':792}
    W=168
    # start
    b.append(f'<circle cx="36" cy="236" r="6" fill="{INK}"/>')
    b.append(path([(42,236),(72,236)]))
    b.append(lab(38,180,'new class',MUTED))
    # promotions
    b += [path([(240,236),(312,236)]), hlab(240,312,236,'≥95% match'),
          path([(480,236),(552,236)]), hlab(480,552,236,'clean runs'),
          path([(720,236),(792,236)],'accent'), hlab(720,792,236,'violation',ACC)]
    # demotions and recovery
    b += [path([(600,272),(600,316),(420,316),(420,272)],dashed=True), lab(510,324,'rollback · slo burn'),
          path([(348,272),(348,364),(156,364),(156,272)],dashed=True), lab(252,372,'human overrides'),
          path([(876,272),(876,412),(108,412),(108,272)],'accent',dashed=True), lab(492,420,'review + fix, then re-earn',ACC)]
    b += [node(72,Y,W,H,'Shadow','agent proposes, human acts',rx=8),
          node(312,Y,W,H,'Approve to run','human clicks, agent runs',rx=8),
          node(552,Y,W,H,'Auto-run','verify + auto-rollback','focal',rx=8),
          node(792,Y,W,H,'Frozen','circuit breaker tripped','security',rx=8)]
    b.append(callout(72,476,'Irreversible actions, and alert classes with no verifier, never leave Approve to run.'))
    b.append(legend(508,[('focal','Earned level'),('security','Circuit breaker'),('backend','Level'),('muted','Promote'),('muted-dash','Demote'),('accent-dash','Recover')]))
    return dict(slug='autonomy-ladder', eyebrow='State machine · 08 of 11 · Autonomy',
      title='Autonomy is earned per alert class, and revocable',
      desc='State machine with four states: shadow, approve to run, auto-run and frozen. Promotion needs measured evidence at each step, rollbacks and human overrides demote, and a policy violation freezes the class until it is reviewed and re-earned.',
      lede='Each alert class climbs one rung at a time on measured evidence. Any regression steps it back down, and a policy violation trips a breaker that has to be reviewed before it can climb again.',
      body=''.join(b), W=1000, H=556, y0=160,
      cards=[('Requirement','', P('Push autonomous remediation into the paths that page people today: alerts that resolve themselves, and a first responder that is an agent with a hypothesis already tested.')),
             ('Promotion criteria (proposed)','accent', UL(['Shadow to approve: proposals match what the human actually did, at least 95% over a fixed window.','Approve to auto: a run of clean executions with zero rollbacks.','Demotion is automatic; promotion is a reviewed decision.'])),
             ('Evidence and gap','link', P('Built in Hangar: HolmesGPT AI-triage on alerts. Your own burns: an order-api prod wipe and a provider restart that caused real data loss are exactly why this ladder has a breaker and a "never" tier. Proposal only: the promotion tracker.'))])

def d9():
    b=[]
    LX=24; LW=952
    lanes=[('MONITORING',52),('TRIAGE AGENT',140),('GATEWAY / VERIFY',228),('ON-CALL HUMAN',316)]
    LH=88
    for i,(nm,y) in enumerate(lanes):
        b.append(f'<rect x="{LX}" y="{y}" width="{LW}" height="{LH}" fill="{"rgba(27,31,36,0.02)" if i%2==0 else "rgba(27,31,36,0.0)"}" stroke="rgba(27,31,36,0.14)" stroke-width="0.8"/>')
        b.append(text(LX+12,y+LH/2+3,nm,8,500,MUTED,mono=True,ls='0.14em'))
    b += [path([(240,124),(240,156)]),
          path([(316,184),(364,184)]),
          path([(440,212),(440,244)]),
          path([(516,272),(564,272)]), hlab(516,564,272,'match'),
          path([(716,272),(764,272)]),
          path([(840,244),(840,124)],'accent'), vlab(840,124,244,'pass',ACC),
          path([(440,300),(440,360),(564,360)]), hlab(440,564,360,'no match'),
          path([(840,300),(840,360),(716,360)],dashed=True), hlab(716,840,360,'failed')]
    b += [node(164,68,152,56,'Alert fires','SLO burn · page rule','input'),
          node(764,68,152,56,'Auto-close','alert resolved','input'),
          node(164,156,152,56,'Read-only triage','T0 · logs · metrics'),
          node(364,156,152,56,'Test hypothesis','replay in sandbox copy','focal'),
          node(364,244,152,56,'Runbook + policy','tier decides who acts'),
          node(564,244,152,56,'Execute fix','scoped token · audited'),
          node(764,244,152,56,'Verify contract','did the SLO recover?'),
          node(564,332,152,56,'Page a human','hypothesis + evidence','security')]
    b.append(legend(436,[('focal','Hypothesis tested first'),('security','Escalation'),('accent','Success handoff'),('muted-dash','Fail path')]))
    return dict(slug='auto-remediation', eyebrow='Swimlane · 09 of 11 · Remediation',
      title='Alerts that resolve themselves, or page with a tested hypothesis',
      desc='Swimlane across monitoring, a triage agent, the gateway and verifier, and an on-call human: an alert triggers read-only triage and a sandbox-tested hypothesis, a matching runbook executes a scoped fix that is verified and auto-closed, and any miss or failed verification pages a human with the evidence attached.',
      lede='The agent never acts on a hunch. It tests the hypothesis on a copy first, and when it cannot fix the problem the human still starts ahead: the page arrives with the hypothesis and the evidence.',
      body=''.join(b), W=1000, H=488, y0=36,
      cards=[('Requirement','', P('Incidents where the first responder is an agent arriving with a hypothesis already tested, and alerts that resolve themselves.')),
             ('Design choices','accent', UL(['Triage is read-only (T0) and cheap, so it can run on every page.','Fixes run only through pre-approved runbooks and the gateway; a failed verify escalates, it does not retry blindly.','Auto-close requires the verify contract, not the absence of an alert.'])),
             ('Evidence and gap','link', P('Built in Hangar: HolmesGPT triage and Sloth-based SLOs. Proposal only: sandboxed hypothesis replay and runbook execution through the gateway.'))])
