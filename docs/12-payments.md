# Chapter 12: Payments & Telegram Stars

## Overview

Telegram provides a built-in payment system that allows bots to sell digital goods and services directly inside chats. The system supports **Telegram Stars** — a virtual currency users purchase with real money — as well as traditional payment providers like Stripe.

### Key Concepts

| Concept | Description |
|---|---|
| **Telegram Stars** | Virtual currency users buy with real money; bots receive Stars for digital goods |
| **Payment Providers** | Third-party processors (e.g. Stripe) that handle real-money transactions |
| **Invoice** | A payment request sent by the bot to a user |
| **Pre-checkout** | Server-side confirmation step the bot must handle within 10 seconds |
| **Paid Media** | Photos, videos, or live photos sold for Stars |

### Use Cases

- Selling digital content (e-books, courses, media)
- In-app purchases and microtransactions
- Subscription-based services
- Paid access to exclusive groups or channels

---

## Telegram Stars

### What They Are

Telegram Stars are a virtual currency native to the Telegram ecosystem. Users purchase Stars with real money through their device's app store. Bots can accept Stars as payment for digital goods and services.

### How Stars Work

1. **User buys Stars** — Users purchase Stars via in-app purchase on iOS or Android.
2. **User pays bot** — Stars are transferred from the user to the bot when purchasing digital goods.
3. **Bot receives Stars** — The bot owner accumulates Stars in their balance.
4. **Conversion** — Stars can be converted to real currency or used to pay other bots for services.

### Star Amounts

Star-denominated amounts use a two-part representation:

| Field | Type | Description |
|---|---|---|
| `amount` | `int` | Whole Star units |
| `nanostar_amount` | `int` | Fractional part in nanostars (1 Star = 1,000,000,000 nanostars) |

For example, 1.5 Stars is represented as `amount=1, nanostar_amount=500000000`.

---

## sendInvoice

The `sendInvoice` method sends a payment request to a user or channel.

### Required Parameters

| Parameter | Type | Description |
|---|---|---|
| `chat_id` | `int \| str` | Target chat ID or username |
| `title` | `str` | Product name (1-32 characters) |
| `description` | `str` | Product description (1-255 characters) |
| `payload` | `str` | Bot-defined order identifier (1-128 bytes, no spaces for private chats) |
| `provider_token` | `str` | Payment provider token from BotFather (empty string for Stars) |
| `currency` | `str` | ISO 4217 currency code (e.g. `"USD"`, `"XTR"` for Stars) |
| `prices` | `list[LabeledPrice]` | Price breakdown |

### Optional Parameters

| Parameter | Type | Description |
|---|---|---|
| `max_tip_amount` | `int` | Maximum tip amount allowed |
| `suggested_tip_amounts` | `list[int]` | Suggested tip amounts (0-4 items) |
| `provider_data` | `str` | JSON string with provider-specific data |
| `photo_url` | `str` | URL of the product photo |
| `photo_size` | `int` | Photo size in bytes |
| `photo_width` | `int` | Photo width in pixels |
| `photo_height` | `int` | Photo height in pixels |
| `need_name` | `bool` | Request recipient's full name |
| `need_phone_number` | `bool` | Request recipient's phone number |
| `need_email` | `bool` | Request recipient's email |
| `need_shipping_address` | `bool` | Request recipient's shipping address |
| `send_email_to_provider` | `bool` | Send email to the payment provider |
| `is_flexible` | `bool` | True if the final price depends on shipping |
| `start_parameter` | `str` | Unique deep-link parameter for public channels |

---

## LabeledPrice

Each element in the `prices` list is a `LabeledPrice` object representing a line item.

```python
from telegram import LabeledPrice

prices = [
    LabeledPrice(label="Subtotal", amount=999),  # $9.99
    LabeledPrice(label="Tax", amount=80),  # $0.80
    LabeledPrice(label="Discount", amount=-200),  # -$2.00
]
# Total: $8.79
```

| Field | Type | Description |
|---|---|---|
| `label` | `str` | Description of the price part (e.g. "Subtotal", "Tax") |
| `amount` | `int` | Price in the **smallest currency unit** (cents for USD, pence for GBP) |

