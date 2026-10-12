"""The Break-glass set: pictures for the essay "Breaking the glass" (2026-10-12), about Tower's break-glass pod terminal."""
from libx import *


def rule(x, y, w, s, color=INK):
    """One short rule line inside a policy column: a small dot and mono text."""
    cont = s.startswith('+')
    s = s.lstrip('+')
    assert len(s) * 5.4 <= w - 18, f'rule too wide: {s} ({len(s) * 5.4:.0f} > {w - 18})'
    dot = '' if cont else f'<circle cx="{x + 7}" cy="{y - 3}" r="2" fill="{ACC}"/>'
    return dot + text(x + 14, y, s, 9, 400, color, mono=True)


def b_exec_vs_debug():
    b = []
    b += [zone(24, 100, 464, 468, 'kubectl exec'), zone(512, 100, 464, 468, 'a break-glass debug container')]
    # Left: exec
    b += [node(48, 128, 416, 56, 'kubectl exec -it pod -- sh', 'a person with cluster rights', 'input'),
          path([(256, 184), (256, 224)]),
          node(48, 224, 416, 56, 'CONNECT pods/exec', 'all admission can see: allow or deny'),
          path([(256, 280), (256, 320)]),
          node(48, 320, 416, 56, 'Inside the app container', "the app's user · its tools · its secrets", 'external')]
    lefts = ['Writes land in the running app', 'A distroless image has no shell', 'Nothing left behind in the pod']
    b.append(path([(72, 376), (72, 532)], marker=False))
    for i, s in enumerate(lefts):
        y = 400 + i * 48
        b += [path([(72, y + 16), (96, y + 16)], marker=False), node(96, y, 368, 32, s, None, 'optional')]
    # Right: debug container
    b += [node(536, 128, 416, 56, 'Debug, in Tower', 'an owner, signed in, with a reason', 'input'),
          path([(744, 184), (744, 224)], 'accent'),
          node(536, 224, 416, 56, 'UPDATE pods/ephemeralcontainers', 'admission reads the whole container spec', 'focal'),
          path([(744, 280), (744, 320)], 'accent'),
          node(536, 320, 416, 56, 'A hardened debug container', 'uid 65532 · read-only · no capabilities', 'focal')]
    rights = ['One pinned, signed image, any app', 'Reads only what you opted into', 'Stays in the pod spec: restart']
    b.append(path([(560, 376), (560, 532)], marker=False))
    for i, s in enumerate(rights):
        y = 400 + i * 48
        b += [path([(560, y + 16), (584, y + 16)], marker=False), node(584, y, 368, 32, s, None, 'backend')]
    b.append(callout(24, 608, 'Exec is a door you can only lock or unlock. A debug container is a request the cluster can read.'))
    b.append(legend(640, [('input', 'Who asks'), ('external', 'The app, as it runs'), ('optional', 'What exec means'),
                          ('focal', 'What the cluster checks'), ('backend', 'What you get instead')]))
    return dict(slug='exec-or-a-debug-container', eyebrow='Break-glass · 01 of 07 · The idea',
      title='Exec, or a debug container?',
      desc='Two columns. Left, kubectl exec: a person with cluster rights runs kubectl exec into a pod. The API server sees one request, CONNECT pods/exec, and admission can only allow or deny it. The shell runs inside the app container, as the app\'s user, with its tools and its secrets. That means writes land in the running app, a distroless image has no shell at all, and nothing is left behind in the pod. Right, a break-glass debug container: an owner, signed in to Tower, presses Debug with a reason. The API server sees UPDATE pods/ephemeralcontainers, and admission reads the whole container spec. What runs is a hardened debug container as user 65532, read-only, with no capabilities. That means one pinned, signed image works for any app, you read only what you opted into, and the container stays in the pod spec, so the pod is restarted at the end.',
      lede='Both give you a shell next to the app. Only one of them hands the cluster something it can inspect before saying yes.',
      body=''.join(b), W=1000, H=668, y0=76,
      cards=[('All or nothing', '', P('Exec is a single verb on a single subresource. A policy can refuse it or allow it, and nothing in between.')),
             ('Inspectable', 'accent', P('An ephemeral container arrives as a full spec: image, user, capabilities, mounts. Every field is something a policy can check.')),
             ('Not safe by nature', 'link', P('Run as the app\'s user with its process namespace shared, a debug container reaches the same secrets as exec. That is why process access is a separate, recorded opt-in.'))])


