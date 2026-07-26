# Chapter 17: Testing & Debugging

Production bots demand rigorous testing. A single unhandled exception in production
can silently drop updates, lose user data, or take your bot offline entirely. This
chapter covers a layered testing strategy—from fast unit tests through integration
tests to full end-to-end validation—plus practical debugging techniques for when
something goes wrong.

---

## Testing Strategy

Adopt a three-tier approach that mirrors established best practices:

| Tier | Scope | Speed | Isolation | Tooling |
|------|-------|-------|-----------|---------|
| **Unit** | Individual handler functions, utility modules | Milliseconds | Full mock isolation | `pytest`, `unittest.mock` |
| **Integration** | Handler registration, filter chains, middleware pipelines | Hundreds of ms | In-process, mocked API | `python-telegram-bot` test utilities, `pytest-asyncio` |
| **End-to-End** | Real Telegram API, real bot token, test group/channel | Seconds | Separate test environment | `Application` builder, dedicated test bot |

**Rule of thumb:** Aim for ~80 % unit tests, ~15 % integration tests, ~5 % E2E.
Unit tests catch logic bugs; integration tests catch wiring bugs; E2E tests catch
platform-specific surprises.

---

## Unit Testing Handlers

### Mock Objects

The core challenge in testing `python-telegram-bot` handlers is that they receive
`Update` and `Context` objects populated by the framework. In tests you build these
manually with mocks:

```python
import logging
import unittest
from unittest.mock import AsyncMock, Mock, patch

from telegram import Chat, Update, User
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class TestStartHandler(unittest.TestCase):
    """Tests for the /start command handler."""

    def setUp(self) -> None:
        self.user = User(id=123, first_name="Test", is_bot=False)
        self.chat = Chat(id=123, type="private")

        self.message = Mock(spec=Update.message)
        self.message.from_user = self.user
        self.message.chat = self.chat
        self.message.reply_text = AsyncMock()
        self.message.text = "/start"

        self.update = Mock(spec=Update)
        self.update.message = self.message
        self.update.effective_user = self.user
        self.update.effective_chat = self.chat

        self.context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.bot = AsyncMock()
        self.context.args: list[str] = []
        self.context.user_data: dict = {}
        self.context.chat_data: dict = {}
        self.context.bot_data: dict = {}

    async def test_start_handler_sends_welcome(self) -> None:
        """Handler must reply with a welcome message."""
        from handlers.start import start

        await start(self.update, self.context)

        self.update.message.reply_text.assert_called_once()
        args, kwargs = self.update.message.reply_text.call_args
        self.assertIn("Welcome", args[0])

    async def test_start_handler_with_argument(self) -> None:
        """Handler should handle deep-link arguments."""
        self.context.args = ["payload123"]

        from handlers.start import start

        await start(self.update, self.context)

        self.update.message.reply_text.assert_called_once()

    async def test_start_handler_records_user(self) -> None:
        """Handler should store user data on first interaction."""
        from handlers.start import start

        await start(self.update, self.context)

        self.assertTrue(len(self.context.user_data) > 0)
```

> **Tip:** Always use `Mock(spec=...)` rather than bare `Mock()`. The `spec`
> parameter constrains mock attributes to those that exist on the real class,
> catching typos and signature mismatches early.

### Using `pytest-asyncio`

For cleaner test code, prefer `pytest` with `pytest-asyncio`. The async test
functions read identically to production handler code:

```python
import pytest
from unittest.mock import AsyncMock, Mock

from telegram import Chat, Update, User
from telegram.ext import ContextTypes


@pytest.fixture
def update() -> Mock:
    """Build a mock Update representing a private text message."""
    user = User(id=456, first_name="Alice", is_bot=False)
    chat = Chat(id=456, type="private")

    upd = Mock(spec=Update)
    upd.message = Mock(spec=Update.message)
    upd.message.from_user = user
    upd.message.chat = chat
    upd.message.reply_text = AsyncMock()
    upd.message.reply_photo = AsyncMock()
    upd.message.reply_document = AsyncMock()
    upd.message.text = "Hello"
    upd.message.photo = []
    upd.effective_user = user
    upd.effective_chat = chat
    return upd


@pytest.fixture
def context() -> Mock:
    """Build a mock Context with empty data stores."""
    ctx = Mock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.bot = AsyncMock()
    ctx.args: list[str] = []
    ctx.user_data: dict = {}
    ctx.chat_data: dict = {}
    ctx.bot_data: dict = {}
    return ctx


@pytest.mark.asyncio
async def test_echo_handler(update: Mock, context: Mock) -> None:
    """Echo handler should repeat the incoming text."""
    from handlers.user import echo

    update.message.text = "Hello"

    await echo(update, context)

    update.message.reply_text.assert_called_once_with("Hello")


@pytest.mark.asyncio
async def test_echo_handler_empty_message(update: Mock, context: Mock) -> None:
    """Echo handler should handle empty text gracefully."""
    from handlers.user import echo

    update.message.text = ""

    await echo(update, context)

    update.message.reply_text.assert_called_once_with("")
```

