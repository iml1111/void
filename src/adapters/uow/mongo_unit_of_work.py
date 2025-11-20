"""
MongoDB Unit of Work Implementation (Adapter Layer)

Manages MongoDB transaction lifecycle using Motor's ClientSession.
Creates session-aware repositories that share the same transaction.
"""
from typing import Optional
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClientSession
from adapters.mongodb.client import MongoDBClient
from adapters.mongodb.collections.item_adapter import ItemAdapter
from adapters.repositories.mongodb.item import MongoItemRepository
from domain.ports.unit_of_work import AbstractUnitOfWork


class MongoUnitOfWork(AbstractUnitOfWork):
    """
    MongoDB implementation of Unit of Work pattern

    Manages MongoDB transaction lifecycle using Motor's ClientSession.
    Creates session-aware repositories that share the same transaction.

    Design:
        1. __aenter__: Start session and transaction
        2. Create session-aware adapters
        3. Instantiate repositories with adapters
        4. __aexit__: Commit or rollback based on exception

    Usage:
        async with MongoUnitOfWork(db_client) as uow:
            item_id = await uow.item_repo.create(entity)
            await uow.item_repo.update(entity2)
            await uow.commit()  # Explicit commit
        # Auto-rollback if commit not called or exception raised

    Requirements:
        - MongoDB Replica Set (required for transactions)
    """

    def __init__(self, db_client: MongoDBClient):
        """
        Initialize UoW with MongoDB client

        Args:
            db_client: MongoDBClient instance
        """
        self._db_client = db_client
        self._session: Optional[AsyncIOMotorClientSession] = None

    async def __aenter__(self):
        """
        Enter transaction context

        1. Start Motor ClientSession
        2. Start transaction
        3. Create session-aware adapters
        4. Instantiate repositories with adapters

        Returns:
            self (with initialized repositories)
        """
        # Start session and transaction
        self._session = await self._db_client.client.start_session()
        self._session.start_transaction()

        logger.debug("Started MongoDB transaction")

        # Create session-aware adapters
        item_adapter = ItemAdapter(self._db_client.db, session=self._session)

        # Instantiate repositories (all share same session)
        self.item_repo = MongoItemRepository(item_adapter)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit transaction context

        Rollback on exception or if commit not called.
        Always end session for cleanup.

        Args:
            exc_type: Exception type (None if no exception)
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        try:
            if exc_type is not None:
                # Exception occurred - rollback
                await self.rollback()
                logger.warning(f"Transaction rolled back due to exception: {exc_type.__name__}")
            else:
                # No exception, but commit not called - rollback (safe default)
                await self.rollback()
                logger.debug("Transaction rolled back (no explicit commit)")
        finally:
            # Always end session
            if self._session:
                self._session.end_session()
                logger.debug("Ended MongoDB session")

    async def commit(self):
        """
        Commit transaction explicitly

        Raises:
            RuntimeError: If no active session
            Exception: If commit fails
        """
        if self._session is None:
            raise RuntimeError("No active session to commit")

        await self._session.commit_transaction()
        logger.info("Transaction committed successfully")

    async def rollback(self):
        """
        Rollback transaction

        Idempotent - safe to call multiple times.

        Raises:
            Exception: If rollback fails
        """
        if self._session is None:
            return  # No active session, nothing to rollback

        if self._session.in_transaction:
            await self._session.abort_transaction()
            logger.debug("Transaction aborted")
