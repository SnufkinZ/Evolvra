from fastapi import Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer # You will use this in a real app
from models.main_models import User # Assuming you have a Pydantic user model
from bson import ObjectId

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # For a real app

# For now, we'll create a FAKE dependency that returns a mock user
async def get_current_user() -> User:

    # ... 从数据库或token获取用户数据 (这是一个字典) ...
    user_data_from_db = {
        "_id": ObjectId("6530c117e1e6f1f3a2b4c5d6"),
        "email": "Alice@example.com",
        "name": "Alice",
        "hashed_password": "fakehashedpassword"
    }

    # 将数据库返回的字典转换为User对象
    # 注意我们是如何使用 id=str(user_data_from_db["_id"]) 来转换类型的
    return User(
        id=str(user_data_from_db["_id"]),
        email=user_data_from_db["email"],
        name=user_data_from_db["name"]
    )