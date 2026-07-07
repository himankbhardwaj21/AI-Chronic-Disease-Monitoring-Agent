# ============================================================
# ChronicCare AI — Dockerfile
# Multi-stage build for production-ready container image.
# IBM watsonx University Engagement Project
# ============================================================

# ── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install Python dependencies into a separate prefix (for clean copy)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN groupadd --gid 1001 chroniccare \
    && useradd --uid 1001 --gid 1001 --no-create-home --shell /bin/false chroniccare

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=chroniccare:chroniccare . .

# Create data directory for SQLite and set permissions
RUN mkdir -p /app/data && chown -R chroniccare:chroniccare /app/data

# Switch to non-root user
USER chroniccare

# Expose application port
EXPOSE 5000

# Environment defaults (override at runtime via --env-file or -e flags)
ENV FLASK_ENV=production \
    PORT=5000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check — Render and Kubernetes compatible
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Production startup via gunicorn
CMD ["gunicorn", "wsgi:app", \
     "--workers", "2", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
