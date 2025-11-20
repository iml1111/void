"""
Domain Layer - Unit of Work Interface (Port)

Abstract interface for managing atomic transactions across repositories.
Service layer depends on this abstraction, not implementation details.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.ports.item import ItemRepository


class AbstractUnitOfWork(ABC):
    """
    Abstract Unit of Work for managing atomic transactions

    Provides repository access and transaction lifecycle management.
    Service layer depends on this abstraction, not infrastructure.

    Usage:
        async with uow:
            item_id = await uow.item_repo.create(entity)
            await uow.item_repo.update(entity2)
            await uow.commit()  # Explicit commit
        # Auto-rollback on exception

    Design Principles:
        - Service layer infrastructure-agnostic
        - Explicit commit required (safe by default)
        - Auto-rollback on exceptions
        - Repository sharing same transaction session
    """

    # Repository properties (initialized in __aenter__)
    item_repo: 'ItemRepository'

    async def __aenter__(self):
        """
        Enter async context - start transaction

        Returns:
            self (for 'as uow' syntax)
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit async context - commit or rollback

        Args:
            exc_type: Exception type (None if no exception)
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if exc_type is None:
            await self.rollback()  # Safe default: explicit commit required
        else:
            await self.rollback()  # Auto-rollback on exception

    @abstractmethod
    async def commit(self):
        """
        Commit transaction explicitly

        Raises:
            Exception: If commit fails
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        """
        Rollback transaction

        Safe to call multiple times (idempotent).

        Raises:
            Exception: If rollback fails
        """
        raise NotImplementedError
