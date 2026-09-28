// Drives a real Backstage/Tower session in a visible Chromium window and records it, for the Tower half of the
// zero-to-running walkthrough. A person signs in first; after that the session is driven step by step over a small
// local HTTP API, so each step can be checked before the next one:
//
//   node tower-driver.mjs signin     # opens the window without recording; sign in, then close it
//   node tower-driver.mjs explore    # same API, no recording, for rehearsing a step
//   node tower-driver.mjs record     # reopens the same profile, recording to out/tower-video/, listens on :7171
//   curl -s localhost:7171/eval -d 'await page.goto(URL + "/tower")'
//   curl -s localhost:7171/caption -d 'Some caption'           # caption bar burned into the recording
//   curl -s localhost:7171/shot -o /tmp/x.png                   # screenshot to check the state
//   curl -s localhost:7171/stop                                 # closes the context and finalises the video
//
// Home-lab names are masked on screen (dev/prod), the same way the terminal cast does it.
import http from 'node:http';
import { chromium } from 'playwright-core';

const URL = process.env.BACKSTAGE_URL || 'http://backstage.prod.kiac.local:1880';
const CHROME = process.env.CHROME ||
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;
const mode = process.argv[2] || 'record';
const profile = new globalThis.URL('./out/tower-profile', import.meta.url).pathname;
const videoDir = new globalThis.URL('./out/tower-video', import.meta.url).pathname;

const MASK = `(() => {
  const subs = [[/gitops-cluster-kind-prod/g,'gitops-cluster-prod'],[/kind-prod/g,'prod'],[/kiac-dev/g,'dev'],[/kind-dev/g,'dev'],
    [/[\\w.-]*\\.kiac\\.local(:\\d+)?/g,'lab.internal'],[/[\\w.-]*prod\\.kind\\.local/g,'app.lab.internal'],
    [/[\\w.+-]+@gmail\\.com/g,'james@hangarplatform.dev']];
  const fix = (n) => { let t = n.nodeValue, o = t; for (const [a,b] of subs) t = t.replace(a,b); if (t !== o) n.nodeValue = t; };
  const walk = (root) => { const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) fix(n); };
  const fixAttrs = (el) => { for (const a of ['value','title','aria-label','placeholder']) { const v = el.getAttribute && el.getAttribute(a);
    if (v) { let t = v; for (const [x,y] of subs) t = t.replace(x,y); if (t !== v) el.setAttribute(a,t); } } };
  new MutationObserver((ms) => { for (const m of ms) { if (m.type === 'characterData') fix(m.target);
    for (const n of m.addedNodes) { if (n.nodeType === 3) fix(n); else if (n.nodeType === 1) { walk(n); fixAttrs(n); n.querySelectorAll && n.querySelectorAll('*').forEach(fixAttrs); } } } })
    .observe(document, { subtree: true, childList: true, characterData: true });
  document.addEventListener('DOMContentLoaded', () => walk(document.body));
  // Caption bar for the recording.
  const bar = () => { let b = document.getElementById('__cap'); if (!b && document.body) { b = document.createElement('div'); b.id = '__cap';
    b.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:1100px;z-index:2147483647;background:rgba(11,13,16,.92);color:#e8e4dc;font:400 24px/1.3 "Instrument Serif",Georgia,serif;padding:14px 26px;border-radius:10px;border:1px solid rgba(232,163,61,.55);box-shadow:0 10px 40px rgba(0,0,0,.35);pointer-events:none;transition:opacity .3s;opacity:0;text-align:center';
    document.body.appendChild(b); } return b; };
  window.__caption = (t) => { const b = bar(); if (!b) return; b.textContent = t; b.style.opacity = t ? 1 : 0; };
})();`;

const launch = (record) => chromium.launchPersistentContext(profile, {
  executablePath: CHROME,
  headless: false,
  viewport: { width: 1440, height: 900 },
  ...(record ? { recordVideo: { dir: videoDir, size: { width: 1440, height: 900 } } } : {}),
});

if (mode === 'signin') {
  const ctx = await launch(false);
  const page = ctx.pages()[0] || (await ctx.newPage());
  await page.goto(URL);
  console.log('Sign in in the window, then close it.');
  await new Promise((r) => ctx.on('close', r));
  process.exit(0);
}

const ctx = await launch(mode === 'record');
await ctx.addInitScript(MASK);
const page = ctx.pages()[0] || (await ctx.newPage());
let caption = '';
page.on('load', () => page.evaluate((t) => window.__caption && window.__caption(t), caption).catch(() => {}));
await page.goto(URL);
// The Backstage session doesn't survive a restart; with GitHub still signed in from the sign-in step, the
// Sign In button completes without a prompt. Recordings trim this part.
const signIn = page.getByRole('button', { name: /sign in/i });
if (await signIn.waitFor({ state: 'visible', timeout: 8000 }).then(() => true, () => false)) { await signIn.click(); await page.waitForTimeout(6000); }

const body = (req) => new Promise((r) => { let b = ''; req.on('data', (c) => (b += c)); req.on('end', () => r(b)); });
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor;
http.createServer(async (req, res) => {
  try {
    if (req.url === '/eval') {
      const fn = new AsyncFunction('page', 'ctx', 'URL', await body(req));
      const out = await fn(page, ctx, URL);
      res.end(JSON.stringify(out ?? null));
    } else if (req.url === '/caption') {
      caption = await body(req);
      await page.evaluate((t) => window.__caption && window.__caption(t), caption);
      res.end('ok');
    } else if (req.url === '/shot') {
      res.setHeader('content-type', 'image/png');
      res.end(await page.screenshot());
    } else if (req.url === '/stop') {
      res.end('stopping');
      const video = page.video();
      await ctx.close();
      console.log('video:', video && (await video.path()));
      process.exit(0);
    } else res.end('?');
  } catch (e) {
    res.statusCode = 500;
    res.end(String(e && e.stack || e));
  }
}).listen(7171, () => console.log('driving on :7171'));
