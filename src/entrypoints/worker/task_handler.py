"""
Task Message Handler

Routes SQS messages to appropriate task handlers using registry
"""
import json
import traceback
from typing import Dict, Any
from loguru import logger

from entrypoints.worker.task_registry import TaskRegistry
from entrypoints.worker.dependencies import WorkerDependencies


class TaskHandler:
    """
    Task message handler using registry-based routing

    Routes messages to registered handlers dynamically via TaskRegistry.
    Handlers are registered via @task decorator in task modules.
    """

    def __init__(self):
        """
        Initialize task handler

        Note:
            Task handlers must be registered before creating TaskHandler instance.
            Call register_all_tasks() in worker startup.
        """
        pass

    async def handle(self, message: Dict[str, Any]) -> None:
        """
        Handle SQS message using registry-based routing

        Args:
            message: Parsed SQS message
                {
                    'body': {
                        'task_type': 'xxx',
                        'data': {...},
                        'metadata': {...}
                    },
                    'receipt_handle': 'xxx',
                    'message_id': 'xxx'
                }
        """
        try:
            # Extract task info
            body = message.get('body', {})
            task_name = body.get('task_type')
            data = body.get('data', {})
            metadata = body.get('metadata', {})
            message_id = message.get('message_id')

            logger.info(
                f"Handling task: name={task_name}, message_id={message_id}",
                extra={
                    "task_name": task_name,
                    "message_id": message_id,
                    "metadata": metadata
                }
            )

            # Get handler from registry
            handler = TaskRegistry.get(task_name)

            if handler is None:
                raise ValueError(
                    f"Unknown task name: {task_name}. "
                    f"Registered tasks: {TaskRegistry.list_tasks()}"
                )

            # Execute handler
            await handler(data)

            logger.info(
                f"Task completed: name={task_name}, message_id={message_id}",
                extra={
                    "task_name": task_name,
                    "message_id": message_id
                }
            )

        except Exception as e:
            logger.error(
                f"Task handling failed: {e}",
                exc_info=True,
                extra={
                    "message_id": message.get('message_id'),
                    "task_name": message.get('body', {}).get('task_type'),
                    "error": str(e)
                }
            )

            # Log error details
            tb_list = traceback.format_list(
                traceback.extract_tb(e.__traceback__)
            )[-3:]
            tb_str = "".join(tb_list)
            tb_str += traceback.format_exception_only(type(e), e)[-1]

            logger.error(
                f"Task error traceback:\n{tb_str}",
                extra={
                    "task_type": message.get('body', {}).get('task_type', 'unknown'),
                    "task_data": json.dumps(
                        message.get('body', {}).get('data', {}),
                        ensure_ascii=False,
                        default=str
                    )
                }
            )

            raise
