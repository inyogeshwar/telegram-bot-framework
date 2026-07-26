# Chapter 20: OpenCode Agent Documentation Review

> **Audience:** Developers maintaining or consuming AI-generated Telegram Bot code.
> **Purpose:** A systematic review of the `python-telegram-bot` documentation from the perspective of an AI coding agent (OpenCode), identifying gaps, ambiguities, and hallucination risks that can cause agents to produce incorrect code or advice.

---

## Table of Contents

1. [Documentation Completeness Assessment](#1-documentation-completeness-assessment)
2. [Potential Hallucination Risks](#2-potential-hallucination-risks)
3. [Missing Best Practices](#3-missing-best-practices)
4. [Missing Production Notes](#4-missing-production-notes)
5. [Missing Security Notes](#5-missing-security-notes)
6. [Recommended Improvements for Documentation Consumers](#6-recommended-improvements-for-documentation-consumers)
7. [Agent-Specific Guidance](#7-agent-specific-guidance)

---

## 1. Documentation Completeness Assessment

### 1.1 Missing Explanations

These are areas where the official documentation is either absent, buried in footnotes, or phrased in a way that an AI agent is likely to misinterpret.

| Topic | What the Docs Say | The Actual Behavior | Risk Level |
|-------|-------------------|---------------------|------------|
| `Context.user_data` lifecycle | "A `dict` you can use to store data for the user" | Created per-user on first access. **Cleared when the user is removed from the bot's memory.** Only persists across restarts with a persistence backend (e.g., `PicklePersistence`). | High |
| Handler group execution order | Mentioned briefly in `Application.add_handler` | Within the same group, handlers execute in **registration order**. Between groups, **lower group numbers execute first**. If a handler in group 0 matches and returns `CallbackContext` (not `None`), group 1 handlers are **skipped entirely** — they are never checked. | Critical |
| `ConversationHandler` `per_message` | "Tracks per message" | When `per_message=True` with a `CallbackQueryHandler`, state is keyed to `(chat_id, message_id)` instead of `(chat_id, user_id)`. Editing the same inline keyboard from a different message creates a **separate conversation state**. | High |
| `JobQueue` dependency | Listed under "Optional Dependencies" | `JobQueue` **requires** the `job-queue` extra: `pip install python-telegram-bot[job-queue]`. It is **not** installed by default. Calling `application.job_queue` without it raises an error at runtime, not import time. | Critical |
| Filter composition order | Examples show `filters.TEXT & ~filters.COMMAND` | Operator precedence: `~` binds tighter than `&`. The expression `~filters.COMMAND & filters.TEXT` may not evaluate as intended. **Always place positive filters first.** | Medium |
| `parse_mode` inheritance | "Applied to all messages in a media group" | In media groups, `parse_mode` is set at the `sendMediaGroup` level. Individual captions can override via the `caption_entities` field on each `InputMedia` object. | Low |
| `file_id` stability | "Unique identifier for this file" | `file_id` values can change when Telegram migrates infrastructure or when a file is re-uploaded. Do **not** treat them as permanent across multi-year timescales. | Low |

### 1.2 Ambiguous Wording

These are phrasings in the docs that are technically correct but frequently misinterpreted by agents.

| Ambiguous Phrase | Correct Interpretation |
|-----------------|----------------------|
| `context.bot` | Use `context.bot` in handler code. `context.application.bot` is also valid but longer and unnecessary in handlers. |
| `chat_id` type | Can be `int` (numeric chat ID) or `str` (e.g., `@channelusername`). Always accept both. |
| `message_id` vs `inline_message_id` | `message_id` is for messages in a chat. `inline_message_id` is for messages sent via inline mode. They use **different API methods** to edit. |
| `parse_mode` at message vs caption level | `parse_mode` on `send_message` applies to the message body. On media, it applies to captions. They are **separate parameters** on separate objects. |

### 1.3 Incomplete APIs

Areas where the source documentation is thin or missing entirely.

- **`application.post_init` / `post_shutdown`**: Lifecycle hooks for async setup/teardown (database connections, cache warming, etc.). Barely documented; agents often skip them.
- **Builder patterns**: `ApplicationBuilder` vs `MessageBuilder` — when to use which. Most agents default to `ApplicationBuilder` and never mention `MessageBuilder`.
- **Persistence configuration**: `pickle` vs `dict` persistence, `per_user` / `per_chat` / `per_message` flags. Agents frequently assume persistence is enabled by default (it is not).
- **Error handler nuances**: Error handlers receive the exception in `context.error`, **not** as a separate parameter. Agents sometimes generate `async def error(update, context, error)` which is wrong.
- **CallbackData patterns**: No built-in pattern matching or routing. Developers must implement their own string-parsing logic. Agents often invent nonexistent `CallbackData` routers.
- **Rate limiting**: No built-in rate limiter. The library raises `telegram.error.RetryAfter` on rate limit violations; handling is the developer's responsibility.
- **Webhook secret validation**: `run_webhook` handles this automatically. Manual webhook setups must validate `X-Telegram-Bot-Api-Secret-Token` headers themselves.

---

## 2. Potential Hallucination Risks

### 2.1 Common Agent Mistakes

The following table catalogs errors that AI agents frequently produce when generating Telegram bot code.

| Mistake | Correct Approach |
|---------|-----------------|
| `application.run_polling()` inside async code | Call from a sync context or use `await application.initialize()` followed by `await application.start()` and `await application.updater.start_polling()` |
| Forgetting `await` on bot methods | All bot API methods are coroutines in v20+. Must be awaited. |
| `update.message.text` without null check | `update.message` is `None` for callback queries, inline queries, etc. Always check `if update.message:` first. |
| Not calling `query.answer()` on `CallbackQuery` | The loading spinner persists indefinitely. Always call `await query.answer()`, even with an empty response. |
| Importing from `telegram` instead of `telegram.ext` | Handler classes live in `telegram.ext`, not `telegram`. |
| Using `context.bot.send_message` everywhere | `update.message.reply_text` is a convenience wrapper. Both work; `reply_text` is shorter and auto-fills `chat_id`. |
| Assuming `callback_data` is always a string | It can be `None` for game callbacks. Always guard with `if query.data is not None:`. |
| Not returning `ConversationHandler.END` | The conversation hangs. Return `ConversationHandler.END` to terminate. |
| Using `filters.Chat.GROUP` | Does not exist. Correct: `filters.ChatType.GROUP` or `filters.ChatType.SUPERGROUP`. |
| Hardcoding `chat_id` | Use `update.effective_chat.id` for dynamic chat targeting. |

### 2.2 Version-Specific Pitfalls

| Pitfall | Details |
|---------|---------|
| Mixing async and sync patterns | v20+ is fully async. v13.x was sync. Mixing `update.message.reply_text()` (sync call) with async handlers causes silent failures or `RuntimeError`. |
| `CallbackQueryHandler` pattern is regex | It is **not** a glob or prefix match. `r"^btn_(.+)$"` is correct; `"btn_*"` is not. |
| `ConversationHandler` fallbacks | Fallbacks do **not** consume the update if they do not match. The update propagates to other handlers. |
| Direct `Application` instantiation | Cannot be done. Must use `ApplicationBuilder().token(TOKEN).build()`. |
| `per_message` + `CallbackQueryHandler` | State is keyed per message, not per user. Editing the same inline keyboard from different messages creates separate states. |

---

## 3. Missing Best Practices

> **Note:** These practices are rarely emphasized in the official docs but are essential for production bots.

### Core Practices

```python
# Always wrap formatted messages in try/except
try:
    await update.message.reply_text(
        "<b>Hello</b>",
        parse_mode=ParseMode.HTML,
    )
except TelegramError as e:
    logger.warning("Failed to send formatted message: %s", e)
    await update.message.reply_text("Hello")  # Fallback without formatting

# Always answer callback queries
query = update.callback_query
await query.answer()  # Even with no data

# Use per_user=True (default) to prevent state leaking
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={...},
    fallbacks=[...],
    per_user=True,  # Explicit is better than implicit
)

# Set conversation_timeout to prevent stuck states
conv_handler = ConversationHandler(
    ...,
    conversation_timeout=300,  # 5 minutes
)
```

### Operational Practices

| Practice | Why It Matters |
|----------|---------------|
| **Structured logging** | `print()` is not recoverable. Use `logging` with structured output. |
| **Validate all user input** | Never trust client-side data. Sanitize before processing. |
| **Use `file_id` over URLs** | Faster, avoids re-downloading, removes external dependency. |
| **Handle `RetryAfter`** | Telegram rate limits aggressively. Ignoring this crashes the bot. |
| **Use `update.effective_chat.id`** | Hardcoded chat IDs break in group chats and multi-tenant bots. |

---

## 4. Missing Production Notes

> **Critical:** The official documentation focuses on development. These notes cover the gap to production readiness.

| Concern | Recommendation |
|---------|---------------|
| **Graceful shutdown** | Handle `SIGTERM` / `SIGINT`. Save state before exit. Use `application.post_shutdown` hook. |
| **Health checks** | Expose an HTTP endpoint (e.g., `/health`) for load balancers and container orchestrators. |
| **Connection pooling** | Use database connection pools (e.g., `asyncpg.Pool`, `aioredis.ConnectionPool`). Do not create connections per request. |
| **Memory management** | Periodically clear stale entries from `context.bot_data` and `context.user_data`. Implement TTL or LRU eviction. |
| **Log rotation** | Configure `RotatingFileHandler` or `TimedRotatingFileHandler`. Prevent disk exhaustion. |
| **Database migrations** | Plan for schema changes from day one. Use Alembic (SQLAlchemy) or `prisma migrate` (Prisma). |
| **Dependency pinning** | Pin exact versions in `requirements.txt`. Use lock files where possible. |
| **Monitoring** | Track handler latency, error rates, and API call counts. Use Prometheus, Datadog, or similar. |

### Graceful Shutdown Example

```python
import signal
import logging

logger = logging.getLogger(__name__)

async def post_shutdown(application):
    """Called after the application shuts down."""
    logger.info("Shutting down gracefully...")
    if hasattr(application.bot_data, "db_pool"):
        await application.bot_data["db_pool"].close()

def run():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.ensure_future(application.shutdown()))

    application.run_polling()
```

---

## 5. Missing Security Notes

> **These are non-negotiable for any bot handling user data.**

| Rule | Rationale |
|------|-----------|
| **NEVER log user messages with PII** | Violates GDPR and Telegram's Terms of Service. Log metadata only. |
| **NEVER store raw user messages without purpose** | Data minimization principle. Store only what you need. |
| **Always validate Web App `initData`** | Telegram Web App data can be spoofed if not validated server-side. Use HMAC verification. |
| **Use `secret_token` in production** | `run_webhook(secret_token=...)` prevents unauthorized webhook calls. |
| **Pin dependency versions** | Prevents supply chain attacks from version drift. |
| **Audit dependencies regularly** | Run `pip-audit` or `safety check` in CI. |

### `initData` Validation

```python
import hmac
import hashlib
from urllib.parse import urlparse, parse_qs

def validate_init_data(init_data: str, bot_token: str) -> bool:
    """Validate Telegram Web App initData."""
    parsed = parse_qs(init_data)
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        return False

    data_check_string = "\n".join(
        f"{k}={v[0]}"
        for k, v in sorted(parsed.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed_hash, received_hash)
```

---

## 6. Recommended Improvements for Documentation Consumers

These are concrete recommendations for developers (and agents) who consume the `python-telegram-bot` docs.

| Recommendation | Rationale |
|---------------|-----------|
| **Prefer HTML over MarkdownV2** | HTML requires less escaping and has more predictable behavior. MarkdownV2 requires escaping `-`, `.`, `(`, `)`, and other characters. |
| **Use `Enum` for ConversationHandler states** | Magic numbers are unreadable. `class States(Enum): AWAITING_NAME = 0` is self-documenting. |
| **Create a base handler class** | Encapsulate common patterns (admin check, rate limit, error handling) in a reusable base. |
| **Implement centralized callback routing** | Do not rely on string matching scattered across handlers. Build a single router that dispatches by `callback_data` prefix. |
| **Use dataclasses or Pydantic for configuration** | Type-safe, validated, self-documenting. Replace raw `dict` configs. |
| **Add type hints everywhere** | The library supports them fully. Agents generate better code when type hints are present in examples. |

### Callback Data Router Example

```python
from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class CallbackRoute:
    prefix: str
    handler: Callable

class CallbackRouter:
    def __init__(self):
        self._routes: list[CallbackRoute] = []

    def register(self, prefix: str, handler: Callable):
        self._routes.append(CallbackRoute(prefix=prefix, handler=handler))

    async def dispatch(self, update, context):
        query = update.callback_query
        if query.data is None:
            return
        for route in self._routes:
            if query.data.startswith(route.prefix):
                await route.handler(update, context)
                return
        await query.answer("Unknown action.")
```

---

## 7. Agent-Specific Guidance

> **For AI agents generating Telegram bot code.** Follow these rules strictly.

### Mandatory Rules

1. **Check `python-telegram-bot` version first.** v20+ is async. v13 is sync. Mixing patterns causes runtime errors.
2. **Always use `from telegram.ext import ...`** for handler classes, filters, and application builders.
3. **Always `await` bot methods.** They return coroutines in v20+. Example: `await context.bot.send_message(...)`.
4. **Always handle `None` values.** `update.message`, `update.callback_query`, `update.effective_user` can all be `None`.
5. **Always call `query.answer()`** on callback queries. Even with no data. The loading spinner otherwise persists.
6. **Use `filters` from `telegram.ext.filters`**, not `telegram.filters`.
7. **Do not assume handler registration order.** Use handler groups (`group=0`, `group=1`) for priority.
8. **Do not use global variables for state.** Use `context.user_data`, `context.chat_data`, or `context.bot_data`.
9. **Do not hardcode tokens.** Use environment variables: `os.environ["BOT_TOKEN"]`.
10. **Do not skip error handling.** Wrap API calls in `try/except TelegramError`.

### Generated Code Checklist

Before outputting any Telegram bot code, verify:

- [ ] All bot method calls are `await`ed
- [ ] All `update.message` accesses are guarded with a `None` check
- [ ] All callback queries have a corresponding `query.answer()`
- [ ] Filter imports are from `telegram.ext.filters`
- [ ] Handler classes are imported from `telegram.ext`
- [ ] `ConversationHandler` returns `ConversationHandler.END` on completion
- [ ] No hardcoded tokens or chat IDs
- [ ] Error handlers accept `(update, context)` — **not** `(update, context, error)`
- [ ] `parse_mode` uses `ParseMode.HTML` or `ParseMode.MARKDOWNV2` constants, not raw strings
- [ ] Application is built via `ApplicationBuilder().token(TOKEN).build()`, not `Application(token=TOKEN)`

---

## Summary

The `python-telegram-bot` documentation is extensive but has significant gaps that can cause AI agents to generate incorrect code. The most dangerous areas are:

1. **Handler group execution order** — frequently misunderstood, causes silent failures.
2. **`JobQueue` dependency** — not installed by default, causes import-time vs runtime confusion.
3. **`ConversationHandler` `per_message` behavior** — state is per-message, not per-user, leading to subtle bugs.
4. **v20+ async migration** — agents trained on v13 examples generate sync code that fails in v20+.
5. **Error handler signature** — agents frequently invent a third `error` parameter that does not exist.

Always validate agent-generated Telegram bot code against this checklist before deploying to production.
