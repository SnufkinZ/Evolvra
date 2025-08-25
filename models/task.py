from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TaskSession(BaseModel):
    start_time: datetime
    end_time: datetime
    content: str

class RelatedGoal(BaseModel):
    goal_id: str
    contribution: float

class Task(BaseModel):
    task_id: str
    name: str
    description: Optional[str]
    sessions: List[TaskSession] = []
    related_goals: List[RelatedGoal] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
