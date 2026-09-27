import { chromium } from 'playwright-core';
import fs from 'fs';
const W = 1440, H = 900;
const SHOTS = process.env.SHOTS === '1';
const browser = await chromium.launch({ executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1,
  ...(SHOTS ? {} : { recordVideo: { dir: '/tmp/tower-demo-rec', size: { width: W, height: H } } }) });
const page = await ctx.newPage();
const T0 = Date.now();
const marks = [];
const errs = new Set();
page.on('pageerror', e => errs.add(e.message.slice(0, 200)));

// overlay: fake cursor + caption bar
await ctx.addInitScript(() => {
  window.addEventListener('DOMContentLoaded', () => {
    const c = document.createElement('div');
    c.id = '__cursor';
    c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;z-index:2147483647;pointer-events:none;transition:transform .12s;';
    c.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.5 20 L13 19 L10.2 12.8 L16 12.8 Z" fill="#fff" stroke="#0B0D10" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => { c.style.left = e.clientX - 3 + 'px'; c.style.top = e.clientY - 2 + 'px'; }, true);
    document.addEventListener('mousedown', () => { c.style.transform = 'scale(.8)'; }, true);
    document.addEventListener('mouseup', () => { c.style.transform = 'scale(1)'; }, true);
    const cap = document.createElement('div');
    cap.id = '__cap';
    cap.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:960px;z-index:2147483646;pointer-events:none;background:rgba(11,13,16,.92);border:1px solid #5C4520;color:#E9ECEF;font:500 19px/1.4 "IBM Plex Sans",sans-serif;padding:12px 22px;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.5);opacity:0;transition:opacity .35s;text-align:center';
    document.body.appendChild(cap);
    const s = sessionStorage.getItem('__cap');
    if (s) { cap.innerHTML = s; cap.style.opacity = '1'; }
  });
});

let shotN = 0;
const wait = ms => page.waitForTimeout(SHOTS ? Math.min(ms, 1200) : ms);
async function caption(html, top = false) {
  if (html) marks.push([((Date.now() - T0) / 1000).toFixed(1), html.replace(/<[^>]+>/g, '')]);
  await page.evaluate(([h, top]) => {
    sessionStorage.setItem('__cap', h || '');
    const cap = document.getElementById('__cap'); if (!cap) return;
    cap.style.top = top ? '24px' : 'auto'; cap.style.bottom = top ? 'auto' : '28px';
    if (!h) { cap.style.opacity = '0'; return; }
    cap.style.opacity = '0';
    setTimeout(() => { cap.innerHTML = h; cap.style.opacity = '1'; }, 250);
  }, [html, top]);
  await page.waitForTimeout(350);
}
let mx = W / 2, my = H / 2;
async function moveTo(x, y, steps = 25) { await page.mouse.move(x, y, { steps }); mx = x; my = y; }
async function clickEl(loc, pause = 500) {
  await loc.scrollIntoViewIfNeeded();
  const b = await loc.boundingBox();
  await moveTo(b.x + b.width / 2, b.y + b.height / 2);
  await page.waitForTimeout(pause);
  await page.mouse.down(); await page.mouse.up();
}
async function smoothScroll(dy, ms = 1500) {
  await page.evaluate(([dy, ms]) => new Promise(res => {
    const y0 = window.scrollY, t0 = performance.now();
    const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    const f = now => { const t = Math.min(1, (now - t0) / ms); window.scrollTo(0, y0 + dy * ease(t)); t < 1 ? requestAnimationFrame(f) : res(); };
    requestAnimationFrame(f);
  }), [dy, ms]);
}
async function scrollToEl(loc, offset = 120, ms = 1400) {
  const b = await loc.boundingBox();
  await smoothScroll(b.y - offset, ms);
}
async function snap(name) { if (SHOTS) await page.screenshot({ path: `/tmp/rec-${String(++shotN).padStart(2, '0')}-${name}.png` }); }
const tab = label => page.locator('button', { hasText: new RegExp(`^${label}`, 'i') }).first();

