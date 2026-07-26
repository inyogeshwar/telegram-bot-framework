# Chapter 16: Security Audit & Best Practices

> **"Security is not a feature — it is a prerequisite."**
> Every Telegram bot interacts with untrusted user input, handles API tokens, and may process sensitive data. This chapter provides a comprehensive security audit framework and hardening guide for production Python Telegram Bot deployments.

---

## Table of Contents

1. [Token Security (CRITICAL)](#1-token-security-critical)
2. [Secrets Management](#2-secrets-management)
3. [Input Validation & Sanitization](#3-input-validation--sanitization)
4. [HTML/Markdown Injection](#4-htmlmarkdown-injection)
5. [Rate Limiting & Flood Protection](#5-rate-limiting--flood-protection)
6. [Authorization & Access Control](#6-authorization--access-control)
7. [Callback Data Security](#7-callback-data-security)
8. [Webhook Security](#8-webhook-security)
9. [Deep Link Abuse Prevention](#9-deep-link-abuse-prevention)
10. [Spam Prevention](#10-spam-prevention)
11. [DoS Protection](#11-dos-protection)
12. [Logging Security](#12-logging-security)
13. [PII Protection](#13-pii-protection)
14. [Mini App / Web App Security](#14-mini-app--web-app-security)
15. [Business Bot Risks](#15-business-bot-risks)
16. [Dependency Security](#16-dependency-security)
17. [Secure Deployment Checklist](#17-secure-deployment-checklist)
18. [OWASP Mapping](#18-owasp-top-10-mapping)
19. [Severity Ratings](#19-severity-ratings)
20. [Copy-Paste Security Checklist](#20-copy-paste-security-checklist)

---

## 1. Token Security (CRITICAL)

The bot token is the single most critical secret in your entire system. Anyone who possesses it has full control over your bot — reading messages, sending messages, accessing user data, and performing administrative actions.

### 1.1 Token Format

Telegram bot tokens follow a strict format:

```
<bot_id>:<secret_string>
# Example: 1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
```

- The first segment (`1234567890`) is the bot's numeric ID — **not** a secret.
- The second segment (`ABCDefGhIjKlMnOpQrStUvWxYz`) is the **secret credential** — this must never be exposed.

### 1.2 Hard Rules

| Rule | Rationale |
|------|-----------|
| **Never hardcode** tokens in source code | Token is exposed to anyone with repo access |
| **Never commit** to version control | History is permanent; `git filter-branch` is unreliable |
| **Never display** tokens in logs | Log aggregation systems store data for years |
| **Never share** tokens in chat messages | Messaging platforms may retain or index content |
| **Never include** tokens in screenshots | Image recognition can extract text |
| **Never paste** tokens into public forums | Content is indexed and cached by search engines |

### 1.3 Token Leakage Vectors

```
┌─────────────────────────────────────────────────────┐
│              TOKEN LEAKAGE VECTORS                   │
├──────────────────────┬──────────────────────────────┤
│ Vector               │ Prevention                   │
├──────────────────────┼──────────────────────────────┤
│ Source code          │ .env + .gitignore             │
│ Exception tracebacks │ Catch-all error handlers      │
│ Log files            │ Structured logging w/ redact  │
│ Crash reports        │ Sanitize before submission    │
│ Screenshots / video  │ Never display in UI           │
│ .env committed       │ .gitignore + pre-commit hook  │
│ CI/CD output         │ Mask secrets in pipeline      │
│ Docker image layers  │ Multi-stage builds, .dockerignore │
│ Docker inspect       │ Use Docker secrets / vaults   │
│ Backup files         │ Exclude from backups          │
│ Editor autocomplete  │ .env only, not source         │
│ Version control GUIs │ .gitignore coverage           │
│ Process listings     │ Use env vars, not argv        │
│ Core dumps           │ Restrict coredump size        │
└──────────────────────┴──────────────────────────────┘
```

### 1.4 Environment Separation

Maintain separate bot tokens for each environment:

```
DEV_TOKEN=1234567890:dev_token_here
STAGING_TOKEN=1234567890:staging_token_here
PRODUCTION_TOKEN=1234567890:prod_token_here
```

> [!WARNING]
> **NEVER** use a production token for development. A compromised dev environment means a compromised production bot.

### 1.5 Token Revocation

If a token is compromised:

1. Immediately revoke via **BotFather** (`/revoke`)
2. Generate a new token
3. Update all deployment configurations **atomically**
4. Verify the old token no longer works
5. Audit access logs for unauthorized usage
6. Rotate any derived credentials (webhook URLs, etc.)

```bash
# Via BotFather:
/mybots → Select bot → API Token → Revoke current token
```

---

## 2. Secrets Management

### 2.1 Environment Variables with python-dotenv

Use `python-dotenv` to load secrets from a `.env` file during development:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env into environment

BOT_TOKEN = os.environ["BOT_TOKEN"]  # Raises KeyError if missing — fail fast
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
DATABASE_URL = os.environ["DATABASE_URL"]
```

### 2.2 .gitignore Configuration

```gitignore
# Secrets
.env
.env.*
!.env.example

# Generated environment files
*.env.local
*.env.production
```

Create a `.env.example` with placeholder values:

```env
BOT_TOKEN=your_token_here
WEBHOOK_SECRET=your_webhook_secret_here
DATABASE_URL=your_database_url_here
```

### 2.3 Platform-Specific Secret Management

| Platform | Secret Store | Notes |
|----------|-------------|-------|
| **Heroku** | Config Vars | `heroku config:set BOT_TOKEN=xxx` |
| **AWS** | Secrets Manager / Parameter Store | Use IAM roles, not hardcoded creds |
| **Google Cloud** | Secret Manager | Integrate with IAM |
| **Azure** | Key Vault | Managed Identity recommended |
| **Docker** | Docker Secrets / BuildKit | `--mount=type=secret` |
| **Kubernetes** | Secrets + Sealed Secrets | Encrypt at rest |
| **Railway** | Variables tab | Support for .env import |
| **Fly.io** | `fly secrets set` | Encrypted at rest |
| **DigitalOcean App Platform** | App Spec secrets | Set via dashboard or CLI |

### 2.4 Secret Rotation

```python
# Rotate secrets without redeployment (polling pattern)
import os
import time


def get_token() -> str:
    """Re-read token from environment on each call.

    Allows rotation without restart when environment
    is updated externally (e.g., Secrets Manager refresh).
    """
    return os.environ["BOT_TOKEN"]
```

> [!IMPORTANT]
> Always rotate secrets immediately if:
> - A team member with access leaves the project
> - A dependency with access is compromised
> - A log or artifact containing the secret is exposed
> - On a regular schedule (e.g., every 90 days)

### 2.5 Common Mistakes

```python
# ❌ WRONG — Hardcoded token
TOKEN = "1234567890:ABCdefGhIjKlMnOpQrStUvWxYz"

# ❌ WRONG — Token in config file committed to git
TOKEN = config["telegram"]["token"]

# ✅ CORRECT — Token from environment, fail if missing
TOKEN = os.environ["BOT_TOKEN"]

# ✅ CORRECT — Token with default for local dev only
TOKEN = os.environ.get("BOT_TOKEN", "local_dev_only_token")
```

---

## 3. Input Validation & Sanitization

### 3.1 The Fundamental Principle

> [!CAUTION]
> **Every piece of data from Telegram updates is UNTRUSTED.** Users can send anything — malformed text, oversized payloads, crafted callback data, or forged inline queries. Treat all incoming data as potentially hostile.

### 3.2 Validation Categories

| Data Source | Risk Level | Validation Required |
|-------------|-----------|---------------------|
| `message.text` | HIGH | Length, encoding, content type |
| `callback_query.data` | HIGH | Format, length (64 bytes max), integrity |
| `inline_query.query` | HIGH | Length, encoding |
| `deep_link` payload | HIGH | Format, encoding, rate limiting |
| `web_app` `initData` | **CRITICAL** | HMAC signature, auth_date freshness |
| `pre_checkout_query` | HIGH | Amount, currency, invoice integrity |
| `chat_member` updates | MEDIUM | Verify chat_id matches expected |
| `poll` / `poll_answer` | LOW | ID format validation |
| File downloads | HIGH | File type, size limits, content sniffing |

### 3.3 Text Input Validation

```python
import re

MAX_MESSAGE_LENGTH = 4096
MAX_CALLBACK_DATA = 64


def validate_text_input(text: str | None, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """Validate and sanitize user text input."""
    if text is None:
        raise ValueError("Input text must not be None")

    # Strip null bytes and control characters (except newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Enforce length limit
    text = text.strip()
    if len(text) == 0:
        raise ValueError("Input text must not be empty")
    if len(text) > max_length:
        raise ValueError(f"Input text exceeds maximum length of {max_length}")

    return text


def validate_callback_data(data: str | None) -> str:
    """Validate callback_data before processing."""
    if data is None:
        raise ValueError("Callback data must not be None")
    if len(data) > MAX_CALLBACK_DATA:
        raise ValueError(f"Callback data exceeds {MAX_CALLBACK_DATA} bytes")
    # Only allow safe characters
    if not re.match(r"^[a-zA-Z0-9_:./\-]+$", data):
        raise ValueError("Callback data contains invalid characters")
    return data


def validate_deep_link(payload: str | None) -> str:
    """Validate deep link payload."""
    if payload is None:
        raise ValueError("Deep link payload must not be None")
    # Deep link payloads max 64 chars
    if len(payload) > 64:
        raise ValueError("Deep link payload too long")
    # Alphanumeric + underscores only (adjust as needed)
    if not re.match(r"^[a-zA-Z0-9_\-]+$", payload):
        raise ValueError("Deep link payload contains invalid characters")
    return payload
```

### 3.4 Numeric Validation

```python
def validate_integer_input(value: str, min_val: int = 0, max_val: int = 2**31) -> int:
    """Safely parse and validate integer input."""
    try:
        parsed = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid integer: {value}")

    if parsed < min_val or parsed > max_val:
        raise ValueError(f"Integer {parsed} out of range [{min_val}, {max_val}]")

    return parsed
```

### 3.5 File Download Validation

```python
import magic  # python-magic
import aiohttp

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


async def safe_download_file(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> bytes:
    """Download a Telegram file with safety checks."""
    file = await context.bot.get_file(file_id)

    # Check file size
    if file.file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file.file_size} bytes")

    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            content = await resp.read()

    # Verify actual size matches reported size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Downloaded file exceeds size limit")

    # Verify MIME type (don't trust extension)
    detected = magic.from_buffer(content, mime=True)
    if detected not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unexpected file type: {detected}")

    return content
```

---

## 4. HTML/Markdown Injection

### 4.1 The Problem

When using `parse_mode="HTML"` or `parse_mode="MarkdownV2"`, user-provided text inserted into formatted messages can break formatting, display unintended content, or — in worst cases — be exploited for phishing.

```python
# DANGEROUS — User input directly in HTML
user_name = update.effective_user.first_name
await message.reply_text(f"<b>Hello, {user_name}!</b>", parse_mode="HTML")
# If user_name is "<script>alert(1)</script>", the output is dangerous
```

### 4.2 HTML Escaping

```python
import html


def safe_html(text: str) -> str:
    """Escape text for safe use in HTML parse_mode messages.

    Escapes: & < > " '
    """
    return html.escape(text, quote=True)


# Usage
user_name = update.effective_user.first_name
await message.reply_text(f"<b>Hello, {safe_html(user_name)}!</b>", parse_mode="HTML")
```

**Characters escaped:**

| Character | HTML Entity |
|-----------|-------------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |

### 4.3 MarkdownV2 Escaping

MarkdownV2 requires escaping of **18 special characters**:

```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

```python
import re


def safe_markdown(text: str) -> str:
    """Escape text for safe use in MarkdownV2 parse_mode messages."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)


# Usage
user_name = update.effective_user.first_name
await message.reply_text(
    f"*Hello, {safe_markdown(user_name)}!*", parse_mode="MarkdownV2"
)
```

### 4.4 Pre-Built Safe Formatting Helpers

```python
import html as _html
import re


class SafeFormatter:
    """Safe message formatting with injection prevention."""

    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{_html.escape(text)}</b>"

    @staticmethod
    def italic(text: str) -> str:
        return f"<i>{_html.escape(text)}</i>"

    @staticmethod
    def code(text: str) -> str:
        return f"<code>{_html.escape(text)}</code>"

    @staticmethod
    def pre(text: str, language: str = "") -> str:
        return f"<pre>{_html.escape(text)}</pre>"

    @staticmethod
    def link(text: str, url: str) -> str:
        """Create a safe hyperlink."""
        safe_text = _html.escape(text)
        # Only allow http/https URLs
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {url}")
        return f'<a href="{url}">{safe_text}</a>'

    @staticmethod
    def mention(text: str, user_id: int) -> str:
        safe_text = _html.escape(text)
        return f'<a href="tg://user?id={user_id}">{safe_text}</a>'


# Usage
fmt = SafeFormatter()
await message.reply_text(
    f"{fmt.bold(safe_html(user_name))} joined the group!", parse_mode="HTML"
)
```

### 4.5 MarkdownV2 Full Escape Pattern

```python
# Telegram MarkdownV2 special characters (from Bot API docs)
MARKDOWN_V2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def escape_markdown_v2(text: str) -> str:
    """Escape all MarkdownV2 special characters.

    Within pre/code blocks, only escape ` and \.
    """
    result = []
    for char in text:
        if char in MARKDOWN_V2_SPECIAL:
            result.append("\\")
        result.append(char)
    return "".join(result)


def escape_markdown_v2_code(text: str) -> str:
    """Escape text inside MarkdownV2 pre or code blocks."""
    return text.replace("\\", "\\\\").replace("`", "\\`")
```

---

## 5. Rate Limiting & Flood Protection

### 5.1 Telegram's Rate Limits

Telegram enforces rate limits on bot API calls:

| Limit | Value | Scope |
|-------|-------|-------|
| Messages to different users | 30 per second | Global |
| Messages to same chat | 1 per second | Per chat |
| Group messages | 20 per minute | Per group |
| Inline queries | 30 per second | Global |
| File downloads | Concurrent limit | Per bot |
| Webhook updates | No explicit limit | But respect 30 msg/sec |

Exceeding limits results in `429 Too Many Requests` with a `RetryAfter` header.

### 5.2 Token Bucket Rate Limiter

```python
import time
import asyncio
from collections import defaultdict


class TokenBucketRateLimiter:
    """Per-user token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: Tokens added per second.
            capacity: Maximum tokens in bucket.
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens: dict[int, float] = defaultdict(lambda: capacity)
        self.last_refill: dict[int, float] = defaultdict(time.monotonic)
        self._lock = asyncio.Lock()

    async def acquire(self, user_id: int) -> bool:
        """Try to acquire a token. Returns True if allowed."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill[user_id]
            self.tokens[user_id] = min(
                self.capacity, self.tokens[user_id] + elapsed * self.rate
            )
            self.last_refill[user_id] = now

            if self.tokens[user_id] >= 1:
                self.tokens[user_id] -= 1
                return True
            return False

    def retry_after(self, user_id: int) -> float:
        """Calculate seconds until next token is available."""
        if self.tokens[user_id] >= 1:
            return 0.0
        return (1 - self.tokens[user_id]) / self.rate


# Global rate limiter: 10 messages per 10 seconds per user
user_limiter = TokenBucketRateLimiter(rate=1.0, capacity=10)

# Strict rate limiter for expensive operations: 3 per 30 seconds
strict_limiter = TokenBucketRateLimiter(rate=0.1, capacity=3)


def rate_limit(limiter: TokenBucketRateLimiter):
    """Decorator for rate-limiting handler functions."""

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id

            if not await limiter.acquire(user_id):
                wait = limiter.retry_after(user_id)
                await update.message.reply_text(
                    f"Rate limit exceeded. Please try again in {wait:.0f} seconds."
                )
                return

            return await func(update, context)

        return wrapper

    return decorator


# Usage
@rate_limit(user_limiter)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process message...
    pass
```

### 5.3 Sliding Window Rate Limiter

```python
import time
from collections import deque


class SlidingWindowRateLimiter:
    """Sliding window counter rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[int, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def is_allowed(self, user_id: int) -> bool:
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove expired entries
            while self.requests[user_id] and self.requests[user_id][0] < window_start:
                self.requests[user_id].popleft()

            if len(self.requests[user_id]) < self.max_requests:
                self.requests[user_id].append(now)
                return True
            return False
```

### 5.4 Handling Telegram's RetryAfter

```python
from telegram.error import RetryAfter, TimedOut, NetworkError


async def safe_send_message(bot, chat_id: int, text: str, **kwargs):
    """Send a message with retry-after handling."""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except RetryAfter as e:
            wait_time = e.retry_after
            logger.warning(
                f"Rate limited. Waiting {wait_time}s (attempt {attempt + 1})"
            )
            await asyncio.sleep(wait_time + 1)  # Add 1s buffer
        except TimedOut:
            logger.warning(f"Timed out sending to {chat_id} (attempt {attempt + 1})")
            await asyncio.sleep(2**attempt)  # Exponential backoff
        except NetworkError as e:
            logger.error(f"Network error: {e} (attempt {attempt + 1})")
            await asyncio.sleep(2**attempt)

    logger.error(f"Failed to send message to {chat_id} after {max_retries} attempts")
    return None
```

---

## 6. Authorization & Access Control

### 6.1 Core Principle

> [!CRITICAL]
> **NEVER trust client-side user identity.** Always verify permissions server-side using the Telegram Bot API. A malicious user can forge any `user_id` in client-side data.

### 6.2 Admin-Only Decorator

```python
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

ALLOWED_ADMIN_IDS = {123456789, 987654321}  # Or load from config


def admin_only(func):
    """Restrict command to bot administrators (by user ID)."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if user_id not in ALLOWED_ADMIN_IDS:
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return

        return await func(update, context)

    return wrapper


# Usage
@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast a message to all users — admin only."""
    pass
```

### 6.3 Chat-Level Admin Check

```python
async def is_chat_admin(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int
) -> bool:
    """Check if user is an admin or creator of the chat."""
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False


def chat_admin_only(func):
    """Restrict command to chat administrators (server-verified)."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if not await is_chat_admin(context, chat_id, user_id):
            await update.message.reply_text("⛔ Chat admin only.")
            return

        return await func(update, context)

    return wrapper
```

### 6.4 Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps


class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


ROLE_HIERARCHY = {
    Role.USER: 0,
    Role.MODERATOR: 1,
    Role.ADMIN: 2,
    Role.SUPER_ADMIN: 3,
}


def get_user_role(user_id: int) -> Role:
    """Look up user role from database/config."""
    # Replace with actual database lookup
    user_roles = {
        123456789: Role.SUPER_ADMIN,
        987654321: Role.ADMIN,
        555555555: Role.MODERATOR,
    }
    return user_roles.get(user_id, Role.USER)


def require_role(minimum_role: Role):
    """Decorator that enforces minimum role level."""

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            user_role = get_user_role(user_id)

            if ROLE_HIERARCHY[user_role] < ROLE_HIERARCHY[minimum_role]:
                await update.message.reply_text(
                    f"⛔ Required role: {minimum_role.value}"
                )
                return

            return await func(update, context)

        return wrapper

    return decorator


# Usage
@require_role(Role.ADMIN)
async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a user record — admin only."""
    pass


@require_role(Role.MODERATOR)
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user — moderator or above."""
    pass
```

### 6.5 Whitelist Approach

```python
import os

# Whitelist of allowed chat IDs for group deployment
ALLOWED_CHAT_IDS: set[int] = set()


def load_allowed_chats():
    """Load allowed chat IDs from environment."""
    global ALLOWED_CHAT_IDS
    raw = os.environ.get("ALLOWED_CHAT_IDS", "")
    ALLOWED_CHAT_IDS = {int(cid.strip()) for cid in raw.split(",") if cid.strip()}


load_allowed_chats()


def bot_in_allowed_chat(func):
    """Only respond in whitelisted chats."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            # Silently ignore — don't reveal bot existence
            return

        return await func(update, context)

    return wrapper
```

> [!NOTE]
> The **whitelist approach** is the most secure pattern for bots deployed in specific groups. An empty `ALLOWED_CHAT_IDS` should mean "allow all" — but consider the security implications.

---

## 7. Callback Data Security

### 7.1 Constraints

- **Maximum length**: 64 bytes (not characters — UTF-8 encoded)
- **Always transmitted in plaintext** in the update object
- **User-controlled** — a user can trigger any callback data value

### 7.2 Safe Callback Data Design

```python
import json
import hashlib
import hmac

SECRET_KEY = os.environ["CALLBACK_SECRET"]


def encode_callback(action: str, payload: dict) -> str:
    """Encode callback data with HMAC integrity check."""
    data = json.dumps({"a": action, "p": payload}, separators=(",", ":"))

    if len(data.encode("utf-8")) > 63:
        raise ValueError("Callback data exceeds 63 bytes (reserving 1 for separator)")

    sig = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()[:8]
    return f"{sig}:{data}"


def decode_callback(data: str) -> tuple[str, dict]:
    """Decode and verify callback data integrity."""
    if ":" not in data:
        raise ValueError("Invalid callback data format")

    sig, payload_str = data.split(":", 1)

    expected_sig = hmac.new(
        SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256
    ).hexdigest()[:8]

    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Callback data signature mismatch")

    decoded = json.loads(payload_str)
    return decoded["a"], decoded["p"]


# Usage
callback_data = encode_callback("confirm_delete", {"user_id": 123})
inline_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Yes", callback_data=encode_callback("confirm_delete", {"user_id": 123})
            ),
            InlineKeyboardButton("No", callback_data=encode_callback("cancel", {})),
        ]
    ]
)


# In handler
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        action, payload = decode_callback(query.data)
    except ValueError:
        await query.answer("Invalid action.", show_alert=True)
        return

    if action == "confirm_delete":
        # Process deletion...
        pass
```

### 7.3 Callback Data Validation Patterns

```python
# Simple pattern-based routing (no HMAC overhead)
VALID_CALLBACKS = {
    "lang:": r"^lang:[a-z]{2}$",  # lang:en, lang:fr
    "settings:": r"^settings:(notifications|theme|language)$",
    "page:": r"^page:\d+$",
}


def validate_callback_data(data: str) -> tuple[str, str] | None:
    """Validate callback data against known patterns.

    Returns (prefix, value) or None if invalid.
    """
    import re

    for prefix, pattern in VALID_CALLBACKS.items():
        if data.startswith(prefix):
            if re.match(pattern, data):
                return prefix, data[len(prefix) :]
            return None
    return None
```

### 7.4 Callback Anti-Patterns

| ❌ Anti-Pattern | ✅ Better Approach |
|----------------|-------------------|
| Storing user_id in callback_data | Look up `update.effective_user.id` server-side |
| Storing sensitive data | Use a session/cache keyed by user |
| Using sequential integer IDs | Use UUIDs or signed tokens |
| No validation | Validate against allowlist of patterns |
| Trusting callback data for authorization | Verify permissions server-side |

---

## 8. Webhook Security

### 8.1 Why Webhooks Require Extra Security

Webhooks expose an HTTP endpoint that receives unauthenticated traffic from Telegram's servers. Without proper verification, an attacker could send forged updates to your bot.

### 8.2 Secret Token Verification

```python
from fastapi import FastAPI, Request, HTTPException
from telegram import Update

app = FastAPI()

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Initialize bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()
# ... register handlers ...


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming Telegram webhook updates."""
    # Verify secret token
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not secret or not hmac.compare_digest(secret, WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Parse update
    data = await request.json()
    update = Update.de_json(data, application.bot)

    # Process update
    await application.process_update(update)

    return {"ok": True}


@app.on_event("startup")
async def startup():
    """Set webhook on startup."""
    await application.bot.set_webhook(
        url="https://yourdomain.com/webhook",
        secret_token=WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES,
    )
```

### 8.3 Flask Equivalent

```python
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify secret token
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    update = Update.de_json(data, bot)

    # Process synchronously or queue for async processing
    application.process_update(update)

    return jsonify({"ok": True})
```

### 8.4 Webhook Security Checklist

| Item | Requirement |
|------|------------|
| HTTPS | **Mandatory** for production webhooks |
| `secret_token` | Always set when calling `set_webhook` |
| Header validation | Check `X-Telegram-Bot-Api-Secret-Token` |
| IP allowlisting | Optional — Telegram publishes IP ranges |
| Request size limits | Reject oversized payloads (>1 MB) |
| Timeout handling | Process updates quickly, return 200 within 30s |
| Error handling | Don't expose internal errors in HTTP response |

### 8.5 Webhook vs. Polling Security Comparison

| Aspect | Polling | Webhook |
|--------|---------|---------|
| Network exposure | Outbound only | Inbound endpoint exposed |
| Authentication | None needed | Secret token required |
| HTTPS | Optional | Required by Telegram |
| Attack surface | Lower | Higher |
| Complexity | Lower | Higher |
| Recommended for | Development, small bots | Production, large-scale bots |

---

## 9. Deep Link Abuse Prevention

### 9.1 Deep Link Format

Deep links use the format: `https://t.me/yourbot?start=<payload>`

- Payload maximum: 64 characters
- Payload characters: `A-Z`, `a-z`, `0-9`, `_`, `-`
- Accessible to anyone with the link

### 9.2 Secure Deep Link Handler

```python
import re
import hashlib
import secrets

# In-memory rate limiter for deep link usage
deep_link_usage: dict[int, list[float]] = {}


def validate_deep_link_payload(payload: str) -> str:
    """Validate deep link payload format."""
    if not payload or len(payload) > 64:
        raise ValueError("Invalid payload length")
    if not re.match(r"^[A-Za-z0-9_\-]+$", payload):
        raise ValueError("Invalid payload characters")
    return payload


def check_deep_link_rate_limit(user_id: int, max_per_hour: int = 10) -> bool:
    """Rate limit deep link usage per user."""
    import time

    now = time.time()
    hour_ago = now - 3600

    if user_id not in deep_link_usage:
        deep_link_usage[user_id] = []

    # Clean old entries
    deep_link_usage[user_id] = [t for t in deep_link_usage[user_id] if t > hour_ago]

    if len(deep_link_usage[user_id]) >= max_per_hour:
        return False

    deep_link_usage[user_id].append(now)
    return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start with deep link payload."""
    user_id = update.effective_user.id

    # Rate limit
    if not check_deep_link_rate_limit(user_id):
        await update.message.reply_text("Too many requests. Try again later.")
        return

    payload = context.args[0] if context.args else None

    if payload:
        try:
            validated = validate_deep_link_payload(payload)
        except ValueError:
            await update.message.reply_text("Invalid start link.")
            return

        # Map payload to actions — NEVER execute arbitrary commands
        ACTION_MAP = {
            "ref": handle_referral,
            "verify": handle_verification,
            "settings": handle_settings_link,
        }

        prefix = validated.split("_", 1)[0] if "_" in validated else validated

        if prefix in ACTION_MAP:
            await ACTION_MAP[prefix](update, context, validated)
        else:
            await update.message.reply_text("Unknown start link.")
    else:
        await update.message.reply_text("Welcome!")
```

### 9.3 Anti-Patterns

```python
# ❌ NEVER — Arbitrary command execution from deep link
async def start(update, context):
    if context.args:
        command = context.args[0]
        await getattr(context.bot, command)()  # DANGEROUS!


# ❌ NEVER — Execute code from deep link
async def start(update, context):
    if context.args:
        eval(context.args[0])  # CRITICAL VULNERABILITY


# ✅ SAFE — Whitelisted action mapping
async def start(update, context):
    if context.args:
        payload = context.args[0]
        if payload in ("ref", "verify", "settings"):
            await ACTION_MAP[payload](update, context)
```

---

## 10. Spam Prevention

### 10.1 Anti-Spam Architecture

```
┌─────────────────────────────────────────────────────┐
│                 INCOMING MESSAGE                      │
│                      │                                │
│                      ▼                                │
│           ┌─────────────────────┐                    │
│           │  Global Rate Limit  │                    │
│           │  (token bucket)     │──── EXCEEDED ──→ Reject │
│           └─────────┬───────────┘                    │
│                     │ OK                              │
│                     ▼                                 │
│           ┌─────────────────────┐                    │
│           │  Per-User Rate      │                    │
│           │  Limit (sliding     │──── EXCEEDED ──→ Warn/Mute │
│           │  window)            │                    │
│           └─────────┬───────────┘                    │
│                     │ OK                              │
│                     ▼                                 │
│           ┌─────────────────────┐                    │
│           │  Content Analysis   │                    │
│           │  (link count,       │──── SPAM ──→ Delete & Warn │
│           │  keyword filter)    │                    │
│           └─────────┬───────────┘                    │
│                     │ OK                              │
│                     ▼                                 │
│           ┌─────────────────────┐                    │
│           │  CAPTCHA (if new)   │                    │
│           │  (optional)         │──── FAIL ──→ Restrict │
│           └─────────┬───────────┘                    │
│                     │ PASS                            │
│                     ▼                                 │
│           ┌─────────────────────┐                    │
│           │  Process Message    │                    │
│           └─────────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

### 10.2 Spam Detection Heuristics

```python
import re
from collections import defaultdict, deque
import time


class SpamDetector:
    """Simple spam detection based on frequency and content analysis."""

    def __init__(self):
        self.user_messages: dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
        self.warning_count: dict[int, int] = defaultdict(int)

    def analyze(self, user_id: int, text: str) -> dict:
        """Analyze message for spam indicators."""
        now = time.time()
        self.user_messages[user_id].append(now)

        indicators = {
            "is_spam": False,
            "reasons": [],
            "confidence": 0.0,
        }

        # Check 1: Message frequency (more than 10 messages in 10 seconds)
        recent = [t for t in self.user_messages[user_id] if now - t < 10]
        if len(recent) > 10:
            indicators["reasons"].append("high_frequency")
            indicators["confidence"] += 0.4

        # Check 2: Excessive URLs (more than 3)
        url_count = len(re.findall(r"https?://\S+", text))
        if url_count > 3:
            indicators["reasons"].append("excessive_urls")
            indicators["confidence"] += 0.3

        # Check 3: ALL CAPS (>80% uppercase, min 10 chars)
        alpha_chars = [c for c in text if c.isalpha()]
        if alpha_chars and len(alpha_chars) >= 10:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if upper_ratio > 0.8:
                indicators["reasons"].append("excessive_caps")
                indicators["confidence"] += 0.1

        # Check 4: Repeated characters (e.g., "AAAAAAAA")
        if re.search(r"(.)\1{5,}", text):
            indicators["reasons"].append("repeated_chars")
            indicators["confidence"] += 0.1

        # Check 5: Known spam patterns
        spam_keywords = [
            r"free\s+(money|crypto|bitcoin|gift)",
            r"click\s+(here|now|this\s+link)",
            r"limited\s+time\s+offer",
            r"earn\s+\$?\d+.*per\s+(day|hour|week)",
        ]
        for pattern in spam_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                indicators["reasons"].append("spam_keywords")
                indicators["confidence"] += 0.3
                break

        indicators["is_spam"] = indicators["confidence"] >= 0.5
        return indicators


spam_detector = SpamDetector()
```

### 10.3 Group Anti-Spam Handler

```python
async def anti_spam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check incoming messages for spam in groups."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text

    result = spam_detector.analyze(user_id, text)

    if result["is_spam"]:
        # Delete the message
        await update.message.delete()

        # Warn the user
        spam_detector.warning_count[user_id] += 1

        if spam_detector.warning_count[user_id] >= 3:
            # Mute the user for 24 hours
            until_date = int(time.time()) + 86400
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date,
            )
            await context.bot.send_message(
                chat_id,
                f"User {update.effective_user.first_name} muted for 24h (repeated spam).",
            )
        else:
            await context.bot.send_message(
                chat_id,
                f"⚠️ Warning {update.effective_user.first_name}: "
                f"Spam detected ({', '.join(result['reasons'])}). "
                f"Warning {spam_detector.warning_count[user_id]}/3.",
            )
```

### 10.4 Reporting Spam to Telegram

```python
async def report_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow admins to report spam messages to Telegram."""
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to report it.")
        return

    # Verify caller is admin
    if not await is_chat_admin(
        context, update.effective_chat.id, update.effective_user.id
    ):
        await update.message.reply_text("Admin only.")
        return

    try:
        await context.bot.report_chat(
            chat_id=update.effective_chat.id,
            message_id=update.message.reply_to_message.message_id,
        )
        await update.message.reply_text("✅ Message reported to Telegram.")
    except TelegramError as e:
        await update.message.reply_text(f"Failed to report: {e}")
```

---

## 11. DoS Protection

### 11.1 Resource Limits

```python
import asyncio
from functools import wraps

# Resource limits
MAX_CONCURRENT_TASKS = 50
MAX_PROCESSING_TIME_SECONDS = 30
MAX_FILE_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# Semaphore to limit concurrent processing
processing_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


def with_timeout(timeout: float = MAX_PROCESSING_TIME_SECONDS):
    """Decorator that enforces a processing timeout."""

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                return await asyncio.wait_for(func(update, context), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(
                    f"Handler {func.__name__} timed out after {timeout}s "
                    f"for user {update.effective_user.id}"
                )
                if update.message:
                    await update.message.reply_text("⚠️ Operation timed out.")
            return None

        return wrapper

    return decorator


def with_semaphore(func):
    """Decorator that limits concurrent execution."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        async with processing_semaphore:
            return await func(update, context)

    return wrapper


# Usage
@with_timeout(timeout=15)
@with_semaphore
async def heavy_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """A handler that might take a long time."""
    result = await some_slow_api_call()
    await update.message.reply_text(f"Result: {result}")
```

### 11.2 Conversation Timeout

```python
from telegram.ext import ConversationHandler

# Timeout for conversation states (e.g., 5 minutes)
CONVERSATION_TIMEOUT = 300


async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle conversation timeout."""
    await update.message.reply_text("⏰ Session timed out due to inactivity.")
    return ConversationHandler.END


# In ConversationHandler setup
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start_form", start_form)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    conversation_timeout=CONVERSATION_TIMEOUT,
)
```

### 11.3 External API Call Protection

```python
import aiohttp

API_TIMEOUT = aiohttp.ClientTimeout(total=10)  # 10 second timeout


async def safe_external_api_call(url: str, params: dict = None) -> dict | None:
    """Make an external API call with timeout and error handling."""
    try:
        async with aiohttp.ClientSession(timeout=API_TIMEOUT) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API returned status {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.warning(f"API call timed out: {url}")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"API call failed: {e}")
        return None
```

---

## 12. Logging Security

### 12.1 What NOT to Log

| Data Type | Risk | Action |
|-----------|------|--------|
| Bot token | Full control if leaked | **NEVER** log |
| User messages | PII exposure, compliance | Redact in production |
| Full user profiles | PII exposure | Log user_id only |
| File contents | May contain sensitive data | Log metadata only |
| Stack traces with tokens | Token leakage | Sanitize before logging |
| Database queries with credentials | Credential exposure | Mask passwords |
| Webhook payloads in full | May contain user data | Log summary only |

### 12.2 Secure Logging Setup

```python
import logging
import re


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive data from log records."""

    PATTERNS = [
        # Bot token pattern
        (re.compile(r"\d{9,10}:[A-Za-z0-9_-]{35}"), "[REDACTED_TOKEN]"),
        # Email addresses
        (
            re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            "[REDACTED_EMAIL]",
        ),
        # Phone numbers (simple pattern)
        (re.compile(r"\+?\d{10,15}"), "[REDACTED_PHONE]"),
        # Credit card numbers (simple pattern)
        (re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}"), "[REDACTED_CARD]"),
        # IP addresses (optional — may be needed for security logs)
        (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "[REDACTED_IP]"),
    ]

    def __init__(self, redact_pii: bool = True):
        super().__init__()
        self.redact_pii = redact_pii

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._redact(record.msg)
        if record.args and isinstance(record.args, tuple):
            record.args = tuple(
                self._redact(str(a)) if isinstance(a, str) else a for a in record.args
            )
        return True

    def _redact(self, text: str) -> str:
        for pattern, replacement in self.PATTERNS:
            text = pattern.sub(replacement, text)
        return text


def setup_logging(level: str = "INFO", redact_pii: bool = True):
    """Configure secure logging."""
    handler = logging.StreamHandler()
    handler.addFilter(SensitiveDataFilter(redact_pii=redact_pii))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))


# Usage
setup_logging(level="INFO", redact_pii=True)

logger = logging.getLogger(__name__)

# These will be automatically redacted:
logger.info("User login: token=1234567890:ABCdef...")  # Token redacted
logger.info("Contact: john@example.com")  # Email redacted
```

### 12.3 Structured Logging

```python
import json
import logging


class StructuredFormatter(logging.Formatter):
    """JSON structured logging for production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "chat_id"):
            log_entry["chat_id"] = record.chat_id
        if hasattr(record, "handler"):
            log_entry["handler"] = record.handler
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        return json.dumps(log_entry)
```

### 12.4 Log Retention Policy

```python
import os
import time
from pathlib import Path

LOG_RETENTION_DAYS = 30  # Retain logs for 30 days


def cleanup_old_logs(log_dir: str = "logs", retention_days: int = LOG_RETENTION_DAYS):
    """Delete log files older than retention period."""
    cutoff = time.time() - (retention_days * 86400)
    log_path = Path(log_dir)

    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff:
            log_file.unlink()
            print(f"Deleted old log: {log_file}")
```

---

## 13. PII Protection

### 13.1 Data Minimization

Only collect and store what you **absolutely need**:

```python
# ❌ WRONG — Storing everything
user_data = {
    "user_id": user.id,
    "username": user.username,
    "first_name": user.first_name,
    "last_name": user.last_name,
    "phone": user.phone_number,  # Don't store unless necessary
    "language_code": user.language_code,
    "is_premium": user.is_premium,
}

# ✅ CORRECT — Storing only what's needed
user_data = {
    "user_id": user.id,
    "language_code": user.language_code,
    "joined_at": datetime.utcnow().isoformat(),
}
```

### 13.2 Encrypted Storage

```python
from cryptography.fernet import Fernet
import os
import json

# Key stored in environment, NOT in code
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"].encode()
cipher = Fernet(ENCRYPTION_KEY)


def encrypt_user_data(data: dict) -> bytes:
    """Encrypt sensitive user data before storage."""
    json_data = json.dumps(data).encode()
    return cipher.encrypt(json_data)


def decrypt_user_data(encrypted: bytes) -> dict:
    """Decrypt user data for processing."""
    decrypted = cipher.decrypt(encrypted)
    return json.loads(decrypted.decode())


# Usage
sensitive_data = {"preferences": {"email": "user@example.com"}}
encrypted = encrypt_user_data(sensitive_data)
# Store encrypted in database...
```

### 13.3 Right to Deletion (GDPR)

```python
async def delete_my_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deletedata command — GDPR right to deletion."""
    user_id = update.effective_user.id

    try:
        # Delete from all data stores
        await delete_user_from_database(user_id)
        await delete_user_from_cache(user_id)
        await delete_user_files(user_id)

        await update.message.reply_text(
            "✅ All your data has been permanently deleted."
        )

        logger.info(f"User data deleted: user_id={user_id}")
    except Exception as e:
        logger.error(f"Data deletion failed for user_id={user_id}: {e}")
        await update.message.reply_text("⚠️ An error occurred. Please contact support.")
```

### 13.4 GDPR Compliance Checklist

- [ ] Privacy policy available to users
- [ ] Consent mechanism for data collection
- [ ] Data minimization applied
- [ ] Right to deletion implemented (`/deletedata`)
- [ ] Data export implemented (`/mydata`)
- [ ] Data retention policy defined and enforced
- [ ] Third-party data sharing disclosed
- [ ] Data processing records maintained

---

## 14. Mini App / Web App Security

### 14.1 initData Validation (CRITICAL)

The `initData` from Telegram Mini Apps contains user identity information. **It MUST be validated server-side.**

### 14.2 HMAC-SHA256 Validation

```python
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, unquote

BOT_TOKEN = os.environ["BOT_TOKEN"]


def validate_webapp_initdata(init_data: str, bot_token: str) -> dict:
    """Validate Telegram Mini App initData.

    Args:
        init_data: The initData string from the Mini App.
        bot_token: The bot's token.

    Returns:
        Parsed and validated data dictionary.

    Raises:
        ValueError: If validation fails.
    """
    # Parse the initData as URL-encoded form data
    parsed = parse_qs(init_data)

    # Extract and remove the hash
    if "hash" not in parsed:
        raise ValueError("Missing hash in initData")

    received_hash = parsed.pop("hash")[0]

    # Sort remaining parameters and create data-check-string
    data_check_pairs = []
    for key, values in sorted(parsed.items()):
        for value in values:
            data_check_pairs.append(f"{key}={value}")

    data_check_string = "\n".join(data_check_pairs)

    # Create secret key from bot token using HMAC-SHA256
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    # Compute expected hash
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Compare hashes (constant-time comparison)
    if not hmac.compare_digest(received_hash, expected_hash):
        raise ValueError("Invalid initData hash")

    # Check auth_date freshness (within 24 hours)
    auth_date = int(parsed.get("auth_date", [0])[0])
    if time.time() - auth_date > 86400:
        raise ValueError("initData expired (auth_date > 24 hours old)")

    # Parse and return validated data
    result = {}
    for key, values in parsed.items():
        result[key] = values[0] if len(values) == 1 else values

    return result


# Usage in FastAPI endpoint
@app.post("/api/validate-session")
async def validate_session(request: Request):
    body = await request.json()
    init_data = body.get("init_data")

    try:
        validated = validate_webapp_initdata(init_data, BOT_TOKEN)
        user_id = json.loads(validated.get("user", "{}")).get("id")

        return {"valid": True, "user_id": user_id}
    except ValueError as e:
        return {"valid": False, "error": str(e)}
```

### 14.3 Mini App Security Checklist

| Requirement | Priority | Implementation |
|------------|----------|----------------|
| Server-side `initData` validation | **CRITICAL** | HMAC-SHA256 verification |
| `auth_date` freshness check | **CRITICAL** | Reject if >24 hours old |
| HTTPS for Mini App URL | **CRITICAL** | Configure in BotFather |
| Origin header validation | HIGH | Check against allowed origins |
| Content Security Policy | HIGH | Restrict script sources |
| CORS configuration | HIGH | Restrict to trusted origins |
| Rate limiting on API endpoints | HIGH | Per-user and global limits |
| Input validation on all endpoints | HIGH | Validate all request data |

### 14.4 Secure Mini App Backend

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Restrict CORS to your bot's domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
    max_age=60,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response
```

---

## 15. Business Bot Risks

### 15.1 Business Connection Security

When using Telegram Business features:

| Risk | Mitigation |
|------|-----------|
| Unauthorized business connections | Verify business connection token |
| Message impersonation | Clearly identify bot-generated messages |
| Data access scope | Request minimum necessary permissions |
| Third-party integration | Audit third-party connectors regularly |
| Customer data exposure | Encrypt business conversation data |

### 15.2 Bot Access Settings

```python
# Configure bot privacy and group access via BotFather
# /setprivacy — Controls whether bot sees all messages or only commands
# /setjoingroups — Controls whether bot can be added to groups
# /setmenulocation — Controls bot menu visibility

# Best practices:
# 1. Set privacy to ENABLED unless you need all messages
# 2. Disable group addition if bot is user-only
# 3. Review connected groups regularly
```

---

## 16. Dependency Security

### 16.1 Pin Dependencies

```txt
# requirements.txt — pin exact versions
python-telegram-bot==21.6
aiohttp==3.10.5
cryptography==43.0.0
python-dotenv==1.0.1
```

### 16.2 Dependency Auditing

```bash
# Install and run pip-audit
pip install pip-audit
pip-audit

# Or use safety
pip install safety
safety check

# Generate requirements with hashes
pip install pip-tools
pip-compile --generate-hashes requirements.in -o requirements.txt
```

### 16.3 Supply Chain Attack Prevention

```bash
# Use --require-hashes to verify package integrity
pip install --require-hashes -r requirements.txt

# Verify package signatures (when available)
pip install --require-hashes --no-deps <package>
```

### 16.4 Automated Dependency Updates

```yaml
# Example: Dependabot configuration (.github/dependabot.yml)
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## 17. Secure Deployment Checklist

| # | Item | Priority | Status |
|---|------|----------|--------|
| 1 | Bot token stored in environment variable | CRITICAL | ☐ |
| 2 | `.env` file in `.gitignore` | CRITICAL | ☐ |
| 3 | `.env.example` with placeholder values committed | LOW | ☐ |
| 4 | Separate tokens for dev/staging/production | CRITICAL | ☐ |
| 5 | HTTPS enabled for webhooks | CRITICAL | ☐ |
| 6 | Webhook `secret_token` configured | HIGH | ☐ |
| 7 | `X-Telegram-Bot-Api-Secret-Token` header validated | HIGH | ☐ |
| 8 | All user input validated and sanitized | HIGH | ☐ |
| 9 | HTML/Markdown injection prevention | HIGH | ☐ |
| 10 | Per-user rate limiting implemented | HIGH | ☐ |
| 11 | RetryAfter exception handled | HIGH | ☐ |
| 12 | Admin access verified server-side | HIGH | ☐ |
| 13 | Callback data validated before processing | HIGH | ☐ |
| 14 | Deep link payloads validated | HIGH | ☐ |
| 15 | Mini App `initData` validated server-side | HIGH | ☐ |
| 16 | File downloads size-limited | MEDIUM | ☐ |
| 17 | File MIME types verified | MEDIUM | ☐ |
| 18 | Error handling catches all exceptions | MEDIUM | ☐ |
| 19 | Sensitive data filtered from logs | MEDIUM | ☐ |
| 20 | Structured logging implemented | MEDIUM | ☐ |
| 21 | Log retention policy defined | MEDIUM | ☐ |
| 22 | Dependency versions pinned | MEDIUM | ☐ |
| 23 | `pip-audit` run before deployment | MEDIUM | ☐ |
| 24 | External API call timeouts configured | MEDIUM | ☐ |
| 25 | Conversation timeouts configured | MEDIUM | ☐ |
| 26 | Anti-spam measures active in groups | MEDIUM | ☐ |
| 27 | GDPR compliance (deletion, export) | LOW | ☐ |
| 28 | PII data minimization applied | LOW | ☐ |
| 29 | Encryption at rest for sensitive data | LOW | ☐ |
| 30 | Security headers on web endpoints | LOW | ☐ |

---

## 18. OWASP Top 10 Mapping

This section maps the [OWASP Top 10 (2021)](https://owasp.org/Top10/) to Telegram bot-specific risks and mitigations.

### A01: Broken Access Control

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| User impersonation via forged `user_id` | Verify user identity server-side |
| Unauthorized admin commands | Admin verification decorator |
| Accessing other users' data | Per-user data isolation |
| Escalating privileges | Role-based access control |

**Relevant sections:** [6. Authorization & Access Control](#6-authorization--access-control)

### A02: Cryptographic Failures

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Bot token exposure | Environment variables, never in code |
| Unencrypted webhook traffic | HTTPS mandatory |
| Weak webhook secret | Use cryptographically random secrets |
| Data at rest not encrypted | Encrypt sensitive stored data |

**Relevant sections:** [1. Token Security](#1-token-security-critical), [2. Secrets Management](#2-secrets-management)

### A03: Injection

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| HTML injection in messages | Escape user input with `html.escape()` |
| MarkdownV2 injection | Escape special characters |
| SQL injection (if using database) | Parameterized queries |
| Command injection via deep links | Whitelist-based action mapping |

**Relevant sections:** [3. Input Validation](#3-input-validation--sanitization), [4. HTML/Markdown Injection](#4-htmlmarkdown-injection)

### A04: Insecure Design

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| No rate limiting | Token bucket / sliding window |
| No conversation timeouts | Set `conversation_timeout` |
| No DoS protection | Processing time limits, semaphore |
| No anti-spam measures | Spam detection and response |

**Relevant sections:** [5. Rate Limiting](#5-rate-limiting--flood-protection), [10. Spam Prevention](#10-spam-prevention), [11. DoS Protection](#11-dos-protection)

### A05: Security Misconfiguration

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Default webhook URLs (HTTP) | Use HTTPS with valid certificate |
| Secrets in source code | Environment variables |
| Verbose error messages in production | Custom error handlers |
| Missing security headers | Add CSP, HSTS, etc. |

**Relevant sections:** [2. Secrets Management](#2-secrets-management), [8. Webhook Security](#8-webhook-security)

### A06: Vulnerable and Outdated Components

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Outdated `python-telegram-bot` | Pin versions, use Dependabot |
| Vulnerable transitive dependencies | `pip-audit`, `safety check` |
| Supply chain attacks | Hash verification |

**Relevant sections:** [16. Dependency Security](#16-dependency-security)

### A07: Identification and Authentication Failures

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Webhook not authenticated | Validate `secret_token` header |
| Mini App `initData` not validated | HMAC-SHA256 server-side validation |
| `auth_date` staleness | Reject `initData` older than 24h |

**Relevant sections:** [8. Webhook Security](#8-webhook-security), [14. Mini App Security](#14-mini-app--web-app-security)

### A08: Software and Data Integrity Failures

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Tampered callback data | HMAC integrity checking |
| Tampered `initData` | Cryptographic validation |
| Tampered deep link payloads | Signature verification |
| Untested dependency updates | CI/CD security scanning |

**Relevant sections:** [7. Callback Data Security](#7-callback-data-security), [14. Mini App Security](#14-mini-app--web-app-security)

### A09: Security Logging and Monitoring Failures

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Tokens in logs | Sensitive data filter |
| PII in logs | Redaction in production |
| No audit trail | Structured logging with user context |
| No alerting on suspicious activity | Rate limit alerts, spam alerts |

**Relevant sections:** [12. Logging Security](#12-logging-security)

### A10: Server-Side Request Forgery (SSRF)

| Bot-Specific Risk | Mitigation |
|-------------------|-----------|
| Bot fetching arbitrary URLs | Validate URL schemes (http/https only) |
| Bot downloading from internal networks | Restrict to public URLs |
| File download exploitation | Size limits, MIME type checks |
| URL-based bot commands | Allowlist of approved domains |

**Relevant sections:** [3.5 File Download Validation](#35-file-download-validation), [11. DoS Protection](#11-dos-protection)

---

## 19. Severity Ratings

| # | Security Concern | Severity | Impact | Likelihood | Mitigation |
|---|-----------------|----------|--------|------------|------------|
| 1 | Token hardcoded in source | CRITICAL | Full bot compromise | High | Environment variables |
| 2 | Token committed to version control | CRITICAL | Full bot compromise | Medium | .gitignore + revoke token |
| 3 | No webhook authentication | CRITICAL | Forged updates injected | Medium | secret_token validation |
| 4 | Mini App `initData` not validated | CRITICAL | User impersonation | High | HMAC-SHA256 validation |
| 5 | No input validation | HIGH | Injection attacks, errors | High | Validate all inputs |
| 6 | HTML/Markdown injection | HIGH | Message manipulation | High | Escape user text |
| 7 | No rate limiting | HIGH | Bot abuse, API bans | High | Token bucket limiter |
| 8 | No authorization checks | HIGH | Privilege escalation | High | Admin verification |
| 9 | Callback data not validated | HIGH | Unexpected behavior | Medium | Pattern validation |
| 10 | Deep link abuse | HIGH | Unintended actions | Medium | Payload validation |
| 11 | No anti-spam measures | MEDIUM | Group pollution | Medium | Spam detection |
| 12 | Tokens in logs | MEDIUM | Token leakage | Medium | Sensitive data filter |
| 13 | PII stored unnecessarily | MEDIUM | Privacy violations | Low | Data minimization |
| 14 | No file size limits | MEDIUM | DoS, resource exhaustion | Low | Download limits |
| 15 | Unpinned dependencies | MEDIUM | Supply chain attacks | Low | Pin + audit deps |
| 16 | No error handling | MEDIUM | Information disclosure | Medium | Custom error handlers |
| 17 | No HTTPS on webhooks | CRITICAL | Token interception | Low | Force HTTPS |
| 18 | Conversation timeouts missing | LOW | Resource exhaustion | Low | Set timeouts |
| 19 | No log retention policy | LOW | Storage bloat, compliance | Low | Automate cleanup |
| 20 | No GDPR compliance | LOW | Legal penalties | Varies | Implement rights |

---

## 20. Copy-Paste Security Checklist

> Copy this checklist and paste it into your project's security review document. Check each item before deploying to production.

```markdown
## Bot Security Pre-Deployment Checklist

### Token Security
- [ ] Bot token is NOT hardcoded in any source file
- [ ] Bot token is loaded from environment variable
- [ ] Bot token is NOT committed to version control
- [ ] `.env` is in `.gitignore`
- [ ] Separate tokens for dev/staging/production
- [ ] Old tokens revoked if compromised

### Webhook Security
- [ ] HTTPS enabled with valid certificate
- [ ] `secret_token` passed to `set_webhook()`
- [ ] `X-Telegram-Bot-Api-Secret-Token` header validated on every request
- [ ] Webhook endpoint returns 200 within 30 seconds
- [ ] Error responses don't expose internal details

### Input Validation
- [ ] All user text input validated for length and content
- [ ] `callback_data` validated before processing
- [ ] Deep link payloads validated
- [ ] File downloads size-limited
- [ ] File MIME types verified server-side

### Injection Prevention
- [ ] User text escaped before HTML `parse_mode` insertion
- [ ] User text escaped before MarkdownV2 `parse_mode` insertion
- [ ] Parameterized queries for all database operations
- [ ] No `eval()`, `exec()`, or `__import__()` on user input

### Rate Limiting
- [ ] Per-user rate limiting implemented
- [ ] Telegram `RetryAfter` exception handled
- [ ] Global rate limiting in place
- [ ] Conversation timeouts configured

### Access Control
- [ ] Admin commands verify user identity server-side
- [ ] User ID not trusted from client-side data alone
- [ ] Role-based access control for sensitive operations
- [ ] Chat membership verified for group bots

### Logging
- [ ] Bot tokens NEVER appear in logs
- [ ] PII redacted in production logs
- [ ] Structured logging implemented
- [ ] Log retention policy defined

### Dependencies
- [ ] All dependency versions pinned
- [ ] `pip-audit` or `safety check` run and passed
- [ ] No known vulnerabilities in dependencies
- [ ] Regular dependency update schedule

### Mini App (if applicable)
- [ ] `initData` validated server-side (HMAC-SHA256)
- [ ] `auth_date` freshness checked (<24 hours)
- [ ] HTTPS for Mini App URL
- [ ] CORS restricted to trusted origins

### Privacy & Compliance
- [ ] Only necessary user data collected
- [ ] Data deletion endpoint available (`/deletedata`)
- [ ] Data export endpoint available (`/mydata`)
- [ ] Privacy policy accessible to users
- [ ] Data retention policy enforced

### Error Handling
- [ ] Global error handler catches all exceptions
- [ ] Error responses don't leak stack traces or tokens
- [ ] Graceful degradation on external service failures
```

---

## Quick Reference: Security Commands

```bash
# Audit dependencies
pip-audit
safety check

# Check for hardcoded secrets in codebase
# (install trufflehog or gitleaks)
trufflehog filesystem --directory .
gitleaks detect

# Verify .env is gitignored
git check-ignore .env

# Check for tokens in git history
git log --all --full-history --source -S "BOT_TOKEN" -- "*.py" "*.env" "*.yml"

# Generate hashed requirements
pip-compile --generate-hashes requirements.in

# Audit Docker images
docker scan your-bot-image:latest
```

---

> [!TIP]
> **Security is an ongoing process, not a one-time task.** Review this checklist regularly, especially when:
> - Adding new features or handlers
> - Updating dependencies
> - Changing deployment infrastructure
> - Onboarding new team members
> - After any security incident

---

*This chapter provides a comprehensive security baseline. Adapt severity levels and mitigations to your specific use case, regulatory requirements, and risk tolerance.*
