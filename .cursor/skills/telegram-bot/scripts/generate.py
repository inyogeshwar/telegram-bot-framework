#!/usr/bin/env python3
"""Generate bot boilerplate code."""

import sys
from pathlib import Path


def create_bot(name: str, description: str = "") -> None:
    """Create a new bot project structure."""
    bot_dir = Path(name)
    bot_dir.mkdir(exist_ok=True)

    # Create main bot file
    bot_py = bot_dir / "bot.py"
    bot_py.write_text(f'''"""
{name} - Telegram Bot
{description}
"""

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
    await update.message.reply_text("Hello! I am {name}.")


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
''')

    # Create requirements.txt
    req_file = bot_dir / "requirements.txt"
    req_file.write_text("python-telegram-bot[job-queue]>=20.0\npython-dotenv>=1.0.0\n")

    # Create .env.example
    env_file = bot_dir / ".env.example"
    env_file.write_text("BOT_TOKEN=your_bot_token_here\n")

    # Create README.md
    readme_file = bot_dir / "README.md"
    readme_file.write_text(f"""# {name}

{description}

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your bot token:
   ```bash
   cp .env.example .env
   ```

3. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

- `/start` - Start the bot
- `/help` - Get help
""")

    print(f"Bot '{name}' created successfully in {bot_dir}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate.py <bot_name> [description]")
        sys.exit(1)

    name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    create_bot(name, description)
