import os
from fastapi import FastAPI
from api.models import UserMessage, AIResponse  # 导入我们定义的数据模型
from brain import AIBrain  # 导入你写好的AIBrain类

# --- 初始化应用 ---

# 1. 创建FastAPI应用实例
app = FastAPI(
    title="Evolvra AI Personal Secretary API",
    description="API for the AI brain to interact with the frontend.",
    version="1.0.0"
)

# 2. 在应用启动时，创建一个AIBrain的单例
#    这样可以避免每次请求都重新加载模型和函数注册表，效率更高
brain_instance = AIBrain()

# --- API 端点 (Endpoint) ---

@app.get("/")
async def root():
    """一个简单的根端点，用来检查服务是否正在运行。"""
    return {"message": "Welcome to the Evolvra AI Brain API!"}


# 3. 这就是连接前端和大脑的核心端点
@app.post("/process-message", response_model=AIResponse)
async def process_message_endpoint(user_input: UserMessage):
    """
    接收前端发来的消息，激活大脑进行处理，然后返回大脑的响应。
    """
    print(f"Received message from frontend: '{user_input.message}'")

    # 4. 调用我们的大脑实例来处理消息
    #    因为 brain 的方法是 async 的，所以我们在这里 await 它
    ai_reply = await brain_instance.process_user_message(user_input.message)

    print(f"Sending response to frontend: '{ai_reply}'")

    # 5. 将大脑返回的字符串包装在我们的响应模型中并返回
    #    FastAPI会自动将其转换为JSON格式：{"response": "..."}
    return AIResponse(response=ai_reply)