import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { FrappeUI } from 'frappe-ui'
import App from './App.vue'
import routes from './router/routes.js'

// Create router instance
const router = createRouter({
  history: createWebHistory('/app/'),
  routes
})

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(router)
app.use(FrappeUI)

// Mount app
app.mount('#app')