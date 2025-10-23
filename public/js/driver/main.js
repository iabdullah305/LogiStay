import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { resourcesPlugin } from 'frappe-ui'
import App from './App.vue'
import Dashboard from './components/Dashboard.vue'
import Trips from './components/Trips.vue'
import Fuel from './components/Fuel.vue'
import Profile from './components/Profile.vue'
import Support from './components/Support.vue'

// Router setup
const routes = [
	{ path: '/', redirect: '/dashboard' },
	{ path: '/dashboard', component: Dashboard },
	{ path: '/trips', component: Trips },
	{ path: '/fuel', component: Fuel },
	{ path: '/profile', component: Profile },
	{ path: '/support', component: Support }
]

const router = createRouter({
	history: createWebHistory('/driver/'),
	routes
})

// Create application
const app = createApp(App)

// Use plugins
app.use(router)
app.use(resourcesPlugin)

// Add global variables
app.config.globalProperties.$frappe = window.frappe
app.config.globalProperties.$__ = window.__

app.mount('#driver-app')