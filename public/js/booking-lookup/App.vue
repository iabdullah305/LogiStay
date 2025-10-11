<template>
  <div class="booking-lookup">
    <!-- Page Header -->
    <div class="page-header mb-8 text-center">
      <h1 class="text-3xl font-bold text-gray-900">Employee Booking Lookup</h1>
      <p class="text-gray-600 mt-2">Search for employee accommodation booking information</p>
    </div>

    <!-- Search Form -->
    <Card class="max-w-2xl mx-auto mb-8">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Employee</h3>
        
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
            <Input 
              v-model="searchForm.phone" 
              placeholder="Enter phone number"
              :disabled="loading"
            />
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
              Search Booking
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Multiple Employees Selection -->
    <Card v-if="multipleEmployees.length > 0" class="max-w-4xl mx-auto mb-8">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Multiple Employees Found</h3>
        <p class="text-gray-600 mb-4">Please select the employee you're looking for:</p>
        
        <div class="space-y-3">
          <div 
            v-for="employee in multipleEmployees" 
            :key="employee.name"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="selectEmployee(employee)"
          >
            <div>
              <p class="font-medium text-gray-900">{{ employee.employee_name }}</p>
              <p class="text-sm text-gray-600">ID: {{ employee.name }} | Department: {{ employee.department }}</p>
              <p class="text-sm text-gray-600">Phone: {{ employee.phone }}</p>
            </div>
            <Button variant="outline" theme="blue" size="sm">
              Select
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Employee Information -->
    <div v-if="employeeInfo" class="max-w-6xl mx-auto">
      <!-- Employee Details -->
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

      <!-- Accommodation Assignments -->
      <Card>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Accommodation History</h3>
            <Badge :label="`${accommodations.length} assignments`" theme="blue" />
          </div>
          
          <div v-if="accommodations.length === 0" class="text-center py-8 text-gray-500">
            <i class="fa fa-home text-2xl mb-2 block"></i>
            <p>No accommodation assignments found</p>
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="accommodation in accommodations" 
              :key="accommodation.assignment_id"
              class="border rounded-lg p-4"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <label class="text-sm font-medium text-gray-600">Accommodation</label>
                      <p class="text-gray-900 font-medium">{{ accommodation.accommodation_name }}</p>
                      <p class="text-sm text-gray-600">{{ accommodation.location }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-600">Room</label>
                      <p class="text-gray-900">{{ accommodation.room_number }}</p>
                      <p class="text-sm text-gray-600">Capacity: {{ accommodation.room_capacity }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-600">Duration</label>
                      <p class="text-gray-900">{{ formatDate(accommodation.check_in_date) }}</p>
                      <p class="text-sm text-gray-600">to {{ formatDate(accommodation.check_out_date) || 'Ongoing' }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-600">Supervisor</label>
                      <p class="text-gray-900">{{ accommodation.supervisor || 'N/A' }}</p>
                    </div>
                  </div>
                </div>
                <div class="ml-4">
                  <Badge 
                    :label="accommodation.status" 
                    :theme="getStatusTheme(accommodation.status)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
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
  name: 'BookingLookup',
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
        phone: ''
      },
      employeeInfo: null,
      accommodations: [],
      multipleEmployees: []
    }
  },
  computed: {
    hasSearchCriteria() {
      return this.searchForm.employee_id || this.searchForm.employee_name || this.searchForm.phone
    }
  },
  methods: {
    async searchEmployee() {
      if (!this.hasSearchCriteria) return
      
      this.loading = true
      this.error = null
      this.employeeInfo = null
      this.accommodations = []
      this.multipleEmployees = []
      
      try {
        const response = await this.$frappe.call({
          method: 'logistay.accommodation_management.api.booking.lookup_employee_booking',
          args: {
            employee_id: this.searchForm.employee_id || null,
            employee_name: this.searchForm.employee_name || null,
            phone: this.searchForm.phone || null
          }
        })
        
        if (response.message) {
          const data = response.message
          
          if (data.employees && data.employees.length > 1) {
            this.multipleEmployees = data.employees
          } else if (data.employee_info) {
            this.employeeInfo = data.employee_info
            this.accommodations = data.accommodations || []
          } else {
            this.error = data.message || 'No employee found with the provided information'
          }
        }
        
      } catch (err) {
        console.error('Search error:', err)
        this.error = err.message || 'Failed to search employee booking information'
      } finally {
        this.loading = false
      }
    },
    
    async selectEmployee(employee) {
      this.multipleEmployees = []
      this.searchForm.employee_id = employee.name
      await this.searchEmployee()
    },
    
    clearSearch() {
      this.searchForm = {
        employee_id: '',
        employee_name: '',
        phone: ''
      }
      this.employeeInfo = null
      this.accommodations = []
      this.multipleEmployees = []
      this.error = null
    },
    
    formatDate(dateStr) {
      if (!dateStr) return null
      return new Date(dateStr).toLocaleDateString('en-US')
    },
    
    getStatusTheme(status) {
      const themes = {
        'Active': 'green',
        'Completed': 'blue',
        'Cancelled': 'red',
        'Pending': 'orange'
      }
      return themes[status] || 'gray'
    }
  }
}
</script>

<style scoped>
.booking-lookup {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .booking-lookup {
    padding: 1rem;
  }
}
</style>