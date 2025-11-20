"""
Item Service (Application Layer)

Orchestrates item business operations using domain entities and adapters.
"""
from typing import Optional

from adapters.mongodb.client import MongoDBClient
from adapters.mongodb.collections.item_adapter import ItemAdapter
from adapters.repositories.mongodb.item import MongoItemRepository
from adapters.uow.mongo_unit_of_work import MongoUnitOfWork
from domain.entities.item import ItemEntity
from domain.value_objects.item_enums import ItemStatus
from service_layer.exceptions import ItemNotFoundError, ItemValidationError


class ItemService:
    """
    Item management service

    Orchestrates item CRUD operations with transaction support.
    Uses Unit of Work pattern for consistent database operations.

    Example:
        service = ItemService(db_client)
        item_id = await service.create_item(name="New Item", description="...")
        item = await service.get_item(item_id)
    """

    def __init__(self, db_client: MongoDBClient):
        """
        Initialize item service

        Args:
            db_client: MongoDB client for database operations
        """
        self._db_client = db_client
        self._item_repo = MongoItemRepository(
            ItemAdapter(db_client.db, session=None)
        )

    async def create_item(
        self,
        name: str,
        description: Optional[str] = None,
        status: ItemStatus = ItemStatus.ACTIVE,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Create new item

        Args:
            name: Item name
            description: Item description (optional)
            status: Item status (default: ACTIVE)
            metadata: Additional metadata (optional)

        Returns:
            Created item ID

        Raises:
            ItemValidationError: If item data is invalid
        """
        try:
            # Create entity
            entity = ItemEntity.create(
                name=name,
                description=description,
                status=status,
                metadata=metadata
            )
        except ValueError as e:
            raise ItemValidationError(str(e))

        # Persist with transaction
        async with MongoUnitOfWork(self._db_client) as uow:
            item_id = await uow.item_repo.create(entity)
            await uow.commit()
            return item_id

    async def get_item(self, item_id: str) -> ItemEntity:
        """
        Get item by ID

        Args:
            item_id: Item ID

        Returns:
            Item entity

        Raises:
            ItemNotFoundError: If item does not exist
        """
        item = await self._item_repo.get_by_id(item_id)

        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")

        return item
