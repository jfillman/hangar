import { dump as yamlDump } from 'js-yaml';
// Demo data for the Tower walkthrough harness. The apps are the Skyport demo
// services from airframe/examples/skyport; everything Tower shows about them
// (versions, runs, PRs, metrics) is invented, across generic dev, staging and
// prod environments on two clusters named dev and prod.

export const OWNER = 'skyport';
const NOW = Date.now();
export const ago = (min: number) => new Date(NOW - min * 60_000).toISOString();

type Strategy = 'canary' | 'rolling';
export interface DemoApp {
  name: string;
  title: string;
  lang: string;
  strategy: Strategy;
  port: number;
  // image version per env
  versions: Record<string, { ver: string; sha: string; deployedMin: number }>;
  canary?: { env: string; stepIndex: number; phase: string; message?: string };
  replicas: Record<string, number>;
}

export const ENVS = [
  { env: 'dev', cluster: 'dev' },
  { env: 'staging', cluster: 'dev' },
  { env: 'prod', cluster: 'prod' },
];

const V = (ver: string, sha: string, deployedMin: number) => ({ ver, sha, deployedMin });

export const APPS: DemoApp[] = [
  {
    name: 'flight-api',
    title: 'System of record for flights and gates',
    lang: 'springboot',
    strategy: 'canary',
    port: 8080,
    versions: {
      dev: V('1.8.1', '6a0e5d2', 38),
      staging: V('1.8.0', '4f9c2ab', 62),
      prod: V('1.8.0', '4f9c2ab', 9),
    },
    canary: { env: 'prod', stepIndex: 2, phase: 'Paused', message: 'CanaryPauseStep' },
    replicas: { dev: 1, staging: 2, prod: 4 },
  },
  {
    name: 'boarding-api',
    title: 'The passenger-facing gate board',
    lang: 'nodejs',
    strategy: 'canary',
    port: 3000,
    versions: {
      dev: V('2.3.1', '9ad04e1', 300),
      staging: V('2.3.1', '9ad04e1', 280),
      prod: V('2.3.1', '9ad04e1', 1440),
    },
    replicas: { dev: 1, staging: 2, prod: 3 },
  },
  {
    name: 'baggage-api',
    title: "Tracks each bag's journey",
    lang: 'python',
    strategy: 'rolling',
    port: 8000,
    versions: {
      dev: V('0.6.0', '71b8e2c', 40),
      staging: V('0.5.4', 'e04d9a3', 3000),
      prod: V('0.5.4', 'e04d9a3', 2900),
    },
    replicas: { dev: 1, staging: 1, prod: 2 },
  },
];

