---
name: bot-template
description:
  Provides templates and scaffolding for creating new Telegram bots with
  proper structure, configuration, and best practices. Use when the user
  asks to "create bot", "scaffold bot", or "new bot project".
disable-model-invocation: true
---

# Bot Template Instructions

You are a bot scaffolding specialist. When this skill is invoked, create a complete bot project structure.

## Project Structure

```
bot_name/
├── bot.py              # Main bot file
├── config.py           # Configuration module
├── requirements.txt    # Dependencies
├── .env.example        # Environment variables template
├── README.md           # Setup instructions
└── tests/
    ├── __init__.py
    └── test_bot.py     # Basic tests
```

## Templates

### bot.py Template
```python
import logging
from os import getenv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
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

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hello! I'm your Telegram bot.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help message here.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
```

### config.py Template
```python
from os import getenv
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str
    database_url: str = "sqlite:///data/bot.db"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            bot_token=getenv("BOT_TOKEN", ""),
            database_url=getenv("DATABASE_URL", "sqlite:///data/bot.db"),
            log_level=getenv("LOG_LEVEL", "INFO"),
        )
```

## Scripts

- `scripts/scaffold.py` — Creates new bot project structure
- `scripts/setup.py` — Initializes project dependencies

## Assets

- `assets/requirements.txt` — Base requirements template
- `assets/.env.example` — Environment variables template
- `assets/README.md` — Documentation template

## Instructions

1. Ask user for bot name and description
2. Create directory structure using scaffold script
3. Generate all template files
4. Initialize git repository
5. Provide setup instructions

## Resources

- Examples: `examples/` directory
- Templates: `templates/` directory
