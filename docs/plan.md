# Complete Application Design Plan - Frappe Framework v15+

## Primary Objective

Design and build a complete, production-ready Frappe application with full functionality including DocTypes, controllers, client scripts, server scripts, reports, and UI customizations.

## Sub-Objectives

1. Generate complete application structure following Frappe best practices
2. Create fully functional DocTypes with business logic
3. Implement validation, permissions, and workflows
4. Build custom reports and dashboards
5. Add client-side and server-side automation
6. Ensure security and data integrity

## Application Components

### Core Components
- DocTypes (parent and child tables)
- Python controllers (document lifecycle methods)
- Client Scripts (JavaScript UI logic)
- Server Scripts (Python automation)
- Print Formats
- Custom Reports
- Dashboards
- Web Forms (optional)
- REST API endpoints (optional)

### Supporting Components
- Fixtures (default data)
- Patches (data migration)
- Hooks (app-level configurations)
- Custom fields (extending standard DocTypes)
- Property Setters (UI customizations)

## Fleet Management System - Specific Requirements

### System Overview
Develop a precise mechanism for recording and analyzing operational costs of vehicle fleets to enhance financial control and facilitate monthly accounting report generation.

### Vehicle Ownership Classification

**Category 1: Company-Owned Vehicles**
- Internal company assets
- Require notional cost calculation
- Driver salary allocation
- Direct fuel cost tracking

**Category 2: Supplier Vehicles**
- Provided through external supplier contracts
- Multiple contract models supported
- Fuel responsibility defined per contract

### Supplier Vehicle Cost Models

**Model 1: Shift-Based Payment**
- Cost per shift formula: `Number of Shifts × Rate per Shift`
- Requires shift logging mechanism
- Monthly aggregation for billing

**Model 2: Fixed-Rate Leasing**
- Monthly flat rate independent of usage
- Optional shift limit enforcement
- Excess shift alert system
- Formula: `Monthly Fixed Rate + Excess Charges`

**Model 3: Fuel Cost Allocation**
- Configurable per contract
- Options: Company Pays / Supplier Pays
- Impacts total cost calculation
- Requires fuel consumption tracking

### Company-Owned Vehicle Costs

**Component 1: Notional Cost**
- Represents asset depreciation
- Estimated operational value
- Used for internal cost allocation
- Formula: `(Asset Value / Expected Life) / 12 months`

**Component 2: Direct Costs**
- **Driver Salaries**: 
  - Monthly salary allocation
  - Pro-rated if multiple vehicles
  - Linked to assignment period
- **Fuel Consumption**:
  - Actual fuel costs tracked
  - Per-vehicle consumption records
  - Monthly totals calculated

### Required Reporting Capabilities

**Monthly Cost Reports with Filters:**

1. **By Supplier**
   - Total costs per supplier
   - Vehicle count per supplier
   - Contract type breakdown
   - Payment summary

2. **By Vehicle**
   - Individual vehicle history
   - Total shifts worked
   - Fuel consumption
   - Assigned driver costs
   - Project allocations

3. **By Shift**
   - Shift-level details
   - Vehicle utilization
   - Cost per shift
   - Driver assignments

4. **By Branch**
   - Branch-wise cost allocation
   - Vehicle distribution
   - Operational metrics

5. **By Project**
   - Project cost allocation
   - Vehicle assignments
   - Duration tracking
   - Resource utilization

### DocType Structure for Fleet Management

**Master Data DocTypes:**
1. **Vehicle Master**
   - Vehicle details
   - Ownership type
   - Registration info
   - Current status

2. **Supplier Master**
   - Supplier information
   - Contact details
   - Contract terms

3. **Driver Master**
   - Driver details
   - Salary information
   - License data

**Transactional DocTypes:**
4. **Supplier Contract**
   - Contract type (Shift/Fixed)
   - Rate details
   - Fuel responsibility
   - Validity period
   - Shift limits

5. **Vehicle Assignment**
   - Vehicle-to-driver mapping
   - Project allocation
   - Branch assignment
   - Period tracking

