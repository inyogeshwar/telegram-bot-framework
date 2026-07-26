# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to yogeshwar853202@gmail.com. All security vulnerabilities will be promptly addressed.

**Please do NOT report security vulnerabilities through public GitHub issues.**

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Guidelines

### For Bot Developers

1. **Never hardcode tokens** — Use environment variables
2. **Validate user input** — Sanitize all data from users
3. **Implement rate limiting** — Prevent abuse
4. **Use webhook signatures** — Verify webhook authenticity
5. **Log securely** — Never log tokens or secrets
6. **Keep dependencies updated** — Monitor for vulnerabilities

### For Repository Contributors

1. **Never commit secrets** — Use .gitignore
2. **Review code changes** — Check for security issues
3. **Update dependencies** — Keep packages current
4. **Follow OWASP guidelines** — Apply security best practices

## Dependency Security

This project uses:
- `pip-audit` for vulnerability scanning
- GitHub Dependabot for automated updates
- CodeQL for static analysis

## Security Resources

- [OWASP Top 10](https://owasp.org/)
- [Python Security](https://python.org/security/)
- [Telegram Bot API Security](https://core.telegram.org/bots/api#using-a-local-bot-api-server)
