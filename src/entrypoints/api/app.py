"""
FastAPI Application Factory

Creates and configures the FastAPI application instance.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import Config
from adapters.mongodb.client import MongoDBClient
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers
from .routes import register_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for singleton initialization

    Initializes heavyweight resources once at startup:
    - MongoDBClient with connection pool (Lifespan Singleton Pattern)

    Resources are shared across all requests for efficiency.
    """
    config = app.state.config

    # Initialize MongoDB client singleton with connection pool settings
    app.state.db_client = MongoDBClient(
        uri=config.mongodb_uri,
        db_name=config.mongodb_name,
        max_pool_size=50,
        min_pool_size=10,
        max_idle_time_ms=60000
    )

    yield

    # Cleanup
    app.state.db_client.close()


def create_app(config: Config = None) -> FastAPI:
    """
    Create and configure FastAPI application

    Args:
        config: Application configuration instance (optional, creates new if None)
    """
    if config is None:
        config = Config()

    is_dev = config.environment == "development"

    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        contact={
            "name": config.contact_name,
            "url": config.contact_url,
            "email": config.contact_email,
        },
        docs_url="/docs" if is_dev else None,
        redoc_url="/redoc" if is_dev else None,
        openapi_url="/openapi.json" if is_dev else None,
        lifespan=lifespan
    )

    # Store config in app state for dependency injection
    app.state.config = config

    # Setup components
    setup_middleware(app)
    setup_exception_handlers(app)
    register_routes(app)

    return app


# Default app instance for uvicorn
# For testing or custom configs, use create_app(config) factory instead
app = create_app()
