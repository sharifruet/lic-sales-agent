"""Retry service with exponential backoff for transient errors."""
import asyncio
import logging
from typing import Callable, TypeVar, Optional, List, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryableError(Exception):
    """Error that should be retried."""
    pass


class NonRetryableError(Exception):
    """Error that should not be retried."""
    pass


class RetryService:
    """Service for retrying operations with exponential backoff."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    async def retry_with_backoff(
        self,
        func: Callable[[], T],
        operation_name: str = "operation",
        retryable_exceptions: Optional[List[Exception]] = None,
        non_retryable_exceptions: Optional[List[Exception]] = None
    ) -> T:
        """
        Retry an async operation with exponential backoff.
        
        Args:
            func: Async function to retry
            operation_name: Name of operation for logging
            retryable_exceptions: List of exception types that should be retried (default: all)
            non_retryable_exceptions: List of exception types that should NOT be retried
        
        Returns:
            Result of the operation
        
        Raises:
            Last exception if all retries fail
        """
        if retryable_exceptions is None:
            retryable_exceptions = [Exception]
        
        last_exception = None
        delay = self.config.initial_delay
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func()
                else:
                    result = func()
                
                # Success - log if retried
                if attempt > 1:
                    logger.info(f"{operation_name} succeeded after {attempt} attempts")
                
                return result
            
            except Exception as e:
                last_exception = e
                
                # Check if this exception should not be retried
                if non_retryable_exceptions:
                    if any(isinstance(e, exc_type) for exc_type in non_retryable_exceptions):
                        logger.warning(f"{operation_name} failed with non-retryable error: {type(e).__name__}")
                        raise
                
                # Check if this exception is retryable
                is_retryable = any(isinstance(e, exc_type) for exc_type in retryable_exceptions)
                
                if not is_retryable:
                    logger.warning(f"{operation_name} failed with non-retryable error: {type(e).__name__}")
                    raise
                
                # Check if we've exhausted retries
                if attempt >= self.config.max_attempts:
                    logger.error(
                        f"{operation_name} failed after {self.config.max_attempts} attempts. "
                        f"Last error: {type(e).__name__}: {str(e)}"
                    )
                    raise
                
                # Calculate delay with exponential backoff
                delay = min(
                    self.config.initial_delay * (self.config.exponential_base ** (attempt - 1)),
                    self.config.max_delay
                )
                
                # Add jitter to prevent thundering herd
                if self.config.jitter:
                    import random
                    jitter_amount = delay * 0.1  # 10% jitter
                    delay = delay + random.uniform(-jitter_amount, jitter_amount)
                    delay = max(0, delay)  # Ensure non-negative
                
                logger.warning(
                    f"{operation_name} failed (attempt {attempt}/{self.config.max_attempts}): "
                    f"{type(e).__name__}. Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise Exception(f"{operation_name} failed after {self.config.max_attempts} attempts")


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[List[Exception]] = None,
    non_retryable_exceptions: Optional[List[Exception]] = None
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Usage:
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        async def my_function():
            ...
    """
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_service = RetryService(
                RetryConfig(
                    max_attempts=max_attempts,
                    initial_delay=initial_delay,
                    max_delay=max_delay
                )
            )
            operation_name = f"{func.__name__}"
            return await retry_service.retry_with_backoff(
                lambda: func(*args, **kwargs),
                operation_name=operation_name,
                retryable_exceptions=retryable_exceptions,
                non_retryable_exceptions=non_retryable_exceptions
            )
        return wrapper
    return decorator

