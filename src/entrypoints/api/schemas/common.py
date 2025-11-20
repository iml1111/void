"""
Common Schemas

Shared response schemas for API endpoints.
"""
from typing import Optional
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Error Type",
                "detail": "Detailed error message"
            }
        }
