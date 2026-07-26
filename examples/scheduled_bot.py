#!/usr/bin/env python3
"""Scheduled Messages Bot — JobQueue example.

This bot demonstrates scheduled and recurring tasks:
- Send reminders
- Schedule messages
- Recurring tasks

Usage:
    1. Set BOT_TOKEN environment variable
    2. Run: python scheduled_bot.py
    3. Use /remind to set reminders
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta
from datetime import time as dt_time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Scheduled Messages Bot\n\n"
        "Commands:\n"
        "/remind <minutes> <message> - Set a reminder\n"
        "/daily - Toggle daily greeting\n"
        "/status - Check scheduled jobs"
    )


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a reminder."""
    if not update.message:
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /remind <minutes> <message>")
        return

    try:
        minutes = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Please provide a valid number of minutes.")
        return

    message = " ".join(context.args[1:])
    chat_id = update.effective_chat.id if update.effective_chat else 0

    if not context.job_queue:
        await update.message.reply_text("Job queue is not available.")
        return

    context.job_queue.run_once(
        send_reminder,
        when=timedelta(minutes=minutes),
        data={"chat_id": chat_id, "message": message},
        name=f"reminder_{chat_id}_{datetime.now().timestamp()}",
    )

    await update.message.reply_text(f"Reminder set for {minutes} minutes from now.")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the reminder message."""
    if not context.job or not context.job.data:
        return
    data: dict[str, str | int] = context.job.data  # type: ignore[assignment]
    chat_id = data["chat_id"]
    message = data["message"]

    await context.bot.send_message(chat_id=chat_id, text=f"⏰ Reminder: {message}")
    logger.info("Reminder sent to chat %s", chat_id)


async def daily_greeting(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily greeting to all subscribed chats."""
    if not context.job:
        return
    chat_id = context.job.chat_id
    if not chat_id:
        return
    await context.bot.send_message(
        chat_id=chat_id,
        text="Good morning! Here's your daily update.",
    )


async def toggle_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle daily greeting."""
    if not update.message:
        return
    chat_id = update.effective_chat.id if update.effective_chat else 0

    if not context.job_queue:
        await update.message.reply_text("Job queue is not available.")
        return

    # Check if daily job already exists
    current_jobs = context.job_queue.get_jobs_by_name(f"daily_{chat_id}")

    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
        await update.message.reply_text("Daily greeting disabled.")
    else:
        context.job_queue.run_daily(
            daily_greeting,
            time=dt_time(8, 0),
            chat_id=chat_id,
            name=f"daily_{chat_id}",
        )
        await update.message.reply_text("Daily greeting enabled (8:00 AM).")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show scheduled jobs."""
    if not update.message:
        return
    jobs = context.job_queue.get_jobs_by_name("") if context.job_queue else []

    if not jobs:
        await update.message.reply_text("No scheduled jobs.")
        return

    text = "Scheduled jobs:\n\n"
    for job in jobs:
        text += f"• {job.name}: {job.next_t}\n"

    await update.message.reply_text(text)


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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("remind", remind))
    application.add_handler(CommandHandler("daily", toggle_daily))
    application.add_handler(CommandHandler("status", status))

    application.add_error_handler(error_handler)

    logger.info("Scheduled Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
