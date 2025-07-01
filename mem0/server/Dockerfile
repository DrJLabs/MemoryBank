FROM python:3.12.2-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user and group for running the API (security best-practice, Context7 Docker Hardening)
RUN addgroup --system --gid 1001 mem0 && \
    adduser  --system --uid 1001 --gid 1001 --home /app mem0 && \
    chown -R mem0:mem0 /app

USER mem0

# Expose the FastAPI port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Add a basic health-check so orchestrators can detect failures (Context7 Docker Patterns)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Use Uvicorn in production mode (no auto-reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