> [!NOTE]
> Amounts are always integers. For USD, `999` means $9.99. For Telegram Stars, `amount` is the number of whole Stars.

---

## Payment Flow

The complete payment lifecycle proceeds through these stages:

```
┌─────────────┐     sendInvoice      ┌──────────────┐
│     Bot      │ ──────────────────▶  │     User      │
│              │                      │               │
│              │  ◀── user taps Pay   │               │
│              │                      │               │
│  (shipping)  │  ◀── shipping_query  │               │  (optional)
│              │  ─── answerShipping  │               │
│              │                      │               │
│              │  ◀── pre_checkout    │               │
│              │  ─── answerPreCheck  │               │
│              │                      │               │
│  successful  │  ◀── successful_     │               │
│  _payment    │      payment message │               │
└─────────────┘                      └──────────────┘
```

### Step-by-Step

1. **Bot sends invoice** — Use `sendInvoice` with product details and pricing.
2. **User taps "Pay"** — Telegram displays a payment form.
3. **(Optional) Shipping** — If `is_flexible=True`, a `ShippingQuery` is sent first.
4. **Pre-checkout** — A `PreCheckoutQuery` is sent. The bot **must** respond within **10 seconds** or the payment fails.
5. **Payment success** — The user's chat receives a `successful_payment` message.

> [!IMPORTANT]
> The pre-checkout response has a strict 10-second deadline. Always respond immediately and process asynchronously if needed.

---

## PreCheckoutQueryHandler

Handle pre-checkout confirmation to validate the order before payment is processed.

### Required Response

Use `answerPreCheckoutQuery` to accept or reject:

```python
from telegram import Update, PreCheckoutQuery
from telegram.ext import ContextTypes


async def precheckout_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle PreCheckoutQuery — must respond within 10 seconds."""
    query: PreCheckoutQuery = update.pre_checkout_query

    # Validate the order
    if query.invoice_payload != "valid_order_123":
        await query.answer(ok=False, error_message="Invalid order. Please restart.")
        return

    if query.total_amount > 5000:
        await query.answer(ok=False, error_message="Order total exceeds limit.")
        return

    # Accept the payment
    await query.answer(ok=True)
```

### PreCheckoutQuery Fields

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique query identifier |
| `from` | `User` | User who initiated the payment |
| `currency` | `str` | Currency code |
| `total_amount` | `int` | Total amount charged |
| `invoice_payload` | `str` | Bot-defined payload from `sendInvoice` |
| `shipping_option_id` | `str \| None` | Selected shipping option ID |
| `order_info` | `OrderInfo \| None` | Order details (name, email, phone, address) |

### Error Messages

When rejecting a payment, provide a user-facing `error_message` (1-256 characters):

```python
await query.answer(ok=False, error_message="Sorry, this item is no longer available.")
```

---

## ShippingQueryHandler

For invoices with `is_flexible=True`, the bot must handle shipping queries to calculate final prices.

### Defining Shipping Options

```python
from telegram import (
    Update,
    LabeledPrice,
    ShippingOption,
    ShippingQuery,
)
from telegram.ext import ContextTypes


async def shipping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ShippingQuery for flexible-price invoices."""
    query: ShippingQuery = update.shipping_query

    # Define available shipping options
    options = [
        ShippingOption(
            id="standard",
            title="Standard Delivery",
            prices=[LabeledPrice(label="Standard", amount=500)],
        ),
        ShippingOption(
            id="express",
            title="Express Delivery",
            prices=[LabeledPrice(label="Express", amount=1500)],
        ),
    ]

    # Validate shipping address if needed
    if query.shipping_address and query.shipping_address.country_code != "US":
        await query.answer(
            ok=False,
            error_message="We only ship within the United States.",
        )
        return

    await query.answer(ok=True, shipping_options=options)
```

### ShippingQuery Fields

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique query identifier |
| `from` | `User` | User who initiated the payment |
| `invoice_payload` | `str` | Bot-defined payload |
| `shipping_address` | `ShippingAddress` | User-provided shipping address |

---

## Subscriptions

