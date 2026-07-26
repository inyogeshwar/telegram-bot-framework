# Chapter 18: FAQ & Common Issues

This chapter collects the most frequently encountered problems when developing with
`python-telegram-bot` and the Telegram Bot API, along with clear solutions.

---

## Installation & Environment

### ModuleNotFoundError: No module named 'telegram'

**Cause:** `python-telegram-bot` is not installed, or the wrong Python environment is
active.

**Fix:**

```bash
pip install python-telegram-bot
```

Verify the installation:

```bash
python -c "import telegram; print(telegram.__version__)"
```

If you use multiple Python versions, ensure `pip` belongs to the same interpreter:

```bash
python -m pip install python-telegram-bot
```

### Version Conflicts with Other Packages

**Cause:** Another dependency pins an incompatible version of `httpx`, `anyio`, or
`certifi`.

**Fix:** Use a virtual environment and pin compatible versions:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
pip install "python-telegram-bot>=20,<22"
```

Check for conflicts:

```bash
pip check
```

### Deprecated `Updater` Usage (v13 → v20+ Migration)

**Cause:** Code written for `python-telegram-bot` v13 uses synchronous patterns
(`Updater`, `CallbackContext`) that no longer exist in v20+.

**Fix:** Migrate to the async `Application` builder. Key replacements:

| v13 | v20+ |
|-----|------|
| `Updater(token=...)` | `ApplicationBuilder().token(...).build()` |
| `updater.start_polling()` | `application.run_polling()` |
| `CallbackContext` | `ContextTypes.DEFAULT_TYPE` |
| `dispatcher.add_handler(...)` | `application.add_handler(...)` |

---

## Bot Token Issues

### "Unauthorized" Error

**Cause:** The token is invalid, revoked, or belongs to a different bot.

**Fix:**

1. Open Telegram and message @BotFather.
2. Send `/mybots`, select your bot, and tap **API Token**.
3. Copy the fresh token and update your environment variable.
4. Revoke the old token via **Revoke token** if it may have been leaked.

```bash
curl "https://api.telegram.org/bot<NEW_TOKEN>/getMe"
# Should return {"ok":true,"result":{...}}
```

### Bot Not Responding to Messages

**Cause:** Another process is already polling or handling updates with the same
token, causing a **Conflict** error.

**Fix:**

1. Stop all running instances of your bot.
2. Check for orphaned processes:

```bash
# Linux / macOS
ps aux | grep "python.*bot"

# Windows
tasklist | findstr python
```

3. Kill stray processes, then restart a single instance.
4. If using webhooks, verify no stale webhook is set:

```bash
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## Handler Issues

### Handler Not Being Called

**Cause:** Handler order, filter mismatch, or another handler consuming the update
first.

**Diagnosis steps:**

1. **Check handler group order.** Lower-numbered groups fire first. If a handler in
   group 0 calls `ConversationHandler.END` or otherwise short-circuits, group 1
   handlers never run.

2. **Check filters.** A `CommandHandler("start", fn)` only matches messages whose
   text starts with `/start`. It will not match `Start` or `start`.

3. **Add a debug handler** at the highest group number to see which updates arrive:

```python
import logging

logger = logging.getLogger(__name__)


async def debug_catcher(update, context):
    logger.warning("Unhandled update: %s", update)

application.add_handler(MessageHandler(filters.ALL, debug_catcher), group=999)
```

### CommandHandler Not Matching

**Cause:** Commands must begin with `/`. Telegram strips the bot mention in groups
(e.g., `/start@MyBot` becomes `/start`), but edge cases exist.

**Fix:**

- Ensure the incoming text actually starts with `/`.
- Use `filters.COMMAND` explicitly if you also handle text.
- Remember that commands are **case-insensitive** in Telegram: `/Start` and
  `/start` both trigger `CommandHandler("start", ...)`.

### CallbackQueryHandler Not Firing

**Cause:** Pattern mismatch, handler not registered, or the callback data format
changed.

**Fix:**

1. Log the actual callback data:

```python
async def debug_callback(update, context):
    import logging
    logging.warning("Callback data: %r", update.callback_query.data)
```

2. Ensure the pattern matches exactly. Patterns are **regex**, not prefix matches:

```python
# Matches "subscribe:weekly" but NOT "subscribe:weekly:extra"
CallbackQueryHandler(callback_fn, pattern=r"^subscribe:\w+$")
```

3. Always call `callback_query.answer()`—Telegram retries unacknowledged callbacks
   repeatedly.

### ConversationHandler Timeout Not Working

**Cause:** `per_message=True` and `per_chat=True` interact in ways that reset
timeouts unexpectedly.

**Fix:** Ensure `ConversationHandler` is added **before** any other handlers that
might match the same messages, and verify `timeout` is set in seconds (an integer,
not a timedelta):

