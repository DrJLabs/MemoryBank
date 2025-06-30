# Source Tree Integration

*The adapter service is completely independent with its own repository structure, separate from your existing Memory Bank Service codebase.*

## Existing Project Structure (Unchanged)

```plaintext
Memory-C*/
├── mem0/                    # Existing Memory Bank Service (unchanged)
├── docs/                    # Existing documentation (brownfield docs added)
├── scripts/                 # Existing scripts (unchanged)
└── tests/                   # Existing tests (unchanged)
```

## New File Organization

```plaintext
Memory-C*/
├── custom-gpt-adapter/      # New independent adapter service
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── search.py
│   │   │   │   │   ├── memories.py
│   │   │   │   │   └── health.py
│   │   │   │   └── __init__.py
│   │   │   └── dependencies.py
│   │   ├── auth/
│   │   │   ├── oauth.py
│   │   │   ├── jwt_handler.py
│   │   │   └── permissions.py
│   │   ├── services/
│   │   │   ├── memory_client.py
│   │   │   ├── audit_service.py
│   │   │   └── rate_limiter.py
│   │   ├── workers/
│   │   │   ├── memory_processor.py
│   │   │   └── celery_app.py
│   │   ├── models/
│   │   │   ├── custom_gpt.py
│   │   │   ├── audit.py
│   │   │   └── session.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── redis.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.worker
│   │   └── docker-compose.yml
│   ├── migrations/
│   │   └── alembic/
│   ├── monitoring/
│   │   ├── prometheus.yml
│   │   └── grafana/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
├── docs/                    # Existing docs with new brownfield additions
│   ├── brownfield-prd.md    # New - John's PRD
│   └── brownfield-architecture.md  # New - This document
```

## Integration Guidelines

- **File Naming:** Standard Python package conventions with `custom_gpt_` prefixes
- **Folder Organization:** Standard FastAPI microservice structure, independent from core service
- **Import/Export Patterns:** Standard Python imports, no dependencies on core service modules