def b_how_it_works():
    b = []
    b += [zone(24, 100, 200, 300, 'your browser'), zone(248, 100, 280, 300, 'backstage · tower backend'),
          zone(552, 100, 424, 300, 'the app namespace · prod cluster'),
          zone(24, 440, 952, 96, 'evidence · kept off the cluster it records', right=True)]
    b.append(node(40, 196, 168, 56, 'Tower, in the browser', 'no Kubernetes credential', 'input'))
    b += [node(264, 124, 248, 56, 'Break-glass routes', 'permission · tier · target'),
          node(264, 196, 248, 56, 'Terminal relay', 'WebSocket to attach · records'),
          node(264, 268, 140, 56, 'Sweep and timers', 'ends, cleans up, revokes'),
          text(388, 380, 'no debug rights at rest', 9, 400, MUTED, 'middle', mono=True)]
    b += [path([(208, 224), (264, 224)], 'accent'), path([(236, 224), (236, 152), (264, 152)], 'accent', marker=True)]
    b += [node(568, 124, 392, 44, 'Admission policies', 'in the API server · fail closed · every write', 'security')]
    b += [node(568, 196, 184, 56, 'RoleBinding', 'to itself · TTL 15-75m', 'security'),
          node(776, 196, 184, 56, 'The app pod', 'serving, as before'),
          node(776, 268, 184, 56, 'Debug container', 'uid 65532 · read-only', 'focal'),
          path([(868, 252), (868, 268)], marker=False)]
    b += [path([(512, 152), (540, 152), (540, 224), (568, 224)], 'accent'), lab(660, 180, '1 GRANT ITSELF', ACC),
          path([(512, 236), (528, 236), (528, 296), (776, 296)], 'accent'), lab(660, 304, '2 ADD AND ATTACH', ACC)]
    b += [node(48, 464, 280, 56, 'Audit log', 'every request, decision and play', 'store'),
          node(360, 464, 280, 56, 'Recording store', 'asciicast · object lock · 365 days', 'store'),
          node(672, 464, 280, 56, 'Transparency log', "Rekor · the recording's SHA-256", 'store'),
          path([(640, 492), (672, 492)], 'open')]
    b += [path([(476, 252), (476, 464)], 'open'), vlab(476, 404, 440, 'EVERY BYTE'),
          path([(300, 324), (300, 464)], 'open'), vlab(300, 404, 440, 'EVERY STEP', side='l')]
    b.append(callout(24, 576, 'The person never holds a credential. The portal holds one for minutes, and the cluster checks it.'))
    b.append(legend(608, [('input', 'You'), ('backend', 'Backstage'), ('security', 'A fence or a grant'),
                          ('focal', 'The session'), ('store', 'Evidence'), ('accent', 'Writes'), ('open', 'Records')]))
    return dict(slug='how-a-session-works', eyebrow='Break-glass · 02 of 07 · The shape',
      title='How a session works',
      desc='Four zones. Your browser runs Tower and holds no Kubernetes credential; it talks only to Backstage. In Backstage, Tower\'s backend has three parts: the break-glass routes, which check permission, decide the tier and check the target; the terminal relay, a WebSocket to the debug container\'s attach stream that records everything; and the sweep and timers, which enforce the hard stop, the idle limit and the disconnect limit. The backend holds no debug rights at rest. In the app namespace on the prod cluster, every write passes admission policies that run in the API server and fail closed. Step 1: Backstage grants itself a RoleBinding to a debug role in that namespace, with a time-to-live label of 15 to 75 minutes. Step 2: it adds a debug container, user 65532 and read-only, to the app pod, which keeps serving, and attaches to it. The sweep and timers end the session, clean up, restart the pod and revoke the grant. Evidence is kept off the cluster it records: every byte goes to a recording store with object lock for 365 days, its SHA-256 is anchored in a Rekor transparency log, and every step goes to the audit log.',
      lede='Tower never hands out access. Its backend borrows a narrow role for itself, in one namespace, for one session, and gives it back when the session ends.',
      body=''.join(b), W=1000, H=636, y0=76,
      cards=[('No credential to leak', '', P('The browser only ever talks to Backstage. There is no kubeconfig to copy, no token to paste into a laptop, nothing to revoke afterwards.')),
             ('Borrowed, briefly', 'accent', P('Backstage can create RoleBindings to two debug roles and nothing else. Each session binds one, in one namespace, and deletes it at the end.')),
             ('Evidence elsewhere', 'link', P('Recordings land in a locked bucket on the dev cluster, not on the prod cluster they record, and the hash goes into a transparency log.'))])


