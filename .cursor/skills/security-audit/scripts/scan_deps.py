#!/usr/bin/env python3
"""Scan Python dependencies for known vulnerabilities."""

import subprocess
import sys


def scan_dependencies() -> None:
    """Scan dependencies using pip-audit."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print("No vulnerabilities found.")
        else:
            print("Vulnerabilities detected:")
            print(result.stdout)

    except FileNotFoundError:
        print("pip-audit not installed. Install with: pip install pip-audit")
        sys.exit(1)


if __name__ == "__main__":
    scan_dependencies()
