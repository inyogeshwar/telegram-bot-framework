#!/usr/bin/env python3
"""Webhook Bot — production deployment with webhooks.

This bot demonstrates webhook-based deployment using aiohttp.
Suitable for production environments behind a reverse proxy.

Usage:
    1. Set BOT_TOKEN, WEBHOOK_URL, and WEBHOOK_SECRET environment variables
    2. Run: python webhook_bot.py
    3. Bot will set up webhook automatically
"""

from __future__ import annotations

import logging
import os
import sys

from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
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
    await update.message.reply_text("Webhook Bot is running!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo messages."""
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({"status": "healthy"})


async def webhook_handler(request: web.Request) -> web.Response:
    """Handle incoming webhook updates."""
    application = request.app["bot_application"]
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return web.Response()


async def on_startup(application: Application) -> None:  # type: ignore[type-arg]
    """Set up webhook on startup."""
    webhook_url = os.getenv("WEBHOOK_URL")
    webhook_secret = os.getenv("WEBHOOK_SECRET")

    if webhook_url:
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=webhook_secret,
        )
        logger.info("Webhook set to: %s", webhook_url)


async def on_shutdown(application: Application) -> None:  # type: ignore[type-arg]
    """Remove webhook on shutdown."""
    await application.bot.delete_webhook()
    logger.info("Webhook removed.")


def main() -> None:
    """Start the bot with webhook server."""
    token = os.getenv("BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")

    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    if not webhook_url:
        logger.error("WEBHOOK_URL environment variable not set.")
        sys.exit(1)

    # Parse webhook URL
    from urllib.parse import urlparse

    parsed = urlparse(webhook_url)
    host = parsed.hostname or "0.0.0.0"
    port = parsed.port or 8443
    path = parsed.path or "/webhook"

    # Build application
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set up startup/shutdown hooks
    application.post_init = on_startup
    application.post_shutdown = on_shutdown

    # Create aiohttp app
    app = web.Application()
    app["bot_application"] = application
    app.router.add_post(path, webhook_handler)
    app.router.add_get("/health", health)

    logger.info("Starting webhook server on %s:%s%s", host, port, path)
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
