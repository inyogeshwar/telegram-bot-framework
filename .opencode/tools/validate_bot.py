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
        tree = ast.parse(content)
    except SyntaxError as e:
        return [f"Syntax error: {e}"]

    # Check for async handlers
    has_async = any(isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree))
    if has_async:
        issues.append("OK: Async patterns used")
    else:
        issues.append("WARNING: No async functions found")

    # Check for hardcoded tokens
    if (
        "BOT_TOKEN" in content
        and "=" in content
        and any(
            token in content for token in ["'", '"', "123456:", "AAH", "your_token"]
        )
    ):
        issues.append("CRITICAL: Possible hardcoded token detected")

    # Check for error handler
    if "error_handler" in content:
        issues.append("OK: Error handler found")
    else:
        issues.append("WARNING: No error handler found")

    # Check for logging
    if "logging" in content or "logger" in content:
        issues.append("OK: Logging configured")
    else:
        issues.append("WARNING: No logging configured")

    # Check for type hints
    has_type_hints = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.returns or any(arg.annotation for arg in node.args.args)
        ):
            has_type_hints = True
            break

    if has_type_hints:
        issues.append("OK: Type hints present")
    else:
        issues.append("WARNING: Consider adding type hints")

    # Check for docstrings
    has_docstring = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        ):
            has_docstring = True
            break

    if has_docstring:
        issues.append("OK: Docstrings present")
    else:
        issues.append("INFO: Consider adding docstrings")

    if not issues:
        issues.append("SUCCESS: No major issues found")

    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_bot.py <bot_file>")
        sys.exit(1)

    results = validate_bot(sys.argv[1])
    for result in results:
        print(result)
