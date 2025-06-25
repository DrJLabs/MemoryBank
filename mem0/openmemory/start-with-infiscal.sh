#!/bin/bash
set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$BLUE" "🔍 Checking prerequisites..."
    
    local missing=()
    
    if ! command_exists docker; then
        missing+=("docker")
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        missing+=("docker-compose")
    fi
    
    if ! command_exists infisical; then
        missing+=("infisical")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_message "$RED" "❌ Missing required tools: ${missing[*]}"
        print_message "$YELLOW" "Please install missing tools before proceeding."
        exit 1
    fi
    
    print_message "$GREEN" "✅ All prerequisites met!"
}

# Function to load secrets from Infiscal
load_infiscal_secrets() {
    print_message "$BLUE" "🔐 Loading secrets from Infiscal..."
    
    # Export secrets from Infiscal
    if ! eval "$(infisical export --format dotenv)"; then
        print_message "$RED" "❌ Failed to load secrets from Infiscal"
        print_message "$YELLOW" "Make sure you've run 'infisical init' and added your secrets"
        exit 1
    fi
    
    # Verify OPENAI_API_KEY is loaded
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        print_message "$RED" "❌ OPENAI_API_KEY not found in Infiscal secrets"
        print_message "$YELLOW" "Run: infisical secrets set OPENAI_API_KEY=your-key"
        exit 1
    fi
    
    print_message "$GREEN" "✅ Secrets loaded successfully!"
}

# Function to create environment files
create_env_files() {
    print_message "$BLUE" "📝 Creating environment files..."
    
    # Set default user if not provided
    USER=${USER:-"openmemory-user"}
    
    # Create API .env file
    cat > api/.env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
USER=${USER}
EOF
    
    # Create UI .env file
    cat > ui/.env << EOF
NEXT_PUBLIC_API_URL=http://localhost:8765
NEXT_PUBLIC_USER_ID=${USER}
EOF
    
    print_message "$GREEN" "✅ Environment files created!"
}

# Function to build and start services
start_services() {
    print_message "$BLUE" "🔨 Building services..."
    
    # Build the services
    if docker compose version >/dev/null 2>&1; then
        docker compose build
    else
        docker-compose build
    fi
    
    print_message "$BLUE" "🚀 Starting services..."
    
    # Start the services
    if docker compose version >/dev/null 2>&1; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    # Wait for services to be ready
    print_message "$BLUE" "⏳ Waiting for services to be ready..."
    sleep 5
    
    # Check service status
    if docker compose version >/dev/null 2>&1; then
        docker compose ps
    else
        docker-compose ps
    fi
    
    print_message "$GREEN" "✅ Services started successfully!"
    print_message "$BLUE" "📍 Access points:"
    print_message "$YELLOW" "   - UI Dashboard: http://localhost:3010"
    print_message "$YELLOW" "   - API Server: http://localhost:8765"
    print_message "$YELLOW" "   - API Docs: http://localhost:8765/docs"
    print_message "$YELLOW" "   - Vector DB (Qdrant): http://localhost:6333"
}

# Function to stop services
stop_services() {
    print_message "$BLUE" "🛑 Stopping services..."
    
    if docker compose version >/dev/null 2>&1; then
        docker compose down
    else
        docker-compose down
    fi
    
    print_message "$GREEN" "✅ Services stopped!"
}

# Main execution
main() {
    print_message "$BLUE" "🎯 OpenMemory (Mem0) Infiscal Integration Startup Script"
    print_message "$BLUE" "=========================================="
    
    # Parse command line arguments
    case "${1:-start}" in
        start)
            check_prerequisites
            load_infiscal_secrets
            create_env_files
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            check_prerequisites
            load_infiscal_secrets
            create_env_files
            start_services
            ;;
        *)
            print_message "$YELLOW" "Usage: $0 {start|stop|restart}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 