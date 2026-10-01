"""The SLO set: how an SLO goes from a values file to a notification (2026-10-01)."""
from libx import *

AMB = lambda a: f'rgba(185,121,31,{a})'   # ACC at an alpha
INKA = lambda a: f'rgba(27,31,36,{a})'


def s_pipeline():
    b = []
    b += [zone(24, 100, 432, 132, 'declare · app repo and chart'),
          zone(472, 100, 488, 296, 'render · crossplane'),
          zone(24, 412, 936, 140, 'observe · prometheus and its readers')]
    b += [path([(224, 172), (264, 172)]), path([(440, 172), (480, 172)]), path([(656, 172), (696, 172)]),
          path([(812, 212), (812, 300)], 'accent'),
          path([(730, 212), (730, 268), (568, 268), (568, 300)]),
          path([(780, 364), (780, 430), (568, 430), (568, 460)], 'accent'),
          path([(480, 492), (440, 492)]), path([(656, 492), (696, 492)])]
    b += [node(48, 140, 176, 64, 'slos: entry', 'platform/envs/<env>.yaml', 'input'),
          node(264, 140, 176, 64, 'airframe-application', 'attached/slos.yaml'),
          node(480, 140, 176, 64, 'SLO XR', 'slos.catalog.hangar.io', 'focal'),
          node(696, 140, 232, 64, 'Composition', 'function-go-templating'),
          node(696, 300, 232, 64, 'PrometheusServiceLevel', 'sloth.slok.dev/v1 · Sloth'),
          node(480, 300, 176, 64, 'Grafana dashboard', 'ConfigMap · sidecar-loaded'),
          node(480, 460, 176, 64, 'Prometheus', 'slo:* recording rules', 'store'),
          node(264, 460, 176, 64, 'Backstage poller', 'notifies on transitions'),
          node(696, 460, 232, 64, 'Tower', 'SLOs tab · fleet dashboards')]
    b.append(callout(24, 588, 'You write an objective and an indicator. Sloth writes the rules, and everything downstream reads them.'))
    b.append(legend(620, [('input', 'Declared in git'), ('focal', 'The SLO API'), ('backend', 'Rendered or running'), ('store', 'Metrics'), ('accent', 'Rules flow')]))
    return dict(slug='slo-pipeline', eyebrow='SLOs · 01 of 04 · From values file to burn rate',
      title='From a values file to a burn rate',
      desc='Left to right across the top: an slos entry in an environment values file is rendered by the airframe-application chart into an SLO XR in the catalog.hangar.io group, which a go-templating composition turns into a Sloth PrometheusServiceLevel and a Grafana dashboard ConfigMap. Sloth generates slo recording rules in Prometheus. Below, Prometheus is read by the Backstage poller, which sends notifications on transitions, and by Tower, which shows the SLOs tab and the fleet dashboards.',
      lede='An SLO is declared once, in an application\'s environment values. Crossplane composes it into a Sloth resource, Sloth generates the burn-rate rules, and the same series feed both what Tower shows and what the poller announces.',
      body=''.join(b), W=1000, H=648, y0=76,
      cards=[('Declared', '', P('One slos: entry per SLO: a service, an objective such as 99.9, and an indicator (availability or latency). There is no window and no burn-rate list; Sloth owns both.')),
             ('Rendered', 'accent', P('The XR is composed into a PrometheusServiceLevel and a Grafana dashboard. Sloth then generates the recording rules and the multi-window alerts for it.')),
             ('Read', 'link', P('Tower and the poller read the same series, among them slo:period_burn_rate:ratio, selected by sloth_service and by sloth_slo, which is <name>_<namespace>.'))])


def _lane(y, title, sub, scale, a, b, ticks, hold_lbl):
    """One threshold lane: healthy | hold band | burning along a burn-rate axis."""
    x0, x1 = 96, 896
    xa, xb = scale(a), scale(b)
    s = text(48, y, title, 8, 500, MUTED, mono=True, ls='0.14em') + text(48, y + 18, sub, 12, 600, INK)
    top, h = y + 36, 44
    s += (f'<rect x="{x0}" y="{top}" width="{xa-x0:g}" height="{h}" fill="{INKA(0.03)}" stroke="{INKA(0.16)}" stroke-width="0.8"/>'
          f'<rect x="{xa:g}" y="{top}" width="{xb-xa:g}" height="{h}" fill="{AMB(0.18)}" stroke="{ACC}" stroke-opacity="0.5" stroke-width="0.8" stroke-dasharray="4,3"/>'
          f'<rect x="{xb:g}" y="{top}" width="{x1-xb:g}" height="{h}" fill="{AMB(0.08)}" stroke="{ACC}" stroke-width="1"/>')
    s += text(x0 + 12, top + 26, 'HEALTHY', 8, 500, MUTED, mono=True, ls='0.14em')
    s += text(x1 - 12, top + 26, 'BURNING', 8, 500, ACC, 'end', mono=True, ls='0.14em')
    ay = top + h + 8
    s += f'<line x1="{x0}" y1="{ay}" x2="{x1}" y2="{ay}" stroke="{MUTED}" stroke-width="1"/>'
    for v, lbl in ticks:
        tx = scale(v)
        s += (f'<line x1="{tx:g}" y1="{ay}" x2="{tx:g}" y2="{ay+6}" stroke="{MUTED}" stroke-width="1"/>'
              + text(tx, ay + 20, lbl, 8, 400, MUTED, 'middle', mono=True))
    s += text((xa + xb) / 2, ay + 36, hold_lbl, 8, 500, ACC, 'middle', mono=True, ls='0.1em')
    return s


