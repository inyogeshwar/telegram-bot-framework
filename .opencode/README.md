# OpenCode Configuration

This directory contains OpenCode CLI configurations for the Telegram Bot Framework.

## Structure

```
.opencode/
├── config.json          # Main configuration file
├── .env.example         # Environment variables template
├── agents/              # Custom agent definitions
│   ├── telegram-bot-creator.md
│   ├── security-auditor.md
│   └── code-reviewer.md
├── mcp/                 # MCP server configurations
│   └── servers.json
└── skills/              # Skill definitions
    ├── telegram-bot/
    ├── security-audit/
    ├── deployment-guide/
    └── bot-template/
```

## Quick Start

### 1. Configure Environment

```bash
cp .opencode/.env.example .env
# Edit .env with your API keys
```

### 2. Start OpenCode

```bash
# Start TUI
opencode

# Or run with specific agent
opencode --agent telegram-bot-creator
```

### 3. Use Skills

Skills are automatically discovered. Use them via:

```bash
# In OpenCode TUI
/telegram-bot
/security-audit
/deployment-guide
/bot-template
```

## Commands

### Session Management

```bash
# List sessions
opencode session list

# Continue last session
opencode --continue

# Continue specific session
opencode --session <session-id>
```

### Agent Management

```bash
# List available agents
opencode agent list

# Create new agent
opencode agent create
```

### MCP Servers

```bash
# List MCP servers
opencode mcp list

# Add MCP server
opencode mcp add
```

### Run Commands

```bash
# Run without TUI
opencode run "Explain how closures work"

# Run with specific model
opencode run --model anthropic/claude-sonnet-4-20250514 "Explain async/await"
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `OPENCODE_AUTO_SHARE` — Auto-share sessions
- `OPENCODE_DISABLE_AUTOUPDATE` — Disable auto-updates
- `OPENCODE_EXPERIMENTAL` — Enable experimental features
- `OPENCODE_SERVER_PASSWORD` — Server authentication

## Resources

- OpenCode Documentation: https://opencode.ai
- Agent Skills Standard: https://agentskills.io
- MCP Protocol: https://modelcontextprotocol.io
