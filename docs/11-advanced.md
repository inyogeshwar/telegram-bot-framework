# Chapter 11: Advanced Features

## Deep Linking

Deep links allow external systems — websites, QR codes, referral programs, apps — to open a Telegram bot with a **pre-filled command and payload**. This is the primary mechanism for connecting your bot to the world outside Telegram.

### Link Format

```
https://t.me/botname?start=PARAMETER
```

| Parameter | Max Length | Description |
|---|---|---|
| `start` | 64 chars | Starts a private chat with the bot, passing `PARAMETER` to `/start` |
| `startgroup` | 64 chars | Prompts user to add bot to a group, passing `PARAMETER` to `/start` |
| `startapp` | 64 chars | Launches a Telegram Mini App with the given parameter |

### Payload Constraints

- Maximum **64 characters** (including any encoding).
- Must be **base64-safe**: `[A-Za-z0-9_-]` only. No spaces, no `+`, no `/`, no `=`.
- The payload is passed as `context.args[0]` in your `/start` handler.

> [!TIP]
> Base64-encode complex payloads before passing them as the `start` parameter. Use URL-safe base64 (`base64.urlsafe_b64encode`) and strip trailing `=` padding to stay within the 64-char limit.

### Handling Deep Links in `/start`

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

REFERRAL_CODES: dict[str, int] = {}  # code → referrer_user_id
USER_PREFERENCES: dict[int, dict] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with optional deep link payload."""
    user = update.effective_user
    logger.info(
        "User %s (id=%d) started bot. args=%s",
        user.full_name,
        user.id,
        context.args,
    )

    if not context.args:
        await update.message.reply_text(
            f"Welcome, {user.first_name}!\n\n"
            "Use me for quick searches, translations, and more."
        )
        return

    payload = context.args[0]

    if payload.startswith("ref_"):
        await handle_referral(update, context, payload)
    elif payload.startswith("settings_"):
        await handle_settings_link(update, context, payload)
    elif payload.startswith("invite_"):
        await handle_invite(update, context, payload)
    else:
        await handle_generic_payload(update, context, payload)


async def handle_referral(
    update: Update, context: ContextTypes.DEFAULT_TYPE, payload: str
) -> None:
    """Process referral deep link: ref_ABC123."""
    code = payload.removeprefix("ref_")
    referrer_id = REFERRAL_CODES.get(code)

    if referrer_id is None:
        await update.message.reply_text("Invalid or expired referral link.")
        return

    if referrer_id == update.effective_user.id:
        await update.message.reply_text("You cannot refer yourself!")
        return

    USER_PREFERENCES.setdefault(update.effective_user.id, {})["referred_by"] = referrer_id
    await update.message.reply_text(
        f"Welcome! You were referred by user #{referrer_id}.\n"
        "You both receive a bonus!"
    )
    logger.info(
        "Referral: user %d referred by %d (code=%s)",
        update.effective_user.id,
        referrer_id,
        code,
    )


async def handle_settings_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE, payload: str
) -> None:
    """Process settings deep link: settings_language_en."""
    settings = payload.removeprefix("settings_")

    if "_" not in settings:
        await update.message.reply_text("Invalid settings link.")
        return

    key, value = settings.split("_", maxsplit=1)
    USER_PREFERENCES.setdefault(update.effective_user.id, {})[key] = value
    await update.message.reply_text(f"Setting updated: {key} = {value}")


async def handle_invite(
    update: Update, context: ContextTypes.DEFAULT_TYPE, payload: str
) -> None:
    """Process group invite deep link: invite_GROUP_ID."""
    group_id = payload.removeprefix("invite_")
    await update.message.reply_text(
        f"Click to add me to your group:\n"
        f"https://t.me/{context.bot.username}?startgroup={group_id}"
    )


async def handle_generic_payload(
    update: Update, context: ContextTypes.DEFAULT_TYPE, payload: str
) -> None:
    """Handle unknown or generic deep link payloads."""
    await update.message.reply_text(
        f"Received payload: `{payload}`",
        parse_mode="Markdown",
    )
```

### Use Cases

| Use Case | Payload Example | Description |
|---|---|---|
| Referral tracking | `ref_AbCdEf` | Track which user referred a new user |
| Pre-filled actions | `search_python` | Auto-execute a search on bot start |
| QR code access | `qr_product_123` | Open product details from a scanned QR |
| Group onboarding | `invite_-100123` | Direct user to add bot to a specific group |
| Marketing campaigns | `promo_SUMMER26` | Track campaign attribution |

---

## Context Objects

The `ContextTypes.DEFAULT_TYPE` (defaulting to `CallbackContext`) is the second argument to every handler. It provides access to bot state, per-user data, per-chat data, and utility objects.

### ContextTypes.DEFAULT_TYPE Properties

| Property | Type | Description |
|---|---|---|
| `context.bot` | `Bot` | The bot instance — use for sending messages, making API calls |
| `context.bot_data` | `dict` | **Bot-wide** persistent data (shared across all users/chats) |
| `context.user_data` | `dict` | **Per-user** persistent data (unique to each user) |
| `context.chat_data` | `dict` | **Per-chat** persistent data (unique to each chat) |
| `context.args` | `list[str]` | Command arguments (split by spaces, only in `CommandHandler`) |
| `context.match` | `re.Match \| None` | Regex match object (only in `MessageHandler` with filters) |
| `context.job_queue` | `JobQueue` | Job queue for scheduling background tasks |
| `context.error` | `Exception` | The exception (only in error handlers) |
| `context.update` | `Update` | The full update object |
| `context.application` | `Application` | The Application instance |

### Using Context Data

```python
from telegram import Update
from telegram.ext import ContextTypes

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Per-user data: persists across handler calls for this user
    context.user_data.setdefault("visit_count", 0)
    context.user_data["visit_count"] += 1
    await update.message.reply_text(
        f"This is visit #{context.user_data['visit_count']}"
    )

    # Bot-wide data: shared across all users
    context.bot_data.setdefault("total_visits", 0)
    context.bot_data["total_visits"] += 1

    # Per-chat data: shared across all users in a chat
    if update.effective_chat.type in ("group", "supergroup"):
        context.chat_data.setdefault("messages_today", 0)
        context.chat_data["messages_today"] += 1
```

### Persisting Data

Without a persistence backend, all `*_data` dictionaries are lost when the bot restarts. Use `PicklePersistence` or `DictPersistence` to survive restarts.

#### PicklePersistence

```python
from telegram.ext import ApplicationBuilder, PicklePersistence

persistence = PicklePersistence(filepath="bot_data.pkl")

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .persistence(persistence)
    .build()
)

# Data is now automatically saved and loaded on restart
# context.user_data, context.bot_data, context.chat_data
# are persisted to bot_data.pkl after each update
```

#### DictPersistence (for testing)

```python
from telegram.ext import ApplicationBuilder, DictPersistence

persistence = DictPersistence()

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .persistence(persistence)
    .build()
)

# Data lives in memory — lost on restart
# Useful for unit testing and development
```

> [!WARNING]
> `PicklePersistence` uses `pickle` for serialization. Do **not** store unpicklable objects (database connections, file handles, async locks) in `user_data` or `bot_data`. Use serializable types only.

---

## Job Queue & Background Tasks

`JobQueue` enables scheduling tasks that run independently of user interactions: reminders, periodic messages, cleanup jobs, and timeout checks.

### Setup

`JobQueue` is available via `context.job_queue` in any handler. It requires the `job-queue` extra:

```bash
pip install python-telegram-bot[job-queue]
```

### Scheduling Patterns

#### run_once — One-Shot Task

Execute a callback after a fixed delay.

```python
from datetime import timedelta
from telegram import Update
from telegram.ext import ContextTypes

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a 1-hour reminder."""
    if not context.args:
        await update.message.reply_text("Usage: /remind <seconds>")
        return

    seconds = int(context.args[0])
    chat_id = update.effective_chat.id

    context.job_queue.run_once(
        callback=send_reminder,
        when=timedelta(seconds=seconds),
        data={
            "chat_id": chat_id,
            "user_id": update.effective_user.id,
            "message": f"⏰ Reminder requested by {update.effective_user.first_name}!",
        },
        name=f"reminder_{update.effective_user.id}_{chat_id}",
    )

    await update.message.reply_text(f"Reminder set for {seconds} seconds from now.")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback executed by the job queue."""
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=data["message"],
    )
```

#### run_repeating — Periodic Task

Execute a callback at fixed intervals.

```python
from telegram.ext import ContextTypes

async def cleanup_old_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs every 30 minutes to clean up old messages."""
    # Perform cleanup logic
    deleted = await context.bot.delete_messages(chat_id=-100123456, limit=100)
    context.job.logger.info("Cleaned up %d messages", deleted)


