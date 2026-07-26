# Deployment Skill

## Overview
This skill provides deployment guidance for Telegram bots.

## When to Use
- Deploying bots to production
- Setting up webhooks
- Containerizing applications
- Configuring CI/CD

## Deployment Options

### 1. Polling (Development)
```python
application.run_polling(drop_pending_updates=True)
```

### 2. Webhook (Production)
```python
from aiohttp import web

async def webhook_handler(request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return web.Response()

app = web.Application()
app.router.add_post("/webhook", webhook_handler)
web.run_app(app, host="0.0.0.0", port=8443)
```

### 3. Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

### 4. Docker Compose
```yaml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    restart: unless-stopped
    depends_on:
      - redis
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Best Practices
1. Use environment variables
2. Implement health checks
3. Add logging
4. Use process managers (systemd, supervisor)
5. Monitor resource usage
6. Set up alerts

## References
- [Deployment Chapter](../docs/15-deployment.md)
