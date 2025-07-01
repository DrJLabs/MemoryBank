#!/bin/bash
# 🔐 Infisical Monitoring Dashboard Startup Script
# Architecture: Memory-C* Infisical Integration Architecture v1.0
# Pattern: Production-Ready Monitoring Dashboard with Auto-healing

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITOR_SCRIPT="$SCRIPT_DIR/infisical-monitoring.py"
DASHBOARD_PORT=8080
REFRESH_INTERVAL=30
LOG_FILE="logs/monitoring-dashboard.log"
PID_FILE="logs/monitoring-dashboard.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$1] $2" | tee -a "$LOG_FILE"
}

print_banner() {
    echo -e "${BLUE}"
    echo "🔐 Memory-C* Infisical Monitoring Dashboard"
    echo "Architecture: Enterprise-Grade Secret Management Monitoring"
    printf '=%.0s' {1..60}; echo
    echo -e "${NC}"
}

check_dependencies() {
    log "INFO" "🔍 Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "❌ Python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check required Python packages
    python3 -c "import requests, psutil" 2>/dev/null || {
        log "INFO" "📦 Installing required Python packages..."
        pip3 install --user requests psutil || {
            log "ERROR" "❌ Failed to install Python dependencies"
            exit 1
        }
    }
    
    # Check Infisical CLI
    if ! command -v infisical &> /dev/null; then
        log "WARNING" "⚠️ Infisical CLI not found. Dashboard will show connection errors."
    else
        log "INFO" "✅ Infisical CLI available: $(infisical --version)"
    fi
    
    # Check memory system integration
    if command -v ai-add-smart &> /dev/null; then
        log "INFO" "✅ AI Memory system integration available"
    else
        log "WARNING" "⚠️ AI Memory system not available (optional)"
    fi
}

setup_directories() {
    log "INFO" "📁 Setting up monitoring directories..."
    mkdir -p logs monitoring/dashboards monitoring/alerts reports
    touch "$LOG_FILE"
}

check_existing_process() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "WARNING" "⚠️ Monitoring process already running (PID: $pid)"
            echo -e "${YELLOW}Options:${NC}"
            echo "  1. Stop existing process and restart"
            echo "  2. View existing dashboard"
            echo "  3. Cancel"
            read -p "Choose option (1-3): " choice
            
            case $choice in
                1)
                    log "INFO" "🛑 Stopping existing process..."
                    kill "$pid" 2>/dev/null || true
                    sleep 2
                    rm -f "$PID_FILE"
                    ;;
                2)
                    show_dashboard_info
                    exit 0
                    ;;
                3)
                    log "INFO" "❌ Operation cancelled"
                    exit 0
                    ;;
                *)
                    log "ERROR" "❌ Invalid option"
                    exit 1
                    ;;
            esac
        else
            # Stale PID file
            rm -f "$PID_FILE"
        fi
    fi
}

start_monitoring() {
    log "INFO" "🚀 Starting Infisical monitoring system..."
    
    # Make monitor script executable
    chmod +x "$MONITOR_SCRIPT"
    
    # Start monitoring in background
    python3 "$MONITOR_SCRIPT" > "$LOG_FILE" 2>&1 &
    local monitor_pid=$!
    echo "$monitor_pid" > "$PID_FILE"
    
    # Wait for initial metrics collection
    log "INFO" "⏳ Collecting initial metrics..."
    sleep 5
    
    # Verify monitoring is working
    if ! kill -0 "$monitor_pid" 2>/dev/null; then
        log "ERROR" "❌ Failed to start monitoring process"
        rm -f "$PID_FILE"
        exit 1
    fi
    
    log "INFO" "✅ Monitoring process started (PID: $monitor_pid)"
}

start_dashboard_server() {
    log "INFO" "🌐 Starting dashboard web server..."
    
    # Simple Python HTTP server for dashboard
    cd monitoring/dashboards
    
    # Create server script
    cat > dashboard_server.py << 'EOF'
import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/infisical-dashboard.html'
        
        # Add auto-refresh header
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            try:
                with open(self.path[1:], 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "Dashboard not ready yet")
        else:
            super().do_GET()

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
    print(f"Dashboard server running on port {PORT}")
    httpd.serve_forever()
EOF

    # Start dashboard server in background
    python3 dashboard_server.py "$DASHBOARD_PORT" > ../../logs/dashboard-server.log 2>&1 &
    local server_pid=$!
    echo "$server_pid" > ../../logs/dashboard-server.pid
    
    # Return to project root
    cd "$PROJECT_ROOT"
    
    # Wait for server to start
    sleep 2
    
    # Verify server is running
    if ! kill -0 "$server_pid" 2>/dev/null; then
        log "ERROR" "❌ Failed to start dashboard server"
        exit 1
    fi
    
    log "INFO" "✅ Dashboard server started (PID: $server_pid)"
}

setup_continuous_monitoring() {
    log "INFO" "🔄 Setting up continuous monitoring..."
    
    # Create monitoring loop script
    cat > scripts/monitoring-loop.sh << 'EOF'
#!/bin/bash
# Continuous monitoring loop

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/infisical-monitoring.py"

while true; do
    python3 "$MONITOR_SCRIPT" || echo "Monitoring cycle failed"
    sleep 30
done
EOF

    chmod +x scripts/monitoring-loop.sh
    
    # Start continuous monitoring
    nohup bash scripts/monitoring-loop.sh > logs/continuous-monitoring.log 2>&1 &
    local loop_pid=$!
    echo "$loop_pid" > logs/monitoring-loop.pid
    
    log "INFO" "✅ Continuous monitoring loop started (PID: $loop_pid)"
}

