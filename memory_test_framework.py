#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Memory-C* AI Memory System
Based on current research and best practices for AI memory testing
"""

import asyncio
import time
import json
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class TestResult:
    test_name: str
    passed: bool
    execution_time: float
    details: Dict[str, Any]
    recommendations: List[str] = None

class MemorySystemTester:
    """Comprehensive testing framework for AI memory systems"""
    
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.test_results = []
        
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite covering all aspects of memory functionality"""
        
        test_categories = [
            self.test_memory_storage_retrieval,
            self.test_cursor_integration,
            self.test_performance_benchmarks,
            self.test_memory_coherence,
            self.test_categorization_accuracy,
            self.test_edge_cases
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
        
        start_time = time.time()
        stored_count = 0
        
        # Test storage
        for content, category in test_memories:
            try:
                result = self.memory_system.enhanced_add_memory(
                    text=content,
                    category=category,
                    metadata={"test_type": "storage_test"}
                )
                if "error" not in str(result):
                    stored_count += 1
            except Exception as e:
                print(f"Storage error: {e}")
        
        # Test retrieval
        retrieval_results = []
        for content, expected_category in test_memories:
            try:
                query_result = self.memory_system.intelligent_memory_search(
                    user_query=content[:20],
                    query_type=getattr(self.memory_system, 'QueryType', type('obj', (object,), {'GENERAL': 'general'})).GENERAL
                )
                retrieval_results.append({
                    "query": content[:20],
                    "found": len(query_result.memories) > 0,
                    "relevance": query_result.confidence
                })
            except Exception as e:
                retrieval_results.append({
                    "query": content[:20],
                    "found": False,
                    "relevance": 0,
                    "error": str(e)
                })
        
        execution_time = time.time() - start_time
        success_rate = sum(1 for r in retrieval_results if r["found"]) / len(retrieval_results)
        
        self.test_results.append(TestResult(
            test_name="memory_storage_retrieval",
            passed=success_rate >= 0.8,
            execution_time=execution_time,
            details={
                "stored_memories": stored_count,
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

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        total_execution_time = sum(result.execution_time for result in self.test_results)
        
        overall_score = passed_tests / total_tests if total_tests > 0 else 0
        
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
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "recommendations": r.recommendations
                }
                for r in self.test_results
            ]
        }
        
        self._print_report_summary(report)
        return report
    
    def _print_report_summary(self, report: Dict[str, Any]):
        """Print formatted test report summary"""
        
        print("\n" + "="*80)
        print("🎯 MEMORY SYSTEM TEST REPORT SUMMARY")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"📊 Overall Score: {summary['overall_score']:.1%} ({summary['status']})")
        print(f"✅ Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")
        print("="*80)

    async def test_cursor_integration(self):
        """Test Cursor Integration Functionality"""
        print("\n🖱️  Testing Cursor Integration...")
        
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
            }
        ]
        
        start_time = time.time()
        cursor_results = []
        
        for scenario in cursor_test_scenarios:
            try:
                context = self.memory_system.get_conversational_context(
                    user_query=scenario["user_query"],
                    query_type=scenario["query_type"], 
                    detailed=True
                )
                
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
                    "proper_format": proper_format,
                    "has_context": len(context) > 100
                })
            except Exception as e:
                cursor_results.append({
                    "query": scenario["user_query"],
                    "error": str(e),
                    "proper_format": False,
                    "has_context": False
                })
        
        execution_time = time.time() - start_time
        context_quality = sum(
            1 for r in cursor_results 
            if r.get("proper_format", False) and r.get("has_context", False)
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
        """Test Performance Benchmarks"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        latency_samples = []
        for i in range(10):
            start_time = time.perf_counter()
            
            try:
                result = self.memory_system.intelligent_memory_search(
                    user_query=f"test query {i}",
                    query_type=getattr(self.memory_system, 'QueryType', type('obj', (object,), {'GENERAL': 'general'})).GENERAL,
                    max_results=10
                )
                
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latency_samples.append(latency_ms)
            except Exception:
                latency_samples.append(1000)
        
        avg_latency = np.mean(latency_samples)
        p95_latency = np.percentile(latency_samples, 95)
        
        performance_passed = avg_latency < 200 and p95_latency < 500
        
        self.test_results.append(TestResult(
            test_name="performance_benchmarks",
            passed=performance_passed,
            execution_time=avg_latency / 1000,
            details={
                "average_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "samples": len(latency_samples)
            },
            recommendations=[
                "Target <50ms average latency for real-time use",
                "Monitor p99 latency for consistent user experience",
                "Consider caching for frequently accessed memories"
            ]
        ))

    async def test_memory_coherence(self):
        """Test Memory Coherence and Consistency"""
        print("\n🧠 Testing Memory Coherence...")
        
        conversation_flow = [
            ("I'm working on a Python AI project", "PROJECT"),
            ("I prefer using TypeScript for frontend", "PREFERENCE"), 
            ("The project uses OpenAI's GPT-4 API", "TECHNICAL")
        ]
        
        start_time = time.time()
        
        for content, category in conversation_flow:
            try:
                self.memory_system.enhanced_add_memory(
                    text=content,
                    category=category,
                    metadata={"conversation_id": "test_conv_001"}
                )
            except Exception as e:
                print(f"Error storing memory: {e}")
        
        coherence_tests = [
            {
                "query": "What programming languages do I use?",
                "expected_memories": 2,
                "coherence_type": "cross_category"
            }
        ]
        
        coherence_results = []
        for test in coherence_tests:
            try:
                result = self.memory_system.intelligent_memory_search(
                    user_query=test["query"],
                    query_type=getattr(self.memory_system, 'QueryType', type('obj', (object,), {'GENERAL': 'general'})).GENERAL
                )
                
                coherence_results.append({
                    "query": test["query"],
                    "memories_found": len(result.memories),
                    "expected_memories": test["expected_memories"],
                    "coherent": abs(len(result.memories) - test["expected_memories"]) <= 1
                })
            except Exception as e:
                coherence_results.append({
                    "query": test["query"],
                    "error": str(e),
                    "coherent": False
                })
        
        execution_time = time.time() - start_time
        coherence_score = sum(1 for r in coherence_results if r.get("coherent", False)) / len(coherence_results)
        
        self.test_results.append(TestResult(
            test_name="memory_coherence",
            passed=coherence_score >= 0.7,
            execution_time=execution_time,
            details={
                "coherence_score": coherence_score,
                "conversation_memories": len(conversation_flow),
                "results": coherence_results
            },
            recommendations=[
                "Improve cross-category memory linking",
                "Enhance project context awareness"
            ]
        ))

    async def test_categorization_accuracy(self):
        """Test Categorization System Accuracy"""
        print("\n📂 Testing Categorization Accuracy...")
        
        categorization_tests = [
            ("I prefer using dark mode in my IDE", "PREFERENCE"),
            ("npm install express for Node.js backend", "TECHNICAL"),
            ("Daily standup meeting at 9:30 AM", "WORKFLOW")
        ]
        
        start_time = time.time()
        categorization_results = []
        
        for content, expected_category in categorization_tests:
            try:
                detected_category = self.memory_system._intelligent_categorization(content)
                
                categorization_results.append({
                    "content": content,
                    "expected_category": expected_category,
                    "detected_category": detected_category,
                    "correct": detected_category == expected_category
                })
            except Exception as e:
                categorization_results.append({
                    "content": content,
                    "expected_category": expected_category,
                    "error": str(e),
                    "correct": False
                })
        
        execution_time = time.time() - start_time
        accuracy = sum(1 for r in categorization_results if r["correct"]) / len(categorization_results)
        
        self.test_results.append(TestResult(
            test_name="categorization_accuracy",
            passed=accuracy >= 0.6,
            execution_time=execution_time,
            details={
                "categorization_accuracy": accuracy,
                "test_cases": len(categorization_tests),
                "results": categorization_results
            },
            recommendations=[
                "Improve keyword matching for technical terms",
                "Consider machine learning for categorization"
            ]
        ))

    async def test_edge_cases(self):
        """Test Edge Cases and Error Handling"""
        print("\n🔀 Testing Edge Cases...")
        
        edge_test_cases = [
            ("", "empty_query"),
            ("a" * 100, "long_query"),
            ("🎉🚀💻", "emoji_query"),
            ("   \n\t  ", "whitespace_only")
        ]
        
        start_time = time.time()
        edge_results = []
        
        for test_query, test_type in edge_test_cases:
            try:
                result = self.memory_system.intelligent_memory_search(
                    user_query=test_query,
                    query_type=getattr(self.memory_system, 'QueryType', type('obj', (object,), {'GENERAL': 'general'})).GENERAL
                )
                
                edge_results.append({
                    "test_type": test_type,
                    "handled_gracefully": True,
                    "returned_results": len(result.memories)
                })
                
            except Exception as e:
                edge_results.append({
                    "test_type": test_type,
                    "handled_gracefully": False,
                    "error": str(e)
                })
        
        execution_time = time.time() - start_time
        graceful_handling = sum(1 for r in edge_results if r["handled_gracefully"]) / len(edge_results)
        
        self.test_results.append(TestResult(
            test_name="edge_cases",
            passed=graceful_handling >= 0.8,
            execution_time=execution_time,
            details={
                "graceful_handling_rate": graceful_handling,
                "edge_cases_tested": len(edge_test_cases),
                "results": edge_results
            },
            recommendations=[
                "Add input validation for query length",
                "Improve handling of special characters"
            ]
        ))


# Example usage function
async def run_memory_tests():
    """Example function to run tests"""
    try:
        from mem0.openmemory.advanced_memory_ai import AdvancedAIMemory
        
        memory_system = AdvancedAIMemory(
            api_url="http://localhost:8765/api/v1",
            user_id="drj"
        )
        
        tester = MemorySystemTester(memory_system)
        test_report = await tester.run_comprehensive_test_suite()
        
        report_filename = f"memory_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w") as f:
            json.dump(test_report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to {report_filename}")
        return test_report
        
    except ImportError as e:
        print(f"❌ Could not import memory system: {e}")
        return None
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(run_memory_tests()) 