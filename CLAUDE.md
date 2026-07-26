# Telegram Bot Framework — Claude Code Instructions

## Repository Purpose
This repository is a comprehensive developer handbook for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x).

## Key Files
- `docs/` — 21-chapter developer handbook
- `examples/` — Production-quality bot examples
- `skills/` — AI agent skill definitions
- `agents/` — AI agent configurations

## Code Standards
- Always use `python-telegram-bot` v20+ (async/await patterns)
- Use PEP 484 type hints throughout
- Include error handling and logging
- Follow PEP 8 style guidelines

## Common Patterns
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello!")

def main() -> None:
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(drop_pending_updates=True)
```

## Security
- Never hardcode tokens
- Use environment variables
- Validate user input
- Implement rate limiting
