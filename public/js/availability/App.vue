<template>
  <div class="availability-checker">
    <!-- Page Header -->
    <div class="page-header mb-8 text-center">
      <h1 class="text-3xl font-bold text-gray-900">Room Availability</h1>
      <p class="text-gray-600 mt-2">Check available accommodations and rooms</p>
    </div>

    <!-- Search Form -->
    <Card class="max-w-4xl mx-auto mb-8">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Availability</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Check-in Date</label>
            <Input 
              type="date"
              v-model="searchForm.check_in_date" 
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Check-out Date</label>
            <Input 
              type="date"
              v-model="searchForm.check_out_date" 
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Accommodation (Optional)</label>
            <Input 
              v-model="searchForm.accommodation_id" 
              placeholder="Enter accommodation ID"
              :disabled="loading"
            />
          </div>
        </div>
        
        <div class="flex justify-center">
          <Button 
            variant="solid" 
            theme="blue" 
            @click="checkAvailability"
            :loading="loading"
          >
            <i class="fa fa-search mr-2"></i>
            Check Availability
          </Button>
        </div>
      </div>
    </Card>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <LoadingIndicator />
    </div>

    <!-- Availability Results -->
    <div v-else-if="availabilityData.length > 0" class="max-w-6xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-semibold text-gray-900">Available Accommodations</h3>
        <Badge :label="`${availabilityData.length} accommodations`" theme="green" />
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card 
          v-for="accommodation in availabilityData" 
          :key="accommodation.accommodation_id"
          class="hover:shadow-lg transition-shadow"
        >
          <div class="p-6">
            <!-- Accommodation Header -->
            <div class="flex items-start justify-between mb-4">
              <div>
                <h4 class="text-lg font-semibold text-gray-900">{{ accommodation.accommodation_name }}</h4>
                <p class="text-gray-600">{{ accommodation.location }}</p>
              </div>
              <Badge 
                :label="`${accommodation.available_capacity} available`" 
                :theme="accommodation.available_capacity > 0 ? 'green' : 'red'"
              />
            </div>
            
            <!-- Capacity Information -->
            <div class="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
              <div class="text-center">
                <p class="text-2xl font-bold text-blue-600">{{ accommodation.total_capacity }}</p>
                <p class="text-sm text-gray-600">Total Capacity</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold text-orange-600">{{ accommodation.current_occupancy }}</p>
                <p class="text-sm text-gray-600">Current Occupancy</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold text-green-600">{{ accommodation.available_capacity }}</p>
                <p class="text-sm text-gray-600">Available</p>
              </div>
            </div>
            
            <!-- Available Rooms -->
            <div v-if="accommodation.rooms && accommodation.rooms.length > 0">
              <h5 class="font-medium text-gray-900 mb-2">Available Rooms (showing first 5)</h5>
              <div class="space-y-2">
                <div 
                  v-for="room in accommodation.rooms" 
                  :key="room.name"
                  class="flex items-center justify-between p-2 bg-white border rounded"
                >
                  <div>
                    <span class="font-medium">Room {{ room.room_number }}</span>
                    <span class="text-sm text-gray-600 ml-2">Capacity: {{ room.room_capacity }}</span>
                  </div>
                  <Badge :label="room.status" theme="blue" size="sm" />
                </div>
              </div>
              
              <div v-if="accommodation.available_rooms > 5" class="mt-2 text-center">
                <p class="text-sm text-gray-600">
                  +{{ accommodation.available_rooms - 5 }} more rooms available
                </p>
              </div>
            </div>
            
            <!-- Action Button -->
            <div class="mt-4 pt-4 border-t">
              <Button 
                variant="outline" 
                theme="blue" 
                @click="viewAccommodationDetails(accommodation.accommodation_id)"
                class="w-full"
              >
                View Details
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- No Results -->
    <div v-else-if="searchPerformed && availabilityData.length === 0" class="max-w-2xl mx-auto">
      <Card>
        <div class="p-8 text-center">
          <div class="text-gray-400 mb-4">
            <i class="fa fa-home text-4xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Availability Found</h3>
          <p class="text-gray-600 mb-4">
            No accommodations are available for the selected criteria. 
            Try adjusting your search dates or check back later.
          </p>
          <Button variant="outline" theme="blue" @click="clearSearch">
            Clear Search
          </Button>
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
          <Button variant="outline" theme="red" @click="clearError">
            Try Again
          </Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script>
import { Card, Button, Input, Badge, LoadingIndicator } from 'frappe-ui'

export default {
  name: 'AvailabilityChecker',
  components: {
    Card,
    Button,
    Input,
    Badge,
    LoadingIndicator
  },
  data() {
    return {
      loading: false,
      error: null,
      searchPerformed: false,
      searchForm: {
        check_in_date: '',
        check_out_date: '',
        accommodation_id: ''
      },
      availabilityData: []
    }
  },
  mounted() {
    // Set default dates (today and tomorrow)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    this.searchForm.check_in_date = today.toISOString().split('T')[0]
    this.searchForm.check_out_date = tomorrow.toISOString().split('T')[0]
    
    // Auto-load availability on page load
    this.checkAvailability()
  },
  methods: {
    async checkAvailability() {
      this.loading = true
      this.error = null
      this.searchPerformed = true
      
      try {
        const response = await this.$frappe.call({
          method: 'logistay.accommodation_management.api.public.check_availability',
          args: {
            accommodation_id: this.searchForm.accommodation_id || null,
            check_in_date: this.searchForm.check_in_date || null,
            check_out_date: this.searchForm.check_out_date || null
          }
        })
        
        if (response.message) {
          this.availabilityData = response.message.availability || []
        }
        
      } catch (err) {
        console.error('Availability check error:', err)
        this.error = err.message || 'Failed to check availability'
      } finally {
        this.loading = false
      }
    },
    
    clearSearch() {
      this.searchForm = {
        check_in_date: '',
        check_out_date: '',
        accommodation_id: ''
      }
      this.availabilityData = []
      this.searchPerformed = false
      this.error = null
    },
    
    clearError() {
      this.error = null
    },
    
    viewAccommodationDetails(accommodationId) {
      // Navigate to accommodation details page
      window.location.href = `/accommodations/${accommodationId}`
    }
  }
}
</script>

<style scoped>
.availability-checker {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .availability-checker {
    padding: 1rem;
  }
}
</style>