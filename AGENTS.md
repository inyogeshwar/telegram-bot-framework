# Telegram Bot Framework — AI Agent Instructions

## Repository Purpose
This repository is a comprehensive developer handbook for building Telegram bots with Python using the `python-telegram-bot` library (v20+/v21.x). It contains documentation, examples, and AI agent configurations.

## Key Files
- `docs/` — 21-chapter developer handbook
- `examples/` — Production-quality bot examples
- `pyproject.toml` — Python project metadata
- `requirements.txt` — Dependencies
- `.env.example` — Environment variable template

## Code Standards
- Always use `python-telegram-bot` v20+ (async/await patterns)
- Use PEP 484 type hints throughout
- Include error handling and logging
- Follow PEP 8 style guidelines
- Use `ApplicationBuilder` pattern, not deprecated `Updater`

## Common Patterns
```python
# Application setup
application = ApplicationBuilder().token(token).build()

# Handler registration
application.add_handler(CommandHandler("start", start))

# Running
application.run_polling(drop_pending_updates=True)
```

## Security Rules
- Never hardcode tokens or secrets
- Use environment variables for configuration
- Validate all user input
- Implement rate limiting
- Follow OWASP guidelines

## Documentation Style
- Use Markdown format
- Include code examples with type hints
- Provide both simple and advanced examples
- Reference official PTB documentation
