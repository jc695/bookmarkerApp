# Use a lightweight Python image
FROM python:3.9-slim

# Prevent Python from writing .pyc files and ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system build dependencies, including curl for installing rustup
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl

# Install rustup and the latest stable Rust toolchain (ensures rustc >= 1.75)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install the UV dependency manager
RUN pip install uv

# Copy dependency descriptor files
COPY ./fastapi-backend/pyproject.toml ./fastapi-backend/uv.lock ./

# Copy frontend templates into the container
COPY ../frontend/templates ./frontend/templates 

# Activate venv
RUN uv venv

# Export a pip-compatible requirements file from uv.lock using the correct format flag
RUN uv export --format=requirements-txt > requirements.txt

# Install dependencies into the system environment using uv (now with updated rustc)
RUN uv pip install -r requirements.txt

# Copy the rest of your application code
COPY ./fastapi-backend .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start your FastAPI application using uv's run command
CMD ["uv", "run", "uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
