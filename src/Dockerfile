# Use a lightweight Python image
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Install system dependencies and Rust in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    apt-get purge -y --auto-remove build-essential curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv and clean pip cache
RUN pip install --no-cache-dir uv==0.5.16

# Copy dependency files first for caching
COPY pyproject.toml uv.lock README.md ./

# Copy application code in a single layer
COPY src/frontend/templates /app/src/frontend/templates/
COPY src/bookmarker /app/src/bookmarker/
COPY src/tests /app/src/tests/

# Create virtual environment and install dependencies in one step
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e . && \
    uv sync

EXPOSE 8000

CMD [".venv/bin/uvicorn", "bookmarker.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]