def b_two_people():
    b = []
    lanes = [('requester · an owner', 100), ('tower backend', 196), ('approver · another owner or an admin', 292),
             ('prod cluster', 388)]
    for name, y in lanes:
        b.append(zone(24, y, 952, 80, name))
    W_ = 156
    b += [node(48, 116, W_, 48, 'Request', 'mode · options · reason', 'input'),
          node(220, 212, W_, 48, 'Checks and stores', 'tier from cicd.yaml'),
          node(392, 308, W_, 48, 'Reviews and decides', 'image · sensitive · why', 'focal'),
          node(564, 116, W_, 48, 'Start', 'within 10 minutes', 'input'),
          node(736, 212, W_, 48, 'Opens the session', 'grant, container, recording'),
          node(736, 404, W_, 48, 'RoleBinding admitted', 'approver is not you', 'security')]
    b += [path([(204, 140), (298, 140), (298, 212)]), lab(298, 172, 'NOTIFY'),
          path([(376, 236), (470, 236), (470, 308)]),
          path([(548, 332), (642, 332), (642, 164)], 'accent'), lab(642, 236, 'APPROVED', ACC),
          path([(720, 140), (814, 140), (814, 212)], 'accent'),
          path([(814, 260), (814, 404)], 'accent')]
    b += [text(48, 434, 'nothing reaches the cluster before Start', 13, 400, MUTED, serif=True, italic=True)]
    b += [lab(298, 270, 'EXPIRES IN 30 MIN'), lab(642, 180, '10 MIN TO START', ACC)]
    b.append(lab(814, 340, 'RUNS 15-60 MIN · +15 ONCE', ACC))
    b.append(callout(24, 508, 'The second person sees exactly what you asked for, and the cluster checks that they exist.'))
    b.append(legend(540, [('input', 'Requester'), ('backend', 'Tower backend'), ('focal', 'Decision, and the clock'),
                          ('security', 'Cluster check'), ('accent', 'After approval')]))
    return dict(slug='two-people-on-flight', eyebrow='Break-glass · 03 of 07 · Flight',
      title='Two people on Flight',
      desc='Four lanes, read left to right. The requester, an owner of the app, sends a request with the mode, the options and a reason. Tower\'s backend checks it, reads the tier from the app\'s cicd.yaml rather than the request, stores it, and notifies the approvers; the request expires in 30 minutes. The approver, another owner or an admin, reviews it, seeing the pod\'s image, whether the session is sensitive and why it is needed, and decides. Once approved, the requester has 10 minutes to press Start. Only then does the backend open the session: the grant, the debug container and the recording. On the prod cluster, the RoleBinding is admitted only if its approver is not the requester. Nothing reaches the cluster before Start. The session then runs 15 to 60 minutes, plus one 15-minute extension.',
      lede='On staging and production, someone else says yes first. The approval is a record, not a click: it names the person, and the cluster refuses a grant that names nobody, or names you.',
      body=''.join(b), W=1000, H=568, y0=76,
      cards=[('Judged like a change', '', P('The approver sees the mode, process and volume access, the duration, the reason, the incident link and the image the pod runs. A vague reason is easy to deny.')),
             ('Nothing early', 'accent', P('An approved request touches nothing until the requester presses Start. The session\'s clock starts then, so approval is not a standing pass.')),
             ('Glass broken', 'link', P('With nobody to approve, an admin can start at once. Everyone is told first, the grant is marked, and someone else must review the recording afterwards.'))])


