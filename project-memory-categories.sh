#!/bin/bash
# Project-Specific Memory Categories for Memory-C*
# Enhanced memory functions for targeted categorization

# ============================================================================
# PROJECT-SPECIFIC MEMORY FUNCTIONS
# ============================================================================

# Memory Operations Category
ai-add-memory-ops() {
    ai-add-adv "$*" MEMORY_OPS
}

# AI/ML Analytics Category  
ai-add-ai-ml() {
    ai-add-adv "$*" AI_ML
}

# Integration Patterns Category
ai-add-integration() {
    ai-add-adv "$*" INTEGRATION
}

# Monitoring and Health Category
ai-add-monitoring() {
    ai-add-adv "$*" MONITORING  
}

# Testing and Quality Category
ai-add-testing() {
    ai-add-adv "$*" TESTING
}

# Development Phase Category
ai-add-phase() {
    ai-add-adv "$*" PHASE
}

# UI/UX Design Category
ai-add-ui-ux() {
    ai-add-adv "$*" UI_UX
}

# BMAD Integration Category
ai-add-bmad() {
    ai-add-adv "$*" BMAD
}

# Architecture Decisions Category
ai-add-architecture() {
    ai-add-adv "$*" ARCHITECTURE
}

# Maintenance Operations Category
ai-add-maintenance() {
    ai-add-adv "$*" MAINTENANCE
}

# ============================================================================
# PROJECT-SPECIFIC CONTEXT FUNCTIONS
# ============================================================================

# Memory Operations Context
ai-ctx-memory-ops() {
    ai-search "$*" MEMORY_OPS
}

# AI/ML Context
ai-ctx-ai-ml() {
    ai-search "$*" AI_ML
}

# Integration Context
ai-ctx-integration() {
    ai-search "$*" INTEGRATION
}

# Monitoring Context
ai-ctx-monitoring() {
    ai-search "$*" MONITORING
}

# Testing Context
ai-ctx-testing() {
    ai-search "$*" TESTING
}

# Phase Context
ai-ctx-phase() {
    ai-search "$*" PHASE
}

# UI/UX Context
ai-ctx-ui-ux() {
    ai-search "$*" UI_UX
}

# BMAD Context
ai-ctx-bmad() {
    ai-search "$*" BMAD
}

# Architecture Context
ai-ctx-architecture() {
    ai-search "$*" ARCHITECTURE
}

# Maintenance Context
ai-ctx-maintenance() {
    ai-search "$*" MAINTENANCE
}

# ============================================================================
# SMART PROJECT CATEGORIZATION
# ============================================================================

# Enhanced smart add with project-specific patterns
ai-add-project-smart() {
    local text="$*"
    local category=""
    
    # Project-specific pattern matching
    if [[ "$text" =~ (memory operation|embedding|vector store|mem0|openmemory core) ]]; then
        category="MEMORY_OPS"
    elif [[ "$text" =~ (machine learning|prediction|analytics|model accuracy|phase5|predictive) ]]; then
        category="AI_ML"
    elif [[ "$text" =~ (github projects|api integration|webhook|sync|graphql) ]]; then
        category="INTEGRATION"
    elif [[ "$text" =~ (health check|monitoring|alert|metrics|performance|dashboard) ]]; then
        category="MONITORING"
    elif [[ "$text" =~ (test framework|validation|coverage|quality|hypothesis|pytest) ]]; then
        category="TESTING"
    elif [[ "$text" =~ (phase|milestone|development stage|sprint|iteration) ]]; then
        category="PHASE"
    elif [[ "$text" =~ (dashboard|visualization|interface|user experience|frontend) ]]; then
        category="UI_UX"
    elif [[ "$text" =~ (bmad|agent|orchestration|workflow|task execution) ]]; then
        category="BMAD"
    elif [[ "$text" =~ (system design|component|dependency|architecture|structure) ]]; then
        category="ARCHITECTURE"
    elif [[ "$text" =~ (backup|maintenance|operational|system health|cleanup) ]]; then
        category="MAINTENANCE"
    else
        # Fall back to standard categorization
        ai-add-smart "$text"
        return
    fi
    
    echo "🎯 Project Category Detected: $category"
    ai-add-adv "$text" "$category"
}

# ============================================================================
# PROJECT ANALYTICS FUNCTIONS
# ============================================================================

