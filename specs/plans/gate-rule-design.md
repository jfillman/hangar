# A platform rule for Clearance's Argo CD gate

Written 2026-11-19. Strip W-42, owner decision Y-32 (option A). Status: design note, no code, nothing applied. The owner answered all the open questions on 2026-11-21 (see
"Decisions"). It replaces the W-35 note in hangar PR #131 (`gate-switch-design.md`), which proposed a platform list of app and
environment pairs in Hangar's `cluster.yaml`. The owner chose a different shape: a rule that lives in Clearance's own
configuration.

Facts were read from the clearance repo at origin/main on 2026-11-19 (`docs/gate.md` "Annotation opt-in",
`providers/argocd/agent/optin.go`, `protect.go`, `charts/clearance-argocd-agent`, `internal/gate/exception.go`,
`internal/server/records.go`). Nothing here was run against a cluster. Where this note leans on something it could not
read, it says so ("To confirm").

## Terms used below

- **The agent.** Clearance's Argo CD agent (`providers/argocd/agent`). It watches Argo CD Applications, switches
  gated ones to the Clearance plugin, writes the merged `ClearanceGrant`, and labels the destination namespace
  `clearance.hangar.io/protected=true` so admission enforces the gate.
- **The core.** Clearance's server. It holds the evidence chain and the set of protected app/environment pairs the
  agent reports (`PUT /v1/protection/{cluster}`).
- **Gated.** An Application the agent has switched to the Clearance plugin and whose namespace is protected.
- **Switched.** The agent has replaced the Application's source with the plugin source and kept the original in the
  Application (annotation `clearance.hangar.io/switched` plus the plugin's own `switched` parameter).
- **Opt-in annotation.** `clearance.hangar.io/protect: "true"` on an Application (G-ARGO-10c). Exactly that value.
- **The rule.** What this note adds: platform configuration that selects Applications to gate.
- **Exemption.** A platform-only, time-limited entry that lifts the rule's requirement from one Application.

## The goal

Today the agent gates an Application only if its owner asked, by the annotation. Anyone who can edit the Application
can remove the annotation, and the agent then puts the original source back. The removal is reported to the core first,
and a pair in the core's static `CLEARANCE_PROTECTED_ENVIRONMENTS` stays protected at the core, but the Application
itself is released (`docs/gate.md`, "Who can set the annotation").

W-42 adds a platform rule so the platform can require the gate for a group of Applications. A team cannot opt out of
what the platform requires. The rule can start empty and grow one project or namespace at a time. The owner rejected
per-app lists; this is a rule, not a list, so it scales with the platform instead of with the number of apps.

## 1. The rule

### Where it lives

In Clearance's settings, not Hangar's. The agent reads one YAML file, `--gate-rule-file` (env
`CLEARANCE_GATE_RULE_FILE`, default empty, meaning no rule). The agent chart renders the file from a new value,
`gateRule`, into a ConfigMap mounted read-only into the agent pod. The chart adds a checksum annotation to the pod
template so a change rolls the pod. The agent also re-reads the file every pass (30 s), so a refreshed mount is picked
up without a restart.

A platform team edits it in gitops: it is a values change for the `clearance-argocd-agent` chart, reviewed as a pull
request like any other chart value. No cluster edit, no new CRD.

The rule needs the opt-in machinery on. `gateRule` set with `optIn.enabled: false` fails chart render, and the agent
refuses to start with a rule and no `--optin`.

### Shape

```yaml
# gateRule (chart value; rendered to rule.yaml)
version: 1
select:                       # empty or absent: the rule gates nothing; annotation opt-in only
  - name: prod-tenants        # required; appears in records and in the status ConfigMap
    projects: [gate-api]      # globs on the Application's spec.project
    namespaces: ["app-*-prod"]  # globs on spec.destination.namespace
    labels: {hangar.io/env: prod}   # exact key=value on the Application's labels
  - name: backstage
    projects: [backstage]
exempt:
  - application: argocd/flight-api-prod   # glob on <namespace>/<name>
    reason: "migration to the new chart; owner 2026-11-19"
    expires: 2026-12-19                   # required; a date or an RFC 3339 time (UTC)
    ref: W-45                             # optional: a strip, ticket or PR
```

### Matching

- Inside one `select` entry, the keys that are present are combined with **AND**: an Application must match every one
  (`projects` and `namespaces` and `labels`).
- Inside one key, the values are combined with **OR**: `projects: [a, b]` matches a or b. Globs use the same matcher
  as `--optin-deny` (`*` and `?`). `labels` is the exception: every listed label must match (AND), exact value.
- Across `select` entries the combination is **OR**: matching any entry is enough.
- An entry with none of the three keys is invalid and refused (it would match everything). To gate everything in a
  project, write `projects: [x]`; to gate everything the agent can see, write `projects: ["*"]` on purpose.
- A project-only entry is valid (decision 2). `projects: [gate-api]` gates gate-api in every environment. The matcher
  does not require `namespaces` or `labels`.

Why AND inside and OR across: one entry can say "this project, but only its prod namespaces", and the next entry can
add a second project. The rule grows by appending an entry, and no entry can accidentally widen another.

The rule applies only inside the agent's existing limits: `--projects` (the Argo CD projects the agent reads; the chart
requires it, `["*"]` for all, and the agent lists Applications and keeps those in it, it does not discover projects) and
`--optin-namespaces` (the namespaces it holds RBAC for). The two limits behave differently, and the order is fixed:

