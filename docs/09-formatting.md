# Chapter 9: Message Formatting

Telegram supports rich text in messages through three formatting modes: **MarkdownV2**, **HTML**, and the legacy **Markdown**. This chapter covers syntax, escaping rules, entity types, custom emoji, and production-ready helper utilities.

---

## Overview

Every text-based message method (`sendMessage`, `editMessageText`, `reply_text`, etc.) accepts an optional `parse_mode` parameter. When set, Telegram interprets special characters as formatting instructions.

| Mode | Recommendation |
|---|---|
| `HTML` | Preferred — familiar syntax, fewer escaping pitfalls |
| `MarkdownV2` | Powerful but escaping-heavy — use when HTML isn't an option |
| `Markdown` | Legacy — limited features, no nesting. Avoid in new code |

!!! tip "Default to HTML"
    HTML mode requires escaping only `<`, `>`, and `&`. MarkdownV2 requires escaping 18+ characters. For most bots, HTML is the pragmatic choice.

---

## MarkdownV2 Style

MarkdownV2 uses wrapping characters to denote entities. Text inside formatting markers is rendered with the corresponding style.

### Syntax Reference

| Entity | Syntax | Example |
|---|---|---|
| Bold | `*text*` | `*bold*` |
| Italic | `_text_` | `_italic_` |
| Underline | `__text__` | `__underlined__` |
| Strikethrough | `~text~` | `~struck~` |
| Spoiler | `\|\|text\|\|` | `\|\|hidden\|\|` |
| Inline code | `` `code` `` | `` `print()` `` |
| Pre-formatted block | ` ```code``` ` | ` ```1 + 1``` ` |
| Code block with language | ` ```python code``` ` | ` ```python\nprint("hi")``` ` |
| Blockquote | `>text` | `>quoted text` |
| Expandable blockquote | `**>text\|\|` | `**>tap to expand\|\|` |
| Inline URL | `[text](url)` | `[Google](https://google.com)` |
| Inline mention | `[name](tg://user?id=123)` | `[John](tg://user?id=123456)` |

### Nesting Rules

Entities can be nested — the innermost entity's markers take precedence:

```text
*bold _and italic_ also ~struck~*
```

Renders as: **bold** ***and italic*** also ~~struck~~.

!!! danger "Escaping is mandatory"
    Any character that is part of MarkdownV2 syntax **must** be escaped with `\` if it appears as literal text. Failing to escape causes `BadRequest` errors.

### Escaping Rules (Critical)

These characters must be escaped with `\` when they appear as **literal text** (not as formatting markers):

```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

**Inside a code/pre block**, only these need escaping:

```
` and \
```

**Inside a link URL**, only these need escaping:

```
) and \
```

The backslash itself must always be escaped: `\\`.

```python
import re

# Characters that MUST be escaped in MarkdownV2 outside code blocks
SPECIAL_CHARS = r"_*[]()~`>#+-=|{}.!"

