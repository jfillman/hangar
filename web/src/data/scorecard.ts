// The Airframe scorecard over time. Every snapshot is a JSON file the scorecard tool wrote
// (tools/airframe-scorecard/scorecard.py --json), committed beside the tool, so the numbers on
// the page are the tool's own output, never retyped. To add a snapshot: run the tool with
// --json baseline-<date>.json, commit it, and give it a label below.
import { gh, ghTree } from '../lib/url';

type Raw = {
  overall: number;
  grade: string;
  a_plus: boolean;
  dimensions: Record<string, { score: number; grade: string; checks: Record<string, number>; note: string }>;
  acceptance: Record<string, boolean>;
};

const files = import.meta.glob<Raw>('../../../tools/airframe-scorecard/baseline-*.json', { eager: true, import: 'default' });

// What each snapshot was, in words. A file with no entry here still shows, labelled by its file name.
const labels: Record<string, { date: string; label: string; note: string }> = {
  'baseline-2026-09-26': {
    date: '2026-09-26',
    label: 'Baseline',
    note: 'Before any of the A+ work. One acceptance check passed: every live values file rendered.',
  },
  'baseline-2026-09-26b': {
    date: '2026-09-26',
    label: 'M0',
    note: 'The chart guard, chart tests and CI, AGENTS.md and a first airframe validate. M0 closed the next day against a target of 35.',
  },
  'baseline-2026-09-29': {
    date: '2026-09-29',
    label: 'M1 and M2',
    note: 'A strict schema, component outputs, a contract bundle, the release-file split, an ownership gate, field-level agent scope and replayable walkthroughs.',
  },
  'baseline-2026-10-09': {
    date: '2026-10-09',
    label: 'Review fixes',
    note: 'Fixes from the architecture review: AGENTS.md on every component, an owner and a risk class on every values field, status conditions and reason codes on 17 of 20 XRDs, and every XRD described and in the catalog. Past the M2 target of 75 for the first time.',
  },
  'baseline-2026-10-09b': {
    date: '2026-10-09',
    label: 'AppSpec in the contract',
    note: 'The AppSpec schema (one document stating an app and its environments) moved into Airframe\'s contract bundle, where an agent reading the contract finds it. Interaction surface doubled; the airframe.* tools are what it still lacks.',
  },
  'baseline-2026-10-25': {
    date: '2026-10-25',
    label: 'Cloud targets and the rebuild',
    note: 'Three new XRDs (23 in all), cross-field CEL rules on 22 of them, fromComponent in nearly every env entry (2 literals left of 78), 23 chart guards and 48 chart tests, seven walkthroughs. Past the M3 target of 88, though M3 itself (the planner and airframe.* tools) is not built. The chart README got shorter when it was rewritten to describe today\'s chart, which cost a little discoverability.',
  },
  'baseline-2026-10-28': {
    date: '2026-10-28',
    label: 'airframe.* tools behind Clearance',
    note: 'Seven read-only airframe.* tools (capabilities, validate, explain, plan, status, describe, verify) behind Clearance over a GET-only Kubernetes reader, live on hangar-dev through MCP (autopilot#19). The planner\'s cicd.yaml patch now passes Glidepath\'s agent scope. The schema marks its 12 deliberate passthroughs, so every other object is strict (airframe#128). The scorecard itself got more honest (hangar#94): tools are counted from what Clearance registers rather than a file name, the extraManifests deny is measured instead of hard-coded, and typed maps and if/then fragments are no longer miscounted as open objects. One check left: two cross-app URLs that wait on fromService.',
  },
};

export type Snapshot = Raw & { id: string; date: string; label: string; note: string; passed: number };

export const snapshots: Snapshot[] = Object.entries(files)
  .map(([path, raw]) => {
    const id = path.split('/').pop()!.replace(/\.json$/, '');
    const meta = labels[id] ?? { date: id.replace(/^baseline-/, '').slice(0, 10), label: id, note: '' };
    return { ...raw, id, ...meta, passed: Object.values(raw.acceptance).filter(Boolean).length };
  })
  .sort((a, b) => a.id.localeCompare(b.id));

export const latest = snapshots[snapshots.length - 1];
export const first = snapshots[0];

// The roadmap's milestone targets (docs/autopilot/roadmap.md). A+ is 97 and all fourteen checks.
export const targets = [
  { milestone: 'M0', score: 35, name: 'Stabilize' },
  { milestone: 'M1', score: 60, name: 'Contract' },
  { milestone: 'M2', score: 75, name: 'Safe write' },
  { milestone: 'M3', score: 88, name: 'Autopilot core' },
  { milestone: 'M4', score: 93, name: 'Skyport AI' },
  { milestone: 'M5', score: 97, name: 'Evidence' },
];
export const aPlus = 97;

// What the latest run found, and what A+ still needs, per dimension. Written from the latest
// snapshot's own metrics; update these when a new snapshot moves a dimension.
export const findings: Record<string, { found: string; next: string }> = {
  '1 Discoverability': {
    found: 'AGENTS.md on all 23 components and every XRD in the catalog; the chart README is down to 170 lines',
    next: 'a chart README that documents every values key again',
  },
  '2 Schema precision': {
    found: 'every schema node is described; all 67 non-passthrough objects strict, 12 passthroughs marked; 22 of 23 XRDs carry a cross-field CEL rule',
    next: 'tighter leaf fields (78 of 206 constrained), examples',
  },
  '3 Component contracts': {
    found: 'every component declares outputs and verify checks; 2 of 80 env entries still hard-code a name (cross-app URLs)',
    next: 'fromService for the two cross-app URLs',
  },
  '4 Pre-merge validation': {
    found: 'airframe validate is a required check, with 23 chart guards that say what to fix',
    next: 'the last two chart guards',
  },
  '5 Write safety': {
    found: 'every values field carries an owner and a risk class; no live file mixes owners',
    next: 'held; keep machine-owned data in the release file',
  },
  '6 Observe and verify': {
    found: '20 of 23 XRDs declare status conditions and a closed set of reason codes',
    next: 'the last three XRDs; describe and status tools are live',
  },
  '7 Docs for agents': {
    found: 'seven walkthroughs replay live, and every YAML block in the user docs parses',
    next: 'held; every new component ships its walkthrough',
  },
  '8 Interaction surface': {
    found: 'seven read-only airframe.* tools behind Clearance, live through MCP; the planner\'s output passes Glidepath\'s agent scope',
    next: 'airframe.apply as the agents\' own GitHub App (AF-8b), and a config API beside Tower\'s UI',
  },
  '9 Safety integration': {
    found: 'every values field is risk-classed and field-level agent scope is built into Clearance',
    next: 'held; extraManifests and the other escape hatches stay denied to agents',
  },
  '10 Hygiene and determinism': {
    found: 'helm lint, 48 chart tests and chart CI; all 17 live values files render',
    next: 'held; keep the fleet rendering clean',
  },
};

export const links = {
  tool: gh('hangar', 'tools/airframe-scorecard/scorecard.py'),
  data: ghTree('hangar', 'tools/airframe-scorecard'),
  rubric: gh('hangar', 'docs/autopilot/airframe-ai-friendly.md'),
  roadmap: gh('hangar', 'docs/autopilot/roadmap.md'),
};
