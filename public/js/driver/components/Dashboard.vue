<template>
	<div class="dashboard">
		<div class="page-header">
			<h2>{{ $__('Driver Dashboard') }}</h2>
			<p class="text-muted">{{ $__('Welcome to Fleet Management System - Driver Application') }}</p>
		</div>

		<!-- Quick Statistics -->
		<div class="stats-grid">
			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-road"></i>
				</div>
				<div class="stat-content">
					<h3>{{ stats.totalTrips }}</h3>
					<p>{{ $__('Total Trips') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-clock"></i>
				</div>
				<div class="stat-content">
					<h3>{{ stats.activeTrips }}</h3>
					<p>{{ $__('Active Trips') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-gas-pump"></i>
				</div>
				<div class="stat-content">
					<h3>{{ stats.fuelEntries }}</h3>
					<p>{{ $__('Fuel Entries') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-calendar"></i>
				</div>
				<div class="stat-content">
					<h3>{{ stats.thisMonth }}</h3>
					<p>{{ $__('This Month') }}</p>
				</div>
			</div>
		</div>

		<!-- Recent Trips -->
		<div class="recent-section">
			<h3>{{ $__('Recent Trips') }}</h3>
			<div class="trips-list">
				<div v-for="trip in recentTrips" :key="trip.name" class="trip-item">
					<div class="trip-info">
						<h4>{{ trip.route }}</h4>
						<p class="trip-date">{{ formatDate(trip.date) }}</p>
					</div>
					<div class="trip-status">
						<span :class="'status-badge status-' + trip.status">
							{{ $__(trip.status) }}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="quick-actions">
			<h3>{{ $__('Quick Actions') }}</h3>
			<div class="actions-grid">
				<button @click="startTrip" class="action-btn primary">
					<i class="fa fa-play"></i>
					{{ $__('Start New Trip') }}
				</button>
				<button @click="addFuelEntry" class="action-btn secondary">
					<i class="fa fa-gas-pump"></i>
					{{ $__('Add Fuel Entry') }}
				</button>
				<button @click="viewProfile" class="action-btn tertiary">
					<i class="fa fa-user"></i>
					{{ $__('View Profile') }}
				</button>
				<button @click="contactSupport" class="action-btn tertiary">
					<i class="fa fa-support"></i>
					{{ $__('Contact Support') }}
				</button>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Dashboard',
	data() {
		return {
			stats: {
				totalTrips: 0,
				activeTrips: 0,
				fuelEntries: 0,
				thisMonth: 0
			},
			recentTrips: []
		}
	},
	mounted() {
		this.loadDashboardData()
	},
	methods: {
		async loadDashboardData() {
			try {
				// Load statistics
				const statsResponse = await frappe.call({
					method: 'logistay.api.driver.get_dashboard_stats'
				})
				if (statsResponse.message) {
					this.stats = statsResponse.message
				}

				// Load recent trips
				const tripsResponse = await frappe.call({
					method: 'logistay.api.driver.get_recent_trips'
				})
				if (tripsResponse.message) {
					this.recentTrips = tripsResponse.message
				}
			} catch (error) {
				console.error('Error loading dashboard data:', error)
				// Test data in case of error
				this.stats = {
					totalTrips: 25,
					activeTrips: 2,
					fuelEntries: 18,
					thisMonth: 8
				}
				this.recentTrips = [
					{
						name: 'TRIP-001',
						route: 'Riyadh - Jeddah',
						date: '2024-01-15',
						status: 'completed'
					},
					{
						name: 'TRIP-002',
						route: 'Jeddah - Dammam',
						date: '2024-01-14',
						status: 'in_progress'
					}
				]
			}
		},
		formatDate(dateStr) {
			return new Date(dateStr).toLocaleDateString('ar-SA')
		},
		startTrip() {
			this.$router.push('/trips')
		},
		addFuelEntry() {
			this.$router.push('/fuel')
		},
		viewProfile() {
			this.$router.push('/profile')
		},
		contactSupport() {
			this.$router.push('/support')
		}
	}
}
</script>

<style scoped>
.dashboard {
	max-width: 1200px;
	margin: 0 auto;
}

.page-header {
	margin-bottom: 2rem;
}

.page-header h2 {
	color: #2c3e50;
	margin-bottom: 0.5rem;
}

.text-muted {
	color: #6c757d;
	margin: 0;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
	gap: 1.5rem;
	margin-bottom: 3rem;
}

.stat-card {
	background: white;
	padding: 2rem;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	display: flex;
	align-items: center;
	transition: transform 0.3s ease;
}

.stat-card:hover {
	transform: translateY(-2px);
}

.stat-icon {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	width: 60px;
	height: 60px;
	border-radius: 12px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 1.5rem;
}

.stat-icon i {
	font-size: 1.5rem;
}

.stat-content h3 {
	font-size: 2rem;
	font-weight: 700;
	color: #2c3e50;
	margin: 0 0 0.5rem 0;
}

.stat-content p {
	color: #6c757d;
	margin: 0;
	font-size: 0.9rem;
}

.recent-section {
	background: white;
	padding: 2rem;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	margin-bottom: 2rem;
}

.recent-section h3 {
	color: #2c3e50;
	margin-bottom: 1.5rem;
}

.trips-list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.trip-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 1rem;
	background: #f8f9fa;
	border-radius: 8px;
	border-left: 4px solid #667eea;
}

.trip-info h4 {
	margin: 0 0 0.25rem 0;
	color: #2c3e50;
}

.trip-date {
	margin: 0;
	color: #6c757d;
	font-size: 0.85rem;
}

.status-badge {
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.8rem;
	font-weight: 600;
}

.status-completed {
	background: #d4edda;
	color: #155724;
}

.status-in_progress {
	background: #fff3cd;
	color: #856404;
}

.quick-actions {
	background: white;
	padding: 2rem;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.quick-actions h3 {
	color: #2c3e50;
	margin-bottom: 1.5rem;
}

.actions-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 1rem;
}

.action-btn {
	padding: 1rem 1.5rem;
	border: none;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
}

.action-btn.primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
}

.action-btn.secondary {
	background: #28a745;
	color: white;
}

.action-btn.tertiary {
	background: #6c757d;
	color: white;
}

.action-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>