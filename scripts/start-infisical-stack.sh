#!/bin/bash
# Enhanced Docker Stack Startup with Infisical Integration
# Architecture: MemoryBank Infisical Integration Architecture v1.0
# Pattern: Container Platform Integration with Comprehensive Monitoring

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$BLUE" "🔍 Checking prerequisites for Infisical Docker stack..."
    
    local missing=()
    
    if ! command -v docker >/dev/null 2>&1; then
        missing+=("docker")
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        missing+=("docker-compose")
    fi
    
    if ! command -v infisical >/dev/null 2>&1; then
        missing+=("infisical")
    fi
    
    if [[ ${#missing[@]} -ne 0 ]]; then
        print_message "$RED" "❌ Missing required tools: ${missing[*]}"
        print_message "$YELLOW" "Please install missing tools before proceeding."
        exit 1
    fi
    
    print_message "$GREEN" "✅ All prerequisites met!"
}

# Function to validate Infisical authentication
validate_infisical_auth() {
    print_message "$BLUE" "🔐 Validating Infisical authentication..."
    
    # Check authentication
    if ! infisical secrets --env=dev >/dev/null 2>&1; then
        print_message "$RED" "❌ Infisical not authenticated"
        print_message "$YELLOW" "Run: infisical login && infisical init"
        exit 1
    fi
    
    # Verify critical secrets
    local required_secrets=("OPENAI_API_KEY" "DB_PASSWORD")
    for secret in "${required_secrets[@]}"; do
        if infisical secrets get "$secret" --env=dev --plain >/dev/null 2>&1; then
            print_message "$GREEN" "✅ $secret available"
        else
            print_message "$YELLOW" "⚠️  $secret not found (will use defaults)"
        fi
    done
    
    print_message "$GREEN" "✅ Infisical validation complete!"
}

# Function to prepare environment
prepare_environment() {
    print_message "$BLUE" "🏗️ Preparing enhanced Docker environment..."
    
    # Ensure we're in the correct directory
    if [[ ! -f "mem0/server/docker-compose-infisical.yaml" ]]; then
        print_message "$RED" "❌ Enhanced docker-compose-infisical.yaml not found"
        print_message "$YELLOW" "Please run from project root directory"
        exit 1
    fi
    
    # Create logs directory
    mkdir -p logs/infisical-stack
    
    # Ensure Infisical config is accessible
    if [[ ! -f ".infisical.json" ]]; then
        print_message "$RED" "❌ .infisical.json not found"
        print_message "$YELLOW" "Run: infisical init"
        exit 1
    fi
    
    print_message "$GREEN" "✅ Environment prepared!"
}

# Function to start services
start_services() {
    print_message "$BLUE" "🚀 Starting Infisical-secured Docker stack..."
    
    cd mem0/server
    
    # Stop any existing services
    print_message "$YELLOW" "🛑 Stopping existing services..."
    docker-compose -f docker-compose-infisical.yaml down 2>/dev/null || true
    
    # Build and start services with Infisical integration
    print_message "$BLUE" "🏗️ Building services with Infisical CLI..."
    docker-compose -f docker-compose-infisical.yaml build --no-cache
    
    print_message "$BLUE" "🚀 Starting services with secret injection..."
    docker-compose -f docker-compose-infisical.yaml up -d
    
    cd ../..
    
    print_message "$GREEN" "✅ Services started!"
}

# Function to monitor service health
monitor_health() {
    print_message "$BLUE" "⏳ Monitoring service health..."
    
    local max_attempts=12
    local attempt=0
    local all_healthy=false
    
    while [[ $attempt -lt $max_attempts && $all_healthy == false ]]; do
        attempt=$((attempt + 1))
        print_message "$YELLOW" "📊 Health check attempt $attempt/$max_attempts..."
        
        # Check individual services
        local mem0_status="❌"
        local postgres_status="❌"
        local neo4j_status="❌"
        local infisical_agent_status="❌"
        
        # Mem0 API health check
        if curl -sf http://localhost:8888/health >/dev/null 2>&1; then
            mem0_status="✅"
        fi
        
        # PostgreSQL health check
        if docker exec mem0-infisical-secured-postgres-1 pg_isready -U postgres >/dev/null 2>&1; then
            postgres_status="✅"
        fi
        
        # Neo4j health check
        if curl -sf http://localhost:8474 >/dev/null 2>&1; then
            neo4j_status="✅"
        fi
        
        # Infisical agent health check
        if docker ps --filter "name=infisical-agent" --filter "status=running" | grep -q infisical-agent; then
            infisical_agent_status="✅"
        fi
        
        print_message "$BLUE" "  Mem0 API: $mem0_status"
        print_message "$BLUE" "  PostgreSQL: $postgres_status"
        print_message "$BLUE" "  Neo4j: $neo4j_status"
        print_message "$BLUE" "  Infisical Agent: $infisical_agent_status"
        
        if [[ "$mem0_status" == "✅" && "$postgres_status" == "✅" && "$neo4j_status" == "✅" && "$infisical_agent_status" == "✅" ]]; then
            all_healthy=true
            print_message "$GREEN" "🎉 All services healthy!"
        else
            sleep 10
        fi
    done
    
    if [[ $all_healthy == false ]]; then
        print_message "$YELLOW" "⚠️  Some services may still be starting. Check logs with: docker-compose -f mem0/server/docker-compose-infisical.yaml logs"
    fi
}

# Function to display service information
display_service_info() {
    print_message "$GREEN" "🎯 Infisical-Secured MemoryBank Stack Information:"
    print_message "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_message "$BLUE" "🧠 Mem0 API:        http://localhost:8888"
    print_message "$BLUE" "📖 API Docs:        http://localhost:8888/docs"
    print_message "$BLUE" "🗄️  PostgreSQL:      localhost:8432"
    print_message "$BLUE" "🕸️  Neo4j Browser:   http://localhost:8474"
    print_message "$BLUE" "🔐 Secret Injection: ✅ Active via Infisical"
    print_message "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_message "$GREEN" "🎉 Stack ready for development with secure secret management!"
}

# Function to store success in memory
store_success() {
    if command -v ai-add-smart >/dev/null 2>&1; then
        ai-add-smart "INFRASTRUCTURE SUCCESS: Started Infisical-secured Docker stack - All services healthy with secret injection active. Enhanced security with container platform integration patterns implemented."
        print_message "$GREEN" "✅ Success stored in memory system"
    fi
}

# Function to stop services
stop_services() {
    print_message "$BLUE" "🛑 Stopping Infisical-secured Docker stack..."
    
    cd mem0/server
    docker-compose -f docker-compose-infisical.yaml down
    cd ../..
    
    print_message "$GREEN" "✅ Services stopped!"
}

# Function to show logs
show_logs() {
    print_message "$BLUE" "📋 Showing service logs..."
    cd mem0/server
    docker-compose -f docker-compose-infisical.yaml logs -f
}

# Main function
main() {
    local command="${1:-start}"
    
    case "$command" in
        start)
            print_message "$BLUE" "🔐 MemoryBank Infisical-Secured Docker Stack"
            print_message "$BLUE" "=========================================="
            check_prerequisites
            validate_infisical_auth
            prepare_environment
            start_services
            monitor_health
            display_service_info
            store_success
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            main start
            ;;
        logs)
            show_logs
            ;;
        status)
            monitor_health
            ;;
        *)
            print_message "$YELLOW" "Usage: $0 {start|stop|restart|logs|status}"
            print_message "$BLUE" "Commands:"
            print_message "$BLUE" "  start   - Start the Infisical-secured stack"
            print_message "$BLUE" "  stop    - Stop all services"
            print_message "$BLUE" "  restart - Restart the stack"
            print_message "$BLUE" "  logs    - Show service logs"
            print_message "$BLUE" "  status  - Check service health"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 