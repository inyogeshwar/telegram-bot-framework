#!/usr/bin/env python3
"""Scaffold a new bot project structure."""

import sys
from pathlib import Path


def scaffold_bot(name: str, description: str = "") -> None:
    """Create bot project directory structure."""
    bot_dir = Path(name)

    # Create directories
    (bot_dir / "tests").mkdir(parents=True, exist_ok=True)

    # Create __init__.py for tests
    (bot_dir / "tests" / "__init__.py").touch()

    print(f"Created project structure for '{name}'")
    print(f"Directory: {bot_dir}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scaffold.py <bot_name>")
        sys.exit(1)

    scaffold_bot(sys.argv[1])
