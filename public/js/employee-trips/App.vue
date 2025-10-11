<template>
  <div class="employee-trips">
    <!-- Page Header -->
    <div class="page-header mb-8 text-center">
      <h1 class="text-3xl font-bold text-gray-900">Employee Trips and Shifts</h1>
      <p class="text-gray-600 mt-2">Search for employee trip and shift information</p>
    </div>

    <!-- Search Form -->
    <Card class="max-w-4xl mx-auto mb-8">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Employee</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Employee ID</label>
            <Input 
              v-model="searchForm.employee_id" 
              placeholder="Enter employee ID"
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Employee Name</label>
            <Input 
              v-model="searchForm.employee_name" 
              placeholder="Enter employee name"
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <Input 
              type="date"
              v-model="searchForm.date_from" 
              :disabled="loading"
            />
          </div>
        </div>
        
        <div class="flex justify-center">
          <Button 
            variant="solid" 
            theme="blue" 
            @click="searchEmployee"
            :loading="loading"
            :disabled="!hasSearchCriteria"
          >
            <i class="fa fa-search mr-2"></i>
            Search
          </Button>
        </div>
      </div>
    </Card>

    <!-- Results -->
    <div v-if="employeeInfo" class="max-w-6xl mx-auto">
      <!-- Employee Info -->
      <Card class="mb-6">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Employee Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-600">Name</label>
              <p class="text-gray-900">{{ employeeInfo.employee_name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600">Employee ID</label>
              <p class="text-gray-900">{{ employeeInfo.name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600">Department</label>
              <p class="text-gray-900">{{ employeeInfo.department || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </Card>

      <!-- Trips and Shifts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Trips -->
        <Card>
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Trips</h3>
              <Badge :label="`${trips.length} trips`" theme="blue" />
            </div>
            
            <div v-if="trips.length === 0" class="text-center py-8 text-gray-500">
              <i class="fa fa-road text-2xl mb-2 block"></i>
              <p>No trips found</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="trip in trips" 
                :key="trip.name"
                class="border rounded-lg p-3"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">{{ trip.route || trip.name }}</h4>
                  <Badge :label="trip.status" :theme="getStatusTheme(trip.status)" size="sm" />
                </div>
                <div class="text-sm text-gray-600">
                  <p>Date: {{ formatDate(trip.trip_date) }}</p>
                  <p>Vehicle: {{ trip.vehicle || 'N/A' }}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <!-- Shifts -->
        <Card>
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Shifts</h3>
              <Badge :label="`${shifts.length} shifts`" theme="green" />
            </div>
            
            <div v-if="shifts.length === 0" class="text-center py-8 text-gray-500">
              <i class="fa fa-clock-o text-2xl mb-2 block"></i>
              <p>No shifts found</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="shift in shifts" 
                :key="shift.name"
                class="border rounded-lg p-3"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">{{ shift.shift_type || shift.name }}</h4>
                  <Badge :label="shift.status" :theme="getStatusTheme(shift.status)" size="sm" />
                </div>
                <div class="text-sm text-gray-600">
                  <p>Date: {{ formatDate(shift.shift_date) }}</p>
                  <p>Time: {{ shift.start_time }} - {{ shift.end_time }}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="max-w-2xl mx-auto">
      <Card class="border-red-200">
        <div class="p-6 text-center">
          <div class="text-red-500 mb-4">
            <i class="fa fa-exclamation-triangle text-2xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Search Error</h3>
          <p class="text-gray-600 mb-4">{{ error }}</p>
          <Button variant="outline" theme="red" @click="clearSearch">
            Clear Search
          </Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script>
import { Card, Button, Input, Badge } from 'frappe-ui'

export default {
  name: 'EmployeeTrips',
  components: {
    Card,
    Button,
    Input,
    Badge
  },
  data() {
    return {
      loading: false,
      error: null,
      searchForm: {
        employee_id: '',
        employee_name: '',
        date_from: ''
      },
      employeeInfo: null,
      trips: [],
      shifts: []
    }
  },
  computed: {
    hasSearchCriteria() {
      return this.searchForm.employee_id || this.searchForm.employee_name
    }
  },
  mounted() {
    console.log('EmployeeTrips component mounted')
    console.log('Frappe available:', !!this.$frappe)
  },
  methods: {
    async searchEmployee() {
      if (!this.hasSearchCriteria) return
      
      this.loading = true
      this.error = null
      this.employeeInfo = null
      this.trips = []
      this.shifts = []
      
      console.log('Searching employee with criteria:', this.searchForm)
      
      try {
        const response = await this.$frappe.call({
          method: 'logistay.api.search_employee_trips_shifts',
          args: {
            employee_id: this.searchForm.employee_id || null,
            employee_name: this.searchForm.employee_name || null,
            date_from: this.searchForm.date_from || null,
            date_to: null
          }
        })
        
        console.log('Search response:', response)
        
        if (response.message) {
          const data = response.message
          this.employeeInfo = data.employee_info
          this.trips = data.trips || []
          this.shifts = data.shifts || []
          
          console.log('Employee found:', this.employeeInfo)
          console.log('Trips:', this.trips.length)
          console.log('Shifts:', this.shifts.length)
        }
        
      } catch (err) {
        console.error('Search error:', err)
        this.error = err.message || 'Failed to search employee information'
      } finally {
        this.loading = false
      }
    },
    
    clearSearch() {
      this.searchForm = {
        employee_id: '',
        employee_name: '',
        date_from: ''
      }
      this.employeeInfo = null
      this.trips = []
      this.shifts = []
      this.error = null
      
      console.log('Search cleared')
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-US')
    },
    
    getStatusTheme(status) {
      const themes = {
        'Active': 'green',
        'Completed': 'blue',
        'In Progress': 'orange',
        'Cancelled': 'red',
        'Scheduled': 'purple'
      }
      return themes[status] || 'gray'
    }
  }
}
</script>

<style scoped>
.employee-trips {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .employee-trips {
    padding: 1rem;
  }
}
</style>