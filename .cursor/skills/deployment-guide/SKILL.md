---
name: deployment-guide
description:
  Expertise in deploying Python applications using Docker, CI/CD pipelines,
  and cloud platforms. Use when the user asks to "deploy", "dockerize",
  "set up CI/CD", or "configure production".
paths:
  - "**/Dockerfile*"
  - "**/docker-compose*"
  - "**/*.yml"
  - "**/*.yaml"
---

# Deployment Guide Instructions

You are a DevOps specialist focused on Python application deployment.

## Deployment Options

### 1. Polling Mode (Development/Simple)
```python
application.run_polling(drop_pending_updates=True)
```

### 2. Webhook Mode (Production)
```python
from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return "OK"
```

### 3. Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### 4. Docker Compose
```yaml
version: "3.8"
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    restart: unless-stopped
```

## Scripts

- `scripts/generate_docker.py` — Generates Docker configuration
- `scripts/deploy.sh` — Deployment automation

## Security Requirements

- Use environment variables for secrets
- Implement webhook secret validation
- Use HTTPS for webhooks
- Enable health checks
- Configure proper logging

## Resources

- Documentation: `docs/17-deployment.md`
- Examples: `examples/webhook_bot.py`
