# Chapter 8: Media, Files & Albums

This chapter covers everything about sending, receiving, downloading, and working with media in the Telegram Bot API. Media messages are among the most common interactions users have with bots — from photo galleries to document management to payment invoices.

---

## Sending Files — Three Methods

The Bot API supports three ways to attach media to a message. Each has distinct trade-offs around speed, size limits, and persistence.

### Method 1: By `file_id` (Recommended)

When a bot receives a file, Telegram assigns it a `file_id`. Sending that same `file_id` back avoids a re-upload — Telegram serves the file directly from its CDN.

```python
async def echo_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive a photo and send it back using file_id — zero re-upload."""
    if not update.message or not update.message.photo:
        return

    file_id = update.message.photo[-1].file_id  # highest resolution
    await update.message.reply_photo(
        photo=file_id,
        caption="Here's your photo, sent back via `file_id`.",
        parse_mode="MarkdownV2",
    )
```

**Advantages:**
- No file-size limit (Telegram handles the transfer internally).
- Instant — no upload latency.
- No bandwidth consumed on your server.

**Constraints:**
- The `file_id` is **scoped to your bot**. Bot A cannot use a `file_id` issued to Bot B.
- A `file_id` may change if the file is re-uploaded to Telegram. Use `file_unique_id` for stable identification across re-uploads.

### Method 2: By HTTP URL

Pass a publicly reachable URL. Telegram's servers download the file and attach it to the message.

```python
URL = "https://example.com/assets/promo.jpg"

async def send_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a photo hosted on a public server."""
    if not update.message:
        return
    await update.message.reply_photo(
        photo=URL,
        caption="Downloaded directly from the web.",
    )
```

**Size limits:**

| Media type     | Max size |
|----------------|----------|
| Photos         | 5 MB     |
| All other      | 20 MB    |

The URL **must** be reachable from Telegram's infrastructure (no `localhost`, no IP-restricted endpoints).

### Method 3: By Upload (Local File)

Open the file in binary mode and pass it as a `BufferedReader`. Telegram receives it as a `multipart/form-data` upload.

```python
from pathlib import Path

async def send_by_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Upload a local file to Telegram."""
    if not update.message:
        return

    photo_path = Path("assets/photo.jpg")
    with photo_path.open("rb") as photo_file:
        await update.message.reply_photo(
            photo=photo_file,
            caption="Uploaded from the bot server.",
        )
```

**Size limits:**

| Media type     | Max size |
|----------------|----------|
| Photos         | 10 MB    |
| All other      | 50 MB    |

!!! tip "Use `file_id` whenever possible"
    Uploading is the slowest method. If you already have a `file_id` from a previous interaction, prefer it over re-uploading the same bytes.

---

## `file_id` Rules

Understanding `file_id` behavior is critical for any bot that stores or reuses media.

| Property | Scope | Stability | Use for download? |
|---|---|---|---|
| `file_id` | Per-bot | May change on re-upload | Yes (pass to `getFile`) |
| `file_unique_id` | Cross-bot | Stable across re-uploads | No (informational only) |

```python
async def inspect_file_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demonstrate file_id vs file_unique_id."""
    if not update.message or not update.message.photo:
        return

    photo = update.message.photo[-1]
    await update.message.reply_text(
        f"`file_id`\n```\n{photo.file_id}\n```\n\n"
        f"`file_unique_id`\n```\n{photo.file_unique_id}\n```",
        parse_mode="MarkdownV2",
    )
```

!!! warning "Never hardcode `file_id` values"
    If you store a `file_id` in a database, treat it as ephemeral. Re-verify with `getFile` before relying on it in production.

---

## Media Types & Methods

Each Telegram media type maps to a dedicated method on the Bot API. Below is every type with its parameters and quirks.

### `sendPhoto`

Photos are JPEG-compressed by Telegram on receipt.

