# Enhanced Mem0 Dockerfile with Infisical Integration
# Architecture: MemoryBank Infisical Integration Architecture v1.0
# Pattern: Container Secret Injection with Infisical CLI

FROM python:3.11-slim

# Install system dependencies and Infisical CLI
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Infisical CLI
RUN curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | bash \
    && apt-get update \
    && apt-get install -y infisical \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r mem0 && useradd -r -g mem0 mem0
RUN chown -R mem0:mem0 /app
USER mem0

# Expose application port
EXPOSE 8000

# Health check with secret validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command with Infisical secret injection
CMD ["infisical", "run", "--env=dev", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 