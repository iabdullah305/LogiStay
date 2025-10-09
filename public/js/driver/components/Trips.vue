<template>
	<div class="trips">
		<div class="page-header">
			<h2>{{ $__('My Trips') }}</h2>
			<button @click="showNewTripModal = true" class="btn-primary">
				<i class="fa fa-plus"></i>
				{{ $__('New Trip') }}
			</button>
		</div>

		<!-- Search Filters -->
		<div class="filters-section">
			<div class="filters-grid">
				<div class="filter-group">
					<label>{{ $__('Status') }}</label>
					<select v-model="filters.status" @change="loadTrips">
						<option value="">{{ $__('All Status') }}</option>
						<option value="draft">{{ $__('Draft') }}</option>
						<option value="in_progress">{{ $__('In Progress') }}</option>
						<option value="completed">{{ $__('Completed') }}</option>
						<option value="cancelled">{{ $__('Cancelled') }}</option>
					</select>
				</div>
				<div class="filter-group">
					<label>{{ $__('Date From') }}</label>
					<input type="date" v-model="filters.dateFrom" @change="loadTrips">
				</div>
				<div class="filter-group">
					<label>{{ $__('Date To') }}</label>
					<input type="date" v-model="filters.dateTo" @change="loadTrips">
				</div>
			</div>
		</div>

		<!-- Trips List -->
		<div class="trips-container">
			<div v-if="loading" class="loading">
				<i class="fa fa-spinner fa-spin"></i>
				{{ $__('Loading trips...') }}
			</div>

			<div v-else-if="trips.length === 0" class="empty-state">
				<i class="fa fa-road"></i>
				<h3>{{ $__('No trips found') }}</h3>
				<p>{{ $__('Start your first trip by clicking the New Trip button') }}</p>
			</div>

			<div v-else class="trips-grid">
				<div v-for="trip in trips" :key="trip.name" class="trip-card">
					<div class="trip-header">
						<h3>{{ trip.route || trip.name }}</h3>
						<span :class="'status-badge status-' + trip.status">
							{{ $__(trip.status) }}
						</span>
					</div>

					<div class="trip-details">
						<div class="detail-row">
							<i class="fa fa-map-marker"></i>
							<span>{{ $__('From') }}: {{ trip.source_location }}</span>
						</div>
						<div class="detail-row">
							<i class="fa fa-map-marker"></i>
							<span>{{ $__('To') }}: {{ trip.destination_location }}</span>
						</div>
						<div class="detail-row">
							<i class="fa fa-calendar"></i>
							<span>{{ formatDate(trip.trip_date) }}</span>
						</div>
						<div class="detail-row">
							<i class="fa fa-truck"></i>
							<span>{{ trip.vehicle }}</span>
						</div>
						<div v-if="trip.distance" class="detail-row">
							<i class="fa fa-road"></i>
							<span>{{ trip.distance }} {{ $__('km') }}</span>
						</div>
					</div>

					<div class="trip-actions">
						<button v-if="trip.status === 'draft'" @click="startTrip(trip)" class="btn-success">
							<i class="fa fa-play"></i>
							{{ $__('Start') }}
						</button>
						<button v-if="trip.status === 'in_progress'" @click="completeTrip(trip)" class="btn-primary">
							<i class="fa fa-check"></i>
							{{ $__('Complete') }}
						</button>
						<button @click="viewTrip(trip)" class="btn-secondary">
							<i class="fa fa-eye"></i>
							{{ $__('View') }}
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- New Trip Modal -->
		<div v-if="showNewTripModal" class="modal-overlay" @click="closeModal">
			<div class="modal" @click.stop>
				<div class="modal-header">
					<h3>{{ $__('New Trip') }}</h3>
					<button @click="closeModal" class="close-btn">
						<i class="fa fa-times"></i>
					</button>
				</div>

				<div class="modal-body">
					<form @submit.prevent="createTrip">
						<div class="form-group">
							<label>{{ $__('Source Location') }}</label>
							<input type="text" v-model="newTrip.source_location" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Destination Location') }}</label>
							<input type="text" v-model="newTrip.destination_location" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Trip Date') }}</label>
							<input type="date" v-model="newTrip.trip_date" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Vehicle') }}</label>
							<select v-model="newTrip.vehicle" required>
								<option value="">{{ $__('Select Vehicle') }}</option>
								<option v-for="vehicle in vehicles" :key="vehicle.name" :value="vehicle.name">
									{{ vehicle.license_plate }} - {{ vehicle.model }}
								</option>
							</select>
						</div>

						<div class="form-group">
							<label>{{ $__('Purpose') }}</label>
							<textarea v-model="newTrip.purpose" rows="3"></textarea>
						</div>

						<div class="form-actions">
							<button type="button" @click="closeModal" class="btn-secondary">
								{{ $__('Cancel') }}
							</button>
							<button type="submit" class="btn-primary" :disabled="creating">
								<i v-if="creating" class="fa fa-spinner fa-spin"></i>
								{{ creating ? $__('Creating...') : $__('Create Trip') }}
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Trips',
	data() {
		return {
			trips: [],
			vehicles: [],
			loading: false,
			creating: false,
			showNewTripModal: false,
			filters: {
				status: '',
				dateFrom: '',
				dateTo: ''
			},
			newTrip: {
				source_location: '',
				destination_location: '',
				trip_date: '',
				vehicle: '',
				purpose: ''
			}
		}
	},
	mounted() {
		this.loadTrips()
		this.loadVehicles()
	},
	methods: {
		async loadTrips() {
			this.loading = true
			try {
				const response = await frappe.call({
					method: 'fleet_management.api.driver.get_trips',
					args: this.filters
				})
				if (response.message) {
					this.trips = response.message
				}
			} catch (error) {
				console.error('Error loading trips:', error)
				// Test data
				this.trips = [
					{
						name: 'TRIP-001',
						route: 'Riyadh - Jeddah',
						source_location: 'Riyadh',
						destination_location: 'Jeddah',
						trip_date: '2024-01-15',
						vehicle: 'VEH-001',
						status: 'completed',
						distance: 950
					},
					{
						name: 'TRIP-002',
						route: 'Jeddah - Dammam',
						source_location: 'Jeddah',
						destination_location: 'Dammam',
						trip_date: '2024-01-16',
						vehicle: 'VEH-001',
						status: 'in_progress',
						distance: 1380
					}
				]
			} finally {
				this.loading = false
			}
		},

		async loadVehicles() {
			try {
				const response = await frappe.call({
					method: 'fleet_management.api.driver.get_assigned_vehicles'
				})
				if (response.message) {
					this.vehicles = response.message
				}
			} catch (error) {
				console.error('Error loading vehicles:', error)
				// Test data
				this.vehicles = [
					{
						name: 'VEH-001',
						license_plate: 'ABC-123',
						model: 'Toyota Camry 2023'
					}
				]
			}
		},

		async createTrip() {
			this.creating = true
			try {
				const response = await frappe.call({
					method: 'fleet_management.api.driver.create_trip',
					args: this.newTrip
				})
				if (response.message) {
					this.trips.unshift(response.message)
					this.closeModal()
					frappe.show_alert({
						message: this.$__('Trip created successfully'),
						indicator: 'green'
					})
				}
			} catch (error) {
				console.error('Error creating trip:', error)
				frappe.show_alert({
					message: this.$__('Error creating trip'),
					indicator: 'red'
				})
			} finally {
				this.creating = false
			}
		},

		async startTrip(trip) {
			try {
				await frappe.call({
					method: 'fleet_management.api.driver.start_trip',
					args: { trip_name: trip.name }
				})
				trip.status = 'in_progress'
				frappe.show_alert({
					message: this.$__('Trip started successfully'),
					indicator: 'green'
				})
			} catch (error) {
				console.error('Error starting trip:', error)
				frappe.show_alert({
					message: this.$__('Error starting trip'),
					indicator: 'red'
				})
			}
		},

		async completeTrip(trip) {
			try {
				await frappe.call({
					method: 'fleet_management.api.driver.complete_trip',
					args: { trip_name: trip.name }
				})
				trip.status = 'completed'
				frappe.show_alert({
					message: this.$__('Trip completed successfully'),
					indicator: 'green'
				})
			} catch (error) {
				console.error('Error completing trip:', error)
				frappe.show_alert({
					message: this.$__('Error completing trip'),
					indicator: 'red'
				})
			}
		},

		viewTrip(trip) {
			// Open trip details page
			window.open(`/app/fleet-trip/${trip.name}`, '_blank')
		},

		closeModal() {
			this.showNewTripModal = false
			this.newTrip = {
				source_location: '',
				destination_location: '',
				trip_date: '',
				vehicle: '',
				purpose: ''
			}
		},

		formatDate(dateStr) {
			return new Date(dateStr).toLocaleDateString('ar-SA')
		}
	}
}
</script>

