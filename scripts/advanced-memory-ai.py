#!/usr/bin/env python3
"""
Advanced AI Memory Integration System
Enterprise-grade conversational memory following LangChain best practices
Utilizes full OpenMemory API capabilities: pagination, filtering, categories, apps, states, analytics
"""

import sys
import requests
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re
from dataclasses import dataclass
from enum import Enum


class MemoryState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DELETED = "deleted"


class QueryType(Enum):
    PREFERENCE = "preference"
    TECHNICAL = "technical"
    PROJECT = "project"
    WORKFLOW = "workflow"
    GENERAL = "general"
    LEARNING = "learning"


@dataclass
class MemorySearchResult:
    memories: List[Dict[str, Any]]
    total: int
    relevance_scores: Dict[str, float]
    categories: List[str]
    related_memories: Dict[str, List[Dict]]
    search_strategy: str
    confidence: float


class AdvancedAIMemory:
    """
    Enterprise-grade AI Memory Integration with full API utilization.
    Implements conversational memory best practices from LangChain and modern AI systems.
    """
    
    def __init__(self, api_url: str = "http://localhost:8765/api/v1", user_id: str = "drj"):
        self.api_url = api_url
        self.user_id = user_id
        self.headers = {"Content-Type": "application/json"}
        self.project_context = self._get_project_context()
        
        # Advanced categorization system
        self.category_mapping = {
            "PREFERENCE": ["prefer", "like", "dislike", "always", "never", "setting", "config", "choice"],
            "TECHNICAL": ["code", "programming", "development", "framework", "language", "library", "technology"],
            "WORKFLOW": ["process", "step", "command", "script", "automation", "procedure", "method"],
            "PROJECT": ["project", "task", "feature", "requirement", "milestone", "deliverable"],
            "LEARNING": ["learned", "discovered", "found", "technique", "insight", "knowledge", "understanding"],
            "SYSTEM": ["install", "setup", "configure", "system", "environment", "infrastructure"],
            "ERROR": ["error", "bug", "issue", "problem", "fix", "resolve", "troubleshoot"],
            "INSIGHT": ["strategy", "decision", "approach", "pattern", "best practice", "recommendation"]
        }
        
        # Initialize system state
        self._load_system_statistics()

    def _get_project_context(self) -> str:
        """Get current project context"""
        try:
            return os.path.basename(os.getcwd())
        except:
            return "unknown"

    def _load_system_statistics(self) -> Dict[str, Any]:
        """Load comprehensive system statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats/", params={"user_id": self.user_id})
            response.raise_for_status()
            self.system_stats = response.json()
            return self.system_stats
        except Exception as e:
            self.system_stats = {"error": str(e)}
            return self.system_stats

    def intelligent_memory_search(self, user_query: str, query_type: QueryType = QueryType.GENERAL, 
                                max_results: int = 20) -> MemorySearchResult:
        """
        Intelligent multi-strategy memory search using all API capabilities.
        Implements ConversationSummaryBufferMemory patterns with semantic search.
        """
        
        # Strategy 1: Semantic search with query expansion
        search_queries = self._generate_intelligent_queries(user_query, query_type)
        
        all_memories = []
        search_strategies = []
        
        for strategy, query in search_queries:
            try:
                # Use advanced filter endpoint with all parameters
                filter_request = {
                    "user_id": self.user_id,
                    "search_query": query,
                    "page": 1,
                    "size": max_results,
                    "sort_column": "created_at",
                    "sort_direction": "desc",
                    "show_archived": False
                }
                
                response = requests.post(f"{self.api_url}/memories/filter", 
                                       json=filter_request, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if data.get("items"):
                    all_memories.extend(data["items"])
                    search_strategies.append(f"{strategy}({len(data['items'])})")
                    
            except Exception:
                search_strategies.append(f"{strategy}(error)")
        
        # Strategy 2: Get related memories for relevant results
        related_memories = {}
        unique_memories = self._deduplicate_memories(all_memories)
        
        for memory in unique_memories[:5]:  # Get related for top 5
            try:
                response = requests.get(f"{self.api_url}/memories/{memory['id']}/related",
                                      params={"user_id": self.user_id})
                if response.status_code == 200:
                    related_data = response.json()
                    if related_data.get("items"):
                        related_memories[memory['id']] = related_data["items"]
            except:
                pass
        
        # Strategy 3: Calculate sophisticated relevance scores
        relevance_scores = self._calculate_advanced_relevance(unique_memories, user_query, query_type)
        
        # Strategy 4: Extract and organize categories
        categories = self._extract_memory_categories(unique_memories)
        
        # Strategy 5: Calculate search confidence
        confidence = self._calculate_search_confidence(unique_memories, user_query, search_strategies)
        
        # Log access for relevant memories
        self._log_memory_access(unique_memories[:10])
        
        return MemorySearchResult(
            memories=unique_memories[:max_results],
            total=len(unique_memories),
            relevance_scores=relevance_scores,
            categories=categories,
            related_memories=related_memories,
            search_strategy=" + ".join(search_strategies),
            confidence=confidence
        )

    def _generate_intelligent_queries(self, user_query: str, query_type: QueryType) -> List[Tuple[str, str]]:
        """Generate multiple intelligent search queries using different strategies"""
        queries = []
        
        # Base query
        queries.append(("direct", user_query))
        
        # Extract key terms
        key_terms = self._extract_semantic_terms(user_query)
        
        # Query type specific strategies
        if query_type == QueryType.PREFERENCE:
            queries.extend([
                ("preference", f"prefer {term}") for term in key_terms[:3]
            ])
            queries.append(("preference_pattern", f"like {user_query}"))
            
        elif query_type == QueryType.TECHNICAL:
            queries.extend([
                ("technical", f"programming {term}") for term in key_terms[:2]
            ])
            queries.append(("learning", f"learned {user_query}"))
            
        elif query_type == QueryType.PROJECT:
            queries.append(("project_context", f"{self.project_context} {user_query}"))
            queries.append(("project_generic", f"project {user_query}"))
            
        elif query_type == QueryType.WORKFLOW:
            queries.extend([
                ("workflow", f"command {term}") for term in key_terms[:2]
            ])
            queries.append(("process", f"how to {user_query}"))
        
        # Context-aware queries
        queries.extend([
            ("semantic", f"{term}") for term in key_terms[:3]
        ])
        
        # Temporal queries for recent relevant information
        queries.append(("recent", f"recent {user_query}"))
        
        return queries

    def _extract_semantic_terms(self, text: str) -> List[str]:
        """Extract semantically meaningful terms with improved NLP"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Enhanced stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
            'how', 'what', 'when', 'where', 'why', 'this', 'that', 'with', 
            'have', 'will', 'was', 'been', 'from', 'they', 'she', 'her', 
            'his', 'their', 'said', 'each', 'which', 'would', 'there', 'could'
        }
        
        # Technical terms get higher priority
        technical_terms = {
            'typescript', 'javascript', 'python', 'react', 'node', 'api', 'database',
            'server', 'client', 'framework', 'library', 'code', 'programming',
            'development', 'environment', 'system', 'application', 'software'
        }
        
        meaningful_words = []
        for word in words:
            if word not in stop_words:
                if word in technical_terms:
                    meaningful_words.insert(0, word)  # Prioritize technical terms
                else:
                    meaningful_words.append(word)
        
        return meaningful_words[:7]  # Return top 7 terms

    def _deduplicate_memories(self, memories: List[Dict]) -> List[Dict]:
        """Remove duplicate memories and preserve most relevant"""
        seen_content = set()
        unique_memories = []
        
        for memory in memories:
            content_hash = hash(memory.get("content", ""))
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_memories.append(memory)
        
        return unique_memories

    def _calculate_advanced_relevance(self, memories: List[Dict], query: str, 
                                    query_type: QueryType) -> Dict[str, float]:
        """Calculate sophisticated relevance scores using multiple factors"""
        relevance_scores = {}
        query_terms = set(self._extract_semantic_terms(query))
        
        for memory in memories:
            score = 0.0
            content = memory.get("content", "").lower()
            memory_terms = set(self._extract_semantic_terms(content))
            
            # Semantic similarity (Jaccard coefficient)
            if query_terms and memory_terms:
                intersection = query_terms.intersection(memory_terms)
                union = query_terms.union(memory_terms)
                semantic_score = len(intersection) / len(union) if union else 0
                score += semantic_score * 0.4
            
            # Query type relevance
            type_keywords = self.category_mapping.get(query_type.value.upper(), [])
            type_matches = sum(1 for keyword in type_keywords if keyword in content)
            score += (type_matches / len(type_keywords)) * 0.3 if type_keywords else 0
            
            # Recency factor (newer memories get slight boost)
            created_at = memory.get("created_at", 0)
            days_old = (datetime.now().timestamp() - created_at) / 86400
            recency_score = max(0, 1 - (days_old / 365))  # Decay over year
            score += recency_score * 0.2
            
            # Content length factor (longer, more detailed memories get boost)
            content_length_score = min(1.0, len(content) / 1000)  # Normalize to 1000 chars
            score += content_length_score * 0.1
            
            relevance_scores[memory["id"]] = score
        
        return relevance_scores

    def _extract_memory_categories(self, memories: List[Dict]) -> List[str]:
        """Extract and categorize memories using advanced pattern recognition"""
        categories = Counter()
        
        for memory in memories:
            content = memory.get("content", "").lower()
            memory_categories = memory.get("categories", [])
            
            # Use existing categories
            categories.update(memory_categories)
            
            # Auto-detect categories from content
            for category, keywords in self.category_mapping.items():
                if any(keyword in content for keyword in keywords):
                    categories[category] += 1
        
        return [cat for cat, count in categories.most_common(10)]

    def _calculate_search_confidence(self, memories: List[Dict], query: str, 
                                   strategies: List[str]) -> float:
        """Calculate confidence score for search results"""
        if not memories:
            return 0.0
        
        # Base confidence from number of results
        result_confidence = min(1.0, len(memories) / 10)
        
        # Strategy diversity (more strategies used = higher confidence)
        strategy_confidence = min(1.0, len(strategies) / 4)
        
        # Query specificity (more specific queries get higher confidence)
        query_specificity = min(1.0, len(query.split()) / 5)
        
        # Average relevance of top results
        if hasattr(self, '_last_relevance_scores'):
            avg_relevance = sum(list(self._last_relevance_scores.values())[:5]) / min(5, len(memories))
        else:
            avg_relevance = 0.5
        
        confidence = (result_confidence * 0.3 + strategy_confidence * 0.2 + 
                     query_specificity * 0.2 + avg_relevance * 0.3)
        
        return round(confidence, 3)

    def _log_memory_access(self, memories: List[Dict]) -> None:
        """Log memory access for analytics"""
        for memory in memories:
            try:
                requests.post(f"{self.api_url}/memories/{memory['id']}/access-log",
                            json={"user_id": self.user_id}, headers=self.headers)
            except:
                pass  # Non-critical operation

    def enhanced_add_memory(self, text: str, category: str = None, 
                          metadata: Dict = None, app_name: str = "cursor_ai") -> Dict[str, Any]:
        """Add memory with sophisticated categorization and metadata"""
        
        # Auto-categorize if not provided
        if not category:
            category = self._intelligent_categorization(text)
        
        # Create rich metadata
        enhanced_metadata = {
            "project": self.project_context,
            "timestamp": datetime.now().isoformat(),
            "auto_category": category,
            "query_type": self._detect_query_type(text).value,
            **(metadata or {})
        }
        
        # Format content with category tags
        formatted_text = self._format_memory_content(text, category)
        
        memory_request = {
            "user_id": self.user_id,
            "text": formatted_text,
            "metadata": enhanced_metadata,
            "app": app_name
        }
        
        try:
            response = requests.post(f"{self.api_url}/memories/", 
                                   json=memory_request, headers=self.headers)
            response.raise_for_status()
            
            # Handle the case where API returns null
            result = response.json()
            if result is None:
                return {"success": True, "content": formatted_text, "message": "Memory added successfully (API returned null)"}
            return result
        except Exception as e:
            return {"error": str(e)}

    def _intelligent_categorization(self, text: str) -> str:
        """Intelligent categorization using pattern matching and context"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.category_mapping.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score / len(keywords)
        
        if scores:
            return max(scores.keys(), key=scores.get)
        return "GENERAL"

    def _detect_query_type(self, text: str) -> QueryType:
        """Detect the type of query from content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["prefer", "like", "always", "never"]):
            return QueryType.PREFERENCE
        elif any(word in text_lower for word in ["code", "programming", "development"]):
            return QueryType.TECHNICAL
        elif self.project_context.lower() in text_lower or "project" in text_lower:
            return QueryType.PROJECT
        elif any(word in text_lower for word in ["command", "process", "workflow"]):
            return QueryType.WORKFLOW
        elif any(word in text_lower for word in ["learned", "discovered", "insight"]):
            return QueryType.LEARNING
        else:
            return QueryType.GENERAL

    def _format_memory_content(self, text: str, category: str) -> str:
        """Format memory content with proper categorization"""
        if not text.startswith(f"[{category}]"):
            return f"[{category}] {text}"
        return text

    def get_conversational_context(self, user_query: str, query_type: str = "general", 
                                 detailed: bool = True) -> str:
        """
        Get rich conversational context for AI responses.
        Main integration point for AI systems.
        """
        try:
            query_type_enum = QueryType(query_type.lower())
        except:
            query_type_enum = QueryType.GENERAL
        
        search_result = self.intelligent_memory_search(user_query, query_type_enum)
        
        if not search_result.memories:
            return ""
        
        context_parts = []
        
        # Main context
        context_parts.append("=== RELEVANT MEMORY CONTEXT ===")
        
        for i, memory in enumerate(search_result.memories[:5], 1):
            content = memory.get("content", "")
            relevance = search_result.relevance_scores.get(memory["id"], 0)
            age_days = (datetime.now().timestamp() - memory.get("created_at", 0)) / 86400
            
            if detailed:
                context_parts.append(f"{i}. {content}")
                context_parts.append(f"   📊 Relevance: {relevance:.2f} | Age: {age_days:.0f} days")
            else:
                context_parts.append(f"• {content}")
        
        # Related memories
        if search_result.related_memories and detailed:
            context_parts.append("\n=== RELATED CONTEXT ===")
            for memory_id, related in list(search_result.related_memories.items())[:2]:
                for rel_mem in related[:2]:
                    context_parts.append(f"◦ {rel_mem.get('content', '')}")
        
        # Search metadata
        if detailed:
            context_parts.append(f"\n📈 Search: {search_result.search_strategy}")
            context_parts.append(f"🎯 Confidence: {search_result.confidence}")
            context_parts.append(f"📂 Categories: {', '.join(search_result.categories[:3])}")
        
        context_parts.append("\n=== AI INSTRUCTIONS ===")
        context_parts.append("Use this context to provide personalized, informed responses.")
        context_parts.append("Reference specific memories when relevant.")
        context_parts.append("Consider user preferences and past patterns.")
        
        return "\n".join(context_parts)

    def get_memory_analytics(self) -> Dict[str, Any]:
        """Get comprehensive memory system analytics"""
        analytics = {
            "system_stats": self.system_stats,
            "total_memories": self.system_stats.get("total_memories", 0),
            "apps": len(self.system_stats.get("apps", [])),
            "project_context": self.project_context,
            "categories_available": list(self.category_mapping.keys()),
            "query_types": [qt.value for qt in QueryType]
        }
        
        # Get recent memory activity
        try:
            recent_response = requests.post(f"{self.api_url}/memories/filter",
                                          json={
                                              "user_id": self.user_id,
                                              "page": 1,
                                              "size": 10,
                                              "sort_column": "created_at",
                                              "sort_direction": "desc"
                                          }, headers=self.headers)
            if recent_response.status_code == 200:
                recent_data = recent_response.json()
                analytics["recent_memories"] = len(recent_data.get("items", []))
                analytics["total_pages"] = recent_data.get("pages", 0)
        except:
            pass
        
        return analytics

    def archive_old_memories(self, days_old: int = 365) -> Dict[str, Any]:
        """Archive memories older than specified days"""
        cutoff_timestamp = (datetime.now() - timedelta(days=days_old)).timestamp()
        
        try:
            # Get old memories
            old_memories_response = requests.post(f"{self.api_url}/memories/filter",
                                                json={
                                                    "user_id": self.user_id,
                                                    "to_date": int(cutoff_timestamp),
                                                    "size": 1000
                                                }, headers=self.headers)
            
            if old_memories_response.status_code == 200:
                old_memories = old_memories_response.json().get("items", [])
                memory_ids = [mem["id"] for mem in old_memories]
                
                if memory_ids:
                    # Archive them
                    archive_response = requests.post(f"{self.api_url}/memories/actions/archive",
                                                   json={
                                                       "memory_ids": memory_ids,
                                                       "user_id": self.user_id
                                                   }, headers=self.headers)
                    
                    if archive_response.status_code == 200:
                        return {"archived": len(memory_ids), "status": "success"}
            
            return {"archived": 0, "status": "no_old_memories"}
        except Exception as e:
            return {"error": str(e)}


