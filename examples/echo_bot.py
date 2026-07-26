#!/usr/bin/env python3
"""Echo Bot — minimal example using python-telegram-bot v21.x.

This bot echoes back any text message it receives.
It demonstrates the basic structure of a PTB v20+ bot.

Usage:
    1. Set BOT_TOKEN environment variable or edit .env file
    2. Run: python echo_bot.py
    3. Send any message to your bot on Telegram
"""

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
    """Handle /start command — send welcome message."""
    if not update.message or not update.effective_user:
        return
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! "
        "I'm an echo bot. Send me any message and I'll repeat it back."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command — send help text."""
    if not update.message:
        return
    await update.message.reply_text(
        "Send me any text message and I'll echo it back.\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user's message back to them."""
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
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
