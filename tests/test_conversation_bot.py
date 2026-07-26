"""Tests for conversation_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from examples.conversation_bot import (
    NAME,
    age,
    cancel,
    location,
    name,
    start_registration,
    timeout,
)


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message.text = "Test"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    context = MagicMock()
    context.user_data = {}
    return context


@pytest.mark.asyncio
async def test_start_registration(
    mock_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test /register starts conversation."""
    result = await start_registration(mock_update, mock_context)
    assert result == NAME
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_name_handler(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test name handler stores name and asks for age."""
    result = await name(mock_update, mock_context)
    assert result == 1  # AGE state
    assert mock_context.user_data["name"] == "Test"


@pytest.mark.asyncio
async def test_age_handler_valid(mock_context: MagicMock) -> None:
    """Test age handler with valid age."""
    update = MagicMock()
    update.message.text = "25"
    update.message.reply_text = AsyncMock()
    result = await age(update, mock_context)
    assert result == 2  # LOCATION state
    assert mock_context.user_data["age"] == 25


@pytest.mark.asyncio
async def test_age_handler_invalid(mock_context: MagicMock) -> None:
    """Test age handler with invalid age."""
    update = MagicMock()
    update.message.text = "abc"
    update.message.reply_text = AsyncMock()
    result = await age(update, mock_context)
    assert result == 1  # Back to NAME state (wait, actually AGE)
    assert "age" not in mock_context.user_data


@pytest.mark.asyncio
async def test_age_handler_out_of_range(mock_context: MagicMock) -> None:
    """Test age handler with out of range age."""
    update = MagicMock()
    update.message.text = "200"
    update.message.reply_text = AsyncMock()
    result = await age(update, mock_context)
    assert result == 1  # Back to AGE state


@pytest.mark.asyncio
async def test_location_handler(mock_context: MagicMock) -> None:
    """Test location handler completes registration."""
    update = MagicMock()
    update.message.text = "New York, USA"
    update.message.reply_text = AsyncMock()
    mock_context.user_data = {"name": "John", "age": 25}
    result = await location(update, mock_context)
    assert result == -1  # ConversationHandler.END
    assert mock_context.user_data["location"] == "New York, USA"


@pytest.mark.asyncio
async def test_cancel(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test cancel returns END."""
    result = await cancel(mock_update, mock_context)
    assert result == -1  # ConversationHandler.END


@pytest.mark.asyncio
async def test_timeout(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test timeout returns END."""
    result = await timeout(mock_update, mock_context)
    assert result == -1  # ConversationHandler.END
