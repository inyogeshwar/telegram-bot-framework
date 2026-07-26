#!/usr/bin/env python3
"""Security audit script for Python applications."""

import re
import sys
from pathlib import Path


def audit_security(filepath: str) -> list[dict]:
    """Perform security audit on a Python file."""
    findings = []
    path = Path(filepath)

    if not path.exists():
        return [{"severity": "CRITICAL", "message": f"File not found: {filepath}"}]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Check for hardcoded secrets
    secret_patterns = [
        (r"['\"](\d{10}:[A-Za-z0-9_-]{35})['\"]", "Telegram bot token"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
        (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
        (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret"),
    ]

    for pattern, desc in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(
                {
                    "severity": "CRITICAL",
                    "message": f"{desc} detected - use environment variables",
                }
            )

    # Check for SQL injection risks
    if "execute(" in content and "%" in content:
        findings.append(
            {
                "severity": "HIGH",
                "message": "Possible SQL injection - use parameterized queries",
            }
        )

    # Check for eval/exec usage
    if "eval(" in content or "exec(" in content:
        findings.append(
            {
                "severity": "HIGH",
                "message": "eval/exec usage detected - potential code injection",
            }
        )

    # Check for unsafe YAML loading
    if "yaml.load(" in content and "Loader=" not in content:
        findings.append(
            {
                "severity": "MEDIUM",
                "message": "Unsafe YAML loading - use yaml.safe_load()",
            }
        )

    # Check for debug mode
    if "debug=True" in content or "DEBUG=True" in content:
        findings.append(
            {
                "severity": "LOW",
                "message": "Debug mode enabled - disable in production",
            }
        )

    if not findings:
        findings.append({"severity": "SUCCESS", "message": "No security issues found"})

    return findings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit.py <file>")
        sys.exit(1)

    results = audit_security(sys.argv[1])
    for result in results:
        print(f"[{result['severity']}] {result['message']}")