def escape_markdown_v2(text: str) -> str:
    """Escape all special characters for MarkdownV2 formatting."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", text)


async def send_safe_markdown(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message with user input safely escaped in MarkdownV2."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    safe_text = escape_markdown_v2(user_text)

    await update.message.reply_text(
        f"You said: {safe_text}",
        parse_mode="MarkdownV2",
    )
```

### Code Blocks

Code blocks suppress formatting interpretation. Only `` ` `` and `\` need escaping inside them:

```text
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```
```

```text
```No language tag — renders as plain pre-formatted text
1 + 1 = 2
```
```

### Blockquotes

Standard blockquotes render as indented text:

```text
>This is a blockquote.
>It can span multiple lines.
```

Expandable blockquotes show a "tap to expand" indicator:

```text
**>This is expandable.
>It collapses by default.
```

---

## HTML Style

HTML mode uses standard HTML tags. It is more verbose but requires far less escaping.

### Syntax Reference

| Entity | HTML | Also accepted |
|---|---|---|
| Bold | `<b>text</b>` | `<strong>text</strong>` |
| Italic | `<i>text</i>` | `<em>text</em>` |
| Underline | `<u>text</u>` | `<ins>text</ins>` |
| Strikethrough | `<s>text</s>` | `<strike>text</strike>`, `<del>text</del>` |
| Spoiler | `<span class="tg-spoiler">text</span>` | `<tg-spoiler>text</tg-spoiler>` |
| Inline code | `<code>text</code>` | — |
| Pre block | `<pre>text</pre>` | — |
| Code block | `<pre><code class="language-python">code</code></pre>` | — |
| Blockquote | `<blockquote>text</blockquote>` | — |
| Expandable blockquote | `<blockquote expandable>text</blockquote>` | — |
| Inline URL | `<a href="URL">text</a>` | — |
| Custom emoji | `<tg-emoji emoji-id="ID">👍</tg-emoji>` | — |

### Nesting Rules

HTML tags nest like standard XML — close the innermost tag first:

```html
<b>Bold and <i>italic</i> together</b>
```

Renders as: **Bold and _italic_ together**.

### HTML Escaping

Only three characters require escaping:

| Character | Escape sequence |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |

Supported named entities: `&lt;`, `&gt;`, `&amp;`, `&quot;`.

```python
import html as html_lib

from telegram import Update
from telegram.ext import ContextTypes


def escape_html(text: str) -> str:
    """Escape text for safe insertion into HTML-formatted Telegram messages."""
    return html_lib.escape(text, quote=False)


async def send_safe_html(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message with user input safely escaped in HTML mode."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    safe_text = escape_html(user_text)

    await update.message.reply_text(
        f"You said: <code>{safe_text}</code>",
        parse_mode="HTML",
    )
```

!!! note "HTML tag validation"
    Telegram only recognizes the specific tags listed above. Unknown tags (e.g., `<div>`, `<span>` with arbitrary classes) are stripped or cause errors.

---

## Markdown (Legacy)

The original Markdown mode. It supports only a small subset of formatting and **does not support nesting**.

| Feature | Syntax |
|---|---|
| Bold | `*text*` |
| Italic | `_text_` |
| Code | `` `code` `` |
| Pre block | ` ```code``` ` |
| Link | `[text](url)` |

!!! warning "Do not use in new code"
    Legacy Markdown cannot represent underline, strikethrough, spoiler, blockquotes, or custom emoji. It also cannot nest entities. Always prefer MarkdownV2 or HTML.

---

## Formatting Comparison Table

| Feature | MarkdownV2 | HTML | Markdown (Legacy) |
|---|---|---|---|
| Bold | `*text*` | `<b>text</b>` | `*text*` |
| Italic | `_text_` | `<i>text</i>` | `_text_` |
| Underline | `__text__` | `<u>text</u>` | — |
| Strikethrough | `~text~` | `<s>text</s>` | — |
| Spoiler | `\|\|text\|\|` | `<tg-spoiler>text</tg-spoiler>` | — |
| Inline code | `` `code` `` | `<code>code</code>` | `` `code` `` |
| Pre block | ` ```code``` ` | `<pre>code</pre>` | ` ```code``` ` |
| Code block + lang | ` ```python code``` ` | `<pre><code class="language-python">code</code></pre>` | — |
| Link | `[text](url)` | `<a href="url">text</a>` | `[text](url)` |
| Mention | `[name](tg://user?id=123)` | `<a href="tg://user?id=123">name</a>` | — |
| Blockquote | `>text` | `<blockquote>text</blockquote>` | — |
| Expandable blockquote | `**>text\|\|` | `<blockquote expandable>text</blockquote>` | — |
| Custom emoji | `![emoji](tg://emoji?id=ID)` | `<tg-emoji emoji-id="ID">👍</tg-emoji>` | — |
| Escaping effort | High (18+ chars) | Low (3 chars) | Low |

---

## Date-Time Entities

Telegram renders Unix timestamps as clickable elements that display the date/time in the user's local timezone. Format the timestamp with a special syntax appended using the pipe `|` character.

### Format String: `r|w?[dD]?[tT]?`

| Flag | Meaning | Example |
|---|---|---|
| `r` | Relative time ("2 hours ago") | `1700000000\|r` |
| `w` | Day of the week | `1700000000\|w` |
| `d` | Short date | `1700000000\|d` |
| `D` | Long date | `1700000000\|D` |
| `t` | Short time | `1700000000\|t` |
| `T` | Long time | `1700000000\|T` |

Flags can be combined: `1700000000|d|t` renders as short date + short time.

### MarkdownV2

```python
import time

timestamp = int(time.time())
# Escape the pipe character in MarkdownV2
escaped_ts = str(timestamp).replace("|", "\\|")

await update.message.reply_text(
    f"Current time: {escaped_ts}\\|T",
    parse_mode="MarkdownV2",
)
```

### HTML

```python
import time

timestamp = int(time.time())

await update.message.reply_text(
    f"Current time: <tg-datetime iso=\"{timestamp}\">{timestamp}</tg-datetime>",
    parse_mode="HTML",
)
```

---

## Custom Emoji

Custom emoji are premium stickers that can be embedded inline in text. They require a `CUSTOM_EMOJI_ID` obtained from the Bot API's `getCustomEmojiStickers` method.

**Requirements:**
- The bot must have purchased usernames on [Fragment](https://fragment.com), **or**
- The emoji's owner has Telegram Premium.

### MarkdownV2

```text
![🔥](tg://emoji?id=5368324170671202286)
```

### HTML

```html
<tg-emoji emoji-id="5368324170671202286">🔥</tg-emoji>
```

```python
from telegram import Update
from telegram.ext import ContextTypes


async def send_custom_emoji(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message containing a custom emoji."""
    if not update.message:
        return

    emoji_id = "5368324170671202286"

    # MarkdownV2
    await update.message.reply_text(
        f"Check out this emoji: ![🔥](tg://emoji?id={emoji_id})",
        parse_mode="MarkdownV2",
    )

    # HTML equivalent
    # await update.message.reply_text(
    #     f'Check out this emoji: <tg-emoji emoji-id="{emoji_id}">🔥</tg-emoji>',
    #     parse_mode="HTML",
    # )
