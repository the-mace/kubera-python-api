# API Key Restrictions and Permissions

This document explains the restrictions and permission requirements for using the Kubera API.

## Overview

Kubera API keys can have different permission levels and restrictions:

1. **Read-only vs Update permissions**
2. **IP address restrictions**
3. **Rate limits**

## Permission Levels

### Read-Only API Keys

Read-only API keys can:
- ✅ List portfolios (`GET /api/v3/data/portfolio`)
- ✅ Get portfolio details (`GET /api/v3/data/portfolio/{id}`)
- ❌ Update items (`POST /api/v3/data/item/{id}`)

### Update-Enabled API Keys

Update-enabled API keys can:
- ✅ List portfolios
- ✅ Get portfolio details
- ✅ Update items

## IP Address Restrictions

Some API keys may be restricted to specific IP addresses.

**Symptoms:**
- 401 Authentication errors despite correct credentials
- Works from one location but not another

**Resolution:**
- Verify your current IP address
- Contact Kubera support to add your IP to the allowlist
- Consider using a VPN if working from multiple locations

## Error Messages

The library provides helpful error messages to identify permission issues:

### 401 Authentication Error
```
Authentication failed: [error message].
Check: 1) Credentials are correct, 2) IP address is allowed (some API keys have IP restrictions)
```

**Possible causes:**
- Invalid API key or secret
- IP address not in allowlist

### 403 Permission Error
```
Permission denied: [error message].
Note: Update operations require an API key with update permissions enabled.
Read-only API keys cannot modify data.
```

**Possible causes:**
- Using read-only API key for update operations
- API key lacks required permissions

### 429 Rate Limit Error
```
Rate limit exceeded: [error message].
Limits: 30 req/min, 100/day (Essential) or 1000/day (Black)
```

**Possible causes:**
- Exceeded requests per minute
- Exceeded daily request limit

## CLI Warnings

The CLI includes warnings about permissions:

### Main Help (`kubera --help`)
```
NOTES:
- Update operations require API keys with update permissions enabled
- Some API keys may be IP address restricted
```

### Update Command (`kubera update --help`)
```
IMPORTANT: This command requires an API key with UPDATE PERMISSIONS enabled.
Read-only API keys will fail with a 403 error.
```

## Python Library Usage

When using the Python library, handle permissions gracefully:

```python
from kubera import KuberaClient, KuberaAPIError

client = KuberaClient()

try:
    # This works with read-only keys
    portfolios = client.get_portfolios()

    # This requires update permissions
    client.update_item("item_id", {"value": 50000})

except KuberaAPIError as e:
    if e.status_code == 401:
        print("Authentication failed - check credentials and IP restrictions")
    elif e.status_code == 403:
        print("Permission denied - API key needs update permissions")
    elif e.status_code == 429:
        print("Rate limit exceeded - wait before retrying")
```

## Best Practices

1. **Use Read-Only Keys for Read Operations**
   - Minimize security risk by using read-only keys when updates aren't needed
   - Only use update-enabled keys when necessary

2. **Monitor Rate Limits**
   - Track your API usage
   - Implement exponential backoff for 429 errors
   - Cache responses when appropriate

3. **Handle IP Restrictions**
   - Document allowed IP addresses
   - Test from all required locations
   - Plan for IP changes (static IPs, VPN solutions)

4. **Error Handling**
   - Always catch and handle permission errors gracefully
   - Provide clear feedback to users about permission requirements
   - Log errors for debugging

## Troubleshooting

### "Authentication failed" errors

1. Verify credentials are correct:
   ```bash
   echo $KUBERA_API_KEY
   echo $KUBERA_SECRET
   ```

2. Check your IP address:
   ```bash
   curl ifconfig.me
   ```

3. Test with the connection script:
   ```bash
   python test_connection.py
   ```

### "Permission denied" errors on updates

1. Verify your API key has update permissions (contact Kubera support)
2. Use read-only operations to verify credentials work:
   ```bash
   kubera list  # Should work with any key
   ```

3. Try update with a different API key if available

### Rate limit errors

1. Check current usage
2. Wait for rate limit window to reset
3. Implement request throttling in your code:
   ```python
   import time

   for item in items:
       client.update_item(item['id'], updates)
       time.sleep(2)  # Wait 2 seconds between requests
   ```

## Support

For issues related to:
- Enabling update permissions on your API key
- Adding IP addresses to allowlist
- Increasing rate limits

Contact Kubera support through your account dashboard.
