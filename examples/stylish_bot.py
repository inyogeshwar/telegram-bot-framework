#!/usr/bin/env python3
"""Stylish Text & Sticker Bot — Unicode formatting and sticker examples.

This bot demonstrates:
- Sending stylish Unicode text (bold, italic, script, double-struck, etc.)
- Sending stickers by file_id
- Converting plain text to fancy Unicode fonts
- Interactive font selection

Usage:
    1. Set BOT_TOKEN environment variable
    2. Run: python stylish_bot.py
    3. Send /start or /fonts to explore

Font categories:
    - Mathematical Bold: 𝐀𝐁𝐂
    - Mathematical Italic: 𝐴𝐵𝐶
    - Mathematical Script: 𝒜𝐵𝐶
    - Mathematical Double-Struck: 𝔸𝔹ℂ
    - Fraktur: 𝔄𝔅ℭ
    - Monospaced: 𝙰𝙱𝙲
    - Full-width: ＡＢＣ
"""

from __future__ import annotations

import logging
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
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

# Unicode font mappings (A-Z, a-z, 0-9)
FONT_MAPS: dict[str, dict[str, str]] = {
    "Bold": {
        "A": "𝐀",
        "B": "𝐁",
        "C": "𝐂",
        "D": "𝐃",
        "E": "𝐄",
        "F": "𝐅",
        "G": "𝐆",
        "H": "𝐇",
        "I": "𝐈",
        "J": "𝐉",
        "K": "𝐊",
        "L": "𝐋",
        "M": "𝐌",
        "N": "𝐍",
        "O": "𝐎",
        "P": "𝐏",
        "Q": "𝐐",
        "R": "𝐑",
        "S": "𝐒",
        "T": "𝐓",
        "U": "𝐔",
        "V": "𝐕",
        "W": "𝐖",
        "X": "𝐗",
        "Y": "𝐘",
        "Z": "𝐙",
        "a": "𝐚",
        "b": "𝐛",
        "c": "𝐜",
        "d": "𝐝",
        "e": "𝐞",
        "f": "𝐟",
        "g": "𝐠",
        "h": "𝐡",
        "i": "𝐢",
        "j": "𝐣",
        "k": "𝐤",
        "l": "𝐥",
        "m": "𝐦",
        "n": "𝐧",
        "o": "𝐨",
        "p": "𝐩",
        "q": "𝐪",
        "r": "𝐫",
        "s": "𝐬",
        "t": "𝐭",
        "u": "𝐮",
        "v": "𝐯",
        "w": "𝐰",
        "x": "𝐱",
        "y": "𝐲",
        "z": "𝐳",
    },
    "Italic": {
        "A": "𝐴",
        "B": "𝐵",
        "C": "𝐶",
        "D": "𝐷",
        "E": "𝐸",
        "F": "𝐹",
        "G": "𝐺",
        "H": "𝐻",
        "I": "𝐼",
        "J": "𝐽",
        "K": "𝐾",
        "L": "𝐿",
        "M": "𝑀",
        "N": "𝑁",
        "O": "𝑂",
        "P": "𝑃",
        "Q": "𝑄",
        "R": "𝑅",
        "S": "𝑆",
        "T": "𝑇",
        "U": "𝑈",
        "V": "𝑉",
        "W": "𝑊",
        "X": "𝑋",
        "Y": "𝑌",
        "Z": "𝑍",
        "a": "𝑎",
        "b": "𝑏",
        "c": "𝑐",
        "d": "𝑑",
        "e": "𝑒",
        "f": "𝑓",
        "g": "𝑔",
        "h": "ℎ",
        "i": "𝑖",
        "j": "𝑗",
        "k": "𝑘",
        "l": "𝑙",
        "m": "𝑚",
        "n": "𝑛",
        "o": "𝑜",
        "p": "𝑝",
        "q": "𝑞",
        "r": "𝑟",
        "s": "𝑠",
        "t": "𝑡",
        "u": "𝑢",
        "v": "𝑣",
        "w": "𝑤",
        "x": "𝑥",
        "y": "𝑦",
        "z": "𝑧",
    },
    "Script": {
        "A": "𝒜",
        "B": "ℬ",
        "C": "𝒞",
        "D": "𝒟",
        "E": "ℰ",
        "F": "ℱ",
        "G": "𝒢",
        "H": "ℋ",
        "I": "ℐ",
        "J": "𝒥",
        "K": "𝒦",
        "L": "ℒ",
        "M": "ℳ",
        "N": "𝒩",
        "O": "𝒪",
        "P": "𝒫",
        "Q": "𝒬",
        "R": "ℛ",
        "S": "𝒮",
        "T": "𝒯",
        "U": "𝒰",
        "V": "𝒱",
        "W": "𝒲",
        "X": "𝒳",
        "Y": "𝒴",
        "Z": "𝒵",
        "a": "𝒶",
        "b": "𝒷",
        "c": "𝒸",
        "d": "𝒹",
        "e": "ℯ",
        "f": "𝒻",
        "g": "ℊ",
        "h": "𝒽",
        "i": "𝒾",
        "j": "𝒿",
        "k": "𝓀",
        "l": "𝓁",
        "m": "𝓂",
        "n": "𝓃",
        "o": "ℴ",
        "p": "𝓅",
        "q": "𝓆",
        "r": "𝓇",
        "s": "𝓈",
        "t": "𝓉",
        "u": "𝓊",
        "v": "𝓋",
        "w": "𝓌",
        "x": "𝓍",
        "y": "𝓎",
        "z": "𝓏",
    },
    "Double-Struck": {
        "A": "𝔸",
        "B": "𝔹",
        "C": "ℂ",
        "D": "𝔻",
        "E": "𝔼",
        "F": "𝔽",
        "G": "𝔾",
        "H": "ℍ",
        "I": "𝕀",
        "J": "𝕁",
        "K": "𝕂",
        "L": "𝕃",
        "M": "𝕄",
        "N": "ℕ",
        "O": "𝕆",
        "P": "ℙ",
        "Q": "ℚ",
        "R": "ℝ",
        "S": "𝕊",
        "T": "𝕋",
        "U": "𝕌",
        "V": "𝕍",
        "W": "𝕎",
        "X": "𝕏",
        "Y": "𝕐",
        "Z": "ℤ",
        "a": "𝕒",
        "b": "𝕓",
        "c": "𝕔",
        "d": "𝕕",
        "e": "𝕖",
        "f": "𝕗",
        "g": "𝕘",
        "h": "𝕙",
        "i": "𝕚",
        "j": "𝕛",
        "k": "𝕜",
        "l": "𝕝",
        "m": "𝕞",
        "n": "𝕟",
        "o": "𝕠",
        "p": "𝕡",
        "q": "𝕢",
        "r": "𝕣",
        "s": "𝕤",
        "t": "𝕥",
        "u": "𝕦",
        "v": "𝕧",
        "w": "𝕨",
        "x": "𝕩",
        "y": "𝕪",
        "z": "𝕫",
    },
    "Fraktur": {
        "A": "𝔄",
        "B": "𝔅",
        "C": "ℭ",
        "D": "𝔇",
        "E": "𝔈",
        "F": "𝔉",
        "G": "𝔊",
        "H": "ℌ",
        "I": "ℑ",
        "J": "𝔍",
        "K": "𝔎",
        "L": "𝔏",
        "M": "𝔐",
        "N": "𝔑",
        "O": "𝔒",
        "P": "𝔓",
        "Q": "𝔔",
        "R": "ℜ",
        "S": "𝔖",
        "T": "𝔗",
        "U": "𝔘",
        "V": "𝔙",
        "W": "𝔚",
        "X": "𝔛",
        "Y": "𝔜",
        "Z": "ℨ",
        "a": "𝔞",
        "b": "𝔟",
        "c": "𝔠",
        "d": "𝔡",
        "e": "𝔢",
        "f": "𝔣",
        "g": "𝔤",
        "h": "𝔥",
        "i": "𝔦",
        "j": "𝔧",
        "k": "𝔨",
        "l": "𝔩",
        "m": "𝔪",
        "n": "𝔫",
        "o": "𝔬",
        "p": "𝔭",
        "q": "𝔮",
        "r": "𝔯",
        "s": "𝔰",
        "t": "𝔱",
        "u": "𝔲",
        "v": "𝔳",
        "w": "𝔴",
        "x": "𝔵",
        "y": "𝔶",
        "z": "𝔷",
    },
    "Monospaced": {
        "A": "𝙰",
        "B": "𝙱",
        "C": "𝙲",
        "D": "𝙳",
        "E": "𝙴",
        "F": "𝙵",
        "G": "𝙶",
        "H": "𝙷",
        "I": "𝙸",
        "J": "𝙹",
        "K": "𝙺",
        "L": "𝙻",
        "M": "𝙼",
        "N": "𝙽",
        "O": "𝙾",
        "P": "𝙿",
        "Q": "𝚀",
        "R": "𝚁",
        "S": "𝚂",
        "T": "𝚃",
        "U": "𝚄",
        "V": "𝚅",
        "W": "𝚆",
        "X": "𝚇",
        "Y": "𝚈",
        "Z": "𝚉",
        "a": "𝚊",
        "b": "𝚋",
        "c": "𝚌",
        "d": "𝚍",
        "e": "𝚎",
        "f": "𝚏",
        "g": "𝚐",
        "h": "𝚑",
        "i": "𝚒",
        "j": "𝚓",
        "k": "𝚔",
        "l": "𝚕",
        "m": "𝚖",
        "n": "𝚗",
        "o": "𝚘",
        "p": "𝚙",
        "q": "𝚚",
        "r": "𝚛",
        "s": "𝚜",
        "t": "𝚝",
        "u": "𝚞",
        "v": "𝚟",
        "w": "𝚠",
        "x": "𝚡",
        "y": "𝚢",
        "z": "𝚣",
    },
}

