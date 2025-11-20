"""
Worker Dependencies

Dependency injection for worker components and task handlers
"""
from typing import Optional, Callable
from config import Config
from adapters.aws import SQSClient, SQSConsumerAdapter
from adapters.mongodb.client import MongoDBClient
from adapters.uow.mongo_unit_of_work import MongoUnitOfWork
from domain.ports.unit_of_work import AbstractUnitOfWork


def get_sqs_client(config: Config) -> SQSClient:
    """
    Get SQS client

    Args:
        config: Application configuration
    """
    return SQSClient(
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_region
    )


def get_sqs_consumer(config: Config) -> SQSConsumerAdapter:
    """
    Get SQS consumer adapter

    Args:
        config: Application configuration
    """
    sqs_client = get_sqs_client(config)

    return SQSConsumerAdapter(
        sqs_client=sqs_client,
        queue_url=config.sqs_queue_url,
        wait_time_seconds=config.sqs_wait_time_seconds
    )


class WorkerDependencies:
    """
    Global dependency container for task handlers

    Initialized once at worker startup, shared across all task handlers.
    Similar to FastAPI's Depends pattern but for background workers.

    Example:
        # In worker startup
        WorkerDependencies.initialize(config)

        # In task handler
        db_client = WorkerDependencies.get_db_client()
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

        Returns a factory function that creates MongoUnitOfWork instances
        for atomic operations across multiple repositories.

        Returns:
            Factory function that creates MongoUnitOfWork instances
        """
        db_client = cls.get_db_client()

        def create_uow() -> AbstractUnitOfWork:
            return MongoUnitOfWork(db_client)

        return create_uow

    @classmethod
    def clear(cls) -> None:
        """Clear all dependencies (for testing)"""
        if cls._db_client:
            cls._db_client.close()
        cls._config = None
        cls._db_client = None
