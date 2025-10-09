import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
	plugins: [vue()],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './logistay/public/js'),
		},
	},
	build: {
		outDir: 'logistay/public/dist',
		rollupOptions: {
			input: {
				driver: 'logistay/public/js/driver/main.js',
			},
			output: {
				entryFileNames: '[name].js',
				chunkFileNames: '[name].js',
				assetFileNames: '[name].[ext]'
			}
		}
	},
	server: {
		port: 3000,
		proxy: {
			'/api': 'http://localhost:8000',
			'/assets': 'http://localhost:8000',
		}
	}
})