from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime
from bson import ObjectId

# --- Helper class for MongoDB's ObjectId ---
class PyObjectId(ObjectId):
    # ... (the same helper class code as before)
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v): raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# --- User Models ---
# 这是数据库中存储的完整User模型
class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    name: str
    hashed_password: str

    class Config:
        json_encoders = {ObjectId: str} # 让id可以被序列化为字符串
        arbitrary_types_allowed = True
        
# 这是我们用来在代码中传递User信息的模型（通常不包含密码）
# 你在api/auth.py里的 get_current_user 函数，就应该返回这个类型
class User(BaseModel):
    id: str
    email: EmailStr
    name: str


# --- Goal Model ---
class GoalModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    parentgoal: Optional[list[str]] = None
    status: Literal["active", "completed", "paused", "deleted"]
    weight: int = Field(..., ge=0, le=100)
    description: Optional[str] = None
    created_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# --- Profile Model ---
class ProfileEntryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    scope: Literal["project", "system", "hobby", "habit", "personality"]
    text: str
    confidence: int = Field(..., ge=0, le=100) # 0-100之间的整数, ... means the field is required

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# ----- Task Models set below -----
# --- Simple, nested data structures ---
class ValueFactorsModel(BaseModel):
    urgency: int
    importance: int
    due_soon: int
    user_defined: int
    contextual_relevance: int
    historical_performance: int

class DescriptionModel(BaseModel):
    field: str
    confidence: int = Field(..., ge=0, le=100)
    last_updated: datetime

class FrequencyModel(BaseModel):
    field: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY", "QUANTITY"]
    number: int
    last_updated: datetime

class MetricsModel(BaseModel):
    success_count: int
    failure_count: int
    created_at: datetime
    last_done_at: datetime
    
class DynamicPriorityModel(BaseModel):
    value: int
    confidence: int = Field(..., ge=0, le=100)
    last_updated: datetime

# --- Models for each type of schedule entry ---

class WindowModel(BaseModel):
    start: datetime
    end: datetime

class AbsoluteScheduleModel(BaseModel):
    mode: Literal["absolute"]
    time: str
    location: Optional[str] = None
    confidence: int = Field(..., ge=0, le=100)
    todo_list: Optional[List[str]] = None

class FuzzyScheduleModel(BaseModel):
    mode: Literal["fuzzy"]
    time: str
    location: Optional[str] = None
    confidence: int = Field(..., ge=0, le=100)
    todo_list: Optional[List[str]] = None

class WorkflowScheduleModel(BaseModel):
    mode: Literal["workflow"]
    time: str
    location: Optional[str] = None # Adjusted to handle 'none' value
    confidence: int = Field(..., ge=0, le=100)
    todo_list: str

# --- Create a Union of all possible schedule types ---
PrescheduleItem = Union[AbsoluteScheduleModel, FuzzyScheduleModel, WorkflowScheduleModel]

# --- The Main Task Model ---

class TaskModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    target_goal_ids: List[str] = None
    target_goal_names: List[str] = None
    status: Literal["active", "completed", "paused", "deleted"]

    # Using the complex sub-models we created
    dynamic_priority: DynamicPriorityModel
    frequency: FrequencyModel
    description: DescriptionModel
    metrics: MetricsModel
    
    # Using the Union type for a list of mixed objects
    preschedule: List[PrescheduleItem]

    # These fields might not always be present
    tags: Optional[List[str]] = None

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True