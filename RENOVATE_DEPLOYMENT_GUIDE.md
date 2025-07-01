# 🚀 Renovate Branch Deployment Guide

## Overview

This guide provides a comprehensive strategy for safely deploying the renovate branch while ensuring compatibility with existing main branch services running in your development environment.

## 🎯 Deployment Strategy

Our approach uses **port isolation** and **service segregation** to enable side-by-side testing and zero-downtime transitions between main and renovate branches.

### Port Allocation Strategy

| Service | Main Branch | Renovate Branch | Offset |
|---------|-------------|----------------|--------|
| Mem0 Server | 8888 | **9888** | +1000 |
| OpenMemory MCP | 8765 | **9765** | +1000 |
| Neo4j HTTP | 8474 | **9474** | +1000 |
| Neo4j Bolt | 8687 | **9687** | +1000 |
| PostgreSQL | 8432 | **9432** | +1000 |
| Qdrant Vector DB | 6333 | **7333** | +1000 |
| Redis | 6379 | **7379** | +1000 |
| OpenMemory UI | 3010 | **4000** | Custom |
| Custom GPT API | - | **9000** | New |
| Grafana | - | **4001** | New |
| Prometheus | - | **9091** | New |

## 🛠️ Prerequisites

Before starting deployment, ensure:

1. **Docker is running** and you have sufficient resources
2. **Main branch services** are operational (if you want to keep them running)
3. **Git repository** is on the renovate branch
4. **Network ports** are available (9000-9999 range)

## 📋 Deployment Steps

### Step 1: Pre-Deployment Analysis

```bash
# Check compatibility between branches
./scripts/compatibility-check.sh

# Review the generated compatibility report
cat compatibility-report.md
```

### Step 2: Health Check Current Services

```bash
# Check what's currently running
./scripts/health-check.sh main

# Get detailed port status
./scripts/health-check.sh ports
```

### Step 3: Deploy Renovate Services

```bash
# Deploy renovate branch with port isolation
./scripts/deploy-renovate.sh
```

This script will:
- ✅ Validate pre-deployment conditions
- 💾 Save current main branch state
- 🔨 Build and deploy renovate services
- 🏥 Run comprehensive health checks
- 📊 Display service access points

### Step 4: Integration Testing

```bash
# Run comprehensive integration tests
./scripts/integration-test.sh

# Or run specific tests
./scripts/integration-test.sh --cross-api
./scripts/integration-test.sh --performance
```

### Step 5: Monitoring and Validation

```bash
# Continuous health monitoring
./scripts/health-check.sh --continuous renovate

# Monitor both stacks simultaneously
./scripts/health-check.sh all
```

## 🔄 Rollback Procedure

If issues are detected:

```bash
# Quick rollback to main branch
./scripts/rollback-to-main.sh

# Emergency rollback (faster, less verification)
./scripts/rollback-to-main.sh --emergency
```

## 📊 Service Access Points

### Main Branch Services (if running)
- 🌐 **Mem0 Server**: http://localhost:8888
- 🔌 **OpenMemory API**: http://localhost:8765
- 🎨 **OpenMemory UI**: http://localhost:3010
- 🔍 **Qdrant Vector DB**: http://localhost:6333
- 📊 **Neo4j Browser**: http://localhost:8474

### Renovate Branch Services
- 🌐 **Mem0 Server**: http://localhost:9888
- 🔌 **OpenMemory API**: http://localhost:9765
- 🎨 **OpenMemory UI**: http://localhost:4000
- 🔍 **Qdrant Vector DB**: http://localhost:7333
- 📊 **Neo4j Browser**: http://localhost:9474
- 📈 **Prometheus**: http://localhost:9091
- 📊 **Grafana**: http://localhost:4001
- 🔧 **Custom GPT API**: http://localhost:9000

## 🧪 Testing Scenarios

### 1. Side-by-Side Comparison
- Run identical API tests against both main and renovate services
- Compare response times and functionality
- Validate data consistency

### 2. Cross-Database Testing
- Test renovate services against main branch databases
- Verify schema compatibility and migration requirements
- Test data migration scripts

### 3. Load Testing
- Run performance tests on both stacks
- Monitor resource usage
- Identify performance regressions

## 🔧 Configuration Files

### Main Docker Compose Files
- `mem0/server/docker-compose.yaml` - Main branch mem0 services
- `mem0/openmemory/docker-compose.yml` - Main OpenMemory services

### Renovate Branch Files
- `docker-compose.renovate.yml` - Isolated renovate services
- `renovate-deployment-strategy.md` - Detailed strategy documentation

## 🚨 Troubleshooting

### Port Conflicts
```bash
# Check what's using specific ports
lsof -i :9888
netstat -tulpn | grep 9888

# Kill processes on specific ports if needed
sudo fuser -k 9888/tcp
```

### Service Not Starting
```bash
# Check Docker logs
docker-compose -f docker-compose.renovate.yml logs renovate-mem0

# Check container status
docker ps --filter "name=renovate-"

# Restart specific service
docker-compose -f docker-compose.renovate.yml restart renovate-mem0
```

### Database Connection Issues
```bash
# Test database connectivity
./scripts/health-check.sh --verbose

# Check database logs
docker-compose -f docker-compose.renovate.yml logs renovate-postgres
```

### Memory or Resource Issues
```bash
# Check Docker resource usage
docker stats

# Clean up unused containers/images
docker system prune -f

# Increase Docker memory limits if needed
```

## 📈 Monitoring and Alerts

### Health Monitoring
```bash
# Continuous monitoring with alerts
./scripts/health-check.sh -c -i 30

# JSON output for external monitoring
./scripts/health-check.sh -f json renovate
```

### Performance Monitoring
- **Grafana Dashboard**: http://localhost:4001
- **Prometheus Metrics**: http://localhost:9091
- Custom performance tests via integration test script

## 🔒 Security Considerations

1. **Network Isolation**: Renovate services use isolated Docker networks
2. **Port Security**: Non-standard ports reduce attack surface
3. **Data Isolation**: Separate databases prevent data corruption
4. **Access Control**: Services only accessible from localhost by default

## 📝 Best Practices

### Before Deployment
- [ ] Review compatibility report
- [ ] Ensure sufficient system resources
- [ ] Backup critical data
- [ ] Plan rollback timing

### During Deployment
- [ ] Monitor logs continuously
- [ ] Run health checks frequently
- [ ] Test critical functionality immediately
- [ ] Document any issues

### After Deployment
- [ ] Run comprehensive integration tests
- [ ] Monitor performance metrics
- [ ] Validate all service endpoints
- [ ] Update documentation

## 🎉 Success Criteria

Deployment is considered successful when:

✅ All renovate services pass health checks  
✅ API endpoints respond correctly  
✅ Database connections are stable  
✅ Performance is within acceptable limits  
✅ Integration tests pass  
✅ No critical errors in logs  

## 📞 Support and Escalation

If you encounter issues:

1. **Check logs** first using the health check script
2. **Review compatibility report** for known issues
3. **Use rollback script** if problems persist
4. **Document issues** for future reference

## 📚 Additional Resources

- `renovate-deployment-strategy.md` - Detailed technical strategy
- `scripts/` directory - All deployment and testing scripts
- `compatibility-report.md` - Generated compatibility analysis
- `integration-test-report.md` - Test results and recommendations

---

**Happy Deploying! 🚀**

*This guide ensures your renovate branch deployment is safe, monitored, and easily reversible.* 