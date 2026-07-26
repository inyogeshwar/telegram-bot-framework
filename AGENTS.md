# Telegram Bot Framework — AI Agent Instructions

## Repository Purpose

This repository is a comprehensive developer handbook for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x). It contains documentation, examples, and AI agent configurations.

## Project Structure

```
├── docs/                    # 22-chapter developer handbook
├── examples/                # 8 production-quality bot examples
├── templates/               # Bot templates (echo, conversation, webhook)
├── .opencode/               # OpenCode configuration
├── .claude/                 # Claude Code configuration
├── .cursor/                 # Cursor configuration
├── .gemini/                 # Gemini CLI configuration
├── pyproject.toml           # Python project metadata
├── requirements.txt         # Dependencies
├── requirements-all.txt     # All optional dependencies
├── .env.example             # Environment variable template
├── README.md                # Project documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md              # Security policy
├── CHANGELOG.md             # Version history
└── AI.md                    # AI agent quick reference
```

## Build, Lint, and Test Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-all.txt  # Optional: all features

# Linting
ruff check .                    # Check for linting errors
ruff format .                   # Auto-format code
ruff format --check .           # Check formatting without changes

# Type checking
mypy .                          # Run mypy type checker

# Testing
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=.                  # With coverage
pytest tests/test_specific.py   # Run specific test file
```

## Code Standards

### Python Style
- **Formatter**: Ruff (line length: 88)
- **Linter**: Ruff with rules: E, F, W, I, N, UP, B, A, SIM
- **Type Checker**: MyPy (strict mode)
- **Async**: Always use async/await patterns (v20+)

### Code Patterns
```python
# Application setup
from telegram.ext import ApplicationBuilder

application = ApplicationBuilder().token(token).build()

# Handler registration
from telegram.ext import CommandHandler, MessageHandler, filters

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT, handle_message))

# Running
application.run_polling(drop_pending_updates=True)
```

### Type Hints
```python
from telegram import Update
from telegram.ext import ContextTypes


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response")
```

### Error Handling
```python
import logging

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
```

## Project-Specific Conventions

### File Naming
- Bot files: `bot_name_bot.py` (e.g., `echo_bot.py`)
- Test files: `test_<module>.py`
- Example files: Descriptive names with `_bot.py` suffix

### Handler Registration Order
1. Command handlers
2. Callback query handlers
3. Message handlers
4. Error handler (last)

### Configuration Management
- Use `python-dotenv` for `.env` files
- Create `Config` dataclass for type-safe configuration
- Validate configuration on startup

## Security Rules

- **Never hardcode tokens** — Use environment variables
- **Validate input** — Sanitize all user input
- **Rate limiting** — Implement per-user/chat limits
- **Webhook validation** — Verify Telegram signatures
- **Error messages** — Don't leak sensitive information

## Common Gotchas

1. **Blocking calls**: Never use blocking calls in async handlers
2. **Memory leaks**: Properly close database connections
3. **Handler order**: Register specific handlers before general ones
4. **Update processing**: Use `drop_pending_updates=True` in production
5. **Type hints**: Always use `ContextTypes.DEFAULT_TYPE` not `Context`

## Documentation Style

- Use Markdown format
- Include code examples with type hints
- Provide both simple and advanced examples
- Reference official PTB documentation
- Keep examples runnable and complete

## External References

For more detailed guidance, see:
- `docs/COMPREHENSIVE-REFERENCE.md` — 1921-line functions reference
- `docs/` directory — 22-chapter developer handbook
- `examples/` directory — Production-quality bot examples

## AI Agent Behavior

When working on this repository:

1. **Always use async/await** — Never use synchronous patterns
2. **Include type hints** — PEP 484 on all functions
3. **Add error handling** — Try/except with logging
4. **Follow PEP 8** — Use ruff for formatting
5. **Test changes** — Run pytest before committing
6. **Update documentation** — Keep docs in sync with code