| Parameter | Type | Description |
|---|---|---|
| `photo` | `str \| Path \| IO` | `file_id`, URL, or binary upload |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | `MarkdownV2`, `HTML`, or `Markdown` |
| `has_spoiler` | `bool` | Blurred until tapped |
| `show_caption_above_media` | `bool` | Caption renders above the photo |

```python
from telegram import Update
from telegram.ext import ContextTypes

async def send_spoiler_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a photo with a spoiler overlay and caption above media."""
    if not update.message:
        return
    await update.message.reply_photo(
        photo="https://example.com/secret.jpg",
        caption="This is a spoiler\!",
        parse_mode="MarkdownV2",
        has_spoiler=True,
        show_caption_above_media=True,
    )
```

### `sendAudio`

Designed for music files. Telegram renders a custom audio player with metadata.

| Parameter | Type | Description |
|---|---|---|
| `audio` | `str \| Path \| IO` | MP3 or M4A recommended |
| `title` | `str` | Track title |
| `performer` | `str` | Artist name |
| `duration` | `int` | Length in seconds |
| `thumbnail` | `str \| Path \| IO` | `.jpg` or `.png`, up to 200 KB |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode for caption |
| `has_spoiler` | `bool` | Blur the audio message |

```python
from pathlib import Path

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send an audio file with full metadata."""
    if not update.message:
        return

    audio_path = Path("media/track.mp3")
    thumb_path = Path("media/cover.jpg")

    with audio_path.open("rb") as audio, thumb_path.open("rb") as thumb:
        await update.message.reply_audio(
            audio=audio,
            title="Midnight Drive",
            performer="Synthwave Collective",
            duration=234,
            thumbnail=thumb,
            caption="Track 01 — <i>Midnight Drive</i>",
            parse_mode="HTML",
        )
```

### `sendDocument`

The catch-all for any file type. Telegram does not attempt to render a player — it shows a downloadable attachment.

| Parameter | Type | Description |
|---|---|---|
| `document` | `str \| Path \| IO` | Any file type |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `disable_content_type_detection` | `bool` | Prevents Telegram from sniffing MIME type |
| `thumbnail` | `str \| Path \| IO` | `.jpg` or `.png`, up to 200 KB |

```python
from pathlib import Path

async def send_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a PDF document."""
    if not update.message:
        return

    pdf_path = Path("reports/quarterly.pdf")
    with pdf_path.open("rb") as doc:
        await update.message.reply_document(
            document=doc,
            caption="Q4 report — <b>Confidential</b>",
            parse_mode="HTML",
        )
```

### `sendVideo`

For MP4 and other video formats. Telegram renders an inline player.

| Parameter | Type | Description |
|---|---|---|
| `video` | `str \| Path \| IO` | MPEG4 recommended |
| `width` | `int` | Video width in pixels |
| `height` | `int` | Video height in pixels |
| `duration` | `int` | Length in seconds |
| `supports_streaming` | `bool` | Enables progressive download |
| `cover` | `str \| Path \| IO` | Thumbnail image shown before playback |
| `start_timestamp` | `int` | Second at which playback begins |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |
| `has_spoiler` | `bool` | Blur the video |

```python
from pathlib import Path

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a video that starts playing at the 10-second mark."""
    if not update.message:
        return

    video_path = Path("media/demo.mp4")
    with video_path.open("rb") as vid:
        await update.message.reply_video(
            video=vid,
            width=1920,
            height=1080,
            duration=120,
            supports_streaming=True,
            start_timestamp=10,
            caption="Demo reel — starts at the highlight",
        )
```

### `sendAnimation`

GIFs and silent H.264/MPEG-4 AVC videos. Telegram renders an auto-playing animated preview.

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

```python
from pathlib import Path

async def send_gif(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a GIF animation with a caption."""
    if not update.message:
        return

    gif_path = Path("media/reaction.gif")
    with gif_path.open("rb") as gif:
        await update.message.reply_animation(
            animation=gif,
            caption="Me when the tests pass on the first run",
        )
```

### `sendVoice`

