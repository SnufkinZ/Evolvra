from operation_library.base_repository import BaseRepository
from database import tasks_collection
from datetime import datetime
from typing import List, Dict, Any
from models import main_models
from models.main_models import TaskModel
from pydantic import ValidationError
from system_tools import get_current_time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                    "description": "Understands a user's natural language request to create a new task. The request can include the task name, a detailed description, and any scheduling information like 'tomorrow at 5pm' or 'every Friday'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "A concise name for the task, inferred from the user's request."},
                            "description": {"type": "string", "description": "All other details provided by the user, including the full description, frequency, and any information guiding how to schedule, in a single block of text."},
                            "schedule": {"type": "string", "description": "Optional. Any scheduling information provided by the user, including time, place, frequency, and deadline, such as 'tomorrow at 5pm in the school' or 'every Friday in my home'."}
                        },
                        "required": ["name", "description"]
                    }
                },
                "internal_method_name": "create_task"
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task_by_id",
                    "description": "Retrieve a task by its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                            "type": "string",
                            "description": "The unique identifier of the task to retrieve."
                            }
                        },
                        "required": ["item_id"]
                    }
                },
                "internal_method_name": "get_task_by_id"
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task_by_name",
                    "description": "Retrieve a task by its name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                            "type": "string",
                            "description": "The name of the task to retrieve."
                            }
                        },
                        "required": ["name"]
                    }
                },
                "internal_method_name": "get_task_by_name"
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task's details using its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "The unique identifier of the task to update."
                            },
                            "update_data": {
                                "type": "object",
                                "description": "A dictionary containing the fields to update and their new values."
                            }
                        },
                        "required": ["item_id", "update_data"]
                    }
                },
                "internal_method_name": "update_task"
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task using its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "The unique identifier of the task to delete."
                            }
                        },
                        "required": ["item_id"]
                    }
                },
                "internal_method_name": "delete_task"
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks, with optional filtering and sorting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter_by": {
                                "type": "object",
                                "description": "Optional. A dictionary to filter tasks, e.g., {'status': 'active'}."
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Optional. The field name to sort the tasks by, e.g., 'created_at'."
                            }
                        },
                        "required": []
                    }
                },
                "internal_method_name": "list_tasks"
            }
            # ... define all other task-related tools here ...
        ]

    # This is the specialized "create" method for Tasks
    async def create_task(self, name: str, description: str, schedule: str = None) -> Dict[str, Any]:
        """
        Creates a TaskModel object, validates the data, and persists it to the database.
        Returns the complete TaskModel object.
        """
        logger.info(f"Attempting to create a task for user '{self.user_id}' with data: {name}, {description}, {schedule}")
        try:
            task = TaskModel(
                user_id=self.user_id,
                name=name,
                description=description,
                schedule=schedule,
                created_at=get_current_time(),
                status="active" # Default status is active
            )
            # 2. Convert the Pydantic model to a dictionary for MongoDB insertion
            task_dict = task.model_dump(by_alias=True)
            # 3. Insert into the database using the base class's create method
            inserted_id = await super()._create(task_dict)
            logger.info(f"Task '{task.name}' created successfully with ID: {inserted_id}.")
            return {
                "status": "success",
                "message": f"Successfully created the task named'{task.name}'",
                "data": task_dict
            }
            
        except ValidationError as e:
            error_message = "Task creation failed due to invalid or missing data."
            logger.warning(f"{error_message} Details: {e.errors()}")
            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "DataValidationError",
                    "summary": "The provided data did not pass validation checks.",
                    "validation_errors": e.errors(), 
                    "original_input": {"name": name, "description": description, "schedule": schedule}
                }
            }
        
        except Exception as e:
            error_message = "Task creation failed due to an unexpected internal error."
            logger.error(f"{error_message} Exception: {e}", exc_info=True)

            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "InternalServerError",
                    "summary": "An unexpected error occurred on the server side. This is likely not a problem with the input data.",
                    "error_info": f"{type(e).__name__}: {str(e)}",
                    "original_input": {"name": name, "description": description, "schedule": schedule}
                }
            }


    async def get_task_by_id(self, item_id: str) -> Dict[str, Any]:
        # 1. Call the base class's internal method to get the raw dictionary
        task_dict = await super()._get_by_id(item_id)

        # 2. If data is found, convert it to a TaskModel object before returning
        if task_dict:
            logger.info(f"Task found with ID: {item_id}")
            task_model = TaskModel(**task_dict)  # This will also validate the data
            return {
                "status": "success",
                "message": f"Successfully retrieved task with ID: {item_id}",
                "data": task_model.model_dump(by_alias=True) # Return as dict with alias (i.e., _id
                }
        
        # 3. If no data, return None
        else:
            logger.info(f"Query successful, but no task found with ID: {item_id}")
            return {
                "status": "success",
                "message": f"No task found with ID: {item_id}",
                "data": None
            }
    
    async def get_task_by_name(self, name):
        item = await super()._get_by_name(name)
        if item:
            logger.info(f"Task found with name: {name}")
            task_model = TaskModel(**item)  # Validate and convert to TaskModel
            return {
                "status": "success",
                "message": f"Successfully retrieved task with name: {name}",
                "data": task_model.model_dump(by_alias=True) # Return as dict with alias (i.e., _id)
            }
        else:
            logger.info(f"Query successful, but no task found with name: {name}")
            return {
                "status": "failure",
                "message": f"No task found with name: {name}",
                "data": None
            }
        
    async def update_task(self, item_id: str, update_data: dict) -> Dict[str, Any]:
        logger.info(f"Attempting to update task with ID: {item_id} using data: {update_data}")
        try:
            task = TaskModel(**update_data)  # Validate the update data
            task_dict = task.model_dump(by_alias=True)
            updated_number = await super()._update(item_id, task_dict)
            if updated_number == 0:
                logger.info(f"No task found with ID: {item_id} to update.")
                return {
                    "status": "failure",
                    "message": f"No task found with ID: {item_id} to update.",
                    "updated_count": 0,
                    "original_input": update_data
                }
            else:
                logger.info(f"Task with ID: {item_id} updated successfully.")
                return {
                    "status": "success",
                    "message": f"Successfully updated task with ID: {item_id}",
                    "updated_count": updated_number,
                    "update_date": update_data
                }
        except ValidationError as e:
            error_message = "Task update failed due to invalid or missing data."
            logger.warning(f"{error_message} Details: {e.errors()}")
            return {
                "status": "failure",
                "message": error_message,
                "updated_count": 0,
                "error_details": {
                    "type": "DataValidationError",
                    "summary": "The provided update data did not pass validation checks.",
                    "validation_errors": e.errors(), 
                    "original_input": update_data
                }
            }
    
    async def delete_task(self, item_id: str) -> Dict[str, Any]:
        # 1. Call the base class's internal method to perform the deletion
        deleted_count = await super()._delete(item_id)

        # 2. Return a structured response based on the deletion result
        if deleted_count > 0:
            logger.info(f"Task with ID: {item_id} deleted successfully.")
            return {
                "status": "success",
                "message": f"Successfully deleted task with ID: {item_id}",
                "deleted_count": deleted_count
            }
        else:
            logger.info(f"No task found with ID: {item_id} to delete.")
            return {
                "status": "failure",
                "message": f"No task found with ID: {item_id} to delete.",
                "deleted_count": 0
            }

    # --- This is a SPECIALIZED function that only makes sense for tasks ---
    async def list_tasks(filter_by: dict = None, sort_by: str = None) -> Dict[str, Any]:
        """List all tasks, optionally filtered and sorted."""
        try:
            tasks = await super()._get_all(filter_query=filter_by, sort_by=sort_by)
            logger.info(f"Retrieved {len(tasks)} tasks with filter: {filter_by} and sort: {sort_by}")
            return {
                "status": "success",
                "message": f"Retrieved {len(tasks)} tasks.",
                "data": tasks
            }
        except Exception as e:
            error_message = "Failed to retrieve tasks due to an unexpected internal error."
            logger.error(f"{error_message} Exception: {e}", exc_info=True)
            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "InternalServerError",
                    "summary": "An unexpected error occurred on the server side while retrieving tasks.",
                    "error_info": f"{type(e).__name__}: {str(e)}"
                }
            }
    
    # async def get_overdue_tasks(self) -> List[dict]:
    #     """Retrieves all active tasks for the user whose deadline has passed."""
    #     overdue_filter = {
    #         "status": "active",
    #         "deadline": {"$lt": datetime.now()} # Deadline is less than now
    #     }
    #     # We can now use the get_all method we inherited from the base class!
    #     return await self.get_all(filter_query=overdue_filter)
    
    # async def get_active_tasks(self)-> list[dict]:
    #     """Find all active tasks"""
    #     active_filter = {
    #         "status": "active",
    #     }
    #     return await self.get_all(filter_query=active_filter)