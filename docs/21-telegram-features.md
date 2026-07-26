# Chapter 21: Complete Telegram Bot Features Reference

> **Every feature Telegram offers, with python-telegram-bot code examples.**

This chapter covers **every feature** available to Telegram bots, organized by category. Each feature includes a working code snippet using `python-telegram-bot` v20+/v21.x.

---

## Table of Contents

1. [Messages](#1-messages)
2. [Media](#2-media)
3. [Interactive](#3-interactive)
4. [Location & Payments](#4-location--payments)
5. [Mini Apps & Web](#5-mini-apps--web)
6. [Inline Mode](#6-inline-mode)
7. [Bot Management](#7-bot-management)
8. [Premium & Boosts](#8-premium--boosts)
9. [Business](#9-business)

---

## 1. Messages

### MarkdownV2 Formatting

```python
async def markdown_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        r"\*Bold\* _Italic_ ~Strikethrough~ "
        r"\|\|Spoiler\|\| `code` \[link\]\(https://example\.com\)"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")
```

### HTML Formatting

```python
async def html_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "<b>Bold</b> <i>Italic</i> <u>Underline</u> "
        "<s>Strikethrough</s> <tg-spoiler>Spoiler</tg-spoiler> "
        "<code>code</code> <a href='https://example.com'>link</a>"
    )
    await update.message.reply_text(text, parse_mode="HTML")
```

### Custom Emoji

```python
async def custom_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Custom emoji from premium sticker sets
    # Get emoji_id by forwarding emoji to @RawDataBot
    emoji_id = "5368324170671202286"
    text = f"Hello <tg-emoji emoji-id='{emoji_id}'>🎉</tg-emoji> World!"
    await update.message.reply_text(text, parse_mode="HTML")
```

### Animated Emoji (Dice)

```python
async def animated_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Send dice animations
    await update.message.reply_dice(emoji="🎲")  # 🎲 🎯 🎤 🏀 ⚽ 🎳
```

### Reply & Forward

```python
async def reply_forward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        # Reply to specific message
        await update.message.reply_text(
            "This is a reply!",
            reply_to_message_id=update.message.message_id,
        )

        # Forward message
        await update.message.forward(chat_id=TARGET_CHAT_ID)
```

### Edit Message

```python
async def edit_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Loading...")
    # Edit text
    await msg.edit_text("Done!")
    # Edit reply markup
    await msg.edit_reply_markup(reply_markup=new_markup)
```

### Delete Message

```python
async def delete_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.delete()
```

### Pin/Unpin Message

```python
async def pin_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.pin()
        # await update.message.unpin()
```

### Message Reactions

```python
async def reaction_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        from telegram import ReactionTypeEmoji
        reactions = [ReactionTypeEmoji("👍"), ReactionTypeEmoji("❤️")]
        await update.message.set_reactions(reactions)
```

---

## 2. Media

### Photo

```python
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # From URL
    await update.message.reply_photo(
        photo="https://example.com/photo.jpg",
        caption="Photo from URL",
    )
    # From file
    with open("photo.jpg", "rb") as f:
        await update.message.reply_photo(photo=f, caption="Local photo")
```

### Sticker

```python
async def send_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_sticker(
        sticker="CAACAgIAAxkBAA..."  # file_id
    )

async def sticker_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.sticker:
        s = update.message.sticker
        await update.message.reply_text(
            f"Emoji: {s.emoji}\nSet: {s.set_name}\nType: {s.type}"
        )
```

### Sticker Sets

```python
async def get_sticker_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return
    set_name = context.args[0]
    try:
        sticker_set = await context.bot.get_sticker_set(set_name)
        await update.message.reply_text(
            f"Set: {sticker_set.title}\n"
            f"Stickers: {len(sticker_set.stickers)}"
        )
    except Exception:
        await update.message.reply_text("Sticker set not found.")
```

### GIF / Animation

```python
async def send_gif(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_animation(
        animation="https://example.com/animation.gif",
        caption="Animated GIF",
    )
```

### Video

```python
async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_video(
        video="https://example.com/video.mp4",
        caption="Video message",
        supports_streaming=True,
    )
```

### Video Note (Circle Video)

```python
async def send_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_video_note(
        video_note="CAACAgIAAxkBAA..."  # file_id
    )
```

### Voice Message

```python
async def send_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_voice(
        voice="https://example.com/voice.ogg",
        caption="Voice message",
    )
```

### Document / File

```python
async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_document(
        document="https://example.com/file.pdf",
        caption="PDF document",
    )
```

### Audio

```python
async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_audio(
        audio="https://example.com/song.mp3",
        title="Song Title",
        performer="Artist",
    )
```

---

## 3. Interactive

### Poll

```python
async def send_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_poll(
        question="What is 2 + 2?",
        options=["3", "4", "5", "6"],
        is_anonymous=True,
        type="quiz",
        correct_option_id=1,
    )
```

### Quiz

```python
async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_poll(
        question="Capital of France?",
        options=["London", "Berlin", "Paris", "Madrid"],
        type="quiz",
        correct_option_id=2,
        explanation="Paris is the capital of France.",
    )
```

### Game

```python
# Game must be set up via @BotFather first
async def send_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_game(chat_id=update.effective_chat.id, game_short_name="my_game")

async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(url="https://example.com/game")  # Open game URL
```

### Inline Keyboard

```python
async def inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="opt1"),
         InlineKeyboardButton("Option 2", callback_data="opt2")],
        [InlineKeyboardButton("URL Button", url="https://example.com")],
    ]
    await update.message.reply_text(
        "Choose:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

### Reply Keyboard

```python
async def reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = [
        [KeyboardButton("Share Location", request_location=True)],
        [KeyboardButton("Share Contact", request_contact=True)],
        ["Button 1", "Button 2"],
    ]
    await update.message.reply_text(
        "Choose:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
```

### Remove Keyboard

```python
async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Keyboard removed!", reply_markup=ReplyKeyboardRemove())
```

### Forum Topics

```python
async def create_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat:
        await context.bot.create_forum_topic(
            chat_id=update.message.chat.id,
            name="New Topic",
        )

async def send_to_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            message_thread_id=1,  # Topic ID
            text="Message in topic",
        )
```

### Story (Premium Only)

```python
# Stories are premium-only and cannot be sent via Bot API
# Bots can only receive story reactions
```

---

## 4. Location & Payments

### Location

```python
async def send_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Simple location
    await update.message.reply_location(latitude=40.7128, longitude=-74.0060)

    # Live location
    await update.message.reply_live_location(
        latitude=40.7128,
        longitude=-74.0060,
        live_period=300,  # 5 minutes
    )
```

### Contact

```python
async def send_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_contact(
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
    )
```

### Venue

```python
async def send_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_venue(
        latitude=40.7128,
        longitude=-74.0060,
        title="Central Park",
        address="New York, NY",
    )
```

### Payments (Telegram Stars)

```python
async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import LabeledPrice

    await update.message.reply_invoice(
        title="Premium Subscription",
        description="1 month of premium features",
        payload="premium_month",
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice("Premium", 100)],
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.successful_payment:
        payment = update.message.successful_payment
        await update.message.reply_text(f"Payment of {payment.total_amount} Stars received!")
```

---

## 5. Mini Apps & Web

### Mini Apps (TWA)

```python
async def send_mini_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Open App", web_app={"url": "https://example.com/app"})
    ]])
    await update.message.reply_text("Open the Mini App:", reply_markup=keyboard)

# Handle web app data
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.web_app_data:
        data = update.message.web_app_data.data
        await update.message.reply_text(f"Received: {data}")
```

### Webhook Setup

```python
from aiohttp import web

async def webhook_handler(request: web.Request) -> web.Response:
    application = request.app["bot_application"]
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return web.Response()

def setup_webhook(application, webhook_url: str) -> None:
    app = web.Application()
    app["bot_application"] = application
    app.router.add_post("/webhook", webhook_handler)
```

### Deep Linking

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        payload = context.args[0]
        await update.message.reply_text(f"Deep link payload: {payload}")
    else:
        await update.message.reply_text("Welcome!")

# Usage: https://t.me/yourbot?start=abc123
```

### Web Apps (via Keyboard)

```python
async def web_app_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = ReplyKeyboardMarkup([[
        KeyboardButton("Open Web App", web_app={"url": "https://example.com"})
    ]])
    await update.message.reply_text("Tap to open:", reply_markup=keyboard)
```

---

## 6. Inline Mode

### Basic Inline Query

```python
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineQueryResultArticle, InputTextMessageContent

    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id="1",
            title=f"Result for: {query}",
            input_message_content=InputTextMessageContent(f"You searched: {query}"),
        )
    ]
    await update.inline_query.answer(results, cache_time=300)
```

### Inline Results with Thumbnails

```python
async def inline_with_thumb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram import InlineQueryResultPhoto

    results = [
        InlineQueryResultPhoto(
            id="1",
            photo_url="https://example.com/photo.jpg",
            thumbnail_url="https://example.com/thumb.jpg",
            title="Photo Result",
            description="A beautiful photo",
        )
    ]
    await update.inline_query.answer(results)
```

---

## 7. Bot Management

### Bot Commands

```python
async def set_commands(application) -> None:
    from telegram import BotCommand

    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
        BotCommand("settings", "Open settings"),
    ]
    await application.bot.set_my_commands(commands)
```

### Menu Button

```python
async def set_menu_button(application) -> None:
    from telegram import MenuButtonCommands
    await application.bot.set_chat_menu_button(
        chat_id=USER_ID,
        menu_button=MenuButtonCommands(),
    )
```

### Chat Join Request

```python
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.chat_join_request:
        # Auto-approve
        await context.bot.approve_chat_join_request(
            chat_id=update.chat_join_request.chat.id,
            user_id=update.chat_join_request.from_user.id,
        )
```

### Chat Boost

```python
async def handle_boost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat_boost:
        boost = update.message.chat_boost
        await update.message.reply_text(
            f"Chat boosted! Boost count: {boost.boost.count}"
        )
```

### Background & Themes

```python
# Background and theme changes are client-side only
# Bots cannot modify user backgrounds/themes
# But bots can receive updates about theme changes in groups
```

---

## 8. Premium & Boosts

### Premium Features

```python
async def check_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user and user.is_premium:
        await update.message.reply_text("You are a Telegram Premium user!")
    else:
        await update.message.reply_text("Upgrade to Premium for extra features!")
```

### Custom Emoji (Premium)

```python
async def premium_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Premium users can use custom emoji in messages
    text = "Hello <tg-emoji emoji-id='5368324170671202286'>🎉</tg-emoji>"
    await update.message.reply_text(text, parse_mode="HTML")
```

---

## 9. Business

### Business Connection

```python
async def business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.business_message:
        biz = update.business_message
        await biz.reply_text(
            "Thank you for your business message!",
            chat_id=biz.chat.id,
        )
```

### Business Bot Features

```python
# Bots can:
# 1. Receive messages from business chats
# 2. Send replies in business conversations
# 3. Access business connection info
# 4. Handle business-specific updates

async def handle_business(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.business_connection:
        conn = update.business_connection
        await context.bot.send_message(
            chat_id=conn.user_chat_id,
            text="Business message received!",
        )
```

---

## Feature Matrix

| Category | Feature | PTB Method | Bot API Version |
|----------|---------|------------|-----------------|
| **Messages** | MarkdownV2 | `reply_text(parse_mode="MarkdownV2")` | All |
| | HTML | `reply_text(parse_mode="HTML")` | All |
| | Custom Emoji | `<tg-emoji emoji-id='...'>` | 5.0+ |
| | Animated Emoji | `reply_dice(emoji="🎲")` | 5.0+ |
| | Reply | `reply_to_message_id=` | All |
| | Forward | `message.forward()` | All |
| | Edit | `message.edit_text()` | All |
| | Delete | `message.delete()` | All |
| | Pin | `message.pin()` | All |
| | Reactions | `message.set_reactions()` | 5.0+ |
| **Media** | Photo | `reply_photo()` | All |
| | Sticker | `reply_sticker()` | All |
| | Sticker Set | `get_sticker_set()` | All |
| | GIF/Animation | `reply_animation()` | All |
| | Video | `reply_video()` | All |
| | Video Note | `reply_video_note()` | All |
| | Voice | `reply_voice()` | All |
| | Document | `reply_document()` | All |
| | Audio | `reply_audio()` | All |
| **Interactive** | Poll | `reply_poll(type="poll")` | All |
| | Quiz | `reply_poll(type="quiz")` | All |
| | Game | `send_game()` | All |
| | Inline Keyboard | `InlineKeyboardMarkup` | All |
| | Reply Keyboard | `ReplyKeyboardMarkup` | All |
| | Forum Topics | `create_forum_topic()` | 5.0+ |
| **Location** | Location | `reply_location()` | All |
| | Live Location | `reply_live_location()` | All |
| | Contact | `reply_contact()` | All |
| | Venue | `reply_venue()` | All |
| **Payments** | Invoice | `reply_invoice()` | All |
| | Pre-Checkout | `PreCheckoutQueryHandler` | All |
| | Stars | `currency="XTR"` | 5.0+ |
| **Web** | Mini Apps | `web_app={"url": "..."}` | 5.0+ |
| | Webhook | `webhook_handler()` | All |
| | Deep Linking | `context.args[0]` | All |
| **Inline** | Inline Query | `InlineQueryHandler` | All |
| | Inline Results | `InlineQueryResult*` | All |
| **Bot Mgmt** | Commands | `set_my_commands()` | All |
| | Menu Button | `set_chat_menu_button()` | 5.0+ |
| | Join Request | `approve_chat_join_request()` | 5.0+ |
| | Chat Boost | `chat_boost` update | 5.0+ |
| **Business** | Business Msg | `business_message` update | 5.0+ |
| | Business Conn | `business_connection` update | 5.0+ |

---

## See Also

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Chapter 04: Handlers](./04-handlers.md)
- [Chapter 06: Keyboards](./06-keyboards.md)
- [Chapter 08: Media](./08-media.md)
- [Chapter 10: Inline Mode](./10-inline-mode.md)
- [Chapter 12: Payments](./12-payments.md)
- [Chapter 13: Mini Apps](./13-mini-apps.md)
- [Chapter 14: Groups & Channels](./14-groups-channels.md)
