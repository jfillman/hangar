"""Site feedback review (Sep 27, 2026): what two AI reviews said about hangarplatform.dev, and what I did."""
from report import Page, chip
import lib
from lib import node, path, zone, text, callout

P = Page(
    'site-feedback-review', 'Review', 'hangarplatform.dev · Review · Site feedback',
    'What two reviews said about this site, and what I did about it',
    'Grok and ChatGPT reviewed hangarplatform.dev a day after launch. Eleven suggestions, checked against the live site, with what I agreed with, what I declined, and where each one landed.',
    '2026-09-27',
    meta=[('Reviewers', 'Grok and ChatGPT, checked by Claude against the live site and repo'),
          ('Scope', 'the website only, not Hangar\'s architecture')],
    lede=('The day the site went live I asked Grok and ChatGPT what they thought of it. Both were kind, and both made '
          'the same three criticisms: it\'s dense, it\'s written for peers more than for hiring managers, and it tells '
          'more than it shows. Claude checked every point against the live site and the repo. Here\'s what I did with them.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">Done · eight changes live by Sep 28, 2026</span>
  <h2>Show more, explain the jargon, and stay honest about what's built.</h2>
  <p>I took eight of the eleven suggestions, kept one as optional and declined two. The ones I declined would have made the site weaker for the people it's written for, or less honest.</p>
</div>
""")

# Figure: eleven suggestions, sorted into what happened to them.
W, H = 760, 236
b = node(24, 92, 136, 56, 'Two reviews', '+ one found checking', 'input')
cols = [(220, 'Do first', '4 items', 'focal'), (352, 'Next', '4 items', 'focal'),
        (484, 'Optional', '1 item', 'optional'), (616, 'Declined', '2 items', 'external')]
for x, name, sub, kind in cols:
    b += node(x, 92, 120, 56, name, sub, kind)
b += path([(160, 120), (216, 120)], 'link')
b += zone(212, 24, 268, 40, 'Live by Sep 28, 2026', center=True)
b += path([(280, 64), (280, 88)], 'accent') + path([(412, 64), (412, 88)], 'accent')
b += callout(220, 192, 'Eight shipped in a day.')
b += callout(484, 192, 'Three I kept to myself.')
fig = P.fig(b, W, H, 'Eleven suggestions, sorted',
            'Two AI reviews plus one issue found while checking produced eleven items: four to do first and four next, all live by Sep 28, 2026; one optional; two declined.',
            'Eleven items, four piles. Everything in Do first and Next shipped the next day.')

ROWS = [
    ('Do first', [
        ('1', 'Take the home-lab cluster names out of the published diagrams', 'Found while checking',
         'Two Autopilot diagrams and the brand page still named the lab clusters. The fix went into the generators, not the built site, and they now say "dev cluster" and "prod cluster".', ('Done', 'ok')),
        ('2', 'Add a tech-stack view', 'ChatGPT, Grok',
         'ChatGPT had to list the tools itself and draw its own stack diagram, which told me a page was missing. Three mockups later, it became <a href="https://hangarplatform.dev/stack/">the stack as decisions</a>: every tool, what I chose it over, and why.', ('Done · /stack/', 'ok')),
        ('3', 'Show the running product on the home page', 'ChatGPT',
         'The Tower walkthrough was hidden behind a card on /tower/. It now plays just under the hero, so "is this real?" gets an answer in ten seconds.', ('Done · home page', 'ok')),
        ('4', 'Bring the track record onto the home page', 'ChatGPT, partly agreed',
         'A short strip of facts from the About page went on the home page. I declined the other half, publishing DORA or MTTR numbers from past jobs: I don\'t have numbers I can share, and estimates would break the honesty the site is built on.', ('Done, in part', 'ok')),
    ]),
    ('Next', [
        ('5', 'Record a "zero to running" walkthrough', 'ChatGPT',
         'The most convincing thing I could add. Two services went from nothing to production on camera, one in the terminal and one in Tower, and the run found four real platform bugs. See <a href="https://hangarplatform.dev/run/">Zero to running</a>.', ('Done · /run/', 'ok')),
        ('6', 'Write about what the stack costs', 'ChatGPT, Grok',
         'The sharpest critique in either review, and exactly what the site is for. It became the first Architecture essay, <a href="https://hangarplatform.dev/architecture/cost-of-the-platform/">what Hangar costs, and where Crossplane stops</a>.', ('Done · essay', 'ok')),
        ('7', 'Explain the jargon in plain words', 'ChatGPT, partly agreed',
         'I didn\'t simplify the pages, because the depth is the point. Instead there\'s <a href="https://hangarplatform.dev/glossary/">a glossary</a> and a short explainer on the first mention of each term.', ('Done · /glossary/', 'ok')),
        ('8', 'Mark Autopilot\'s maturity on the product cards', 'ChatGPT, partly agreed',
         'Every product card now carries a status, so Autopilot reads "Early: core built, runtime proposed" instead of looking as finished as Glidepath.', ('Done · badges', 'ok')),
    ]),
    ('Optional, or declined', [
        ('9', 'A 30-second path for first-time visitors', 'Grok',
         '"Start here" already did this, just too far down. Fine to move up, not worth a new section.', ('Optional', 'info')),
        ('10', 'Move more of the deep content onto the site', 'Grok',
         'Mostly done already: <a href="https://hangarplatform.dev/docs/">the docs</a> sync from every repo. ADRs stay linked to GitHub, because the source of truth belongs next to the code.', ('Declined', 'warn')),
        ('11', 'Rewrite the site for executives', 'ChatGPT',
         'The site is here to show the work and share opinions, and peers are the people who can judge both. Items 3 and 4 give a hiring manager what they need in ten seconds.', ('Declined', 'warn')),
    ]),
]

body = f'<section><h2>Eleven suggestions, sorted</h2>{fig}</section>'
for heading, items in ROWS:
    rows = ''
    for n, title, who, p, (status, tone) in items:
        rows += (f'<div class="row"><h3>{n}. {title}</h3>{chip(status, tone)}'
                 f'<p><span class="eyebrow" style="color:var(--ink-2)">{who}</span><br>{p}</p></div>')
    body += f'<section><h2>{heading}</h2><div class="track">{rows}</div></section>'

body += """
<section>
  <h2>What the reviews got wrong</h2>
  <ul class="plain">
    <li>ChatGPT listed Airframe XRDs that don't exist, such as <code>OAuthServer</code> and <code>Queue</code>. The real ones are applications (Node, Spring Boot, Go, Python), ApplicationEnvironment, PostgreSQL, Redis, RabbitMQ, InfraService, SecretStore, SLO, RolloutWatch and TektonCICD.</li>
    <li>ChatGPT's diagrams showed dev, stage and prod clusters. Hangar runs two: a dev cluster and a prod cluster.</li>
    <li>Neither review is something to quote as a testimonial. If I ever want those, they'll come from people.</li>
  </ul>
</section>
"""
P.add(body)
