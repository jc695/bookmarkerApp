FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install uv==0.5.16

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/frontend/templates /app/src/frontend/templates/
COPY src/bookmarker /app/src/bookmarker/
COPY src/tests /app/src/tests/
 
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e . && \
    uv sync

EXPOSE 8000

CMD [".venv/bin/uvicorn", "bookmarker.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]