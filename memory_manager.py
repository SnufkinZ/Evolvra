# In main.py, or a new workspace_manager.py
from memory import Memory
import cachetools # A great library for caching! `pip install cachetools`

# Create a cache that holds a maximum of 500 user workspaces.
# When it's full, it will automatically remove the least recently used one.
workspace_cache = cachetools.LRUCache(maxsize=500)

async def get_workspace_for_user(user_id: str) -> Memory:
    """
    This function gets a user's Workspace, using a cache to avoid re-loading.
    """
    # Check if the user's workspace is in the cache
    if user_id in workspace_cache:
        print(f"CACHE HIT for user {user_id}")
        return workspace_cache[user_id]
    
    # CACHE MISS: If not, create a new one and load it
    print(f"CACHE MISS for user {user_id}")
    new_workspace = Memory(user_id=user_id)
    await new_workspace.initialize() # The one-time slow operation
    
    # Store the newly loaded workspace in the cache for next time
    workspace_cache[user_id] = new_workspace
    
    return new_workspace