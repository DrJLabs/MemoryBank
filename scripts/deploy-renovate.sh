#!/bin/bash

# Renovate Branch Deployment Script
# Safely deploys renovate branch services with port isolation and health monitoring

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.renovate.yml"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
HEALTH_CHECK_INTERVAL=10   # 10 seconds

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if we're on the renovate branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "renovate" ]; then
        log_warning "You're not on the renovate branch (current: $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Check for port conflicts with main branch services
    log "🔍 Checking for port conflicts..."
    conflicting_ports=()
    renovate_ports=(9888 9432 9474 9687 7333 9765 4000 9000 7379 9091 4001)
    
    for port in "${renovate_ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            conflicting_ports+=($port)
        fi
    done
    
    if [ ${#conflicting_ports[@]} -gt 0 ]; then
        log_warning "The following renovate ports are already in use: ${conflicting_ports[*]}"
        log "This might indicate renovate services are already running or port conflicts exist."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "Pre-deployment checks passed"
}

# Save current main state
save_main_state() {
    log "💾 Saving current main branch service state..."
    
    local state_file="$PROJECT_ROOT/main-services-state.json"
    
    # Get current running containers
    docker ps --format "{{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}" > "$PROJECT_ROOT/main-services-running.txt"
    
    # Get main branch commit
    git rev-parse HEAD > "$PROJECT_ROOT/main-branch-commit.txt"
    
    log_success "Main state saved to:"
    log "  - Container state: main-services-running.txt"
    log "  - Branch commit: main-branch-commit.txt"
}

# Deploy renovate services
deploy_renovate_services() {
    log "🚀 Deploying renovate branch services..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images first
    log "📥 Pulling latest images..."
    docker compose -f "$COMPOSE_FILE" pull --ignore-pull-failures
    
    # Build services
    log "🔨 Building renovate services..."
    docker compose -f "$COMPOSE_FILE" build --parallel
    
    # Start services in dependency order
    log "⚡ Starting renovate services..."
    docker compose -f "$COMPOSE_FILE" up -d
    
    log_success "Services deployment initiated"
}

# Health check for specific service
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1
    
    log "🏥 Checking health of $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            log_success "$service_name is healthy"
            return 0
        fi
        
        log "⏳ Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done
    
    log_error "$service_name failed health check after $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

# Comprehensive health checks
run_health_checks() {
    log "🏥 Running comprehensive health checks..."
    
    local failed_services=()
    
    # Check core services
    services=(
        "renovate-mem0:http://localhost:9888/health"
        "renovate-openmemory-mcp:http://localhost:9765/health"
        "renovate-qdrant:http://localhost:7333/health"
        "renovate-postgres:http://localhost:9432"
        "renovate-neo4j:http://localhost:9474"
    )
    
    for service_health in "${services[@]}"; do
        IFS=':' read -r service_name health_url <<< "$service_health"
        if ! check_service_health "$service_name" "$health_url"; then
            failed_services+=("$service_name")
        fi
    done
    
    # Check container status
    log "📋 Checking container status..."
    docker compose -f "$COMPOSE_FILE" ps
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "The following services failed health checks: ${failed_services[*]}"
        return 1
    fi
    
    log_success "All services passed health checks"
}

# Post-deployment verification
post_deployment_verification() {
    log "🔍 Running post-deployment verification..."
    
    # Verify service connectivity
    log "🔗 Testing service connectivity..."
    
    # Test API endpoints
    local endpoints=(
        "http://localhost:9888/health:Mem0 Server"
        "http://localhost:9765/health:OpenMemory MCP API"
        "http://localhost:7333/health:Qdrant Vector DB"
        "http://localhost:9474:Neo4j HTTP"
    )
    
    for endpoint in "${endpoints[@]}"; do
        IFS=':' read -r url name <<< "$endpoint"
        if curl -s -f "$url" > /dev/null; then
            log_success "$name endpoint is accessible"
        else
            log_warning "$name endpoint is not accessible at $url"
        fi
    done
    
    # Test database connections
    log "🗄️ Testing database connections..."
    
    # Test PostgreSQL
    if docker compose -f "$COMPOSE_FILE" exec -T renovate-postgres pg_isready -q -d renovate_mem0 -U postgres; then
        log_success "PostgreSQL connection successful"
    else
        log_warning "PostgreSQL connection failed"
    fi
    
    # Display service URLs
    log_success "🎉 Renovate deployment completed successfully!"
    echo
    log "📍 Service Access Points:"
    echo "  🌐 Mem0 Server:        http://localhost:9888"
    echo "  🔌 OpenMemory API:     http://localhost:9765"
    echo "  🎨 OpenMemory UI:      http://localhost:4000"
    echo "  🔍 Qdrant Vector DB:   http://localhost:7333"
    echo "  📊 Neo4j Browser:      http://localhost:9474"
    echo "  📈 Prometheus:         http://localhost:9091"
    echo "  📊 Grafana:            http://localhost:4001"
    echo "  🔧 Custom GPT API:     http://localhost:9000"
    echo
    log "🔄 To rollback to main: ./scripts/rollback-to-main.sh"
}

# Cleanup on failure
cleanup_on_failure() {
    log_error "Deployment failed. Cleaning up..."
    
    docker compose -f "$COMPOSE_FILE" down --remove-orphans
    
    log "🧹 Cleanup completed. You can retry deployment or rollback to main."
}

# Main deployment function
main() {
    log "🚀 Starting Renovate Branch Deployment"
    echo "=========================================="
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    pre_deployment_checks
    save_main_state
    deploy_renovate_services
    
    # Wait a bit for services to initialize
    sleep 30
    
    if run_health_checks; then
        post_deployment_verification
    else
        log_error "Health checks failed. Check logs and consider rollback."
        exit 1
    fi
    
    log_success "🎉 Renovate deployment completed successfully!"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 