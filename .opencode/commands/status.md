---
description: Show project status
agent: build
---

Show comprehensive project status.

## Git Status
!`git status`

## Recent Commits
!`git log --oneline -10`

## Code Quality
```bash
ruff check . --statistics 2>/dev/null || echo "No linting issues"
```

## Test Status
```bash
pytest --tb=no -q 2>/dev/null || echo "No tests configured"
```

## Dependencies
```bash
pip list --format=columns | grep -E "telegram|python"
```

## Disk Usage
```bash
du -sh . --exclude=.git 2>/dev/null || dir /s /b *.py 2>nul | find /c /v ""
```

Summarize:
- Project health
- Areas needing attention
- Suggested next steps
