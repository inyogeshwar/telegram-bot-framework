# python-telegram-bot v20+/v21.x — Comprehensive Reference

Complete reference of every function, class, method, filter, handler, keyboard, API method, configuration option, security practice, deployment pattern, and testing pattern documented across all 22 handbook chapters.

---

## 1. Core Application & Builder

### `Application` / `ApplicationBuilder`

```python
from telegram.ext import ApplicationBuilder
```

| Builder Method | Purpose |
|---|---|
| `.token(token)` | Set bot token (required) |
| `.base_url(url)` | Override Telegram API base URL |
| `.base_file_url(url)` | Override file download base URL |
| `.get_updates_connection_pool_size(n)` | Connection pool for `getUpdates` |
| `.read_timeout(seconds)` | Read timeout for HTTP requests |
| `.write_timeout(seconds)` | Write timeout for HTTP requests |
| `.connect_timeout(seconds)` | Connect timeout |
| `.pool_timeout(seconds)` | Pool timeout |
| `.bot(bot)` | Pass pre-built `Bot` instance |
| `.update_queue(queue)` | Pass custom `asyncio.Queue` |
| `.persistence(persistence)` | Attach persistence backend |
| `.defaults(defaults)` | Set default parse_mode, link_preview, etc. |
| `.job_queue(job_queue)` | Pass custom `JobQueue` |
| `.post_init(coroutine)` | Coroutine called after initialization |
| `.post_shutdown(coroutine)` | Coroutine called after shutdown |
| `.post_stop(coroutine)` | Coroutine called after stop |

```python
application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
```

| Application Method | Purpose |
|---|---|
| `add_handler(handler, group=0)` | Register handler in a group |
| `remove_handler(handler, group=0)` | Remove a registered handler |
| `add_error_handler(callback)` | Register global error handler |
| `run_polling(drop_pending_updates=True)` | Start polling loop |
| `run_webhook(listen, port, url_path, ...)` | Start webhook server |
| `post_init(coroutine)` | Register post-init hook |
| `post_shutdown(coroutine)` | Register shutdown hook |
| `stop()` | Gracefully stop the application |

---

## 2. Handlers — Complete Reference

### `CommandHandler`

Responds to messages starting with `/command`. Arguments available in `context.args`.

```python
from telegram.ext import CommandHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(rf"Hello {user.mention_html()}!")


application.add_handler(CommandHandler("start", start))
```

### `MessageHandler`

Matches non-command messages based on a **filter**. The workhorse for text replies, media processing, and catch-all logic.

```python
from telegram.ext import MessageHandler, filters

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_callback))
```

### `CallbackQueryHandler`

Handles presses on inline keyboard buttons. Must always answer callback queries.

```python
from telegram.ext import CallbackQueryHandler


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "option_a":
        await query.edit_message_text("Selected A")


application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(CallbackQueryHandler(handler, pattern=r"^delete_\d+$"))
```

### `InlineQueryHandler`

Handles inline queries via `@yourbot query`.

```python
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=query,
            title=f"Result for: {query}",
            input_message_content=InputTextMessageContent(
                message_text=f"Result: {query}"
            ),
        )
    ]
    await update.inline_query.answer(results, cache_time=300, is_personal=True)


application.add_handler(InlineQueryHandler(inline_query))
```

### `ChosenInlineResultHandler`

Fires when a user selects an inline result.

```python
from telegram.ext import ChosenInlineResultHandler


async def chosen_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = update.chosen_inline_result
    logger.info("User %s selected result %s", result.from_user.id, result.result_id)


application.add_handler(ChosenInlineResultHandler(chosen_result))
```

### `PreCheckoutQueryHandler`

Fires when a user confirms a payment. Must respond within 10 seconds.

```python
from telegram.ext import PreCheckoutQueryHandler


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload == "order_123":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Something went wrong.")


application.add_handler(PreCheckoutQueryHandler(pre_checkout))
```

### `ShippingQueryHandler`

Fires when a user provides a shipping address.

```python
from telegram.ext import ShippingQueryHandler
from telegram import ShippingOption, LabeledPrice


async def shipping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.shipping_query
    options = [
        ShippingOption(
            id="standard", title="Standard", prices=[LabeledPrice("Standard", 150)]
        ),
    ]
    await query.answer(ok=True, shipping_options=options)


application.add_handler(ShippingQueryHandler(shipping))
```

### `PollAnswerHandler`

Handles answers to polls the bot created.

```python
from telegram.ext import PollAnswerHandler


async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    logger.info(
        "User %s answered poll %s with options %s",
        answer.user.id,
        answer.poll_id,
        answer.option_ids,
    )


application.add_handler(PollAnswerHandler(poll_answer))
```

### `PollHandler`

Handles updates when a poll the bot sent is updated.

```python
from telegram.ext import PollHandler


async def poll_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poll = update.poll
    logger.info("Poll %s updated. Total votes: %d", poll.id, poll.total_voter_count)


application.add_handler(PollHandler(poll_update))
```

### `ChatMemberHandler`

Tracks when chat members change status.

| Mode | Constant | When it fires |
|---|---|---|
| Any member status change | `ChatMemberHandler.CHAT_MEMBER` | Any member's status changes |
| Bot's own status change | `ChatMemberHandler.MY_CHAT_MEMBER` | The bot's own status changes |

```python
from telegram.ext import ChatMemberHandler

application.add_handler(
    ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER)
)
```

### `ChatJoinRequestHandler`

Fires when a user sends a join request to a group/channel with approvals enabled.

```python
from telegram.ext import ChatJoinRequestHandler


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = update.chat_join_request
    await request.approve()  # or await request.decline()


application.add_handler(ChatJoinRequestHandler(join_request))
```

### `MessageReactionHandler`

Tracks when users add, remove, or change reactions.

```python
from telegram.ext import MessageReactionHandler


async def reaction_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reaction = update.message_reaction
    logger.info(
        "Reaction in chat %s: old=%s new=%s",
        reaction.chat.id,
        reaction.old_reaction,
        reaction.new_reaction,
    )


application.add_handler(MessageReactionHandler(reaction_update))
```

### `ErrorHandler`

Catches all unhandled exceptions from any handler callback.

```python
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    exception = context.error
    if isinstance(exception, Forbidden):
        logger.warning("User blocked the bot")
    elif isinstance(exception, BadRequest):
        logger.error("Bad request: %s", exception)
    elif isinstance(exception, TimedOut):
        logger.warning("Timed out")
    elif isinstance(exception, NetworkError):
        logger.error("Network error: %s", exception)
    else:
        logger.exception("Unexpected error: %s", exception)


application.add_error_handler(error_handler)
```

### Handler Groups & Priority

| Rule | Detail |
|---|---|
| Lower group number = higher priority | Group 0 checked before group 1 |
| First handler in a group wins | Registration order matters within a group |
| `ApplicationHandlerStop` stops propagation | Raising it prevents subsequent groups from running |
| Default group is `0` | Omitting `group` places handler in group 0 |

