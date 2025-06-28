#!/bin/bash
# Advanced Memory Integration Aliases - Enterprise Grade
# Updated for C-System structure (removed * from directory names)
# Utilizes full OpenMemory API: pagination, filtering, categories, related memories, analytics

# ============================================================================
# CORE ADVANCED MEMORY COMMANDS
# ============================================================================

alias adv-memory='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py'
alias ai-search='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'
alias ai-context='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context'
alias ai-add-adv='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py add'
alias ai-analytics='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py analytics'

# What AI should use automatically (recommended for AI integration)
alias ai-get-context='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context'
alias ai-intelligent-search='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'

# ============================================================================
# QUERY TYPE SPECIFIC SEARCHES
# ============================================================================

alias ai-search-pref='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'
alias ai-search-tech='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'
alias ai-search-project='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'
alias ai-search-workflow='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search'

# ============================================================================
# AI INTEGRATION FUNCTIONS (Enhanced Context Commands)
# ============================================================================

# Main AI context function with type detection
ai-ctx() {
    local query="$*"
    local query_type="${query_type:-general}"
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$query" "$query_type"
}

# Type-specific context functions for AI responses
ai-ctx-pref() {
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$*" preference
}

ai-ctx-tech() {
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$*" technical
}

ai-ctx-project() {
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$*" project
}

ai-ctx-workflow() {
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$*" workflow
}

ai-ctx-learning() {
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py context "$*" learning
}

# ============================================================================
# ENHANCED MEMORY MANAGEMENT
# ============================================================================

alias ai-archive-old='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py archive-old'
alias ai-demo='python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py demo'

# Alternative integration script (lighter weight) - FULL COVERAGE
alias ai-integration='python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py'
alias ai-integration-context='python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py ai-context'
alias ai-auto-search='python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py auto-search'
alias ai-categorize='python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py categorize'
alias ai-integration-demo='python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py demo'

# ============================================================================
# COMPATIBILITY ALIASES (Enhanced versions of simple commands)
# ============================================================================

alias mem-search-enhanced='ai-search'
alias mem-add-enhanced='ai-add-adv'
alias mem-context='ai-context'
alias mem-analytics='ai-analytics'

# ============================================================================
# INTELLIGENT MEMORY FUNCTIONS (Advanced Features)
# ============================================================================

# Smart add with auto-categorization
ai-add-smart() {
    local category=""
    local text="$*"
    
    # Auto-detect category from text patterns
    if [[ "$text" =~ (prefer|like|always|never|setting) ]]; then
        category="PREFERENCE"
    elif [[ "$text" =~ (command|workflow|process|step) ]]; then
        category="WORKFLOW"
    elif [[ "$text" =~ (programming|code|technical|development) ]]; then
        category="TECHNICAL"
    elif [[ "$text" =~ (project|feature|task) ]]; then
        category="PROJECT"
    elif [[ "$text" =~ (learned|discovered|insight) ]]; then
        category="LEARNING"
    fi
    
    if [[ -n "$category" ]]; then
        python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py add "$text" "$category"
    else
        python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py add "$text"
    fi
}

# Contextual search with project awareness
ai-search-contextual() {
    local query="$*"
    local project_context=$(basename "$(pwd)")
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py search "$project_context $query" project
}

# Quick analytics dashboard
ai-memory-status() {
    echo "🧠 Advanced Memory System Status"
    echo "================================="
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py analytics
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Test memory system functionality
ai-memory-test() {
    echo "🧪 Testing Advanced Memory System..."
    python3 $HOME/C-System/Memory-C*/scripts/advanced-memory-ai.py demo
    echo ""
    echo "🔧 Testing AI Integration..."
    python3 $HOME/C-System/Memory-C*/scripts/ai-memory-integration.py demo
}

# Show available commands
ai-memory-help() {
    echo "🧠 Advanced AI Memory Integration Commands"
    echo "========================================="
    echo ""
    echo "🔍 SEARCH & CONTEXT:"
    echo "  ai-search <query> [type]        - Intelligent multi-strategy search"
    echo "  ai-context <query> [type]       - Get rich AI conversation context"
    echo "  ai-ctx <query>                  - Quick context (auto-detect type)"
    echo "  ai-ctx-tech <query>             - Technical context"
    echo "  ai-ctx-pref <query>             - Preference context"
    echo "  ai-ctx-project <query>          - Project context"
    echo "  ai-ctx-workflow <query>         - Workflow context"
    echo ""
    echo "💾 MEMORY MANAGEMENT:"
    echo "  ai-add-adv <text> [category]    - Add enhanced memory"
    echo "  ai-add-smart <text>             - Add with auto-categorization"
    echo "  ai-categorize <text>            - Add with auto-categorization (integration script)"
    echo "  ai-archive-old [days]           - Archive old memories"
    echo ""
    echo "📊 ANALYTICS & SYSTEM:"
    echo "  ai-analytics                    - System analytics"
    echo "  ai-memory-status                - Quick status overview"
    echo "  ai-memory-test                  - Test system functionality"
    echo "  ai-auto-search <query> [type]   - Demonstrate auto-search functionality"
    echo "  ai-integration-context <query>  - Get lighter-weight AI context"
    echo ""
    echo "🎯 QUERY TYPES: preference, technical, project, workflow, learning, general"
    echo ""
    echo "💡 AI INTEGRATION TIP:"
    echo "   Use 'ai-get-context \"<user_query>\" [type]' before generating responses"
}

# ============================================================================
# SYSTEM LOADING MESSAGE
# ============================================================================

echo "🧠 Advanced AI Memory Integration Loaded - Enterprise Grade"
echo "🚀 Core Commands: ai-search, ai-context, ai-add-adv, ai-analytics"
echo "🎯 AI Context: ai-ctx, ai-ctx-pref, ai-ctx-tech, ai-ctx-project, ai-ctx-workflow"
echo "📊 Features: Multi-Strategy Search, Relevance Scoring, Auto-Categorization"
echo "💡 AI Integration: Use ai-get-context before responses for personalized context"
echo "❓ Help: Type 'ai-memory-help' for full command reference"
echo "" alias bmad=\"/home/drj/C-System/Memory-C*/bmad.sh\"