def b_layers():
    b = []
    rows = [
        ('1 · Tower', 'your browser', 'backend', 'Shows only what you may do, and why the rest is greyed out',
         'a convenience, never trusted: every route checks again'),
        ('2 · Permissions', 'backstage permission framework', 'backend', 'Owners request, owners and admins approve, admins break glass',
         'anyone else gets a 403'),
        ('3 · Backend rules', 'tower backend', 'backend', 'The tier comes from cicd.yaml and the cluster, never the request',
         'no self-approval · one open session each · namespace labels must name the app'),
        ('4 · Just-in-time RBAC', 'kubernetes rbac', 'security', 'No debug rights at rest: one RoleBinding to itself, per session',
         'may bind two debug roles only; the escalation check refuses anything else'),
        ('5 · Admission', 'api server · fails closed', 'security', 'Grant shape, image digest and signature, securityContext, no exec',
         'a buggy or compromised backend still cannot widen what a session can do'),
        ('6 · Expiry', 'timers, and the cluster', 'security', 'Hard stop, 10 minutes idle, 2 minutes disconnected, a TTL label',
         "Kyverno's cleanup deletes the grant even if Backstage never comes back"),
        ('7 · Record and review', 'audit · object lock · rekor', 'store', 'Every byte recorded, hashed, locked for a year, anchored',
         'no recording, no session · a broken glass is always reviewed'),
    ]
    b.append(path([(36, 112), (36, 540)], 'accent'))
    b.append(vlab(36, 300, 340, 'A REQUEST', ACC))
    for i, (name, where, kind, what, stops) in enumerate(rows):
        y = 112 + i * 62
        b += [node(64 + 52, y, 248, 48, name, where, kind),
              path([(364, y + 24), (388, y + 24)], 'muted'),
              node(388, y, 588, 48, what, stops, 'backend' if kind != 'store' else 'store')]
    b.append(callout(24, 584, 'No layer trusts the one above it.'))
    b.append(legend(616, [('backend', 'Enforced by Backstage'), ('security', 'Enforced by the cluster'),
                          ('store', 'Evidence afterwards'), ('accent', 'Passes every layer')]))
    return dict(slug='seven-layers', eyebrow='Break-glass · 04 of 07 · Guardrails',
      title='Seven layers, each assuming the last one failed',
      desc='A request passes seven layers from top to bottom. 1, Tower in your browser shows only what you may do; it is a convenience and never trusted, because every route checks again. 2, Backstage\'s permission framework: owners request, owners and admins approve, only admins break glass; anyone else gets a 403. 3, the backend\'s rules: the tier comes from cicd.yaml and the cluster, never the request; nobody approves their own; one open session per person; the namespace\'s labels must name the app. 4, just-in-time RBAC: Backstage has no debug rights at rest and binds one debug role to itself per session; it may bind only two roles, and Kubernetes\' escalation check refuses anything else. 5, admission policies in the API server, failing closed: the grant\'s shape, the image digest and signature, the security context, and no exec; a buggy or compromised backend still cannot widen what a session can do. 6, expiry: a hard stop, 10 minutes idle, 2 minutes disconnected, and a TTL label, so Kyverno\'s cleanup deletes the grant even if Backstage never comes back. 7, record and review: every byte recorded, hashed, locked for a year and anchored in a transparency log; no recording means no session, and a glass-broken session is always reviewed.',
      lede='Layers 1 to 3 are the portal being careful. Layers 4 to 6 are the cluster refusing to take the portal\'s word for it. Layer 7 is what makes the rest provable afterwards.',
      body=''.join(b), W=1000, H=644, y0=76,
      cards=[('The portal', '', P('Permissions and backend rules stop the honest mistakes and the crafted requests: the wrong app, the wrong tier, your own approval.')),
             ('The cluster', 'accent', P('RBAC and admission policies are the second lock, in the API server itself. They are there for the day the portal has a bug, or worse.')),
             ('The record', 'link', P('A shell nobody watched live is still a shell everybody can replay. That is the trade that makes the rest acceptable.'))])


