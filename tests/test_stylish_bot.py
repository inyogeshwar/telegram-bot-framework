"""Tests for stylish_bot example."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from examples.stylish_bot import (
    convert_to_font,
    font_callback,
    get_all_fonts_preview,
    handle_text,
    send_sticker_example,
    show_fonts,
    start,
)


class TestConvertToFont:
    """Test font conversion functions."""

    def test_bold_conversion(self) -> None:
        """Test bold font conversion."""
        result = convert_to_font("ABC", "Bold")
        assert result == "𝐀𝐁𝐂"

    def test_italic_conversion(self) -> None:
        """Test italic font conversion."""
        result = convert_to_font("ABC", "Italic")
        assert result == "𝐴𝐵𝐶"

    def test_script_conversion(self) -> None:
        """Test script font conversion."""
        result = convert_to_font("ABC", "Script")
        assert result == "𝒜ℬ𝒞"

    def test_double_struck_conversion(self) -> None:
        """Test double-struck font conversion."""
        result = convert_to_font("ABC", "Double-Struck")
        assert result == "𝔸𝔹ℂ"

    def test_fraktur_conversion(self) -> None:
        """Test Fraktur font conversion."""
        result = convert_to_font("ABC", "Fraktur")
        assert result == "𝔄𝔅ℭ"

    def test_monospaced_conversion(self) -> None:
        """Test monospaced font conversion."""
        result = convert_to_font("ABC", "Monospaced")
        assert result == "𝙰𝙱𝙲"

    def test_unknown_font_returns_original(self) -> None:
        """Test unknown font returns original text."""
        result = convert_to_font("Hello", "NonExistent")
        assert result == "Hello"

    def test_mixed_case(self) -> None:
        """Test mixed case conversion."""
        result = convert_to_font("AbC", "Bold")
        assert result == "𝐀𝐛𝐂"

    def test_numbers_preserved(self) -> None:
        """Test that numbers are preserved (not in font map)."""
        result = convert_to_font("123", "Bold")
        assert result == "123"

    def test_special_chars_preserved(self) -> None:
        """Test that special characters are preserved."""
        result = convert_to_font("Hello!", "Bold")
        assert result == "𝐇𝐞𝐥𝐥𝐨!"


class TestGetAllFontsPreview:
    """Test font preview generation."""

    def test_preview_contains_all_fonts(self) -> None:
        """Test preview includes all font names."""
        preview = get_all_fonts_preview("Test")
        assert "Bold:" in preview
        assert "Italic:" in preview
        assert "Script:" in preview
        assert "Double-Struck:" in preview
        assert "Fraktur:" in preview
        assert "Monospaced:" in preview

    def test_preview_contains_original(self) -> None:
        """Test preview includes original text."""
        preview = get_all_fonts_preview("Hello")
        assert "Original: Hello" in preview


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.message.text = "Hello"
    update.message.reply_text = AsyncMock(return_value=None)
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    return MagicMock()


@pytest.mark.asyncio
async def test_start_replies(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /start command sends welcome message."""
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_show_fonts(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /fonts command shows all fonts."""
    await show_fonts(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_convert_text(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """Test /convert command converts text."""
    mock_context.args = ["Bold", "Hello"]
    await send_sticker_example(mock_update, mock_context)
    # Should reply with sticker instructions
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_handle_text_shows_keyboard(
    mock_update: MagicMock, mock_context: MagicMock
) -> None:
    """Test plain text shows font selection keyboard."""
    await handle_text(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_font_callback(mock_context: MagicMock) -> None:
    """Test font callback selects font."""
    query = MagicMock()
    query.data = "font:Bold:Hello World"
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    update = MagicMock()
    update.callback_query = query

    await font_callback(update, mock_context)
    query.answer.assert_called_once()
    query.edit_message_text.assert_called_once()
