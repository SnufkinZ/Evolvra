from pydantic import BaseModel

# 定义前端发来的请求体(Request Body)的结构
class UserMessage(BaseModel):
    message: str
    # 未来可以扩展，比如 user_id, conversation_id 等
    # user_id: str

# 定义后端返回的响应体(Response Body)的结构
class AIResponse(BaseModel):
    response: str