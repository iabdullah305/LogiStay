<template>
  <div class="driver-dashboard">
    <div class="page-header">
      <h1>Driver Dashboard</h1>
      <p>Manage your trips and profile information</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <LoadingIndicator />
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Navigation Tabs -->
      <div class="tabs-container mb-8">
        <div class="flex border-b border-gray-200">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 font-medium text-sm border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <i :class="tab.icon" class="mr-2"></i>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="profile-section">
          <Card>
            <template #header>
              <h2 class="text-lg font-semibold">Driver Profile</h2>
            </template>
            <template #body>
              <div v-if="driverInfo" class="profile-content">
                <div class="flex items-center mb-6">
                  <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mr-4">
                    <i class="fa fa-user text-2xl text-gray-600"></i>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold">{{ driverInfo.full_name || driverInfo.name }}</h3>
                    <p class="text-gray-600">Driver ID: {{ driverInfo.name }}</p>
                    <Badge :variant="getStatusVariant(driverInfo.status)">
                      {{ driverInfo.status || 'Active' }}
                    </Badge>
                  </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="info-item">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <p class="text-gray-900">{{ driverInfo.full_name || '-' }}</p>
                  </div>
                  <div class="info-item">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
                    <p class="text-gray-900">{{ driverInfo.employee || '-' }}</p>
                  </div>
                  <div class="info-item">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <p class="text-gray-900">{{ driverInfo.phone || '-' }}</p>
                  </div>
                  <div class="info-item">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <p class="text-gray-900">{{ driverInfo.email || '-' }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-8">
                <i class="fa fa-user-times text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600">No driver profile found</p>
              </div>
            </template>
          </Card>
        </div>

        <!-- Trips Tab -->
        <div v-if="activeTab === 'trips'" class="trips-section">
          <Card>
            <template #header>
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold">My Trips</h2>
                <Button variant="solid" @click="showNewTripModal = true">
                  <template #prefix>
                    <i class="fa fa-plus"></i>
                  </template>
                  New Trip
                </Button>
              </div>
            </template>
            <template #body>
              <!-- Trip Filters -->
              <div class="filters-section mb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select v-model="tripFilters.status" @change="loadTrips" class="form-select">
                      <option value="">All Status</option>
                      <option value="draft">Draft</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Date From</label>
                    <input type="date" v-model="tripFilters.dateFrom" @change="loadTrips" class="form-input">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Date To</label>
                    <input type="date" v-model="tripFilters.dateTo" @change="loadTrips" class="form-input">
                  </div>
                </div>
              </div>

              <!-- Trips List -->
              <div v-if="trips.length === 0" class="empty-state text-center py-8">
                <i class="fa fa-road text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No trips found</h3>
                <p class="text-gray-600">Start your first trip by clicking the New Trip button</p>
              </div>
              <div v-else class="trips-list space-y-4">
                <div v-for="trip in trips" :key="trip.name" class="trip-card border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium text-gray-900">{{ trip.route || trip.name }}</h4>
                    <Badge :variant="getStatusVariant(trip.status)">
                      {{ trip.status }}
                    </Badge>
                  </div>
                  <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span class="font-medium">Vehicle:</span> {{ trip.vehicle || '-' }}
                    </div>
                    <div>
                      <span class="font-medium">Date:</span> {{ formatDate(trip.trip_date) }}
                    </div>
                    <div>
                      <span class="font-medium">Start Time:</span> {{ trip.start_time || '-' }}
                    </div>
                    <div>
                      <span class="font-medium">End Time:</span> {{ trip.end_time || '-' }}
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>
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
import { Card, Button, LoadingIndicator, Badge } from 'frappe-ui'

export default {
  name: 'DriverDashboard',
  components: {
    Card,
    Button,
    LoadingIndicator,
    Badge
  },
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const activeTab = ref('profile')
    const driverInfo = ref(null)
    const trips = ref([])
    const showNewTripModal = ref(false)
    
    const tripFilters = ref({
      status: '',
      dateFrom: '',
      dateTo: ''
    })

    const tabs = [
      { id: 'profile', label: 'Profile', icon: 'fa fa-user' },
      { id: 'trips', label: 'My Trips', icon: 'fa fa-road' }
    ]

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Load driver profile
        const profileResponse = await frappe.call({
          method: 'logistay.api.get_current_driver_profile',
          args: {}
        })
        
        if (profileResponse.message) {
          driverInfo.value = profileResponse.message
        }

        // Load trips if on trips tab
        if (activeTab.value === 'trips') {
          await loadTrips()
        }

      } catch (err) {
        console.error('Error loading driver data:', err)
        error.value = err.message || 'Failed to load data'
      } finally {
        loading.value = false
      }
    }

    const loadTrips = async () => {
      try {
        const response = await frappe.call({
          method: 'logistay.api.get_driver_trips',
          args: {
            filters: tripFilters.value
          }
        })
        
        if (response.message) {
          trips.value = response.message
        }
      } catch (err) {
        console.error('Error loading trips:', err)
      }
    }

    const getStatusVariant = (status) => {
      const statusMap = {
        'active': 'green',
        'inactive': 'gray',
        'draft': 'gray',
        'in_progress': 'blue',
        'completed': 'green',
        'cancelled': 'red'
      }
      return statusMap[status] || 'gray'
    }

    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      error,
      activeTab,
      driverInfo,
      trips,
      tripFilters,
      showNewTripModal,
      tabs,
      loadData,
      loadTrips,
      getStatusVariant,
      formatDate
    }
  }
}
</script>

<style scoped>
.driver-dashboard {
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

.form-select,
.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.trip-card:hover {
  background-color: #f9fafb;
}

.empty-state i,
.error-state i {
  display: block;
}
</style>