def schedule_cleanup(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Schedule the cleanup job (called from /start)."""
    context.job_queue.run_repeating(
        callback=cleanup_old_messages,
        interval=1800,  # 30 minutes in seconds
        first=60,       # Start after 1 minute
        name="message_cleanup",
    )
```

#### run_daily — Daily Recurring Task

Execute a callback at a specific time every day.

```python
from datetime import time, timezone
from telegram.ext import ContextTypes

async def daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily report to the admin channel."""
    stats = collect_daily_stats()
    await context.bot.send_message(
        chat_id=-100987654,
        text=(
            f"📊 *Daily Report*\n\n"
            f"Users: {stats['active_users']}\n"
            f"Messages: {stats['total_messages']}\n"
            f"Errors: {stats['error_count']}"
        ),
        parse_mode="Markdown",
    )


def setup_daily_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set up daily scheduled tasks."""
    context.job_queue.run_daily(
        callback=daily_report,
        time=time(hour=9, minute=0, tzinfo=timezone.utc),  # 09:00 UTC
        name="daily_report",
    )
```

### Job Properties

| Property | Type | Description |
|---|---|---|
| `context.job.name` | `str` | Unique job name |
| `context.job.chat_id` | `int \| None` | Chat ID (set automatically if job created from a chat context) |
| `context.job.user_id` | `int \| None` | User ID (set automatically) |
| `context.job.data` | `Any` | Arbitrary data passed when creating the job |
| `context.job.job_queue` | `JobQueue` | Reference back to the job queue |

### Cancelling Jobs

```python
from telegram import Update
from telegram.ext import ContextTypes

async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel all reminders for the current user in this chat."""
    current_jobs = context.job_queue.get_jobs_by_name(
        f"reminder_{update.effective_user.id}_{update.effective_chat.id}"
    )

    if not current_jobs:
        await update.message.reply_text("No active reminders to cancel.")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text(f"Cancelled {len(current_jobs)} reminder(s).")
```

### Error Handling in Jobs

Jobs silently fail if the callback raises an exception. Always handle errors within the callback or use a wrapper:

```python
import functools
import logging
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def job_error_handler(func):
    """Decorator to catch and log errors in job callbacks."""
    @functools.wraps(func)
    async def wrapper(context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(context)
        except Exception as e:
            logger.error("Job '%s' failed: %s", context.job.name, e, exc_info=True)
    return wrapper


@job_error_handler
async def safe_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reminder with automatic error handling."""
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=data["message"],
    )
```

### Use Cases

| Pattern | Use Case |
|---|---|
| `run_once` | Reminders, timeouts, delayed messages |
| `run_repeating` | Status updates, cleanup tasks, monitoring |
| `run_daily` | Reports, daily digests, scheduled announcements |

---

## Ephemeral Messages

Ephemeral messages let the bot send **private responses to a specific user** within a group chat. Other users in the group do not see these messages.

> [!NOTE]
> Available in **python-telegram-bot v10.2+** and Telegram Bot API **6.1+**.

### Sending Ephemeral Messages

```python
from telegram import Update
from telegram.ext import ContextTypes

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a private response in a group chat."""
    if update.message is None:
        return

    # Only works in groups/supergroups
    if update.effective_chat.type not in ("group", "supergroup"):
        await update.message.reply_text("This command is for groups only.")
        return

    await update.message.reply_text(
        text="This message is only visible to you!",
        # No special parameter needed — reply_text in groups is visible to all.
        # Ephemeral messages are sent via callback_query responses.
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to a button press with an ephemeral message."""
    query = update.callback_query
    await query.answer(
        text="✅ Action completed (only you can see this)",
        show_alert=True,  # Makes it a popup (always ephemeral)
    )
```

### Callback Query Ephemeral Responses

When a user presses an inline button, `callback_query.answer()` can send a toast notification or popup that **only the pressing user sees**:

```python
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge without message

    # Or show a popup (ephemeral — only the pressing user sees it)
    await query.answer(
        text="Processing your request...",
        show_alert=True,
    )
```

### Limitations

- The 15-second window applies to **all** responses to a callback query — send ephemeral messages promptly.
- Ephemeral messages are **not guaranteed** delivery if the user has certain privacy settings.
- Not all message types support ephemeral delivery.

---

## Bot-to-Bot Communication

Bots can send messages to other bots, enabling orchestration, microservices, and multi-bot workflows.

> [!NOTE]
> Available in **python-telegram-bot v10.0+** and Telegram Bot API **6.0+**.

### Enabling Bot-to-Bot Communication

1. Open a chat with **@BotFather**.
2. Send `/mybots` → select your bot.
3. Navigate to **Bot Settings** → **Group Privacy** → **Turn off** (both bots need this).
4. Both bots must be added to the **same group** (or you can send messages by username in private chats).

### Sending Messages Between Bots

```python
from telegram import Update
from telegram.ext import ContextTypes

async def forward_to_analytics(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Forward a user event to the analytics bot."""
    event = {
        "user_id": update.effective_user.id,
        "chat_id": update.effective_chat.id,
        "message": update.message.text,
    }

    # Send to another bot by username (both bots must be in the same group,
    # or this must be a private chat with the target bot)
    await context.bot.send_message(
        chat_id="@analytics_bot",
        text=f"EVENT: {event}",
    )
```

### Use Cases

| Pattern | Description |
|---|---|
| Bot orchestration | A coordinator bot delegates tasks to specialized bots |
| Microservices | Each bot handles a domain (payments, auth, notifications) |
| Logging bot | A dedicated bot receives and stores all events |
| Moderation delegation | One bot detects issues, another handles enforcement |

> [!WARNING]
> Bot-to-bot communication is not a true IPC mechanism. Messages go through Telegram's servers and are subject to rate limits and delivery delays. For tightly coupled communication, consider direct HTTP calls between your services instead.

---

## Local Bot API Server

The local Bot API server lets you run Telegram's Bot API locally, bypassing the 50 MB file size limit and gaining additional features.

### When to Use

- Your bot handles **files larger than 50 MB** (the standard API limit).
- You need **HTTP webhooks** with custom certificates.
- You need **more simultaneous connections** to Telegram's servers.
- You want to reduce **latency** for high-traffic bots.

### Setup

```bash
# Clone and build the local Bot API server
git clone https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
mkdir build && cd build
cmake ..
cmake --build . --target telegram-bot-api -j2
```

### Running the Server

```bash
./telegram-bot-api \
    --api-id=YOUR_API_ID \
    --api-hash=YOUR_API_HASH \
    --http-port=8081 \
    --local
```

### Connecting Your Bot

```python
from telegram import Bot
from telegram.ext import ApplicationBuilder

# Point your bot to the local server
app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .base_url("http://localhost:8081/bot")
    .build()
)
```

### Benefits and Limitations

| Feature | Standard API | Local API Server |
|---|---|---|
| Max file size | 50 MB | 2 GB |
| Max download | 20 MB | 2 GB |
| Webhook certs | Limited | Custom certificates |
| Simultaneous connections | 400 | Higher (configurable) |
| Self-hosted | No | Yes |
| File download speed | Telegram servers | Local network |
| Requires API credentials | Bot token only | API ID + hash + bot token |
| Maintenance overhead | None | Server management |

> [!TIP]
> For most bots, the standard API is sufficient. Only deploy the local Bot API server when you specifically need larger file support or are operating at a scale where connection limits become a bottleneck.

---

## Communities

Communities are groups of supergroups and channels managed together. Bots in communities receive special service messages.

### Community Service Messages

| Event | Handler | Description |
|---|---|---|
| Bot added to community | `ChatMemberHandler` | A community added the bot |
| Bot removed from community | `ChatMemberHandler` | A community removed the bot |

```python
from telegram import Update
from telegram.ext import ContextTypes

async def community_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle bot being added/removed from a community."""
    status = update.chat_member.new_chat_member.status
    old_status = update.chat_member.old_chat_member.status

    if status == "member" and old_status != "member":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 I've joined this community! Available commands: /help",
        )
    elif status != "member" and old_status == "member":
        # Bot was removed — cleanup persistent data if needed
        context.chat_data.clear()
```

---

## Rich Messages

Rich messages provide structured, formatted content beyond plain text and Markdown. They support block-level elements like paragraphs, headings, lists, tables, and code blocks.

> [!NOTE]
> Available in **python-telegram-bot v10.1+** and Telegram Bot API **8.0+**.

### sendRichMessage

```python
from telegram import Update
from telegram.rich import (
    RichMessage,
    Block,
    Paragraph,
    Heading,
    List,
    ListItem,
    CodeBlock,
    Table,
    TableRow,
    TableCell,
    InlineStyle,
    Bold,
    Italic,
    Link,
)

async def rich_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a rich message with structured blocks."""
    rich = RichMessage(blocks=[
        Heading(level=2, text="Project Status"),
        Paragraph(blocks=[
            InlineStyle(text="All systems "),
            Bold(text="operational"),
            InlineStyle(text=". Last check: "),
            InlineStyle(text="2026-07-26 10:30 UTC", italic=True),
        ]),
        Heading(level=3, text="Service Health"),
        Table(rows=[
            TableRow(cells=[
                TableCell(text="Service", bold=True),
                TableCell(text="Status", bold=True),
                TableCell(text="Latency", bold=True),
            ]),
            TableRow(cells=[
                TableCell(text="API Gateway"),
                TableCell(text="✅ Up"),
                TableCell(text="12ms"),
            ]),
            TableRow(cells=[
                TableCell(text="Database"),
                TableCell(text="✅ Up"),
                TableCell(text="3ms"),
            ]),
            TableRow(cells=[
                TableCell(text="Worker Pool"),
                TableCell(text="⚠️ Degraded"),
                TableCell(text="245ms"),
            ]),
        ]),
        Heading(level=3, text="Recent Changes"),
        List(items=[
            ListItem(text="Deployed v2.4.1 — bug fixes"),
            ListItem(text="Updated rate limiting config"),
            ListItem(text="Added community support"),
        ]),
    ])

    await update.message.reply_rich_message(rich)
```

### sendRichMessageDraft for Streaming AI Responses

When building AI-powered bots, you can stream partial responses as the AI generates them:

```python
from telegram import Update
from telegram.rich import RichMessage, Block, Paragraph, CodeBlock
from telegram.ext import ContextTypes

async def ai_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle an AI query with streaming response."""
    query = update.message.text

    # Create a draft that can be updated incrementally
    draft = await update.message.reply_rich_message_draft(
        blocks=[Paragraph(text="Thinking...")]
    )

    collected = ""
    async for chunk in stream_ai_response(query):
        collected += chunk
        # Update the draft with the latest content
        await draft.edit(blocks=[
            Paragraph(text=collected),
            Paragraph(text="_Generating..._", italic=True) if not is_complete else [],
        ])

    # Finalize with the complete response
    await draft.edit(blocks=[
        Paragraph(text=collected),
    ])
```

### Block Types Reference

| Block Type | Description | Key Parameters |
|---|---|---|
| `Paragraph` | Text block with inline styles | `blocks`, `text` |
| `Heading` | Section heading | `text`, `level` (1-6) |
| `List` | Bulleted or numbered list | `items`, `ordered` |
| `ListItem` | Single list entry | `text`, `blocks` |
| `CodeBlock` | Syntax-highlighted code | `text`, `language` |
| `Table` | Data table | `rows` |
| `TableRow` | Table row | `cells` |
| `TableCell` | Table cell | `text`, `bold`, `italic` |
| `Blockquote` | Quoted text | `blocks` |
| `Divider` | Horizontal rule | — |

### Inline Styles

| Style | Description |
|---|---|
| `Bold(text=...)` | Bold text |
| `Italic(text=...)` | Italic text |
| `Underline(text=...)` | Underlined text |
| `Strikethrough(text=...)` | Strikethrough text |
| `Spoiler(text=...)` | Spoiler (tap to reveal) |
| `Code(text=...)` | Inline monospace code |
| `Link(text=..., url=...)` | Clickable hyperlink |
| `Mention(text=..., user_id=...)` | Mention a user by ID |
| `CustomEmoji(text=..., emoji_id=...)` | Custom emoji by sticker ID |

---

## Persistence

Persistence ensures that `user_data`, `bot_data`, and `chat_data` survive bot restarts.

### Persistence Backends

| Backend | Storage | Use Case |
|---|---|---|
| `PicklePersistence` | File (pickle) | Production bots — simple, reliable |
| `DictPersistence` | In-memory (dict) | Testing and development |
| `PostgresPersistence` | PostgreSQL | High-concurrency production bots |
| `MongoPersistence` | MongoDB | Document-oriented storage |

### Configuring Persistence

```python
from telegram.ext import ApplicationBuilder, PicklePersistence

# Create persistence with custom filepath
persistence = PicklePersistence(
    filepath="bot_data.pkl",
    store_bot_data=True,      # Persist context.bot_data
    store_chat_data=True,      # Persist context.chat_data
    store_user_data=True,      # Persist context.user_data
    collect_files=False,       # Don't persist file objects
)

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .persistence(persistence)
    .build()
)
```

### What Gets Persisted

| Data Store | Scope | Example Use |
|---|---|---|
| `context.user_data` | Per user | Preferences, settings, conversation state |
| `context.chat_data` | Per chat | Group-specific counters, rules |
| `context.bot_data` | Global | Shared configuration, statistics |

> [!CAUTION]
> `PicklePersistence` uses Python's `pickle` module. **Never** store non-serializable objects (database connections, threads, locks). Store only simple types: `dict`, `list`, `str`, `int`, `float`, `bool`, `None`.

### Using Persistence in Handlers

```python
from telegram import Update
from telegram.ext import ContextTypes

async def save_preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save a user preference — automatically persisted."""
    if not context.args:
        await update.message.reply_text("Usage: /setpref <key> <value>")
        return

    key, value = context.args[0], " ".join(context.args[1:])
    context.user_data[key] = value  # Automatically saved on update completion
    await update.message.reply_text(f"Saved: {key} = {value}")


async def get_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieve user preferences — loaded from persistence."""
    if not context.user_data:
        await update.message.reply_text("No preferences saved yet.")
        return

    prefs = "\n".join(f"• {k}: {v}" for k, v in context.user_data.items())
    await update.message.reply_text(f"Your preferences:\n{prefs}")
```

---

## Bot Commands Menu

The commands menu is the popup that appears when a user types `/` in a chat with your bot. You can programmatically register which commands appear, scoped by user, chat, and language.

### Registering Commands

```python
from telegram import BotCommand, BotCommandScopeDefault

async def set_bot_commands(bot) -> None:
    """Set the default commands shown in the / menu."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
        BotCommand("search", "Search for something"),
        BotCommand("settings", "Open settings"),
        BotCommand("lang", "Change language"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    print("Bot commands set successfully.")
```

### BotCommandScope

Scoping lets you show **different commands** to different users or chats.

| Scope | Description |
|---|---|
| `BotCommandScopeDefault` | Default for all users (fallback) |
| `BotCommandScopeAllPrivateChats` | All private chats |
| `BotCommandScopeAllGroupChats` | All group chats |
| `BotCommandScopeAllChatAdministrators` | Admins in any chat |
| `BotCommandScopeChat(chat_id)` | Specific chat |
| `BotCommandScopeChatAdministrators(chat_id)` | Admins in a specific chat |
| `BotCommandScopeChatMember(chat_id, user_id)` | Specific user in a specific chat |
| `BotCommandScopeAllGroupAdministrators` | Admins in all group chats |
| `BotCommandScopePeerUser(peer_user_id)` | Specific user |

### Per-Language Commands

```python
from telegram import BotCommand, BotCommandScopeAllPrivateChats

# English commands
await bot.set_my_commands(
    commands=[
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
    ],
    language_code="en",
    scope=BotCommandScopeAllPrivateChats(),
)

# Spanish commands
await bot.set_my_commands(
    commands=[
        BotCommand("start", "Iniciar el bot"),
        BotCommand("help", "Mostrar ayuda"),
    ],
    language_code="es",
    scope=BotCommandScopeAllPrivateChats(),
)
```

### Admin-Only Commands

```python
from telegram import BotCommand, BotCommandScopeChatAdministrators

ADMIN_CHAT_ID = -100123456789

await bot.set_my_commands(
    commands=[
        BotCommand("ban", "Ban a user"),
        BotCommand("mute", "Mute a user"),
        BotCommand("stats", "View group statistics"),
        BotCommand("config", "Group configuration"),
    ],
    scope=BotCommandScopeChatAdministrators(chat_id=ADMIN_CHAT_ID),
)
```

### Deleting Commands

```python
# Delete all commands for a specific language
await bot.delete_my_commands(language_code="es")

# Delete all commands for a specific scope
await bot.delete_my_commands(
    scope=BotCommandScopeChatAdministrators(chat_id=ADMIN_CHAT_ID)
)

# Delete default commands
await bot.delete_my_commands(scope=BotCommandScopeDefault())
```

---

## Rate Limiting

Telegram enforces strict rate limits on bot API calls. Exceeding these limits results in `429 Too Many Requests` errors and temporary bans.

### Official Limits

| Limit | Value | Description |
|---|---|---|
| Messages to different users | **30 messages/second** | Across all chats |
| Messages per chat | **1 message/second** | Per group or channel |
| Group creation | **1 group/minute** | Per bot |
| Inline queries | **30 queries/second** | Per bot |
| File downloads | **~1.5 GB/minute** | Per bot |
| File uploads (standard) | **50 MB per file** | Standard Bot API |
| File uploads (local API) | **2 GB per file** | Local Bot API server |

### Paid Broadcasts

For broadcast messages to large audiences, Telegram offers paid broadcasts at **0.1 Stars per message**, with a limit of **1000 messages/second**.

### Implementation Patterns

#### Token Bucket Algorithm

A token bucket controls the rate at which requests are made. Tokens are added at a fixed rate and consumed with each request.

```python
import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Rate limiter using the token bucket algorithm."""

    def __init__(self, max_tokens: int, refill_rate: float) -> None:
        """
        Args:
            max_tokens: Maximum burst size.
            refill_rate: Tokens added per second.
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = float(max_tokens)
        self.last_refill = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available, then consume it."""
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.refill_rate
                logger.debug("Rate limited — waiting %.2f seconds", wait_time)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


# Usage
limiter = TokenBucketRateLimiter(max_tokens=30, refill_rate=30.0)

async def safe_send_message(bot, chat_id: int, text: str) -> None:
    """Send a message with rate limiting."""
    await limiter.acquire()
    await bot.send_message(chat_id=chat_id, text=text)
```

#### Sliding Window Algorithm

A sliding window tracks requests within a rolling time window, providing smoother rate limiting than fixed windows.

```python
import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """Rate limiter using the sliding window algorithm."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: deque[float] = deque()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request can be made within the window."""
        while True:
            async with self.lock:
                now = time.monotonic()
                cutoff = now - self.window_seconds

                # Remove expired timestamps
                while self.timestamps and self.timestamps[0] < cutoff:
                    self.timestamps.popleft()

                if len(self.timestamps) < self.max_requests:
                    self.timestamps.append(now)
                    return

                # Calculate wait time until the oldest request expires
                wait_time = self.timestamps[0] + self.window_seconds - now
                logger.debug(
                    "Sliding window full — waiting %.2f seconds", wait_time
                )

            await asyncio.sleep(wait_time)
```

### python-telegram-bot Built-in Rate Limiter

The library provides a built-in rate limiter that can be configured on the `Application`:

```python
from telegram.ext import ApplicationBuilder, RateLimiter
from telegram.request import HTTPXRequest

# Create a custom HTTPXRequest with rate limiting
request = HTTPXRequest(
    connect_timeout=5.0,
    read_timeout=10.0,
)

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .request(request)
    .rate_limiter(RateLimiter())
    .build()
)
```

### Best Practices

| Practice | Description |
|---|---|
| **Batch sends** | Send to multiple users with a delay between each |
| **Retry with backoff** | On `429` errors, wait for the `Retry-After` header value |
| **Queue messages** | Use a queue with the rate limiter to smooth out bursts |
| **Monitor `Retry-After`** | Telegram tells you exactly how long to wait |
| **Use webhooks** | More efficient than polling for high-traffic bots |

### Handling 429 Errors

```python
import asyncio
import logging
from telegram.error import RetryAfter, TimedOut

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def resilient_send(bot, chat_id: int, text: str, retries: int = MAX_RETRIES) -> bool:
    """Send a message with automatic retry on rate limits."""
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=text)
            return True
        except RetryAfter as e:
            wait = e.retry_after
            logger.warning(
                "Rate limited (attempt %d/%d). Waiting %d seconds.",
                attempt + 1,
                retries,
                wait,
            )
            await asyncio.sleep(wait)
        except TimedOut:
            logger.warning("Request timed out (attempt %d/%d).", attempt + 1, retries)
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error("Unexpected error sending message: %s", e, exc_info=True)
            return False

    logger.error("Failed to send message after %d retries.", retries)
    return False
```