# Sample sticker file_ids (popular stickers)
# Replace these with actual sticker file_ids from your bot
SAMPLE_STICKERS: dict[str, str] = {
    "👍": "CAACAgIAAxkBAAI",  # Replace with actual file_id
    "❤️": "CAACAgIAAxkBAAJ",  # Replace with actual file_id
    "🎉": "CAACAgIAAxkBAAK",  # Replace with actual file_id
}


def convert_to_font(text: str, font: str) -> str:
    """Convert text to specified Unicode font style."""
    if font not in FONT_MAPS:
        return text

    font_map = FONT_MAPS[font]
    result = []
    for char in text:
        if char in font_map:
            result.append(font_map[char])
        else:
            result.append(char)
    return "".join(result)


def get_all_fonts_preview(text: str) -> str:
    """Generate preview of text in all available fonts."""
    lines = [f"Original: {text}\n"]
    for font_name in FONT_MAPS:
        styled = convert_to_font(text, font_name)
        lines.append(f"{font_name}: {styled}")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — show welcome and font options."""
    if not update.message:
        return

    welcome_text = (
        "✨ *Stylish Text & Sticker Bot* ✨\n\n"
        "I can convert your text into fancy Unicode fonts!\n\n"
        "*Commands:*\n"
        "/fonts - See all available fonts\n"
        "/convert <font> <text> - Convert text to a font\n"
        "/sticker - Send a sample sticker\n\n"
        "*Or just send me any text and I'll style it!*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def show_fonts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all available fonts with preview."""
    if not update.message:
        return

    preview_text = get_all_fonts_preview("Hello World 123")
    await update.message.reply_text(
        f"🎨 *Available Fonts:*\n\n{preview_text}", parse_mode="Markdown"
    )