```python
from telegram.ext import ConversationHandler

conv = ConversationHandler(
    entry_points=[CommandHandler("start", entry)],
    states={0: [MessageHandler(filters.TEXT, collect)]},
    fallbacks=[CommandHandler("cancel", cancel)],
    timeout=300,  # 5 minutes, in seconds
)
application.add_handler(conv, group=0)
```

---

## Message Issues

### "Bad Request: message text is too long"

**Cause:** Telegram limits message text to **4096 UTF-8 code points**.

**Fix:** Split long messages:

```python
def split_message(text: str, max_length: int = 4096) -> list[str]:
    """Split text into chunks that fit Telegram's message limit."""
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


async def send_long_message(update, text: str) -> None:
    for chunk in split_message(text):
        await update.message.reply_text(chunk)
```

### "Bad Request: can't parse entities"

**Cause:** Malformed MarkdownV2 or HTML in the message text.

**Fix:** Always escape user-supplied content before formatting:

```python
from telegram.helpers import escape_markdown


async def send_formatted(update, user_text: str) -> None:
    safe = escape_markdown(user_text, version=2)
    try:
        await update.message.reply_text(
            f"*You said:* {safe}",
            parse_mode="MarkdownV2",
        )
    except Exception:
        # Fallback: send without formatting
        await update.message.reply_text(f"You said: {user_text}")
```

### "Message to edit not found"

**Cause:** The message was deleted, sent by a different bot, or is too old to edit.

**Fix:**

- Use `allow_sending_without_reply=True` when the reply target may not exist.
- Wrap `edit_message_text` in a try/except and fall back to sending a new message:

```python
async def safe_edit(query, text: str) -> None:
    try:
        await query.edit_message_text(text)
    except Exception:
        await query.answer("Could not update the message.", show_alert=True)
```

### "Message can't be forwarded" / Private Channel Restrictions

**Cause:** The bot is not an admin in the channel, or the channel disallows
forwarding.

**Fix:** Use `copy_message` instead of `forwardMessage`—it does not require
forwarding privileges and does not show the original sender.

---

## Group & Channel Bot Issues

### Bot Not Receiving Messages in Groups

**Cause:** Privacy mode is **ON** by default. With privacy mode, bots only receive
commands, replies to their messages, and channel posts—**not** arbitrary text.

**Fix:**

1. Message @BotFather: `/setprivacy`.
2. Select your bot and choose **Disable**.
3. Restart the bot. Existing group members may need to `/start` the bot.

Alternatively, make the bot an **administrator** in the group—admins always receive
all messages regardless of privacy mode.

### Bot Receiving Too Many Messages

**Cause:** Privacy mode is off in a very active group.

**Fix:**

- Re-enable privacy mode via `/setprivacy` if the bot only needs commands.
- Use narrow filters so handlers only activate on relevant messages:

```python
from telegram.ext import filters

# Only respond to mentions or commands
application.add_handler(
    MessageHandler(
        filters.COMMAND | filters.Entity("mention"),
        handle_command_or_mention,
    )
)
```

### Bot Cannot Delete Messages in Groups

**Cause:** Bots can only delete their own messages or messages posted in channels
where they are admins.

**Fix:** Ensure the bot is an admin with **Delete Messages** permission, or only
attempt to delete messages the bot itself sent.

### Bot Cannot Restrict Admins

**Cause:** Telegram does not allow bots to restrict users with admin privileges.

**Fix:** Check the user's status before attempting restriction:

```python
member = await context.bot.get_chat_member(chat_id, user_id)
if member.status in ("administrator", "creator"):
    await update.message.reply_text("Cannot restrict admins.")
    return
await context.bot.restrict_chat_member(chat_id, user_id, permissions=...)
```

---

## Webhook Issues

### Webhook Not Receiving Updates

**Diagnosis:**

1. Check webhook status:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

Look for `"has_custom_certificate": false` and `"pending_update_count": 0`.

2. Common causes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pending_update_count` increasing | Server unreachable or SSL error | Verify HTTPS certificate, check firewall |
| `"last_error_message": "SSL" ` | Self-signed or invalid certificate | Use a valid certificate from Let's Encrypt |
| `"last_error_message": "Connection refused"` | Server not listening on expected port | Check port binding; Telegram requires 443, 80, 88, or 8443 |
| `"last_error_message": "Bad Gateway"` | Application crashes on webhook POST | Check application logs for exceptions |

3. Test the endpoint manually:

```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id": 999}'
```

A `200 OK` response (even if your handler errors internally) confirms connectivity.

### "Wrong Webhook URL" Error

**Cause:** The URL must be HTTPS, publicly resolvable, and on an allowed port.

**Fix:**

- URLs like `http://example.com/webhook` are rejected—use `https://`.
- Ports must be **443**, **80**, **88**, or **8443**.
- Do not include a trailing slash unless your route expects it.
- If behind a reverse proxy (nginx, Caddy), ensure it forwards to the correct
  upstream port.

