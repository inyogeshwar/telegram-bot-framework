# Add Handler

Adds a new handler to an existing Telegram bot.

## Instructions

1. Ask user for:
   - Handler type (command, message, callback, etc.)
   - Trigger pattern/command name
   - Handler function name
   - Response message/action

2. Generate handler code with:
   - Proper async function signature
   - Type hints
   - Error handling
   - Logging

3. Add handler to bot.py using proper registration method

## Handler Types

### Command Handler
```python
async def command_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /command_name."""
    await update.message.reply_text("Response")


application.add_handler(CommandHandler("command_name", command_name))
```

### Message Handler
```python
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages matching filter."""
    await update.message.reply_text("Response")


application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
)
```

### Callback Query Handler
```python
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Updated")


application.add_handler(CallbackQueryHandler(callback_handler))
```

### Conversation Handler
```python
from telegram.ext import ConversationHandler

FIRST, SECOND = range(2)


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation."""
    await update.message.reply_text("Enter first value:")
    return FIRST


async def first_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process first step."""
    context.user_data["first"] = update.message.text
    await update.message.reply_text("Enter second value:")
    return SECOND


async def second_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process second step."""
    first = context.user_data["first"]
    second = update.message.text
    await update.message.reply_text(f"Result: {first} + {second}")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_conversation)],
    states={
        FIRST: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_step)],
        SECOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_step)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
application.add_handler(conv_handler)
```

## Code Quality Requirements
- Include type hints
- Add docstrings
- Implement error handling
- Add logging
- Follow PEP 8