async def convert_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert text to specified font."""
    if not update.message or not context.args:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /convert <font> <text>\n"
            "Example: /convert Bold Hello World\n\n"
            "Available fonts: " + ", ".join(FONT_MAPS.keys())
        )
        return

    font_name = context.args[0]
    text = " ".join(context.args[1:])

    if font_name not in FONT_MAPS:
        await update.message.reply_text(
            f"Unknown font: {font_name}\n\n"
            "Available fonts: " + ", ".join(FONT_MAPS.keys())
        )
        return

    styled_text = convert_to_font(text, font_name)
    await update.message.reply_text(styled_text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain text messages — show font options as inline keyboard."""
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # Create inline keyboard with font options
    keyboard = []
    row = []
    for font_name in FONT_MAPS:
        styled_preview = convert_to_font(text[:10], font_name)
        if len(text) > 10:
            styled_preview += "..."
        row.append(
            InlineKeyboardButton(
                f"{font_name}", callback_data=f"font:{font_name}:{text}"
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Choose a font for: *{_escape_markdown(text)}*",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle font selection callback."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    parts = query.data.split(":", 2)
    if len(parts) != 3:
        return

    _, font_name, text = parts

    if font_name not in FONT_MAPS:
        return

    styled_text = convert_to_font(text, font_name)

    # Edit the original message with the styled text
    await query.edit_message_text(
        f"✨ *{font_name}:*\n\n{styled_text}",
        parse_mode="Markdown",
    )


async def send_sticker_example(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a sample sticker."""
    if not update.message:
        return

    # Example: Send a sticker by file_id
    # In production, replace with actual sticker file_ids
    # To get a sticker's file_id:
    #   1. Add @FindMyIdBot to a group
    #   2. Forward a sticker to it
    #   3. It will reply with the file_id

    # For demo, we'll send an emoji as text since we don't have real sticker file_ids
    await update.message.reply_text(
        "📝 *How to send stickers:*\n\n"
        "1. Forward any sticker to @FindMyIdBot\n"
        "2. It will reply with the sticker's file_id\n"
        "3. Use `context.bot.send_sticker(chat_id, sticker=file_id)`\n\n"
        "*Example code:*\n"
        "```python\n"
        "await context.bot.send_sticker(\n"
        "    chat_id=update.effective_chat.id,\n"
        "    sticker='CAACAgIAAxkBAA...'\n"
        ")\n"
        "```",
        parse_mode="Markdown",
    )


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back received stickers with file_id info."""
    if not update.message or not update.message.sticker:
        return

    sticker = update.message.sticker
    await update.message.reply_text(
        f"📦 *Sticker Info:*\n\n"
        f"File ID: `{sticker.file_id}`\n"
        f"Unique ID: `{sticker.file_unique_id}`\n"
        f"Emoji: {sticker.emoji or 'N/A'}\n"
        f"Set: {sticker.set_name or 'Custom/Unknown'}\n"
        f"Type: {sticker.type}",
        parse_mode="Markdown",
    )


def _escape_markdown(text: str) -> str:
    """Escape special Markdown characters."""
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fonts", show_fonts))
    application.add_handler(CommandHandler("convert", convert_text))
    application.add_handler(CommandHandler("sticker", send_sticker_example))

    # Callback query handler for inline keyboard
    application.add_handler(CallbackQueryHandler(font_callback, pattern=r"^font:"))

    # Message handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))

    # Error handler
    application.add_error_handler(error_handler)

    logger.info("Stylish Bot started. Press Ctrl+C to stop.")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