def b_policies():
    b = []
    b.append(zone(24, 100, 952, 80, 'what backstage asks the api server to do'))
    b.append(f'<rect x="24" y="212" width="952" height="312" rx="8" fill="rgba(27,31,36,0.02)" stroke="rgba(27,31,36,0.16)" stroke-width="0.8"/>')
    b.append(text(36, 512, 'TOWER-BREAKGLASS-* · EVERY ONE FAILS CLOSED', 8, 400, MUTED, mono=True, ls='0.14em'))
    asks = [(36, 148, 'CREATE RoleBinding', 'the grant', 'input'),
            (192, 304, 'Add a debug container', 'ephemeral, or a copy pod', 'input'),
            (504, 148, 'DELETE a pod', 'cleanup', 'input'),
            (660, 148, 'PATCH a pod', 'process access', 'input'),
            (816, 148, 'exec or attach', 'anyone, on Flight', 'external')]
    for x, w, n, s, k in asks:
        b.append(node(x, 120, w, 44, n, s, k))
    cols = [
        ('rolebinding', ['name tower-breakglass-*', 'role: debug-live, -copy', 'subject: Backstage', 'TTL label 15m to 75m',
                         'app namespace only', 'Flight: approver is not', '+the requester, or glass', '+broken, never neither']),
        ('debug-container', ['image: pinned digest', 'runAsNonRoot, gid not 0', 'read-only root', 'no privilege escalation',
                             'capabilities: drop ALL', 'every mount read-only', 'process access only for', '+the session named on it']),
        ('debug-image', ['cosign keyless signed', "from tower's workflow", 'on main, public Rekor', 'Kyverno, as a webhook',
                         'scoped to break-glass', 'fails closed too']),
        ('pod-delete', ['deletes copy pods, or', '+pods with a debug-*', '+container, only', 'nothing else in the', '+namespace']),
        ('pod-annotate', ['spec unchanged', 'labels unchanged', 'one annotation may', '+change: process-access', '+with the session id']),
        ('no-exec', ['no exec into app pods', 'attach: debug-* only', 'operators excepted', 'Flight only']),
    ]
    for i, (name, rules) in enumerate(cols):
        x = 36 + i * 156
        b.append(path([(x + 74, 164), (x + 74, 236)], 'accent' if i < 5 else 'muted'))
        b.append(node(x, 236, 148, 40, name, None, 'security'))
        for j, r in enumerate(rules):
            b.append(rule(x, 304 + j * 26, 148, r))
    b += [node(36, 548, 460, 48, 'Ground: Kyverno ValidatingPolicy', 'compiled to native admission policy · no webhook', 'backend'),
          node(516, 548, 448, 48, 'Flight: hand-written ValidatingAdmissionPolicy', 'Argo CD · synced before the backend that needs it', 'backend')]
    b.append(callout(24, 636, 'Every rule is scoped to break-glass objects, so a policy bug can only ever break break-glass.'))
    b.append(legend(668, [('input', 'A request Backstage makes'), ('external', 'A request anyone makes'),
                          ('security', 'Policy'), ('backend', 'How it is deployed')]))
    return dict(slug='the-admission-policies', eyebrow='Break-glass · 05 of 07 · The policies',
      title='Six admission policies, one per thing that could go wrong',
      desc='Top: what Backstage asks the API server to do: create a RoleBinding (the grant), add a debug container (ephemeral, or in a copy pod), delete a pod (cleanup), patch a pod (process access); and, from anyone on Flight, exec or attach. Below, six policies named tower-breakglass-something, all failing closed. rolebinding: the name starts tower-breakglass-, the role is debug-live or debug-copy, the only subject is Backstage, a TTL label of 15 to 75 minutes, an app namespace only, and on Flight either an approver who is not the requester or the glass-broken mark, never neither. debug-container: the pinned image digest, runAsNonRoot with a non-zero group, a read-only root, no privilege escalation, all capabilities dropped, every mount read-only, and process access only for the session the pod\'s annotation names. debug-image: a cosign keyless signature from tower\'s own workflow on main, logged in the public Rekor; it runs in Kyverno as a webhook scoped to these requests and fails closed too. pod-delete: Backstage may delete only copy pods or pods carrying a debug container, nothing else in the namespace. pod-annotate: the spec and labels are unchanged and only the process-access annotation with the session id may change. no-exec: no exec into app pods, attach only to debug containers, operators excepted, Flight only. Bottom: on Ground they are Kyverno ValidatingPolicies compiled to native admission policies with no webhook; on Flight they are hand-written ValidatingAdmissionPolicies synced by Argo CD before the backend that needs them.',
      lede='The backend is the first lock. These are the second, inside each cluster\'s API server, written so that a bug in Tower, or a compromised Backstage, still cannot turn a debugging session into something bigger.',
      body=''.join(b), W=1000, H=696, y0=76,
      cards=[('Native first', '', P('Validation runs as built-in ValidatingAdmissionPolicy, inside the API server. It cannot be down on its own, which matters most during the incident you opened the session for.')),
             ('One webhook, fenced', 'accent', P('Only the image signature needs Kyverno\'s webhook. Its match conditions are copied onto the webhook, so it never sees a request that is not break-glass.')),
             ('Learned the hard way', 'link', P('An unguarded CEL field once refused every pod create on the dev cluster for ten minutes. Now every optional field is guarded and every policy is scoped.'))])


