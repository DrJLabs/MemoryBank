#!/bin/bash
# Enhanced AI Memory Integration Aliases for Cursor Environment
# These aliases implement proper conversational memory patterns

# Core AI Memory Commands
alias ai-memory='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py'
alias ai-add='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py categorize'
alias ai-search='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py search'
alias ai-context='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py ai-context'
alias ai-demo='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py demo'

# Specialized Memory Functions
alias ai-preference='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py add'
alias ai-learn='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py categorize'
alias ai-auto-search='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py auto-search'

# Quick Memory Access (What AI should do automatically)
alias mem-ai-context='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py ai-context'
alias mem-auto='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py auto-search'

# Compatibility with existing mem commands but enhanced
alias mem-add-ai='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py categorize'
alias mem-search-ai='python3 $HOME/*C-System/Memory-C*/mem0/openmemory/ai-memory-integration.py search'

echo "🧠 Enhanced AI Memory Integration Aliases Loaded"
echo "Commands: ai-add, ai-search, ai-context, ai-demo, ai-auto-search"
echo "AI Integration: mem-ai-context, mem-auto for automatic memory enrichment" 