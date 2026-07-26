# Chapter 13: Mini Apps & Web Apps

## Overview

Telegram Mini Apps (also called Web Apps) are full-featured web applications that run inside Telegram. They provide access to the device's full screen, Telegram user data, and seamless integration with the bot ecosystem.

### What Mini Apps Are

| Aspect | Description |
|---|---|
| **Technology** | Standard HTML, CSS, and JavaScript (any web framework) |
| **Runtime** | Runs in Telegram's built-in browser (WebKit on iOS, Chromium on Android) |
| **User Data** | Access to authenticated user info via the WebApp API |
| **Screen** | Full-screen immersive experience |
| **Backend** | Your own server handles logic, database, payments, etc. |

### Use Cases

- E-commerce storefronts with rich product catalogs
- Booking and reservation systems
- Games and interactive experiences
- Complex forms and configuration UIs
- Dashboards and data visualization
- Subscription management portals

---

## Web App Integration

### Inline Keyboard Launch

Launch a Mini App from an inline keyboard button using the `web_app` parameter:

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def launch_miniapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a button that opens a Mini App."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Open Store",
                    web_app={"url": "https://yourdomain.com/miniapp"},
                )
            ]
        ]
    )

    await update.message.reply_text(
        "Tap below to open the store:",
        reply_markup=keyboard,
    )
```

### Keyboard Button Launch

Pin a Mini App as a persistent keyboard button:

```python
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def set_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a Mini App as the bot's menu button."""
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button={
            "type": "web_app",
            "text": "Open App",
            "web_app": {"url": "https://yourdomain.com/miniapp"},
        },
    )
```

### MenuButtonWebApp

The menu button appears at the bottom of the chat interface, providing persistent access to the Mini App.

| Field | Type | Description |
|---|---|---|
| `type` | `str` | Always `"web_app"` |
| `text` | `str` | Button label (1-64 characters) |
| `web_app.url` | `str` | HTTPS URL of the Mini App |

> [!NOTE]
> Mini App URLs must be served over HTTPS and use ports 443, 80, 88, or 8443.

---

## Receiving Data from Mini Apps

When a user interacts with a Mini App, data can be sent back to the bot via `WebAppData`.

### WebAppData Structure

| Field | Type | Description |
|---|---|---|
| `data` | `str` | The data string sent by the Mini App |
| `button_text` | `str` | Text of the keyboard button that launched the app |

### Handling WebAppData

```python
from telegram import Update
from telegram.ext import ContextTypes

import json
import logging

logger = logging.getLogger(__name__)