def main():
    """Advanced main function with sophisticated memory operations"""
    if len(sys.argv) < 2:
        print("🧠 Advanced AI Memory Integration System")
        print("=======================================")
        print("Commands:")
        print("  search <query> [type]         - Intelligent memory search")
        print("  context <query> [type]        - Get AI conversation context") 
        print("  add <text> [category]         - Add enhanced memory")
        print("  analytics                     - System analytics")
        print("  archive-old [days]            - Archive old memories")
        print("  demo                          - Demo advanced features")
        print("")
        print("Query Types: preference, technical, project, workflow, learning, general")
        sys.exit(1)
    
    ai_memory = AdvancedAIMemory()
    command = sys.argv[1].lower()
    
    if command == "search":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a search query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        query_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        
        try:
            query_type_enum = QueryType(query_type.lower())
        except:
            query_type_enum = QueryType.GENERAL
        
        result = ai_memory.intelligent_memory_search(query, query_type_enum)
        
        print(f"🔍 Advanced Search: {query}")
        print(f"📊 Found {result.total} memories | Confidence: {result.confidence}")
        print(f"🎯 Strategy: {result.search_strategy}")
        print(f"📂 Categories: {', '.join(result.categories)}")
        
        if result.memories:
            print("\n📋 Results:")
            for i, memory in enumerate(result.memories[:5], 1):
                relevance = result.relevance_scores.get(memory["id"], 0)
                print(f"{i}. {memory.get('content', '')}")
                print(f"   📊 Relevance: {relevance:.3f}")
        else:
            print("\n📭 No memories found")
    
    elif command == "context":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a query")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        query_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        
        context = ai_memory.get_conversational_context(query, query_type)
        
        if context:
            print("🤖 Advanced AI Context:")
            print(context)
        else:
            print("📭 No conversation context available")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide text to remember")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        category = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = ai_memory.enhanced_add_memory(text, category)
        
        if result and "error" not in result:
            print(f"✅ Advanced memory added: {result}")
        else:
            print(f"❌ Error: {result.get('error') if result else 'Unknown error'}")
    
    elif command == "analytics":
        analytics = ai_memory.get_memory_analytics()
        
        print("📊 Advanced Memory Analytics:")
        print("=" * 40)
        print(f"Total Memories: {analytics['total_memories']}")
        print(f"Apps: {analytics['apps']}")
        print(f"Current Project: {analytics['project_context']}")
        print(f"Available Categories: {', '.join(analytics['categories_available'])}")
        print(f"Query Types: {', '.join(analytics['query_types'])}")
        
        if 'recent_memories' in analytics:
            print(f"Recent Activity: {analytics['recent_memories']} memories")
            print(f"Total Pages: {analytics['total_pages']}")
    
    elif command == "archive-old":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        result = ai_memory.archive_old_memories(days)
        
        if result.get("status") == "success":
            print(f"✅ Archived {result['archived']} memories older than {days} days")
        elif result.get("status") == "no_old_memories":
            print(f"📭 No memories older than {days} days found")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    elif command == "demo":
        print("🚀 Advanced AI Memory Integration Demo")
        print("=" * 50)
        
        # Demo analytics
        analytics = ai_memory.get_memory_analytics()
        print(f"System has {analytics['total_memories']} memories")
        
        # Demo intelligent search
        test_queries = [
            ("programming preferences", "preference"),
            ("dashboard configuration", "technical"),
            ("cursor commands", "workflow")
        ]
        
        for query, qtype in test_queries:
            print(f"\n🔍 Testing: '{query}' (type: {qtype})")
            try:
                result = ai_memory.intelligent_memory_search(query, QueryType(qtype))
                print(f"   📊 Found: {result.total} | Confidence: {result.confidence}")
                print(f"   🎯 Strategy: {result.search_strategy}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'search', 'context', 'add', 'analytics', 'archive-old', or 'demo'")
        sys.exit(1)


if __name__ == "__main__":
    main() 