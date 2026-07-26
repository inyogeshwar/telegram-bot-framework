# Appendix

Quick-reference tables, formatting guides, and external resources for the
`python-telegram-bot` developer handbook.

---

## A. Bot API Methods

Essential methods from the Telegram Bot API. Full documentation:
<https://core.telegram.org/bots/api#available-methods>

### Getting Information

| Method | Description |
|--------|-------------|
| `getMe` | Get basic information about the bot |
| `getChat` | Get information about a chat |
| `getChatMember` | Get information about a member in a chat |
| `getChatMemberCount` | Get the number of members in a chat |
| `getUpdates` | Receive updates via long polling |

### Sending Messages

| Method | Description |
|--------|-------------|
| `sendMessage` | Send a text message |
| `forwardMessage` | Forward a message from one chat to another |
| `copyMessage` | Copy a message without showing the original sender |
| `reply_text` | Reply to a message (convenience method on Message object) |

### Sending Media

| Method | Description |
|--------|-------------|
| `sendPhoto` | Send a photo |
| `sendAudio` | Send an audio file |
| `sendDocument` | Send a general file |
| `sendVideo` | Send a video |
| `sendAnimation` | Send an animated GIF |
| `sendVoice` | Send a voice message (.ogg / .mp3) |
| `sendVideoNote` | Send a round video note |
| `sendPaidMedia` | Send paid media with stars |
| `sendMediaGroup` | Send a group of photos/videos/documents (2–10) |
| `sendSticker` | Send a sticker |

### Interactive Elements

| Method | Description |
|--------|-------------|
| `sendPoll` | Send a poll |
| `sendDice` | Send an animated dice |
| `sendPoll` (quiz) | Send a quiz (use `sendPoll` with `quiz=True`) |
| `sendInvoice` | Send a payment invoice |
| `sendGame` | Send a game |
| `sendLocation` | Send a geographic location |
| `sendVenue` | Send a venue (location with title) |
| `sendContact` | Send a phone contact |

### Editing & Managing Messages

| Method | Description |
|--------|-------------|
| `editMessageText` | Edit a text message |
| `editMessageCaption` | Edit a media caption |
| `editMessageMedia` | Edit the media in a message |
| `editMessageReplyMarkup` | Edit the reply markup |
| `deleteMessage` | Delete a message |
| `pinChatMessage` | Pin a message in a chat |
| `unpinChatMessage` | Unpin a message |

### Webhook Management

| Method | Description |
|--------|-------------|
| `setWebhook` | Register a webhook URL |
| `deleteWebhook` | Remove the webhook |
| `getWebhookInfo` | Get current webhook status and error info |

### Chat Administration

| Method | Description |
|--------|-------------|
| `kickChatMember` | Kick (ban) a member *(deprecated; use `banChatMember`)* |
| `banChatMember` | Ban a member from a chat |
| `unbanChatMember` | Unban a previously banned member |
| `restrictChatMember` | Restrict a member's permissions |
| `promoteChatMember` | Promote a member to admin |
| `setChatTitle` | Set the chat title |
| `setChatDescription` | Set the chat description |

---

## B. Common Filters

Quick reference for `telegram.ext.filters`. Full list:
<https://docs.python-telegram-bot.org/en/stable/handlers.html#module-telegram.ext.filters>

### Message Content Filters