export const FEATURED = 'flight-api';
export const appByName = (n?: string) => APPS.find(a => a.name === n);
export const imageOf = (app: DemoApp, env: string) => {
  const v = app.versions[env];
  return `ghcr.io/${OWNER}/${app.name}:${v.ver}-${v.sha}`;
};
const fullSha = (short: string) => (short + 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855').slice(0, 40);
export const shaFor = fullSha;

// ---------- catalog ----------
export const entities = APPS.map(a => ({
  apiVersion: 'backstage.io/v1alpha1',
  kind: 'Component',
  metadata: {
    name: a.name,
    namespace: 'default',
    title: a.name,
    description: a.title,
    tags: [`kind:${a.lang}application`, a.lang],
    annotations: {
      'backstage.io/kubernetes-id': a.name,
      'github.com/project-slug': `${OWNER}/${a.name}`,
    },
  },
  spec: { type: 'service', lifecycle: 'production', owner: 'team-skyport' },
}));

// ---------- kubernetes objects ----------
const ns = (app: DemoApp, env: string) => `app-${app.name}-${env}`;
const labels = (app: DemoApp, env: string) => ({
  'hangar.io/app': app.name,
  'hangar.io/env': env,
  'app.kubernetes.io/name': app.name,
  'app.kubernetes.io/part-of': 'hangar',
});

function container(app: DemoApp, env: string) {
  return {
    name: app.name,
    image: imageOf(app, env),
    ports: [{ name: 'http', containerPort: app.port, protocol: 'TCP' }],
    resources: {
      requests: { cpu: env === 'prod' ? '250m' : '100m', memory: env === 'prod' ? '512Mi' : '256Mi' },
      limits: { cpu: env === 'prod' ? '1' : '500m', memory: env === 'prod' ? '1Gi' : '512Mi' },
    },
    readinessProbe: { httpGet: { path: '/healthz', port: app.port }, periodSeconds: 10, initialDelaySeconds: 5, timeoutSeconds: 1, successThreshold: 1, failureThreshold: 3 },
    livenessProbe: { httpGet: { path: '/livez', port: app.port }, periodSeconds: 20, initialDelaySeconds: 10, timeoutSeconds: 1, successThreshold: 1, failureThreshold: 3 },
  };
}

const podHash = (app: DemoApp, env: string, prev = false) =>
  (prev ? 'b7' : '5c') + (app.name.length * 7919 + env.length * 131).toString(16).slice(0, 6) + (prev ? 'd' : 'f');

function pods(app: DemoApp, env: string) {
  const n = app.replicas[env];
  const out: any[] = [];
  const canaryHere = app.canary?.env === env;
  const deployedMin = app.versions[env].deployedMin;
  for (let i = 0; i < n; i++) {
    const isNew = !canaryHere || i < Math.max(1, Math.round(n * 0.4));
    const hash = podHash(app, env, !isNew);
    const suffix = ['x7k2p', 'q9m4r', 'h3n8w', 'd2v6t', 'z5c1b'][i];
    out.push({
      apiVersion: 'v1',
      kind: 'Pod',
      metadata: {
        name: `${app.name}-${hash}-${suffix}`,
        namespace: ns(app, env),
        labels: { ...labels(app, env), 'rollouts-pod-template-hash': hash },
        creationTimestamp: ago(isNew ? deployedMin : deployedMin + 2000),
      },
      spec: { containers: [container(app, env)], nodeName: `${env === 'prod' ? 'prod' : 'dev'}-worker-${(i % 3) + 1}`, serviceAccountName: app.name },
      status: {
        phase: 'Running',
        podIP: `10.244.${i + 1}.${20 + i * 3}`,
        startTime: ago(isNew ? deployedMin : deployedMin + 2000),
        conditions: [{ type: 'Ready', status: 'True' }],
        containerStatuses: [{ name: app.name, ready: true, restartCount: i === 1 && env === 'dev' ? 1 : 0, image: imageOf(app, env), state: { running: { startedAt: ago(deployedMin) } } }],
      },
    });
  }
  return out;
}

function service(app: DemoApp, env: string, name = app.name) {
  return {
    apiVersion: 'v1',
    kind: 'Service',
    metadata: { name, namespace: ns(app, env), labels: labels(app, env) },
    spec: { type: 'ClusterIP', clusterIP: `10.96.${app.port % 200}.${env.length * 11}`, ports: [{ name: 'http', port: 80, targetPort: app.port, protocol: 'TCP' }], selector: { 'app.kubernetes.io/name': app.name } },
  };
}

function deployment(app: DemoApp, env: string) {
  const n = app.replicas[env];
  return {
    apiVersion: 'apps/v1',
    kind: 'Deployment',
    metadata: { name: app.name, namespace: ns(app, env), labels: labels(app, env), annotations: { 'argocd.argoproj.io/tracking-id': `${app.name}-${env}:apps/Deployment:${ns(app, env)}/${app.name}` } },
    spec: { replicas: n, strategy: { type: 'RollingUpdate' }, template: { spec: { containers: [container(app, env)] } } },
    status: { replicas: n, availableReplicas: n, readyReplicas: n, updatedReplicas: n },
  };
}

const CANARY_STEPS = [
  { setWeight: 20 },
  { pause: { duration: '2m' } },
  { setWeight: 40 },
  { pause: {} },
  { setWeight: 60 },
  { analysis: { templates: [{ templateName: 'success-rate' }] } },
  { setWeight: 80 },
  { pause: { duration: '5m' } },
];

function rollout(app: DemoApp, env: string) {
  const n = app.replicas[env];
  const canaryHere = app.canary?.env === env;
  return {
    apiVersion: 'argoproj.io/v1alpha1',
    kind: 'Rollout',
    metadata: { name: app.name, namespace: ns(app, env), labels: labels(app, env), annotations: { 'rollout.argoproj.io/revision': canaryHere ? '14' : '13' } },
    spec: {
      replicas: n,
      template: { spec: { containers: [container(app, env)] } },
      strategy: app.strategy === 'rolling' ? {} : {
        canary: {
          canaryService: `${app.name}-canary`,
          stableService: `${app.name}-stable`,
          steps: CANARY_STEPS,
          analysis: { templates: [{ templateName: 'error-rate-guard' }] },
        },
      } as any,
    },
    status: {
      replicas: n,
      availableReplicas: n,
      phase: canaryHere ? app.canary!.phase : 'Healthy',
      message: canaryHere ? app.canary!.message : undefined,
      currentStepIndex: app.strategy === 'rolling' ? undefined : canaryHere ? app.canary!.stepIndex + 1 : CANARY_STEPS.length,
      currentPodHash: podHash(app, env),
      stableRS: canaryHere ? podHash(app, env, true) : podHash(app, env),
      canary: canaryHere ? { currentBackgroundAnalysisRunStatus: { name: `${app.name}-${podHash(app, env)}-14`, status: 'Running' } } : {},
    },
  };
}

function httpRoute(app: DemoApp, env: string) {
  return {
    apiVersion: 'gateway.networking.k8s.io/v1',
    kind: 'HTTPRoute',
    metadata: { name: app.name, namespace: ns(app, env), labels: labels(app, env) },
    spec: { hostnames: [`${app.name}.${env}.example.internal`], parentRefs: [{ name: 'hangar', namespace: 'hangar-gateway' }] },
  };
}

function hpa(app: DemoApp, env: string) {
  if (env !== 'prod') return undefined;
  return {
    apiVersion: 'autoscaling/v2',
    kind: 'HorizontalPodAutoscaler',
    metadata: { name: app.name, namespace: ns(app, env), labels: labels(app, env) },
    spec: { minReplicas: app.replicas.prod, maxReplicas: app.replicas.prod * 3, metrics: [{ type: 'Resource', resource: { name: 'cpu', target: { type: 'Utilization', averageUtilization: 70 } } }] },
    status: { currentReplicas: app.replicas.prod },
  };
}

function simple(kind: string, apiVersion: string, app: DemoApp, env: string, name: string, extra: any = {}) {
  return { apiVersion, kind, metadata: { name, namespace: ns(app, env), labels: labels(app, env) }, ...extra };
}

const byCluster = (cluster: string) => ENVS.filter(e => e.cluster === cluster);

export function k8sObjectsFor(entity: any) {
  const app = appByName(entity?.metadata?.name);
  if (!app) return { items: [] };
  return {
    items: ['dev', 'prod'].map(cluster => {
      const envs = byCluster(cluster).map(e => e.env);
      const all = (fn: (env: string) => any) => envs.map(fn).filter(Boolean);
      return {
        cluster: { name: cluster },
        podMetrics: [],
        errors: [],
        resources: [
          { type: 'pods', resources: envs.flatMap(e => pods(app, e)) },
          { type: 'services', resources: envs.flatMap(e => app.strategy === 'canary' ? [service(app, e), service(app, e, `${app.name}-canary`), service(app, e, `${app.name}-stable`)] : [service(app, e)]) },
          { type: 'deployments', resources: [] },
          { type: 'horizontalpodautoscalers', resources: all(e => hpa(app, e)) },
          { type: 'configmaps', resources: all(e => simple('ConfigMap', 'v1', app, e, `${app.name}-config`, { data: { LOG_LEVEL: e === 'prod' ? 'info' : 'debug', SIMULATOR_ENABLED: e === 'prod' ? 'false' : 'true' } })) },
          { type: 'secrets', resources: all(e => simple('Secret', 'v1', app, e, `${app.name}-secrets`, { type: 'Opaque' })) },
          { type: 'ingresses', resources: [] },
        ],
      };
    }),
  };
}

export function customResourcesFor(entity: any, matchers: any[]) {
  const app = appByName(entity?.metadata?.name);
  if (!app) return { items: [] };
  const plural = matchers[0]?.plural;
  return {
    items: ['dev', 'prod'].map(cluster => {
      const envs = byCluster(cluster).map(e => e.env);
      let resources: any[] = [];
      switch (plural) {
        case 'rollouts':
          resources = envs.map(e => rollout(app, e));
          break;
        case 'httproutes':
          resources = envs.map(e => httpRoute(app, e));
          break;
        case 'gateways':
          resources = [{ metadata: { name: 'hangar', namespace: 'hangar-gateway' }, spec: { listeners: [{ protocol: 'HTTPS', tls: {} }] } }];
          break;
        case 'poddisruptionbudgets':
          resources = envs.filter(e => e !== 'dev').map(e => simple('PodDisruptionBudget', 'policy/v1', app, e, app.name, { spec: { minAvailable: 1 }, status: { currentHealthy: app.replicas[e], desiredHealthy: 1, disruptionsAllowed: app.replicas[e] - 1 } }));
          break;
        case 'serviceaccounts':
          resources = envs.map(e => simple('ServiceAccount', 'v1', app, e, app.name));
          break;
        case 'networkpolicies':
          resources = envs.map(e => simple('NetworkPolicy', 'networking.k8s.io/v1', app, e, `${app.name}-default-deny`));
          break;
        case 'endpoints':
          resources = envs.map(e => simple('Endpoints', 'v1', app, e, app.name));
          break;
        case 'roles':
          resources = envs.map(e => simple('Role', 'rbac.authorization.k8s.io/v1', app, e, `${app.name}-reader`));
          break;
        case 'rolebindings':
          resources = envs.map(e => simple('RoleBinding', 'rbac.authorization.k8s.io/v1', app, e, `${app.name}-reader`));
          break;
        case 'externalsecrets':
          resources = envs.map(e => simple('ExternalSecret', 'external-secrets.io/v1', app, e, `${app.name}-secrets`, { status: { conditions: [{ type: 'Ready', status: 'True' }] } }));
          break;
        case 'servicemonitors':
          resources = envs.map(e => simple('ServiceMonitor', 'monitoring.coreos.com/v1', app, e, app.name));
          break;
        case 'slos':
          resources = envs.flatMap(e => [
            { metadata: { name: 'availability', namespace: ns(app, e), labels: { 'hangar.io/env': e } }, spec: { service: app.name, objective: e === 'prod' ? 99.9 : 99, indicator: { type: 'availability', metric: 'http_requests_total', totalFilter: `service="${app.name}"`, errorFilter: 'code=~"5.."' } } },
            { metadata: { name: 'latency', namespace: ns(app, e), labels: { 'hangar.io/env': e } }, spec: { service: app.name, objective: 99, indicator: { type: 'latency', metric: 'http_request_duration_seconds', totalFilter: `service="${app.name}"`, latencyThreshold: '0.3' } } },
          ]);
          break;
        default:
          resources = [];
      }
      return { cluster: { name: cluster }, podMetrics: [], errors: [], resources: [{ type: 'customresources', resources }] };
    }),
  };
}

// Raw proxy GETs (rollout topology, analysis runs, events...)
export function rawNamespaceList(path: string, cluster: string): any | undefined {
  const m = path.match(/namespaces\/app-([a-z-]+?)-(dev|staging|prod|cicd)\//);
  if (!m) return undefined;
  const app = appByName(m[1]);
  const env = m[2];
  if (!app) return undefined;
  if (env === 'cicd') return undefined;
  if (path.includes('/rollouts/')) return rollout(app, env);
  if (path.endsWith('/replicasets')) {
    const cur = podHash(app, env);
    const prev = podHash(app, env, true);
    const n = app.replicas[env];
    const canaryHere = app.canary?.env === env;
    const newCount = canaryHere ? Math.max(1, Math.round(n * 0.4)) : n;
    const rs = (hash: string, count: number, rev: string) => ({
      apiVersion: 'apps/v1', kind: 'ReplicaSet',
      metadata: { name: `${app.name}-${hash}`, namespace: ns(app, env), labels: { ...labels(app, env), 'rollouts-pod-template-hash': hash }, annotations: { 'rollout.argoproj.io/revision': rev }, ownerReferences: [{ kind: 'Rollout', name: app.name }], creationTimestamp: ago(app.versions[env].deployedMin) },
      spec: { replicas: count, template: { spec: { containers: [container(app, env)] } } },
      status: { replicas: count, readyReplicas: count, availableReplicas: count },
    });
    return { items: canaryHere ? [rs(cur, newCount, '14'), rs(prev, n - newCount, '13')] : [rs(cur, n, '13')] };
  }
  if (path.endsWith('/pods')) return { items: pods(app, env) };
  if (path.endsWith('/services')) return { items: app.strategy === 'canary' ? [service(app, env), service(app, env, `${app.name}-canary`), service(app, env, `${app.name}-stable`)] : [service(app, env)] };
  if (path.endsWith('/analysisruns')) return { items: analysisRuns(app, env) };
  if (path.endsWith('/jobs')) return { items: [] };
  return undefined;
}

function analysisRuns(app: DemoApp, env: string) {
  if (app.strategy !== 'canary') return [];
  const canaryHere = app.canary?.env === env;
  const hash = podHash(app, env);
  const started = app.versions[env].deployedMin;
  const measurements = (n: number, base: number) =>
    Array.from({ length: n }, (_, i) => ({ startedAt: ago(started - i), value: `[${(base - (i % 3) * 0.0004).toFixed(4)}]`, phase: 'Successful' }));
  return [
    {
      metadata: { name: `${app.name}-${hash}-14`, namespace: ns(app, env), labels: { 'rollout-type': 'Background', 'rollouts-pod-template-hash': hash }, ownerReferences: [{ kind: 'Rollout', name: app.name }] },
      spec: { metrics: [{ name: 'error-rate', successCondition: 'result[0] <= 0.01', provider: { prometheus: { query: `sum(rate(http_requests_total{service="${app.name}-canary",code=~"5.."}[2m])) / sum(rate(http_requests_total{service="${app.name}-canary"}[2m]))` } } }] },
      status: {
        phase: canaryHere ? 'Running' : 'Successful',
        startedAt: ago(started),
        completedAt: canaryHere ? undefined : ago(started - 12),
        metricResults: [{ name: 'error-rate', phase: canaryHere ? 'Running' : 'Successful', measurements: measurements(canaryHere ? Math.min(8, started) : 10, 0.0021) }],
      },
    },
  ];
}

// ---------- Tekton ----------
const BUILD_TASKS: Array<[string, string[]]> = [
  ['clone-repo', []], ['validate-config', ['clone-repo']], ['start-flow', ['validate-config']],
  ['start-build-stage-span', ['start-flow']], ['pipelinerun-started', ['start-flow']],
  ['sast-scan', ['start-build-stage-span']], ['unit-test', ['start-build-stage-span']], ['build-source', ['start-build-stage-span']],
  ['build-image', ['build-source', 'unit-test', 'sast-scan']], ['image-scan', ['build-image']], ['generate-sbom', ['build-image']],
];
const DEPLOY_TASKS: Array<[string, string[]]> = [
  ['start-flow', []], ['pipelinerun-started', ['start-flow']], ['start-deploy-stage-span', ['start-flow']],
  ['resolve-image-ref', ['start-deploy-stage-span']], ['deploy', ['resolve-image-ref']], ['resolve-notify-config', []],
];
const TEST_TASKS: Array<[string, string[]]> = [
  ['clone-repo', []], ['start-flow', ['clone-repo']], ['pipelinerun-started', ['start-flow']], ['validate-config', ['clone-repo']],
  ['start-test-stage-span', ['start-flow', 'validate-config']], ['run-testworkflow', ['start-test-stage-span']],
];
const RELEASE_TASKS: Array<[string, string[]]> = [
  ['start-flow', []], ['pipelinerun-started', ['start-flow']], ['start-release-stage-span', ['start-flow']],
  ['resolve-image-ref', ['start-release-stage-span']], ['open-release-pr', ['resolve-image-ref']], ['mark-release-pending', ['open-release-pr']], ['resolve-notify-config', []],
];
const FINALLY = (stage: string) => [`end-${stage}-stage-span`, 'end-flow', 'notify', 'notify-backstage', 'send-cdevent', 'pipelinerun-finished'];

const STEP_DUR: Record<string, number> = { 'clone-repo': 0.3, 'sast-scan': 1.4, 'unit-test': 2.2, 'build-source': 1.8, 'build-image': 2.6, 'image-scan': 1.1, 'generate-sbom': 0.6, 'run-testworkflow': 3.5, deploy: 1.2, 'open-release-pr': 0.5 };

interface RunSpec {
  pipeline: 'build' | 'deploy' | 'test' | 'release';
  app: DemoApp;
  ver: string;
  sha: string;
  env?: string;
  startMin: number;
  phase: 'succeeded' | 'failed' | 'running';
  slug: string;
  chain: string;
  stepIndex: number;
  runningTask?: string;
  failTask?: string;
  author?: string;
  branch?: string;
}

function makeRun(spec: RunSpec) {
  const { pipeline, app } = spec;
  const tasks = { build: BUILD_TASKS, deploy: DEPLOY_TASKS, test: TEST_TASKS, release: RELEASE_TASKS }[pipeline];
  const stage = pipeline;
  const stageName = pipeline === 'build' ? 'build' : spec.env ?? pipeline;
  const rand = (spec.sha.charCodeAt(0) * 31 + spec.startMin).toString(36).slice(-5).padStart(5, 'x');
  const name = `ci-${spec.stepIndex}-${stageName}-${spec.slug}-${rand}`;
  const namespace = `app-${app.name}-cicd`;
  const start = NOW - spec.startMin * 60_000;
  // schedule tasks by DAG
  const endAt: Record<string, number> = {};
  const taskRuns: any[] = [];
  const childRefs: any[] = [];
  let reachedRunning = false;
  let failed = false;
  for (const [tname, after] of tasks) {
    const st = Math.max(start + 4000, ...after.map(a => endAt[a] ?? start));
    const dur = (STEP_DUR[tname] ?? 0.15) * 60_000;
    let phase: 'succeeded' | 'running' | 'failed' | 'pending' = 'succeeded';
    if (spec.phase === 'running') {
      if (st > NOW) phase = 'pending';
      else if (st + dur > NOW || tname === spec.runningTask) { phase = 'running'; reachedRunning = true; }
    }
    if (spec.failTask === tname) { phase = 'failed'; failed = true; }
    if (failed && spec.failTask !== tname && after.some(a => a === spec.failTask)) phase = 'pending';
    endAt[tname] = st + dur;
    if (phase === 'pending') continue;
    const trName = `${name}-${tname}`;
    childRefs.push({ kind: 'TaskRun', name: trName, pipelineTaskName: tname });
    const results: any[] = [];
    if (tname === 'start-flow') results.push({ name: 'chain-slug', value: spec.slug }, { name: 'chain-id', value: spec.chain });
    if (tname === 'build-image') results.push({ name: 'image-ref', value: `ghcr.io/${OWNER}/${app.name}:${spec.ver}-${spec.sha}` }, { name: 'IMAGE_DIGEST', value: 'sha256:' + fullSha(spec.sha) + fullSha(spec.sha).slice(0, 24) });
    if (tname === 'clone-repo') results.push({ name: 'url', value: `https://github.com/${OWNER}/${app.name}` }, { name: 'commit', value: fullSha(spec.sha) });
    if (tname === 'unit-test') results.push({ name: 'tests-passed', value: '412' }, { name: 'coverage', value: '87.4' });
    if (tname === 'image-scan') results.push({ name: 'critical', value: '0' }, { name: 'high', value: '0' }, { name: 'medium', value: '3' });
    const steps = tname === 'build-image'
      ? ['prepare', 'build-and-push', 'sign-image', 'attest-provenance']
      : tname === 'unit-test' ? ['install', 'test'] : tname === 'sast-scan' ? ['semgrep', 'attest'] : ['run'];
    const stepDur = dur / steps.length;
    taskRuns.push({
      metadata: { name: trName, namespace, labels: { 'tekton.dev/pipelineTask': tname, 'tekton.dev/pipelineRun': name } },
      spec: { params: [{ name: 'app-name', value: app.name }] },
      status: {
        conditions: [{ type: 'Succeeded', status: phase === 'succeeded' ? 'True' : phase === 'failed' ? 'False' : 'Unknown', reason: phase === 'succeeded' ? 'Succeeded' : phase === 'failed' ? 'Failed' : 'Running', message: phase === 'failed' ? `"step-test" exited with code 1` : undefined }],
        podName: `${trName}-pod`,
        startTime: new Date(st).toISOString(),
        completionTime: phase === 'succeeded' || phase === 'failed' ? new Date(st + dur).toISOString() : undefined,
        steps: steps.map((s, i) => {
          const ss = st + i * stepDur;
          const se = ss + stepDur;
          if (phase === 'running' && se > NOW) return ss <= NOW ? { name: s, container: `step-${s}`, running: { startedAt: new Date(ss).toISOString() } } : { name: s, container: `step-${s}` };
          return { name: s, container: `step-${s}`, terminated: { exitCode: phase === 'failed' && i === steps.length - 1 ? 1 : 0, startedAt: new Date(ss).toISOString(), finishedAt: new Date(se).toISOString() } };
        }),
        results,
      },
    });
  }
  const lastEnd = Math.max(...Object.values(endAt));
  const done = spec.phase !== 'running';
  const finallyTasks = FINALLY(stage);
  if (done) {
    finallyTasks.forEach((f, i) => {
      const trName = `${name}-${f}`;
      childRefs.push({ kind: 'TaskRun', name: trName, pipelineTaskName: f });
      taskRuns.push({
        metadata: { name: trName, namespace, labels: { 'tekton.dev/pipelineTask': f } },
        status: { conditions: [{ type: 'Succeeded', status: 'True', reason: 'Succeeded' }], podName: `${trName}-pod`, startTime: new Date(lastEnd + i * 1000).toISOString(), completionTime: new Date(lastEnd + i * 1000 + 6000).toISOString(), steps: [{ name: 'run', container: 'step-run', terminated: { exitCode: 0, startedAt: new Date(lastEnd).toISOString(), finishedAt: new Date(lastEnd + 6000).toISOString() } }], results: [] },
      });
    });
  }
  const pr = {
    metadata: {
      name,
      namespace,
      creationTimestamp: new Date(start).toISOString(),
      labels: {
        'tekton.dev/pipeline': pipeline,
        'hangar.io/app': app.name,
        'hangar.io/flow': pipeline === 'build' || pipeline === 'test' ? 'ci' : 'cd',
        'hangar.io/stage': stageName,
        'hangar.io/step-index': String(spec.stepIndex),
        'pipelinesascode.tekton.dev/sha': fullSha(spec.sha),
        'pipelinesascode.tekton.dev/event-type': pipeline === 'build' ? 'push' : 'incoming',
        'pipelinesascode.tekton.dev/url-org': OWNER,
        'pipelinesascode.tekton.dev/url-repository': app.name,
      },
      annotations: {
        'pipelinesascode.tekton.dev/source-branch': `refs/heads/${spec.branch ?? 'main'}`,
        'pipelinesascode.tekton.dev/sender': spec.author ?? 'jamie-dev',
      },
    },
    spec: { params: [{ name: 'chain-id', value: spec.chain }, { name: 'git-revision', value: fullSha(spec.sha) }, ...(spec.env ? [{ name: 'env', value: spec.env }] : []), { name: 'app-name', value: app.name }] },
    status: {
      conditions: [{ type: 'Succeeded', status: spec.phase === 'succeeded' ? 'True' : spec.phase === 'failed' ? 'False' : 'Unknown', reason: spec.phase === 'succeeded' ? 'Succeeded' : spec.phase === 'failed' ? 'Failed' : 'Running', message: spec.phase === 'failed' ? `Tasks Completed: 7 (Failed: 1, Cancelled 0), Skipped: 3` : spec.phase === 'running' ? 'Tasks Completed: 5 (Failed: 0, Cancelled 0), Incomplete: 6, Skipped: 0' : 'Tasks Completed: 11 (Failed: 0, Cancelled 0), Skipped: 0' }],
      pipelineSpec: { tasks: tasks.map(([n, a]) => ({ name: n, runAfter: a, taskRef: { resolver: 'cluster', params: [{ name: 'name', value: n === 'build-image' ? 'buildah-sign' : n }] } })), finally: finallyTasks.map(n => ({ name: n, taskRef: { resolver: 'cluster', params: [{ name: 'name', value: n }] } })) },
      childReferences: childRefs,
      startTime: new Date(start).toISOString(),
      completionTime: done ? new Date(lastEnd + 12000).toISOString() : undefined,
      results: [],
    },
  };
  return { pr, taskRuns };
}

function runsFor(app: DemoApp) {
  const specs: RunSpec[] = [];
  const cur = app.versions.dev;
  const slugs = ['amber-heron', 'quiet-falcon', 'steady-otter', 'bright-lynx', 'calm-kestrel', 'swift-marten'];
  if (app.name === FEATURED) {
    // A new build running right now, the current release's flow, and an older one
    specs.push({ pipeline: 'build', app, ver: '1.9.0', sha: 'd81f3c6', startMin: 4, phase: 'running', slug: 'bright-lynx', chain: 'c-81f3', stepIndex: 0, author: 'priya-k', branch: 'main' });
    specs.push({ pipeline: 'test', app, ver: '1.8.1', sha: '6a0e5d2', env: 'dev', startMin: 34, phase: 'succeeded', slug: 'calm-kestrel', chain: 'c-6a0e', stepIndex: 2 });
    specs.push({ pipeline: 'deploy', app, ver: '1.8.1', sha: '6a0e5d2', env: 'dev', startMin: 40, phase: 'succeeded', slug: 'calm-kestrel', chain: 'c-6a0e', stepIndex: 1 });
    specs.push({ pipeline: 'build', app, ver: '1.8.1', sha: '6a0e5d2', startMin: 49, phase: 'succeeded', slug: 'calm-kestrel', chain: 'c-6a0e', stepIndex: 0, author: 'alex-m' });
    specs.push({ pipeline: 'release', app, ver: '1.8.0', sha: '4f9c2ab', env: 'prod', startMin: 21, phase: 'succeeded', slug: 'amber-heron', chain: 'c-4f9c', stepIndex: 5 });
    specs.push({ pipeline: 'deploy', app, ver: '1.8.0', sha: '4f9c2ab', env: 'staging', startMin: 64, phase: 'succeeded', slug: 'amber-heron', chain: 'c-4f9c', stepIndex: 3 });
    specs.push({ pipeline: 'test', app, ver: '1.8.0', sha: '4f9c2ab', env: 'dev', startMin: 80, phase: 'succeeded', slug: 'amber-heron', chain: 'c-4f9c', stepIndex: 2 });
    specs.push({ pipeline: 'deploy', app, ver: '1.8.0', sha: '4f9c2ab', env: 'dev', startMin: 97, phase: 'succeeded', slug: 'amber-heron', chain: 'c-4f9c', stepIndex: 1 });
    specs.push({ pipeline: 'build', app, ver: '1.8.0', sha: '4f9c2ab', startMin: 106, phase: 'succeeded', slug: 'amber-heron', chain: 'c-4f9c', stepIndex: 0, author: 'jamie-dev' });
    specs.push({ pipeline: 'build', app, ver: '1.7.3', sha: '0c2d7e9', startMin: 260, phase: 'failed', slug: 'quiet-falcon', chain: 'c-0c2d', stepIndex: 0, failTask: 'unit-test', author: 'sam-r', branch: 'feat/flight-events' });
    specs.push({ pipeline: 'build', app, ver: '1.7.2', sha: 'b71e0d4', startMin: 1500, phase: 'succeeded', slug: 'steady-otter', chain: 'c-b71e', stepIndex: 0 });
  } else {
    specs.push({ pipeline: 'deploy', app, ver: cur.ver, sha: cur.sha, env: 'dev', startMin: cur.deployedMin + 3, phase: 'succeeded', slug: slugs[app.name.length % 6], chain: `c-${cur.sha.slice(0, 4)}`, stepIndex: 1 });
    specs.push({ pipeline: 'build', app, ver: cur.ver, sha: cur.sha, startMin: cur.deployedMin + 12, phase: 'succeeded', slug: slugs[app.name.length % 6], chain: `c-${cur.sha.slice(0, 4)}`, stepIndex: 0 });
  }
  const built = specs.map(makeRun);
  return { items: built.map(b => b.pr), taskRuns: built.flatMap(b => b.taskRuns) };
}

const runCache = new Map<string, ReturnType<typeof runsFor>>();
export function tektonFor(path: string) {
  const m = path.match(/namespaces\/app-([a-z-]+?)-cicd\/(pipelineruns|taskruns)/);
  if (!m) return undefined;
  const app = appByName(m[1]);
  if (!app) return { items: [] };
  if (!runCache.has(app.name)) runCache.set(app.name, runsFor(app));
  const r = runCache.get(app.name)!;
  return m[2] === 'pipelineruns' ? { items: r.items } : { items: r.taskRuns };
}

export function taskLog(path: string): string {
  const step = path.match(/container=step-([a-z-]+)/)?.[1] ?? 'run';
  const t = (s: number) => new Date(NOW - s * 1000).toISOString();
  const lines: Record<string, string[]> = {
    'build-and-push': [
      'STEP 1/6: FROM cgr.dev/chainguard/jre:latest',
      'STEP 2/6: WORKDIR /app',
      'STEP 3/6: COPY target/flight-api.jar app.jar',
      'STEP 4/6: USER 65532',
      'STEP 5/6: EXPOSE 8080',
      'STEP 6/6: ENTRYPOINT ["java", "-jar", "app.jar"]',
      'COMMIT ghcr.io/skyport/flight-api:1.9.0-d81f3c6',
      'Getting image source signatures',
      'Copying blob sha256:7a1b… done',
      'Writing manifest to image destination',
    ],
    test: ['[INFO] --- surefire:3.2.5:test (default-test) @ flight-api ---', '[INFO] Running io.skyport.flight.FlightControllerTest', '[INFO] Tests run: 38, Failures: 0, Errors: 0, Skipped: 0', '[INFO] Running io.skyport.flight.FlightServiceTest', '[INFO] Tests run: 64, Failures: 0, Errors: 0, Skipped: 0', '[INFO] Running io.skyport.flight.SimulatorTest', '[INFO] Tests run: 21, Failures: 0, Errors: 0, Skipped: 0', '[INFO] Results:', '[INFO] Tests run: 412, Failures: 0, Errors: 0, Skipped: 0', '[INFO] \u001b[32mBUILD SUCCESS\u001b[0m'],
    semgrep: ['Scanning 96 files with 1,148 rules…', 'Findings: 0 blocking, 2 informational', '\u001b[32mSAST gate passed\u001b[0m'],
  };
  const body = lines[step] ?? ['starting…', 'done'];
  return body.map((l, i) => `${t(body.length - i + 30)} ${l}`).join('\n');
}

// ---------- Glidepath backend ----------
export function provenanceFor(image: string) {
  const m = image.match(/ghcr\.io\/[^/]+\/([a-z-]+):([\d.]+)-([0-9a-f]+)/);
  const appName = m?.[1] ?? 'app';
  const sha = m?.[3] ?? '0000000';
  const digest = 'sha256:' + fullSha(sha) + fullSha(sha).slice(0, 24);
  const cert = { subject: `https://github.com/${OWNER}/glidepath/.tekton/build.yaml@refs/heads/main`, issuer: 'https://fulcio.sigstore.dev', identity: 'tekton-chains', validFrom: ago(120), validTo: ago(110) };
  return {
    digest,
    attestations: [
      {
        predicateType: 'https://slsa.dev/provenance/v0.2',
        verified: true,
        certificate: cert,
        transparencyLog: { logIndex: 104_883_211 + sha.charCodeAt(0), integratedTime: Math.floor(NOW / 1000) - 7000 },
        subject: [{ name: `ghcr.io/${OWNER}/${appName}`, digest: { sha256: digest.slice(7) } }],
        predicate: {
          builder: { id: 'https://tekton.dev/chains/v2' },
          buildType: 'tekton.dev/v1/PipelineRun',
          metadata: { buildStartedOn: ago(110), buildFinishedOn: ago(102) },
          buildConfig: {
            tasks: [
              { invocation: { environment: { labels: { 'tekton.dev/task': 'clone-repo-authenticated' } } }, results: [{ name: 'url', value: `https://github.com/${OWNER}/${appName}` }, { name: 'commit', value: fullSha(sha) }] },
              { invocation: { environment: { labels: { 'tekton.dev/task': 'buildah-sign' } } }, results: [{ name: 'IMAGE_DIGEST', value: digest }] },
            ],
          },
        },
      },
      { predicateType: 'https://cyclonedx.org/bom', verified: true, certificate: cert, transparencyLog: { logIndex: 104_883_260, integratedTime: Math.floor(NOW / 1000) - 6900 }, predicate: { bomFormat: 'CycloneDX', specVersion: '1.5', components: ['express', 'react', 'zod', 'pino'].map(name => ({ type: 'library', name })) } },
      { predicateType: 'cosign.sigstore.dev/signature/simple-signing', verified: true, certificate: cert, transparencyLog: { logIndex: 104_883_199, integratedTime: Math.floor(NOW / 1000) - 7100 } },
      { predicateType: 'https://cosign.sigstore.dev/attestation/vuln/v1', verified: true, certificate: cert, predicate: { scanner: { uri: 'pkg:github/aquasecurity/trivy', result: { summary: { CRITICAL: 0, HIGH: 0, MEDIUM: 3, LOW: 11 } } } } },
      { predicateType: 'https://hangar.io/attestations/sast/v1', verified: true, certificate: cert, predicate: { tool: 'semgrep', blocking: 0, informational: 2 } },
    ],
  };
}

export function imagesFor(appName: string) {
  const app = appByName(appName);
  if (!app) return [];
  const vs = new Map<string, { ver: string; sha: string; min: number }>();
  Object.values(app.versions).forEach(v => vs.set(v.sha, { ver: v.ver, sha: v.sha, min: v.deployedMin + 10 }));
  if (app.name === FEATURED) {
    vs.set('4f9c2ab', { ver: '1.8.0', sha: '4f9c2ab', min: 105 });
    vs.set('b71e0d4', { ver: '1.7.2', sha: 'b71e0d4', min: 1490 });
    vs.set('8e3f1a0', { ver: '1.7.1', sha: '8e3f1a0', min: 4300 });
    vs.set('5d2c9b7', { ver: '1.7.0', sha: '5d2c9b7', min: 7200 });
  }
  const out: any[] = [];
  [...vs.values()].sort((a, b) => a.min - b.min).forEach(v => {
    const d = fullSha(v.sha) + fullSha(v.sha).slice(0, 24);
    out.push({ digest: `sha256:${d}`, tags: [`${v.ver}-${v.sha}`], createdAt: ago(v.min), htmlUrl: `https://github.com/${OWNER}/${app.name}/pkgs/container/${app.name}` });
    out.push({ digest: `sha256:${fullSha('a' + v.sha)}${fullSha('a').slice(0, 24)}`, tags: [`sha256-${d}.sig`], createdAt: ago(v.min - 1) });
    out.push({ digest: `sha256:${fullSha('b' + v.sha)}${fullSha('b').slice(0, 24)}`, tags: [`sha256-${d}.att`], createdAt: ago(v.min - 1) });
    out.push({ digest: `sha256:${fullSha('c' + v.sha)}${fullSha('c').slice(0, 24)}`, tags: [`sha256-${d}`], createdAt: ago(v.min - 1) });
  });
  return out;
}

export function deployHistoryFor(appName: string, envs: Array<{ env: string }>) {
  const app = appByName(appName);
  if (!app) return {};
  const out: Record<string, any[]> = {};
  envs.forEach(({ env }) => {
    const v = app.versions[env];
    if (!v) return;
    const hist: any[] = [];
    if (app.name === FEATURED) {
      const offs: Record<string, number> = { dev: 0, staging: 30, prod: 90 };
      hist.push({ sha: fullSha('5d2c9b7'), date: ago(7100 - (offs[env] ?? 0)), imageTag: '1.7.0-5d2c9b7' });
      hist.push({ sha: fullSha('8e3f1a0'), date: ago(4200 - (offs[env] ?? 0)), imageTag: '1.7.1-8e3f1a0' });
      hist.push({ sha: fullSha('b71e0d4'), date: ago(1400 - (offs[env] ?? 0)), imageTag: '1.7.2-b71e0d4' });
      if (env === 'dev') hist.push({ sha: fullSha('4f9c2ab'), date: ago(95), imageTag: '1.8.0-4f9c2ab' });
    } else if (app.name === 'baggage-api' && env === 'dev') {
      hist.push({ sha: fullSha('e04d9a3'), date: ago(3050), imageTag: '3.1.5-e04d9a3' });
    }
    hist.push({ sha: fullSha(v.sha), date: ago(v.deployedMin), imageTag: `${v.ver}-${v.sha}` });
    out[env] = hist;
  });
  return out;
}

export function argoAppFor(argoName: string) {
  const m = argoName.match(/^(.*)-(dev|staging|prod)$/);
  const app = appByName(m?.[1]);
  const env = m?.[2];
  if (!app || !env) return [];
  const canaryHere = app.canary?.env === env;
  const v = app.versions[env];
  const kinds = app.strategy === 'canary' ? ['Rollout', 'Service', 'Service', 'Service', 'HTTPRoute', 'ConfigMap', 'ExternalSecret', 'ServiceMonitor', 'AnalysisTemplate'] : ['Deployment', 'Service', 'HTTPRoute', 'ConfigMap', 'ExternalSecret', 'ServiceMonitor'];
  const names = app.strategy === 'canary' ? [app.name, app.name, `${app.name}-canary`, `${app.name}-stable`, app.name, `${app.name}-config`, `${app.name}-secrets`, app.name, 'success-rate'] : [app.name, app.name, app.name, `${app.name}-config`, `${app.name}-secrets`, app.name];
  return [
    {
      applications: [
        {
          metadata: { name: argoName },
          spec: {
            source: { repoURL: `https://github.com/${OWNER}/gitops-${env === 'prod' ? 'prod' : 'dev'}`, path: `apps/${app.name}/${env}`, targetRevision: 'main' },
            syncPolicy: { automated: { prune: true, selfHeal: true } },
          },
          status: {
            sync: { status: 'Synced', revision: fullSha(v.sha).split('').reverse().join('') },
            health: { status: canaryHere ? 'Suspended' : 'Healthy', lastTransitionTime: ago(canaryHere ? 6 : v.deployedMin - 2) },
            reconciledAt: ago(1),
            operationState: { phase: 'Succeeded', message: 'successfully synced (all tasks run)', startedAt: ago(v.deployedMin + 1), finishedAt: ago(v.deployedMin) },
            resources: kinds.map((k, i) => ({ kind: k, name: names[i], namespace: `app-${app.name}-${env}`, status: 'Synced', health: { status: k === 'Rollout' && canaryHere ? 'Suspended' : 'Healthy' } })),
          },
        },
      ],
    },
  ];
}

export function repoHead(repo: string, ref?: string) {
  const app = appByName(repo);
  return { sha: ref ?? fullSha(app?.versions.dev.sha ?? '0000000'), branch: 'main', author: 'jamie-dev', pushedAt: ago(110), message: 'Record a gate change and its event in one transaction' };
}

export const pipelineOrder = { order: ['dev', 'staging', 'prod'], lower: ['dev', 'staging'], upper: ['prod'], upperClusters: { prod: 'prod' } };

// ---------- pull requests ----------
export function demoPullRequests(appName: string) {
  const app = appByName(appName);
  if (!app) return [];
  const url = (repo: string, n: number) => `https://github.com/${OWNER}/${repo}/pull/${n}`;
  const checks = (state: 'success' | 'pending') => [
    { name: 'Pipelines as Code CI / sast-check', status: 'completed', conclusion: 'success', message: 'SAST attestation verified: 0 blocking findings' },
    { name: 'Pipelines as Code CI / image-scan-check', status: 'completed', conclusion: 'success', message: 'No critical or high CVEs' },
    { name: 'Pipelines as Code CI / provenance-check', status: 'completed', conclusion: 'success', message: 'SLSA provenance signed by tekton-chains, Rekor entry found' },
    { name: 'Pipelines as Code CI / sbom-check', status: 'completed', conclusion: 'success', message: 'SPDX SBOM attached (212 packages)' },
    { name: 'Pipelines as Code CI / image-promotion-check', status: state === 'pending' ? 'in_progress' : 'completed', conclusion: state === 'pending' ? undefined : 'success', message: 'Image already running in staging for 45m' },
    { name: 'Pipelines as Code CI / governance-check', status: 'completed', conclusion: 'success', message: 'Change window open, approver present' },
  ];
  const prs: any[] = [];
  if (app.name === FEATURED) {
    prs.push(
      { number: 214, repo: 'gitops', title: 'Release: flight-api to prod @ 1.8.0-4f9c2ab', url: url('gitops-prod', 214), state: 'merged', author: 'glidepath-bot', labels: ['release'], createdAt: ago(20), updatedAt: ago(10), mergedAt: ago(10), mergeCommitSha: fullSha('aa12bc3'), review: { state: 'approved' }, ci: { state: 'success', passedChecks: 6, totalChecks: 6, checks: checks('success') } },
      { number: 188, repo: 'source', title: 'Publish flight events to the broker', url: url('flight-api', 188), state: 'open', author: 'sam-r', labels: ['preview'], createdAt: ago(300), updatedAt: ago(250), review: { state: 'changes_requested' }, ci: { state: 'failure', passedChecks: 3, totalChecks: 4, checks: [] } },
      { number: 191, repo: 'source', title: 'Page the flight events endpoint', url: url('flight-api', 191), state: 'open', author: 'priya-k', labels: [], createdAt: ago(90), updatedAt: ago(5), review: { state: 'pending' }, ci: { state: 'pending', passedChecks: 2, totalChecks: 4, checks: [] } },
      { number: 187, repo: 'source', title: 'Record a gate change and its event in one transaction', url: url('flight-api', 187), state: 'merged', author: 'jamie-dev', labels: [], createdAt: ago(600), updatedAt: ago(110), mergedAt: ago(110), mergeCommitSha: fullSha('4f9c2ab'), review: { state: 'approved' } },
      { number: 185, repo: 'source', title: 'Use estimated departure for the boarding group', url: url('flight-api', 185), state: 'merged', author: 'alex-m', labels: [], createdAt: ago(1700), updatedAt: ago(1510), mergedAt: ago(1510), mergeCommitSha: fullSha('b71e0d4'), review: { state: 'approved' } },
      { number: 209, repo: 'gitops', title: 'Release: flight-api to prod @ 1.7.2-b71e0d4', url: url('gitops-prod', 209), state: 'merged', author: 'glidepath-bot', labels: ['release'], createdAt: ago(1340), updatedAt: ago(1310), mergedAt: ago(1310), review: { state: 'approved' } },
    );
  } else if (app.name === 'baggage-api') {
    prs.push({ number: 77, repo: 'gitops', title: 'Release: baggage-api to staging @ 0.6.0-71b8e2c', url: url('gitops-dev', 77), state: 'open', author: 'glidepath-bot', labels: ['release'], createdAt: ago(25), updatedAt: ago(3), review: { state: 'pending' }, ci: { state: 'pending', passedChecks: 5, totalChecks: 6, checks: checks('pending') } });
  }
  return prs;
}

// ---------- notifications ----------
export function notificationsFor(search?: string) {
  const app = appByName(search) ?? APPS[0];
  const n = (id: number, min: number, topic: string, title: string, description: string, severity = 'normal') => ({
    id: `n-${app.name}-${id}`,
    user: 'user:default/demo',
    created: new Date(NOW - min * 60_000),
    origin: 'plugin:glidepath',
    payload: { title, description, topic, severity, link: '/tower' },
  });
  if (app.name !== FEATURED) return [n(1, 300, 'build', `${app.name}: build succeeded`, `${app.versions.dev.ver}-${app.versions.dev.sha} · main`)];
  const repo = `${OWNER}/${FEATURED}`;
  const d = (env: string | undefined, sha: string, tag: string, extra = '') =>
    [env ? `Environment: ${env}` : '', `Repo: ${repo} @ ${sha}`, `Image: ghcr.io/${repo}:${tag}`, `Chain: c-${sha.slice(0, 4)}`, extra].filter(Boolean).join('\n');
  return [
    n(1, 4, 'build', 'flight-api: build started', d(undefined, 'd81f3c6', '1.9.0-d81f3c6')),
    n(2, 9, 'deploying', 'flight-api: deploying to prod', d('prod', '4f9c2ab', '1.8.0-4f9c2ab')),
    n(3, 10, 'release', 'flight-api: release PR merged', d('prod', '4f9c2ab', '1.8.0-4f9c2ab', `PR: https://github.com/${OWNER}/gitops-prod/pull/214`)),
    n(4, 20, 'release', 'flight-api: release PR opened', d('prod', '4f9c2ab', '1.8.0-4f9c2ab', `PR: https://github.com/${OWNER}/gitops-prod/pull/214`)),
    n(10, 32, 'test', 'flight-api: tests succeeded', d('dev', '6a0e5d2', '1.8.1-6a0e5d2')),
    n(11, 38, 'deploy', 'flight-api: deploy succeeded', d('dev', '6a0e5d2', '1.8.1-6a0e5d2')),
    n(12, 47, 'build', 'flight-api: build succeeded', d(undefined, '6a0e5d2', '1.8.1-6a0e5d2')),
    n(5, 62, 'deploy', 'flight-api: deploy succeeded', d('staging', '4f9c2ab', '1.8.0-4f9c2ab')),
    n(6, 80, 'test', 'flight-api: tests succeeded', d('dev', '4f9c2ab', '1.8.0-4f9c2ab')),
    n(7, 95, 'deploy', 'flight-api: deploy succeeded', d('dev', '4f9c2ab', '1.8.0-4f9c2ab')),
    n(8, 104, 'build', 'flight-api: build succeeded', d(undefined, '4f9c2ab', '1.8.0-4f9c2ab')),
    n(9, 255, 'build', 'flight-api: build failed', d(undefined, '0c2d7e9', '1.7.3-0c2d7e9'), 'high'),
  ];
}


// ---------- Prometheus ----------
function hashStr(s: string) { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) | 0; return Math.abs(h); }
export function promInstant(query: string) {
  const services = APPS.map(a => a.name);
  if (query.includes('slo:')) {
    const svc = query.match(/sloth_service="([^"]+)"/)?.[1];
    const slo = query.match(/sloth_slo="([^"]+)"/)?.[1];
    const targets: Array<[string, string]> = svc && slo ? [[svc, slo]] : services.flatMap(s => ['dev', 'staging', 'prod'].flatMap(e => [[s, `availability_app-${s}-${e}`], [s, `latency_app-${s}-${e}`]] as Array<[string, string]>));
    const out: any[] = [];
    targets.forEach(([s, sl]) => {
      const h = hashStr(s + sl);
      const isProd = sl.endsWith('-prod');
      const objective = sl.startsWith('availability') && isProd ? 0.999 : 0.99;
      const burn = (h % 70) / 100 + 0.12;
      const remaining = 1 - burn * 0.55;
      const metric = (name: string, extra: Record<string, string> = {}) => ({ __name__: name, sloth_service: s, sloth_slo: sl, sloth_id: `${s}-${sl}`, ...extra });
      if (query.includes('sli_error')) {
        ['5m', '30m', '1h', '2h', '6h', '1d', '3d', '30d'].forEach((w, i) => out.push({ metric: metric(`slo:sli_error:ratio_rate${w}`, { sloth_window: w }), value: [NOW / 1000, String((1 - objective) * burn * (0.7 + ((h >> i) % 5) / 10))] }));
      } else {
        const push = (name: string, v: number) => out.push({ metric: metric(name), value: [NOW / 1000, String(v)] });
        if (query.includes('objective') || !query.includes('period_burn_rate|period_error')) push('slo:objective:ratio', objective);
        if (query.includes('current_burn_rate')) push('slo:current_burn_rate:ratio', burn * 0.9);
        push('slo:period_burn_rate:ratio', burn);
        push('slo:period_error_budget_remaining:ratio', remaining);
        if (query.includes('time_period')) push('slo:time_period:days', 30);
      }
    });
    return { status: 'success', data: { resultType: 'vector', result: out } };
  }
  return { status: 'success', data: { resultType: 'vector', result: [{ metric: {}, value: [NOW / 1000, String(0.0021 + (hashStr(query) % 10) / 10000)] }] } };
}

