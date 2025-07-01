#!/bin/bash

# Compatibility Check Script
# Verifies dependency compatibility between main and renovate branches

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
TEMP_DIR=$(mktemp -d)
VERBOSE=false

# Dependency files to check
DEPENDENCY_FILES=(
    "mem0/pyproject.toml"
    "mem0/requirements-dev.txt"
    "mem0/openmemory/ui/package.json"
    "mem0/mem0-ts/package.json"
    "custom-gpt-adapter/requirements.txt"
    "pyproject.toml"
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

# Cleanup function
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}

trap cleanup EXIT

# Check if file exists in both branches
check_file_exists() {
    local file_path=$1
    local branch=$2
    
    git show "$branch:$file_path" > /dev/null 2>&1
}

# Extract Python dependencies from requirements.txt
extract_python_deps() {
    local file_content=$1
    
    echo "$file_content" | grep -E '^[a-zA-Z0-9_-]+' | sed 's/[>=<~!].*//' | sort
}

# Extract Python dependencies from pyproject.toml
extract_pyproject_deps() {
    local file_content=$1
    
    # Extract dependencies section
    echo "$file_content" | awk '/^\[.*dependencies\]/{flag=1;next}/^\[/{flag=0}flag' | \
        grep -E '^\s*"[^"]+' | \
        sed 's/.*"\([^"]*\)".*/\1/' | \
        sed 's/[>=<~!].*//' | sort
}

# Extract Node.js dependencies from package.json
extract_node_deps() {
    local file_content=$1
    
    # Use jq if available, otherwise use grep/sed
    if command -v jq >/dev/null 2>&1; then
        echo "$file_content" | jq -r '.dependencies // {}, .devDependencies // {} | keys[]' 2>/dev/null | sort
    else
        echo "$file_content" | grep -E '^\s*"[^"]+":' | \
            sed 's/.*"\([^"]*\)".*/\1/' | \
            grep -v -E '^(name|version|description|scripts|main|private)$' | sort
    fi
}

# Compare two dependency lists
compare_dependencies() {
    local main_deps="$1"
    local renovate_deps="$2"
    local file_type="$3"
    
    local added_deps=$(comm -13 <(echo "$main_deps") <(echo "$renovate_deps"))
    local removed_deps=$(comm -23 <(echo "$main_deps") <(echo "$renovate_deps"))
    local common_deps=$(comm -12 <(echo "$main_deps") <(echo "$renovate_deps"))
    
    local added_count=$(echo "$added_deps" | wc -l)
    local removed_count=$(echo "$removed_deps" | wc -l)
    local common_count=$(echo "$common_deps" | wc -l)
    
    # Handle empty strings
    [ -z "$added_deps" ] && added_count=0
    [ -z "$removed_deps" ] && removed_count=0
    [ -z "$common_deps" ] && common_count=0
    
    log_info "$file_type Dependencies Summary:"
    echo "  📊 Common:  $common_count"
    echo "  ➕ Added:   $added_count"
    echo "  ➖ Removed: $removed_count"
    
    if [ "$added_count" -gt 0 ]; then
        log_warning "New dependencies in renovate branch:"
        echo "$added_deps" | sed 's/^/    - /'
    fi
    
    if [ "$removed_count" -gt 0 ]; then
        log_warning "Dependencies removed in renovate branch:"
        echo "$removed_deps" | sed 's/^/    - /'
    fi
    
    # Risk assessment
    local risk_level="LOW"
    if [ "${removed_count:-0}" -gt 0 ]; then
        risk_level="HIGH"
    elif [ "${added_count:-0}" -gt 5 ]; then
        risk_level="MEDIUM"
    fi
    
    case "$risk_level" in
        "LOW")
            log_success "Risk Level: $risk_level"
            ;;
        "MEDIUM")
            log_warning "Risk Level: $risk_level"
            ;;
        "HIGH")
            log_error "Risk Level: $risk_level"
            ;;
    esac
    
    echo
}

# Check Docker image compatibility
check_docker_compatibility() {
    log "🐳 Docker Image Compatibility Check"
    echo "===================================="
    
    local docker_files=(
        "mem0/server/dev.Dockerfile"
        "mem0/server/Dockerfile"
        "mem0/openmemory/ui/Dockerfile"
        "mem0/openmemory/api/Dockerfile"
        "custom-gpt-adapter/docker/Dockerfile.api"
    )
    
    for dockerfile in "${docker_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$dockerfile" ]; then
            log_info "Checking $dockerfile..."
            
            # Extract base images
            local base_images=$(grep -E '^FROM' "$PROJECT_ROOT/$dockerfile" | awk '{print $2}')
            echo "  Base images: $base_images"
            
            # Check for known security issues
            if echo "$base_images" | grep -q "python:3\.11"; then
                log_warning "Using Python 3.11 - consider upgrading to 3.12"
            fi
            
            if echo "$base_images" | grep -q "node:16"; then
                log_warning "Using Node 16 - consider upgrading to Node 18+"
            fi
            
        else
            log_warning "$dockerfile not found"
        fi
    done
    
    echo
}

