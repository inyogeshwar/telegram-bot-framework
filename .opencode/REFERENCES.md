# OpenCode References Configuration

## Overview

References give OpenCode access to directories outside the current project. Use them to make documentation, shared libraries, examples, or another repository available while you work.

## Reference Types

### Local Directories

```json
{
  "references": {
    "docs": {
      "path": "./docs",
      "description": "Use for documentation and tutorials"
    }
  }
}
```

**Path Types:**
- Relative: `./docs`, `../shared`
- Absolute: `/home/user/docs`
- Home directory: `~/docs`

**String Shorthand:**
```json
{
  "references": {
    "docs": "./docs"
  }
}
```

### Git Repositories

```json
{
  "references": {
    "ptb-docs": {
      "repository": "python-telegram-bot/python-telegram-bot",
      "branch": "master",
      "description": "Use for python-telegram-bot library source"
    }
  }
}
```

**Repository Formats:**
- GitHub shorthand: `owner/repo`
- Full URL: `https://github.com/owner/repo.git`
- Git URL: `git@github.com:owner/repo.git`

**String Shorthand:**
```json
{
  "references": {
    "ptb-docs": "python-telegram-bot/python-telegram-bot"
  }
}
```

## Reference Fields

| Field | Local | Git | Description |
|-------|-------|-----|-------------|
| `path` | Yes | No | Local reference directory |
| `repository` | No | Yes | Git URL or owner/repo |
| `branch` | No | Yes | Optional Git branch or ref |
| `description` | Yes | Yes | When to use this reference |
| `hidden` | Yes | Yes | Hide from @ autocomplete |

## Current References

### ptb-docs (Git)
```json
{
  "repository": "python-telegram-bot/python-telegram-bot",
  "branch": "master",
  "description": "Use for python-telegram-bot library source, API reference, and implementation details"
}
```

### telegram-bot-api (Git)
```json
{
  "repository": "Telegram/Telegram-Bot-API",
  "branch": "main",
  "description": "Use for official Telegram Bot API documentation and specifications"
}
```

### handbook (Local)
```json
{
  "path": "./docs",
  "description": "Use for this repository's 22-chapter developer handbook and tutorials"
}
```

### examples (Local)
```json
{
  "path": "./examples",
  "description": "Use for production-quality bot code examples and patterns"
}
```

### templates (Local)
```json
{
  "path": "./templates",
  "description": "Use for bot project templates and scaffolding"
}
```

## Usage

### TUI Autocomplete

Type `@` to see available references:

```
@ptb-docs/    # Browse python-telegram-bot source
@handbook/    # Browse documentation
@examples/    # Browse examples
```

### In Commands

```bash
# Compare implementation with reference
Compare this implementation with @ptb-docs/ext/application.py

# Check documentation
Read @handbook/03-configuration.md

# Use example code
See @examples/echo_bot.py
```

### Agent Context

References with descriptions are automatically included in agent context. Agents can inspect references when relevant without manual attachment.

## Best Practices

1. **Add descriptions** — Help agents know when to use each reference
2. **Use specific branches** — Pin to stable branches for consistency
3. **Hide internal refs** — Use `hidden: true` for non-essential references
4. **Keep paths relative** — Easier to share across teams
5. **Document usage** — Explain when each reference should be used

## Example Configuration

```json
{
  "references": {
    "docs": {
      "path": "./docs",
      "description": "Use for project documentation"
    },
    "sdk": {
      "repository": "owner/sdk",
      "branch": "main",
      "description": "Use for SDK implementation details"
    },
    "internal": {
      "path": "../shared-libs",
      "description": "Use for shared components",
      "hidden": true
    }
  }
}
```

## Resources

- OpenCode Docs: https://opencode.ai
- References: https://opencode.ai/docs/references