async def webapp_data_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle data received from a Mini App."""
    message = update.message
    if not message or not message.web_app_data:
        return

    raw_data: str = message.web_app_data.data
    button_text: str = message.web_app_data.button_text

    logger.info(
        "Received Mini App data from user %s (button: %s)",
        message.from_user.id,
        button_text,
    )

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        logger.error("Invalid JSON from Mini App: %s", raw_data)
        await message.reply_text("Invalid data received. Please try again.")
        return

    # Process the data
    await message.reply_text(f"Received: {json.dumps(data, indent=2)}")
```

> [!IMPORTANT]
> Data sent from the Mini App is **client-supplied** and must **always** be validated server-side. Never trust `web_app_data.data` without verification.

---

## Telegram WebApp JavaScript API

The Mini App frontend accesses Telegram features through `window.Telegram.WebApp`.

### Core Methods

| Method | Description |
|---|---|
| `.ready()` | Signal that the Mini App is loaded and ready |
| `.expand()` | Expand the Mini App to full available height |
| `.close()` | Close the Mini App and return to the chat |
| `.sendData(data)` | Send a string (max 4096 bytes) back to the bot |
| `.openLink(url, options)` | Open an external URL in the default browser |
| `.openTelegramLink(url)` | Open a Telegram link (t.me/...) |

### Data Properties

| Property | Type | Description |
|---|---|---|
| `.initData` | `string` | Signed authentication data from Telegram |
| `.initDataUnsafe` | `object` | Parsed version of `initData` (untrusted) |
| `.initDataUnsafe.user` | `object` | Current user info (id, first_name, etc.) |
| `.initDataUnsafe.chat_type` | `string` | `"private"`, `"group"`, `"supergroup"`, or `"channel"` |
| `.theme_params` | `object` | Theme colors defined by the user |
| `.colorScheme` | `string` | `"light"` or `"dark"` |
| `.viewportHeight` | `number` | Current viewport height |
| `.viewportStableHeight` | `number` | Stable viewport height (excludes keyboard) |
| `.isExpanded` | `boolean` | Whether the Mini App is expanded |
| `.platform` | `string` | Client platform (`"ios"`, `"android"`, `"tdesktop"`, etc.) |

### Sending Data Back to the Bot

```javascript
// In your Mini App frontend JavaScript
const TelegramApp = window.Telegram.WebApp;

// Signal that the app is ready
TelegramApp.ready();

// Expand to full height
TelegramApp.expand();

// Send data back to the bot when the user completes an action
function submitOrder(orderData) {
    const payload = JSON.stringify(orderData);
    TelegramApp.sendData(payload);
}
```

### Controlling the Mini App

```javascript
const TelegramApp = window.Telegram.WebApp;

// Read theme colors
const bgColor = TelegramApp.theme_params.bg_color;
const textColor = TelegramApp.theme_params.text_color;

document.body.style.backgroundColor = bgColor;
document.body.style.color = textColor;

// Close the app
TelegramApp.close();

// Open an external link
TelegramApp.openLink("https://example.com", { try_browser: true });

// Open a Telegram link
TelegramApp.openTelegramLink("https://t.me/yourbot");
```

---

## initData Validation

**CRITICAL:** Always validate `initData` on the server. This data is cryptographically signed by Telegram and proves the request originated from a genuine Telegram client.

### Why Validation Is Essential

Without validation, an attacker can forge arbitrary user data (user ID, name, etc.) and impersonate any user. The HMAC signature in `initData` prevents this.

### Validation Algorithm

1. Parse `initData` as a URL-encoded query string.
2. Extract the `hash` parameter.
3. Remove `hash` from the data.
4. Sort remaining key-value pairs alphabetically by key.
5. Join them as `key=value` pairs separated by newlines → `data_check_string`.
6. Compute `secret_key = HMAC-SHA256("WebAppData", bot_token)`.
7. Compute `computed_hash = HMAC-SHA256(secret_key, data_check_string)`.
8. Compare `computed_hash` with the received `hash`.

### Python Implementation

```python
import hmac
import hashlib
import logging
from time import time
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

# Maximum age for initData (24 hours in seconds)
INIT_DATA_MAX_AGE: int = 86400


def validate_webapp_init_data(init_data: str, bot_token: str) -> dict[str, str] | None:
    """
    Validate Telegram Mini App initData using HMAC-SHA256.

    Args:
        init_data: The raw initData string from the Mini App.
        bot_token: The bot token used to generate the HMAC secret.

    Returns:
        Parsed initData dict if valid, None otherwise.
    """
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
    except Exception:
        logger.warning("Failed to parse initData")
        return None

    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        logger.warning("No hash in initData")
        return None

    # Build the data check string
    data_check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed.items()))

    # Compute the secret key
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()

    # Compute and compare the hash
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        logger.warning("Hash mismatch — possible tampering detected")
        return None

    # Check auth_date freshness
    auth_date_str = parsed.get("auth_date", [None])[0]
    if auth_date_str is None:
        logger.warning("No auth_date in initData")
        return None

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        logger.warning("Invalid auth_date: %s", auth_date_str)
        return None

    if abs(time() - auth_date) > INIT_DATA_MAX_AGE:
        logger.warning(
            "InitData expired: auth_date=%d, now=%d, diff=%d",
            auth_date,
            int(time()),
            abs(time() - auth_date),
        )
        return None

    # Return flat dict
    return {k: v[0] for k, v in parsed.items()}
```

### Using Validation in a Request Handler

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()
BOT_TOKEN = "YOUR_BOT_TOKEN"


@app.post("/api/webapp/submit")
async def submit_webapp_data(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
):
    """Receive and validate Mini App data."""
    validated = validate_webapp_init_data(x_telegram_init_data, BOT_TOKEN)

    if validated is None:
        raise HTTPException(status_code=401, detail="Invalid init data")

    user_id = validated.get("user")
    # Proceed with authenticated user
    return {"status": "ok", "user": user_id}
```

---

## Complete Mini App Example

### Backend (Python + FastAPI)

```python
import hmac
import hashlib
import json
import logging
from time import time
from urllib.parse import parse_qs

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"
INIT_DATA_MAX_AGE = 86400


# ─── initData Validation ────────────────────────────────────────


def validate_init_data(init_data: str) -> dict[str, str] | None:
    """Validate Telegram Mini App initData."""
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
    except Exception:
        return None

    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()

    computed = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        return None

    auth_date = int(parsed.get("auth_date", [0])[0])
    if abs(time() - auth_date) > INIT_DATA_MAX_AGE:
        return None

    return {k: v[0] for k, v in parsed.items()}


# ─── API Routes ─────────────────────────────────────────────────


class OrderRequest(BaseModel):
    init_data: str
    product_id: str
    quantity: int


@app.post("/api/order")
async def create_order(req: OrderRequest):
    """Create an order from Mini App data."""
    validated = validate_init_data(req.init_data)

    if validated is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = json.loads(validated.get("user", "{}"))
    logger.info(
        "Order from user %s: %s x%d", user.get("id"), req.product_id, req.quantity
    )

    return {
        "status": "created",
        "order_id": "order_abc123",
        "user_id": user.get("id"),
    }


@app.get("/", response_class=HTMLResponse)
async def serve_miniapp():
    """Serve the Mini App HTML page."""
    return MINIAPP_HTML


# ─── Mini App HTML ─────────────────────────────────────────────

MINIAPP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>My Mini App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--tg-theme-bg-color, #ffffff);
            color: var(--tg-theme-text-color, #000000);
            padding: 16px;
        }
        .product {
            border: 1px solid var(--tg-theme-hint-color, #ccc);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .product h3 { margin-bottom: 8px; }
        .btn {
            background: var(--tg-theme-button-color, #3390ec);
            color: var(--tg-theme-button-text-color, #ffffff);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            width: 100%;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Store</h1>
    <div class="product">
        <h3>Premium Plan</h3>
        <p>Full access for 30 days</p>
        <br>
        <button class="btn" onclick="buy('premium')">Buy for 10 Stars</button>
    </div>

    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        function buy(productId) {
            fetch('/api/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': tg.initData,
                },
                body: JSON.stringify({
                    init_data: tg.initData,
                    product_id: productId,
                    quantity: 1,
                }),
            })
            .then(r => r.json())
            .then(data => {
                // Send order confirmation back to the bot
                tg.sendData(JSON.stringify(data));
            })
            .catch(err => {
                console.error('Order failed:', err);
            });
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=443)
```

### Bot Handler (python-telegram-bot)

```python
import json
import logging
from typing import Final

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN: Final[str] = "YOUR_BOT_TOKEN"
MINIAPP_URL: Final[str] = "https://yourdomain.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Launch the Mini App."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Open Store",
                    web_app={"url": MINIAPP_URL},
                )
            ]
        ]
    )
    await update.message.reply_text(
        "Welcome! Tap below to browse products:",
        reply_markup=keyboard,
    )


async def handle_webapp_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle data received from the Mini App."""
    message = update.message
    if not message or not message.web_app_data:
        return

    try:
        data = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        await message.reply_text("Invalid data received.")
        return

    logger.info("Mini App data from user %s: %s", message.from_user.id, data)

    await message.reply_text(
        f"Order confirmed!\nOrder ID: {data.get('order_id', 'N/A')}"
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
    )

    logger.info("Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

---

## Security Considerations

### Critical Security Rules

| Rule | Description |
|---|---|
| **Validate `initData` server-side** | Never trust client-side validation alone. Always verify the HMAC signature. |
| **Check `auth_date` freshness** | Reject data older than 24 hours to prevent replay attacks. |
| **Use HTTPS only** | Mini App URLs must use HTTPS. Telegram enforces this. |
| **Validate all inputs** | Treat every value from `web_app_data` and `initData` as untrusted. |
| **Origin restrictions** | Starting from Bot API v10.2, you can restrict which domains are allowed to send data. |

### Threat Model

| Threat | Mitigation |
|---|---|
| Forged user ID | HMAC signature verification prevents tampering |
| Replay attacks | `auth_date` freshness check (max 24 hours) |
| Man-in-the-middle | HTTPS enforcement for all Mini App URLs |
| Data injection | Server-side input validation and sanitization |
| Cross-site scripting | Content Security Policy headers, input escaping |

### Recommended Headers

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Restrict CORS to Telegram Mini App origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

---

## Login Widget

The Login Widget provides an alternative to Mini Apps for authenticating users on external websites. It uses the same HMAC-SHA-256 validation approach.

### Installation

1. Open BotFather and use `/mybots` → select your bot → **Bot Settings** → **Domain**.
2. Add your website domain.
3. Embed the widget script on your login page:

```html
<script src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YourBotName"
        data-size="large"
        data-onauth="onTelegramAuth(user)">
</script>
```

```javascript
function onTelegramAuth(user) {
    // user contains: id, first_name, last_name, username, photo_url, auth_date, hash
    fetch('/auth/telegram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user),
    })
    .then(r => r.json())
    .then(data => {
        window.location.href = '/dashboard';
    });
}
```

### Server-Side Validation

The Login Widget uses the same HMAC validation as Mini Apps:

```python
import hmac
import hashlib
from time import time
from urllib.parse import parse_qs


def validate_login_widget(data: dict, bot_token: str) -> bool:
    """
    Validate Telegram Login Widget data.

    Args:
        data: Dict with 'hash', 'auth_date', and user fields.
        bot_token: Bot token for HMAC secret.

    Returns:
        True if the data is authentic and fresh.
    """
    received_hash = data.get("hash")
    auth_date = data.get("auth_date")

    if not received_hash or not auth_date:
        return False

    # Check freshness
    if abs(time() - int(auth_date)) > 86400:
        return False

    # Build check string from all fields except hash
    check_data = {k: v for k, v in sorted(data.items()) if k != "hash"}
    data_check_string = "\n".join(f"{k}={v}" for k, v in check_data.items())

    # Compute HMAC
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    computed = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, received_hash)
```

---

## Best Practices

1. **Always validate server-side** — Client-side checks are UX improvements, not security measures.
2. **Keep `initData` fresh** — Reject data older than 24 hours.
3. **Use a proper web framework** — FastAPI, Django, or Flask for the Mini App backend.
4. **Implement CSP headers** — Prevent XSS by setting Content-Security-Policy.
5. **Test on all platforms** — Mini Apps render differently on iOS, Android, and desktop.
6. **Handle theme changes** — Use CSS custom properties (`var(--tg-theme-*)`) for dynamic theming.
7. **Optimize for mobile** — Mini Apps primarily run on mobile devices; design mobile-first.
8. **Graceful degradation** — Handle cases where the Mini App fails to load or the user closes it prematurely.
