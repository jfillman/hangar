export const isKubernetesAvailable = (e: any) => Boolean(e?.metadata?.annotations?.['backstage.io/kubernetes-id'] || e?.metadata?.annotations?.['backstage.io/kubernetes-label-selector']);
