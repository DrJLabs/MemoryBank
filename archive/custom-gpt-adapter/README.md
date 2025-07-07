# Custom GPT Adapter Service

This service provides an adapter for integrating ChatGPT Custom GPTs with the Memory Bank Service. It manages OAuth authentication, application credentials, rate limiting, and provides secure API endpoints for memory operations.

## Overview

The Custom GPT Adapter Service is a completely independent microservice that:
- Provides OAuth 2.0 authentication for Custom GPT applications
- Offers REST API endpoints for memory search and creation
- Implements rate limiting and circuit breaker patterns
- Processes operations asynchronously for scalability
- Maintains comprehensive audit logs
- Operates with zero impact on the core Memory Bank Service

## Project Structure

- `app/`: FastAPI application code
  - `api/`: API endpoints and routes
  - `core/`: Core configuration and utilities
  - `models/`: Database models
  - `workers/`: Celery background workers
  - `clients/`: External service clients
- `docker/`: Docker configurations
- `monitoring/`: Prometheus and Grafana configs
- `scripts/`: Deployment and management scripts
- `tests/`: Unit and integration tests
- `migrations/`: Alembic database migrations

## Quick Start

For development:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up --build
```

For production deployment, see the [Deployment Guide](./DEPLOYMENT_GUIDE.md).

## API Documentation

The service provides the following main endpoints:

- `POST /auth/token` - OAuth 2.0 token generation
- `POST /api/v1/search` - Search memories
- `POST /api/v1/memories` - Create new memories
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics

Generate full API documentation:
```bash
python scripts/manage/generate_api_docs.py
```

## Management

Create a Custom GPT application:
```bash
python scripts/manage/manage_custom_gpt_app.py create "My GPT" --rate-limit "100/minute"
```

For more management commands, see the [Deployment Guide](./DEPLOYMENT_GUIDE.md).

## Development Status

This service was developed as part of Epic 1 (stories 1.1-1.6) and is now ready for operational deployment (story 1.7).

## License

This project is part of the Memory Bank Service ecosystem. 