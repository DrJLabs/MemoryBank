#!/bin/bash

# BMAD Tracking API Management Script
# Provides start, stop, restart, and status commands

set -e

# Configuration
API_DIR="$(dirname "$0")"
API_SCRIPT="bmad-tracking-api.py"
PID_FILE="/tmp/bmad-tracking-api.pid"
LOG_FILE="$API_DIR/bmad-api.log"
PORT=8767

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

start_api() {
    if check_running; then
        print_warning "BMAD API is already running (PID: $(cat $PID_FILE))"
        return 0
    fi

    print_status "Starting BMAD Tracking API..."
    
    cd "$API_DIR"
    
    # Check dependencies
    python3 -c "import fastapi, uvicorn, yaml, pydantic" 2>/dev/null || {
        print_error "Missing dependencies. Install with: pip install fastapi uvicorn pyyaml pydantic"
        exit 1
    }

    # Start the API
    nohup python3 "$API_SCRIPT" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    # Wait and check if it started successfully
    sleep 2
    if check_running; then
        print_success "BMAD API started successfully (PID: $PID)"
        
        # Test the API
        for i in {1..5}; do
            if curl -s "http://localhost:$PORT/api/v1/bmad/health" > /dev/null; then
                print_success "API is responding at http://localhost:$PORT"
                break
            fi
            sleep 1
        done
    else
        print_error "Failed to start BMAD API"
        return 1
    fi
}

stop_api() {
    if ! check_running; then
        print_warning "BMAD API is not running"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    print_status "Stopping BMAD API (PID: $PID)..."
    
    kill "$PID"
    rm -f "$PID_FILE"
    
    print_success "BMAD API stopped"
}

restart_api() {
    print_status "Restarting BMAD API..."
    stop_api
    sleep 1
    start_api
}

status_api() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_success "BMAD API is running (PID: $PID)"
        
        # Check API health
        if curl -s "http://localhost:$PORT/api/v1/bmad/health" > /dev/null; then
            print_success "API is healthy and responding"
        else
            print_warning "API process is running but not responding"
        fi
        
        # Show recent logs
        echo -e "\n${BLUE}Recent logs:${NC}"
        tail -n 10 "$LOG_FILE"
    else
        print_error "BMAD API is not running"
        return 1
    fi
}

logs_api() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        print_error "No log file found"
    fi
}

# Main script
case "$1" in
    start)
        start_api
        ;;
    stop)
        stop_api
        ;;
    restart)
        restart_api
        ;;
    status)
        status_api
        ;;
    logs)
        logs_api
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the BMAD tracking API"
        echo "  stop     - Stop the BMAD tracking API"
        echo "  restart  - Restart the BMAD tracking API"
        echo "  status   - Check if the API is running"
        echo "  logs     - Follow the API logs"
        exit 1
        ;;
esac

exit 0 