// Stills of Tower's release record for the essay "The release record, and the users I haven't met".
//   npm run dev                                   # leave running
//   node stills-release-record.mjs <out-dir>      # 2x PNGs, cropped to each panel
// The essay's copies live in web/public/media/release-record/ (renamed, see that page's source).
import { chromium } from 'playwright-core';
const out = process.argv[2] ?? '/tmp/release-record-stills';
import fs from 'fs';
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
const box = async (loc) => { await loc.scrollIntoViewIfNeeded(); const r = await loc.boundingBox(); const s = await p.evaluate(() => window.scrollY); return { ...r, y: r.y + s }; };
const shot = async (name, top, bottom) => {
  await p.screenshot({ path: `${out}/${name}.png`, fullPage: true, clip: { x: 12, y: top, width: 1416, height: bottom - top } });
  console.log(name, Math.round(top), Math.round(bottom));
};
await p.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
await p.waitForTimeout(1200);
await p.getByText('flight-api', { exact: true }).first().click(); await p.waitForTimeout(1500);
await p.locator('button', { hasText: /^Releases/i }).first().click(); await p.waitForTimeout(2500);
// 1. the three cards and the mode bar
const nr = await box(p.getByText('Next release', { exact: true }).first());
const ae = await box(p.getByText(/Autoland eligibility/).first());
await shot('01-cards', nr.y - 34, ae.y + ae.height + 14);
// 2. the draft
const promote = await box(p.getByRole('button', { name: /^Promote 1\.8\.1/ }).first());
const foot = await box(p.getByText(/^Scope, candidates and readiness are computed/).first());
await shot('02-draft', promote.y - 22, foot.y + foot.height + 20);
// 3. notes and owner
await p.getByText(/Notes and owner/).first().click(); await p.waitForTimeout(800);
const no = await box(p.getByText(/Notes and owner/).first());
const sv = await box(p.getByText(/^Saved as a commit to/).first());
await shot('03-notes', no.y - 14, sv.y + sv.height + 14);
await p.getByText(/Notes and owner/).first().click(); await p.waitForTimeout(500);
// 4. a sealed record: header and release notes and sign-off
await p.locator('button', { hasText: /^DOGWOOD$/ }).first().click(); await p.waitForTimeout(1800);
const hd = await box(p.getByText(/Release record · flight-api/i).first());
const wc = await box(p.getByText('What changed', { exact: true }).first());
await shot('04-record-head', hd.y - 24, wc.y - 24);
const rn = await box(p.getByText(/Release notes and sign-off/i).first());
const ar = await box(p.getByText(/^After release$/i).first());
await shot('05-signoff', rn.y - 22, ar.y - 26);
// 5. an outcome
await p.locator('button', { hasText: /^CEDAR$/ }).first().click(); await p.waitForTimeout(1800);
const oc = await box(p.getByText(/^Outcome$/).first());
const rn2 = await box(p.getByText(/Release notes and sign-off/i).first());
await shot('06-outcome', oc.y - 22, rn2.y - 26);
await b.close();
