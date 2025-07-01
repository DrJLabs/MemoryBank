#!/bin/bash

# Rollback to Main Branch Script
# Safely stops renovate services and restores main branch services

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
RENOVATE_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.renovate.yml"
MAIN_COMPOSE_FILE="$PROJECT_ROOT/mem0/server/docker-compose.yaml"
OPENMEMORY_COMPOSE="$PROJECT_ROOT/mem0/openmemory"

# Logging functions
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

# Pre-rollback checks
pre_rollback_checks() {
    log "🔍 Running pre-rollback checks..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if renovate compose file exists
    if [ ! -f "$RENOVATE_COMPOSE_FILE" ]; then
        log_warning "Renovate compose file not found: $RENOVATE_COMPOSE_FILE"
        log "This might indicate renovate services were never deployed."
    fi
    
    # Check if any renovate containers are running
    renovate_containers=$(docker ps --filter "name=renovate-" --format "{{.Names}}" || true)
    if [ -z "$renovate_containers" ]; then
        log_warning "No renovate containers found running."
        log "This might indicate renovate services are already stopped."
    else
        log "Found running renovate containers:"
        echo "$renovate_containers" | sed 's/^/  - /'
    fi
    
    log_success "Pre-rollback checks completed"
}

# Stop renovate services
stop_renovate_services() {
    log "🛑 Stopping renovate branch services..."
    
    if [ -f "$RENOVATE_COMPOSE_FILE" ]; then
        cd "$PROJECT_ROOT"
        
        # Stop and remove renovate containers
        log "📦 Stopping renovate containers..."
        docker compose -f "$RENOVATE_COMPOSE_FILE" down --remove-orphans --volumes
        
        # Remove renovate images (optional, saves space)
        log "🗑️ Cleaning up renovate images..."
        docker images --filter "reference=*renovate*" -q | xargs -r docker rmi -f || true
        
        # Remove renovate networks
        log "🌐 Cleaning up renovate networks..."
        docker network ls --filter "name=renovate" -q | xargs -r docker network rm || true
        
        log_success "Renovate services stopped and cleaned up"
    else
        log_warning "Renovate compose file not found, skipping service stop"
    fi
    
    # Force remove any remaining renovate containers
    renovate_containers=$(docker ps -a --filter "name=renovate-" --format "{{.Names}}" || true)
    if [ -n "$renovate_containers" ]; then
        log "🧹 Force removing remaining renovate containers..."
        echo "$renovate_containers" | xargs -r docker rm -f
    fi
}

# Restore main branch services
restore_main_services() {
    log "🔄 Restoring main branch services..."
    
    # Switch to main branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        log "🔀 Switching to main branch (current: $current_branch)..."
        git stash push -m "Auto-stash before rollback to main" || true
        git checkout main
        log_success "Switched to main branch"
    else
        log "Already on main branch"
    fi
    
    # Start main branch mem0 services
    if [ -f "$MAIN_COMPOSE_FILE" ]; then
        log "🚀 Starting main branch mem0 services..."
        cd "$(dirname "$MAIN_COMPOSE_FILE")"
        docker compose up -d
        
        # Wait for services to start
        sleep 20
        log_success "Main branch mem0 services started"
    else
        log_warning "Main compose file not found: $MAIN_COMPOSE_FILE"
    fi
    
    # Start openmemory services
    if [ -d "$OPENMEMORY_COMPOSE" ]; then
        log "🧠 Starting OpenMemory services..."
        cd "$OPENMEMORY_COMPOSE"
        
        # Check if there's a run script or docker-compose file
        if [ -f "run.sh" ]; then
            ./run.sh &
            log_success "OpenMemory services started via run.sh"
        elif [ -f "docker-compose.yml" ]; then
            docker compose up -d
            log_success "OpenMemory services started via docker-compose"
        else
            log_warning "No run script or compose file found in $OPENMEMORY_COMPOSE"
        fi
    else
        log_warning "OpenMemory directory not found: $OPENMEMORY_COMPOSE"
    fi
}

