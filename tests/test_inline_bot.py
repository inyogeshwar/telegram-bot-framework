"""Tests for inline_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from examples.inline_bot import inline_query


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    return MagicMock()


@pytest.mark.asyncio
async def test_inline_query_with_results(mock_context: MagicMock) -> None:
    """Test inline query returns matching results."""
    update = MagicMock()
    update.inline_query.query = "hello"
    update.inline_query.answer = AsyncMock()
    await inline_query(update, mock_context)
    update.inline_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_inline_query_empty(mock_context: MagicMock) -> None:
    """Test empty inline query returns default result."""
    update = MagicMock()
    update.inline_query.query = ""
    update.inline_query.answer = AsyncMock()
    await inline_query(update, mock_context)
    update.inline_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_inline_query_no_match(mock_context: MagicMock) -> None:
    """Test inline query with no matches returns no results message."""
    update = MagicMock()
    update.inline_query.query = "xyznonexistent"
    update.inline_query.answer = AsyncMock()
    await inline_query(update, mock_context)
    update.inline_query.answer.assert_called_once()
