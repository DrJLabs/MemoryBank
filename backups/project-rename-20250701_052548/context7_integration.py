#!/usr/bin/env python3
"""
Context7 Integration with Memory-C* System
==========================================

Memory-enhanced Context7 integration that stores documentation lookups
and builds reusable patterns for technical development.

Author: Memory-Enhanced Developer Agent
Integration: Context7 MCP + Memory-C* Storage
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Optional httpx import for async HTTP requests
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available, using simulation mode")

# Import memory system components
try:
    from advanced_memory_ai import AdvancedAIMemory
    from ai_memory_integration import AIMemoryIntegration
except ImportError:
    # Fallback if advanced memory not available
    AdvancedAIMemory = None
    AIMemoryIntegration = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Context7Config:
    """Configuration for Context7 integration"""
    memory_storage: bool = True
    confidence_threshold: float = 0.7
    auto_categorize: bool = True
    store_patterns: bool = True
    memory_api_url: str = "http://localhost:8765"

@dataclass
class Context7Result:
    """Result from Context7 operation with memory integration"""
    success: bool
    library_id: str
    documentation: str
    memory_stored: bool = False
    memory_id: Optional[str] = None
    patterns_extracted: List[str] = None
    confidence: float = 0.0
    error: Optional[str] = None

class Context7MemoryIntegration:
    """
    Memory-enhanced Context7 integration service.
    
    Provides Context7 MCP tool functionality with intelligent memory storage,
    pattern recognition, and reusable documentation caching.
    """
    
    def __init__(self, config: Context7Config = None):
        self.config = config or Context7Config()
        self.memory_system = self._initialize_memory_system()
        
        # Initialize HTTP client if available
        if HTTPX_AVAILABLE:
            self.session = httpx.AsyncClient(timeout=30.0)
        else:
            self.session = None
            logger.warning("httpx not available, running in simulation mode")
        
        # Enhanced memory categories for Context7
        self.memory_categories = {
            'CONTEXT7_DOCS': 'Documentation from Context7 library lookups',
            'CONTEXT7_PATTERNS': 'Successful Context7 integration patterns',
            'CONTEXT7_LIBS': 'Library-specific learnings and configurations',
            'API_INTEGRATION': 'Context7 API usage patterns and optimizations'
        }
        
        logger.info("Context7 Memory Integration initialized")
    
    def _initialize_memory_system(self) -> Optional[Any]:
        """Initialize memory system with fallback handling"""
        try:
            if AdvancedAIMemory:
                return AdvancedAIMemory()
            elif AIMemoryIntegration:
                return AIMemoryIntegration()
            else:
                logger.warning("Advanced memory system not available, using basic storage")
                return None
        except Exception as e:
            logger.error(f"Memory system initialization failed: {e}")
            return None
    
    async def resolve_library_id(self, library_name: str) -> Tuple[bool, str, str]:
        """
        Resolve library name to Context7-compatible library ID.
        
        Memory-enhanced: Checks memory first for cached resolutions.
        """
        try:
            # Check memory first for cached library ID resolution
            cached_result = await self._check_memory_for_library(library_name)
            if cached_result:
                logger.info(f"Found cached library ID for {library_name}")
                return True, cached_result['library_id'], f"Cached: {cached_result['source']}"
            
            # Use Context7 MCP tool to resolve library ID
            # Note: This would call the actual Context7 MCP resolve-library-id tool
            # For now, implementing a simulation
            library_id = await self._call_context7_resolve(library_name)
            
            if library_id:
                # Store successful resolution in memory
                await self._store_library_resolution(library_name, library_id)
                return True, library_id, "Resolved via Context7 MCP"
            else:
                return False, "", f"Library '{library_name}' not found in Context7"
                
        except Exception as e:
            logger.error(f"Library ID resolution failed: {e}")
            return False, "", str(e)
    
    async def get_library_docs(self, library_id: str, topic: str = None, 
                             tokens: int = 10000) -> Context7Result:
        """
        Get library documentation with memory-enhanced caching and pattern storage.
        
        Memory Integration:
        1. Check memory for cached documentation
        2. Use Context7 if not cached or outdated  
        3. Store new documentation with patterns
        4. Extract and store reusable patterns
        """
        try:
            # Check memory for cached documentation
            cached_docs = await self._check_memory_for_docs(library_id, topic)
            if cached_docs and self._is_cache_fresh(cached_docs):
                logger.info(f"Using cached documentation for {library_id}")
                return Context7Result(
                    success=True,
                    library_id=library_id,
                    documentation=cached_docs['content'],
                    memory_stored=True,
                    memory_id=cached_docs.get('memory_id'),
                    confidence=cached_docs.get('confidence', 0.8)
                )
            
            # Fetch fresh documentation from Context7
            docs_content = await self._call_context7_get_docs(library_id, topic, tokens)
            
            if not docs_content:
                return Context7Result(
                    success=False,
                    library_id=library_id,
                    documentation="",
                    error="Failed to fetch documentation from Context7"
                )
            
            # Extract patterns and insights
            patterns = self._extract_patterns(docs_content, library_id)
            
            # Store in memory with enhanced categorization
            memory_id = await self._store_documentation_memory(
                library_id, docs_content, topic, patterns
            )
            
            return Context7Result(
                success=True,
                library_id=library_id,
                documentation=docs_content,
                memory_stored=True,
                memory_id=memory_id,
                patterns_extracted=patterns,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Documentation retrieval failed: {e}")
            return Context7Result(
                success=False,
                library_id=library_id,
                documentation="",
                error=str(e)
            )
    
    async def _call_context7_resolve(self, library_name: str) -> Optional[str]:
        """Call Context7 MCP resolve-library-id tool (simulation)"""
        # TODO: Replace with actual Context7 MCP tool call
        # This would use the MCP client to call resolve-library-id
        
        # Simulation based on common patterns
        common_libraries = {
            'react': '/facebook/react',
            'next': '/vercel/next.js',
            'nextjs': '/vercel/next.js',
            'next.js': '/vercel/next.js',
            'supabase': '/supabase/supabase',
            'mongodb': '/mongodb/docs',
            'fastapi': '/tiangolo/fastapi',
            'django': '/django/django',
            'flask': '/pallets/flask',
            'typescript': '/microsoft/typescript'
        }
        
        library_key = library_name.lower().replace('-', '').replace('_', '')
        return common_libraries.get(library_key)
    
    async def _call_context7_get_docs(self, library_id: str, topic: str = None, 
                                    tokens: int = 10000) -> Optional[str]:
        """Call Context7 MCP get-library-docs tool (simulation)"""
        # TODO: Replace with actual Context7 MCP tool call
        # This would use the MCP client to call get-library-docs
        
        # Simulation returning structured documentation
        return f"""
