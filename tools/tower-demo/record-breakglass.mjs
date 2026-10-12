// The break-glass walkthrough: a Flight request on a live prod pod, a second owner's approval, the recorded
// terminal, the player with its hash check, and breaking the glass. Same harness and overlay as record.mjs.
//
//   npm run record:breakglass              records the video to /tmp/tower-demo-rec-bg
//   SHOTS=1 npm run record:breakglass      fast dry run, a screenshot per step in /tmp/bg-shots
//   STILLS=dir npm run record:breakglass   2x stills of the key screens for the essay (no captions, no cursor)
import { chromium } from 'playwright-core';
import fs from 'fs';

const W = 1440, H = 900;
const SHOTS = process.env.SHOTS === '1';
const STILLS = process.env.STILLS;
const FAST = SHOTS || !!STILLS;
const REC_DIR = '/tmp/tower-demo-rec-bg';
const BASE = process.env.BASE ?? 'http://127.0.0.1:5173/';
const ENTITY = 'component:default/flight-api';

if (STILLS) fs.mkdirSync(STILLS, { recursive: true });
if (SHOTS) fs.mkdirSync('/tmp/bg-shots', { recursive: true });
if (!FAST) fs.rmSync(REC_DIR, { recursive: true, force: true });

const browser = await chromium.launch({ executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: STILLS ? 2 : 1,
  ...(FAST ? {} : { recordVideo: { dir: REC_DIR, size: { width: W, height: H } } }),
});
const page = await ctx.newPage();
const V0 = Date.now();
let T0 = Date.now();
const marks = [];
const chapters = [];
const errs = new Set();
page.on('pageerror', e => errs.add(e.message.slice(0, 200)));
page.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.add('console: ' + m.text().slice(0, 200)); });

