#!/usr/bin/env python3
"""Initialize project dependencies."""

import subprocess
import sys


def setup_project() -> None:
    """Install project dependencies."""
    print("Installing dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        check=True,
    )

    print("\nInitializing git repository...")
    subprocess.run(
        ["git", "init"],
        check=False,
    )

    print("\nProject setup complete!")


if __name__ == "__main__":
    setup_project()
