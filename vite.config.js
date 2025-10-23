import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
	plugins: [
		vue(),
		Icons({
			compiler: 'vue3',
			autoInstall: true,
		}),
	],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './public/js'),
			'~icons': path.resolve(__dirname, 'node_modules/unplugin-icons'),
		},
	},
	build: {
		outDir: 'public/dist',
		rollupOptions: {
			input: {
				driver: 'public/js/driver/main.js',
				fleet: 'public/js/fleet/main.js',
				'booking-lookup': 'public/js/booking-lookup/main.js',
				availability: 'public/js/availability/main.js',
				'supervisor-tasks': 'public/js/supervisor-tasks/main.js',
				'employee-trips': 'public/js/employee-trips/main.js',
			},
			output: {
				entryFileNames: '[name].js',
				chunkFileNames: '[name].js',
				assetFileNames: '[name].[ext]'
			},
			external: []
		}
	},
	optimizeDeps: {
		include: ['frappe-ui']
	},
	server: {
		port: 3000,
		proxy: {
			'/api': 'http://localhost:8000',
			'/assets': 'http://localhost:8000',
		}
	}
})