export function promRange(query: string, start: number, end: number, step: number) {
  const h = hashStr(query);
  const pods = [...query.matchAll(/pod=~"([^"]+)"/g)].map(m => m[1]);
  const names = pods.length ? pods[0].split('|').slice(0, 4) : ['series'];
  const base = query.includes('memory') ? 180e6 : query.includes('cpu') ? 0.12 : query.includes('network') ? 42_000 : query.includes('fs_') ? 8_000 : 0.002;
  const result = names.map((pod, idx) => {
    const values: Array<[number, string]> = [];
    for (let t = start; t <= end; t += step) {
      const x = (t - start) / (end - start || 1);
      const v = base * (1 + 0.25 * Math.sin(x * 9 + idx + (h % 7)) + 0.1 * Math.sin(x * 37 + idx * 3) + idx * 0.08);
      values.push([t, String(Math.max(0, v))]);
    }
    return { metric: { pod }, values };
  });
  return { status: 'success', data: { resultType: 'matrix', result } };
}

// ---------- release records ----------
export function releaseRecordFor(params: URLSearchParams) {
  const app = params.get('appName');
  const tag = params.get('imageTag') ?? '';
  const docs: Record<string, any> = {
    '1.8.0-4f9c2ab': {
      summary: 'Gate changes and their events now commit in one transaction, so the gate board can never show a gate the event stream never announced.',
      risk: 'medium',
      riskNotes: 'Touches the gate write path. Canary holds at 40% for the error-rate analysis before going wider.',
      verificationNotes: 'e2e-smoke green in dev and staging. Watched gate-change latency in staging for 45m, p99 flat at 38ms.',
      approvals: [{ by: 'priya-k', at: ago(18), role: 'service owner' }, { by: 'sam-r', at: ago(16), role: 'on-call' }],
      authoredBy: 'jamie-dev',
      tags: ['gate-board', 'outbox'],
    },
    '1.7.2-b71e0d4': {
      summary: 'Boarding groups use the estimated departure time instead of the scheduled one.',
      risk: 'low',
      verificationNotes: 'Checked against three delayed flights in staging.',
      approvals: [{ by: 'priya-k', at: ago(1320), role: 'service owner' }],
      authoredBy: 'alex-m',
    },
  };
  const hc = app === FEATURED ? docs[tag] : undefined;
  if (!hc) return { found: false };
  const [ver, sha] = tag.split('-');
  return {
    schemaVersion: 1,
    id: `${app}-${tag}`,
    appName: app,
    imageTag: tag,
    imageRepo: `ghcr.io/${OWNER}/${app}`,
    gitRevisionShort: sha,
    cluster: 'prod',
    env: 'prod',
    generatedAt: ago(tag.startsWith('1.8.0') ? 8 : 1300),
    humanContext: hc,
    _ok: true,
  };
}

