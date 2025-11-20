"""
MongoDB Client Connection Manager
"""
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase


class MongoDBClient:
    """MongoDB connection manager with connection pool support"""

    def __init__(
        self,
        uri: str,
        db_name: str,
        max_pool_size: int = 50,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 60000
    ):
        """
        Initialize MongoDB client with connection pool settings

        Args:
            uri: MongoDB connection URI
            db_name: Default database name
            max_pool_size: Maximum connections in pool (default: 50)
            min_pool_size: Minimum connections in pool (default: 10)
            max_idle_time_ms: Max idle time before closing connection (default: 60000ms = 1min)
        """
        self._client = AsyncIOMotorClient(
            uri,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms
        )
        self._db_name = db_name

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get raw motor client"""
        return self._client

    @property
    def db(self) -> AgnosticDatabase:
        """Get default database instance"""
        return self.get_database(self._db_name)

    def get_database(self, db_name: str) -> AgnosticDatabase:
        """
        Get database instance

        Args:
            db_name: Database name
        """
        return self._client[db_name]

    def close(self):
        """Close MongoDB connection"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
