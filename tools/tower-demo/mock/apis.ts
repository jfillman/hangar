import * as F from './fixtures';

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const text = (body: string) => new Response(body, { status: 200, headers: { 'Content-Type': 'text/plain' } });

const unknown = new Set<string>();
function miss(url: string) {
  if (!unknown.has(url)) {
    unknown.add(url);
    console.warn('[demo] unmocked', url);
  }
  return json({ error: 'not in demo data' }, 404);
}

async function route(input: string, init?: RequestInit): Promise<Response> {
  const url = new URL(input, 'http://demo.local');
  const p = url.pathname;
  const q = url.searchParams;
  const body = init?.body ? JSON.parse(String(init.body)) : undefined;
  const method = (init?.method ?? 'GET').toUpperCase();
  await new Promise(r => setTimeout(r, 120));

  // kubernetes proxy
  if (p.startsWith('/api/kubernetes/proxy')) {
    const kp = p.slice('/api/kubernetes/proxy'.length) + url.search;
    const cluster = (init?.headers as any)?.['Backstage-Kubernetes-Cluster'] ?? 'dev';
    if (method !== 'GET') return json({ metadata: { name: 'ok' } });
    if (kp.includes('/services/prometheus') || kp.includes(':9090/proxy')) {
      const inner = new URL('http://x' + kp.slice(kp.indexOf('/proxy') + 6));
      const query = inner.searchParams.get('query') ?? '';
      if (inner.pathname.endsWith('query_range')) {
        return json(F.promRange(query, Number(inner.searchParams.get('start')), Number(inner.searchParams.get('end')), Number(inner.searchParams.get('step'))));
      }
      return json(F.promInstant(query));
    }
    if (kp.includes('results.tekton.dev')) return json({ records: [], nextPageToken: '' });
    if (kp.includes('/log?')) return text(F.taskLog(kp));
    const tk = F.tektonFor(kp);
    if (tk) return json(tk);
    const raw = F.rawNamespaceList(kp.split('?')[0], cluster);
    if (raw) return json(raw);
    return miss(input);
  }

  if (p.startsWith('/api/argocd/find/name/')) {
    return json(F.argoAppFor(decodeURIComponent(p.split('/').pop()!)));
  }

  if (p.startsWith('/api/glidepath')) {
    const sub = p.slice('/api/glidepath'.length);
    switch (sub) {
      case '/head': return json(F.repoHead(q.get('repo')!, q.get('ref') ?? undefined));
      case '/images': return json(F.imagesFor(q.get('repo')!));
      case '/pipeline-order': return json(F.pipelineOrder);
      case '/provenance': return json(F.provenanceFor(q.get('image')!));
      case '/deploy-history': return json(F.deployHistoryFor(body.appName, body.environments));
      case '/promote': return json({ mode: 'pr', prUrl: `https://github.com/${F.OWNER}/gitops-prod/pull/215`, alreadyOpen: false });
      case '/argo/refresh':
      case '/argo/sync': return json({ ok: true });
      case '/release-record': return json(F.releaseRecordFor(q), 404);
      case '/config/cicd':
        if (method === 'GET') return json(F.cicdFor(q.get('repo') ?? q.get('appName') ?? 'storefront'));
        return json({ prUrl: `https://github.com/${F.OWNER}/storefront/pull/192`, alreadyOpen: false });
      case '/config':
        if (method === 'GET') return json(F.appConfigFor(q.get('appName') ?? q.get('repo') ?? 'storefront', q.get('env') ?? 'dev', q.get('cluster') ?? 'dev'));
        return json({ prUrl: `https://github.com/${F.OWNER}/gitops-${body?.env === 'prod' ? 'prod' : 'dev'}/pull/${body?.env === 'prod' ? 216 : 78}`, alreadyOpen: false });
      case '/config/platform-envs': return json({ envs: ['dev', 'staging'] });
      case '/config/platform-env':
        if (method === 'GET') { const c = F.appConfigFor(q.get('appName') ?? 'storefront', q.get('env') ?? 'dev', 'dev'); return json({ repo: `${F.OWNER}/${q.get('appName')}`, path: `platform/${q.get('env') ? 'envs/' + q.get('env') : 'pr-env'}.yaml`, values: c.values, raw: c.raw }); }
        return json({ prUrl: `https://github.com/${F.OWNER}/storefront/pull/193`, alreadyOpen: false });
      case '/config/env-xr': return json({ env: q.get('env'), path: `envs/${q.get('env')}.yaml`, configMapGenerator: true });
      case '/config/configmap-files':
        if (method === 'GET') return json({ cluster: q.get('cluster'), env: q.get('env'), path: `apps/${q.get('appName')}/${q.get('env')}/files`, configMapName: `${q.get('appName')}-files`, files: [{ name: 'app.properties', content: 'checkout.currency=CAD\ncheckout.maxItems=50\n' }] });
        return json({ prUrl: `https://github.com/${F.OWNER}/gitops-dev/pull/79`, alreadyOpen: false });
      case '/config/schema':
      case '/config/cicd/schema': return json({ type: 'object' });
      default:
        return miss(input);
    }
  }
  return miss(input);
}

