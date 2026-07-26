"""Tests for feature_matrix_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import InlineKeyboardMarkup

from examples.feature_matrix_bot import (
    category_callback,
    feat_check_premium,
    feat_html,
    feat_invoice,
    feat_keyboard,
    feat_location,
    feat_markdown,
    feat_photo,
    feat_poll,
    feat_quiz,
    help_command,
    start,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.chat_id = 100
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    ctx = MagicMock()
    ctx.bot.send_message = AsyncMock()
    ctx.bot.send_photo = AsyncMock()
    ctx.bot.send_poll = AsyncMock()
    ctx.bot.send_location = AsyncMock()
    ctx.bot.send_invoice = AsyncMock()
    ctx.bot.send_dice = AsyncMock()
    ctx.bot.send_animation = AsyncMock()
    ctx.bot.send_video = AsyncMock()
    ctx.bot.send_voice = AsyncMock()
    ctx.bot.send_document = AsyncMock()
    ctx.bot.send_audio = AsyncMock()
    ctx.bot.send_sticker = AsyncMock()
    ctx.bot.send_contact = AsyncMock()
    ctx.bot.edit_message_text = AsyncMock()
    ctx.bot.pin_chat_message = AsyncMock()
    ctx.bot.set_message_reaction = AsyncMock()
    ctx.bot.set_chat_menu_button = AsyncMock()
    return ctx


@pytest.fixture
def mock_query() -> MagicMock:
    """Create a mock CallbackQuery object."""
    query = MagicMock()
    query.data = "cat_messages"
    query.message.chat_id = 100
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    return query


@pytest.fixture
def callback_update(mock_query: MagicMock) -> MagicMock:
    """Create a mock Update with a callback_query."""
    update = MagicMock()
    update.callback_query = mock_query
    return update


# ---------------------------------------------------------------------------
# 1. start handler
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_start_sends_welcome_with_keyboard(
    mock_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test /start sends welcome text with inline keyboard."""
    mock_update.effective_user.first_name = "Alice"
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    args, kwargs = mock_update.message.reply_text.call_args
    assert "Alice" in args[0]
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_start_returns_on_no_message(mock_context: MagicMock) -> None:
    """Test /start returns early when update.message is None."""
    update = MagicMock()
    update.message = None
    await start(update, mock_context)
    # Should not raise; just return


# ---------------------------------------------------------------------------
# 2. help_command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_help_sends_help_text(
    mock_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test /help sends help text."""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    text = mock_update.message.reply_text.call_args[0][0]
    assert "Help" in text


@pytest.mark.asyncio
async def test_help_returns_on_no_message(mock_context: MagicMock) -> None:
    """Test /help returns early when update.message is None."""
    update = MagicMock()
    update.message = None
    await help_command(update, mock_context)


# ---------------------------------------------------------------------------
# 3. category_callback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_category_callback_routes_to_category(
    callback_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test callback routes to the correct category menu."""
    callback_update.callback_query.data = "cat_media"
    await category_callback(callback_update, mock_context)
    callback_update.callback_query.edit_message_text.assert_called_once()
    args = callback_update.callback_query.edit_message_text.call_args[0]
    assert "Media" in args[0]


@pytest.mark.asyncio
async def test_category_callback_back_main(
    callback_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test back_main callback returns to main menu."""
    callback_update.callback_query.data = "back_main"
    await category_callback(callback_update, mock_context)
    callback_update.callback_query.edit_message_text.assert_called_once()
    args = callback_update.callback_query.edit_message_text.call_args[0]
    assert "Pick a category" in args[0]


@pytest.mark.asyncio
async def test_category_callback_no_query(mock_context: MagicMock) -> None:
    """Test callback returns early when query is None."""
    update = MagicMock()
    update.callback_query = None
    await category_callback(update, mock_context)


@pytest.mark.asyncio
async def test_category_callback_unknown_feat(
    callback_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test unknown feat callback answers with alert."""
    callback_update.callback_query.data = "feat_nonexistent"
    await category_callback(callback_update, mock_context)
    callback_update.callback_query.answer.assert_called_with(
        "Unknown feature.", show_alert=True
    )


# ---------------------------------------------------------------------------
# 4. feat_markdown
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_markdown(mock_context: MagicMock) -> None:
    """Test feat_markdown sends MarkdownV2 formatted message."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_markdown(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_message.assert_called_once()
    kwargs = mock_context.bot.send_message.call_args[1]
    assert kwargs["parse_mode"] == "MarkdownV2"


# ---------------------------------------------------------------------------
# 5. feat_html
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_html(mock_context: MagicMock) -> None:
    """Test feat_html sends HTML formatted message."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_html(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_message.assert_called_once()
    kwargs = mock_context.bot.send_message.call_args[1]
    assert kwargs["parse_mode"] == "HTML"


# ---------------------------------------------------------------------------
# 6. feat_photo
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_photo(mock_context: MagicMock) -> None:
    """Test feat_photo sends a photo from URL."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_photo(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_photo.assert_called_once()
    kwargs = mock_context.bot.send_photo.call_args[1]
    assert kwargs["photo"].startswith("https://")
    assert "Photo" in kwargs["caption"]


# ---------------------------------------------------------------------------
# 7. feat_poll
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_poll(mock_context: MagicMock) -> None:
    """Test feat_poll sends a poll with options."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_poll(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_poll.assert_called_once()
    kwargs = mock_context.bot.send_poll.call_args[1]
    assert "framework" in kwargs["question"]
    assert len(kwargs["options"]) == 4


# ---------------------------------------------------------------------------
# 8. feat_quiz
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_quiz(mock_context: MagicMock) -> None:
    """Test feat_quiz sends a quiz with correct_option_id."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_quiz(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_poll.assert_called_once()
    kwargs = mock_context.bot.send_poll.call_args[1]
    assert kwargs["type"] == "quiz"
    assert kwargs["correct_option_id"] == 0


# ---------------------------------------------------------------------------
# 9. feat_keyboard
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_keyboard(mock_context: MagicMock) -> None:
    """Test feat_keyboard sends inline keyboard."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_keyboard(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_message.assert_called_once()
    kwargs = mock_context.bot.send_message.call_args[1]
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


# ---------------------------------------------------------------------------
# 10. feat_location
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_location(mock_context: MagicMock) -> None:
    """Test feat_location sends coordinates."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_location(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_location.assert_called_once()
    kwargs = mock_context.bot.send_location.call_args[1]
    assert kwargs["latitude"] == 48.8566
    assert kwargs["longitude"] == 2.3522


# ---------------------------------------------------------------------------
# 11. feat_invoice
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_invoice(mock_context: MagicMock) -> None:
    """Test feat_invoice sends a payment invoice."""
    query = MagicMock()
    query.message.chat_id = 100
    query.answer = AsyncMock()
    await feat_invoice(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_invoice.assert_called_once()
    kwargs = mock_context.bot.send_invoice.call_args[1]
    assert kwargs["currency"] == "XTR"
    assert "Premium" in kwargs["title"]


# ---------------------------------------------------------------------------
# 12. feat_check_premium
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_feat_check_premium_not_premium(
    mock_context: MagicMock,
) -> None:
    """Test feat_check_premium reports non-premium user."""
    query = MagicMock()
    query.message.chat_id = 100
    query.from_user.is_premium = False
    query.answer = AsyncMock()
    await feat_check_premium(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_message.assert_called_once()
    text = mock_context.bot.send_message.call_args[1]["text"]
    assert "No" in text


@pytest.mark.asyncio
async def test_feat_check_premium_is_premium(
    mock_context: MagicMock,
) -> None:
    """Test feat_check_premium reports premium user."""
    query = MagicMock()
    query.message.chat_id = 100
    query.from_user.is_premium = True
    query.answer = AsyncMock()
    await feat_check_premium(query, mock_context)
    query.answer.assert_called_once()
    mock_context.bot.send_message.assert_called_once()
    text = mock_context.bot.send_message.call_args[1]["text"]
    assert "Yes" in text
