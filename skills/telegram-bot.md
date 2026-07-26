# Telegram Bot Development Skill

## Overview
This skill provides guidance for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x).

## When to Use
- Building Telegram bots
- Implementing bot handlers
- Working with Telegram API
- Bot deployment and testing

## Key Patterns

### Application Setup
```python
from telegram.ext import ApplicationBuilder

application = ApplicationBuilder().token(token).build()
```

### Handler Registration
```python
from telegram.ext import CommandHandler, MessageHandler, filters

application.add_handler(CommandHandler("start", start_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
```

### Async Handler
```python
from telegram import Update
from telegram.ext import ContextTypes

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")
```

## Common Tasks

### Send Message
```python
await context.bot.send_message(chat_id=chat_id, text="Hello!")
```

### Send Photo
```python
await context.bot.send_photo(chat_id=chat_id, photo=open("photo.jpg", "rb"))
```

### Reply to Message
```python
await update.message.reply_text("Reply text")
```

## Best Practices
1. Always use async/await
2. Include type hints
3. Add error handling
4. Use logging
5. Validate user input
6. Implement rate limiting

## References
- [PTB Documentation](https://docs.python-telegram-bot.org)
- [Bot API Reference](https://core.telegram.org/bots/api)
- [Examples](../../examples/)
