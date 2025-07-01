#!/bin/bash

# Health Check Script for Memory Bank Services
# Monitors both main and renovate branch services with detailed reporting

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMEOUT=10
VERBOSE=false
CONTINUOUS=false
INTERVAL=30
OUTPUT_FORMAT="text"  # text, json, prometheus

# Service definitions
declare -A MAIN_SERVICES=(
    ["mem0-server"]="http://localhost:8888/health"
    ["openmemory-api"]="http://localhost:8765/health"
    ["qdrant-vector"]="http://localhost:6333/health"
    ["neo4j-http"]="http://localhost:8474"
    ["postgres-main"]="postgresql://postgres:postgres@localhost:8432/postgres"
    ["redis-main"]="redis://localhost:6379"
)

declare -A RENOVATE_SERVICES=(
    ["renovate-mem0"]="http://localhost:9888/health"
    ["renovate-openmemory"]="http://localhost:9765/health"
    ["renovate-qdrant"]="http://localhost:7333/health"
    ["renovate-neo4j"]="http://localhost:9474"
    ["renovate-postgres"]="postgresql://postgres:postgres@localhost:9432/renovate_mem0"
    ["renovate-redis"]="redis://localhost:7379"
)

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️${NC} $1"
}

log_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] ℹ️${NC} $1"
}

# Usage information
show_usage() {
    cat << EOF
Health Check Script for Memory Bank Services

Usage: $0 [OPTIONS] [TARGET]

OPTIONS:
    -v, --verbose           Verbose output with detailed information
    -c, --continuous        Continuous monitoring mode
    -i, --interval SECONDS  Interval for continuous mode (default: 30)
    -t, --timeout SECONDS   Timeout for health checks (default: 10)
    -f, --format FORMAT     Output format: text, json, prometheus (default: text)
    -h, --help              Show this help message

TARGETS:
    main                    Check only main branch services
    renovate               Check only renovate branch services
    all                    Check both main and renovate services (default)
    containers             Check Docker container status
    ports                  Check port availability
    dependencies           Check external dependencies

EXAMPLES:
    $0                      # Check all services
    $0 main                 # Check only main services
    $0 -c -i 60            # Continuous monitoring every 60 seconds
    $0 -f json             # Output in JSON format
    $0 --verbose renovate  # Verbose check of renovate services

EOF
}

# Check if a port is open
check_port() {
    local port=$1
    local host=${2:-localhost}
    
    if timeout $TIMEOUT bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local service_name=$2
    
    local response
    local http_code
    local response_time
    
    # Measure response time
    local start_time=$(date +%s.%N)
    
    if response=$(timeout $TIMEOUT curl -s -w "%{http_code}" "$url" 2>/dev/null); then
        local end_time=$(date +%s.%N)
        response_time=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
        
        http_code="${response: -3}"
        response_body="${response%???}"
        
        if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
            if [ "$VERBOSE" = true ]; then
                log_success "$service_name: HTTP $http_code (${response_time}s)"
            else
                log_success "$service_name: Healthy"
            fi
            return 0
        else
            log_error "$service_name: HTTP $http_code"
            return 1
        fi
    else
        log_error "$service_name: Connection failed"
        return 1
    fi
}

