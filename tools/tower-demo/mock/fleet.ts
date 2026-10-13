// The fleet-wide side of the demo: what the Ops Wall reads across every app at once (all PipelineRuns on
// the Tekton cluster, Glidepath's release records, Tekton Results history, dora-exporter's series), and a
// new service (checkin-api) half-way through provisioning for the Services page's Provisioning tab.
import { APPS, OWNER, ago, allRunsFor, makeRun, shaFor, type DemoApp } from './fixtures';

const NOW = Date.now();

// ---------- checkin-api, being provisioned ----------
// Requested 11 minutes ago through the scaffolder; Crossplane has made its repos, secrets and pipeline
// namespace, and the first build is running. It is not in the catalog yet, so it is not a service card.
export const PROVISIONING_APP = 'checkin-api';
const PROV_NS = 'team-skyport';
const provApp = { name: PROVISIONING_APP, versions: {}, replicas: {} } as unknown as DemoApp;
const provBuild = makeRun({ pipeline: 'build', app: provApp, ver: '0.1.0', sha: '2b7f0e1', startMin: 2, phase: 'running', slug: 'early-wren', chain: 'c-2b7f', stepIndex: 0, author: 'glidepath-bot' });

const cond = (type: string, status: string, min: number, reason = status === 'True' ? 'Available' : 'Creating') =>
  ({ type, status, reason, lastTransitionTime: ago(min) });
const managed = (name: string, kind: string, readyMin: number, extra: any = {}) => ({
  kind, metadata: { name, annotations: { 'crossplane.io/external-name': name } },
  status: { conditions: [cond('Ready', 'True', readyMin), cond('Synced', 'True', readyMin, 'ReconcileSuccess')], ...extra },
});

export function provisioningRoute(kp: string): any | undefined {
  const path = kp.split('?')[0];
  if (path.startsWith('/apis/catalog.hangar.io/v1alpha1/') && !path.includes('/namespaces/')) {
    if (!path.endsWith('/pythonapplications')) return { items: [] };
    return {
      items: [{
        kind: 'PythonApplication',
        metadata: {
          name: PROVISIONING_APP, namespace: PROV_NS, creationTimestamp: ago(9),
          annotations: { 'terasky.backstage.io/source-info': JSON.stringify({ gitRepo: `github.com?owner=${OWNER}&repo=gitops-cluster-dev-tenants` }) },
        },
        spec: {
          devCluster: 'dev',
          crossplane: { resourceRefs: [
            { kind: 'Repository', name: `${PROVISIONING_APP}-src` },
            { kind: 'Repository', name: `${PROVISIONING_APP}-gitops` },
            { kind: 'RepositoryFile', name: `${PROVISIONING_APP}-cicd-yaml` },
            { kind: 'RepositoryFile', name: `${PROVISIONING_APP}-catalog-info` },
            { kind: 'TektonCICD', name: `${PROVISIONING_APP}-cicd` },
          ] },
        },
        status: { conditions: [cond('DevClusterReady', 'True', 8), cond('CicdOnboarded', 'True', 5), cond('Synced', 'True', 8, 'ReconcileSuccess'), cond('Ready', 'False', 9)] },
      }],
    };
  }
  if (path.includes(`/namespaces/${PROV_NS}/repositories`)) {
    return { items: ['src', 'gitops'].map((r, i) => managed(`${PROVISIONING_APP}-${r}`, 'Repository', 8 - i, {
      atProvider: { htmlUrl: `https://github.com/${OWNER}/${r === 'src' ? PROVISIONING_APP : `gitops-${PROVISIONING_APP}`}`, fullName: `${OWNER}/${r === 'src' ? PROVISIONING_APP : `gitops-${PROVISIONING_APP}`}` },
    })) };
  }
  if (path.includes(`/namespaces/${PROV_NS}/repositoryfiles`)) {
    return { items: ['cicd-yaml', 'catalog-info'].map(f => managed(`${PROVISIONING_APP}-${f}`, 'RepositoryFile', 7)) };
  }
  if (path.includes(`/namespaces/${PROV_NS}/secretstores`)) {
    return { items: [{ ...managed(`${PROVISIONING_APP}-secrets`, 'SecretStore', 6), metadata: { name: `${PROVISIONING_APP}-secrets`, namespace: PROV_NS, creationTimestamp: ago(9) }, spec: { appRef: { name: PROVISIONING_APP } } }] };
  }
  if (path.includes(`/namespaces/${PROV_NS}/tektoncicds`)) return { items: [managed(`${PROVISIONING_APP}-cicd`, 'TektonCICD', 5)] };
  if (path.includes(`/namespaces/${PROV_NS}/projects`)) {
    return { items: [{ metadata: { name: `${PROVISIONING_APP}-secrets`, annotations: { 'crossplane.io/external-name': '7c1e04aa-skyport-checkin' } } }] };
  }
  if (path === `/apis/argoproj.io/v1alpha1/namespaces/argocd/applications/${PROVISIONING_APP}-cicd`) {
    return { status: { sync: { status: 'Synced' }, health: { status: 'Healthy' } } };
  }
  if (path === `/apis/tekton.dev/v1/namespaces/app-${PROVISIONING_APP}-cicd/pipelineruns`) return { items: [provBuild.pr] };
  if (path === `/apis/tekton.dev/v1/namespaces/app-${PROVISIONING_APP}-cicd/taskruns`) return { items: provBuild.taskRuns };
  if (path === `/apis/argoproj.io/v1alpha1/namespaces/app-${PROVISIONING_APP}-dev/rollouts`) return { items: [] };
  return undefined;
}