def s_thresholds():
    b = []
    s1 = lambda v: 96 + v * 400
    b.append(_lane(132, 'BUDGET EXHAUSTED', 'Period burn rate over the whole SLO window', s1, 0.9, 1.0,
                   [(0, '0'), (0.5, '0.5×'), (0.9, '0.9×'), (1.0, '1.0×'), (1.5, '1.5×'), (2.0, '2×')], 'HOLDS'))
    s2 = lambda v: 96 + v * 40
    b.append(_lane(300, 'BURNING FAST', 'Burn rate over 5 minutes AND over 1 hour', s2, 12.96, 14.4,
                   [(0, '0'), (5, '5×'), (10, '10×'), (12.96, '13×'), (14.4, '14.4×'), (20, '20×')], 'HOLDS'))
    # Lane 3: fifteen empty ticks.
    y = 468
    b.append(text(48, y, 'NO DATA', 8, 500, MUTED, mono=True, ls='0.14em') + text(48, y + 18, 'Consecutive checks with no burn-rate series', 12, 600, INK))
    for i in range(15):
        x = 96 + i * 44
        last = i == 14
        b.append(f'<rect x="{x}" y="{y+36}" width="36" height="28" rx="3" fill="{AMB(0.18) if last else INKA(0.05)}" stroke="{ACC if last else MUTED}" stroke-width="1"/>')
        b.append(text(x + 18, y + 54, str(i + 1), 8, 500, ACC if last else MUTED, 'middle', mono=True))
    b.append(text(96, y + 84, 'TICK 1 · EVERY 120 SECONDS', 8, 400, MUTED, mono=True))
    b.append(text(748, y + 84, 'TICK 15 · ABOUT 30 MIN · FIRES', 8, 500, ACC, 'end', mono=True))
    b.append(text(780, y + 50, 'Any tick with data resets the count.', 11, 400, MUTED))
    b.append(callout(24, 612, 'Each signal has its own state, so one SLO can be spent, burning fast and blind at once.'))
    b.append(legend(648, [('backend', 'Healthy'), ('security', 'Holds previous state'), ('focal', 'Burning'), ('dot-accent', 'Fires')]))
    return dict(slug='slo-thresholds', eyebrow='SLOs · 02 of 04 · Three signals',
      title='Three signals, three questions',
      desc='Three horizontal lanes. Budget exhausted: period burn rate on a 0 to 2 times axis, healthy below 0.9, burning above 1.0, and the state held in between. Burning fast: burn rate over 5 minutes and 1 hour on a 0 to 20 times axis, burning only when both exceed 14.4, clearing when either drops below about 13, held in between. No data: fifteen consecutive 120 second checks with no burn-rate series, which fires on the fifteenth, about 30 minutes, and resets on any tick with data.',
      lede='A single "is it red?" hides three different questions: is the budget spent, is it being spent right now, and can we see the SLO at all. Each is its own signal with its own threshold, its own clear level and its own notification.',
      body=''.join(b), W=1000, H=676, y0=76,
      cards=[('Budget exhausted', '', P('Whole-window burn rate above 1× means the window\'s error budget is spent. It lags: an outage that ended an hour ago can leave it red for days. It clears below 0.9×.')),
             ('Burning fast', 'accent', P('Both windows above 14.4× is 2% of a 30-day budget gone in an hour. Both must agree to fire, so a one-minute spike is ignored; either dropping below 13× clears it.')),
             ('No data', 'link', P('A failed Prometheus query does not count as a miss, so an outage never reads as every SLO going blind. New SLOs get about 30 minutes while Sloth loads their rules.'))])


