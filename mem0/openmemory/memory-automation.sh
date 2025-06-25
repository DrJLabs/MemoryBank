#!/bin/bash
set -euo pipefail

# Memory Automation Script for OpenMemory
# Uses direct API calls instead of MCP due to compatibility issues

API_URL="http://localhost:8765/api/v1"
USER_ID="drj"

# Function to add memory
add_memory() {
    local text="$1"
    echo "Adding memory: $text"
    curl -s -X POST "$API_URL/memories/" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$text\", \"user_id\": \"$USER_ID\"}" | jq .
}

# Function to search memories
search_memories() {
    local query="$1"
    echo "Searching for: $query"
    curl -s -X POST "$API_URL/memories/filter" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"user_id\": \"$USER_ID\"}" | jq .
}

# Function to list all memories
list_memories() {
    echo "Listing all memories for user: $USER_ID"
    curl -s -X GET "$API_URL/memories/?user_id=$USER_ID" | jq . 2>/dev/null || echo "Note: List endpoint has a known issue, use the UI instead"
}

# Main menu
case "${1:-help}" in
    add)
        shift
        add_memory "$*"
        ;;
    search)
        shift
        search_memories "$*"
        ;;
    list)
        list_memories
        ;;
    *)
        echo "Usage: $0 {add|search|list} [text]"
        echo "Examples:"
        echo "  $0 add I prefer Python for AI development"
        echo "  $0 search Python preferences"
        echo "  $0 list"
        ;;
esac 