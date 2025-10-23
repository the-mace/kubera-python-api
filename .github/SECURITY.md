# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please follow these steps:

1. **Email the maintainers** directly (do not open a public issue)
   - Include as much detail as possible about the vulnerability
   - Include steps to reproduce if possible
   - Specify which versions are affected

2. **Wait for a response** - we aim to respond within 48 hours

3. **Coordinate disclosure** - we'll work with you to:
   - Confirm the vulnerability
   - Develop and test a fix
   - Plan a coordinated disclosure timeline

## Security Best Practices

When using this library:

1. **Protect your API credentials**
   - Never commit credentials to version control
   - Use environment variables or `.env` files (listed in `.gitignore`)
   - Rotate credentials regularly

2. **Keep the library updated**
   - Update to the latest version to receive security patches
   - Monitor GitHub security advisories for this repository

3. **Validate API responses**
   - The library includes built-in validation, but always sanitize data before using it in security-sensitive contexts

4. **Be aware of rate limits**
   - Respect Kubera's rate limits to avoid service disruption
   - Handle `KuberaRateLimitError` exceptions appropriately

## Known Security Considerations

- **API Key IP Restrictions**: Some Kubera API keys may be restricted to specific IP addresses. This is a security feature - ensure your application's IP is allowlisted.
- **HTTPS Only**: The library enforces HTTPS for all API communications.
- **HMAC Authentication**: Uses HMAC-SHA256 signature-based authentication as required by the Kubera API.

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 0.1.1)
- Announced in GitHub Security Advisories
- Documented in the changelog

## Questions?

If you have questions about security but not a vulnerability to report, feel free to:
- Open a [GitHub Discussion](https://github.com/the-mace/kubera-python-api/discussions)
- Check the [documentation](README.md)
