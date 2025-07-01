#!/bin/bash

# BMAD Tracking API Startup Script
# This script starts the BMAD tracking API server

set -e

echo "🎯 Starting BMAD Tracking API"
printf '=%.0s' {1..60}; echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -f "bmad-tracking-api.py" ]; then
    print_warning "bmad-tracking-api.py not found. Please run this script from the mem0/openmemory directory"
    exit 1
fi

# Check Python dependencies
print_status "Checking Python dependencies..."
python3 -c "import fastapi, uvicorn, yaml, pydantic" 2>/dev/null || {
    print_warning "Missing Python dependencies. Installing..."
    pip3 install --user pyyaml || sudo apt install -y python3-yaml
}

# Start the BMAD tracking API server
print_status "Starting BMAD tracking API server on port 8767..."
python3 bmad-tracking-api.py &
API_PID=$!

# Wait a moment for the API server to start
sleep 2

# Check if API server is running
if ! kill -0 $API_PID 2>/dev/null; then
    print_error "Failed to start BMAD tracking API server"
    exit 1
fi

print_success "BMAD tracking API server started (PID: $API_PID)"

# Test API connectivity
print_status "Testing API connectivity..."
for i in {1..5}; do
    if curl -s http://localhost:8767/api/v1/bmad/health > /dev/null; then
        print_success "API server is responding"
        break
    fi
    if [ $i -eq 5 ]; then
        print_warning "API server not responding after 5 attempts"
    fi
    print_status "Waiting for API server... (attempt $i/5)"
    sleep 2
done

# Display status
echo ""
echo "🎯 BMAD Tracking API is now running!"
printf '=%.0s' {1..60}; echo
echo "📊 API Endpoints:"
echo "  - Health: http://localhost:8767/api/v1/bmad/health"
echo "  - Stories: http://localhost:8767/api/v1/bmad/stories"
echo "  - Epics: http://localhost:8767/api/v1/bmad/epics"
echo "  - Tasks: http://localhost:8767/api/v1/bmad/tasks/active"
echo "  - Summary: http://localhost:8767/api/v1/bmad/summary"
printf '=%.0s' {1..60}; echo
echo ""
print_warning "Keep this terminal open or the API will stop"
echo ""

# Keep the script running
wait $API_PID 