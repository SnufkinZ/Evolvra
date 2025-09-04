from bson import ObjectId
from database import user_profiles_collection
from typing import Dict, Any, List

# --- Create ---
async def add_profile_entry(entry_data: dict) -> str:
    if "user_id" not in entry_data or "text" not in entry_data:
        raise ValueError("'user_id' and 'text' are required.")
    
    result = await user_profiles_collection.insert_one(entry_data)
    print(f"Profile entry created with ID: {result.inserted_id}")
    return str(result.inserted_id)

# --- Read ---
async def get_all_profile_entries_for_user(user_id: str) -> List[dict]:
    cursor = user_profiles_collection.find({"user_id": user_id})
    return await cursor.to_list(length=None) 

async def get_user_profile_as_text(user_id: str) -> str:
    """
    Get all profile entries for a user and consolidate them into a text block.
    This is for preparing context for LLM.
    """
    entries = await get_all_profile_entries_for_user(user_id)
    # sort by scope and confidence, higher confidence first
    entries.sort(key=lambda x: (x.get("scope", ""), x.get("confidence", 0)), reverse=True)
    
    profile_text = "\n".join([f"- {entry['text']} (source: {entry.get('scope', 'unknown')})" for entry in entries])
    return profile_text

# --- Update ---
async def update_profile_entry(entry_id: str, update_data: Dict[str, Any]) -> int:
    try:
        obj_id = ObjectId(entry_id)
        if "_id" in update_data: del update_data["_id"]
        if "user_id" in update_data: del update_data["user_id"]
        
        if not update_data: return 0

        result = await user_profiles_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        return result.modified_count
    except Exception:
        return 0

# --- Delete ---
async def delete_profile_entry(entry_id: str) -> int:
    try:
        obj_id = ObjectId(entry_id)
        result = await user_profiles_collection.delete_one({"_id": obj_id})
        return result.deleted_count
    except Exception:
        return 0