def b_lifecycle():
    b = []
    b.append(zone(24, 100, 952, 200, 'a session'))
    states = [('Requested', 'Flight: 30 min to approve', 'propose'), ('Approved', '10 min to press Start', 'propose'),
              ('Active', '15/30/60 min · +15 once', 'focal'), ('Ended', 'never reopens', 'store')]
    for i, (n, s, k) in enumerate(states):
        x = 48 + i * 236
        b.append(node(x, 172, 200, 56, n, s, k))
        if i < 3:
            b.append(path([(x + 200, 200), (x + 236, 200)], 'accent' if i == 1 else 'muted'))
    b += [path([(560, 136), (560, 172)], 'accent'), lab(560, 120, 'GROUND OPENS HERE', ACC),
          path([(680, 136), (680, 156), (640, 156), (640, 172)], 'link'), lab(720, 120, 'GLASS BROKEN TOO', LINK)]
    b.append(text(48, 264, 'it ends when you end it, at its time, idle 10 min, tab closed 2 min, shell exit, pod gone, or terminated',
                  9, 400, MUTED, mono=True))
    b += [node(756, 316, 200, 56, 'Review due', 'glass broken only', 'security'),
          path([(856, 228), (856, 316)], 'link')]
    b.append(text(740, 392, 'remind at 24 h · escalate at 72 h', 9, 400, MUTED, 'start', mono=True))
    b.append(zone(24, 412, 952, 104, 'when it ends, in this order'))
    steps = [('1 Close terminal', 'and the k8s stream'), ('2 Delete the copy', 'copy mode'),
             ('3 Restart the pod', 'not a last ready one'), ('4 Remove the grant', 'the RoleBinding'),
             ('5 Store and audit', 'SHA-256 · Rekor')]
    for i, (n, s) in enumerate(steps):
        x = 48 + i * 184
        b.append(node(x, 444, 168, 48, n, s, 'backend' if i != 3 else 'security'))
        if i < 4:
            b.append(path([(x + 168, 468), (x + 184, 468)]))
    b += [node(48, 540, 904, 48, 'If Backstage never comes back',
               'the TTL label on the grant and the copy pod: Kyverno cleanup deletes both · a restarted backend ends every orphan in 15 s',
               'security')]
    b.append(callout(24, 628, 'A forgotten tab costs two minutes, not a standing door into production.'))
    b.append(legend(660, [('propose', 'Waiting'), ('focal', 'Open'), ('store', 'Done'), ('security', 'Cluster-side'),
                          ('link', 'Glass broken')]))
    return dict(slug='life-of-a-session', eyebrow='Break-glass · 06 of 07 · Time',
      title='The life of a session, and how it ends',
      desc='A session has four states. Requested, on Flight, has 30 minutes to be approved. Approved has 10 minutes to be started. Active lasts 15, 30 or 60 minutes, plus one 15-minute extension; a Ground session and a glass-broken session open straight into Active. Ended never reopens. A session ends when you end it, when it expires, after 10 idle minutes, 2 minutes after the terminal tab is closed, when the shell exits, when the pod is gone, or when an admin or the approver terminates it. A glass-broken session also becomes review due, with a reminder at 24 hours and an escalation at 72 hours. When it ends, in this order: close the terminal and the Kubernetes stream; delete the copy pod in copy mode; restart the live pod, unless it is the last ready one; remove the grant, the RoleBinding; store the recording with its SHA-256, anchor it in Rekor, and audit. If Backstage never comes back, the TTL label on the grant and the copy pod lets Kyverno\'s cleanup controller delete both, and a restarted backend ends every orphaned session within 15 seconds.',
      lede='Every clock in break-glass is short on purpose. Approval lapses, sessions expire, idle terminals end, and the cluster has its own timer in case everything else forgets.',
      body=''.join(b), W=1000, H=688, y0=76,
      cards=[('Short by default', '', P('Pick the shortest duration that will do. One free extension, audited, and then it is a new request.')),
             ('Clean up while allowed', 'accent', P('The pod is restarted and the copy deleted while the grant still exists, and only then is the grant removed. Anything left over is written on the record as a note.')),
             ('A backstop with no brain', 'link', P('The TTL label is set to the session plus fifteen minutes at creation. The cluster deletes the grant at that time, whatever state Backstage is in.'))])


