# MemoryBank Centralized Dependencies

This directory contains consolidated dependency files to replace the scattered `requirements*.txt` files throughout the project.

## Dependency Categories

### Core Dependencies (`core.txt`)
Essential runtime packages required for production operation:
- Web framework (FastAPI, Uvicorn)
- Database (SQLAlchemy, PostgreSQL)
- Authentication & security
- Task queues & caching
- Monitoring & observability

### AI/ML Dependencies (`ai.txt`)
Machine learning and AI-specific packages:
- Vector databases (ChromaDB, Pinecone, Weaviate, Faiss)
- LLM providers (OpenAI, Groq, Together, Ollama)
- Search engines (Elasticsearch, OpenSearch)
- Graph databases for memory
- ML libraries and embeddings

### Testing Dependencies (`test.txt`)
Comprehensive testing framework:
- Core testing (pytest ecosystem)
- AI testing enhancements
- Performance testing
- Security testing
- CI/CD integration tools

### Development Dependencies (`dev.txt`)
Development tools and utilities:
- Code quality (ruff, black, mypy)
- Documentation tools
- Debugging & profiling
- Build & packaging tools

### Examples Dependencies (`examples.txt`)
Dependencies for demo applications and examples:
- UI frameworks (Streamlit, Flask)
- Communication integrations (Discord, Slack)
- Content processing tools
- Media handling libraries

## Usage

### Install All Dependencies
```bash
# Core runtime (required)
pip install -r dependencies/core.txt

# AI/ML capabilities
pip install -r dependencies/ai.txt

# Development tools
pip install -r dependencies/dev.txt

# Testing framework
pip install -r dependencies/test.txt

# Example applications
pip install -r dependencies/examples.txt
```

### Install Specific Categories
```bash
# Production deployment
pip install -r dependencies/core.txt -r dependencies/ai.txt

# Development environment
pip install -r dependencies/core.txt -r dependencies/ai.txt -r dependencies/dev.txt -r dependencies/test.txt

# CI/CD pipeline
pip install -r dependencies/core.txt -r dependencies/test.txt
```

### Poetry Integration
Add to `pyproject.toml`:
```toml
[tool.poetry.dependencies]
# Core dependencies from dependencies/core.txt

[tool.poetry.group.ai.dependencies]
# AI dependencies from dependencies/ai.txt

[tool.poetry.group.dev.dependencies]
# Development dependencies from dependencies/dev.txt

[tool.poetry.group.test.dependencies]
# Testing dependencies from dependencies/test.txt
```

## Migration Status

### Replaced Files
The following scattered requirements files are now consolidated:
- `requirements-testing.txt` → `dependencies/test.txt`
- `custom-gpt-adapter/requirements.txt` → `dependencies/core.txt`
- `mem0/requirements-dev.txt` → `dependencies/ai.txt` + `dependencies/dev.txt`
- 24+ example requirements files → `dependencies/examples.txt`

### Legacy Files
Original requirements files are preserved for compatibility during migration.
They will be removed after successful validation of the new structure.

## Best Practices

1. **Version Pinning**: Use `>=` for minimum versions to allow updates
2. **Security**: Regularly update `dependencies/test.txt` for security scanning tools
3. **AI Updates**: Monitor `dependencies/ai.txt` for ML library updates
4. **Examples**: Keep `dependencies/examples.txt` lightweight for demos

## Validation

Test the consolidated dependencies:
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Test core functionality
pip install -r dependencies/core.txt
pip install -r dependencies/ai.txt

# Run basic tests
python -c "import fastapi, sqlalchemy, sentence_transformers; print('Dependencies OK')"
``` 