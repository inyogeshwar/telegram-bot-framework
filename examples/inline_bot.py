#!/usr/bin/env python3
"""Inline Bot — inline query mode example.

This bot responds to inline queries with search results.
Users can type @yourbot <query> in any chat to use it.

Usage:
    1. Set BOT_TOKEN environment variable
    2. Enable inline mode via @BotFather
    3. Run: python inline_bot.py
    4. Type @yourbot <query> in any Telegram chat
"""

from __future__ import annotations

import logging
import os
import sys

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    InlineQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Sample data for demonstration
SAMPLE_RESPONSES = {
    "hello": "Hello! How can I help you?",
    "help": "Type a query to get results.",
    "info": "This is an inline bot example.",
    "joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
}


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries."""
    query = update.inline_query.query.lower()

    if not query:
        results = [
            InlineQueryResultArticle(
                id="1",
                title="Type something",
                input_message_content=InputTextMessageContent(
                    "Type a query after the bot name!"
                ),
                description="Enter a search term",
            )
        ]
    else:
        results = []
        for key, response in SAMPLE_RESPONSES.items():
            if query in key or key in query:
                results.append(
                    InlineQueryResultArticle(
                        id=key,
                        title=key.title(),
                        input_message_content=InputTextMessageContent(response),
                        description=response[:50],
                    )
                )

        if not results:
            results = [
                InlineQueryResultArticle(
                    id="no_results",
                    title=f"No results for '{query}'",
                    input_message_content=InputTextMessageContent(
                        f"No results found for: {query}"
                    ),
                    description="Try a different query",
                )
            ]

    await update.inline_query.answer(results, cache_time=300, is_personal=True)


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

    application.add_handler(InlineQueryHandler(inline_query))
    application.add_error_handler(error_handler)

    logger.info("Inline Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
