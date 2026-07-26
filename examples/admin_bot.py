#!/usr/bin/env python3
"""Admin Bot — group management and moderation.

This bot provides admin features for Telegram groups:
- Ban/unban users
- Mute/unmute users
- Delete messages
- Welcome messages
- Anti-spam

Usage:
    1. Set BOT_TOKEN environment variable
    2. Add bot to a group as admin
    3. Run: python admin_bot.py
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
    """Handle /start command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Admin Bot\n\n"
        "Commands:\n"
        "/ban - Ban a user (reply to their message)\n"
        "/unban - Unban a user\n"
        "/mute - Mute a user\n"
        "/unmute - Unmute a user\n"
        "/delete - Delete a message (reply to it)\n"
        "/welcome - Set welcome message\n"
        "/help - Show this help"
    )


async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a user from the group."""
    if not update.message:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to ban them.")
        return

    user = update.message.reply_to_message.from_user
    if not user:
        await update.message.reply_text("Cannot identify the user to ban.")
        return

    try:
        await update.message.chat.ban_member(user.id)
        await update.message.reply_text(
            f"Banned {user.mention_html()}.", parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Failed to ban user: %s", e)
        await update.message.reply_text("Failed to ban user. Am I an admin?")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban a user from the group."""
    if not update.message:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to unban them.")
        return

    user = update.message.reply_to_message.from_user
    if not user:
        await update.message.reply_text("Cannot identify the user to unban.")
        return

    try:
        await update.message.chat.unban_member(user.id)
        await update.message.reply_text(
            f"Unbanned {user.mention_html()}.", parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Failed to unban user: %s", e)
        await update.message.reply_text("Failed to unban user.")


async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mute a user in the group."""
    if not update.message:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to mute them.")
        return

    user = update.message.reply_to_message.from_user
    if not user:
        await update.message.reply_text("Cannot identify the user to mute.")
        return

    try:
        from telegram import ChatPermissions

        permissions = ChatPermissions(can_send_messages=False)
        await update.message.chat.restrict_member(user.id, permissions)
        await update.message.reply_text(
            f"Muted {user.mention_html()}.", parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Failed to mute user: %s", e)
        await update.message.reply_text("Failed to mute user. Am I an admin?")


async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unmute a user in the group."""
    if not update.message:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to unmute them.")
        return

    user = update.message.reply_to_message.from_user
    if not user:
        await update.message.reply_text("Cannot identify the user to unmute.")
        return

    try:
        from telegram import ChatPermissions

        permissions = ChatPermissions(can_send_messages=True)
        await update.message.chat.restrict_member(user.id, permissions)
        await update.message.reply_text(
            f"Unmuted {user.mention_html()}.", parse_mode="HTML"
        )
    except Exception as e:
        logger.error("Failed to unmute user: %s", e)
        await update.message.reply_text("Failed to unmute user.")


async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete the replied-to message."""
    if not update.message:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to delete it.")
        return

    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        logger.error("Failed to delete message: %s", e)
        await update.message.reply_text("Failed to delete message.")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message to new members."""
    if not update.message:
        return
    if not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.is_bot:
            continue
        await update.message.reply_text(
            f"Welcome {user.mention_html()}! "
            "I'm the admin bot. Use /help to see available commands.",
            parse_mode="HTML",
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help text."""
    if not update.message:
        return
    await update.message.reply_text(
        "Admin Bot Commands:\n\n"
        "/ban - Ban a user (reply to their message)\n"
        "/unban - Unban a user\n"
        "/mute - Mute a user\n"
        "/unmute - Unmute a user\n"
        "/delete - Delete a message (reply to it)\n"
        "/help - Show this help"
    )


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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("delete", delete_message))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )

    application.add_error_handler(error_handler)

    logger.info("Admin Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