| Filter | Matches |
|--------|---------|
| `filters.TEXT` | Text messages (non-command) |
| `filters.COMMAND` | Messages starting with `/` |
| `filters.PHOTO` | Messages containing a photo |
| `filters.VIDEO` | Messages containing a video |
| `filters.AUDIO` | Messages containing audio |
| `filters.VOICE` | Messages containing a voice note |
| `filters.VIDEO_NOTE` | Messages containing a video note |
| `filters.Document.ALL` | Messages containing any document |
| `filters.Document.PDF` | Messages containing a PDF document |
| `filters.Document.IMAGE` | Messages containing an image file |
| `filters.Sticker.ALL` | Messages containing any sticker |
| `filters.Sticker.REGULAR` | Regular (static/animated) stickers |
| `filters.Sticker.VIDEO` | Video stickers |
| `filters.ANIMATION` | Messages containing a GIF |
| `filters.LOCATION` | Messages containing a location |
| `filters.VENUE` | Messages containing a venue |
| `filters.CONTACT` | Messages containing a contact |
| `filters.INVOICE` | Messages containing an invoice |
| `filters.GAME` | Messages containing a game |
| `filters.POLL` | Messages containing a poll |
| `filters.DICE` | Messages containing a dice |
| `filters.StatusUpdate.NEW_CHAT_MEMBERS` | New chat member joined |
| `filters.StatusUpdate.LEFT_CHAT_MEMBER` | Member left the chat |
| `filters.StatusUpdate.NEW_CHAT_TITLE` | Chat title changed |
| `filters.StatusUpdate.NEW_CHAT_PHOTO` | Chat photo changed |

### Logical Combinators

| Operator | Meaning |
|----------|---------|
| `filters.TEXT & filters.ChatType.PRIVATE` | Both conditions true (AND) |
| `filters.TEXT \| filters.PHOTO` | Either condition true (OR) |
| `~filters.COMMAND` | Negation (NOT) |

### Regex & Entity Filters

| Filter | Matches |
|--------|---------|
| `filters.Regex(r"^/status$")` | Text matching the regex |
| `filters.Entity("url")` | Messages containing a URL entity |
| `filters.Entity("mention")` | Messages containing a @mention |
| `filters.Entity("bot_command")` | Messages containing a bot command entity |
| `filters.HasAttachment()` | Messages with any file attachment |

### Chat Type Filters

| Filter | Matches |
|--------|---------|
| `filters.ChatType.PRIVATE` | Private (1:1) chats |
| `filters.ChatType.GROUP` | Basic groups |
| `filters.ChatType.SUPERGROUP` | Supergroups |
| `filters.ChatType.CHANNEL` | Channels |

### User & Chat Filters

| Filter | Matches |
|--------|---------|
| `filters.User(user_id=123)` | Messages from a specific user ID |
| `filters.User(username="alice")` | Messages from a specific username |
| `filters.Chat(chat_id=-100123)` | Messages in a specific chat |
| `filters.ChatType.GROUP \| filters.ChatType.SUPERGROUP` | Any group chat |

---

## C. Callback Data Patterns

Recommended conventions for `callback_data` in `InlineKeyboardButton` and
`CallbackQueryHandler`.

### Naming Convention

Use colon-separated segments with a **category** prefix:

```
<category>:<action>[:<id>[:<extra>]]
```

| Pattern | Example | Use Case |
|---------|---------|----------|
| `category:action` | `settings:toggle_dark` | Simple toggle |
| `category:action:id` | `order:confirm:456` | Confirm a specific order |
| `category:action:id:extra` | `item:edit:789:price` | Edit a sub-field |

### Regex Matching

```python
from telegram.ext import CallbackQueryHandler

application.add_handler(
    CallbackQueryHandler(
        handle_order,
        pattern=r"^order:(confirm|cancel):\d+$",
    )
)
```

### Extracting Data

```python
async def handle_order(update, context):
    query = update.callback_query
    parts = query.data.split(":")
    action = parts[1]
    order_id = int(parts[2])

    await query.answer()
    # ...
```

### Limitations

| Constraint | Value |
|------------|-------|
| Max `callback_data` length | 64 bytes |
| Encoding | UTF-8 |
| Storage | Sent with every update; no server-side persistence |

Keep callback data compact. Store detail in `context.user_data` or your database
instead.

---

## D. Message Formatting

Telegram supports two parse modes: **MarkdownV2** and **HTML**.

### MarkdownV2 Syntax

```
*bold \*text*
_italic \*text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
![👍](tg://emoji?id=5368324170671202286)
`inline fixed-width code`
```pre-formatted fixed-width code block
```python
pre-formatted fixed-width code block written in the Python programming language
```
```

### HTML Syntax

```html
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough
<span class="tg-spoiler">italic bold strikethrough spoiler</span></s>
<u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block
written in the Python programming language</code></pre>
```

### Escaping Helpers

```python
from telegram.helpers import escape_markdown