```python
from telegram.ext import ApplicationHandlerStop


async def privileged_handler(update, context):
    if is_spam(update):
        await update.message.delete()
        raise ApplicationHandlerStop
```

---

## 3. Filters — Complete Reference

All filters accessed via `telegram.ext.filters`.

### Text & Command Filters

| Filter | Matches |
|---|---|
| `filters.TEXT` | Any text message (plain text and entities) |
| `filters.COMMAND` | Messages starting with `/` |
| `filters.Regex(pattern)` | Messages matching regex (sets `context.match`) |
| `filters.Entity(type)` | Messages containing a specific entity type |
| `filters.Entity(types)` | Messages containing any of the given entity types |
| `filters.CaptionRegex(pattern)` | Photo/video/document captions matching a regex |

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
| `filters.LOCATION` | Messages containing a location |
| `filters.VENUE` | Messages containing a venue |
| `filters.CONTACT` | Messages containing a contact |
| `filters.INVOICE` | Messages containing an invoice |
| `filters.GAME` | Messages containing a game |
| `filters.POLL` | Messages containing a poll |
| `filters.DICE` | Messages containing a dice |

### Status Update Filters

| Filter | Matches |
|---|---|
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | One or more users joined |
| `filters.StatusUpdate.LEFT_CHAT_MEMBER` | A user left |
| `filters.StatusUpdate.NEW_CHAT_TITLE` | Chat title changed |
| `filters.StatusUpdate.NEW_CHAT_PHOTO` | Chat photo changed |
| `filters.StatusUpdate.DELETE_CHAT_PHOTO` | Chat photo deleted |
| `filters.StatusUpdate.GROUP_CHAT_CREATED` | Group chat created |
| `filters.StatusUpdate.SUPERGROUP_CHAT_CREATED` | Supergroup created |
| `filters.StatusUpdate.CHANNEL_CHAT_CREATED` | Channel created |
| `filters.StatusUpdate.PINNED_MESSAGE` | Message pinned |
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
| `filters.StatusUpdate.ALL` | Any status update |

### Chat Type Filters

| Filter | Matches |
|---|---|
| `filters.ChatType.PRIVATE` | One-on-one chats |
| `filters.ChatType.GROUP` | Basic group chats |
| `filters.ChatType.SUPERGROUP` | Supergroup chats |
| `filters.ChatType.CHANNEL` | Channel posts |
| `filters.ChatType.ALL` | Any chat type |

### User & Chat Filters

| Filter | Matches |
|---|---|
| `filters.User(user_id=id)` | Messages from a specific user ID |
| `filters.User(user_id=[id1, id2])` | Messages from any of the listed user IDs |
| `filters.User(username="name")` | Messages from a specific username |
| `filters.User(username=["name1", "name2"])` | Messages from any of the listed usernames |
| `filters.Chat(chat_id=-100123)` | Messages in a specific chat |
| `filters.Chat(chat_id=[-100111, -100222])` | Messages in any of the listed chats |
| `filters.PRIVATE` | Shortcut for `filters.ChatType.PRIVATE` |

### Other Content Filters

| Filter | Matches |
|---|---|
| `filters.FORWARDED` | Forwarded messages |
| `filters.REPLY` | Messages that are replies |
| `filters.VIA_BOT` | Messages sent via another bot |
| `filters.SUCCESSFUL_PAYMENT` | Successful payment |
| `filters.ALL` | Matches every message |

### Filter Combinators

| Operator | Meaning | Example |
|---|---|---|
| `&` | AND — both conditions true | `filters.TEXT & ~filters.COMMAND` |
| `\|` | OR — at least one true | `filters.PHOTO \| filters.VIDEO` |
| `~` | NOT — inverts the filter | `~filters.COMMAND` |

```python
# Common patterns
filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE & ~filters.User(is_bot=True)
(filters.PHOTO | filters.VIDEO) & filters.CaptionRegex(r"\S+")
filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.SUPERGROUP)
```

### Custom Filters

```python
from telegram.ext import filters


class AdminFilter(filters.BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        super().__init__()
        self.admin_ids = admin_ids

    def filter(self, update) -> bool:
        if update.effective_user is None:
            return False
        return update.effective_user.id in self.admin_ids


application.add_handler(
    MessageHandler(AdminFilter(ADMIN_IDS) & filters.COMMAND, handle_admin_command)
)
```

### Common Filter Combinations Quick Reference

| Use Case | Filter Expression |
|---|---|
| Text that isn't a command | `filters.TEXT & ~filters.COMMAND` |
| Private text from humans | `filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND & ~filters.User(is_bot=True)` |
| Photos or videos | `filters.PHOTO \| filters.VIDEO` |
| Messages with URLs | `filters.Entity(MessageEntityType.URL)` |
| Forwarded messages | `filters.FORWARDED` |
| Replies to the bot | `filters.REPLY & filters.User(is_bot=True)` |
| Messages from admins only | `filters.User(user_id=ADMIN_IDS)` |
| Any status update | `filters.StatusUpdate.ALL` |
| New members joining | `filters.StatusUpdate.NEW_CHAT_MEMBERS` |

---

## 4. Keyboards & Inline Buttons

### InlineKeyboardButton — All Fields

| Field | Type | Description |
|---|---|---|
| `text` | `str` | **Required.** Button label (1–64 chars). Supports emoji. |
| `url` | `str` | Opens URL in browser on tap. |
| `callback_data` | `str` | 1–64 bytes sent back via `CallbackQuery`. |
| `web_app` | `WebAppInfo` | Launches a Telegram Mini App. |
| `login_url` | `LoginUrl` | Auto-authorizes via Telegram Login Widget. |
| `switch_inline_query` | `str` | Switches to inline mode with pre-filled query. |
| `switch_inline_query_current_chat` | `str` | Same, scoped to current chat. |
| `switch_inline_query_chosen_chat` | `SwitchInlineQueryChosenChat` | Prompts user to pick a chat before inline mode. |
| `copy_text` | `CopyTextButton` | Copies text to clipboard on tap. |
| `callback_game` | `CallbackGame` | Launches bot's game. |
| `pay` | `bool` | Payment button. Must be first button in single-button keyboard. |

### InlineKeyboardMarkup

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [
        InlineKeyboardButton("Option A", callback_data="opt_a"),
        InlineKeyboardButton("Option B", callback_data="opt_b"),
    ],
    [InlineKeyboardButton("Visit Docs", url="https://example.com")],
]
markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Choose:", reply_markup=markup)
```

### ReplyKeyboardMarkup

| Parameter | Type | Default | Description |
|---|---|---|---|
| `keyboard` | `list[list[KeyboardButton]]` | — | **Required.** 2D list of button rows. |
| `resize_keyboard` | `bool` | `False` | Shrink keyboard to fit. **Always set True.** |
| `one_time_keyboard` | `bool` | `False` | Hide keyboard after one press. |
| `input_field_placeholder` | `str` | `""` | Hint text in input field. Max 64 chars. |
| `selective` | `bool` | `False` | Show only to specific users in groups. |
| `is_persistent` | `bool` | `False` | Keep visible after user sends a message. |

```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

