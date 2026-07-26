# Examples

Production-quality Telegram bot examples using python-telegram-bot v20+.

## Available Examples

| Example | Description | Difficulty |
|---------|-------------|------------|
| `echo_bot.py` | Minimal echo bot | Beginner |
| `ai_chatbot.py` | AI-powered chatbot with OpenAI | Intermediate |
| `admin_bot.py` | Group admin and moderation | Intermediate |
| `payment_bot.py` | Telegram Stars payments | Intermediate |
| `conversation_bot.py` | Multi-step dialogs | Intermediate |
| `webhook_bot.py` | Webhook deployment | Advanced |
| `inline_bot.py` | Inline query mode | Intermediate |
| `scheduled_bot.py` | JobQueue and reminders | Intermediate |

## Running Examples

```bash
# 1. Set your bot token
export BOT_TOKEN="your_token_here"

# 2. Run an example
python examples/echo_bot.py
```

Or use the `.env` file:

```bash
# 1. Copy .env.example
cp .env.example .env

# 2. Edit .env with your token

# 3. Run
python examples/echo_bot.py
```

## Example Structure

Each example follows these standards:

- **Async/await** — v20+ patterns
- **Type hints** — PEP 484 compliant
- **Error handling** — try/except with logging
- **Logging** — Python logging module
- **Comments** — Docstrings and inline where needed
- **Modular** — Clean, readable code

## Adding New Examples

1. Use the template in `templates/bot-template.py`
2. Follow the coding standards
3. Add a docstring with usage instructions
4. Include error handling
5. Test thoroughly
6. Update this README
