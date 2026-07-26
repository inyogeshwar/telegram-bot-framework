# Webhook Template

```python
#!/usr/bin/env python3
"""Webhook Bot Template — production deployment example."""

from __future__ import annotations

import logging
import os
import sys

from aiohttp import web
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
    await update.message.reply_text("Webhook bot running!")


async def health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({"status": "healthy"})


async def webhook_handler(request: web.Request) -> web.Response:
    """Handle incoming webhook updates."""
    application = request.app["bot_application"]
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return web.Response()


async def on_startup(application) -> None:
    """Set up webhook on startup."""
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(url=webhook_url)
        logger.info("Webhook set to: %s", webhook_url)


def main() -> None:
    """Start the bot with webhook server."""
    token = os.getenv("BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")

    if not token or not webhook_url:
        logger.error("BOT_TOKEN and WEBHOOK_URL must be set.")
        sys.exit(1)

    from urllib.parse import urlparse

    parsed = urlparse(webhook_url)
    host = parsed.hostname or "0.0.0.0"
    port = parsed.port or 8443
    path = parsed.path or "/webhook"

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.post_init = on_startup

    app = web.Application()
    app["bot_application"] = application
    app.router.add_post(path, webhook_handler)
    app.router.add_get("/health", health)

    logger.info("Starting webhook server on %s:%s%s", host, port, path)
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
```
