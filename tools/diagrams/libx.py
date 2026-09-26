from lib import *
from d123 import P, UL

def chip(x,y,w,name,tag,planned=False):
    assert len(name)*6.7 + len(tag)*4.8 + 24 <= w, f'chip too wide: {name} {tag}'
    da = ' stroke-dasharray="4,3"' if planned else ''
    st = ACC if planned else MUTED
    return (f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="4" fill="rgba(27,31,36,0.05)" stroke="{st}" stroke-width="1"{da}/>'
            + text(x+8,y+16,name,12,500,INK)
            + text(x+w-8,y+15,tag,8,400,ACC if planned else MUTED,'end',mono=True))

def depnode(x,y,w,h,tag,name,chips,kind='backend'):
    fill,stroke,dash = KINDS[kind]
    d = f' stroke-dasharray="{dash}"' if dash else ''
    tw = up4(len(tag)*5.6+8)
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER}"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>'
    s += (f'<rect x="{x+8}" y="{y+8}" width="{tw}" height="12" rx="2" fill="transparent" stroke="{stroke}" stroke-opacity="0.5" stroke-width="0.8"/>'
          f'<text x="{x+8+tw/2}" y="{y+17}" fill="{stroke}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing="0.08em">{esc(tag.upper())}</text>')
    s += text(x+8+tw+8,y+19,name,12,600,INK)
    cy = y+32
    for (cn,ct,pl) in chips:
        s += chip(x+8,cy,w-16,cn,ct,pl); cy += 32
    return s

def C3(principle, changes, verify, vt='Verify live'):
    return [('Principle honored','', principle), ('What changes','accent', changes), (vt,'link', verify)]
