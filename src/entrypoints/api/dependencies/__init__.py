"""
Dependency Injection Container

Re-exports all dependency functions for FastAPI routes.
"""
from .config import get_config
from .clients import get_db_client, get_sqs_client
from .services import get_item_service

__all__ = [
    # Config
    "get_config",
    # Clients
    "get_db_client",
    "get_sqs_client",
    # Services
    "get_item_service",
]
