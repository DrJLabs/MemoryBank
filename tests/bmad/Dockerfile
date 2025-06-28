# BMAD Testing Framework Docker Container
# Provides isolated environment for running comprehensive BMAD test suites

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies for testing
RUN pip install --no-cache-dir \
    pytest==8.3.5 \
    pytest-cov==6.1.1 \
    pytest-xdist==3.6.1 \
    pytest-timeout==2.3.1 \
    pytest-html==4.1.1 \
    coverage==7.6.1

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Create test reports directory
RUN mkdir -p /app/reports/bmad

# Default command runs all BMAD tests with coverage
CMD ["pytest", "tests/bmad/", "-v", "--cov=.bmad-core", "--cov-report=html:/app/reports/bmad/coverage", "--cov-report=term", "--html=/app/reports/bmad/test-report.html", "--self-contained-html"] 