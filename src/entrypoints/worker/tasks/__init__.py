"""
Task Handlers (Entry Point)

Worker task handlers that delegate to Service Layer.
Similar to FastAPI route handlers that call services.
"""
from loguru import logger
from entrypoints.worker.task_registry import TaskRegistry

# Import all task modules
from . import sample

# All task modules
TASK_MODULES = [sample]


def register_all_tasks() -> None:
    """
    Auto-discover and register all task handlers

    Scans all task modules and registers functions marked with @task.
    Similar to FastAPI's app.include_router() pattern.
    """
    for module in TASK_MODULES:
        module_name = module.__name__.split('.')[-1]

        # Scan module for task handlers
        for name in dir(module):
            func = getattr(module, name)
            if callable(func) and hasattr(func, '_is_task_handler'):
                task_name = func._task_name
                TaskRegistry.register(task_name, func)
                logger.info(
                    f"Registered task: {task_name} "
                    f"(module={module_name}, func={name})"
                )
