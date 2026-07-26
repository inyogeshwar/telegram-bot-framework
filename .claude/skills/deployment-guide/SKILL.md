---
description: Deploy Telegram bots to production with Docker, webhooks, and cloud platforms. Use when setting up deployment, CI/CD, or infrastructure.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash(git *)
---

## What I do

- Guide bot deployment using polling or webhooks
- Provide Docker and docker-compose configurations
- Cover cloud platform deployment (Heroku, Fly.io, Railway)
- Include systemd service configuration for VPS

## When to use me

Use this skill when deploying bots to production, setting up CI/CD, or configuring infrastructure.

## Deployment Options

### Polling (Development)
```python
application.run_polling(drop_pending_updates=True)
```

### Webhook (Production)
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

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### Docker Compose
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

### Systemd Service
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/opt/bot
ExecStart=/opt/bot/venv/bin/python bot.py
Restart=always
RestartSec=10
Environment=BOT_TOKEN=your_token

[Install]
WantedBy=multi-user.target
```

## Best Practices

1. Use environment variables
2. Implement health checks
3. Set up process management (systemd/supervisor)
4. Configure logging
5. Monitor resource usage
6. Use Docker for consistency
7. Set up CI/CD pipeline

## References

- See `docs/15-deployment.md` for complete deployment guide
- See `docs/16-security-audit.md` for security in deployment
