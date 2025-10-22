import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from unittest.mock import MagicMock
from fastapi import FastAPI, Depends
import asyncio

# --- 1. 模拟 / 复制 依赖结构 (Mocking/Copying Dependencies) ---

# 模拟用户在 api.models 中定义的 Pydantic 模型
class UserMessage(BaseModel):
    message: str

class AIResponse(BaseModel):
    response: str

# 模拟 brain2.Brain 类
# 我们使用 MagicMock 来模拟它，这样我们就可以检查它的方法是否被调用
class MockBrain:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # 模拟 run_conscious_loop 方法，它是一个异步方法
        self.run_conscious_loop = MagicMock(
            side_effect=lambda msg: asyncio.Future()
        )
        self.run_conscious_loop.side_effect.set_result = lambda result: result # 简化异步 mock

# 模拟 api.dependencies.get_brain 依赖函数
# 它应该返回一个 Brain 实例
def get_brain():
    """这是真实的依赖，但在测试中会被覆盖。"""
    # 实际代码会返回一个真实配置的 Brain 实例
    return MockBrain(user_id="real_user_id_123") 

# --- 2. 复制你的 main.py 逻辑 ---

# 假设你的 main.py 内容如下 (为了测试自包含，直接在这里定义)
# 注意：我们在这里使用了原始的 get_brain 依赖定义
app = FastAPI()

@app.post("/process-message", response_model=AIResponse)
async def process_message_endpoint(
    user_input: UserMessage,
    brain: MockBrain = Depends(get_brain) # 注意类型提示在测试中使用了 MockBrain
):
    """
    接收消息并使用 Brain 实例进行处理。
    """
    # 确保 run_conscious_loop 返回一个字符串
    ai_reply = await brain.run_conscious_loop(user_input.message)
    
    return AIResponse(response=ai_reply)

# --- 3. 测试准备 (Setup for Testing) ---

# 实例化 TestClient
client = TestClient(app)

# 创建一个用于覆盖依赖的函数。
# 这个函数返回的 MockBrain 实例需要被我们“记住”，以便后续检查它是否被调用。
mock_brain_instance = MockBrain(user_id="test_user_456")

def override_get_brain():
    """用于测试环境的依赖覆盖函数。"""
    # 每次调用依赖时都返回同一个 Mock 实例
    return mock_brain_instance

# 在测试开始前，覆盖依赖
app.dependency_overrides[get_brain] = override_get_brain


# --- 4. 编写测试函数 (Writing Test Functions) ---

@pytest.mark.asyncio
async def test_process_message_success():
    """测试 /process-message 端点是否成功处理请求并调用 Brain。"""
    
    # 定义测试输入数据
    test_message = "帮我总结一下昨天的会议要点。"
    expected_response_text = "好的，这是会议总结：..."
    
    # 设定 MockBrain 的行为：当 run_conscious_loop 被调用时，返回预期的响应文本
    # 注意：由于 Brain.run_conscious_loop 是异步的，我们需要模拟异步返回值
    mock_brain_instance.run_conscious_loop.side_effect = \
        lambda msg: expected_response_text # 简化：直接返回字符串，TestClient会处理async/await
    
    # 发送 POST 请求
    response = client.post(
        "/process-message",
        json={"message": test_message}
    )
    
    # 1. 验证 HTTP 状态码
    assert response.status_code == 200
    
    # 2. 验证响应 JSON 结构和内容
    response_data = response.json()
    assert "response" in response_data
    assert response_data["response"] == expected_response_text
    
    # 3. **验证依赖被正确调用 (核心测试点)**
    # 检查 mock_brain_instance 的 run_conscious_loop 方法是否被调用了一次
    mock_brain_instance.run_conscious_loop.assert_called_once()
    
    # 4. 验证 Brain 接收到了正确的用户输入
    mock_brain_instance.run_conscious_loop.assert_called_with(test_message)

# 提示：运行测试的命令行：
# pip install pytest pytest-asyncio
# pytest test_main.py
