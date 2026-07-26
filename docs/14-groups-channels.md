# Chapter 14: Groups, Channels & Admin

This chapter covers everything you need to know about deploying bots into Telegram groups, supergroups, and channels. You will learn how privacy mode affects message visibility, how to handle group-specific events, implement admin-only commands, manage permissions, and work with forum topics.

---

## Table of Contents

- [Group & Supergroup Bots](#group--supergroup-bots)
- [Privacy Mode](#privacy-mode)
- [Chat Types Comparison](#chat-types-comparison)
- [Handling Group Events](#handling-group-events)
- [Admin Operations](#admin-operations)
- [ChatPermissions](#chatpermissions)
- [Chat Administrator Rights](#chat-administrator-rights)
- [Channel Bots](#channel-bots)
- [Forum Topics](#forum-topics)
- [Ephemeral Messages in Groups](#ephemeral-messages-in-groups)
- [Complete Group Bot Example](#complete-group-bot-example)

---

## Group & Supergroup Bots

### Adding a Bot to a Group

Any user can add your bot to a group or supergroup. When the bot joins, it receives a `NEW_CHAT_MEMBERS` update. There are two ways a bot can end up in a group:

1. **Direct add** — a member uses the group settings to add the bot by username.
2. **`@username` in a message** — if the bot is not in the group yet, mentioning it prompts Telegram to suggest adding it.

> **Important:** A bot cannot add itself to a group. A human member must perform the action.

### Privacy Mode (Default: ON)

By default, every bot created via @BotFather has **privacy mode enabled**. This means the bot only receives:

- Commands (messages starting with `/`)
- Replies to the bot's own messages
- Messages that explicitly `@mention` the bot
- Service messages (new members, pinned messages, etc.)
- Channel posts (if the bot is an admin)

In a group with privacy mode ON, **the bot cannot see regular messages** from other users.

### Disabling Privacy Mode

You can disable privacy mode through @BotFather:

```
/mybots → Select your bot → Bot Settings → Group Privacy → Turn off
```

Alternatively, use the HTTP API directly:

```
POST https://api.telegram.org/bot<token>/deleteWebhook
GET  https://api.telegram.org/bot<token>/getMe
```

Set privacy via the Bot API:

```
POST https://api.telegram.org/bot<token>/setMyDescription
```

> **Recommendation:** Keep privacy mode ON unless your bot explicitly needs to read all messages. Disabling it means your bot processes every message in the group, which increases load and may raise privacy concerns.

### Bot Must Be Admin to See All Messages

Even with privacy mode OFF, a bot in a **supergroup** must be an **administrator** to receive all messages in channels it administers. In regular groups (non-supergroup), privacy mode alone controls visibility.

| Scenario | Privacy Mode | Admin Status | Sees All Messages? |
|----------|:------------:|:------------:|:------------------:|
| Regular group | ON | No | No (commands/replies only) |
| Regular group | OFF | No | Yes |
| Supergroup | ON | No | No |
| Supergroup | ON | Yes | Yes |
| Supergroup | OFF | No | Yes |
| Supergroup | OFF | Yes | Yes |

---

## Chat Types Comparison

Telegram defines four distinct chat types. Each presents different capabilities and constraints for bots.

| Type | Member Count | Bot Capabilities | Typical Use Case |
|------|:------------|------------------|-----------------|
| `private` | 2 | Full access to all messages; direct conversation | Personal assistants, customer support |
| `group` | 2 – 200,000 | Limited by privacy mode; 32 MB file size limit | Small team coordination, task bots |
| `supergroup` | 2 – 200,000 | Full access if admin or privacy mode disabled; 2 GB file size limit | Large communities, moderation bots |
| `channel` | Unlimited | Post messages, edit, delete; admin rights required | Broadcasting, content delivery |

### Detecting Chat Type in Code

```python
from telegram import Update


async def detect_chat_type(update: Update) -> str:
    """Return the chat type string for the current update."""
    chat = update.effective_chat
    if chat.type == "private":
        return "private"
    elif chat.type == "group":
        return "group"
    elif chat.type == "supergroup":
        return "supergroup"
    elif chat.type == "channel":
        return "channel"
    return "unknown"
```

### Differences Between Group and Supergroup

| Feature | Group | Supergroup |
|---------|:-----:|:----------:|
| Member limit | 200,000 | 200,000 |
| Message history | Visible to new members | Visible to new members |
| File size limit | 32 MB | 2 GB |
| Slow mode | Not available | Available |
| Topics / forums | Not available | Available |
| Invite links | Yes | Yes |
| Anti-spam | Basic | Advanced |
| Linked channel | No | Yes |
| Translatable | No | Yes |

> **Note:** Regular groups can be converted to supergroups by a Telegram client. When this happens, the chat ID changes.

---

## Handling Group Events

Groups generate a variety of service messages. `python-telegram-bot` provides dedicated filters to handle them.

### Available Status Update Filters

| Filter | Event | Description |
|--------|-------|-------------|
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | New member(s) joined | Fires when one or more users are added |
| `filters.StatusUpdate.LEFT_CHAT_MEMBER` | Member left or was kicked | Fires when a user leaves or is removed |
| `filters.StatusUpdate.NEW_CHAT_TITLE` | Group title changed | Fires when an admin renames the group |
| `filters.StatusUpdate.NEW_CHAT_PHOTO` | Group photo changed | Fires when the group avatar is updated |
| `filters.StatusUpdate.DELETE_CHAT_PHOTO` | Group photo deleted | Fires when the avatar is removed |
| `filters.StatusUpdate.GROUP_CHAT_CREATED` | Group just created | Fires immediately after creation |
| `filters.StatusUpdate.SUPERGROUP_CHAT_CREATED` | Supergroup just created | Fires after upgrade to supergroup |
| `filters.StatusUpdate.PINNED_MESSAGE` | Message pinned | Fires when any message is pinned |
| `filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED` | Auto-delete timer changed | Fires when auto-delete settings change |
| `filters.StatusUpdate.FORUM_TOPIC_CREATED` | Forum topic created | Fires when a new topic is opened |
| `filters.StatusUpdate.FORUM_TOPIC_EDITED` | Forum topic edited | Fires when a topic is renamed or icon changed |
| `filters.StatusUpdate.FORUM_TOPIC_CLOSED` | Forum topic closed | Fires when a topic is closed |
| `filters.StatusUpdate.FORUM_TOPIC_REOPENED` | Forum topic reopened | Fires when a closed topic is reopened |
| `filters.StatusUpdate.SHARED_USERS` | Users shared via button | Fires when users are shared via keyboard button |
| `filters.StatusUpdate.WRITE_ACCESS_ALLOWED` | User unblocked bot | Fires when a user starts the bot after blocking |

### New Members Handler

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def welcome_new_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a welcome message when new members join the chat."""
    chat = update.effective_chat

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        name = member.first_name or "there"
        welcome_text = (
            f"Welcome to {chat.title}, {name}!\n\n"
            f"There are now {chat.get_member_count()} members."
        )
        await chat.send_message(welcome_text)
        logger.info(
            "Welcomed new member %s (id=%d) to chat %d", name, member.id, chat.id
        )


welcome_handler = MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS,
    welcome_new_members,
)
```

### Left Members Handler

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def handle_left_member(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Log and acknowledge when a member leaves."""
    left_member = update.message.left_chat_member
    chat = update.effective_chat

    if left_member.is_bot:
        logger.info("Bot %s removed from chat %d", left_member.full_name, chat.id)
        return

    logger.info(
        "Member %s (id=%d) left chat %d",
        left_member.full_name,
        left_member.id,
        chat.id,
    )
```

### Pinned Message Handler

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def handle_pinned_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """React to a pinned message in the group."""
    pinned = update.message.pinned_message
    chat = update.effective_chat

    if pinned is None:
        return

    logger.info(
        "Message %d pinned in chat %d by user %s",
        pinned.message_id,
        chat.id,
        update.effective_user.id if update.effective_user else "unknown",
    )
```

### Forum Topic Handler

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def handle_forum_topic_created(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle a new forum topic being created."""
    topic = update.message.forum_topic_created
    chat = update.effective_chat

    logger.info(
        "Forum topic '%s' (id=%d) created in chat %d",
        topic.name,
        update.message.message_thread_id,
        chat.id,
    )
```

---

## Admin Operations

### Checking User Status with `getChatMember`

Every bot should validate that a user has sufficient privileges before executing admin commands.

```python
from telegram import Update
from telegram.ext import ContextTypes


ADMIN_STATUSES = frozenset({"creator", "administrator"})


async def is_chat_admin(bot, chat_id: int, user_id: int) -> bool:
    """Check whether a user is an admin or creator in the given chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ADMIN_STATUSES
    except Exception:
        return False
```

### Status Values

| Status | Description |
|--------|-------------|
| `creator` | The chat owner. Has all permissions unconditionally. |
| `administrator` | Has elevated permissions granted by the creator. |
| `member` | A regular member with no special privileges. |
| `restricted` | A member whose permissions have been limited (e.g., muted). |
| `left` | The user has left the chat or was kicked. |
| `banned` | The user is permanently banned from the chat. |

### Admin-Only Command Pattern

This pattern is reusable across any admin command in your bot:

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

ADMIN_STATUSES = frozenset({"creator", "administrator"})


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Example admin-only command."""
    user = update.effective_user
    chat = update.effective_chat

    if user is None or chat is None:
        return

    member = await context.bot.get_chat_member(chat.id, user.id)

    if member.status not in ADMIN_STATUSES:
        await update.message.reply_text("⛔ This command is admin-only.")
        logger.warning(
            "Non-admin user %s (id=%d) attempted admin command in chat %d",
            user.full_name,
            user.id,
            chat.id,
        )
        return

    # --- Admin logic below ---
    logger.info(
        "Admin %s (id=%d) executed admin command in chat %d",
        user.full_name,
        user.id,
        chat.id,
    )
    await update.message.reply_text("✅ Admin command executed.")
```

### Decorator Approach

For cleaner handler registration, wrap the check in a decorator:

```python
import functools
import logging
from typing import Callable, Coroutine, Any
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

ADMIN_STATUSES = frozenset({"creator", "administrator"})


def admin_only(
    func: Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]],
) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]:
    """Decorator that restricts a handler to chat administrators and creators."""

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat

        if user is None or chat is None:
            return

        member = await context.bot.get_chat_member(chat.id, user.id)

        if member.status not in ADMIN_STATUSES:
            await update.message.reply_text("⛔ Admins only.")
            logger.warning(
                "Non-admin %s (id=%d) denied access to %s in chat %d",
                user.full_name,
                user.id,
                func.__name__,
                chat.id,
            )
            return

        return await func(update, context)

    return wrapper


@admin_only
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a replied-to user from the chat. Admins only."""
    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to ban them.")
        return

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat

    await context.bot.ban_chat_member(chat.id, target.id)
    await update.message.reply_text(f"Banned {target.full_name}.")
```

### Checking Specific Admin Rights

```python
from telegram import Update
from telegram.ext import ContextTypes


async def check_admin_rights(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Verify the bot has the required admin rights before performing an action."""
    chat = update.effective_chat
    bot = context.bot

    bot_member = await bot.get_chat_member(chat.id, bot.id)

    if bot_member.status != "administrator":
        await update.message.reply_text("I am not an admin in this chat.")
        return

    rights = bot_member.can_delete_messages
    if not rights:
        await update.message.reply_text(
            "I need the 'Delete Messages' permission to do this."
        )
        return

    # Proceed with message deletion...
```

---

## ChatPermissions

Permissions control what regular (non-admin) members can do in a supergroup. Use `ChatPermissions` to set them.

### Permission Fields

| Permission | Type | Description |
|------------|------|-------------|
| `can_send_messages` | `bool` | Send text messages |
| `can_send_audios` | `bool` | Send audio files |
| `can_send_documents` | `bool` | Send documents and files |
| `can_send_photos` | `bool` | Send photos |
| `can_send_videos` | `bool` | Send videos |
| `can_send_video_notes` | `bool` | Send video notes (round video) |
| `can_send_voice_notes` | `bool` | Send voice messages |
| `can_send_polls` | `bool` | Send polls |
| `can_send_other_messages` | `bool` | Send animations, games, stickers, inline bots |
| `can_add_web_page_previews` | `bool` | Add link previews to messages |
| `can_change_info` | `bool` | Change group info/title |
| `can_invite_users` | `bool` | Invite new members |
| `can_pin_messages` | `bool` | Pin messages |
| `can_manage_topics` | `bool` | Create, close, reopen, and edit forum topics |

### Restricting a User

```python
from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes


async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mute a replied-to user for 1 hour."""
    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to mute that user.")
        return

    chat = update.effective_chat
    target = update.message.reply_to_message.from_user
    until_date = update.message.date.timestamp() + 3600  # 1 hour from now

    await context.bot.restrict_chat_member(
        chat_id=chat.id,
        user_id=target.id,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        ),
        until_date=until_date,
    )

    await update.message.reply_text(f"Muted {target.full_name} for 1 hour.")
```

### Restricting with Default Permissions

```python
from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes


async def set_slow_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set default permissions to restrict all members to text only."""
    chat = update.effective_chat

    await context.bot.set_chat_permissions(
        chat_id=chat.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_voice_notes=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
            can_manage_topics=False,
        ),
    )

    await update.message.reply_text("Default permissions updated: text only.")
```

---

## Chat Administrator Rights

When you add your bot as an admin to a group, you can specify exactly which rights it receives.

### Full List of Admin Rights

| Right | Type | Description |
|-------|------|-------------|
| `can_manage_chat` | `bool` | General management access (required for many operations) |
| `can_delete_messages` | `bool` | Delete any message in the chat |
| `can_manage_video_chats` | `bool` | Manage video chat settings |
| `can_restrict_members` | `bool` | Ban, mute, or restrict members |
| `can_promote_members` | `bool` | Promote other members to admin |
| `can_change_info` | `bool` | Change group title, description, and photo |
| `can_invite_users` | `bool` | Generate and share invite links |
| `can_pin_messages` | `bool` | Pin messages in the chat |
| `can_manage_topics` | `bool` | Manage forum topics |
| `can_post_messages` | `bool` | Post messages in a channel (channel admin only) |
| `can_edit_messages` | `bool` | Edit messages posted by others (channel admin only) |
| `can_answer_callbacks` | `bool` | Answer inline callback queries |

### Setting Admin Rights for Your Bot

```python
from telegram import ChatAdministratorRights, Update
from telegram.ext import ContextTypes


async def promote_self(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Promote the bot to admin with specific rights."""
    chat = update.effective_chat
    bot = context.bot

    rights = ChatAdministratorRights(
        can_manage_chat=True,
        can_delete_messages=True,
        can_manage_video_chats=False,
        can_restrict_members=True,
        can_promote_members=False,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=True,
        can_manage_topics=True,
        can_post_messages=False,
        can_edit_messages=False,
    )

    await bot.promote_chat_member(
        chat_id=chat.id,
        user_id=bot.id,
        rights=rights,
    )

    await update.message.reply_text("Bot promoted with specified rights.")
```

> **Note:** The bot must already be an admin to promote itself further, or the chat creator must perform the promotion.

---

## Channel Bots

Channels are one-way broadcasting tools. Bots can post, edit, and manage content in channels they administrate.

### Bot as Channel Admin

A bot must be added as an administrator to a channel before it can post. Add the bot via the channel's admin settings.

### Posting to Channels

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

CHANNEL_ID = -1001234567890  # Channel chat IDs start with -100


async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward a message to the configured channel."""
    chat = update.effective_chat

    if chat.type != "channel":
        await update.message.reply_text("This command can only be used in a channel.")
        return

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="Hello from the bot!",
    )
```

### Editing Channel Posts

```python
from telegram import Update
from telegram.ext import ContextTypes


async def edit_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit a previously posted message in the channel."""
    if not update.channel_post:
        return

    await context.bot.edit_message_text(
        chat_id=update.channel_post.chat.id,
        message_id=update.channel_post.message_id,
        text="This message has been edited.",
    )
```

### Channel Post Handling

Use `filters.UpdateType.CHANNEL_POST` to listen for new posts in channels where the bot is an admin:

```python
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters


async def handle_channel_post(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Process new channel posts."""
    post = update.channel_post

    if post is None:
        return

    text = post.text or ""
    if "#feedback" in text.lower():
        await post.reply_text("Thank you for your feedback!")
```

### Anonymous Admin Messages

When a bot sends messages in a group as an admin with the "Anonymous Admin" option enabled, messages appear to come from the group itself rather than the bot. This is configured at the Telegram client level and cannot be set via the Bot API.

---

## Forum Topics

Forum topics allow organizing discussions within a supergroup into separate threads.

### Enabling Forum Topics

Forum topics can only be enabled through the Telegram client (group settings → Topics). There is no Bot API method to enable them.

### Topic-Enabled Supergroup Structure

```
Supergroup (Forum Enabled)
├── General (always exists, thread_id = 0)
├── Topic: "Support"
│   └── thread_id = 12345
├── Topic: "Development"
│   └── thread_id = 12346
└── Topic: "Off-topic"
    └── thread_id = 12347
```

### Sending Messages to a Specific Topic

```python
from telegram import Update
from telegram.ext import ContextTypes


THREAD_ID = 12345  # The target topic's thread ID


async def post_to_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to a specific forum topic."""
    chat = update.effective_chat

    await context.bot.send_message(
        chat_id=chat.id,
        text="This message is in a specific topic.",
        message_thread_id=THREAD_ID,
    )
```

### Handling Topic Events

```python
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def on_topic_created(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle forum topic creation."""
    topic = update.message.forum_topic_created
    thread_id = update.message.message_thread_id
    logger.info("Forum topic '%s' created (thread=%d)", topic.name, thread_id)


async def on_topic_edited(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle forum topic edit."""
    edit = update.message.forum_topic_edited
    thread_id = update.message.message_thread_id
    logger.info("Forum topic edited (thread=%d): name=%s", thread_id, edit.name)


async def on_topic_closed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle forum topic closure."""
    thread_id = update.message.message_thread_id
    logger.info("Forum topic closed (thread=%d)", thread_id)


async def on_topic_reopened(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle forum topic reopening."""
    thread_id = update.message.message_thread_id
    logger.info("Forum topic reopened (thread=%d)", thread_id)
```

### Creating and Managing Topics via Bot

```python
from telegram import Update
from telegram.ext import ContextTypes


async def create_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a new forum topic (bot must have manage_topics right)."""
    chat = update.effective_chat

    topic = await context.bot.create_forum_topic(
        chat_id=chat.id,
        name="New Discussion",
        icon_color=0xFF0000,  # Red icon
    )

    await update.message.reply_text(
        f"Topic created: {topic.name} (thread_id={topic.thread_id})"
    )


async def close_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close a forum topic by thread ID."""
    chat = update.effective_chat
    thread_id = 12345  # Replace with dynamic thread ID

    await context.bot.close_forum_topic(chat_id=chat.id, message_thread_id=thread_id)
    await update.message.reply_text("Topic closed.")


async def delete_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a forum topic permanently."""
    chat = update.effective_chat
    thread_id = 12345

    await context.bot.delete_forum_topic(chat_id=chat.id, message_thread_id=thread_id)
    await update.message.reply_text("Topic deleted.")
```

### Forum Topic Icon Colors

| Color Constant | Hex Value | Preview |
|----------------|-----------|---------|
| `0x6FB33F` | Green | ![#6FB33F](https://via.placeholder.com/15/6FB33F/6FB33F.png) |
| `0xFFD310` | Yellow | ![#FFD310](https://via.placeholder.com/15/FFD310/FFD310.png) |
| `0xE05252` | Red | ![#E05252](https://via.placeholder.com/15/E05252/E05252.png) |
| `0xD87EE5` | Purple | ![#D87EE5](https://via.placeholder.com/15/D87EE5/D87EE5.png) |
| `0xFF8714` | Orange | ![#FF8714](https://via.placeholder.com/15/FF8714/FF8714.png) |
| `0x6FB33F` | Rose | ![#EB6D6D](https://via.placeholder.com/15/EB6D6D/EB6D6D.png) |

---

## Ephemeral Messages in Groups

Ephemeral messages are temporary — they disappear after a set duration. This is useful for bot responses that should not clutter the group history.

### Bot-to-User Private Responses

When responding in a group, it is often better to reply privately to avoid noise:

```python
from telegram import Update
from telegram.ext import ContextTypes


async def private_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a private reply instead of a group message."""
    user = update.effective_user

    await user.send_message(
        text="Here is your result. This message was sent privately.",
    )

    await update.message.reply_text("Check your private messages!")
```

### Admin-Only Ephemeral Messages

For moderation actions, bots can send messages that only specific users can see by using inline keyboards or by restricting visibility through reply mechanics.

```python
from telegram import Update
from telegram.ext import ContextTypes


async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Issue a warning that is visible only in the thread."""
    chat = update.effective_chat

    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to warn that user.")
        return

    target = update.message.reply_to_message.from_user
    admin = update.effective_user

    warning_text = (
        f"⚠️ Warning issued to {target.full_name} by {admin.full_name}.\n"
        f"Reason: {update.message.text.split(maxsplit=1)[-1] if update.message.text else 'No reason given'}"
    )

    await update.message.reply_text(warning_text)
```

---

## Complete Group Bot Example

The following is a full production-grade group bot that handles welcomes, admin commands, spam detection, and auto-moderation.

```python
"""
Complete group moderation bot.
Demonstrates: welcome messages, admin commands, spam detection, auto-moderation.

Requirements:
    python-telegram-bot>=20.0

Usage:
    Set BOT_TOKEN environment variable, then run:
        python group_bot.py
"""

import os
import re
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Final

from telegram import ChatPermissions, Update
from telegram.ext import (
    Application,
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

BOT_TOKEN: Final[str] = os.environ["BOT_TOKEN"]

ADMIN_STATUSES: Final[frozenset[str]] = frozenset({"creator", "administrator"})

SPAM_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"https?://t\.me/\+", re.IGNORECASE),
    re.compile(r"(buy|sell|cheap|discount|free money)", re.IGNORECASE),
    re.compile(r"(@\w+){3,}"),
]

MAX_WARNINGS: Final[int] = 3

_warn_counts: dict[int, int] = defaultdict(int)


async def is_chat_admin(bot, chat_id: int, user_id: int) -> bool:
    """Check whether a user is an admin or creator."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ADMIN_STATUSES
    except Exception:
        return False


async def welcome_new_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Greet new members and set default permissions."""
    chat = update.effective_chat

    for member in update.message.new_chat_members or []:
        if member.is_bot:
            continue

        name = member.first_name or "there"
        await chat.send_message(
            f"Welcome to {chat.title}, {name}!\n\n"
            f"Please read the rules and be respectful."
        )
        logger.info("Welcomed %s (id=%d) to chat %d", name, member.id, chat.id)


async def handle_left_member(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Log when a member leaves."""
    left = update.message.left_chat_member
    if left and not left.is_bot:
        logger.info(
            "Member %s (id=%d) left chat %d",
            left.full_name,
            left.id,
            update.effective_chat.id,
        )


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a replied-to user. Admins only."""
    user = update.effective_user
    chat = update.effective_chat

    if not await is_chat_admin(context.bot, chat.id, user.id):
        await update.message.reply_text("⛔ Admins only.")
        return

    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to ban that user.")
        return

    target = update.message.reply_to_message.from_user
    reason = (
        update.message.text.split(maxsplit=1)[-1]
        if len(update.message.text.split()) > 1
        else "No reason"
    )

    await context.bot.ban_chat_member(chat.id, target.id)
    await update.message.reply_text(f"Banned {target.full_name}. Reason: {reason}")
    logger.info(
        "User %s banned %s in chat %d. Reason: %s",
        user.full_name,
        target.full_name,
        chat.id,
        reason,
    )


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mute a replied-to user for 1 hour. Admins only."""
    user = update.effective_user
    chat = update.effective_chat

    if not await is_chat_admin(context.bot, chat.id, user.id):
        await update.message.reply_text("⛔ Admins only.")
        return

    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to mute that user.")
        return

    target = update.message.reply_to_message.from_user
    until = datetime.now(timezone.utc).timestamp() + 3600

    await context.bot.restrict_chat_member(
        chat_id=chat.id,
        user_id=target.id,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        ),
        until_date=until,
    )

    await update.message.reply_text(f"Muted {target.full_name} for 1 hour.")
    logger.info(
        "User %s muted %s in chat %d", user.full_name, target.full_name, chat.id
    )


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Warn a replied-to user. After MAX_WARNINGS, auto-ban. Admins only."""
    user = update.effective_user
    chat = update.effective_chat

    if not await is_chat_admin(context.bot, chat.id, user.id):
        await update.message.reply_text("⛔ Admins only.")
        return

    if not update.message or not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to warn that user.")
        return

    target = update.message.reply_to_message.from_user
    _warn_counts[target.id] += 1
    count = _warn_counts[target.id]

    if count >= MAX_WARNINGS:
        await context.bot.ban_chat_member(chat.id, target.id)
        await update.message.reply_text(
            f"{target.full_name} reached {MAX_WARNINGS} warnings and has been banned."
        )
        logger.info(
            "User %s auto-banned after %d warnings in chat %d",
            target.full_name,
            count,
            chat.id,
        )
        del _warn_counts[target.id]
    else:
        await update.message.reply_text(
            f"⚠️ {target.full_name} warned ({count}/{MAX_WARNINGS})."
        )
        logger.info(
            "User %s warned (%d/%d) in chat %d",
            target.full_name,
            count,
            MAX_WARNINGS,
            chat.id,
        )


async def spam_detector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto-detect spam messages and delete them."""
    message = update.message
    if message is None or message.text is None:
        return

    chat = update.effective_chat
    user = update.effective_user

    if user is None:
        return

    if await is_chat_admin(context.bot, chat.id, user.id):
        return

    for pattern in SPAM_PATTERNS:
        if pattern.search(message.text):
            await message.delete()
            logger.info(
                "Spam deleted from user %s (id=%d) in chat %d: %s",
                user.full_name,
                user.id,
                chat.id,
                message.text[:100],
            )
            await chat.send_message(
                f"Message from {user.full_name} removed: suspected spam."
            )
            return


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show group statistics. Admins only."""
    user = update.effective_user
    chat = update.effective_chat

    if not await is_chat_admin(context.bot, chat.id, user.id):
        await update.message.reply_text("⛔ Admins only.")
        return

    member_count = await chat.get_member_count()
    await update.message.reply_text(
        f"📊 {chat.title}\n"
        f"Members: {member_count}\n"
        f"Chat ID: {chat.id}\n"
        f"Type: {chat.type}"
    )


def main() -> None:
    """Start the group moderation bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_member)
    )
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, spam_detector)
    )

    logger.info("Group bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

---

## Summary

| Topic | Key Takeaway |
|-------|-------------|
| Privacy Mode | ON by default; bot only sees commands and mentions |
| Group vs Supergroup | Supergroups support forums, larger files, and more features |
| Admin Commands | Always validate `get_chat_member` status before privileged actions |
| Permissions | Use `ChatPermissions` to restrict or allow member actions |
| Channels | Bot must be admin; use `CHANNEL_ID` for posting |
| Forum Topics | Use `message_thread_id` to target specific topics |
| Spam Detection | Combine regex patterns with auto-moderation for best results |

> **Next Chapter:** [Chapter 15: Deployment & Hosting](15-deployment.md) — Learn how to deploy your bot to production with Docker, webhooks, and cloud platforms.
