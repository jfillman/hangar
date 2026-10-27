#!/bin/sh
# Copies Tower's plugin source from a tower checkout into ./tower, adds the stand-in
# modules the plugin imports from its host Backstage app (only where the checkout has
# none of its own), and swaps home-lab names for the generic dev/prod ones the demo
# uses. Nothing here touches the tower repo.
#
# The tower repo moved its plugin from plugin/src to src (and now carries brand/,
# shared/ and pullRequests/ itself); both layouts are handled.
set -eu
TOWER=${TOWER:-../../../tower}
rm -rf tower
mkdir -p tower
if [ -d "$TOWER/src" ]; then SRC="$TOWER/src"; else SRC="$TOWER/plugin/src"; fi
cp -r "$SRC" tower/src
for d in brand shared pullRequests; do
  [ -d "tower/src/$d" ] || cp -r "stand-ins/$d" "tower/src/$d"
  cp -r "stand-ins/$d" "tower/$d"
done
mkdir -p tower/brand
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
# js-yaml 5 has no default export; Tower's own build tolerates `import yaml from 'js-yaml'`, Vite does not.
grep -rl "import yaml from 'js-yaml'" tower/src | xargs -r sed -i "s/import yaml from 'js-yaml'/import * as yaml from 'js-yaml'/"
echo "tower/ is ready; run npm run dev"
