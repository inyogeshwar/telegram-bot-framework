# Create Telegram Bot

Creates a new Telegram bot with proper structure and configuration.

## Instructions

1. Ask user for bot name and description
2. Create bot directory with proper structure:
   ```
   bot_name/
   ├── bot.py          # Main bot file
   ├── config.py       # Configuration module
   ├── requirements.txt # Dependencies
   ├── .env.example    # Environment variables template
   └── README.md       # Setup instructions
   ```

3. Generate bot.py with:
   - Async main function
   - Application setup with ApplicationBuilder
   - Basic command handlers (/start, /help)
   - Error handling
   - Logging configuration
   - Type hints on all functions

4. Generate config.py with:
   - Environment variable loading
   - Configuration dataclass
   - Validation

5. Generate requirements.txt with:
   - python-telegram-bot[job-queue]>=20.0
   - python-dotenv (for .env loading)

6. Generate .env.example with:
   - BOT_TOKEN=your_bot_token_here
   - DATABASE_URL=your_database_url

7. Generate README.md with:
   - Bot description
   - Setup instructions
   - Usage examples
   - Environment variables documentation

## Code Template

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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load environment variables
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
