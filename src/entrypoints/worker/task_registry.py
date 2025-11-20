"""
Task Registry Module

Provides decorator-based task handler registration for extensible task routing
"""
from typing import Callable, Dict, Optional
from functools import wraps


class TaskRegistry:
    """
    Task handler registry for dynamic routing

    Provides centralized registry for task handlers with automatic discovery
    """

    _handlers: Dict[str, Callable] = {}

    @classmethod
    def register(cls, task_name: str, handler: Callable) -> None:
        """
        Register task handler (bound method)

        Args:
            task_name: Task name identifier
            handler: Task handler function (bound method)
        """
        if task_name in cls._handlers:
            raise ValueError(f"Task handler already registered: {task_name}")

        cls._handlers[task_name] = handler

    @classmethod
    def get(cls, task_name: str) -> Optional[Callable]:
        """
        Get registered handler by task name

        Args:
            task_name: Task name identifier
        """
        return cls._handlers.get(task_name)

    @classmethod
    def list_tasks(cls) -> list[str]:
        """
        List all registered task names
        """
        return list(cls._handlers.keys())

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered handlers

        Used for testing and cleanup
        """
        cls._handlers.clear()


def task(func: Callable) -> Callable:
    """
    Decorator for marking task handler functions

    Automatically uses function name as task name.
    Similar to FastAPI's @router.get() decorator pattern.

    Args:
        func: Task handler function

    Note:
        - Function name becomes the task name
        - Actual registration happens in register_all_tasks()
        - Handler must accept (data: Dict[str, Any]) -> None signature

    Example:
        @task
        async def process_item(data: Dict[str, Any]) -> None:
            item_id = data['item_id']
            # Process item...
    """
    # Use function name as task name
    func._task_name = func.__name__
    func._is_task_handler = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
