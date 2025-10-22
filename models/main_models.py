from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler
from typing import Optional, List, Dict, Any, Literal, Union, Type
from datetime import datetime
from bson import ObjectId
from pydantic_core import CoreSchema, core_schema, ValidationError

# --- Helper class for MongoDB's ObjectId (Pydantic V2 FIX) ---
class PyObjectId(ObjectId):
    """
    Custom type for MongoDB's ObjectId when used with Pydantic v2.
    It handles validation and serialization to/from strings.
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        
        def validate_object_id(value: Union[str, ObjectId]) -> ObjectId:
            """
            Custom validator that checks if the input is a valid ObjectId 
            or a valid string representation, and returns an ObjectId instance.
            """
            if isinstance(value, ObjectId):
                return value
            
            if not ObjectId.is_valid(value):
                # Raise Pydantic's internal ValidationError for clear error messages
                raise ValueError("Invalid ObjectId string")
            
            return ObjectId(value)

        # 核心逻辑：定义 Pydantic 应该如何处理这个类型
        object_id_schema = core_schema.chain_schema(
            [
                # 1. 尝试从字符串（API输入）或ObjectId实例（数据库读取）中验证
                core_schema.union_schema([
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.str_schema(min_length=24, max_length=24),
                ]),
                # 2. 调用我们的自定义验证函数
                core_schema.no_info_plain_validator_function(validate_object_id),
            ],
            # 3. 序列化（输出到 JSON 时）：强制转换为字符串
            serialization=core_schema.to_string_ser_schema(),
        )

        return object_id_schema

# --- User Models ---
# 这是数据库中存储的完整User模型
class UserModel(BaseModel):
    # Field(default_factory=PyObjectId) 仍然工作，但 alias="_id" 是关键
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    name: str
    hashed_password: str

    class Config:
        # Pydantic v2 不再需要 json_encoders = {ObjectId: str}，
        # 因为 PyObjectId 类本身已经通过 __get_pydantic_core_schema__ 实现了序列化。
        arbitrary_types_allowed = True
        populate_by_name = True # 允许通过 alias（_id）进行赋值

        
# 这是我们用来在代码中传递User信息的模型（通常不包含密码）
class User(BaseModel):
    # 将 PyObjectId 转换为 str 用于外部 API
    id: str
    email: EmailStr
    name: str


# --- Goal Model ---
class GoalModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    parent_goal: Optional[list[str]] = None # 修复了原始代码中的 parentgoal 拼写
    weight: int = Field(..., ge=0, le=100)
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Literal["active", "completed", "paused", "deleted"]

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

# --- Profile Model ---
class ProfileEntryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    scope: Literal["project", "system", "hobby", "habit", "personality"]
    text: str
    confidence: int = Field(..., ge=0, le=100)

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

# ----- Task Models set below -----
# --- Simple, nested data structures ---
class TaskModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: str
    schedule: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Literal["active", "completed", "paused", "deleted"] = "active"

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

# class ValueFactorsModel(BaseModel):
#     urgency: int
#     importance: int
#     due_soon: int
#     user_defined: int
#     contextual_relevance: int
#     historical_performance: int

# class DescriptionModel(BaseModel):
#     field: str
#     confidence: int = Field(..., ge=0, le=100)
#     last_updated: datetime

# class FrequencyModel(BaseModel):
#     field: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY", "QUANTITY"]
#     number: int
#     last_updated: datetime

# class MetricsModel(BaseModel):
#     success_count: int
#     failure_count: int
#     created_at: datetime
#     last_done_at: datetime
    
# class DynamicPriorityModel(BaseModel):
#     value: int
#     confidence: int = Field(..., ge=0, le=100)
#     last_updated: datetime

# # --- Models for each type of schedule entry ---

# class WindowModel(BaseModel):
#     start: datetime
#     end: datetime

# class AbsoluteScheduleModel(BaseModel):
#     mode: Literal["absolute"]
#     time: str
#     location: Optional[str] = None
#     confidence: int = Field(..., ge=0, le=100)
#     todo_list: Optional[List[str]] = None

# class FuzzyScheduleModel(BaseModel):
#     mode: Literal["fuzzy"]
#     time: str
#     location: Optional[str] = None
#     confidence: int = Field(..., ge=0, le=100)
#     todo_list: Optional[List[str]] = None

# class WorkflowScheduleModel(BaseModel):
#     mode: Literal["workflow"]
#     time: str
#     location: Optional[str] = None # Adjusted to handle 'none' value
#     confidence: int = Field(..., ge=0, le=100)
#     todo_list: str

# # --- Create a Union of all possible schedule types ---
# PrescheduleItem = Union[AbsoluteScheduleModel, FuzzyScheduleModel, WorkflowScheduleModel]

# # --- The Main Task Model ---

# class TaskModel(BaseModel):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     user_id: str
#     name: str
#     target_goal_ids: List[str] = None
#     target_goal_names: List[str] = None
#     status: Literal["active", "completed", "paused", "deleted"]

#     # Using the complex sub-models we created
#     dynamic_priority: DynamicPriorityModel
#     frequency: FrequencyModel
#     description: DescriptionModel
#     metrics: MetricsModel
    
#     # Using the Union type for a list of mixed objects
#     preschedule: List[PrescheduleItem]

#     # These fields might not always be present
#     tags: Optional[List[str]] = None

#     class Config:
#         json_encoders = {ObjectId: str}
#         arbitrary_types_allowed = True