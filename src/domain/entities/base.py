"""Base Entity"""
from dataclasses import fields as get_fields
from typing import Dict, Any


class BaseEntity:
    """Base class for all domain entities"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dict"""
        return {f.name: getattr(self, f.name) for f in get_fields(self)}
