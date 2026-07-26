# Telegram Bot Plugin for Claude Code

A comprehensive plugin for building production-ready Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x).

## Features

- **telegram-bot**: Build Telegram bots with async/await patterns
- **security-audit**: OWASP-aligned security review
- **deployment-guide**: Production deployment with Docker, webhooks, cloud
- **bot-template**: Generate bot boilerplate code
- **commit**: Git commit helper with conventional commits
- **code-review**: Code quality and security review

## Installation

### From Marketplace

```bash
/plugin install telegram-bot@claude-community
```

### From Local Directory

```bash
claude --plugin-dir ./telegram-bot-plugin
```

### From Git Repository

```bash
/plugin add https://github.com/inyogeshwar/telegram-bot-framework
```

## Usage

After installation, use the skills with namespaced commands:

```
/telegram-bot:telegram-bot    # Build Telegram bots
/telegram-bot:security-audit  # Audit code security
/telegram-bot:deployment-guide # Deploy to production
/telegram-bot:bot-template    # Generate bot boilerplate
/telegram-bot:commit          # Create git commit
/telegram-bot:code-review     # Review code quality
```

## Skills

### telegram-bot
Build Telegram bots with python-telegram-bot v20+ using async/await patterns.

### security-audit
Audit Telegram bot code for vulnerabilities following OWASP guidelines.

### deployment-guide
Deploy Telegram bots to production with Docker, webhooks, and cloud platforms.

### bot-template
Generate production-quality Telegram bot boilerplate code.

### commit
Create a git commit with a descriptive message.

### code-review
Review code changes for quality, security, and best practices.

## Documentation

- [Documentation](docs/README.md)
- [Security Audit](docs/16-security-audit.md)
- [Complete Reference](docs/COMPREHENSIVE-REFERENCE.md)
- [Examples](examples/)

## License

MIT License

## Author

Yogeshwar Kumar — [@inyogeshwar](https://github.com/inyogeshwar)
