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
    found: 'AGENTS.md on all 20 components; every XRD is in the catalog or opts out with a reason',
    next: 'held; every new component ships its AGENTS.md',
  },
  '2 Schema precision': {
    found: 'every schema node and XRD field is described; 46 of 82 objects strict; 8 of 20 XRDs carry a CEL rule',
    next: 'every object strict, tighter leaf fields, examples',
  },
  '3 Component contracts': {
    found: 'every component declares outputs and verify checks; 33 of 47 env entries still hard-code a name',
    next: 'fromComponent in every live env entry',
  },
  '4 Pre-merge validation': {
    found: 'airframe validate is a required check, with 11 dead-end rules and 18 chart guards',
    next: 'the last seven chart guards, with actionable messages',
  },
  '5 Write safety': {
    found: 'every values field carries an owner and a risk class; no live file mixes owners',
    next: 'held; keep machine-owned data in the release file',
  },
  '6 Observe and verify': {
    found: '17 of 20 XRDs declare status conditions and a closed set of reason codes',
    next: 'the last three XRDs, a describe tool',
  },
  '7 Docs for agents': {
    found: 'all three quickstarts replay as live walkthroughs, green',
    next: 'held; every new component ships its walkthrough',
  },
  '8 Interaction surface': {
    found: 'still Tower and Git only; no AppSpec schema, no airframe.* tools',
    next: 'AppSpec, the planner and airframe.* tools (M3)',
  },
  '9 Safety integration': {
    found: 'every values field is risk-classed and field-level agent scope is built into Clearance',
    next: 'escape hatches (extraManifests) denied by default',
  },
  '10 Hygiene and determinism': {
    found: 'helm lint, 30 chart tests and chart CI; all 21 live values files render',
    next: 'held; keep the fleet rendering clean',
  },
};

export const links = {
  tool: gh('hangar', 'tools/airframe-scorecard/scorecard.py'),
  data: ghTree('hangar', 'tools/airframe-scorecard'),
  rubric: gh('hangar', 'docs/autopilot/airframe-ai-friendly.md'),
  roadmap: gh('hangar', 'docs/autopilot/roadmap.md'),
};
