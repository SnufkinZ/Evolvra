from operation_library.base_repository import BaseRepository
from database import tasks_collection
from datetime import datetime
from typing import List
from models.main_models import TaskModel

class TaskRepository(BaseRepository):
    def __init__(self, user_id: str):
        # Tell the base class which collection to use and who the user is
        super().__init__(collection=tasks_collection, user_id=user_id)

    @staticmethod
    def get_tool_definitions():
        """Returns a list of tool definitions this repository provides."""
        return [
            {
                "type": "function", 
                "function": {
                    "name": "create_task",
                    "description": "Add a new task to the user's task system.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the task."},
                            "description": {"type": "string", "description": "A short description of the task."},
                            "time": {"type": "string", "description": "The time or date of the task."},
                            "status": {"type": "string", "description": "The current status of the task (e.g. active, completed)."},
                            "place": {"type": "string", "description": "The place where the task happens (optional)."}
                        },
                        "required": ["name", "description"]
                    }
                },
                "internal_method_name": "create"
            }
            # ... define all other task-related tools here ...
        ]

    # This is the specialized "create" method for Tasks
    async def create_task(self, name: str, description: str, **other_fields) -> TaskModel:
        """
        Creates a TaskModel object, validates the data, and persists it to the database.
        Returns the complete TaskModel object.
        """
        # 1. Create a TaskModel instance in memory.
        task_to_create = TaskModel(
            user_id=self._user_id, # <-- Inject the user_id from self
            name=name,
            description=description,
            **other_fields
        )
        # At this exact moment, Pydantic sees 'id' is missing and calls
        # the default_factory, generating a new ObjectId.
        
        # 2. Convert the Pydantic model to a dictionary suitable for MongoDB.
        # model_dump(by_alias=True) will correctly use the "_id" key.
        task_dict = task_to_create.model_dump(by_alias=True)

        # 3. Call the base class's generic internal create method
        await super()._create(task_dict)
        
        # 4. Return the fully-formed object, which now includes the generated ID.
        return task_to_create

    async def get_task_by_id(self, item_id: str) -> TaskModel | None:
        # 1. Call the base class's internal method to get the raw dictionary
        task_dict = await super()._get_by_id(item_id)

        # 2. If data is found, convert it to a TaskModel object before returning
        if task_dict:
            return TaskModel(**task_dict)
        
        # 3. If no data, return None
        return None

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