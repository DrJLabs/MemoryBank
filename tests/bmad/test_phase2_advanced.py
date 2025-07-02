#!/usr/bin/env python3
"""
BMAD Phase 2: Advanced Testing Suite
Comprehensive BDD and Property-Based Testing Integration

This module integrates:
1. Behavior-Driven Testing (BDD) for agent persona validation
2. Property-Based Testing for memory system invariants
3. Advanced quality metrics and reporting
"""

import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Phase 2 components
from tests.bmad.behavior.step_definitions.agent_steps import (
    BMAdBDDTestRunner, context, mock_agents, mock_memory
)
from tests.bmad.properties.memory_properties import (
    BMAdMemoryPropertyTests, MockAdvancedMemorySystem
)

class BMAdPhase2AdvancedTestSuite:
    """
    Phase 2 Advanced Testing Suite for BMAD
    Combines BDD and Property-Based Testing methodologies
    """
    
    def __init__(self):
        self.bdd_runner = BMAdBDDTestRunner()
        self.property_tester = BMAdMemoryPropertyTests()
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = None
        self.end_time = None
        
    def run_bdd_agent_tests(self) -> Dict[str, Any]:
        """Run Behavior-Driven Tests for agent personas"""
        print("\n🎭 **Phase 2: Behavior-Driven Testing (BDD)**")
        print("=" * 60)
        
        # Define BDD scenarios to test
        scenarios = [
            {
                "name": "Orchestrator Agent Maintains Master Orchestrator Persona",
                "steps": [
                    ("Given", "the BMAD system is initialized"),
                    ("Given", "the memory system is available"),
                    ("Given", "all agents are configured with their personas"),
                    ("Given", 'I am interacting with the "bmad-orchestrator" agent'),
                    ("When", 'I send the command "*help"'),
                    ("Then", 'the agent should respond as the "BMAD Master Orchestrator"'),
                    ("Then", 'the response should mention "commands start with *"'),
                    ("Then", "the response should include available agents and workflows"),
                    ("Then", "the persona consistency score should be >= 95%")
                ]
            },
            {
                "name": "Agent Transformation Preserves Context",
                "steps": [
                    ("Given", "the BMAD system is initialized"),
                    ("Given", "the memory system is available"),
                    ("Given", 'I am interacting with the "bmad-orchestrator" agent'),
                    ("Given", 'there is existing memory context about "testing implementation"'),
                    ("When", 'I execute the command "*agent dev"'),
                    ("Then", "the memory context should be preserved"),
                    ("Then", "the context retrieval should be successful")
                ]
            },
            {
                "name": "Dev Agent Maintains Technical Persona",
                "steps": [
                    ("Given", "the BMAD system is initialized"),
                    ("Given", 'I am interacting with the "dev" agent'),
                    ("When", "I ask about implementing unit tests"),
                    ("Then", 'the agent should respond as the "Full Stack Developer"'),
                    ("Then", "the persona consistency score should be >= 95%")
                ]
            }
        ]
        
        # Run BDD scenarios
        passed_scenarios = 0
        total_scenarios = len(scenarios)
        
        for scenario in scenarios:
            success = self.bdd_runner.run_scenario(scenario["name"], scenario["steps"])
            if success:
                passed_scenarios += 1
        
        # Generate BDD results
        bdd_results = {
            "total_scenarios": total_scenarios,
            "scenarios_passed": passed_scenarios,
            "scenarios_failed": total_scenarios - passed_scenarios,
            "success_rate": (passed_scenarios / total_scenarios) * 100,
            "status": "PASSED" if passed_scenarios == total_scenarios else "FAILED"
        }
        
        print("\n📋 **BDD Results Summary**")
        print(f"Scenarios: {passed_scenarios}/{total_scenarios} passed")
        print(f"Success Rate: {bdd_results['success_rate']:.1f}%")
        
        return bdd_results
    
    def run_property_based_tests(self) -> Dict[str, Any]:
        """Run Property-Based Tests for memory system"""
        print("\n🧬 **Phase 2: Property-Based Testing**")
        print("=" * 60)
        
        # Execute property-based tests
        property_results = self.property_tester.run_all_property_tests()
        
        print("\n📊 **Property Testing Results Summary**")
        print(f"Tests: {property_results['tests_passed']}/{property_results['total_tests']} passed")
        print(f"Success Rate: {property_results['success_rate']:.1f}%")
        
        return property_results
    
    def run_advanced_integration_tests(self) -> Dict[str, Any]:
        """Run advanced integration tests combining BDD and property testing"""
        print("\n🔗 **Phase 2: Advanced Integration Testing**")
        print("=" * 60)
        
        integration_tests = []
        
        # Test 1: Agent-Memory Integration
        print("🧪 Running Agent-Memory Integration Test...")
        try:
            # Simulate agent storing memory through BDD scenario
            context.clear()
            
            # Set up agent
            context.current_agent = mock_agents["dev"]
            
            # Agent processes development task
            response = context.current_agent.process_command("Store this learning: Phase 2 testing works")
            
            # Verify memory integration
            memory_stored = mock_memory.retrieve_context("Phase 2 testing")
            
            integration_success = (
                response.get("persona_consistency", 0) >= 0.95 and
                memory_stored.get("found", False)
            )
            
            integration_tests.append({
                "name": "Agent-Memory Integration",
                "passed": integration_success,
                "details": {
                    "persona_consistency": response.get("persona_consistency", 0),
                    "memory_found": memory_stored.get("found", False)
                }
            })
            
            if integration_success:
                print("  ✅ Agent-Memory Integration: PASSED")
            else:
                print("  ❌ Agent-Memory Integration: FAILED")
                
        except Exception as e:
            integration_tests.append({
                "name": "Agent-Memory Integration",
                "passed": False,
                "error": str(e)
            })
            print(f"  💥 Agent-Memory Integration: ERROR - {e}")
        
        # Test 2: Cross-System Consistency
        print("🧪 Running Cross-System Consistency Test...")
        try:
            # Test that BDD agent responses are consistent with property-based memory operations
            property_memory = MockAdvancedMemorySystem()
            
            # Store memory via property system
            stored = property_memory.store_memory(
                "consistency_test", 
                "BDD and property testing integration", 
                "TESTING"
            )
            
            # Retrieve via property system
            retrieved = property_memory.retrieve_memory("consistency_test")
            
            # Verify cross-system consistency
            consistency_check = (
                stored["content"] == retrieved["content"] and
                stored["category"] == retrieved["category"] and
                retrieved["checksum"] == property_memory._calculate_checksum(stored["content"])
            )
            
            integration_tests.append({
                "name": "Cross-System Consistency",
                "passed": consistency_check,
                "details": {
                    "content_match": stored["content"] == retrieved["content"],
                    "category_match": stored["category"] == retrieved["category"],
                    "checksum_valid": retrieved["checksum"] == property_memory._calculate_checksum(stored["content"])
                }
            })
            
            if consistency_check:
                print("  ✅ Cross-System Consistency: PASSED")
            else:
                print("  ❌ Cross-System Consistency: FAILED")
                
        except Exception as e:
            integration_tests.append({
                "name": "Cross-System Consistency",
                "passed": False,
                "error": str(e)
            })
            print(f"  💥 Cross-System Consistency: ERROR - {e}")
        
        # Calculate integration results
        passed_integration = sum(1 for test in integration_tests if test["passed"])
        total_integration = len(integration_tests)
        
        integration_results = {
            "total_tests": total_integration,
            "tests_passed": passed_integration,
            "tests_failed": total_integration - passed_integration,
            "success_rate": (passed_integration / total_integration) * 100 if total_integration > 0 else 0,
            "status": "PASSED" if passed_integration == total_integration else "FAILED",
            "test_details": integration_tests
        }
        
        print("\n🔗 **Integration Testing Results Summary**")
        print(f"Tests: {passed_integration}/{total_integration} passed")
        print(f"Success Rate: {integration_results['success_rate']:.1f}%")
        
        return integration_results
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        execution_time = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        
        metrics = {
            "total_execution_time": execution_time,
            "bdd_scenarios_per_second": self.test_results.get("bdd", {}).get("total_scenarios", 0) / max(execution_time, 0.1),
            "property_tests_per_second": self.test_results.get("property", {}).get("total_tests", 0) / max(execution_time, 0.1),
            "average_test_time": execution_time / max(self._get_total_test_count(), 1),
            "performance_threshold_met": execution_time < 60.0,  # Should complete in under 1 minute
            "memory_efficiency": "Excellent" if execution_time < 30.0 else "Good" if execution_time < 60.0 else "Needs Improvement"
        }
        
        return metrics
    
    def _get_total_test_count(self) -> int:
        """Get total number of tests executed"""
        bdd_count = self.test_results.get("bdd", {}).get("total_scenarios", 0)
        property_count = self.test_results.get("property", {}).get("total_tests", 0)
        integration_count = self.test_results.get("integration", {}).get("total_tests", 0)
        return bdd_count + property_count + integration_count
    
    def generate_phase2_report(self) -> Dict[str, Any]:
        """Generate comprehensive Phase 2 testing report"""
        
        # Calculate overall success
        bdd_success = self.test_results.get("bdd", {}).get("success_rate", 0)
        property_success = self.test_results.get("property", {}).get("success_rate", 0)
        integration_success = self.test_results.get("integration", {}).get("success_rate", 0)
        
        overall_success = (bdd_success + property_success + integration_success) / 3
        
        # Generate quality score
        quality_score = self._calculate_quality_score()
        
        report = {
            "phase": "Phase 2: Advanced Testing",
            "timestamp": time.time(),
            "execution_time": self.performance_metrics.get("total_execution_time", 0),
            "overall_success_rate": overall_success,
            "quality_score": quality_score,
            "status": "PASSED" if overall_success >= 95.0 and quality_score >= 95.0 else "FAILED",
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _calculate_quality_score(self) -> float:
        """Calculate comprehensive quality score for Phase 2"""
        
        # Component weights
        weights = {
            "bdd_success": 0.4,      # 40% - Agent behavior consistency
            "property_success": 0.4,  # 40% - Memory system reliability  
            "integration_success": 0.2 # 20% - Cross-system integration
        }
        
        # Get success rates
        bdd_rate = self.test_results.get("bdd", {}).get("success_rate", 0)
        property_rate = self.test_results.get("property", {}).get("success_rate", 0)
        integration_rate = self.test_results.get("integration", {}).get("success_rate", 0)
        
        # Calculate weighted score
        quality_score = (
            bdd_rate * weights["bdd_success"] +
            property_rate * weights["property_success"] +
            integration_rate * weights["integration_success"]
        )
        
        return round(quality_score, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        bdd_success = self.test_results.get("bdd", {}).get("success_rate", 0)
        property_success = self.test_results.get("property", {}).get("success_rate", 0)
        integration_success = self.test_results.get("integration", {}).get("success_rate", 0)
        
        if bdd_success < 95.0:
            recommendations.append("Improve agent persona consistency and behavior validation")
        
        if property_success < 95.0:
            recommendations.append("Enhance memory system reliability and property invariants")
        
        if integration_success < 95.0:
            recommendations.append("Strengthen cross-system integration and consistency checks")
        
        execution_time = self.performance_metrics.get("total_execution_time", 0)
        if execution_time > 60.0:
            recommendations.append("Optimize test execution performance for faster feedback")
        
        if not recommendations:
            recommendations.append("All Phase 2 advanced testing components are performing excellently!")
        
        return recommendations
    
    def run_complete_phase2_suite(self) -> Dict[str, Any]:
        """Run the complete Phase 2 advanced testing suite"""
        
        print("\n" + "="*80)
        print("🚀 **BMAD PHASE 2: ADVANCED TESTING SUITE**")
        print("   Behavior-Driven Testing + Property-Based Testing")
        print("="*80)
        
        self.start_time = time.time()
        
        try:
            # 1. Run BDD Tests
            self.test_results["bdd"] = self.run_bdd_agent_tests()
            
            # 2. Run Property-Based Tests  
            self.test_results["property"] = self.run_property_based_tests()
            
            # 3. Run Advanced Integration Tests
            self.test_results["integration"] = self.run_advanced_integration_tests()
            
            self.end_time = time.time()
            
            # 4. Calculate Performance Metrics
            self.performance_metrics = self.calculate_performance_metrics()
            
            # 5. Generate Final Report
            final_report = self.generate_phase2_report()
            
            # Display final results
            print("\n" + "="*80)
            print("📊 **PHASE 2 FINAL RESULTS**")
            print("="*80)
            print(f"Overall Success Rate: {final_report['overall_success_rate']:.1f}%")
            print(f"Quality Score: {final_report['quality_score']:.1f}/100")
            print(f"Execution Time: {final_report['execution_time']:.2f}s")
            print(f"Status: {final_report['status']}")
            
            print("\n📋 **Component Results:**")
            print(f"  BDD Testing: {self.test_results['bdd']['success_rate']:.1f}%")
            print(f"  Property Testing: {self.test_results['property']['success_rate']:.1f}%")
            print(f"  Integration Testing: {self.test_results['integration']['success_rate']:.1f}%")
            
            print("\n💡 **Recommendations:**")
            for i, rec in enumerate(final_report['recommendations'], 1):
                print(f"  {i}. {rec}")
            
            return final_report
            
        except Exception as e:
            self.end_time = time.time()
            print(f"\n💥 **Phase 2 Testing Failed:** {e}")
            
            return {
                "phase": "Phase 2: Advanced Testing",
                "status": "ERROR",
                "error": str(e),
                "execution_time": self.end_time - self.start_time if self.start_time else 0
            }

def test_bmad_phase2_advanced_suite():
    """Pytest entry point for Phase 2 advanced testing"""
    suite = BMAdPhase2AdvancedTestSuite()
    results = suite.run_complete_phase2_suite()
    
    # Assert overall success for pytest
    assert results.get("status") == "PASSED", f"Phase 2 testing failed: {results.get('error', 'Unknown error')}"
    assert results.get("overall_success_rate", 0) >= 95.0, "Overall success rate below threshold"
    assert results.get("quality_score", 0) >= 95.0, "Quality score below threshold"

if __name__ == "__main__":
    # Direct execution
    suite = BMAdPhase2AdvancedTestSuite()
    results = suite.run_complete_phase2_suite()
    
    # Exit with appropriate code
    sys.exit(0 if results.get("status") == "PASSED" else 1) 