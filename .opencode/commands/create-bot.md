---
description: Create new Telegram bot
agent: telegram-bot-creator
subtask: true
---

Create a new Telegram bot named $ARGUMENTS.

Bot requirements:
1. Async/await patterns with python-telegram-bot v20+
2. Type hints on all functions
3. Error handling with logging
4. Environment variable configuration
5. README with setup instructions

Generate:
1. `bot_name/bot.py` - Main bot file
2. `bot_name/config.py` - Configuration module
3. `bot_name/requirements.txt` - Dependencies
4. `bot_name/.env.example` - Environment template
5. `bot_name/README.md` - Documentation

Include common handlers:
- /start - Welcome message
- /help - Help information
- Echo handler for demonstration
