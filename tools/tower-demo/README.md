# Tower demo harness

This is what records the Tower walkthrough on hangarplatform.dev/tower/. It runs Tower's real
plugin source in a small Vite app with Backstage's API providers, and feeds it invented data:
four demo apps (storefront, orders-api, payments-worker, search-indexer) across dev, staging and
prod on two clusters called dev and prod. No cluster, GitHub or Backstage backend is involved.

## Pieces

- `mock/fixtures.ts`: the demo world (Kubernetes objects, Tekton runs, ArgoCD apps, PRs,
  provenance, Prometheus answers, notifications, config files).
- `mock/apis.ts`: stand-ins for the Backstage APIs Tower calls, routing its fetches to the fixtures.
- `mock/k8sReact.ts`: replaces `@backstage/plugin-kubernetes-react`'s hooks with fixture-backed ones.
- `stand-ins/`: modules the plugin imports from its host app that aren't in the tower repo.
  `brand/tokens.ts` is rebuilt from `docs/brand/hangar-brand-system.html`; `usePullRequests` and
  `shared/format` are minimal versions with the same shapes.
- `prepare.sh`: copies `tower/plugin/src` into `./tower` and swaps home-lab names for generic ones.
- `record.mjs`: the scripted walkthrough (captions, cursor, scenes), recorded with Playwright.
- `encode.sh`: turns the recording into the MP4, WebM and poster under `web/public/media/`.

## Re-recording

```sh
npm install --legacy-peer-deps
TOWER=../../../tower npm run prepare-plugin   # path to a tower checkout
npm run dev                                   # leave running
npm run record                                # about two minutes
FFMPEG=/path/to/ffmpeg npm run encode         # needs libx264 and libvpx
```

`SHOTS=1 npm run record` does a fast dry run that saves a screenshot per scene to `/tmp` instead
of recording. If a scene's timing changes, update the chapter list in `web/src/pages/tower.astro`.
