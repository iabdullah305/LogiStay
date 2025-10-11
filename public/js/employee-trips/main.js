import { createApp } from 'vue'
import { FrappeUI } from 'frappe-ui'
import App from './App.vue'

// Create application
const app = createApp(App)

// Use frappe-ui
app.use(FrappeUI)

// Add global variables
app.config.globalProperties.$frappe = window.frappe
app.config.globalProperties.$__ = window.__

// Console testing
console.log('Employee Trips Vue app initializing...')
console.log('FrappeUI loaded:', !!FrappeUI)

app.mount('#employee-trips-app')