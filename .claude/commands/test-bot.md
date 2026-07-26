# Test Bot

Generates comprehensive tests for a Telegram bot.

## Instructions

1. Analyze bot.py to identify:
   - All handler functions
   - Database interactions (if any)
   - External API calls
   - Configuration loading

2. Generate test file with:
   - pytest fixtures for bot setup
   - Mock objects for Update and Context
   - Unit tests for each handler
   - Integration tests for handler chains
   - Error handling tests

3. Create test configuration:
   - conftest.py with shared fixtures
   - pytest.ini or pyproject.toml configuration

## Test Structure

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes

from bot import start, help_command, echo


@pytest.fixture
def update():
    """Create mock update."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.text = "Test message"
    update.message.from_user = MagicMock(spec=User)
    update.message.from_user.id = 12345
    return update


@pytest.fixture
def context():
    """Create mock context."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_start(update, context):
    """Test /start command."""
    await start(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_help(update, context):
    """Test /help command."""
    await help_command(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_echo(update, context):
    """Test echo handler."""
    update.message.text = "Hello"
    await echo(update, context)
    update.message.reply_text.assert_called_with("Hello")


@pytest.mark.asyncio
async def test_error_handler(update, context):
    """Test error handling."""
    context.error = Exception("Test error")
    # Test error handler implementation
```

## Test Categories
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test handler chains
- **Error Tests**: Test error handling
- **Performance Tests**: Test response times (optional)

## Coverage Requirements
- 80%+ for business logic
- 100% for security-critical code
- All handler functions tested
- Error paths covered

## Resources
- Reference: .claude/rules/testing.md
- Examples: tests/ directory structure
