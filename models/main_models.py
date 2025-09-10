from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

# 这是一个辅助类，用来让Pydantic能够正确处理MongoDB的ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
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

# --- Task Model ---
class TaskModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    status: str = "active"
    deadline: Optional[datetime] = None
    # ... 你可以添加任何其他在Task中需要的字段

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# --- Goal Model ---
class GoalModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None # 注意：这里是字符串ID，而不是PyObjectId
    weight: int = 50

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

# --- Profile Model ---
class ProfileEntryModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    text: str
    scope: str
    confidence: float

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True