---
description: Generate production-quality Telegram bot boilerplate code. Use when creating new bot projects or need a starting point.
disable-model-invocation: true
allowed-tools: Read Write
---

## What I do

- Generate bot boilerplate with proper structure
- Include async patterns, error handling, and logging
- Follow PEP 8 and PEP 484 standards
- Provide templates for common bot types

## When to use me

Use this skill when creating new bot projects or need a starting point.

## Templates Available

1. **Basic Bot** — `templates/bot-template.py`
2. **Conversation Bot** — `templates/conversation-template.py`
3. **Webhook Bot** — `templates/webhook-template.py`

## Basic Bot Template

```python
#!/usr/bin/env python3
"""Bot Name — Description."""

from __future__ import annotations

import logging
import os
import sys

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text("Help text here")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo messages."""
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_error_handler(error_handler)

    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
```

## Usage

1. Copy the template
2. Replace `Bot Name` and `Description`
3. Add your handlers
4. Set `BOT_TOKEN` environment variable
5. Run: `python bot.py`
