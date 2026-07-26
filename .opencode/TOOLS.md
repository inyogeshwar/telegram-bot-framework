# OpenCode Custom Tools

## Overview

Custom tools are functions you create that the LLM can call during conversations. They work alongside OpenCode's built-in tools like read, write, and bash.

## Tool Locations

### Project Tools
**Location:** `.opencode/tools/`

```
.opencode/tools/
├── validate-bot.ts      # TypeScript definition
├── validate_bot.py      # Python implementation
├── security-audit.ts
├── security_audit.py
├── generate-docker.ts
├── generate_docker.py
├── review-code.ts
├── review_code.py
├── math.ts
├── project-info.ts
└── search-imports.ts
```

### Global Tools
**Location:** `~/.config/opencode/tools/`

## Tool Structure

### TypeScript Definition

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Tool description",
  args: {
    param: tool.schema.string().describe("Parameter description"),
  },
  async execute(args, context) {
    // Tool implementation
    return "result"
  },
})
```

### Multiple Tools Per File

```typescript
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return (args.a + args.b).toString()
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return (args.a * args.b).toString()
  },
})
```

**Result:** Creates `math_add` and `math_multiply` tools.

## Context Object

Tools receive context about the current session:

```typescript
async execute(args, context) {
  const { agent, sessionID, messageID, directory, worktree } = context
  // directory = session working directory
  // worktree = git worktree root
}
```

## Current Tools

### validate-bot
Validates Telegram bot code for best practices.

```bash
# Usage in TUI
validate-bot bot.py
```

**Checks:**
- Async patterns
- Hardcoded tokens
- Error handling
- Logging
- Type hints
- Docstrings

### security-audit
Runs security audit on Python files.

```bash
# Usage in TUI
security-audit bot.py
```

**Checks:**
- Hardcoded secrets
- SQL injection
- eval/exec usage
- Unsafe YAML
- Debug mode
- HTTP without TLS

### generate-docker
Generates Docker configuration.

```bash
# Usage in TUI
generate-docker mybot 8080
```

**Generates:**
- Dockerfile
- docker-compose.yml
- .dockerignore

### review-code
Reviews Python code quality.

```bash
# Usage in TUI
review-code bot.py
```

**Checks:**
- Docstrings
- Type hints
- Async patterns
- Error handling
- Logging
- Line length
- Hardcoded values

### math
Performs math operations.

```bash
# Usage in TUI
math add 5 3
math multiply 4 2
```

### project-info
Gets project statistics.

```bash
# Usage in TUI
project-info
```

**Returns:**
- File counts
- Git information
- Directory structure

### search-imports
Searches for Python imports.

```bash
# Usage in TUI
search-imports telegram
```

**Searches:**
- Import statements
- From imports
- Requirements files

## Python Scripts

### validate_bot.py
```python
#!/usr/bin/env python3
"""Validate Telegram bot code for best practices."""

import ast
import sys
from pathlib import Path


def validate_bot(filepath: str) -> list[str]:
    # Validation logic
    pass
```

### security_audit.py
```python
#!/usr/bin/env python3
"""Security audit script for Python applications."""

import re
import sys
from pathlib import Path


def audit_security(filepath: str) -> list[dict]:
    # Audit logic
    pass
```

### generate_docker.py
```python
#!/usr/bin/env python3
"""Generate Docker configuration for Python applications."""

import sys
from pathlib import Path


def generate_dockerfile(app_name: str, port: int) -> str:
    # Generation logic
    pass
```

### review_code.py
```python
#!/usr/bin/env python3
"""Code review script for Python files."""

import ast
import sys
from pathlib import Path


def review_code(filepath: str) -> dict:
    # Review logic
    pass
```

## Best Practices

1. **Use TypeScript for definitions** — Type-safe tool definitions
2. **Use Python for logic** — Easier to implement complex operations
3. **Handle errors gracefully** — Return meaningful error messages
4. **Validate inputs** — Check required parameters
5. **Use context** — Access session and directory information
6. **Document tools** — Clear descriptions and parameter docs

## Resources

- OpenCode Docs: https://opencode.ai
- Plugin API: https://opencode.ai/docs/plugins
