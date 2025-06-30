# Memory Bank Service - Brownfield Architecture Document

## Introduction
This document captures the CURRENT STATE of the Memory Bank Service codebase for **ChatGPT Custom GPT Integration** enhancement. It documents the existing enterprise AI-powered memory management system, technical patterns, and integration points needed for the new ChatGPT Custom GPT connection feature.

### Document Scope
Focused on areas relevant to: **Adding ChatGPT Custom GPT integration to existing Memory Bank Service**

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-17 | 1.0 | Initial brownfield analysis for ChatGPT Custom GPT integration | Winston (Architect) |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System
- **Main Entry**: `mem0/server/main.py` - FastAPI server with core memory endpoints
- **Memory Core**: `mem0/mem0/memory/main.py` - Main Memory class with CRUD operations
- **API Client**: `mem0/mem0/client/main.py` - MemoryClient for external integrations
- **MCP Server**: `mem0/openmemory/api/app/mcp_server.py` - Model Context Protocol server
- **Configuration**: `mem0/mem0/configs/` - Various config files for different components
- **Database Models**: `mem0/openmemory/api/app/models.py` - SQLAlchemy models
- **Core API Routes**: `mem0/openmemory/api/app/routers/memories.py` - Memory management endpoints

### Enhancement Impact Areas - ChatGPT Custom GPT Integration
**Files that will be affected by ChatGPT Custom GPT integration:**
- `mem0/mem0/client/main.py` - Add ChatGPT Custom GPT client integration
- `mem0/openmemory/api/app/routers/` - New ChatGPT integration endpoints
- `mem0/mem0/configs/` - New ChatGPT configuration files
- `mem0/server/main.py` - Add ChatGPT Custom GPT endpoints
- `mem0/openmemory/api/app/mcp_server.py` - Add ChatGPT Custom GPT MCP tools

## High Level Architecture

### Technical Summary
**Current Architecture Assessment:** Well-structured enterprise system with excellent separation of concerns, comprehensive API design, and mature AI/ML pipeline. The system is production-ready with robust error handling and professional monitoring.

### Actual Tech Stack (from analysis)
| Category | Technology | Version | Notes |
|----------|------------|---------|-------|
| Runtime | Python | 3.12+ | Production-ready |
| Framework | FastAPI | Latest | RESTful API with OpenAPI |
| Database | SQLite/PostgreSQL | 13+ | Dual support with SQLAlchemy |
| Vector DB | Qdrant | Latest | Semantic search capabilities |
| AI/ML | scikit-learn | Latest | 97.5% accuracy models |
| Container | Docker | Latest | Microservices architecture |
| Memory System | Mem0 | Custom | Enterprise memory management |
| Integration | MCP | Latest | Model Context Protocol |

### Repository Structure Reality Check
- **Type**: Monorepo with multiple specialized modules
- **Package Manager**: pip with requirements.txt
- **Notable**: Sophisticated multi-component architecture with clear separation

## Source Tree and Module Organization

### Project Structure (Actual)
```
Memory-C*/
├── mem0/
│   ├── mem0/
│   │   ├── memory/
│   │   │   ├── main.py          # Core Memory class - CRITICAL for ChatGPT integration
│   │   │   ├── base.py          # Abstract base class for memory operations
│   │   │   └── sync_manager.py  # Synchronization between stores
│   │   ├── client/
│   │   │   └── main.py          # MemoryClient - KEY integration point
│   │   ├── configs/             # Configuration management
│   │   ├── llms/                # LLM integrations (20+ providers)
│   │   ├── embeddings/          # Embedding models (14+ providers)
│   │   └── vector_stores/       # Vector store implementations
│   ├── server/
│   │   └── main.py              # FastAPI server - will need ChatGPT endpoints
│   ├── openmemory/
│   │   ├── api/
│   │   │   ├── app/
│   │   │   │   ├── routers/
│   │   │   │   │   └── memories.py  # Core memory API routes
│   │   │   │   ├── mcp_server.py    # MCP server for tool integration
│   │   │   │   └── models.py        # Database models
│   │   │   └── main.py          # OpenMemory API server
│   │   ├── github-projects-integration.py  # GitHub integration example
│   │   └── working-memory-dashboard.py     # Web dashboard
│   └── docs/
│       └── openapi.json         # Complete API documentation
├── docs/
│   ├── architecture.md          # System architecture
│   └── brownfield-architecture.md  # Brownfield enhancement patterns
└── README.md                    # Project overview and setup
```

### Key Modules and Their Purpose
- **Memory Core** (`mem0/mem0/memory/main.py`): Main Memory class with get/set/search/delete operations
- **API Client** (`mem0/mem0/client/main.py`): MemoryClient for external integrations - **CRITICAL for ChatGPT**
- **FastAPI Server** (`mem0/server/main.py`): Core REST API with memory endpoints
- **MCP Server** (`mem0/openmemory/api/app/mcp_server.py`): Model Context Protocol for tool integration
- **OpenMemory API** (`mem0/openmemory/api/`): Advanced memory management with permissions
- **LLM Integrations** (`mem0/mem0/llms/`): 20+ LLM providers including OpenAI

## Data Models and APIs

