import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

// PORT LAYOUT (anti-tabrakan):
//   Dev mode   : frontend=5188, backend via BACKEND_ORIGIN env
//   Prod Docker: frontend=3015, backend=8015 (via nginx proxy)
//
// BACKEND_ORIGIN env var:
//   Tidak diset  -> pakai port 8015 (Docker production backend — yang biasanya jalan)
//   Local dev bd -> BACKEND_ORIGIN=http://localhost:8016 make dev-frontend

const DEFAULT_BACKEND = 'http://localhost:8015';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		})
	],
	server: {
		host: '0.0.0.0',
		port: 5188,
		strictPort: true,
		// Proxy /api/* ke backend.
		// Dev default -> localhost:8016 (port dev, tidak tabrakan dengan prod Docker di 8015)
		// Override: BACKEND_ORIGIN=http://localhost:8015 untuk arahkan ke prod Docker
		proxy: {
			'/api': {
				target: process.env.BACKEND_ORIGIN ?? DEFAULT_BACKEND,
				changeOrigin: true
			}
		},
		// Hot reload: izinkan HMR dari luar container / ngrok
		watch: {
			usePolling: true,
			interval: 300
		}
	}
});
