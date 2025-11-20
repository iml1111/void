"""Worker Entrypoint - SQS Consumer for async task processing"""
from .task_registry import task, TaskRegistry

__all__ = ["task", "TaskRegistry"]
