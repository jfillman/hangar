"""Kit for the Overview set (docs/overview/diagrams): high-level Hangar pictures with optional motion.

Same Hangar profile as lib.py, but colours are CSS classes on custom properties, so light and dark
need no per-colour remapping, and nodes can carry the product dial marks and link to site pages.
Motion follows the diagram-design skill's animation.md; motion_controller.js is the skill's
template-motion.html controller, copied verbatim (its verifier rejects any edit).
"""
import html, math, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = ''  # links are root-relative site paths; they open in the top window when the page is embedded

def esc(s): return html.escape(s, quote=True)
def up4(v): return int(math.ceil(v / 4.0) * 4)

# ---------------------------------------------------------------- tokens
SITE_LIGHT = dict(paper='#f2efe9', paper2='#e8e3da', card='#ffffff', ink='#1b1f24', muted='#5b6570', soft='#838b93',
                  accent='#b9791f', link='#2e7ba6', rgb='27,31,36', acc_rgb='185,121,31', link_rgb='46,123,166', mut_rgb='91,101,112')
SITE_DARK = dict(paper='#131619', paper2='#1b1f24', card='#1c2127', ink='#e8e4dc', muted='#a1aab3', soft='#7f8891',
                 accent='#e8a33d', link='#6fb2d9', rgb='232,228,220', acc_rgb='232,163,61', link_rgb='111,178,217', mut_rgb='161,170,179')
def vars_(t, dark=False):
    k = 1.3 if dark else 1.0
    return (f"--paper:{t['paper']};--paper-2:{t['paper2']};--card:{t['card']};--ink:{t['ink']};--muted:{t['muted']};"
            f"--soft:{t['soft']};--accent:{t['accent']};--link:{t['link']};"
            f"--rule:rgba({t['rgb']},.12);--zone:rgba({t['rgb']},.02);--zone-line:rgba({t['rgb']},.16);"
            f"--store:rgba({t['rgb']},.05);--ext:rgba({t['rgb']},.03);--ext-line:rgba({t['rgb']},.30);"
            f"--acc-tint:rgba({t['acc_rgb']},{.08*k:.3f});--acc-soft:rgba({t['acc_rgb']},{.05*k:.3f});"
            f"--link-tint:rgba({t['link_rgb']},{.10*k:.3f});--input:rgba({t['mut_rgb']},.10)")

SITE_FONTS = "--font-sans:'Geist',system-ui,sans-serif;--font-serif:'Instrument Serif',serif;--font-mono:'Geist Mono',ui-monospace,monospace;--h1-weight:400;--h1-ls:-.02em;--r:6px"
THEME_CSS = f"""
:root{{{vars_(SITE_LIGHT)};{SITE_FONTS};color-scheme:light}}
:root[data-theme=dark]{{{vars_(SITE_DARK, True)};color-scheme:dark}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{vars_(SITE_DARK, True)};color-scheme:dark}}}}
"""

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{--motion-fast:160ms;--motion-step:480ms;--motion-hold:720ms;--motion-total:3600ms;--motion-ease:cubic-bezier(.2,.8,.2,1)}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font-sans);padding:2.25rem 1rem 2rem}
.frame{max-width:1040px;margin:0 auto}
.eyebrow{margin:0 0 .5rem;color:var(--muted);font:500 11px/1.4 var(--font-mono);letter-spacing:.18em;text-transform:uppercase}
h1{margin:0 0 .5rem;font-family:var(--font-serif);font-weight:var(--h1-weight);letter-spacing:var(--h1-ls);font-size:clamp(1.5rem,2.4vw + .75rem,2.1rem);line-height:1.15}
.lede{margin:0 0 1rem;color:var(--muted);font-size:.92rem;line-height:1.5;max-width:72ch}
.bar{display:flex;flex-wrap:wrap;gap:.4rem 1.4rem;align-items:center;margin:0 0 1rem;padding:.55rem .8rem;border:1px dashed var(--zone-line);border-radius:var(--r);font:500 11px/1.4 var(--font-mono);color:var(--muted)}
.bar fieldset{border:0;margin:0;padding:0;display:flex;gap:.6rem;align-items:center}
.bar legend{float:left;margin-right:.4rem;color:var(--soft);letter-spacing:.12em;text-transform:uppercase}
.bar label{display:inline-flex;gap:.25rem;align-items:center;cursor:pointer}
.bar input{accent-color:var(--accent)}
.bar .note{margin-left:auto;color:var(--soft)}
[data-motion-root]{max-width:100%;min-width:0}
.diagram-container{width:100%;overflow-x:auto}
.diagram-container>svg{display:block;width:100%}
.hint{margin:.5rem 0 0;color:var(--soft);font:400 11px/1.4 var(--font-mono)}

