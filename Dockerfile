# Docker image for the FastAPI employee portal.
#
# Cloud Run sends traffic to the port stored in the PORT environment variable.
# The default below is 8080, which is Cloud Run's standard container port.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# Keeps uv installs fast and predictable inside Docker.
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PORT=8080

# Copy dependency files first so Docker can cache dependency installation.
COPY pyproject.toml uv.lock ./

# Install only application dependencies, not dev/test dependencies.
RUN uv sync --frozen --no-dev --no-install-project

# Copy the FastAPI app and the files it needs to render pages.
COPY app.py ./
COPY static ./static
COPY templates ./templates
COPY models ./models

EXPOSE 8080

# Start the FastAPI app with Uvicorn.
# app:app means "use the app variable inside app.py".
CMD ["sh", "-c", "uv run uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
