"""
Graceful Error Handling Framework for Mem0 Memory System

Provides standardized error handling, retry policies, circuit breaker pattern,
and partial-success response handling for robust memory operations.
"""

import logging
import time
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, List, Union, Type
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationStatus(Enum):
    """Operation completion status"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    RETRYING = "retrying"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ErrorDetail:
    """Detailed error information"""
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_exception(cls, exc: Exception, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                      context: Optional[Dict[str, Any]] = None) -> 'ErrorDetail':
        """Create ErrorDetail from an exception"""
        return cls(
            error_type=type(exc).__name__,
            error_message=str(exc),
            severity=severity,
            stack_trace=traceback.format_exc(),
            context=context or {}
        )


@dataclass
class OperationResult:
    """Standardized operation result with error handling"""
    status: OperationStatus
    success: bool
    data: Any = None
    errors: List[ErrorDetail] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    retry_count: int = 0
    
    def add_error(self, error: Union[ErrorDetail, Exception], 
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  context: Optional[Dict[str, Any]] = None):
        """Add an error to the result"""
        if isinstance(error, Exception):
            error = ErrorDetail.from_exception(error, severity, context)
        self.errors.append(error)
        
        # Update status based on error severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.status = OperationStatus.FAILURE
            self.success = False
        elif not self.success and error.severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM]:
            self.status = OperationStatus.PARTIAL_SUCCESS
    
    def add_warning(self, message: str):
        """Add a warning to the result"""
        self.warnings.append(message)
    
    def is_success(self) -> bool:
        """Check if operation was successful"""
        return self.status == OperationStatus.SUCCESS
    
    def is_partial_success(self) -> bool:
        """Check if operation had partial success"""
        return self.status == OperationStatus.PARTIAL_SUCCESS
    
    def has_critical_errors(self) -> bool:
        """Check if operation has critical errors"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)


