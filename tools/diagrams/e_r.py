"""The Release record set: pictures for the essay "The release record, and the users I haven't met" (2026-10-27),
about Tower's release record."""
from libx import *


def r_lifecycle():
    b = []
    b += [zone(24, 100, 952, 112, 'one release · named when its draft opens'),
          zone(24, 240, 952, 112, 'written down as', center=True),
          zone(24, 380, 952, 96, 'who decides at the release pr · release modes')]
    stages = [('Draft', 'opens as the last ships'), ('Release PR', 'sign-off before merge'),
              ('Rolling out', 'Rollout facts arrive'), ('Sealed', 'healthy in first Flight'),
              ('Baking', '7 days in production'), ('Outcome', 'clean or rolled back')]
    where = [('next.yaml', 'direct commit · app repo', 'store'),
             ('Release PR', 'gitops-<app> · reviewed', 'store'),
             ('Tracking record', 'ConfigMap · swept at 14d', 'external'),
             ('Record PR', 'releases/<app>@<tag>', 'store'),
             ('Nothing saved', 'read live, not stored', 'optional'),
             ('Outcome PR', 'the same record file', 'store')]
    for i, ((n, s), (wn, ws, wk)) in enumerate(zip(stages, where)):
        x = 48 + i * 156
        b.append(node(x, 128, 140, 56, n, s, 'focal'))
        if i < 5:
            b.append(path([(x + 140, 156), (x + 156, 156)], 'accent'))
        b.append(path([(x + 70, 184), (x + 70, 268)], 'muted', dashed=wk != 'store'))
        b.append(node(x, 268, 140, 56, wn, ws, wk))
    modes = [('Hand-flown', "an owner's approving review", 'backend'),
             ('Assisted · the default', 'a person merges, Tower notes who', 'backend'),
             ('Autoland', 'no human · not built yet', 'propose')]
    for i, (n, s, k) in enumerate(modes):
        x = 48 + i * 312
        b.append(node(x, 404, 280, 48, n, s, k))
    b.append(callout(24, 516, 'Git gets every decision. The cluster keeps only what is still moving.'))
    b.append(legend(548, [('focal', 'A stage'), ('store', 'A commit or a PR'), ('external', 'Cluster state, not git'),
                          ('optional', 'Computed, not saved'), ('propose', 'Not built')]))
    return dict(slug='one-release-in-git', eyebrow='Release record · 01 of 03 · The shape',
      title='One release, and where each step is written',
      desc='Top row, the six stages of one release, named when its draft opens: the draft opens as the previous release ships; the release PR carries the sign-off before it merges; the release rolls out while Argo Rollouts sends facts; the record is sealed once the release is healthy in its first Flight environment; it bakes for seven days in production; and it ends with an outcome, clean or rolled back. Middle row, where each step is written down: the draft is next.yaml, a direct commit to the app repo; the release PR is a reviewed PR in the app\'s gitops repo; rollout state is a tracking ConfigMap on the dev cluster, swept after 14 days, not git; the sealed record is a PR adding releases/<app>@<tag> to the gitops repo; baking is read live and not stored; and the outcome is a second PR to the same record file. Bottom row, the release modes that decide what the release PR needs: Hand-flown, an approving review from one of the app\'s owners; Assisted, the default, where a person merges and Tower notes who; and Autoland, no human, not built yet.',
      lede='A release is followed from the moment the one before it ships until anyone can say how it went. Every step a person decides lands in git as a commit or a pull request. Only the part that is still moving lives on a cluster.',
      body=''.join(b), W=1000, H=600, y0=76,
      cards=[('Starts early', '', P('The draft exists before any pull request does, so notes get written while the work merges, not the night before.')),
             ('Sealed in git', 'accent', P('The record is a YAML file in the app\'s gitops repo, added by a pull request. Tower reads it back; it never owns it.')),
             ('Ends late', 'link', P('A release is not done at healthy. The outcome is written into the same file once the bake window says how it went.'))])


def r_six_questions():
    b = []
    b += [zone(24, 100, 304, 452, 'who asks · my guess'), zone(352, 100, 624, 452, 'what the record answers'),
          zone(24, 580, 952, 80, 'one file · releases/flight-api@1.8.0-4f9c2ab.yaml', center=True)]
    rows = [('The release owner', 'writing notes, picking a build',
             'What changed?', 'scope PRs · closed issues · incoming PRs'),
            ('A reviewer', 'asked to sign off',
             'Is it ready?', 'readiness checks · candidates · version'),
            ('An auditor', 'months later',
             'How was it proven?', 'gates · commit proof · check ride · change'),
            ('Whoever merges', 'at the release PR',
             'Who decided?', 'owner · mode · sign-off and who signed'),
            ('The person on call', 'after it ships',
             'How did it go?', 'outcome · rollback and why · bake'),
            ('The next team', 'planning the next one',
             'What did we learn?', 'after release: checks · follow-ups')]
    for i, (who, ws, q, qs) in enumerate(rows):
        y = 124 + i * 68
        b.append(node(48, y, 256, 48, who, ws, 'input'))
        b.append(path([(304, y + 24), (376, y + 24)], 'accent'))
        b.append(node(376, y, 576, 48, q, qs, 'focal' if i in (2, 4) else 'backend'))
    keys = 'release · guardrails · testEvidence · changeRequest · humanContext · outcome'
    b.append(text(500, 624, keys, 11, 400, INK, 'middle', mono=True))
    b.append(text(500, 644, 'the draft, mode and sign-off live under release; the outcome is added once it is final', 9, 400, MUTED, 'middle', mono=True))
    b.append(callout(24, 700, 'Six questions people ask about a release, kept where they can still be answered later.'))
    b.append(legend(732, [('input', 'Who I think asks'), ('backend', 'What the record holds'),
                          ('focal', 'Frozen, so it outlives its source')]))
    return dict(slug='six-questions-one-file', eyebrow='Release record · 02 of 03 · Anatomy',
      title='Six questions, one file',
      desc='Two columns. Left, who I think asks about a release, a guess rather than research: the release owner writing notes and picking a build; a reviewer asked to sign off; an auditor, months later; whoever merges the release PR; the person on call after it ships; and the next team planning the next release. Right, what the record answers for each: what changed (the scope PRs, the issues they close and the incoming PRs); is it ready (the readiness checks, the candidate builds and the version); how was it proven (the release gates, the commit proof, the check ride and the change request), highlighted because it is frozen into the record so it outlives the pipeline runs it came from; who decided (the owner, the release mode, and the sign-off and who signed); how did it go (the outcome, any rollback and why, and the bake), also highlighted; and what did we learn (after-release notes: how it was checked, and follow-ups). All of it is one YAML file in the app\'s gitops repo, for example releases/flight-api@1.8.0-4f9c2ab.yaml.',
      lede='The record is shaped around the questions I expect people to ask about a release. The people on the left are my guess, not research, which is what the third diagram is about.',
      body=''.join(b), W=1000, H=772, y0=76,
      cards=[('Before', '', P('What changed and whether it is ready are answered while the release is still a draft, from data Tower already reads.')),
             ('Frozen', 'accent', P('Pipeline runs get pruned and tracking state is swept. The evidence a release shipped with is copied into the record when it is sealed.')),
             ('After', 'link', P('The outcome and the after-release notes arrive later, as pull requests to the same file, so the story stays in one place.'))])


