#!/usr/bin/env python3
"""
Advanced AI Memory Integration for Cursor AI
Implements conversational memory best practices from LangChain and modern AI systems
"""

import sys
import json
import requests
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import re


class AIMemoryIntegration:
    """
    Advanced memory integration following conversational AI best practices.
    Automatically enriches AI responses with relevant memory context.
    """
    
    def __init__(self, api_url: str = "http://localhost:8765/api/v1", user_id: str = "drj"):
        self.api_url = api_url
        self.user_id = user_id
        self.headers = {"Content-Type": "application/json"}
        self.project_context = self._get_project_context()
        
        # Memory categories for better organization
        self.memory_categories = {
            "PREFERENCE": "User preferences and settings",
            "LEARNING": "Technical knowledge and insights",
            "PROJECT": "Project-specific information",
            "WORKFLOW": "Development workflow patterns",
            "SYSTEM": "System configuration and setup",
            "ERROR": "Error patterns and solutions",
            "INSIGHT": "Strategic insights and decisions"
        }

    def _get_project_context(self) -> str:
        """Get current project context"""
        try:
            return os.path.basename(os.getcwd())
        except:
            return "unknown"

    def auto_search_before_response(self, user_query: str, query_type: str = "general") -> Dict[str, Any]:
        """
        Automatically search memories before generating AI responses.
        This is the core function that should be called before any AI response.
        """
        search_results = {
            "relevant_memories": [],
            "context_enrichment": "",
            "memory_summary": "",
            "should_consider": False
        }
        
        # Determine search strategy based on query type
        search_queries = self._generate_search_queries(user_query, query_type)
        
        all_memories = []
        for query in search_queries:
            memories = self._search_memories(query)
            if memories and "items" in memories:
                all_memories.extend(memories["items"])
        
        # Remove duplicates and rank by relevance
        unique_memories = self._deduplicate_and_rank(all_memories, user_query)
        
        if unique_memories:
            search_results["relevant_memories"] = unique_memories[:5]  # Top 5 most relevant
            search_results["context_enrichment"] = self._create_context_enrichment(unique_memories)
            search_results["memory_summary"] = self._create_memory_summary(unique_memories)
            search_results["should_consider"] = True
        
        return search_results

    def _generate_search_queries(self, user_query: str, query_type: str) -> List[str]:
        """Generate multiple search queries to find relevant memories"""
        queries = [user_query]  # Always include the original query
        
        # Extract key terms for additional searches
        key_terms = self._extract_key_terms(user_query)
        
        # Add category-specific searches based on query type
        if query_type == "preference":
            queries.extend([
                f"PREFERENCE {term}" for term in key_terms
            ])
        elif query_type == "technical":
            queries.extend([
                f"LEARNING {term}" for term in key_terms[:3]
            ])
        elif query_type == "project":
            queries.extend([
                f"PROJECT {self.project_context}",
                f"{self.project_context} {user_query}"
            ])
        
        # Add general enrichment queries
        queries.extend([
            f"WORKFLOW {term}" for term in key_terms[:2]
        ])
        
        return list(set(queries))  # Remove duplicates

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from user query for enhanced searching"""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'how', 'what', 'when', 'where', 'why', 'this', 'that', 'with', 'have', 'will', 'was', 'been'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        return meaningful_words[:5]  # Return top 5 meaningful terms

    def _search_memories(self, query: str) -> Dict[str, Any]:
        """Search memories using the API"""
        endpoint = f"{self.api_url}/memories/filter"
        data = {"query": query, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _deduplicate_and_rank(self, memories: List[Dict], user_query: str) -> List[Dict]:
        """Remove duplicates and rank memories by relevance"""
        seen_content = set()
        unique_memories = []
        
        for memory in memories:
            content = memory.get("content", "")
            if content not in seen_content:
                seen_content.add(content)
                # Add relevance score based on keyword matching
                memory["relevance_score"] = self._calculate_relevance(content, user_query)
                unique_memories.append(memory)
        
        # Sort by relevance score
        return sorted(unique_memories, key=lambda x: x.get("relevance_score", 0), reverse=True)

    def _calculate_relevance(self, memory_content: str, user_query: str) -> float:
        """Calculate relevance score between memory and query"""
        query_terms = set(self._extract_key_terms(user_query))
        memory_terms = set(self._extract_key_terms(memory_content))
        
        if not query_terms:
            return 0.0
        
        # Jaccard similarity
        intersection = query_terms.intersection(memory_terms)
        union = query_terms.union(memory_terms)
        
        return len(intersection) / len(union) if union else 0.0

    def _create_context_enrichment(self, memories: List[Dict]) -> str:
        """Create context enrichment text for AI responses"""
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories[:3]:  # Use top 3 memories
            content = memory.get("content", "")
            if content:
                # Extract category if present
                category = self._extract_category(content)
                if category:
                    context_parts.append(f"[{category}] {content}")
                else:
                    context_parts.append(content)
        
        return "Relevant context from your previous interactions:\n" + "\n".join(f"• {part}" for part in context_parts)

    def _create_memory_summary(self, memories: List[Dict]) -> str:
        """Create a summary of relevant memories"""
        if not memories:
            return "No relevant previous context found."
        
        categories = Counter()
        for memory in memories:
            category = self._extract_category(memory.get("content", ""))
            if category:
                categories[category] += 1
        
        summary_parts = [f"Found {len(memories)} relevant memories"]
        if categories:
            top_categories = categories.most_common(3)
            category_str = ", ".join([f"{cat}({count})" for cat, count in top_categories])
            summary_parts.append(f"Categories: {category_str}")
        
        return " | ".join(summary_parts)

    def _extract_category(self, content: str) -> Optional[str]:
        """Extract category from memory content"""
        match = re.match(r'\[([A-Z]+)\]', content)
        return match.group(1) if match else None

    def enhanced_add_memory(self, text: str, category: str = None, auto_categorize: bool = True) -> Dict[str, Any]:
        """Add memory with enhanced categorization and context"""
        # Auto-categorize if not provided
        if not category and auto_categorize:
            category = self._auto_categorize(text)
        
        # Add category tag
        if category and category.upper() in self.memory_categories:
            formatted_text = f"[{category.upper()}] {text}"
        else:
            formatted_text = text
        
        # Add project context for project-related memories
        if category == "PROJECT" or self._is_project_related(text):
            formatted_text = f"[PROJECT:{self.project_context}] {formatted_text}"
        
        endpoint = f"{self.api_url}/memories/"
        data = {"text": formatted_text, "user_id": self.user_id}
        
        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def _auto_categorize(self, text: str) -> Optional[str]:
        """Automatically categorize memory based on content"""
        text_lower = text.lower()
        
        # Preference indicators
        if any(word in text_lower for word in ["prefer", "like", "hate", "always", "never", "setting", "config"]):
            return "PREFERENCE"
        
        # Learning indicators
        elif any(word in text_lower for word in ["learned", "discovered", "found", "technique", "method", "solution"]):
            return "LEARNING"
        
        # Workflow indicators
        elif any(word in text_lower for word in ["workflow", "process", "step", "command", "script", "automation"]):
            return "WORKFLOW"
        
        # System indicators
        elif any(word in text_lower for word in ["install", "setup", "configure", "system", "environment"]):
            return "SYSTEM"
        
        # Error indicators
        elif any(word in text_lower for word in ["error", "bug", "issue", "problem", "fix", "resolve"]):
            return "ERROR"
        
        return None

    def _is_project_related(self, text: str) -> bool:
        """Check if memory is project-related"""
        return self.project_context.lower() in text.lower()

    def get_conversational_context(self, user_query: str, query_type: str = "general") -> str:
        """
        Get conversational context for AI responses - main integration point.
        This should be called before generating any AI response.
        """
        memory_results = self.auto_search_before_response(user_query, query_type)
        
        if memory_results["should_consider"]:
            return f"""
