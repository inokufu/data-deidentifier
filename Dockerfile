ARG VARIANT=3.13.11-slim-bookworm
# Base stage
FROM python:${VARIANT} AS base
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

## Dev with mounted volumes and dev deps
FROM base AS dev

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY pyproject.toml uv.lock ./

VOLUME ["/app/src", "/app/tests"]
CMD ["uv", "run", "start"]

# Standalone dev with code included
FROM base AS dev-standalone

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY tests ./tests

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

CMD ["uv", "run", "start"]

## Prod with copied code and minimal deps
FROM base AS prod

# Install dependencies only (intermediate layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy source code
COPY pyproject.toml uv.lock gunicorn.conf.py ./
COPY src ./src

# Install project with bytecode compilation and non-editable mode
ENV UV_COMPILE_BYTECODE=1
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"

CMD ["gunicorn", "data_deidentifier.adapters.api.main:app"]
