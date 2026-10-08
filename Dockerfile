# =====================================================
# Stage 1: Builder
# =====================================================

ARG PYTHON_IMAGE=docker.io/library/python:3.12-slim

FROM ${PYTHON_IMAGE} AS builder

WORKDIR /app

# Build-time pip configuration
ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST

ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL}
ENV PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# =====================================================
# Stage 2: Runtime
# =====================================================

FROM ${PYTHON_IMAGE}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=builder /usr/local/bin /usr/local/bin

# Runtime files
COPY app ./app
COPY alembic ./alembic
COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY alembic.ini ./alembic.ini

RUN chmod +x docker-entrypoint.sh && \
    useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["./docker-entrypoint.sh"]