6. **Shift Log**
   - Shift date and time
   - Vehicle used
   - Driver assigned
   - Project/Branch
   - Status

7. **Fuel Entry**
   - Vehicle reference
   - Fuel quantity
   - Cost amount
   - Date and location
   - Responsible party

8. **Driver Salary Allocation**
   - Monthly salary split
   - Vehicle assignments
   - Calculation logic

**Report DocTypes:**
9. **Monthly Cost Summary**
   - Auto-generated monthly
   - All vehicles included
   - Cost breakdowns
   - Variance analysis

10. **Fleet Cost Analysis**
    - Custom report
    - Multiple filters
    - Export capability
    - Drill-down features

### Critical Business Logic

**Cost Calculation Workflows:**

1. **Shift-Based Supplier Costs**
```python
def calculate_shift_costs(contract, month, year):
    shifts = get_shifts_for_contract(contract, month, year)
    total = len(shifts) * contract.rate_per_shift
    if not contract.company_pays_fuel:
        fuel_costs = get_fuel_costs(shifts)
        total += fuel_costs
    return total
```

2. **Fixed-Rate Supplier Costs**
```python
def calculate_fixed_costs(contract, month, year):
    base_cost = contract.monthly_rate
    shifts = get_shifts_for_contract(contract, month, year)
    
    excess_cost = 0
    if contract.max_shifts and len(shifts) > contract.max_shifts:
        excess = len(shifts) - contract.max_shifts
        excess_cost = excess * contract.excess_shift_rate
    
    fuel_cost = 0
    if contract.company_pays_fuel:
        fuel_cost = get_fuel_costs(shifts)
    
    return base_cost + excess_cost + fuel_cost
```

3. **Company Vehicle Costs**
```python
def calculate_company_vehicle_costs(vehicle, month, year):
    # Notional cost
    notional = vehicle.notional_monthly_cost
    
    # Driver salary allocation
    assignments = get_assignments(vehicle, month, year)
    driver_cost = sum(a.allocated_salary for a in assignments)
    
    # Fuel costs
    fuel_cost = get_fuel_costs_for_vehicle(vehicle, month, year)
    
    return notional + driver_cost + fuel_cost
```

### Validation Rules

**Contract Validations:**
- Shift-based contracts must have rate_per_shift
- Fixed contracts must have monthly_rate
- Fuel responsibility must be specified
- Contract dates must not overlap for same vehicle

**Assignment Validations:**
- Vehicle cannot be assigned to multiple drivers simultaneously
- Assignment must be within contract validity (supplier vehicles)
- Driver must have valid license
- Project and branch must be active

**Shift Log Validations:**
- Shift must be within assignment period
- Vehicle must be available (not in maintenance)
- Driver must be assigned to vehicle
- No overlapping shifts for same vehicle

**Fuel Entry Validations:**
- Must link to valid vehicle
- Date must be logical (not future)
- Responsible party must match contract terms
- Quantity must be reasonable

### Automation Requirements

**Scheduled Tasks:**
1. **End of Month Processing** (Runs on 1st of month)
   - Generate cost summaries for previous month
   - Calculate all vehicle costs
   - Send alerts for anomalies

2. **Daily Validations** (Runs daily)
   - Check for missing shift logs
   - Validate fuel entries
   - Alert on contract expirations

3. **Weekly Reports** (Runs every Monday)
   - Send utilization reports
   - Highlight cost variances
   - Flag maintenance needs

**Event-Based Automation:**
- On shift creation: Validate assignment and availability
- On fuel entry: Calculate running costs
- On contract expiry: Alert and prevent new shifts
- On assignment end: Calculate final costs

### Report Specifications

**1. Monthly Fleet Cost Report**
- **Filters**: Month, Year, Supplier, Vehicle, Branch, Project
- **Columns**: Vehicle, Ownership Type, Shifts, Base Cost, Fuel Cost, Driver Cost, Total
- **Grouping**: By supplier, then by vehicle
- **Totals**: Subtotals per supplier, grand total
- **Charts**: Cost breakdown pie chart, trend line

