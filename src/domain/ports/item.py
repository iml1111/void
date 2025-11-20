"""Item Repository Interface (Port)"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.item import ItemEntity


class ItemRepository(ABC):
    """
    Repository interface for Item entity

    Defines the contract for Item persistence operations.
    All methods are async for non-blocking I/O.
    """

    @abstractmethod
    async def create(self, entity: ItemEntity) -> str:
        """
        Create new item

        Args:
            entity: ItemEntity to persist

        Returns:
            Created item ID (str)
        """
        pass

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[ItemEntity]:
        """
        Retrieve item by ID

        Args:
            item_id: Item ID to search for

        Returns:
            ItemEntity if found, None otherwise
        """
        pass
