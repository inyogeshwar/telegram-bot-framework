# Telegram Bot Framework — Claude Code Instructions

## Repository Purpose
This repository is a comprehensive developer handbook for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x). It contains documentation, examples, and AI agent configurations.

## Key Files
- `docs/` — 21-chapter developer handbook
- `docs/COMPREHENSIVE-REFERENCE.md` — Complete functions reference (1900+ lines)
- `examples/` — 8 production-quality bot examples
- `templates/` — Bot code templates

## Code Standards
- Always use `python-telegram-bot` v20+ (async/await patterns)
- Use PEP 484 type hints throughout
- Include error handling and logging
- Follow PEP 8 style guidelines
- Use `ApplicationBuilder` pattern, not deprecated `Updater`

## Common Patterns
```python
# Application setup
from telegram.ext import ApplicationBuilder

application = ApplicationBuilder().token(token).build()

# Handler registration
from telegram.ext import CommandHandler, MessageHandler, filters

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Running
application.run_polling(drop_pending_updates=True)
```

## Handler Signature
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")
```

## Security Rules
- Never hardcode tokens or secrets
- Use environment variables for configuration
- Validate all user input
- Implement rate limiting
- Follow OWASP guidelines

## Documentation Style
- Use Markdown format
- Include code examples with type hints
- Provide both simple and advanced examples
- Reference official PTB documentation

## Available Skills

### /telegram-bot
Build Telegram bots with python-telegram-bot v20+ using async/await patterns.

### /security-audit
Audit Telegram bot code for vulnerabilities following OWASP guidelines.

### /deployment-guide
Deploy Telegram bots to production with Docker, webhooks, and cloud platforms.

### /bot-template
Generate production-quality Telegram bot boilerplate code.

### /commit
Create a git commit with a descriptive message.

### /code-review
Review code changes for quality, security, and best practices.

## Quick Reference

### Essential Imports
```python
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
```

### Common Filters
```python
filters.TEXT          # Text messages
filters.COMMAND      # Commands
filters.PHOTO        # Photos
filters.VIDEO        # Videos
filters.Document.ALL # Documents
```

### Keyboard Types
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import ReplyKeyboardRemove, ForceReply
```

## References
- [Official PTB Docs](https://docs.python-telegram-bot.org)
- [Bot API Reference](https://core.telegram.org/bots/api)
- [Security Audit](docs/16-security-audit.md)
- [Complete Reference](docs/COMPREHENSIVE-REFERENCE.md)
