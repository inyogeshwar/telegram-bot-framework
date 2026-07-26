#!/usr/bin/env python3
"""Validate Telegram bot code for best practices."""

import ast
import sys
from pathlib import Path


def validate_bot(filepath: str) -> list[str]:
    """Validate a bot file for common issues."""
    issues = []
    path = Path(filepath)

    if not path.exists():
        return [f"File not found: {filepath}"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Parse AST
    try:
        ast.parse(content)
    except SyntaxError as e:
        return [f"Syntax error: {e}"]

    # Check for hardcoded tokens
    if (
        "BOT_TOKEN" in content
        and "=" in content
        and any(
            token in content for token in ["'", '"', "123456:", "AAH", "your_token"]
        )
    ):
        issues.append("WARNING: Possible hardcoded token detected")

    # Check for error handler
    if "error_handler" not in content:
        issues.append("INFO: No error handler found")

    # Check for logging
    if "logging" not in content:
        issues.append("INFO: No logging configured")

    # Check for type hints
    if "-> None" not in content and "async def" in content:
        issues.append("INFO: Consider adding return type hints")

    if not issues:
        issues.append("SUCCESS: No major issues found")

    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <bot_file>")
        sys.exit(1)

    results = validate_bot(sys.argv[1])
    for result in results:
        print(result)
