"""
Item Collection Adapter
"""
from typing import Optional, Dict, Any, List
from ..base import BaseMongoAdapter


class ItemAdapter(BaseMongoAdapter):
    """Adapter for Item collection"""

    collection_name = "Item"

    async def find_one(
        self,
        filter_dict: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find single item document with optional projection

        Args:
            filter_dict: MongoDB filter query
            projection: MongoDB projection dict (if None, returns all fields)
        """
        return await self.col.find_one(filter_dict, projection, session=self.session)

    async def find_many(
        self,
        filter_dict: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
        limit: int = 50,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple item documents

        Args:
            filter_dict: MongoDB filter query
            projection: MongoDB projection dict
            limit: Maximum documents to return
            skip: Number of documents to skip
            sort: Sort specification [(field, direction), ...]
        """
        cursor = self.col.find(filter_dict, projection, session=self.session)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_documents(self, filter_dict: Dict[str, Any]) -> int:
        """
        Count documents matching filter

        Args:
            filter_dict: MongoDB filter query
        """
        return await self.col.count_documents(filter_dict, session=self.session)

    async def insert_one(self, document: Dict[str, Any]):
        """
        Insert item document

        Args:
            document: MongoDB document to insert
        """
        return await self.col.insert_one(document, session=self.session)

    async def update_one(
        self,
        filter_dict: Dict[str, Any],
        update: Dict[str, Any]
    ):
        """
        Update single item document

        Args:
            filter_dict: MongoDB filter query
            update: MongoDB update operations
        """
        return await self.col.update_one(filter_dict, update, session=self.session)

    async def delete_one(self, filter_dict: Dict[str, Any]):
        """
        Delete single item document

        Args:
            filter_dict: MongoDB filter query
        """
        return await self.col.delete_one(filter_dict, session=self.session)
