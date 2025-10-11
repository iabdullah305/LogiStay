<template>
  <div class="supervisor-tasks">
    <!-- Authentication Check -->
    <div v-if="!isAuthenticated" class="max-w-md mx-auto mt-20">
      <Card>
        <div class="p-8 text-center">
          <div class="text-blue-500 mb-4">
            <i class="fa fa-lock text-3xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Authentication Required</h3>
          <p class="text-gray-600 mb-4">Please log in to access supervisor tasks.</p>
          <Button variant="solid" theme="blue" @click="redirectToLogin">
            Login
          </Button>
        </div>
      </Card>
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- Page Header -->
      <div class="page-header mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Supervisor Tasks</h1>
            <p class="text-gray-600 mt-2">Manage daily accommodation tasks</p>
          </div>
          <Button variant="solid" theme="green" @click="refreshTasks">
            <i class="fa fa-refresh mr-2"></i>
            Refresh
          </Button>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card class="p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100 mr-4">
              <i class="fa fa-tasks text-blue-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.total_tasks }}</p>
              <p class="text-sm text-gray-600">Total Tasks</p>
            </div>
          </div>
        </Card>
        
        <Card class="p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-orange-100 mr-4">
              <i class="fa fa-clock-o text-orange-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.pending_tasks }}</p>
              <p class="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </Card>
        
        <Card class="p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-green-100 mr-4">
              <i class="fa fa-check text-green-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.completed_tasks }}</p>
              <p class="text-sm text-gray-600">Completed</p>
            </div>
          </div>
        </Card>
        
        <Card class="p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-red-100 mr-4">
              <i class="fa fa-exclamation-triangle text-red-600"></i>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.overdue_tasks }}</p>
              <p class="text-sm text-gray-600">Overdue</p>
            </div>
          </div>
        </Card>
      </div>

      <!-- Filters -->
      <Card class="mb-6">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Filter Tasks</h3>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select 
                v-model="filters.status" 
                class="w-full p-2 border border-gray-300 rounded-md"
                @change="loadTasks"
              >
                <option value="">All Status</option>
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Overdue">Overdue</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">From Date</label>
              <Input 
                type="date"
                v-model="filters.date_from" 
                @change="loadTasks"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">To Date</label>
              <Input 
                type="date"
                v-model="filters.date_to" 
                @change="loadTasks"
              />
            </div>
            <div class="flex items-end">
              <Button variant="outline" theme="gray" @click="clearFilters" class="w-full">
                Clear Filters
              </Button>
            </div>
          </div>
        </div>
      </Card>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <LoadingIndicator />
      </div>

      <!-- Tasks List -->
      <Card v-else>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Tasks</h3>
            <Badge :label="`${tasks.length} tasks`" theme="blue" />
          </div>
          
          <div v-if="tasks.length === 0" class="text-center py-8 text-gray-500">
            <i class="fa fa-tasks text-2xl mb-2 block"></i>
            <p>No tasks found</p>
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="task in tasks" 
              :key="task.task_id"
              class="border rounded-lg p-4 hover:bg-gray-50"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center mb-2">
                    <h4 class="font-medium text-gray-900 mr-3">{{ task.description }}</h4>
                    <Badge 
                      :label="task.status" 
                      :theme="getStatusTheme(task.status)"
                      size="sm"
                    />
                    <Badge 
                      v-if="task.priority === 'High'"
                      label="High Priority" 
                      theme="red"
                      size="sm"
                      class="ml-2"
                    />
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div>
                      <span class="font-medium">Accommodation:</span>
                      {{ task.accommodation_name || 'N/A' }}
                    </div>
                    <div>
                      <span class="font-medium">Room:</span>
                      {{ task.room_number || 'N/A' }}
                    </div>
                    <div>
                      <span class="font-medium">Task Date:</span>
                      {{ formatDate(task.task_date) }}
                    </div>
                    <div>
                      <span class="font-medium">Due Date:</span>
                      {{ formatDate(task.due_date) }}
                    </div>
                  </div>
                  
                  <div v-if="task.completion_notes" class="mt-2 text-sm text-gray-600">
                    <span class="font-medium">Notes:</span> {{ task.completion_notes }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Error State -->
      <div v-if="error" class="mt-6">
        <Card class="border-red-200">
          <div class="p-6 text-center">
            <div class="text-red-500 mb-4">
              <i class="fa fa-exclamation-triangle text-2xl"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Error Loading Tasks</h3>
            <p class="text-gray-600 mb-4">{{ error }}</p>
            <Button variant="outline" theme="red" @click="loadTasks">
              Retry
            </Button>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import { Card, Button, Input, Badge, LoadingIndicator } from 'frappe-ui'

export default {
  name: 'SupervisorTasks',
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
      isAuthenticated: false,
      tasks: [],
      statistics: {
        total_tasks: 0,
        pending_tasks: 0,
        completed_tasks: 0,
        overdue_tasks: 0
      },
      filters: {
        status: '',
        date_from: '',
        date_to: ''
      }
    }
  },
  mounted() {
    this.checkAuthentication()
  },
  methods: {
    checkAuthentication() {
      // Check if user is logged in
      if (window.frappe && window.frappe.session && window.frappe.session.user !== 'Guest') {
        this.isAuthenticated = true
        this.loadStatistics()
        this.loadTasks()
      } else {
        this.isAuthenticated = false
      }
    },
    
    async loadStatistics() {
      try {
        const response = await this.$frappe.call({
          method: 'logistay.accommodation_management.api.supervisor.get_task_statistics'
        })
        
        if (response.message) {
          this.statistics = response.message
        }
        
      } catch (err) {
        console.error('Error loading statistics:', err)
      }
    },
    
    async loadTasks() {
      this.loading = true
      this.error = null
      
      try {
        const response = await this.$frappe.call({
          method: 'logistay.accommodation_management.api.supervisor.get_supervisor_tasks',
          args: {
            status: this.filters.status || null,
            date_from: this.filters.date_from || null,
            date_to: this.filters.date_to || null
          }
        })
        
        if (response.message) {
          this.tasks = response.message.tasks || []
        }
        
      } catch (err) {
        console.error('Error loading tasks:', err)
        this.error = err.message || 'Failed to load tasks'
      } finally {
        this.loading = false
      }
    },
    
    refreshTasks() {
      this.loadStatistics()
      this.loadTasks()
    },
    
    clearFilters() {
      this.filters = {
        status: '',
        date_from: '',
        date_to: ''
      }
      this.loadTasks()
    },
    
    redirectToLogin() {
      window.location.href = '/login'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-US')
    },
    
    getStatusTheme(status) {
      const themes = {
        'Pending': 'orange',
        'In Progress': 'blue',
        'Completed': 'green',
        'Satisfactory': 'green',
        'Overdue': 'red'
      }
      return themes[status] || 'gray'
    }
  }
}
</script>

<style scoped>
.supervisor-tasks {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .supervisor-tasks {
    padding: 1rem;
  }
}
</style>