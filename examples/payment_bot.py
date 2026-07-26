#!/usr/bin/env python3
"""Payment Bot — Telegram Stars integration example.

This bot demonstrates Telegram Stars payments:
- Send invoices
- Handle pre-checkout
- Process successful payments

Usage:
    1. Set BOT_TOKEN environment variable
    2. Set up payment provider via @BotFather
    3. Run: python payment_bot.py
    4. Send /buy to test payment flow
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TypedDict

from telegram import (
    LabeledPrice,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)


class ProductDict(TypedDict):
    title: str
    description: str
    price: int
    payload: str


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Product catalog
PRODUCTS: dict[str, ProductDict] = {
    "premium": {
        "title": "Premium Subscription",
        "description": "1 month of premium features",
        "price": 100,  # Stars
        "payload": "premium_month",
    },
    "vip": {
        "title": "VIP Access",
        "description": "Lifetime VIP access",
        "price": 500,
        "payload": "vip_lifetime",
    },
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Payment Bot\n\n"
        "Commands:\n"
        "/buy - View products\n"
        "/buy premium - Buy premium subscription\n"
        "/buy vip - Buy VIP access"
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show products or send invoice."""
    if not update.message:
        return

    args = context.args
    if not args:
        # Show product list
        text = "Available products:\n\n"
        for key, product in PRODUCTS.items():
            text += f"• {product['title']}: {product['price']} Stars\n"
            text += f"  {product['description']}\n"
            text += f"  Use /buy {key} to purchase\n\n"
        await update.message.reply_text(text)
        return

    product_key = args[0].lower()
    if product_key not in PRODUCTS:
        await update.message.reply_text(
            "Unknown product. Use /buy to see available products."
        )
        return

    product = PRODUCTS[product_key]

    try:
        await update.message.reply_invoice(
            title=product["title"],
            description=product["description"],
            payload=product["payload"],
            currency="XTR",  # Telegram Stars
            prices=[LabeledPrice(product["title"], product["price"])],
        )
    except Exception as e:
        logger.error("Failed to send invoice: %s", e)
        await update.message.reply_text("Failed to send payment request.")


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout query."""
    query = update.pre_checkout_query
    if not query:
        return

    if query.invoice_payload not in [p["payload"] for p in PRODUCTS.values()]:
        await query.answer(ok=False, error_message="Invalid product.")
        return

    await query.answer(ok=True)


async def successful_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle successful payment."""
    if not update.message or not update.message.successful_payment:
        return

    payment = update.message.successful_payment
    user = update.effective_user

    logger.info(
        "Payment received: %s Stars from user %s (%s)",
        payment.total_amount,
        user.id if user else "unknown",
        payment.invoice_payload,
    )

    await update.message.reply_text(
        f"Payment successful!\n\n"
        f"Product: {payment.invoice_payload}\n"
        f"Amount: {payment.total_amount} Stars\n\n"
        f"Thank you for your purchase!"
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
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )

    application.add_error_handler(error_handler)

    logger.info("Payment Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
