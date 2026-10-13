// The Tower walkthrough on hangarplatform.dev/tower/ and the home page: provisioning a new service, the Ops Wall,
// then one app's tabs from pull requests to config. Dark theme, recorded with Playwright against `npm run dev`.
//
//   npm run record              records the video to /tmp/tower-demo-rec
//   SHOTS=1 npm run record      fast dry run, a screenshot per scene in /tmp/rec-shots
import { chromium } from 'playwright-core';
import fs from 'fs';

const W = 1440, H = 900;
const SHOTS = process.env.SHOTS === '1';
const REC_DIR = '/tmp/tower-demo-rec';
const BASE = process.env.BASE ?? 'http://127.0.0.1:5173/';

if (SHOTS) fs.mkdirSync('/tmp/rec-shots', { recursive: true });
if (!SHOTS) fs.rmSync(REC_DIR, { recursive: true, force: true });

const browser = await chromium.launch({ executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1,
  ...(SHOTS ? {} : { recordVideo: { dir: REC_DIR, size: { width: W, height: H } } }) });
const page = await ctx.newPage();
const V0 = Date.now();
let T0 = Date.now();
const marks = [];
const chapters = [];
const errs = new Set();
page.on('pageerror', e => errs.add(e.message.slice(0, 200)));
page.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.add('console: ' + m.text().slice(0, 200)); });

// overlay: fake cursor + caption bar, both kept across page loads
await ctx.addInitScript(() => {
  window.addEventListener('DOMContentLoaded', () => {
    const c = document.createElement('div');
    c.id = '__cursor';
    c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;z-index:2147483647;pointer-events:none;transition:transform .12s;';
    c.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.5 20 L13 19 L10.2 12.8 L16 12.8 Z" fill="#fff" stroke="#0B0D10" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    const pos = sessionStorage.getItem('__cur');
    if (pos) { const [x, y] = pos.split(',').map(Number); c.style.left = x - 3 + 'px'; c.style.top = y - 2 + 'px'; }
    document.addEventListener('mousemove', e => { c.style.left = e.clientX - 3 + 'px'; c.style.top = e.clientY - 2 + 'px'; sessionStorage.setItem('__cur', e.clientX + ',' + e.clientY); }, true);
    document.addEventListener('mousedown', () => { c.style.transform = 'scale(.8)'; }, true);
    document.addEventListener('mouseup', () => { c.style.transform = 'scale(1)'; }, true);
    const cap = document.createElement('div');
    cap.id = '__cap';
    cap.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:960px;z-index:2147483646;pointer-events:none;background:rgba(11,13,16,.92);border:1px solid #5C4520;color:#E9ECEF;font:500 19px/1.4 "IBM Plex Sans",sans-serif;padding:12px 22px;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.5);opacity:0;transition:opacity .35s;text-align:center';
    document.body.appendChild(cap);
    const s = sessionStorage.getItem('__cap');
    const top = sessionStorage.getItem('__capTop') === '1';
    cap.style.top = top ? '24px' : 'auto'; cap.style.bottom = top ? 'auto' : '28px';
    if (s) { cap.innerHTML = s; cap.style.opacity = '1'; }
  });
});