### Fixtures for Reuse

Consolidate mock construction into shared fixtures to avoid repetition. Place
fixtures in a `conftest.py` at the project root:

```python
# conftest.py
import pytest
from unittest.mock import AsyncMock, Mock

from telegram import Chat, User
from telegram.ext import ContextTypes


@pytest.fixture
def private_chat_update() -> Mock:
    """Mock Update for a private-chat text message."""
    user = User(id=1, first_name="Tester", is_bot=False)
    chat = Chat(id=1, type="private")

    update = Mock(spec=["message", "effective_user", "effective_chat"])
    update.message = Mock(spec=["text", "reply_text", "from_user", "chat"])
    update.message.from_user = user
    update.message.chat = chat
    update.message.reply_text = AsyncMock()
    update.message.text = ""
    update.effective_user = user
    update.effective_chat = chat
    return update


@pytest.fixture
def group_update() -> Mock:
    """Mock Update for a group text message."""
    user = User(id=2, first_name="GroupUser", is_bot=False)
    chat = Chat(id=-100123456, type="supergroup")

    update = Mock(spec=["message", "effective_user", "effective_chat"])
    update.message = Mock(spec=["text", "reply_text", "from_user", "chat"])
    update.message.from_user = user
    update.message.chat = chat
    update.message.reply_text = AsyncMock()
    update.message.text = ""
    update.effective_user = user
    update.effective_chat = chat
    return update


@pytest.fixture
def default_context() -> Mock:
    """Mock Context with empty data stores."""
    ctx = Mock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.bot = AsyncMock()
    ctx.args = []
    ctx.user_data = {}
    ctx.chat_data = {}
    ctx.bot_data = {}
    return ctx
```

### Testing CallbackQueryHandler

Callback queries require careful mocking because both `answer` and `edit_message_text`
are async methods on the callback query object:

```python
import pytest
from unittest.mock import AsyncMock, Mock

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes


@pytest.fixture
def callback_update() -> Mock:
    """Mock Update carrying a callback query."""
    user = User(id=1, first_name="Tester", is_bot=False)

    update = Mock(spec=Update)
    update.callback_query = Mock(spec=CallbackQuery)
    update.callback_query.from_user = user
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.data = "subscribe:weekly"
    update.effective_user = user
    return update


@pytest.mark.asyncio
async def test_subscribe_weekly(callback_update: Mock) -> None:
    """Weekly subscription callback should answer and edit message."""
    from handlers.callbacks import subscribe_handler

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    await subscribe_handler(callback_update, context)

    callback_update.callback_query.answer.assert_awaited_once()
    callback_update.callback_query.edit_message_text.assert_awaited_once()
```

---

## Integration Testing

Integration tests verify that handlers are correctly registered, filters behave as
expected, and the application processes updates through the full handler chain
without touching the real Telegram API.

### Testing Handler Registration

```python
import pytest
from unittest.mock import AsyncMock

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.start import start
from handlers.user import echo
from handlers.callbacks import subscribe_handler


@pytest.fixture
def app():
    """Build an Application with test handlers and no network."""
    return (
        ApplicationBuilder()
        .token("TEST:FAKE-TOKEN")
        .build()
    )


def test_command_handlers_registered(app) -> None:
    """Application should resolve /start to the start handler."""
    app.add_handler(CommandHandler("start", start))

    handler = app.handler_check resolving /start
    assert handler is not None


def test_handler_group_ordering(app) -> None:
    """Handlers in lower-numbered groups fire first."""
    app.add_handler(CommandHandler("start", start), group=0)
    app.add_handler(MessageHandler(filters.TEXT, echo), group=1)

    # Group 0 handlers fire before group 1
    assert len(app.handlers[0]) >= 1
    assert len(app.handlers[1]) >= 1
```

### Testing Filter Logic

