# Public Lookup Security Documentation

## Security Architecture

### Access Control
- **Guest Access**: Enabled for public consumption without authentication
- **Read-Only**: No database writes or modifications allowed
- **Whitelisted Methods**: Only specific API endpoints are exposed

### Rate Limiting Policy

#### Limits
- **Per Hour**: 100 requests per IP address
- **Per Minute**: 10 requests per IP address
- **Enforcement**: Frappe's built-in rate limiter with Redis backend

#### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Input Validation Rules

### Search Value Patterns
```python
# Employee Code: 3-10 alphanumeric characters
EMPLOYEE_CODE_PATTERN = r'^[A-Z0-9]{3,10}$'

# Date Format: YYYY-MM-DD
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'

# ID Pattern: 5-20 alphanumeric with hyphens
ID_PATTERN = r'^[A-Z0-9\-]{5,20}$'
```

### Parameter Validation
- **search_mode**: Must be 'employee', 'shift', or 'trip'
- **search_value**: Must match respective pattern
- **date_from/date_to**: Valid date format, logical range
- **limit**: Integer between 1-50
- **offset**: Non-negative integer

### Date Range Restrictions
- **Maximum Range**: 90 days
- **Future Dates**: Not allowed beyond current date
- **Historical Limit**: No restriction on past dates

## Field Whitelisting

### Employee Fields (No PII)
```python
EMPLOYEE_FIELDS = [
    "name",           # System ID
    "employee_code",  # Public identifier
    "status",         # Employment status
    "hire_date"       # Employment start date
]
```

### Trip Fields
```python
TRIP_FIELDS = [
    "name",                    # Trip ID
    "trip_date",              # Date of trip
    "status",                 # Trip status
    "start_time",             # Start time
    "end_time",               # End time
    "source_location",        # Origin
    "destination_location",   # Destination
    "distance"                # Distance in km
]
```

### Shift Fields
```python
SHIFT_FIELDS = [
    "name",         # Shift ID
    "shift_date",   # Date of shift
    "shift_type",   # Type of shift
    "status",       # Shift status
    "start_time",   # Start time
    "end_time"      # End time
]
```

## Excluded Sensitive Data

### Personal Information (PII)
- Full names
- National ID numbers
- Phone numbers
- Email addresses
- Home addresses
- Date of birth
- Nationality
- Gender

### Operational Data
- Vehicle details
- Driver assignments
- Project information
- Branch details
- Financial data
- Internal notes

## Security Measures

### SQL Injection Prevention
- **Parameterized Queries**: All database queries use Frappe ORM
- **Input Sanitization**: Strict regex validation
- **No Raw SQL**: Direct SQL execution is prohibited

### Cross-Site Scripting (XSS)
- **Output Encoding**: All data is JSON-encoded
- **Content-Type**: Proper headers set
- **No HTML Output**: Pure JSON API responses

### Cross-Origin Resource Sharing (CORS)
- **Same-Origin Policy**: Default Frappe CORS handling
- **No Wildcard Origins**: Specific domain restrictions
- **Preflight Handling**: Automatic OPTIONS support

### Data Exposure Prevention
- **Field Filtering**: Only whitelisted fields returned
- **Error Sanitization**: No stack traces in responses
- **Log Sanitization**: No sensitive data in logs

## Audit and Logging

### Access Logging
Every API call is logged with:
```python
{
    "user": "Guest",
    "document_type": "Public Lookup",
    "action": search_mode,
    "success": True/False,
    "timestamp": "2024-01-01 12:00:00",
    "ip_address": "192.168.1.1",
    "user_agent": "Browser/Version",
    "session_id": "session_hash",
    "error_message": null,
    "additional_info": {
        "search_value": "EMP001",
        "date_range": "2024-01-01 to 2024-01-31"
    }
}
```

### Security Events
- Rate limit violations
- Invalid input attempts
- Unauthorized access attempts
- System errors

## Compliance Requirements

### Data Protection
- **Minimal Data**: Only necessary fields exposed
- **Purpose Limitation**: Data used only for lookup
- **Retention**: Logs retained per policy
- **Access Control**: Guest-only, read-only access

### Security Standards
- **Input Validation**: OWASP guidelines
- **Rate Limiting**: Industry best practices
- **Error Handling**: Secure error responses
- **Logging**: Comprehensive audit trail

## Incident Response

### Security Breach Indicators
- Unusual traffic patterns
- Multiple rate limit violations
- Invalid input flood attacks
- Unauthorized data access attempts

### Response Procedures
1. **Immediate**: Block suspicious IP addresses
2. **Analysis**: Review access logs and patterns
3. **Mitigation**: Adjust rate limits if needed
4. **Documentation**: Record incident details
5. **Review**: Update security measures

## Regular Security Reviews

### Monthly Tasks
- Review access logs for anomalies
- Analyze rate limit effectiveness
- Check for new security vulnerabilities
- Update field whitelist if needed

### Quarterly Tasks
- Security penetration testing
- Code review for security issues
- Update validation patterns
- Review and update documentation