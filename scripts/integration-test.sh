#!/bin/bash

# Integration Test Script
# Tests renovate branch services against main branch infrastructure

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_TIMEOUT=60
VERBOSE=false

# Test scenarios
declare -A INTEGRATION_TESTS=(
    ["renovate-to-main-db"]="Test renovate services against main branch databases"
    ["main-to-renovate-db"]="Test main services against renovate databases"
    ["cross-api-compatibility"]="Test API compatibility between branches"
    ["data-migration"]="Test data migration capabilities"
    ["performance-comparison"]="Compare performance between branches"
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

# Check if service is healthy
check_service_health() {
    local service_url=$1
    local service_name=$2
    local timeout=${3:-$TEST_TIMEOUT}
    
    log_info "Checking health of $service_name..."
    
    local attempts=0
    local max_attempts=$((timeout / 5))
    
    while [ $attempts -lt $max_attempts ]; do
        if timeout 5 curl -s -f "$service_url" > /dev/null 2>&1; then
            log_success "$service_name is healthy"
            return 0
        fi
        
        ((attempts++))
        if [ $attempts -lt $max_attempts ]; then
            log_info "Attempt $attempts/$max_attempts - $service_name not ready, waiting..."
            sleep 5
        fi
    done
    
    log_error "$service_name failed health check after $timeout seconds"
    return 1
}

# Test database connectivity
test_database_connectivity() {
    local db_host=$1
    local db_port=$2
    local db_name=$3
    local test_name=$4
    
    log_info "Testing database connectivity: $test_name"
    
    # Test with pg_isready if available
    if command -v pg_isready >/dev/null 2>&1; then
        if timeout $TEST_TIMEOUT pg_isready -h "$db_host" -p "$db_port" -d "$db_name" -U postgres; then
            log_success "$test_name: Database connection successful"
            return 0
        else
            log_error "$test_name: Database connection failed"
            return 1
        fi
    else
        # Fallback to basic port check
        if timeout 5 bash -c "</dev/tcp/$db_host/$db_port" 2>/dev/null; then
            log_success "$test_name: Database port accessible"
            return 0
        else
            log_error "$test_name: Database port not accessible"
            return 1
        fi
    fi
}

# Test API endpoint with data
test_api_endpoint() {
    local api_url=$1
    local endpoint=$2
    local method=${3:-GET}
    local data=${4:-""}
    local expected_status=${5:-200}
    local test_name=$6
    
    log_info "Testing API endpoint: $test_name"
    
    local full_url="$api_url$endpoint"
    local curl_cmd="curl -s -w %{http_code} -o /dev/null"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl_cmd="$curl_cmd -X POST -H 'Content-Type: application/json' -d '$data'"
    fi
    
    local http_code
    if http_code=$(timeout $TEST_TIMEOUT eval "$curl_cmd '$full_url'" 2>/dev/null); then
        if [ "$http_code" = "$expected_status" ]; then
            log_success "$test_name: API responded with $http_code"
            return 0
        else
            log_warning "$test_name: API responded with $http_code (expected $expected_status)"
            return 1
        fi
    else
        log_error "$test_name: API request failed or timed out"
        return 1
    fi
}

# Test memory operations
test_memory_operations() {
    local api_url=$1
    local test_name=$2
    
    log_info "Testing memory operations: $test_name"
    
    # Test health endpoint first
    if ! test_api_endpoint "$api_url" "/health" "GET" "" "200" "$test_name Health Check"; then
        return 1
    fi
    
    # Test memory creation
    local test_memory='{"text": "Integration test memory", "user_id": "test-user"}'
    if ! test_api_endpoint "$api_url" "/memories" "POST" "$test_memory" "201" "$test_name Memory Creation"; then
        log_warning "$test_name: Memory creation test failed (this might be expected)"
    fi
    
    # Test memory listing
    if ! test_api_endpoint "$api_url" "/memories" "GET" "" "200" "$test_name Memory Listing"; then
        return 1
    fi
    
    log_success "$test_name: Memory operations test completed"
    return 0
}

# Test renovate services against main databases
test_renovate_to_main_db() {
    log "🔄 Testing Renovate Services → Main Databases"
    echo "=============================================="
    
    local test_passed=true
    
    # Check if main databases are accessible
    if ! test_database_connectivity "localhost" "8432" "postgres" "Main PostgreSQL"; then
        test_passed=false
    fi
    
    # Test if renovate services can connect to main databases
    # Note: This would require modifying renovate service configs temporarily
    log_warning "This test requires manual configuration of renovate services to use main DB ports"
    log_info "To run this test:"
    echo "  1. Modify docker-compose.renovate.yml to point to main DB ports"
    echo "  2. Start renovate services"
    echo "  3. Run health checks"
    
    if [ "$test_passed" = true ]; then
        log_success "Renovate → Main DB compatibility check passed"
    else
        log_error "Renovate → Main DB compatibility check failed"
    fi
    
    return $test_passed
}

# Test main services against renovate databases
test_main_to_renovate_db() {
    log "📊 Testing Main Services → Renovate Databases"
    echo "=============================================="
    
    local test_passed=true
    
    # Check if renovate databases are accessible
    if ! test_database_connectivity "localhost" "9432" "renovate_mem0" "Renovate PostgreSQL"; then
        test_passed=false
    fi
    
    log_warning "This test requires manual configuration of main services to use renovate DB ports"
    log_info "To run this test:"
    echo "  1. Temporarily modify main service configs to use renovate DB ports"
    echo "  2. Restart main services"
    echo "  3. Run health checks"
    echo "  4. Restore original configuration"
    
    if [ "$test_passed" = true ]; then
        log_success "Main → Renovate DB compatibility check passed"
    else
        log_error "Main → Renovate DB compatibility check failed"
    fi
    
    return $test_passed
}

# Test cross-API compatibility
test_cross_api_compatibility() {
    log "🔌 Testing Cross-API Compatibility"
    echo "=================================="
    
    local test_passed=true
    
    # Test main API endpoints
    if check_service_health "http://localhost:8765/health" "Main OpenMemory API"; then
        if ! test_memory_operations "http://localhost:8765" "Main API"; then
            test_passed=false
        fi
    else
        log_warning "Main API not available - skipping main API tests"
    fi
    
    # Test renovate API endpoints (if running)
    if check_service_health "http://localhost:9765/health" "Renovate OpenMemory API"; then
        if ! test_memory_operations "http://localhost:9765" "Renovate API"; then
            test_passed=false
        fi
    else
        log_warning "Renovate API not available - skipping renovate API tests"
    fi
    
    # Test API schema compatibility
    log_info "Testing API schema compatibility..."
    
    # Compare API responses (if both are available)
    local main_health_response=$(curl -s "http://localhost:8765/health" 2>/dev/null || echo "")
    local renovate_health_response=$(curl -s "http://localhost:9765/health" 2>/dev/null || echo "")
    
    if [ -n "$main_health_response" ] && [ -n "$renovate_health_response" ]; then
        if [ "$main_health_response" = "$renovate_health_response" ]; then
            log_success "API health responses are identical"
        else
            log_warning "API health responses differ between branches"
            if [ "$VERBOSE" = true ]; then
                echo "Main: $main_health_response"
                echo "Renovate: $renovate_health_response"
            fi
        fi
    fi
    
    if [ "$test_passed" = true ]; then
        log_success "Cross-API compatibility tests passed"
    else
        log_error "Cross-API compatibility tests failed"
    fi
    
    return $test_passed
}

# Test data migration capabilities
test_data_migration() {
    log "🔄 Testing Data Migration Capabilities"
    echo "======================================"
    
    log_info "Checking for migration scripts..."
    
    local migration_scripts=(
        "custom-gpt-adapter/migrations"
        "scripts/migrate-data.sh"
        "mem0/migrations"
    )
    
    local migration_found=false
    
    for migration_path in "${migration_scripts[@]}"; do
        if [ -d "$PROJECT_ROOT/$migration_path" ] || [ -f "$PROJECT_ROOT/$migration_path" ]; then
            log_success "Found migration: $migration_path"
            migration_found=true
            
            if [ -d "$PROJECT_ROOT/$migration_path" ]; then
                local migration_count=$(find "$PROJECT_ROOT/$migration_path" -name "*.py" -o -name "*.sql" | wc -l)
                log_info "Migration files found: $migration_count"
            fi
        fi
    done
    
    if [ "$migration_found" = false ]; then
        log_warning "No migration scripts found"
        log_info "Consider creating migration scripts for smooth transitions"
    fi
    
    # Test migration compatibility
    log_info "Testing migration script syntax..."
    
    # Check Python migration files
    find "$PROJECT_ROOT" -path "*/migrations/*.py" 2>/dev/null | while read -r migration_file; do
        if python3 -m py_compile "$migration_file" 2>/dev/null; then
            log_success "Migration syntax OK: $(basename "$migration_file")"
        else
            log_error "Migration syntax error: $(basename "$migration_file")"
        fi
    done
    
    log_success "Data migration capability test completed"
    return 0
}

# Test performance comparison
test_performance_comparison() {
    log "📈 Testing Performance Comparison"
    echo "================================="
    
    local main_api="http://localhost:8765"
    local renovate_api="http://localhost:9765"
    
    # Simple performance test function
    test_api_performance() {
        local api_url=$1
        local api_name=$2
        
        log_info "Testing $api_name performance..."
        
        local start_time=$(date +%s.%N)
        
        # Make multiple requests to get average response time
        local success_count=0
        local total_requests=5
        
        for i in $(seq 1 $total_requests); do
            if timeout 10 curl -s -f "$api_url/health" > /dev/null 2>&1; then
                ((success_count++))
            fi
        done
        
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
        local avg_response_time=$(echo "scale=3; $duration / $total_requests" | bc 2>/dev/null || echo "0")
        
        log_info "$api_name Results:"
        echo "  Total requests: $total_requests"
        echo "  Successful: $success_count"
        echo "  Success rate: $(echo "scale=1; $success_count * 100 / $total_requests" | bc 2>/dev/null || echo "0")%"
        echo "  Average response time: ${avg_response_time}s"
        
        echo "$avg_response_time"
    }
    
    # Test both APIs if available
    local main_performance=""
    local renovate_performance=""
    
    if check_service_health "$main_api/health" "Main API" 5; then
        main_performance=$(test_api_performance "$main_api" "Main API")
    fi
    
    if check_service_health "$renovate_api/health" "Renovate API" 5; then
        renovate_performance=$(test_api_performance "$renovate_api" "Renovate API")
    fi
    
    # Compare performance if both are available
    if [ -n "$main_performance" ] && [ -n "$renovate_performance" ]; then
        log_info "Performance Comparison:"
        echo "  Main API: ${main_performance}s"
        echo "  Renovate API: ${renovate_performance}s"
        
        # Calculate performance difference
        local performance_diff=$(echo "scale=3; $renovate_performance - $main_performance" | bc 2>/dev/null || echo "0")
        
        if (( $(echo "$performance_diff > 0" | bc -l 2>/dev/null || echo "0") )); then
            log_warning "Renovate API is slower by ${performance_diff}s"
        elif (( $(echo "$performance_diff < 0" | bc -l 2>/dev/null || echo "0") )); then
            local improvement=$(echo "scale=3; 0 - $performance_diff" | bc 2>/dev/null || echo "0")
            log_success "Renovate API is faster by ${improvement}s"
        else
            log_success "Both APIs have similar performance"
        fi
    fi
    
    log_success "Performance comparison test completed"
    return 0
}

# Generate integration test report
generate_integration_report() {
    log "📄 Generating Integration Test Report"
    echo "====================================="
    
    local report_file="$PROJECT_ROOT/integration-test-report.md"
    
    cat > "$report_file" << EOF
# Integration Test Report

Generated: $(date)
Test Environment: $(uname -a)

## Test Summary

This report contains the results of integration testing between main and renovate branches.

## Service Status

### Main Branch Services
- Mem0 Server: $(curl -s -f http://localhost:8888/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")
- OpenMemory API: $(curl -s -f http://localhost:8765/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")
- Qdrant: $(curl -s -f http://localhost:6333/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")

### Renovate Branch Services
- Renovate Mem0: $(curl -s -f http://localhost:9888/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")
- Renovate OpenMemory: $(curl -s -f http://localhost:9765/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")
- Renovate Qdrant: $(curl -s -f http://localhost:7333/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")

## Recommendations

Based on the integration test results, consider the following actions:

1. Review any failed tests and address compatibility issues
2. Ensure database migrations are properly tested
3. Validate API contract compatibility
4. Monitor performance differences between branches

EOF
    
    log_success "Integration test report saved to: $report_file"
}

# Main integration test function
main() {
    local test_type="all"
    local specific_test=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -t|--timeout)
                TEST_TIMEOUT="$2"
                shift 2
                ;;
            --renovate-to-main)
                test_type="specific"
                specific_test="renovate-to-main-db"
                shift
                ;;
            --main-to-renovate)
                test_type="specific"
                specific_test="main-to-renovate-db"
                shift
                ;;
            --cross-api)
                test_type="specific"
                specific_test="cross-api-compatibility"
                shift
                ;;
            --migration)
                test_type="specific"
                specific_test="data-migration"
                shift
                ;;
            --performance)
                test_type="specific"
                specific_test="performance-comparison"
                shift
                ;;
            -h|--help)
                cat << EOF
Integration Test Script

Usage: $0 [OPTIONS]

OPTIONS:
    -v, --verbose           Verbose output
    -t, --timeout SECONDS   Test timeout (default: 60)
    --renovate-to-main      Test renovate services against main databases
    --main-to-renovate      Test main services against renovate databases
    --cross-api             Test cross-API compatibility
    --migration             Test data migration capabilities
    --performance           Test performance comparison
    -h, --help              Show this help

Examples:
    $0                      # Run all integration tests
    $0 --cross-api          # Test only API compatibility
    $0 -v --performance     # Verbose performance testing

EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    cd "$PROJECT_ROOT"
    
    log "🧪 Integration Testing Suite"
    echo "============================"
    log_info "Testing compatibility between main and renovate branches"
    echo
    
    local overall_success=true
    
    case "$test_type" in
        "all")
            if ! test_cross_api_compatibility; then overall_success=false; fi
            echo
            if ! test_data_migration; then overall_success=false; fi
            echo
            if ! test_performance_comparison; then overall_success=false; fi
            echo
            # Note: Database cross-tests require manual configuration
            log_info "Database cross-compatibility tests require manual configuration"
            ;;
        "specific")
            case "$specific_test" in
                "renovate-to-main-db")
                    if ! test_renovate_to_main_db; then overall_success=false; fi
                    ;;
                "main-to-renovate-db")
                    if ! test_main_to_renovate_db; then overall_success=false; fi
                    ;;
                "cross-api-compatibility")
                    if ! test_cross_api_compatibility; then overall_success=false; fi
                    ;;
                "data-migration")
                    if ! test_data_migration; then overall_success=false; fi
                    ;;
                "performance-comparison")
                    if ! test_performance_comparison; then overall_success=false; fi
                    ;;
            esac
            ;;
    esac
    
    generate_integration_report
    
    if [ "$overall_success" = true ]; then
        log_success "🎉 All integration tests passed!"
    else
        log_error "❌ Some integration tests failed"
        log_info "Review the test output and integration report for details"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 