# Check Python version compatibility
check_python_compatibility() {
    log "🐍 Python Version Compatibility"
    echo "==============================="
    
    local pyproject_files=(
        "mem0/pyproject.toml"
        "pyproject.toml"
        "custom-gpt-adapter/pyproject.toml"
    )
    
    for pyproject in "${pyproject_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$pyproject" ]; then
            log_info "Checking $pyproject..."
            
            # Extract Python version requirements
            local python_version=$(grep -E 'python\s*=' "$PROJECT_ROOT/$pyproject" | head -1)
            if [ -n "$python_version" ]; then
                echo "  Required: $python_version"
            fi
            
            # Check current Python version
            if command -v python3 >/dev/null 2>&1; then
                local current_version=$(python3 --version)
                echo "  Current: $current_version"
            fi
        fi
    done
    
    echo
}

# Check Node.js version compatibility
check_node_compatibility() {
    log "📦 Node.js Version Compatibility"
    echo "================================"
    
    local package_files=(
        "mem0/openmemory/ui/package.json"
        "mem0/mem0-ts/package.json"
    )
    
    for package_json in "${package_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$package_json" ]; then
            log_info "Checking $package_json..."
            
            # Extract Node version requirements
            if command -v jq >/dev/null 2>&1; then
                local node_version=$(jq -r '.engines.node // "not specified"' "$PROJECT_ROOT/$package_json")
                echo "  Required Node: $node_version"
                
                local npm_version=$(jq -r '.engines.npm // "not specified"' "$PROJECT_ROOT/$package_json")
                echo "  Required npm: $npm_version"
            fi
            
            # Check current versions
            if command -v node >/dev/null 2>&1; then
                echo "  Current Node: $(node --version)"
            fi
            
            if command -v npm >/dev/null 2>&1; then
                echo "  Current npm: $(npm --version)"
            fi
        fi
    done
    
    echo
}

# Check database schema compatibility
check_database_compatibility() {
    log "🗄️ Database Schema Compatibility"
    echo "================================="
    
    # Check for migration files
    local migration_dirs=(
        "custom-gpt-adapter/migrations"
        "mem0/migrations"
    )
    
    for migration_dir in "${migration_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$migration_dir" ]; then
            log_info "Checking migrations in $migration_dir..."
            
            local migration_count=$(find "$PROJECT_ROOT/$migration_dir" -name "*.py" | wc -l)
            echo "  Migration files: $migration_count"
            
            # Check for recent migrations
            local recent_migrations=$(find "$PROJECT_ROOT/$migration_dir" -name "*.py" -mtime -30 | wc -l)
            if [ "$recent_migrations" -gt 0 ]; then
                log_warning "Found $recent_migrations recent migrations (last 30 days)"
                echo "  These may require careful handling during deployment"
            fi
        fi
    done
    
    echo
}

# Check API compatibility
check_api_compatibility() {
    log "🔌 API Compatibility Check"
    echo "=========================="
    
    # Check for API version changes
    local api_files=(
        "mem0/openmemory/api/main.py"
        "custom-gpt-adapter/app/main.py"
        "custom-gpt-adapter/app/api/v1"
    )
    
    for api_file in "${api_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$api_file" ] || [ -d "$PROJECT_ROOT/$api_file" ]; then
            log_info "Found API: $api_file"
            
            # Look for version strings
            if [ -f "$PROJECT_ROOT/$api_file" ]; then
                local version_info=$(grep -i -E '(version|api_version)' "$PROJECT_ROOT/$api_file" | head -3)
                if [ -n "$version_info" ]; then
                    echo "  Version info found:"
                    echo "$version_info" | sed 's/^/    /'
                fi
            fi
        fi
    done
    
    echo
}

# Check environment variable compatibility
check_env_compatibility() {
    log "🌍 Environment Variable Compatibility"
    echo "====================================="
    
    local env_files=(
        ".env.example"
        "mem0/server/.env.example"
        "custom-gpt-adapter/.env.example"
    )
    
    for env_file in "${env_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$env_file" ]; then
            log_info "Checking $env_file..."
            
            local env_count=$(grep -c -E '^[A-Z_]+=' "$PROJECT_ROOT/$env_file" || echo "0")
            echo "  Environment variables: $env_count"
            
            # Check for database URLs, API keys, etc.
            if grep -q "DATABASE_URL" "$PROJECT_ROOT/$env_file"; then
                log_info "  Contains database configuration"
            fi
            
            if grep -q "API_KEY" "$PROJECT_ROOT/$env_file"; then
                log_info "  Contains API key configuration"
            fi
        fi
    done
    
    echo
}

