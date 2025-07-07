#!/bin/bash

# Cursor Global Memory Rule Installer
# Automatically adds Mem0 OpenMemory integration to Cursor User Rules

set -e

RULE_FILE="/tmp/cursor-memory-rule.txt"
BACKUP_FILE="$HOME/.cursor-memory-rule-backup-$(date +%Y%m%d-%H%M%S).txt"

echo "🤖 Adding Mem0 OpenMemory to Cursor Global User Rules"
echo "================================================="

# Create the comprehensive memory rule
cat > "$RULE_FILE" << 'EOF'
**Memory System Integration (Mem0 OpenMemory)**

I have a persistent memory system running locally. Always use these commands for memory operations:

**Add Memory:**
```bash
python3 /home/drj/*C-System/MemoryBank/mem0/openmemory/cursor-memory-enhanced.py remember "information to store"
```
Or: `mem-add "information to store"`

**Search Memory:**
```bash
python3 /home/drj/*C-System/MemoryBank/mem0/openmemory/cursor-memory-enhanced.py recall "search query"
```
Or: `mem-search "search query"`

**Memory Workflow:**
1. **Always search memories first** when answering questions about my preferences, past conversations, or project history
2. **Add new memories** when I share personal information, preferences, or important context
3. Use semantic search - the system understands context, not just keywords

**System Info:**
- Memory API: http://localhost:8765
- UI Dashboard: http://localhost:3010  
- User ID: "drj"
- Vector database provides intelligent semantic search

**Example Usage:**
Before answering "What programming languages do I prefer?", first run:
`mem-search "programming languages preferences"`

When I say "I prefer TypeScript over JavaScript", run:
`mem-add "Prefers TypeScript over JavaScript for development"`
EOF

echo "✅ Memory rule created at: $RULE_FILE"
echo ""

# Show the rule content
echo "📝 Rule Content:"
echo "=================="
cat "$RULE_FILE"
echo ""
echo "=================="
echo ""

# Method 1: Try to open Cursor Settings directly
echo "🔧 Method 1: Opening Cursor Settings..."
if command -v cursor >/dev/null 2>&1; then
    echo "📖 Instructions for adding the rule:"
    echo "1. Cursor Settings will open automatically"
    echo "2. Navigate to: Settings > Rules > User Rules"
    echo "3. Copy the rule from: $RULE_FILE"
    echo "4. Paste it into the User Rules text area"
    echo "5. Click Save"
    echo ""
    
    # Try to open Cursor settings
    cursor --command workbench.action.openSettings2 2>/dev/null &
    sleep 2
else
    echo "❌ Cursor command not found in PATH"
fi

# Method 2: Create a manual instruction file
INSTRUCTION_FILE="$HOME/cursor-memory-rule-instructions.md"
cat > "$INSTRUCTION_FILE" << EOF
# Adding Mem0 Memory System to Cursor Global User Rules

## Steps:
1. Open Cursor
2. Go to: **Cursor Settings > Rules > User Rules**
3. Copy the content from: \`$RULE_FILE\`
4. Paste it into the User Rules text area
5. Click **Save**

## Rule File Location:
\`$RULE_FILE\`

## What this does:
- Integrates our local Mem0 OpenMemory system with Cursor AI
- Provides global commands for memory operations across all projects
- Enables persistent context and preferences across sessions
- Superior to project-specific .cursorrules files (avoids context bloat)

## Commands Available After Setup:
- \`mem-add "information"\` - Store new memories
- \`mem-search "query"\` - Search existing memories  
- \`mem-analytics\` - View memory statistics
- Plus 8 more enhanced memory commands

Generated: $(date)
EOF

echo "📋 Created instruction file: $INSTRUCTION_FILE"
echo ""

# Method 3: Try to find and modify Cursor user rules directly
echo "🔍 Method 3: Searching for existing Cursor rules storage..."

# Look for common rule storage locations
POSSIBLE_LOCATIONS=(
    "$HOME/.config/Cursor/User/globalStorage/cursor-rules"
    "$HOME/.config/Cursor/User/rules"
    "$HOME/.cursor/user-rules"
    "$HOME/.cursor/rules/user"
    "$HOME/.config/Cursor/rules"
)

FOUND_LOCATION=""
for location in "${POSSIBLE_LOCATIONS[@]}"; do
    if [[ -d "$location" ]] || [[ -f "$location" ]]; then
        FOUND_LOCATION="$location"
        echo "📁 Found potential rules location: $location"
        break
    fi
done

if [[ -z "$FOUND_LOCATION" ]]; then
    echo "❓ Could not locate Cursor user rules storage"
    echo "   Manual addition through UI is recommended"
else
    echo "✅ Potential rules location found: $FOUND_LOCATION"
    # Note: We don't automatically modify this as the format is uncertain
fi

echo ""
echo "🎯 RECOMMENDED APPROACH:"
echo "========================"
echo "1. Open Cursor"
echo "2. Press Ctrl+, (or Cmd+, on Mac) to open Settings"
echo "3. Search for 'Rules' in the settings search"
echo "4. Click on 'Rules' in the left sidebar"
echo "5. Scroll to 'User Rules' section"
echo "6. Copy content from: $RULE_FILE"
echo "7. Paste into the User Rules text area"
echo "8. Click Save"
echo ""

# Create quick copy command
echo "📋 Quick copy command:"
echo "cat $RULE_FILE | xclip -selection clipboard"
echo "(Run this to copy the rule to clipboard)"
echo ""

# Final summary
echo "✨ SUMMARY:"
echo "==========="
echo "• Memory rule created: $RULE_FILE"
echo "• Instructions saved: $INSTRUCTION_FILE"
echo "• This replaces project-specific .cursorrules files"
echo "• Global rules apply to ALL Cursor projects"
echo "• No more context bloat from nested rulesets"
echo "• Persistent memory across all development sessions"
echo ""

echo "🚀 Next Steps:"
echo "1. Follow instructions above to add to Cursor User Rules"
echo "2. Test with: mem-search \"test query\""
  echo "3. Verify memory system integration works globally"
  echo ""

exit 0 