def s_state():
    b = []
    b.append(zone(376, 100, 248, 376, 'slo_transition_state · one row per signal'))
    b += [path([(224, 284), (312, 284), (312, 172), (400, 172)]), vlab(312, 172, 284, 'SILENT SEED', side='l'),
          path([(224, 300), (336, 300), (336, 412), (400, 412)], 'accent'), vlab(336, 300, 412, 'ANNOUNCE', ACC, 'l'),
          path([(470, 204), (470, 380)]), vlab(470, 204, 380, 'ABOVE FIRE', side='l'),
          path([(530, 380), (530, 204)]), vlab(530, 380, 204, 'BELOW CLEAR'),
          path([(600, 172), (676, 172), (676, 276), (720, 276)]),
          path([(600, 412), (660, 412), (660, 308), (720, 308)], 'accent')]
    b += [node(48, 260, 176, 64, 'No row yet', 'first sighting', 'input'),
          node(400, 140, 200, 64, 'healthy', 'state = healthy'),
          node(400, 380, 200, 64, 'burning', 'state = burning', 'focal'),
          node(720, 260, 232, 64, 'Announce', 'one notification, then persist')]
    b.append(callout(24, 520, 'The first time an SLO is seen it is either announced or recorded silently. It is never ignored.'))
    b.append(legend(556, [('input', 'No stored state'), ('backend', 'Healthy'), ('focal', 'Burning'), ('accent', 'Announces'), ('muted', 'Moves silently')]))
    return dict(slug='slo-state', eyebrow='SLOs · 03 of 04 · State',
      title='One signal, two states, and a first sighting',
      desc='A state diagram for one signal of one SLO. A signal with no stored row is seeded silently as healthy, or announced when first seen burning. Within the stored row, healthy moves to burning when the value goes above the fire level, and burning moves back to healthy when it drops below the clear level. Both of those moves, and the first-seen burning case, lead to an Announce step that sends one notification and then persists the new state.',
      lede='Every signal of every SLO is one row in the plugin database. A transition is announced exactly once, and a restart no longer forgets what was already said.',
      body=''.join(b), W=1000, H=584, y0=76,
      cards=[('First sighting', '', P('An SLO first seen burning is announced; one first seen healthy is recorded silently. That is why a restart does not replay old alerts, and why a new burning SLO is never missed.')),
             ('The band', 'accent', P('Between the clear and fire levels the stored state holds. An SLO hovering at the line used to flap between burning and recovered every 10 to 30 minutes; it now stays put.')),
             ('Failure', 'link', P('The row is claimed with a compare-and-set before announcing. If the send fails the claim is undone and the next tick retries, and two overlapping ticks cannot both announce.'))])


def s_tick():
    b = []
    b += [zone(24, 100, 932, 132, 'poll · every 120 seconds'),
          zone(24, 300, 932, 196, 'transition · claim, then announce')]
    b += [path([(224, 180), (264, 180)]), path([(440, 180), (480, 180)]), path([(656, 180), (696, 180)]),
          path([(812, 212), (812, 348)], 'accent'), vlab(812, 212, 348, 'STATE CHANGED', ACC),
          path([(696, 380), (656, 380)], 'accent'), path([(480, 380), (440, 380)], 'accent'),
          path([(568, 412), (568, 452), (812, 452), (812, 412)], dashed=True), hlab(568, 812, 452, 'SEND FAILED · RESTORE')]
    b += [node(48, 148, 176, 64, 'Scheduler task', 'every 120s · global lock'),
          node(264, 148, 176, 64, 'List SLOs', 'each cluster · K8s API'),
          node(480, 148, 176, 64, 'Query Prometheus', '3 batched queries / cluster'),
          node(696, 148, 232, 64, 'Classify', 'hysteresis · 3 signals per SLO'),
          node(696, 348, 232, 64, 'Claim', 'compare-and-set in Postgres', 'focal'),
          node(480, 348, 176, 64, 'Announce', 'notifications.send'),
          node(264, 348, 176, 64, 'Tower', 'Recent Activity · SLOs')]
    b.append(callout(24, 540, 'Nothing is sent unless a stored state actually changed.'))
    b.append(legend(572, [('backend', 'Step'), ('focal', 'The dedupe point'), ('accent', 'Change path'), ('muted-dash', 'Restore on failure')]))
    return dict(slug='slo-tick', eyebrow='SLOs · 04 of 04 · One poll tick',
      title='What happens in one poll tick',
      desc='Top row, left to right: a scheduler task runs every 120 seconds under a global lock, lists the SLOs on each cluster through the Kubernetes API, queries Prometheus with three batched queries per cluster through the apiserver service proxy, and classifies each of three signals per SLO with hysteresis. When a state changed, it flows down to a Claim step, a compare-and-set in Postgres, then to Announce, which sends a Backstage notification, and then to Tower, which shows it in Recent Activity under the SLOs filter. A dashed return path from Announce back to Claim restores the claim when the send fails.',
      lede='One scheduled task, one cluster at a time. The expensive parts, listing and querying, are batched per cluster, and the part that must never repeat, announcing, is guarded by an atomic claim.',
      body=''.join(b), W=1000, H=600, y0=76,
      cards=[('Batched', '', P('Three queries per cluster: period burn, 5-minute burn and 1-hour burn, matched back to each SLO by label. Cost no longer grows with the number of SLOs.')),
             ('One runner', 'accent', P('The scheduler runs the task on one replica at a time. The claim covers the remaining case, a timed-out run still going when the next one starts.')),
             ('Who gets it', 'link', P('Everyone, by default. Set recentActivity.slo.recipients to owner to send to the app\'s catalog owner instead; an app with no owner still broadcasts.'))])