# Check PostgreSQL connection
check_postgres() {
    local connection_string=$1
    local service_name=$2
    
    # Extract components from connection string
    local host=$(echo "$connection_string" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    local port=$(echo "$connection_string" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    local db=$(echo "$connection_string" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    local user=$(echo "$connection_string" | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    
    if command -v pg_isready >/dev/null 2>&1; then
        if timeout $TIMEOUT pg_isready -h "$host" -p "$port" -d "$db" -U "$user" >/dev/null 2>&1; then
            log_success "$service_name: Database accessible"
            return 0
        else
            log_error "$service_name: Database connection failed"
            return 1
        fi
    else
        # Fallback to port check
        if check_port "$port" "$host"; then
            log_warning "$service_name: Port open (pg_isready not available)"
            return 0
        else
            log_error "$service_name: Port closed"
            return 1
        fi
    fi
}

# Check Redis connection
check_redis() {
    local connection_string=$1
    local service_name=$2
    
    local host=$(echo "$connection_string" | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    local port=$(echo "$connection_string" | sed -n 's/.*:\([0-9]*\).*/\1/p')
    
    if command -v redis-cli >/dev/null 2>&1; then
        if timeout $TIMEOUT redis-cli -h "$host" -p "$port" ping >/dev/null 2>&1; then
            log_success "$service_name: Redis responding"
            return 0
        else
            log_error "$service_name: Redis connection failed"
            return 1
        fi
    else
        # Fallback to port check
        if check_port "$port" "$host"; then
            log_warning "$service_name: Port open (redis-cli not available)"
            return 0
        else
            log_error "$service_name: Port closed"
            return 1
        fi
    fi
}

# Check individual service
check_service() {
    local service_name=$1
    local endpoint=$2
    
    if [[ "$endpoint" =~ ^http ]]; then
        check_http_endpoint "$endpoint" "$service_name"
    elif [[ "$endpoint" =~ ^postgresql ]]; then
        check_postgres "$endpoint" "$service_name"
    elif [[ "$endpoint" =~ ^redis ]]; then
        check_redis "$endpoint" "$service_name"
    else
        log_error "$service_name: Unknown endpoint type: $endpoint"
        return 1
    fi
}

# Check Docker containers
check_containers() {
    local filter_pattern=${1:-""}
    
    log "🐳 Docker Container Status"
    echo "=========================="
    
    if [ -n "$filter_pattern" ]; then
        docker ps --filter "name=$filter_pattern" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || {
            log_error "Failed to get Docker container status"
            return 1
        }
    else
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -20 2>/dev/null || {
            log_error "Failed to get Docker container status"
            return 1
        }
    fi
    
    echo
}

# Check port availability
check_ports() {
    local target=$1
    
    log "🔌 Port Availability Check"
    echo "=========================="
    
    local ports_to_check=()
    
    case "$target" in
        "main")
            ports_to_check=(8888 8432 8474 8687 6333 8765 6379)
            ;;
        "renovate")
            ports_to_check=(9888 9432 9474 9687 7333 9765 7379 4000 9000 9091 4001)
            ;;
        "all"|*)
            ports_to_check=(8888 8432 8474 8687 6333 8765 6379 9888 9432 9474 9687 7333 9765 7379 4000 9000 9091 4001)
            ;;
    esac
    
    for port in "${ports_to_check[@]}"; do
        if check_port "$port"; then
            log_success "Port $port: Open"
        else
            log_warning "Port $port: Closed"
        fi
    done
    
    echo
}

# Generate JSON output
generate_json_output() {
    local target=$1
    local results=()
    
    case "$target" in
        "main")
            for service in "${!MAIN_SERVICES[@]}"; do
                if check_service "$service" "${MAIN_SERVICES[$service]}" >/dev/null 2>&1; then
                    results+=("\"$service\": {\"status\": \"healthy\", \"endpoint\": \"${MAIN_SERVICES[$service]}\"}")
                else
                    results+=("\"$service\": {\"status\": \"unhealthy\", \"endpoint\": \"${MAIN_SERVICES[$service]}\"}")
                fi
            done
            ;;
        "renovate")
            for service in "${!RENOVATE_SERVICES[@]}"; do
                if check_service "$service" "${RENOVATE_SERVICES[$service]}" >/dev/null 2>&1; then
                    results+=("\"$service\": {\"status\": \"healthy\", \"endpoint\": \"${RENOVATE_SERVICES[$service]}\"}")
                else
                    results+=("\"$service\": {\"status\": \"unhealthy\", \"endpoint\": \"${RENOVATE_SERVICES[$service]}\"}")
                fi
            done
            ;;
        "all")
            # Combine both main and renovate
            for service in "${!MAIN_SERVICES[@]}"; do
                if check_service "$service" "${MAIN_SERVICES[$service]}" >/dev/null 2>&1; then
                    results+=("\"$service\": {\"status\": \"healthy\", \"endpoint\": \"${MAIN_SERVICES[$service]}\"}")
                else
                    results+=("\"$service\": {\"status\": \"unhealthy\", \"endpoint\": \"${MAIN_SERVICES[$service]}\"}")
                fi
            done
            for service in "${!RENOVATE_SERVICES[@]}"; do
                if check_service "$service" "${RENOVATE_SERVICES[$service]}" >/dev/null 2>&1; then
                    results+=("\"$service\": {\"status\": \"healthy\", \"endpoint\": \"${RENOVATE_SERVICES[$service]}\"}")
                else
                    results+=("\"$service\": {\"status\": \"unhealthy\", \"endpoint\": \"${RENOVATE_SERVICES[$service]}\"}")
                fi
            done
            ;;
    esac
    
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"target\": \"$target\","
    echo "  \"services\": {"
    printf "    %s" "${results[0]}"
    for result in "${results[@]:1}"; do
        printf ",\n    %s" "$result"
    done
    echo ""
    echo "  }"
    echo "}"
}

