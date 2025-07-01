#!/bin/bash
"""
GitHub Projects Integration Startup Script
Launches Memory-C* GitHub Projects integration service
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MEMORY_API_PORT=8765
GITHUB_PROJECT_NUMBER=1

echo -e "${BLUE}🚀 Memory-C* GitHub Projects Integration Startup${NC}"
echo -e "${BLUE}===============================================${NC}"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Memory-C* API running on port $port${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Memory-C* API not running on port $port${NC}"
        return 1
    fi
}

# Function to check environment variables
check_env() {
    echo -e "${BLUE}🔍 Checking environment configuration...${NC}"
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}❌ GITHUB_TOKEN environment variable not set${NC}"
        echo -e "${YELLOW}💡 To fix this:${NC}"
        echo "   1. Go to https://github.com/settings/tokens"
        echo "   2. Create a Personal Access Token with 'repo' and 'project' scopes"
        echo "   3. Export it: export GITHUB_TOKEN=your_token_here"
        echo "   4. Add to ~/.bashrc: echo 'export GITHUB_TOKEN=your_token' >> ~/.bashrc"
        return 1
    else
        echo -e "${GREEN}✅ GITHUB_TOKEN configured${NC}"
    fi
    
    echo -e "${GREEN}✅ GitHub Org: ${GITHUB_ORG:-DrJLabs}${NC}"
    echo -e "${GREEN}✅ GitHub Repo: ${GITHUB_REPO:-MemoryBank}${NC}"
    echo -e "${GREEN}✅ Project Number: ${GITHUB_PROJECT_NUMBER:-1}${NC}"
    
    return 0
}

# Function to test GitHub connection
test_github_connection() {
    echo -e "${BLUE}🔗 Testing GitHub Projects connection...${NC}"
    
    cd "$(dirname "$0")"
    
    if python3 github-projects-integration.py --test; then
        echo -e "${GREEN}✅ GitHub Projects connection successful${NC}"
        return 0
    else
        echo -e "${RED}❌ GitHub Projects connection failed${NC}"
        return 1
    fi
}

# Function to start the service
start_service() {
    echo -e "${BLUE}🚀 Starting GitHub Projects integration service...${NC}"
    
    cd "$(dirname "$0")"
    
    # Create log directory
    mkdir -p logs
    
    # Start the service
    echo -e "${GREEN}📝 Logs will be written to logs/github-projects.log${NC}"
    echo -e "${GREEN}🔄 Service starting... (Press Ctrl+C to stop)${NC}"
    
    python3 github-projects-integration.py 2>&1 | tee logs/github-projects.log
}

# Function to show help
show_help() {
    echo -e "${BLUE}GitHub Projects Integration for Memory-C*${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --test         Test connection only"
    echo "  --sync-once    Run one sync and exit"
    echo "  --setup        Show setup instructions"
    echo "  --health       Check system health"
    echo "  --help         Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  GITHUB_TOKEN           Required: GitHub Personal Access Token"
    echo "  GITHUB_ORG            Optional: GitHub organization (default: DrJLabs)"
    echo "  GITHUB_REPO           Optional: Repository name (default: MemoryBank)"
    echo "  GITHUB_PROJECT_NUMBER Optional: Project number (default: 1)"
    echo ""
}

# Function to show setup instructions
show_setup() {
    echo -e "${BLUE}📋 GitHub Projects Setup Instructions${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo ""
    echo -e "${YELLOW}1. Create GitHub Personal Access Token:${NC}"
    echo "   • Go to: https://github.com/settings/tokens"
    echo "   • Click 'Generate new token' → 'Generate new token (classic)'"
    echo "   • Select scopes: 'repo', 'project', 'write:org'"
    echo "   • Copy the token"
    echo ""
    echo -e "${YELLOW}2. Set Environment Variable:${NC}"
    echo "   export GITHUB_TOKEN=your_token_here"
    echo "   echo 'export GITHUB_TOKEN=your_token' >> ~/.bashrc"
    echo ""
    echo -e "${YELLOW}3. Create GitHub Project:${NC}"
    echo "   • Go to: https://github.com/orgs/DrJLabs/projects"
    echo "   • Click 'New project' → 'Table'"
    echo "   • Name: 'Memory-C* Development'"
    echo "   • Add fields: Status, Priority, Category"
    echo ""
    echo -e "${YELLOW}4. Configure Repository:${NC}"
    echo "   • Repository: DrJLabs/MemoryBank"
    echo "   • Enable Issues and Projects in repo settings"
    echo ""
}

# Function to check system health
check_health() {
    echo -e "${BLUE}🏥 System Health Check${NC}"
    echo -e "${BLUE}====================${NC}"
    
    local health_score=0
    local total_checks=4
    
    # Check Memory-C* API
    if check_port $MEMORY_API_PORT; then
        ((health_score++))
    fi
    
    # Check environment
    if check_env > /dev/null 2>&1; then
        ((health_score++))
        echo -e "${GREEN}✅ Environment configuration${NC}"
    else
        echo -e "${RED}❌ Environment configuration${NC}"
    fi
    
    # Check GitHub connection
    if test_github_connection > /dev/null 2>&1; then
        ((health_score++))
        echo -e "${GREEN}✅ GitHub Projects connection${NC}"
    else
        echo -e "${RED}❌ GitHub Projects connection${NC}"
    fi
    
    # Check Python dependencies
    if python3 -c "import requests, asyncio" 2>/dev/null; then
        ((health_score++))
        echo -e "${GREEN}✅ Python dependencies${NC}"
    else
        echo -e "${RED}❌ Python dependencies (run: pip install requests)${NC}"
    fi
    
    # Calculate health percentage
    local health_percent=$((health_score * 100 / total_checks))
    
    echo ""
    if [ $health_percent -ge 75 ]; then
        echo -e "${GREEN}🎉 System Health: $health_percent% - Good to go!${NC}"
    elif [ $health_percent -ge 50 ]; then
        echo -e "${YELLOW}⚠️  System Health: $health_percent% - Some issues need attention${NC}"
    else
        echo -e "${RED}🔥 System Health: $health_percent% - Critical issues detected${NC}"
    fi
}

# Main execution logic
case "${1:-}" in
    --test)
        check_env && test_github_connection
        ;;
    --sync-once)
        echo -e "${BLUE}🔄 Running one-time sync...${NC}"
        cd "$(dirname "$0")"
        python3 -c "
import asyncio
from github_projects_integration import GitHubProjectsService
service = GitHubProjectsService()
asyncio.run(service.sync_service.sync_insights())
print('✅ Sync completed!')
"
        ;;
    --setup)
        show_setup
        ;;
    --health)
        check_health
        ;;
    --help)
        show_help
        ;;
    "")
        # Default: start the service
        echo -e "${BLUE}Starting GitHub Projects integration...${NC}"
        
        # Check prerequisites
        if ! check_port $MEMORY_API_PORT; then
            echo -e "${YELLOW}💡 Start Memory-C* API first: cd mem0/openmemory && python3 api.py${NC}"
            echo ""
        fi
        
        if ! check_env; then
            echo -e "${YELLOW}💡 Run with --setup for configuration instructions${NC}"
            exit 1
        fi
        
        if ! test_github_connection; then
            echo -e "${YELLOW}💡 Run with --setup to fix GitHub connection${NC}"
            exit 1
        fi
        
        # Start the service
        start_service
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac 