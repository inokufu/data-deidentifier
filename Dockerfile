ARG VARIANT=3.13-slim-bookworm

# Base stage
FROM python:${VARIANT} AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/0.9.14/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY gunicorn.conf.py pyproject.toml ./

## Dev with mounted volumes and dev deps
FROM base AS dev
COPY requirements-dev.lock ./
RUN uv pip install --system -r requirements-dev.lock
COPY src ./src
CMD ["gunicorn", "src.data_deidentifier.adapters.api.main:app"]

# Standalone dev with code included
FROM dev AS dev-standalone
COPY tests ./tests
VOLUME ["/app/src", "/app/tests"]

## Prod with copied code and minimal deps
FROM base AS prod
COPY requirements.lock ./
RUN uv pip install --system --no-deps --no-compile -r requirements.lock
COPY src ./src

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "src.data_deidentifier.adapters.api.main:app"]