```

---

## Best Practices

### 1. Always Handle Formatting Errors

Malformed text raises `BadRequest` with `MessageTextIsNotModified` or `Can't parse entities`. Wrap formatted sends in error handling:

```python
import logging
from html import escape as html_escape

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def send_formatted(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    parse_mode: str = ParseMode.HTML,
) -> None:
    """Send a formatted message with graceful fallback on parse errors."""
    if not update.message:
        return

    try:
        await update.message.reply_text(text, parse_mode=parse_mode)
    except BadRequest as exc:
        logger.warning("Formatting failed (%s), retrying without parse_mode", exc)
        await update.message.reply_text(text, parse_mode=None)
```

### 2. Escape User Input Before Inserting

Never inject raw user text into a formatted string. Always escape it first:

```python
from telegram.constants import ParseMode

def build_response(user_input: str, parse_mode: str = ParseMode.HTML) -> str:
    """Build a formatted response with safely escaped user input."""
    if parse_mode == ParseMode.HTML:
        safe = html_escape(user_input, quote=False)
        return f"<b>You said:</b> {safe}"
    elif parse_mode == ParseMode.MARKDOWN_V2:
        safe = escape_markdown_v2(user_input)
        return f"*You said:* {safe}"
    return user_input
```

### 3. Prefer HTML Over MarkdownV2

HTML mode escapes 3 characters. MarkdownV2 escapes 18+. Unless you have a specific reason to use MarkdownV2, HTML reduces bugs.

### 4. Use `parse_mode` Defaults

Set a default `parse_mode` in your `Application` builder to avoid repeating it on every call:

```python
from telegram.ext import ApplicationBuilder, Defaults

app = (
    ApplicationBuilder()
    .token("BOT_TOKEN")
    .defaults(Defaults(parse_mode=ParseMode.HTML))
    .build()
)
```

All subsequent `reply_text`, `send_message`, and similar calls will default to HTML formatting.

### 5. Test Formatting in Both Light and Dark Themes

Some entity colors are subtle in certain themes. Test your formatted messages in Telegram's light mode, dark mode, and night mode.

---

## Utility Functions

Production-ready helpers for escaping and building formatted messages.

### MarkdownV2 Escaper

```python
import re

_MDV2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def escape_markdown_v2(text: str) -> str:
    """
    Escape all MarkdownV2 special characters in *text*.

    This does NOT escape inside code blocks — handle those separately.

    Args:
        text: Raw text to escape.

    Returns:
        MarkdownV2-safe text.
    """
    return re.sub(r"([\\_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


def escape_markdown_v2_code(text: str) -> str:
    """
    Escape text for inside a MarkdownV2 code or pre block.

    Only backticks and backslashes need escaping here.

    Args:
        text: Raw code text.

    Returns:
        Code-safe text.
    """
    return text.replace("\\", "\\\\").replace("`", "\\`")


def escape_markdown_v2_url(url: str) -> str:
    """
    Escape text for inside a MarkdownV2 link URL.

    Only closing parentheses and backslashes need escaping.

    Args:
        url: Raw URL.

    Returns:
        URL-safe text.
    """
    return url.replace("\\", "\\\\").replace(")", "\\)")
```

### HTML Builder

```python
import html as html_lib


def escape_html(text: str) -> str:
    """
    Escape text for safe insertion into HTML-formatted Telegram messages.

    Args:
        text: Raw text.

    Returns:
        HTML-safe text.
    """
    return html_lib.escape(text, quote=False)


def bold(text: str, parse_mode: str = "HTML") -> str:
    """Wrap text in bold formatting."""
    safe = escape_html(text) if parse_mode == "HTML" else escape_markdown_v2(text)
    if parse_mode == "HTML":
        return f"<b>{safe}</b>"
    return f"*{safe}*"


def italic(text: str, parse_mode: str = "HTML") -> str:
    """Wrap text in italic formatting."""
    safe = escape_html(text) if parse_mode == "HTML" else escape_markdown_v2(text)
    if parse_mode == "HTML":
        return f"<i>{safe}</i>"
    return f"_{safe}_"


def code(text: str, parse_mode: str = "HTML") -> str:
    """Wrap text in inline code formatting."""
    if parse_mode == "HTML":
        return f"<code>{escape_html(text)}</code>"
    return f"`{escape_markdown_v2_code(text)}`"


def link(text: str, url: str, parse_mode: str = "HTML") -> str:
    """Create a hyperlink."""
    if parse_mode == "HTML":
        return f'<a href="{escape_html(url)}">{escape_html(text)}</a>'
    return f"[{escape_markdown_v2(text)}]({escape_markdown_v2_url(url)})"


def mention(text: str, user_id: int, parse_mode: str = "HTML") -> str:
    """Create an inline mention link."""
    if parse_mode == "HTML":
        return f'<a href="tg://user?id={user_id}">{escape_html(text)}</a>'
    return f"[{escape_markdown_v2(text)}](tg://user?id={user_id})"
```

### Message Template System

