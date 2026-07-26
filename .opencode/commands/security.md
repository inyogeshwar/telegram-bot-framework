---
description: Security audit
agent: security-auditor
subtask: true
---

Perform a security audit on the codebase.

!`find . -name "*.py" -type f | head -20`

Check for:
1. Hardcoded secrets or tokens
2. SQL injection vulnerabilities
3. Command injection risks
4. Input validation issues
5. Authentication flaws
6. Dependency vulnerabilities

Run dependency check:

```bash
pip-audit 2>/dev/null || echo "pip-audit not installed"
```

Report findings with severity levels:
- CRITICAL: Immediate fix required
- HIGH: Fix soon
- MEDIUM: Consider fixing
- LOW: Nice to have