MEMORY CONTEXT FOR AI RESPONSE:
{memory_results['context_enrichment']}

Memory Summary: {memory_results['memory_summary']}

INSTRUCTIONS: Use this context to provide more personalized and informed responses. Reference relevant memories when appropriate.
"""
        else:
            return ""

    def demonstrate_proper_usage(self):
        """Demonstrate how the AI should be using this system"""
        examples = [
            {
                "user_query": "What programming languages do I prefer?",
                "query_type": "preference",
                "expected_behavior": "Search for PREFERENCE memories about programming languages before responding"
            },
            {
                "user_query": "How should I set up a new project?",
                "query_type": "workflow", 
                "expected_behavior": "Search for WORKFLOW and PROJECT memories about setup processes"
            },
            {
                "user_query": "What did we discuss about dashboards?",
                "query_type": "project",
                "expected_behavior": "Search current project context and dashboard-related memories"
            }
        ]
        
        print("🤖 AI Memory Integration - Proper Usage Examples")
        print("=" * 60)
        
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. User Query: '{example['user_query']}'")
            print(f"   Query Type: {example['query_type']}")
            print(f"   Expected AI Behavior: {example['expected_behavior']}")
            
            # Demonstrate actual search
            context = self.get_conversational_context(example['user_query'], example['query_type'])
            if context:
                print("   ✅ Found relevant context:")
                print("   " + "\n   ".join(context.split("\n")[:3]))
            else:
                print("   ❌ No relevant context found")


def main():
    """Enhanced main function with AI integration commands"""
    if len(sys.argv) < 2:
        print("🧠 Advanced AI Memory Integration")
        print("================================")
        print("Commands:")
        print("  add <text>                    - Add enhanced memory")
        print("  search <query>                - Search with AI context")
        print("  ai-context <query> [type]     - Get AI conversation context") 
        print("  auto-search <query> [type]    - Demonstrate auto-search")
        print("  demo                          - Show proper usage examples")
        print("  categorize <text>             - Add with auto-categorization")
        print("")
        print("Query Types: general, preference, technical, project, workflow")
        sys.exit(1)
    
    ai_memory = AIMemoryIntegration()
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide text to remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = ai_memory.enhanced_add_memory(text)
        
        if result and "error" not in result:
            print(f"✅ Enhanced memory added: {result.get('content', text)}")
        elif result and "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Enhanced memory added successfully: {text}")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        query_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        
        results = ai_memory.auto_search_before_response(query, query_type)
        
        print(f"🔍 AI Memory Search: {query}")
        print(f"📊 {results['memory_summary']}")
        
        if results['should_consider']:
            print("\n📋 Context Enrichment:")
            print(results['context_enrichment'])
        else:
            print("\n📭 No relevant context found")
    
    elif command == "ai-context":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        query_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        
        context = ai_memory.get_conversational_context(query, query_type)
        
        if context:
            print("🤖 AI Conversation Context:")
            print(context)
        else:
            print("📭 No conversation context available")
    
    elif command == "auto-search":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        query_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        
        print(f"🔄 Demonstrating Auto-Search for: '{query}'")
        print(f"Query Type: {query_type}")
        print("-" * 50)
        
        results = ai_memory.auto_search_before_response(query, query_type)
        
        print(f"📊 Search Results: {results['memory_summary']}")
        if results['should_consider']:
            print(f"✅ Should enrich AI response: YES")
            print(f"📝 Context: {len(results['relevant_memories'])} relevant memories found")
        else:
            print(f"❌ Should enrich AI response: NO")
    
    elif command == "demo":
        ai_memory.demonstrate_proper_usage()
    
    elif command == "categorize":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide text to categorize and remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = ai_memory.enhanced_add_memory(text, auto_categorize=True)
        
        if result and "error" not in result:
            print(f"✅ Categorized memory added: {result.get('content', text)}")
        elif result and "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Categorized memory added successfully: {text}")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'add', 'search', 'ai-context', 'auto-search', 'demo', or 'categorize'")
        sys.exit(1)


if __name__ == "__main__":
    main() 