# Verify main services are running
verify_main_services() {
    log "🏥 Verifying main branch services..."
    
    # Check main ports
    main_ports=(8888 8432 8474 8687 6333 8765)
    services_status=()
    
    for port in "${main_ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            services_status+=("✅ Port $port: Active")
        else
            services_status+=("❌ Port $port: Inactive")
        fi
    done
    
    log "📊 Service Status:"
    for status in "${services_status[@]}"; do
        echo "  $status"
    done
    
    # Test main service endpoints
    local endpoints=(
        "http://localhost:8888/health:Mem0 Server"
        "http://localhost:8765/health:OpenMemory MCP API"
        "http://localhost:6333/health:Qdrant Vector DB"
        "http://localhost:8474:Neo4j HTTP"
    )
    
    log "🔗 Testing main service endpoints..."
    local accessible_count=0
    local total_endpoints=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        IFS=':' read -r url name <<< "$endpoint"
        if timeout 5 curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$name is accessible"
            ((accessible_count++))
        else
            log_warning "$name is not accessible at $url"
        fi
    done
    
    log "📈 Accessibility: $accessible_count/$total_endpoints endpoints accessible"
    
    if [ $accessible_count -eq $total_endpoints ]; then
        log_success "All main services are fully operational"
    elif [ $accessible_count -gt 0 ]; then
        log_warning "Some main services are operational, but not all"
    else
        log_error "No main services appear to be accessible"
        return 1
    fi
}

# Display service status summary
display_status_summary() {
    log "📋 Post-Rollback Status Summary"
    echo "================================="
    
    log "🌐 Main Branch Service URLs:"
    echo "  📡 Mem0 Server:        http://localhost:8888"
    echo "  🔌 OpenMemory API:     http://localhost:8765"
    echo "  🔍 Qdrant Vector DB:   http://localhost:6333"
    echo "  📊 Neo4j Browser:      http://localhost:8474"
    echo "  🗄️ PostgreSQL:         localhost:8432"
    echo
    
    # Show running containers
    log "🐳 Currently Running Containers:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | head -10
    
    echo
    log "📁 Saved State Files:"
    if [ -f "$PROJECT_ROOT/main-services-running.txt" ]; then
        echo "  📄 main-services-running.txt (previous state)"
    fi
    if [ -f "$PROJECT_ROOT/main-branch-commit.txt" ]; then
        echo "  📄 main-branch-commit.txt (commit hash)"
    fi
    
    echo
    log_success "🎉 Rollback to main branch completed!"
    log "💡 To deploy renovate again: ./scripts/deploy-renovate.sh"
}

# Cleanup rollback artifacts
cleanup_rollback_artifacts() {
    log "🧹 Cleaning up rollback artifacts..."
    
    # Remove state files (optional)
    read -p "Remove saved state files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$PROJECT_ROOT/main-services-running.txt"
        rm -f "$PROJECT_ROOT/main-branch-commit.txt"
        log_success "State files removed"
    else
        log "State files preserved for future reference"
    fi
    
    # Cleanup Docker system (optional)
    read -p "Run Docker system cleanup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -f
        log_success "Docker system cleanup completed"
    fi
}

# Emergency rollback (faster, less verification)
emergency_rollback() {
    log_error "🚨 EMERGENCY ROLLBACK MODE"
    log "Performing rapid rollback with minimal verification..."
    
    # Force stop all renovate containers
    docker ps --filter "name=renovate-" -q | xargs -r docker stop
    docker ps -a --filter "name=renovate-" -q | xargs -r docker rm -f
    
    # Switch to main branch
    git checkout main --force
    
    # Start essential main services only
    cd "$PROJECT_ROOT/mem0/server"
    docker compose up -d mem0 postgres neo4j
    
    log_warning "Emergency rollback completed. Manual verification recommended."
}

# Main rollback function
main() {
    log "🔄 Starting Rollback to Main Branch"
    echo "====================================="
    
    # Check for emergency mode
    if [[ "${1:-}" == "--emergency" ]]; then
        emergency_rollback
        exit 0
    fi
    
    # Confirm rollback action
    log_warning "This will stop all renovate services and restore main branch services."
    read -p "Continue with rollback? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Rollback cancelled by user"
        exit 0
    fi
    
    pre_rollback_checks
    stop_renovate_services
    restore_main_services
    
    # Wait for services to stabilize
    sleep 30
    
    if verify_main_services; then
        display_status_summary
        cleanup_rollback_artifacts
    else
        log_error "Main services verification failed. Manual intervention may be required."
        log "💡 Try emergency rollback: ./scripts/rollback-to-main.sh --emergency"
        exit 1
    fi
    
    log_success "🎉 Rollback completed successfully!"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 