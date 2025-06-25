# OpenMemory (Mem0) with Infiscal Integration

This setup provides a production-ready deployment of OpenMemory (Mem0) with secure secret management using Infiscal and direct API integration.

## Features

- ✅ **Secure Secret Management**: OpenAI API keys stored in Infiscal, not in files
- ✅ **Custom Port Configuration**: UI runs on port 3010 (instead of default 3000)
- ✅ **Production-Ready**: Proper error handling and service health checks
- ✅ **Easy Management**: Simple start/stop/restart commands
- ✅ **Docker-Based**: Containerized deployment with persistent storage
- ✅ **Direct API Integration**: Reliable memory operations without protocol complications
- ✅ **Enhanced Features**: Analytics, categorization, project context, backups

## Architecture

- **UI Dashboard**: http://localhost:3010
- **API Server**: http://localhost:8765
- **API Documentation**: http://localhost:8765/docs
- **Vector Database (Qdrant)**: http://localhost:6333

## Prerequisites

1. **Docker** and **Docker Compose**
2. **Infiscal CLI** (already configured in this workspace)
3. **OpenAI API Key** (already stored in Infiscal)

## Quick Start

### 1. Start the services

```bash
./start-with-infiscal.sh start
```

This command will:
- ✅ Check all prerequisites
- ✅ Load the OpenAI API key from Infiscal
- ✅ Create environment files
- ✅ Build Docker images
- ✅ Start all services

### 2. Access the UI

Open your browser and navigate to: http://localhost:3010

### 3. Use Memory Commands

Direct API integration with enhanced features:

```bash
# Basic usage
mem-add "information to remember"
mem-search "search query"

# Enhanced features  
mem-analytics                    # View memory statistics
mem-learn "new knowledge"        # Add learning memory
mem-preference "user setting"    # Add preference memory
mem-project-add "project info"   # Add project-scoped memory
mem-backup-now                   # Create backup
```

## Managing Services

### Stop services
```bash
./start-with-infiscal.sh stop
```

### Restart services
```bash
./start-with-infiscal.sh restart
```

### View logs
```bash
docker compose logs -f
```

### View specific service logs
```bash
docker compose logs -f openmemory-mcp  # API logs
docker compose logs -f openmemory-ui   # UI logs
docker compose logs -f mem0_store      # Vector DB logs
```

## Memory Integration

### Available Commands

#### Basic Memory Operations
```bash
mem-add "text"           # Add basic memory
mem-search "query"       # Search memories
```

#### Enhanced Operations
```bash
mem-analytics           # Show memory statistics
mem-learn "content"     # Add categorized learning
mem-preference "pref"   # Add user preference
mem-project-add "info"  # Add project-scoped memory
mem-project-search "q"  # Search current project only
mem-backup-now         # Create timestamped backup
```

#### System Management
```bash
mem-health            # Check API health
mem-stats            # View API statistics
mem-logs             # View service logs
mem-secure-check     # Security status
mem-ui              # Open web dashboard
```

### Memory Categories

Memories are automatically categorized:
- `[LEARNING]` - Knowledge and discoveries
- `[PREFERENCE]` - User preferences and settings
- `[PROJECT:name]` - Project-specific information (auto-detected)

### Project Context

The system automatically detects your current project based on the working directory and tags memories accordingly, enabling project-scoped search and organization.

## Configuration

### Environment Variables

The script automatically creates two environment files:

1. **api/.env**
   - `OPENAI_API_KEY`: Loaded from Infiscal
   - `USER`: Your user identifier (defaults to system username)

2. **ui/.env**
   - `NEXT_PUBLIC_API_URL`: http://localhost:8765
   - `NEXT_PUBLIC_USER_ID`: Same as USER

### Changing Ports

To change ports, edit `docker-compose.yml`:

```yaml
services:
  openmemory-ui:
    ports:
      - "3010:3000"  # Change 3010 to your desired port
```

## Security Best Practices

1. **Never commit .env files** - They're already in .gitignore
2. **Use Infiscal for all secrets** - Never hardcode API keys
3. **Rotate API keys regularly** - Update in Infiscal when needed
4. **Monitor access logs** - Check docker logs for suspicious activity

## Troubleshooting

### Services won't start

1. Check if ports are already in use:
   ```bash
   lsof -i :3010
   lsof -i :8765
   lsof -i :6333
   ```

2. Check Docker status:
   ```bash
   docker ps
   docker compose ps
   ```

3. Check logs for errors:
   ```bash
   docker compose logs
   ```

### Memory commands not working

1. Verify API service is running:
   ```bash
   mem-health
   ```

2. Check if aliases are loaded:
   ```bash
   source ~/.bashrc
   ```

3. Test direct Python script:
   ```bash
   python3 cursor-memory-enhanced.py analytics
   ```

### UI not accessible

If http://localhost:3010 doesn't work:

1. Check if the UI container is running:
   ```bash
   docker compose ps openmemory-ui
   ```

2. Try manual UI startup:
   ```bash
   cd ui
   pnpm install
   pnpm dev
   ```

## Data Persistence

All memory data is stored in a Docker volume named `mem0_storage`. This ensures:
- Data persists across container restarts
- Backup-friendly architecture
- Easy migration to other systems

### Backup & Restore

Create backup:
```bash
mem-backup-now
```

Manual backup:
```bash
docker run --rm -v openmemory_mem0_storage:/data -v $(pwd):/backup alpine tar czf /backup/mem0-backup-$(date +%Y%m%d).tar.gz -C /data .
```

## Updates

To update OpenMemory:

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart:
   ```bash
   ./start-with-infiscal.sh restart
   ```

## Support

- OpenMemory Documentation: https://docs.mem0.ai/openmemory/quickstart
- GitHub Repository: https://github.com/mem0ai/mem0
- Discord Community: https://discord.gg/mem0

---

**Note**: This setup uses direct API integration for maximum reliability. MCP protocol integration has known compatibility issues, so we've implemented a robust direct API approach instead. 