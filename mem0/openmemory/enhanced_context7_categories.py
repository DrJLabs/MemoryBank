#!/usr/bin/env python3
"""
Enhanced Memory Categories for Context7 Integration
==================================================

Extends the existing memory system with Context7-specific categories
and intelligent categorization patterns.

Author: Memory-Enhanced Developer Agent
"""

import sys
from pathlib import Path

# Add scripts directory to path for memory system imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from advanced_memory_ai import AdvancedAIMemory
    from ai_memory_integration import AIMemoryIntegration
except ImportError:
    print("Warning: Advanced memory system not available")
    AdvancedAIMemory = None
    AIMemoryIntegration = None

class Context7MemoryCategories:
    """Enhanced memory categories for Context7 integration"""
    
    # New Context7-specific categories
    CONTEXT7_CATEGORIES = {
        'CONTEXT7_DOCS': {
            'description': 'Documentation from Context7 library lookups',
            'patterns': ['Context7 docs:', 'library documentation', 'API reference'],
            'priority': 'high'
        },
        'CONTEXT7_PATTERNS': {
            'description': 'Successful Context7 integration patterns',
            'patterns': ['CONTEXT7_PATTERN:', 'integration pattern', 'import pattern'],
            'priority': 'high'
        },
        'CONTEXT7_LIBS': {
            'description': 'Library-specific learnings and configurations',
            'patterns': ['CONTEXT7_RESOLUTION:', 'library_id:', 'library resolution'],
            'priority': 'medium'
        },
        'API_INTEGRATION': {
            'description': 'Context7 API usage patterns and optimizations',
            'patterns': ['CONTEXT7_SUCCESS:', 'API integration', 'MCP tool'],
            'priority': 'medium'
        }
    }
    
    # Enhanced categorization patterns
    ENHANCED_PATTERNS = {
        'CONTEXT7_DOCS': [
            'Context7 documentation',
            'library docs',
            'API reference',
            'documentation from Context7',
            'get-library-docs',
            'MCP documentation'
        ],
        'CONTEXT7_PATTERNS': [
            'Context7 pattern',
            'integration pattern',
            'import pattern',
            'NPM_INSTALL:',
            'PIP_INSTALL:',
            'IMPORT_PATTERN:',
            'CONFIG_PATTERN:',
            'API_USAGE:'
        ],
        'CONTEXT7_LIBS': [
            'Context7 resolution',
            'library resolution',
            'library_id:',
            'resolve-library-id',
            'library mapping'
        ],
        'API_INTEGRATION': [
            'Context7 success',
            'Context7 integration',
            'MCP integration',
            'API usage pattern',
            'integration approach'
        ]
    }
    
    @classmethod
    def add_context7_categories(cls, memory_system):
        """Add Context7 categories to memory system if supported"""
        if not memory_system:
            return False
            
        try:
            # Check if memory system supports category management
            if hasattr(memory_system, 'add_category'):
                for category, config in cls.CONTEXT7_CATEGORIES.items():
                    memory_system.add_category(
                        name=category,
                        description=config['description'],
                        patterns=config['patterns']
                    )
                print("✅ Context7 categories added to memory system")
                return True
            else:
                print("ℹ️  Memory system doesn't support dynamic categories")
                return False
        except Exception as e:
            print(f"⚠️  Failed to add Context7 categories: {e}")
            return False
    
    @classmethod
    def categorize_context7_content(cls, content: str) -> str:
        """Intelligent categorization for Context7-related content"""
        content_lower = content.lower()
        
        # Check each category's patterns
        for category, patterns in cls.ENHANCED_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    return category
        
        # Fallback to existing categorization logic
        if any(word in content_lower for word in ['documentation', 'docs', 'api reference']):
            return 'CONTEXT7_DOCS'
        elif any(word in content_lower for word in ['pattern', 'integration', 'approach']):
            return 'CONTEXT7_PATTERNS'
        elif any(word in content_lower for word in ['library', 'resolution', 'library_id']):
            return 'CONTEXT7_LIBS'
        else:
            return 'TECHNICAL'  # Default fallback
    
    @classmethod
    def get_category_stats(cls, memory_system) -> dict:
        """Get statistics for Context7 categories"""
        stats = {}
        
        if not memory_system:
            return stats
            
        try:
            for category in cls.CONTEXT7_CATEGORIES.keys():
                if hasattr(memory_system, 'count_memories_by_category'):
                    count = memory_system.count_memories_by_category(category)
                    stats[category] = count
                else:
                    # Fallback: search for category-specific content
                    if hasattr(memory_system, 'search_memories'):
                        results = memory_system.search_memories(f"category:{category}")
                        stats[category] = len(results) if results else 0
                    else:
                        stats[category] = 0
        except Exception as e:
            print(f"Warning: Could not get category stats: {e}")
            
        return stats

def setup_context7_memory_categories():
    """Setup Context7 memory categories in the system"""
    print("🧠 Setting up Context7 Memory Categories...")
    
    # Initialize memory system
    memory_system = None
    if AdvancedAIMemory:
        try:
            memory_system = AdvancedAIMemory()
            print("✅ Advanced Memory System loaded")
        except Exception as e:
            print(f"⚠️  Advanced Memory System failed: {e}")
    
    if not memory_system and AIMemoryIntegration:
        try:
            memory_system = AIMemoryIntegration()
            print("✅ AI Memory Integration loaded")
        except Exception as e:
            print(f"⚠️  AI Memory Integration failed: {e}")
    
    if not memory_system:
        print("❌ No memory system available")
        return False
    
    # Add Context7 categories
    success = Context7MemoryCategories.add_context7_categories(memory_system)
    
    if success:
        # Show category statistics
        stats = Context7MemoryCategories.get_category_stats(memory_system)
        print("\n📊 Context7 Category Statistics:")
        for category, count in stats.items():
            print(f"  {category}: {count} memories")
    
    return success

def test_context7_categorization():
    """Test Context7 content categorization"""
    print("\n🧪 Testing Context7 Categorization...")
    
    test_cases = [
        ("CONTEXT7_DOCS: /facebook/react documentation from Context7", "CONTEXT7_DOCS"),
        ("CONTEXT7_PATTERN: NPM_INSTALL: react", "CONTEXT7_PATTERNS"),
        ("CONTEXT7_RESOLUTION: react -> library_id: /facebook/react", "CONTEXT7_LIBS"),
        ("CONTEXT7_SUCCESS: FastAPI integration successful", "API_INTEGRATION"),
        ("General technical content", "TECHNICAL")
    ]
    
    for content, expected in test_cases:
        result = Context7MemoryCategories.categorize_context7_content(content)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{content[:50]}...' -> {result}")

if __name__ == "__main__":
    # Setup categories
    success = setup_context7_memory_categories()
    
    # Test categorization
    test_context7_categorization()
    
    if success:
        print("\n🚀 Context7 memory integration ready!")
    else:
        print("\n⚠️  Context7 integration setup incomplete") 