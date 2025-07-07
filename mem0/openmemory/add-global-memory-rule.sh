#!/bin/bash

# Cursor Global Memory Rule Installer
# Automatically adds Mem0 OpenMemory integration to Cursor User Rules

set -e

RULE_FILE="/tmp/cursor-memory-rule.txt"

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

echo "🎯 TO ADD TO CURSOR:"
echo "===================="
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
echo "cat $RULE_FILE | xclip -selection clipboard 2>/dev/null || cat $RULE_FILE"
echo ""

echo "✨ BENEFITS:"
echo "============"
echo "• Global rules apply to ALL Cursor projects"
echo "• No more context bloat from nested rulesets"
echo "• Persistent memory across all development sessions"
echo "• Superior to project-specific .cursorrules files"
echo ""

exit 0