1. **Project filter first.** The agent drops an Application outside `--projects` before it classifies it
   (`classify`: "an Application outside the agent's projects is not seen at all"). The rule is never evaluated for it,
   and nothing is reported or marked `blocked`. The one exception is an Application the agent already switched that has
   left the projects: it is put back like an opt-out (existing). So the project ceiling is guarded at **render time**,
   not at run time: apron fails the render when an entry's `projects` value is not in the ceiling. apron cannot expand
   a glob, so a glob value (for example `team-*`) passes only when the explicit ceiling list holds the same glob or
   `*`; otherwise the render fails and names the entry. A literal value passes when the ceiling holds it, the same glob
   that matches it, or `*`. A namespace-only or label-only entry names no project, so apron cannot check it; its projects must be in the explicit
   list (section 6, step 7.3.1), and the migration's coverage check (step 7.2) is what catches a miss.
2. **Namespace ceiling second.** An Application that passes the project filter and matches the rule, but whose
   destination namespace is not in `--optin-namespaces`, is `blocked`, with the reason in the status ConfigMap, and
   still reported as a protected pair, exactly as a blocked annotated one is today (`docs/gate.md`, "What is never
   switched").

The rule never widens what the agent may touch. Decision 1 covers what that
means for growth: the owner accepted it for step one.

### Precedence

In order, the first that applies wins:

1. **Deny list** (`--optin-deny`: `clearance`, `clearance-*`, `*-clearance`). Never gated, rule or not. Unchanged. It
   keeps Clearance's own Applications repairable through Argo CD.
2. **Exemption** (section 2). Lifts the rule only.
3. **The rule.** Matched means gated, as if the Application carried the annotation.
4. **The annotation.** Gated if present, as today.

An Application is gated if (the rule matches and no exemption applies) or it is annotated, and it is not denied. In
`optin.go` terms: `optedIn` stays what the annotation says, a new `ruled` is what the rule says, `protectedIntent` and
`wantsSwitch` become `(optedIn || ruled) && !denied`, and an exemption clears only `ruled`. The agent never writes the
annotation for a ruled Application; it evaluates the rule every pass from the Application's current labels, project and
destination.

The tenant's annotation can add to the rule (an exempt Application that still carries the annotation stays gated) but
can never subtract from it.

### Why a rule and not a list

A per-app list needs an edit for every new app and environment, in every place that names them. The W-35 note counted
those places, PR #131 collapsed them to one list, and the owner rejected that list too. A rule selects by properties
every Application already has: its Argo CD project, its destination namespace, its labels. A new tenant that lands in a
gated project or an `app-*-prod` namespace is covered with no edit. The platform grows coverage by widening the rule,
one project or namespace at a time, and narrows it only through exemptions, which are visible and expire.

## 2. Exemptions

### Shape and home

An exemption is an `exempt` entry in the same rule file. Fields:

| Field | Required | Meaning |
|---|---|---|
| `application` | yes | glob on `<namespace>/<name>` of the Application. Same matcher as the deny list. |
| `reason` | yes | free text, 10 to 500 characters. Goes into the record. |
| `expires` | yes | a date or RFC 3339 time. At most `--gate-exempt-max` (default 90 days) from now; a longer one is refused. No cooling-off period: a repeat exemption for the same Application is allowed (decision 5). |
| `ref` | no | a strip, ticket or PR. |

"Who" is the git history of the gitops change that added the entry (author, reviewer, merge), not a field a person types.
The agent cannot see git, so its record names the rule file's digest and the entry; the evidence of who is the pull
request. There is no `approvedBy` field (decision 4): the pull request is the record of who.

An invalid entry (no reason, no expiry, expiry too far out, an empty glob) is refused as a whole. The agent ignores it,
so the Application stays gated, and posts one exception.

### Treatment by the agent

- An exemption lifts `ruled` only. It does not lift the annotation: a tenant can always opt in, and an exemption never
  un-gates an annotated Application.
- An exempt Application that is not yet gated is left alone (the agent reads it and never writes it).
- An exempt Application that is already gated by the rule alone is released by the normal removal order: report the
  removal to the core, label off, put the original source back, remove the merged grant. The reason on the report names
  the exemption. If the core cannot be reached, nothing is released (existing behaviour).
- **Statically protected environments (decision 6, decided 2026-11-21).** The core's `CLEARANCE_PROTECTED_ENVIRONMENTS` keeps a
  pair protected whatever the agent reports (`static_removed`). The agent does not honour an exemption whose pair is
  static. The core, not the agent, enforces it: the core refuses the exemption
  request (see "Records") when the pair is static, so it is refused before any release and also for an Application that
  was never gated. The core refuses a removal report whose reason is an exemption on a static pair for the same
  reason. The agent leaves the Application gated and shows `refused: static` in its status. This is the owner's decision; see "Decisions", item 6.

### Records

The core's `deploy.exception` kinds are a closed list (`internal/gate/exception.go`): `out-of-band`, `drift`,
`untraced-apply`, `digest-mismatch`, `attempted-refused`, `monitoring-protection`. None fits "the platform has let this
Application out of the gate until a date". So two records result:

1. **`protection.report`**, as today, when an exemption releases a gated Application: the pair leaves the reported set
   and the reason names the exemption. No core change.
2. **`deploy.exception` with a new kind, `gate-exemption`** (a small core change: the kind joins `ExceptionKinds` and the
   statement's exception classes, so an exemption shows in the coverage statement as the gap it is). The agent posts it
   with `state` `active` when an exemption first matches an Application, as `expiring` seven days before `expires`, and
   as `expired` when it lapses. `detail` carries the `reason`, `expires`, `ref`, the matching rule name and the rule
   file's digest. While active it is reposted at most once per 24 hours, the pattern the agent already uses for a
   failing CRD check.

A `protection.report` exists only when a gated Application is released. An exemption that matches an Application never
gated produces no release and so no report, which would leave it unrecorded, and would give the core no chance to
refuse it (for example when the pair is static, decision 6). So the core decides **every** exemption, gated or not. The
agent posts the `gate-exemption` record with `state` `requested` for each exemption it intends to honour, naming the
Application's app and environment pair. The core answers `accepted` or `refused` with a reason (`refused: static`, or
`unknown kind` on an old core). The agent **honours an exemption only after the core has accepted it**, and keeps the
answer with the rule digest and the entry, so a changed entry is asked again. A refused or unanswered exemption is
ignored: the Application stays gated (fail closed), the status shows the reason, and the agent posts one exception. The
request is retried each pass until answered, with the 24 hour repost limit on the exception.

An acceptance is **keyed to the Application's current (app, environment) pair**, together with the Application's
`<namespace>/<name>`, the rule entry and the rule file's digest. If any of these changes (a relabelled namespace, a
moved destination, an edited entry, a new digest), the acceptance is void and the agent asks again before honouring
anything. The core also re-decides: it checks the pair against `CLEARANCE_PROTECTED_ENVIRONMENTS` each time it is
asked, so if the platform adds an actively exempt pair to that list, the next answer is `refused: static`. The agent
re-asks for every honoured exemption on every rule reload, on any key change, and at least every 5 minutes
(`--gate-exemption-recheck`, default 5m). A refusal revokes the exemption: the agent re-gates the Application in the
normal add order and posts the `expired` state with reason `revoked`. The revocation window is therefore at most the
recheck interval. If the core cannot be reached at a recheck, the acceptance is dropped at once and the Application is
re-gated (fail closed, no retention). Every recheck request carries a deadline shorter than the recheck interval
(default 30 seconds, `--gate-exemption-recheck-timeout`); a request that misses its deadline counts as unreachable. The bound is exactly one recheck interval: the longest an exemption can outlive
a change at the core, or the core's absence, is the time to the next recheck. Only an accepted
exemption then produces the `active`, `expiring` and `expired` states below. Exemptions are enabled only after the core
change ships. The owner chose the new kind (decision 3), so this is a two-repo change.

