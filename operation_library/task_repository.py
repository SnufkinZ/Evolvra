from operation_library.base_repository import BaseRepository
from database import tasks_collection
from datetime import datetime
from typing import List
from models import main_models
from models.main_models import TaskModel
from system_tools import get_current_time

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
                            "confidence_to_description": {"type": "integer", "description": "The confidence level of the description (1-100)."},
                            "target_goal": {"type": "string", "description": "The goal this task is associated with (optional)."},
                            "priority": {"type": "string", "description": "The priority desciption of the task."},
                            "confidence_to_priority": {"type": "integer", "description": "The confidence level of the priority (1-100)."},
                            "frequency": {"type": "string", "description": "The frequency of the task (choose one from DAILY | WEEKLY | MONTHLY | YEARLY | QUANTITY)."},
                            "number": {"type": "integer", "description": "combined with the field of frequency, e.g. if frequency is DAILY and time is 3, it means every 3 days.If frequency is QUANTITY and time is 3, it means 3 times totally."},
                            "preschedule_mode": {"type": "string", "description": "The preschedule mode of the task (choose one from absolute | fuzzy | workflow). If there is no any schedule, just fill in None."},
                            "time": {"type": "string", "description": "The time or date of the task."},
                            "place": {"type": "string", "description": "The place where the task happens (optional)."},
                            "confidence_to_schedeule": {"type": "integer", "description": "The confidence level of the schedule including the mode, time and place (1-100)."},
                            "todo_list": {"type": "array", "items": {"type": "string"}, "description": "A list of to-do items associated with the task (optional)."},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "A list of tags associated with the task (optional)."}
                        },
                        "required": ["name", "description", "confidence_to_description", "priority", "confidence_to_priority", "frequency", "number", "tags"]
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
            }
            # ... define all other task-related tools here ...
        ]

    # This is the specialized "create" method for Tasks
    async def create_task(self, task_data: dict) -> str:
        """
        Creates a TaskModel object, validates the data, and persists it to the database.
        Returns the complete TaskModel object.
        """
        message = []
        if task_data["name"] is None:
            raise ValueError("Task name is required.")
        if task_data["description"] is None:
            raise ValueError("Task description is required.")
        if task_data["confidence_to_description"] is None:
            raise ValueError("Task confidence_to_description is required.")
        if task_data["priority"] is None:
            raise ValueError("Task priority is required.")
        if task_data["confidence_to_priority"] is None:
            raise ValueError("Task confidence_to_priority is required.")
        if task_data["frequency"] is None:
            raise ValueError("Task frequency is required.")
        if task_data["number"] is None:
            raise ValueError("Task number is required.")
        if task_data["tags"] is None:
            raise ValueError("Task tags is required.")
        if task_data["preschedule_mode"]:
            if task_data["preschedule_mode"] not in ["absolute", "fuzzy", "workflow"]:
                raise ValueError("preschedule_mode must be one of absolute, fuzzy, workflow or None.")
            else:
                if task_data["preschedule_mode"] == "absolute":
                    preschedule_item = main_models.AbsoluteScheduleModel(
                        mode="absolute",
                        time=task_data["time"],
                        location=task_data["place"],
                        confidence=task_data["confidence_to_schedeule"],
                        todo_list=task_data["todo_list"] if "todo_list" in task_data else None)
                elif task_data["preschedule_mode"] == "fuzzy":
                    preschedule_item = main_models.FuzzyScheduleModel(
                        mode="fuzzy",
                        time=task_data["time"],
                        location=task_data["place"],
                        confidence=task_data["confidence_to_schedeule"],
                        todo_list=task_data["todo_list"] if "todo_list" in task_data else None)
                else: # workflow
                    preschedule_item = main_models.WorkflowScheduleModel(
                        mode="workflow",
                        time=task_data["time"],
                        location=task_data["place"],
                        confidence=task_data["confidence_to_schedeule"],
                        todo_list=task_data["todo_list"][0] if task_data["todo_list"] else "")
        if task_data["target_goal"]:
            try:
                target_goal_id = await self.get_id_by_name(task_data["target_goal"])
            except Exception:
                message.append(f"Warning: The target goal '{task_data['target_goal']}' does not exist. The task will be created without linking to a goal.")
            
        current_time = get_current_time()
        # 1. Create a TaskModel instance in memory.
        dynamic_priority = main_models.DynamicPriorityModel(value=task_data["priority"], confidence=task_data["confidence_to_priority"], last_updated=current_time)
        metircs = main_models.MetricsModel(success_count=0, failure_count=0, created_at=current_time, updated_at=current_time)
        description = main_models.DescriptionModel(filed=task_data["description"], confidence=task_data["confidence_to_description"], last_updated=current_time)
        frequency = main_models.FrequencyModel(field=task_data["frequency"], number=task_data["number"], last_updated=current_time)
        task_to_create = TaskModel(
            user_id=self._user_id, # <-- Inject the user_id from self
            name=task_data["name"],
            target_goal_ids = target_goal_id,
            target_goal_names = task_data["target_goal"],
            status="active",
            dynamic_priority=dynamic_priority,
            frequency=frequency,
            description=description,
            metrics=metircs,
            preschedule=[],
            tags=task_data["tags"]
        )
        # At this exact moment, Pydantic sees 'id' is missing and calls
        # the default_factory, generating a new ObjectId.
        
        # 2. Convert the Pydantic model to a dictionary suitable for MongoDB.
        # model_dump(by_alias=True) will correctly use the "_id" key.
        task_dict = task_to_create.model_dump(by_alias=True)

        # 3. Call the base class's generic internal create method
        id = await super()._create(task_dict)
        message.append(f"Success: Task '{task_data['name']}'(id: {id}) has been created.")
        # 4. Return the fully-formed object, which now includes the generated ID.
        return message

    async def get_task_by_id(self, item_id: str) -> TaskModel | None:
        # 1. Call the base class's internal method to get the raw dictionary
        task_dict = await super()._get_by_id(item_id)

        # 2. If data is found, convert it to a TaskModel object before returning
        if task_dict:
            return TaskModel(**task_dict)
        
        # 3. If no data, return None
        return None
    
    async def get_task_by_name(self, name):
        item = await super().get_by_name(name)
        if item:
            return TaskModel(**item)
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