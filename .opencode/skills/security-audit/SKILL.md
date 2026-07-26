---
name: security-audit
description: Audit Telegram bot code for vulnerabilities following OWASP guidelines
license: MIT
compatibility: opencode
metadata:
  audience: security
  framework: owasp
---

## What I do

- Review bot code for security vulnerabilities
- Check token management and secret handling
- Validate input sanitization and rate limiting
- Assess webhook security and deployment practices

## When to use me

Use this skill when auditing bot code, reviewing pull requests, or hardening deployments.
Follow OWASP Top 10 mapping for Telegram bot applications.

## Security Checklist

1. No hardcoded tokens or secrets
2. Environment variables for configuration
3. Input validation and sanitization
4. Rate limiting implemented
5. Webhook signatures validated
6. Logging does not expose sensitive data
7. Dependencies are up to date
8. Mini App initData validated with HMAC-SHA256

## References

- See `docs/16-security-audit.md` for complete security guide
- OWASP Top 10: https://owasp.org/