let shotN = 0;
// PACE scales every pause, to land the whole tour at about three minutes.
const PACE = Number(process.env.PACE ?? 0.8);
const wait = ms => page.waitForTimeout(SHOTS ? Math.min(ms, 900) : ms * PACE);
const now = () => ((Date.now() - T0) / 1000);
async function caption(html, top = false) {
  if (html) marks.push([now().toFixed(1), html.replace(/<[^>]+>/g, '')]);
  await page.evaluate(([h, top]) => {
    sessionStorage.setItem('__cap', h || '');
    sessionStorage.setItem('__capTop', top ? '1' : '0');
    const cap = document.getElementById('__cap'); if (!cap) return;
    if (!h) { cap.style.opacity = '0'; return; }
    cap.style.opacity = '0';
    setTimeout(() => { cap.style.top = top ? '24px' : 'auto'; cap.style.bottom = top ? 'auto' : '28px'; cap.innerHTML = h; cap.style.opacity = '1'; }, 250);
  }, [html, top]);
  await page.waitForTimeout(350);
}
function chapter(title) { chapters.push({ t: now(), title }); }
let mx = W / 2, my = H / 2;
async function moveTo(x, y, steps = 22) { await page.mouse.move(x, y, { steps: SHOTS ? 2 : steps }); mx = x; my = y; }
async function clickEl(loc, pause = 450) {
  await loc.scrollIntoViewIfNeeded();
  const b = await loc.boundingBox();
  await moveTo(b.x + b.width / 2, b.y + b.height / 2);
  await page.waitForTimeout(SHOTS ? 50 : pause);
  await page.mouse.down(); await page.mouse.up();
}
async function hover(loc, dx = 0, dy = 0) {
  const b = await loc.boundingBox();
  await moveTo(b.x + b.width / 2 + dx, b.y + b.height / 2 + dy);
}
async function smoothScroll(dy, ms = 1400) {
  await page.evaluate(([dy, ms]) => new Promise(res => {
    const y0 = window.scrollY, t0 = performance.now();
    const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    const f = now => { const t = Math.min(1, (now - t0) / ms); window.scrollTo(0, y0 + dy * ease(t)); t < 1 ? requestAnimationFrame(f) : res(); };
    requestAnimationFrame(f);
  }), [dy, SHOTS ? 10 : ms]);
}
/** Scroll so the element's top sits `offset` px below the top of the viewport. */
async function scrollToEl(loc, offset = 120, ms = 1300) {
  const b = await loc.boundingBox();
  await smoothScroll(b.y - offset, ms);
}
const toTop = () => smoothScroll(-20000, 800);
async function snap(name) { if (SHOTS) await page.screenshot({ path: `/tmp/rec-shots/${String(++shotN).padStart(2, '0')}-${name}.png` }); }
const tab = label => page.locator('button', { hasText: new RegExp(`^${label}`, 'i') }).first();

await page.goto(BASE, { waitUntil: 'networkidle' });
await page.mouse.move(mx, my);
await page.waitForTimeout(1500);
T0 = Date.now();

// ---- Services and provisioning
chapter('Provisioning a new service');
await caption('Tower is my release command center for <b style="color:#E8A33D">Backstage</b>.');
await wait(2600);
await caption('It opens on the services, and on anything being provisioned right now.');
await hover(page.getByText('checkin-api', { exact: true }).first(), 120);
await wait(3000);
await snap('services');
await clickEl(tab('Provisioning'));
await wait(1200);
await caption('checkin-api was asked for ten minutes ago. Every step, from the request PR to a healthy pod in dev.');
await wait(3400);
await snap('provisioning');
await moveTo(700, 560);
await scrollToEl(page.getByText('Steps', { exact: true }).first(), 90, 1500);
await caption('Each step is timed against the median of recent provisions, so a slow one stands out.', true);
await wait(4200);
await snap('prov-steps');
await scrollToEl(page.getByText(/What gets created/i).first(), 120, 1600);
await caption('Repos, the pipeline namespace and the secrets all come from one Crossplane XR.', true);
await wait(3600);
await snap('prov-created');
await toTop();

// ---- Ops Wall
chapter('The Ops Wall');
await caption('Then the whole fleet, on one screen: the Ops Wall.', true);
await clickEl(page.getByText('Fleet Dashboard'));
await page.waitForLoadState('networkidle');
await wait(2800);
await caption('What’s running, what’s deploying, what’s waiting on a review, and how the SLOs are holding up.', true);
await hover(page.getByText('Awaiting approval', { exact: false }).first(), 0, 30);
await wait(3600);
await snap('opswall');
await hover(page.getByText('Needs attention', { exact: false }).first(), 200, 50);
await caption('Needs attention is ranked: a canary paused in prod, a release that failed overnight.', true);
await wait(3800);
await snap('attention');
await hover(page.getByText('Running now', { exact: false }).first(), 300, 40);
await caption('Live pipelines show progress against their typical run time. Below, the last 24 hours as a strip.', true);
await wait(4000);
await snap('pipelines-panel');
await hover(page.getByText('Waiting for approval', { exact: false }).first(), 200, 30);
await caption('Deployments in flight, the release PR waiting for approval, and what landed today.', true);
await wait(3800);
await snap('in-flight');
await scrollToEl(page.getByText(/^DORA/i).first(), 380, 1200);
await hover(page.getByText('Deploy frequency', { exact: false }).first(), 60, 30);
await caption('And DORA, from the same queries as Glidepath’s Grafana dashboards.', true);
await wait(3600);
await snap('dora');
await toTop();

