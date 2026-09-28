// Records player.html playing a run's cast to a WebM (out/<run>-raw.webm). Serve the hangar repo root first:
//   python3 -m http.server 8767   (from the hangar repo root)
//   node record-terminal.mjs gate
import { chromium } from 'playwright-core';
import { renameSync } from 'node:fs';

const run = process.argv[2] || 'gate';
const CHROME = process.env.CHROME ||
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;
const out = new URL('./out/', import.meta.url).pathname;

const browser = await chromium.launch({ executablePath: CHROME });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, recordVideo: { dir: out, size: { width: 1440, height: 900 } } });
const page = await ctx.newPage();
await page.goto(`http://localhost:8767/tools/zero-to-running/player.html?run=${run}&speed=${process.env.SPEED || 1}`);
await page.waitForFunction(() => window.__done === true, null, { timeout: 30 * 60 * 1000, polling: 1000 });
const video = page.video();
await ctx.close();
await browser.close();
renameSync(await video.path(), `${out}${run}-raw.webm`);
console.log(`${out}${run}-raw.webm`);
