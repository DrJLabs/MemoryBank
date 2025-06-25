#!/bin/bash
# Advanced Memory Integration Aliases - Enterprise Grade
# Utilizes full OpenMemory API: pagination, filtering, categories, related memories, analytics

# Core Advanced Memory Commands
alias adv-memory='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py'
alias ai-search='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'
alias ai-context='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context'
alias ai-add-adv='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py add'
alias ai-analytics='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py analytics'

# What AI should use automatically (my new behavior)
alias ai-get-context='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context'
alias ai-intelligent-search='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'

# Query Type Specific Searches
alias ai-search-pref='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'
alias ai-search-tech='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'
alias ai-search-project='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'
alias ai-search-workflow='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py search'

# Quick Context Commands (what I should use before responses)
ai-ctx() {
    local query="$*"
    local query_type="${query_type:-general}"
    python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context "$query" "$query_type"
}

ai-ctx-pref() {
    python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context "$*" preference
}

ai-ctx-tech() {
    python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context "$*" technical
}

ai-ctx-project() {
    python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context "$*" project
}

ai-ctx-workflow() {
    python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py context "$*" workflow
}

# Enhanced Memory Management
alias ai-archive-old='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py archive-old'
alias ai-demo='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/advanced-memory-ai.py demo'

# Compatibility with existing simple commands but enhanced
alias mem-search-enhanced='ai-search'
alias mem-add-enhanced='ai-add-adv'
alias mem-context='ai-context'

echo "🧠 Advanced AI Memory Integration Loaded - Enterprise Grade"
echo "🚀 Commands: ai-search, ai-context, ai-add-adv, ai-analytics"
echo "🎯 AI Context: ai-ctx, ai-ctx-pref, ai-ctx-tech, ai-ctx-project, ai-ctx-workflow"
echo "📊 Features: Pagination, Filtering, Categories, Related Memories, Relevance Scoring"
echo "💡 AI should use: ai-get-context \"query\" [type] before generating responses" 