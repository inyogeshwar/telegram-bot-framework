#!/usr/bin/env python3
"""Linting and formatting check script."""

import subprocess


def run_linting() -> None:
    """Run ruff linter and formatter check."""
    print("Running ruff linter...")
    result = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Linting passed!")
    else:
        print("Linting issues found:")
        print(result.stdout)

    print("\nRunning ruff formatter check...")
    result = subprocess.run(
        ["ruff", "format", "--check", "."],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Formatting check passed!")
    else:
        print("Formatting issues found:")
        print(result.stdout)


if __name__ == "__main__":
    run_linting()
