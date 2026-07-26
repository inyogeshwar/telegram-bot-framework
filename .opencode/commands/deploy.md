---
description: Deploy bot with Docker
agent: build
---

Generate Docker configuration for the Telegram bot.

Create:
1. `Dockerfile` - Multi-stage build
2. `docker-compose.yml` - Service configuration
3. `.dockerignore` - Build exclusions

Include:
- Non-root user
- Health check
- Resource limits
- Logging configuration
- Environment variable support

Show deployment commands:
```bash
# Build
docker build -t telegram-bot .

# Run
docker run -d --name telegram-bot -e BOT_TOKEN=$BOT_TOKEN telegram-bot

# Docker Compose
docker-compose up -d
```
