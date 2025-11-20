"""
Job Handlers (Entry Point)

CLI job handlers that delegate to Service Layer.
Similar to Worker task handlers pattern.
"""
from loguru import logger

from entrypoints.cli.job_registry import JobRegistry
from . import sample


# List of all job modules
JOB_MODULES = [
    sample,
]


def register_all_jobs() -> None:
    """
    Auto-discover and register all job handlers

    Mirrors Worker's register_all_tasks() pattern.
    Scans all job modules for functions decorated with @job.

    Similar to FastAPI's app.include_router() pattern.
    """
    for module in JOB_MODULES:
        module_name = module.__name__.split('.')[-1]

        for name in dir(module):
            func = getattr(module, name)
            if callable(func) and hasattr(func, '_is_job_handler'):
                JobRegistry.register(func._job_name, func)
                logger.info(
                    f"Registered job: {func._job_name} "
                    f"(module={module_name})"
                )
