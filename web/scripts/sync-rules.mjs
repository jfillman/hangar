// Turns Hangar's business rules (docs/policy/business-rules.md) into data for /docs/business-rules/ at build
// time, so the site page is always the document as it stands on main. Nothing here is edited by hand: change a
// rule in the document, in the same change as the code that holds it.
//
// The document's shape is what this reads: an intro, a "How to read it" strength table, then numbered "## N. Title"
// sections holding paragraphs, lists and tables. A table whose first column is ID is a table of rules; one whose
// first column is Gap is the list of rules that are weaker than they read. Anything else is kept as prose.
//
// Output (git-ignored): src/data/rules.generated.json
import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, posix, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scrubLabNames } from './lab-names.mjs';

const web = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const hangarRoot = resolve(web, '..');
const base = (process.env.SITE_BASE || '/').replace(/\/?$/, '/');
const REL = 'docs/policy/business-rules.md';
const SOURCE = `https://github.com/jfillman/hangar/blob/main/${REL}`;

// Strength keys, in the order the page shows them. A cell is placed by the first of these it starts with.
const STRENGTHS = [
  ['fails-closed', /^fails closed/i],
  ['enforced', /^enforced/i],
  ['soft', /^soft/i],
  ['display', /^display/i],
  ['convention', /^convention/i],
  ['off-here', /^off here/i],
];

const md = scrubLabNames(readFileSync(join(hangarRoot, REL), 'utf8')).replace(/\r\n/g, '\n');
const ids = new Set([...md.matchAll(/^\|\s*(?:~~)?([A-Z]+-\d+)/gm)].map((m) => m[1]));