<style scoped>
.trips {
	max-width: 1200px;
	margin: 0 auto;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 2rem;
}

.page-header h2 {
	color: #2c3e50;
	margin: 0;
}

.btn-primary, .btn-success, .btn-secondary {
	padding: 0.75rem 1.5rem;
	border: none;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
}

.btn-primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
}

.btn-success {
	background: #28a745;
	color: white;
}

.btn-secondary {
	background: #6c757d;
	color: white;
}

.btn-primary:hover, .btn-success:hover, .btn-secondary:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.filters-section {
	background: white;
	padding: 1.5rem;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	margin-bottom: 2rem;
}

.filters-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 1rem;
}

.filter-group label {
	display: block;
	margin-bottom: 0.5rem;
	font-weight: 600;
	color: #2c3e50;
}

.filter-group select,
.filter-group input {
	width: 100%;
	padding: 0.75rem;
	border: 1px solid #ddd;
	border-radius: 6px;
	font-size: 0.9rem;
}

.trips-container {
	min-height: 400px;
}

.loading, .empty-state {
	text-align: center;
	padding: 3rem;
	color: #6c757d;
}

.loading i, .empty-state i {
	font-size: 3rem;
	margin-bottom: 1rem;
	display: block;
}

.trips-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
	gap: 1.5rem;
}

