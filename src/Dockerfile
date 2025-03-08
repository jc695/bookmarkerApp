# Use a lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system build dependencies, including curl for rustup
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install rustup and the latest stable Rust toolchain (ensures rustc >= 1.75)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install uv 0.5.16 explicitly
RUN pip install uv==0.5.16

# Copy dependency descriptor files and README from the root
COPY ./pyproject.toml ./uv.lock ./README.md ./

# Copy frontend templates
COPY ./src/frontend/templates # ./src/frontend/templates/

# Copy the app source code
COPY ./src/app ./src/app/

# Create virtual environment and install dependencies in one RUN command
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e . && \
    uv sync

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI application using the virtual environment's uvicorn
CMD [".venv/bin/uvicorn", "bookmarker.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]