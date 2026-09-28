"""Turns a raw run log into the cast the player shows: home-lab names swapped, personal details masked,
kubectl's --context flag turned into a "dev cluster" / "prod cluster" badge.

    python3 make_cast.py gate     # runs/gate.jsonl -> out/gate.json

Only presentation changes here. The commands ran exactly as logged and every output line is the real one,
apart from the substitutions below.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
run = sys.argv[1]
META = json.loads((HERE / 'runs' / f'{run}.meta.json').read_text())

SUBS = [
    (r'gitops-cluster-kind-prod', 'gitops-cluster-prod'),
    (r'kind-prod', 'prod'),
    (r'kiac-dev', 'dev'),
    (r'kind-dev', 'dev'),
    (r'kind-man', 'mgmt'),
    (r'dev\.kiac\.local', 'dev.lab.internal'),
    (r'[\w.+-]*prod\.kind\.local', 'app.lab.internal'),
    (r'kiac\.local', 'lab.internal'),
    (r'192\.168\.\d+\.\d+', '10.0.0.2'),
    (r'[\w.+-]+@gmail\.com', '<a signer email>'),
    (r'/Users/jerf/tech/', '~/'),
]


def scrub(s: str) -> str:
    for a, b in SUBS:
        s = re.sub(a, b, s)
    return s


def display(cmd: str):
    where = 'prod cluster' if '--context kind-prod' in cmd else 'dev cluster' if '--context kiac-dev' in cmd else ''
    cmd = re.sub(r'\s--context \S+', '', cmd)
    cmd = re.sub(r"\s-l 'tekton\.dev/pipeline notin \([^)]*\)'", '', cmd)
    cmd = re.sub(r"\s2>/dev/null \| grep -v -E '[^']*'", '', cmd)
    cmd = cmd.replace('git -C ~/glidepath', 'git -C glidepath')
    return scrub(cmd), where


rows = [json.loads(line) for line in (HERE / 'runs' / f'{run}.jsonl').read_text().splitlines() if line.strip()]
rows.sort(key=lambda r: r['t'])
t0 = rows[0]['t']
chapters = META['chapters']  # [[first caption prefix, chapter name], ...] in order
steps, chapter = [], None
for r in rows:
    text = r.get('caption') or r.get('note')
    for prefix, name in chapters:
        if text.startswith(prefix):
            chapter = name
    step = {'at': round(r['t'] - t0), 'chapter': chapter, 'caption': scrub(text)}
    if 'cmd' in r:
        shown = next((c for pre, c in META.get('display', {}).items() if text.startswith(pre)), r['cmd'])
        step['cmd'], step['where'] = display(shown)
        step['out'] = scrub(r['out']).split('\n') if r['out'] else []
        step['rc'] = r['rc']
    else:
        step['note'] = True
    steps.append(step)

out = HERE / 'out'
out.mkdir(exist_ok=True)
cast = {'title': META['title'], 'subtitle': META['subtitle'], 'chapters': [c[1] for c in chapters], 'steps': steps,
        'total': steps[-1]['at']}
(out / f'{run}.json').write_text(json.dumps(cast, indent=1))
leaks = [s for s in json.dumps(cast).split('"') if re.search(r'kiac|kind-prod|kind-dev|crossfader|192\.168', s)]
print(f'{len(steps)} steps, {cast["total"] // 60} minutes of real time, leaks: {leaks or "none"}')
