# Public Lookup Test Plan

## Test Overview

### Scope
This test plan covers functional, security, and compliance testing for the Public Lookup feature. All tests should be executed on a fresh Frappe site installation.

### Test Environment Setup
```bash
# Fresh site setup
bench new-site test-site
bench --site test-site install-app logistay
bench build --app logistay
bench clear-cache
```

## Functional Tests

### 1. Route Accessibility Tests

#### Test Case: F001 - Basic Route Access
**Objective**: Verify the public lookup page is accessible
**Steps**:
1. Navigate to `http://localhost:8000/public-lookup`
2. Verify page loads without authentication
3. Check page title and basic UI elements

**Expected Result**: Page loads successfully with search form

#### Test Case: F002 - Form Rendering
**Objective**: Verify all form elements render correctly
**Steps**:
1. Check search mode dropdown (employee, shift, trip)
2. Verify search value input field
3. Check date range inputs (from/to)
4. Verify search button

**Expected Result**: All form elements are present and functional

### 2. Search Functionality Tests

#### Test Case: F003 - Employee Search (Valid)
**Objective**: Test valid employee code search
**Test Data**: 
```json
{
  "search_mode": "employee",
  "search_value": "EMP001",
  "date_from": "2024-01-01",
  "date_to": "2024-01-31"
}
```
**Expected Result**: Returns employee data with trips and shifts

#### Test Case: F004 - Shift Search (Valid)
**Objective**: Test valid shift ID search
**Test Data**:
```json
{
  "search_mode": "shift",
  "search_value": "SHF-2024-001"
}
```
**Expected Result**: Returns shift data with employee info

#### Test Case: F005 - Trip Search (Valid)
**Objective**: Test valid trip ID search
**Test Data**:
```json
{
  "search_mode": "trip",
  "search_value": "TRP-2024-001"
}
```
**Expected Result**: Returns trip data with employee info

### 3. Validation Tests

#### Test Case: F006 - Invalid Employee Code
**Objective**: Test input validation for employee codes
**Test Data**: `"invalid_code_123"`
**Expected Result**: Validation error message displayed

#### Test Case: F007 - Invalid Date Format
**Objective**: Test date format validation
**Test Data**: `"2024/01/01"` (wrong format)
**Expected Result**: Date format error message

#### Test Case: F008 - Date Range Validation
**Objective**: Test maximum date range limit
**Test Data**: 
```json
{
  "date_from": "2024-01-01",
  "date_to": "2024-06-01"
}
```
**Expected Result**: Date range too large error (>90 days)

### 4. Empty State Tests

#### Test Case: F009 - No Results Found
**Objective**: Test behavior when no data matches
**Test Data**: Non-existent employee code
**Expected Result**: "No results found" message displayed

#### Test Case: F010 - Empty Database
**Objective**: Test behavior with no data in system
**Setup**: Fresh site with no test data
**Expected Result**: Graceful empty state handling

## Security Tests

### 1. Rate Limiting Tests

#### Test Case: S001 - Rate Limit Per Minute
**Objective**: Verify 10 requests per minute limit
**Steps**:
1. Make 10 valid API requests within 1 minute
2. Make 11th request immediately
3. Check response and headers

**Expected Result**: 11th request returns 429 Too Many Requests

#### Test Case: S002 - Rate Limit Per Hour
**Objective**: Verify 100 requests per hour limit
**Steps**:
1. Simulate 100 requests within 1 hour
2. Make 101st request
3. Check response

**Expected Result**: 101st request returns 429 Too Many Requests

### 2. Input Validation Security Tests

#### Test Case: S003 - SQL Injection Attempt
**Objective**: Test SQL injection prevention
**Test Data**: `"'; DROP TABLE tabEmployee; --"`
**Expected Result**: Input validation error, no database impact

#### Test Case: S004 - XSS Attempt
**Objective**: Test XSS prevention
**Test Data**: `"<script>alert('xss')</script>"`
**Expected Result**: Input validation error, no script execution

#### Test Case: S005 - Path Traversal Attempt
**Objective**: Test path traversal prevention
**Test Data**: `"../../../etc/passwd"`
**Expected Result**: Input validation error

### 3. Data Exposure Tests

#### Test Case: S006 - PII Field Filtering
**Objective**: Verify no PII is returned
**Steps**:
1. Make valid employee search
2. Check response fields
3. Verify no sensitive data

**Expected Result**: Only whitelisted fields returned