@dataclass
class RetryConfig:
    """Configuration for retry policies"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (ConnectionError, TimeoutError, Exception)
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)  # Add ±25% jitter
            
        return delay


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.RLock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception(f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        return (self.last_failure_time and 
                datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.reset_timeout))
    
    def _on_success(self):
        """Handle successful operation"""
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"


class ErrorHandler:
    """Main error handling orchestrator"""
    
    def __init__(self, retry_config: Optional[RetryConfig] = None,
                 circuit_breaker: Optional[CircuitBreaker] = None):
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = circuit_breaker
        
    def execute_with_handling(self, operation: Callable, operation_name: str,
                            context: Optional[Dict[str, Any]] = None) -> OperationResult:
        """Execute operation with comprehensive error handling"""
        start_time = time.time()
        result = OperationResult(status=OperationStatus.SUCCESS, success=True)
        result.metadata["operation_name"] = operation_name
        result.metadata["context"] = context or {}
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Apply circuit breaker if configured
                if self.circuit_breaker:
                    data = self.circuit_breaker.call(operation)
                else:
                    data = operation()
                
                result.data = data
                result.execution_time = time.time() - start_time
                result.retry_count = attempt
                result.status = OperationStatus.SUCCESS  # Ensure status is SUCCESS
                result.success = True
                
                if attempt > 0:
                    result.add_warning(f"Operation succeeded after {attempt} retries")
                
                logger.info(f"Operation '{operation_name}' completed successfully"
                           f"{f' after {attempt} retries' if attempt > 0 else ''}")
                return result
                
            except Exception as e:
                result.retry_count = attempt
                
                # Check if this is the last attempt
                is_last_attempt = attempt == self.retry_config.max_retries
                
                # Determine error severity
                severity = self._classify_error_severity(e)
                
                # Add error details
                error_context = {
                    "attempt": attempt + 1,
                    "max_attempts": self.retry_config.max_retries + 1,
                    "operation_name": operation_name
                }
                error_context.update(context or {})
                
                result.add_error(e, severity, error_context)
                
                # Log the error using logger.exception for full stack trace
                logger.exception(f"Operation '{operation_name}' failed on attempt {attempt + 1}: {e}")
                
                # Check if error is retryable
                if (not is_last_attempt and 
                    isinstance(e, self.retry_config.retryable_exceptions) and
                    severity != ErrorSeverity.CRITICAL):
                    
                    delay = self.retry_config.get_delay(attempt)
                    result.status = OperationStatus.RETRYING
                    
                    logger.warning(f"Retrying operation '{operation_name}' in {delay:.2f}s "
                                 f"(attempt {attempt + 2}/{self.retry_config.max_retries + 1})")
                    
                    time.sleep(delay)
                    continue
                else:
                    # Final failure
                    result.status = OperationStatus.FAILURE
                    result.success = False
                    result.execution_time = time.time() - start_time
                    
                    logger.error(f"Operation '{operation_name}' failed permanently after "
                               f"{attempt + 1} attempts")
                    break
        
        return result
    
    async def execute_with_handling_async(self, operation: Callable, operation_name: str,
                                        context: Optional[Dict[str, Any]] = None) -> OperationResult:
        """Async version of execute_with_handling"""
        start_time = time.time()
        result = OperationResult(status=OperationStatus.SUCCESS, success=True)
        result.metadata["operation_name"] = operation_name
        result.metadata["context"] = context or {}
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Apply circuit breaker if configured (run in thread for sync circuit breaker)
                if self.circuit_breaker:
                    data = await asyncio.to_thread(self.circuit_breaker.call, operation)
                else:
                    if asyncio.iscoroutinefunction(operation):
                        data = await operation()
                    else:
                        data = await asyncio.to_thread(operation)
                
                result.data = data
                result.execution_time = time.time() - start_time
                result.retry_count = attempt
                result.status = OperationStatus.SUCCESS  # Ensure status is SUCCESS
                result.success = True
                
                if attempt > 0:
                    result.add_warning(f"Operation succeeded after {attempt} retries")
                
                logger.info(f"Async operation '{operation_name}' completed successfully"
                           f"{f' after {attempt} retries' if attempt > 0 else ''}")
                return result
                
            except Exception as e:
                result.retry_count = attempt
                
                # Check if this is the last attempt
                is_last_attempt = attempt == self.retry_config.max_retries
                
                # Determine error severity
                severity = self._classify_error_severity(e)
                
                # Add error details
                error_context = {
                    "attempt": attempt + 1,
                    "max_attempts": self.retry_config.max_retries + 1,
                    "operation_name": operation_name
                }
                error_context.update(context or {})
                
                result.add_error(e, severity, error_context)
                
                # Log the error using logger.exception for full stack trace
                logger.exception(f"Async operation '{operation_name}' failed on attempt {attempt + 1}: {e}")
                
                # Check if error is retryable
                if (not is_last_attempt and 
                    isinstance(e, self.retry_config.retryable_exceptions) and
                    severity != ErrorSeverity.CRITICAL):
                    
                    delay = self.retry_config.get_delay(attempt)
                    result.status = OperationStatus.RETRYING
                    
                    logger.warning(f"Retrying async operation '{operation_name}' in {delay:.2f}s "
                                 f"(attempt {attempt + 2}/{self.retry_config.max_retries + 1})")
                    
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Final failure
                    result.status = OperationStatus.FAILURE
                    result.success = False
                    result.execution_time = time.time() - start_time
                    
                    logger.error(f"Async operation '{operation_name}' failed permanently after "
                               f"{attempt + 1} attempts")
                    break
        
        return result
    
    def _classify_error_severity(self, error: Exception) -> ErrorSeverity:
        """Classify error severity based on exception type"""
        error_type = type(error).__name__
        
        # Critical errors that should not be retried
        critical_errors = [
            "PermissionError", "SecurityError", "AuthenticationError",
            "ValidationError", "ValueError", "TypeError"
        ]
        
        # High severity errors
        high_severity_errors = [
            "FileNotFoundError", "DatabaseError", "IntegrityError"
        ]
        
        # Medium severity errors (default for most network/temporary issues)
        medium_severity_errors = [
            "ConnectionError", "TimeoutError", "RequestException"
        ]
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_severity_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_severity_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW


def with_error_handling(operation_name: str = None, 
                       retry_config: Optional[RetryConfig] = None,
                       circuit_breaker: Optional[CircuitBreaker] = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        handler = ErrorHandler(retry_config, circuit_breaker)
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            def operation():
                return func(*args, **kwargs)
            return handler.execute_with_handling(operation, op_name)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            async def operation():
                return await func(*args, **kwargs)
            return await handler.execute_with_handling_async(operation, op_name)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator 