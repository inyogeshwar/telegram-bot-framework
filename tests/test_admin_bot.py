"""Tests for admin_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from examples.admin_bot import (
    ban_user,
    delete_message,
    help_command,
    mute_user,
    start,
    unban_user,
    unmute_user,
    welcome,
)


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_to_message.from_user.id = 12345
    update.message.reply_to_message.from_user.mention_html.return_value = "User"
    update.message.chat.ban_member = AsyncMock()
    update.message.chat.unban_member = AsyncMock()
    update.message.chat.restrict_member = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    return MagicMock()


@pytest.mark.asyncio
async def test_start_replies(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /start command sends help text."""
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_help_replies(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /help command sends help text."""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_ban_user_requires_reply(mock_context: MagicMock) -> None:
    """Test ban requires reply to message."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()
    await ban_user(update, mock_context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_unban_user_requires_reply(mock_context: MagicMock) -> None:
    """Test unban requires reply to message."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()
    await unban_user(update, mock_context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_mute_user_requires_reply(mock_context: MagicMock) -> None:
    """Test mute requires reply to message."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()
    await mute_user(update, mock_context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_unmute_user_requires_reply(mock_context: MagicMock) -> None:
    """Test unmute requires reply to message."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()
    await unmute_user(update, mock_context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_delete_requires_reply(mock_context: MagicMock) -> None:
    """Test delete requires reply to message."""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()
    await delete_message(update, mock_context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_welcome_ignores_bots(mock_context: MagicMock) -> None:
    """Test welcome ignores bot members."""
    update = MagicMock()
    user = MagicMock()
    user.is_bot = True
    update.message.new_chat_members = [user]
    await welcome(update, mock_context)
    update.message.reply_text.assert_not_called()
