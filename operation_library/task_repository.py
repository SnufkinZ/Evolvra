from operation_library.base_repository import BaseRepository
from database import tasks_collection
from datetime import datetime
from typing import List

class TaskRepository(BaseRepository):
    def __init__(self, user_id: str):
        # Tell the base class which collection to use and who the user is
        super().__init__(collection=tasks_collection, user_id=user_id)

    @staticmethod
    def get_tool_definitions():
        """Returns a list of tool definitions this repository provides."""
        return [
            {
                "name": "get_overdue_tasks",
                "method_name": "get_overdue_tasks",
                "description": "Retrieve all overdue tasks for the user.",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "create_task",
                "method_name": "create", # The method in BaseRepository
                "description": "Create a new task.",
                "parameters": { ... } # Full parameter definition
            },
            # ... define all other task-related tools here ...
        ]
    
    # --- This is a SPECIALIZED function that only makes sense for tasks ---
    async def get_overdue_tasks(self) -> List[dict]:
        """Retrieves all active tasks for the user whose deadline has passed."""
        overdue_filter = {
            "status": "active",
            "deadline": {"$lt": datetime.now()} # Deadline is less than now
        }
        # We can now use the get_all method we inherited from the base class!
        return await self.get_all(filter_query=overdue_filter)
    
    async def get_active_tasks(self)-> list[dict]:
        """Find all active tasks"""
        active_filter = {
            "status": "active",
        }
        return await self.get_all(filter_query=active_filter)