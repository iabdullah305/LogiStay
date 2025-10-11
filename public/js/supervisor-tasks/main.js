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

app.mount('#supervisor-tasks-app')