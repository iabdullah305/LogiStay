# Public Lookup Operations Guide

## Overview
The Public Lookup feature provides read-only access to employee trips and shifts data through a secure, public-facing interface. This guide covers deployment, verification, and maintenance procedures.

## Deployment Steps

### 1. Fresh Site Installation
```bash
# Install the LogiStay app on a fresh site
bench get-app logistay
bench --site [site-name] install-app logistay
```

### 2. Build and Cache Management
```bash
# Build application assets
bench build --app logistay

# Clear cache to ensure changes are loaded
bench clear-cache

# Restart server (if needed)
bench restart
```

### 3. Route Verification
The public lookup page is accessible at: `http://[your-domain]/public-lookup`

## Verification Checklist

### Functional Tests
- [ ] Route responds with 200 status code
- [ ] Search form renders correctly
- [ ] All three search modes work (employee, shift, trip)
- [ ] Date range filtering functions properly
- [ ] Results display with proper formatting
- [ ] Pagination works correctly
- [ ] Error states display appropriately

### Security Tests
- [ ] Rate limiting is enforced (100/hour, 10/minute)
- [ ] Input validation rejects invalid formats
- [ ] Only whitelisted fields are returned
- [ ] No PII (Personally Identifiable Information) is exposed
- [ ] Guest access works without authentication

### Compliance Tests
- [ ] No Arabic/RTL content in UI or code
- [ ] No inline CSS styles
- [ ] No external CDN dependencies
- [ ] Uses only Frappe UI components
- [ ] No direct database writes in API

## Monitoring

### Usage Logs
API usage is logged to `Fleet Access Log` DocType with:
- Search mode used
- IP address (for rate limiting)
- Timestamp
- Success/failure status

### Performance Metrics
- Response time should be < 2 seconds
- Rate limit violations are logged
- Database query optimization for large datasets

## Troubleshooting

### Common Issues
1. **Route not found (404)**
   - Verify `website_route_rules` in hooks.py
   - Run `bench clear-cache`
   - Check if app is properly installed

2. **API errors**
   - Check server logs for validation errors
   - Verify DocType permissions
   - Ensure rate limits are not exceeded

3. **Empty results**
   - Verify test data exists in Fleet Driver, Fleet Trip, Fleet Shift
   - Check date range parameters
   - Validate search value format

### Log Locations
- Application logs: `[bench-path]/logs/[site].log`
- Error logs: `[bench-path]/logs/[site].error.log`
- Access logs: Fleet Access Log DocType in Frappe

## Maintenance

### Regular Tasks
- Monitor API usage patterns
- Review rate limit effectiveness
- Update field whitelist as needed
- Performance optimization for growing datasets

### Security Updates
- Regular review of exposed fields
- Rate limit adjustment based on usage
- Input validation pattern updates
- Access log analysis for suspicious activity