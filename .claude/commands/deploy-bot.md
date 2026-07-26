# Deploy Bot

Sets up deployment configuration for a Telegram bot.

## Instructions

1. Ask user for deployment type:
   - Polling (development/simple production)
   - Webhook (production with HTTPS)

2. Generate deployment files based on type:

### Polling Deployment
```python
# In bot.py
def main() -> None:
    """Start the bot with polling."""
    application = Application.builder().token(BOT_TOKEN).build()
    # ... add handlers ...
    application.run_polling(drop_pending_updates=True)
```

### Webhook Deployment
```python
# webhook.py
import logging
from os import getenv

from flask import Flask, request
from telegram import Update
from telegram.ext import Application

app = Flask(__name__)

WEBHOOK_URL = getenv("WEBHOOK_URL")
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
BOT_TOKEN = getenv("BOT_TOKEN")

application = Application.builder().token(BOT_TOKEN).build()
# ... add handlers ...


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle webhook updates."""
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return "Unauthorized", 401

    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"


@app.route("/health")
def health():
    """Health check endpoint."""
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

3. Generate Docker files:

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### docker-compose.yml
```yaml
version: "3.8"

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

4. Generate deployment documentation:
   - Environment variables needed
   - Setup instructions
   - Monitoring guidance
   - Scaling considerations

## Security Requirements
- Use environment variables for secrets
- Implement webhook secret validation
- Use HTTPS for webhooks
- Enable health checks
- Configure proper logging

## Resources
- Reference: docs/17-deployment.md
- Examples: examples/webhook_bot.py
