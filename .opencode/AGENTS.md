# OpenCode Agents Configuration

## Agent Types

### Primary Agents
Main assistants you interact with directly. Switch with `Tab` key.

| Agent | Mode | Purpose |
|-------|------|---------|
| `build` | primary | Full development work with all tools |
| `plan` | primary | Analysis and planning without changes |

### Subagents
Specialized assistants invoked by primary agents or via `@mention`.

| Agent | Mode | Purpose |
|-------|------|---------|
| `code-reviewer` | subagent | Code quality review |
| `security-auditor` | subagent | Security vulnerability scanning |
| `telegram-bot-creator` | subagent | Bot implementation creation |

## Agent Locations

### Project Agents
**Location:** `.opencode/agents/`

```
.opencode/agents/
├── code-reviewer.md
├── security-auditor.md
└── telegram-bot-creator.md
```

### Global Agents
**Location:** `~/.config/opencode/agents/`

```
~/.config/opencode/agents/
├── my-custom-agent.md
└── another-agent.md
```

## Agent Configuration

### JSON Format (config.json)

```json
{
  "agent": {
    "my-agent": {
      "description": "What this agent does",
      "mode": "subagent",
      "model": "opencode/big-pickle",
      "temperature": 0.3,
      "permission": {
        "read": "allow",
        "edit": "deny",
        "bash": "ask"
      }
    }
  }
}
```

### Markdown Format (.md files)

```markdown
---
description: What this agent does
mode: subagent
model: opencode/big-pickle
temperature: 0.3
permission:
  read: allow
  edit: deny
  bash: ask
---

You are a specialized agent. Your instructions go here.
```

## Agent Options

| Option | Description | Values |
|--------|-------------|--------|
| `description` | What the agent does | Text |
| `mode` | How the agent can be used | `primary`, `subagent`, `all` |
| `model` | Model to use | `provider/model-id` |
| `temperature` | Response randomness | 0.0 - 1.0 |
| `permission` | Tool access control | See below |
| `steps` | Max agentic iterations | Number |
| `disable` | Disable the agent | `true`/`false` |
| `hidden` | Hide from autocomplete | `true`/`false` |
| `color` | UI appearance | Hex or theme color |

## Permission Keys

| Key | Tools |
|-----|-------|
| `read` | read |
| `edit` | write, edit, apply_patch |
| `bash` | bash |
| `grep` | grep |
| `glob` | glob |
| `skill` | skill |
| `todowrite` | todowrite, todoread |
| `webfetch` | webfetch |
| `websearch` | websearch |
| `question` | question |
| `task` | task (subagent invocation) |

### Permission Values

| Value | Description |
|-------|-------------|
| `allow` | Tool runs without asking |
| `ask` | Tool asks for user approval |
| `deny` | Tool is blocked |

### Fine-Grained Bash Permissions

```json
{
  "bash": {
    "*": "ask",
    "python *": "allow",
    "pip install *": "allow",
    "git status": "allow",
    "rm -rf *": "deny"
  }
}
```

## Usage

### Primary Agents
- Press `Tab` to cycle through primary agents
- Use configured keybind to switch

### Subagents

**Automatic invocation:**
```bash
# Primary agent invokes subagent for specialized tasks
@code-reviewer review this code
@security-auditor check for vulnerabilities
@telegram-bot-creator create a new bot
```

**Manual invocation:**
```bash
# In OpenCode TUI
@general help me search for this function
```

## Navigation

### Child Sessions
When subagents create child sessions:

| Key | Action |
|-----|--------|
| `<Leader>+Down` | Enter first child session |
| `Right` | Cycle to next child |
| `Left` | Cycle to previous child |
| `Up` | Return to parent |

## Built-in Agents

### Primary
- **build** — Full development work
- **plan** — Analysis and planning
- **compaction** — Context compaction (hidden)
- **title** — Session title generation (hidden)
- **summary** — Session summaries (hidden)

### Subagents
- **general** — General-purpose tasks
- **explore** — Read-only codebase exploration
- **scout** — External docs and dependency research

## Best Practices

1. **Use plan for analysis** — Prevents unintended changes
2. **Use subagents for parallel work** — Run multiple tasks simultaneously
3. **Set appropriate temperature** — Low for analysis, medium for coding
4. **Configure permissions** — Restrict dangerous operations
5. **Use hidden agents** — For internal automation

## Resources

- OpenCode Docs: https://opencode.ai
- Agent Skills: https://agentskills.io
