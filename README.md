# Telegram Bot Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-v21.x-green.svg)](https://github.com/python-telegram-bot/python-telegram-bot)
[![Docs](https://img.shields.io/badge/docs-complete-brightgreen.svg)](docs/README.md)
[![Security Audit](https://img.shields.io/badge/security-OWASP%20aligned-red.svg)](docs/16-security-audit.md)

**The most comprehensive, AI-first, enterprise-grade developer handbook for building Telegram bots with Python.**

---

## What Is This?

An open-source, production-ready documentation platform for the `python-telegram-bot` library (v20+/v21.x). Built for developers, maintained for AI agents.

## Who Is This For?

- **Python developers** building Telegram bots
- **Backend engineers** adding chatbot functionality
- **AI coding agents** (OpenCode, Claude Code, Cursor, Copilot, and 10+ others)
- **Automation enthusiasts** creating workflow bots
- **Students** learning bot development

## Repository Structure

```
telegram-bot-framework/
├── docs/                    # 21-chapter developer handbook
│   ├── README.md           # Table of contents
│   ├── 00-introduction.md  # Getting started
│   ├── 01-architecture.md  # Bot architecture
│   ├── ...                 # Chapters 02-19
│   └── 20-agent-review.md  # AI agent specific guidance
├── examples/               # Production-quality code examples
│   ├── echo_bot.py         # Minimal echo bot
│   ├── ai_chatbot.py       # AI-powered chatbot
│   ├── admin_bot.py        # Group admin bot
│   ├── payment_bot.py      # Telegram Stars payments
│   └── ...                 # More examples
├── .github/                # GitHub templates & CI/CD
├── .opencode/              # OpenCode configuration
├── .cursor/                # Cursor rules
├── CLAUDE.md               # Claude Code instructions
├── .clinerules             # Cline configuration
├── pyproject.toml          # Python project metadata
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── LICENSE                 # MIT License
└── AGENTS.md               # AI agent workspace guidance
```

## Quick Start

```bash
# Clone
git clone https://github.com/inyogeshwar/telegram-bot-framework.git
cd telegram-bot-framework

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token

# Run the echo bot
python examples/echo_bot.py
```

## Documentation

| Part | Chapters | Topics |
|------|----------|--------|
| **I. Foundations** | 00-03 | Introduction, Architecture, Installation, Configuration |
| **II. Core Concepts** | 04-07 | Handlers, Filters, Keyboards, Conversations |
| **III. Features** | 08-11 | Media, Formatting, Inline Mode, Advanced |
| **IV. Platforms** | 12-14 | Payments, Mini Apps, Groups & Channels |
| **V. Operations** | 15-17 | Deployment, Security Audit, Testing |
| **VI. Reference** | 18-20 | FAQ, Appendix, Agent Review |

**[Read the Full Handbook →](docs/README.md)**

## Code Examples

All examples follow these standards:

- **Async/await** — python-telegram-bot v20+ patterns
- **Fully typed** — PEP 484 type hints throughout
- **Production-ready** — error handling, logging, graceful shutdown
- **PEP 8 compliant** — consistent code style
- **Documented** — docstrings and inline comments where needed

## AI Agent Support

This repository is designed to work with every major AI coding agent:

| Agent | Config File | Status |
|-------|-------------|--------|
| OpenCode | `.opencode/config.json` | Supported |
| Claude Code | `CLAUDE.md` | Supported |
| Cursor | `.cursor/rules` | Supported |
| Cline | `.clinerules` | Supported |
| RooCode | `.roo/rules` | Supported |
| Continue.dev | `.continue/config.yaml` | Supported |
| GitHub Copilot | `.github/copilot-instructions.md` | Supported |
| Gemini CLI | `.gemini/settings.json` | Supported |

## Security

This repository follows OWASP security guidelines:

- No hardcoded tokens or secrets
- Environment-based configuration
- Input validation examples
- Rate limiting patterns
- Comprehensive [Security Audit](docs/16-security-audit.md)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yogeshwar Kumar** — [GitHub](https://github.com/inyogeshwar)

---

*Built with care for the Python Telegram bot community.*