const prUrl = (repo: string, n: number) => `https://github.com/${OWNER}/${repo}/pull/${n}`;
export const provisioningPrs = () => [
  { repo: 'source', number: 1, title: `Onboarding: re-sync ${PROVISIONING_APP} pipeline files`, url: prUrl(PROVISIONING_APP, 1), state: 'merged', mergedAt: ago(4), createdAt: ago(6), updatedAt: ago(4), draft: false, labels: [], author: 'glidepath-bot' },
  { repo: 'gitops', number: 1, title: `Onboarding: ${PROVISIONING_APP} environments`, url: prUrl(`gitops-${PROVISIONING_APP}`, 1), state: 'merged', mergedAt: ago(5), createdAt: ago(6), updatedAt: ago(5), draft: false, labels: [], author: 'glidepath-bot' },
];
export const provisioningRequestPr = () => ({ pr: { number: 42, url: prUrl('gitops-cluster-dev-tenants', 42), state: 'merged', createdAt: NOW - 11 * 60_000, mergedAt: NOW - 9.6 * 60_000 } });

// Finished provisions the backend remembers, and the medians the steps are timed against.
export function provisioningHistory(path: string) {
  const step = (id: string, seconds: number) => ({ id, seconds });
  const run = (service: string, kind: string, daysAgo: number, scale: number) => {
    const steps = [step('merge', 140 * scale), step('request', 50 * scale), step('cluster', 70 * scale), step('repos', 40 * scale), step('cicd', 150 * scale),
      step('onboarding', 120 * scale), step('secrets', 60 * scale), step('build', 420 * scale), step('catalog', 90 * scale), step('running', 75 * scale)].map(s => ({ ...s, seconds: Math.round(s.seconds) }));
    const total = steps.reduce((a, s) => a + s.seconds, 0) * 0.82;
    const completedAt = NOW - daysAgo * 86_400_000;
    return { service, kind, startedAt: completedAt - total * 1000, completedAt, totalSeconds: Math.round(total), steps };
  };
  if (path.endsWith('/runs')) {
    return { runs: [run('gate-api', 'NodeJSApplication', 3.2, 0.95), run('baggage-api', 'PythonApplication', 9.5, 1.1), run('boarding-api', 'NodeJSApplication', 14, 1.0), run('flight-api', 'SpringBootApplication', 16, 1.3)] };
  }
  const med = (median: number) => ({ median, samples: 4 });
  const all = { merge: med(140), request: med(50), cluster: med(70), repos: med(40), cicd: med(150), onboarding: med(120), secrets: med(60), build: med(430), catalog: med(90), running: med(75) };
  return { all, byKind: { PythonApplication: all } };
}

// ---------- every PipelineRun on the Tekton cluster ----------
export function fleetPipelineRuns() {
  const items: any[] = [provBuild.pr];
  for (const a of APPS) items.push(...allRunsFor(a.name).items);
  // Tekton Results prunes finished runs after about an hour, so the cluster only holds the recent ones.
  return { items: items.filter(r => !r.status.completionTime || NOW - Date.parse(r.status.completionTime) < 70 * 60_000) };
}
export function fleetTaskRuns(selector: string) {
  const names = new Set((selector.match(/in \(([^)]*)\)/)?.[1] ?? '').split(',').map(s => s.trim()));
  const all: any[] = [...provBuild.taskRuns];
  for (const a of APPS) all.push(...allRunsFor(a.name).taskRuns);
  return { items: all.filter(t => names.has(t.metadata.labels?.['tekton.dev/pipelineRun'])) };
}

