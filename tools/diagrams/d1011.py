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
      cards=[('Problem','', P('Infrastructure agents need an evaluation that is as rigorous as the gates their changes have to pass.')),
             ('Design choices','accent', UL(['Corpus: past incidents and golden-path tasks, replayable against a fresh sandbox.','Scored on outcome, blast radius, policy violations, retries and cost, all by deterministic verifiers.','Scorecard history makes model and prompt regressions visible per version.'])),
             ('Evidence and gap','link', P('Built in Hangar: the verifier side (gate checks, verify contracts, release records). Proposal only: the replay corpus and harness. This is the design to build first; none of it is built.'))])
