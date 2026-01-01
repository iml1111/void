"""
Job Handlers (Entry Point)

CLI job handlers that delegate to Service Layer.
Similar to Worker task handlers pattern.
"""
from typing import Callable

import click
from loguru import logger

from entrypoints.cli.job_registry import JobRegistry, create_job_command
from . import sample


# List of all job modules
JOB_MODULES = [
    sample,
]


def register_all_jobs(
    job_group: click.Group,
    initialize_deps: Callable,
    cleanup_deps: Callable
) -> None:
    """
    Auto-discover and register all job handlers as Click commands

    Scans all job modules for functions decorated with @job.
    Creates Click commands with auto-generated options from function signature.

    Args:
        job_group: Click Group to add commands to
        initialize_deps: Dependency initialization function
        cleanup_deps: Dependency cleanup function
    """
    for module in JOB_MODULES:
        module_name = module.__name__.split('.')[-1]

        for name in dir(module):
            func = getattr(module, name)
            if callable(func) and hasattr(func, '_is_job_handler'):
                # Create Click command from handler
                cmd = create_job_command(func, initialize_deps, cleanup_deps)
                job_group.add_command(cmd)

                # Register in JobRegistry for programmatic access
                JobRegistry.register(func._job_name, func)

                logger.debug(
                    f"Registered job: {cmd.name} "
                    f"(module={module_name})"
                )
