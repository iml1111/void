"""
Sample Job Handlers (Entry Point)

Example CLI job handlers demonstrating the @job decorator pattern.
"""
from loguru import logger

from entrypoints.cli.dependencies import CLIDependencies
from entrypoints.cli.job_registry import job
from service_layer.application.item_service import ItemService


@job
async def process_item(item_id: str) -> None:
    """
    Sample job: Process a specific item by ID

    Demonstrates get_item (Read) usage pattern.

    Example:
        ./void run job process-item --item-id 507f1f77bcf86cd799439011
    """
    logger.info(f"Starting process_item job for item_id: {item_id}")

    db_client = CLIDependencies.get_db_client()
    service = ItemService(db_client)

    item = await service.get_item(item_id)
    logger.info(f"Processing item: {item.name} (status: {item.status})")

    # Add your processing logic here
    logger.info("Item processing completed")
