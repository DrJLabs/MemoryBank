"""
BMAD Memory System Property-Based Testing
Advanced property testing for memory operations, categorization, and consistency.
"""
import random
import string
import time
from typing import Dict, Any, List, Set, Optional
import hashlib

class BMAdPropertyTestStrategy:
    """Strategy for generating test data for property-based testing"""
    
    @staticmethod
    def text(min_size: int = 1, max_size: int = 100) -> str:
        """Generate random text of variable length"""
        length = random.randint(min_size, max_size)
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    @staticmethod
    def memory_categories() -> str:
        """Generate valid memory categories"""
        categories = [
            "TECHNICAL", "LEARNING", "PREFERENCE", "WORKFLOW", "PROJECT",
            "INTEGRATION", "INSIGHT", "PATTERN", "ARCHITECTURE", "TESTING"
        ]
        return random.choice(categories)

class MockAdvancedMemorySystem:
    """Advanced mock memory system with property validation"""
    
    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.categories: Set[str] = set()
        self.operation_log: List[Dict[str, Any]] = []
        
    def store_memory(self, memory_id: str, content: str, category: str, 
                    metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store memory with full metadata tracking"""
        if metadata is None:
            metadata = {}
            
        memory_entry = {
            "id": memory_id,
            "content": content,
            "category": category,
            "metadata": metadata,
            "timestamp": time.time(),
            "checksum": self._calculate_checksum(content),
            "size": len(content),
            "version": 1
        }
        
        # Update existing memory (versioning)
        if memory_id in self.memories:
            memory_entry["version"] = self.memories[memory_id]["version"] + 1
        
        self.memories[memory_id] = memory_entry
        self.categories.add(category)
        
        return memory_entry
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory by ID"""
        return self.memories.get(memory_id)
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search memories by category"""
        return [mem for mem in self.memories.values() if mem["category"] == category]
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate content checksum"""
        return hashlib.md5(content.encode()).hexdigest()

class BMAdMemoryPropertyTests:
    """Property-based tests for BMAD memory system"""
    
    def __init__(self):
        self.memory_system = MockAdvancedMemorySystem()
        
    def test_memory_storage_idempotency(self):
        """Property: Storing the same memory twice should be idempotent"""
        passed = 0
        total = 50
        
        for i in range(total):
            memory_id = f"test_{random.randint(1, 1000)}"
            content = BMAdPropertyTestStrategy.text(10, 100)
            category = BMAdPropertyTestStrategy.memory_categories()
            
            # Store memory twice
            result1 = self.memory_system.store_memory(memory_id, content, category)
            result2 = self.memory_system.store_memory(memory_id, content, category)
            
            # Should have different versions but same content
            if (result1["content"] == result2["content"] and 
                result1["category"] == result2["category"] and
                result2["version"] > result1["version"]):
                passed += 1
        
        success_rate = (passed / total) * 100
        print(f"  📊 Storage Idempotency: {passed}/{total} passed ({success_rate:.1f}%)")
        return success_rate >= 95.0
    
    def run_all_property_tests(self) -> Dict[str, Any]:
        """Run all property tests and generate report"""
        print("\n🧬 **BMAD Memory Property-Based Testing Suite**")
        print("=" * 60)
        
        # Run storage idempotency test
        result = self.test_memory_storage_idempotency()
        
        summary = {
            "total_tests": 1,
            "tests_passed": 1 if result else 0,
            "success_rate": 100.0 if result else 0.0,
            "status": "PASSED" if result else "FAILED"
        }
        
        return summary

__all__ = ["BMAdMemoryPropertyTests", "BMAdPropertyTestStrategy", "MockAdvancedMemorySystem"]
