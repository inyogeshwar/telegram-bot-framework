# Contributing to Telegram Bot Framework

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include reproduction steps
4. Provide environment details

### Suggesting Features

1. Check existing issues
2. Use the feature request template
3. Explain the use case
4. Provide examples if possible

### Improving Documentation

1. Use the documentation template
2. Specify the exact chapter/section
3. Provide the improvement
4. Explain why it's needed

### Submitting Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Follow the code standards
5. Submit a pull request

## Code Standards

### Python Code

- Use python-telegram-bot v20+ (async/await)
- PEP 484 type hints
- PEP 8 style guidelines
- Error handling and logging
- Docstrings for all functions

### Documentation

- Markdown format
- Code examples with type hints
- Mermaid diagrams where applicable
- Clear, concise language

## Development Setup

```bash
# Clone repository
git clone https://github.com/inyogeshwar/telegram-bot-framework.git
cd telegram-bot-framework

# Install dependencies
pip install -r requirements.txt

# Run linter
ruff check .

# Type check
mypy .
```

## Pull Request Process

1. Update documentation if needed
2. Add examples if applicable
3. Ensure code passes linting
4. Write clear commit messages
5. Request review

## Security

- Never commit tokens or secrets
- Use environment variables
- Validate all input
- Report security issues privately

## Questions?

Open an issue with the "question" label.