# Run health checks
run_health_checks() {
    local target=$1
    
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        generate_json_output "$target"
        return
    fi
    
    log "🏥 Health Check Report - $(date)"
    echo "======================================="
    
    local total_services=0
    local healthy_services=0
    
    case "$target" in
        "main")
            log "📊 Main Branch Services"
            echo "----------------------"
            for service in "${!MAIN_SERVICES[@]}"; do
                ((total_services++))
                if check_service "$service" "${MAIN_SERVICES[$service]}"; then
                    ((healthy_services++))
                fi
            done
            ;;
        "renovate")
            log "🔄 Renovate Branch Services"
            echo "--------------------------"
            for service in "${!RENOVATE_SERVICES[@]}"; do
                ((total_services++))
                if check_service "$service" "${RENOVATE_SERVICES[$service]}"; then
                    ((healthy_services++))
                fi
            done
            ;;
        "all")
            log "📊 Main Branch Services"
            echo "----------------------"
            for service in "${!MAIN_SERVICES[@]}"; do
                ((total_services++))
                if check_service "$service" "${MAIN_SERVICES[$service]}"; then
                    ((healthy_services++))
                fi
            done
            echo
            log "🔄 Renovate Branch Services"
            echo "--------------------------"
            for service in "${!RENOVATE_SERVICES[@]}"; do
                ((total_services++))
                if check_service "$service" "${RENOVATE_SERVICES[$service]}"; then
                    ((healthy_services++))
                fi
            done
            ;;
        "containers")
            check_containers
            return
            ;;
        "ports")
            check_ports "all"
            return
            ;;
    esac
    
    echo
    log "📈 Summary"
    echo "==========="
    log_info "Total Services: $total_services"
    log_info "Healthy: $healthy_services"
    log_info "Unhealthy: $((total_services - healthy_services))"
    
    local health_percentage=$((healthy_services * 100 / total_services))
    
    if [ $health_percentage -eq 100 ]; then
        log_success "Overall Status: All systems operational ($health_percentage%)"
    elif [ $health_percentage -ge 80 ]; then
        log_warning "Overall Status: Mostly operational ($health_percentage%)"
    else
        log_error "Overall Status: Multiple issues detected ($health_percentage%)"
    fi
    
    echo
}

# Continuous monitoring mode
continuous_monitoring() {
    local target=$1
    
    log "🔄 Starting continuous monitoring (every ${INTERVAL}s)"
    log "Press Ctrl+C to stop"
    echo
    
    while true; do
        clear
        run_health_checks "$target"
        echo "Next check in ${INTERVAL} seconds..."
        sleep $INTERVAL
    done
}

# Main function
main() {
    local target="all"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--continuous)
                CONTINUOUS=true
                shift
                ;;
            -i|--interval)
                INTERVAL="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            main|renovate|all|containers|ports|dependencies)
                target="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate output format
    if [[ "$OUTPUT_FORMAT" != "text" && "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "prometheus" ]]; then
        log_error "Invalid output format: $OUTPUT_FORMAT"
        exit 1
    fi
    
    # Check if required tools are available
    if ! command -v curl >/dev/null 2>&1; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "docker is not available - container checks will be skipped"
    fi
    
    # Run checks
    if [ "$CONTINUOUS" = true ]; then
        continuous_monitoring "$target"
    else
        run_health_checks "$target"
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 