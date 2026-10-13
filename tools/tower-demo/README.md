# Tower demo harness

This is what records the Tower walkthrough on hangarplatform.dev/tower/. It runs Tower's real
plugin source in a small Vite app with Backstage's API providers, and feeds it invented data about
the Skyport demo services from airframe/examples/skyport (flight-api in the lead, boarding-api,
baggage-api) across dev, staging and prod on two clusters called dev and prod. No cluster, GitHub or Backstage backend is involved.

## Pieces

- `mock/fixtures.ts`: the demo world (Kubernetes objects, Tekton runs, ArgoCD apps, PRs,
  provenance, Prometheus answers, notifications, config files).
- `mock/fleet.ts`: the fleet-wide reads the Ops Wall makes (every PipelineRun on the Tekton cluster, Tekton Results
  history, Glidepath's release records, dora-exporter's series) and checkin-api, a new service half-way through
  provisioning, for the Services page's Provisioning tab.
- `mock/apis.ts`: stand-ins for the Backstage APIs Tower calls, routing its fetches to the fixtures.
- `mock/k8sReact.ts`: replaces `@backstage/plugin-kubernetes-react`'s hooks with fixture-backed ones.
- `stand-ins/`: modules the plugin imports from its host app that aren't in the tower repo.
  `brand/tokens.ts` is rebuilt from `docs/brand/hangar-brand-system.html`; `usePullRequests` and
  `shared/format` are minimal versions with the same shapes.
- `prepare.sh`: copies Tower's plugin source (`tower/src`; older checkouts `tower/plugin/src`) into `./tower` and
  swaps home-lab names for generic ones.
- `mock/breakglass.ts`: the break-glass backend: the `/breakglass/*` routes (stateful, kept in sessionStorage),
  a fake attach WebSocket that plays a shell in the debug container (`debug / $`, uid 65532, read-only), and
  asciicast v2 recordings with a SHA-256 and a Rekor index on the session record.
- `record-breakglass.mjs` / `encode-breakglass.sh`: the break-glass walkthrough and its encoder.
- `record.mjs`: the scripted walkthrough (captions, cursor, scenes, chapters), recorded with Playwright.
- `encode.sh`: turns the recording into the MP4, WebM and poster under `web/public/media/`, and writes
  `tower-chapters.json` from the recording's marks.

## Re-recording

```sh
npm install --legacy-peer-deps
TOWER=../../../tower npm run prepare-plugin   # path to a tower checkout
npm run dev                                   # leave running
npm run record                                # about three and a half minutes; PACE=0.8 scales the pauses
FFMPEG=/path/to/ffmpeg npm run encode         # needs libx264 and libvpx
```

`SHOTS=1 npm run record` does a fast dry run that saves a screenshot per scene to `/tmp/rec-shots` instead
of recording. If a scene's timing changes, copy the times from `tower-chapters.json` into the chapter list in
`web/src/pages/tower.astro`. Recording needs the same ffmpeg setup as the break-glass walkthrough below.

## The break-glass walkthrough

Who is signed in is a demo toggle: `?as=james|sam|alex` on the URL (kept in sessionStorage), or
`window.__demo.setUser('sam')` then reload. james and sam are owners of the Skyport apps, alex is an admin (may break
the glass). `?badge=1` shows a "signed in as" pill; `window.__demo.reset()` drops the mock's sessions back to the seed.
The live terminal answers a fixed set of commands (`id`, `ps`, `ss -tnp`, `dig`, `nc -zv`, `ls /pod-volumes/`,
`touch`, `apk add`, `cat /proc/1/environ`, ...); anything else is `sh: x: not found`. Ending a session turns
what was typed and shown into the recording the player hashes.

```sh
npm run dev                                       # leave running
SHOTS=1 npm run record:breakglass                 # fast dry run, screenshots in /tmp/bg-shots
npm run record:breakglass                         # about 3.5 minutes; PACE=0.72 scales the pauses
FFMPEG=/path/to/ffmpeg npm run encode:breakglass  # MP4, WebM, poster, and breakglass-chapters.json
STILLS=../../web/public/media/breakglass npm run record:breakglass   # 2x stills for the essay
```

Recording needs an ffmpeg that Playwright accepts for its video. playwright-core 1.63 looks for
`ffmpeg-1013/ffmpeg-linux` under `PLAYWRIGHT_BROWSERS_PATH` and needs VP9 and a Matroska demuxer; if only an older
Playwright ffmpeg is installed, point a browsers path at a wrapper that runs a full build (`pip install
imageio-ffmpeg`; `python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`), which also has
libx264 and libvpx-vp9 for the encode step:

```sh
mkdir -p /tmp/pw/ffmpeg-1013 && printf '#!/bin/sh\nexec %s "$@"\n' "$FFMPEG" > /tmp/pw/ffmpeg-1013/ffmpeg-linux
chmod +x /tmp/pw/ffmpeg-1013/ffmpeg-linux
PLAYWRIGHT_BROWSERS_PATH=/tmp/pw npm run record:breakglass
```

If a scene's timing changes, the encoder rewrites `breakglass-chapters.json` from the recording's marks.
