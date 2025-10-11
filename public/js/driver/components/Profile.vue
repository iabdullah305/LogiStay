<template>
	<div class="profile">
		<!-- Page Header -->
		<div class="mb-6">
			<h2 class="text-2xl font-bold text-gray-900">{{ $__('Driver Profile') }}</h2>
		</div>

		<!-- Loading State -->
		<div v-if="loading" class="flex justify-center items-center py-12">
			<LoadingIndicator />
		</div>

		<!-- Profile Content -->
		<div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Main Profile Card -->
			<Card class="lg:col-span-2">
				<!-- Profile Header -->
				<div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-lg">
					<div class="flex items-center">
						<div class="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4">
							<i class="fa fa-user text-2xl"></i>
						</div>
						<div>
							<h3 class="text-xl font-bold">{{ driverInfo.full_name || driverInfo.name }}</h3>
							<p class="opacity-90">{{ $__('Driver ID') }}: {{ driverInfo.name }}</p>
							<Badge :label="$__(driverInfo.status || 'active')" theme="green" />
						</div>
					</div>
				</div>

				<!-- Profile Details -->
				<div class="p-6 space-y-6">
					<!-- Personal Information -->
					<div>
						<h4 class="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">{{ $__('Personal Information') }}</h4>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('Full Name') }}</label>
								<p class="text-gray-900">{{ driverInfo.full_name || '-' }}</p>
							</div>
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('Employee ID') }}</label>
								<p class="text-gray-900">{{ driverInfo.employee || '-' }}</p>
							</div>
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('Phone') }}</label>
								<p class="text-gray-900">{{ driverInfo.phone || '-' }}</p>
							</div>
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('Email') }}</label>
								<p class="text-gray-900">{{ driverInfo.email || '-' }}</p>
							</div>
						</div>
					</div>

					<!-- License Information -->
					<div>
						<h4 class="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">{{ $__('License Information') }}</h4>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('License Number') }}</label>
								<p class="text-gray-900">{{ driverInfo.license_number || '-' }}</p>
							</div>
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('License Type') }}</label>
								<p class="text-gray-900">{{ driverInfo.license_type || '-' }}</p>
							</div>
							<div>
								<label class="text-sm font-medium text-gray-600">{{ $__('Expiry Date') }}</label>
								<p :class="{'text-red-600': isLicenseExpiring(driverInfo.license_expiry_date)}">
									{{ formatDate(driverInfo.license_expiry_date) || '-' }}
									<i v-if="isLicenseExpiring(driverInfo.license_expiry_date)" class="fa fa-exclamation-triangle text-yellow-500 ml-2"></i>
								</p>
							</div>
						</div>
					</div>
				</div>
			</Card>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Assigned Vehicles -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $__('Assigned Vehicles') }}</h3>
					<div v-if="assignedVehicles.length === 0" class="text-center py-8 text-gray-500">
						<i class="fa fa-car text-2xl mb-2 block"></i>
						<p>{{ $__('No vehicles assigned') }}</p>
					</div>
					<div v-else class="space-y-3">
						<div v-for="vehicle in assignedVehicles" :key="vehicle.name" 
							 class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
							<div>
								<p class="font-medium text-gray-900">{{ vehicle.license_plate }}</p>
								<p class="text-sm text-gray-600">{{ vehicle.make }} {{ vehicle.model }}</p>
							</div>
							<Badge :label="$__(vehicle.status)" theme="blue" />
						</div>
					</div>
				</Card>

				<!-- Performance Stats -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $__('Performance Statistics') }}</h3>
					<div class="grid grid-cols-2 gap-4">
						<div class="text-center p-3 bg-gray-50 rounded-lg">
							<p class="text-2xl font-bold text-gray-900">{{ performanceStats.totalTrips }}</p>
							<p class="text-sm text-gray-600">{{ $__('Total Trips') }}</p>
						</div>
						<div class="text-center p-3 bg-gray-50 rounded-lg">
							<p class="text-2xl font-bold text-gray-900">{{ performanceStats.safetyScore }}%</p>
							<p class="text-sm text-gray-600">{{ $__('Safety Score') }}</p>
						</div>
					</div>
				</Card>

				<!-- Quick Actions -->
				<Card class="p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $__('Quick Actions') }}</h3>
					<div class="space-y-3">
						<Button variant="solid" theme="blue" @click="updateProfile" class="w-full">
							<i class="fa fa-edit mr-2"></i>
							{{ $__('Update Profile') }}
						</Button>
						<Button variant="outline" theme="gray" @click="downloadReport" class="w-full">
							<i class="fa fa-download mr-2"></i>
							{{ $__('Download Report') }}
						</Button>
					</div>
				</Card>
			</div>
		</div>
	</div>
</template>

<script>
import { Card, Button, Badge, LoadingIndicator } from 'frappe-ui'

export default {
	name: 'Profile',
	components: {
		Card,
		Button,
		Badge,
		LoadingIndicator
	},
	data() {
		return {
			loading: true,
			driverInfo: {},
			assignedVehicles: [],
			performanceStats: {
				totalTrips: 0,
				safetyScore: 0
			}
		}
	},
	mounted() {
		this.loadDriverProfile()
	},
	methods: {
		async loadDriverProfile() {
			this.loading = true
			try {
				const response = await this.$frappe.call({
					method: 'logistay.api.get_current_driver_profile'
				})
				if (response.message) {
					this.driverInfo = response.message
				}
				
				// Load additional data
				await this.loadAssignedVehicles()
				await this.loadPerformanceStats()
				
			} catch (error) {
				console.error('Error loading driver profile:', error)
				// Test data
				this.driverInfo = {
					name: 'DRV-001',
					full_name: 'Ahmed Mohammed Al-Saeed',
					employee: 'EMP-001',
					phone: '+966501234567',
					email: 'ahmed.mohammed@company.com',
					license_number: 'LIC-123456789',
					license_type: 'General',
					license_expiry_date: '2025-01-15',
					status: 'Active'
				}
				this.assignedVehicles = [
					{
						name: 'VEH-001',
						license_plate: 'ABC-123',
						make: 'Toyota',
						model: 'Camry',
						status: 'Active'
					}
				]
				this.performanceStats = {
					totalTrips: 125,
					safetyScore: 95
				}
			} finally {
				this.loading = false
			}
		},

		async loadAssignedVehicles() {
			// Implementation for loading assigned vehicles
		},

		async loadPerformanceStats() {
			// Implementation for loading performance stats
		},

		formatDate(dateStr) {
			if (!dateStr) return null
			return new Date(dateStr).toLocaleDateString('en-US')
		},

		isLicenseExpiring(expiryDate) {
			if (!expiryDate) return false
			const expiry = new Date(expiryDate)
			const today = new Date()
			const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
			return daysUntilExpiry <= 90
		},

		updateProfile() {
			window.open(`/app/fleet-driver/${this.driverInfo.name}`, '_blank')
		},

		async downloadReport() {
			try {
				const response = await this.$frappe.call({
					method: 'logistay.api.generate_driver_report',
					args: { driver: this.driverInfo.name }
				})
				if (response.message && response.message.file_url) {
					window.open(response.message.file_url, '_blank')
				}
			} catch (error) {
				console.error('Error generating report:', error)
			}
		}
	}
}
</script>