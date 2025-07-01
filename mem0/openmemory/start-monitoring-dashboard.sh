#!/bin/bash

# Memory-C* Enhanced Monitoring Dashboard Startup Script
# This script starts both the monitoring API server and the React development server

set -e

echo "🚀 Starting Memory-C* Enhanced Monitoring Dashboard"
printf '=%.0s' {1..60}; echo

# Colors for output
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "monitoring-api-server.py" ]; then
    print_error "monitoring-api-server.py not found. Please run this script from the mem0/openmemory directory"
    exit 1
fi

# Check Python dependencies
print_status "Checking Python dependencies..."
python3 -c "import fastapi, uvicorn, sqlite3, psutil, requests" 2>/dev/null || {
    print_error "Missing Python dependencies. Installing..."
    pip3 install fastapi uvicorn psutil requests || {
        print_error "Failed to install Python dependencies"
        exit 1
    }
}

# Check if React UI directory exists
if [ ! -d "ui" ]; then
    print_error "UI directory not found. Please ensure you're in the correct directory"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    print_warning "Shutting down monitoring dashboard..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        print_status "Stopped monitoring API server (PID: $API_PID)"
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null || true
        print_status "Stopped React development server (PID: $UI_PID)"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the monitoring API server
print_status "Starting monitoring API server on port 8766..."
python3 monitoring-api-server.py > monitoring-api.log 2>&1 &
API_PID=$!

# Wait a moment for the API server to start
sleep 2

# Check if API server is running
if ! kill -0 $API_PID 2>/dev/null; then
    print_error "Failed to start monitoring API server"
    cat monitoring-api.log
    exit 1
fi

print_success "Monitoring API server started (PID: $API_PID)"

# Test API connectivity
print_status "Testing API connectivity..."
for i in {1..5}; do
    if curl -s http://localhost:8766/api/v1/monitoring/current > /dev/null; then
        print_success "API server is responding"
        break
    fi
    if [ $i -eq 5 ]; then
        print_error "API server not responding after 5 attempts"
        cleanup
        exit 1
    fi
    print_status "Waiting for API server... (attempt $i/5)"
    sleep 2
done

# Start the React development server
print_status "Starting React development server..."
cd ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    pnpm install || npm install || {
        print_error "Failed to install Node.js dependencies"
        cleanup
        exit 1
    }
fi

# Start the development server
pnpm dev > ../react-dev.log 2>&1 &
UI_PID=$!

# Wait a moment for the React server to start
sleep 3

# Check if React server is running
if ! kill -0 $UI_PID 2>/dev/null; then
    print_error "Failed to start React development server"
    cat ../react-dev.log
    cleanup
    exit 1
fi

print_success "React development server started (PID: $UI_PID)"

# Display status and URLs
echo ""
echo "🎉 Enhanced Monitoring Dashboard is now running!"
printf '=%.0s' {1..60}; echo
echo "📊 Monitoring API:     http://localhost:8766"
echo "📱 Dashboard UI:       http://localhost:3010"  
echo "📋 API Documentation:  http://localhost:8766/docs"
printf '=%.0s' {1..60}; echo
echo ""
print_status "Real-time monitoring features:"
echo "  ✅ System Health (CPU, Memory, Disk)"
echo "  ✅ Database Metrics (Memory count, Growth trends)" 
echo "  ✅ API Performance (Response times)"
echo "  ✅ Alerts & Notifications"
echo "  ✅ Historical Data & Charts"
echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Keep the script running and monitor the processes
while true; do
    # Check if API server is still running
    if ! kill -0 $API_PID 2>/dev/null; then
        print_error "Monitoring API server has stopped"
        cleanup
        exit 1
    fi
    
    # Check if React server is still running
    if ! kill -0 $UI_PID 2>/dev/null; then
        print_error "React development server has stopped"
        cleanup
        exit 1
    fi
    
    sleep 5
done 