<template>
	<div class="profile">
		<div class="page-header">
			<h2>{{ $__('Driver Profile') }}</h2>
		</div>

		<div class="profile-container">
			<!-- Basic Driver Information -->
			<div class="profile-card">
				<div class="profile-header">
					<div class="profile-avatar">
						<i class="fa fa-user"></i>
					</div>
					<div class="profile-info">
						<h3>{{ driverInfo.full_name || driverInfo.name }}</h3>
						<p class="driver-id">{{ $__('Driver ID') }}: {{ driverInfo.name }}</p>
						<span :class="'status-badge status-' + driverInfo.status">
							{{ $__(driverInfo.status || 'active') }}
						</span>
					</div>
				</div>

				<div class="profile-details">
					<div class="detail-section">
						<h4>{{ $__('Personal Information') }}</h4>
						<div class="detail-grid">
							<div class="detail-item">
								<label>{{ $__('Full Name') }}</label>
								<span>{{ driverInfo.full_name || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Employee ID') }}</label>
								<span>{{ driverInfo.employee || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Phone') }}</label>
								<span>{{ driverInfo.phone || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Email') }}</label>
								<span>{{ driverInfo.email || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Date of Birth') }}</label>
								<span>{{ formatDate(driverInfo.date_of_birth) || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Address') }}</label>
								<span>{{ driverInfo.address || '-' }}</span>
							</div>
						</div>
					</div>

					<div class="detail-section">
						<h4>{{ $__('License Information') }}</h4>
						<div class="detail-grid">
							<div class="detail-item">
								<label>{{ $__('License Number') }}</label>
								<span>{{ driverInfo.license_number || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('License Type') }}</label>
								<span>{{ driverInfo.license_type || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Issue Date') }}</label>
								<span>{{ formatDate(driverInfo.license_issue_date) || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Expiry Date') }}</label>
								<span :class="{'text-danger': isLicenseExpiring(driverInfo.license_expiry_date)}">
									{{ formatDate(driverInfo.license_expiry_date) || '-' }}
									<i v-if="isLicenseExpiring(driverInfo.license_expiry_date)" class="fa fa-exclamation-triangle text-warning"></i>
								</span>
							</div>
						</div>
					</div>

					<div class="detail-section">
						<h4>{{ $__('Employment Information') }}</h4>
						<div class="detail-grid">
							<div class="detail-item">
								<label>{{ $__('Join Date') }}</label>
								<span>{{ formatDate(driverInfo.joining_date) || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Department') }}</label>
								<span>{{ driverInfo.department || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Branch') }}</label>
								<span>{{ driverInfo.branch || '-' }}</span>
							</div>
							<div class="detail-item">
								<label>{{ $__('Supervisor') }}</label>
								<span>{{ driverInfo.supervisor || '-' }}</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Assigned Vehicles -->
			<div class="assigned-vehicles-card">
				<h3>{{ $__('Assigned Vehicles') }}</h3>
				<div v-if="assignedVehicles.length === 0" class="empty-state">
					<i class="fa fa-car"></i>
					<p>{{ $__('No vehicles assigned') }}</p>
				</div>
				<div v-else class="vehicles-list">
					<div v-for="vehicle in assignedVehicles" :key="vehicle.name" class="vehicle-item">
						<div class="vehicle-info">
							<h4>{{ vehicle.license_plate }}</h4>
							<p>{{ vehicle.make }} {{ vehicle.model }} ({{ vehicle.year }})</p>
						</div>
						<div class="vehicle-status">
							<span :class="'status-badge status-' + vehicle.status">
								{{ $__(vehicle.status) }}
							</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Performance Statistics -->
			<div class="performance-stats-card">
				<h3>{{ $__('Performance Statistics') }}</h3>
				<div class="stats-grid">
					<div class="stat-item">
						<div class="stat-value">{{ performanceStats.totalTrips }}</div>
						<div class="stat-label">{{ $__('Total Trips') }}</div>
					</div>
					<div class="stat-item">
						<div class="stat-value">{{ performanceStats.totalDistance }}km</div>
						<div class="stat-label">{{ $__('Total Distance') }}</div>
					</div>
					<div class="stat-item">
						<div class="stat-value">{{ performanceStats.fuelEfficiency }}L/100km</div>
						<div class="stat-label">{{ $__('Fuel Efficiency') }}</div>
					</div>
					<div class="stat-item">
						<div class="stat-value">{{ performanceStats.safetyScore }}%</div>
						<div class="stat-label">{{ $__('Safety Score') }}</div>
					</div>
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="quick-actions-card">
				<h3>{{ $__('Quick Actions') }}</h3>
				<div class="actions-grid">
					<button @click="updateProfile" class="action-btn primary">
						<i class="fa fa-edit"></i>
						{{ $__('Update Profile') }}
					</button>
					<button @click="changePassword" class="action-btn secondary">
						<i class="fa fa-lock"></i>
						{{ $__('Change Password') }}
					</button>
					<button @click="downloadReport" class="action-btn tertiary">
						<i class="fa fa-download"></i>
						{{ $__('Download Report') }}
					</button>
					<button @click="contactHR" class="action-btn tertiary">
						<i class="fa fa-phone"></i>
						{{ $__('Contact HR') }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Profile',
	data() {
		return {
			driverInfo: {},
			assignedVehicles: [],
			performanceStats: {
				totalTrips: 0,
				totalDistance: 0,
				fuelEfficiency: 0,
				safetyScore: 0
			}
		}
	},
	mounted() {
		this.loadDriverProfile()
		this.loadAssignedVehicles()
		this.loadPerformanceStats()
	},
	methods: {
		async loadDriverProfile() {
			try {
				const response = await frappe.call({
					method: 'logistay.api.driver.get_driver_profile'
				})
				if (response.message) {
					this.driverInfo = response.message
				}
			} catch (error) {
				console.error('Error loading driver profile:', error)
				// Test data
				this.driverInfo = {
					name: 'DRV-001',
					full_name: 'Ahmed Mohammed Al-Saeed',
					employee: 'EMP-001',
					phone: '+966501234567',
					email: 'ahmed.mohammed@company.com',
					date_of_birth: '1985-05-15',
					address: 'Riyadh, Saudi Arabia',
					license_number: 'LIC-123456789',
					license_type: 'General',
					license_issue_date: '2020-01-15',
					license_expiry_date: '2025-01-15',
					joining_date: '2022-03-01',
					department: 'Transportation',
					branch: 'Main Branch',
					supervisor: 'Mohammed Ahmed Al-Mudeer',
					status: 'active'
				}
			}
		},

		async loadAssignedVehicles() {
			try {
				const response = await frappe.call({
					method: 'logistay.api.driver.get_assigned_vehicles'
				})
				if (response.message) {
					this.assignedVehicles = response.message
				}
			} catch (error) {
				console.error('Error loading assigned vehicles:', error)
				// Test data
				this.assignedVehicles = [
					{
						name: 'VEH-001',
						license_plate: 'ABC-123',
						make: 'Toyota',
						model: 'Camry',
						year: 2023,
						status: 'active'
					}
				]
			}
		},

		async loadPerformanceStats() {
			try {
				const response = await frappe.call({
					method: 'logistay.api.driver.get_performance_stats'
				})
				if (response.message) {
					this.performanceStats = response.message
				}
			} catch (error) {
				console.error('Error loading performance stats:', error)
				// Test data
				this.performanceStats = {
					totalTrips: 125,
					totalDistance: 15750,
					fuelEfficiency: 8.5,
					safetyScore: 95
				}
			}
		},

		formatDate(dateStr) {
			if (!dateStr) return null
			return new Date(dateStr).toLocaleDateString('ar-SA')
		},

		isLicenseExpiring(expiryDate) {
			if (!expiryDate) return false
			const expiry = new Date(expiryDate)
			const today = new Date()
			const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
			return daysUntilExpiry <= 90 // Warning if license expires within 90 days
		},

		updateProfile() {
			// Open profile update page
			window.open(`/app/fleet-driver/${this.driverInfo.name}`, '_blank')
		},

		changePassword() {
			// Open password change page
			frappe.show_alert({
				message: this.$__('Please contact your administrator to change password'),
				indicator: 'blue'
			})
		},

		async downloadReport() {
			try {
				const response = await frappe.call({
					method: 'logistay.api.driver.generate_driver_report',
					args: { driver: this.driverInfo.name }
				})
				if (response.message && response.message.file_url) {
					window.open(response.message.file_url, '_blank')
				}
			} catch (error) {
				console.error('Error generating report:', error)
				frappe.show_alert({
					message: this.$__('Error generating report'),
					indicator: 'red'
				})
			}
		},

		contactHR() {
			// Open support page or contact HR
			this.$router.push('/support')
		}
	}
}
</script>

<style scoped>
.profile {
	max-width: 1200px;
	margin: 0 auto;
}

.page-header {
	margin-bottom: 2rem;
}

.page-header h2 {
	color: #2c3e50;
	margin: 0;
}

.profile-container {
	display: grid;
	grid-template-columns: 2fr 1fr;
	gap: 2rem;
}

.profile-card {
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	overflow: hidden;
}

.profile-header {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	padding: 2rem;
	display: flex;
	align-items: center;
}

.profile-avatar {
	width: 80px;
	height: 80px;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 1.5rem;
}

.profile-avatar i {
	font-size: 2rem;
}

.profile-info h3 {
	margin: 0 0 0.5rem 0;
	font-size: 1.5rem;
}

.driver-id {
	margin: 0 0 1rem 0;
	opacity: 0.9;
}

.status-badge {
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.8rem;
	font-weight: 600;
}

.status-active {
	background: rgba(255, 255, 255, 0.2);
	color: white;
}

.profile-details {
	padding: 2rem;
}

.detail-section {
	margin-bottom: 2rem;
}

.detail-section:last-child {
	margin-bottom: 0;
}

.detail-section h4 {
	color: #2c3e50;
	margin-bottom: 1rem;
	padding-bottom: 0.5rem;
	border-bottom: 2px solid #f8f9fa;
}

.detail-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
	gap: 1rem;
}

.detail-item {
	display: flex;
	flex-direction: column;
}

.detail-item label {
	font-weight: 600;
	color: #6c757d;
	font-size: 0.85rem;
	margin-bottom: 0.25rem;
}

.detail-item span {
	color: #2c3e50;
	font-size: 0.95rem;
}

.text-danger {
	color: #dc3545 !important;
}

.text-warning {
	color: #ffc107;
	margin-left: 0.5rem;
}

.assigned-vehicles-card,
.performance-stats-card,
.quick-actions-card {
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	padding: 2rem;
	margin-bottom: 2rem;
}

.assigned-vehicles-card h3,
.performance-stats-card h3,
.quick-actions-card h3 {
	color: #2c3e50;
	margin-bottom: 1.5rem;
}

.empty-state {
	text-align: center;
	padding: 2rem;
	color: #6c757d;
}

.empty-state i {
	font-size: 2rem;
	margin-bottom: 1rem;
	display: block;
}

.vehicles-list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.vehicle-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 1rem;
	background: #f8f9fa;
	border-radius: 8px;
	border-left: 4px solid #667eea;
}

.vehicle-info h4 {
	margin: 0 0 0.25rem 0;
	color: #2c3e50;
}

.vehicle-info p {
	margin: 0;
	color: #6c757d;
	font-size: 0.85rem;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 1rem;
}

.stat-item {
	text-align: center;
	padding: 1rem;
	background: #f8f9fa;
	border-radius: 8px;
}

.stat-value {
	font-size: 1.5rem;
	font-weight: 700;
	color: #2c3e50;
	margin-bottom: 0.5rem;
}

.stat-label {
	color: #6c757d;
	font-size: 0.85rem;
}

.actions-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 1rem;
}

.action-btn {
	padding: 1rem;
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

@media (max-width: 768px) {
	.profile-container {
		grid-template-columns: 1fr;
	}
	
	.profile-header {
		flex-direction: column;
		text-align: center;
	}
	
	.profile-avatar {
		margin-right: 0;
		margin-bottom: 1rem;
	}
	
	.detail-grid {
		grid-template-columns: 1fr;
	}
	
	.stats-grid,
	.actions-grid {
		grid-template-columns: 1fr;
	}
}
</style>