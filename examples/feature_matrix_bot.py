#!/usr/bin/env python3
"""Feature Matrix Bot — comprehensive Telegram Bot API feature showcase.

This bot demonstrates virtually every feature of the Telegram Bot API
using python-telegram-bot v21.x, organized into a menu-driven interface.

Features covered:
    Messages: Markdown, HTML, emoji, dice, replies, edits, pins, reactions
    Media: photo, sticker, GIF, video, voice, document, audio
    Interactive: polls, quizzes, inline keyboards, reply keyboards, forum
    Location & Payments: location, contact, invoice (Stars), premium check
    Web & Inline: deep links, mini apps, inline mode help
    Bot Management: commands list, menu button

Usage:
    1. Set BOT_TOKEN environment variable
    2. Run: python feature_matrix_bot.py
    3. Send /start to see the main menu
"""

from __future__ import annotations

import logging
import os
import sys

from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    LabeledPrice,
    MenuButtonCommands,
    ReactionTypeEmoji,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SAMPLE_PHOTO_URL = (
    "https://python-telegram-bot.readthedocs.io/en/latest/_images/ptb_logo.png"
)
SAMPLE_AUDIO_URL = "https://www2.cs.uic.edu/~i101/SoundFiles/gettysburg10.wav"
SAMPLE_GIF_URL = "https://media.giphy.com/media/3o7abKhOpu0NwenHtO/giphy.gif"
SAMPLE_VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"


# ---------------------------------------------------------------------------
# Main menu & help
# ---------------------------------------------------------------------------

MAIN_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("Messages", callback_data="cat_messages"),
        InlineKeyboardButton("Media", callback_data="cat_media"),
    ],
    [
        InlineKeyboardButton("Interactive", callback_data="cat_interactive"),
        InlineKeyboardButton("Location & Payments", callback_data="cat_location"),
    ],
    [
        InlineKeyboardButton("Web & Inline", callback_data="cat_web"),
        InlineKeyboardButton("Bot Management", callback_data="cat_botmgmt"),
    ],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — show main menu."""
    if not update.message or not update.effective_user:
        return
    text = (
        f"Welcome {update.effective_user.first_name}! "
        "This bot showcases all Telegram Bot API features.\n"
        "Pick a category below:"
    )
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — show help text."""
    if not update.message:
        return
    await update.message.reply_text(
        "Feature Matrix Bot — Help\n\n"
        "Send /start to see the main menu.\n"
        "Each category contains a list of feature commands.\n\n"
        "Source: python-telegram-bot v21.x"
    )


# ---------------------------------------------------------------------------
# Category menus
# ---------------------------------------------------------------------------

CATEGORY_TEXTS: dict[str, str] = {
    "cat_messages": "Messages — text formatting, dice, replies, edits, pins",
    "cat_media": "Media — photos, stickers, GIFs, video, voice, documents",
    "cat_interactive": ("Interactive — polls, quizzes, keyboards, forum topics"),
    "cat_location": "Location & Payments — location, contact, invoices",
    "cat_web": "Web & Inline — deep links, mini apps, inline mode",
    "cat_botmgmt": "Bot Management — commands list, menu button",
}

