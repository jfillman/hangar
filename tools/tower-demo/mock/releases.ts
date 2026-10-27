// The release record routes Tower added after the September walkthrough (R1 to R4: the draft, release modes,
// sign-off, outcomes, planned scope and the fleet calendar), for flight-api's invented history. Every name,
// person and number here is made up for the Skyport demo.
import { ago, FEATURED, OWNER } from './fixtures';

const gh = (repo: string, kind: 'pull' | 'issues', n: number) => `https://github.com/${OWNER}/${repo}/${kind}/${n}`;

// flight-api's committed records, oldest first. The names (ASPEN, BIRCH, CEDAR, DOGWOOD) follow from this order.
const HISTORY = [
  { imageTag: '1.7.0-5d2c9b7', at: 7200, owner: 'jamie-dev', summary: 'Gates can be reassigned while boarding is open.',
    notes: { added: ['Reassign a gate during boarding (#176)'] }, outcome: 'clean' as const, closedBy: 'superseded' as const },
  { imageTag: '1.7.1-8e3f1a0', at: 4200, owner: 'alex-m', summary: 'Departure board reads its gates from the cache first.',
    notes: { changed: ['Read gates from the cache before the database (#181)'] }, outcome: 'clean' as const, closedBy: 'superseded' as const },
  { imageTag: '1.7.2-b71e0d4', at: 1300, owner: 'alex-m', summary: 'Boarding groups use the estimated departure time instead of the scheduled one.',
    notes: { fixed: ['Use estimated departure for the boarding group (#185)'] }, outcome: 'clean' as const, closedBy: 'superseded' as const },
  { imageTag: '1.8.0-4f9c2ab', at: 8, owner: 'jamie-dev', summary: 'Gate changes and their events now commit in one transaction, so the gate board can never show a gate the event stream never announced.',
    notes: { changed: ['Record a gate change and its event in one transaction (#187)'] } },
];

const signoffFor = (prNumber: number, mergedMin: number, by: string, approvedMin: number) => ({
  env: 'prod', prNumber, prUrl: gh('gitops-prod', 'pull', prNumber), state: 'merged' as const, author: 'glidepath-bot',
  mergedBy: 'jamie-dev', mergedAt: ago(mergedMin),
  approvals: [{ by, at: ago(approvedMin), beforeMerge: true, counts: true }], status: 'signed' as const,
});

function outcomeOf(h: (typeof HISTORY)[number], i: number) {
  if (!h.outcome) return undefined;
  const next = HISTORY[i + 1];
  return { result: h.outcome, state: 'superseded', env: 'prod', healthyAt: ago(h.at - 20), closedAt: ago(next.at),
    closedBy: h.closedBy, supersededBy: next.imageTag, bakeDays: 7, sloMeasured: false as const };
}

export function releaseRecordsFor(app: string | null) {
  if (app !== FEATURED) return [];
  return HISTORY.map((h, i) => ({
    imageTag: h.imageTag, env: 'prod', generatedAt: ago(h.at), store: 'gitops', signoffs: 1,
    outcome: outcomeOf(h, i), summary: h.summary, notes: h.notes, owner: h.owner,
  }));
}

// The v2 block a sealed record carries: the draft it was released from, its mode and its sign-off.
export function sealedReleaseFor(tag: string) {
  const i = HISTORY.findIndex(h => h.imageTag === tag);
  if (i < 0) return {};
  const h = HISTORY[i];
  const sealed = tag === '1.8.0-4f9c2ab'
    ? { owner: h.owner, summary: h.summary, notes: h.notes, knownIssues: ['The gate board takes up to 30s to show a reassignment made during the rollout.'],
        risk: { level: 'medium' as const, notes: 'Touches the gate write path.', rollback: 'Safe to roll back to 1.7.2: the new outbox table is additive.' },
        mode: 'hand-flown' as const, signoff: signoffFor(214, 10, 'priya-k', 14) }
    : { owner: h.owner, summary: h.summary, notes: h.notes, mode: 'hand-flown' as const, signoff: signoffFor(209, h.at - 10, 'priya-k', h.at - 6) };
  return { schemaVersion: 2, release: sealed, outcome: outcomeOf(h, i) };
}

export const draftFor = (app: string | null) => app !== FEATURED ? {} : {
  owner: 'priya-k',
  summary: 'The gate board shows each gate\'s change history, and the departure board stops mixing time zones.',
  notes: {
    added: ['Gate change history endpoint (#189)'],
    fixed: ['Departure board times in the airport\'s own time zone (#190)'],
  },
  knownIssues: [],
  risk: { level: 'low', rollback: 'Safe to roll back to 1.8.0: no schema change.' },
  targetDate: new Date(Date.now() + 2 * 86_400_000).toISOString().slice(0, 10),
  updatedAt: ago(25),
  updatedBy: 'priya-k',
};

export const modeFor = (app: string | null) => ({
  mode: app === FEATURED ? 'hand-flown' : 'assisted',
  source: app === FEATURED ? 'app' : 'default',
  file: { owner: OWNER, repo: 'gitops-cluster-dev-tenants', path: 'release-modes.yaml' },
  signoffEnv: 'prod',
  settable: ['hand-flown', 'assisted'],
  canSetMode: true,
  canEditDraft: true,
});

export function signoffRoute(tag: string | null) {
  if (tag === '1.8.0-4f9c2ab') return signoffFor(214, 10, 'priya-k', 14);
  const h = HISTORY.find(x => x.imageTag === tag);
  return h ? signoffFor(209, h.at - 10, 'priya-k', h.at - 6) : undefined;
}

export const plannedFor = () => ({ issues: [] });

export const calendar = () => [
  { appName: FEATURED, owner: OWNER, mode: 'hand-flown', signoffEnv: 'prod',
    next: { name: 'ELM', targetDate: draftFor(FEATURED).targetDate, releaseOwner: 'priya-k', noteCount: 2 },
    inFlight: [], last: { name: 'DOGWOOD', imageTag: '1.8.0-4f9c2ab', at: ago(8) } },
  { appName: 'baggage-api', owner: OWNER, mode: 'assisted', signoffEnv: 'prod',
    next: { name: 'BIRCH', noteCount: 0 },
    inFlight: [{ env: 'prod', imageTag: '0.6.0-71b8e2c', prUrl: gh('gitops-prod', 'pull', 219) }],
    last: { name: 'ASPEN', imageTag: '0.5.2-1c4d9e0', at: ago(5200), outcome: 'clean' } },
  { appName: 'boarding-api', owner: OWNER, mode: 'assisted', signoffEnv: 'prod',
    next: { name: 'CEDAR', noteCount: 1 }, inFlight: [],
    last: { name: 'BIRCH', imageTag: '2.3.1-9a7b3f2', at: ago(2900), outcome: 'clean' } },
];
