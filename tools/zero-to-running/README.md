# Zero to running

Records the two real runs on hangarplatform.dev/run/: `gate-api` from nothing to a canary, in the terminal, and
`checkin-api` the same way through Tower. Nothing here is mocked; it drives and records the real platform.

- `rec.py`: runs one real command and appends it, with its output and timing, to `runs/<run>.jsonl` (gitignored,
  since it keeps the home lab's real names).
- `make_cast.py` + `runs/<run>.meta.json`: turns a log into `out/<run>.json` for the player, swapping cluster names for
  dev/prod and masking personal details. Output lines are otherwise exactly as logged.
- `player.html` + `record-terminal.mjs`: plays a cast as a captioned terminal and records it (serve the hangar repo
  root on :8767 first). `SPEED=1.2` shortens it.
- `tower-driver.mjs`: a visible Chromium on Backstage/Tower, driven over a small local API and recorded in segments.
  `signin` first (a person signs in), then `explore` to rehearse a step or `record` to record it. It masks lab names
  on screen and burns in captions.
- `tower-cuts.json` + `encode.py`: which parts of each segment are kept, then the cut, the H.264/VP9 encodes and the
  posters into `web/public/media/`, using ffmpeg from a container.
- `gate-api/`, `checkin-api/`: the two small apps' source, as pushed to their repos.

After re-cutting a video, update the chapter times in `web/src/pages/run.astro`.
