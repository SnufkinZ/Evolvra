from operation_library.base_repository import BaseRepository
from database import goals_collection
from datetime import datetime
from typing import List, Dict, Any
from models.main_models import GoalModel
from pydantic import ValidationError
from system_tools import get_current_time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                    "name": "create_goal",
                    "description": "Understands a user's natural language request to create a new goal. The request can include the goal name, a detailed description, the parent goal if applicable, and the weight (0-100) indicating the goal's importance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "A concise name for the goal, inferred from the user's request."},
                            "description": {"type": "string", "description": "All other details provided by the user, including the full description."},
                            "parentgoal": {"type": "string", "description": "Optional. The name or ID of the parent goal, if this goal is a sub-goal."},
                            "weight": {"type": "integer", "description": "Optional. An integer from 0 to 100 indicating the importance of this goal."}
                        },
                        "required": ["name", "description"]
                    }
                },
                "internal_method_name": "create_goal"
            },
                        {
                "type": "function",
                "function": {
                    "name": "get_goal_by_id",
                    "description": "Retrieve a goal by its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                            "type": "string",
                            "description": "The unique identifier of the goal to retrieve."
                            }
                        },
                        "required": ["item_id"]
                    }
                },
                "internal_method_name": "get_goal_by_id"
            },
            {
                "type": "function",
                "function": {
                    "name": "get_goal_by_name",
                    "description": "Retrieve a goal by its name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                            "type": "string",
                            "description": "The name of the goal to retrieve."
                            }
                        },
                        "required": ["name"]
                    }
                },
                "internal_method_name": "get_goal_by_name"
            },
            {
                "type": "function",
                "function": {
                    "name": "update_goal",
                    "description": "Update an existing goal's details using its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "The unique identifier of the goal to update."
                            },
                            "update_data": {
                                "type": "object",
                                "description": "A dictionary containing the fields to update and their new values."
                            }
                        },
                        "required": ["item_id", "update_data"]
                    }
                },
                "internal_method_name": "update_goal"
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_goal",
                    "description": "Delete a goal using its unique identifier (ID).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "The unique identifier of the goal to delete."
                            }
                        },
                        "required": ["item_id"]
                    }
                },
                "internal_method_name": "delete_goal"
            },
            {
                "type": "function",
                "function": {
                    "name": "list_goals",
                    "description": "List all goals, with optional filtering and sorting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filter_by": {
                                "type": "object",
                                "description": "Optional. A dictionary to filter goals, e.g., {'status': 'active'}."
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Optional. The field name to sort the goals by, e.g., 'created_at'."
                            }
                        },
                        "required": []
                    }
                },
                "internal_method_name": "list_goals"
            }
        ]
    
    async def create_goal(self, name: str, description: str, parentgoal: str = None, weight: int = None) -> Dict[str, Any]:
        logger.info(f"Attempting to create a goal for user '{self.user_id}' with data: {name}, {description}, {parentgoal}, {weight}")
        try:
            goal = GoalModel(
                user_id=self.user_id,
                name=name,
                description=description,
                parentgoal=parentgoal,
                weight=weight,
                created_at=get_current_time(),
                status="active" # Default status is active
            )
            # 2. Convert the Pydantic model to a dictionary for MongoDB insertion
            goal_dict = goal.model_dump(by_alias=True)
            # 3. Insert into the database using the base class's create method
            inserted_id = await super()._create(goal_dict)
            logger.info(f"Goal '{goal.name}' created successfully with ID: {inserted_id}.")
            return {
                "status": "success",
                "message": f"Successfully created the goal named'{goal.name}'",
                "data": goal_dict
            }
            
        except ValidationError as e:
            error_message = "Goal creation failed due to invalid or missing data."
            logger.warning(f"{error_message} Details: {e.errors()}")
            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "DataValidationError",
                    "summary": "The provided data did not pass validation checks.",
                    "validation_errors": e.errors(), 
                    "original_input": {"name": name, "description": description, "parentgoal": parentgoal, "weight": weight}
                }
            }
        
        except Exception as e:
            error_message = "Goal creation failed due to an unexpected internal error."
            logger.error(f"{error_message} Exception: {e}", exc_info=True)

            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "InternalServerError",
                    "summary": "An unexpected error occurred on the server side. This is likely not a problem with the input data.",
                    "error_info": f"{type(e).__name__}: {str(e)}",
                    "original_input": {"name": name, "description": description, "parentgoal": parentgoal, "weight": weight}
                }
            }


    async def get_goal_by_id(self, item_id: str) -> Dict[str, Any]:
        goal_dict = await super()._get_by_id(item_id)

        if goal_dict:
            logger.info(f"Goal found with ID: {item_id}")
            goal_model = GoalModel(**goal_dict)  # This will also validate the data
            return {
                "status": "success",
                "message": f"Successfully retrieved goal with ID: {item_id}",
                "data": goal_model.model_dump(by_alias=True) # Return as dict with alias (i.e., _id
                }
        
        else:
            logger.info(f"Query successful, but no goal found with ID: {item_id}")
            return {
                "status": "success",
                "message": f"No goal found with ID: {item_id}",
                "data": None
            }
    
    async def get_goal_by_name(self, name):
        item = await super()._get_by_name(name)
        if item:
            logger.info(f"Goal found with name: {name}")
            goal_model = GoalModel(**item)
            return {
                "status": "success",
                "message": f"Successfully retrieved goal with name: {name}",
                "data": goal_model.model_dump(by_alias=True) # Return as dict with alias (i.e., _id)
            }
        else:
            logger.info(f"Query successful, but no goal found with name: {name}")
            return {
                "status": "failure",
                "message": f"No goal found with name: {name}",
                "data": None
            }
        
    async def update_goal(self, item_id: str, update_data: dict) -> Dict[str, Any]:
        logger.info(f"Attempting to update goal with ID: {item_id} using data: {update_data}")
        try:
            goal = GoalModel(**update_data)  # Validate the update data
            goal_dict = goal.model_dump(by_alias=True)
            updated_number = await super()._update(item_id, goal_dict)
            if updated_number == 0:
                logger.info(f"No goal found with ID: {item_id} to update.")
                return {
                    "status": "failure",
                    "message": f"No goal found with ID: {item_id} to update.",
                    "updated_count": 0
                }
            else:
                logger.info(f"Goal with ID: {item_id} updated successfully.")
                return {
                    "status": "success",
                    "message": f"Successfully updated goal with ID: {item_id}",
                    "updated_count": updated_number
                }
        except ValidationError as e:
            error_message = "Goal update failed due to invalid or missing data."
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
    
    async def delete_goal(self, item_id: str) -> Dict[str, Any]:
        # 1. Call the base class's internal method to perform the deletion
        deleted_count = await super()._delete(item_id)

        # 2. Return a structured response based on the deletion result
        if deleted_count > 0:
            logger.info(f"Goal with ID: {item_id} deleted successfully.")
            return {
                "status": "success",
                "message": f"Successfully deleted goal with ID: {item_id}",
                "deleted_count": deleted_count
            }
        else:
            logger.info(f"No goal found with ID: {item_id} to delete.")
            return {
                "status": "failure",
                "message": f"No goal found with ID: {item_id} to delete.",
                "deleted_count": 0
            }

    async def list_goal(filter_by: dict = None, sort_by: str = None) -> Dict[str, Any]:
        try:
            goals = await super()._get_all(filter_query=filter_by, sort_by=sort_by)
            logger.info(f"Retrieved {len(goals)} goals with filter: {filter_by} and sort: {sort_by}")
            return {
                "status": "success",
                "message": f"Retrieved {len(goals)} goals.",
                "data": goals
            }
        except Exception as e:
            error_message = "Failed to retrieve goals due to an unexpected internal error."
            logger.error(f"{error_message} Exception: {e}", exc_info=True)
            return {
                "status": "failure",
                "message": error_message,
                "data": None,
                "error_details": {
                    "type": "InternalServerError",
                    "summary": "An unexpected error occurred on the server side while retrieving goals.",
                    "error_info": f"{type(e).__name__}: {str(e)}"
                }
            }