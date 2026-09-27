import manifest from './docs.generated.json';
import { products } from './products';

export type NavItem = { label: string; route?: string; children?: NavItem[]; more?: boolean };
export type DocSet = { id: string; repo: string; pages: number; nav: NavItem[]; home: string };

export const docSets = manifest as DocSet[];

export const docSet = (id: string) => docSets.find((d) => d.id === id);
export const productOf = (id: string) => products.find((p) => p.key === id);

// Where to start in each product's docs, when the nav has a user or admin guide.
export function guides(set: DocSet) {
  const find = (re: RegExp) => set.nav.find((n) => re.test(n.label));
  const first = (n?: NavItem) => (n?.route ? n.route : n?.children?.[0]?.route);
  return { user: first(find(/^user/i)), admin: first(find(/^admin/i)) };
}