// ---- One app
chapter('One app at a glance');
await caption('One canary is mid-flight in prod. Let’s open that app.');
await clickEl(page.getByText('All applications').first());
await wait(900);
await clickEl(page.getByText('flight-api', { exact: true }).first());
await page.waitForLoadState('networkidle');
await wait(1800);
await caption('Overview: what’s live where, on the promotion path from dev to prod.');
await wait(3400);
await snap('overview');
await moveTo(700, 600);
await smoothScroll(560, 1700);
await caption('Every event from the pipeline lands here, stitched to the commit and the image.');
await wait(3200);
await snap('activity');
await toTop();

chapter('Pull requests');
await caption('Pull Requests: release, preview and source PRs, and what merged recently.');
await clickEl(tab('Pull Requests'));
await wait(3600);
await snap('prs');

chapter('Pipelines');
await caption('Pipelines: every Tekton run for this app, grouped into named release flows.');
await clickEl(tab('Pipelines'));
await wait(2600);
await snap('pipelines');
await clickEl(page.getByRole('button', { name: /^Show$/ }).last());
await wait(700);
await scrollToEl(page.getByRole('button', { name: /^Hide$/ }).last(), 90, 1500);
await caption('A build is running right now. Each node is a task in the DAG, live from Tekton.');
await wait(3600);
await snap('dag');
await toTop();

// ---- Deployments
chapter('Deployments and the canary');
await caption('Deployments: each environment’s delivery, from the release PR to the canary.');
await clickEl(tab('Deployments'));
await wait(3000);
await snap('deployments');
await moveTo(700, 600);
await scrollToEl(page.getByText('PR created', { exact: false }).first(), 140, 1700);
await caption('The release PR, its guardrails, the merge, the sync, and now the rollout: step 4 of 9, at 40%.');
await wait(4400);
await snap('stepper');
await scrollToEl(page.getByText('Rollout controls', { exact: false }).first(), 110, 1200);
await hover(page.getByRole('button', { name: /^Resume$/ }).first());
await caption('Owners can resume, promote or abort the canary right here, within their tier’s rules.', true);
await wait(4000);
await snap('rollout-controls');
await scrollToEl(page.getByText(/Kubernetes topology/i).first(), 120, 1600);
await caption('Stable and canary ReplicaSets, splitting traffic while the analysis watches the error rate.', true);
await wait(3800);
await snap('k8s');
await toTop();

// ---- Releases
chapter('Release matrix');
await caption('Releases opens on a command deck: drift, triage and the week at a glance.');
await clickEl(tab('Releases'));
await wait(3400);
await snap('releases');
const matrix = page.getByText('Release matrix', { exact: true }).first();
await moveTo(700, 560);
await scrollToEl(matrix, 90, 1400);
await caption('The matrix: a column is what’s live in an environment, a row is one release’s journey.', true);
await wait(2400);
chapter('Promoting a release');
const row = tag => page.locator('tr', { hasText: tag }).first();
const cell = (tag, i) => row(tag).locator('td').nth(i).locator('[tabindex="0"]').first();
await caption('1.8.1 has landed in dev. The + marks the one place it can go next.', true);
await clickEl(cell('1.8.1-6a0e5d2', 1));
await wait(1800);
await clickEl(page.getByRole('button', { name: /Promote to staging/ }));
await caption('Staging takes a direct commit to the app’s platform config. Prod always goes through a reviewed PR.', true);
await wait(3800);
await snap('promote-dialog');
await clickEl(page.getByRole('button', { name: /Commit and deploy/ }));
await caption('Committed. Argo CD picks it up from Git, not from Tower.', true);
await wait(2600);
await snap('promote-done');
await clickEl(page.getByRole('button', { name: /^Close$/ }), 300);
await wait(500);
await toTop();
await clickEl(page.getByText(/^Lead time$/).first());
await caption('Lead time: commit to deploy, for each environment.');
await wait(3200);
await snap('lead-time');

