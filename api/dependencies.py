from fastapi import Depends
from operation_library.task_repository import TaskRepository
from operation_library.goal_repository import GoalRepository
from brain2 import Brain # Assuming your Brain class is in brain/brain.py
from database import tasks_collection, goals_collection
from .auth import get_current_user
from models.main_models import User

# --- Repository Dependencies ---
def get_task_repo(current_user: User = Depends(get_current_user)) -> TaskRepository:
    """
    This function is called by FastAPI for each request.
    It gets the current user, and creates a TaskRepository with that user's ID.
    """
    return TaskRepository(user_id=current_user.id)

def get_goal_repo(current_user: User = Depends(get_current_user)) -> GoalRepository:
    """Creates a GoalRepository instance scoped to the current user."""
    return GoalRepository(user_id=current_user.id)


# --- Brain Dependency ---
async def get_brain(
    task_repo: TaskRepository = Depends(get_task_repo),
    goal_repo: GoalRepository = Depends(get_goal_repo)
) -> Brain:
    """
    This master dependency is now ASYNC.s
    It uses the .create() factory to build a fully initialized,
    ready-to-use Brain instance.
    """
    # Instead of calling the constructor directly...
    # return Brain(task_repo=task_repo, goal_repo=goal_repo, user_id=task_repo.user_id)
    
    # ...we now await the asynchronous factory method!
    return await Brain.create(task_repo=task_repo, goal_repo=goal_repo,user_id=task_repo._user_id)