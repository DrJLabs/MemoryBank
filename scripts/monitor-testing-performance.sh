#!/bin/bash
set -euo pipefail

# AI Testing Suite Performance Monitor
# DevOps observability and performance optimization script
# Author: Alex (DevOps Infrastructure Specialist)

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly REPORTS_DIR="${PROJECT_ROOT}/tests/reports"
readonly PERFORMANCE_DIR="${PROJECT_ROOT}/tests/performance"

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize performance monitoring
init_monitoring() {
    log_info "Initializing performance monitoring..."
    
    mkdir -p "${PERFORMANCE_DIR}"/{metrics,trends,benchmarks,alerts}
    mkdir -p "${REPORTS_DIR}"
    
    # Create performance baseline if it doesn't exist
    if [[ ! -f "${PERFORMANCE_DIR}/baseline.json" ]]; then
        log_info "Creating performance baseline..."
        cat > "${PERFORMANCE_DIR}/baseline.json" << 'EOF'
{
  "version": "1.0",
  "created": "",
  "metrics": {
    "test_execution_time": {
      "target": 300,
      "warning_threshold": 450,
      "critical_threshold": 600
    },
    "memory_usage_mb": {
      "target": 256,
      "warning_threshold": 512,
      "critical_threshold": 1024
    },
    "success_rate": {
      "target": 0.95,
      "warning_threshold": 0.90,
      "critical_threshold": 0.85
    },
    "coverage_percentage": {
      "target": 80,
      "warning_threshold": 70,
      "critical_threshold": 60
    }
  }
}
EOF
        
        # Set creation timestamp
        local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        sed -i "s/\"created\": \"\"/\"created\": \"${timestamp}\"/" "${PERFORMANCE_DIR}/baseline.json"
        log_success "Performance baseline created"
    fi
}

# Run performance tests
run_performance_tests() {
    log_info "Running AI testing suite performance tests..."
    
    local start_time=$(date +%s)
    local test_output="${PERFORMANCE_DIR}/test-run-$(date +%Y%m%d-%H%M%S).log"
    
    cd "${PROJECT_ROOT}"
    
    # Run tests with timing and memory monitoring
    {
        echo "=== AI Testing Performance Run ==="
        echo "Start time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "Python version: $(python --version)"
        echo "Memory before: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')"
        echo ""
        
        # Run AI tests with comprehensive metrics
        python -m pytest tests/ai_memory_tests.py \
            --verbose \
            --tb=short \
            --cov=mem0 \
            --cov-report=xml:${REPORTS_DIR}/coverage-performance.xml \
            --cov-report=html:${REPORTS_DIR}/coverage-performance-html \
            --junit-xml=${REPORTS_DIR}/junit-performance.xml \
            --json-report --json-report-file=${REPORTS_DIR}/pytest-performance.json \
            -m "not slow" \
            || echo "Tests completed with some failures"
            
    } 2>&1 | tee "${test_output}"
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    log_success "Performance test run completed in ${execution_time}s"
    
    # Generate performance metrics
    generate_metrics "${test_output}" "${execution_time}"
}