Push-to-talk–style voice messages. Telegram renders a voice player.

| Parameter | Type | Description |
|---|---|---|
| `voice` | `str \| Path \| IO` | OGG/OPUS, MP3, or M4A |
| `duration` | `int` | Length in seconds |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |

```python
from pathlib import Path

async def send_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a voice message."""
    if not update.message:
        return

    voice_path = Path("media/voice.ogg")
    with voice_path.open("rb") as voice:
        await update.message.reply_voice(
            voice=voice,
            duration=8,
            caption="Quick note from the field",
        )
```

### `sendVideoNote`

Rounded-square video messages (the "video circles" in Telegram).

| Parameter | Type | Description |
|---|---|---|
| `video_note` | `str \| Path \| IO` | MPEG4, up to 1 minute |
| `length` | `int` | Diameter of the video message (1–1080 px) |
| `duration` | `int` | Length in seconds |
| `thumbnail` | `str \| Path \| IO` | Custom thumbnail |

```python
from pathlib import Path

async def send_videonote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a rounded video note."""
    if not update.message:
        return

    note_path = Path("media/videonote.mp4")
    with note_path.open("rb") as note:
        await update.message.reply_video_note(
            video_note=note,
            length=360,
            duration=15,
        )
```

### `sendSticker`

Stickers come in three formats: static (WEBP), animated (TGS), and video (WEBM).

| Parameter | Type | Description |
|---|---|---|
| `sticker` | `str \| Path \| IO` | `.webp`, `.tgs`, or `.webm` |

```python
async def send_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a sticker by file_id."""
    if not update.message or not update.message.sticker:
        return
    await update.message.reply_sticker(sticker=update.message.sticker.file_id)
```

### `sendLocation`

Geographic coordinates. Supports static, live, and proximity-based locations.

| Parameter | Type | Description |
|---|---|---|
| `latitude` | `float` | Latitude in degrees |
| `longitude` | `float` | Longitude in degrees |
| `horizontal_accuracy` | `float` | Accuracy radius in meters (0–1500) |
| `live_period` | `int` | Seconds the location updates (60–86400) |
| `heading` | `int` | Direction of movement (1–360°) |
| `proximity_alert_radius` | `int` | Meters to trigger arrival alert (0–100000) |

```python
async def send_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a live location that updates for 10 minutes."""
    if not update.message:
        return

    await update.message.reply_location(
        latitude=51.5074,
        longitude=-0.1278,
        live_period=600,
        horizontal_accuracy=10.0,
        heading=90,
    )
```

### `sendVenue`

A location with a name and address — the "pin" messages users see for restaurants, events, etc.

| Parameter | Type | Description |
|---|---|---|
| `latitude` | `float` | Latitude |
| `longitude` | `float` | Longitude |
| `title` | `str` | Venue name |
| `address` | `str` | Street address |
| `foursquare_id` | `str` | Foursquare venue ID (deprecated) |
| `foursquare_type` | `str` | Foursquare venue type (deprecated) |
| `google_place_id` | `str` | Google Place ID |
| `google_place_type` | `str` | Google Place type |

```python
async def send_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a venue with Google Place integration."""
    if not update.message:
        return

    await update.message.reply_venue(
        latitude=48.8584,
        longitude=2.2945,
        title="Eiffel Tower",
        address="Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
        google_place_id="ChIJLU7jZClu5kcR4PcOknswkOI",
        google_place_type="tourist_attraction",
    )
```

### `sendContact`

Share a phone contact.

| Parameter | Type | Description |
|---|---|---|
| `phone_number` | `str` | International format |
| `first_name` | `str` | Contact's first name |
| `last_name` | `str` | Contact's last name |
| `vcard` | `str` | vCard 2.1 formatted contact data |