def r_assumptions():
    b = []
    b += [zone(24, 100, 304, 452, 'what i assumed'), zone(352, 100, 296, 452, 'what i built'),
          zone(672, 100, 304, 452, 'how i would find out')]
    rows = [('Notes are written late', 'so they are thin or skipped',
             'A draft from day one', 'pre-filled from merged PRs',
             'Notes before Promote?', 'and how often the pre-fill is kept'),
            ('Approval after the fact', 'is only an acknowledgement',
             'Sign-off on the PR', 'Hand-flown · a soft gate',
             'Is it a rubber stamp?', 'time from approval to merge'),
            ('People say a name', 'not 1.8.0-4f9c2ab',
             'Tree names: DOGWOOD', 'one per release, never reused',
             'Do the names stick?', 'listen in standups and PRs'),
            ('Evidence goes missing', 'runs pruned, state swept',
             'Frozen at the seal', 'gates · commit proof · tests',
             'Would an audit pass?', 'one dry run with a real auditor'),
            ('Seven days means clean', 'a bake window I picked',
             'Outcome after the bake', 'clean · rolled back · stopped',
             'Does it match incidents?', 'compare with what on-call saw'),
            ('Autoland at 80 and 15%', 'thresholds I made up',
             'Eligibility, display only', 'Autoland itself not built',
             'Do teams trust it?', 'which mode they choose, and keep')]
    for i, (a, asub, w, wsub, t, tsub) in enumerate(rows):
        y = 124 + i * 68
        b.append(node(48, y, 256, 48, a, asub, 'input'))
        b.append(path([(304, y + 24), (376, y + 24)], 'muted'))
        b.append(node(376, y, 248, 48, w, wsub, 'propose' if i == 5 else 'focal'))
        b.append(path([(624, y + 24), (696, y + 24)], 'link', dashed=True))
        b.append(node(696, y, 256, 48, t, tsub, 'optional'))
    b.append(callout(24, 596, 'Every feature here is a hypothesis with one customer: me.'))
    b.append(legend(628, [('input', 'An assumption'), ('focal', 'Built on it'), ('propose', 'Not built'),
                          ('optional', 'Not yet tested'), ('link-dash', 'The test I would run')]))
    return dict(slug='built-on-assumptions', eyebrow='Release record · 03 of 03 · Honest notes',
      title='Built on assumptions, and how I would test them',
      desc='Three columns: what I assumed, what I built on it, and how I would find out if I was right. Notes are written late, so they are thin or skipped: I built a draft that exists from day one, pre-filled from merged PRs; I would check how many releases have notes before Promote, and how often the pre-fill is kept as is. Approval after the fact is only an acknowledgement: I moved sign-off onto the release PR, Hand-flown mode, a soft gate; I would check whether it is a rubber stamp by the time from approval to merge. People say a name, not an image tag like 1.8.0-4f9c2ab: I built tree names such as DOGWOOD, one per release and never reused; I would listen for them in standups and pull requests. Evidence goes missing because pipeline runs are pruned and tracking state is swept: I freeze the gates, the commit proof and the test evidence into the record when it is sealed; I would run one dry-run audit with a real auditor. Seven days means clean, a bake window I picked: the outcome is written after the bake, as clean, rolled back or stopped; I would compare outcomes with what on-call actually saw. Autoland at an average readiness of 80 and under 15% rolled back, thresholds I made up: Tower shows eligibility, display only, and Autoland itself is not built; I would watch which release mode teams choose, and keep. None of these tests has been run.',
      lede='With no users, I wrote the release record for the people I imagine using it. These are the guesses it rests on. Each one is built, and none of them has been tested against anyone but me.',
      body=''.join(b), W=1000, H=668, y0=76,
      cards=[('Assumed', '', P('Each row starts as something I believe about how teams release software, from experience and from reading, not from talking to Hangar\'s users. It has none.')),
             ('Built', 'accent', P('Everything in the middle column is in Tower today, except Autoland itself. Building first was cheap in a lab, and it gives me something real to put in front of people.')),
             ('Untested', 'link', P('The right column is the discovery work a real team would do first. Here it comes last, and I would expect at least one row to be wrong.'))])
