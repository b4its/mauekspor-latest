import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

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
		// Proxy API ke backend agar frontend selalu same-origin (/api/v1).
		// Aman diakses dari device/jaringan lain tanpa hardcode localhost.
		proxy: {
			'/api': {
				target: process.env.BACKEND_ORIGIN ?? 'http://localhost:8015',
				changeOrigin: true
			}
		},
		// Hot reload: izinkan HMR dari luar container
		watch: {
			usePolling: true,
			interval: 300
		}
	}
});