```python
async def send_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a contact with a vCard."""
    if not update.message:
        return

    vcard = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        "N:Doe;Jane\n"
        "FN:Jane Doe\n"
        "ORG:Acme Corp\n"
        "TEL;TYPE=CELL:+1234567890\n"
        "END:VCARD"
    )
    await update.message.reply_contact(
        phone_number="+1234567890",
        first_name="Jane",
        last_name="Doe",
        vcard=vcard,
    )
```

### `sendPoll`

Interactive polls with extensive configuration.

| Parameter | Type | Description |
|---|---|---|
| `question` | `str` | Poll question (1–300 chars) |
| `options` | `list[str]` | 2–10 answer options (1–100 chars each) |
| `is_anonymous` | `bool` | Hide who voted for what (default `True`) |
| `type` | `str` | `"regular"` or `"quiz"` |
| `allows_multiple_answers` | `bool` | Let users pick more than one option |
| `correct_option_id` | `int` | Index of the correct answer (quiz only) |
| `explanation` | `str` | Shown after a user votes |
| `explanation_parse_mode` | `str` | Formatting for explanation |
| `open_period` | `int` | Seconds the poll stays open (5–600) |
| `close_date` | `int` | Unix timestamp to close the poll |
| `question_parse_mode` | `str` | Formatting for the question text |

```python
async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send an anonymous quiz poll."""
    if not update.message:
        return

    await update.message.reply_poll(
        question="What is the capital of France?",
        options=["London", "Berlin", "Paris", "Madrid"],
        type="quiz",
        correct_option_id=2,
        is_anonymous=True,
        explanation="Paris is the capital and largest city of France\.",
        explanation_parse_mode="MarkdownV2",
        open_period=30,
    )
```

### `sendDice`

Animated dice with random outcomes. Useful for games and casual interactions.

| Parameter | Type | Description |
|---|---|---|
| `emoji` | `str` | One of: 🎯 🎲 🎳 🏀 ⚽ 🎰 |

```python
from telegram.constants import DiceEmoji

async def send_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Roll a dice with a random emoji."""
    if not update.message:
        return

    await update.message.reply_dice(emoji=DiceEmoji.DICE)
```

### `sendInvoice`

Payment integration via Telegram Stars or external payment providers. Covered in detail in the [Payments chapter](12-payments.md).

---

## Albums (Media Groups)

Albums let you send 2–10 media items as a single grouped message. Telegram renders them as a swipeable carousel.

**Rules:**
- All items must be the same media type (all photos, all videos, etc.) — except mixing photos and videos is supported.
- Each item can have its own caption and parse mode.
- You must use `sendMediaGroup`, not individual `sendPhoto` calls.
- Album grouping is preserved on forward/copy if you forward the entire group.

```python
from telegram import InputMediaPhoto, Update
from telegram.ext import ContextTypes

async def send_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a photo album with individual captions."""
    if not update.message:
        return

    media = [
        InputMediaPhoto(
            media="https://example.com/photo1.jpg",
            caption="Photo 1 of 3",
        ),
        InputMediaPhoto(
            media="https://example.com/photo2.jpg",
            caption="Photo 2 of 3",
        ),
        InputMediaPhoto(
            media="https://example.com/photo3.jpg",
            caption="Photo 3 of 3",
        ),
    ]

    await update.message.reply_media_group(media=media)
```

!!! warning "Album caption limitation"
    When forwarding an album, only the **first** item's caption is preserved. If you need captions on all items after a forward, re-send the album with captions manually.

---

## `InputMedia` Classes

Use `InputMedia*` classes to construct album items. Each class wraps a media source with per-item formatting.

| Class | Supported media | Notes |
|---|---|---|
| `InputMediaPhoto` | `.jpg`, `.png`, `.webp` | Most common album item |
| `InputMediaVideo` | `.mp4`, other video | Supports `width`, `height`, `duration`, `supports_streaming` |
| `InputMediaAnimation` | `.gif`, silent `.mp4` | Auto-playing animated preview |
| `InputMediaAudio` | `.mp3`, `.m4a` | Supports `performer`, `title`, `duration` |
| `InputMediaDocument` | Any file type | Generic file attachment |
| `InputMediaLivePhoto` | Live photo pair | `photo` (JPEG) + `video` (MOV) |

