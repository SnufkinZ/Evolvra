from operation_library.base_repository import BaseRepository
from database import goals_collection
from datetime import datetime
from typing import List

class GoalRepository(BaseRepository):
    def __init__(self, user_id: str):
        # Tell the base class which collection to use and who the user is
        super().__init__(collection=goals_collection, user_id=user_id)

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
                "real_method": "create" # The actual Python method
            },
            {
                "tool_name": "get_overdue_tasks",
                "description": "Get a list of all active tasks that are past their deadline.",
                "parameters": {"type": "object", "properties": {}},
                "method_name": "get_overdue_tasks" # The actual Python method
            }
            # ... define all other task-related tools here ...
        ]