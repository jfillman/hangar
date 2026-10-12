"""The see / change / own instrument panel the Tower field reports score each pillar on."""
from report import GOOD, BAD
import lib
from lib import text

FILL = {'full': 1.0, 'most': 0.78, 'half': 0.46, 'none': 0.06}
TONE = {'full': GOOD, 'most': GOOD, 'half': lib.ACC, 'none': BAD}
VERDICT = {'Strong': GOOD, 'Partial': lib.ACC, 'Gap': BAD}
COLS = ('SEE', 'CHANGE', 'OWN')
X0, BW, GAP = 300, 128, 18


def panel(rows, W=760, top=24, rh=56):
    """rows: (name, replaces, verdict, (see, change, own), then) where then is None or a
    (see, change, own) tuple marking where the pillar stood before, drawn as a tick on each bar."""
    s = ''
    for j, c in enumerate(COLS):
        s += text(X0 + j * (BW + GAP), top + 8, c, 8, 500, lib.MUTED, mono=True, ls='0.14em')
    for i, (name, sub, verdict, levels, then) in enumerate(rows):
        y = top + 22 + i * rh
        s += f'<line x1="24" y1="{y}" x2="{W - 24}" y2="{y}" stroke="{lib.RULE}" stroke-width="0.8"/>'
        s += text(24, y + 22, name, 12, 600, lib.INK)
        s += text(24, y + 38, sub, 8, 400, lib.MUTED, mono=True)
        s += text(X0 - 16, y + 22, verdict.upper(), 8, 600, VERDICT[verdict], anchor='end', mono=True, ls='0.08em')
        for j, lv in enumerate(levels):
            x = X0 + j * (BW + GAP)
            s += f'<rect x="{x}" y="{y + 16}" width="{BW}" height="8" rx="4" fill="rgba(27,31,36,0.05)" stroke="rgba(27,31,36,0.16)" stroke-width="0.8"/>'
            s += f'<rect x="{x}" y="{y + 16}" width="{BW * FILL[lv]:g}" height="8" rx="4" fill="{TONE[lv]}"/>'
            if then:
                tx = x + BW * FILL[then[j]]
                tx = min(tx, x + BW - 1)
                s += f'<line x1="{tx:g}" y1="{y + 11}" x2="{tx:g}" y2="{y + 29}" stroke="{lib.INK}" stroke-width="1.4"/>'
    return s, top + 22 + len(rows) * rh
