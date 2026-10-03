# Diagram generator

Builds the 37 pages in `docs/autopilot/diagrams/` (plan 8, autopilot 19, reference 10) and the 7 in
`docs/glidepath/diagrams/` with the
diagram-design skill's grammar and the Hangar profile (amber, sky, warm bone, Instrument Serif,
Geist). Python standard library only.

```bash
python3 build_hangar.py                 # writes ../../docs/autopilot/diagrams and ../../docs/glidepath/diagrams
python3 build_hangar.py /some/out/dir   # or anywhere else
./shot.sh /abs/path/page.html out.png   # optional: a Chrome screenshot for review
```

- `lib.py`, `libx.py`: primitives (nodes, connectors with rounded right angles, zones, legends, page shell).
- `e_g.py` plan set, `e_a` to `e_f` Autopilot set, `d123` to `d1011` reference set, `e_h.py` Glidepath set, `e_i.py` Crossplane set (docs/crossplane/diagrams), `e_j.py` Service catalog set (docs/catalog/diagrams), `e_m.py` Testing set (docs/testing/diagrams), `e_k.py` SLO set (docs/slo/diagrams), `e_l.py` Overview set (docs/overview/diagrams).
- Every page has a light and a dark theme: `lib.DARK` maps each colour to its dark value, the page follows
  `prefers-color-scheme`, and an embedder can force either with `<html data-theme="light|dark">`.
- Check a page with the skill's `scripts/self_check.py`.
- Every page separates **Built** from **Proposal**; keep that when editing.
- The Overview set uses its own kit, `ov.py`: colours as CSS classes on custom properties, the product dial marks from
  `brand/marks`, root-relative links that open in the top window, and optional motion. `motion_controller.js` is the
  skill's `assets/template-motion.html` controller copied verbatim; the skill's `verify-motion.py` rejects any edit to it.
  Check motion pages with `verify-motion.py` as well as `self_check.py`.
