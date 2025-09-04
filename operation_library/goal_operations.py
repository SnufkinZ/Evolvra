from bson import ObjectId
from database import goals_collection
from typing import Dict, Any, List

# --- Create ---
async def create_goal(goal_data: dict) -> str:
    result = await goals_collection.insert_one(goal_data)
    print(f"Task created with ID: {result.inserted_id}")
    return str(result.inserted_id)

# --- Read ---
async def get_goal_by_id(goal_id: str) -> dict | None:
    try:
        obj_id = ObjectId(goal_id)
        goal = await goals_collection.find_one({"_id": obj_id})
        return goal
    except Exception as e:
        print(f"Could not find goal by id {goal_id}: {e}")
        return None

# --- Get goal tree ---
async def get_goal_tree_for_user(user_id: str) -> List[dict]:
    """
    Get all goals for a user and organize them into a tree structure.
    """
    # 1. Get all the goals of the user at once.
    flat_goals = []
    cursor = goals_collection.find({"user_id": user_id})
    async for goal in cursor:
        goal["sub_goals"] = []  # Preparing for nesting
        flat_goals.append(goal)

    # 2. Reconstruct the flat list into a tree structure in memory.
    goal_map = {str(goal["_id"]): goal for goal in flat_goals}
    root_goals = []

    for goal in flat_goals:
        parent_id = goal.get("parent_id")
        if parent_id and parent_id in goal_map:
            # If it has a parent goal，add it into the parent goal's sub_goals list.
            parent_goal = goal_map[parent_id]
            parent_goal["sub_goals"].append(goal)
        else:
            # If it has no parent, it's a root goal.
            root_goals.append(goal)
            
    return root_goals

# --- Get subgoals ---
async def get_sub_goals(parent_goal_id: str) -> List[dict]:
    cursor = goals_collection.find({"parent_id": parent_goal_id})
    return await cursor.to_list(length=None)

# --- Update ---
async def update_goal(goal_id: str, update_data: Dict[str, Any]) -> int:
    try:
        obj_id = ObjectId(goal_id)
        # Security: Avoid updating immutable fields
        if "_id" in update_data: del update_data["_id"]
        if "user_id" in update_data: del update_data["user_id"]
        
        if not update_data: return 0

        result = await goals_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        print(f"Goal updated: Matched {result.matched_count}, Modified {result.modified_count}.")
        return result.modified_count
    except Exception as e:
        print(f"An error occurred during goal update: {e}")
        return 0

# --- Delete ---
async def delete_goal(goal_id: str) -> dict:
    """
    Deletes a goal. If the goal has sub-goals, they are re-parented
    to their grandparent before the goal is deleted.
    :param goal_id: The ID of the goal to delete.
    :return: A dictionary summarizing the operation.
    """
    try:
        obj_id = ObjectId(goal_id)

        # 1. First, get the goal we intend to delete to find its parent_id
        goal_to_delete = await get_goal_by_id(goal_id)
        if not goal_to_delete:
            print("Goal not found.")
            return {"deleted_count": 0, "reparented_count": 0}

        # The ID of the "grandparent" goal
        grandparent_id = goal_to_delete.get("parent_id")

        # 2. Find all direct sub-goals
        sub_goals = await get_sub_goals(goal_id)
        
        reparented_count = 0
        if sub_goals:
            # 3. Use update_many for efficiency: update all sub-goals in one go
            # Set their parent_id to the grandparent_id
            update_result = await goals_collection.update_many(
                {"parent_id": goal_id}, # Filter: find all children of the goal
                {"$set": {"parent_id": grandparent_id}} # Action: update their parent_id
            )
            reparented_count = update_result.modified_count
            print(f"{reparented_count} sub-goals were re-assigned.")

        # 4. Now that children are safe, delete the actual goal
        delete_result = await goals_collection.delete_one({"_id": obj_id})
        
        print(f"Goal {goal_id} deleted successfully.")
        return {"deleted_count": delete_result.deleted_count, "reparented_count": reparented_count}

    except Exception as e:
        print(f"An error occurred during goal deletion: {e}")
        return {"deleted_count": 0, "reparented_count": 0}