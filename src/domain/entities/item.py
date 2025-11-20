"""Item Domain Entity (Sample)"""
from dataclasses import dataclass, fields as get_fields
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from .base import BaseEntity
from domain.value_objects.item_enums import ItemStatus


@dataclass(eq=False, frozen=True)
class ItemEntity(BaseEntity):
    """
    Item domain entity (Sample)

    Demonstrates the Entity pattern with:
    - @dataclass(eq=False, frozen=True) for immutability
    - from_dict() for MongoDB document conversion
    - validate() for business rule validation
    - Identity-based __eq__ and __hash__
    """

    name: str
    description: str
    status: ItemStatus
    created_at: datetime  # UTC timezone-aware datetime
    id: Optional[str] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        name: str,
        description: Optional[str] = None,
        status: ItemStatus = ItemStatus.ACTIVE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ItemEntity":
        """
        Factory method for creating new ItemEntity

        Args:
            name: Item name (required)
            description: Item description
            status: Item status (default: ACTIVE)
            metadata: Additional metadata

        Returns:
            New ItemEntity instance
        """
        return cls(
            name=name,
            description=description or "",
            status=status,
            created_at=datetime.now(timezone.utc),
            metadata=metadata
        )

    def __post_init__(self):
        self.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemEntity':
        """
        Create entity from dictionary (MongoDB document)

        Args:
            data: Dictionary with entity data

        Returns:
            ItemEntity instance
        """
        # Convert MongoDB _id to id
        if '_id' in data:
            data = {**data}  # Copy to avoid mutating original
            data['id'] = str(data.pop('_id'))

        # Validate required fields
        if 'name' not in data:
            raise ValueError("Field 'name' is required")
        if 'description' not in data:
            raise ValueError("Field 'description' is required")
        if 'status' not in data:
            raise ValueError("Field 'status' is required")
        if 'created_at' not in data:
            raise ValueError("Field 'created_at' is required")

        # Extract only defined fields
        known_fields = {f.name for f in get_fields(cls)}
        entity_data = {k: v for k, v in data.items() if k in known_fields}

        # Convert status string to Enum
        if 'status' in entity_data and isinstance(entity_data['status'], str):
            entity_data['status'] = ItemStatus(entity_data['status'])

        # Convert timestamp string to UTC datetime
        for field in ['created_at', 'updated_at']:
            if field in entity_data and entity_data[field] is not None:
                if isinstance(entity_data[field], str):
                    entity_data[field] = datetime.fromisoformat(entity_data[field])
                elif isinstance(entity_data[field], datetime):
                    # Apply UTC timezone if naive datetime from MongoDB
                    if entity_data[field].tzinfo is None:
                        entity_data[field] = entity_data[field].replace(tzinfo=timezone.utc)

        return cls(**entity_data)

    def validate(self) -> None:
        """
        Validate entity business rules

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Field 'name' must be a non-empty string")

        if not isinstance(self.description, str):
            raise ValueError("Field 'description' must be a string")

        if not isinstance(self.status, ItemStatus):
            raise ValueError("Field 'status' must be an ItemStatus enum")

        if not isinstance(self.created_at, datetime):
            raise ValueError("Field 'created_at' must be a datetime object")

        if self.id is not None and not isinstance(self.id, str):
            raise ValueError("Field 'id' must be a string")

        if self.updated_at is not None and not isinstance(self.updated_at, datetime):
            raise ValueError("Field 'updated_at' must be a datetime object")

        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("Field 'metadata' must be a dict")

    def __eq__(self, other: object) -> bool:
        """Identity-based equality"""
        if not isinstance(other, ItemEntity):
            return False

        # Entities without ID are not comparable
        if self.id is None or other.id is None:
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        """Identity-based hash"""
        if self.id is None:
            raise TypeError("Cannot hash ItemEntity without id")
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dict with enum serialization"""
        result = super().to_dict()
        # Convert enum to string value
        if isinstance(result.get('status'), ItemStatus):
            result['status'] = result['status'].value
        return result
