---
description: Audit Telegram bot code for vulnerabilities following OWASP guidelines. Use when reviewing security, checking tokens, or hardening deployments.
allowed-tools: Read Grep Glob
---

## What I do

- Review bot code for security vulnerabilities
- Check token management and secret handling
- Validate input sanitization and rate limiting
- Assess webhook security and deployment practices

## When to use me

Use this skill when auditing bot code, reviewing pull requests, or hardening deployments.
Follow OWASP Top 10 mapping for Telegram bot applications.

## Security Checklist

1. No hardcoded tokens or secrets
2. Environment variables for configuration
3. Input validation and sanitization
4. Rate limiting implemented
5. Webhook signatures validated
6. Logging does not expose sensitive data
7. Dependencies are up to date
8. Mini App initData validated with HMAC-SHA256

## Common Vulnerabilities

### Token Exposure
```python
# BAD - never do this
TOKEN = "1234567890:ABC123..."

# GOOD - use environment variables
import os
TOKEN = os.getenv("BOT_TOKEN")
```

### Missing Input Validation
```python
# BAD - no validation
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    # process without validation

# GOOD - validate input
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    if not user_input or len(user_input) > 1000:
        await update.message.reply_text("Invalid input.")
        return
```

### No Rate Limiting
```python
from collections import defaultdict
from time import time

rate_limits = defaultdict(list)

def is_rate_limited(user_id: int, limit: int = 10, window: int = 60) -> bool:
    now = time()
    cutoff = now - window
    rate_limits[user_id] = [t for t in rate_limits[user_id] if t > cutoff]
    if len(rate_limits[user_id]) >= limit:
        return True
    rate_limits[user_id].append(now)
    return False
```

## References

- See `docs/16-security-audit.md` for complete security guide
- OWASP Top 10: https://owasp.org/
