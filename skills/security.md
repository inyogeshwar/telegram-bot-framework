# Security Skill

## Overview
This skill provides security guidelines for Telegram bot development.

## When to Use
- Implementing authentication
- Validating user input
- Handling sensitive data
- Deploying bots

## Key Principles

### 1. Never Hardcode Secrets
```python
# Bad
TOKEN = "1234567890:ABC123..."

# Good
import os
TOKEN = os.getenv("BOT_TOKEN")
```

### 2. Validate Input
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    
    # Validate input
    if not user_input or len(user_input) > 1000:
        await update.message.reply_text("Invalid input.")
        return
    
    # Process safe input
```

### 3. Implement Rate Limiting
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

### 4. Use Webhook Signatures
```python
from telegram import Update

async def webhook_handler(request):
    update = Update.de_json(await request.json(), bot)
    # Validate webhook secret
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return Response(status=403)
```

### 5. Log Securely
```python
import logging

logger = logging.getLogger(__name__)

# Good - log user ID, not token
logger.info("Message from user %s", user.id)

# Bad - never log tokens
logger.info("Token: %s", token)  # NEVER DO THIS
```

## OWASP Top 10 Mapping
1. **Injection** - Validate and sanitize all input
2. **Broken Authentication** - Use proper token management
3. **Sensitive Data Exposure** - Never log secrets
4. **XML External Entities** - Not applicable (JSON API)
5. **Broken Access Control** - Implement RBAC
6. **Security Misconfiguration** - Use environment variables
7. **Cross-Site Scripting** - Escape user input
8. **Insecure Deserialization** - Validate webhook data
9. **Known Vulnerabilities** - Keep dependencies updated
10. **Insufficient Logging** - Log security events

## References
- [Security Audit Chapter](../docs/16-security-audit.md)
- [OWASP Guidelines](https://owasp.org/)
