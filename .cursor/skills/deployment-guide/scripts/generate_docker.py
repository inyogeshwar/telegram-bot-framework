#!/usr/bin/env python3
"""Generate Docker configuration for Python applications."""

import sys
from pathlib import Path


def generate_dockerfile(app_name: str = "bot", port: int = 8080) -> str:
    """Generate a Dockerfile for a Python application."""
    return f"""FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{port}/health')" || exit 1

# Run application
CMD ["python", "{app_name}.py"]
"""


def generate_compose(app_name: str = "bot", port: int = 8080) -> str:
    """Generate docker-compose.yml."""
    return f"""version: "3.8"

services:
  {app_name}:
    build: .
    container_name: {app_name}
    restart: unless-stopped
    ports:
      - "{port}:{port}"
    environment:
      - BOT_TOKEN=${{BOT_TOKEN}}
      - DATABASE_URL=${{DATABASE_URL:-sqlite:///data/bot.db}}
      - LOG_LEVEL=${{LOG_LEVEL:-INFO}}
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:{port}/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
"""


def generate_dockerignore() -> str:
    """Generate .dockerignore content."""
    return """# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.production

# Documentation
*.md
LICENSE

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
Dockerfile
docker-compose.yml
"""


if __name__ == "__main__":
    app_name = sys.argv[1] if len(sys.argv) > 1 else "bot"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

    output_dir = Path(".")
    (output_dir / "Dockerfile").write_text(generate_dockerfile(app_name, port))
    (output_dir / "docker-compose.yml").write_text(generate_compose(app_name, port))
    (output_dir / ".dockerignore").write_text(generate_dockerignore())

    print(
        f"Generated Dockerfile, docker-compose.yml, and .dockerignore for '{app_name}'"
    )