CATEGORY_BUTTONS: dict[str, list[list[InlineKeyboardButton]]] = {
    "cat_messages": [
        [
            InlineKeyboardButton("/markdown", callback_data="feat_markdown"),
            InlineKeyboardButton("/html", callback_data="feat_html"),
        ],
        [
            InlineKeyboardButton("/emoji", callback_data="feat_emoji"),
            InlineKeyboardButton("/dice", callback_data="feat_dice"),
        ],
        [
            InlineKeyboardButton("/reply", callback_data="feat_reply"),
            InlineKeyboardButton("/edit", callback_data="feat_edit"),
        ],
        [
            InlineKeyboardButton("/pin", callback_data="feat_pin"),
            InlineKeyboardButton("/react", callback_data="feat_react"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
    "cat_media": [
        [
            InlineKeyboardButton("/photo", callback_data="feat_photo"),
            InlineKeyboardButton("/sticker_info", callback_data="feat_sticker_info"),
        ],
        [
            InlineKeyboardButton("/gif", callback_data="feat_gif"),
            InlineKeyboardButton("/video", callback_data="feat_video"),
        ],
        [
            InlineKeyboardButton("/voice", callback_data="feat_voice"),
            InlineKeyboardButton("/document", callback_data="feat_document"),
        ],
        [
            InlineKeyboardButton("/audio", callback_data="feat_audio"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
    "cat_interactive": [
        [
            InlineKeyboardButton("/poll", callback_data="feat_poll"),
            InlineKeyboardButton("/quiz", callback_data="feat_quiz"),
        ],
        [
            InlineKeyboardButton("/keyboard", callback_data="feat_keyboard"),
            InlineKeyboardButton(
                "/reply_keyboard", callback_data="feat_reply_keyboard"
            ),
        ],
        [
            InlineKeyboardButton(
                "/remove_keyboard", callback_data="feat_remove_keyboard"
            ),
            InlineKeyboardButton("/forum", callback_data="feat_forum"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
    "cat_location": [
        [
            InlineKeyboardButton("/location", callback_data="feat_location"),
            InlineKeyboardButton("/contact", callback_data="feat_contact"),
        ],
        [
            InlineKeyboardButton("/invoice", callback_data="feat_invoice"),
            InlineKeyboardButton("/check_premium", callback_data="feat_check_premium"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
    "cat_web": [
        [
            InlineKeyboardButton("/deeplink", callback_data="feat_deeplink"),
            InlineKeyboardButton("/miniapp", callback_data="feat_miniapp"),
        ],
        [
            InlineKeyboardButton("/inline_help", callback_data="feat_inline_help"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
    "cat_botmgmt": [
        [
            InlineKeyboardButton("/commands", callback_data="feat_commands"),
            InlineKeyboardButton("/menu", callback_data="feat_menu"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ],
}


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback queries for category navigation."""
    query = update.callback_query
    if not query or not query.data:
        return

    if query.data == "back_main":
        await query.edit_message_text(
            "Pick a category below:",
            reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD),
        )
        return

    if query.data in CATEGORY_TEXTS:
        text = CATEGORY_TEXTS[query.data]
        buttons = CATEGORY_BUTTONS.get(query.data, [])
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return

    if query.data.startswith("feat_"):
        handler = FEATURE_DISPATCH.get(query.data)
        if handler:
            await handler(query, context)
        else:
            await query.answer("Unknown feature.", show_alert=True)
        return

    await query.answer()


# ---------------------------------------------------------------------------
# Category 1 — Messages
# ---------------------------------------------------------------------------

FEAT_BOLD = "bold"
FEAT_ITALIC = "italic"
FEAT_CODE = "code"
FEAT_LINK = "link"


async def _handle_feature_callback(
    query: object, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Dispatch feature callbacks to the corresponding command handlers."""
    pass


async def feat_markdown(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send MarkdownV2 formatted text."""
    text = (
        "*Bold* \\| _Italic_ \\| ~Spoiler~\\*\n"
        "`monospace` \\| [link](https://python-telegram-bot\\.org)\n"
        "__underline__ \\| \\+\\+strikethrough\\+\\+\n"
        "\\*\\*Escape example\\*\\*"
    )
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        parse_mode="MarkdownV2",
    )


async def feat_html(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send HTML formatted text."""
    text = (
        "<b>Bold</b> | <i>Italic</i> | <u>Underline</u>\n"
        "<s>Strikethrough</s> | <span class='tg-spoiler'>"
        "Spoiler</span>\n"
        "<code>monospace</code> | "
        "<a href='https://python-telegram-bot.org'>link</a>"
    )
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        parse_mode="HTML",
    )


async def feat_emoji(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a custom emoji placeholder."""
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "Custom emoji example (replace CUSTOM_EMOJI_ID with a real "
            "custom emoji file_id from @sticker): "
            "Use <tg-emoji emoji-id='CUSTOM_EMOJI_ID'>🔔</tg-emoji> "
            "in HTML mode."
        ),
        parse_mode="HTML",
    )


async def feat_dice(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a dice animation."""
    await query.answer()
    await context.bot.send_dice(
        chat_id=query.message.chat_id,
        emoji="\U0001f3b2",
    )


async def feat_reply(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message replying to the original interaction message."""
    await query.answer()
    if query.message:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="This message is a reply to your interaction!",
            reply_to_message_id=query.message.message_id,
        )


async def feat_edit(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message then edit it."""
    await query.answer()
    msg = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="This message will be edited in 2 seconds...",
    )
    import asyncio

    await asyncio.sleep(2)
    await context.bot.edit_message_text(
        chat_id=msg.chat_id,
        message_id=msg.message_id,
        text="Message edited successfully!",
    )


async def feat_pin(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pin the last sent message."""
    await query.answer()
    msg = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="This message has been pinned!",
    )
    await context.bot.pin_chat_message(
        chat_id=query.message.chat_id,
        message_id=msg.message_id,
    )


async def feat_react(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a reaction to a message."""
    await query.answer()
    if query.message:
        await context.bot.set_message_reaction(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reaction=[ReactionTypeEmoji("\U0001f44d")],
        )


# ---------------------------------------------------------------------------
# Category 2 — Media
# ---------------------------------------------------------------------------


async def feat_photo(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a photo from a URL."""
    await query.answer()
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=SAMPLE_PHOTO_URL,
        caption="Photo sent from URL",
    )


async def feat_sticker_info(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send an informational message about sticker file_id usage."""
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "Sticker file_id usage:\n\n"
            "1. Send a sticker to @userinfobot or use "
            "/sticker command to get its file_id.\n"
            "2. Store the file_id in your database.\n"
            "3. Send it later with:\n"
            "   await bot.send_sticker(chat_id, sticker=file_id)\n\n"
            "file_id values are unique per sticker and do not expire."
        ),
    )


async def feat_gif(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a GIF from a URL."""
    await query.answer()
    await context.bot.send_animation(
        chat_id=query.message.chat_id,
        animation=SAMPLE_GIF_URL,
        caption="GIF sent from URL",
    )


async def feat_video(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a video from a URL."""
    await query.answer()
    await context.bot.send_video(
        chat_id=query.message.chat_id,
        video=SAMPLE_VIDEO_URL,
        caption="Video sent from URL",
    )


async def feat_voice(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a voice message."""
    await query.answer()
    await context.bot.send_voice(
        chat_id=query.message.chat_id,
        voice=SAMPLE_AUDIO_URL,
        caption="Voice message from URL",
    )


async def feat_document(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a document from a URL."""
    await query.answer()
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=SAMPLE_AUDIO_URL,
        caption="Document sent from URL",
    )


async def feat_audio(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send an audio file from a URL."""
    await query.answer()
    await context.bot.send_audio(
        chat_id=query.message.chat_id,
        audio=SAMPLE_AUDIO_URL,
        title="Sample Audio",
        caption="Audio sent from URL",
    )


# ---------------------------------------------------------------------------
# Category 3 — Interactive
# ---------------------------------------------------------------------------


async def feat_poll(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a poll."""
    await query.answer()
    await context.bot.send_poll(
        chat_id=query.message.chat_id,
        question="What is your favorite Python web framework?",
        options=["Django", "Flask", "FastAPI", "Starlette"],
        is_anonymous=False,
    )


async def feat_quiz(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a quiz with a correct answer."""
    await query.answer()
    await context.bot.send_poll(
        chat_id=query.message.chat_id,
        question="What does PEP stand for?",
        options=[
            "Python Enhancement Proposal",
            "Programming Error Prevention",
            "Package Environment Protocol",
            "Project Execution Plan",
        ],
        type="quiz",
        correct_option_id=0,
        explanation="PEP = Python Enhancement Proposal.",
    )


async def feat_keyboard(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show an inline keyboard with action buttons."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Visit GitHub",
                url="https://github.com/python-telegram-bot/python-telegram-bot",
            ),
            InlineKeyboardButton("Callback Demo", callback_data="back_main"),
        ],
        [
            InlineKeyboardButton("Switch to inline", switch_inline_query="help"),
        ],
    ]
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Inline keyboard demo — tap a button:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def feat_reply_keyboard(
    query: object, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show a reply keyboard."""
    keyboard = [
        [KeyboardButton("Share location", request_location=True)],
        [KeyboardButton("Share contact", request_contact=True)],
        [
            KeyboardButton(
                "Choose chat", request_chat=KeyboardButtonRequestChat(request_id=1)
            )
        ],
        [
            KeyboardButton(
                "Choose users", request_users=KeyboardButtonRequestUsers(request_id=2)
            )
        ],
    ]
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Reply keyboard — tap a button below:",
        reply_markup=keyboard,
    )


async def feat_remove_keyboard(
    query: object, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Remove the reply keyboard."""
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Reply keyboard removed.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def feat_forum(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a forum topic (works in groups with topics enabled)."""
    await query.answer("This only works in groups with topics.", show_alert=True)


# ---------------------------------------------------------------------------
# Category 4 — Location & Payments
# ---------------------------------------------------------------------------


async def feat_location(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a static location."""
    await query.answer()
    await context.bot.send_location(
        chat_id=query.message.chat_id,
        latitude=48.8566,
        longitude=2.3522,
    )


async def feat_contact(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a contact."""
    await query.answer()
    await context.bot.send_contact(
        chat_id=query.message.chat_id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
    )


async def feat_invoice(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a payment invoice (Telegram Stars)."""
    await query.answer()
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title="Premium Bot Access",
        description="Unlock premium features for 1 month",
        payload="premium_month_demo",
        currency="XTR",
        prices=[LabeledPrice("Premium Access", 100)],
    )


async def feat_check_premium(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if the user has Telegram Premium."""
    await query.answer()
    user = query.from_user
    is_premium = bool(user and user.is_premium)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"Telegram Premium: {'Yes' if is_premium else 'No'}",
    )


# ---------------------------------------------------------------------------
# Category 5 — Web & Inline
# ---------------------------------------------------------------------------


async def feat_deeplink(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show deep link information."""
    await query.answer()
    bot_username = context.bot.username
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "Deep links let users open your bot with parameters:\n\n"
            f"https://t.me/{bot_username}?start=param1\n\n"
            "Access parameters via context.args in /start handler.\n"
            "Useful for referral programs, shared content, etc."
        ),
    )


async def feat_miniapp(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show a Mini App (Web App) button."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Open Mini App",
                web_app={"url": "https://example.com/miniapp"},
            ),
        ],
    ]
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Telegram Mini App (Web App) button:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def feat_inline_help(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show inline mode usage instructions."""
    await query.answer()
    bot_username = context.bot.username
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            f"To use inline mode, type in any chat:\n\n"
            f"@{bot_username} <query>\n\n"
            "The bot will return results that can be "
            "inserted directly into the chat.\n\n"
            "Enable inline mode via @BotFather > Bot Settings "
            "> Inline Mode."
        ),
    )


# ---------------------------------------------------------------------------
# Category 6 — Bot Management
# ---------------------------------------------------------------------------

ALL_COMMANDS = [
    BotCommand("start", "Show main menu"),
    BotCommand("help", "Show help text"),
    BotCommand("markdown", "MarkdownV2 formatting demo"),
    BotCommand("html", "HTML formatting demo"),
    BotCommand("emoji", "Custom emoji demo"),
    BotCommand("dice", "Send dice animation"),
    BotCommand("reply", "Reply to message demo"),
    BotCommand("edit", "Edit message demo"),
    BotCommand("pin", "Pin message"),
    BotCommand("react", "Add reaction"),
    BotCommand("photo", "Send photo from URL"),
    BotCommand("sticker_info", "Sticker file_id info"),
    BotCommand("gif", "Send GIF from URL"),
    BotCommand("video", "Send video from URL"),
    BotCommand("voice", "Send voice message"),
    BotCommand("document", "Send document from URL"),
    BotCommand("audio", "Send audio from URL"),
    BotCommand("poll", "Create a poll"),
    BotCommand("quiz", "Create a quiz"),
    BotCommand("keyboard", "Show inline keyboard"),
    BotCommand("reply_keyboard", "Show reply keyboard"),
    BotCommand("remove_keyboard", "Remove reply keyboard"),
    BotCommand("forum", "Create forum topic"),
    BotCommand("location", "Send location"),
    BotCommand("contact", "Send contact"),
    BotCommand("invoice", "Send payment invoice"),
    BotCommand("check_premium", "Check Telegram Premium"),
    BotCommand("deeplink", "Deep link info"),
    BotCommand("miniapp", "Open Mini App"),
    BotCommand("inline_help", "Inline mode help"),
    BotCommand("commands", "List all commands"),
    BotCommand("menu", "Set menu button"),
]


async def feat_commands(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all bot commands."""
    await query.answer()
    lines = "\n".join(f"/{cmd.command} — {cmd.description}" for cmd in ALL_COMMANDS)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"All bot commands:\n\n{lines}",
    )


async def feat_menu(query: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the bot menu button."""
    await query.answer()
    await context.bot.set_chat_menu_button(
        chat_id=query.message.chat_id,
        menu_button=MenuButtonCommands(),
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Menu button set to show commands list.",
    )


# ---------------------------------------------------------------------------
# Callback dispatch table
# ---------------------------------------------------------------------------

FEATURE_DISPATCH: dict[str, object] = {
    "feat_markdown": feat_markdown,
    "feat_html": feat_html,
    "feat_emoji": feat_emoji,
    "feat_dice": feat_dice,
    "feat_reply": feat_reply,
    "feat_edit": feat_edit,
    "feat_pin": feat_pin,
    "feat_react": feat_react,
    "feat_photo": feat_photo,
    "feat_sticker_info": feat_sticker_info,
    "feat_gif": feat_gif,
    "feat_video": feat_video,
    "feat_voice": feat_voice,
    "feat_document": feat_document,
    "feat_audio": feat_audio,
    "feat_poll": feat_poll,
    "feat_quiz": feat_quiz,
    "feat_keyboard": feat_keyboard,
    "feat_reply_keyboard": feat_reply_keyboard,
    "feat_remove_keyboard": feat_remove_keyboard,
    "feat_forum": feat_forum,
    "feat_location": feat_location,
    "feat_contact": feat_contact,
    "feat_invoice": feat_invoice,
    "feat_check_premium": feat_check_premium,
    "feat_deeplink": feat_deeplink,
    "feat_miniapp": feat_miniapp,
    "feat_inline_help": feat_inline_help,
    "feat_commands": feat_commands,
    "feat_menu": feat_menu,
}


# ---------------------------------------------------------------------------
# Standalone command aliases (users can invoke directly)
# ---------------------------------------------------------------------------


async def cmd_markdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /markdown command."""
    if not update.message:
        return
    text = (
        "*Bold* \\| _Italic_ \\| ~Spoiler~\\*\n"
        "`monospace` \\| [link](https://python-telegram-bot\\.org)\n"
        "__underline__ \\| \\+\\+strikethrough\\+\\+"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")


async def cmd_html(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /html command."""
    if not update.message:
        return
    text = (
        "<b>Bold</b> | <i>Italic</i> | <u>Underline</u>\n"
        "<s>Strikethrough</s> | <span class='tg-spoiler'>"
        "Spoiler</span>\n"
        "<code>monospace</code> | "
        "<a href='https://python-telegram-bot.org'>link</a>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /emoji command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Custom emoji: replace CUSTOM_EMOJI_ID with a real ID.",
        parse_mode="HTML",
    )


async def cmd_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dice command."""
    if not update.message:
        return
    await update.message.reply_dice(emoji="\U0001f3b2")


async def cmd_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reply command."""
    if not update.message:
        return
    await update.message.reply_text("This is a reply!")


async def cmd_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /edit command."""
    if not update.message:
        return
    import asyncio

    msg = await update.message.reply_text("Editing in 2 seconds...")
    await asyncio.sleep(2)
    await msg.edit_text("Message edited successfully!")


async def cmd_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pin command."""
    if not update.message or not update.effective_chat:
        return
    msg = await update.message.reply_text("Pinned!")
    await context.bot.pin_chat_message(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
    )


async def cmd_react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /react command."""
    if not update.message or not update.effective_chat:
        return
    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji("\U0001f44d")],
    )


async def cmd_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /photo command."""
    if not update.message:
        return
    await update.message.reply_photo(
        photo=SAMPLE_PHOTO_URL,
        caption="Photo from URL",
    )


async def cmd_sticker_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sticker_info command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Sticker file_id usage:\n"
        "1. Send a sticker to @userinfobot to get file_id\n"
        "2. Store it in your database\n"
        "3. Use bot.send_sticker(chat_id, sticker=file_id)"
    )


async def cmd_gif(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /gif command."""
    if not update.message:
        return
    await update.message.reply_animation(
        animation=SAMPLE_GIF_URL,
        caption="GIF from URL",
    )


async def cmd_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /video command."""
    if not update.message:
        return
    await update.message.reply_video(
        video=SAMPLE_VIDEO_URL,
        caption="Video from URL",
    )


async def cmd_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /voice command."""
    if not update.message:
        return
    await update.message.reply_voice(
        voice=SAMPLE_AUDIO_URL,
        caption="Voice message",
    )


async def cmd_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /document command."""
    if not update.message:
        return
    await update.message.reply_document(
        document=SAMPLE_AUDIO_URL,
        caption="Document from URL",
    )


async def cmd_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /audio command."""
    if not update.message:
        return
    await update.message.reply_audio(
        audio=SAMPLE_AUDIO_URL,
        title="Sample Audio",
        caption="Audio from URL",
    )


async def cmd_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /poll command."""
    if not update.message:
        return
    await update.message.reply_text("Sending poll...")
    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question="Favorite Python web framework?",
        options=["Django", "Flask", "FastAPI", "Starlette"],
        is_anonymous=False,
    )


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /quiz command."""
    if not update.message:
        return
    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question="What does PEP stand for?",
        options=[
            "Python Enhancement Proposal",
            "Programming Error Prevention",
            "Package Environment Protocol",
            "Project Execution Plan",
        ],
        type="quiz",
        correct_option_id=0,
        explanation="PEP = Python Enhancement Proposal.",
    )


async def cmd_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /keyboard command."""
    if not update.message:
        return
    keyboard = [
        [
            InlineKeyboardButton(
                "GitHub",
                url="https://github.com/python-telegram-bot/python-telegram-bot",
            ),
            InlineKeyboardButton("Demo", callback_data="back_main"),
        ],
    ]
    await update.message.reply_text(
        "Inline keyboard:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_reply_keyboard(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /reply_keyboard command."""
    if not update.message:
        return
    keyboard = [
        [KeyboardButton("Share location", request_location=True)],
        [KeyboardButton("Share contact", request_contact=True)],
    ]
    await update.message.reply_text(
        "Reply keyboard:",
        reply_markup=keyboard,
    )


async def cmd_remove_keyboard(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /remove_keyboard command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Keyboard removed.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def cmd_forum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /forum command."""
    if not update.message:
        return
    await update.message.reply_text(
        "Forum topics only work in groups with topics enabled."
    )


async def cmd_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /location command."""
    if not update.message:
        return
    await update.message.reply_location(
        latitude=48.8566,
        longitude=2.3522,
    )


async def cmd_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /contact command."""
    if not update.message:
        return
    await update.message.reply_contact(
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
    )


async def cmd_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /invoice command."""
    if not update.message:
        return
    await update.message.reply_invoice(
        title="Premium Bot Access",
        description="Unlock premium features for 1 month",
        payload="premium_month_demo",
        currency="XTR",
        prices=[LabeledPrice("Premium Access", 100)],
    )


async def cmd_check_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /check_premium command."""
    if not update.message or not update.effective_user:
        return
    is_premium = bool(update.effective_user.is_premium)
    await update.message.reply_text(
        f"Telegram Premium: {'Yes' if is_premium else 'No'}"
    )


async def cmd_deeplink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /deeplink command."""
    if not update.message:
        return
    bot_username = context.bot.username
    await update.message.reply_text(
        f"Deep links:\n"
        f"https://t.me/{bot_username}?start=param1\n\n"
        "Access via context.args in /start."
    )


async def cmd_miniapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /miniapp command."""
    if not update.message:
        return
    keyboard = [
        [
            InlineKeyboardButton(
                "Open Mini App",
                web_app={"url": "https://example.com/miniapp"},
            ),
        ],
    ]
    await update.message.reply_text(
        "Mini App button:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_inline_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /inline_help command."""
    if not update.message:
        return
    bot_username = context.bot.username
    await update.message.reply_text(
        f"Type @{bot_username} <query> in any chat to use inline mode."
    )


async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /commands command."""
    if not update.message:
        return
    lines = "\n".join(f"/{c.command} — {c.description}" for c in ALL_COMMANDS)
    await update.message.reply_text(f"Commands:\n\n{lines}")


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command."""
    if not update.message or not update.effective_chat:
        return
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonCommands(),
    )
    await update.message.reply_text("Menu button set.")


# ---------------------------------------------------------------------------
# Pre-checkout & successful payment
# ---------------------------------------------------------------------------


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout query."""
    query = update.pre_checkout_query
    if not query:
        return
    await query.answer(ok=True)


async def successful_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle successful payment."""
    if not update.message or not update.message.successful_payment:
        return
    payment = update.message.successful_payment
    await update.message.reply_text(f"Payment received: {payment.total_amount} Stars")


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    # Navigation & general
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(category_callback))

    # Category 1 — Messages
    application.add_handler(CommandHandler("markdown", cmd_markdown))
    application.add_handler(CommandHandler("html", cmd_html))
    application.add_handler(CommandHandler("emoji", cmd_emoji))
    application.add_handler(CommandHandler("dice", cmd_dice))
    application.add_handler(CommandHandler("reply", cmd_reply))
    application.add_handler(CommandHandler("edit", cmd_edit))
    application.add_handler(CommandHandler("pin", cmd_pin))
    application.add_handler(CommandHandler("react", cmd_react))

    # Category 2 — Media
    application.add_handler(CommandHandler("photo", cmd_photo))
    application.add_handler(CommandHandler("sticker_info", cmd_sticker_info))
    application.add_handler(CommandHandler("gif", cmd_gif))
    application.add_handler(CommandHandler("video", cmd_video))
    application.add_handler(CommandHandler("voice", cmd_voice))
    application.add_handler(CommandHandler("document", cmd_document))
    application.add_handler(CommandHandler("audio", cmd_audio))

    # Category 3 — Interactive
    application.add_handler(CommandHandler("poll", cmd_poll))
    application.add_handler(CommandHandler("quiz", cmd_quiz))
    application.add_handler(CommandHandler("keyboard", cmd_keyboard))
    application.add_handler(CommandHandler("reply_keyboard", cmd_reply_keyboard))
    application.add_handler(CommandHandler("remove_keyboard", cmd_remove_keyboard))
    application.add_handler(CommandHandler("forum", cmd_forum))

    # Category 4 — Location & Payments
    application.add_handler(CommandHandler("location", cmd_location))
    application.add_handler(CommandHandler("contact", cmd_contact))
    application.add_handler(CommandHandler("invoice", cmd_invoice))
    application.add_handler(CommandHandler("check_premium", cmd_check_premium))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )

    # Category 5 — Web & Inline
    application.add_handler(CommandHandler("deeplink", cmd_deeplink))
    application.add_handler(CommandHandler("miniapp", cmd_miniapp))
    application.add_handler(CommandHandler("inline_help", cmd_inline_help))

    # Category 6 — Bot Management
    application.add_handler(CommandHandler("commands", cmd_commands))
    application.add_handler(CommandHandler("menu", cmd_menu))

    # Error handler
    application.add_error_handler(error_handler)

    logger.info("Feature Matrix Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
