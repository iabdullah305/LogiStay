<template>
	<div id="app" class="driver-app">
		<!-- Top Navigation Bar -->
		<nav class="navbar">
			<div class="navbar-brand">
				<h1>{{ $__('Driver Dashboard') }}</h1>
			</div>
			<div class="navbar-user">
				<span>{{ $__('Welcome') }}, {{ user }}</span>
			</div>
		</nav>

		<!-- Side Navigation Bar -->
		<div class="app-container">
			<aside class="sidebar">
				<ul class="nav-menu">
					<li>
						<router-link to="/dashboard" class="nav-link">
							<i class="fa fa-dashboard"></i>
							{{ $__('Dashboard') }}
						</router-link>
					</li>
					<li>
						<router-link to="/trips" class="nav-link">
							<i class="fa fa-road"></i>
							{{ $__('My Trips') }}
						</router-link>
					</li>
					<li>
						<router-link to="/fuel" class="nav-link">
							<i class="fa fa-gas-pump"></i>
							{{ $__('Fuel Management') }}
						</router-link>
					</li>
					<li>
						<router-link to="/profile" class="nav-link">
							<i class="fa fa-user"></i>
							{{ $__('Profile') }}
						</router-link>
					</li>
					<li>
						<router-link to="/support" class="nav-link">
							<i class="fa fa-support"></i>
							{{ $__('Support') }}
						</router-link>
					</li>
				</ul>
			</aside>

			<!-- Main Content -->
			<main class="main-content">
				<router-view></router-view>
			</main>
		</div>
	</div>
</template>

<script>
export default {
	name: 'DriverApp',
	data() {
		return {
			user: frappe.session.user || 'Driver'
		}
	}
}
</script>

<style scoped>
.driver-app {
	min-height: 100vh;
	background-color: #f8f9fa;
}

.navbar {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	padding: 1rem 2rem;
	display: flex;
	justify-content: space-between;
	align-items: center;
	box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.navbar-brand h1 {
	margin: 0;
	font-size: 1.5rem;
	font-weight: 600;
}

.navbar-user {
	font-size: 0.9rem;
}

.app-container {
	display: flex;
	min-height: calc(100vh - 80px);
}

.sidebar {
	width: 250px;
	background: white;
	box-shadow: 2px 0 4px rgba(0,0,0,0.1);
	padding: 2rem 0;
}

.nav-menu {
	list-style: none;
	padding: 0;
	margin: 0;
}

.nav-menu li {
	margin-bottom: 0.5rem;
}

.nav-link {
	display: flex;
	align-items: center;
	padding: 1rem 2rem;
	color: #6c757d;
	text-decoration: none;
	transition: all 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
}

.nav-link i {
	margin-right: 0.75rem;
	width: 20px;
}

.main-content {
	flex: 1;
	padding: 2rem;
}
</style>