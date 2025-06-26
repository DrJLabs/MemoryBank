#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Memory-C* AI Memory System
Based on analysis of advanced-memory-ai.py and current AI memory testing best practices
"""

import asyncio
import time
import json
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

# Import your system components
from mem0.openmemory.advanced_memory_ai import AdvancedAIMemory, QueryType


@dataclass
class TestResult:
    test_name: str
    passed: bool
    execution_time: float
    details: Dict[str, Any]
    recommendations: List[str] = None


class MemorySystemTester:
    """
    Comprehensive testing framework for AI memory systems following 
    current best practices from research papers and production systems
    """
    
    def __init__(self, memory_system: AdvancedAIMemory):
        self.memory_system = memory_system
        self.test_results = []
        self.performance_baseline = {}
        
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite covering all aspects of memory functionality"""
        
        test_categories = [
            self.test_memory_storage_retrieval,
            self.test_semantic_search_quality,
            self.test_categorization_accuracy,
            self.test_cursor_integration,
            self.test_performance_benchmarks,
            self.test_memory_coherence,
            self.test_edge_cases,
            self.test_scalability,
            self.test_data_integrity
        ]
        
        print("🧪 Starting Comprehensive Memory System Test Suite")
        print("=" * 60)
        
        for test_category in test_categories:
            try:
                await test_category()
            except Exception as e:
                self.test_results.append(TestResult(
                    test_name=test_category.__name__,
                    passed=False,
                    execution_time=0,
                    details={"error": str(e)}
                ))
        
        return self.generate_test_report()

    async def test_memory_storage_retrieval(self):
        """Test 1: Core Storage and Retrieval Functionality"""
        print("\n📝 Testing Memory Storage & Retrieval...")
        
        test_memories = [
            ("I prefer TypeScript over JavaScript for better type safety", "PREFERENCE"),
            ("Use cursor_enhanced_commands for 60-80% keystroke reduction", "WORKFLOW"), 
            ("Memory-C* project uses enterprise OpenMemory API", "TECHNICAL"),
            ("Daily standup at 9 AM with team in Slack", "PROJECT"),
            ("Learned that HNSW indexing provides sub-10ms query latency", "LEARNING")
        ]
        
        stored_ids = []
        start_time = time.time()
        
        # Test storage
        for content, category in test_memories:
            result = self.memory_system.enhanced_add_memory(
                text=content,
                category=category,
                metadata={"test_type": "storage_test"}
            )
            if "error" not in result:
                stored_ids.append(result)
        
        # Test retrieval
        retrieval_results = []
        for content, expected_category in test_memories:
            query_result = self.memory_system.intelligent_memory_search(
                user_query=content[:20],  # Use partial query
                query_type=QueryType.GENERAL
            )
            retrieval_results.append({
                "query": content[:20],
                "found": len(query_result.memories) > 0,
                "relevance": query_result.confidence,
                "strategy": query_result.search_strategy
            })
        
        execution_time = time.time() - start_time
        success_rate = sum(1 for r in retrieval_results if r["found"]) / len(retrieval_results)
        
        self.test_results.append(TestResult(
            test_name="memory_storage_retrieval",
            passed=success_rate >= 0.8,
            execution_time=execution_time,
            details={
                "stored_memories": len(stored_ids),
                "retrieval_success_rate": success_rate,
                "average_confidence": np.mean([r["relevance"] for r in retrieval_results]),
                "results": retrieval_results
            },
            recommendations=[
                "Ensure storage success rate > 95%",
                "Optimize retrieval for partial queries",
                "Monitor confidence scores consistently"
            ]
        ))

    async def test_semantic_search_quality(self):
        """Test 2: Semantic Search Quality (Based on research best practices)"""
        print("\n🔍 Testing Semantic Search Quality...")
        
        # Test semantic similarity vs exact matching
        semantic_test_cases = [
            {
                "stored": "I like using Python for AI development projects",
                "queries": [
                    ("Python programming", True, 0.7),  # High relevance
                    ("AI development", True, 0.6),      # Medium relevance  
                    ("machine learning coding", True, 0.4),  # Low but relevant
                    ("Java programming", False, 0.2),   # Irrelevant
                ]
            },
            {
                "stored": "Use cursor cmd for enhanced development workflow",
                "queries": [
                    ("cursor commands", True, 0.8),
                    ("development tools", True, 0.5),
                    ("productivity workflow", True, 0.4),
                    ("database queries", False, 0.1),
                ]
            }
        ]
        
        start_time = time.time()
        semantic_scores = []
        
        for test_case in semantic_test_cases:
            # Store the memory
            self.memory_system.enhanced_add_memory(
                text=test_case["stored"],
                category="TEST",
                metadata={"test_type": "semantic_test"}
            )
            
            for query, should_find, min_relevance in test_case["queries"]:
                result = self.memory_system.intelligent_memory_search(
                    user_query=query,
                    query_type=QueryType.GENERAL
                )
                
                found_relevant = any(
                    test_case["stored"].lower() in mem.get("content", "").lower() 
                    for mem in result.memories
                )
                
                semantic_scores.append({
                    "query": query,
                    "expected_found": should_find,
                    "actually_found": found_relevant,
                    "confidence": result.confidence,
                    "min_expected_relevance": min_relevance,
                    "correct": (should_find == found_relevant)
                })
        
        execution_time = time.time() - start_time
        accuracy = sum(1 for s in semantic_scores if s["correct"]) / len(semantic_scores)
        
        self.test_results.append(TestResult(
            test_name="semantic_search_quality", 
            passed=accuracy >= 0.75,
            execution_time=execution_time,
            details={
                "semantic_accuracy": accuracy,
                "test_cases": len(semantic_test_cases),
                "total_queries": len(semantic_scores),
                "scores": semantic_scores
            },
            recommendations=[
                "Improve semantic matching for technical terms",
                "Tune relevance thresholds based on query type",
                "Consider query expansion for better recall"
            ]
        ))

    async def test_cursor_integration(self):
        """Test 3: Cursor Integration Functionality"""
        print("\n🖱️  Testing Cursor Integration...")
        
        # Test conversational context generation
        cursor_test_scenarios = [
            {
                "user_query": "What programming languages do I prefer?",
                "expected_context_keywords": ["typescript", "javascript", "prefer"],
                "query_type": "preference"
            },
            {
                "user_query": "How do I use enhanced commands?", 
                "expected_context_keywords": ["cursor", "command", "workflow"],
                "query_type": "workflow"
            },
            {
                "user_query": "What did I learn about memory systems?",
                "expected_context_keywords": ["memory", "learned", "system"],
                "query_type": "learning"
            }
        ]
        
        start_time = time.time()
        cursor_results = []
        
        for scenario in cursor_test_scenarios:
            # Test conversational context generation
            context = self.memory_system.get_conversational_context(
                user_query=scenario["user_query"],
                query_type=scenario["query_type"], 
                detailed=True
            )
            
            # Analyze context quality
            context_lower = context.lower()
            keyword_matches = sum(
                1 for keyword in scenario["expected_context_keywords"]
                if keyword in context_lower
            )
            
            has_instructions = "=== AI INSTRUCTIONS ===" in context
            has_memory_context = "=== RELEVANT MEMORY CONTEXT ===" in context
            proper_format = has_instructions and has_memory_context
            
            cursor_results.append({
                "query": scenario["user_query"],
                "context_length": len(context),
                "keyword_matches": keyword_matches,
                "total_keywords": len(scenario["expected_context_keywords"]),
                "proper_format": proper_format,
                "has_context": len(context) > 100,
                "context_preview": context[:200] + "..." if len(context) > 200 else context
            })
        
        execution_time = time.time() - start_time
        context_quality = sum(
            1 for r in cursor_results 
            if r["proper_format"] and r["has_context"]
        ) / len(cursor_results)
        
        self.test_results.append(TestResult(
            test_name="cursor_integration",
            passed=context_quality >= 0.8,
            execution_time=execution_time,
            details={
                "context_quality_score": context_quality,
                "scenarios_tested": len(cursor_test_scenarios),
                "results": cursor_results
            },
            recommendations=[
                "Ensure all contexts include AI instructions",
                "Optimize context length for different query types", 
                "Validate context formatting consistency"
            ]
        ))

    async def test_performance_benchmarks(self):
        """Test 4: Performance Benchmarks (Latency, Throughput, Memory Usage)"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Latency tests
        latency_samples = []
        for i in range(50):  # 50 sample queries
            start_time = time.perf_counter()
            
            result = self.memory_system.intelligent_memory_search(
                user_query=f"test query {i}",
                query_type=QueryType.GENERAL,
                max_results=10
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latency_samples.append(latency_ms)
        
        # Throughput test
        throughput_start = time.time()
        concurrent_queries = 20
        tasks = []
        
        for i in range(concurrent_queries):
            task = asyncio.create_task(self._async_search_query(f"concurrent query {i}"))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        throughput_time = time.time() - throughput_start
        qps = concurrent_queries / throughput_time
        
        # Calculate statistics
        avg_latency = np.mean(latency_samples)
        p95_latency = np.percentile(latency_samples, 95)
        p99_latency = np.percentile(latency_samples, 99)
        
        performance_passed = (
            avg_latency < 100 and  # Under 100ms average
            p95_latency < 200 and  # Under 200ms for 95th percentile
            qps > 5  # At least 5 queries per second
        )
        
        self.test_results.append(TestResult(
            test_name="performance_benchmarks",
            passed=performance_passed,
            execution_time=throughput_time,
            details={
                "average_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency, 
                "p99_latency_ms": p99_latency,
                "queries_per_second": qps,
                "samples": len(latency_samples),
                "concurrent_queries": concurrent_queries
            },
            recommendations=[
                "Target <50ms average latency for real-time use",
                "Monitor p99 latency for consistent user experience",
                "Consider caching for frequently accessed memories"
            ]
        ))

    async def _async_search_query(self, query: str):
        """Helper for concurrent query testing"""
        return self.memory_system.intelligent_memory_search(
            user_query=query,
            query_type=QueryType.GENERAL
        )

    async def test_memory_coherence(self):
        """Test 5: Memory Coherence and Consistency"""
        print("\n🧠 Testing Memory Coherence...")
        
        # Test conversational coherence across multiple interactions
        conversation_flow = [
            ("I'm working on a Python AI project", "PROJECT"),
            ("I prefer using TypeScript for frontend", "PREFERENCE"), 
            ("The project uses OpenAI's GPT-4 API", "TECHNICAL"),
            ("Team meetings are every Tuesday at 2 PM", "WORKFLOW"),
            ("I learned that vector embeddings improve search", "LEARNING")
        ]
        
        start_time = time.time()
        
        # Store conversation memories
        for content, category in conversation_flow:
            self.memory_system.enhanced_add_memory(
                text=content,
                category=category,
                metadata={"conversation_id": "test_conv_001"}
            )
        
        # Test coherence queries
        coherence_tests = [
            {
                "query": "What programming languages do I use?",
                "expected_memories": 2,  # Python and TypeScript
                "coherence_type": "cross_category"
            },
            {
                "query": "Tell me about my current project",
                "expected_memories": 3,  # Python AI project + GPT-4 + vector embeddings
                "coherence_type": "project_context"
            },
            {
                "query": "What are my work schedules?",
                "expected_memories": 1,  # Tuesday meetings
                "coherence_type": "workflow_context"
            }
        ]
        
        coherence_results = []
        for test in coherence_tests:
            result = self.memory_system.intelligent_memory_search(
                user_query=test["query"],
                query_type=QueryType.GENERAL
            )
            
            coherence_results.append({
                "query": test["query"],
                "memories_found": len(result.memories),
                "expected_memories": test["expected_memories"],
                "confidence": result.confidence,
                "categories": result.categories,
                "coherent": abs(len(result.memories) - test["expected_memories"]) <= 1
            })
        
        execution_time = time.time() - start_time
        coherence_score = sum(1 for r in coherence_results if r["coherent"]) / len(coherence_results)
        
        self.test_results.append(TestResult(
            test_name="memory_coherence",
            passed=coherence_score >= 0.7,
            execution_time=execution_time,
            details={
                "coherence_score": coherence_score,
                "conversation_memories": len(conversation_flow),
                "test_queries": len(coherence_tests),
                "results": coherence_results
            },
            recommendations=[
                "Improve cross-category memory linking",
                "Enhance project context awareness",
                "Consider conversation threading for better coherence"
            ]
        ))

    async def test_categorization_accuracy(self):
        """Test 6: Categorization System Accuracy"""
        print("\n📂 Testing Categorization Accuracy...")
        
        categorization_tests = [
            ("I prefer using dark mode in my IDE", "PREFERENCE"),
            ("npm install express for Node.js backend", "TECHNICAL"),
            ("Daily standup meeting at 9:30 AM", "WORKFLOW"), 
            ("Memory-C* system architecture documentation", "PROJECT"),
            ("Discovered that HNSW indexing is faster than IVF", "LEARNING"),
            ("Setup Docker environment for development", "SYSTEM"),
            ("Fixed the API timeout error in production", "ERROR"),
            ("Best practice: use async/await for API calls", "INSIGHT")
        ]
        
        start_time = time.time()
        categorization_results = []
        
        for content, expected_category in categorization_tests:
            # Test auto-categorization
            detected_category = self.memory_system._intelligent_categorization(content)
            
            # Test storage with auto-categorization
            result = self.memory_system.enhanced_add_memory(
                text=content,
                metadata={"test_type": "categorization_test"}
            )
            
            categorization_results.append({
                "content": content,
                "expected_category": expected_category,
                "detected_category": detected_category,
                "correct": detected_category == expected_category,
                "stored_successfully": "error" not in result
            })
        
        execution_time = time.time() - start_time
        accuracy = sum(1 for r in categorization_results if r["correct"]) / len(categorization_results)
        
        self.test_results.append(TestResult(
            test_name="categorization_accuracy",
            passed=accuracy >= 0.75,
            execution_time=execution_time,
            details={
                "categorization_accuracy": accuracy,
                "test_cases": len(categorization_tests),
                "results": categorization_results,
                "category_distribution": {
                    cat: sum(1 for r in categorization_results if r["expected_category"] == cat)
                    for cat in set(expected for _, expected in categorization_tests)
                }
            },
            recommendations=[
                "Improve keyword matching for technical terms",
                "Add more training examples for edge categories",
                "Consider machine learning for categorization"
            ]
        ))

    async def test_edge_cases(self):
        """Test 7: Edge Cases and Error Handling"""
        print("\n🔀 Testing Edge Cases...")
        
        edge_test_cases = [
            ("", "empty_query"),
            ("a" * 10000, "very_long_query"),
            ("🎉🚀💻🔥⭐", "emoji_only"),
            ("SELECT * FROM users; DROP TABLE memories;", "sql_injection"),
            ("   \n\t  ", "whitespace_only"),
            ("query with\nnewlines\tand\ttabs", "special_characters"),
            ("QUERY IN ALL CAPS WITH NUMBERS 123456", "caps_and_numbers")
        ]
        
        start_time = time.time()
        edge_results = []
        
        for test_query, test_type in edge_test_cases:
            try:
                result = self.memory_system.intelligent_memory_search(
                    user_query=test_query,
                    query_type=QueryType.GENERAL
                )
                
                edge_results.append({
                    "test_type": test_type,
                    "query_length": len(test_query),
                    "handled_gracefully": True,
                    "returned_results": len(result.memories),
                    "confidence": result.confidence,
                    "error": None
                })
                
            except Exception as e:
                edge_results.append({
                    "test_type": test_type,
                    "query_length": len(test_query),
                    "handled_gracefully": False,
                    "returned_results": 0,
                    "confidence": 0,
                    "error": str(e)
                })
        
        execution_time = time.time() - start_time
        graceful_handling = sum(1 for r in edge_results if r["handled_gracefully"]) / len(edge_results)
        
        self.test_results.append(TestResult(
            test_name="edge_cases",
            passed=graceful_handling >= 0.9,
            execution_time=execution_time,
            details={
                "graceful_handling_rate": graceful_handling,
                "edge_cases_tested": len(edge_test_cases),
                "results": edge_results
            },
            recommendations=[
                "Add input validation for query length",
                "Improve handling of special characters",
                "Consider sanitization for security"
            ]
        ))

    async def test_scalability(self):
        """Test 8: Scalability Under Load"""
        print("\n📈 Testing Scalability...")
        
        # Test with increasing memory count
        scalability_phases = [
            (50, "small_scale"),
            (200, "medium_scale"), 
            (500, "large_scale")
        ]
        
        start_time = time.time()
        scalability_results = []
        
        for memory_count, phase in scalability_phases:
            phase_start = time.time()
            
            # Add memories for this phase
            for i in range(memory_count):
                content = f"Scalability test memory {i} with technical content about AI systems"
                self.memory_system.enhanced_add_memory(
                    text=content,
                    category="TEST",
                    metadata={"phase": phase, "index": i}
                )
            
            # Test search performance at this scale
            search_times = []
            for j in range(10):  # 10 search samples
                search_start = time.perf_counter()
                
                result = self.memory_system.intelligent_memory_search(
                    user_query=f"technical content {j}",
                    query_type=QueryType.TECHNICAL
                )
                
                search_end = time.perf_counter()
                search_times.append((search_end - search_start) * 1000)
            
            phase_time = time.time() - phase_start
            avg_search_time = np.mean(search_times)
            
            scalability_results.append({
                "phase": phase,
                "memory_count": memory_count,
                "phase_duration": phase_time,
                "avg_search_time_ms": avg_search_time,
                "search_samples": len(search_times),
                "performance_acceptable": avg_search_time < 200  # Under 200ms
            })
        
        execution_time = time.time() - start_time
        performance_maintained = all(r["performance_acceptable"] for r in scalability_results)
        
        self.test_results.append(TestResult(
            test_name="scalability",
            passed=performance_maintained,
            execution_time=execution_time,
            details={
                "performance_maintained": performance_maintained,
                "phases_tested": len(scalability_phases),
                "total_memories_added": sum(count for count, _ in scalability_phases),
                "results": scalability_results
            },
            recommendations=[
                "Monitor search performance as memory count grows",
                "Consider indexing optimizations for large datasets",
                "Implement memory archiving for old entries"
            ]
        ))

    async def test_data_integrity(self):
        """Test 9: Data Integrity and Persistence"""
        print("\n🛡️  Testing Data Integrity...")
        
        # Test data consistency across operations
        integrity_test_memories = [
            ("Critical system configuration for production", "SYSTEM"),
            ("Important client meeting notes from Q4", "PROJECT"),
            ("Security vulnerability discovered in auth", "ERROR")
        ]
        
        start_time = time.time()
        stored_memory_ids = []
        
        # Store critical memories
        for content, category in integrity_test_memories:
            result = self.memory_system.enhanced_add_memory(
                text=content,
                category=category,
                metadata={"critical": True, "test_type": "integrity_test"}
            )
            if "error" not in result:
                stored_memory_ids.append(result)
        
        # Test persistence - retrieve after storage
        time.sleep(1)  # Brief delay to simulate persistence
        
        retrieved_memories = []
        for memory_content, _ in integrity_test_memories:
            result = self.memory_system.intelligent_memory_search(
                user_query=memory_content[:30],
                query_type=QueryType.GENERAL
            )
            retrieved_memories.append({
                "original": memory_content,
                "found": len(result.memories) > 0,
                "exact_match": any(
                    memory_content in mem.get("content", "")
                    for mem in result.memories
                )
            })
        
        # Test data consistency
        analytics = self.memory_system.get_memory_analytics()
        
        execution_time = time.time() - start_time
        integrity_score = sum(1 for r in retrieved_memories if r["exact_match"]) / len(retrieved_memories)
        
        self.test_results.append(TestResult(
            test_name="data_integrity",
            passed=integrity_score >= 0.9,
            execution_time=execution_time,
            details={
                "integrity_score": integrity_score,
                "memories_stored": len(stored_memory_ids),
                "memories_retrieved": len(retrieved_memories),
                "system_analytics": analytics,
                "results": retrieved_memories
            },
            recommendations=[
                "Implement checksums for data verification",
                "Add backup and recovery procedures",
                "Monitor for data corruption"
            ]
        ))

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        total_execution_time = sum(result.execution_time for result in self.test_results)
        
        # Calculate overall scores
        overall_score = passed_tests / total_tests if total_tests > 0 else 0
        performance_score = np.mean([
            r.details.get("performance_acceptable", True) 
            for r in self.test_results 
            if "performance_acceptable" in r.details
        ])
        
        # Priority recommendations
        all_recommendations = []
        for result in self.test_results:
            if not result.passed and result.recommendations:
                all_recommendations.extend(result.recommendations)
        
        # Generate status
        if overall_score >= 0.9:
            status = "EXCELLENT"
        elif overall_score >= 0.8:
            status = "GOOD"
        elif overall_score >= 0.7:
            status = "ACCEPTABLE"
        else:
            status = "NEEDS_IMPROVEMENT"
        
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "overall_score": overall_score,
                "status": status,
                "total_execution_time": total_execution_time
            },
            "performance_metrics": {
                "performance_score": performance_score,
                "average_test_time": total_execution_time / total_tests if total_tests > 0 else 0
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "execution_time": r.execution_time,
                    "key_metrics": self._extract_key_metrics(r.details)
                }
                for r in self.test_results
            ],
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "recommendations": r.recommendations
                }
                for r in self.test_results
            ],
            "priority_recommendations": list(set(all_recommendations)),
            "next_steps": self._generate_next_steps(overall_score, all_recommendations)
        }
        
        self._print_report_summary(report)
        return report
    
    def _extract_key_metrics(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for summary view"""
        key_metrics = {}
        
        # Common metrics to extract
        metric_keys = [
            "accuracy", "success_rate", "confidence", "latency_ms", 
            "throughput", "coherence_score", "integrity_score"
        ]
        
        for key in metric_keys:
            if key in details:
                key_metrics[key] = details[key]
        
        return key_metrics
    
    def _generate_next_steps(self, overall_score: float, recommendations: List[str]) -> List[str]:
        """Generate actionable next steps based on test results"""
        next_steps = []
        
        if overall_score < 0.7:
            next_steps.append("🚨 CRITICAL: Address failing tests before production deployment")
            next_steps.append("🔧 Focus on core functionality improvements")
        elif overall_score < 0.9:
            next_steps.append("⚠️  Address performance and reliability issues")
            next_steps.append("🎯 Optimize for production readiness")
        else:
            next_steps.append("✅ System ready for production with monitoring")
            next_steps.append("📊 Implement continuous performance monitoring")
        
        # Add specific recommendations
        if recommendations:
            next_steps.extend([f"🔧 {rec}" for rec in recommendations[:3]])
        
        next_steps.extend([
            "📈 Set up automated testing pipeline",
            "🔄 Schedule regular performance benchmarks",
            "📋 Document test procedures for team"
        ])
        
        return next_steps
    
    def _print_report_summary(self, report: Dict[str, Any]):
        """Print formatted test report summary"""
        
        print("\n" + "="*80)
        print("🎯 MEMORY SYSTEM TEST REPORT SUMMARY")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"📊 Overall Score: {summary['overall_score']:.1%} ({summary['status']})")
        print(f"✅ Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")
        
        print(f"\n📈 Performance Score: {report['performance_metrics']['performance_score']:.1%}")
        
        print("\n🔥 Priority Recommendations:")
        for rec in report["priority_recommendations"][:5]:
            print(f"   • {rec}")
        
        print("\n🚀 Next Steps:")
        for step in report["next_steps"][:5]:
            print(f"   • {step}")
        
        print("\n" + "="*80)


# Example usage and integration
async def main():
    """Main testing function"""
    
    # Initialize your memory system
    memory_system = AdvancedAIMemory(
        api_url="http://localhost:8765/api/v1",
        user_id="drj"
    )
    
    # Create tester
    tester = MemorySystemTester(memory_system)
    
    # Run comprehensive test suite
    test_report = await tester.run_comprehensive_test_suite()
    
    # Save detailed report
    with open(f"memory_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(test_report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to memory_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return test_report


if __name__ == "__main__":
    asyncio.run(main()) 