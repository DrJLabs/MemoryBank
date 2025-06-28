#!/bin/bash
# BMAD Universal Agent Infisical Integration Script
# Architecture: Memory-C* Infisical Integration Architecture v1.0
# Created by: Winston (BMAD Architect)

set -euo pipefail

# Color output for better UX
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

# Universal Infisical Context Loading Function
load_infisical_context() {
    local agent_name="${AGENT_NAME:-BMAD Agent}"
    
    if command -v infisical >/dev/null 2>&1; then
        print_message "$BLUE" "🔐 Loading Infisical context for ${agent_name}..."
        
        # Test Infisical authentication
        if infisical secrets --env=dev >/dev/null 2>&1; then
            print_message "$GREEN" "✅ Infisical authenticated - secrets available"
            
            # Export essential environment variables from Infisical
            eval "$(infisical export --format dotenv --env=dev 2>/dev/null || true)"
            
            # Verify critical secrets are loaded
            if [[ -n "${OPENAI_API_KEY:-}" ]]; then
                print_message "$GREEN" "✅ OPENAI_API_KEY loaded successfully"
            else
                print_message "$YELLOW" "⚠️  OPENAI_API_KEY not found in secrets"
            fi
            
            return 0
        else
            print_message "$YELLOW" "⚠️  Infisical not authenticated - limited functionality"
            print_message "$BLUE" "💡 Run: infisical login && infisical init"
            return 1
        fi
    else
        print_message "$YELLOW" "⚠️  Infisical CLI not installed - secret management disabled"
        print_message "$BLUE" "💡 Install: curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.alpine.sh' | bash && apk add infisical"
        return 2
    fi
}

# Load Memory System Integration
load_memory_system() {
    local agent_name="${AGENT_NAME:-BMAD Agent}"
    
    print_message "$BLUE" "🧠 Loading Memory System for ${agent_name}..."
    
    # Check if memory system is available
    if [[ -f "advanced-memory-aliases.sh" ]]; then
        source advanced-memory-aliases.sh
        print_message "$GREEN" "✅ Memory system aliases loaded"
        
        # Test memory system connectivity
        if command -v ai-analytics >/dev/null 2>&1; then
            print_message "$GREEN" "✅ Memory system commands available"
        else
            print_message "$YELLOW" "⚠️  Memory system commands not in PATH"
        fi
    else
        print_message "$YELLOW" "⚠️  advanced-memory-aliases.sh not found"
    fi
}

# Integrated Agent Status Check
check_agent_status() {
    local agent_name="${AGENT_NAME:-BMAD Agent}"
    
    print_message "$BLUE" "📊 ${agent_name} System Status:"
    
    # Infisical Status
    if command -v infisical >/dev/null 2>&1; then
        if infisical secrets --env=dev >/dev/null 2>&1; then
            print_message "$GREEN" "  Infisical: ✅ Available & Authenticated"
        else
            print_message "$YELLOW" "  Infisical: ⚠️  Available but not authenticated"
        fi
    else
        print_message "$RED" "  Infisical: ❌ Not installed"
    fi
    
    # Memory System Status
    if command -v ai-analytics >/dev/null 2>&1; then
        print_message "$GREEN" "  Memory System: ✅ Available"
    else
        print_message "$YELLOW" "  Memory System: ⚠️  Not available"
    fi
    
    # Docker Status
    if command -v docker >/dev/null 2>&1; then
        print_message "$GREEN" "  Docker: ✅ Available"
    else
        print_message "$YELLOW" "  Docker: ⚠️  Not available"
    fi
    
    # Git Status
    if command -v git >/dev/null 2>&1; then
        print_message "$GREEN" "  Git: ✅ Available"
    else
        print_message "$YELLOW" "  Git: ⚠️  Not available"
    fi
}

# Store Agent Integration Success in Memory
store_integration_success() {
    local agent_name="${AGENT_NAME:-BMAD Agent}"
    
    # Store integration success if memory system is available
    if command -v ai-add-smart >/dev/null 2>&1; then
        ai-add-smart "BMAD INTEGRATION: ${agent_name} successfully integrated with Infisical secret management and memory system. Full context loading enabled."
        print_message "$GREEN" "✅ Integration success stored in memory"
    fi
}

# Main Integration Function
main() {
    local agent_name="${1:-${AGENT_NAME:-BMAD Agent}}"
    export AGENT_NAME="$agent_name"
    
    print_message "$BLUE" "🎭 Initializing ${agent_name} with enhanced integration..."
    
    # Phase 1: Load Infisical Context
    load_infisical_context
    infisical_status=$?
    
    # Phase 2: Load Memory System
    load_memory_system
    
    # Phase 3: Status Check
    check_agent_status
    
    # Phase 4: Store Success
    if [[ $infisical_status -eq 0 ]]; then
        store_integration_success
    fi
    
    print_message "$GREEN" "🚀 ${agent_name} integration complete!"
    
    return $infisical_status
}

# Export functions for use in other scripts
export -f load_infisical_context
export -f load_memory_system
export -f check_agent_status
export -f store_integration_success

# If script is run directly, execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 