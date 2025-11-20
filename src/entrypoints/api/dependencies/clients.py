"""
Client Dependencies

Provides access to infrastructure clients.
"""
from fastapi import Request, Depends
from config import Config
from adapters.mongodb.client import MongoDBClient
from adapters.aws.sqs_client import SQSClient
from .config import get_config


def get_db_client(request: Request) -> MongoDBClient:
    """
    Get MongoDB client singleton from app state

    Initialized once at app startup via lifespan pattern.
    Shared across all requests for connection pool efficiency.

    Args:
        request: FastAPI request object

    Returns:
        MongoDBClient: Singleton MongoDB client instance
    """
    return request.app.state.db_client


def get_sqs_client(config: Config = Depends(get_config)) -> SQSClient:
    """
    Get SQS client (per-request)

    Creates new SQS client instance for each request.
    AWS SDK handles connection pooling internally.

    Args:
        config: Application configuration

    Returns:
        SQSClient: SQS client instance
    """
    return SQSClient(
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_region
    )
