<template>
	<div class="fuel">
		<div class="page-header">
			<h2>{{ $__('Fuel Management') }}</h2>
			<button @click="showNewEntryModal = true" class="btn-primary">
				<i class="fa fa-plus"></i>
				{{ $__('Add Fuel Entry') }}
			</button>
		</div>

		<!-- Fuel Statistics -->
		<div class="fuel-stats">
			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-gas-pump"></i>
				</div>
				<div class="stat-content">
					<h3>{{ fuelStats.totalEntries }}</h3>
					<p>{{ $__('Total Entries') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-tint"></i>
				</div>
				<div class="stat-content">
					<h3>{{ fuelStats.totalLiters }}L</h3>
					<p>{{ $__('Total Liters') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-money"></i>
				</div>
				<div class="stat-content">
					<h3>{{ fuelStats.totalCost }} {{ $__('SAR') }}</h3>
					<p>{{ $__('Total Cost') }}</p>
				</div>
			</div>

			<div class="stat-card">
				<div class="stat-icon">
					<i class="fa fa-calendar"></i>
				</div>
				<div class="stat-content">
					<h3>{{ fuelStats.thisMonth }}</h3>
					<p>{{ $__('This Month') }}</p>
				</div>
			</div>
		</div>

		<!-- Search Filters -->
		<div class="filters-section">
			<div class="filters-grid">
				<div class="filter-group">
					<label>{{ $__('Vehicle') }}</label>
					<select v-model="filters.vehicle" @change="loadFuelEntries">
						<option value="">{{ $__('All Vehicles') }}</option>
						<option v-for="vehicle in vehicles" :key="vehicle.name" :value="vehicle.name">
							{{ vehicle.license_plate }} - {{ vehicle.model }}
						</option>
					</select>
				</div>
				<div class="filter-group">
					<label>{{ $__('Date From') }}</label>
					<input type="date" v-model="filters.dateFrom" @change="loadFuelEntries">
				</div>
				<div class="filter-group">
					<label>{{ $__('Date To') }}</label>
					<input type="date" v-model="filters.dateTo" @change="loadFuelEntries">
				</div>
			</div>
		</div>

		<!-- Fuel Entries List -->
		<div class="fuel-entries-container">
			<div v-if="loading" class="loading">
				<i class="fa fa-spinner fa-spin"></i>
				{{ $__('Loading fuel entries...') }}
			</div>

			<div v-else-if="fuelEntries.length === 0" class="empty-state">
				<i class="fa fa-gas-pump"></i>
				<h3>{{ $__('No fuel entries found') }}</h3>
				<p>{{ $__('Add your first fuel entry by clicking the Add Fuel Entry button') }}</p>
			</div>

			<div v-else class="fuel-entries-grid">
				<div v-for="entry in fuelEntries" :key="entry.name" class="fuel-entry-card">
					<div class="entry-header">
						<div class="entry-info">
							<h3>{{ entry.vehicle }}</h3>
							<p class="entry-date">{{ formatDate(entry.date) }}</p>
						</div>
						<div class="entry-amount">
							<span class="amount">{{ entry.fuel_qty }}L</span>
						</div>
					</div>

					<div class="entry-details">
						<div class="detail-row">
							<i class="fa fa-map-marker"></i>
							<span>{{ entry.fuel_station || $__('Not specified') }}</span>
						</div>
						<div class="detail-row">
							<i class="fa fa-money"></i>
							<span>{{ entry.expense_amount }} {{ $__('SAR') }}</span>
						</div>
						<div class="detail-row">
							<i class="fa fa-calculator"></i>
							<span>{{ (entry.expense_amount / entry.fuel_qty).toFixed(2) }} {{ $__('SAR/L') }}</span>
						</div>
						<div v-if="entry.odometer_reading" class="detail-row">
							<i class="fa fa-tachometer"></i>
							<span>{{ entry.odometer_reading }} {{ $__('km') }}</span>
						</div>
					</div>

					<div v-if="entry.remarks" class="entry-remarks">
						<p>{{ entry.remarks }}</p>
					</div>

					<div class="entry-actions">
						<button @click="viewEntry(entry)" class="btn-secondary">
							<i class="fa fa-eye"></i>
							{{ $__('View') }}
						</button>
						<button @click="editEntry(entry)" class="btn-primary">
							<i class="fa fa-edit"></i>
							{{ $__('Edit') }}
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- New Fuel Entry Modal -->
		<div v-if="showNewEntryModal" class="modal-overlay" @click="closeModal">
			<div class="modal" @click.stop>
				<div class="modal-header">
					<h3>{{ editingEntry ? $__('Edit Fuel Entry') : $__('New Fuel Entry') }}</h3>
					<button @click="closeModal" class="close-btn">
						<i class="fa fa-times"></i>
					</button>
				</div>

				<div class="modal-body">
					<form @submit.prevent="saveFuelEntry">
						<div class="form-group">
							<label>{{ $__('Vehicle') }}</label>
							<select v-model="fuelEntry.vehicle" required>
								<option value="">{{ $__('Select Vehicle') }}</option>
								<option v-for="vehicle in vehicles" :key="vehicle.name" :value="vehicle.name">
									{{ vehicle.license_plate }} - {{ vehicle.model }}
								</option>
							</select>
						</div>

						<div class="form-group">
							<label>{{ $__('Date') }}</label>
							<input type="date" v-model="fuelEntry.date" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Fuel Quantity (Liters)') }}</label>
							<input type="number" step="0.01" v-model="fuelEntry.fuel_qty" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Total Amount (SAR)') }}</label>
							<input type="number" step="0.01" v-model="fuelEntry.expense_amount" required>
						</div>

						<div class="form-group">
							<label>{{ $__('Fuel Station') }}</label>
							<input type="text" v-model="fuelEntry.fuel_station">
						</div>

						<div class="form-group">
							<label>{{ $__('Odometer Reading (km)') }}</label>
							<input type="number" v-model="fuelEntry.odometer_reading">
						</div>

						<div class="form-group">
							<label>{{ $__('Remarks') }}</label>
							<textarea v-model="fuelEntry.remarks" rows="3"></textarea>
						</div>

						<div class="form-actions">
							<button type="button" @click="closeModal" class="btn-secondary">
								{{ $__('Cancel') }}
							</button>
							<button type="submit" class="btn-primary" :disabled="saving">
								<i v-if="saving" class="fa fa-spinner fa-spin"></i>
								{{ saving ? $__('Saving...') : (editingEntry ? $__('Update') : $__('Save')) }}
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
	name: 'Fuel',
	data() {
		return {
			fuelEntries: [],
			vehicles: [],
			loading: false,
			saving: false,
			showNewEntryModal: false,
			editingEntry: null,
			filters: {
				vehicle: '',
				dateFrom: '',
				dateTo: ''
			},
			fuelStats: {
				totalEntries: 0,
				totalLiters: 0,
				totalCost: 0,
				thisMonth: 0
			},
			fuelEntry: {
				vehicle: '',
				date: '',
				fuel_qty: '',
				expense_amount: '',
				fuel_station: '',
				odometer_reading: '',
				remarks: ''
			}
		}
	},
	mounted() {
		this.loadFuelEntries()
		this.loadVehicles()
		this.loadFuelStats()
	},
	methods: {
		async loadFuelEntries() {
			this.loading = true
			try {
				const response = await frappe.call({
					method: 'fleet_management.api.driver.get_fuel_entries',
					args: this.filters
				})
				if (response.message) {
					this.fuelEntries = response.message
				}
			} catch (error) {
				console.error('Error loading fuel entries:', error)
				// Test data
				this.fuelEntries = [
					{
						name: 'FUEL-001',
						vehicle: 'VEH-001',
						date: '2024-01-15',
						fuel_qty: 45.5,
						expense_amount: 136.5,
						fuel_station: 'Aramco Station - Riyadh',
						odometer_reading: 15000,
						remarks: 'Full tank'
					},
					{
						name: 'FUEL-002',
						vehicle: 'VEH-001',
						date: '2024-01-10',
						fuel_qty: 38.2,
						expense_amount: 114.6,
						fuel_station: 'Petromin Station - Jeddah',
						odometer_reading: 14500,
						remarks: ''
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

		async loadFuelStats() {
			try {
				const response = await frappe.call({
					method: 'fleet_management.api.driver.get_fuel_stats'
				})
				if (response.message) {
					this.fuelStats = response.message
				}
			} catch (error) {
				console.error('Error loading fuel stats:', error)
				// Test data
				this.fuelStats = {
					totalEntries: 15,
					totalLiters: 650.5,
					totalCost: 1951.5,
					thisMonth: 5
				}
			}
		},

		async saveFuelEntry() {
			this.saving = true
			try {
				const method = this.editingEntry 
					? 'fleet_management.api.driver.update_fuel_entry'
					: 'fleet_management.api.driver.create_fuel_entry'
				
				const args = this.editingEntry 
					? { ...this.fuelEntry, name: this.editingEntry.name }
					: this.fuelEntry

				const response = await frappe.call({
					method: method,
					args: args
				})

				if (response.message) {
					if (this.editingEntry) {
						const index = this.fuelEntries.findIndex(e => e.name === this.editingEntry.name)
						if (index !== -1) {
							this.fuelEntries[index] = response.message
						}
					} else {
						this.fuelEntries.unshift(response.message)
					}
					
					this.closeModal()
					this.loadFuelStats()
					frappe.show_alert({
						message: this.$__(this.editingEntry ? 'Fuel entry updated successfully' : 'Fuel entry created successfully'),
						indicator: 'green'
					})
				}
			} catch (error) {
				console.error('Error saving fuel entry:', error)
				frappe.show_alert({
					message: this.$__('Error saving fuel entry'),
					indicator: 'red'
				})
			} finally {
				this.saving = false
			}
		},

		editEntry(entry) {
			this.editingEntry = entry
			this.fuelEntry = { ...entry }
			this.showNewEntryModal = true
		},

		viewEntry(entry) {
			// Open fuel entry details page
			window.open(`/app/fuel-entry/${entry.name}`, '_blank')
		},

		closeModal() {
			this.showNewEntryModal = false
			this.editingEntry = null
			this.fuelEntry = {
				vehicle: '',
				date: '',
				fuel_qty: '',
				expense_amount: '',
				fuel_station: '',
				odometer_reading: '',
				remarks: ''
			}
		},

		formatDate(dateStr) {
			return new Date(dateStr).toLocaleDateString('ar-SA')
		}
	}
}
</script>

<style scoped>
.fuel {
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

.fuel-stats {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
	gap: 1.5rem;
	margin-bottom: 2rem;
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
	background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
	font-size: 1.8rem;
	font-weight: 700;
	color: #2c3e50;
	margin: 0 0 0.5rem 0;
}

.stat-content p {
	color: #6c757d;
	margin: 0;
	font-size: 0.9rem;
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

.fuel-entries-container {
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

.fuel-entries-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
	gap: 1.5rem;
}

.fuel-entry-card {
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	overflow: hidden;
	transition: transform 0.3s ease;
}

.fuel-entry-card:hover {
	transform: translateY(-2px);
}

.entry-header {
	padding: 1.5rem;
	background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
	color: white;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.entry-info h3 {
	margin: 0 0 0.25rem 0;
	font-size: 1.1rem;
}

.entry-date {
	margin: 0;
	opacity: 0.9;
	font-size: 0.85rem;
}

.entry-amount .amount {
	font-size: 1.5rem;
	font-weight: 700;
}

.entry-details {
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
	color: #28a745;
}

.entry-remarks {
	padding: 0 1.5rem 1rem;
	color: #6c757d;
	font-style: italic;
}

.entry-actions {
	padding: 1rem 1.5rem;
	background: #f8f9fa;
	display: flex;
	gap: 0.5rem;
	justify-content: flex-end;
}

.btn-primary, .btn-secondary {
	padding: 0.5rem 1rem;
	border: none;
	border-radius: 6px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	font-size: 0.85rem;
}

.btn-primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
}

.btn-secondary {
	background: #6c757d;
	color: white;
}

.btn-primary:hover, .btn-secondary:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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