# Get project-specific memory distribution
ai-project-memory-stats() {
    echo "📊 Memory-C* Project Memory Distribution:"
    echo "=========================================="
    
    for category in MEMORY_OPS AI_ML INTEGRATION MONITORING TESTING PHASE UI_UX BMAD ARCHITECTURE MAINTENANCE; do
        count=$(ai-search "" "$category" 2>/dev/null | grep -c "📊" || echo "0")
        echo "$category: $count memories"
    done
}

# Get comprehensive project context
ai-project-context() {
    local query="$1"
    echo "🎯 Memory-C* Project Context for: $query"
    echo "========================================"
    
    echo ""
    echo "🧠 Core Memory Operations:"
    ai-ctx-memory-ops "$query" 2>/dev/null | head -3
    
    echo ""
    echo "🤖 AI/ML Analytics:"
    ai-ctx-ai-ml "$query" 2>/dev/null | head -3
    
    echo ""
    echo "🔗 Integration Patterns:"
    ai-ctx-integration "$query" 2>/dev/null | head -3
    
    echo ""
    echo "📊 Monitoring Insights:"
    ai-ctx-monitoring "$query" 2>/dev/null | head -3
}

# ============================================================================
# PHASE-SPECIFIC FUNCTIONS
# ============================================================================

# Phase progression tracking
ai-track-phase() {
    local phase="$1"
    local status="$2"
    local insight="$3"
    
    ai-add-phase "PHASE_TRACK: Phase $phase - Status: $status - Insight: $insight - Date: $(date)"
}

# Phase analytics
ai-phase-analytics() {
    echo "📈 Memory-C* Phase Analytics:"
    echo "============================"
    ai-ctx-phase "phase progression" | head -10
}

# ============================================================================
# HELP AND DISCOVERY
# ============================================================================

# Show all project-specific commands
ai-project-help() {
    echo "🎯 Memory-C* Project-Specific Commands:"
    echo "======================================="
    echo ""
    echo "📝 STORAGE COMMANDS:"
    echo "  ai-add-memory-ops <text>    - Core memory operations"
    echo "  ai-add-ai-ml <text>         - AI/ML analytics insights"
    echo "  ai-add-integration <text>   - Integration patterns"
    echo "  ai-add-monitoring <text>    - Monitoring and health"
    echo "  ai-add-testing <text>       - Testing and quality"
    echo "  ai-add-phase <text>         - Development phases"
    echo "  ai-add-ui-ux <text>         - UI/UX design"
    echo "  ai-add-bmad <text>          - BMAD integration"
    echo "  ai-add-architecture <text>  - Architecture decisions"
    echo "  ai-add-maintenance <text>   - Maintenance operations"
    echo ""
    echo "🔍 CONTEXT COMMANDS:"
    echo "  ai-ctx-memory-ops <query>   - Memory operations context"
    echo "  ai-ctx-ai-ml <query>        - AI/ML context"
    echo "  ai-ctx-integration <query>  - Integration context"
    echo "  ai-ctx-monitoring <query>   - Monitoring context"
    echo "  ai-ctx-testing <query>      - Testing context"
    echo "  ai-ctx-phase <query>        - Phase context"
    echo "  ai-ctx-ui-ux <query>        - UI/UX context"
    echo "  ai-ctx-bmad <query>         - BMAD context"
    echo "  ai-ctx-architecture <query> - Architecture context"
    echo "  ai-ctx-maintenance <query>  - Maintenance context"
    echo ""
    echo "🧠 SMART FUNCTIONS:"
    echo "  ai-add-project-smart <text> - Auto-categorize with project patterns"
    echo "  ai-project-context <query>  - Comprehensive project context"
    echo "  ai-project-memory-stats     - Memory distribution by category"
    echo "  ai-track-phase <phase> <status> <insight> - Track phase progression"
    echo "  ai-phase-analytics          - Phase progression analytics"
    echo ""
    echo "💡 Example Usage:"
    echo "  ai-add-memory-ops 'Vector embedding optimization improved search by 15%'"
    echo "  ai-ctx-ai-ml 'predictive analytics'"
    echo "  ai-project-context 'testing framework'"
    echo "  ai-track-phase '5' 'Complete' 'Advanced AI integration successful'"
}

# Load project-specific categories
echo "🎯 Memory-C* Project Categories Loaded"
echo "📂 Categories: MEMORY_OPS, AI_ML, INTEGRATION, MONITORING, TESTING, PHASE, UI_UX, BMAD, ARCHITECTURE, MAINTENANCE"
echo "❓ Help: Type 'ai-project-help' for project-specific commands" 