#!/bin/sh
# Copies Tower's plugin source from a tower checkout into ./tower, adds the stand-in
# modules the plugin imports from its host Backstage app, and swaps home-lab names
# for the generic dev/prod ones the demo uses. Nothing here touches the tower repo.
set -eu
TOWER=${TOWER:-../../../tower}
rm -rf tower
mkdir -p tower
cp -r "$TOWER/plugin/src" tower/src
cp -r stand-ins/brand stand-ins/shared stand-ins/pullRequests tower/
python3 - "$TOWER/brand/marks" > tower/brand/marks.json <<'PY'
import json, os, re, sys
d = sys.argv[1]
out = {}
for f in sorted(os.listdir(d)):
    if f.endswith('-inline.svg'):
        s = open(os.path.join(d, f)).read().strip()
        out[f[:-len('-inline.svg')]] = re.sub(r'</svg>$', '', re.sub(r'^<svg[^>]*>', '', s))
print(json.dumps(out))
PY
grep -rl "kind-dev\|kind-prod\|kiac" tower/src | xargs sed -i \
  -e 's/kind-dev/dev/g' -e 's/kind-prod/prod/g' -e 's/kiac-dev/dev/g' -e 's/kiac-prod/prod/g' \
  -e 's/kiac\.local/example.internal/g' -e 's/kiac/hangar/g'
echo "tower/ is ready; run npm run dev"
