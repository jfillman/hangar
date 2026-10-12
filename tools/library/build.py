"""Builds the Library's illustrated pages into docs/library/.

    python3 build.py              # writes ../../docs/library
    python3 build.py /some/dir    # or anywhere else
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'docs', 'library')

for name in sorted(f[:-3] for f in os.listdir(HERE) if f.startswith('r_') and f.endswith('.py')):
    page = importlib.import_module(name).P
    print(os.path.relpath(page.write(OUT)))
