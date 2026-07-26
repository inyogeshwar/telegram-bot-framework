---
description: Run tests with coverage
agent: build
---

Run the full test suite with coverage report and show any failures.

```bash
pytest -v --cov=. --cov-report=term-missing
```

Focus on:
1. Any failing tests
2. Coverage gaps
3. Test quality issues
4. Suggest fixes for failures
