"""Page shell for the Library: reviews, reports and specs as standalone illustrated pages.

Every page shares one stylesheet (report.css, the profile the Sep 27, 2026 architecture review
set) and draws its figures with the diagram generator's primitives (tools/diagrams/lib.py), so a
report and a diagram look like they came from the same hand. Standard library only.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'diagrams'))
import lib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, 'report.css')).read()

EXTRA = """
.fig{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:16px;display:flex;flex-direction:column;gap:10px}
.fig .scroll{overflow-x:auto}
.fig svg{display:block;width:100%;min-width:600px;max-width:760px;height:auto;margin:0 auto}
.fig figcaption{font-size:.85rem;color:var(--ink-2)}
.fig figcaption b{font-family:var(--mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;font-weight:500;color:var(--amber);margin-right:6px}
.stamp{display:inline-flex;align-self:flex-start;font-family:var(--mono);font-size:.8rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;padding:4px 10px;border-radius:3px}
.verdict.ok{border-top-color:var(--ok)} .verdict.ok .stamp{color:var(--ok);background:var(--ok-bg)}
.verdict.info{border-top-color:var(--accent)} .verdict.info .stamp{color:var(--accent);background:var(--accent-soft)}
.verdict.bad{border-top-color:var(--bad)} .verdict.bad .stamp{color:var(--bad);background:var(--bad-bg)}
.track{display:flex;flex-direction:column;background:var(--paper);border:1px solid var(--rule);border-radius:6px}
.track .row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 16px;padding:14px 16px;border-bottom:1px solid var(--rule);align-items:baseline}
.track .row:last-child{border-bottom:0}
.track .row h3{font-family:var(--sans);font-size:1rem;font-weight:600}
.track .row p{grid-column:1/-1;font-size:.92rem;color:var(--ink-2)}
.track .row .chip{justify-self:end}
.quote{border-left:3px solid var(--amber);padding:4px 0 4px 16px;font-family:var(--serif);font-size:1.35rem;line-height:1.3}
p.prose{display:block}\n@media (max-width:560px){.track .row{grid-template-columns:1fr}.track .row .chip{justify-self:start}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
         '&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">')

MONTHS = 'January February March April May June July August September October November December'.split()


def long_date(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return f'{MONTHS[m - 1]} {d}, {y}'


def short_date(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return f'{MONTHS[m - 1][:3]} {d}, {y}'


def esc(s):
    return html.escape(s, quote=True)


def chip(text, tone='info'):
    return f'<span class="chip c-{tone}">{esc(text)}</span>'


# Status colours a figure may use beyond lib's palette (report.css --ok and --bad), with dark values.
GOOD, BAD = '#2e7d4f', '#a3352b'
STATUS_DARK = {GOOD: '#5fae84', BAD: '#ec8d82'}


def tick(x, y, color=GOOD):
    """A small check mark: the guarantee holds."""
    return f'<path d="M{x - 4},{y} L{x - 1},{y + 3} L{x + 4},{y - 3}" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'


def _svg_dark(svg):
    """Dark-theme rules for the colours an SVG uses (the attribute half of lib.dark_css)."""
    rules = []
    for attr, val in sorted(set(re.findall(r'\b(fill|stroke)="([^"]+)"', svg))):
        d = None if val == lib.PAPER else (STATUS_DARK.get(val) or lib.dark_colour(val))
        if d:
            rules.append(f'svg [{attr}="{val}"]{{{attr}:{d}}}')
    if not rules:
        return ''
    return ('@media (prefers-color-scheme:dark){'
            + ''.join(f':root:not([data-theme=light]) {r}' for r in rules) + '}\n'
            + ''.join(f':root[data-theme=dark] {r}' for r in rules) + '\n')


class Page:
    def __init__(self, slug, kind, eyebrow, title, description, date, meta=(), lede=''):
        self.slug, self.kind, self.eyebrow, self.title = slug, kind, eyebrow, title
        self.description, self.date, self.meta, self.lede = description, date, meta, lede
        self.parts, self.svgs, self.n = [], [], 0

    def add(self, s):
        self.parts.append(s)
        return self

    def fig(self, body, W, H, title, desc, caption=''):
        """One figure drawn with tools/diagrams/lib.py on the paper colour, light and dark."""
        self.n += 1
        fid = f'{self.slug}-f{self.n}'
        svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
               f'aria-labelledby="{fid}-t {fid}-d"><title id="{fid}-t">{esc(title)}</title>'
               f'<desc id="{fid}-d">{esc(desc)}</desc><defs>{lib.defs()}</defs>'
               f'<rect width="100%" height="100%" fill="{lib.PAPER}"/>{body}</svg>')
        self.svgs.append(svg)
        cap = f'<figcaption><b>Figure {self.n}</b>{caption}</figcaption>' if caption else ''
        return f'<figure class="fig"><div class="scroll">{svg}</div>{cap}</figure>'

    def html(self):
        # Figures sit on the page's panel colour (var(--paper)), so the diagram paper maps to it.
        dark = _svg_dark(''.join(self.svgs))
        meta = ''.join(f'<span><b>{esc(k)}</b> {v}</span>' for k, v in self.meta)
        lede = f'<p class="prose" style="color:var(--ink-2)">{self.lede}</p>' if self.lede else ''
        # Site links open in the top window, since the site shows these pages in a frame.
        return self._page(dark, meta, lede).replace('<a href="https://hangarplatform.dev', '<a target="_top" href="https://hangarplatform.dev')

    def _page(self, dark, meta, lede):
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(self.title)}</title>
<meta name="description" content="{esc(self.description)}">
{FONTS}
<style>
{CSS}{EXTRA}
svg rect[fill="{lib.PAPER}"]{{fill:var(--paper)}}
{dark}</style>
</head>
<body>
<div class="wrap">

<header>
  <span class="eyebrow">{esc(self.eyebrow)}</span>
  <h1>{esc(self.title)}</h1>
  {lede}
  <div class="meta"><span><b>{esc(self.kind)}</b> {long_date(self.date)}</span>{meta}</div>
</header>

{''.join(self.parts)}

<footer>{esc(self.title)} · {long_date(self.date)} · Part of the Hangar library at hangarplatform.dev/library/</footer>

</div>
</body>
</html>
"""

    def write(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f'{self.date}-{self.slug}.html')
        with open(path, 'w') as f:
            f.write(self.html())
        return path