**2. Vehicle Utilization Report**
- **Filters**: Date range, Vehicle, Driver, Project
- **Columns**: Vehicle, Total Shifts, Idle Days, Utilization %
- **Sorting**: By utilization descending
- **Highlights**: Underutilized vehicles

**3. Supplier Performance Report**
- **Filters**: Month, Year, Supplier
- **Metrics**: Total vehicles, Total cost, Average cost per shift
- **Comparison**: Month-over-month variance
- **Export**: Excel with detailed breakdown

### Security & Permissions

**Role-Based Access:**
- **Fleet Manager**: Full access to all modules
- **Finance Team**: Read-only on costs, write on approvals
- **Project Manager**: Read-only on assigned vehicles
- **Driver**: Limited to own assignments and shift logs
- **Supplier**: View own contracts and vehicles only

**Document-Level Permissions:**
- Submitted shifts cannot be edited
- Cost summaries locked after approval
- Contract modifications require approval workflow

## Development Phases

### Phase 1: Requirements Analysis

**Tasks:**
- Understand business process and workflows
- Identify all entities and relationships
- Define user roles and permissions
- Map data flow between modules
- Identify integration points

**Deliverables:**
- Business requirements document
- Entity relationship diagram
- User role matrix
- Workflow diagrams

### Phase 2: Application Architecture

**Tasks:**
- Design DocType structure
- Plan field types and validations
- Define naming series
- Create child table relationships
- Design permission rules
- Plan automation triggers

**Deliverables:**
- DocType specifications
- Field mapping document
- Permission matrix
- Automation flowcharts

### Phase 3: Core Development

**Tasks:**
- Create DocType JSON files
- Build Python controllers with hooks:
  - `validate()` - data validation
  - `before_save()` - pre-save logic
  - `after_insert()` - post-creation actions
  - `on_submit()` - submission workflow
  - `on_cancel()` - cancellation logic
  - `on_trash()` - deletion handling
- Implement business logic methods
- Add calculated fields
- Create server scripts for automation

**Deliverables:**
- Complete DocType files
- Controller Python files
- Server scripts
- Unit tests

### Phase 4: User Interface

**Tasks:**
- Create client scripts for:
  - Field dependency management
  - Dynamic form behavior
  - Custom buttons and actions
  - Data fetching and filtering
- Design custom print formats
- Build dashboard charts
- Create custom pages (if needed)

**Deliverables:**
- Client script files
- Print format HTML/Jinja
- Dashboard JSON
- Custom page code

### Phase 5: Reports & Analytics

**Tasks:**
- Build Query Reports (SQL-based)
- Create Script Reports (Python-based)
- Design dashboard widgets
- Implement data visualization
- Add report filters and permissions

**Deliverables:**
- Report Python/JSON files
- Dashboard configurations
- Chart specifications

### Phase 6: Testing & Deployment

**Tasks:**
- Write unit tests for controllers
- Perform integration testing
- Test permissions and workflows
- Load test with sample data
- Prepare deployment package

**Deliverables:**
- Test cases and results
- Deployment documentation
- User training materials

## Critical Rules & Best Practices

### DocType Design Rules

**Field Naming:**
- Use `lowercase_with_underscores`
- Descriptive names (avoid abbreviations)
- Consistent naming convention

**Field Types:**
- Choose appropriate types for data
- Use Link for relationships
- Currency for money values
- Check for boolean flags

**Defaults & Validations:**
- Set sensible defaults
- Add mandatory field checks
- Implement custom validations
- Use regex patterns where needed

### Controller Development Rules

**Code Organization:**
```python
class YourDocType(Document):
    def validate(self):
        # Validation logic
        
    def before_save(self):
        # Pre-save calculations
        
    def on_submit(self):
        # Post-submission actions
```

**Best Practices:**
- Keep methods focused and small
- Use helper functions
- Add error handling
- Log important actions
- Follow PEP 8 style guide

### Client Script Rules

