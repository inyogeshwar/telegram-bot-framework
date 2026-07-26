---
name: bot-template
description: Generate production-quality Telegram bot boilerplate code
license: MIT
compatibility: opencode
metadata:
  audience: developers
  type: template
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

## Template Structure

```python
#!/usr/bin/env python3
"""Bot Name — Description."""

from __future__ import annotations
import logging
import os
import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello!")

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN not set.")
        sys.exit(1)
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
```
