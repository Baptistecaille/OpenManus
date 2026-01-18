"""Retry handler module with max 3 attempts and error raising."""

from typing import Callable, Any
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from app.exceptions import ToolError
from app.logger import logger


class RetryHandler:
    """Handle retry logic with max 3 attempts and error raising."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        try:
            return self._retry_wrapper(func, args, kwargs)
        except RetryError as e:
            logger.error(f"Function failed after {self.max_retries} retries: {e}")
            raise ToolError(
                f"Operation failed after {self.max_retries} attempts. "
                f"Last error: {str(e)}"
            ) from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def _retry_wrapper(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """Wrapper for retry logic."""
        return func(*args, **kwargs)