.trip-card {
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	overflow: hidden;
	transition: transform 0.3s ease;
}

.trip-card:hover {
	transform: translateY(-2px);
}

.trip-header {
	padding: 1.5rem;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.trip-header h3 {
	margin: 0;
	font-size: 1.1rem;
}

.status-badge {
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.8rem;
	font-weight: 600;
}

.status-draft {
	background: #f8f9fa;
	color: #6c757d;
}

.status-in_progress {
	background: #fff3cd;
	color: #856404;
}

.status-completed {
	background: #d4edda;
	color: #155724;
}

.status-cancelled {
	background: #f8d7da;
	color: #721c24;
}

.trip-details {
	padding: 1.5rem;
}

.detail-row {
	display: flex;
	align-items: center;
	margin-bottom: 0.75rem;
	color: #6c757d;
}

.detail-row i {
	width: 20px;
	margin-right: 0.75rem;
	color: #667eea;
}

.trip-actions {
	padding: 1rem 1.5rem;
	background: #f8f9fa;
	display: flex;
	gap: 0.5rem;
	justify-content: flex-end;
}

.trip-actions button {
	padding: 0.5rem 1rem;
	font-size: 0.85rem;
}

/* Modal Styles */
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal {
	background: white;
	border-radius: 12px;
	width: 90%;
	max-width: 500px;
	max-height: 90vh;
	overflow-y: auto;
}

.modal-header {
	padding: 1.5rem;
	border-bottom: 1px solid #eee;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.modal-header h3 {
	margin: 0;
	color: #2c3e50;
}

.close-btn {
	background: none;
	border: none;
	font-size: 1.5rem;
	cursor: pointer;
	color: #6c757d;
}

.modal-body {
	padding: 1.5rem;
}

.form-group {
	margin-bottom: 1.5rem;
}

.form-group label {
	display: block;
	margin-bottom: 0.5rem;
	font-weight: 600;
	color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
	width: 100%;
	padding: 0.75rem;
	border: 1px solid #ddd;
	border-radius: 6px;
	font-size: 0.9rem;
}

.form-actions {
	display: flex;
	gap: 1rem;
	justify-content: flex-end;
	margin-top: 2rem;
}
</style>