# {library_id} Documentation

## Overview
This library provides comprehensive functionality for modern web development.

## Installation
```bash
npm install {library_id.split('/')[-1]}
```

## Basic Usage
```javascript
import {{ createApp }} from '{library_id.split('/')[-1]}';

const app = createApp({{
  // configuration
}});
```

## API Reference
- Core functions and components
- Configuration options
- Advanced patterns

## Best Practices
- Performance optimization
- Security considerations
- Development workflow integration

Topic focus: {topic or 'general'}
Tokens: {tokens}
"""
    
    async def _check_memory_for_library(self, library_name: str) -> Optional[Dict]:
        """Check memory for cached library ID resolution"""
        if not self.memory_system:
            return None
            
        try:
            # Search for cached library resolution
            search_query = f"library resolution {library_name} Context7"
            
            if hasattr(self.memory_system, 'intelligent_memory_search'):
                results = self.memory_system.intelligent_memory_search(search_query)
                if results.memories:
                    for memory in results.memories:
                        content = memory.get('content', '')
                        if 'library_id:' in content and library_name in content:
                            # Extract library_id from content
                            lines = content.split('\n')
                            for line in lines:
                                if 'library_id:' in line:
                                    library_id = line.split('library_id:')[1].strip()
                                    return {
                                        'library_id': library_id,
                                        'source': 'memory cache',
                                        'memory_id': memory.get('id')
                                    }
            return None
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return None
    
    async def _check_memory_for_docs(self, library_id: str, topic: str = None) -> Optional[Dict]:
        """Check memory for cached documentation"""
        if not self.memory_system:
            return None
            
        try:
            search_query = f"Context7 documentation {library_id}"
            if topic:
                search_query += f" {topic}"
                
            if hasattr(self.memory_system, 'intelligent_memory_search'):
                results = self.memory_system.intelligent_memory_search(search_query)
                if results.memories:
                    for memory in results.memories:
                        content = memory.get('content', '')
                        if library_id in content and 'Context7 docs:' in content:
                            return {
                                'content': content,
                                'memory_id': memory.get('id'),
                                'confidence': results.relevance_scores.get(memory['id'], 0.0),
                                'timestamp': memory.get('created_at', 0)
                            }
            return None
        except Exception as e:
            logger.warning(f"Memory docs check failed: {e}")
            return None
    
    def _is_cache_fresh(self, cached_data: Dict) -> bool:
        """Check if cached documentation is still fresh (24 hours)"""
        try:
            cache_time = cached_data.get('timestamp', 0)
            current_time = datetime.now().timestamp()
            age_hours = (current_time - cache_time) / 3600
            return age_hours < 24  # Fresh for 24 hours
        except:
            return False
    
    def _extract_patterns(self, content: str, library_id: str) -> List[str]:
        """Extract reusable patterns from documentation"""
        patterns = []
        
        # Extract installation patterns
        if 'npm install' in content:
            patterns.append(f"NPM_INSTALL: {library_id}")
        if 'pip install' in content:
            patterns.append(f"PIP_INSTALL: {library_id}")
        
        # Extract import patterns
        import_lines = [line.strip() for line in content.split('\n') 
                       if 'import' in line and ('from' in line or 'require' in line)]
        for import_line in import_lines[:3]:  # Limit to first 3 imports
            patterns.append(f"IMPORT_PATTERN: {import_line}")
        
        # Extract configuration patterns
        if 'createApp' in content or 'configure' in content:
            patterns.append(f"CONFIG_PATTERN: {library_id}")
        
        # Extract API patterns
        if 'API Reference' in content or 'methods' in content.lower():
            patterns.append(f"API_USAGE: {library_id}")
        
        return patterns
    
    async def _store_library_resolution(self, library_name: str, library_id: str):
        """Store successful library resolution in memory"""
        if not self.memory_system:
            return
            
        try:
            content = f"CONTEXT7_RESOLUTION: {library_name} -> library_id: {library_id}"
            
            if hasattr(self.memory_system, 'add_memory'):
                await self.memory_system.add_memory(
                    content=content,
                    category='CONTEXT7_LIBS'
                )
            logger.info(f"Stored library resolution: {library_name} -> {library_id}")
        except Exception as e:
            logger.warning(f"Failed to store library resolution: {e}")
    
    async def _store_documentation_memory(self, library_id: str, content: str, 
                                        topic: str = None, patterns: List[str] = None) -> Optional[str]:
        """Store documentation and patterns in memory"""
        if not self.memory_system:
            return None
            
        try:
            # Store main documentation
            memory_content = f"CONTEXT7_DOCS: {library_id}"
            if topic:
                memory_content += f" (topic: {topic})"
            memory_content += f"\n\nContext7 docs:\n{content}"
            
            if patterns:
                memory_content += "\n\nExtracted patterns:\n" + "\n".join(patterns)
            
            memory_id = None
            if hasattr(self.memory_system, 'add_memory'):
                result = await self.memory_system.add_memory(
                    content=memory_content,
                    category='CONTEXT7_DOCS'
                )
                memory_id = result.get('memory_id') if result else None
            
            # Store patterns separately for better searchability
            if patterns:
                for pattern in patterns:
                    pattern_content = f"CONTEXT7_PATTERN: {library_id} - {pattern}"
                    if hasattr(self.memory_system, 'add_memory'):
                        await self.memory_system.add_memory(
                            content=pattern_content,
                            category='CONTEXT7_PATTERNS'
                        )
            
            logger.info(f"Stored Context7 documentation for {library_id}")
            return memory_id
            
        except Exception as e:
            logger.warning(f"Failed to store documentation memory: {e}")
            return None
    
    async def get_memory_enhanced_context(self, query: str, library_context: str = None) -> Dict:
        """
        Get enhanced context combining Context7 docs with stored memory patterns.
        
        This is the main integration point for AI development workflows.
        """
        try:
            context = {
                'context7_docs': None,
                'memory_patterns': [],
                'related_libraries': [],
                'confidence': 0.0
            }
            
            # If library context provided, get fresh docs
            if library_context:
                success, library_id, _ = await self.resolve_library_id(library_context)
                if success:
                    docs_result = await self.get_library_docs(library_id)
                    if docs_result.success:
                        context['context7_docs'] = docs_result.documentation
                        context['confidence'] = docs_result.confidence
            
            # Get relevant memory patterns
            if self.memory_system:
                search_query = f"Context7 patterns {query}"
                if hasattr(self.memory_system, 'intelligent_memory_search'):
                    results = self.memory_system.intelligent_memory_search(search_query)
                    for memory in results.memories[:5]:  # Top 5 relevant memories
                        content = memory.get('content', '')
                        if 'CONTEXT7_PATTERN:' in content:
                            context['memory_patterns'].append(content)
            
            return context
            
        except Exception as e:
            logger.error(f"Enhanced context retrieval failed: {e}")
            return {'error': str(e)}
    
    async def store_integration_success(self, library_id: str, approach: str, 
                                      outcome: str, insights: str):
        """Store successful integration patterns for future reuse"""
        if not self.memory_system:
            return
            
        try:
            content = f"CONTEXT7_SUCCESS: {library_id} integration"
            content += f"\nApproach: {approach}"
            content += f"\nOutcome: {outcome}"
            content += f"\nInsights: {insights}"
            content += f"\nTimestamp: {datetime.now().isoformat()}"
            
            if hasattr(self.memory_system, 'add_memory'):
                await self.memory_system.add_memory(
                    content=content,
                    category='API_INTEGRATION'
                )
            
            logger.info(f"Stored integration success for {library_id}")
        except Exception as e:
            logger.warning(f"Failed to store integration success: {e}")
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.aclose()

# Convenience functions for easy integration
async def resolve_library(library_name: str) -> Tuple[bool, str, str]:
    """Quick library resolution with memory caching"""
    integration = Context7MemoryIntegration()
    try:
        return await integration.resolve_library_id(library_name)
    finally:
        await integration.close()

async def get_docs_with_memory(library_id: str, topic: str = None) -> Context7Result:
    """Quick documentation retrieval with memory storage"""
    integration = Context7MemoryIntegration()
    try:
        return await integration.get_library_docs(library_id, topic)
    finally:
        await integration.close()

async def get_enhanced_context(query: str, library: str = None) -> Dict:
    """Get memory-enhanced context for development tasks"""
    integration = Context7MemoryIntegration()
    try:
        return await integration.get_memory_enhanced_context(query, library)
    finally:
        await integration.close()

if __name__ == "__main__":
    # Demo usage
    async def demo():
        integration = Context7MemoryIntegration()
        
        # Test library resolution
        success, library_id, msg = await integration.resolve_library_id("react")
        print(f"Resolution: {success}, ID: {library_id}, Message: {msg}")
        
        if success:
            # Test documentation retrieval
            result = await integration.get_library_docs(library_id, "hooks")
            print(f"Docs success: {result.success}")
            print(f"Memory stored: {result.memory_stored}")
            print(f"Patterns: {result.patterns_extracted}")
        
        # Test enhanced context
        context = await integration.get_memory_enhanced_context("React hooks usage", "react")
        print(f"Enhanced context: {context}")
        
        await integration.close()
    
    # Run demo
    asyncio.run(demo()) 