"""
Job Registry Module

Provides decorator-based job handler registration for CLI jobs.
Supports argument passing via Click options auto-generated from function signature.
"""
import inspect
import asyncio
from typing import Callable, Dict, Optional

import click


class JobRegistry:
    """
    Job handler registry for dynamic routing

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
    Stores function signature for Click option generation.

    Args:
        func: Async job handler function

    Example:
        @job
        async def process_item(item_id: str) -> None:
            # Process item...
            pass
    """
    func._job_name = func.__name__
    func._is_job_handler = True
    func._job_signature = inspect.signature(func)
    return func


def create_job_command(
    handler: Callable,
    initialize_deps: Callable,
    cleanup_deps: Callable
) -> click.Command:
    """
    Create Click Command from job handler

    Analyzes function signature and generates Click options.
    All arguments are treated as STRING type.

    Args:
        handler: Decorated async job handler
        initialize_deps: Dependency initialization function
        cleanup_deps: Dependency cleanup function

    Returns:
        click.Command: Configured Click command
    """
    sig = handler._job_signature

    # Build Click options from signature (all STRING type)
    params = []
    for name, param in sig.parameters.items():
        has_default = param.default is not inspect.Parameter.empty
        params.append(click.Option(
            ['--' + name.replace('_', '-')],
            type=click.STRING,
            required=not has_default,
            default=param.default if has_default else None,
            help=f"{name} parameter",
        ))

    def callback(**kwargs):
        """Synchronous wrapper for async handler"""
        async def run():
            initialize_deps()
            try:
                await handler(**kwargs)
            finally:
                cleanup_deps()
        asyncio.run(run())

    # Command name: snake_case -> kebab-case
    cmd_name = handler._job_name.replace('_', '-')

    return click.Command(
        name=cmd_name,
        callback=callback,
        params=params,
        help=handler.__doc__,
    )
