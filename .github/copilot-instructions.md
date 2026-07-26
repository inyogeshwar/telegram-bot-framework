# Telegram Bot Framework — GitHub Copilot Instructions

## Project Context
This repository is a comprehensive developer handbook for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x).

## Code Standards
- Use python-telegram-bot v20+ (async/await patterns)
- PEP 484 type hints throughout
- Error handling and logging in all examples
- PEP 8 compliant code style

## Key Imports
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
```

## Common Pattern
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")
```

## Security
- Never hardcode tokens
- Use environment variables
- Validate user input
- Implement rate limiting