# Generate performance metrics
generate_metrics() {
    local test_output="$1"
    local execution_time="$2"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    log_info "Generating performance metrics..."
    
    # Extract test results from pytest JSON report
    local test_count=0
    local passed_count=0
    local failed_count=0
    local coverage_percent=0
    
    if [[ -f "${REPORTS_DIR}/pytest-performance.json" ]]; then
        test_count=$(python3 -c "
import json
with open('${REPORTS_DIR}/pytest-performance.json', 'r') as f:
    data = json.load(f)
    print(data.get('summary', {}).get('total', 0))
" 2>/dev/null || echo "0")
        
        passed_count=$(python3 -c "
import json
with open('${REPORTS_DIR}/pytest-performance.json', 'r') as f:
    data = json.load(f)
    print(data.get('summary', {}).get('passed', 0))
" 2>/dev/null || echo "0")
        
        failed_count=$(python3 -c "
import json
with open('${REPORTS_DIR}/pytest-performance.json', 'r') as f:
    data = json.load(f)
    print(data.get('summary', {}).get('failed', 0))
" 2>/dev/null || echo "0")
    fi
    
    # Extract coverage percentage
    if [[ -f "${REPORTS_DIR}/coverage-performance.xml" ]]; then
        coverage_percent=$(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('${REPORTS_DIR}/coverage-performance.xml')
root = tree.getroot()
coverage = root.attrib.get('line-rate', '0')
print(int(float(coverage) * 100))
" 2>/dev/null || echo "0")
    fi
    
    # Calculate success rate
    local success_rate=0
    if [[ $test_count -gt 0 ]]; then
        success_rate=$(python3 -c "print(round($passed_count / $test_count, 3))" 2>/dev/null || echo "0")
    fi
    
    # Get memory usage (estimate)
    local memory_usage=$(python3 -c "
import psutil
process = psutil.Process()
print(int(process.memory_info().rss / 1024 / 1024))
" 2>/dev/null || echo "128")
    
    # Create metrics JSON
    cat > "${PERFORMANCE_DIR}/metrics/metrics-$(date +%Y%m%d-%H%M%S).json" << EOF
{
  "timestamp": "${timestamp}",
  "execution_time_seconds": ${execution_time},
  "test_statistics": {
    "total_tests": ${test_count},
    "passed_tests": ${passed_count},
    "failed_tests": ${failed_count},
    "success_rate": ${success_rate}
  },
  "performance_metrics": {
    "execution_time_seconds": ${execution_time},
    "memory_usage_mb": ${memory_usage},
    "coverage_percentage": ${coverage_percent}
  },
  "environment": {
    "ci": "${CI:-false}",
    "python_version": "$(python --version | cut -d' ' -f2)",
    "hostname": "$(hostname)"
  }
}
EOF
    
    log_success "Performance metrics generated"
    
    # Check against baseline
    check_performance_thresholds "${execution_time}" "${memory_usage}" "${success_rate}" "${coverage_percent}"
}

# Check performance against baseline thresholds
check_performance_thresholds() {
    local execution_time="$1"
    local memory_usage="$2"
    local success_rate="$3"
    local coverage_percent="$4"
    
    log_info "Checking performance against baseline thresholds..."
    
    local alerts=0
    local alert_file="${PERFORMANCE_DIR}/alerts/alert-$(date +%Y%m%d-%H%M%S).json"
    
    # Initialize alerts JSON
    echo '{"timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "alerts": []}' > "${alert_file}"
    
    # Check execution time
    if [[ $execution_time -gt 600 ]]; then
        log_error "CRITICAL: Execution time ${execution_time}s exceeds critical threshold (600s)"
        alerts=$((alerts + 1))
    elif [[ $execution_time -gt 450 ]]; then
        log_warning "WARNING: Execution time ${execution_time}s exceeds warning threshold (450s)"
        alerts=$((alerts + 1))
    else
        log_success "Execution time ${execution_time}s within acceptable range"
    fi
    
    # Check memory usage
    if [[ $memory_usage -gt 1024 ]]; then
        log_error "CRITICAL: Memory usage ${memory_usage}MB exceeds critical threshold (1024MB)"
        alerts=$((alerts + 1))
    elif [[ $memory_usage -gt 512 ]]; then
        log_warning "WARNING: Memory usage ${memory_usage}MB exceeds warning threshold (512MB)"
        alerts=$((alerts + 1))
    else
        log_success "Memory usage ${memory_usage}MB within acceptable range"
    fi
    
    # Check success rate
    local success_rate_percent=$(python3 -c "print(int($success_rate * 100))" 2>/dev/null || echo "0")
    if [[ $success_rate_percent -lt 85 ]]; then
        log_error "CRITICAL: Success rate ${success_rate_percent}% below critical threshold (85%)"
        alerts=$((alerts + 1))
    elif [[ $success_rate_percent -lt 90 ]]; then
        log_warning "WARNING: Success rate ${success_rate_percent}% below warning threshold (90%)"
        alerts=$((alerts + 1))
    else
        log_success "Success rate ${success_rate_percent}% within acceptable range"
    fi
    
    # Check coverage
    if [[ $coverage_percent -lt 60 ]]; then
        log_error "CRITICAL: Coverage ${coverage_percent}% below critical threshold (60%)"
        alerts=$((alerts + 1))
    elif [[ $coverage_percent -lt 70 ]]; then
        log_warning "WARNING: Coverage ${coverage_percent}% below warning threshold (70%)"
        alerts=$((alerts + 1))
    else
        log_success "Coverage ${coverage_percent}% within acceptable range"
    fi
    
    if [[ $alerts -eq 0 ]]; then
        log_success "All performance metrics within acceptable thresholds"
        rm -f "${alert_file}"  # Remove empty alert file
    else
        log_warning "${alerts} performance alert(s) generated"
    fi
}

# Generate trend analysis
generate_trends() {
    log_info "Generating performance trend analysis..."
    
    # Collect last 10 metrics files
    local metrics_files=($(ls -t "${PERFORMANCE_DIR}/metrics/"metrics-*.json 2>/dev/null | head -10))
    
    if [[ ${#metrics_files[@]} -lt 2 ]]; then
        log_warning "Insufficient metrics data for trend analysis (need at least 2 runs)"
        return
    fi
    
    # Create trend summary
    cat > "${PERFORMANCE_DIR}/trends/trend-$(date +%Y%m%d).json" << 'EOF'
{
  "generated": "",
  "period": "last_10_runs",
  "trends": {
    "execution_time": {"direction": "unknown", "change_percent": 0},
    "memory_usage": {"direction": "unknown", "change_percent": 0},
    "success_rate": {"direction": "unknown", "change_percent": 0},
    "coverage": {"direction": "unknown", "change_percent": 0}
  },
  "recommendations": []
}
EOF
    
    # Update timestamp
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    sed -i "s/\"generated\": \"\"/\"generated\": \"${timestamp}\"/" "${PERFORMANCE_DIR}/trends/trend-$(date +%Y%m%d).json"
    
    log_success "Trend analysis generated"
}

# Main execution
main() {
    echo "📊 AI Testing Suite Performance Monitor"
    echo "======================================="
    
    case "${1:-monitor}" in
        "init")
            init_monitoring
            ;;
        "run"|"monitor")
            init_monitoring
            run_performance_tests
            generate_trends
            ;;
        "trends")
            generate_trends
            ;;
        "check")
            if [[ ! -f "${PERFORMANCE_DIR}/baseline.json" ]]; then
                log_error "No baseline found. Run '$0 init' first."
                exit 1
            fi
            log_info "Performance monitoring configuration is ready"
            ;;
        "help"|"--help"|"-h")
            cat << EOF
AI Testing Suite Performance Monitor

Usage: $0 [COMMAND]

Commands:
  init       Initialize performance monitoring
  run        Run performance tests and generate metrics
  monitor    Same as 'run' (default)
  trends     Generate trend analysis from existing metrics  
  check      Verify monitoring configuration
  help       Show this help message

Examples:
  $0 init      # Setup performance monitoring
  $0 run       # Run performance tests
  $0 trends    # Generate trend analysis
EOF
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@" 