#!/bin/bash
# Memory-C* Development Environment Manager
# Ensures all commands execute in the correct directories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UI_DIR="${PROJECT_ROOT}/mem0/openmemory/ui"
API_DIR="${PROJECT_ROOT}/mem0/openmemory/api"
OPENMEMORY_DIR="${PROJECT_ROOT}/mem0/openmemory"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_command() {
    echo -e "${CYAN}[EXEC]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use. Attempting to free it..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to run command in specific directory
run_in_dir() {
    local dir=$1
    shift
    local cmd="$@"
    
    print_command "cd $dir && $cmd"
    (cd "$dir" && eval "$cmd")
}

# Function to start UI server
start_ui() {
    print_status "Starting UI Development Server..."
    
    # Check if UI directory exists
    if [ ! -d "$UI_DIR" ]; then
        print_error "UI directory not found: $UI_DIR"
        return 1
    fi
    
    # Kill existing process on port 3010
    kill_port 3010
    
    # Install dependencies if needed
    if [ ! -d "$UI_DIR/node_modules" ]; then
        print_status "Installing UI dependencies..."
        run_in_dir "$UI_DIR" "pnpm install"
    fi
    
    # Start the UI server
    print_success "Starting UI server on port 3010..."
    run_in_dir "$UI_DIR" "pnpm dev --port 3010" &
    UI_PID=$!
    
    print_success "UI server started (PID: $UI_PID)"
    echo -e "${GREEN}➜${NC} UI Dashboard: http://localhost:3010"
}

# Function to start API server
start_api() {
    print_status "Starting API Server..."
    
    # Check if API directory exists
    if [ ! -d "$API_DIR" ]; then
        print_error "API directory not found: $API_DIR"
        return 1
    fi
    
    # Kill existing process on port 8765
    kill_port 8765
    
    # Check Python dependencies
    print_status "Checking API dependencies..."
    run_in_dir "$API_DIR" "pip install -r requirements.txt --quiet" || true
    
    # Start the API server
    print_success "Starting API server on port 8765..."
    run_in_dir "$API_DIR" "uvicorn main:app --host 0.0.0.0 --port 8765 --reload" &
    API_PID=$!
    
    print_success "API server started (PID: $API_PID)"
    echo -e "${GREEN}➜${NC} API Server: http://localhost:8765"
    echo -e "${GREEN}➜${NC} API Docs: http://localhost:8765/docs"
}

# Function to start all services
start_all() {
    print_status "Starting all Memory-C* services..."
    
    # Start Vector DB
    if ! check_port 6333; then
        print_status "Starting Qdrant Vector DB..."
        docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest || true
    fi
    
    start_api
    sleep 2
    start_ui
    
    print_success "All services started!"
    show_status
}

# Function to stop all services
stop_all() {
    print_status "Stopping all services..."
    
    # Stop UI server
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null || true
    fi
    kill_port 3010
    
    # Stop API server
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    kill_port 8765
    
    print_success "All services stopped"
}

# Function to show status
show_status() {
    echo ""
    echo "🎯 Memory-C* Service Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if check_port 3010; then
        echo -e "UI Server:     ${GREEN}● Running${NC} (http://localhost:3010)"
    else
        echo -e "UI Server:     ${RED}○ Stopped${NC}"
    fi
    
    if check_port 8765; then
        echo -e "API Server:    ${GREEN}● Running${NC} (http://localhost:8765)"
    else
        echo -e "API Server:    ${RED}○ Stopped${NC}"
    fi
    
    if check_port 6333; then
        echo -e "Vector DB:     ${GREEN}● Running${NC} (http://localhost:6333)"
    else
        echo -e "Vector DB:     ${RED}○ Stopped${NC}"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to run specific npm/pnpm commands in UI directory
ui_cmd() {
    local cmd="$@"
    print_status "Running UI command: $cmd"
    run_in_dir "$UI_DIR" "$cmd"
}

# Function to run specific commands in API directory
api_cmd() {
    local cmd="$@"
    print_status "Running API command: $cmd"
    run_in_dir "$API_DIR" "$cmd"
}

# Main menu
show_menu() {
    echo ""
    echo "🧠 Memory-C* Development Environment Manager"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1) Start UI Server (port 3010)"
    echo "2) Start API Server (port 8765)"
    echo "3) Start All Services"
    echo "4) Stop All Services"
    echo "5) Show Status"
    echo "6) Install UI Dependencies"
    echo "7) Build UI for Production"
    echo "8) Run UI Command"
    echo "9) Run API Command"
    echo "0) Exit"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Handle Ctrl+C
trap 'stop_all; exit 0' INT TERM

# Parse command line arguments
case "$1" in
    start-ui)
        start_ui
        ;;
    start-api)
        start_api
        ;;
    start|start-all)
        start_all
        ;;
    stop|stop-all)
        stop_all
        ;;
    status)
        show_status
        ;;
    ui)
        shift
        ui_cmd "$@"
        ;;
    api)
        shift
        api_cmd "$@"
        ;;
    *)
        # Interactive mode
        while true; do
            show_menu
            read -p "Select option: " choice
            
            case $choice in
                1) start_ui ;;
                2) start_api ;;
                3) start_all ;;
                4) stop_all ;;
                5) show_status ;;
                6) ui_cmd "pnpm install" ;;
                7) ui_cmd "pnpm build" ;;
                8) 
                    read -p "Enter UI command: " cmd
                    ui_cmd "$cmd"
                    ;;
                9)
                    read -p "Enter API command: " cmd
                    api_cmd "$cmd"
                    ;;
                0) exit 0 ;;
                *) print_error "Invalid option" ;;
            esac
            
            read -p "Press Enter to continue..."
        done
        ;;
esac 