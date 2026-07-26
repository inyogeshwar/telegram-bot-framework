# Python Telegram Bot v21.x API Reference

## Quick Reference

### Application Setup
```python
from telegram.ext import ApplicationBuilder

app = ApplicationBuilder().token(TOKEN).build()
```

### Handler Types
| Handler | Use Case |
|---------|----------|
| `CommandHandler` | /commands |
| `MessageHandler` | Text, photos, etc. |
| `CallbackQueryHandler` | Inline button presses |
| `InlineQueryHandler` | Inline queries |
| `PreCheckoutQueryHandler` | Payment pre-checkout |
| `ConversationHandler` | Multi-step dialogs |
| `JobQueue` | Scheduled tasks |

### Filters
| Filter | Description |
|--------|-------------|
| `filters.TEXT` | Text messages |
| `filters.COMMAND` | Commands |
| `filters.PHOTO` | Photos |
| `filters.VIDEO` | Videos |
| `filters.Document.ALL` | Documents |
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | New members |

### Context Methods
```python
context.bot.send_message(chat_id, text)
context.bot.send_photo(chat_id, photo)
context.bot.send_document(chat_id, document)
context.job_queue.run_once(callback, when)
context.user_data[key] = value
context.chat_data[key] = value
```

### Update Properties
```python
update.message.text
update.message.from_user.id
update.callback_query.data
update.inline_query.query
```

## References
- [Official PTB Docs](https://docs.python-telegram-bot.org)
- [Bot API Reference](https://core.telegram.org/bots/api)
