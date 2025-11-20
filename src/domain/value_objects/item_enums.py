"""Item Value Objects - Enums"""
from enum import Enum


class ItemStatus(str, Enum):
    """Item status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
