#!/bin/bash
# Real-time resource monitoring for Memory-C*

while true; do
    clear
    echo "=== Memory-C* Resource Monitor ==="
    echo "$(date)"
    echo
    
    echo "=== System Resources ==="
    free -h
    echo
    
    echo "=== Docker Container Resources ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "(openmemory|mem0)"
    echo
    
    echo "=== Memory System Status ==="
    if curl -sf http://localhost:8765/docs >/dev/null 2>&1; then
        echo "✅ OpenMemory API: Healthy"
    else
        echo "❌ OpenMemory API: Down"
    fi
    
    if curl -sf http://localhost:6333/health >/dev/null 2>&1; then
        echo "✅ Qdrant Vector DB: Healthy"
    else
        echo "❌ Qdrant Vector DB: Down"
    fi
    
    echo
    echo "Press Ctrl+C to exit"
    sleep 5
done
