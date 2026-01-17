import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/tasks': 'http://localhost:8000',
            '/config': 'http://localhost:8000',
            '/download': 'http://localhost:8000',
        }
    }
})
