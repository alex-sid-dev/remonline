import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// Позволяет переопределить целевой backend через переменную окружения,
// что удобно внутри Docker (`http://app:8000`) и локально (`http://localhost:8000`).
const apiTarget = process.env.VITE_API_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});