show_dashboard_info() {
    local dashboard_url="http://localhost:$DASHBOARD_PORT"
    
    echo -e "${GREEN}"
    echo "🎉 Infisical Monitoring Dashboard is LIVE!"
    printf '=%.0s' {1..50}; echo
    echo -e "${NC}"
    echo "📊 Dashboard URL: $dashboard_url"
    echo "📁 Dashboard File: $(pwd)/monitoring/dashboards/infisical-dashboard.html"
    echo "📋 JSON Data: $(pwd)/monitoring/dashboards/infisical-dashboard.json"
    echo "📝 Logs: $(pwd)/$LOG_FILE"
    echo
    echo -e "${BLUE}Management Commands:${NC}"
    echo "  View Status: bash $0 status"
    echo "  Stop All: bash $0 stop"
    echo "  Restart: bash $0 restart"
    echo "  View Logs: tail -f $LOG_FILE"
    echo
    
    # Try to open in browser
    if command -v xdg-open &> /dev/null; then
        read -p "Open dashboard in browser? (y/N): " open_browser
        if [[ "$open_browser" =~ ^[Yy]$ ]]; then
            xdg-open "$dashboard_url" 2>/dev/null &
        fi
    fi
}

stop_monitoring() {
    log "INFO" "🛑 Stopping monitoring services..."
    
    # Stop monitoring process
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log "INFO" "✅ Stopped monitoring process (PID: $pid)"
        fi
        rm -f "$PID_FILE"
    fi
    
    # Stop dashboard server
    if [[ -f "logs/dashboard-server.pid" ]]; then
        local server_pid=$(cat "logs/dashboard-server.pid")
        if kill -0 "$server_pid" 2>/dev/null; then
            kill "$server_pid"
            log "INFO" "✅ Stopped dashboard server (PID: $server_pid)"
        fi
        rm -f "logs/dashboard-server.pid"
    fi
    
    # Stop monitoring loop
    if [[ -f "logs/monitoring-loop.pid" ]]; then
        local loop_pid=$(cat "logs/monitoring-loop.pid")
        if kill -0 "$loop_pid" 2>/dev/null; then
            kill "$loop_pid"
            log "INFO" "✅ Stopped monitoring loop (PID: $loop_pid)"
        fi
        rm -f "logs/monitoring-loop.pid"
    fi
}

show_status() {
    echo -e "${BLUE}🔐 Infisical Monitoring Status${NC}"
    printf '=%.0s' {1..40}; echo
    
    # Check monitoring process
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "📊 Monitoring: ${GREEN}RUNNING${NC} (PID: $pid)"
        else
            echo -e "📊 Monitoring: ${RED}STOPPED${NC} (stale PID)"
        fi
    else
        echo -e "📊 Monitoring: ${RED}STOPPED${NC}"
    fi
    
    # Check dashboard server
    if [[ -f "logs/dashboard-server.pid" ]]; then
        local server_pid=$(cat "logs/dashboard-server.pid")
        if kill -0 "$server_pid" 2>/dev/null; then
            echo -e "🌐 Dashboard: ${GREEN}RUNNING${NC} (PID: $server_pid, Port: $DASHBOARD_PORT)"
        else
            echo -e "🌐 Dashboard: ${RED}STOPPED${NC} (stale PID)"
        fi
    else
        echo -e "🌐 Dashboard: ${RED}STOPPED${NC}"
    fi
    
    # Check monitoring loop
    if [[ -f "logs/monitoring-loop.pid" ]]; then
        local loop_pid=$(cat "logs/monitoring-loop.pid")
        if kill -0 "$loop_pid" 2>/dev/null; then
            echo -e "🔄 Auto-refresh: ${GREEN}RUNNING${NC} (PID: $loop_pid)"
        else
            echo -e "🔄 Auto-refresh: ${RED}STOPPED${NC} (stale PID)"
        fi
    else
        echo -e "🔄 Auto-refresh: ${RED}STOPPED${NC}"
    fi
    
    # Show recent metrics if available
    if [[ -f "monitoring/dashboards/infisical-dashboard.json" ]]; then
        echo
        echo -e "${BLUE}📈 Latest Metrics:${NC}"
        python3 -c "
import json
try:
    with open('monitoring/dashboards/infisical-dashboard.json') as f:
        data = json.load(f)
    print(f\"  Load Time: {data['performance_metrics']['secret_load_time_seconds']:.2f}s\")
    print(f\"  Cache Ratio: {data['performance_metrics']['secret_cache_hit_ratio']:.1%}\")
    print(f\"  Status: {data['system_status']['authentication_status']}\")
    print(f\"  Last Update: {data['timestamp']}\")
except:
    print('  No metrics available')
"
    fi
}

# Main execution
main() {
    print_banner
    
    case "${1:-start}" in
        start)
            check_dependencies
            setup_directories
            check_existing_process
            start_monitoring
            start_dashboard_server
            setup_continuous_monitoring
            show_dashboard_info
            
            # Store success in memory system
            if command -v ai-add-smart &> /dev/null; then
                ai-add-smart "SUCCESS: Infisical monitoring dashboard started successfully with continuous monitoring on port $DASHBOARD_PORT"
            fi
            ;;
        stop)
            stop_monitoring
            echo -e "${GREEN}✅ All monitoring services stopped${NC}"
            ;;
        restart)
            stop_monitoring
            sleep 2
            "$0" start
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status}"
            echo
            echo "Commands:"
            echo "  start   - Start monitoring dashboard (default)"
            echo "  stop    - Stop all monitoring services"
            echo "  restart - Restart monitoring services"
            echo "  status  - Show current status"
            exit 1
            ;;
    esac
}

# Trap for cleanup on exit
trap 'echo "Cleaning up..."; stop_monitoring' EXIT

# Change to project directory
cd "$PROJECT_ROOT"

# Run main function
main "$@" 