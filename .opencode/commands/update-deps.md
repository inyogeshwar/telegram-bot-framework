---
description: Update dependencies
agent: build
---

Update project dependencies to latest versions.

Steps:
1. Check current versions in requirements.txt
2. Check for security vulnerabilities
3. Update to latest stable versions
4. Run tests to verify compatibility

Commands:
```bash
# Check outdated
pip list --outdated

# Update
pip install --upgrade python-telegram-bot python-dotenv

# Generate new requirements
pip freeze > requirements.txt

# Test
pytest
```

Report:
- Updated packages
- Breaking changes
- Security fixes
- Compatibility issues
