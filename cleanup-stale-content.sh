#!/usr/bin/env bash
# Memory-C* Stale Content Cleanup Script
# Generated from comprehensive project analysis

set -e

echo "🧹 Starting Memory-C* Stale Content Cleanup..."

# Phase 1: Safe Cache & Generated Files Cleanup
echo "📁 Phase 1: Removing cache and generated files..."
find . -name "__pycache__" -type d -print -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove editor-specific directories
if [ -d ".obsidian" ]; then
    echo "📝 Removing .obsidian directory (note-taking app files)"
    rm -rf .obsidian/
fi

# Phase 2: Create Organized Directory Structure
echo "📂 Phase 2: Creating organized directory structure..."
mkdir -p archive/docs archive/configs archive/experimental tests/integration tests/standalone

# Phase 3: Archive Stale Documentation
echo "📚 Phase 3: Archiving potentially stale documentation..."

# Archive resolved implementation docs
stale_docs=(
    "CONNECTIVITY_ISSUE_RESOLUTION.md"
    "VECTOR_GRAPH_SYNC_IMPLEMENTATION.md"
    "TRUE_RESET_ALL_IMPLEMENTATION.md"
    "network-analysis-report.md"
    "DASHBOARD_TROUBLESHOOTING.md"
    "port-management-summary.md"
    "tls-migration-guide.md"
    "STEP_3_COMPLETION_SUMMARY.md"
    "implementation-summary.md"
)

for doc in "${stale_docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  📄 Archiving: $doc"
        mv "$doc" archive/docs/
    fi
done

# Phase 4: Move Configuration Files
echo "⚙️  Phase 4: Archiving configuration files..."
config_files=(
    "docker-compose-dashboard.yml"
    "dashy-host-config.yml" 
    "dashy-config-fixed.yml"
    "traefik-tls13-config.yml"
    "nginx.conf"
    "portainer-proxy.conf"
)

for config in "${config_files[@]}"; do
    if [ -f "$config" ]; then
        echo "  ⚙️  Archiving: $config"
        mv "$config" archive/configs/
    fi
done

# Phase 5: Move Test Files to Organized Structure
echo "🧪 Phase 5: Organizing test files..."
test_files=(
    "test_error_handler_direct.py"
    "test_integration_simple.py"
    "test_reset_manager.py"
    "test-port-fix.py"
    "test_memory_error_integration.py"
    "test_graceful_error_handling.py"
    "test_vector_graph_sync.py"
    "memory_testing_standalone.py"
)

for test in "${test_files[@]}"; do
    if [ -f "$test" ]; then
        if [[ "$test" == *"standalone"* ]]; then
            echo "  🧪 Moving to standalone tests: $test"
            mv "$test" tests/standalone/
        else
            echo "  🧪 Moving to integration tests: $test"
            mv "$test" tests/integration/
        fi
    fi
done

# Phase 6: Archive Experimental Scripts
echo "🔬 Phase 6: Archiving experimental scripts..."
experimental_files=(
    "debug-memory.py"
    "fix-memory-ui.py"
    "growth-pattern-analyzer-fixed.py"
    "memory-ui-server.py"
    "port-manager.py"
    "working-memory-dashboard.py"
    "simple-memory-ui.html"
    "port-commands.sh"
)

for exp in "${experimental_files[@]}"; do
    if [ -f "$exp" ]; then
        echo "  🔬 Archiving: $exp"
        mv "$exp" archive/experimental/
    fi
done

# Phase 7: Archive Deployment Scripts (if not actively used)
echo "🚀 Phase 7: Archiving deployment scripts..."
deployment_files=(
    "deploy-dashboard-stack.sh"
    "run-dashy-host-network.sh"
)

for deploy in "${deployment_files[@]}"; do
    if [ -f "$deploy" ]; then
        echo "  🚀 Archiving: $deploy"
        mv "$deploy" archive/experimental/
    fi
done

# Create archive summary
echo "📋 Creating archive summary..."
cat > archive/ARCHIVE_SUMMARY.md << EOF
# Archive Summary - $(date)

This directory contains files that were moved during the stale content cleanup.

## Structure:
- \`docs/\` - Documentation that may be outdated or resolved
- \`configs/\` - Configuration files for services that may not be in use
- \`experimental/\` - Experimental scripts and deployment files

## Files Archived:
$(find archive/ -type f | sort)

## Rationale:
These files were identified as potentially stale content during project cleanup.
They are preserved in case they need to be restored or referenced.

To restore any file: \`mv archive/category/filename ./\`
EOF

echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "   📁 $(find archive/ -type f | wc -l) files archived"
echo "   🧪 $(find tests/ -type f 2>/dev/null | wc -l) test files organized"
echo "   📂 Archive structure created in ./archive/"
echo ""
echo "📖 See archive/ARCHIVE_SUMMARY.md for details" 