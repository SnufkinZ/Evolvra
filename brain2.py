from tool_registry import ToolRegistry
from openai import AsyncOpenAI
from Brain.Functions import defination
from typing import List, Dict, Any
import json
import os
from operation_library.task_repository import TaskRepository
from operation_library.goal_repository import GoalRepository
from neocortex import NeocortexManager
from brain_memory.emotion import Emotion
from llm_provider import LLMProvider

class Brain:
    def __init__(self, task_repo: TaskRepository, goal_repo: GoalRepository, user_id: str):
        self.user_id = user_id
        self.llm_provider = LLMProvider()
        self.tool_registry = ToolRegistry() # Placeholder user_id
        self.neocortex_manager = NeocortexManager(user_id=user_id)
        self.emotion = Emotion(user_id=user_id)
        self.repository_map = {
            "task_repo": self.task_repo,
            "goal_repo": self.goal_repo
        }
        self._register_all_tools()

    def _register_all_tools(self):
        self.tool_registry.register_from_repository("task_repo", self.task_repo)
        self.tool_registry.register_from_repository("goal_repo", self.goal_repo)

    async def run_conscious_loop(self, user_message: str) -> str:
        # --- 1. ENRICH THE CONTEXT WITH MEMORY ---
        relevant_memories = await self.memory.search_memories(user_message, top_k=5)
        memory_context = "\n".join([f"-{mem}" for mem in relevant_memories])

        # --- 2. Create THE CONTEXT FOR THE LLM ---
        persona = self.memory.get_persona()

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": f"{persona}\Here are some relevant past memories to consider:\n{memory_context}"},
            {"role": "user", "content": user_message}
        ]

        # --- 3. Get THE EMOTIONAL STATE ---
        current_emotion_state = await self.emotion.get_emotion_state()
        max_steps = self.emotion.max_steps # Assuming max_steps is on the Emotion object

        try:
            # --- 意图理解层 ---
            for step in range(max_steps):
                print(f"\n--- Brain Step {step + 1} ---")

                response = self.llm_provider.think_with_tools(messages, self.tool_registry.get_definitions_for_llm())

                response_message = response.choices[0].message
                messages.append(response_message)

                # --- 指令执行层 ---
                if response_message.tool_calls:
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Invoking function: {function_name}({function_args})")

                        tool_info = self.tool_registry.get_tool_for_execution(function_name)
                        
                        if not tool_info:
                            messages.append(f"Error: Function '{function_name}' is not registered.")
                            continue
                        else:
                            source_repo_name = tool_info["source_repo"]
                            method_name = tool_info["internal_method_name"]
                            instance_repo = self.repository_map[source_repo_name]
                            result = await getattr(instance_repo, method_name)(**function_args)
                            
                            print(f"Observation: {result}")
                            messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": str(result), # Result must be a string
                                })
                    continue
                elif response_message.content:
                    print(f"The response from LLM: {response_message.content}")
                    continue        
                else:
                    return "The process is compelete."
                
            return "The agent reached the maximum number of steps."
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Sorry, I encountered an error."
        
