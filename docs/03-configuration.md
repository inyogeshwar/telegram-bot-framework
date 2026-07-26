# Chapter 3: Configuration & Environment

A production Telegram bot must behave differently in development and production
without changing a single line of code. This chapter covers secrets management,
configuration classes, validation, database setup, Redis integration, and
structured logging.

---

## Table of Contents

- [Why Configuration Matters](#why-configuration-matters)
- [Environment Variables](#environment-variables)
- [Using python-dotenv](#using-python-dotenv)
- [Bot Token Security](#bot-token-security)
- [Configuration Class](#configuration-class)
- [Configuration Validation](#configuration-validation)
- [Database Configuration](#database-configuration)
- [Redis Configuration](#redis-configuration)
- [Logging Configuration](#logging-configuration)
- [Complete config.py](#complete-configpy)
- [Common Mistakes](#common-mistakes)

---

## Why Configuration Matters

Hardcoding values like API tokens, database URLs, or admin IDs creates three
problems:

1. **Security risk** — secrets leak into version control.
2. **Rigidity** — switching between local development and production requires
   editing source files.
3. **Auditability** — there is no single place that documents which values the
   application expects.

The standard solution is to read all environment-specific values from
**environment variables** and load them at application startup through a typed
configuration object.

---

## Environment Variables

The following table lists every environment variable your bot should support.
All are optional at the framework level; your application logic decides which
ones are required.

| Variable          | Type      | Default                   | Description                                      |
|-------------------|-----------|---------------------------|--------------------------------------------------|
| `BOT_TOKEN`       | `str`     | `""`                      | Telegram Bot API token from BotFather.           |
| `DATABASE_URL`    | `str`     | `sqlite:///bot.db`        | SQLAlchemy connection string.                    |
| `REDIS_URL`       | `str`     | `redis://localhost:6379`  | Redis connection URL for caching / sessions.     |
| `ADMIN_IDS`       | `str`     | `""`                      | Comma-separated list of Telegram user IDs.       |
| `WEBHOOK_URL`     | `str`     | `""`                      | Public HTTPS URL for webhook mode.               |
| `WEBHOOK_SECRET`  | `str`     | `""`                      | Secret token Telegram sends with each update.    |
| `LOG_LEVEL`       | `str`     | `INFO`                    | Python log level (`DEBUG`, `INFO`, `WARNING`, …).|
| `ENVIRONMENT`     | `str`     | `development`             | Active environment (`development`, `production`).|

> [!NOTE]
> Use `ADMIN_IDS` (plural) even though it may contain a single ID. This makes
> it clear the variable accepts a list.

---

## Using python-dotenv

[`python-dotenv`](https://pypi.org/project/python-dotenv/) reads a `.env` file
and injects its values into `os.environ` so that every module can access them
without passing a config object around.

### Installation

```bash
pip install python-dotenv
```

### Basic Usage

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env into os.environ


class Config:
    """Centralized, typed configuration read from environment variables."""

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    ADMIN_IDS: list[int] = [
        int(uid)
        for uid in os.getenv("ADMIN_IDS", "").split(",")
        if uid.strip()
    ]
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
```

### .env File Example

```dotenv
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
DATABASE_URL=postgresql://user:password@localhost:5432/bot_db
REDIS_URL=redis://:secret@localhost:6379/0
ADMIN_IDS=123456789,987654321
WEBHOOK_URL=https://example.com/webhook
WEBHOOK_SECRET=my-super-secret-token
LOG_LEVEL=DEBUG
ENVIRONMENT=production
```

> [!CAUTION]
> Never place real secrets in `.env.example`. Use descriptive placeholders like
> `your-bot-token-here` so the file is safe to commit.

---

## Bot Token Security

Your bot token grants **full control** over your Telegram bot. Treat it with
the same severity as a database password or cloud API key.

| Rule | Rationale |
|------|-----------|
| Never hardcode the token in source files. | Anyone with repository access gains bot control. |
| Never commit `.env` to version control. | Git history is permanent; a leaked token cannot be fully purged. |
| Use environment-specific tokens. | A compromised dev token should not affect production. |
| Rotate the token if it is accidentally exposed. | Use BotFather → `/revoke` to generate a new one immediately. |
| Restrict bot scope where possible. | Limit what the bot can do if the token is ever compromised. |

### Revoking a Compromised Token

```text
1. Open Telegram and search for @BotFather.
2. Send /mybots and select the affected bot.
3. Tap "API Token" → "Revoke current token".
4. BotFather issues a new token — update your .env and redeploy.
```

> [!IMPORTANT]
> After revoking, every running instance of the bot using the old token will
> immediately lose API access. Coordinate with your team before rotating.

---

## Configuration Class

A single, importable configuration class gives your codebase one source of
truth for all settings:

```python
# config.py
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _split_int_csv(raw: str) -> list[int]:
    """Parse a comma-separated string of integers, ignoring blanks."""
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Config:
    """Immutable application configuration.

    Attributes are populated from environment variables at import time.
    Use ``Config.from_env()`` to get the singleton instance.
    """

    # Telegram
    BOT_TOKEN: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    WEBHOOK_URL: str = field(default_factory=lambda: os.getenv("WEBHOOK_URL", ""))
    WEBHOOK_SECRET: str = field(default_factory=lambda: os.getenv("WEBHOOK_SECRET", ""))

    # Database
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///bot.db")
    )

    # Redis
    REDIS_URL: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )

    # Access control
    ADMIN_IDS: list[int] = field(
        default_factory=lambda: _split_int_csv(os.getenv("ADMIN_IDS", ""))
    )

    # Application
    ENVIRONMENT: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    MAX_MESSAGE_LENGTH: int = 4096
    RATE_LIMIT: int = 30  # requests per minute per user

    @property
    def is_production(self) -> bool:
        """Return ``True`` when running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def use_webhook(self) -> bool:
        """Determine whether webhook mode should be used.

        A bot runs in webhook mode only when a public URL is provided **and**
        the environment is production.
        """
        return bool(self.WEBHOOK_URL) and self.is_production


# ── Singleton ───────────────────────────────────────────────
_config: Config | None = None


def get_config() -> Config:
    """Return the application configuration (created on first call)."""
    global _config  # noqa: PLW0603
    if _config is None:
        _config = Config()
    return _config
```

### Usage Anywhere in Your Code

```python
from config import get_config

cfg = get_config()
print(cfg.BOT_TOKEN[:10] + "...")  # Partial token for debugging only
print(f"Environment: {cfg.ENVIRONMENT}")
```

---

## Configuration Validation

Environment variables are always strings. A missing or malformed value can
cause runtime failures that are difficult to diagnose. Validate at startup.

### Option A — Pydantic Settings (Recommended)

The [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
package provides type coercion, default values, and error messages out of the
box.

```bash
pip install pydantic-settings
```

```python
# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Validated configuration loaded from environment variables."""

    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite:///bot.db"
    REDIS_URL: str = "redis://localhost:6379"
    ADMIN_IDS: list[int] = []
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @classmethod
    def parse_admin_ids(cls, v: str | list[int]) -> list[int]:
        """Accept a comma-separated string or a list of integers."""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


settings = Settings()
```

### Option B — Manual Validation

If you prefer to avoid additional dependencies:

```python
def validate_config(cfg: Config) -> None:
    """Validate configuration at startup and fail fast on errors."""
    errors: list[str] = []

    if not cfg.BOT_TOKEN:
        errors.append("BOT_TOKEN is required but was not provided.")

    if cfg.is_production and not cfg.WEBHOOK_URL:
        errors.append("WEBHOOK_URL is required in production.")

    if cfg.is_production and not cfg.WEBHOOK_SECRET:
        errors.append("WEBHOOK_SECRET is required in production.")

    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if cfg.LOG_LEVEL.upper() not in valid_levels:
        errors.append(f"LOG_LEVEL must be one of {valid_levels}, got '{cfg.LOG_LEVEL}'.")

    if errors:
        header = "Configuration validation failed:"
        detail = "\n  - ".join(errors)
        raise ValueError(f"{header}\n  - {detail}")


# Call at startup in bot.py
cfg = get_config()
validate_config(cfg)
```

> [!TIP]
> Validate **before** calling `Application.run_polling()` or
> `Application.run_webhook()`. Failing fast at startup prevents half-initialized
> bots from accepting traffic.

---

## Database Configuration

| Environment | Recommended Backend | Connection String Example |
|-------------|---------------------|---------------------------|
| Development | SQLite              | `sqlite:///bot.db`        |
| Production  | PostgreSQL          | `postgresql://user:pass@host:5432/bot` |

### SQLAlchemy Setup

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import get_config


class Base(DeclarativeBase):
    """Base class for all ORM models."""


engine = create_engine(
    get_config().DATABASE_URL,
    echo=get_config().LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,  # Detect stale connections
)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Yield a database session and ensure it is closed after use."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

### SQLite-Specific Considerations

- SQLite does not support concurrent writers. Use it **only** for development
  and testing.
- Set `connect_args={"check_same_thread": False}` if you use `AsyncSession`
  with `aiosqlite`.

### PostgreSQL Production Tips

- Use connection pooling (`pool_size=5`, `max_overflow=10`) for high-throughput
  bots.
- Set `pool_pre_ping=True` to automatically recover from dropped connections.
- Store credentials in the connection URL, never in source code.

---

## Redis Configuration

Redis provides a fast, shared key-value store for caching, rate limiting, and
storing temporary session data.

```python
# cache.py
import json
from typing import Any

import redis.asyncio as redis

from config import get_config

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Return a shared Redis client (lazy-initialized)."""
    global _pool  # noqa: PLW0603
    if _pool is None:
        _pool = redis.from_url(
            get_config().REDIS_URL,
            decode_responses=True,
        )
    return _pool


async def cache_get(key: str) -> Any | None:
    """Retrieve a cached value by key, deserializing JSON."""
    client = await get_redis()
    raw = await client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Store a value in cache with a time-to-live in seconds."""
    client = await get_redis()
    await client.set(key, json.dumps(value), ex=ttl)
```

> [!NOTE]
> Redis is **not** a persistence layer. Always use a relational database for
> data you cannot afford to lose.

---

## Logging Configuration

Structured, consistent logging makes debugging production issues dramatically
easier.

```python
# logging_config.py
import logging
import sys
from pathlib import Path

from config import get_config


def setup_logging() -> None:
    """Configure root logger with console and file handlers."""
    cfg = get_config()

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ──────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(cfg.LOG_LEVEL.upper())
    console.setFormatter(fmt)

    # ── File handler ─────────────────────────────────────────
    file_handler = logging.FileHandler(
        log_dir / "bot.log",
        encoding="utf-8",
    )
    file_handler.setLevel("DEBUG")  # File always captures everything
    file_handler.setFormatter(fmt)

    # ── Root logger ──────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel("DEBUG")
    root.addHandler(console)
    root.addHandler(file_handler)

    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
```

### Log Levels at a Glance

| Level      | Numeric | When to Use                                     |
|------------|---------|-------------------------------------------------|
| `DEBUG`    | 10      | Detailed diagnostic information. Never in production user-facing logs. |
| `INFO`     | 20      | Normal operational messages (bot started, command received). |
| `WARNING`  | 30      | Unexpected but recoverable situations (rate limit approached). |
| `ERROR`    | 40      | Operation failed (API call timed out, DB write failed). |
| `CRITICAL` | 50      | The process cannot continue and must shut down.  |

---

## Complete config.py

The following is a fully typed, production-ready configuration module that
combines everything discussed in this chapter:

```python
# config.py
"""Centralized application configuration.

All values are read from environment variables. The ``.env`` file is loaded
automatically at import time via ``python-dotenv``.

Usage::

    from config import get_config

    cfg = get_config()
    print(cfg.BOT_TOKEN)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _split_int_csv(raw: str) -> list[int]:
    """Parse a comma-separated string of integers, ignoring blanks."""
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Config:
    """Immutable, typed configuration sourced from environment variables.

    Attributes
    ----------
    BOT_TOKEN : str
        Telegram Bot API token issued by @BotFather.
    DATABASE_URL : str
        SQLAlchemy connection string for the primary database.
    REDIS_URL : str
        Connection URL for the Redis instance.
    ADMIN_IDS : list[int]
        Telegram user IDs granted administrative privileges.
    WEBHOOK_URL : str
        Public HTTPS endpoint for receiving Telegram updates in production.
    WEBHOOK_SECRET : str
        Secret token used to verify incoming Telegram requests.
    LOG_LEVEL : str
        Root logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    ENVIRONMENT : str
        Active environment name (``development`` or ``production``).
    MAX_MESSAGE_LENGTH : int
        Maximum characters a single Telegram text message may contain.
    RATE_LIMIT : int
        Maximum API requests allowed per user per minute.
    """

    # ── Telegram ─────────────────────────────────────────────
    BOT_TOKEN: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    WEBHOOK_URL: str = field(default_factory=lambda: os.getenv("WEBHOOK_URL", ""))
    WEBHOOK_SECRET: str = field(default_factory=lambda: os.getenv("WEBHOOK_SECRET", ""))

    # ── Data stores ──────────────────────────────────────────
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///bot.db")
    )
    REDIS_URL: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )

    # ── Access control ───────────────────────────────────────
    ADMIN_IDS: list[int] = field(
        default_factory=lambda: _split_int_csv(os.getenv("ADMIN_IDS", ""))
    )

    # ── Application ──────────────────────────────────────────
    ENVIRONMENT: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    MAX_MESSAGE_LENGTH: int = 4096
    RATE_LIMIT: int = 30

    # ── Derived properties ───────────────────────────────────

    @property
    def is_production(self) -> bool:
        """Return ``True`` when running in a production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def use_webhook(self) -> bool:
        """Return ``True`` if the bot should run in webhook mode."""
        return bool(self.WEBHOOK_URL) and self.is_production


# ── Singleton accessor ────────────────────────────────────────────
_config: Config | None = None


def get_config() -> Config:
    """Return the global configuration instance, creating it on first call."""
    global _config  # noqa: PLW0603
    if _config is None:
        _config = Config()
    return _config


# ── Validation ────────────────────────────────────────────────────

_VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def validate_config(cfg: Config | None = None) -> None:
    """Validate the configuration and raise ``ValueError`` on any error.

    This function **must** be called before starting the bot to guarantee
    that all required values are present and well-formed.

    Parameters
    ----------
    cfg : Config | None
        The configuration to validate. When ``None``, the global instance
        is retrieved via :func:`get_config`.

    Raises
    ------
    ValueError
        If one or more configuration values are invalid.
    """
    if cfg is None:
        cfg = get_config()

    errors: list[str] = []

    if not cfg.BOT_TOKEN:
        errors.append("BOT_TOKEN is required.")

    if cfg.is_production and not cfg.WEBHOOK_URL:
        errors.append("WEBHOOK_URL is required in production mode.")

    if cfg.is_production and not cfg.WEBHOOK_SECRET:
        errors.append("WEBHOOK_SECRET is required in production mode.")

    if cfg.LOG_LEVEL.upper() not in _VALID_LOG_LEVELS:
        errors.append(
            f"LOG_LEVEL must be one of {sorted(_VALID_LOG_LEVELS)}, "
            f"got '{cfg.LOG_LEVEL}'."
        )

    if not isinstance(cfg.RATE_LIMIT, int) or cfg.RATE_LIMIT < 1:
        errors.append(f"RATE_LIMIT must be a positive integer, got '{cfg.RATE_LIMIT}'.")

    if errors:
        header = "Configuration validation failed:"
        body = "\n  - ".join(errors)
        raise ValueError(f"{header}\n  - {body}")

    logger.info("Configuration validated successfully (env=%s).", cfg.ENVIRONMENT)
```

### Wiring It Into bot.py

```python
# bot.py
"""Application entry point."""

import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from config import get_config, validate_config
from handlers.start import start_handler
from logging_config import setup_logging


def main() -> None:
    """Initialize and run the bot."""
    setup_logging()
    cfg = get_config()
    validate_config(cfg)

    app = ApplicationBuilder().token(cfg.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))

    if cfg.use_webhook:
        app.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path="webhook",
            webhook_url=f"{cfg.WEBHOOK_URL}/webhook",
            secret_token=cfg.WEBHOOK_SECRET,
        )
    else:
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
```

---

## Common Mistakes

| # | Mistake | Consequence | Fix |
|---|---------|-------------|-----|
| 1 | Hardcoding `BOT_TOKEN` in source code | Token exposed in version control history. | Use environment variables and `.env`. |
| 2 | Committing `.env` to git | Secrets are public the moment the repo is pushed. | Add `.env` to `.gitignore` immediately. |
| 3 | Using SQLite in production | Concurrency limits cause data corruption under load. | Use PostgreSQL with connection pooling. |
| 4 | Ignoring config validation | Bot starts, then crashes on the first missing value. | Validate at startup with `validate_config()`. |
| 5 | No logging configuration | Default logs are unstructured and hard to search. | Set up console + file handlers with a consistent format. |
| 6 | Sharing one token across dev and prod | Revoking a dev token kills production, or vice versa. | Maintain separate tokens per environment. |
| 7 | Leaving `DEBUG` logging in production | Disk fills up; sensitive data leaks into log files. | Set `LOG_LEVEL=INFO` in production. |
| 8 | Not calling `validate_config()` before `run_polling()` | Runtime errors surface deep inside handler code. | Validate first; fail fast. |

---

## Next Steps

With configuration in place, proceed to
[Chapter 4: Bot Lifecycle & Application Setup](./04-bot-lifecycle.md) to learn
how to initialize the `Application` object, register handlers, and start
receiving updates.
