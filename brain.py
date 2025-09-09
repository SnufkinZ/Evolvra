import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from Brain.Functions import defination
from operation_library import task_repository, goal_operations

load_dotenv()

import json
from typing import List # 导入List类型提示

class AIBrain:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # 1.【改进】使用函数字典进行动态分发，替代 if/elif
        self.function_registry = {
            "create_task": task_repository.get_overdue_tasks,
            "create_goal": goal_operations.create_goal,
            "update_task": task_operations.update_task,
            "update_goal": goal_operations.update_goal,
            "get_task_by_id": task_operations.get_task_by_id,
            # ... 在这里注册所有你的函数
        }

    async def process_user_message(self, message: str) -> str:
        """
        处理单条用户消息，决定并执行函数，返回结果。
        这是一个完整的、可重复使用的处理单元。
        """
        try:
            # --- 意图理解层 ---
            response = await self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that decides which functions to call based on user requests."},
                    {"role": "user", "content": message}
                ],
                tools=defination.classification_tool,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # --- 指令执行层 ---
            if tool_calls:
                # 【修正】创建一个列表来收集所有函数调用的结果
                execution_results: List[str] = []
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    print(f"Invoking function: {function_name}")
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"With arguments: {function_args}")

                    if function_name in self.function_registry:
                        function_to_call = self.function_registry[function_name]
                        result = await function_to_call(**function_args)
                        print(f"Function '{function_name}' executed with result: {result}")
                        execution_results.append(str(result)) # 将结果转为字符串并收集
                    else:
                        execution_results.append(f"Error: Function '{function_name}' is not registered.")
                
                # 【修正】在循环结束后，将所有结果合并成一个字符串返回
                # 这样即使 tool_calls 是空列表，也会返回一个空字符串，而不是None
                return "\n".join(execution_results)
            else:
                # 如果LLM认为不需要调用函数，可以直接返回它的文本回复
                # response_message.content 可能为 None，我们提供一个默认值
                return response_message.content or "I'm not sure how to respond to that."

        except Exception as e:
            print(f"An error occurred: {e}")
            return "Sorry, I encountered an error while processing your request."

# --- 如何使用这个新大脑？ ---
async def main():
    brain = AIBrain()
    
    user_input = "I am going to the centre library to attend the English Class at 6pm"
    # user_input = "I want to set a goal to learn Python this year"

    final_response = await brain.process_user_message(user_input)
    print("\nFinal Response to User:")
    print(final_response)

if __name__ == "__main__":
    asyncio.run(main())