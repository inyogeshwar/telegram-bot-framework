# Telegram Bot Development - Core Principles

## Framework: python-telegram-bot v20+
- Always use async/await patterns
- Use ApplicationBuilder, not deprecated Updater
- Handle errors with error_handler decorated handlers
- Include logging in all modules

## Code Style
- PEP 8 compliant
- Type hints on all functions (PEP 484)
- Docstrings on public functions
- Max line length: 88 characters (ruff default)

## Security First
- Never hardcode tokens
- Use environment variables or .env files
- Validate user input before processing
- Implement rate limiting
- Follow OWASP guidelines for webhooks
