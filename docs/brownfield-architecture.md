# MemoryBank Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the MemoryBank codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements.

### Document Scope

Comprehensive documentation of entire system

### Change Log

|   |   |   |   |
|---|---|---|---|
|**Date**|**Version**|**Description**|**Author**|
|2025-07-07|1.0|Initial brownfield analysis|Mary (Business Analyst)|

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `mem0/server/main.py`
    
- **Configuration**: `.bmad-core/core-config.yml`
    
- **Core Business Logic**: `mem0/mem0/memory/main.py`
    
- **API Definitions**: `mem0/openmemory/api/app/routers/memories.py`
    
- **Database Models**: `mem0/openmemory/api/app/models.py`
    
- **Key Algorithms**: `mem0/mem0/memory/main.py` , `mem0/mem0/memory/graph_memory.py`
    

## High Level Architecture

### Technical Summary

MemoryBank employs a hybrid monolithic-microservice architecture within a monorepo structure, combining a stable mem0 core with modular openmemory components. The system integrates advanced AI analytics, predictive modeling, and workflow automation while maintaining enterprise-grade reliability and performance. Core architectural patterns include event-driven processing for real-time updates, repository pattern for data abstraction, and plugin architecture for extensible AI model integration.

### Actual Tech Stack (from package.json/requirements.txt)

|   |   |   |   |
|---|---|---|---|
|**Category**|**Technology**|**Version**|**Notes**|
|Runtime|Python|3.12+|Production-ready|
|Framework|FastAPI|Latest|RESTful API with OpenAPI|
|Database|PostgreSQL|13+|Primary relational storage|
|Vector DB|Configurable|Latest|Vector storage (Chroma/Pinecone)|
|Cache|Redis|7.0|In-memory caching|
|API Style|REST + GraphQL|-|API interfaces|
|Testing|pytest + hypothesis|7.4.0|Test framework|
|IaC Tool|Docker Compose|2.20|Infrastructure|
|Monitoring|Prometheus|2.45|Metrics collection|

### Repository Structure Reality Check

- **Type**: Monorepo
    
- **Package Manager**: npm/pnpm and pip
    
- **Notable**: The project is structured as a monorepo with multiple components, including the core `mem0` library, a `mem0-ts` TypeScript implementation, an `openmemory` enterprise layer, an `embedchain` legacy integration, and a `custom-gpt-adapter` service.
    

## Source Tree and Module Organization

### Project Structure (Actual)

```
memorybank/
├── .bmad-core/           # BMad framework core
├── .github/              # GitHub Actions workflows
├── .codacy/              # Codacy configuration
├── ADVANCED_MEMORY_SYSTEM_GUIDE.md
├── archive/              # Archived files
├── app/                  # FastAPI application
├── docs/                 # Documentation
├── infrastructure/       # Infrastructure scripts
├── mem0/                 # Core memory library
│   ├── mem0/
│   │   ├── cli/
│   │   ├── client/
│   │   ├── configs/
│   │   ├── embeddings/
│   │   ├── llms/
│   │   ├── memory/
│   │   └── vector_stores/
│   ├── mem0-ts/
│   └── openmemory/
├── monitoring/           # Monitoring configurations
├── quality/              # Quality gates
├── reports/              # Test reports
├── scripts/              # Various scripts
└── tests/                # Test suites
```

### Key Modules and Their Purpose

- **mem0**: The core library for the memory system. It includes modules for handling embeddings, LLMs, vector stores, and the main memory operations.
    
- **openmemory**: An enterprise layer on top of `mem0` that provides advanced features like a dashboard UI, enhanced monitoring, and more robust API functionalities.
    
- **.bmad-core**: Contains the BMad agent framework for development, including definitions for agents, tasks, templates, and workflows.
    
- **custom-gpt-adapter**: A separate FastAPI service to integrate with ChatGPT Custom GPTs.
    

## Data Models and APIs

### Data Models

- **SQLAlchemy Models**: Defined in `mem0/openmemory/api/app/models.py`, these models represent the database schema for users, applications, memories, and their states.
    
- **Pydantic Models**: Used for API request and response validation, defined in `mem0/openmemory/api/app/schemas.py`.
    

### API Specifications

- **OpenAPI Spec**: The API documentation is available at the `/docs` endpoint of the running API server, as is standard for FastAPI applications. A pre-generated `openapi.json` is available in `mem0/docs/openapi.json`.
    

## Technical Debt and Known Issues

- **Mixed Backend Implementations**: The `mem0` library has both Python and TypeScript implementations, which could lead to inconsistencies.
    
- **Legacy Components**: The `embedchain` directory appears to be a legacy component that is still integrated.
    
- **Fragmented Monitoring**: There are multiple monitoring and analytics scripts and configurations scattered across the project.
    
- **Stale Content**: An `archive` directory contains a large number of files that are likely outdated but have been kept for reference.
    

## Integration Points and External Dependencies

### External Services

|   |   |   |
|---|---|---|
|**Service**|**Purpose**|**Integration Type**|
|OpenAI|LLM and Embedding services|REST API|
|Anthropic|LLM services|REST API|
|Google|LLM and Embedding services|REST API|
|Infisical|Secret Management|CLI & API|
|GitHub|Version Control and Project Management|REST API & GraphQL|

### Internal Integration Points

- **Frontend/Backend Communication**: The Next.js frontend communicates with the FastAPI backend via REST APIs.
    
- **Background Jobs**: Celery is used for asynchronous task processing with Redis as the message broker.
    

## Development and Deployment

### Local Development Setup

The project uses Docker Compose for setting up the local development environment. Several `docker-compose.yml` files are present for different configurations (testing, production, with/without Infisical).

### Build and Deployment Process

- **Build**: The `web-builder.js` tool is used to create web-ready bundles for the BMad framework.
    
- **Deployment**: The `.github/workflows` directory contains GitHub Actions for CI/CD, including deployment to Infisical-secured environments.
    

## Testing Reality

### Current Test Coverage

- **Unit Tests**: The `tests` directory contains a large number of unit tests for the various components of the project.
    
- **Integration Tests**: There are several integration tests, particularly for the memory system and its components.
    
- **E2E Tests**: End-to-end tests are present for the `custom-gpt-adapter` service.
    

### Running Tests

Tests are run using `pytest`. The `pytest.ini` file in the root directory contains the configuration for the test suite.

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

- `npx bmad-method install`: Installs the BMad framework in the IDE.
    
- `docker-compose up`: Starts the local development environment.
    
- `./start-with-infiscal.sh start`: Starts the services with Infisical integration.
    
- `./scripts/setup-testing-environment.sh`: Sets up the testing environment.
    

### Debugging and Troubleshooting

- **Logs**: The project has extensive logging configured, with logs being written to files in the `logs` directory.
    
- **Debug Mode**: The FastAPI application can be run in debug mode for more verbose output.