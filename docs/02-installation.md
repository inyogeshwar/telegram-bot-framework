# Chapter 2: Installation & Project Setup

This chapter walks you through installing `python-telegram-bot`, setting up a
virtual environment, and structuring your project for long-term maintainability.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installing the Library](#installing-the-library)
- [Virtual Environment](#virtual-environment)
- [Verifying the Installation](#verifying-the-installation)
- [Project Structure](#project-structure)
- [Dependency Management](#dependency-management)
- [Git Ignore Rules](#git-ignore-rules)
- [IDE Recommendations](#ide-recommendations)

---

## Prerequisites

| Requirement | Minimum Version | Recommended |
|-------------|-----------------|-------------|
| Python      | 3.8             | 3.11+       |
| pip         | 21.0            | 23.0+       |
| git         | 2.30            | latest      |

> [!NOTE]
> Python 3.11+ provides significant performance improvements and better error
> messages. If you are starting a new project, there is little reason to target
> anything older.

Verify your Python version:

```bash
python --version
# Python 3.11.4
```

---

## Installing the Library

Install the latest stable release from PyPI:

```bash
pip install python-telegram-bot
```

This pulls in only the core dependencies required for basic bot functionality.

### Extended Install (Optional Dependencies)

To install **all** optional extras — including the `JobQueue` (backed by
`APScheduler`), rate-limiting support, and persistence backends — use the `[all]`
extra:

```bash
pip install "python-telegram-bot[all]"
```

| Extra          | Provides                              | Use Case                        |
|----------------|---------------------------------------|---------------------------------|
| `job-queue`    | APScheduler-based `JobQueue`          | Scheduled messages, reminders   |
| `rate-limiter` | Token-bucket rate limiter             | Protect downstream APIs         |
| `ext`          | All extensions bundled together       | Full-featured production bots   |

> [!TIP]
> Start with the base install during development. Add extras only when you
> actually need the feature to keep your dependency tree small.

---

## Virtual Environment

Always isolate project dependencies inside a virtual environment.

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (macOS / Linux)
source venv/bin/activate
```

Your shell prompt should now show `(venv)` to indicate the active environment.

To deactivate:

```bash
deactivate
```

> [!WARNING]
> Never install production dependencies system-wide. A virtual environment
> prevents version conflicts between unrelated projects.

---

## Verifying the Installation

Run a quick smoke test to confirm everything is wired correctly:

```python
# verify_install.py
import telegram

print(f"python-telegram-bot version: {telegram.__version__}")
```

```bash
python verify_install.py
# python-telegram-bot version: 20.7
```

You can also confirm the CLI entry point is available:

```bash
python -m telegram --version
```

---

## Project Structure

The following layout scales from a small hobby bot to a production system with
multiple handler modules, database models, and background jobs.

```
my_telegram_bot/
├── bot.py                 # Entry point — creates and runs the Application
├── config.py              # Centralized configuration (env vars, constants)
├── handlers/              # Command and message handlers
│   ├── __init__.py
│   ├── start.py           # /start, /help, and onboarding flows
│   ├── admin.py           # Admin-only commands
│   └── user.py            # General user-facing commands
├── models/                # Database models / schemas
│   ├── __init__.py
│   └── user.py            # User model, ORM definitions
├── utils/                 # Shared utilities
│   ├── __init__.py
│   └── helpers.py         # Formatting, date helpers, sanitization
├── keyboards/             # Keyboard builders
│   ├── __init__.py
│   └── inline.py          # Inline and reply keyboard factories
├── middlewares/            # Pre/post-processing hooks (optional)
│   ├── __init__.py
│   └── rate_limiter.py
├── .env                   # Environment variables (NEVER commit)
├── .gitignore
├── requirements.txt       # Pinned production dependencies
├── requirements-dev.txt   # Development / testing dependencies
└── Dockerfile             # Container build definition
```

### Why This Structure?

| Directory      | Responsibility                                    |
|----------------|---------------------------------------------------|
| `handlers/`    | One module per domain — keeps `handle_message()` functions short and testable. |
| `models/`      | Isolates database schema from business logic.      |
| `utils/`       | Pure functions with no Telegram-specific imports.  |
| `keyboards/`   | Centralizes inline/reply markup construction.      |
| `middlewares/` | Cross-cutting concerns like rate limiting and logging. |

> [!IMPORTANT]
> Every directory listed above must contain an `__init__.py` file. It may be
> empty, but it marks the directory as a Python package so imports resolve
> correctly.

---

## Dependency Management

### requirements.txt

Pin your production dependencies to exact versions for reproducible builds:

```
# requirements.txt — production
python-telegram-bot==20.7
python-dotenv==1.0.0
sqlalchemy==2.0.23
redis==5.0.1
gunicorn==21.2.0
```

### requirements-dev.txt

Development and testing dependencies live in a separate file:

```
# requirements-dev.txt — development only
-r requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
ruff==0.1.14
mypy==1.8.0
pre-commit==3.6.0
```

Install both sets:

```bash
# Production only
pip install -r requirements.txt

# Production + development tools
pip install -r requirements-dev.txt
```

---

## Git Ignore Rules

Add the following to your `.gitignore` to keep secrets and build artifacts out
of version control:

```gitignore
# .gitignore

# Virtual environment
venv/
.venv/
env/

# Python bytecode
__pycache__/
*.py[cod]
*$py.class

# Environment variables
.env
.env.*
!.env.example

# Database files
*.db
*.sqlite3

# IDE / editor
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Distribution
dist/
build/
*.egg-info/

# Docker
docker-compose.override.yml
```

> [!CAUTION]
> The `.env` file contains your `BOT_TOKEN` and other secrets. It **must never**
> be committed. Use `.env.example` (with placeholder values) to document the
> required variables for other developers.

Create a template for collaborators:

```bash
# .env.example
BOT_TOKEN=your-bot-token-here
DATABASE_URL=sqlite:///bot.db
REDIS_URL=redis://localhost:6379
ADMIN_IDS=123456789
LOG_LEVEL=INFO
```

---

## IDE Recommendations

| IDE / Editor               | Why It Works Well                                   |
|----------------------------|-----------------------------------------------------|
| **VS Code** + Python ext   | IntelliSense, debugging, remote containers, free.   |
| **PyCharm Professional**   | Best-in-class refactoring, database tools, profiler.|
| **Neovim** + LSP           | Lightweight, fast, full Python language server.     |

### VS Code Settings (suggested)

Add these to `.vscode/settings.json` for a consistent experience:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [88, 120],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

---

## Next Steps

With the project scaffolded and dependencies installed, move on to
[Chapter 3: Configuration & Environment](./03-configuration.md) to learn how
to manage secrets, database connections, and environment-specific settings.