.foot{font-family:var(--font-mono);font-size:.62rem;letter-spacing:.06em;color:var(--soft);border-top:1px solid var(--rule);margin-top:1.25rem;padding-top:.6rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.notes{display:grid;grid-template-columns:1.15fr 1fr .95fr;gap:.75rem;margin-top:1.5rem}
.notes>div{background:var(--card);border:1px solid var(--rule);border-radius:var(--r);padding:.9rem 1rem}
.notes h2{margin:0 0 .4rem;color:var(--muted);font:500 10px/1.4 var(--font-mono);letter-spacing:.16em;text-transform:uppercase}
.notes p,.notes li{margin:0 0 .4rem;font-size:.82rem;line-height:1.5}
.notes ul{margin:0;padding-left:1rem}
@media (max-width:860px){.notes{grid-template-columns:1fr}}
a{color:var(--link)}

/* diagram skin */
.bg{fill:var(--paper)}
.zone{fill:var(--zone);stroke:var(--zone-line);stroke-width:.8}
.mask{fill:var(--paper)}
.zt{fill:var(--muted);font:500 8px var(--font-mono);letter-spacing:.14em}
.k{stroke-width:1}
.k-backend{fill:var(--card);stroke:var(--ink)}
.k-focal{fill:var(--acc-tint);stroke:var(--accent)}
.k-store{fill:var(--store);stroke:var(--muted)}
.k-external{fill:var(--ext);stroke:var(--ext-line)}
.k-input{fill:var(--input);stroke:var(--soft)}
.k-propose{fill:var(--link-tint);stroke:var(--link)}
.k-optional{fill:var(--zone);stroke:var(--zone-line);stroke-dasharray:4 3}
.nm{fill:var(--ink);font:600 12px var(--font-sans)}
.nm-l{fill:var(--ink);font:600 14px var(--font-sans)}
.sub{fill:var(--muted);font:400 8px var(--font-mono)}
.sub-l{fill:var(--muted);font:400 9px var(--font-mono)}
.why{fill:var(--muted);font:400 11px var(--font-sans)}
.tagb{fill:none;stroke-width:.8;stroke-opacity:.55}
.tagt{font:500 8px var(--font-mono);letter-spacing:.08em}
.t-ink{stroke:var(--ink);fill:var(--muted)} .t-acc{stroke:var(--accent);fill:var(--accent)} .t-link{stroke:var(--link);fill:var(--link)} .t-soft{stroke:var(--soft);fill:var(--soft)}
text.t-ink,text.t-acc,text.t-link,text.t-soft{stroke:none}
rect.tagb{fill:none}
.lbl{fill:var(--soft);font:400 8px var(--font-mono);letter-spacing:.06em}
.lbl-acc{fill:var(--accent)} .lbl-link{fill:var(--link)}
.a{fill:none;stroke:var(--muted);stroke-width:1.2}
.a.acc{stroke:var(--accent)} .a.lnk{stroke:var(--link)} .a.dash{stroke-dasharray:5 4}
.a.thin{stroke-width:1}
.mk{fill:var(--muted)} .mk-acc{fill:var(--accent)} .mk-lnk{fill:var(--link)}
.callout{fill:var(--muted);font:italic 400 15px var(--font-serif)}
.rule{stroke:var(--rule);stroke-width:.8}
.badge{fill:var(--paper);stroke:var(--accent);stroke-width:1}
.badget{fill:var(--accent);font:600 8px var(--font-mono)}
.go{fill:var(--soft);font:400 9px var(--font-mono)}
svg a{cursor:pointer}
svg a:hover .k,svg a:focus-visible .k{stroke:var(--accent);stroke-width:1.6}
svg a:hover .go,svg a:focus-visible .go{fill:var(--accent)}
svg a:focus{outline:none}
svg a:focus-visible .k{stroke-width:2.4}

/* motion (from template-motion.html) */
.motion-ready [data-motion-item]{opacity:.12;transform:translateY(8px);transform-box:fill-box;transform-origin:center;
  transition:opacity var(--motion-step) var(--motion-ease),transform var(--motion-step) var(--motion-ease)}
.motion-ready [data-motion-item].is-visible,.motion-ready[data-frame="end"] [data-motion-item],.motion-ready[data-frame="static"] [data-motion-item]{opacity:1;transform:none}
.draw-path{fill:none;stroke:var(--accent);stroke-width:3;stroke-dasharray:1;stroke-dashoffset:1;pointer-events:none;opacity:0}
.motion-ready .draw-path.is-visible{opacity:1;animation:draw-path var(--motion-step) linear forwards}
.motion-ready[data-frame="end"] .draw-path,.motion-ready[data-frame="static"] .draw-path{opacity:0;animation:none}
@keyframes draw-path{to{stroke-dashoffset:0}}
[data-motion-controls]{display:none;align-items:center;flex-wrap:wrap;gap:8px;margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)}
.motion-ready [data-motion-controls]{display:flex}
[data-motion-controls][hidden]{display:none !important}
[data-motion-controls] button{min-width:44px;min-height:44px;padding:8px 12px;border:1px solid var(--muted);border-radius:4px;color:var(--ink);background:var(--paper);font:600 12px/1 var(--font-sans);cursor:pointer}
[data-motion-controls] button:hover{border-color:var(--accent)}
[data-motion-controls] button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
[data-motion-controls] button:disabled{cursor:not-allowed;opacity:.45}
.keyboard-help{color:var(--soft);font:400 11px/1.4 var(--font-mono)}
[data-motion-status-visible]{margin-left:auto;color:var(--muted);font:500 12px/1.4 var(--font-mono)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
noscript p{margin:12px 0 0;color:var(--muted);font:500 12px/1.4 var(--font-mono)}
html[data-motion="static"] [data-motion-controls],html[data-motion="static"] [data-motion-decorative]{display:none !important}
html[data-motion="static"] [data-motion-item]{opacity:1 !important;transform:none !important;animation:none !important;transition:none !important}
html[data-motion="step"] [data-motion-controls],html[data-motion="step"] [data-motion-decorative]{display:none !important}
html[data-motion="step"] [data-motion-item]{animation:none !important;transition:none !important}
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.001ms !important;animation-iteration-count:1 !important;scroll-behavior:auto !important;transition-duration:.001ms !important}
  [data-motion-item]{opacity:1 !important;transform:none !important}
  [data-motion-decorative]{display:none !important}
  [data-motion-controls]{display:none !important}
}
@media print{
  .diagram-container{overflow-x:visible} .diagram-container>svg{min-width:0 !important}
  [data-motion-controls],[data-motion-decorative]{display:none !important}
  [data-motion-item]{opacity:1 !important;transform:none !important;animation:none !important;transition:none !important}
}
"""

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600'
         '&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">')

def controller():
    return f'<script data-diagram-controls>{(HERE / "motion_controller.js").read_text()}</script>'

def controls_html(count):
    return f'''<div data-motion-controls role="group" aria-label="Diagram playback controls">
      <button type="button" data-motion-action="prev">Previous</button>
      <button type="button" data-motion-action="play" aria-pressed="false">Play</button>
      <button type="button" data-motion-action="pause" aria-pressed="true">Pause</button>
      <button type="button" data-motion-action="next">Next</button>
      <button type="button" data-motion-action="replay">Replay</button>
      <span class="keyboard-help">←/→ step · Space play/pause · R replay · Home/End jump</span>
      <span data-motion-status-visible aria-hidden="true">Step <span data-motion-step-label>{count}</span> of {count}</span>
    </div>
    <p class="sr-only" data-motion-status role="status" aria-live="polite" aria-atomic="true"></p>
    <noscript><p>Animation controls require JavaScript. The complete final diagram is shown above.</p></noscript>'''

# ---------------------------------------------------------------- primitives
def defs(slug):
    m = lambda i, c: f'<marker id="{slug}-{i}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon class="{c}" points="0 0, 8 3, 0 6"/></marker>'
    return m('arrow', 'mk') + m('arrow-acc', 'mk-acc') + m('arrow-lnk', 'mk-lnk')

def rounded(points, r=8):
    pts = list(points)
    for i in range(len(pts) - 1):
        assert pts[i][0] == pts[i + 1][0] or pts[i][1] == pts[i + 1][1], f'diagonal {pts[i]}->{pts[i+1]}'
    d = f'M{pts[0][0]},{pts[0][1]}'
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        l1 = abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]); l2 = abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
        rr = min(r, l1 / 2, l2 / 2)
        sg = lambda a, b: (a > b) - (a < b)
        s1 = (sg(p1[0], p0[0]), sg(p1[1], p0[1])); s2 = (sg(p2[0], p1[0]), sg(p2[1], p1[1]))
        a = (p1[0] - s1[0] * rr, p1[1] - s1[1] * rr); b = (p1[0] + s2[0] * rr, p1[1] + s2[1] * rr)
        d += f' L{a[0]:g},{a[1]:g} Q{p1[0]},{p1[1]} {b[0]:g},{b[1]:g}'
    return d + f' L{pts[-1][0]},{pts[-1][1]}'

class Fig:
    def __init__(self, slug):
        self.slug = slug
        self.out = []
    def add(self, s): self.out.append(s); return s
    def svg(self): return '\n'.join(self.out)

    def arrow(self, pts, color='muted', dashed=False, marker=True, thin=False):
        cls = 'a' + {'muted': '', 'acc': ' acc', 'lnk': ' lnk'}[color] + (' dash' if dashed else '') + (' thin' if thin else '')
        mk = {'muted': 'arrow', 'acc': 'arrow-acc', 'lnk': 'arrow-lnk'}[color]
        m = f' marker-end="url(#{self.slug}-{mk})"' if marker else ''
        return self.add(f'<path class="{cls}" d="{rounded(pts)}"{m}/>')

def label(cx, top, text, tone=''):
    w = up4(len(text) * 5.6 + 8)
    cls = 'lbl' + (f' lbl-{tone}' if tone else '')
    return (f'<rect class="mask" x="{cx - w / 2:g}" y="{top}" width="{w}" height="12" rx="2"/>'
            f'<text class="{cls}" x="{cx:g}" y="{top + 9}" text-anchor="middle">{esc(text.upper())}</text>')

def hlab(x1, x2, y, text, tone='', below=False):
    return label((x1 + x2) / 2, y + 6 if below else y - 18, text, tone)

def vlab(x, y1, y2, text, tone='', side='r'):
    w = up4(len(text) * 5.6 + 8)
    cx = x + 8 + w / 2 if side == 'r' else x - 8 - w / 2
    return label(cx, (y1 + y2) / 2 - 6, text, tone)

def zone(x, y, w, h, text, align='left', href=None, icon=None):
    lw = up4(len(text) * 5.6 + 16) + (22 if icon else 0)
    lx = {'left': x + 12, 'right': x + w - 12 - lw, 'center': x + (w - lw) // 2}[align]
    ty = y + 4 if not icon else y - 4
    lab = f'<rect class="mask" x="{lx}" y="{ty}" width="{lw}" height="{12 if not icon else 20}" rx="2"/>'
    if icon:
        lab += icon_svg(icon, lx + 2, y - 4, 20)
    lab += f'<text class="zt" x="{lx + (22 if icon else 0) + (lw - (22 if icon else 0)) / 2:g}" y="{y + (13 if not icon else 9)}" text-anchor="middle">{esc(text.upper())}</text>'
    if href:
        lab = f'<a href="{SITE}{href}" target="_top" aria-label="{esc(text)}: open its page">{lab}</a>'
    return f'<rect class="zone" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>' + lab

TAGTONE = {'backend': 'ink', 'focal': 'acc', 'propose': 'link', 'external': 'soft', 'input': 'soft', 'store': 'ink', 'optional': 'soft'}

def node(x, y, w, h, name, sub=None, kind='backend', tag=None, href=None, big=False, go=True, icon=None, isz=28):
    nmc, subc, cw, sw = ('nm-l', 'sub-l', 7.8, 5.6) if big else ('nm', 'sub', 6.7, 5.0)
    tx, tw_ = (x + isz + 16, w - isz - 16) if icon else (x, w)
    assert len(name) * cw <= tw_ - 12, f'name too wide: {name}'
    if sub: assert len(sub) * sw <= tw_ - 10, f'sub too wide: {sub} ({len(sub)*sw:.0f} > {tw_-10})'
    s = f'<rect class="mask" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
    s += f'<rect class="k k-{kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
    cx = tx + tw_ / 2 - (4 if icon else 0)
    body_top = y
    if tag:
        tw = up4(len(tag) * 5.6 + 8); tone = TAGTONE[kind]
        s += (f'<rect class="tagb t-{tone}" x="{x + 8}" y="{y + 6}" width="{tw}" height="12" rx="2"/>'
              f'<text class="tagt t-{tone}" x="{x + 8 + tw / 2:g}" y="{y + 15}" text-anchor="middle">{esc(tag.upper())}</text>')
        body_top = y + 18
    mid = body_top + (y + h - body_top) / 2
    ny = mid + (-2 if sub else 4)
    if icon:
        s += icon_svg(icon, x + 8, mid - isz / 2, isz)
    s += f'<text class="{nmc}" x="{cx:g}" y="{ny:g}" text-anchor="middle">{esc(name)}</text>'
    if sub:
        s += f'<text class="{subc}" x="{cx:g}" y="{ny + (16 if big else 14):g}" text-anchor="middle">{esc(sub)}</text>'
    if href:
        if go: s += f'<text class="go" x="{x + w - 8}" y="{y + 13}" text-anchor="end" aria-hidden="true">↗</text>'
        s = f'<a href="{SITE}{href}" target="_top" aria-label="{esc(name)}: open its page">{s}</a>'
    return s

def badge(cx, cy, n):
    return (f'<circle class="badge" cx="{cx}" cy="{cy}" r="8"/>'
            f'<text class="badget" x="{cx}" y="{cy + 3}" text-anchor="middle">{n}</text>')

def item(step, aria, body, decorative=False):
    if decorative:
        return f'<g data-motion-item data-step="{step}" data-motion-decorative aria-hidden="true" focusable="false">{body}</g>'
    return f'<g data-motion-item data-step="{step}" aria-label="{esc(aria)}">{body}</g>'

def drawpath(step, pts):
    return (f'<path data-motion-item data-step="{step}" data-motion-decorative aria-hidden="true" focusable="false" '
            f'pathLength="1" class="draw-path" d="{rounded(pts)}"/>')

KIND_LEG = {'input': 'k-input', 'backend': 'k-backend', 'focal': 'k-focal', 'external': 'k-external', 'propose': 'k-propose', 'store': 'k-store', 'optional': 'k-optional'}

def legend(y, items, W=1000):
    s = f'<line class="rule" x1="24" y1="{y - 12}" x2="{W - 24}" y2="{y - 12}"/>'
    s += f'<text class="zt" x="24" y="{y + 9}">LEGEND</text>'
    x = 96
    for kind, text in items:
        if kind in KIND_LEG:
            s += f'<rect class="k {KIND_LEG[kind]}" x="{x}" y="{y}" width="16" height="12" rx="3"/>'; adv = 24
        else:
            col, dash = kind.split('-') if '-' in kind else (kind, '')
            cls = 'a' + {'muted': '', 'acc': ' acc', 'lnk': ' lnk'}[col] + (' dash' if dash else '')
            s += f'<line class="{cls}" x1="{x}" y1="{y + 6}" x2="{x + 20}" y2="{y + 6}"/>'; adv = 28
        s += f'<text class="sub" x="{x + adv}" y="{y + 9}">{esc(text)}</text>'
        x += adv + int(len(text) * 5.0) + 20
    assert x <= W, f'legend too wide: {x}'
    return s

# product dial marks from hangar/brand/marks, drawn inline
MARKS = HERE.parent.parent / 'brand/marks'
def icon_svg(key, x, y, size):
    src = (MARKS / f'{key}-tile.svg').read_text()
    inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', src.strip())
    return f'<svg x="{x:g}" y="{y:g}" width="{size}" height="{size}" viewBox="0 0 96 96" aria-hidden="true" focusable="false">{inner}</svg>'

# ---------------------------------------------------------------- page
def page(*, n, slug, eyebrow, title, lede, desc, W, H, body, mode, steps, notes, hint, extra_css='', extra_bar='', after_svg='', svg_min=None):
    controlled = mode in ('reveal', 'step')
    ctl = controls_html(steps) if controlled else ''
    script = controller() if controlled else ''
    svg_min = svg_min or W
    notes_html = ''.join(f'<div><h2>{esc(h)}</h2>{b}</div>' for h, b in notes)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{FONTS}
<style>{THEME_CSS}{BASE_CSS}
:root{{--motion-total:{steps * 720}ms}}
.diagram-container>svg{{min-width:{svg_min}px}}
{extra_css}</style>
</head>
<body>
<div class="frame">
<main data-motion-root data-motion-mode="{mode}" data-step-count="{steps}" data-step-current="{steps}" data-frame="static" data-static-frame="complete">
  <p class="eyebrow">{esc(eyebrow)}</p>
  <h1>{esc(title)}</h1>
  <p class="lede">{lede}</p>
  <div class="diagram-container">
    <svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
      <title id="{slug}-title">{esc(title)}</title>
      <desc id="{slug}-desc">{esc(desc)}</desc>
      <defs>{defs(slug)}</defs>
      <rect class="bg" width="{W}" height="{H}"/>
{body}
    </svg>
  </div>
  {after_svg}
  <p class="hint">{hint}</p>
  {ctl}
</main>
<div class="foot"><span>Hangar · Overview</span><span>Click any box to open its page</span></div>
</div>
{script}
</body>
</html>
'''
