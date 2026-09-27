// Pulls each Hangar product's user and admin docs into the site at build time, so the docs
// keep living next to the code they describe (and keep working as Backstage TechDocs), and
// the site only renders them. Nothing here is edited by hand: fix a page in its own repo.
//
// Where the repos come from:
//   - hangar is this repo.
//   - the others are looked up under DOCS_REPOS_DIR (the Pages workflow checks them out
//     there), falling back to sibling checkouts next to this repo for local builds.
// A repo that is not found is skipped with a warning, so a partial local build still works.
//
// Output (all git-ignored):
//   src/docs.generated/<product>/**.md   pages with frontmatter, links rewritten for the site
//   public/docs-assets/<product>/**      images and standalone HTML pages the pages link to
//   src/data/docs.generated.json         per-product navigation, taken from each mkdocs.yml
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, posix, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';

const web = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const hangarRoot = resolve(web, '..');
const reposDir = process.env.DOCS_REPOS_DIR ? resolve(process.env.DOCS_REPOS_DIR) : resolve(hangarRoot, '..');
const base = (process.env.SITE_BASE || '/').replace(/\/?$/, '/');
const OWNER = 'jfillman';

// The order here is the order on /docs/.
const SOURCES = [
  { id: 'glidepath', repo: 'glidepath', docs: 'docs' },
  { id: 'airframe', repo: 'airframe', docs: 'docs' },
  { id: 'tower', repo: 'tower', docs: 'docs' },
  { id: 'autopilot', repo: 'autopilot', docs: 'docs' },
  { id: 'apron', repo: 'apron', files: ['README.md'] },
  {
    id: 'hangar',
    repo: 'hangar',
    docs: 'docs',
    // Runbooks for one particular home lab rather than for the platform.
    skip: ['local-clusters.md', 'cluster-provisioning.md', 'kind-prod-infisical-migration-plan.md'],
  },
];
// Never published: history, unreviewed drafts, generated diagram folders, and brand pages
// (the brand has its own place on the site).
const SKIP_DIRS = new Set(['archive', 'drafts', 'brand', 'diagrams', 'node_modules']);
// Images, and standalone pages such as the illustrated guides, are copied as they are.
const ASSET = /\.(svg|png|jpe?g|gif|webp|html)$/i;

const outPages = join(web, 'src/docs.generated');
const outAssets = join(web, 'public/docs-assets');
for (const d of [outPages, outAssets]) { rmSync(d, { recursive: true, force: true }); mkdirSync(d, { recursive: true }); }

const manifest = [];
let total = 0;

for (const src of SOURCES) {
  const root = src.repo === 'hangar' ? hangarRoot : join(reposDir, src.repo);
  if (!existsSync(root)) { console.warn(`sync-docs: ${src.repo} not found at ${root}, skipped`); continue; }

  // 1. Which files are pages, and where each one lives on the site.
  const files = src.files ?? walk(join(root, src.docs)).map((f) => posix.join(src.docs, f));
  const pages = new Map(); // repo-relative path -> page
  for (const rel of files) {
    const inDocs = src.docs ? posix.relative(src.docs, rel) : '';
    if (src.skip?.includes(inDocs)) continue;
    pages.set(rel, { rel, slug: slugFor(src, rel) });
  }
  // index.md and README.md in the same folder want the same slug; README gives way.
  const taken = new Set();
  for (const p of [...pages.values()].sort((a, b) => /index\.md$/.test(b.rel) - /index\.md$/.test(a.rel))) {
    if (taken.has(p.slug)) p.slug = posix.join(p.slug, 'contents');
    taken.add(p.slug);
  }
  for (const p of pages.values()) p.route = `docs/${src.id}/${p.slug ? p.slug + '/' : ''}`;

  // 2. Navigation, from mkdocs.yml when there is one.
  const navLabels = new Map();
  let nav = [];
  const mk = join(root, 'mkdocs.yml');
  if (existsSync(mk) && src.docs) {
    const conf = yaml.load(readFileSync(mk, 'utf8'), { json: true, schema: yaml.JSON_SCHEMA }) || {};
    nav = toNav(conf.nav || [], src, pages, navLabels);
  }

  // 3. Write each page with its links pointed at the site, or at GitHub for anything that
  //    is not a published page.
  const list = [];
  for (const p of pages.values()) {
    let md = readFileSync(join(root, p.rel), 'utf8').replace(/^---\n[\s\S]*?\n---\n/, '');
    md = rewrite(md, src, root, p, pages);
    md = scrubLabNames(md);
    const title = firstHeading(md) || navLabels.get(p.rel) || posix.basename(p.slug || src.id);
    const front = {
      title,
      product: src.id,
      route: p.route,
      source: `https://github.com/${OWNER}/${src.repo}/blob/main/${p.rel}`,
    };
    const out = join(outPages, src.id, (p.slug || 'index') + '.md');
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, `---\n${yaml.dump(front, { lineWidth: -1 })}---\n\n${md}`);
    list.push({ route: p.route, title, rel: p.rel });
  }
  // Pages that exist but that mkdocs.yml does not list still get a home in the sidebar.
  const listed = new Set(navLabels.keys());
  const rest = list.filter((p) => !listed.has(p.rel) && p.route !== `docs/${src.id}/`).sort((a, b) => a.route.localeCompare(b.route));
  if (rest.length) nav.push({ label: nav.length ? 'More pages' : 'Pages', children: rest.map((p) => ({ label: p.title, route: p.route })), more: nav.length > 0 });

  manifest.push({ id: src.id, repo: src.repo, pages: list.length, nav, home: `docs/${src.id}/` });
  total += list.length;
}

