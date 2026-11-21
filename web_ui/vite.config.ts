import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Proxy health and stats endpoints to FastAPI backend
      '/health': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/bot-status': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/stats': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/users': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/activity': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/history': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/daily-stats': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/platforms': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/admin': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
        },
      },
    },
  },
});