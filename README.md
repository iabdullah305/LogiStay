# LogiStay

**Fleet and Accommodation Management System for Frappe Framework**

LogiStay is a comprehensive management solution built on Frappe Framework v16, designed to streamline fleet operations and accommodation management for organizations. The system provides both administrative interfaces and public-facing pages for efficient operations management.

## 🚀 Features

### Fleet Management
- **Vehicle Management**: Complete vehicle lifecycle tracking, ownership records, and maintenance scheduling
- **Driver Management**: Driver profiles, license tracking, and vehicle assignments
- **Trip Management**: Route planning, trip scheduling, and real-time tracking
- **Fuel Management**: Fuel consumption tracking and expense management
- **Maintenance Tracking**: Preventive maintenance scheduling and service history
- **Supplier Management**: Vendor contracts and service provider management
- **Cost Analysis**: Comprehensive cost calculation and reporting engine

### Accommodation Management
- **Property Management**: Accommodation units, room management, and facility tracking
- **Employee Assignments**: Staff accommodation allocation and management
- **Inspection System**: Regular property inspections and maintenance tracking
- **Supervisor Tasks**: Daily task management and workflow automation
- **Asset Management**: Property asset tracking and maintenance logs

## 🌐 Public Access Pages

LogiStay provides several public-facing pages for users to access information without requiring system login:

### For Employees & General Users
- **[Employee Trips & Shifts Lookup](/employee-trips-shifts)** - Search and view employee trip schedules and shift information
- **[Accommodation Booking Lookup](/booking-lookup)** - Check accommodation availability and booking status
- **[Availability Checker](/availability)** - Real-time accommodation and vehicle availability

### For Drivers
- **[Driver Dashboard](/driver)** - Dedicated driver interface for trip management, fuel logging, and support

### For Supervisors
- **[Supervisor Tasks](/supervisor/tasks)** - Daily task management and accommodation oversight

### For Fleet Managers
- **[Fleet Management Portal](/fleet-management)** - Fleet overview and management interface

## 📋 System Requirements

- **Frappe Framework**: v16.x or higher
- **Python**: 3.8+
- **Node.js**: 16+ (for frontend assets)
- **Database**: MariaDB 10.6+ or PostgreSQL 13+

## 🛠️ Installation

### Quick Installation

```bash
# Navigate to your Frappe bench directory
cd /path/to/your/bench

# Get the LogiStay app
bench get-app https://github.com/iabdullah305/LogiStay.git

# Install the app on your site
bench --site [your-site] install-app logistay

# Build assets
bench build --app logistay

# Restart services
bench restart
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/iabdullah305/LogiStay.git
cd LogiStay

# Install pre-commit hooks for code quality
pre-commit install

# Install dependencies
npm install

# Start development server
bench start
```

## 🔧 Configuration

After installation, LogiStay automatically creates two main workspaces:

1. **Fleet Management Workspace** - Access all fleet-related features
2. **Accommodation Management Workspace** - Manage accommodation operations

### Initial Setup Steps

1. **Configure Fleet Settings**: Set up vehicle types, fuel types, and maintenance schedules
2. **Create Accommodation Properties**: Add accommodation units and room configurations
3. **Set Up User Roles**: Assign appropriate roles (Fleet Manager, Driver, Accommodation Supervisor, etc.)
4. **Configure Public Access**: Customize public page settings and permissions

## 👥 User Roles

LogiStay includes predefined roles for different user types:

- **Fleet Manager**: Full fleet management access
- **Fleet Supervisor**: Fleet oversight and reporting
- **Fleet Driver**: Driver-specific features and trip management
- **Accommodation Manager**: Complete accommodation management
- **Accommodation Supervisor**: Daily operations and task management
- **Project Manager**: Cross-functional project oversight
- **Fleet Viewer**: Read-only access to fleet data

## 🔒 Security Features

- **Role-based Access Control**: Granular permissions for different user types
- **Public API Rate Limiting**: Protection against abuse of public endpoints
- **Audit Trail**: Comprehensive access logging via Fleet Access Log
- **Data Sanitization**: Secure public data exposure without PII
- **Session Management**: Secure authentication and session handling

## 🎨 Frontend Technology

- **Vue.js 3**: Modern reactive frontend framework
- **Frappe UI**: Consistent design system and components
- **Vite**: Fast build tool and development server
- **Responsive Design**: Mobile-friendly interfaces

## 📊 Reporting & Analytics

- **Driver Status Reports**: Driver performance and availability tracking
- **Vehicle Utilization Reports**: Fleet efficiency and usage analytics
- **Fuel Expense Reports**: Fuel consumption and cost analysis
- **Monthly Fleet Cost Reports**: Comprehensive cost breakdowns
- **Accommodation Occupancy**: Property utilization tracking

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Quality**: All code must pass pre-commit hooks
2. **Testing**: Include tests for new features
3. **Documentation**: Update documentation for any changes
4. **Frappe Standards**: Follow Frappe Framework conventions

### Development Tools

LogiStay uses the following tools for code quality:

- **ruff**: Python linting and formatting
- **eslint**: JavaScript linting
- **prettier**: Code formatting
- **pyupgrade**: Python syntax modernization

```bash
# Install development dependencies
pre-commit install

# Run quality checks
pre-commit run --all-files
```

## 📄 License

MIT License - see [LICENSE](license.txt) for details.

## 🏢 Publisher

**AFMCOltd**  
Email: afm@afmcoltd.com

## 🆘 Support

For support and questions:

1. **GitHub Issues**: Report bugs and feature requests
2. **Documentation**: Check the built-in help system
3. **Community**: Join the Frappe community discussions

---

**LogiStay** - Streamlining Fleet and Accommodation Management with Modern Technology
