---
name: telegram-bot
description: Build Telegram bots with python-telegram-bot v20+ using async/await patterns
license: MIT
compatibility: opencode
metadata:
  audience: developers
  library: python-telegram-bot
  version: "21"
---

## What I do

- Guide Telegram bot development with python-telegram-bot v20+/v21.x
- Provide correct async/await patterns with type hints
- Reference official PTB documentation and Bot API
- Ensure error handling and logging in all examples

## When to use me

Use this skill when building, debugging, or reviewing Telegram bot code.
Always use async/await, PEP 484 type hints, and ApplicationBuilder pattern.

## Key Patterns

```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")

application = ApplicationBuilder().token(token).build()
application.add_handler(CommandHandler("start", handler))
application.run_polling(drop_pending_updates=True)
```

## Rules

1. Never use deprecated `Updater` pattern
2. Always include error handler
3. Use `ContextTypes.DEFAULT_TYPE` for type hints
4. Validate user input
5. Use environment variables for tokens
