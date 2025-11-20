"""
Item Schemas

Request/Response schemas for Item API endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from domain.value_objects.item_enums import ItemStatus


class ItemCreateRequest(BaseModel):
    """Request schema for creating an item"""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Item description"
    )
    status: ItemStatus = Field(default=ItemStatus.ACTIVE, description="Item status")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "This is a sample item",
                "status": "active",
                "metadata": {"category": "example"},
            }
        }


class ItemResponse(BaseModel):
    """Response schema for a single item"""
    id: str
    name: str
    description: Optional[str]
    status: ItemStatus
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Sample Item",
                "description": "This is a sample item",
                "status": "active",
                "metadata": {"category": "example"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
