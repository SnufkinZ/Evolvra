from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import List, Dict, Any


class BaseRepository:
    def __init__(self, collection: AsyncIOMotorCollection, user_id: str):
        self._collection = collection
        self._user_id = user_id

    async def create(self, data: dict) -> str:
        data["user_id"] = self._user_id
        result = await self._collection.insert_one(data)
        return str(result.inserted_id)
    
    async def get_by_id(self, item_id: str) -> dict | None:
        try:
            obj_id = ObjectId(item_id)
            item = await self._collection.find_one({"_id": obj_id, "user_id": self._user_id})
            return item
        except Exception:
            return None
        
    async def get_by_name(self, name: str) -> dict | None:
        try:
            item = await self._collection.find_one({"name": name, "user_id": self._user_id})
            return item
        except Exception:
            return None
    
    async def get_id_by_name(self, name: str) -> str | None:
        try:
            item = await self._collection.find_one({"name": name, "user_id": self._user_id}, {"_id": 1})
            if item:
                return str(item["_id"])
            return None
        except Exception:
            return None

    async def update(self, item_id: str, update_data: dict) -> int:
        try:
            obj_id = ObjectId(item_id)

            # Security: Avoid updating immutable fields
            if "_id" in update_data:
                del update_data["_id"]
            if "user_id" in update_data:
                del update_data["user_id"]

            if not update_data:
                print("No fields to update.")
                return 0

            result = await self._collection.update_one(
                {"_id": obj_id, "user_id": self._user_id},
                {"$set": update_data}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error updating item {item_id}: {e}")
            return 0
        
    async def delete(self, item_id: str) -> int:
        try:
            obj_id = ObjectId(item_id)
            result = await self._collection.delete_one({"_id": obj_id, "user_id": self._user_id})
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting item {item_id}: {e}")
            return 0

    async def get_all(self, filter_query: Dict = None, sort_by: str = None, ascending: bool = True) -> List[dict]:
        """
        Retrieves all items for the user, with optional filtering and sorting.
        """
        # Start with the essential security filter
        query = {"user_id": self._user_id}
        
        # Add any additional filters if provided
        if filter_query:
            query.update(filter_query)
            
        cursor = self._collection.find(query)
        
        # Apply sorting if requested
        if sort_by:
            sort_direction = 1 if ascending else -1
            cursor = cursor.sort(sort_by, sort_direction)
            
        return await cursor.to_list(length=None) # Use a reasonable length limit in production

    async def delete_many(self, filter_query: Dict) -> int:
        """
        Deletes multiple items based on a filter, ensuring they belong to the user.
        """
        # Start with the essential security filter
        query = {"user_id": self._user_id}
        query.update(filter_query)
        
        result = await self._collection.delete_many(query)
        return result.deleted_count