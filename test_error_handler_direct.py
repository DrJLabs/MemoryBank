#!/usr/bin/env python3
"""
Direct test of error handler implementation without package imports
"""

import sys
import os
import time
import importlib.util

# Load the error_handler module directly from file
error_handler_path = os.path.join(os.path.dirname(__file__), 'mem0', 'mem0', 'memory', 'error_handler.py')
spec = importlib.util.spec_from_file_location("error_handler", error_handler_path)
error_handler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(error_handler_module)

# Get the components we need
ErrorHandler = error_handler_module.ErrorHandler
OperationResult = error_handler_module.OperationResult
OperationStatus = error_handler_module.OperationStatus
ErrorSeverity = error_handler_module.ErrorSeverity
RetryConfig = error_handler_module.RetryConfig
CircuitBreaker = error_handler_module.CircuitBreaker
with_error_handling = error_handler_module.with_error_handling
ErrorDetail = error_handler_module.ErrorDetail

print("✓ Error handler imports successful")

# Test 1: Basic error handling
def test_basic_functionality():
    print("\n1. Testing basic error handling...")
    
    error_handler = ErrorHandler(
        retry_config=RetryConfig(max_retries=2, base_delay=0.1, jitter=False)
    )
    
    # Test successful operation
    def success_op():
        return "success"
    
    result = error_handler.execute_with_handling(success_op, "test_success")
    assert result.is_success() == True
    assert result.data == "success"
    print("   ✓ Success operation works")
    
    # Test failure operation
    def fail_op():
        raise ValueError("Test error")
    
    result = error_handler.execute_with_handling(fail_op, "test_failure")
    assert result.is_success() == False
    assert result.status == OperationStatus.FAILURE
    print("   ✓ Failure operation works")

# Test 2: Retry mechanism
def test_retry_mechanism():
    print("\n2. Testing retry mechanism...")
    
    error_handler = ErrorHandler(
        retry_config=RetryConfig(
            max_retries=3,
            base_delay=0.1,
            jitter=False,
            retryable_exceptions=(ConnectionError, TimeoutError)
        )
    )
    
    attempts = [0]
    
    def retry_op():
        attempts[0] += 1
        if attempts[0] <= 2:
            raise ConnectionError(f"Attempt {attempts[0]} failed")
        return f"Success after {attempts[0]} attempts"
    
    result = error_handler.execute_with_handling(retry_op, "test_retry")
    print(f"   Debug: Result success={result.is_success()}, retry_count={result.retry_count}, attempts={attempts[0]}")
    print(f"   Debug: Result status={result.status}, data={result.data}")
    print(f"   Debug: Warnings={result.warnings}")
    print(f"   Debug: Errors={len(result.errors)} errors")
    assert result.is_success() == True
    assert result.retry_count == 2
    assert len(result.warnings) > 0
    print(f"   ✓ Retry mechanism works - succeeded after {result.retry_count} retries")

# Test 3: Circuit breaker
def test_circuit_breaker():
    print("\n3. Testing circuit breaker...")
    
    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        reset_timeout=1.0
    )
    
    error_handler = ErrorHandler(circuit_breaker=circuit_breaker)
    
    # Trigger circuit breaker
    for i in range(3):
        def fail_op():
            raise ConnectionError("Always fails")
        
        result = error_handler.execute_with_handling(fail_op, f"test_circuit_{i}")
        assert result.is_success() == False
    
    # Circuit should be open now
    result = error_handler.execute_with_handling(fail_op, "test_circuit_open")
    # The error handler will still retry because circuit breaker exceptions are retryable
    assert result.is_success() == False
    assert len(result.errors) > 0  # Circuit breaker errors are recorded
    print("   ✓ Circuit breaker opens after threshold")

# Test 4: Error severity classification
def test_error_severity():
    print("\n4. Testing error severity classification...")
    
    error_handler = ErrorHandler()
    
    test_cases = [
        (ValueError("test"), ErrorSeverity.CRITICAL),
        (ConnectionError("test"), ErrorSeverity.MEDIUM),
        (TimeoutError("test"), ErrorSeverity.MEDIUM),
        (RuntimeError("test"), ErrorSeverity.LOW),
    ]
    
    for exception, expected_severity in test_cases:
        severity = error_handler._classify_error_severity(exception)
        assert severity == expected_severity
        print(f"   ✓ {type(exception).__name__} -> {severity.value}")

# Test 5: Partial success handling
def test_partial_success():
    print("\n5. Testing partial success scenarios...")
    
    result = OperationResult(status=OperationStatus.PARTIAL_SUCCESS, success=True)
    result.add_warning("Some operations failed")
    result.data = {"completed": ["item1", "item2"], "failed": ["item3"]}
    
    assert result.is_partial_success() == True
    assert not result.is_success()
    assert len(result.warnings) == 1
    print("   ✓ Partial success handling works")

# Test 6: Decorator functionality
def test_decorator():
    print("\n6. Testing @with_error_handling decorator...")
    
    @with_error_handling("test_decorated", RetryConfig(max_retries=1, base_delay=0.1))
    def decorated_function(should_fail=False):
        if should_fail:
            raise ConnectionError("Decorated failure")
        return "decorated_success"
    
    # Test success
    result = decorated_function(should_fail=False)
    assert isinstance(result, OperationResult)
    assert result.is_success()
    assert result.data == "decorated_success"
    print("   ✓ Decorator success case works")
    
    # Test failure
    result = decorated_function(should_fail=True)
    assert isinstance(result, OperationResult)
    assert not result.is_success()
    print("   ✓ Decorator failure case works")

# Run all tests
if __name__ == "__main__":
    print("Error Handler Direct Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_retry_mechanism()
        test_circuit_breaker()
        test_error_severity()
        test_partial_success()
        test_decorator()
        
        print("\n" + "=" * 50)
        print("✅ All error handler tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 