Telegram supports recurring payments through subscription-based invite links.

### Creating Subscription Links

Create a subscription with `subscription_period` and `subscription_price` parameters. This is configured through BotFather or the Bot API for generating subscription invite links.

| Parameter | Description |
|---|---|
| `subscription_period` | Billing period in seconds (minimum 2,592,000 = 30 days) |
| `subscription_price` | Price per period in Stars |

### Handling Subscription State Changes

When a subscription state changes, the bot receives a `BotSubscriptionUpdated` update:

```python
from telegram import Update, BotSubscriptionUpdated
from telegram.ext import ContextTypes

import logging

logger = logging.getLogger(__name__)


async def subscription_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle subscription state changes."""
    subscription: BotSubscriptionUpdated = update.bot_subscription_updated

    status = subscription.subscription.status

    if status == "active":
        logger.info("Subscription activated for user %s", subscription.user.id)
        # Grant access

    elif status == "canceled":
        logger.info("Subscription canceled for user %s", subscription.user.id)
        # Revoke access

    elif status == "failed":
        logger.warning("Subscription payment failed for user %s", subscription.user.id)
        # Notify user, revoke access
```

### Subscription States

| State | Description |
|---|---|
| `active` | Subscription is active and payments are being processed |
| `canceled` | User or system canceled the subscription |
| `failed` | Recurring payment failed |

---

## Refunds

Bot owners can issue refunds for Star payments using `refundPayment`.

```python
from telegram import Update
from telegram.ext import ContextTypes

import logging

logger = logging.getLogger(__name__)


async def refund_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Issue a refund for a successful Star payment."""
    message = update.message
    if not message or not message.successful_payment:
        return

    payment = message.successful_payment

    if payment.currency != "XTR":
        await message.reply_text("Refunds are only supported for Star payments.")
        return

    try:
        await context.bot.refund_payment(
            user_id=message.from_user.id,
            payment_charge_id=payment.telegram_payment_charge_id,
        )
        await message.reply_text("Your refund has been processed.")
        logger.info(
            "Refund issued to user %s for charge %s",
            message.from_user.id,
            payment.telegram_payment_charge_id,
        )
    except Exception as e:
        logger.error("Refund failed: %s", e)
        await message.reply_text("Failed to process refund. Please contact support.")
```

---

## Paid Media

Sell individual photos, videos, or collections of media for Stars using `sendPaidMedia`.

### sendPaidMedia

| Parameter | Type | Description |
|---|---|---|
| `chat_id` | `int \| str` | Target chat |
| `star_count` | `int` | Price in Stars |
| `media` | `list[InputMedia]` | Array of media to send (1-10 items) |
| `caption` | `str` | Media caption (0-1024 characters) |
| `parse_mode` | `str` | Markdown/HTML parsing mode |
| `payload` | `str` | Bot-defined payload (1-128 characters) |

### Media Types in PaidMedia

| Type | Description |
|---|---|
| `InputMediaPhoto` | Static image (JPEG/PNG) |
| `InputMediaVideo` | Video file |
| `InputMediaLivePhoto` | Live photo (iOS) |
| `InputMediaPreview` | Animation preview for unsupported formats |

### Handling Paid Media Purchases

When a user purchases paid media, the bot receives a `PaidMediaPurchased` update:

```python
from telegram import Update, PaidMediaPurchased
from telegram.ext import ContextTypes

import logging

logger = logging.getLogger(__name__)


async def paid_media_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle PaidMediaPurchased update."""
    purchased: PaidMediaPurchased = update.paid_media_purchased

    payload = purchased.payload
    user_id = purchased.from_user.id
    star_count = purchased.paid_media.stars

    logger.info(
        "User %s purchased paid media (payload=%s, stars=%d)",
        user_id,
        payload,
        star_count,
    )

    # Deliver the content or grant access based on payload
    # e.g., unlock a channel, send a file, etc.
```

---

## Complete Payment Example

A production-ready payment flow with product catalog, shipping, and error handling.

