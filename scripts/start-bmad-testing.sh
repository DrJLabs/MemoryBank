#!/bin/bash
# BMAD Testing Container Management Script
# Provides easy management of containerized BMAD testing environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.bmad.yml"
REPORT_PORT=8090
REPORTS_DIR="reports/bmad"

# Print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check dependencies
check_dependencies() {
    print_color "$BLUE" "🔍 Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_color "$RED" "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_color "$RED" "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_color "$GREEN" "✅ All dependencies satisfied"
}

# Create necessary directories
setup_directories() {
    print_color "$BLUE" "📁 Setting up directories..."
    
    mkdir -p $REPORTS_DIR/{phase1,phase2,coverage,memory}
    mkdir -p quality/monitoring
    mkdir -p logs/bmad
    
    print_color "$GREEN" "✅ Directories created"
}

# Build containers
build_containers() {
    print_color "$BLUE" "🏗️ Building BMAD test containers..."
    
    docker compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    print_color "$GREEN" "✅ Containers built successfully"
}

# Run all tests
run_all_tests() {
    print_color "$YELLOW" "🧪 Running all BMAD tests..."
    
    # Run main test suite
    docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-tests
    
    # Run Phase 1
    print_color "$BLUE" "📊 Phase 1: Foundation Tests"
    docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase1
    
    # Run Phase 2
    print_color "$BLUE" "🧬 Phase 2: Advanced Tests"
    docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase2
    
    # Run Quality Gates
    print_color "$BLUE" "🎯 Running Quality Gates"
    docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-quality-gates
    
    # Run Phase 4
    print_color "$BLUE" "📈 Phase 4: Monitoring & Optimization"
    docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase4
}

# Run specific phase
run_phase() {
    local phase=$1
    print_color "$YELLOW" "🧪 Running Phase $phase tests..."
    
    case $phase in
        1)
            docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase1
            ;;
        2)
            docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase2
            ;;
        4)
            docker compose -f $DOCKER_COMPOSE_FILE run --rm bmad-phase4
            ;;
        *)
            print_color "$RED" "❌ Invalid phase: $phase"
            exit 1
            ;;
    esac
}

# Start report server
start_report_server() {
    print_color "$BLUE" "🌐 Starting test report server..."
    
    docker compose -f $DOCKER_COMPOSE_FILE up -d bmad-reports
    
    print_color "$GREEN" "✅ Report server started at http://localhost:$REPORT_PORT"
    print_color "$YELLOW" "📋 Access test reports at:"
    echo "   - Coverage: http://localhost:$REPORT_PORT/coverage"
    echo "   - Phase 1: http://localhost:$REPORT_PORT/phase1"
    echo "   - Phase 2: http://localhost:$REPORT_PORT/phase2"
}

# Stop all services
stop_services() {
    print_color "$BLUE" "🛑 Stopping BMAD test services..."
    
    docker compose -f $DOCKER_COMPOSE_FILE down
    
    print_color "$GREEN" "✅ All services stopped"
}

# Clean up containers and volumes
cleanup() {
    print_color "$YELLOW" "🧹 Cleaning up BMAD test environment..."
    
    docker compose -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
    
    # Remove test reports (optional)
    read -p "Remove test reports? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf $REPORTS_DIR/*
        print_color "$GREEN" "✅ Test reports removed"
    fi
    
    print_color "$GREEN" "✅ Cleanup complete"
}

# Show status
show_status() {
    print_color "$BLUE" "📊 BMAD Testing Environment Status"
    echo "=================================="
    
    # Check if containers are running
    if docker compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        print_color "$GREEN" "✅ Services are running:"
        docker compose -f $DOCKER_COMPOSE_FILE ps
    else
        print_color "$YELLOW" "⚠️ No services are currently running"
    fi
    
    # Check for test reports
    if [ -d "$REPORTS_DIR" ] && [ "$(ls -A $REPORTS_DIR)" ]; then
        print_color "$GREEN" "📋 Test reports available:"
        find $REPORTS_DIR -name "*.html" -type f | head -10
    else
        print_color "$YELLOW" "📋 No test reports found"
    fi
}

# Interactive mode
interactive_mode() {
    print_color "$BLUE" "🎯 BMAD Testing Container Manager"
    echo "=================================="
    echo "1) Run all tests"
    echo "2) Run Phase 1 tests"
    echo "3) Run Phase 2 tests"
    echo "4) Run Phase 4 tests"
    echo "5) Start report server"
    echo "6) Show status"
    echo "7) Stop services"
    echo "8) Clean up"
    echo "9) Exit"
    echo
    read -p "Select an option: " choice
    
    case $choice in
        1) run_all_tests ;;
        2) run_phase 1 ;;
        3) run_phase 2 ;;
        4) run_phase 4 ;;
        5) start_report_server ;;
        6) show_status ;;
        7) stop_services ;;
        8) cleanup ;;
        9) exit 0 ;;
        *) print_color "$RED" "Invalid option" ;;
    esac
}

# Main script logic
main() {
    check_dependencies
    setup_directories
    
    case "${1:-}" in
        "build")
            build_containers
            ;;
        "test")
            run_all_tests
            ;;
        "phase")
            run_phase "${2:-1}"
            ;;
        "reports")
            start_report_server
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            cleanup
            ;;
        "status")
            show_status
            ;;
        "interactive"|"-i")
            while true; do
                interactive_mode
                echo
                read -p "Press Enter to continue..."
            done
            ;;
        *)
            print_color "$BLUE" "🚀 BMAD Testing Container Manager"
            echo "Usage: $0 [command] [options]"
            echo
            echo "Commands:"
            echo "  build       - Build test containers"
            echo "  test        - Run all tests"
            echo "  phase [N]   - Run specific phase (1, 2, or 4)"
            echo "  reports     - Start report server"
            echo "  stop        - Stop all services"
            echo "  clean       - Clean up environment"
            echo "  status      - Show current status"
            echo "  interactive - Interactive mode"
            echo
            echo "Examples:"
            echo "  $0 build           # Build containers"
            echo "  $0 test            # Run all tests"
            echo "  $0 phase 1         # Run Phase 1 tests"
            echo "  $0 phase 4         # Run Phase 4 monitoring"
            echo "  $0 reports         # Start report server"
            echo "  $0 interactive     # Interactive mode"
            ;;
    esac
}

# Run main function
main "$@" 