from tool_registry import ToolRegistry
from openai import AsyncOpenAI
from Brain.Functions import defination
from typing import List
import json
import os
from operation_library.task_repository import TaskRepository
from operation_library.goal_repository import GoalRepository

class Brain:
    def __init__(self, task_repo: TaskRepository, goal_repo: GoalRepository, user_id: str):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tool_registry = ToolRegistry() # Placeholder user_id
        self.repository_map = {
            "task_repo": self.task_repo,
            "goal_repo": self.goal_repo
        }
        self._register_all_tools()

    def _register_all_tools(self):
        self.tool_registry.register_from_repository("task_repo", self.task_repo)
        self.tool_registry.register_from_repository("goal_repo", self.goal_repo)

    async def process_user_message(self, message: str) -> str:
        try:
            # --- 意图理解层 ---
            response = await self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that decides which functions to call based on user requests."},
                    {"role": "user", "content": message}
                ],
                tools=self.tool_registry.get_definitions_for_llm(),
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
                    function_args = json.loads(tool_call.function.arguments)

                    tool_info = self.tool_registry.get_tool_for_execution(function_name)
                    if not tool_info:
                        execution_results.append(f"Error: Function '{function_name}' is not registered.")
                        continue
                    else:
                        source_repo_name = tool_info["source_repo"]
                        method_name = tool_info["internal_method_name"]
                    instance_repo = self.repository_map[source_repo_name]
                    result = await getattr(instance_repo, method_name)(**function_args)
                    execution_results.append(str(result)) # 将结果转为字符串并收集
                                    
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