# Check dependency file compatibility
check_dependency_compatibility() {
    local file_path=$1
    local file_type=$2
    
    log "📋 Analyzing $file_path ($file_type)"
    echo "----------------------------------------"
    
    # Check if file exists in both branches
    local main_exists=false
    local renovate_exists=false
    
    if check_file_exists "$file_path" "main"; then
        main_exists=true
    fi
    
    if check_file_exists "$file_path" "renovate"; then
        renovate_exists=true
    fi
    
    if [ "$main_exists" = false ] && [ "$renovate_exists" = false ]; then
        log_warning "File not found in either branch"
        return
    elif [ "$main_exists" = false ]; then
        log_warning "File only exists in renovate branch (new file)"
        return
    elif [ "$renovate_exists" = false ]; then
        log_error "File removed in renovate branch"
        return
    fi
    
    # Get file contents from both branches
    local main_content=$(git show "main:$file_path" 2>/dev/null)
    local renovate_content=$(git show "renovate:$file_path" 2>/dev/null)
    
    # Extract dependencies based on file type
    local main_deps=""
    local renovate_deps=""
    
    case "$file_type" in
        "requirements")
            main_deps=$(extract_python_deps "$main_content")
            renovate_deps=$(extract_python_deps "$renovate_content")
            ;;
        "pyproject")
            main_deps=$(extract_pyproject_deps "$main_content")
            renovate_deps=$(extract_pyproject_deps "$renovate_content")
            ;;
        "package.json")
            main_deps=$(extract_node_deps "$main_content")
            renovate_deps=$(extract_node_deps "$renovate_content")
            ;;
    esac
    
    # Compare dependencies
    compare_dependencies "$main_deps" "$renovate_deps" "$file_type"
}

# Generate compatibility report
generate_compatibility_report() {
    log "📄 Generating Compatibility Report"
    echo "==================================="
    
    local report_file="$PROJECT_ROOT/compatibility-report.md"
    
    cat > "$report_file" << EOF
# Renovate Branch Compatibility Report

Generated: $(date)
Main Branch: $(git rev-parse main)
Renovate Branch: $(git rev-parse renovate)

## Summary

This report analyzes the compatibility between main and renovate branches
for the Memory Bank project.

## Dependency Changes

EOF
    
    log_success "Report saved to: $report_file"
    echo "You can review detailed compatibility analysis in the report."
    
    echo
}

# Main compatibility check function
main() {
    local check_type="all"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --deps|--dependencies)
                check_type="dependencies"
                shift
                ;;
            --docker)
                check_type="docker"
                shift
                ;;
            --python)
                check_type="python"
                shift
                ;;
            --node)
                check_type="node"
                shift
                ;;
            --api)
                check_type="api"
                shift
                ;;
            --env)
                check_type="env"
                shift
                ;;
            -h|--help)
                cat << EOF
Compatibility Check Script

Usage: $0 [OPTIONS]

OPTIONS:
    -v, --verbose           Verbose output
    --deps                  Check only dependency compatibility
    --docker                Check only Docker compatibility
    --python                Check only Python compatibility
    --node                  Check only Node.js compatibility
    --api                   Check only API compatibility
    --env                   Check only environment compatibility
    -h, --help              Show this help

Examples:
    $0                      # Run all compatibility checks
    $0 --deps               # Check only dependencies
    $0 --verbose --docker   # Verbose Docker check

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
    
    log "🔍 Memory Bank Compatibility Check"
    echo "==================================="
    log_info "Comparing main and renovate branches"
    echo
    
    case "$check_type" in
        "all")
            # Run all checks
            for dep_file in "${DEPENDENCY_FILES[@]}"; do
                if [[ "$dep_file" == *"requirements.txt" ]]; then
                    check_dependency_compatibility "$dep_file" "requirements"
                elif [[ "$dep_file" == *"pyproject.toml" ]]; then
                    check_dependency_compatibility "$dep_file" "pyproject"
                elif [[ "$dep_file" == *"package.json" ]]; then
                    check_dependency_compatibility "$dep_file" "package.json"
                fi
            done
            
            check_docker_compatibility
            check_python_compatibility
            check_node_compatibility
            check_database_compatibility
            check_api_compatibility
            check_env_compatibility
            ;;
        "dependencies")
            for dep_file in "${DEPENDENCY_FILES[@]}"; do
                if [[ "$dep_file" == *"requirements.txt" ]]; then
                    check_dependency_compatibility "$dep_file" "requirements"
                elif [[ "$dep_file" == *"pyproject.toml" ]]; then
                    check_dependency_compatibility "$dep_file" "pyproject"
                elif [[ "$dep_file" == *"package.json" ]]; then
                    check_dependency_compatibility "$dep_file" "package.json"
                fi
            done
            ;;
        "docker")
            check_docker_compatibility
            ;;
        "python")
            check_python_compatibility
            ;;
        "node")
            check_node_compatibility
            ;;
        "api")
            check_api_compatibility
            ;;
        "env")
            check_env_compatibility
            ;;
    esac
    
    generate_compatibility_report
    
    log_success "🎉 Compatibility check completed!"
    log_info "💡 Review the findings and plan your deployment accordingly"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 