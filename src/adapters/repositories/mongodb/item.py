"""MongoDB Item Repository Implementation"""
from typing import Optional

from bson import ObjectId
from loguru import logger

from adapters.mongodb.base import BaseMongoAdapter
from adapters.mongodb.collections.item_adapter import ItemAdapter
from domain.entities.item import ItemEntity
from domain.ports.item import ItemRepository


class MongoItemRepository(ItemRepository):
    """MongoDB implementation of ItemRepository"""

    def __init__(self, adapter: ItemAdapter):
        self._adapter = adapter

    async def create(self, entity: ItemEntity) -> str:
        """
        Create new item

        Args:
            entity: ItemEntity to persist

        Returns:
            Created item ID (str)
        """
        doc = BaseMongoAdapter.prepare_for_insert(entity.to_dict())
        result = await self._adapter.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_id(self, item_id: str) -> Optional[ItemEntity]:
        """
        Retrieve item by ID

        Args:
            item_id: Item ID to search for

        Returns:
            ItemEntity if found, None otherwise
        """
        projection = BaseMongoAdapter.entity_projection(ItemEntity)
        try:
            doc = await self._adapter.find_one({"_id": ObjectId(item_id)}, projection)
        except Exception as e:
            logger.error(f"Invalid item_id format '{item_id}': {e}")
            return None

        if not doc:
            return None

        try:
            entity = ItemEntity.from_dict(doc)
            return entity
        except (ValueError, KeyError) as e:
            logger.error(f"Data validation failed for item_id '{item_id}': {e}")
            raise