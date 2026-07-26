#!/usr/bin/env python3
"""AI Chatbot — production example with OpenAI integration.

This bot uses the OpenAI API to generate intelligent responses.
It demonstrates async architecture, error handling, and rate limiting.

Usage:
    1. Set BOT_TOKEN and OPENAI_API_KEY environment variables
    2. Run: python ai_chatbot.py
    3. Send messages to your bot — it will respond using GPT
"""

from __future__ import annotations

import logging
import os
import sys
from collections import defaultdict
from time import time

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

# Rate limiting: max messages per user per minute
RATE_LIMIT = 10
RATE_LIMIT_WINDOW = 60  # seconds


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self) -> None:
        self._timestamps: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limit."""
        now = time()
        cutoff = now - RATE_LIMIT_WINDOW
        self._timestamps[user_id] = [t for t in self._timestamps[user_id] if t > cutoff]
        if len(self._timestamps[user_id]) >= RATE_LIMIT:
            return False
        self._timestamps[user_id].append(now)
        return True


rate_limiter = RateLimiter()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not update.message or not update.effective_user:
        return
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! I'm an AI-powered chatbot. "
        "Send me any message and I'll respond using GPT."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Send me a message and I'll respond using AI.\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/clear - Clear conversation history"
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history for this user."""
    if not update.message:
        return
    if context.user_data is None:
        context.user_data = {}
    context.user_data.clear()
    await update.message.reply_text("Conversation history cleared.")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user message and generate AI response."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id if update.effective_user else 0

    if not rate_limiter.is_allowed(user_id):
        await update.message.reply_text(
            "Rate limit exceeded. Please wait a moment and try again."
        )
        return

    if context.user_data is None:
        context.user_data = {}

    user_text = update.message.text

    # Initialize conversation history
    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append({"role": "user", "content": user_text})

    # Keep only last 20 messages
    if len(context.user_data["history"]) > 20:
        context.user_data["history"] = context.user_data["history"][-20:]

    await update.message.chat.send_action("typing")

    try:
        import openai

        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            *context.user_data["history"],
        ]

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )

        assistant_text = response.choices[0].message.content or "No response generated."
        context.user_data["history"].append(
            {"role": "assistant", "content": assistant_text}
        )

        await update.message.reply_text(assistant_text)

    except ImportError:
        await update.message.reply_text(
            "OpenAI library not installed. Run: pip install openai"
        )
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        await update.message.reply_text(
            "Sorry, I encountered an error processing your request."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    if not openai_key:
        logger.warning("OPENAI_API_KEY not set. AI responses will be disabled.")

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    application.add_error_handler(error_handler)

    logger.info("AI Chatbot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
