#!/usr/bin/env python3
"""Conversation Bot Template — multi-step dialog example."""

from __future__ import annotations

import logging
import os
import sys

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# States
STATE_ONE, STATE_TWO = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation."""
    if not update.message:
        return ConversationHandler.END
    await update.message.reply_text("Enter your name:")
    return STATE_ONE


async def state_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle first state."""
    if not update.message or not update.message.text:
        return ConversationHandler.END
    if context.user_data is None:
        context.user_data = {}
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your age:")
    return STATE_TWO


async def state_two(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle second state."""
    if not update.message or not update.message.text:
        return ConversationHandler.END
    if context.user_data is None:
        context.user_data = {}
    context.user_data["age"] = update.message.text
    await update.message.reply_text(
        f"Name: {context.user_data.get('name', '')}\nAge: {context.user_data.get('age', '')}"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    if not update.message:
        return ConversationHandler.END
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATE_ONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, state_one)],
            STATE_TWO: [MessageHandler(filters.TEXT & ~filters.COMMAND, state_two)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
