# Chapter 5: Filters

Filters determine which updates a `MessageHandler` (or other handlers that support them) will process. A well-chosen filter prevents irrelevant updates from reaching your logic, keeps code clean, and reduces unnecessary processing.

---

## Table of Contents

- [What Are Filters](#what-are-filters)
- [Built-in Filters — Complete Reference](#built-in-filters--complete-reference)
- [Text and Command Filters](#text-and-command-filters)
- [Media Filters](#media-filters)
- [Status Update Filters](#status-update-filters)
- [Chat Type Filters](#chat-type-filters)
- [User Filters](#user-filters)
- [Message Content Filters](#message-content-filters)
- [Combined Filters](#combined-filters)
- [Custom Filters](#custom-filters)
- [Filter Evaluation and Priority](#filter-evaluation-and-priority)
- [Common Filter Combinations — Quick Reference](#common-filter-combinations--quick-reference)

---

## What Are Filters

Filters are boolean predicates evaluated against an incoming update. When used with `MessageHandler`, a filter determines whether the handler's callback is invoked for a given message.

```python
from telegram.ext import MessageHandler, filters

# Only handle text messages that are NOT commands
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
)
```

> [!IMPORTANT]
> Filters are used with `MessageHandler` and certain other handlers. `CommandHandler` already filters by command name — you do not pass a filter to it.

### How Filters Work Internally

A filter is any callable (or `filters.BaseFilter` subclass) that accepts a `Message` and returns `True` or `False`. The `filters` module provides a rich set of built-in filter objects that can be combined with logical operators.

```python
from telegram import Message

# The filter protocol (simplified)
class MyFilter:
    def __call__(self, update: Message) -> bool:
        return some_condition(update)

    def __invert__(self):
        """Supports ~ operator."""
        ...

    def __and__(self, other):
        """Supports & operator."""
        ...

    def __or__(self, other):
        """Supports | operator."""
        ...
```

---

## Built-in Filters — Complete Reference

All built-in filters are accessed via the `filters` namespace from `telegram.ext`.

### Text and Command Filters

| Filter | Matches | Type |
|---|---|---|
| `filters.TEXT` | Any text message (plain text and entities) | Content |
| `filters.COMMAND` | Messages starting with `/` | Content |
| `filters.Regex(pattern)` | Messages matching a regex (also sets `match` on `context`) | Content |
| `filters.Entity(type)` | Messages containing a specific entity type | Content |
| `filters.Entity(types)` | Messages containing any of the given entity types | Content |
| `filters.CaptionRegex(pattern)` | Photo/video/document captions matching a regex | Content |

#### `filters.TEXT`

```python
from telegram.ext import MessageHandler, filters

async def handle_text(update, context):
    await update.message.reply_text(f"You said: {update.message.text}")

application.add_handler(
    MessageHandler(filters.TEXT, handle_text)
)
```

#### `filters.COMMAND`

```python
# Match any message starting with /
application.add_handler(
    MessageHandler(filters.COMMAND, handle_any_command)
)
```

> [!NOTE]
> `filters.COMMAND` matches the raw text starting with `/`. `CommandHandler` performs additional parsing (extracting command name and arguments). Use `filters.COMMAND` only in `MessageHandler` when you need to intercept commands before `CommandHandler` processes them.

#### `filters.Regex`

`filters.Regex` wraps Python's `re.search`. When the filter matches, the match object is stored in `context.match`.

```python
import logging
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters

logger = logging.getLogger(__name__)

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    match = context.match
    email = match.group(0)
    logger.info("Extracted email: %s", email)
    await update.message.reply_text(f"Found email: {email}")

application.add_handler(
    MessageHandler(
        filters.Regex(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        handle_email,
    )
)
```

#### `filters.Entity`

Match messages containing specific entity types:

```python
from telegram import MessageEntityType
from telegram.ext import MessageHandler, filters

# Messages containing a URL
application.add_handler(
    MessageHandler(filters.Entity(MessageEntityType.URL), handle_url)
)

# Messages containing a phone number or email
application.add_handler(
    MessageHandler(
        filters.Entity([MessageEntityType.PHONE_NUMBER, MessageEntityType.EMAIL]),
        handle_contact_info,
    )
)
```

Available entity types (from `MessageEntityType`):

| Entity Type | Description |
|---|---|
| `MENTION` | @username mention |
| `HASHTAG` | #hashtag |
| `CASHTAG` | $CASHTAG |
| `BOT_COMMAND` | /command |
| `URL` | URL |
| `EMAIL` | Email address |
| `PHONE_NUMBER` | Phone number |
| `BOLD` | Bold text |
| `ITALIC` | Italic text |
| `UNDERLINE` | Underlined text |
| `STRIKETHROUGH` | Strikethrough text |
| `SPOILER` | Spoiler text |
| `CODE` | Inline code |
| `PRE` | Pre-formatted text |
| `TEXT_LINK` | Clickable text link |
| `TEXT_MENTION` | Mention by user ID |
| `CUSTOM_EMOJI` | Custom emoji |
| `BLOCKQUOTE` | Block quotation |

#### `filters.CaptionRegex`

Match media captions instead of message text:

```python
from telegram.ext import MessageHandler, filters

async def handle_caption(update, context):
    tag = context.match.group(1)
    await update.message.reply_text(f"Tag: {tag}")

application.add_handler(
    MessageHandler(
        filters.PHOTO & filters.CaptionRegex(r"#(\w+)"),
        handle_caption,
    )
)
```

---

### Media Filters

| Filter | Matches |
|---|---|
| `filters.PHOTO` | Photo messages |
| `filters.VIDEO` | Video messages |
| `filters.VIDEO_NOTE` | Video note (round video) messages |
| `filters.AUDIO` | Audio messages |
| `filters.VOICE` | Voice messages |
| `filters.ANIMATION` | GIF / animation messages |
| `filters.Document.ALL` | Any document |
| `filters.Document.IMAGE` | Image documents (JPEG, PNG, etc.) |
| `filters.Document.AUDIO` | Audio files sent as documents |
| `filters.Document.VIDEO` | Video files sent as documents |
| `filters.Document.PDF` | PDF documents |
| `filters.Document.ZIP` | ZIP archives |
| `filters.Sticker.ALL` | Any sticker |
| `filters.Sticker.REGULAR` | Regular (non-animated, non-video) stickers |
| `filters.Sticker.ANIMATED` | Animated stickers (Lottie) |
| `filters.Sticker.VIDEO` | Video stickers |
| `filters.PHOTO | filters.VIDEO` | Photos or videos |

#### Handling Photos

```python
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]  # Highest resolution variant
    file = await photo.get_file()
    path = await file.download_to_drive(f"downloads/{photo.file_id}.jpg")
    await update.message.reply_text(f"Photo saved to {path}")

application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
```

#### Handling Documents

```python
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    if doc.file_size > 50 * 1024 * 1024:  # 50 MB limit
        await update.message.reply_text("File too large (max 50 MB).")
        return

    file = await doc.get_file()
    path = await file.download_to_drive(f"downloads/{doc.file_name}")
    await update.message.reply_text(f"Document saved: {doc.file_name}")

application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
```

#### Handling Stickers

```python
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sticker = update.message.sticker
    await update.message.reply_text(
        f"Sticker: {sticker.emoji or '(no emoji)'} — Type: {sticker.type}"
    )

application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
```

---

### Status Update Filters

Status updates are non-message updates that represent chat state changes. They are available under `filters.StatusUpdate`.

| Filter | Matches |
|---|---|
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | One or more users joined the chat |
| `filters.StatusUpdate.LEFT_CHAT_MEMBER` | A user left the chat |
| `filters.StatusUpdate.NEW_CHAT_TITLE` | Chat title changed |
| `filters.StatusUpdate.NEW_CHAT_PHOTO` | Chat photo changed |
| `filters.StatusUpdate.DELETE_CHAT_PHOTO` | Chat photo deleted |
| `filters.StatusUpdate.GROUP_CHAT_CREATED` | Group chat created |
| `filters.StatusUpdate.SUPERGROUP_CHAT_CREATED` | Supergroup created |
| `filters.StatusUpdate.CHANNEL_CHAT_CREATED` | Channel created |
| `filters.StatusUpdate.PINNED_MESSAGE` | A message was pinned |
| `filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED` | Auto-delete timer changed |
| `filters.StatusUpdate.USERS_SHARED` | Users shared via keyboard |
| `filters.StatusUpdate.CHAT_SHARED` | Chat shared via keyboard |
| `filters.StatusUpdate.WEB_APP_DATA` | Web App data received |
| `filters.StatusUpdate.CHAT_BOOST_ADDED` | Chat boost added |
| `filters.StatusUpdate.CHAT_BACKGROUND_SET` | Chat background set |
| `filters.StatusUpdate.VIDEO_CHAT_STARTED` | Video chat started |
| `filters.StatusUpdate.VIDEO_CHAT_ENDED` | Video chat ended |
| `filters.StatusUpdate.VIDEO_CHAT_PARTICIPANTS_INVITED` | Participants invited to video chat |
| `filters.StatusUpdate.VIDEO_CHAT_SCHEDULED` | Video chat scheduled |

#### Handling New Members

```python
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for user in update.message.new_chat_members:
        if user.is_bot:
            continue
        await update.message.reply_text(f"Welcome, {user.first_name}!")

application.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)
```

#### Handling Pinned Messages

```python
async def pinned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pinned_msg = update.message.pinned_message
    if pinned_msg:
        await update.message.reply_text(
            f"A message was pinned: {pinned_msg.text or '(non-text)'}"
        )

application.add_handler(
    MessageHandler(filters.StatusUpdate.PINNED_MESSAGE, pinned)
)
```

#### Catching All Status Updates

Use `filters.StatusUpdate.ALL` to match any status update:

```python
application.add_handler(
    MessageHandler(filters.StatusUpdate.ALL, handle_any_status)
)
```

---

### Chat Type Filters

| Filter | Matches |
|---|---|
| `filters.ChatType.PRIVATE` | One-on-one chats with the bot |
| `filters.ChatType.GROUP` | Small group chats (≤200 members) |
| `filters.ChatType.SUPERGROUP` | Supergroup chats |
| `filters.ChatType.CHANNEL` | Channel posts |
| `filters.ChatType.ALL` | Any chat type |

```python
from telegram.ext import MessageHandler, CommandHandler, filters

# Only respond to /start in private chats
application.add_handler(
    CommandHandler("start", start_private),
    # Note: chat type filtering is done via filter, not group
)

# Or combine with MessageHandler
application.add_handler(
    MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE,
        handle_private_text,
    )
)
```

#### Filtering by Specific Chat ID

```python
from telegram.ext import MessageHandler, filters

# Only respond in a specific group
application.add_handler(
    MessageHandler(
        filters.TEXT & filters.Chat(chat_id=-1001234567890),
        handle_specific_group,
    )
)

# Multiple chat IDs
application.add_handler(
    MessageHandler(
        filters.TEXT & filters.Chat(chat_id=[-1001111111, -1002222222]),
        handle_multi_group,
    )
)
```

---

### User Filters

| Filter | Matches |
|---|---|
| `filters.User(user_id=id)` | Message from a specific user ID |
| `filters.User(user_id=[id1, id2])` | Message from any of the listed user IDs |
| `filters.User(username="name")` | Message from a specific username |
| `filters.User(username=["name1", "name2"])` | Message from any of the listed usernames |
| `filters.User(user_id=id, username="name")` | Matches both criteria |
| `filters.PRIVATE` | Shortcut for `filters.ChatType.PRIVATE` |

```python
from telegram.ext import MessageHandler, filters

# Only the bot developer can use /admin
ADMIN_IDS = [123456789, 987654321]

application.add_handler(
    CommandHandler(
        "admin",
        admin_panel,
    ),
    # Filter applied via MessageHandler, not CommandHandler
)

# If using with MessageHandler:
application.add_handler(
    MessageHandler(
        filters.User(user_id=ADMIN_IDS) & filters.COMMAND,
        handle_admin_command,
    )
)
```

#### Filtering Non-Bot Messages

```python
# Only messages from humans (not bots)
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.User(is_bot=True),
        handle_human_text,
    )
)
```

---

### Message Content Filters

| Filter | Matches |
|---|---|
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | New members |
| `filters.StatusUpdate.LEFT_CHAT_MEMBER` | Member left |
| `filters.VIA_BOT` | Messages sent via another bot |
| `filters.FORWARDED` | Forwarded messages |
| `filters.REPLY` | Messages that are replies |
| `filters.SUCCESSFUL_PAYMENT` | Successful payment |
| `filters.INVOICE` | Invoice messages |
| `filters.LEFT_CHAT_MEMBER` | Member left (alias) |

---

## Combined Filters

Filters are composable using Python's bitwise operators. This is one of the most powerful features of the filter system.

### Operators

| Operator | Meaning | Example |
|---|---|---|
| `&` | AND — both conditions must be true | `filters.TEXT & ~filters.COMMAND` |
| `\|` | OR — at least one condition must be true | `filters.PHOTO \| filters.VIDEO` |
| `~` | NOT — inverts the filter | `~filters.COMMAND` |

### Parentheses

Use parentheses to control evaluation order:

```python
# (TEXT that is NOT a command) AND in a PRIVATE chat
filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE

# TEXT in (PRIVATE or SUPERGROUP) chats
filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.SUPERGROUP)
```

> [!WARNING]
> Without parentheses, `&` and `|` may not evaluate as expected due to operator precedence. Always use explicit parentheses when combining `&` and `|` together.

### Common Patterns

```python
# Text messages from humans in private chats
filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE & ~filters.User(is_bot=True)

# Photos or videos with a caption
(filters.PHOTO | filters.VIDEO) & filters.CaptionRegex(r"\S+")

# Forwarded text messages
filters.TEXT & filters.FORWARDED

# Replies to the bot's own messages
filters.REPLY & filters.User(is_bot=True)
```

---

## Custom Filters

### Custom Filter Class

Subclass `filters.BaseFilter` for reusable, composable filters:

```python
import logging
from telegram.ext import filters

logger = logging.getLogger(__name__)


class AdminFilter(filters.BaseFilter):
    """Filter that only matches messages from admin users."""

    def __init__(self, admin_ids: list[int]) -> None:
        super().__init__()
        self.admin_ids = admin_ids

    def filter(self, update) -> bool:
        if update.effective_user is None:
            return False
        return update.effective_user.id in self.admin_ids

    def __repr__(self) -> str:
        return f"<AdminFilter(admin_ids={self.admin_ids})>"


# Usage
ADMIN_IDS = [123454789, 987654321]
admin_filter = AdminFilter(ADMIN_IDS)

application.add_handler(
    MessageHandler(admin_filter & filters.COMMAND, handle_admin_command)
)
```

### Custom Filter Function

For simpler cases, use `filters.update_extender` or wrap a function:

```python
from telegram import Update
from telegram.ext import filters


class TextLengthFilter(filters.BaseFilter):
    """Filter messages by text length."""

    def __init__(self, min_length: int = 1, max_length: int = 4096) -> None:
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length

    def filter(self, update: Update) -> bool:
        if not update.message or not update.message.text:
            return False
        length = len(update.message.text)
        return self.min_length <= length <= self.max_length

    def __repr__(self) -> str:
        return f"<TextLengthFilter(min={self.min_length}, max={self.max_length})>"


# Usage: messages between 10 and 100 characters
application.add_handler(
    MessageHandler(
        TextLengthFilter(min_length=10, max_length=100),
        handle_medium_text,
    )
)
```

### Rate Limit Filter

A practical production example — filter out users who are spamming:

```python
import time
import logging
from telegram import Update
from telegram.ext import filters

logger = logging.getLogger(__name__)


class RateLimitFilter(filters.BaseFilter):
    """Reject messages from users exceeding the rate limit.

    Args:
        max_messages: Maximum messages allowed in the time window.
        window_seconds: Time window in seconds.
    """

    def __init__(self, max_messages: int = 5, window_seconds: int = 60) -> None:
        super().__init__()
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._user_timestamps: dict[int, list[float]] = {}

    def filter(self, update: Update) -> bool:
        if not update.effective_user:
            return True

        user_id = update.effective_user.id
        now = time.monotonic()
        cutoff = now - self.window_seconds

        timestamps = self._user_timestamps.setdefault(user_id, [])
        timestamps[:] = [t for t in timestamps if t > cutoff]

        if len(timestamps) >= self.max_messages:
            logger.warning(
                "Rate limited user %d (%d messages in %ds)",
                user_id,
                len(timestamps),
                self.window_seconds,
            )
            return False

        timestamps.append(now)
        return True


# Usage: max 10 messages per 60 seconds
rate_filter = RateLimitFilter(max_messages=10, window_seconds=60)

application.add_handler(
    MessageHandler(
        rate_filter & filters.TEXT & ~filters.COMMAND,
        handle_text,
    )
)
```

### Elevated Chat Filter

```python
from telegram import ChatType
from telegram.ext import filters


class ElevatedChatFilter(filters.BaseFilter):
    """Match only chats where the bot has admin privileges."""

    def filter(self, update: Update) -> bool:
        bot = update.get_bot()
        chat = update.effective_chat
        if chat is None or bot is None:
            return False

        try:
            member = chat.get_member(bot.id)
            return member.status in ("administrator", "creator")
        except Exception:
            return False
```

---

## Filter Evaluation and Priority

When multiple filters are combined, they are evaluated with standard short-circuit logic:

| Operator | Left evaluated first | Short-circuits on |
|---|---|---|
| `&` (AND) | Left operand | `False` — right operand not evaluated |
| `\|` (OR) | Left operand | `True` — right operand not evaluated |
| `~` (NOT) | N/A | Inverts the single operand |

### Filter Precedence

When a `MessageHandler` is registered with a filter, the filter is evaluated **before** the callback is invoked. If the filter returns `False`, the handler is skipped and the next handler in the group is checked.

```
Update arrives
  → Handler 1 filter: TEXT & ~COMMAND
    → filters.TEXT evaluates to True
    → ~filters.COMMAND evaluates to True
    → Combined: True → callback invoked
  → (If handler 1 didn't match) Handler 2 filter: PHOTO
    → filters.PHOTO evaluates to False → skipped
```

> [!TIP]
> Place the cheapest filter first in an `&` chain. Filter evaluation is short-circuited, so if the leftmost filter is `False`, the more expensive filter on the right is never evaluated.

```python
# Good: filters.ALL is cheapest, Regex is expensive
filters.ALL & filters.Regex(r"complex_pattern")

# Better: put the cheap, selective filter first
filters.ChatType.PRIVATE & filters.Regex(r"complex_pattern")
```

---

## Common Filter Combinations — Quick Reference

| Use Case | Filter Expression |
|---|---|
| Text that isn't a command | `filters.TEXT & ~filters.COMMAND` |
| Private text messages from humans | `filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND & ~filters.User(is_bot=True)` |
| Photos or videos | `filters.PHOTO \| filters.VIDEO` |
| Messages with URLs | `filters.Entity(MessageEntityType.URL)` |
| Forwarded messages | `filters.FORWARDED` |
| Replies to the bot | `filters.REPLY & filters.User(is_bot=True)` |
| Messages from a specific user in a specific chat | `filters.User(user_id=123) & filters.Chat(chat_id=-100123)` |
| Text messages in groups only | `filters.TEXT & (filters.ChatType.GROUP \| filters.ChatType.SUPERGROUP)` |
| Any sticker type | `filters.Sticker.ALL` |
| Documents that are images | `filters.Document.IMAGE` |
| Messages from admins only | `filters.User(user_id=ADMIN_IDS)` |
| Non-bot text messages in private chats | `filters.TEXT & filters.ChatType.PRIVATE & ~filters.User(is_bot=True)` |
| Messages containing a phone number | `filters.Entity(MessageEntityType.PHONE_NUMBER)` |
| Text messages containing "hello" (case-insensitive) | `filters.Regex(r"(?i)\bhello\b")` |
| Photos with a caption tag | `filters.PHOTO & filters.CaptionRegex(r"#\w+")` |
| Any status update | `filters.StatusUpdate.ALL` |
| New members joining | `filters.StatusUpdate.NEW_CHAT_MEMBERS` |
| Messages that are replies AND contain text | `filters.REPLY & filters.TEXT` |

---

## Reference: All Filter Modules

| Module | Contents |
|---|---|
| `filters.TEXT` | Text message filter |
| `filters.COMMAND` | Command message filter |
| `filters.Regex` | Regex filter (sets `context.match`) |
| `filters.CaptionRegex` | Caption regex filter |
| `filters.Entity` | Entity-based filter |
| `filters.PHOTO` | Photo filter |
| `filters.VIDEO` | Video filter |
| `filters.AUDIO` | Audio filter |
| `filters.VOICE` | Voice filter |
| `filters.ANIMATION` | Animation/GIF filter |
| `filters.Document.*` | Document type filters |
| `filters.Sticker.*` | Sticker type filters |
| `filters.StatusUpdate.*` | Status update filters |
| `filters.ChatType.*` | Chat type filters |
| `filters.Chat` | Specific chat ID filter |
| `filters.User` | Specific user filter |
| `filters.PRIVATE` | Shortcut for `ChatType.PRIVATE` |
| `filters.FORWARDED` | Forwarded message filter |
| `filters.REPLY` | Reply message filter |
| `filters.VIA_BOT` | Sent via bot filter |
| `filters.SUCCESSFUL_PAYMENT` | Successful payment filter |
| `filters.INVOICE` | Invoice message filter |
| `filters.ALL` | Matches every message |

---

## Summary

Filters are composable, reusable predicates that determine which updates reach your handlers. Use the built-in filters for common cases — text, media, chat type, user identity — and build custom filters for domain-specific logic like rate limiting, admin checks, or content validation. Combined with the handler system (Chapter 4), filters give you precise control over your bot's update processing pipeline.
