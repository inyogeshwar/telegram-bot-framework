<div align="center">

# Telegram Bot Framework

### The Most Comprehensive, AI-First, Enterprise-Grade Developer Handbook for Building Telegram Bots with Python

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB.svg)](https://www.python.org/downloads/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-v21.x-26A5E4.svg)](https://github.com/python-telegram-bot/python-telegram-bot)
[![Docs](https://img.shields.io/badge/docs-21%20chapters-brightgreen.svg)](docs/README.md)
[![Security](https://img.shields.io/badge/security-OWASP%20aligned-red.svg)](docs/16-security-audit.md)
[![Examples](https://img.shields.io/badge/examples-8%20production%20bots-orange.svg)](examples/)
[![AI Agents](https://img.shields.io/badge/AI-8%20agents%20supported-purple.svg)](#ai-agent-support)

---

**Build production-ready Telegram bots with Python — from zero to deployment.**

21 chapters | 8 production examples | 1900+ line reference | OWASP security audit | 8 AI agent configs

[Get Started](#quick-start) · [Documentation](docs/README.md) · [Examples](examples/) · [Security](docs/16-security-audit.md) · [Contributing](#contributing)

---

</div>

## Why This Repository?

| Problem | Solution |
|---------|----------|
| Fragmented Telegram bot tutorials | **21-chapter unified handbook** covering everything |
| Outdated v13 code examples | **100% v20+/v21.x** async/await patterns |
| No security guidance | **OWASP-aligned security audit** with checklists |
| AI agents generate wrong code | **8 AI agent configs** with hallucination prevention |
| No production examples | **8 production-quality bots** ready to deploy |
| Missing type hints | **PEP 484 typed** throughout every example |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/inyogeshwar/telegram-bot-framework.git
cd telegram-bot-framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your BOT_TOKEN from @BotFather

# 4. Run the echo bot
python examples/echo_bot.py
```

### Your First Bot in 30 Seconds

```python
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your bot.")

def main() -> None:
    app = ApplicationBuilder().token("YOUR_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
```

---

## Repository Structure

```
telegram-bot-framework/
├── docs/                           # 21-chapter developer handbook
│   ├── README.md                  # Table of contents
│   ├── COMPREHENSIVE-REFERENCE.md # Complete functions reference (1900+ lines)
│   ├── 00-introduction.md         # Getting started
│   ├── 01-architecture.md         # Bot architecture & API mechanics
│   ├── 02-installation.md         # Setup & project structure
│   ├── 03-configuration.md        # Environment & secrets management
│   ├── 04-handlers.md             # All handler types & patterns
│   ├── 05-filters.md              # Complete filter reference
│   ├── 06-keyboards.md            # Inline & reply keyboards
│   ├── 07-conversations.md        # ConversationHandler & FSM
│   ├── 08-media.md                # Photos, videos, documents, albums
│   ├── 09-formatting.md           # MarkdownV2, HTML, entities
│   ├── 10-inline-mode.md          # Inline queries & results
│   ├── 11-advanced.md             # Deep linking, jobs, persistence
│   ├── 12-payments.md             # Telegram Stars & payments
│   ├── 13-mini-apps.md            # Web Apps & Mini Apps
│   ├── 14-groups-channels.md      # Group & channel management
│   ├── 15-deployment.md           # Docker, webhooks, cloud hosting
│   ├── 16-security-audit.md       # OWASP security audit (2000+ lines)
│   ├── 17-testing.md              # pytest, mocks, debugging
│   ├── 18-faq.md                  # Common issues & solutions
│   ├── 19-appendix.md             # API quick reference
│   └── 20-agent-review.md         # AI agent guidance
├── examples/                       # 8 production-quality bots
│   ├── echo_bot.py               # Minimal echo bot
│   ├── ai_chatbot.py             # OpenAI-powered chatbot
│   ├── admin_bot.py              # Group admin & moderation
│   ├── payment_bot.py            # Telegram Stars payments
│   ├── conversation_bot.py       # Multi-step dialogs
│   ├── webhook_bot.py            # Production webhook deployment
│   ├── inline_bot.py             # Inline query mode
│   └── scheduled_bot.py          # JobQueue & reminders
├── .opencode/                      # OpenCode configuration
│   ├── config.json               # Main config with skills, references, formatters
│   └── skills/                   # 4 reusable skills
│       ├── telegram-bot/SKILL.md
│       ├── security-audit/SKILL.md
│       ├── deployment-guide/SKILL.md
│       └── bot-template/SKILL.md
├── .cursor/rules                   # Cursor AI rules
├── .clinerules                     # Cline configuration
├── .roo/rules                      # RooCode configuration
├── .continue/config.yaml           # Continue.dev config
├── .gemini/settings.json           # Gemini CLI config
├── CLAUDE.md                       # Claude Code instructions
├── AGENTS.md                       # AI agent workspace guidance
├── .github/                        # GitHub templates & CI/CD
├── pyproject.toml                  # Python project metadata
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── CONTRIBUTING.md                 # Contribution guidelines
├── SECURITY.md                     # Security policy
├── CHANGELOG.md                    # Version history
└── LICENSE                         # MIT License
```

---

## Documentation

### Complete Handbook (21 Chapters)

| Part | Chapters | Topics | Link |
|------|----------|--------|------|
| **I. Foundations** | 00-03 | Introduction, Architecture, Installation, Configuration | [Read →](docs/00-introduction.md) |
| **II. Core Concepts** | 04-07 | Handlers, Filters, Keyboards, Conversations | [Read →](docs/04-handlers.md) |
| **III. Features** | 08-11 | Media, Formatting, Inline Mode, Advanced | [Read →](docs/08-media.md) |
| **IV. Platforms** | 12-14 | Payments, Mini Apps, Groups & Channels | [Read →](docs/12-payments.md) |
| **V. Operations** | 15-17 | Deployment, Security Audit, Testing | [Read →](docs/15-deployment.md) |
| **VI. Reference** | 18-20 | FAQ, Appendix, Agent Review | [Read →](docs/18-faq.md) |

**[Read the Full Handbook →](docs/README.md)**

### Quick Reference

| Reference | Description | Link |
|-----------|-------------|------|
| **Functions Reference** | Every function, class, method, filter, handler | [View →](docs/COMPREHENSIVE-REFERENCE.md) |
| **Security Audit** | OWASP-aligned security guide with checklists | [View →](docs/16-security-audit.md) |
| **API Reference** | Telegram Bot API methods quick reference | [View →](docs/19-appendix.md) |
| **FAQ** | Common issues and solutions | [View →](docs/18-faq.md) |

---

## Code Examples

All examples follow these standards:

- **Async/await** — python-telegram-bot v20+ patterns
- **Fully typed** — PEP 484 type hints throughout
- **Production-ready** — error handling, logging, graceful shutdown
- **PEP 8 compliant** — consistent code style
- **Documented** — docstrings and inline comments where needed

### Available Examples

| Example | Description | Difficulty | Link |
|---------|-------------|------------|------|
| **Echo Bot** | Minimal echo bot — start here | Beginner | [View →](examples/echo_bot.py) |
| **AI Chatbot** | OpenAI-powered with rate limiting | Intermediate | [View →](examples/ai_chatbot.py) |
| **Admin Bot** | Group admin & moderation | Intermediate | [View →](examples/admin_bot.py) |
| **Payment Bot** | Telegram Stars integration | Intermediate | [View →](examples/payment_bot.py) |
| **Conversation Bot** | Multi-step dialogs with FSM | Intermediate | [View →](examples/conversation_bot.py) |
| **Webhook Bot** | Production webhook deployment | Advanced | [View →](examples/webhook_bot.py) |
| **Inline Bot** | Inline query mode | Intermediate | [View →](examples/inline_bot.py) |
| **Scheduled Bot** | JobQueue & reminders | Intermediate | [View →](examples/scheduled_bot.py) |

### Run Any Example

```bash
# Set your bot token
export BOT_TOKEN="your_token_here"

# Run any example
python examples/echo_bot.py
python examples/ai_chatbot.py
python examples/admin_bot.py
```

---

## AI Agent Support

This repository is optimized for every major AI coding agent:

| Agent | Config File | Features |
|-------|-------------|----------|
| **OpenCode** | `.opencode/config.json` | Skills, references, formatters, permissions |
| **Claude Code** | `CLAUDE.md` | System instructions, code patterns |
| **Cursor** | `.cursor/rules` | Project rules, code standards |
| **Cline** | `.clinerules` | Code generation rules |
| **RooCode** | `.roo/rules` | Code standards, patterns |
| **Continue.dev** | `.continue/config.yaml` | Project context |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Code suggestions |
| **Gemini CLI** | `.gemini/settings.json` | Project configuration |

### OpenCode Skills

| Skill | Description | Location |
|-------|-------------|----------|
| `telegram-bot` | Bot development guidance | `.opencode/skills/telegram-bot/SKILL.md` |
| `security-audit` | OWASP security review | `.opencode/skills/security-audit/SKILL.md` |
| `deployment-guide` | Production deployment | `.opencode/skills/deployment-guide/SKILL.md` |
| `bot-template` | Boilerplate generation | `.opencode/skills/bot-template/SKILL.md` |

### OpenCode References

| Reference | Description |
|-----------|-------------|
| `ptb-docs` | Official python-telegram-bot library source |
| `telegram-bot-api` | Official Telegram Bot API documentation |
| `handbook` | This repository's 21-chapter handbook |
| `examples` | Production bot code examples |

---

## Security

This repository follows OWASP security guidelines:

- **No hardcoded tokens** — Environment-based configuration
- **Input validation** — Sanitization examples in every handler
- **Rate limiting** — Token bucket & sliding window implementations
- **Webhook security** — Signature validation, secret tokens
- **Mini App validation** — HMAC-SHA256 `initData` verification
- **Dependency scanning** — GitHub Dependabot & CodeQL integration
- **Secret scanning** — Gitleaks pre-commit hooks

**[Read the Complete Security Audit →](docs/16-security-audit.md)**

---

## Project Highlights

### What Makes This Different

| Feature | This Repository | Other Tutorials |
|---------|-----------------|------------------|
| **Scope** | 21 chapters, 1900+ lines reference | 1-5 articles |
| **Version** | 100% v20+/v21.x | Often outdated v13 |
| **Security** | OWASP-aligned audit | Basic tips |
| **AI Support** | 8 agent configs | None |
| **Examples** | 8 production bots | 1-2 toy examples |
| **Type Hints** | PEP 484 throughout | Rarely used |
| **Testing** | pytest patterns | None |
| **Deployment** | Docker, webhooks, cloud | Basic instructions |

### Topics Covered

- Bot architecture & update cycle
- All 13 handler types
- 40+ filters with combinations
- Inline & reply keyboards
- ConversationHandler (FSM)
- Media handling (photos, videos, documents, albums)
- Message formatting (MarkdownV2, HTML)
- Inline mode & queries
- Deep linking & start parameters
- JobQueue & scheduled tasks
- Persistence & storage
- Telegram Stars & payments
- Mini Apps & Web Apps
- Group & channel management
- Forum topics
- Webhook deployment
- Docker & containerization
- Cloud hosting (Heroku, Fly.io, Railway, VPS)
- Unit testing & debugging
- Security hardening
- Performance optimization

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the list of contributors.

---

## Support

- **Documentation**: [docs/](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/inyogeshwar/telegram-bot-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/inyogeshwar/telegram-bot-framework/discussions)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author & Maintainer

**Yogeshwar Kumar** — [@inyogeshwar](https://github.com/inyogeshwar)

---

<div align="center">

**Built with care by Yogeshwar Kumar for the Python Telegram bot community**

[⬆ Back to Top](#telegram-bot-framework)

</div>
