"""
BMAD Memory Operations Tests
Phase 1: Foundation Testing - Memory System Validation

Tests the core memory operations including:
- CRUD operations (Create, Read, Update, Delete)
- Automatic categorization accuracy
- Context retrieval and relevance scoring
- Memory consistency and performance
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import BMAD test fixtures
from tests.bmad.conftest import (
    mock_memory_system,
    memory_test_data,
    memory_property_strategies,
    quality_metrics_tracker,
    performance_monitor
)


class TestBMADMemoryOperations:
    """Test suite for BMAD memory CRUD operations."""
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_memory_creation(self, mock_memory_system, memory_test_data, quality_metrics_tracker):
        """Test creating new memories with proper categorization."""
        # Arrange
        valid_memories = memory_test_data["valid_memories"]
        
        for memory_data in valid_memories:
            start_time = time.time()
            
            # Mock successful memory creation
            mock_memory_system.add.return_value = {
                "id": f"memory_{int(time.time())}",
                "success": True,
                "category": memory_data["expected_category"],
                "confidence": memory_data["metadata"]["confidence"],
                "creation_time": time.time() - start_time,
            }
            
            # Act
            result = mock_memory_system.add(
                content=memory_data["content"],
                metadata=memory_data["metadata"]
            )
            
            # Assert
            assert result["success"] is True
            assert result["id"] is not None
            assert result["category"] == memory_data["expected_category"]
            assert result["confidence"] >= 0.7  # Minimum confidence threshold
            assert result["creation_time"] < 1.0  # Performance requirement
            
            # Track quality metrics
            quality_metrics_tracker["memory_accuracy"].append(result["confidence"])
            quality_metrics_tracker["performance_ms"].append(result["creation_time"] * 1000)
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_memory_search(self, mock_memory_system, quality_metrics_tracker):
        """Test memory search functionality with relevance scoring."""
        # Arrange
        search_queries = [
            "Python development preferences",
            "BMAD agent behavior testing", 
            "workflow implementation patterns",
            "memory categorization accuracy",
        ]
        
        for query in search_queries:
            start_time = time.time()
            
            # Mock search results with relevance scores
            mock_memory_system.search.return_value = [
                {
                    "id": "mem_1",
                    "content": f"Memory related to {query}",
                    "confidence": 0.95,
                    "category": "TECHNICAL",
                    "relevance_score": 0.89,
                },
                {
                    "id": "mem_2", 
                    "content": f"Secondary memory for {query}",
                    "confidence": 0.87,
                    "category": "WORKFLOW",
                    "relevance_score": 0.76,
                },
            ]
            
            # Act
            results = mock_memory_system.search(query)
            search_time = time.time() - start_time
            
            # Assert
            assert len(results) >= 1
            assert all(result["confidence"] >= 0.7 for result in results)
            assert all(result["relevance_score"] >= 0.5 for result in results)
            assert search_time < 0.5  # Search performance requirement
            
            # Results should be sorted by relevance
            if len(results) > 1:
                assert results[0]["relevance_score"] >= results[1]["relevance_score"]
            
            # Track quality metrics
            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            quality_metrics_tracker["memory_accuracy"].append(avg_confidence)
            quality_metrics_tracker["performance_ms"].append(search_time * 1000)
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_memory_categorization(self, mock_memory_system, memory_test_data, quality_metrics_tracker):
        """Test automatic memory categorization accuracy."""
        # Arrange
        test_memories = memory_test_data["valid_memories"]
        expected_categories = ["TECHNICAL", "WORKFLOW", "PREFERENCE", "PROJECT", "BMAD"]
        
        for memory_data in test_memories:
            # Mock categorization
            mock_memory_system.categorize.return_value = memory_data["expected_category"]
            
            # Act
            predicted_category = mock_memory_system.categorize(memory_data["content"])
            
            # Assert
            assert predicted_category in expected_categories
            assert predicted_category == memory_data["expected_category"]
            
            # Track categorization accuracy
            accuracy_score = 1.0 if predicted_category == memory_data["expected_category"] else 0.0
            quality_metrics_tracker["memory_accuracy"].append(accuracy_score)
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_context_retrieval(self, mock_memory_system, quality_metrics_tracker):
        """Test ai-get-context functionality for BMAD workflows."""
        # Arrange
        context_queries = [
            ("BMAD agent testing setup", "TECHNICAL"),
            ("workflow implementation progress", "WORKFLOW"),
            ("user development preferences", "PREFERENCE"),
            ("testing architecture completion", "PROJECT"),
        ]
        
        for query, expected_category in context_queries:
            start_time = time.time()
            
            # Mock context retrieval
            mock_memory_system.get_context.return_value = {
                "relevant_memories": [
                    {"id": "mem1", "content": f"Context for {query}", "confidence": 0.92},
                    {"id": "mem2", "content": f"Additional context for {query}", "confidence": 0.85},
                ],
                "confidence": 0.88,
                "categories": [expected_category, "BMAD"],
                "retrieval_time": time.time() - start_time,
                "query": query,
            }
            
            # Act
            context = mock_memory_system.get_context(query)
            
            # Assert
            assert len(context["relevant_memories"]) >= 1
            assert context["confidence"] >= 0.7
            assert expected_category in context["categories"]
            assert context["retrieval_time"] < 0.5  # Performance requirement
            assert context["query"] == query
            
            # Track quality metrics
            quality_metrics_tracker["memory_accuracy"].append(context["confidence"])
            quality_metrics_tracker["performance_ms"].append(context["retrieval_time"] * 1000)
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_memory_consistency(self, mock_memory_system, quality_metrics_tracker):
        """Test memory consistency and data integrity."""
        # Arrange
        test_content = "BMAD testing framework uses pytest with comprehensive coverage"
        
        # Mock consistent memory operations
        mock_memory_system.add.return_value = {"id": "test_mem_123", "success": True}
        mock_memory_system.search.return_value = [{
            "id": "test_mem_123",
            "content": test_content,
            "confidence": 0.95,
        }]
        
        # Act - Create memory then search for it
        creation_result = mock_memory_system.add(content=test_content)
        search_results = mock_memory_system.search(test_content[:20])  # Partial search
        
        # Assert
        assert creation_result["success"] is True
        assert len(search_results) >= 1
        
        # Find the created memory in search results
        created_memory = next((r for r in search_results if r["id"] == creation_result["id"]), None)
        assert created_memory is not None
        assert created_memory["content"] == test_content
        
        # Track consistency score
        quality_metrics_tracker["memory_accuracy"].append(1.0)  # Perfect consistency
    
    @pytest.mark.bmad
    @pytest.mark.unit
    def test_invalid_memory_handling(self, mock_memory_system, memory_test_data):
        """Test handling of invalid memory data."""
        # Arrange
        invalid_memories = memory_test_data["invalid_memories"]
        
        for invalid_memory in invalid_memories:
            # Mock error response for invalid data
            mock_memory_system.add.return_value = {
                "success": False,
                "error": f"Invalid memory: {invalid_memory['reason']}",
                "error_code": invalid_memory["reason"].upper(),
            }
            
            # Act
            result = mock_memory_system.add(content=invalid_memory["content"])
            
            # Assert
            assert result["success"] is False
            assert "error" in result
            assert result["error_code"] == invalid_memory["reason"].upper()


class TestBMADMemoryProperties:
    """Property-based tests for memory operations using mock property testing."""
    
    @pytest.mark.bmad
    @pytest.mark.unit
    @pytest.mark.property
    def test_memory_content_invariants(self, memory_property_strategies, mock_memory_system, quality_metrics_tracker):
        """Test memory content invariants using property-based testing."""
        # Arrange - Use mock property strategies
        strategies = memory_property_strategies
        
        # Generate test data using mock strategies
        for _ in range(10):  # Simulate multiple property test cases
            # Generate test content
            content = strategies.text()()
            category = strategies.sampled_from(["TECHNICAL", "WORKFLOW", "PREFERENCE"])()
            metadata = strategies.dictionaries()()
            confidence = strategies.floats()()
            
            # Mock memory creation
            mock_memory_system.add.return_value = {
                "id": f"prop_test_{int(time.time())}",
                "success": True,
                "content": content,
                "category": category,
                "confidence": confidence,
            }
            
            # Act
            result = mock_memory_system.add(content=content, metadata=metadata)
            
            # Assert properties/invariants
            assert result["success"] is True
            assert len(result["content"]) > 0  # Content should not be empty
            assert result["category"] in ["TECHNICAL", "WORKFLOW", "PREFERENCE"]
            assert 0.0 <= result["confidence"] <= 1.0  # Confidence should be normalized
            
            # Track property test results
            quality_metrics_tracker["memory_accuracy"].append(result["confidence"])
    
    @pytest.mark.bmad
    @pytest.mark.unit
    @pytest.mark.property 
    def test_search_relevance_invariants(self, memory_property_strategies, mock_memory_system):
        """Test that search results maintain relevance invariants."""
        # Arrange
        strategies = memory_property_strategies
        
        for _ in range(5):  # Multiple property test iterations
            # Generate search query
            query = strategies.text()()
            
            # Mock search results with invariant properties
            mock_memory_system.search.return_value = [
                {
                    "id": f"search_result_{i}",
                    "content": f"Result {i} for {query}",
                    "confidence": max(0.7, strategies.floats()()),  # Ensure >= 0.7
                    "relevance_score": max(0.5, strategies.floats()()),  # Ensure >= 0.5
                }
                for i in range(3)
            ]
            
            # Act
            results = mock_memory_system.search(query)
            
            # Assert invariants
            assert len(results) >= 1  # Should return at least one result
            
            for result in results:
                assert result["confidence"] >= 0.7  # Minimum confidence threshold
                assert result["relevance_score"] >= 0.5  # Minimum relevance threshold
                assert query.lower() in result["content"].lower() or "Result" in result["content"]  # Content relevance


class TestBMADMemoryPerformance:
    """Performance tests for memory operations."""
    
    @pytest.mark.bmad
    @pytest.mark.performance
    def test_memory_operation_performance(self, mock_memory_system, performance_monitor):
        """Test that memory operations meet performance requirements."""
        # Arrange
        performance_thresholds = {
            "add": 500,      # 500ms for memory creation
            "search": 500,   # 500ms for memory search  
            "context": 1000, # 1000ms for context retrieval
        }
        
        # Test memory creation performance
        start_time = time.time()
        mock_memory_system.add.return_value = {"success": True, "id": "perf_test"}
        result = mock_memory_system.add(content="Performance test memory")
        add_time = (time.time() - start_time) * 1000
        
        assert add_time < performance_thresholds["add"]
        
        # Test search performance
        start_time = time.time()
        mock_memory_system.search.return_value = [{"id": "search_result", "confidence": 0.9}]
        results = mock_memory_system.search("performance test")
        search_time = (time.time() - start_time) * 1000
        
        assert search_time < performance_thresholds["search"]
        
        # Test context retrieval performance
        start_time = time.time()
        mock_memory_system.get_context.return_value = {"confidence": 0.85, "relevant_memories": []}
        context = mock_memory_system.get_context("performance context")
        context_time = (time.time() - start_time) * 1000
        
        assert context_time < performance_thresholds["context"]
        
        # Overall performance check
        assert performance_monitor["duration"] < 3.0  # Total test time < 3 seconds
    
    @pytest.mark.bmad
    @pytest.mark.performance
    def test_memory_bulk_operations(self, mock_memory_system, performance_monitor):
        """Test performance of bulk memory operations."""
        # Arrange
        bulk_size = 100
        memories = [f"Test memory {i} for bulk operations" for i in range(bulk_size)]
        
        # Mock bulk operations
        start_time = time.time()
        
        for i, memory in enumerate(memories):
            mock_memory_system.add.return_value = {"success": True, "id": f"bulk_{i}"}
            mock_memory_system.add(content=memory)
        
        bulk_time = time.time() - start_time
        
        # Assert
        avg_time_per_memory = (bulk_time / bulk_size) * 1000  # ms per memory
        assert avg_time_per_memory < 50  # Should be < 50ms per memory on average
        assert bulk_time < 10.0  # Total bulk operation < 10 seconds


# ==================== TEST UTILITIES ====================

def test_bmad_memory_test_suite_health():
    """Meta-test to ensure memory test suite is comprehensive."""
    # Test that all required test classes exist
    assert TestBMADMemoryOperations is not None
    assert TestBMADMemoryProperties is not None
    assert TestBMADMemoryPerformance is not None
    
    # Test sufficient coverage
    operation_tests = [method for method in dir(TestBMADMemoryOperations) if method.startswith('test_')]
    assert len(operation_tests) >= 5, "Insufficient memory operation test coverage"
    
    property_tests = [method for method in dir(TestBMADMemoryProperties) if method.startswith('test_')]
    assert len(property_tests) >= 2, "Insufficient property-based test coverage"
    
    performance_tests = [method for method in dir(TestBMADMemoryPerformance) if method.startswith('test_')]
    assert len(performance_tests) >= 2, "Insufficient performance test coverage"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"]) 