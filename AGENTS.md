# AGENTS.md

## Overview

This is a flat workspace of standalone Python scripts — no package structure, no build system, no test framework, no CI.

## Conventions

- Scripts are single-file, mostly Python 3. Dependencies vary per script (requests, etc.) — check imports at the top of each file.
- No shared modules or internal libraries. Each script is self-contained.
- Output files (`.txt`, `.log`) are generated artifacts, not source of truth.
- `__pycache__/` can be ignored.

## Running scripts

```
python <script>.py
```

No special setup, environment variables, or virtual environment is enforced. Individual scripts may require API tokens or credentials referenced in their code.
