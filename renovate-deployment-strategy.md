# Renovate Branch Deployment Strategy

## 🎯 Objective
Ensure the renovated repository works seamlessly with existing containers and dev servers currently running from the main branch, with zero downtime and easy rollback capabilities.

## 📊 Current Infrastructure Analysis

### Running Services (Main Branch)
```
Port Map:
├── 6333  → Qdrant Vector DB (openmemory)
├── 8000  → Portainer Web UI
├── 8432  → PostgreSQL (mem0-dev)
├── 8474  → Neo4j HTTP
├── 8687  → Neo4j Bolt
├── 8765  → OpenMemory MCP API
├── 8888  → Mem0 Server
└── 9443  → Portainer HTTPS
```

### Service Dependencies
- **Mem0 Server** (8888) → PostgreSQL (8432) + Neo4j (8474/8687)
- **OpenMemory MCP** (8765) → Qdrant (6333)
- **Portainer** → Managing Docker ecosystem

## 🔧 Strategy 1: Port Isolation Testing

### Renovate Branch Port Allocation
```
Service                 Main Port   Renovate Port   Offset
─────────────────────────────────────────────────────────
Mem0 Server            8888        →   9888        +1000
OpenMemory MCP         8765        →   9765        +1000
Neo4j HTTP             8474        →   9474        +1000
Neo4j Bolt             8687        →   9687        +1000
PostgreSQL (mem0)      8432        →   9432        +1000
Qdrant Vector DB       6333        →   7333        +1000
Test Grafana           -           →   9001        new
Test Prometheus        -           →   9091        new
```

### Benefits
- ✅ Zero interference with main branch services
- ✅ Side-by-side comparison testing
- ✅ Easy rollback (just switch ports)
- ✅ Gradual migration possible

## 🐳 Strategy 2: Docker Service Isolation

### Network Segregation
```
Networks:
├── main-network      → Current main branch services
├── renovate-network  → New renovate branch services
└── bridge-network    → Integration testing bridge
```

### Container Naming Convention
```
Main Branch:           Renovate Branch:
├── mem0-dev-*         ├── renovate-mem0-*
├── openmemory-*       ├── renovate-openmemory-*
└── bmad-*            └── renovate-bmad-*
```

## 🧪 Strategy 3: Progressive Integration Testing

### Phase 1: Isolated Testing
1. Start renovate services on isolated ports
2. Run full test suites in isolation
3. Verify all services start and communicate

### Phase 2: Cross-Compatibility Testing
1. Test renovate services against main branch databases
2. Verify API compatibility
3. Check dependency versions

### Phase 3: Load Testing
1. Parallel load testing on both stacks
2. Performance comparison
3. Resource usage analysis

### Phase 4: Switch-over Testing
1. Gradual traffic migration
2. A/B testing capabilities
3. Rollback verification

## 🔄 Strategy 4: Smart Rollback Mechanism

### Service State Management
```bash
# Save current state
./scripts/save-main-state.sh

# Deploy renovate
./scripts/deploy-renovate.sh

# Rollback if needed
./scripts/rollback-to-main.sh
```

### Health Monitoring
- Continuous health checks during transition
- Automatic rollback triggers
- Service dependency health verification

## 🚀 Implementation Plan

### Immediate Actions
1. Create port-isolated docker-compose files
2. Implement service naming conventions
3. Set up monitoring for both stacks
4. Create switch-over scripts

### Files to Create/Modify
- `docker-compose.renovate.yml`
- `scripts/deploy-renovate.sh`
- `scripts/rollback-to-main.sh`
- `scripts/health-check.sh`
- `monitoring/renovate-dashboard.json` 