"""Tests for echo_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from examples.echo_bot import echo, error_handler, help_command, start


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message.text = "Hello"
    update.message.reply_html = AsyncMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.mention_html.return_value = "TestUser"
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    return MagicMock()


@pytest.mark.asyncio
async def test_start_replies(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /start command sends welcome message."""
    await start(mock_update, mock_context)
    mock_update.message.reply_html.assert_called_once()


@pytest.mark.asyncio
async def test_help_replies(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /help command sends help text."""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_echo_replies_with_text(
    mock_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test echo handler replies with the same text."""
    await echo(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Hello")


@pytest.mark.asyncio
async def test_echo_ignores_no_message(mock_context: MagicMock) -> None:
    """Test echo handler does nothing when message is None."""
    update = MagicMock()
    update.message = None
    await echo(update, mock_context)
    # Should not raise


@pytest.mark.asyncio
async def test_echo_ignores_no_text(mock_context: MagicMock) -> None:
    """Test echo handler does nothing when text is None."""
    update = MagicMock()
    update.message.text = None
    await echo(update, mock_context)
    # Should not raise


@pytest.mark.asyncio
async def test_error_handler_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Test error handler logs the exception."""
    context = MagicMock()
    context.error = ValueError("test error")
    await error_handler(MagicMock(), context)
    assert "test error" in caplog.text
