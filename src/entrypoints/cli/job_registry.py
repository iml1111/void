"""
Job Registry Module

Provides decorator-based job handler registration for CLI jobs.
Mirrors TaskRegistry pattern from Worker entrypoint.
"""
from typing import Callable, Dict, Optional
from functools import wraps


class JobRegistry:
    """
    Job handler registry for dynamic routing

    Mirrors TaskRegistry pattern from Worker entrypoint.
    Manages registration and lookup of job handlers marked with @job decorator.
    """

    _handlers: Dict[str, Callable] = {}

    @classmethod
    def register(cls, job_name: str, handler: Callable) -> None:
        """
        Register job handler

        Args:
            job_name: Job identifier (function name)
            handler: Async job handler function
        """
        if job_name in cls._handlers:
            raise ValueError(f"Job already registered: {job_name}")
        cls._handlers[job_name] = handler

    @classmethod
    def get(cls, job_name: str) -> Optional[Callable]:
        """
        Get registered handler by job name

        Args:
            job_name: Job identifier
        """
        return cls._handlers.get(job_name)

    @classmethod
    def list_jobs(cls) -> list[str]:
        """
        List all registered job names
        """
        return list(cls._handlers.keys())

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered handlers

        Used for testing only.
        """
        cls._handlers.clear()


def job(func: Callable) -> Callable:
    """
    Decorator for marking job handler functions

    Automatically uses function name as job name.
    All job handlers must be async functions with no parameters.

    Args:
        func: Async job handler function (no parameters)

    Example:
        @job
        async def cleanup_items() -> None:
            # Clean up old items...
            pass
    """
    # Use function name as job name
    func._job_name = func.__name__
    func._is_job_handler = True

    @wraps(func)
    async def wrapper():
        return await func()

    return wrapper