keyboard = [
    [KeyboardButton("Share Location", request_location=True)],
    [KeyboardButton("Share Contact", request_contact=True)],
    [KeyboardButton("Menu")],
]
await update.message.reply_text(
    "Use the keyboard:",
    reply_markup=ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    ),
)
```

### KeyboardButton — All Fields

| Field | Type | Description |
|---|---|---|
| `text` | `str` | **Required.** Button label. |
| `request_users` | `KeyboardButtonRequestUsers` | Opens UI to select users. |
| `request_chat` | `KeyboardButtonRequestChat` | Opens UI to select a chat. |
| `request_contact` | `bool` | Prompts user to share phone number. |
| `request_location` | `bool` | Prompts user to share location. |
| `request_poll` | `KeyboardButtonRequestPoll` | Opens poll creation interface. |
| `web_app` | `WebAppInfo` | Launches Mini App from keyboard. |

### ReplyKeyboardRemove

Removes the custom reply keyboard and restores the default.

```python
from telegram import ReplyKeyboardRemove

await update.message.reply_text("Done.", reply_markup=ReplyKeyboardRemove())
```

### ForceReply

Forces the user to reply to a specific message. Highlights the message and opens reply interface.

```python
from telegram import ForceReply

await update.message.reply_text(
    "What is your name?", reply_markup=ForceReply(selective=False)
)
```

---

## 5. ConversationHandler

Implements a finite state machine for multi-step dialogs.

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `entry_points` | `list[Handler]` | **Required** | Handlers that start a conversation. |
| `states` | `dict[int \| str \| Enum, list[Handler]]` | **Required** | Maps each state to its handlers. |
| `fallbacks` | `list[Handler]` | `[]` | Handlers that fire from any state. |
| `per_user` | `bool` | `True` | Track state per user. |
| `per_chat` | `bool` | `False` | Track state per chat. |
| `per_message` | `bool` | `False` | Track state per message. |
| `conversation_timeout` | `int \| float \| None` | `None` | Seconds before auto-cancel. `None` = no timeout. |
| `name` | `str \| None` | `None` | Unique name for persistence. |
| `persistent` | `bool` | `False` | Persist state across restarts. |
| `map_to_parent` | `dict[int \| str, int \| str]` | `{}` | Map states to parent conversation states (nested). |
| `block` | `bool` | `True` | Whether handler blocks other handlers. |

### State Definition Patterns

```python
# Using range() for numbered states
NAME, EMAIL, CONFIRM = range(3)


# Using Enum for named states
class RegistrationState(enum.Enum):
    NAME = "name"
    EMAIL = "email"
    CONFIRM = "confirm"


# String-based states
states = {
    "awaiting_name": [MessageHandler(filters.TEXT, get_name)],
    "awaiting_email": [MessageHandler(filters.TEXT, get_email)],
}
```

### Complete Example

```python
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

NAME, AGE = range(2)


async def start_conversation(update, context):
    await update.message.reply_text("What is your name?")
    return NAME


async def receive_name(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE


async def receive_age(update, context):
    name = context.user_data["name"]
    age = update.message.text
    await update.message.reply_text(f"{name}, you are {age} years old.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register", start_conversation)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_user=True,
    per_chat=False,
    per_message=False,
    conversation_timeout=300,
    name="registration",
    persistent=True,
)
```

### Nested Conversations with `map_to_parent`

```python
MAIN, SUB_CONVERSATION = range(2)
SUB_START, SUB_STATE1, SUB_STATE2 = range(3)

sub_conv = ConversationHandler(
    entry_points=[CommandHandler("sub", sub_start)],
    states={
        SUB_STATE1: [MessageHandler(filters.TEXT, sub_state1)],
        SUB_STATE2: [MessageHandler(filters.TEXT, sub_state2)],
    },
    fallbacks=[CommandHandler("cancel", sub_cancel)],
    map_to_parent={ConversationHandler.END: MAIN},
)

main_conv = ConversationHandler(
    entry_points=[CommandHandler("start", main_start)],
    states={MAIN: [sub_conv]},
    fallbacks=[CommandHandler("cancel", main_cancel)],
)
```

---

## 6. Context Objects

### `ContextTypes.DEFAULT_TYPE` Properties

| Property | Type | Description |
|---|---|---|
| `context.bot` | `Bot` | Bot instance — for sending messages, API calls |
| `context.bot_data` | `dict` | **Bot-wide** persistent data (shared across all users/chats) |
| `context.user_data` | `dict` | **Per-user** persistent data |
| `context.chat_data` | `dict` | **Per-chat** persistent data |
| `context.args` | `list[str]` | Command arguments (split by spaces, only in `CommandHandler`) |
| `context.match` | `re.Match \| None` | Regex match object (only in `MessageHandler` with `filters.Regex`) |
| `context.job_queue` | `JobQueue` | Job queue for scheduling background tasks |
| `context.error` | `Exception` | The exception (only in error handlers) |
| `context.update` | `Update` | The full update object |
| `context.application` | `Application` | The Application instance |

---

## 7. Job Queue & Background Tasks

Requires: `pip install python-telegram-bot[job-queue]`

### Scheduling Methods

#### `run_once` — One-Shot Task

```python
context.job_queue.run_once(
    callback=send_reminder,
    when=timedelta(seconds=seconds),
    data={"chat_id": chat_id, "message": "Reminder!"},
    name=f"reminder_{user_id}_{chat_id}",
)
```

#### `run_repeating` — Periodic Task

```python
context.job_queue.run_repeating(
    callback=cleanup_old_messages,
    interval=1800,  # 30 minutes
    first=60,  # Start after 1 minute
    name="message_cleanup",
)
```

#### `run_daily` — Daily Recurring Task

```python
from datetime import time, timezone

context.job_queue.run_daily(
    callback=daily_report,
    time=time(hour=9, minute=0, tzinfo=timezone.utc),
    name="daily_report",
)
```

### Job Properties

| Property | Type | Description |
|---|---|---|
| `context.job.name` | `str` | Unique job name |
| `context.job.chat_id` | `int \| None` | Chat ID |
| `context.job.user_id` | `int \| None` | User ID |
| `context.job.data` | `Any` | Arbitrary data passed when creating the job |
| `context.job.job_queue` | `JobQueue` | Reference back to the job queue |

### Cancelling Jobs

```python
current_jobs = context.job_queue.get_jobs_by_name(f"reminder_{user_id}_{chat_id}")
for job in current_jobs:
    job.schedule_removal()
