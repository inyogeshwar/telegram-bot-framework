# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-25

### Added
- 21-chapter developer handbook covering all aspects of Telegram bot development
- Production-quality code examples (echo, AI chatbot, admin, payments, inline, scheduled)
- Complete security audit chapter with OWASP mapping
- AI agent-specific review and guidance
- GitHub issue templates (bug report, documentation, feature request)
- GitHub Actions workflows (code quality, security scan, documentation)
- AI ecosystem configurations (OpenCode, Claude Code, Cursor, Cline, RooCode, Continue.dev, Gemini CLI, GitHub Copilot)
- Skill definitions (telegram-bot, security, deployment)
- Agent configurations (telegram-bot-agent, security-agent)
- Command templates
- Bot templates (basic, conversation, webhook)
- API reference quick guide
- System prompt for AI agents
- CONTRIBUTING.md
- SECURITY.md
- CHANGELOG.md
- pyproject.toml
- requirements.txt
- .env.example

### Security
- Removed sensitive files from repository
- Added .gitignore for tokens, logs, and sensitive data
- Implemented GitHub secret scanning with CodeQL
- Added gitleaks integration for pre-commit hooks
- All example tokens replaced with placeholders