Filters are plain predicates—test them directly:

```python
from telegram import Chat, Message, Update, User
from telegram.ext import filters


def test_text_filter_matches_plain_text() -> None:
    """filters.TEXT should match plain text messages."""
    msg = Message(
        message_id=1,
        date=None,
        chat=Chat(id=1, type="private"),
        text="Hello",
    )
    assert filters.TEXT.check_update(msg)


def test_text_filter_rejects_photo() -> None:
    """filters.TEXT should not match photo messages."""
    msg = Message(
        message_id=1,
        date=None,
        chat=Chat(id=1, type="private"),
        photo=[],
    )
    assert not filters.TEXT.check_update(msg)


def test_regex_filter() -> None:
    """filters.Regex should match messages containing the pattern."""
    import re

    f = filters.Regex(re.compile(r"^/status\s+\w+$"))
    msg = Message(
        message_id=1,
        date=None,
        chat=Chat(id=1, type="private"),
        text="/status active",
    )
    assert f.check_update(msg)
```

---

## End-to-End Testing

E2E tests exercise the full stack against a real Telegram Bot API using a dedicated
**test bot** (never your production bot). Create a separate bot via @BotFather and
store its token in an environment variable:

```python
import asyncio
import os

import pytest
from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.start import start


@pytest.fixture
def live_app():
    """Application connected to a real test bot."""
    token = os.environ.get("TEST_BOT_TOKEN")
    if not token:
        pytest.skip("TEST_BOT_TOKEN not set")
    return ApplicationBuilder().token(token).build()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_start_command_live(live_app) -> None:
    """Send /start to the test bot and verify a reply arrives."""
    live_app.add_handler(CommandHandler("start", start))

    async with live_app.bot as bot:
        me = await bot.get_me()
        assert me.is_bot
```

> **Warning:** E2E tests are inherently slower and flakier than unit or integration
> tests. Gate them behind a marker (`pytest -m e2e`) so they don't slow down
> regular CI runs.

---

## Debugging

### Logging Configuration

Enable verbose logging early when debugging. The `python-telegram-bot` library uses
the standard `logging` module:

```python
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
# Quieten noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

In production, drop to `INFO` or `WARNING`. Only enable `DEBUG` during active
development.

### Inspecting the Update Object

When a handler isn't behaving as expected, log the raw update to see exactly what
Telegram sent:

```python
import json
import logging

logger = logging.getLogger(__name__)


async def debug_handler(update, context) -> None:
    """Temporary handler that dumps every incoming update."""
    if update.message:
        logger.debug("Message text: %s", update.message.text)
        logger.debug("From user: %s", update.effective_user.id)
        logger.debug("Chat type: %s", update.effective_chat.type)
    elif update.callback_query:
        logger.debug("Callback data: %s", update.callback_query.data)
    else:
        logger.debug("Update type: %s", type(update).__name__)
```

Register this as the first handler during debugging to capture all updates before
more specific handlers consume them.

### Common Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized` | Invalid or revoked token | Regenerate via @BotFather |
| `Timed out` | Network latency or long handler | Increase `read_timeout`, move slow work to background |
| `Conflict: terminated by other getUpdates` | Two instances polling same token | Stop the other instance; use one webhook or one polling bot |
| `Bad Request: message not modified` | Edit with identical content | Compare before editing |
| `BadRequest: can't parse entities` | Malformed Markdown/HTML | Wrap `parse_mode` sends in try/except; use `telegram.helpers.escape_markdown` |
| `RetryAfter` | Rate limit hit | Respect `retry_after` value from exception |

### Network Debugging

Test raw API calls with `curl` to isolate whether the problem is your code or the
network:

```bash
# Verify token works
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Check pending updates
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates?offset=-1"

# Inspect webhook status
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

### Using the Python Debugger

Drop into `pdb` or `breakpoint()` during local development:

```python
async def suspicious_handler(update, context) -> None:
    breakpoint()  # Drops into pdb when hit
    result = some_complex_logic(update.message.text)
    await update.message.reply_text(result)
```

> **Never** leave `breakpoint()` calls in code that runs in production.

---

## Checklist Before Deploying

- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] No `DEBUG`-level logging in production config
- [ ] Token stored in environment variable, not hardcoded
- [ ] Error handlers registered for `TelegramError` and unhandled exceptions
- [ ] Webhook URL verified (`getWebhookInfo` shows no pending updates)
- [ ] Rate-limit handling in place for high-traffic commands