# Escape user text for MarkdownV2
safe_text = escape_markdown(user_input, version=2)
await update.message.reply_text(f"*{safe_text}*", parse_mode="MarkdownV2")
```

For HTML, use `html.escape()` from the standard library:

```python
import html

safe_text = html.escape(user_input)
await update.message.reply_text(
    f"<b>{safe_text}</b>",
    parse_mode="HTML",
)
```

### Parse Mode Comparison

| Feature | MarkdownV2 | HTML |
|---------|------------|------|
| Bold | `*text*` | `<b>text</b>` |
| Italic | `_text_` | `<i>text</i>` |
| Underline | `__text__` | `<u>text</u>` |
| Strikethrough | `~text~` | `<s>text</s>` |
| Spoiler | `\|\|text\|\|` | `<tg-spoiler>text</tg-spoiler>` |
| Inline code | `` `code` `` | `<code>code</code>` |
| Code block | ```` ``` ```` | `<pre>code</pre>` |
| Link | `[text](url)` | `<a href="url">text</a>` |
| Mention | `[name](tg://user?id=)` | `<a href="tg://user?id=">name</a>` |

---

## E. Version History

### python-telegram-bot Library

| Version | Highlights |
|---------|------------|
| **v20.0** | Async/await throughout; dropped Python 3.7; `ApplicationBuilder` replaces `Updater`; new persistence API |
| **v20.3** | Job queue stability fixes; improved `ConversationHandler` timeout handling |
| **v20.7** | Bug fixes; improved webhook reliability; better error messages |
| **v20.8** | Type annotation improvements; deprecated legacy callback patterns |
| **v21.0** | Latest stable release; performance improvements; expanded filter combinators |

### Telegram Bot API

| Version | Features |
|---------|----------|
| **v10.0** | Guest mode for channels; live photos; bot-to-bot communication |
| **v10.1** | Rich message formatting improvements; `sendPaidMedia`; join request queries |
| **v10.2** | Ephemeral messages; communities support; `copyMessage` improvements |
| **v9.x** | Business accounts; business connections; chat theme customisation |
| **v8.x** | Reaction support; `readBusinessMessage`; business intro/sticker |

> Always check the
> [Bot API changelog](https://core.telegram.org/bots/api#recent-changes)
> for the latest additions.

---

## F. External Resources

| Resource | URL |
|----------|-----|
| Telegram Bot API reference | <https://core.telegram.org/bots/api> |
| Bot API tutorials | <https://core.telegram.org/bots/tutorials> |
| python-telegram-bot docs | <https://docs.python-telegram-bot.org> |
| python-telegram-bot GitHub | <https://github.com/python-telegram-bot/python-telegram-bot> |
| Bot support Telegram group | [@PyTelegramBotAPI](https://t.me/PyTelegramBotAPI) |
| BotFather | [@BotFather](https://t.me/BotFather) |
| BotSupport (official) | [@BotSupport](https://t.me/BotSupport) |

---

## G. Project Layout Template

Suggested directory structure for a production `python-telegram-bot` project:

```
mybot/
├── bot.py                  # Application entry point
├── config.py               # Configuration / env loading
├── requirements.txt        # Pinned dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Local dev / deploy
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start handler
│   ├── help.py             # /help handler
│   ├── user.py             # User-facing handlers
│   ├── admin.py            # Admin-only handlers
│   └── callbacks.py        # Inline callback handlers
├── middlewares/
│   ├── __init__.py
│   └── logging.py          # Update logging middleware
├── persistence/
│   ├── __init__.py
│   └── database.py         # Database connection & models
├── utils/
│   ├── __init__.py
│   ├── formatting.py       # Message formatting helpers
│   └── validators.py       # Input validation
└── tests/
    ├── conftest.py         # Shared pytest fixtures
    ├── unit/
    │   ├── test_start.py
    │   └── test_user.py
    ├── integration/
    │   └── test_handlers.py
    └── e2e/
        └── test_live.py
```
