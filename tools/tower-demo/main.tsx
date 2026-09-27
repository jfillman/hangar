import '@fontsource/ibm-plex-sans/400.css';
import '@fontsource/ibm-plex-sans/500.css';
import '@fontsource/ibm-plex-sans/600.css';
import '@fontsource/ibm-plex-sans/700.css';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import '@fontsource/ibm-plex-mono/600.css';
import '@fontsource/ibm-plex-sans-condensed/500.css';
import '@fontsource/ibm-plex-sans-condensed/600.css';
import '@fontsource/ibm-plex-sans-condensed/700.css';
import { translationApiRef } from '@backstage/core-plugin-api/alpha';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ApiProvider } from '@backstage/core-app-api';
import { discoveryApiRef, fetchApiRef, errorApiRef, alertApiRef } from '@backstage/core-plugin-api';
import { catalogApiRef, starredEntitiesApiRef } from '@backstage/plugin-catalog-react';
import { notificationsApiRef } from '@backstage/plugin-notifications';
import { UnifiedThemeProvider, themes } from '@backstage/theme';
import CssBaseline from '@material-ui/core/CssBaseline';
import { kubernetesApiRef, kubernetesProxyApiRef } from './mock/k8sReact';
import { apis } from './mock/apis';
import { TowerPage } from './tower/src/TowerPage';

class Registry {
  constructor(private m: Map<string, unknown>) {}
  get(ref: { id: string }) { return this.m.get(ref.id) as any; }
}
const registry = new Registry(new Map<string, unknown>([
  [discoveryApiRef.id, apis.discovery],
  [fetchApiRef.id, apis.fetch],
  [translationApiRef.id, (() => {
    const make = (ref: any) => { const msgs = ref.getDefaultMessages?.() ?? ref.messages ?? {}; return { ready: true, t: (k: string, o?: any) => { let m = msgs[k] ?? k; if (o) Object.keys(o).forEach(x => { m = m.replace(`{{${x}}}`, o[x]).replace(`{{ ${x} }}`, o[x]); }); return m; } }; };
    return { getTranslation: make, translation$: (ref: any) => ({ subscribe: (fn: any) => { (typeof fn === 'function' ? fn : fn.next)?.(make(ref)); return { unsubscribe() {} }; } }) };
  })()],
  [errorApiRef.id, { post: () => {}, error$: () => ({ subscribe: () => ({ unsubscribe() {} }) }) }],
  [alertApiRef.id, { post: () => {}, alert$: () => ({ subscribe: () => ({ unsubscribe() {} }) }) }],
  [catalogApiRef.id, apis.catalog],
  [starredEntitiesApiRef.id, apis.starred],
  [notificationsApiRef.id, apis.notifications],
  [kubernetesApiRef.id, apis.kubernetes],
  [kubernetesProxyApiRef.id, apis.kubernetesProxy],
]));

createRoot(document.getElementById('root')!).render(
  <ApiProvider apis={registry}>
    <UnifiedThemeProvider theme={themes.dark}>
      <CssBaseline />
      <BrowserRouter>
        <TowerPage />
      </BrowserRouter>
    </UnifiedThemeProvider>
  </ApiProvider>,
);