def b_report_card():
    b = []
    rows = [
        ('Exec, removed', 'A-', 'Refused on Flight by the cluster; platform operators keep it, by design'),
        ('Who can open one', 'A', 'Owners only, checked on every route, tier decided by the server'),
        ('Least privilege', 'A', 'No standing rights; a per-session grant the API server checks'),
        ('The debug container', 'A', 'Pinned, signed, non-root, read-only, no capabilities, no token'),
        ('Two-person rule', 'B', 'Backstage writes the approver name the cluster checks; admins can skip it'),
        ('Evidence', 'B+', 'Locked a year, hashed, anchored; but self-hosted log, governance mode'),
        ('Data exposure', 'C+', 'Process and volume access read Secrets; open egress; recordings keep it'),
        ('Staying up', 'A-', 'Native policies, fail closed; the signature check still needs Kyverno'),
    ]
    b.append(zone(24, 100, 952, 8 * 52 + 24, 'tower break-glass · graded october 12, 2026'))
    for i, (area, grade, why) in enumerate(rows):
        y = 120 + i * 52
        weak = grade[0] in 'BC'
        b.append(node(48, y, 232, 40, area, None, 'security' if weak else 'backend'))
        b.append(text(336, y + 30, grade, 30, 400, ACC if weak else INK, 'middle', serif=True))
        b.append(text(392, y + 25, why, 12, 400, INK if not weak else INK))
        if i < 7:
            b.append(f'<line x1="48" y1="{y + 46}" x2="952" y2="{y + 46}" stroke="{RULE}" stroke-width="0.8"/>')
    b.append(text(48, 600, 'Overall', 12, 600, INK))
    b.append(text(336, 604, 'B+', 36, 400, ACC, 'middle', serif=True))
    b.append(text(392, 598, 'Strong where the cluster enforces it. Softest where it has to trust Backstage or the person.', 12, 400, INK))
    b.append(callout(24, 660, 'An A for the design. The B+ is for where it lives today.'))
    b.append(legend(692, [('backend', 'Holds up'), ('security', 'Where a security team will push')]))
    return dict(slug='an-honest-report-card', eyebrow='Break-glass · 07 of 07 · Honest notes',
      title='An honest report card',
      desc='Eight areas graded on October 12, 2026. Exec removed: A minus, refused on Flight by the cluster, though platform operators keep it by design. Who can open one: A, owners only, checked on every route, with the tier decided by the server. Least privilege: A, no standing rights and a per-session grant the API server checks. The debug container: A, pinned, signed, non-root, read-only, no capabilities and no ServiceAccount token. Two-person rule: B, because Backstage writes the approver name the cluster checks, and admins can skip it by breaking the glass. Evidence: B plus, locked for a year, hashed and anchored, but in a self-hosted transparency log and with governance-mode retention. Data exposure: C plus, because process and volume access can read Secrets, egress is open, and recordings keep whatever was shown. Staying up: A minus, native policies that fail closed, though the signature check still needs Kyverno. Overall: B plus, strong where the cluster enforces it and softest where it has to trust Backstage or the person.',
      lede='Where it holds up, and where a good security team would push. Graded by me, so read it as the case for the defence, with the weak spots left in.',
      body=''.join(b), W=1000, H=720, y0=76,
      cards=[('Hardest to argue with', '', P('No standing exec on Flight, no credential in anyone\'s hands, and a cluster that checks every field of every grant and container.')),
             ('Trust in one place', 'accent', P('Backstage is the one principal that can create grants. Protect it like a tier-0 system, because the two-person check in the cluster reads names Backstage wrote.')),
             ('Reading is still access', 'link', P('A read-only shell next to a database, with the app\'s credentials, is data access. The approver and the recording are the controls, not the container.'))])