// ---------- config / cicd ----------
export function cicdFor(appName: string) {
  const app = appByName(appName);
  const agent = { nodejs: 'nodejs-20', springboot: 'openjdk-21', go: 'go-1.23', python: 'python-3.12' }[app?.lang ?? 'nodejs'];
  const values: any = {
    build: { agent, containerfile: './Containerfile', unitTest: { enabled: true, command: './test.sh' }, cache: { enabled: true, size: 'medium' } },
    test: { enabled: true, name: 'e2e-smoke' },
    deploy: { lowerEnvironments: ['dev', 'staging'], upperEnvironments: [{ name: 'prod', cluster: 'prod' }], strategy: 'rollout', promotionOrder: ['dev', 'staging', 'prod'] },
    ephemeralEnvironments: { pullRequest: { enabled: true, labels: ['preview'] }, ttl: '3d' },
    governance: { sast: true, imageScan: true, policyCheck: true, sbom: true, allowedCommitSigners: ['jamie@example.com', 'priya@example.com', 'sam@example.com'] },
    notifications: { slack: { enabled: true, channel: '#skyport-releases', scanResults: true }, backstage: { enabled: true } },
    pipelines: {
      ci: {
        trigger: { source: 'git', event: 'push', branch: 'main' },
        steps: [
          { stage: 'build' }, { stage: 'deploy', env: 'dev' }, { stage: 'test', env: 'dev', testName: 'e2e-smoke' },
          { stage: 'deploy', env: 'staging' }, { stage: 'release', env: 'prod' },
        ],
      },
    },
  };
  const raw = 'apiVersion: platform/v1\nkind: PipelineConfig\n\n' + yamlDump(values);
  return { repo: `${OWNER}/${appName}`, path: 'cicd.yaml', apiVersion: 'platform/v1', kind: 'PipelineConfig', values, raw };
}

