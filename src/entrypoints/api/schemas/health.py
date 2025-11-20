"""
Health Check Schemas

Schemas for health check endpoints.
"""
from pydantic import BaseModel
from __about__ import __version__


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "VOID",
                "version": __version__
            }
        }
