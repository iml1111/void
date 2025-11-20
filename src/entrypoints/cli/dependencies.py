"""
CLI Dependencies

Dependency injection for CLI components and job handlers.
"""
from typing import Optional, Callable
from config import Config
from adapters.mongodb.client import MongoDBClient
from adapters.uow.mongo_unit_of_work import MongoUnitOfWork
from domain.ports.unit_of_work import AbstractUnitOfWork


class CLIDependencies:
    """
    Global dependency container for CLI job handlers

    Initialized once at CLI startup, shared across all job handlers.
    Similar to WorkerDependencies pattern.

    Example:
        # In CLI startup
        CLIDependencies.initialize(config)

        # In job handler
        db_client = CLIDependencies.get_db_client()
    """

    _config: Optional[Config] = None
    _db_client: Optional[MongoDBClient] = None

    @classmethod
    def initialize(cls, config: Config) -> None:
        """
        Initialize all dependencies

        Args:
            config: Config instance
        """
        cls._config = config
        cls._db_client = MongoDBClient(
            uri=config.mongodb_uri,
            db_name=config.mongodb_name
        )

    @classmethod
    def get_config(cls) -> Config:
        """Get config instance"""
        if cls._config is None:
            raise RuntimeError("Dependencies not initialized. Call initialize() first.")
        return cls._config

    @classmethod
    def get_db_client(cls) -> MongoDBClient:
        """Get MongoDB client instance"""
        if cls._db_client is None:
            raise RuntimeError("Dependencies not initialized. Call initialize() first.")
        return cls._db_client

    @classmethod
    def get_uow_factory(cls) -> Callable[[], AbstractUnitOfWork]:
        """
        Get UnitOfWork factory

        Returns a factory function that creates MongoUnitOfWork instances.

        Returns:
            Factory function that creates MongoUnitOfWork instances
        """
        db_client = cls.get_db_client()

        def create_uow() -> AbstractUnitOfWork:
            return MongoUnitOfWork(db_client)

        return create_uow

    @classmethod
    def clear(cls) -> None:
        """Clear all dependencies"""
        if cls._db_client:
            cls._db_client.close()
        cls._config = None
        cls._db_client = None