**Event Handlers:**
```javascript
frappe.ui.form.on('DocType Name', {
    refresh: function(frm) {
        // Form refresh logic
    },
    field_name: function(frm) {
        // Field change logic
    }
});
```

**Best Practices:**
- Minimize API calls
- Cache data when possible
- Show user-friendly messages
- Handle errors gracefully

### Security Rules

**Permissions:**
- Define role-based access
- Set field-level permissions
- Control document states
- Restrict sensitive operations

**Data Validation:**
- Validate on both client and server
- Sanitize user inputs
- Prevent SQL injection
- Verify file uploads

## Application Structure

```
app_name/
├── app_name/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── config/
│   │   ├── desktop.py
│   │   └── docs.py
│   ├── module_name/
│   │   ├── doctype/
│   │   │   ├── doctype_name/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── doctype_name.py
│   │   │   │   ├── doctype_name.js
│   │   │   │   ├── doctype_name.json
│   │   │   │   └── test_doctype_name.py
│   │   ├── report/
│   │   │   ├── report_name/
│   │   │   │   ├── report_name.py
│   │   │   │   └── report_name.json
│   │   └── page/
│   │       └── page_name/
│   └── public/
│       ├── js/
│       └── css/
├── requirements.txt
└── setup.py
```

## Common Patterns & Solutions

### Pattern 1: Master-Detail Relationship
```python
# Parent DocType with Child Table
class SalesOrder(Document):
    def calculate_total(self):
        total = sum(item.amount for item in self.items)
        self.total = total
```

### Pattern 2: Workflow Automation
```python
def on_submit(self):
    if self.approval_status == "Approved":
        self.create_delivery_note()
```

### Pattern 3: Dynamic Field Filtering
```javascript
frappe.ui.form.on('DocType', {
    customer: function(frm) {
        frm.set_query('contact', function() {
            return {
                filters: {
                    'customer': frm.doc.customer
                }
            };
        });
    }
});
```

### Pattern 4: Custom Reports
```python
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
```

## Quality Assurance Checklist

### Code Quality
- [ ] Follows Frappe coding standards
- [ ] Proper error handling
- [ ] Meaningful variable names
- [ ] Commented complex logic
- [ ] No hardcoded values

### Functionality
- [ ] All validations work correctly
- [ ] Workflows function as expected
- [ ] Reports display accurate data
- [ ] Permissions enforced properly
- [ ] No data integrity issues

### Performance
- [ ] Efficient database queries
- [ ] Optimized loops and calculations
- [ ] Minimal API calls
- [ ] Proper indexing on fields
- [ ] Fast page load times

### User Experience
- [ ] Intuitive form layouts
- [ ] Clear error messages
- [ ] Helpful field descriptions
- [ ] Responsive UI elements
- [ ] Mobile-friendly design

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database backup created
- [ ] Migration scripts prepared
- [ ] Documentation completed

### Deployment Steps
- [ ] Install app on production
- [ ] Run database migrations
- [ ] Import fixtures/master data
- [ ] Configure permissions
- [ ] Test critical workflows

### Post-Deployment
- [ ] Monitor error logs
- [ ] Verify data integrity
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Gather user feedback

## Common Errors & Solutions

### Error: "Invalid Field Name"
**Cause:** Field name contains uppercase or spaces
**Solution:** Use lowercase_with_underscores format

### Error: "Mandatory field missing"
**Cause:** Required field not set before save
**Solution:** Set value in validate() or before_save()

### Error: "Permission denied"
**Cause:** User lacks required role
**Solution:** Adjust role permissions in DocType

### Error: "Duplicate entry"
**Cause:** Unique constraint violation
**Solution:** Check for existing records before creating

## Success Metrics

### Technical Metrics
- Zero critical bugs in production
- Page load time < 2 seconds
- API response time < 500ms
- Test coverage > 80%

### Business Metrics
- User adoption rate
- Process efficiency improvement
- Error reduction percentage
- Time saved per transaction

## Conclusion

This comprehensive plan ensures systematic development of production-ready Frappe applications. Success depends on thorough planning, adherence to best practices, and continuous testing throughout the development lifecycle.