For complex messages with multiple formatting types, a template function keeps things clean:

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FormattedMessage:
    """Builder for complex Telegram messages with consistent formatting."""

    parse_mode: str = "HTML"
    _parts: list[str] = field(default_factory=list, repr=False)

    def text(self, content: str) -> "FormattedMessage":
        """Append raw text (escaped automatically)."""
        self._parts.append(escape_html(content) if self.parse_mode == "HTML"
                           else escape_markdown_v2(content))
        return self

    def bold_text(self, content: str) -> "FormattedMessage":
        """Append bold text."""
        self._parts.append(bold(content, self.parse_mode))
        return self

    def code_block(self, content: str, language: str = "") -> "FormattedMessage":
        """Append a code block."""
        if self.parse_mode == "HTML":
            lang_attr = f' class="language-{language}"' if language else ""
            self._parts.append(f"<pre><code{lang_attr}>{escape_html(content)}</code></pre>")
        else:
            fence = "```"
            self._parts.append(f"{fence}{language}\n{escape_markdown_v2_code(content)}\n{fence}")
        return self

    def inline_code(self, content: str) -> "FormattedMessage":
        """Append inline code."""
        self._parts.append(code(content, self.parse_mode))
        return self

    def link(self, text: str, url: str) -> "FormattedMessage":
        """Append a hyperlink."""
        self._parts.append(link(text, url, self.parse_mode))
        return self

    def mention(self, text: str, user_id: int) -> "FormattedMessage":
        """Append a user mention."""
        self._parts.append(mention(text, user_id, self.parse_mode))
        return self

    def newline(self) -> "FormattedMessage":
        """Append a newline separator."""
        self._parts.append("\n")
        return self

    def raw(self, content: str) -> "FormattedMessage":
        """Append pre-formatted content (no escaping). Use with caution."""
        self._parts.append(content)
        return self

    def build(self) -> str:
        """Return the final formatted string."""
        return "".join(self._parts)


async def send_template_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: FormattedMessage,
) -> None:
    """Send a FormattedMessage with error handling."""
    if not update.message:
        return

    text = message.build()
    try:
        await update.message.reply_text(text, parse_mode=message.parse_mode)
    except BadRequest as exc:
        logger.warning("Template render failed (%s), sending plain text", exc)
        await update.message.reply_text(text, parse_mode=None)
```

### Usage Example

```python
async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show a formatted status report using the template system."""
    if not update.effective_user:
        return

    msg = (
        FormattedMessage(parse_mode="HTML")
        .bold_text("Bot Status Report")
        .newline()
        .newline()
        .text("User: ")
        .mention(update.effective_user.full_name, update.effective_user.id)
        .newline()
        .text("Uptime: ")
        .inline_code("4h 32m")
        .newline()
        .text("Docs: ")
        .link("View on GitHub", "https://github.com/example/bot")
        .newline()
        .newline()
        .code_block(
            'python\nprint("Hello, world!")\n',
            language="python",
        )
    )

    await send_template_message(update, context, msg)
```

---

## Entity Parsing Utilities

The Bot API can parse entities from plain text using `parseMessageEntities` and `parseMarkdownV2`. This is useful for extracting mentions, links, or code from messages your bot receives:

```python
from telegram import Update
from telegram.constants import MessageEntityType
from telegram.ext import ContextTypes


async def extract_entities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse and report all entities in the user's message."""
    if not update.message or not update.message.entities:
        return

    results: list[str] = []
    for entity in update.message.entities:
        text = entity.parse_text(update.message.text or "")
        type_name = MessageEntityType(entity.type).name
        results.append(f"{type_name}: {text}")

    summary = "\n".join(results) or "No entities found."
    await update.message.reply_text(f"Detected entities:\n{summary}")
```

---

## Quick Reference

| Task | Recommendation |
|---|---|
| New bot, no formatting preference | Use `HTML` mode |
| Need expandable blockquotes | MarkdownV2 (`**>...\|\|`) or HTML (`<blockquote expandable>`) |
| User input in messages | Always escape before inserting |
| Setting default parse mode | `Defaults(parse_mode=ParseMode.HTML)` on `ApplicationBuilder` |
| Formatting parse error | Catch `BadRequest`, retry without `parse_mode` |
| Custom emoji | Requires `CUSTOM_EMOJI_ID` + Premium or Fragment purchase |
| Timestamps | Use `1234567890\|T` (MarkdownV2) or `<tg-datetime>` (HTML) |