// 1. Split into the part before the first "##", and each "## " section.
const parts = md.split(/^## /m);
const head = parts.shift().replace(/^# .*\n/, '');
const sections = parts.map((p) => {
  const nl = p.indexOf('\n');
  return { heading: p.slice(0, nl).trim(), body: p.slice(nl + 1) };
});

const take = (title) => sections.find((s) => s.heading.toLowerCase() === title)?.body ?? '';
const headBlocks = blocks(head);
const checkedPara = headBlocks.find((b) => b.type === 'p' && /^Last checked/i.test(b.text));
const checkedDates = checkedPara ? [...checkedPara.text.matchAll(/\b\d{4}-\d{2}-\d{2}\b/g)].map((m) => m[0]).sort() : [];

// The strength legend is the "How to read it" table.
const legendTable = blocks(take('how to read it')).find((b) => b.type === 'table');
const legend = (legendTable?.rows ?? []).map(([name, meaning]) => {
  const label = name.replace(/\*/g, '').trim();
  return { key: strengthKey(label), label, meaning: inline(meaning) };
});

const out = [];
const counts = Object.fromEntries(STRENGTHS.map(([k]) => [k, 0]));
for (const s of sections) {
  const m = s.heading.match(/^(\d+)\.\s+(.*)$/);
  if (!m) continue;
  const [, n, title] = m;
  const bs = blocks(s.body);
  // Section 14's table has no Strength column; its intro says every policy fails closed, and the page says so.
  const prose = bs.filter((b) => b.type !== 'table').map((b) => b.text ?? '').join(' ');
  const fallback = /fails closed/i.test(prose) ? 'Fails closed' : '';
  const section = { n: Number(n), id: anchor(s.heading), title: inline(title), blocks: [] };
  for (const b of bs) {
    if (b.type === 'table' && /^id$/i.test(b.header[0])) {
      const col = (name) => b.header.findIndex((h) => h.toLowerCase() === name);
      const [cRule, cStrength, cHeld, cPolicy, cCluster] = ['rule', 'strength', 'held by', 'policy', 'cluster'].map(col);
      const rules = b.rows.map((r) => {
        const retired = /^~~/.test(r[0]);
        const id = r[0].replace(/~~/g, '').trim();
        const strength = cStrength >= 0 ? r[cStrength] : fallback;
        const key = strengthKey(strength.replace(/\*/g, ''));
        if (!retired && key) counts[key]++;
        return {
          id,
          retired,
          rule: inline(r[cRule] ?? ''),
          text: plain(r[cRule] ?? ''),
          strength: inline(strength),
          key,
          heldBy: cHeld >= 0 ? inline(r[cHeld]) : '',
          policy: cPolicy >= 0 ? inline(r[cPolicy]) : '',
          cluster: cCluster >= 0 ? inline(r[cCluster]) : '',
        };
      });
      section.blocks.push({ type: 'rules', rules });
    } else if (b.type === 'table' && /^gap$/i.test(b.header[0])) {
      section.blocks.push({
        type: 'gaps',
        gaps: b.rows.map(([gap, rules, today]) => ({ gap: inline(gap), rules: [...rules.matchAll(/[A-Z]+-\d+/g)].map((x) => x[0]), today: inline(today) })),
      });
    } else {
      section.blocks.push({ type: 'html', html: html(b) });
    }
  }
  out.push(section);
}

const total = Object.values(counts).reduce((a, b) => a + b, 0);
const data = {
  source: SOURCE,
  docsRoute: 'docs/hangar/policy/business-rules/',
  commit: git(['log', '-1', '--format=%h', '--', REL]),
  intro: headBlocks.filter((b) => b !== checkedPara).map(html),
  checked: checkedPara ? html(checkedPara) : '',
  checkedOn: checkedDates.at(-1) ?? null,
  legend,
  total,
  counts,
  sections: out,
};
mkdirSync(join(web, 'src/data'), { recursive: true });
writeFileSync(join(web, 'src/data/rules.generated.json'), JSON.stringify(data, null, 2) + '\n');
console.log(`sync-rules: ${total} rules in ${out.length} sections from ${REL}`);

// ---------------------------------------------------------------------------------------

// Paragraphs, lists and tables, which is all the document uses.
function blocks(text) {
  const out = [];
  let cur = null;
  const flush = () => { if (cur) out.push(cur); cur = null; };
  for (const line of text.split('\n')) {
    if (!line.trim()) { flush(); continue; }
    if (/^#/.test(line)) { flush(); continue; }
    if (/^\|/.test(line)) {
      const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      if (cur?.type !== 'table') { flush(); cur = { type: 'table', header: cells, rows: [] }; }
      else if (!cells.every((c) => /^:?-+:?$/.test(c))) cur.rows.push(cells);
      continue;
    }
    const li = line.match(/^(\s*)(?:[-*]|\d+\.)\s+(.*)$/);
    if (li && !li[1]) {
      const type = /^\s*\d+\./.test(line) ? 'ol' : 'ul';
      if (cur?.type !== type) { flush(); cur = { type, items: [] }; }
      cur.items.push(li[2]);
      continue;
    }
    if (cur?.type === 'ul' || cur?.type === 'ol') { cur.items[cur.items.length - 1] += ' ' + line.trim(); continue; }
    if (cur?.type !== 'p') { flush(); cur = { type: 'p', text: '' }; }
    cur.text += (cur.text ? ' ' : '') + line.trim();
  }
  flush();
  return out;
}

function html(b) {
  if (b.type === 'p') return `<p>${inline(b.text)}</p>`;
  if (b.type === 'ul' || b.type === 'ol') return `<${b.type}>${b.items.map((i) => `<li>${inline(i)}</li>`).join('')}</${b.type}>`;
  const row = (cells, tag) => `<tr>${cells.map((c) => `<${tag}>${inline(c)}</${tag}>`).join('')}</tr>`;
  return `<div class="table-wrap"><table><thead>${row(b.header, 'th')}</thead><tbody>${b.rows.map((r) => row(r, 'td')).join('')}</tbody></table></div>`;
}

// Inline Markdown: code, links, bold, italic and strike-through. Rule IDs become links to their rows, and ISO
// dates are written month first, as everywhere on the site.
function inline(text) {
  return text.split(/(\[(?:[^\]`]|`[^`]*`)*\]\([^)\s]*\))/).map((seg, j) => {
    if (!(j % 2)) return spans(seg);
    const [, label, target] = seg.match(/^\[(.*)\]\(([^)]*)\)$/);
    return `<a href="${esc(link(target))}">${spans(label, false)}</a>`;
  }).join('');
}

function spans(text, refs = true) {
  return text.split(/(`[^`]*`)/).map((part, i) => {
    if (i % 2) return `<code>${esc(part.slice(1, -1))}</code>`;
    const out = esc(part)
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*\w])\*([^*]+)\*(?!\w)/g, '$1<em>$2</em>')
      .replace(/~~([^~]+)~~/g, '<s>$1</s>')
      .replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g, (d) => shortDate(d));
    return refs ? out.replace(/\b[A-Z]+-\d+\b/g, (id) => (ids.has(id) ? `<a class="rule-ref" href="#${id.toLowerCase()}">${id}</a>` : id)) : out;
  }).join('');
}

function plain(text) {
  return text.replace(/[`*~]/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
}

// Anchors inside the document point at its own sections; other relative links point at the published docs page.
function link(target) {
  if (/^([a-z][a-z0-9+.-]*:|\/\/)/i.test(target)) return target;
  if (target.startsWith('#')) {
    const s = sections.find((x) => anchor(x.heading) === target.slice(1) || githubAnchor(x.heading) === target.slice(1));
    return s ? '#' + anchor(s.heading) : SOURCE + target;
  }
  const [path, hash] = target.split('#');
  const rel = posix.normalize(posix.join(posix.dirname(REL), path)).replace(/^docs\//, '');
  const slug = rel.replace(/\.md$/, '').replace(/\/?(README|index)$/i, '').toLowerCase().replace(/_/g, '-');
  return `${base}docs/hangar/${slug ? slug + '/' : ''}${hash ? '#' + hash : ''}`;
}

function anchor(heading) {
  return heading.replace(/^\d+\.\s+/, '').toLowerCase().replace(/[`]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}
function githubAnchor(heading) {
  return heading.toLowerCase().replace(/[^\w\s-]/g, '').trim().replace(/\s/g, '-');
}

function strengthKey(label) {
  return STRENGTHS.find(([, re]) => re.test(label.trim()))?.[0] ?? '';
}

function shortDate(iso) {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function git(args) {
  try { return execFileSync('git', args, { cwd: hangarRoot, encoding: 'utf8' }).trim() || null; } catch { return null; }
}
