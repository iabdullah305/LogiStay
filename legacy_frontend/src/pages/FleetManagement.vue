<template>
  <div class="fleet-management">
    <div class="page-header">
      <h1>Fleet Management Dashboard</h1>
      <p>Monitor and manage your fleet operations</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <LoadingIndicator />
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card v-for="stat in statistics" :key="stat.title" class="stat-card">
          <template #body>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">{{ stat.title }}</p>
                <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
              </div>
              <div class="text-3xl" :class="stat.color">
                <i :class="stat.icon"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Today's Fuel Entries -->
      <Card class="fuel-entries-card">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Today's Fuel Entries</h2>
            <Button variant="outline" size="sm" @click="refreshData">
              <template #prefix>
                <i class="fa fa-refresh"></i>
              </template>
              Refresh
            </Button>
          </div>
        </template>
        <template #body>
          <div v-if="fuelEntries.length === 0" class="empty-state text-center py-8">
            <i class="fa fa-gas-pump text-4xl text-gray-400 mb-4"></i>
            <h3 class="text-lg font-medium text-gray-900 mb-2">No fuel entries today</h3>
            <p class="text-gray-600">Fuel entries will appear here when added</p>
          </div>
          <div v-else class="fuel-entries-list">
            <div v-for="entry in fuelEntries" :key="entry.name" class="fuel-entry-item">
              <div class="flex items-center justify-between p-4 border-b border-gray-200 last:border-b-0">
                <div class="flex items-center space-x-4">
                  <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <i class="fa fa-car text-blue-600"></i>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ entry.vehicle }}</p>
                    <p class="text-sm text-gray-600">{{ entry.driver || 'No driver assigned' }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-medium text-gray-900">{{ entry.fuel_amount }} L</p>
                  <p class="text-sm text-gray-600">{{ formatCurrency(entry.total_cost) }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state text-center py-8">
      <i class="fa fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Error loading data</h3>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <Button @click="loadData">Try Again</Button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Card, Button, LoadingIndicator } from 'frappe-ui'

export default {
  name: 'FleetManagement',
  components: {
    Card,
    Button,
    LoadingIndicator
  },
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const statistics = ref([])
    const fuelEntries = ref([])

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Load statistics
        const statsResponse = await frappe.call({
          method: 'logistay.api.get_fleet_statistics',
          args: {}
        })
        
        if (statsResponse.message) {
          statistics.value = [
            {
              title: 'Total Vehicles',
              value: statsResponse.message.total_vehicles || 0,
              icon: 'fa fa-car',
              color: 'text-blue-600'
            },
            {
              title: 'Active Drivers',
              value: statsResponse.message.active_drivers || 0,
              icon: 'fa fa-users',
              color: 'text-green-600'
            },
            {
              title: 'Ongoing Trips',
              value: statsResponse.message.ongoing_trips || 0,
              icon: 'fa fa-road',
              color: 'text-orange-600'
            },
            {
              title: 'Fuel Entries Today',
              value: statsResponse.message.fuel_entries_today || 0,
              icon: 'fa fa-gas-pump',
              color: 'text-purple-600'
            }
          ]
        }

        // Load today's fuel entries
        const fuelResponse = await frappe.call({
          method: 'logistay.api.get_todays_fuel_entries',
          args: {}
        })
        
        if (fuelResponse.message) {
          fuelEntries.value = fuelResponse.message
        }

      } catch (err) {
        console.error('Error loading fleet data:', err)
        error.value = err.message || 'Failed to load data'
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadData()
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'SAR'
      }).format(amount || 0)
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      error,
      statistics,
      fuelEntries,
      loadData,
      refreshData,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.fleet-management {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.page-header p {
  color: #6b7280;
  font-size: 1.1rem;
}

.stat-card {
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.fuel-entry-item:hover {
  background-color: #f9fafb;
}

.empty-state i {
  display: block;
}

.error-state i {
  display: block;
}
</style>