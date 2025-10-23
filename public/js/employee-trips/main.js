import { createApp } from 'vue'
import { resourcesPlugin } from 'frappe-ui'
import App from './App.vue'

// Create application
const app = createApp(App)

// Use frappe-ui resources plugin
app.use(resourcesPlugin)

// Add global variables
app.config.globalProperties.$frappe = window.frappe
app.config.globalProperties.$__ = window.__

app.mount('#employee-trips-app')