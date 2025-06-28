#!/bin/bash
# Advanced Memory Integration Setup Script
# Permanently installs the enterprise-grade memory system

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_ROOT="$HOME/C-System/Memory-C*"
ALIASES_FILE="$MEMORY_ROOT/advanced-memory-aliases.sh"

echo "🧠 Advanced AI Memory Integration Setup"
echo "======================================="
echo ""

# Verify we're in the right location
if [[ ! -f "$ALIASES_FILE" ]]; then
    echo "❌ Error: Cannot find advanced-memory-aliases.sh in $MEMORY_ROOT"
    echo "   Please run this script from the Memory-C* root directory"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$MEMORY_ROOT/scripts/advanced-memory-ai.py"
chmod +x "$MEMORY_ROOT/scripts/ai-memory-integration.py"
chmod +x "$ALIASES_FILE"

# Test the system first
echo "🧪 Testing memory system functionality..."
if ! python3 "$MEMORY_ROOT/scripts/advanced-memory-ai.py" analytics > /dev/null 2>&1; then
    echo "❌ Error: Memory system not responding. Is the OpenMemory API running?"
    echo "   Please ensure the memory service is running on localhost:8765"
    exit 1
fi

echo "✅ Memory system is functional"

# Check if already installed
BASHRC_LINE="source $ALIASES_FILE"
if grep -Fxq "$BASHRC_LINE" ~/.bashrc; then
    echo "⚠️  Advanced memory aliases already installed in ~/.bashrc"
    echo "   To reinstall, remove the line from ~/.bashrc and run this script again"
else
    # Install to bashrc
    echo ""
    echo "📝 Installing to ~/.bashrc for permanent access..."
    echo "# Advanced AI Memory Integration - Auto-loaded" >> ~/.bashrc
    echo "$BASHRC_LINE" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
fi

# Create convenience symlinks
echo ""
echo "🔗 Creating convenience links..."
mkdir -p ~/bin
ln -sf "$MEMORY_ROOT/scripts/advanced-memory-ai.py" ~/bin/ai-memory 2>/dev/null || true
ln -sf "$MEMORY_ROOT/scripts/ai-memory-integration.py" ~/bin/ai-integration 2>/dev/null || true

# Test installation
echo ""
echo "🧪 Testing installation..."
source "$ALIASES_FILE"

if command -v ai-search >/dev/null 2>&1; then
    echo "✅ Aliases loaded successfully"
else
    echo "⚠️  Aliases not loaded in current session. They will be available in new terminal sessions."
fi

# Summary
echo ""
echo "🎉 Advanced Memory Integration Setup Complete!"
echo "=============================================="
echo ""
echo "🚀 IMMEDIATELY AVAILABLE:"
echo "   • All ai-* commands are now active in new terminal sessions"
echo "   • Scripts available as: ~/bin/ai-memory and ~/bin/ai-integration"
echo ""
echo "📋 QUICK START:"
echo "   ai-memory-help              - Show all available commands"
echo "   ai-search \"query\" [type]    - Intelligent memory search"
echo "   ai-context \"query\" [type]   - Get AI conversation context"
echo "   ai-add-smart \"text\"         - Add memory with auto-categorization"
echo "   ai-analytics                - View system analytics"
echo ""
echo "🤖 AI INTEGRATION:"
echo "   For AI responses, use: ai-get-context \"user_query\" [type]"
echo "   This provides rich conversational context with relevance scoring"
echo ""
echo "🔄 TO ACTIVATE IN CURRENT SESSION:"
echo "   source ~/.bashrc"
echo "   # OR simply open a new terminal"
echo ""
echo "💡 QUERY TYPES: preference, technical, project, workflow, learning, general"
echo ""

# Optional: Test a command
if [[ "${1:-}" == "--test" ]]; then
    echo "🧪 Running quick test..."
    ai-analytics
fi

echo "✨ Setup complete! Your memory system is now enhanced and ready to use." 