export const apis = {
  discovery: { getBaseUrl: async (id: string) => `/api/${id}` },
  fetch: { fetch: (input: any, init?: RequestInit) => route(typeof input === 'string' ? input : input.url, init) },
  catalog: {
    getEntities: async () => ({ items: F.entities }),
    getEntityByRef: async (ref: any) => {
      const name = typeof ref === 'string' ? ref.split('/').pop() : ref.name;
      return F.entities.find(e => e.metadata.name === name);
    },
  },
  starred: {
    starredEntitie$: () => ({ subscribe: (fn: any) => { const v = typeof fn === 'function' ? fn : fn.next; v?.(new Set(['component:default/storefront'])); return { unsubscribe() {} }; } }),
    toggleStarred: async () => {},
    isStarred: async () => false,
  },
  notifications: {
    getNotifications: async (opts: any) => ({ notifications: F.notificationsFor(opts?.search), totalCount: 9 }),
    getStatus: async () => ({ unread: 0, read: 0 }),
    notification$: () => ({ subscribe: () => ({ unsubscribe() {} }) }),
  },
  kubernetes: {
    proxy: async ({ clusterName, path }: { clusterName: string; path: string }) => {
      if (path.includes('/events')) {
        const m = path.match(/namespaces\/app-([a-z-]+?)-(dev|staging|prod)\//);
        const items = m ? eventsFor(m[1], m[2]) : [];
        return json({ items });
      }
      if (path.match(/^\/api\/v1\/namespaces\/[^/]+$/)) {
        const name = path.split('/').pop();
        return json({ apiVersion: 'v1', kind: 'Namespace', metadata: { name, labels: { 'hangar.io/app': name?.replace(/^app-|-(dev|staging|prod)$/g, ''), 'pod-security.kubernetes.io/enforce': 'restricted' } }, status: { phase: 'Active' } });
      }
      if (path.includes('clusterrolebindings')) return json({ items: [] });
      return json({ items: [] });
    },
    getClusters: async () => [{ name: 'dev' }, { name: 'prod' }],
  },
  kubernetesProxy: {
    getPodLogs: async ({ podName }: any) => ({
      text: [0, 1, 2, 3, 4, 5, 6, 7].map(i => `${new Date(Date.now() - (8 - i) * 4000).toISOString()} INFO  GET /api/products 200 ${12 + i * 3}ms`).join('\n') + `\n${new Date().toISOString()} INFO  ${podName} ready`,
    }),
    getEventsByInvolvedObjectName: async () => [],
  },
};

function eventsFor(appName: string, env: string) {
  const app = F.appByName(appName);
  if (!app) return [];
  const ns = `app-${appName}-${env}`;
  const ev = (min: number, reason: string, message: string, kind = 'Rollout', type = 'Normal') => ({
    metadata: { name: `${appName}.${reason}.${min}`, namespace: ns },
    type, reason, message, count: 1,
    involvedObject: { kind, name: appName, namespace: ns },
    firstTimestamp: F.ago(min), lastTimestamp: F.ago(min),
  });
  if (app.canary?.env === env) {
    return [
      ev(6, 'RolloutPaused', 'Rollout is paused (CanaryPauseStep)'),
      ev(7, 'SetWeight', 'Set weight to 40'),
      ev(8, 'AnalysisRunRunning', `Background Analysis Run '${appName}-14' Status New: 'Running'`),
      ev(9, 'SetWeight', 'Set weight to 20'),
      ev(9, 'RolloutUpdated', `Rollout updated to revision 14`),
      ev(9, 'ScalingReplicaSet', 'Scaled up ReplicaSet to 2', 'Rollout'),
    ];
  }
  return [ev(app.versions[env].deployedMin, 'RolloutCompleted', 'Rollout completed update to revision 13')];
}
