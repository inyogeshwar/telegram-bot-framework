---
description: Lint and format code
agent: build
---

Run linting and formatting checks on the codebase.

```bash
ruff check .
ruff format --check .
```

Report:
1. Any linting errors with file locations
2. Formatting issues
3. Suggest auto-fixes where possible