chapter('Release record');
await caption('Every release that reaches prod gets a release record.');
await clickEl(page.getByText(/^Record/).first());
await wait(2200);
await clickEl(page.getByText('confidence', { exact: true }).first());
await wait(1200);
await scrollToEl(page.getByText('Back to records').first(), 110, 1200);
await caption('What changed, what was built and what happened, in one place.');
await wait(2400);
await clickEl(page.getByRole('button', { name: /how\?/ }).first());
await caption('The confidence score shows its working, line by line.');
await wait(3400);
await snap('record-score');
await clickEl(page.getByRole('button', { name: /(hide how|how\?)/ }).first(), 200);
await moveTo(700, 600);
await scrollToEl(page.getByText('What was built', { exact: false }).first(), 100, 1600);
await caption('Every gate it passed on the way to prod, with the evidence behind it.', true);
await wait(3600);
await snap('record-gates');
await scrollToEl(page.getByText('Human context', { exact: true }).first(), 100, 1700);
await caption('And the part a machine can’t write: the summary, the risk and the sign-offs, committed through a PR.', true);
await wait(4400);
await snap('record-human');
await toTop();

// ---- Environments
chapter('Environments');
await caption('Environments: Ground deploys on every push, Flight only through an approved release.');
await clickEl(tab('Environments'));
await wait(3400);
await snap('environments');
await clickEl(page.getByRole('button', { name: /Add environment/ }));
await wait(900);
await page.keyboard.type('qa', { delay: SHOTS ? 0 : 160 });
await caption('Adding one is a form: a name, a tier, and a deploy step in the pipeline.', true);
await wait(2600);
await snap('env-add');
await clickEl(page.getByRole('button', { name: /Stage environment/ }));
await wait(1200);
await hover(page.getByText('Pending changes', { exact: false }).first(), 40, 120);
await caption('Changes stage on the right, then go out together as one pull request.', true);
await wait(3800);
await snap('env-staged');
await clickEl(page.getByRole('button', { name: /^Discard all$/ }));
await wait(800);

// ---- Topology and SLOs
chapter('Topology');
await caption('Topology: route, service, workload and pods, read live from each cluster.', true);
await clickEl(tab('Topology'));
await wait(2000);
await clickEl(page.getByText('prod', { exact: true }).first());
await wait(1500);
await moveTo(700, 600);
await smoothScroll(470, 1600);
await caption('The canary ramp and its analysis, step by step.');
await wait(3600);
await snap('topology');
await toTop();

chapter('SLOs');
await caption('SLOs: burn rate and error budget per environment, straight from Prometheus.');
await clickEl(tab('SLOs'));
await wait(3600);
await snap('slos');

chapter('Config as a pull request');
await caption('Changing config is a form, but it never commits directly.');
await clickEl(tab('App Configuration'));
await wait(2200);
const replicas = page.locator('input[type=number]').first();
await scrollToEl(replicas, 260, 1400);
await clickEl(replicas);
await page.keyboard.press('Control+A');
await page.keyboard.type('6', { delay: SHOTS ? 0 : 120 });
await wait(900);
await caption('It becomes a reviewed GitOps pull request against the environment’s values.', true);
const openPr = page.getByRole('button', { name: /^Open pull request$/ }).first();
await hover(openPr);
await wait(1300);
await snap('review');
await clickEl(openPr);
await wait(3000);
await snap('prdialog');
await page.keyboard.press('Escape');
await wait(600);
await toTop();
await caption('', true);
await caption('The same goes for the pipeline itself: Glidepath’s cicd.yaml, edited in place.');
await clickEl(tab('Glidepath'));
await wait(3400);
await snap('glidepath');
await caption('Tower: calm, honest visibility from commit to production.');
await wait(3400);
await caption('');
await wait(700);

const total = now();
console.log(JSON.stringify(marks, null, 1));
console.log('chapters', JSON.stringify(chapters));
console.log('total', total.toFixed(1), 'video offset of T0', ((T0 - V0) / 1000).toFixed(2));
console.log('errors:', [...errs].join('\n'));
if (!SHOTS) fs.writeFileSync(`${REC_DIR}/chapters.raw.json`, JSON.stringify({ chapters, total, offset: (T0 - V0) / 1000, marks }, null, 1));
await ctx.close();
await browser.close();
if (!SHOTS) console.log(fs.readdirSync(REC_DIR).filter(x => x.endsWith('.webm')).map(x => `${REC_DIR}/${x}`));
