import { defineConfig } from 'astro/config';

// SITE_URL and SITE_BASE come from actions/configure-pages in CI, so the same build works
// at jfillman.github.io/hangar/ before the custom domain is live and at the root after.
export default defineConfig({
  site: process.env.SITE_URL || 'https://hangarplatform.dev',
  base: process.env.SITE_BASE || '/',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  markdown: {
    // Code in the docs follows the page theme; mermaid blocks are drawn in the browser.
    syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] },
    shikiConfig: { themes: { light: 'github-light', dark: 'github-dark' }, defaultColor: false },
  },
});