```

---

## 8. Media, Files & Albums

### Three Methods of Sending Files

| Method | Size Limit | Speed | Use Case |
|---|---|---|---|
| `file_id` | No limit (Telegram handles internally) | Instant | Re-sending previously received files |
| HTTP URL | 5 MB (photos), 20 MB (other) | Fast | Files hosted on public servers |
| Binary upload | 10 MB (photos), 50 MB (other) | Slow | Local files not accessible via URL |

### `file_id` Rules

| Property | Scope | Stability | Use for download? |
|---|---|---|---|
| `file_id` | Per-bot | May change on re-upload | Yes (pass to `getFile`) |
| `file_unique_id` | Cross-bot | Stable across re-uploads | No (informational only) |

### Media Types & Methods

#### `sendPhoto`

| Parameter | Type | Description |
|---|---|---|
| `photo` | `str \| Path \| IO` | `file_id`, URL, or binary upload |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | `MarkdownV2`, `HTML`, or `Markdown` |
| `has_spoiler` | `bool` | Blurred until tapped |
| `show_caption_above_media` | `bool` | Caption renders above the photo |

#### `sendAudio`

| Parameter | Type | Description |
|---|---|---|
| `audio` | `str \| Path \| IO` | MP3 or M4A recommended |
| `title` | `str` | Track title |
| `performer` | `str` | Artist name |
| `duration` | `int` | Length in seconds |
| `thumbnail` | `str \| Path \| IO` | `.jpg` or `.png`, up to 200 KB |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `has_spoiler` | `bool` | Blur the audio message |

#### `sendDocument`

| Parameter | Type | Description |
|---|---|---|
| `document` | `str \| Path \| IO` | Any file type |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `disable_content_type_detection` | `bool` | Prevents MIME type sniffing |
| `thumbnail` | `str \| Path \| IO` | `.jpg` or `.png`, up to 200 KB |

#### `sendVideo`

| Parameter | Type | Description |
|---|---|---|
| `video` | `str \| Path \| IO` | MPEG4 recommended |
| `width` | `int` | Video width in pixels |
| `height` | `int` | Video height in pixels |
| `duration` | `int` | Length in seconds |
| `supports_streaming` | `bool` | Enables progressive download |
| `cover` | `str \| Path \| IO` | Thumbnail image before playback |
| `start_timestamp` | `int` | Second at which playback begins |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `has_spoiler` | `bool` | Blur the video |

#### `sendAnimation`

| Parameter | Type | Description |
|---|---|---|
| `animation` | `str \| Path \| IO` | `.gif` or silent `.mp4` |
| `width` | `int` | Width in pixels |
| `height` | `int` | Height in pixels |
| `duration` | `int` | Loop duration in seconds |
| `thumbnail` | `str \| Path \| IO` | Custom thumbnail |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `has_spoiler` | `bool` | Blur the animation |

#### `sendVoice`

| Parameter | Type | Description |
|---|---|---|
| `voice` | `str \| Path \| IO` | OGG/OPUS, MP3, or M4A |
| `duration` | `int` | Length in seconds |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |

#### `sendVideoNote`

| Parameter | Type | Description |
|---|---|---|
| `video_note` | `str \| Path \| IO` | MPEG4, up to 1 minute |
| `length` | `int` | Diameter (1–1080 px) |
| `duration` | `int` | Length in seconds |
| `thumbnail` | `str \| Path \| IO` | Custom thumbnail |

#### `sendSticker`

| Parameter | Type | Description |
|---|---|---|
| `sticker` | `str \| Path \| IO` | `.webp`, `.tgs`, or `.webm` |

#### `sendLocation`

| Parameter | Type | Description |
|---|---|---|
| `latitude` | `float` | Latitude in degrees |
| `longitude` | `float` | Longitude in degrees |
| `horizontal_accuracy` | `float` | Accuracy radius in meters (0–1500) |
| `live_period` | `int` | Seconds the location updates (60–86400) |
| `heading` | `int` | Direction of movement (1–360°) |
| `proximity_alert_radius` | `int` | Meters to trigger arrival alert (0–100000) |

#### `sendVenue`

| Parameter | Type | Description |
|---|---|---|
| `latitude` | `float` | Latitude |
| `longitude` | `float` | Longitude |
| `title` | `str` | Venue name |
| `address` | `str` | Venue address |
| `foursquare_id` | `str` | Foursquare venue ID |
| `foursquare_type` | `str` | Foursquare venue type |

#### `sendContact`

| Parameter | Type | Description |
|---|---|---|
| `phone_number` | `str` | Contact's phone number |
| `first_name` | `str` | Contact's first name |
| `last_name` | `str` | Contact's last name |
| `vcard` | `str` | Additional data (vCard format) |

#### `sendPoll`

| Parameter | Type | Description |
|---|---|---|
| `question` | `str` | Poll question (1–300 chars) |
| `options` | `list[str]` | List of answer options (2–10 strings, 1–100 chars each) |
| `is_anonymous` | `bool` | True by default |
| `type` | `str` | `"regular"` or `"quiz"` |
| `allows_multiple_answers` | `bool` | Allow multiple selections |
| `correct_option_id` | `int` | Correct option ID (for quiz) |
| `explanation` | `str` | Explanation of correct answer |
| `explanation_parse_mode` | `str` | Formatting mode for explanation |
| `open_period` | `int` | Seconds the poll is open (5–600) |
| `close_date` | `datetime` | When the poll closes |
| `is_closed` | `bool` | Close immediately |

#### `sendDice`

| Parameter | Type | Description |
|---|---|---|
| `emoji` | `str` | `"🎲"`, `"🎯"`, `"🏀"`, `"⚽"`, `"🎳"`, `"🎰"` |

#### `sendMediaGroup`

| Parameter | Type | Description |
|---|---|---|
| `media` | `list[InputMedia]` | 2–10 media objects (InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument) |

#### `sendPaidMedia`

| Parameter | Type | Description |
|---|---|---|
| `star_count` | `int` | Number of Stars to charge |
| `media` | `list[InputPaidMedia]` | Media items |
| `caption` | `str` | Caption for all media |
| `parse_mode` | `str` | Formatting mode |

---

## 9. Message Formatting

### MarkdownV2 Syntax

| Entity | Syntax | Example |
|---|---|---|
| Bold | `*text*` | `*bold*` |
| Italic | `_text_` | `_italic_` |
| Underline | `__text__` | `__underlined__` |
| Strikethrough | `~text~` | `~struck~` |
| Spoiler | `\|\|text\|\|` | `\|\|hidden\|\|` |
| Inline code | `` `code` `` | `` `print()` `` |
| Pre block | ` ```code``` ` | ` ```1 + 1``` ` |
| Code block with lang | ` ```python code``` ` | ` ```python\nprint("hi")``` ` |
| Blockquote | `>text` | `>quoted text` |
| Expandable blockquote | `**>text\|\|` | `**>tap to expand\|\|` |
| Inline URL | `[text](url)` | `[Google](https://google.com)` |
| Inline mention | `[name](tg://user?id=123)` | `[John](tg://user?id=123456)` |

**Characters that MUST be escaped in MarkdownV2:**
```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

**Inside code/pre blocks:** Only `` ` `` and `\` need escaping.

### HTML Syntax

| Entity | HTML | Also accepted |
|---|---|---|
| Bold | `<b>text</b>` | `<strong>text</strong>` |
| Italic | `<i>text</i>` | `<em>text</em>` |
| Underline | `<u>text</u>` | `<ins>text</ins>` |
| Strikethrough | `<s>text</s>` | `<strike>`, `<del>` |
| Spoiler | `<span class="tg-spoiler">text</span>` | `<tg-spoiler>text</tg-spoiler>` |
| Inline code | `<code>text</code>` | — |
| Pre block | `<pre>text</pre>` | — |
| Code block | `<pre><code class="language-python">code</code></pre>` | — |
| Blockquote | `<blockquote>text</blockquote>` | — |
| Expandable blockquote | `<blockquote expandable>text</blockquote>` | — |
| Inline URL | `<a href="URL">text</a>` | — |
| Custom emoji | `<tg-emoji emoji-id="ID">👍</tg-emoji>` | — |

**Characters that need escaping in HTML:** Only `<`, `>`, `&`

### Entity Types

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

### Formatting Recommendation

| Mode | Recommendation |
|---|---|
| `HTML` | Preferred — familiar syntax, fewer escaping pitfalls |
| `MarkdownV2` | Powerful but escaping-heavy — use when HTML isn't an option |
| `Markdown` | Legacy — limited features, no nesting. Avoid in new code |

---

## 10. Inline Mode

### InlineQueryHandler

| Property | Type | Description |
|---|---|---|
| `update.inline_query.query` | `str` | Text user typed after `@botname` |
| `update.inline_query.from_user` | `User` | The user who sent the query |
| `update.inline_query.offset` | `str` | Pagination offset (empty string for first page) |
| `update.inline_query.location` | `Location \| None` | User's location (if shared) |
| `update.inline_query.chat_type` | `str \| None` | `sender`, `private`, `group`, `supergroup`, `channel` |
| `update.inline_query.id` | `str` | Unique query ID for answering |

### InlineQueryResult Types

**`InlineQueryResultArticle`** (Most Common):

| Parameter | Required | Description |
|---|---|---|
| `id` | ✅ | Unique identifier |
| `title` | ✅ | Result title |
| `input_message_content` | ✅ | Content sent when selected |
| `description` | ❌ | Short description (1-100 chars) |
| `thumb_url` | ❌ | Thumbnail URL (96×96 recommended) |
| `thumb_width` | ❌ | Thumbnail width |
| `thumb_height` | ❌ | Thumbnail height |
| `reply_markup` | ❌ | Inline keyboard |
| `parse_mode` | ❌ | `HTML` or `MarkdownV2` |

### Pagination

```python
offset = int(update.inline_query.offset) if update.inline_query.offset else 0
page_size = 10
results = fetch_results(offset, page_size)
next_offset = str(offset + page_size) if len(results) == page_size else ""
await update.inline_query.answer(
    results=results, next_offset=next_offset, cache_time=30, is_personal=True
)
```

---

## 11. Deep Linking

### Link Format

```
https://t.me/botname?start=PARAMETER
```

| Parameter | Max Length | Description |
|---|---|---|
| `start` | 64 chars | Starts private chat, passes `PARAMETER` to `/start` |
| `startgroup` | 64 chars | Prompts user to add bot to group |
| `startapp` | 64 chars | Launches Telegram Mini App |

- Maximum **64 characters** (including encoding)
- Must be **base64-safe**: `[A-Za-z0-9_-]` only
- Payload passed as `context.args[0]` in `/start` handler

### Use Cases

| Use Case | Payload Example |
|---|---|
| Referral tracking | `ref_AbCdEf` |
| Pre-filled actions | `search_python` |
| QR code access | `qr_product_123` |
| Group onboarding | `invite_-100123` |
| Marketing campaigns | `promo_SUMMER26` |

---

## 12. Payments & Telegram Stars

### Key Concepts

| Concept | Description |
|---|---|
| **Telegram Stars** | Virtual currency users buy with real money; bots receive Stars for digital goods |
| **Payment Providers** | Third-party processors (e.g. Stripe) |
| **Invoice** | Payment request sent by bot to user |
| **Pre-checkout** | Server-side confirmation (must respond within 10 seconds) |
| **Paid Media** | Photos, videos, or live photos sold for Stars |

### `sendInvoice` Parameters

**Required:**

| Parameter | Type | Description |
|---|---|---|
| `chat_id` | `int \| str` | Target chat ID or username |
| `title` | `str` | Product name (1-32 chars) |
| `description` | `str` | Product description (1-255 chars) |
| `payload` | `str` | Bot-defined order ID (1-128 bytes) |
| `provider_token` | `str` | Payment provider token from BotFather (empty string for Stars) |
| `currency` | `str` | ISO 4217 currency code (`"USD"`, `"XTR"` for Stars) |
| `prices` | `list[LabeledPrice]` | Price breakdown |

**Optional:**

| Parameter | Type | Description |
|---|---|---|
| `max_tip_amount` | `int` | Maximum tip amount |
| `suggested_tip_amounts` | `list[int]` | Suggested tip amounts (0-4 items) |
| `provider_data` | `str` | JSON string with provider-specific data |
| `photo_url` | `str` | Product photo URL |
| `need_name` | `bool` | Request recipient's full name |
| `need_phone_number` | `bool` | Request recipient's phone number |
| `need_email` | `bool` | Request recipient's email |
| `need_shipping_address` | `bool` | Request recipient's shipping address |
| `is_flexible` | `bool` | True if final price depends on shipping |
| `start_parameter` | `str` | Unique deep-link parameter for public channels |

### `LabeledPrice`

```python
from telegram import LabeledPrice

prices = [
    LabeledPrice(label="Subtotal", amount=999),  # $9.99
    LabeledPrice(label="Tax", amount=80),  # $0.80
    LabeledPrice(label="Discount", amount=-200),  # -$2.00
]
```

### Payment Flow

1. **Bot sends invoice** → `sendInvoice`
2. **User taps "Pay"** → Telegram displays payment form
3. **(Optional) Shipping** → If `is_flexible=True`, `ShippingQuery` sent
4. **Pre-checkout** → `PreCheckoutQuery` sent, bot must respond within 10 seconds
5. **Payment success** → `successful_payment` message in user's chat

### Telegram Stars

| Field | Type | Description |
|---|---|---|
| `amount` | `int` | Whole Star units |
| `nanostar_amount` | `int` | Fractional part (1 Star = 1,000,000,000 nanostars) |

---

## 13. Mini Apps / Web Apps

### Launching a Mini App

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [
        InlineKeyboardButton(
            "Open Mini App", web_app=WebAppInfo(url="https://yourdomain.com/app")
        )
    ]
]
await update.message.reply_text("Launch:", reply_markup=InlineKeyboardMarkup(keyboard))
```

### MenuButtonWebApp

```python
from telegram import MenuButtonWebApp

await bot.set_chat_menu_button(
    chat_id=chat_id,
    menu_button=MenuButtonWebApp(
        text="Open App", web_app=WebAppInfo(url="https://yourdomain.com/app")
    ),
)
```

### initData Validation (CRITICAL)

```python
import hashlib, hmac, json, time
from urllib.parse import parse_qs


def validate_webapp_initdata(init_data: str, bot_token: str) -> dict:
    parsed = parse_qs(init_data)
    if "hash" not in parsed:
        raise ValueError("Missing hash in initData")
    received_hash = parsed.pop("hash")[0]
    data_check_pairs = [
        f"{key}={value}" for key, values in sorted(parsed.items()) for value in values
    ]
    data_check_string = "\n".join(data_check_pairs)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(received_hash, expected_hash):
        raise ValueError("Invalid initData hash")
    auth_date = int(parsed.get("auth_date", [0])[0])
    if time.time() - auth_date > 86400:
        raise ValueError("initData expired")
    return {
        key: values[0] if len(values) == 1 else values for key, values in parsed.items()
    }
```

### Mini App Security Checklist

| Requirement | Priority |
|---|---|
| Server-side `initData` validation | CRITICAL |
| `auth_date` freshness check | CRITICAL |
| HTTPS for Mini App URL | CRITICAL |
| Origin header validation | HIGH |
| Content Security Policy | HIGH |
| CORS configuration | HIGH |
| Rate limiting on API endpoints | HIGH |
| Input validation on all endpoints | HIGH |

---

## 14. Persistence

### Persistence Backends

| Backend | Storage | Use Case |
|---|---|---|
| `PicklePersistence` | File (pickle) | Production bots — simple, reliable |
| `DictPersistence` | In-memory (dict) | Testing and development |
| `PostgresPersistence` | PostgreSQL | High-concurrency production bots |
| `MongoPersistence` | MongoDB | Document-oriented storage |

### What Gets Persisted

| Data Store | Scope | Example Use |
|---|---|---|
| `context.user_data` | Per user | Preferences, settings, conversation state |
| `context.chat_data` | Per chat | Group-specific counters, rules |
| `context.bot_data` | Global | Shared configuration, statistics |

### Configuring PicklePersistence

```python
from telegram.ext import ApplicationBuilder, PicklePersistence

persistence = PicklePersistence(
    filepath="bot_data.pkl",
    store_bot_data=True,
    store_chat_data=True,
    store_user_data=True,
    collect_files=False,
)

app = ApplicationBuilder().token("BOT_TOKEN").persistence(persistence).build()
```

> **Warning:** Never store non-serializable objects (DB connections, threads, locks) in PicklePersistence.

---

## 15. Groups, Channels & Admin

### Chat Types Comparison

| Type | Member Count | Bot Capabilities | File Size Limit |
|---|---|---|---|
| `private` | 2 | Full access | Standard |
| `group` | 2–200,000 | Limited by privacy mode | 32 MB |
| `supergroup` | 2–200,000 | Full if admin or privacy off | 2 GB |
| `channel` | Unlimited | Admin rights required | Standard |

### Privacy Mode (Default: ON)

Bot only receives:
- Commands (messages starting with `/`)
- Replies to the bot's own messages
- Messages that explicitly `@mention` the bot
- Service messages (new members, pinned messages, etc.)
- Channel posts (if bot is admin)

### Privacy Mode + Admin Visibility

| Scenario | Privacy Mode | Admin Status | Sees All Messages? |
|---|:---:|:---:|:---:|
| Regular group | ON | No | No |
| Regular group | OFF | No | Yes |
| Supergroup | ON | No | No |
| Supergroup | ON | Yes | Yes |
| Supergroup | OFF | No | Yes |
| Supergroup | OFF | Yes | Yes |

### ChatPermissions

```python
from telegram import ChatPermissions

permissions = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
    can_manage_topics=True,
)
await bot.restrict_chat_member(
    chat_id=chat_id, user_id=user_id, permissions=permissions
)
```

### ChatAdministratorRights

```python
from telegram import ChatAdministratorRights

rights = ChatAdministratorRights(
    is_anonymous=True,
    can_manage_chat=True,
    can_delete_messages=True,
    can_manage_video_chats=True,
    can_restrict_members=True,
    can_promote_members=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
    can_manage_topics=True,
    can_post_stories=True,
    can_edit_stories=True,
    can_delete_stories=True,
)
await bot.promote_chat_member(chat_id=chat_id, user_id=user_id, rights=rights)
```

### Forum Topics

```python
# Send message to specific topic
await bot.send_message(
    chat_id=chat_id,
    message_thread_id=thread_id,
    text="Hello from topic!",
)

# Create forum topic
await bot.create_forum_topic(chat_id=chat_id, name="General", icon_color=0x6FB3F2)
```

---

## 16. Bot Commands Menu

### `BotCommandScope`

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

### Registering Commands

```python
from telegram import BotCommand, BotCommandScopeDefault

commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Show help"),
    BotCommand("settings", "Open settings"),
]
await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
```

### Per-Language Commands

```python
await bot.set_my_commands(
    commands=[BotCommand("start", "Iniciar el bot")],
    language_code="es",
    scope=BotCommandScopeAllPrivateChats(),
)
```

### Admin-Only Commands

```python
await bot.set_my_commands(
    commands=[BotCommand("ban", "Ban a user"), BotCommand("mute", "Mute a user")],
    scope=BotCommandScopeChatAdministrators(chat_id=ADMIN_CHAT_ID),
)
```

---

## 17. Rich Messages

Available in python-telegram-bot v20+ and Telegram Bot API 8.0+.

### Block Types

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

### `sendRichMessage`

```python
from telegram.rich import (
    RichMessage,
    Heading,
    Paragraph,
    List,
    ListItem,
    CodeBlock,
    Table,
    TableRow,
    TableCell,
    Bold,
    Italic,
)

rich = RichMessage(
    blocks=[
        Heading(level=2, text="Status"),
        Paragraph(blocks=[Bold(text="Operational")]),
        Table(
            rows=[
                TableRow(
                    cells=[
                        TableCell(text="Service", bold=True),
                        TableCell(text="Status", bold=True),
                    ]
                ),
                TableRow(cells=[TableCell(text="API"), TableCell(text="Up")]),
            ]
        ),
    ]
)
await update.message.reply_rich_message(rich)
```

### Streaming AI Responses

```python
draft = await update.message.reply_rich_message_draft(
    blocks=[Paragraph(text="Thinking...")]
)
collected = ""
async for chunk in stream_ai_response(query):
    collected += chunk
    await draft.edit(
        blocks=[
            Paragraph(text=collected),
            Paragraph(text="_Generating..._", italic=True),
        ]
    )
await draft.edit(blocks=[Paragraph(text=collected)])
```

---

## 18. Local Bot API Server

### Benefits

| Feature | Standard API | Local API Server |
|---|---|---|
| Max file size | 50 MB | 2 GB |
| Max download | 20 MB | 2 GB |
| Simultaneous connections | 400 | Higher (configurable) |
| Self-hosted | No | Yes |
| File download speed | Telegram servers | Local network |

### Setup

```python
from telegram.ext import ApplicationBuilder

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .base_url("http://localhost:8081/bot")
    .build()
)
```

---

## 19. Rate Limiting

### Official Limits

| Limit | Value |
|---|---|
| Messages to different users | **30 messages/second** |
| Messages per chat | **1 message/second** |
| Group creation | **1 group/minute** |
| Inline queries | **30 queries/second** |
| File downloads | **~1.5 GB/minute** |
| File uploads (standard) | **50 MB per file** |
| File uploads (local API) | **2 GB per file** |

### Token Bucket Implementation

```python
import asyncio, time


class TokenBucketRateLimiter:
    def __init__(self, max_tokens: int, refill_rate: float) -> None:
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = float(max_tokens)
        self.last_refill = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.refill_rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
```

---

## 20. Deployment & Hosting

### Polling vs Webhooks

| Feature | Polling | Webhooks |
|---|---|---|
| Setup complexity | Low | Medium |
| Public URL required | No | Yes (HTTPS) |
| Latency | ~1-2 seconds | Near-instant |
| Resource usage | Higher (constant requests) | Lower (event-driven) |
| Best for | Development, local testing | Production, high-traffic bots |

### Built-in Webhook Runner

```python
app.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path="webhook",
    webhook_url="https://yourdomain.com/webhook",
    secret_token="YOUR_SECRET_TOKEN",
)
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### systemd Service Example

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/bot
ExecStart=/opt/bot/venv/bin/python bot.py
Restart=always
RestartSec=10
Environment=BOT_TOKEN=your_token_here

[Install]
WantedBy=multi-user.target
```

---

## 21. Security

### Token Security (CRITICAL)

| # | Security Concern | Severity | Mitigation |
|---|---|---|---|
| 1 | Token hardcoded in source | CRITICAL | Environment variables |
| 2 | Token committed to version control | CRITICAL | .gitignore + revoke token |
| 3 | No webhook authentication | CRITICAL | `secret_token` validation |
| 4 | Mini App `initData` not validated | CRITICAL | HMAC-SHA256 validation |
| 5 | No input validation | HIGH | Validate all inputs |
| 6 | HTML/Markdown injection | HIGH | Escape user text |
| 7 | No rate limiting | HIGH | Token bucket limiter |
| 8 | No authorization checks | HIGH | Admin verification |
| 9 | Callback data not validated | HIGH | Pattern validation |
| 10 | Deep link abuse | HIGH | Payload validation |

### Webhook Security

```python
# Validate X-Telegram-Bot-Api-Secret-Token header
secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
if secret_token != expected_secret:
    return Response(status_code=403)
```

### HTML/Markdown Injection Prevention

```python
import html


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


await update.message.reply_text(
    f"User said: {escape_html(user_input)}",
    parse_mode="HTML",
)
```

### Input Validation

```python
def validate_callback_data(data: str) -> bool:
    import re

    pattern = r"^(order|item|settings):(confirm|cancel|edit|toggle):\d+$"
    return bool(re.match(pattern, data))
```

### Rate Limiting Implementation

```python
class RateLimitFilter(filters.BaseFilter):
    def __init__(self, max_messages: int = 5, window_seconds: int = 60) -> None:
        super().__init__()
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._user_timestamps: dict[int, list[float]] = {}

    def filter(self, update: Update) -> bool:
        user_id = update.effective_user.id
        now = time.monotonic()
        cutoff = now - self.window_seconds
        timestamps = self._user_timestamps.setdefault(user_id, [])
        timestamps[:] = [t for t in timestamps if t > cutoff]
        if len(timestamps) >= self.max_messages:
            return False
        timestamps.append(now)
        return True
```

### Secure Deployment Checklist

| # | Item | Priority |
|---|---|---|
| 1 | Bot token stored in environment variable | CRITICAL |
| 2 | `.env` file in `.gitignore` | CRITICAL |
| 3 | Separate tokens for dev/staging/production | CRITICAL |
| 4 | HTTPS enabled for webhooks | CRITICAL |
| 5 | Webhook `secret_token` configured | HIGH |
| 6 | `X-Telegram-Bot-Api-Secret-Token` header validated | HIGH |
| 7 | All user input validated and sanitized | HIGH |
| 8 | HTML/Markdown injection prevention | HIGH |
| 9 | Per-user rate limiting implemented | HIGH |
| 10 | RetryAfter exception handled | HIGH |
| 11 | Admin access verified server-side | HIGH |
| 12 | Callback data validated before processing | HIGH |
| 13 | Deep link payloads validated | HIGH |
| 14 | Mini App `initData` validated server-side | HIGH |
| 15 | File downloads size-limited | MEDIUM |
| 16 | File MIME types verified | MEDIUM |
| 17 | Error handling catches all exceptions | MEDIUM |
| 18 | Sensitive data filtered from logs | MEDIUM |
| 19 | Structured logging implemented | MEDIUM |
| 20 | Dependency versions pinned | MEDIUM |
| 21 | `pip-audit` run before deployment | MEDIUM |
| 22 | Conversation timeouts configured | MEDIUM |
| 23 | Anti-spam measures active in groups | MEDIUM |
| 24 | GDPR compliance (deletion, export) | LOW |
| 25 | PII data minimization applied | LOW |

### Dependency Security

```bash
# Pin exact versions
pip install pip-audit
pip-audit

# Or use safety
pip install safety
safety check

# Generate hashed requirements
pip install pip-tools
pip-compile --generate-hashes requirements.in -o requirements.txt
```

---

## 22. Testing

### Testing Strategy

| Tier | Scope | Speed | Tooling |
|---|---|---|---|
| **Unit** | Individual handler functions, utility modules | Milliseconds | `pytest`, `unittest.mock` |
| **Integration** | Handler registration, filter chains, middleware pipelines | Hundreds of ms | `python-telegram-bot` test utilities, `pytest-asyncio` |
| **End-to-End** | Real Telegram API, real bot token, test group/channel | Seconds | `Application` builder, dedicated test bot |

### Unit Testing with pytest

```python
import pytest
from unittest.mock import AsyncMock, Mock
from telegram import Chat, Update, User
from telegram.ext import ContextTypes


@pytest.fixture
def update() -> Mock:
    user = User(id=456, first_name="Alice", is_bot=False)
    chat = Chat(id=456, type="private")
    upd = Mock(spec=Update)
    upd.message = Mock(spec=Update.message)
    upd.message.from_user = user
    upd.message.chat = chat
    upd.message.reply_text = AsyncMock()
    upd.message.text = "Hello"
    upd.effective_user = user
    upd.effective_chat = chat
    return upd


@pytest.fixture
def context() -> Mock:
    ctx = Mock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.bot = AsyncMock()
    ctx.args: list[str] = []
    ctx.user_data: dict = {}
    ctx.chat_data: dict = {}
    ctx.bot_data: dict = {}
    return ctx


@pytest.mark.asyncio
async def test_echo_handler(update: Mock, context: Mock) -> None:
    await echo_handler(update, context)
    update.message.reply_text.assert_called_once_with("Hello")
```

### Using ExtBot for Testing

```python
from telegram.ext import ExtBot

bot = ExtBot(token="FAKE_TOKEN")
# ExtBot allows testing without a real token
```

### Checkpointing

Save and restore handler state between test runs using `DictPersistence`:

```python
from telegram.ext import ApplicationBuilder, DictPersistence

persistence = DictPersistence()
app = ApplicationBuilder().token("FAKE").persistence(persistence).build()
```

---

## 23. Common Bot Commands Menu

| API Method | Description |
|---|---|
| `getMe` | Get basic information about the bot |
| `getChat` | Get information about a chat |
| `getChatMember` | Get information about a member in a chat |
| `getChatMemberCount` | Get the number of members in a chat |
| `getUpdates` | Receive updates via long polling |
| `sendMessage` | Send a text message |
| `forwardMessage` | Forward a message from one chat to another |
| `copyMessage` | Copy a message without showing original sender |
| `sendPhoto` | Send a photo |
| `sendAudio` | Send an audio file |
| `sendDocument` | Send a general file |
| `sendVideo` | Send a video |
| `sendAnimation` | Send an animated GIF |
| `sendVoice` | Send a voice message |
| `sendVideoNote` | Send a round video note |
| `sendPaidMedia` | Send paid media with stars |
| `sendMediaGroup` | Send a group of photos/videos/documents (2–10) |
| `sendSticker` | Send a sticker |
| `sendPoll` | Send a poll |
| `sendDice` | Send an animated dice |
| `sendInvoice` | Send a payment invoice |
| `sendGame` | Send a game |
| `sendLocation` | Send a geographic location |
| `sendVenue` | Send a venue (location with title) |
| `sendContact` | Send a phone contact |
| `editMessageText` | Edit a text message |
| `editMessageCaption` | Edit a media caption |
| `editMessageMedia` | Edit the media in a message |
| `editMessageReplyMarkup` | Edit the reply markup |
| `deleteMessage` | Delete a message |
| `pinChatMessage` | Pin a message in a chat |
| `unpinChatMessage` | Unpin a message |
| `setWebhook` | Register a webhook URL |
| `deleteWebhook` | Remove the webhook |
| `getWebhookInfo` | Get current webhook status and error info |
| `banChatMember` | Ban a member from a chat |
| `unbanChatMember` | Unban a previously banned member |
| `restrictChatMember` | Restrict a member's permissions |
| `promoteChatMember` | Promote a member to admin |
| `setChatTitle` | Set the chat title |
| `setChatDescription` | Set the chat description |

---

## 24. Configuration & Environment Variables

### Environment Variables Pattern

```python
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://yourdomain.com/webhook")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
```

### `.env.example`

```bash
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook
DATABASE_URL=sqlite:///bot.db
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
```

---

## 25. Ephemeral Messages

### Callback Query Ephemeral Responses

```python
# Toast notification (only pressing user sees)
await query.answer(text="Processing...", show_alert=False)

# Popup alert (ephemeral — only pressing user sees)
await query.answer(text="Action completed!", show_alert=True)
```

### Limitations

- 15-second window for all responses to a callback query
- Ephemeral messages not guaranteed if user has certain privacy settings
- Not all message types support ephemeral delivery

---

## 26. Bot-to-Bot Communication

```python
# Send to another bot by username (both bots must be in same group)
await context.bot.send_message(chat_id="@analytics_bot", text=f"EVENT: {event}")
```

**Requirements:**
- Both bots must have privacy mode OFF
- Both bots must be added to the same group

---

## 27. Communities

Communities are groups of supergroups and channels managed together.

| Event | Handler |
|---|---|
| Bot added to community | `ChatMemberHandler` |
| Bot removed from community | `ChatMemberHandler` |

---

## 28. Callback Data Patterns

### Naming Convention

```
<category>:<action>[:<id>[:<extra>]]
```

| Pattern | Example | Use Case |
|---|---|---|
| `category:action` | `settings:toggle_dark` | Simple toggle |
| `category:action:id` | `order:confirm:456` | Confirm a specific order |
| `category:action:id:extra` | `item:edit:789:price` | Edit a sub-field |

### Regex Matching

```python
application.add_handler(
    CallbackQueryHandler(handle_order, pattern=r"^order:(confirm|cancel):\d+$")
)
```

---

## 29. Inline Mode Result Types

### `InlineQueryResultArticle`

| Parameter | Required | Description |
|---|---|---|
| `id` | ✅ | Unique identifier |
| `title` | ✅ | Result title |
| `input_message_content` | ✅ | Content sent when selected |
| `description` | ❌ | Short description (1-100 chars) |
| `thumb_url` | ❌ | Thumbnail URL (96×96) |
| `reply_markup` | ❌ | Inline keyboard |

### `answerInlineQuery` Parameters

| Parameter | Type | Description |
|---|---|---|
| `results` | `list[InlineQueryResult]` | List of results (max 50) |
| `cache_time` | `int` | Cache results for N seconds (default 300) |
| `is_personal` | `bool` | Results are per-user |
| `next_offset` | `str` | Offset for next page |
| `switch_pm_text` | `str` | Text for "Start" button if bot not started |
| `switch_pm_parameter` | `str` | Deep link parameter for PM button |

---

## 30. Error Handling Patterns

### Exception Types

| Exception | Description |
|---|---|
| `Forbidden` | User blocked the bot |
| `BadRequest` | Malformed request |
| `TimedOut` | Transient network issue |
| `NetworkError` | Broader network issue |
| `RetryAfter` | Rate limited (contains `retry_after` seconds) |
| `ChatMigrated` | Chat migrated to supergroup |
| `Conflict` | Conflict with another bot instance |

### Handling RetryAfter

```python
from telegram.error import RetryAfter

try:
    await context.bot.send_message(chat_id=chat_id, text="Hello")
except RetryAfter as e:
    await asyncio.sleep(e.retry_after)
    await context.bot.send_message(chat_id=chat_id, text="Hello")
```

---

*This reference document covers all functions, classes, methods, filters, handlers, keyboards, API methods, configuration options, security practices, deployment patterns, and testing patterns from the 22-chapter python-telegram-bot developer handbook.*
