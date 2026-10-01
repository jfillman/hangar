import all from './diagrams.generated.json';

export type Diagram = {
  id: string;
  set: 'plan' | 'autopilot' | 'reference' | 'glidepath' | 'crossplane' | 'catalog' | 'slo';
  num: string;
  title: string;
  eyebrow: string;
  path: string;
};

export const diagrams = all as Diagram[];

export const SET_LABELS: Record<Diagram['set'], string> = {
  autopilot: 'Autopilot',
  plan: 'Plan',
  reference: 'Reference architecture',
  glidepath: 'Glidepath',
  crossplane: 'Crossplane journey',
  catalog: 'Service catalog',
  slo: 'SLOs',
};

export function diagram(id: string): Diagram {
  const d = diagrams.find((x) => x.id === id);
  if (!d) throw new Error(`Unknown diagram id: ${id}. Run npm run sync, or check the id.`);
  return d;
}

export const bySet = (set: Diagram['set']) => diagrams.filter((d) => d.set === set);
