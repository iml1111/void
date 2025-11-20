"""Health Check Endpoint"""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from config import Config
from entrypoints.api.dependencies import get_config
from entrypoints.api.schemas.health import HealthCheckResponse

router = APIRouter()


@router.get("/", response_class=PlainTextResponse)
async def root():
    """Root endpoint"""
    return "VOID API - Ready to serve"


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(config: Config = Depends(get_config)):
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        service=config.app_name,
        version=config.version
    )
