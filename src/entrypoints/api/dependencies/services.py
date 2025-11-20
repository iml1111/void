"""
Service Dependencies

Provides access to application services with dependency injection.
"""
from fastapi import Depends
from adapters.mongodb.client import MongoDBClient
from service_layer.application.item_service import ItemService
from .clients import get_db_client


def get_item_service(
    db_client: MongoDBClient = Depends(get_db_client)
) -> ItemService:
    """
    Get Item Service dependency

    Args:
        db_client: MongoDB client (injected)

    Returns:
        ItemService: Item service instance
    """
    return ItemService(db_client)
