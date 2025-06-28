#!/bin/bash

# BMAD Orchestrator Shim - Enhanced with Infisical Integration

# This script simulates the behavior of the bmad-orchestrator agent.
# It reads the agent's definition file and executes the commands accordingly.

# Function to check and load Infisical secrets
load_infisical_context() {
    if command -v infisical >/dev/null 2>&1; then
        echo "🔐 Loading Infisical context..."
        # Test Infisical authentication
        if infisical secrets --env=dev >/dev/null 2>&1; then
            echo "✅ Infisical authenticated - secrets available"
            # Export essential environment variables from Infisical
            eval "$(infisical export --format dotenv --env=dev 2>/dev/null || true)"
        else
            echo "⚠️  Infisical not authenticated - run 'infisical login' and 'infisical init'"
        fi
    else
        echo "⚠️  Infisical CLI not installed - secret management disabled"
    fi
    
    # Load memory system aliases if available
    if [[ -f "advanced-memory-aliases.sh" ]]; then
        source advanced-memory-aliases.sh >/dev/null 2>&1
    fi
}

# Function to read a value from a YAML file
# Usage: read_yaml <file> <key>
read_yaml() {
    grep "^$2:" "$1" | sed "s/^$2: //" | tr -d ''''
}

# Main function
main() {
    local agent_file="/home/drj/C-System/Memory-C*/.bmad-core/agents/bmad-orchestrator.md"
    local command="$1"
    local args="${@:2}"

    # Load Infisical context on startup
    if [[ -z "$command" ]] || [[ "$command" == "*help" ]] || [[ "$command" == "*status" ]]; then
        load_infisical_context
    fi

    if [[ -z "$command" ]]; then
        # Enhanced startup message with Infisical status
        echo "🎭 BMad Orchestrator (Memory-Enhanced + Infisical-Secured)"
        echo "I can coordinate agents and workflows with contextual awareness and secure secret management."
        echo "All commands start with * (e.g., *help, *agent, *workflow)"
        echo "🔐 Secret management: $(command -v infisical >/dev/null && echo "✅ Available" || echo "❌ Not installed")"
        return
    fi

    # Remove the leading asterisk from the command
    command="${command#\*}"

    case "$command" in
        "help")
            echo "Available commands:"
            grep -E '^\s+\*.*:' "$agent_file" | sed 's/^\s+\*//'
            echo ""
            echo "🔐 Infisical Integration:"
            echo "  *secrets        - Show available secrets"
            echo "  *reload-secrets - Reload secrets from Infisical"
            ;;
        "secrets")
            if command -v infisical >/dev/null 2>&1; then
                echo "🔐 Available secrets in dev environment:"
                infisical secrets --env=dev --recursive
            else
                echo "❌ Infisical CLI not available"
            fi
            ;;
        "reload-secrets")
            load_infisical_context
            ;;
        "status")
            load_infisical_context
            echo "📊 BMAD System Status:"
            echo "  Memory System: $(type ai-analytics >/dev/null 2>&1 && echo "✅ Available" || echo "❌ Not available")"
            echo "  Infisical: $(command -v infisical >/dev/null && echo "✅ Available" || echo "❌ Not installed")"
            echo "  Docker: $(command -v docker >/dev/null && echo "✅ Available" || echo "❌ Not installed")"
            ;;
        "agent")
            if [[ -n "$args" ]]; then
                echo "🔄 Transforming into agent: $args"
                echo "🔐 Loading Infisical context for agent..."
                load_infisical_context
                # Here you would add the logic to "become" the agent.
                # For now, we'll just display a message.
            else
                echo "Available agents:"
                ls -1 "/home/drj/C-System/Memory-C*/.bmad-core/agents" | sed 's/\.md$//'
            fi
            ;;
        "workflow")
            if [[ -n "$args" ]]; then
                echo "🚀 Starting workflow: $args"
                echo "🔐 Ensuring secrets are available for workflow..."
                load_infisical_context
                # Here you would add the logic to start the workflow.
            else
                echo "Available workflows:"
                ls -1 "/home/drj/C-System/Memory-C*/.bmad-core/workflows" | sed 's/\.yml$//' 2>/dev/null || echo "No workflows directory found"
            fi
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use *help to see available commands"
            ;;
    esac
}

main "$@"
