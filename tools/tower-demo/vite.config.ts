import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: /^@material-ui\/icons\/(?!esm)(\w+)$/, replacement: '@material-ui/icons/esm/$1' },
      { find: /^@backstage\/plugin-kubernetes-react$/, replacement: path.resolve(__dirname, 'mock/k8sReact.ts') },
      { find: /^@backstage\/plugin-kubernetes$/, replacement: path.resolve(__dirname, 'mock/k8s.ts') },
    ],
  },
  define: { 'process.env': {} },
  optimizeDeps: { include: ['@material-ui/core', '@material-ui/icons'] },
});
