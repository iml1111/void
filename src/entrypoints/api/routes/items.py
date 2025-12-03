"""
Item API Endpoints

CRUD operations for Item entity.
"""
from fastapi import APIRouter, Depends, HTTPException

from domain.exceptions import ItemNotFoundError, ItemValidationError
from entrypoints.api.dependencies import get_item_service
from entrypoints.api.schemas.item import ItemCreateRequest, ItemResponse
from service_layer.application.item_service import ItemService

router = APIRouter()


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    request: ItemCreateRequest,
    service: ItemService = Depends(get_item_service)
):
    """
    Create a new item

    Args:
        request: Item creation data
        service: Item service (injected)

    Returns:
        Created item
    """
    try:
        item_id = await service.create_item(
            name=request.name,
            description=request.description,
            status=request.status,
            metadata=request.metadata
        )
        item = await service.get_item(item_id)
    except ItemValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        status=item.status,
        metadata=item.metadata,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_by_id(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    """
    Get item by ID

    Args:
        item_id: Item ID
        service: Item service (injected)

    Returns:
        Item details
    """
    try:
        item = await service.get_item(item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        status=item.status,
        metadata=item.metadata,
        created_at=item.created_at,
        updated_at=item.updated_at
    )
