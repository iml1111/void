"""
API Routes Registry

Registers all API routes to the FastAPI application.
"""
from fastapi import FastAPI
from .health import router as health_router
from .items import router as items_router


def register_routes(app: FastAPI) -> None:
    """
    Register all routes to the application

    Args:
        app: FastAPI application instance
    """
    app.include_router(health_router, tags=["health"])
    app.include_router(items_router, prefix="/api/v1/items", tags=["items"])
