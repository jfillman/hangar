// Shared by the scripts that bring repo docs onto the site (sync-docs, sync-rules).
// The home lab's cluster names are an implementation detail of where Hangar happens to run, so the site says
// "dev" and "prod" instead. Link targets are left alone so they still resolve.
export function scrubLabNames(md) {
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
