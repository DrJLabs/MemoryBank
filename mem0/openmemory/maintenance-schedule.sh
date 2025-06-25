#!/bin/bash
# Advanced Memory System Maintenance Script
# Following best practices from system optimization guides

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Logging function
log() {
    echo "[$DATE] $1" | tee -a "$LOG_FILE"
}

# Health check function
health_check() {
    log "=== HEALTH CHECK START ==="
    
    # Check services
    if docker compose ps | grep -q "Up"; then
        log "✅ Services are running"
    else
        log "❌ Services are down - attempting restart"
        docker compose up -d
    fi
    
    # Check API response
    if curl -s http://localhost:8765/docs >/dev/null; then
        log "✅ API is responsive"
    else
        log "❌ API is not responsive"
    fi
    
    # Check memory system
    cd "$SCRIPT_DIR/../.."
    MEMORY_COUNT=$(python3 mem0/openmemory/advanced-memory-ai.py analytics | grep "Total Memories:" | awk '{print $3}')
    log "📊 Total memories: $MEMORY_COUNT"
    
    log "=== HEALTH CHECK COMPLETE ==="
}

# Docker cleanup function
docker_cleanup() {
    log "=== DOCKER CLEANUP START ==="
    
    # Show current usage
    docker system df
    
    # Remove unused images
    log "Removing unused Docker images..."
    docker image prune -f
    
    # Remove unused containers
    log "Removing unused containers..."
    docker container prune -f
    
    # Remove unused volumes
    log "Removing unused volumes..."
    docker volume prune -f
    
    # Remove build cache
    log "Removing build cache..."
    docker builder prune -f
    
    # Show new usage
    log "Post-cleanup usage:"
    docker system df
    
    log "=== DOCKER CLEANUP COMPLETE ==="
}

# Memory system cleanup
memory_cleanup() {
    log "=== MEMORY CLEANUP START ==="
    
    cd "$SCRIPT_DIR/../.."
    
    # Archive old memories (older than 180 days)
    log "Archiving memories older than 180 days..."
    python3 mem0/openmemory/advanced-memory-ai.py archive-old 180
    
    # Get updated analytics
    log "Updated system analytics:"
    python3 mem0/openmemory/advanced-memory-ai.py analytics
    
    log "=== MEMORY CLEANUP COMPLETE ==="
}

# Performance optimization
performance_optimization() {
    log "=== PERFORMANCE OPTIMIZATION START ==="
    
    # Restart services for fresh state
    log "Restarting services for optimization..."
    docker compose restart
    
    # Wait for services to be ready
    sleep 10
    
    # Test response time
    log "Testing API response time..."
    RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8765/docs)
    log "API response time: ${RESPONSE_TIME}s"
    
    log "=== PERFORMANCE OPTIMIZATION COMPLETE ==="
}

# Backup function
backup_system() {
    log "=== BACKUP START ==="
    
    BACKUP_DIR="$SCRIPT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup Docker volumes
    log "Backing up Docker volumes..."
    docker run --rm -v mem0_openmemory_mem0_storage:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/mem0_storage.tar.gz -C /data .
    
    # Backup configuration
    log "Backing up configuration..."
    cp "$SCRIPT_DIR/docker-compose.yml" "$BACKUP_DIR/"
    cp "$SCRIPT_DIR"/.env "$BACKUP_DIR/" 2>/dev/null || log "No .env file to backup"
    
    log "Backup completed in: $BACKUP_DIR"
    log "=== BACKUP COMPLETE ==="
}

# Main maintenance function
run_maintenance() {
    local maintenance_type="${1:-full}"
    
    log "Starting $maintenance_type maintenance..."
    
    case $maintenance_type in
        "health")
            health_check
            ;;
        "cleanup")
            docker_cleanup
            memory_cleanup
            ;;
        "backup")
            backup_system
            ;;
        "performance")
            performance_optimization
            ;;
        "full")
            health_check
            backup_system
            docker_cleanup
            memory_cleanup
            performance_optimization
            ;;
        *)
            log "Unknown maintenance type: $maintenance_type"
            echo "Usage: $0 [health|cleanup|backup|performance|full]"
            exit 1
            ;;
    esac
    
    log "Maintenance completed successfully!"
}

# Run maintenance
run_maintenance "$@" 