### Switching Between Polling and Webhook

You cannot use both simultaneously. Before switching:

```bash
# Remove webhook
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"

# Verify it's removed
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
# Should show: "url": ""
```

Then switch your code from `run_polling()` to `run_webhook()`.

---

## Performance Issues

### Bot Is Slow to Respond

**Diagnosis:** Profile where time is spent.

**Common fixes:**

1. **Use webhooks** instead of polling—eliminates the polling interval overhead.
2. **Move slow I/O to background tasks** using `context.job_queue` or a task queue:

```python
async def long_running_task(context) -> None:
    result = await expensive_api_call()
    await context.bot.send_message(chat_id=chat_id, text=result)


async def trigger(update, context) -> None:
    await update.message.reply_text("Processing…")
    context.job_queue.run_once(
        callback=long_running_task,
        when=0,
        data={"chat_id": update.effective_chat.id},
    )
```

3. **Cache frequently accessed data** in `context.bot_data` or an in-memory store.
4. **Use `async` correctly.** Blocking calls (`requests.get(...)`) inside async
   handlers block the entire event loop. Use `httpx` or `aiohttp` instead.

### Memory Usage Growing Over Time

**Cause:** `user_data`, `chat_data`, and `bot_data` dictionaries accumulate entries
without bounds.

**Fix:**

- Implement periodic cleanup:

```python
from telegram.ext import CallbackContext


async def cleanup_old_data(context: CallbackContext) -> None:
    """Remove user_data entries older than 24 hours."""
    import time

    now = time.time()
    stale_keys = [
        uid
        for uid, data in context.bot_data.get("last_seen", {}).items()
        if now - data > 86400
    ]
    for uid in stale_keys:
        context.bot_data["last_seen"].pop(uid, None)


# Schedule cleanup daily
job_queue.run_daily(cleanup_old_data, when=0)
```

- Use `PicklePersistence` or `DictPersistence` to offload data from memory.

---

## Deployment Issues

### Bot Works Locally but Fails in Production

**Checklist:**

1. **Environment variables.** Verify all required variables are set:

```bash
python -c "import os; print(os.environ.get('BOT_TOKEN', 'NOT SET'))"
```

2. **Network access.** Production servers may block outbound HTTPS to
   `api.telegram.org`. Test:

```bash
curl -v https://api.telegram.org/bot<TOKEN>/getMe
```

3. **SSL certificates.** Outdated CA bundles cause `SSLError`. Update system
   certificates or pin `certifi` in requirements.

4. **Python version.** `python-telegram-bot` v20+ requires Python 3.8+. Confirm:

```bash
python --version
```

### Process Crashes on Restart

**Fix:** Use a process manager to auto-restart on failure.

**systemd (Linux):**

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/mybot
ExecStart=/opt/mybot/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable mybot
sudo systemctl start mybot
sudo journalctl -u mybot -f   # tail logs
```

**Docker:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker run -d --restart unless-stopped \
  -e BOT_TOKEN="$BOT_TOKEN" \
  mybot:latest
```

### Container Cannot Reach Telegram API

**Cause:** DNS resolution or firewall rules in the container network.

**Fix:** Ensure the container can resolve external hostnames:

```bash
docker run --rm python:3.12-slim \
  python -c "import urllib.request; print(urllib.request.urlopen('https://api.telegram.org').status)"
```

If this fails, check your Docker network configuration or use `host.docker.internal`
if applicable.

---

## Logging & Observability

### How Do I See What My Bot Is Doing?

Configure structured logging at application startup:

```python
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
```

For production, redirect to a file or external logging service and set
`level=logging.WARNING` to reduce noise.

### How Do I Track Which Handlers Are Triggered?

Add a middleware-like debug handler at group 0 that logs every update:

```python
import logging

logger = logging.getLogger(__name__)


async def log_updates(update, context):
    if update.message:
        logger.info(
            "Update %s: msg from %s in chat %s",
            update.update_id,
            update.effective_user.id,
            update.effective_chat.id,
        )
    elif update.callback_query:
        logger.info(
            "Update %s: callback '%s' from %s",
            update.update_id,
            update.callback_query.data,
            update.effective_user.id,
        )

application.add_handler(MessageHandler(filters.ALL, log_updates), group=-1)
```

---

## Still Stuck?

1. Search [existing issues](https://github.com/python-telegram-bot/python-telegram-bot/issues)
   on GitHub.
2. Ask in the [python-telegram-bot Telegram group](https://t.me/PyTelegramBotAPI).
3. File a bug report with a **minimal reproducible example**—include your
   `python-telegram-bot` version, Python version, OS, and the exact error traceback.
