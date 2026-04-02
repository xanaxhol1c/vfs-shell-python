# Multi-stage build: Stage 1 - Build environment with all tools
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install Poetry and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry via pip (more reliable than curl method)
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install Python dependencies into .venv
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-directory --only main

# Copy source code
COPY src/ /app/src/
COPY main.py /app/main.py
COPY vfs_config.json* /app/

# Verify installation using the venv Python
RUN /app/.venv/bin/python -c "import rich; print('Dependencies verified')"


# Stage 2 - Runtime environment (minimal and lightweight)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 vfsuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/vfs_config.json* /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Change ownership to non-root user
RUN chown -R vfsuser:vfsuser /app

# Switch to non-root user
USER vfsuser

# Default command: start interactive shell
ENTRYPOINT ["python", "/app/main.py"]
