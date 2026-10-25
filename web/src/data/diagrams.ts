import all from './diagrams.generated.json';

export type Diagram = {
  id: string;
  set: 'overview' | 'plan' | 'autopilot' | 'reference' | 'glidepath' | 'crossplane' | 'catalog' | 'expansion' | 'paving' | 'portability' | 'testing' | 'slo' | 'breakglass';
  num: string;
  title: string;
  eyebrow: string;
  path: string;
};

export const diagrams = all as Diagram[];

export const SET_LABELS: Record<Diagram['set'], string> = {
  overview: 'Hangar at a glance',
  autopilot: 'Autopilot',
  plan: 'Plan',
  reference: 'Reference architecture',
  glidepath: 'Glidepath',
  crossplane: 'Crossplane journey',
  catalog: 'Service catalog',
  expansion: 'Beyond the cluster',
  paving: 'Paving the cloud',
  portability: 'Any forge, any registry',
  testing: 'Testing',
  slo: 'SLOs',
  breakglass: 'Break-glass',
};

export function diagram(id: string): Diagram {
  const d = diagrams.find((x) => x.id === id);
  if (!d) throw new Error(`Unknown diagram id: ${id}. Run npm run sync, or check the id.`);
  return d;
}

export const bySet = (set: Diagram['set']) => diagrams.filter((d) => d.set === set);