```python
import logging
from typing import Final

from telegram import (
    Update,
    LabeledPrice,
    ShippingOption,
    PreCheckoutQuery,
    ShippingQuery,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN: Final[str] = "YOUR_BOT_TOKEN"
PAYMENT_PROVIDER_TOKEN: Final[str] = "YOUR_STRIPE_PROVIDER_TOKEN"


# ─── Product Catalog ────────────────────────────────────────────

PRODUCTS = {
    "basic": {
        "title": "Basic Plan",
        "description": "Access to basic features for 30 days",
        "price": 499,  # $4.99
    },
    "premium": {
        "title": "Premium Plan",
        "description": "Full access for 30 days",
        "price": 999,  # $9.99
    },
}


# ─── Command Handlers ───────────────────────────────────────────


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display available products."""
    keyboard = [
        [{"text": f"Buy {p['title']} — ${p['price'] / 100:.2f}", "pay": True}]
        for p in PRODUCTS.values()
    ]
    await update.message.reply_text(
        "Welcome! Choose a plan to purchase:",
        reply_markup={"inline_keyboard": keyboard},
    )


# ─── Invoice Creation ───────────────────────────────────────────


async def handle_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout query from Stripe."""
    query: PreCheckoutQuery = update.pre_checkout_query

    # Validate the payload
    if query.invoice_payload not in PRODUCTS:
        await query.answer(ok=False, error_message="Unknown product.")
        return

    product = PRODUCTS[query.invoice_payload]
    if query.total_amount != product["price"]:
        await query.answer(ok=False, error_message="Price mismatch.")
        return

    logger.info(
        "Pre-checkout approved for user %s: %s",
        query.from_user.id,
        query.invoice_payload,
    )
    await query.answer(ok=True)


# ─── Shipping (Flexible Pricing) ───────────────────────────────


async def shipping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shipping queries for flexible-price invoices."""
    query: ShippingQuery = update.shipping_query

    options = [
        ShippingOption(
            id="email",
            title="Email Delivery (Free)",
            prices=[LabeledPrice(label="Email", amount=0)],
        ),
        ShippingOption(
            id="usb",
            title="USB Drive (+$5.00)",
            prices=[LabeledPrice(label="USB", amount=500)],
        ),
    ]

    await query.answer(ok=True, shipping_options=options)


# ─── Successful Payment ────────────────────────────────────────


async def successful_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle successful payment confirmation."""
    payment = update.message.successful_payment

    logger.info(
        "Payment received from %s: %s %s (charge: %s)",
        update.effective_user.id,
        payment.total_amount,
        payment.currency,
        payment.telegram_payment_charge_id,
    )

    # Grant access, send confirmation, etc.
    await update.message.reply_text(
        f"Payment of {payment.total_amount} {payment.currency} received! "
        "Your access has been activated."
    )


# ─── Application Setup ─────────────────────────────────────────


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(PreCheckoutQueryHandler(handle_checkout))
    app.add_handler(ShippingQueryHandler(shipping_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    logger.info("Bot started polling.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

---

## Error Handling

Always implement graceful error handling in payment flows:

| Scenario | Handling |
|---|---|
| Pre-checkout timeout (>10s) | Bot must respond within 10 seconds; process heavy validation asynchronously |
| Provider token invalid | Verify token with BotFather before deployment |
| Currency mismatch | Always verify `currency` in pre-checkout matches expected value |
| Duplicate payment | Check `invoice_payload` idempotency before granting access |
| Refund failure | Log error, provide manual support path |

> [!WARNING]
> Never grant access or deliver goods before receiving a `successful_payment` message. The `pre_checkout_query` confirmation only indicates the payment was initiated, not completed.

---

## Best Practices

1. **Idempotency** — Store `invoice_payload` in a database and check for duplicates before granting access.
2. **Webhook mode** — Prefer webhooks over polling for production payment bots to minimize latency.
3. **Payload validation** — Always verify `invoice_payload` in `pre_checkout_query` matches expected orders.
4. **Amount verification** — Compare `total_amount` in pre-checkout against your calculated total.
5. **Logging** — Log all payment events with user ID, charge ID, and amounts for audit trails.
6. **User feedback** — Always confirm successful payments with a clear message and next steps.