// overlay: fake cursor + caption bar (as in record.mjs); stills get neither
await ctx.addInitScript(([stills]) => {
  window.addEventListener('DOMContentLoaded', () => {
    if (stills) return;
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
}, [!!STILLS]);

let shotN = 0;
// PACE scales every pause in the recording (0.72 keeps the whole thing under three and a half minutes).
const PACE = Number(process.env.PACE ?? 0.72);
const wait = ms => page.waitForTimeout(FAST ? Math.min(ms, STILLS ? 700 : 900) : ms * PACE);
const now = () => ((Date.now() - T0) / 1000);
async function caption(html, top = false) {
  if (STILLS) return;
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
async function moveTo(x, y, steps = 16) { await page.mouse.move(x, y, { steps: FAST ? 2 : steps }); mx = x; my = y; }
async function clickEl(loc, pause = 450) {
  await loc.scrollIntoViewIfNeeded();
  const b = await loc.boundingBox();
  await moveTo(b.x + b.width / 2, b.y + b.height / 2);
  await page.waitForTimeout(FAST ? 50 : pause);
  await page.mouse.down(); await page.mouse.up();
}
async function hover(loc, dx = 0) {
  const b = await loc.boundingBox();
  await moveTo(b.x + b.width / 2 + dx, b.y + b.height / 2);
}
async function smoothScroll(dy, ms = 1400) {
  await page.evaluate(([dy, ms]) => new Promise(res => {
    const y0 = window.scrollY, t0 = performance.now();
    const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    const f = now => { const t = Math.min(1, (now - t0) / ms); window.scrollTo(0, y0 + dy * ease(t)); t < 1 ? requestAnimationFrame(f) : res(); };
    requestAnimationFrame(f);
  }), [dy, FAST ? 10 : ms]);
}
/** Scroll so the element's top sits `offset` px below the top of the viewport. */
async function scrollToEl(loc, offset = 120, ms = 1300) {
  const b = await loc.boundingBox();
  await smoothScroll(b.y - offset, ms);
}
async function snap(name) { if (SHOTS) await page.screenshot({ path: `/tmp/bg-shots/${String(++shotN).padStart(2, '0')}-${name}.png` }); }
/** A still for the essay: the element (with a margin) or the viewport, at 2x. */
async function still(name, loc, pad = 16) {
  if (!STILLS) return;
  await page.waitForTimeout(400);
  let clip;
  if (loc) {
    const b = await loc.boundingBox();
    const x = Math.max(0, b.x - pad), y = Math.max(0, b.y - pad);
    clip = { x, y, width: Math.min(W - x, b.width + pad * 2), height: Math.min(H - y, b.height + pad * 2) };
  }
  await page.screenshot({ path: `${STILLS}/${name}.png`, ...(clip ? { clip } : {}) });
}
/** A still spanning two elements, top of the first to bottom of the second. */
async function stillSpan(name, a, b, pad = 12) {
  if (!STILLS) return;
  await page.waitForTimeout(400);
  const ba = await a.boundingBox(), bb = await b.boundingBox();
  const x = Math.max(0, Math.min(ba.x, bb.x) - pad), y = Math.max(0, ba.y - pad);
  const right = Math.min(W, Math.max(ba.x + ba.width, bb.x + bb.width) + pad), bottom = Math.min(H, bb.y + bb.height + pad);
  await page.screenshot({ path: `${STILLS}/${name}.png`, clip: { x, y, width: right - x, height: bottom - y } });
}
async function typeSlow(loc, text, delay = 38) {
  await clickEl(loc, 250);
  await page.keyboard.type(text, { delay: FAST ? 0 : delay });
}
const tab = label => page.locator('button', { hasText: new RegExp(`^${label}`, 'i') }).first();
async function as(user, query = '') {
  await page.goto(`${BASE}?as=${user}&badge=${STILLS ? 0 : 1}${query}`, { waitUntil: 'networkidle' });
  await page.mouse.move(mx, my);
}
const card = () => page.getByTestId('breakglass-card');
const panel = () => page.getByTestId('breakglass-panel');
async function openPods() {
  await clickEl(page.getByText(/^pods$/i).first());
  await wait(900);
}
async function term(cmd, after = 1500, cap) {
  if (cap) await caption(cap, true);
  await page.keyboard.type(cmd, { delay: FAST ? 0 : 34 });
  await page.waitForTimeout(FAST ? 50 : 260);
  await page.keyboard.press('Enter');
  await wait(after);
}

// ---------------------------------------------------------------- 1. the request (james)
await as('james');
T0 = Date.now();
await wait(700);
chapter('James asks for a live session on a prod pod');
await caption('Tower’s new break-glass terminal: a recorded shell on a running pod, for when logs aren’t enough.');
await wait(3200);
await caption('This is <b style="color:#E8A33D">james</b>, an owner of flight-api. Something in prod is wrong, and the logs don’t say why.');
await clickEl(page.getByText('flight-api', { exact: true }).first());
await page.waitForLoadState('networkidle');
await wait(1500);
await clickEl(tab('Topology'));
await wait(1200);
await clickEl(page.getByText('prod', { exact: true }).first());
await wait(900);
await openPods();
await snap('pods');
const pod1 = page.getByText('flight-api-5c13762f-x7k2p', { exact: true }).first();
await clickEl(pod1);
await wait(600);
await scrollToEl(page.getByText('Containers', { exact: true }).first(), 220, 1200);
await clickEl(page.getByRole('button', { name: /^Debug$/ }));
await wait(700);
await scrollToEl(panel(), 70, 1300);
await caption('Debug opens the request form. Prod is Flight, so a second person has to approve.');
await wait(3400);
await snap('form');
await caption('A copy of the pod is the safe default. This bug only shows on live traffic, so james picks the live pod…');
await clickEl(page.getByText('The live pod', { exact: true }));
await wait(1700);
await caption('…with process access, to see what the app is doing. Both are written on the session record.');
await clickEl(panel().locator('label', { hasText: 'Process access to' }).locator('input'));
await wait(2400);
await caption('Fifteen, thirty or sixty minutes, a reason, and the incident it belongs to.');
await hover(page.locator('#bg-duration'));
await wait(500);
await page.selectOption('#bg-duration', '30');
await wait(700);
await typeSlow(page.locator('#bg-reason'), 'Gate updates hang for 30 s in prod only. Need the live pod: its DB connections and what the app is waiting on.', 13);
await wait(400);
await typeSlow(page.locator('#bg-ticket'), 'https://tickets.example.com/INC-4127', 18);
await wait(600);
await scrollToEl(page.getByTestId('breakglass-sensitive-note'), 420, 900);
await caption('Process access can reach secrets, so the recording will be restricted.');
await hover(page.getByTestId('breakglass-sensitive-note'), -200);
await wait(2600);
await snap('form-filled');
await still('01-request-form', panel());
await clickEl(page.getByRole('button', { name: /^Request approval$/ }));
await wait(1600);
await caption('Sent. Another owner, or an admin, has 30 minutes to decide. james can withdraw it any time.');
await hover(page.getByTestId('breakglass-awaiting'));
await wait(3800);
await snap('awaiting');

// ---------------------------------------------------------------- 2. the approval (sam)
chapter('Sam, another owner, approves it');
await caption('Now the view of <b style="color:#E8A33D">sam</b>, another owner of flight-api.');
await wait(1600);
await as('sam');
await wait(1200);
const strip = page.getByTestId('breakglass-queue');
await caption('The Break-glass strip on Tower’s home page lists what needs sam, across every app.');
await hover(strip, 120);
await wait(3200);
await snap('strip');
await still('02-queue-strip', strip);
await clickEl(strip.locator('button').first());
await page.waitForLoadState('networkidle');
await wait(1600);
const decide = page.getByTestId('breakglass-to-decide');
await decide.waitFor();
await scrollToEl(decide, 200, 900);
await caption('Who is asking, for what, and why: live pod, process access, 30 minutes.');
await hover(decide.getByText('asks for a', { exact: false }), 120);
await wait(3600);
await caption('It shows the image the pod runs, by digest, and warns that this session can read secrets.');
await hover(decide.locator('[data-testid^="breakglass-request-image-"]'), 60);
await wait(3600);
await snap('approver');
await still('03-approver-card', decide);
const noteBox = decide.locator('input[placeholder="Note (optional)"]');
await typeSlow(noteBox, 'OK for INC-4127. Live pod and process access make sense; 30 minutes.', 15);
await wait(600);
await clickEl(decide.getByRole('button', { name: /^Approve$/ }));
await wait(1200);
await caption('Approved, with a note. james now has 10 minutes to press Start.');
await wait(3000);
await snap('approved');

// ---------------------------------------------------------------- 3. the session (james)
chapter('The recorded session: what the debug container can and can’t do');
await caption('Back to <b style="color:#E8A33D">james</b>. The approval is waiting on his home page.');
await wait(1500);
await as('james');
await wait(1500);
await hover(page.getByTestId('breakglass-queue'), 120);
await wait(2200);
await snap('to-start');
await clickEl(page.getByTestId('breakglass-queue').locator('button').first());
await page.waitForLoadState('networkidle');
await wait(1400);
const startBtn = card().getByRole('button', { name: /^Start recorded session$/ });
await startBtn.waitFor();
await scrollToEl(card(), 160, 900);
await caption('The 30-minute clock starts only when he presses Start.');
await hover(startBtn);
await wait(2600);
await clickEl(startBtn, 200);
await caption('Tower adds a hardened debug container to the live pod: non-root, read-only, no capabilities.');
await wait(2600);
const termEl = card().getByTestId('breakglass-terminal');
await termEl.waitFor();
await scrollToEl(card().getByRole('status'), 150, 900);
await caption('The red banner never goes away: this is a recorded break-glass session, with its countdown.', true);
await hover(card().getByRole('status'), 100);
await wait(3300);
await snap('session');
await clickEl(termEl, 200);
await wait(500);
await term('id', 2300, 'The shell runs as user 65532, not root.');
await term('ps -o pid,user,args', 3000, 'Process access: the app’s java process is right there…');
await term('cat /proc/1/environ', 3000, '…but not its environment. The app runs as a different user, so its secrets stay closed.');
await term('ss -tnp', 3400, 'Ten connections open to the database. Now the hunch has evidence.');
await term('dig +short flight-db.app-flight-api-prod.svc.cluster.local', 1400, 'The database resolves and answers from inside the pod.');
await term('nc -zv flight-db.app-flight-api-prod.svc.cluster.local 5432', 2600);
await term('ls /pod-volumes/', 2600, 'No volume access was asked for, so no volumes are mounted.');
await term('touch /tmp/x', 2700, 'The filesystem is read-only…');
await snap('readonly');
await term('apk add tcpdump', 3000, '…and nothing can be installed. The image has what it has, and no more.');
await snap('terminal');
await stillSpan('04-terminal-readonly', card().getByRole('status'), termEl);
await caption('Need more time? One free extension of 15 minutes, no approval needed.', true);
await clickEl(card().getByRole('button', { name: /^Extend \+15 min$/ }));
await wait(2800);
await snap('extended');
await caption('Done. Ending the session cleans up after it.', true);
await clickEl(card().getByRole('button', { name: /^End session$/ }));
await wait(700);
await card().getByText('Session ended.', { exact: true }).waitFor({ timeout: 15000 });
await caption('The live pod is restarted, the grant removed, the recording stored and hashed.', true);
await wait(3200);
const myRow = card().locator('[data-testid^="breakglass-session-"]').first();
await scrollToEl(card(), 150, 900);
await hover(myRow.getByText('pod restarted'));
await wait(3400);
await snap('ended');

// ---------------------------------------------------------------- 4. the recording
chapter('The recording, checked against its hash');
await caption('Every session stays in the Break-glass card under Pods, with its recording.');
await wait(2200);
await clickEl(myRow.getByRole('button', { name: /^play$/ }));
await wait(1500);
const player = page.getByTestId('breakglass-player');
await player.waitFor();
await scrollToEl(player, 90, 1000);
await caption('The browser hashes the recording: the SHA-256 matches the session record, and that hash is anchored in Rekor.', true);
await hover(player.getByText('SHA-256 matches the session record'));
await wait(4200);
await snap('player');
await clickEl(player.getByRole('button', { name: /^Play$/ }));
await caption('It replays exactly what james saw, keystroke by keystroke.', true);
await wait(3600);
await hover(player.getByLabel('Speed'));
await page.selectOption('[aria-label="Speed"]', '4');
await caption('Change the speed, or jump to any moment.', true);
await wait(2400);
{
  const seek = player.getByLabel('Seek');
  const b = await seek.boundingBox();
  await moveTo(b.x + b.width * 0.72, b.y + b.height / 2);
  await page.waitForTimeout(FAST ? 50 : 300);
  await page.mouse.down(); await page.mouse.up();
}
await wait(2600);
await snap('player-seek');
if (STILLS) {
  // a settled frame for the essay: let it play to the end
  await player.getByRole('button', { name: /^Replay$/ }).waitFor({ timeout: 60000 });
  await still('05-player-sha-match', player);
}
await clickEl(player.getByRole('button', { name: /^Close$/ }));
await wait(600);

// ---------------------------------------------------------------- 5. glass broken (alex, then sam)
chapter('Breaking the glass, and the review after');
await caption('And when no second person is around? <b style="color:#E8A33D">alex</b> is a platform admin.');
await wait(1200);
await as('alex', `&entity=${encodeURIComponent(ENTITY)}&tab=topology&env=prod`);
await wait(1500);
await openPods();
await clickEl(page.getByText('flight-api-5c13762f-q9m4r', { exact: true }).first());
await wait(500);
await scrollToEl(page.getByText('Containers', { exact: true }).first(), 220, 1000);
await clickEl(page.getByRole('button', { name: /^Debug$/ }));
await wait(700);
const gb = page.getByTestId('breakglass-glass-broken');
await scrollToEl(gb, 380, 1200);
await typeSlow(page.locator('#bg-reason'), 'Every gate update failing; no other owner reachable. Checking flight-db from the pod.', 12);
await wait(400);
await clickEl(gb.locator('input'));
await caption('Admins can break the glass: start now, with no second person. Everyone is told, and it’s audited as critical.');
await hover(gb.locator('b').first());
await wait(4200);
await snap('glass-option');
await still('06-break-glass-option', gb, 12);
await clickEl(page.getByRole('button', { name: /^Break glass and start$/ }));
await wait(2600);
await panel().getByRole('status').waitFor();
await scrollToEl(panel().getByRole('status'), 160, 800);
await caption('The session opens at once, marked glass broken, review due.', true);
await hover(panel().getByRole('status'), 100);
await wait(2600);
await snap('glass-session');
await clickEl(panel().getByRole('button', { name: /^End session$/ }));
await panel().getByText('Session ended.', { exact: true }).waitFor({ timeout: 15000 });
await wait(1000);
await caption('Until someone else watches the recording and signs it off, the session stays review due. Here is <b style="color:#E8A33D">sam</b> again.');
await wait(1800);
await as('sam');
await wait(1200);
await hover(page.getByTestId('breakglass-queue'), 120);
await wait(2600);
await snap('review-strip');
await clickEl(page.getByTestId('breakglass-queue').locator('button').first());
await page.waitForLoadState('networkidle');
await wait(1400);
const review = page.locator('[data-testid^="breakglass-review-"]').first();
await review.waitFor();
const reviewRow = page.locator('[data-testid^="breakglass-session-"]', { has: review });
await scrollToEl(reviewRow, 300, 900);
await caption('Glass broken, review due. sam plays the recording, then writes what it showed.');
await hover(reviewRow.getByText('glass broken'));
await wait(3000);
await still('07-glass-broken-review', reviewRow, 4);
await typeSlow(review.locator('input'), 'Watched it: read-only checks on flight-db, nothing changed. Justified.', 14);
await wait(500);
await clickEl(review.getByRole('button', { name: /^Mark reviewed$/ }));
await wait(1600);
await hover(card().getByText(/^reviewed by sam$/).first());
await caption('Reviewed, and on the record for good.');
await wait(3000);
await snap('reviewed');
await caption('Break-glass in Tower: a way in on the bad day, with a second person, a recording and a clean exit.');
await wait(4200);
await caption('');
await wait(700);

const total = now();
console.log(JSON.stringify(marks, null, 1));
console.log('chapters', JSON.stringify(chapters));
console.log('total', total.toFixed(1), 'video offset of T0', ((T0 - V0) / 1000).toFixed(2));
console.log('errors:', [...errs].join('\n'));
if (!FAST) fs.writeFileSync('/tmp/tower-demo-rec-bg/chapters.raw.json', JSON.stringify({ chapters, total, offset: (T0 - V0) / 1000, marks }, null, 1));
await ctx.close();
await browser.close();
if (!FAST) console.log(fs.readdirSync(REC_DIR).filter(x => x.endsWith('.webm')).map(x => `${REC_DIR}/${x}`));
