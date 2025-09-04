getWeather_tool = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]

classification_tool = [
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
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_task_by_id",
            "description": "Find a task by the id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task to retrieve."},
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "create_goal",
            "description": "Create a new long-term or short-term goal for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the goal."},
                    "description": {"type": "string", "description": "Details about the goal."},
                    "priority": {"type": "string", "description": "Goal priority level (e.g. High, Medium, Low)."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "update_task",
            "description": "Edit an existing task's information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID or name of the task to be edited."},
                    "fields_to_update": {
                        "type": "object",
                        "description": "Fields and values to update.",
                        "properties": {
                            "time": {"type": "string"},
                            "content": {"type": "string"},
                            "place": {"type": "string"}
                        }
                    }
                },
                "required": ["task_id", "fields_to_update"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "update_goal",
            "description": "Edit an existing goal's attributes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_id": {"type": "string", "description": "The ID or name of the goal to be edited."},
                    "fields_to_update": {
                        "type": "object",
                        "description": "Fields and values to update.",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "string"}
                        }
                    }
                },
                "required": ["goal_id", "fields_to_update"]
            }
        }
    },
    {
        "type": "function",
        "function": { 
            "name": "schedule",
            "description": "Generate or modify a schedule for today or a given time period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Scheduling mode: 'today', 'range', or 'auto'."
                    },
                    "time_range": {
                        "type": "string",
                        "description": "The specific time range if 'range' mode is used."
                    }
                },
                "required": ["mode"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "chat",
            "description": "Engage in a personality-driven chat with the user. Respond with tone and style based on familiarity level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The topic the user wants to talk about."},
                    "user_familiarity": {
                        "type": "string",
                        "description": "Level of familiarity: 'stranger', 'acquaintance', 'friend', or 'close_friend'."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "recorder",
            "description": "Record the user's performance on a task, including start time, end time, and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The task name or ID."},
                    "start_time": {"type": "string", "description": "Start time of the task."},
                    "end_time": {"type": "string", "description": "End time of the task."},
                    "status": {"type": "string", "description": "Completion status or user state."},
                    "note": {"type": "string", "description": "Optional additional note."}
                },
                "required": ["task", "status"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "check_state",
            "description": "Check today'progress, task completion, and user's current state. Suggest adjustments if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date to check (default: today)."},
                    "include_feedback": {"type": "boolean", "description": "Whether to include suggestions and feedback."}
                },
                "required": []
            }
        }
    }

]