from tool_registry import ToolRegistry
from openai import AsyncOpenAI
from Brain.Functions import defination
from typing import List, Dict, Any
import json
import os
from operation_library.task_repository import TaskRepository
from operation_library.goal_repository import GoalRepository
from GlobalWorkspace import GlobalWorkspace
from llm_provider import LLMProvider

# Helper function from previous review
def format_system_prompt(workspace: GlobalWorkspace) -> str:
        # ... (implementation from the previous response) ...
        persona_str = "\n".join([f"  {k}: {v}" for k, v in workspace.persona.items() if k != '_id'])
        emotion_str = "\n".join([f"  {k}: {v}" for k, v in workspace.emotion.items() if k != '_id'])
        main_memory_str = "\n".join([f"- {item}" for item in workspace.main_memory])
        working_memory_str = workspace.working_memory if isinstance(workspace.working_memory, str) else "\n".join([f"- {item}" for item in workspace.working_memory])

        prompt = f"""
            # Your Persona
            {persona_str}
            # Your Current Emotion
            {emotion_str}
            # Your Core Memories (Remember these to avoid past mistakes and recall user preferences)
            {main_memory_str}
            # Your Relevant Memories for Current Task (Working Memory)
            {working_memory_str}
        """
        return prompt

class Brain:
    def __init__(self, task_repo: TaskRepository, goal_repo: GoalRepository, user_id: str):
        self.user_id = user_id
        self.llm_provider = LLMProvider()
        self.tool_registry = ToolRegistry() # Placeholder user_id
        self.global_workspace = GlobalWorkspace(self.user_id)
        self.task_repo = task_repo
        self.goal_repo = goal_repo
        self.repository_map = {
            "task_repo": self.task_repo,
            "goal_repo": self.goal_repo
        }

    async def _async_init(self):
        """Asynchronously loads the workspace and registers tools."""
        await self.global_workspace.load()
        self._register_all_tools()
        return self

    # Public factory method to create instances
    @classmethod
    async def create(cls, user_id: str, task_repo: TaskRepository, goal_repo: GoalRepository):
        """Creates and asynchronously initializes a Brain instance."""
        brain_instance = cls(task_repo, goal_repo, user_id)
        return await brain_instance._async_init()

    def _register_all_tools(self):
        self.tool_registry.register_from_repository("task_repo", self.task_repo)
        self.tool_registry.register_from_repository("goal_repo", self.goal_repo)

    async def run_conscious_loop(self, user_message: str) -> str:
        # --- 1. ENRICH THE CONTEXT WITH MEMORY ---
        await self.global_workspace.add_relevant_memories_to_work(user_message)
        who_you_are = format_system_prompt(self.global_workspace)
        # --- 2. PREPARE THE MESSAGES FOR LLM ---
        tool_definitions_json = json.dumps(self.tool_registry.tools)

        what_your_job_is = f"""  
        You are an advanced AI assistant designed to help the owner achieve their goals through thoughtful planning and tool usage.
        Here are the only functions (tools) you are allowed to use:
        {tool_definitions_json}
        At first, you need to understand the owner's words deeply: ask yourself weather the owner needs help or just wants to chat.
        If the owner just wants to chat, respond briefly like a real human without using any tools.

        **CRITICAL RULE:** For simple greetings ("hello", "hi", "how are you"), small talk, or simple questions that can be answered in one sentence, you **MUST** set "max_steps" to 0.
        Use "max_steps" 1 or more **ONLY** if the request requires using a tool or a multi-stage thought process.
        
        Return the result strictly in the following JSON schema:
        {{
          "thinking": "Your thinking to the owner's messages before the final reponse.",
          "max_steps": "An integer (0-10).",
          "response": "Your final response to the owner."
        }}
        """
        messages_recorder = f"History messages:{self.global_workspace.context},current message:{user_message}"
        self.global_workspace.add_to_context(f"Owner:{user_message}")
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": f"{who_you_are}"},
            {"role": "developer", "content": what_your_job_is},
            {"role": "user", "content": messages_recorder}
        ]
        print(f"Prepared 'system messages' for LLM: {who_you_are}")
        print(f"--------------------------------------------------------")
        print(f"Prepared 'user messages' for LLM: {messages_recorder}")
        # --- 3. Get THE EMOTIONAL STATE ---
        max_steps = self.global_workspace.emotion["energy"]

        try:
            # --- 意图理解层 ---
            plan_json = await self.llm_provider.think_with_tools(messages, model_choice="powerful")
            print(f"--------------------------------------------------------")
            print(f"Plan JSON received from LLM: {plan_json}")
            
            max_steps = int(plan_json.get("max_steps",0))
            thinking_plan = plan_json.get("thinking","")
            if max_steps == 0:
                final_response = plan_json.get("response","I've completed the thought process.")
                print(f"--------------------------------------------------------")
                print(f"Final response from LLM(0 steps): {final_response}")
                self.global_workspace.add_to_context(f"You:{final_response}")
                await self.global_workspace.save()
                print (f"Workspace for user {self.user_id} saved.")
                return final_response
            
            planning_message_for_context = {
                        "role": "assistant",
                        "content": json.dumps(plan_json) # 将规划字典转为字符串存入 content
                    }
            self.global_workspace.add_to_context(f"You:{json.dumps(plan_json)}")

            excuse_hitory = {}

            for step in range(min(max_steps,10)):
                print(f"\n--- Brain Step {step + 1} ---")

                record_messages: List[Dict[str, Any]] = [
                    {"role": "system", "content": f"{who_you_are}"},
                    {"role": "user", "content": f"Based on our conversation history and your plan, execute the next step. Your plan was: '{thinking_plan}'. The original request was: '{user_message}'. Here is the excuse history so far: '{json.dumps(excuse_hitory)}'."},
                ]
                response_message = await self.llm_provider.think_with_tools(record_messages, self.tool_registry.get_definitions_for_llm(), model_choice="fast")
                
                print(f"--------------------------------------------------------")
                print(f"Response from LLM (Step {step+1}): {response_message}")
                excuse_hitory[f"Step {step+1}"] = response_message

                # --- 指令执行层 ---
                if response_message.tool_calls:
                    tool_calls_str = json.dumps([tc.function.model_dump() for tc in response_message.tool_calls])
                    self.global_workspace.add_to_context(f"You (Tool Call):{tool_calls_str}")

                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Invoking function: {function_name}({function_args})")

                        tool_info = self.tool_registry.get_tool_for_execution(function_name)
                        
                        if not tool_info:
                            excuse_hitory[f"Step {step+1} result"]=f"Error: Function '{function_name}' is not registered."
                            continue
                        else:
                            source_repo_name = tool_info["source_repo"]
                            method_name = tool_info["internal_method_name"]
                            instance_repo = self.repository_map[source_repo_name]
                            result = await getattr(instance_repo, method_name)(**function_args)
                            
                            print(f"Observation: {result}")
                            excuse_hitory[f"Step {step+1} result"]={
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": str(result), # Result must be a string
                                }
                        self.global_workspace.add_to_context(f"Tool Result ({function_name}): {str(result)}")
                    continue
                elif response_message.content:
                    self.global_workspace.add_to_context(f"You:{response_message.content}")
                    print(f"Final response from LLM (Step {step+1}): {response_message.content}")
                    await self.global_workspace.save()
                    return response_message.content
                else:
                    return "The process is compelete."
            final_answer = "I have completed the steps based on my plan."
            await self.global_workspace.save()
            return final_answer
                    
        except json.JSONDecodeError as e:
            print(f"An error occurred: Failed to decode LLM's JSON response. {e}")
            return "Sorry, I had a little trouble formatting my thoughts."
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Sorry, I encountered an error."
        
