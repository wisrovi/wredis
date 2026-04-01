# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently supported:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please send an email to wisrovi.rodriguez@gmail.com with the following information:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes (optional)

We appreciate your efforts to responsibly disclose the vulnerability, and will make every effort to acknowledge and address it promptly.

## Security Best Practices

When using WRedis, consider the following security best practices:

### Redis Connection

- Use password authentication for Redis connections in production
- Use SSL/TLS encryption for Redis connections when possible
- Don't expose Redis to the public internet
- Use firewall rules to restrict access to Redis

### Data Handling

- Be careful about what data you store in Redis (avoid storing sensitive data in plaintext)
- Consider using Redis encryption modules for sensitive data
- Implement proper key expiration policies

### Network Security

- Use Redis in a private network
- Implement proper network segmentation
- Use VPC peering or VPN connections for Redis access

### Access Control

- Use Redis ACLs to limit access to specific commands and keys
- Implement proper authentication
- Rotate Redis passwords regularly

## Changelog

Security vulnerabilities will be documented in the CHANGELOG.md.
