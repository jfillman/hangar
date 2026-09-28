"""Runs one real command and appends it, with its real output and timing, to a run log.

    python3 rec.py <run> "<caption>" -- <command...>
    python3 rec.py <run> --note "<caption>"            # a caption card with no command (e.g. "12 minutes later")

The log (runs/<run>.jsonl) keeps the output exactly as the command printed it. Home-lab names are swapped for
dev/prod only when the player renders it (player.html), so the raw record stays honest and local.
"""
import json, pathlib, subprocess, sys, time

run, rest = sys.argv[1], sys.argv[2:]
log = pathlib.Path(__file__).parent / 'runs' / f'{run}.jsonl'
log.parent.mkdir(exist_ok=True)
if rest[0] == '--note':
    entry = {'t': time.time(), 'note': rest[1]}
else:
    caption, cmd = rest[0], rest[rest.index('--') + 1:]
    shown = cmd[0] if len(cmd) == 1 else ' '.join(cmd)
    start = time.time()
    p = subprocess.run(shown if len(cmd) == 1 else cmd, shell=len(cmd) == 1, capture_output=True, text=True)
    out = (p.stdout + p.stderr).rstrip('\n')
    entry = {'t': start, 'dur': round(time.time() - start, 2), 'caption': caption, 'cmd': shown, 'out': out, 'rc': p.returncode}
    print(out)
    if p.returncode: print(f'[rc={p.returncode}]', file=sys.stderr)
with log.open('a') as f: f.write(json.dumps(entry) + '\n')