### Core Memory Model (from mem0/mem0/memory/base.py)
```python
class MemoryBase(ABC):
    @abstractmethod
    def get(self, memory_id): pass
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def update(self, memory_id, data): pass
    @abstractmethod
    def delete(self, memory_id): pass
    @abstractmethod
    def history(self, memory_id): pass
```

### API Specifications
- **OpenAPI Spec**: `mem0/docs/openapi.json` - Comprehensive API documentation
- **Core Endpoints**:
  - `GET /v1/memories/` - List all memories with filtering
  - `POST /v1/memories/` - Create new memory
  - `GET /v1/memories/{memory_id}` - Get specific memory
  - `PUT /v1/memories/{memory_id}` - Update memory
  - `DELETE /v1/memories/{memory_id}` - Delete memory
  - `POST /v1/memories/search/` - Semantic search
  - `GET /v1/memories/{memory_id}/history` - Memory history

### Database Models (from openmemory/api/app/models.py)
- **Memory**: Core memory storage with content, metadata, categories
- **User**: User management and permissions
- **App**: Application-specific memory access
- **MemoryAccessLog**: Audit trail for memory operations
- **Category**: Memory categorization system

## Technical Debt and Known Issues

### Current System Strengths
1. **Excellent Architecture**: Well-designed microservices with clear separation
2. **Comprehensive API**: Full CRUD operations with advanced search
3. **Production Ready**: 88.8% health score with monitoring
4. **AI/ML Integration**: 97.5% accuracy with predictive analytics
5. **Robust Error Handling**: Circuit breakers and graceful degradation

### Areas for ChatGPT Integration Consideration
- **LLM Integration Pattern**: System already supports 20+ LLM providers, ChatGPT will fit naturally
- **Authentication**: Will need OpenAI API key management
- **Rate Limiting**: ChatGPT Custom GPT has specific rate limits to consider
- **Response Formatting**: Custom GPT responses may need special handling

## Integration Points and External Dependencies

### Current External Services
| Service | Purpose | Integration Type | Key Files |
|---------|---------|------------------|-----------|
| OpenAI | LLM Provider | API Client | `mem0/mem0/llms/openai.py` |
| Qdrant | Vector Store | Python Client | `mem0/mem0/vector_stores/qdrant.py` |
| PostgreSQL | Database | SQLAlchemy | `mem0/openmemory/api/app/database.py` |
| GitHub | Project Integration | REST API | `mem0/openmemory/github-projects-integration.py` |

### ChatGPT Custom GPT Integration Points
- **Authentication**: OpenAI API key management (already supported)
- **Custom GPT API**: New endpoints for Custom GPT communication
- **Memory Context**: Providing memory context to Custom GPT
- **Response Processing**: Handling Custom GPT responses and storing insights
- **Real-time Sync**: Bi-directional memory synchronization

## Development and Deployment

### Local Development Setup
1. **Python Environment**: Python 3.12+ with virtual environment
2. **Dependencies**: `pip install -r requirements.txt`
3. **Database**: SQLite for development, PostgreSQL for production
4. **Vector DB**: Qdrant running locally or via Docker
5. **Environment Variables**: See `.env.example` for required variables

### Current API Endpoints (relevant to ChatGPT integration)
```bash
# Core memory operations
GET /v1/memories/                 # List memories
POST /v1/memories/                # Create memory
GET /v1/memories/{id}             # Get specific memory
POST /v1/memories/search/         # Semantic search

# MCP server tools (for ChatGPT integration)
POST /mcp/search_memory           # Search through memories
POST /mcp/list_memories           # List all memories
POST /mcp/add_memory              # Add new memory
```

## ChatGPT Custom GPT Integration - Impact Analysis

### New Files/Modules Needed
- `mem0/mem0/llms/chatgpt_custom.py` - ChatGPT Custom GPT client
- `mem0/openmemory/api/app/routers/chatgpt.py` - ChatGPT-specific endpoints
- `mem0/mem0/configs/chatgpt_config.py` - ChatGPT configuration
- `mem0/openmemory/chatgpt_integration.py` - Main integration service

### Files That Will Need Modification
- `mem0/mem0/client/main.py` - Add ChatGPT Custom GPT client methods
- `mem0/server/main.py` - Add ChatGPT Custom GPT endpoints
- `mem0/openmemory/api/app/mcp_server.py` - Add ChatGPT Custom GPT MCP tools
- `mem0/mem0/configs/__init__.py` - Include ChatGPT configuration

### Integration Architecture for ChatGPT Custom GPT
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ChatGPT       │    │   Memory Bank    │    │   Vector Store  │
│   Custom GPT    │◄──►│   Service        │◄──►│   (Qdrant)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         │                        ▼                       │
         │              ┌──────────────────┐              │
         │              │   MCP Server     │              │
         └──────────────►│   (Tools)        │◄─────────────┘
                        └──────────────────┘
```

### Key Integration Considerations
1. **Authentication**: OpenAI API key for Custom GPT access
2. **Real-time Sync**: Bi-directional memory updates
3. **Context Management**: Providing relevant memory context to Custom GPT
4. **Response Processing**: Storing Custom GPT insights back to memory
5. **Rate Limiting**: Respecting ChatGPT Custom GPT rate limits
6. **Error Handling**: Graceful degradation when Custom GPT is unavailable

**The Memory Bank Service is perfectly positioned for ChatGPT Custom GPT integration with its existing LLM infrastructure, MCP server, and comprehensive API design.** 