await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
await page.mouse.move(mx, my);
await wait(800);
await caption('Tower is my release command center for <b style="color:#E8A33D">Backstage</b>.');
await wait(2600);
await caption('It starts with the fleet: every app, in every environment, at a glance.');
await clickEl(page.getByText('Fleet Dashboard'));
await page.waitForLoadState('networkidle');
await wait(3200);
await snap('fleet');
await clickEl(page.getByText('Ops Wall', { exact: false }).first());
await wait(3200);
await snap('opswall');
await caption('One canary is mid-flight in prod. Let’s open that app.');
await clickEl(page.getByText('All applications').first());
await wait(900);
await clickEl(page.getByText('flight-api', { exact: true }).first());
await page.waitForLoadState('networkidle');
await wait(2200);
await caption('Overview: what’s live where, on the promotion path from dev to prod.');
await wait(3000);
await snap('overview');
await moveTo(700, 600);
await smoothScroll(520, 1800);
await caption('Every event from the pipeline lands here, stitched to the commit and the image.');
await wait(3400);
await snap('activity');
await smoothScroll(-600, 900);

await caption('Pipelines: Tekton runs for this app, grouped into named release flows.');
await clickEl(tab('Pipelines'));
await wait(2800);
await snap('pipelines');
await clickEl(page.getByRole('button', { name: /^Show$/ }).last());
await wait(700);
await scrollToEl(page.getByText(/^BUILD\s+·/).first().or(page.getByRole('button', { name: /^Hide$/ }).last()), 90, 1600);
await caption('A build is running right now. Each node is a task in the DAG, live from Tekton.');
await wait(3500);
await snap('dag');
await smoothScroll(-3000, 900);

await caption('Deployments: the delivery for each environment, from release PR to canary.');
await clickEl(tab('Deployments'));
await wait(3200);
await snap('deployments');
await moveTo(700, 600);
await smoothScroll(480, 1800);
await caption('Prod is paused at 40% traffic while background analysis watches the error rate.');
await wait(3800);
await snap('stepper');
await smoothScroll(520, 1600);
await caption('The live topology: stable and canary ReplicaSets splitting traffic.');
await wait(3400);
await snap('k8s');
await scrollToEl(page.getByText('Supply chain security').first(), 200, 1500);
await caption('Supply chain evidence rides along: provenance, SBOM, signature and Rekor entry.', true);
await wait(3400);
await snap('supply');
await smoothScroll(-5000, 900);

await caption('Releases: which build is live in which environment, newest first.');
await clickEl(tab('Releases'));
await wait(3800);
await snap('releases');

await caption('Topology: route, service, workload and pods, read live from each cluster.');
await clickEl(tab('Topology'));
await wait(2200);
const prodChip = page.getByText('prod', { exact: true }).first();
await clickEl(prodChip);
await wait(1500);
await moveTo(700, 600);
await smoothScroll(450, 1600);
await caption('The canary ramp and its analysis, step by step.');
await wait(3800);
await snap('topology');
await smoothScroll(-3000, 800);

await caption('SLOs: burn rate and error budget per environment, straight from Prometheus.');
await clickEl(tab('SLOs'));
await wait(3600);
await snap('slos');

await caption('Changing config is a form, but it never commits directly.');
await clickEl(tab('App Configuration'));
await wait(2200);
const replicas = page.locator('input[type=number]').first();
await scrollToEl(replicas, 260, 1500);
await clickEl(replicas);
await page.keyboard.press('Control+A');
await page.keyboard.type('6', { delay: 120 });
await wait(900);
await caption('It becomes a reviewed GitOps pull request against the environment\u2019s values.', true);
const openPr = page.getByRole('button', { name: /^Open PR$/ }).first();
await scrollToEl(openPr, 300, 1200);
await wait(1500);
await snap('review');
await clickEl(openPr);
await wait(3200);
await snap('prdialog');
await page.keyboard.press('Escape');
await wait(600);
await smoothScroll(-5000, 700);
await caption('', true);
await caption('The same goes for the pipeline itself: Glidepath\u2019s cicd.yaml, edited in place.');
await clickEl(tab('Glidepath'));
await wait(3400);
await snap('glidepath');
await caption('Tower: calm, honest visibility from commit to production.');
await wait(3200);
await caption('');
await wait(600);

console.log(JSON.stringify(marks, null, 1));
console.log('errors:', [...errs].join('\n'));
await ctx.close();
await browser.close();
if (!SHOTS) { const f = fs.readdirSync('/tmp/tower-demo-rec').filter(x => x.endsWith('.webm')).map(x => '/tmp/tower-demo-rec/' + x); console.log(f); }
