import { createApiRef, useApi } from '@backstage/core-plugin-api';
import { useEffect, useState } from 'react';
import { k8sObjectsFor, customResourcesFor } from './fixtures';

export const kubernetesApiRef = createApiRef<any>({ id: 'plugin.kubernetes.service' });
export const kubernetesProxyApiRef = createApiRef<any>({ id: 'plugin.kubernetes.proxy' });

function useTick() {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 5000);
    return () => clearInterval(id);
  }, []);
  return tick;
}

export function useKubernetesObjects(entity: any) {
  const tick = useTick();
  const [state, setState] = useState<any>({ loading: true });
  useEffect(() => {
    const t = setTimeout(() => setState({ loading: false, kubernetesObjects: k8sObjectsFor(entity) }), 250);
    return () => clearTimeout(t);
  }, [entity?.metadata?.name, tick]);
  return { kubernetesObjects: state.kubernetesObjects, loading: state.loading, error: undefined };
}

export function useCustomResources(entity: any, matchers: any[]) {
  const tick = useTick();
  const [state, setState] = useState<any>({ loading: true });
  const key = matchers.map(m => m.plural).join(',');
  useEffect(() => {
    const t = setTimeout(() => setState({ loading: false, kubernetesObjects: customResourcesFor(entity, matchers) }), 250);
    return () => clearTimeout(t);
  }, [entity?.metadata?.name, key, tick]);
  return { kubernetesObjects: state.kubernetesObjects, loading: state.loading, error: undefined };
}
export { useApi };
