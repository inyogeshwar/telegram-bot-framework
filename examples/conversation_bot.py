#!/usr/bin/env python3
"""Conversation Bot — multi-step dialog with ConversationHandler.

This bot demonstrates ConversationHandler for building multi-step workflows:
- User registration flow
- State management
- Fallback handling
- Timeout handling

Usage:
    1. Set BOT_TOKEN environment variable
    2. Run: python conversation_bot.py
    3. Send /register to start the registration flow
"""

from __future__ import annotations

import logging
import os
import sys

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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

# Conversation states
NAME, AGE, LOCATION = range(3)

# Reply keyboards
reply_keyboard = [["Yes", "No"]]
markup = ReplyKeyboardMarkup(
    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the registration conversation."""
    await update.message.reply_text(
        "Let's get you registered!\n\nWhat's your name?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store name and ask for age."""
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Nice to meet you, {update.message.text}!\n\nHow old are you?"
    )
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store age and ask for location."""
    text = update.message.text
    if not text.isdigit() or int(text) < 0 or int(text) > 150:
        await update.message.reply_text("Please enter a valid age (0-150).")
        return AGE

    context.user_data["age"] = int(text)
    await update.message.reply_text("Great!\n\nWhere are you located? (City, Country)")
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store location and complete registration."""
    context.user_data["location"] = update.message.text

    # Summary
    name = context.user_data.get("name", "Unknown")
    age = context.user_data.get("age", "Unknown")
    location = context.user_data.get("location", "Unknown")

    await update.message.reply_text(
        "Registration complete!\n\n"
        f"Name: {name}\n"
        f"Age: {age}\n"
        f"Location: {location}\n\n"
        "Thank you for registering!",
        reply_markup=ReplyKeyboardRemove(),
    )

    logger.info("User registered: %s", context.user_data)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Registration cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle conversation timeout."""
    await update.message.reply_text(
        "Registration timed out. Please start again with /register.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_registration)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        timeout=300,  # 5 minutes
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    logger.info("Conversation Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