// ---------- Tekton Results: finished runs for the fleet, newest first ----------
let historyCache: any[] | undefined;
export function fleetResults() {
  if (!historyCache) {
    const out: any[] = [];
    const pipelines = ['build', 'test', 'deploy', 'sast-check', 'release', 'image-scan-check', 'build', 'deploy', 'provenance-check', 'onboarding-resync'];
    const dur: Record<string, number> = { build: 410, test: 260, deploy: 115, release: 80, 'sast-check': 70, 'image-scan-check': 55, 'provenance-check': 40, 'onboarding-resync': 35 };
    let seed = 7;
    const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    let i = 0;
    for (let min = 75; min < 8 * 1440; min += 35 + Math.floor(rnd() * 70)) {
      const app = APPS[i % APPS.length].name;
      const pipeline = pipelines[(i * 7 + Math.floor(min / 97)) % pipelines.length];
      const r = rnd();
      const status = r < 0.07 ? 'FAILURE' : r < 0.09 ? 'CANCELLED' : 'SUCCESS';
      const seconds = Math.round(dur[pipeline] * (0.85 + rnd() * 0.3));
      const start = NOW - min * 60_000;
      const name = `ci-h${i}-${pipeline}-${app}`.slice(0, 50);
      const ns = `app-${app}-cicd`;
      out.push({
        name: `${ns}/results/r${i}`,
        create_time: new Date(start).toISOString(),
        annotations: { 'object.metadata.name': name, 'tekton.dev/pipeline': pipeline },
        summary: {
          type: 'tekton.dev/v1.PipelineRun', status,
          start_time: new Date(start).toISOString(), end_time: new Date(start + seconds * 1000).toISOString(),
          annotations: { commit: shaFor((i * 2654435761 >>> 0).toString(16).padStart(7, '0').slice(0, 7)), eventType: pipeline === 'build' ? 'push' : 'incoming' },
        },
      });
      i++;
    }
    historyCache = out;
  }
  return { results: historyCache, nextPageToken: '' };
}

// ---------- Glidepath's release records (ConfigMaps on the Tekton cluster) ----------
export function fleetReleaseRecords() {
  const rec = (app: string, env: string, chain: string, state: string, stateMin: number, extra: Record<string, string> = {}) => ({
    metadata: { name: `release-tracking-${chain}`, namespace: `app-${app}-cicd`, labels: { 'hangar.io/subcomponent': 'release-tracking', 'hangar.io/app': app, 'hangar.io/env': env } },
    data: { appName: app, env, cluster: env === 'prod' ? 'prod' : 'dev', state, stateAt: ago(stateMin), kind: 'release', ...extra },
  });
  return {
    items: [
      rec('flight-api', 'prod', 'c-4f9c', 'progressing', 9, { releaseId: '1.8.0-4f9c2ab', prUrl: prUrl('gitops-prod', 214), prCreatedAt: ago(20), mergedAt: ago(10), flowStartTime: ago(106), gitRevision: shaFor('4f9c2ab') }),
      rec('baggage-api', 'prod', 'c-71b8', 'proposed', 25, { releaseId: '0.6.0-71b8e2c', prUrl: prUrl('gitops-prod', 219), prCreatedAt: ago(25), flowStartTime: ago(52), gitRevision: shaFor('71b8e2c') }),
      rec('boarding-api', 'prod', 'c-9ad0', 'healthy', 1430, { releaseId: '2.3.1-9ad04e1', mergedAt: ago(1445), gitRevision: shaFor('9ad04e1') }),
      rec('flight-api', 'prod', 'c-b71e', 'superseded', 1300, { releaseId: '1.7.2-b71e0d4', supersededBy: 'c-4f9c' }),
    ],
  };
}

// ---------- dora-exporter's series ----------
export function doraInstant(query: string) {
  const days = Number(query.match(/\[(\d+)d\]/)?.[1] ?? 30);
  const k = days / 30;
  const prev = query.includes('offset');
  const v = (value: number, metric: Record<string, string> = {}) => ({ metric, value: [NOW / 1000, String(value)] });
  const apps: Array<[string, number, number]> = [['flight-api', 31, 1], ['boarding-api', 19, 1], ['baggage-api', 14, 0]];
  const share = (n: number) => Math.round(n * k * 10) / 10;
  if (query.startsWith('sum by (app, outcome)')) {
    return apps.flatMap(([app, d, f]) => [v(share(d * 0.38), { app, outcome: 'succeeded' }), ...(f ? [v(share(f), { app, outcome: 'failed' })] : [])]);
  }
  if (query.startsWith('sum by (app)')) return apps.map(([app, d]) => v(share(d), { app }));
  if (query.includes('dora_lead_time') && query.includes('by (app, le)')) return apps.map(([app], i) => v(9800 + i * 2600, { app }));
  if (query.includes('dora_time_to_restore') && query.includes('by (app, le)')) return apps.map(([app], i) => v(1900 + i * 700, { app }));
  if (query.includes('dora_lead_time')) return [v(11_400)];
  if (query.includes('dora_time_to_restore')) return [v(2_340)];
  if (query.includes('dora_deployments_total')) return [v(prev ? share(52) : share(64))];
  if (query.includes('outcome="failed"')) return [v(prev ? share(3) : share(2))];
  if (query.includes('dora_releases_total')) return [v(prev ? share(18) : share(22))];
  return [v(0)];
}
export function doraRange(query: string, start: number, end: number, step: number) {
  const values: Array<[number, string]> = [];
  let n = 0;
  for (let t = start; t <= end; t += step, n++) {
    const failed = query.includes('outcome="failed"');
    const weekday = new Date(t * 1000).getUTCDay() % 6 !== 0;
    const x = failed ? (n % 13 === 5 ? 1 : 0) : (weekday ? 2 + ((n * 7) % 3) : n % 2);
    values.push([t, String(x)]);
  }
  return [{ metric: {}, values }];
}
