# OpenCode Permissions Reference

## Tool Permissions

OpenCode uses a simple permission system to control what the LLM can do.

### Permission Values

| Value | Description |
|-------|-------------|
| `allow` | Tool runs without asking |
| `deny` | Tool is blocked |
| `ask` | Tool asks for user approval |

### Built-in Tools

| Tool | Description | Default |
|------|-------------|---------|
| `read` | Read file contents | allow |
| `edit` | Modify files (edit, write, apply_patch) | allow |
| `bash` | Execute shell commands | allow |
| `grep` | Search file contents | allow |
| `glob` | Find files by pattern | allow |
| `skill` | Load skill files | allow |
| `todowrite` | Manage todo lists | allow |
| `webfetch` | Fetch web content | allow |
| `websearch` | Search the web | allow |
| `question` | Ask user questions | allow |
| `lsp` | LSP server interaction | deny (experimental) |

### Configuration Examples

#### Basic Configuration
```json
{
  "permission": {
    "read": "allow",
    "edit": "allow",
    "bash": "ask",
    "grep": "allow",
    "glob": "allow"
  }
}
```

#### Restrictive Configuration
```json
{
  "permission": {
    "read": "allow",
    "edit": "ask",
    "bash": "deny",
    "grep": "allow",
    "glob": "allow"
  }
}
```

#### Per-Command Bash Permissions
```json
{
  "permission": {
    "bash": {
      "python *": "allow",
      "pip install *": "allow",
      "pytest *": "allow",
      "ruff *": "allow",
      "mypy *": "allow",
      "git status": "allow",
      "git log *": "allow",
      "git diff *": "allow",
      "rm -rf *": "deny",
      "git push --force *": "deny"
    }
  }
}
```

### MCP Server Permissions

Control permissions for MCP server tools using wildcards:

```json
{
  "permission": {
    "mymcp_*": "ask",
    "filesystem_*": "allow",
    "github_*": "ask"
  }
}
```

## Environment Variables

### Permission-Related Variables

| Variable | Description |
|----------|-------------|
| `OPENCODE_PERMISSION` | Inline JSON permissions config |
| `OPENCODE_AUTO_SHARE` | Auto-share sessions |

### Security Variables

| Variable | Description |
|----------|-------------|
| `OPENCODE_SERVER_PASSWORD` | Server authentication |
| `OPENCODE_SERVER_USERNAME` | Server username (default: opencode) |

## Best Practices

1. **Development**: Use `allow` for read/edit, `ask` for bash
2. **Production**: Use `deny` for bash, `ask` for edit
3. **CI/CD**: Use `allow` for all tools (automated environment)
4. **Learning**: Use `ask` for everything (see what LLM does)

## Resources

- OpenCode Docs: https://opencode.ai
- Permission System: https://opencode.ai/docs/permissions
