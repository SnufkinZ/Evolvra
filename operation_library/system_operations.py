from bson import ObjectId
from database import tasks_collection, goals_collection
from typing import Dict, Any

# --- Create ---
async def create_item(item_data: dict, collection_name: str) -> str:
    """Create a new item in this type's collection"""
    if collection_name == "tasks":
        collection = tasks_collection
    elif collection_name == "goals":
        collection = goals_collection
    else:
        raise ValueError("Unsupported collection name")
    result = await collection.insert_one(item_data)
    print(f"Task created with ID: {result.inserted_id}")
    return str(result.inserted_id)

# --- Read ---
async def get_task_by_id(task_id: str) -> dict | None:
    """Find a task by the id"""
    try:
        obj_id = ObjectId(task_id)
        task = await tasks_collection.find_one({"_id": obj_id})
        return task
    except Exception:
        return None

# -- Get active tasks ---
async def get_active_tasks_for_user(user_id: str) -> list[dict]:
    """Find all active tasks"""
    tasks_list = []
    # find() return a async cursor
    cursor = tasks_collection.find({
        "user_id": user_id, 
        "status": "active"
    })
    async for task in cursor:
        tasks_list.append(task)
    return tasks_list

# --- Update ---
async def update_task(task_id: str, update_data: Dict[str, Any]) -> int:
    """
    Update a task by id with the provided fields.
    :param task_id: the task ID。
    :param update_data: a dictionary including updated fields, e.g., {"name": "New Name", "status": "completed"}
    :return: the modified count (should be 1 or 0)。
    """
    try:
        obj_id = ObjectId(task_id)

        # Security: Avoid updating immutable fields
        if "_id" in update_data:
            del update_data["_id"]
        if "user_id" in update_data:
            del update_data["user_id"]

        if not update_data:
            print("No fields to update.")
            return 0
        
        result = await tasks_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        print(f"Matched {result.matched_count} doc(s) and modified {result.modified_count} doc(s).")
        return result.modified_count

    except Exception as e:
        print(f"An error occurred during task update: {e}")
        return 0

# --- Delete (删除) ---
async def delete_task(task_id: str) -> int:
    """Delete a task by id"""
    obj_id = ObjectId(task_id)
    result = await tasks_collection.delete_one({"_id": obj_id})
    print(f"Deleted {result.deleted_count} document(s).")
    return result.deleted_count