```python
from telegram import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Update,
)
from telegram.ext import ContextTypes

async def send_mixed_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send an album mixing different media types."""
    if not update.message:
        return

    media = [
        InputMediaPhoto("https://example.com/scene1.jpg"),
        InputMediaVideo(
            media="https://example.com/clip.mp4",
            caption="A short clip",
            supports_streaming=True,
        ),
        InputMediaAudio(
            media="https://example.com/track.mp3",
            title="Background Music",
            performer="Artist",
        ),
        InputMediaDocument("https://example.com/script.pdf"),
    ]

    await update.message.reply_media_group(media=media)
```

### File ID Support in `InputMedia`

All `InputMedia*` classes accept `file_id`, HTTP URLs, or binary uploads:

```python
media = [
    InputMediaPhoto(media=update.message.photo[-1].file_id),       # file_id
    InputMediaVideo(media="https://example.com/video.mp4"),        # URL
    InputMediaDocument(media=open("report.pdf", "rb")),            # upload
]
```

---

## File Download

When a user sends a file to your bot, you can download it to your server using `getFile`.

### Download URL Pattern

```
https://api.telegram.org/file/bot<token>/<file_path>
```

The `<file_path>` is obtained from `getFile`. Standard bots can download files up to **20 MB**. Local Bot API Servers have no download size limit.

```python
from pathlib import Path

from telegram import Bot, Update
from telegram.ext import ContextTypes

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

async def download_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download a photo sent by the user to the local filesystem."""
    if not not update.message or not update.message.photo:
        return

    bot: Bot = context.bot
    photo = update.message.photo[-1]

    file = await bot.get_file(photo.file_id)
    dest = DOWNLOAD_DIR / f"{photo.file_unique_id}.jpg"
    await file.download_to_drive(custom_path=dest)

    await update.message.reply_text(f"Saved to `{dest}`", parse_mode="MarkdownV2")
```

### Download to Memory

If you need the bytes in memory (e.g., for processing without writing to disk):

```python
import io

async def process_photo_in_memory(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Download a photo into a BytesIO buffer for processing."""
    if not update.message or not update.message.photo:
        return

    bot: Bot = context.bot
    photo = update.message.photo[-1]

    file = await bot.get_file(photo.file_id)
    buffer = io.BytesIO()
    await file.download_to_memory(buffer)

    buffer.seek(0)
    size_kb = len(buffer.getvalue()) / 1024
    await update.message.reply_text(f"Downloaded {size_kb:.1f} KB into memory")
```

### Download Methods Comparison

| Method | Target | Use case |
|---|---|---|
| `download_to_drive()` | Filesystem path | Persistent storage, large files |
| `download_to_memory()` | `BytesIO` buffer | In-memory processing, image manipulation |

---

## Paid Media

Telegram Stars enable monetized media. `sendPaidMedia` requires a `star_count` and an array of media items.

| Parameter | Type | Description |
|---|---|---|
| `star_count` | `int` | Price in Telegram Stars |
| `media` | `list[InputPaidMedia*]` | 1–10 media items |
| `caption` | `str` | 0–1024 characters |
| `parse_mode` | `str` | Formatting mode |

### Paid Media Input Classes

| Class | Supported media |
|---|---|
| `InputPaidMediaPhoto` | Photos |
| `InputPaidMediaVideo` | Videos |
| `InputPaidMediaLivePhoto` | Live photos |

```python
from telegram import InputPaidMediaPhoto, InputPaidMediaVideo, Update
from telegram.ext import ContextTypes

async def send_paid_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send paid media content for 50 Telegram Stars."""
    if not update.message:
        return

    media = [
        InputPaidMediaPhoto("https://example.com/preview1.jpg"),
        InputPaidMediaPhoto("https://example.com/preview2.jpg"),
        InputPaidMediaVideo(
            media="https://example.com/full_video.mp4",
            caption="Full resolution — unlock for 50 stars",
            supports_streaming=True,
        ),
    ]

    await update.message.reply_paid_media(
        star_count=50,
        media=media,
        caption="Premium photo pack + bonus video",
    )
```

