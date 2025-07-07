# ICE-graph

This project contains the core database, vector store, graph database, FastAPI API services, and UI dashboard extracted from MemoryBank.

## Directory Structure
- **vector_stores/**: database backends
- **graph/**: graph memory implementations
- **memory/**: core memory logic
- **api/**: FastAPI services
- **embeddings/**: embedding models
- **llms/**: LLM wrappers
- **ui/**: Next.js dashboard
- **config/**: configuration files
- **utils/**: shared utilities

## Setup
1. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Start the FastAPI server:
```bash
uvicorn api.main:app --reload --port 8765
```
3. Start the UI:
```bash
cd ui
pnpm install
pnpm run dev --port 3010
```

## Docker
A docker-compose.yml will be provided to spin up Postgres, Neo4j, and the API/UI services.
