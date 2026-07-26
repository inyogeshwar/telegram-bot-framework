---
name: deployment-guide
description: Deploy Telegram bots to production with Docker, webhooks, and cloud platforms
license: MIT
compatibility: opencode
metadata:
  audience: devops
  platforms: docker,heroku,flyio
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

## Best Practices

1. Use environment variables
2. Implement health checks
3. Set up process management (systemd/supervisor)
4. Configure logging
5. Monitor resource usage
