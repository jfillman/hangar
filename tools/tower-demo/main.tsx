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
import { discoveryApiRef, fetchApiRef, errorApiRef, alertApiRef, identityApiRef, configApiRef } from '@backstage/core-plugin-api';
import { catalogApiRef, starredEntitiesApiRef } from '@backstage/plugin-catalog-react';
import { notificationsApiRef } from '@backstage/plugin-notifications';
import { UnifiedThemeProvider, themes } from '@backstage/theme';
import CssBaseline from '@material-ui/core/CssBaseline';
import { kubernetesApiRef, kubernetesProxyApiRef } from './mock/k8sReact';
import { apis } from './mock/apis';
import { currentUser, installDemoControls, installFakeWebSocket } from './mock/breakglass';

installFakeWebSocket();
installDemoControls();
const demoUser = currentUser();
// The "signed in as" pill is for the break-glass walkthrough, where whose view it is matters (?badge=1 or the
// recording script's sessionStorage flag); the original walkthrough never shows it.
const showBadge = (() => {
  try {
    const b = new URLSearchParams(window.location.search).get('badge');
    if (b === '1') sessionStorage.setItem('demo-badge', '1');
    if (b === '0') sessionStorage.removeItem('demo-badge');
    return sessionStorage.getItem('demo-badge') === '1';
  } catch {
    return false;
  }
})();
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
  // Tower now reads app-config for the DORA source (tower.dora.metrics); the demo has none, so the defaults apply.
  [configApiRef.id, {
    getOptionalConfig: () => undefined, getOptionalString: () => undefined, getOptionalNumber: () => undefined,
    getOptionalBoolean: () => undefined, getOptional: () => undefined, has: () => false, keys: () => [],
    getString: (k: string) => { throw new Error(`no config ${k}`); }, getConfig: (k: string) => { throw new Error(`no config ${k}`); },
  }],
  [identityApiRef.id, {
    getCredentials: async () => ({ token: `demo-token-${demoUser}` }),
    getBackstageIdentity: async () => ({ type: 'user', userEntityRef: `user:default/${demoUser}`, ownershipEntityRefs: [`user:default/${demoUser}`, 'group:default/team-skyport'] }),
    getProfileInfo: async () => ({ displayName: demoUser }),
    signOut: async () => {},
  }],
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
        {showBadge && (
          <div id="__whoami" style={{ position: 'fixed', top: 10, right: 16, zIndex: 2000, font: '500 11.5px "IBM Plex Mono", monospace', color: '#C9CED6', background: 'rgba(20,24,30,.9)', border: '1px solid #2A3038', borderRadius: 12, padding: '3px 10px', pointerEvents: 'none' }}>
            signed in as <b style={{ color: '#E8A33D' }}>{demoUser}</b>
          </div>
        )}
      </BrowserRouter>
    </UnifiedThemeProvider>
  </ApiProvider>,
);