---

## Complete Example: Media Handling Bot

A production-ready bot that receives photos, stores their `file_id`s, re-sends them with captions, handles documents with downloads, and sends albums.

```python
"""Media handling bot — receive, store, re-send, and download files."""

import io
import logging
from pathlib import Path
from typing import Final

from telegram import InputMediaPhoto, Update
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

TOKEN: Final[str] = "BOT_TOKEN_HERE"
STORAGE_DIR = Path("media_storage")
STORAGE_DIR.mkdir(exist_ok=True)

# In-memory store: chat_id -> list of file_ids
photo_store: dict[int, list[str]] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user and explain usage."""
    if not update.message:
        return
    await update.message.reply_text(
        "Send me photos and I'll store them\\.\n\n"
        "Commands:\n"
        "/gallery — view all stored photos\n"
        "/download — download the last photo you sent",
        parse_mode="MarkdownV2",
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store a received photo's file_id."""
    if not update.effective_chat or not update.message or not update.message.photo:
        return

    chat_id = update.effective_chat.id
    photo = update.message.photo[-1]  # highest resolution

    photo_store.setdefault(chat_id, []).append(photo.file_id)
    count = len(photo_store[chat_id])

    await update.message.reply_text(
        f"Photo #{count} stored\\.", parse_mode="MarkdownV2"
    )
    logger.info(
        "Stored photo %s for chat %d (total: %d)",
        photo.file_unique_id,
        chat_id,
        count,
    )


async def send_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send all stored photos as an album."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    files = photo_store.get(chat_id, [])

    if not files:
        await update.message.reply_text("No photos stored yet.")  # type: ignore[union-attr]
        return

    # Albums are capped at 10 items
    batch = files[:10]
    media = [InputMediaPhoto(fid) for fid in batch]

    await context.bot.send_media_group(chat_id=chat_id, media=media)


async def download_last(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download the last photo the user sent."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    files = photo_store.get(chat_id, [])

    if not files:
        await update.message.reply_text("No photos to download.")  # type: ignore[union-attr]
        return

    file_id = files[-1]
    tg_file = await context.bot.get_file(file_id)

    buffer = io.BytesIO()
    await tg_file.download_to_memory(buffer)
    buffer.seek(0)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=buffer,
        caption=f"Re-downloaded from file_id",
    )


async def receive_document(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Download a received document to the local filesystem."""
    if not update.effective_chat or not update.message or not update.message.document:
        return

    doc = update.message.document
    if not doc.file_name:
        await update.message.reply_text("Document has no file name.")
        return

    dest = STORAGE_DIR / doc.file_name
    tg_file = await context.bot.get_file(doc.file_id)
    await tg_file.download_to_drive(custom_path=dest)

    await update.message.reply_text(
        f"Saved `{doc.file_name}` ({doc.file_size or 0} bytes)",
        parse_mode="MarkdownV2",
    )
    logger.info("Downloaded document to %s", dest)


def main() -> None:
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gallery", send_gallery))
    app.add_handler(CommandHandler("download", download_last))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_document))

    logger.info("Media bot starting")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

---

## Quick Reference

| Action | Method | Max size |
|---|---|---|
| Send photo (fastest) | `file_id` | No limit |
| Send photo (URL) | HTTP URL | 5 MB |
| Send photo (upload) | Binary | 10 MB |
| Send other media (URL) | HTTP URL | 20 MB |
| Send other media (upload) | Binary | 50 MB |
| Download file | `getFile` → `download_to_drive()` | 20 MB (standard) / unlimited (local) |
| Album size | `sendMediaGroup` | 2–10 items |
| Paid media | `sendPaidMedia` | 1–10 items |