export function appConfigFor(appName: string, env: string, cluster: string) {
  const app = appByName(appName);
  const prod = env === 'prod';
  const values: any = {
    rollout: {
      replicas: app?.replicas[env] ?? 2,
      ports: [{ name: 'http', containerPort: app?.port ?? 8080 }],
      resources: { requests: { cpu: prod ? '250m' : '100m', memory: prod ? '512Mi' : '256Mi' }, limits: { cpu: prod ? '1' : '500m', memory: prod ? '1Gi' : '512Mi' } },
      livenessProbe: { httpGet: { path: '/livez', port: 'http' }, periodSeconds: 20 },
      readinessProbe: { httpGet: { path: '/healthz', port: 'http' }, periodSeconds: 10 },
      ...(app?.strategy === 'canary' ? { steps: CANARY_STEPS.map((st: any) => st.analysis ? { analysis: { templates: st.analysis.templates, args: [{ name: 'canary-hash', valueFrom: { podTemplateHashValue: 'Latest' } }] } } : st) } : {}),
    },
    env: [{ name: 'LOG_LEVEL', value: prod ? 'info' : 'debug' }, { name: 'SIMULATOR_ENABLED', value: prod ? 'false' : 'true' }, { name: 'SIMULATOR_INTERVAL_MS', value: '30000' }],
    autoscaling: prod ? { enabled: true, min: app?.replicas.prod, max: (app?.replicas.prod ?? 2) * 3, targetCPUPercent: 70 } : { enabled: false },
    podDisruptionBudget: env === 'dev' ? { enabled: false } : { enabled: true, minAvailable: 1 },
    httpRoute: { enabled: true, hostnames: [`${appName}.${env}.example.internal`], parentRefs: [{ name: 'hangar', namespace: 'hangar-gateway' }] },
    serviceMonitor: { enabled: true, path: '/metrics', interval: '30s' },
    networkPolicy: { enabled: true, allowIngressFromIngressController: true },
    serviceAccount: { create: true },
    ...(appName === FEATURED ? { components: [{ type: 'postgresql', name: 'flight-db', spec: { instances: prod ? 3 : 1, storage: prod ? '20Gi' : '5Gi' } }] } : {}),
    notifications: { slack: { enabled: true, channel: '#skyport-releases' } },
    slos: [{ name: 'availability', objective: prod ? 99.9 : 99 }, { name: 'latency', objective: 99, thresholdSeconds: 0.3 }],
  };
  const raw = yamlDump(values);
  return { cluster, env, path: `apps/${appName}/${env}/values.yaml`, values, raw };
}
