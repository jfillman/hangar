# Diagram generator

Builds the 37 pages in `docs/autopilot/diagrams/` (plan 8, autopilot 19, reference 10) with the
diagram-design skill's grammar and the Hangar profile (amber, sky, warm bone, Instrument Serif,
Geist). Python standard library only.

```bash
python3 build_hangar.py                 # writes ../../docs/autopilot/diagrams
python3 build_hangar.py /some/out/dir   # or anywhere else
./shot.sh /abs/path/page.html out.png   # optional: a Chrome screenshot for review
```

- `lib.py`, `libx.py`: primitives (nodes, connectors with rounded right angles, zones, legends, page shell).
- `e_g.py` plan set, `e_a` to `e_f` Autopilot set, `d123` to `d1011` reference set.
- Check a page with the skill's `scripts/self_check.py`.
- Every page separates **Built** from **Proposal**; keep that when editing.
