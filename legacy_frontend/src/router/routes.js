export default [
  {
    path: '/',
    redirect: '/fleet-management'
  },
  {
    path: '/fleet-management',
    name: 'FleetManagement',
    component: () => import('../pages/FleetManagement.vue'),
    meta: {
      title: 'Fleet Management Dashboard'
    }
  },
  {
    path: '/driver-dashboard',
    name: 'DriverDashboard', 
    component: () => import('../pages/DriverDashboard.vue'),
    meta: {
      title: 'Driver Dashboard'
    }
  },
  {
    path: '/employee-trips-shifts',
    name: 'EmployeeTripsShifts',
    component: () => import('../pages/EmployeeTripsShifts.vue'),
    meta: {
      title: 'Employee Trips and Shifts'
    }
  }
]