#### Test Case: S007 - Error Information Leakage
**Objective**: Test error message sanitization
**Steps**:
1. Trigger various error conditions
2. Check error responses
3. Verify no stack traces or internal info

**Expected Result**: Clean error messages only

## Performance Tests

### Test Case: P001 - Response Time
**Objective**: Verify acceptable response times
**Steps**:
1. Make 10 concurrent requests
2. Measure response times
3. Check for timeouts

**Expected Result**: All responses < 2 seconds

### Test Case: P002 - Large Dataset Handling
**Objective**: Test performance with large result sets
**Setup**: Employee with 100+ trips/shifts
**Expected Result**: Pagination works, reasonable response time

## Compliance Tests

### 1. Code Quality Tests

#### Test Case: C001 - No Arabic/RTL Content
**Objective**: Verify English-only codebase
**Steps**:
1. Search all files for Arabic characters
2. Check for RTL CSS properties
3. Verify UI text is English

**Command**: `grep -r "[\u0600-\u06FF]" /path/to/app/`
**Expected Result**: No Arabic characters found

#### Test Case: C002 - No Inline CSS
**Objective**: Verify no inline styles
**Steps**:
1. Search HTML files for style attributes
2. Check for embedded CSS

**Command**: `grep -r "style=" /path/to/app/`
**Expected Result**: No inline styles found

#### Test Case: C003 - No External CDNs
**Objective**: Verify no external dependencies
**Steps**:
1. Search for CDN URLs
2. Check network requests in browser

**Command**: `grep -r "cdn\|googleapis\|jsdelivr" /path/to/app/`
**Expected Result**: No external CDN references

### 2. Frappe Compliance Tests

#### Test Case: C004 - Frappe UI Usage
**Objective**: Verify only Frappe UI components used
**Steps**:
1. Check CSS imports
2. Verify component usage
3. Test with Frappe build process

**Expected Result**: Only Frappe UI assets loaded

#### Test Case: C005 - No Direct DB Writes
**Objective**: Verify read-only operations
**Steps**:
1. Search code for write operations
2. Monitor database during tests

**Command**: `grep -r "frappe\.db\.\(insert\|save\|delete\)" /path/to/app/`
**Expected Result**: No write operations found

## Automated Test Scripts

### Basic Functionality Test
```bash
#!/bin/bash
# Test basic functionality
curl -X POST http://localhost:8000/api/method/logistay.api.public_lookup.lookup_employee_data \
  -H "Content-Type: application/json" \
  -d '{"search_mode":"employee","search_value":"EMP001"}'
```

### Rate Limit Test
```bash
#!/bin/bash
# Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/method/logistay.api.public_lookup.lookup_employee_data \
    -H "Content-Type: application/json" \
    -d '{"search_mode":"employee","search_value":"EMP001"}'
  echo "Request $i completed"
done
```

### Security Test
```bash
#!/bin/bash
# Test input validation
curl -X POST http://localhost:8000/api/method/logistay.api.public_lookup.lookup_employee_data \
  -H "Content-Type: application/json" \
  -d '{"search_mode":"employee","search_value":"<script>alert(1)</script>"}'
```

## Test Data Requirements

### Minimum Test Data
```json
{
  "employees": [
    {
      "employee_code": "EMP001",
      "status": "Active",
      "hire_date": "2024-01-01"
    }
  ],
  "trips": [
    {
      "name": "TRP-2024-001",
      "trip_date": "2024-01-15",
      "status": "Completed",
      "employee": "EMP001"
    }
  ],
  "shifts": [
    {
      "name": "SHF-2024-001",
      "shift_date": "2024-01-15",
      "shift_type": "Day",
      "status": "Completed",
      "employee": "EMP001"
    }
  ]
}
```

## Test Execution Schedule

### Pre-Release Testing
- All functional tests (F001-F010)
- All security tests (S001-S007)
- Performance tests (P001-P002)
- Compliance tests (C001-C005)

### Post-Deployment Testing
- Basic functionality verification
- Rate limiting verification
- Security validation

### Regular Testing (Monthly)
- Performance regression tests
- Security vulnerability scans
- Compliance verification

## Test Report Template

### Test Summary
- Total tests executed: X
- Passed: Y
- Failed: Z
- Blocked: A

### Failed Test Details
- Test ID: [ID]
- Description: [Description]
- Expected Result: [Expected]
- Actual Result: [Actual]
- Severity: [High/Medium/Low]

### Recommendations
- [List of recommendations based on test results]