mkdirSync(join(web, 'src/data'), { recursive: true });
writeFileSync(join(web, 'src/data/docs.generated.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(`sync-docs: ${total} pages from ${manifest.map((m) => `${m.id} (${m.pages})`).join(', ')}`);

// ---------------------------------------------------------------------------------------

function walk(dir, prefix = '') {
  if (!existsSync(dir)) return [];
  const out = [];
  for (const name of readdirSync(dir).sort()) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) { if (!SKIP_DIRS.has(name)) out.push(...walk(full, posix.join(prefix, name))); }
    else if (name.endsWith('.md')) out.push(posix.join(prefix, name));
  }
  return out;
}

function slugFor(src, rel) {
  const inDocs = src.docs ? posix.relative(src.docs, rel) : rel;
  const noExt = inDocs.replace(/\.md$/, '');
  const leaf = posix.basename(noExt);
  const dir = posix.dirname(noExt) === '.' ? '' : posix.dirname(noExt);
  if (/^(index|README)$/i.test(leaf)) return dir.toLowerCase();
  return noExt.toLowerCase().replace(/_/g, '-');
}

function toNav(items, src, pages, labels) {
  const out = [];
  for (const item of items) {
    const [label, value] = typeof item === 'string' ? [null, item] : Object.entries(item)[0];
    if (Array.isArray(value)) {
      const children = toNav(value, src, pages, labels);
      if (children.length) out.push({ label, children });
    } else if (typeof value === 'string' && !/^https?:/.test(value)) {
      const page = pages.get(posix.join(src.docs, value));
      if (!page) continue;
      labels.set(page.rel, label || value);
      out.push({ label: label || value, route: page.route });
    }
  }
  return out;
}

function firstHeading(md) {
  let fenced = false;
  for (const line of md.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    if (!fenced && /^# /.test(line)) return line.slice(2).replace(/[`*]/g, '').trim();
  }
  return '';
}

// The home lab's cluster names are an implementation detail of where Hangar happens to run, so the site says
// "dev" and "prod" instead. Link targets are left alone so they still resolve.
function scrubLabNames(md) {
  const LAB_NAMES = [
    [/gitops-cluster-kind-prod/g, 'gitops-cluster-prod'],
    [/kind-prod/g, 'prod'],
    [/kiac-dev/g, 'dev'],
    [/kind-man/g, 'mgmt'],
    [/\bkiac\.local\b/g, 'lab.internal'],
  ];
  return md.split(/(\]\([^)]*\)|\b(?:src|href)="[^"]*")/).map((part, i) =>
    i % 2 ? part : LAB_NAMES.reduce((t, [re, to]) => t.replace(re, to), part)).join('');
}

// Rewrites link and image targets outside fenced code blocks.
function rewrite(md, src, root, page, pages) {
  const fix = (target) => resolveTarget(target, src, root, page, pages);
  let fenced = false;
  return md.split('\n').map((line) => {
    if (/^\s*(```|~~~)/.test(line)) { fenced = !fenced; return line; }
    if (fenced) return line;
    return line
      .replace(/(!?\[[^\]]*\]\()(<[^>]+>|[^)\s]+)((?:\s+"[^"]*")?\))/g, (_, a, t, b) => a + fix(t.replace(/^<|>$/g, '')) + b)
      .replace(/^(\s*\[[^\]]+\]:\s*)(\S+)/, (_, a, t) => a + fix(t))
      .replace(/(<img\b[^>]*\bsrc=")([^"]+)(")/g, (_, a, t, b) => a + fix(t) + b);
  }).join('\n');
}

function resolveTarget(target, src, root, page, pages) {
  if (/^([a-z][a-z0-9+.-]*:|#|\/\/)/i.test(target)) return target;
  const [path, hash = ''] = target.split('#');
  const anchor = hash ? '#' + hash : '';
  if (!path) return target;
  const rel = path.startsWith('/') ? path.slice(1) : posix.normalize(posix.join(posix.dirname(page.rel), decodeURI(path)));
  if (rel.startsWith('..')) {
    // Sibling repos in the family are linked as ../<repo>/<path> in a few places.
    const m = rel.match(/^\.\.\/([^/]+)\/?(.*)$/);
    return m ? `https://github.com/${OWNER}/${m[1]}${m[2] ? '/blob/main/' + m[2] : ''}${anchor}` : target;
  }
  for (const cand of [rel, rel + '.md', posix.join(rel, 'index.md'), posix.join(rel, 'README.md')]) {
    const hit = pages.get(cand);
    if (hit) return base + hit.route + anchor;
  }
  const full = join(root, rel);
  if (ASSET.test(rel) && existsSync(full) && statSync(full).isFile()) {
    const out = join(outAssets, src.id, rel);
    mkdirSync(dirname(out), { recursive: true });
    cpSync(full, out);
    return `${base}docs-assets/${src.id}/${rel}`;
  }
  const kind = existsSync(full) && statSync(full).isDirectory() ? 'tree' : 'blob';
  return `https://github.com/${OWNER}/${src.repo}/${kind}/main/${rel}${anchor}`;
}
