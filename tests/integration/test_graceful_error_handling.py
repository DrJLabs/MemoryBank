#!/usr/bin/env python3
"""
Test script for graceful error handling in Mem0 Memory System
"""

import sys
import os
import time
import unittest
from unittest.mock import Mock, patch

# Add the mem0 module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mem0'))

def test_error_handler_import():
    """Test that we can import the error handling components"""
    try:
        from mem0.memory.error_handler import (
            ErrorHandler, OperationResult, OperationStatus, ErrorSeverity,
            RetryConfig, CircuitBreaker, with_error_handling
        )
        print("✓ Error handling imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_error_handling():
    """Test basic error handling functionality"""
    from mem0.memory.error_handler import ErrorHandler, RetryConfig
    
    retry_config = RetryConfig(
        max_retries=2,
        base_delay=0.1,
        jitter=False
    )
    
    error_handler = ErrorHandler(retry_config=retry_config)
    
    # Test successful operation
    def success_op():
        return "success"
    
    result = error_handler.execute_with_handling(success_op, "test_success")
    
    if result.is_success() and result.data == "success":
        print("✓ Basic error handling test passed")
        return True
    else:
        print("❌ Basic error handling test failed")
        return False

def test_retry_mechanism():
    """Test retry mechanism"""
    from mem0.memory.error_handler import ErrorHandler, RetryConfig
    
    retry_config = RetryConfig(
        max_retries=2,
        base_delay=0.1,
        jitter=False,
        retryable_exceptions=(ConnectionError,)
    )
    
    error_handler = ErrorHandler(retry_config=retry_config)
    
    attempts = [0]
    
    def retry_op():
        attempts[0] += 1
        if attempts[0] < 2:
            raise ConnectionError("Connection failed")
        return "success_after_retry"
    
    result = error_handler.execute_with_handling(retry_op, "test_retry")
    
    if result.is_success() and result.retry_count == 1:
        print("✓ Retry mechanism test passed")
        return True
    else:
        print("❌ Retry mechanism test failed")
        return False

if __name__ == "__main__":
    print("Mem0 Graceful Error Handling - Basic Test Suite")
    print("=" * 50)
    
    tests = [
        test_error_handler_import,
        test_basic_error_handling,
        test_retry_mechanism
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("✅ All basic tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1) 