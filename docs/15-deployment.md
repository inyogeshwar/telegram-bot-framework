# Chapter 15: Deployment & Hosting

This chapter covers everything you need to take your Telegram bot from local development to a production environment. You will learn when to use polling versus webhooks, how to deploy with Docker, configure CI/CD pipelines, manage secrets, scale horizontally, and monitor your bot in production.

---

## Table of Contents

- [Development vs Production](#development-vs-production)
- [Webhook Setup](#webhook-setup)
- [Deployment Options](#deployment-options)
- [CI/CD](#cicd)
- [Environment Variables in Production](#environment-variables-in-production)
- [Scaling](#scaling)
- [Monitoring & Observability](#monitoring--observability)
- [systemd Service Example](#systemd-service-example)

---

## Development vs Production

The two primary update delivery methods are **polling** and **webhooks**. Each is suited to different environments.

```mermaid
flowchart LR
    A[Bot Process] -->|polls| B[Telegram API]
    B -->|returns updates| A
    C[Telegram API] -->|pushes updates| D[Your Webhook Endpoint]
    D -->|processes & responds| C

    style A fill:#e8f5e9,stroke:#388e3c
    style B fill:#e3f2fd,stroke:#1565c0
    style C fill:#e3f2fd,stroke:#1565c0
    style D fill:#fff3e0,stroke:#e65100
```

| Feature | Polling | Webhooks |
|---------|---------|----------|
| Setup complexity | Low | Medium |
| Public URL required | No | Yes (HTTPS) |
| Latency | ~1-2 seconds | Near-instant |
| Resource usage | Higher (constant requests) | Lower (event-driven) |
| Best for | Development, local testing | Production, high-traffic bots |
| Network requirements | Outbound only | Inbound port exposed |

> **Rule of thumb:** Use polling during development and webhooks in production.

---

## Webhook Setup

### Using `python-telegram-bot`'s Built-in Webhook

The `python-telegram-bot` library provides a first-class webhook runner with TLS support:

```python
import logging
import os
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # e.g. https://yourdomain.com/webhook


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text("Bot is running via webhook!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo received messages."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot with webhook."""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
        cert=Path("cert.pem"),
        key=Path("private.key"),
        secret_token=os.environ.get("WEBHOOK_SECRET", "my-secret-token"),
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
```

### Manual Webhook Setup

You can manage webhooks manually via the Bot API and integrate with any HTTP framework.

#### Setting a Webhook

```python
import os
import logging
import httpx

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
SECRET_TOKEN = os.environ["WEBHOOK_SECRET"]


async def set_webhook() -> None:
    """Register the webhook with Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "url": f"{WEBHOOK_URL}/webhook",
                "secret_token": SECRET_TOKEN,
                "allowed_updates": ["message", "callback_query", "my_chat_member"],
                "max_connections": 40,
                "drop_pending_updates": True,
            },
        )
        result = response.json()

        if result.get("ok"):
            logger.info("Webhook set successfully: %s", result["description"])
        else:
            logger.error("Failed to set webhook: %s", result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(set_webhook())
```

#### Flask Integration

```python
import os
import logging

import httpx
from flask import Flask, Request, abort, jsonify

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

flask_app = Flask(__name__)

application = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello from Flask webhook!")


application.add_handler(CommandHandler("start", start))


@flask_app.post("/webhook")
def webhook() -> tuple[str, int]:
    """Handle incoming Telegram updates."""
    header_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if header_token != WEBHOOK_SECRET:
        abort(403)

    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
    except Exception as e:
        logger.error("Failed to process update: %s", e)
        return jsonify({"error": "internal error"}), 500

    return jsonify({"status": "ok"}), 200
```

#### FastAPI Integration

```python
import os
import logging
import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

application = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello from FastAPI webhook!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI app."""
    await application.initialize()
    await application.start()
    yield
    await application.stop()
    await application.shutdown()


fastapi_app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)


@fastapi_app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> dict:
    """Handle incoming Telegram updates."""
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, application.bot)

    await application.process_update(update)
    return {"status": "ok"}


@fastapi_app.get("/health")
async def health() -> dict:
    """Health check endpoint for load balancers."""
    return {"status": "healthy"}
```

### Verifying Webhook Requests

Always verify that incoming requests actually come from Telegram. The `secret_token` parameter is the primary defense:

```python
import hmac


def verify_telegram_request(
    body: bytes,
    secret_token: str,
    header_token: str | None,
) -> bool:
    """Verify the webhook request is from Telegram."""
    if not header_token:
        return False

    return hmac.compare_digest(header_token, secret_token)
```

### Supported Ports

Telegram supports the following ports for webhook connections:

| Port | Protocol | Notes |
|------|----------|-------|
| **443** | HTTPS | Recommended for production |
| **80** | HTTP | Not recommended; no encryption |
| **88** | HTTPS | Alternative if 443 is unavailable |
| **8443** | HTTPS | Common for development/testing |

> **Important:** Port 443 is strongly recommended for production. Use a reverse proxy (Nginx, Caddy) to terminate TLS and forward to your application.

---

## Deployment Options

### Docker (Recommended)

Docker provides consistent, reproducible deployments across any environment.

#### Dockerfile

```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser
RUN mkdir -p /app/data && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

CMD ["python", "bot.py"]
```

#### docker-compose.yml

```yaml
version: "3.9"

services:
  bot:
    build: .
    container_name: telegram-bot
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://bot:secret@postgres:5432/botdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - bot-data:/app/data
    ports:
      - "8443:8443"
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    image: postgres:16-alpine
    container_name: bot-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: botdb
      POSTGRES_USER: bot
      POSTGRES_PASSWORD: secret
    volumes:
      - pg-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bot -d botdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: bot-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  bot-data:
  pg-data:
  redis-data:
```

### Heroku

Heroku offers one-click deployment with automatic scaling.

#### Procfile

```
worker: python bot.py
```

For webhook-based bots:

```
web: uvicorn webhook_app:fastapi_app --host 0.0.0.0 --port $PORT
```

#### Setup Commands

```bash
# Create the app
heroku create my-telegram-bot

# Set environment variables
heroku config:set BOT_TOKEN=your_token_here
heroku config:set WEBHOOK_URL=https://my-telegram-bot.herokuapp.com/webhook
heroku config:set WEBHOOK_SECRET=your_secret_here

# Add a database
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Scale the worker
heroku ps:scale worker=1
```

> **Limitation:** Heroku's free tier was discontinued in November 2022. The Eco tier ($5/month) provides 1000 dyno hours per month.

### Railway

Railway provides a modern deployment experience with automatic GitHub integration.

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Set environment variables
railway variables set BOT_TOKEN=your_token_here
railway variables set WEBHOOK_URL=https://your-app.up.railway.app/webhook

# Deploy
railway up
```

Railway automatically detects Python projects and builds them using the `Dockerfile` or `requirements.txt`.

### Render

Render offers a free tier for background workers, making it ideal for polling-based bots.

#### render.yaml

```yaml
services:
  - type: worker
    name: telegram-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
    autoDeploy: true
```

### AWS Lambda (Serverless)

AWS Lambda with API Gateway provides a serverless deployment option for webhook-based bots.

```python
"""AWS Lambda handler for Telegram bot webhook."""

import os
import json
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

application = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello from Lambda!")


application.add_handler(CommandHandler("start", start))


def lambda_handler(event: dict, context) -> dict:
    """Handle incoming API Gateway events."""
    try:
        if event.get("httpMethod") != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed"}),
            }

        headers = event.get("headers", {})
        secret = headers.get("x-telegram-bot-api-secret-token")
        if secret != WEBHOOK_SECRET:
            return {"statusCode": 403, "body": json.dumps({"error": "Forbidden"})}

        body = json.loads(event.get("body", "{}"))
        update = Update.de_json(body, application.bot)

        import asyncio

        asyncio.run(application.process_update(update))

        return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

    except Exception as e:
        logger.error("Lambda error: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
```

#### SAM Template

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Resources:
  TelegramBotFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: lambda_handler.lambda_handler
      MemorySize: 256
      Timeout: 30
      Environment:
        Variables:
          BOT_TOKEN: !Ref BotToken
          WEBHOOK_SECRET: !Ref WebhookSecret
      Events:
        TelegramWebhook:
          Type: Api
          Properties:
            Path: /webhook
            Method: post

Parameters:
  BotToken:
    Type: String
    NoEcho: true
  WebhookSecret:
    Type: String
    NoEcho: true
```

> **Cold Start Warning:** Lambda functions may experience 1-3 second cold starts. Use provisioned concurrency for latency-sensitive bots.

### VPS (DigitalOcean, Linode, Hetzner)

A VPS gives you full control over the environment.

#### Initial Server Setup

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create a dedicated user
adduser --disabled-password botuser
usermod -aG sudo botuser

# Install Python and dependencies
apt install -y python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx
```

#### Application Setup

```bash
# Switch to bot user
su - botuser

# Clone your repository
git clone https://github.com/you/telegram-bot.git ~/bot
cd ~/bot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > ~/.env << EOF
BOT_TOKEN=your_token_here
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_SECRET=your_secret_here
DATABASE_URL=sqlite:///data/bot.db
EOF
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Telegram-Bot-Api-Secret-Token $http_x_telegram_bot_api_secret_token;
    }

    location /health {
        proxy_pass http://127.0.0.1:8443;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/telegram-bot

gcloud run deploy telegram-bot \
    --image gcr.io/PROJECT_ID/telegram-bot \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "BOT_TOKEN=xxx,WEBHOOK_SECRET=xxx"
```

#### App Engine

```yaml
# app.yaml
runtime: python311
instance_class: F1

env_variables:
  BOT_TOKEN: "your_token_here"
  WEBHOOK_URL: "https://your-project-id.appspot.com/webhook"

handlers:
  - url: /webhook
    script: auto
  - url: /health
    script: auto
```

### Microsoft Azure

#### App Service

```bash
# Create resource group
az group create --name telegram-bot-rg --location eastus

# Create App Service plan
az appservice plan create --name bot-plan --resource-group telegram-bot-rg --sku B1

# Create web app
az webapp create --name my-telegram-bot --resource-group telegram-bot-rg --plan bot-plan

# Configure environment variables
az webapp config appsettings set \
    --name my-telegram-bot \
    --resource-group telegram-bot-rg \
    --settings BOT_TOKEN=xxx WEBHOOK_SECRET=xxx

# Deploy from local
az webapp deployment source config-local-git --name my-telegram-bot --resource-group telegram-bot-rg
git push azure main
```

---

## CI/CD

Automated pipelines ensure every push is tested and deployed consistently.

### GitHub Actions

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linter
        run: ruff check .

      - name: Run type checker
        run: mypy .

      - name: Run tests
        run: pytest --cov=bot tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t telegram-bot:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USER }}" --password-stdin
          docker tag telegram-bot:${{ github.sha }} your-registry/telegram-bot:latest
          docker push your-registry/telegram-bot:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd ~/bot
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

### Environment-Specific Configurations

```yaml
# .github/workflows/deploy-staging.yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        run: |
          docker build -t bot-staging:${{ github.sha }} .
          docker push registry.example.com/bot-staging:${{ github.sha }}

      - name: Update staging server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.STAGING_HOST }}
          script: |
            export IMAGE_TAG=${{ github.sha }}
            docker compose -f docker-compose.staging.yml up -d
```

---

## Environment Variables in Production

### Never Hardcode Secrets

```python
# ❌ WRONG — never commit secrets
BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
DATABASE_URL = "postgresql://user:password@localhost:5432/db"

# ✅ CORRECT — read from environment
import os
from pathlib import Path

BOT_TOKEN = os.environ["BOT_TOKEN"]
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/bot.db")
```

### Local Development with `.env`

```bash
# .env (add to .gitignore!)
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
WEBHOOK_URL=http://localhost:8443/webhook
WEBHOOK_SECRET=local-dev-secret
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=DEBUG
```

```python
# Load .env in development only
import os
from pathlib import Path


def load_env() -> None:
    """Load .env file if it exists (development only)."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


load_env()
```

> **Important:** Never commit `.env` files. Always add `.env` to `.gitignore`.

### Platform-Specific Secret Management

| Platform | Secret Management |
|----------|-------------------|
| Heroku | `heroku config:set KEY=VALUE` |
| Railway | `railway variables set KEY=VALUE` |
| Render | Dashboard → Environment → Secrets |
| AWS | Secrets Manager or SSM Parameter Store |
| GCP | Secret Manager or environment variables |
| Azure | App Service → Configuration → Application Settings |
| Docker | `docker-compose` `env_file` or Docker secrets |
| Kubernetes | Kubernetes Secrets + mounted volumes |

---

## Scaling

### Horizontal Scaling with Webhooks

Webhook-based bots can be scaled horizontally by running multiple instances behind a load balancer.

```mermaid
flowchart TD
    A[Telegram API] --> B[Load Balancer]
    B --> C[Bot Instance 1]
    B --> D[Bot Instance 2]
    B --> E[Bot Instance N]
    C --> F[(PostgreSQL)]
    D --> F
    E --> F
    C --> G[(Redis)]
    D --> G
    E --> G

    style A fill:#e3f2fd,stroke:#1565c0
    style B fill:#fff3e0,stroke:#e65100
    style C fill:#e8f5e9,stroke:#388e3c
    style D fill:#e8f5e9,stroke:#388e3c
    style E fill:#e8f5e9,stroke:#388e3c
    style F fill:#fce4ec,stroke:#c62828
    style G fill:#fce4ec,stroke:#c62828
```

### Multiple Webhook Instances

For high-availability, register multiple webhook endpoints with different priority values:

```python
import asyncio
import httpx

BOT_TOKEN = "your_token"
WEBHOOK_URLS = [
    ("https://primary.example.com/webhook", 0),
    ("https://secondary.example.com/webhook", 1),
]


async def register_webhooks() -> None:
    """Register webhooks with different priorities."""
    async with httpx.AsyncClient() as client:
        for url, max_connections in WEBHOOK_URLS:
            response = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={
                    "url": url,
                    "max_connections": max_connections,
                    "drop_pending_updates": True,
                },
            )
            print(f"Registered {url}: {response.json()}")
```

### Database Considerations

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool

DATABASE_URL = "postgresql://user:pass@host:5432/botdb"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # number of persistent connections
    max_overflow=20,  # temporary overflow connections
    pool_timeout=30,  # seconds to wait for a connection
    pool_recycle=1800,  # recycle connections after 30 minutes
    pool_pre_ping=True,  # verify connections before use
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
```

### Redis for Shared State

```python
import redis.asyncio as redis

redis_client = redis.from_url(
    "redis://localhost:6379/0",
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)


async def set_user_state(user_id: int, state: str, ttl: int = 3600) -> None:
    """Store user state in Redis with TTL."""
    await redis_client.setex(f"user_state:{user_id}", ttl, state)


async def get_user_state(user_id: int) -> str | None:
    """Retrieve user state from Redis."""
    return await redis_client.get(f"user_state:{user_id}")


async def acquire_distributed_lock(
    lock_name: str,
    timeout: int = 10,
) -> bool:
    """Acquire a distributed lock via Redis."""
    return await redis_client.set(
        f"lock:{lock_name}",
        "1",
        nx=True,
        ex=timeout,
    )
```

### Load Balancing Considerations

| Strategy | Use Case | Notes |
|----------|----------|-------|
| Round-robin | Equal-sized instances | Simple, no state awareness |
| Least connections | Variable request times | Better for mixed workloads |
| IP hash | Session affinity | Sticky sessions per client |
| Weighted | Mixed instance sizes | Distribute by capacity |

> **Important:** Telegram guarantees at-most-once delivery for updates. Your bot must be idempotent — processing the same update twice should produce the same result.

---

## Monitoring & Observability

### Structured Logging

```python
import logging
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for production."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
```

### Health Check Endpoints

```python
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

_start_time = datetime.now(timezone.utc)


@app.get("/health")
async def health_check() -> dict:
    """Basic health check for load balancers."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/detailed")
async def detailed_health() -> dict:
    """Detailed health check including dependencies."""
    checks = {
        "bot": "healthy",
        "database": "healthy",
        "redis": "healthy",
    }

    # Check database connectivity
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"

    # Check Redis connectivity
    try:
        await redis_client.ping()
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"

    all_healthy = all(v == "healthy" for v in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

### Error Tracking with Sentry

```python
import os
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[sentry_logging],
    traces_sample_rate=0.1,
    environment=os.environ.get("ENVIRONMENT", "production"),
    release=os.environ.get("APP_VERSION", "unknown"),
)

logger = logging.getLogger(__name__)


async def risky_operation() -> None:
    """Example operation that reports errors to Sentry."""
    try:
        # ... operation that might fail ...
        result = await some_external_api_call()
    except Exception as e:
        logger.error("Operation failed: %s", e, exc_info=True)
        sentry_sdk.capture_exception(e)
        raise
```

### Metrics Collection

```python
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

_metrics: dict[str, list[float]] = {
    "handler_duration": [],
    "api_calls": [],
    "errors": [],
}


def track_metric(metric_name: str) -> Callable:
    """Decorator to track execution metrics."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                duration = time.monotonic() - start
                _metrics[metric_name].append(duration)

                if len(_metrics[metric_name]) > 1000:
                    _metrics[metric_name] = _metrics[metric_name][-500:]

                return result
            except Exception as e:
                _metrics["errors"].append(time.monotonic())
                logger.error("Error in %s: %s", func.__name__, e)
                raise

        return wrapper

    return decorator


def get_metrics_summary() -> dict:
    """Return a summary of collected metrics."""
    summary = {}
    for name, values in _metrics.items():
        if values:
            summary[name] = {
                "count": len(values),
                "avg_ms": round(sum(values) / len(values) * 1000, 2),
                "min_ms": round(min(values) * 1000, 2),
                "max_ms": round(max(values) * 1000, 2),
            }
    return summary
```

---

## systemd Service Example

For VPS deployments, `systemd` provides reliable process management with automatic restarts.

### Service File

```ini
[Unit]
Description=Telegram Bot
Documentation=https://github.com/you/telegram-bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/home/botuser/bot
ExecStart=/home/botuser/bot/venv/bin/python bot.py
Restart=always
RestartSec=10
StartLimitIntervalSec=300
StartLimitBurst=5

# Environment
EnvironmentFile=/home/botuser/.env

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/botuser/bot/data
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits
LimitNOFILE=65536
MemoryMax=512M
CPUQuota=80%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

### Installation Commands

```bash
# Copy the service file
sudo cp telegram-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f

# Restart after code update
sudo systemctl restart telegram-bot
```

### Supervisor Alternative

```ini
[program:telegram-bot]
command=/home/botuser/bot/venv/bin/python bot.py
directory=/home/botuser/bot
user=botuser
autostart=true
autorestart=true
startretries=5
startsecs=10
stopwaitsecs=30
stopsignal=TERM
environment=
    BOT_TOKEN="your_token",
    WEBHOOK_URL="https://yourdomain.com/webhook",
    WEBHOOK_SECRET="your_secret",
    DATABASE_URL="sqlite:///data/bot.db"
stdout_logfile=/var/log/telegram-bot/stdout.log
stderr_logfile=/var/log/telegram-bot/stderr.log
stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=5
stderr_logfile_backups=5
```

```bash
# Install supervisor
apt install -y supervisor

# Copy config
sudo cp telegram-bot.conf /etc/supervisor/conf.d/

# Reload and start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start telegram-bot

# Check status
sudo supervisorctl status telegram-bot
```

---

## Summary

| Topic | Recommendation |
|-------|----------------|
| Development | Use polling; no public URL needed |
| Production | Use webhooks; lower latency, lower resource usage |
| Containerization | Docker + docker-compose for reproducibility |
| VPS | systemd or supervisor for process management |
| CI/CD | GitHub Actions for automated testing and deployment |
| Secrets | Environment variables; never commit `.env` files |
| Scaling | Horizontal scaling with Redis for shared state |
| Monitoring | Structured logging + Sentry + health check endpoints |

> **Previous Chapter:** [Chapter 14: Groups, Channels & Admin](14-groups-channels.md) — Handle group events, admin operations, permissions, and channel broadcasting.
