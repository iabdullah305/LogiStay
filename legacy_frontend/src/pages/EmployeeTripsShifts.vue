<template>
  <div class="employee-trips-shifts">
    <div class="page-header">
      <h1>Employee Trips and Shifts</h1>
      <p>Search for employee trip and shift information</p>
    </div>

    <!-- Search Form -->
    <Card class="search-card mb-8">
      <template #header>
        <h2 class="text-lg font-semibold">Employee Lookup</h2>
      </template>
      <template #body>
        <form @submit.prevent="searchEmployee" class="search-form">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
              <input
                type="text"
                v-model="searchForm.employeeId"
                placeholder="Enter employee ID"
                class="form-input"
                :disabled="loading"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Employee Name</label>
              <input
                type="text"
                v-model="searchForm.employeeName"
                placeholder="Enter employee name"
                class="form-input"
                :disabled="loading"
              >
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date From</label>
              <input
                type="date"
                v-model="searchForm.dateFrom"
                class="form-input"
                :disabled="loading"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date To</label>
              <input
                type="date"
                v-model="searchForm.dateTo"
                class="form-input"
                :disabled="loading"
              >
            </div>
          </div>

          <div class="flex justify-center">
            <Button
              type="submit"
              variant="solid"
              :loading="loading"
              :disabled="!canSearch"
            >
              <template #prefix>
                <i class="fa fa-search"></i>
              </template>
              Search Employee
            </Button>
          </div>
        </form>
      </template>
    </Card>

    <!-- Search Results -->
    <div v-if="hasSearched" class="results-section">
      <!-- Employee Info -->
      <Card v-if="employeeInfo" class="employee-info-card mb-6">
        <template #header>
          <h3 class="text-lg font-semibold">Employee Information</h3>
        </template>
        <template #body>
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mr-4">
              <i class="fa fa-user text-xl text-gray-600"></i>
            </div>
            <div>
              <h4 class="text-lg font-semibold">{{ employeeInfo.employee_name }}</h4>
              <p class="text-gray-600">ID: {{ employeeInfo.name }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <p class="text-gray-900">{{ employeeInfo.department || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Designation</label>
              <p class="text-gray-900">{{ employeeInfo.designation || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <Badge :variant="getStatusVariant(employeeInfo.status)">
                {{ employeeInfo.status || 'Active' }}
              </Badge>
            </div>
          </div>
        </template>
      </Card>

      <!-- Trips Section -->
      <Card class="trips-card mb-6">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Trips</h3>
            <Badge variant="gray">{{ trips.length }} trips found</Badge>
          </div>
        </template>
        <template #body>
          <div v-if="trips.length === 0" class="empty-state text-center py-8">
            <i class="fa fa-road text-4xl text-gray-400 mb-4"></i>
            <h4 class="text-lg font-medium text-gray-900 mb-2">No trips found</h4>
            <p class="text-gray-600">No trips found for the selected criteria</p>
          </div>
          <div v-else class="trips-list">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trip Details
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vehicle
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="trip in trips" :key="trip.name" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ trip.route || trip.name }}</div>
                        <div class="text-sm text-gray-500">{{ trip.purpose || '-' }}</div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ trip.vehicle || '-' }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDate(trip.trip_date) }}</div>
                      <div class="text-sm text-gray-500">
                        {{ trip.start_time || '-' }} - {{ trip.end_time || '-' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <Badge :variant="getStatusVariant(trip.status)">
                        {{ trip.status }}
                      </Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </Card>

      <!-- Shifts Section -->
      <Card class="shifts-card">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Shifts</h3>
            <Badge variant="gray">{{ shifts.length }} shifts found</Badge>
          </div>
        </template>
        <template #body>
          <div v-if="shifts.length === 0" class="empty-state text-center py-8">
            <i class="fa fa-clock text-4xl text-gray-400 mb-4"></i>
            <h4 class="text-lg font-medium text-gray-900 mb-2">No shifts found</h4>
            <p class="text-gray-600">No shifts found for the selected criteria</p>
          </div>
          <div v-else class="shifts-list">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Shift Details
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="shift in shifts" :key="shift.name" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ shift.shift_type || shift.name }}</div>
                        <div class="text-sm text-gray-500">{{ shift.department || '-' }}</div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDate(shift.shift_date) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">
                        {{ shift.start_time || '-' }} - {{ shift.end_time || '-' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <Badge :variant="getStatusVariant(shift.status)">
                        {{ shift.status }}
                      </Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state text-center py-8">
      <i class="fa fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Search Error</h3>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <Button @click="clearError">Try Again</Button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { Card, Button, Badge } from 'frappe-ui'

export default {
  name: 'EmployeeTripsShifts',
  components: {
    Card,
    Button,
    Badge
  },
  setup() {
    const loading = ref(false)
    const error = ref(null)
    const hasSearched = ref(false)
    
    const searchForm = ref({
      employeeId: '',
      employeeName: '',
      dateFrom: '',
      dateTo: ''
    })
    
    const employeeInfo = ref(null)
    const trips = ref([])
    const shifts = ref([])

    const canSearch = computed(() => {
      return searchForm.value.employeeId.trim() || searchForm.value.employeeName.trim()
    })

    const searchEmployee = async () => {
      if (!canSearch.value) return

      try {
        loading.value = true
        error.value = null
        hasSearched.value = true
        
        // Reset results
        employeeInfo.value = null
        trips.value = []
        shifts.value = []

        // Search for employee and their data
        const response = await frappe.call({
          method: 'logistay.api.search_employee_trips_shifts',
          args: {
            employee_id: searchForm.value.employeeId,
            employee_name: searchForm.value.employeeName,
            date_from: searchForm.value.dateFrom,
            date_to: searchForm.value.dateTo
          }
        })
        
        if (response.message) {
          employeeInfo.value = response.message.employee_info
          trips.value = response.message.trips || []
          shifts.value = response.message.shifts || []
        }

      } catch (err) {
        console.error('Error searching employee:', err)
        error.value = err.message || 'Failed to search employee data'
      } finally {
        loading.value = false
      }
    }

    const clearError = () => {
      error.value = null
    }

    const getStatusVariant = (status) => {
      const statusMap = {
        'active': 'green',
        'inactive': 'gray',
        'draft': 'gray',
        'in_progress': 'blue',
        'completed': 'green',
        'cancelled': 'red',
        'scheduled': 'blue',
        'ongoing': 'orange'
      }
      return statusMap[status?.toLowerCase()] || 'gray'
    }

    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    return {
      loading,
      error,
      hasSearched,
      searchForm,
      employeeInfo,
      trips,
      shifts,
      canSearch,
      searchEmployee,
      clearError,
      getStatusVariant,
      formatDate
    }
  }
}
</script>

<style scoped>
.employee-trips-shifts {
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

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background-color: #f9fafb;
  color: #6b7280;
}

.empty-state i,
.error-state i {
  display: block;
}

.search-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.search-card :deep(.card-header) {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.search-card h2 {
  color: white;
}

.search-card label {
  color: rgba(255, 255, 255, 0.9) !important;
}
</style>