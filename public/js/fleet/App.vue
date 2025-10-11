<template>
  <div class="fleet-management">
    <!-- Page Header -->
    <div class="page-header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">{{ $__('Fleet Management Dashboard') }}</h1>
      <p class="text-gray-600 mt-2">{{ $__('Monitor and manage your fleet operations') }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <LoadingIndicator />
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="!error" class="space-y-6">
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card 
          v-for="stat in statistics" 
          :key="stat.label"
          class="p-6"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">{{ stat.label }}</p>
              <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
            </div>
            <div class="p-3 rounded-full" :class="stat.bgColor">
              <i :class="stat.icon + ' text-white'"></i>
            </div>
          </div>
        </Card>
      </div>

      <!-- Today's Fuel Entries -->
      <Card class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">{{ $__("Today's Fuel Entries") }}</h3>
          <Badge :label="fuelEntries.length + ' entries'" theme="blue" />
        </div>
        
        <div v-if="fuelEntries.length === 0" class="text-center py-8">
          <p class="text-gray-500">{{ $__('No fuel entries for today') }}</p>
        </div>
        
        <div v-else class="space-y-3">
          <div 
            v-for="entry in fuelEntries" 
            :key="entry.name"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ entry.name }}</p>
              <p class="text-sm text-gray-600">{{ entry.vehicle }}</p>
            </div>
            <div class="text-right">
              <p class="font-medium text-gray-900">{{ entry.fuel_amount || entry.liters }} L</p>
              <p class="text-sm text-gray-600">{{ entry.total_cost || entry.amount }}</p>
            </div>
          </div>
        </div>
      </Card>

      <!-- Quick Actions -->
      <Card class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $__('Quick Actions') }}</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button 
            variant="solid" 
            theme="blue"
            @click="navigateToDocType('Fleet Vehicle')"
          >
            <i class="fa fa-car mr-2"></i>
            {{ $__('Manage Vehicles') }}
          </Button>
          <Button 
            variant="solid" 
            theme="green"
            @click="navigateToDocType('Fleet Driver')"
          >
            <i class="fa fa-user mr-2"></i>
            {{ $__('Manage Drivers') }}
          </Button>
          <Button 
            variant="solid" 
            theme="orange"
            @click="navigateToDocType('Fuel Entry')"
          >
            <i class="fa fa-gas-pump mr-2"></i>
            {{ $__('Add Fuel Entry') }}
          </Button>
        </div>
      </Card>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <div class="text-red-500 mb-4">
        <i class="fa fa-exclamation-triangle text-4xl"></i>
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ $__('Error Loading Dashboard') }}</h3>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <Button variant="solid" theme="blue" @click="loadDashboard">
        {{ $__('Retry') }}
      </Button>
    </div>
  </div>
</template>

<script>
import { Card, Button, Badge, LoadingIndicator } from 'frappe-ui'

export default {
  name: 'FleetManagement',
  components: {
    Card,
    Button,
    Badge,
    LoadingIndicator
  },
  data() {
    return {
      loading: true,
      error: null,
      statistics: [],
      fuelEntries: []
    }
  },
  mounted() {
    this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      this.error = null
      
      try {
        // Load fleet statistics
        const statsResponse = await this.$frappe.call({
          method: 'logistay.api.get_fleet_statistics'
        })
        
        if (statsResponse.message) {
          this.statistics = [
            {
              label: this.$__('Total Vehicles'),
              value: statsResponse.message.total_vehicles || 0,
              icon: 'fa fa-car',
              bgColor: 'bg-blue-500'
            },
            {
              label: this.$__('Active Drivers'),
              value: statsResponse.message.active_drivers || 0,
              icon: 'fa fa-user',
              bgColor: 'bg-green-500'
            },
            {
              label: this.$__('Ongoing Trips'),
              value: statsResponse.message.ongoing_trips || 0,
              icon: 'fa fa-road',
              bgColor: 'bg-orange-500'
            },
            {
              label: this.$__('Fuel Entries Today'),
              value: statsResponse.message.fuel_entries_today || 0,
              icon: 'fa fa-gas-pump',
              bgColor: 'bg-red-500'
            }
          ]
        }
        
        // Load today's fuel entries
        const fuelResponse = await this.$frappe.call({
          method: 'logistay.api.get_todays_fuel_entries'
        })
        
        if (fuelResponse.message) {
          this.fuelEntries = fuelResponse.message
        }
        
      } catch (err) {
        console.error('Error loading dashboard:', err)
        this.error = err.message || this.$__('Failed to load dashboard data')
      } finally {
        this.loading = false
      }
    },
    
    navigateToDocType(doctype) {
      // Navigate to Frappe desk for the specific doctype
      window.location.href = `/app/${doctype.toLowerCase().replace(' ', '-')}`
    }
  }
}
</script>

<style scoped>
.fleet-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
}

@media (max-width: 768px) {
  .fleet-management {
    padding: 1rem;
  }
}
</style>