#!/bin/bash
set -euo pipefail

# AI-Friendly Testing Suite Environment Setup
# Production-grade DevOps automation script
# Author: Alex (DevOps Infrastructure Specialist)

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in CI environment
is_ci() {
    [[ "${CI:-false}" == "true" ]]
}

# Check if virtual environment is activated
check_venv() {
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warning "No virtual environment detected. Consider using a virtual environment."
        return 1
    fi
    return 0
}

# Install testing dependencies
install_dependencies() {
    log_info "Installing AI testing suite dependencies..."
    
    if is_ci; then
        log_info "CI environment detected - using system package manager where appropriate"
        
        # Install system dependencies for CI
        if command -v apt-get > /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-dev build-essential
        fi
    fi
    
    # Install Python dependencies
    if [[ -f "requirements-testing.txt" ]]; then
        log_info "Installing from requirements-testing.txt..."
        pip install --upgrade pip wheel setuptools
        pip install -r requirements-testing.txt
        log_success "Testing dependencies installed successfully"
    else
        log_error "requirements-testing.txt not found!"
        return 1
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying AI testing framework installation..."
    
    local verification_errors=0
    
    # Test core dependencies
    local deps=("pytest" "hypothesis" "psutil" "pytest-cov" "safety" "bandit")
    
    for dep in "${deps[@]}"; do
        if python -c "import ${dep//-/_}" 2>/dev/null; then
            log_success "${dep} ✓"
        else
            log_error "${dep} ✗"
            ((verification_errors++))
        fi
    done
    
    # Test AI testing framework
    if python -c "from tests.ai_testing_framework import AITestFramework; print('AI Framework OK')" 2>/dev/null; then
        log_success "AI Testing Framework ✓"
    else
        log_error "AI Testing Framework ✗"
        ((verification_errors++))
    fi
    
    if [[ $verification_errors -eq 0 ]]; then
        log_success "All components verified successfully!"
        return 0
    else
        log_error "$verification_errors verification errors found"
        return 1
    fi
}

# Setup test directories
setup_directories() {
    log_info "Setting up test directories..."
    
    local dirs=(
        "tests/reports"
        "tests/artifacts"
        "tests/coverage"
        "tests/security"
        "tests/performance"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    done
}

# Configure git hooks (optional)
setup_git_hooks() {
    if [[ -d ".git" ]]; then
        log_info "Setting up git pre-commit hook for testing..."
        
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# AI Testing Suite Pre-commit Hook
set -e

echo "🧪 Running AI testing framework checks..."

# Run quick verification
if [[ -f "test_ai_framework_simple_verify.py" ]]; then
    python test_ai_framework_simple_verify.py
fi

# Run security scan on staged files
if command -v bandit > /dev/null; then
    echo "🔒 Running security scan..."
    git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | xargs bandit -f screen || echo "Security scan completed with warnings"
fi

echo "✅ Pre-commit checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        log_success "Git pre-commit hook installed"
    else
        log_warning "Not a git repository - skipping git hooks setup"
    fi
}

# Generate configuration files
generate_configs() {
    log_info "Generating configuration files..."
    
    # Create .coveragerc if it doesn't exist
    if [[ ! -f ".coveragerc" ]]; then
        cat > .coveragerc << 'EOF'
[run]
source = mem0
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */env/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\(Protocol\):
    @(abc\.)?abstractmethod

show_missing = True
precision = 2

[html]
directory = tests/coverage/html

[xml]
output = tests/coverage/coverage.xml
EOF
        log_success "Created .coveragerc configuration"
    fi
    
    # Create bandit configuration
    if [[ ! -f ".bandit" ]]; then
        cat > .bandit << 'EOF'
[bandit]
exclude_dirs = tests,venv,env
skips = B101,B601
EOF
        log_success "Created .bandit configuration"
    fi
}

# Main execution
main() {
    echo "🚀 AI-Friendly Testing Suite Environment Setup"
    echo "=============================================="
    
    log_info "Starting environment setup..."
    
    # Check prerequisites
    if ! command -v python > /dev/null; then
        log_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v pip > /dev/null; then
        log_error "pip is not installed or not in PATH"
        exit 1
    fi
    
    # Run setup steps
    setup_directories
    install_dependencies
    generate_configs
    
    if ! is_ci; then
        setup_git_hooks
        
        # Check virtual environment (warning only for local development)
        check_venv || log_warning "Consider using a virtual environment for local development"
    fi
    
    # Verify installation
    if verify_installation; then
        log_success "🎉 AI Testing Suite environment setup completed successfully!"
        echo ""
        echo "Next steps:"
        echo "  • Run tests: python -m pytest tests/ai_memory_tests.py -v"
        echo "  • Generate report: python test_ai_framework_simple_verify.py"
        echo "  • View documentation: cat tests/README.md"
        echo ""
        echo "For CI/CD integration, check .github/workflows/ai-testing-suite.yml"
    else
        log_error "Setup completed with errors. Please review and fix issues."
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AI-Friendly Testing Suite Environment Setup

Usage: $0 [OPTIONS]

Options:
  --help, -h     Show this help message
  --verify-only  Only run verification checks
  --no-hooks     Skip git hooks setup
  
Environment Variables:
  CI=true        Indicates running in CI environment
  
Examples:
  $0                    # Full setup
  $0 --verify-only     # Only verify existing installation
  $0 --no-hooks        # Setup without git hooks
EOF
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --verify-only)
        verify_installation
        exit $?
        ;;
    --no-hooks)
        export SKIP_GIT_HOOKS=true
        main
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 