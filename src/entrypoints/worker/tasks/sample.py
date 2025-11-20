"""
Sample Task Handlers (Entry Point)

Example worker task handlers demonstrating the @task decorator pattern.
Delegates to ItemService in service layer.
"""
from typing import Any, Dict

from loguru import logger

from domain.value_objects.item_enums import ItemStatus
from entrypoints.worker.dependencies import WorkerDependencies
from entrypoints.worker.task_registry import task
from service_layer.application.item_service import ItemService


@task
async def process_item(data: Dict[str, Any]) -> None:
    """
    Process item task (Entry Point)

    Example task that creates a new item via service layer (Write example).

    Args:
        data: Task payload
            - name: Item name (required)
            - description: Item description (optional)
            - metadata: Additional metadata (optional)

    Example message body:
        {
            "task_type": "process_item",
            "data": {
                "name": "New Item",
                "description": "Created by worker"
            }
        }
    """
    db_client = WorkerDependencies.get_db_client()
    service = ItemService(db_client)

    name = data.get("name", "Unnamed Item")
    description = data.get("description")
    metadata = data.get("metadata", {})

    metadata["created_by"] = "worker"
    metadata["task_type"] = "process_item"

    item_id = await service.create_item(
        name=name,
        description=description,
        status=ItemStatus.ACTIVE,
        metadata=metadata,
    )

    logger.info(f"Task process_item completed: created item {item_id}")
