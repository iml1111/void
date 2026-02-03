"""
Task Registry Module

Provides decorator-based task handler registration for extensible task routing.
Supports immediate registration at decorator time (auto-discovery pattern).
"""
from typing import Callable, Dict, List, Optional


class TaskRegistry:
    """
    Task handler registry for dynamic routing

    Provides centralized registry for task handlers with automatic discovery.
    """

    _handlers: Dict[str, Callable] = {}

    @classmethod
    def register(cls, task_name: str, handler: Callable) -> None:
        """
        Register task handler

        Args:
            task_name: Task name identifier
            handler: Task handler function

        Note:
            Allows duplicate registration of same handler (idempotent).
            Raises error only if different handler attempts to use same name.
        """
        if task_name in cls._handlers:
            if cls._handlers[task_name] is handler:
                return  # Same handler, idempotent
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
    def get_all_handlers(cls) -> Dict[str, Callable]:
        """
        Get all registered handlers

        Returns:
            Dict of task_name -> handler mappings
        """
        return cls._handlers.copy()

    @classmethod
    def list_tasks(cls) -> List[str]:
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
    Decorator for marking and registering task handler functions

    Immediately registers the handler with TaskRegistry at decoration time.

    Example:
        @task
        async def process_item(data: Dict[str, Any]) -> None:
            item_id = data['item_id']
            # Process item...
    """
    task_name = func.__name__
    TaskRegistry.register(task_name, func)
    func._is_task_handler = True
    func._task_name = task_name
    return func
