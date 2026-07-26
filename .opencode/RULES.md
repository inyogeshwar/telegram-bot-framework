# OpenCode Rules Configuration

## Rule File Locations

OpenCode supports multiple locations for rule files:

### 1. Project Rules (AGENTS.md)

**Location:** Project root directory

**Purpose:** Project-specific rules shared with team

**Example:**
```
telegram-bot-framework/
├── AGENTS.md          # Project rules
├── docs/
├── examples/
└── ...
```

### 2. Global Rules

**Location:** `~/.config/opencode/AGENTS.md`

**Purpose:** Personal rules across all projects

**Windows Path:**
```
C:\Users\<username>\.config\opencode\AGENTS.md
```

**Example:**
```markdown
# Personal Coding Rules

## Style Preferences
- Use 4 spaces for indentation
- Prefer functional programming
- Write concise code

## Workflow
- Always run tests before committing
- Use conventional commits
- Review code before pushing
```

### 3. Claude Code Compatibility

**Location:** `~/.claude/CLAUDE.md`

**Purpose:** Rules from Claude Code (fallback)

**Windows Path:**
```
C:\Users\<username>\.claude\CLAUDE.md
```

## Precedence Order

1. Local `AGENTS.md` (project root)
2. Global `~/.config/opencode/AGENTS.md`
3. Claude Code `~/.claude/CLAUDE.md` (fallback)

**Note:** If both `AGENTS.md` and `CLAUDE.md` exist, only `AGENTS.md` is used.

## Custom Instructions

You can reference external instruction files in `opencode.json`:

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/**/*.md",
    "examples/**/*.py"
  ]
}
```

This allows you to:
- Reuse existing documentation
- Keep `AGENTS.md` concise
- Share rules across projects
- Reference remote files

## Remote Instructions

You can also load instructions from remote URLs:

```json
{
  "instructions": [
    "https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"
  ]
}
```

**Note:** Remote instructions have a 5-second timeout.

## Disabling Claude Code Compatibility

If you don't want OpenCode to read from `.claude/`:

```bash
# Disable all .claude support
export OPENCODE_DISABLE_CLAUDE_CODE=1

# Disable only ~/.claude/CLAUDE.md
export OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1

# Disable only .claude/skills
export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1
```

## Best Practices

1. **Commit project rules** — `AGENTS.md` should be in Git
2. **Keep global rules personal** — Don't commit `~/.config/opencode/AGENTS.md`
3. **Use external references** — Reference detailed docs in `instructions`
4. **Be concise** — Focus on what future sessions need to know
5. **Include commands** — Build, lint, test commands are essential

## Resources

- OpenCode Docs: https://opencode.ai
- Agent Skills: https://agentskills.io
