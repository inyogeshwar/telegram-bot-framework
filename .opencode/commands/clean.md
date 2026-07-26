---
description: Clean project files
agent: build
---

Clean temporary and cache files from the project.

Remove:
```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Test artifacts
rm -rf .pytest_cache htmlcov .coverage

# Build artifacts
rm -rf dist build *.egg-info

# IDE files
rm -rf .vscode/.history .idea

# Logs
rm -rf logs *.log
```

Verify cleanup:
```bash
git status
```

Report what was cleaned.