### Re-gating while the core is down

**What the code does today.** The agent's add order starts with the core: `reportPairs` reports the protected pairs, and
a new Application is not switched until `pairAccepted` says the core took its pair (`providers/argocd/agent/optin.go`,
"A pair is added at the core before its Application is switched"; status `waiting for the core to take its pair`). With
the core down, a new Application therefore waits ungated. For a first gating that is the existing, accepted window
(section 5, "Core down").

**What this design needs.** A revoked, dropped or expired exemption re-gates an Application that was just released from
the gate, and the core being down is exactly when a revocation is dropped for lack of an answer. The re-gate must not
wait for the core, or "fail closed" would mean ungated until the core returns. So for a **re-gate only** (the Application
was released by an exemption, or an exemption's acceptance is dropped) the agent gates locally first: switch, grant,
then label, with no `pairAccepted` wait, and queues the pair report in its state ConfigMap, delivering it when the core
is back (retry each pass). The report intent is **persisted before the switch**, so a crash after any later step still
leaves it queued. As a second guard, every pass reports the full set of gated pairs from the live Applications
(`reportPairs`, to confirm it re-sends the whole set each pass), so a restarted agent rebuilds the report for any gated
Application that has none recorded. A first gating of a never-gated Application keeps today's order, core first. To confirm
before build: that the agent can write the merged grant and label the namespace without a core call (the label needs
the grant active and valid, section 5, "Admission"), and that the queued report survives an agent restart.

**Code change, on the W-42 build list.** This reverses the core-first order for re-gates, so it is a change to
`optin.go`, not only new code: a re-gate path that skips `pairAccepted`, a persisted report queue, and tests (a re-gate
with the core down gates locally and delivers the report on return; a first gating still waits for the core).

### Expiry

When `expires` passes (the agent's clock, no grace), the exemption stops applying on the next pass. The rule gates the
Application again: switch, grant, then label. See "Re-gating while the core is down" below for the order.
The agent posts `expired` once. An expired entry left in the file is ignored and reported once per 24 hours as a stale
`gate-exemption`, so the platform removes it. The agent never edits the file, and never renews an exemption; renewing is
a pull request that changes the date.

### Only the platform creates them

- The file is a ConfigMap in `clearance-system`, rendered from the chart value and mounted read-only. The agent's
  ServiceAccount does not write it (its ConfigMap rights are `get, create, patch` in the state Role; to confirm that
  Role is limited by `resourceNames` to the state ConfigMap before rollout).
- No Application field, label or annotation creates an exemption. An annotation such as `clearance.hangar.io/exempt` is
  not read at all, and a test pins that.
- Tenants have no write path to `clearance-system` (their AppProjects restrict destinations). To confirm on hangar-dev
  and hangar-prod in the rehearsal (section 6).

## 3. Opt-out, release and transitions

**A team cannot opt out of the rule.** Removing the annotation from a rule-matched, non-exempt Application changes
nothing: `ruled` is still true and the Application stays gated. Nothing is recorded, because no pair left the set.

The transitions. "Gated" means rule or annotation, non-exempt, not denied.

| Event | What the agent does |
|---|---|
| Rule starts matching an Application that already carries the annotation (and may be switched) | Nothing new. It is already switched and labelled. Status notes both reasons. The pair is already reported. |
| Rule starts matching an unannotated Application | Normal add order: report the pair, switch, grant, then label. The first change needs a clearance, as for any gated Application. |
| Rule stops matching an Application (entry removed or narrowed) and it is **not annotated** | Release by the normal removal order: report the removal (reason: `rule no longer matches <app>/<env>`), label off, restore the source, remove the grant. |
| Rule stops matching an Application that **is annotated** | Stays gated by the annotation. Nothing released. |
| Annotation removed, rule still matches | Stays gated. |
| Annotation removed, rule does not match | Released, as today. |
| Exemption added for a rule-gated, unannotated Application | Released as above, with the exemption in the reason; a `gate-exemption` active record. |
| Exemption added for an annotated Application | Stays gated by the annotation. Recorded as active but ineffective. |
| Exemption expires, or its acceptance is revoked or dropped | Gated again by the rule: switch, grant, label locally, pair report queued if the core is down (section 2). |
| The rule file cannot be read or is invalid while running | **Keep the last good rule.** Nothing is released: the removal order only runs for an Application the agent has positively decided to release. One exception is posted, at most once per 24 hours. |
| The agent restarts and the rule file cannot be read or is invalid | The agent keeps a copy of the last good rule (and its digest) in its state ConfigMap, beside its other state, and uses that copy. With no file and no copy it **does not become ready** and gates nothing new; it never starts with an empty rule when a rule is configured. Releases are not made. One exception is posted. Because the chart renders the file from a value it has already validated, this needs a failed mount or a bad hand edit of the ConfigMap. |
| A pair is shared by two Applications and one is released | As an opt-out of one of two Applications today: the set does not change, the removal is still recorded, and the other Application is named. |

**Narrowing the rule is the one move that can release many Applications at once.** Two guards. The agent acts on a
release only after the core has taken the report (existing). And it limits rule-caused releases to
`--gate-release-max` (default 3) Applications per hour, leaving the rest gated and saying so in the status. The platform
can raise the limit on purpose. This stops one bad rule edit from un-gating a whole project in one pass.

### ApplicationSet interaction

Most Applications on Hangar are generated by the tenant-onboarding ApplicationSet. The W-40 findings, as handed to me,
are these: an ApplicationSet resets an Application to what its template says, so any annotation not in the template is
wiped unless it is listed in `preservedFields`; and the agent's `switched` marker is exactly such an annotation. I could
not find the W-40 write-up in the hangar or clearance repos, so this note does not restate its evidence. To confirm
against it before implementation.

What the rule changes:

- **The opt-in annotation is no longer the only way in.** For an ApplicationSet-made Application today, the annotation
  must be in the template or the ApplicationSet wipes it. The rule needs no annotation on the Application, so that wipe
  cannot remove the platform's requirement. This is the main reason the rule suits the platform's own Applications
  better than the annotation does.
- **The `switched` marker is still an annotation the ApplicationSet can wipe.** `docs/gate.md` ("What the parent must
  say") already requires the parent to ignore `/spec/source` and `/spec/sources` (`ignoreApplicationDifferences` with
  `RespectIgnoreDifferences=true`). Per W-40 the template also needs
  `preservedFields.annotations: [clearance.hangar.io/switched]` (and `clearance.hangar.io/protect` for annotated ones).
  That is a Hangar-layer change in apron's ApplicationSet. Clearance does not edit the parent, but its parent check
  already reads the ApplicationSet and refuses to switch when the entry is missing. The rule path reuses that check and
  adds `preservedFields` to what it asks for.
- **A wiped marker on a rule-gated Application** leaves it on the plugin with a plugin `switched` parameter and no
  matching annotation. Today such an Application is "left alone" and reported once, so that an annotate-only user cannot
  take a hand-made plugin Application off the plugin. For a rule-gated one this is a protection gap, so it also posts a
  `deploy.exception` (existing kind `drift`) naming the Application, once per 24 hours. Prevention is the
  `preservedFields` entry above.

## 4. Two layers: Clearance installs alone, Hangar only sets the rule

**Clearance (the product).** Owns everything in this note: the rule schema, the matching, the precedence, exemptions,
records, the chart value `gateRule`, the flags, the tests and `docs/gate.md`. It works on a cluster with Argo CD and
nothing else: no apron, no Airframe, no Hangar, no tenant-onboarding ApplicationSet. An install with an empty or absent
rule behaves exactly as today. This is the standing rule that Clearance installs on its own.

**Hangar (the platform).** Owns only the values. apron's `cluster.yaml` gets a pass-through,
`clearance.gate.agent.rule`, rendered unchanged into the chart's `gateRule`. apron does not interpret or validate the
rule's contents; the chart and the agent do (the chart fails render on a bad rule, the agent refuses it at start). The
one thing apron derives is the `protectedNamespaces` ceiling that sizes the agent's RBAC: it reads the literal
namespaces in the rule's entries (decision 1) and adds them. A glob namespace gives no literal, so it needs its names
listed by hand. Hangar also owns the `preservedFields` and `ignoreApplicationDifferences` entries in its
ApplicationSet, which concern its own Applications and not the rule.

Hangar's old path goes away (decision 7, section 6): `clearance.gate.apps`, the ApplicationSet's app and environment
regexes and its plugin source. The rule replaces them. `gate.agent.projects` stays as the agent's project ceiling, derived
from the rule where it can be (section 6, step 7.3.1). The two paths are not kept side by side
after the migration.

The line: if the product needs it to work on a bare cluster, it is Clearance's. If it exists because Hangar generates
Applications from an ApplicationSet, it is Hangar's.

## 5. Security

**Who can change the rule.** Whoever can merge a values change to the `clearance-argocd-agent` chart in the cluster's
gitops repo. On hangar-prod that is the owner (prod gitops pull requests are owner-merged). The ConfigMap is not
writable by the agent or by tenants.

**Audit trail.** Three layers: the git history of the values change; the agent logging the rule file's digest on every
change and carrying it in its `gate-exemption` records and release reasons; and the core's evidence chain (a
`protection.report` for every release, a `gate-exemption` record for every exemption). A rule change that gates more
needs no record, because more protection is not a hole. A rule change that un-gates something produces a
`protection.report`. A rule file changed with no pull request behind it is drift that Argo CD reports on the ConfigMap.

**Admission.** Unchanged. Admission selects on `clearance.hangar.io/protected=true` on the namespace. The agent still
sets that label only after the namespace's merged grant is active and valid, and removes it before the grant goes. The
rule decides which Applications the agent works on; it does not change who may label a namespace. A hand label (no
`protected-by: optin` marker) is still never removed by the agent.

**Failure modes.**

- **Agent down.** What is labelled stays enforced; what is switched stays switched. A new rule-matched Application is
  not gated until the agent returns (the same window a new annotated one has today). The core marks the agent's report
  stale after 15 minutes and does nothing else with it (existing).
- **Core down.** No removal is acted on and no new Application is switched, because a pair is added at the core before
  its Application is switched (existing). Nothing is released; new first gating waits. An exemption whose acceptance
  cannot be rechecked is dropped at once and its Application is re-gated locally, with the pair report queued (section
  2, "Re-gating while the core is down").
- **Rule invalid or unreadable.** Last good rule kept, from the state ConfigMap across a restart; one exception. Never a
  release. With no good rule anywhere the agent stays not ready, so a new rule-matched Application waits, in the same
  window as agent down. Admission cannot cover it: it does not select an unlabelled namespace.
- **Clock wrong.** A clock ahead makes an exemption lapse early, which gates sooner (safe). A clock behind lets an
  exemption run past its date. The agent uses its node clock.

**Known gaps already on the board, referenced and not solved here.**

- **I-43:** plain-HTTP tokens between components. The rule adds no token and no endpoint, but every record this note
  adds travels the same way.
- **I-44:** admission has no clock. Admission itself does not enforce a grant's expiry, and an exemption's expiry is
  enforced by the agent, not by admission, so the same weakness applies: an exemption that lapses while the agent is
  down does not re-gate until the agent is back.

## 6. Rollout and tests

### Order

1. **Clearance PR (code, behind the flag).** `--gate-rule-file`, the matcher, `ruled` and exemption handling, the
   release-rate guard, the records, the chart value, docs, and the re-gate path that does not wait for the core with a
   queued pair report (an `optin.go` order change, see "Re-gating while the core is down"). With no file, nothing changes: a render with no `gateRule` is
   byte-identical to today's (`tools/charttest` pins that).
2. **Core PR (small).** The `gate-exemption` kind. Exemptions are not enabled anywhere until it ships; an agent on a core
   that refuses the kind ignores every exemption (Applications stay gated) and says so once.
3. **Release and pin.** New Clearance image digest and chart version; Hangar pins them in apron.
4. **hangar-dev.** Pin, then enable the pass-through with an **empty** rule and confirm nothing changes. Then one
   project (a test tenant), then a namespace pattern. This is the live rehearsal.
5. **Hangar's ApplicationSet change** (`preservedFields`, per W-40) lands before any ApplicationSet-made Application is
   put under the rule on dev.
6. **hangar-prod.** The same ladder, owner-merged: empty rule, then one project (`gate-api`, already gated by the old
   lists), then a namespace pattern. Overlap with the old regexes introduces no gap: an Application both gate is gated
   once.
7. **Migrate Hangar off the old path (decision 7).** Within W-42. The order is fixed so nothing is ungated at any point:
   render the rule first, confirm coverage, then remove the old lists. Do dev first, then prod.
   1. **Render the rule next to the old lists.** In the cluster's `cluster.yaml`, add the rule under
      `clearance.gate.agent.rule` with one entry for each app the old lists gate. hangar-prod today: `apps:
      [gate-api, backstage]`, `agent.projects: [gate-api, backstage]`, `agent.protectedNamespaces:
      [app-gate-api-prod, app-backstage-prod]`, so entries `projects: [gate-api]` and `projects: [backstage]` (or
      `namespaces` where a project holds more than the old apps). hangar-dev has no `apps` list and runs with
      `tenantPlugin: false`, with `projects: [w40-optin-test]`; its entry is that project. Render with apron and
      commit the render. Old lists stay in place. An Application both gate is gated once.
   2. **Confirm coverage.** For every Application the old lists gate, read the agent's status ConfigMap and check that
      the rule selects it (reason `rule`) and that the namespace is still labelled `clearance.hangar.io/protected=true`.
      Compare the set of protected pairs the core holds before and after: they must be equal. Do not go on until they
      are. A rule-matched Application that shows `blocked` means a namespace is missing from the ceiling; fix that first.
      An Application the old lists gate that does not appear in the status at all is in no project of the ceiling (the
      agent does not see it): add its project to the project list first.
   3. **Remove the old lists, in this order, one render and one pull request each, confirming after each.**
      1. `clearance.gate.agent.projects` **stays, as the agent's project ceiling.** The agent does not discover projects:
         the chart requires `argocd.projects` and the agent reads only Applications in it. A namespace-only or
         label-only rule names no project, so removing the list would leave such a rule with nothing to read. What
         changes is who writes it: apron derives the ceiling from the literal `projects` values of the rule's entries,
         and adds the list `clearance.gate.agent.projects` (renamed in the values to extra projects, if wanted) for
         the projects that namespace-only and label-only entries need. Without a derivable or listed project the render
         fails. `["*"]` stays allowed. Check that every project holding a rule-matched Application is in the ceiling.
      2. `clearance.gate.apps`, then `clearance.gate.canary.apps` if set. `gate.apps` feeds
         `CLEARANCE_GATE_APP_REGEX`, which the tenant-onboarding ApplicationSet uses to decide which Applications get the
         plugin source. The Applications are gated by the rule from here on, so the source switch moves to the agent.
      3. The ApplicationSet regexes and plugin source: the `regexMatch` condition on `CLEARANCE_GATE_ENV_REGEX` and
         `CLEARANCE_GATE_APP_REGEX` and the `plugin: name: CLEARANCE_PLUGIN_NAME` source in
         `02-argocd-apps/tenant-onboarding/chart/applicationset.tmpl.yaml`. Remove them last. Until the agent has
         switched an Application, the ApplicationSet's plugin source is what gates it; removing it earlier would
         release the Application. Confirm each Application is `switched` first. Add `preservedFields` and
         `ignoreApplicationDifferences` here, so the ApplicationSet does not wipe the agent's marker (section 3).
      4. `clearance.gate.tenantPlugin` (a switch for the regex path, so it has no job left) and any of
         `gate.agent.protectedNamespaces` that the rule's literal namespaces now derive.
   4. **Confirm again after each removal.** The protected-pair set at the core must not shrink. A shrink means stop and
      put the removed list back.
   5. **Update the docs that name the old path:** apron `README.md` (the `clearance.gate.*` rows),
      `templates/TOKENS.md`, and hangar `docs/policy/business-rules.md` (CLR-20 and the "only gate-api is gated" row).
   **Rollback.** Revert each removal as a pair: the values commit and, for step 3.3, the commit that changed
   `applicationset.tmpl.yaml` (regexes and plugin source). Restoring only the list cannot bring back the deleted
   template logic. For 3.3, revert the template commit and its apron render together, with the `gate.apps` and
   `tenantPlugin` values, then render and check that the old protected-pair set is back. Do the template removal in its
   own pull request so one `git revert` undoes it. The rule is never deleted by the migration, so rolling back leaves
   both paths active, which is harmless.

### Tests

Unit (agent, `providers/argocd/agent`, table-driven in the style of `optin_test.go`):

- Matcher: OR across entries, AND inside one, OR across a key's values, labels all-match, an empty entry refused, glob
  edges, an Application with no labels.
- Precedence: deny beats exemption beats rule beats nothing; annotation plus exemption stays gated; annotation absent
  with a rule stays gated; `clearance.hangar.io/exempt` on an Application is ignored.
- Every row of the transitions table in section 3, including narrowing with the annotation present and absent, and the
  release-rate guard (a fourth rule-caused release in an hour waits).
- Exemption validation (missing reason, expiry too far, malformed date) and expiry on a fake clock: active, expiring at
  seven days, expired, stale entry.
- Rule file failures: invalid after a good rule (last good kept), invalid at restart (state copy used), neither
  available (not ready, nothing released, nothing new gated), re-read without a restart.
- Exemption against a core that refuses the kind: ignored, Application stays gated, one exception.
- A pair shared by two Applications; a blocked rule-matched Application still reported as a pair.
- Chart: byte-identical default render; `gateRule` with `optIn.enabled: false` fails render; checksum annotation.
- Core: the `gate-exemption` kind is accepted, validated and shown in the coverage statement.
- Static pair (decision 6): the core refuses an exemption request whose pair is static; the agent leaves
  the Application gated and shows `refused: static`. Two cases: an Application already gated (the removal report is
  also refused) and an Application **never gated** that matches both a static pair and an exemption (no removal report
  exists, the request alone is refused, the Application is switched and labelled by the rule).
- Exemption keying and revocation: a pair change (namespace relabelled, destination moved) voids an accepted exemption
  and the agent asks again; an edited entry or new rule digest does the same; the core adds an exempt pair to
  `CLEARANCE_PROTECTED_ENVIRONMENTS` after acceptance, the next recheck is refused and the Application is re-gated;
  the recheck runs on rule reload and at the interval; an unreachable core at a recheck drops the acceptance at once
  and the Application is re-gated, with no one-interval retention.
- Recheck deadline: a recheck that stays pending past its deadline counts as unreachable; the acceptance is dropped and
  the Application re-gated within one recheck interval, even when the connection never fails.
- Re-gate with the core down: a revoked, dropped or expired exemption's Application is switched, granted and labelled
  with no core call, the pair report is queued and delivered when the core returns (also across an agent restart); a
  crash between the label and the report (and between the intent write and the switch) still ends with the pair
  reported; a
  first gating of a never-gated Application still waits for the core.
- Exemption decision: no exemption is honoured before the core accepts it; an unanswered request leaves the Application
  gated; a changed entry is asked again.
- Project ceiling: a namespace-only rule and a label-only rule each gate their Application once the old list is gone,
  when its project is in the derived or listed ceiling; with the project missing the Application is not seen (no
  status row, nothing reported, no rule evaluation), and apron fails the render when a rule entry's `projects` value
  is not in the ceiling. Glob case: an entry `projects: ["team-*"]` with a ceiling of `[team-a]` fails the render; it
  passes with `["team-*"]` or `["*"]` in the ceiling. A matched Application in a project of the ceiling but a namespace outside
  `protectedNamespaces` is `blocked` and reported as a pair.
- Migration (apron): with the rule rendered and the old lists still present, the protected pair set is unchanged; with
  the old lists removed, it is still unchanged; `tools/charttest` and `tests/run.sh` pass with the old keys gone.

Live rehearsal on hangar-dev (a script, like the W-40 rehearsal; no prod writes):

1. Empty rule: nothing changes anywhere.
2. Rule for a test project: the unannotated Application is switched, granted and labelled; a deploy needs a clearance.
3. Remove the annotation from a rule-matched one: still gated.
4. Narrow the rule: it is released, and the core shows the `protection.report`.
5. Restore the matching rule so it is gated again. Exempt it with a short expiry: released and a `gate-exemption`
   active record; let it expire: gated again.
6. Corrupt the rule file: last good kept, one exception, nothing released. Restart the agent with the file corrupt:
   the state copy is used. Restart with neither: not ready, nothing released.
7. Repeat for an ApplicationSet-made Application, with and without `preservedFields`: the marker survives with it and
   the exception fires without it.
8. Stop the core mid-release: nothing released.
9. As a tenant identity, try to write the ConfigMap and set the exempt annotation: refused or ignored.

## Decisions (owner, 2026-11-21)

The owner answered the seven questions on 2026-11-21. All seven are decided.

1. **Namespace growth: accepted for step one.** The `protectedNamespaces` list is a safety ceiling. The rule decides
   what is gated. apron derives the ceiling from the rule's literal namespaces, so a rule that names a namespace needs
   no second edit. A rule that matches by glob still needs its names listed, or the Application is `blocked` (reported
   as a pair, not switched) with the reason in the status. The cluster-wide Namespace `patch` alternative is not taken.
2. **Project-only entries are allowed.** `projects: [gate-api]` gates gate-api in every environment. The matcher does
   not require `namespaces` or `labels`.
3. **New core exception kind: yes.** `gate-exemption` joins the core's `deploy.exception` kinds. This makes W-42 a
   two-repo change (clearance and the core). Exemptions are not enabled until the core ships it.
4. **"Who" is the pull request.** There is no `approvedBy` field. The git history of the gitops change is the record.
5. **Limits: right as written.** 90-day maximum exemption, 7-day warning, at most 3 rule-caused releases per hour. No
   cooling-off period: a repeat exemption for the same Application is allowed.
6. **Statically protected environments: exemptions are refused there, enforced at the core.** The owner chose this
   on 2026-11-21 (board ask A-16, option a). The core's `CLEARANCE_PROTECTED_ENVIRONMENTS` keeps a pair protected
   whatever the agent reports. An exemption in such an environment would release the Application at the agent while the
   core still holds the pair, so the pair and the Application would disagree. So the core refuses every exemption
   request for a pair on its static list, and refuses a removal report whose reason is an exemption on such a pair. The
   agent then leaves the Application gated and shows `refused: static` in its status. Enforcing at the core means a
   misconfigured agent cannot get around it.
7. **The old Hangar path: migrate now.** Within W-42 the rule replaces `clearance.gate.apps`, the ApplicationSet regexes
   and the plugin source. `gate.agent.projects` is kept as a project ceiling, derived from the rule (the agent reads
   only the projects it is given and does not discover them). The two paths are not kept side by side. The order is in
   section 6, step 7: render the rule, confirm coverage, then remove the old lists.

## What the owner does by hand

- Review and merge the clearance, core and apron pull requests, and the gitops changes for dev and prod (prod: owner
  only), including each removal step of the migration (section 6, step 7).
- Pin the new Clearance image and chart in `cluster.yaml` after release.
- After the first non-empty rule on prod, check one Application and its namespace by hand.
- Nothing in the tenants repos or Airframe.
