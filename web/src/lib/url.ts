// Every internal link goes through here so the site works under a base path.
const base = import.meta.env.BASE_URL.replace(/\/$/, '');

export const u = (path: string) => `${base}/${path.replace(/^\//, '')}`;

export const gh = (repo: string, path = '') =>
  `https://github.com/jfillman/${repo}${path ? `/blob/main/${path.replace(/^\//, '')}` : ''}`;

export const ghTree = (repo: string, path: string) => `https://github.com/jfillman/${repo}/tree/main/${path.replace(/^\//, '')}`;
