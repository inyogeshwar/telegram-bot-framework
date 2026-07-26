#!/usr/bin/env python3
"""Code review script for Python files."""

import ast
import sys
from pathlib import Path


def review_code(filepath: str) -> dict:
    """Perform code review on a Python file."""
    path = Path(filepath)
    results = {
        "score": 10,
        "critical": [],
        "warnings": [],
        "suggestions": [],
        "positive": [],
    }

    if not path.exists():
        results["critical"].append(f"File not found: {filepath}")
        results["score"] = 0
        return results

    with open(path, encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        results["critical"].append(f"Syntax error: {e}")
        results["score"] = 0
        return results

    # Check for docstrings
    has_docstring = False
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        ):
            has_docstring = True
            break

    if has_docstring:
        results["positive"].append("Docstrings present")
    else:
        results["warnings"].append("Consider adding docstrings")
        results["score"] -= 1

    # Check for type hints
    has_type_hints = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.returns or any(arg.annotation for arg in node.args.args)
        ):
            has_type_hints = True
            break

    if has_type_hints:
        results["positive"].append("Type hints present")
    else:
        results["warnings"].append("Consider adding type hints")
        results["score"] -= 1

    # Check for async functions
    has_async = any(isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree))
    if has_async:
        results["positive"].append("Async patterns used")
    else:
        results["suggestions"].append("Consider using async/await patterns")

    # Check for error handling
    has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
    if has_try:
        results["positive"].append("Error handling present")
    else:
        results["warnings"].append("Consider adding error handling")
        results["score"] -= 1

    # Check for logging
    has_logging = "logging" in content or "logger" in content
    if has_logging:
        results["positive"].append("Logging configured")
    else:
        results["suggestions"].append("Consider adding logging")

    # Check line length
    long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 88]
    if long_lines:
        results["warnings"].append(f"Long lines found: {long_lines[:5]}...")
        results["score"] -= 1

    # Check for hardcoded values
    if "localhost" in content or "127.0.0.1" in content:
        results["warnings"].append("Hardcoded localhost found")
        results["score"] -= 1

    # Ensure score doesn't go below 0
    results["score"] = max(0, results["score"])

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review.py <file>")
        sys.exit(1)

    results = review_code(sys.argv[1])

    print("Code Review Results")
    print("=" * 50)
    print(f"Overall Score: {results['score']}/10\n")

    if results["critical"]:
        print("CRITICAL ISSUES:")
        for issue in results["critical"]:
            print(f"  ❌ {issue}")

    if results["warnings"]:
        print("\nWARNINGS:")
        for warning in results["warnings"]:
            print(f"  ⚠️  {warning}")

    if results["suggestions"]:
        print("\nSUGGESTIONS:")
        for suggestion in results["suggestions"]:
            print(f"  💡 {suggestion}")

    if results["positive"]:
        print("\nPOSITIVE ASPECTS:")
        for positive in results["positive"]:
            print(f"  ✅ {positive}")
