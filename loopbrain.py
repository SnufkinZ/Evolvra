import os
import json
import asyncio
from openai import AsyncOpenAI
from typing import List, Dict, Any

# Assuming these are correctly set up and imported
from Brain.Functions import defination
from operation_library import task_operations, goal_operations

# ... (load_dotenv) ...

class AIBrain:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.function_registry = {
            "create_task": task_operations.create_task,
            "get_task_by_id": task_operations.get_task_by_id,
            "update_task": task_operations.update_task,
            # ... all your other functions
        }
        # A safety measure to prevent infinite loops
        self.max_steps = 10 

    async def run_agent_loop(self, user_message: str) -> str:
        """
        This is the main agent loop. It takes a user message,
        and cycles through thought, action, and observation until the task is complete.
        """
        # 1. Initialize the conversation history with the user's request
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": "You are a world-class autonomous agent. Your goal is to fulfill the user's request by creating a plan and using the available tools step-by-step. Reflect on the results of each tool call to inform your next action. Only provide the final answer to the user when the entire request is complete."},
            {"role": "user", "content": user_message}
        ]

        for step in range(self.max_steps):
            print(f"\n--- Agent Step {step + 1} ---")
            
            # --- REASON Step ---
            # The AI reasons based on the entire history
            print("AI is thinking...")
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # --- DECISION Step ---
            # Decide whether to act or to respond to the user

            if tool_calls:
                # --- ACT Step ---
                # The AI decided to use a tool.
                # Append the AI's decision to the history
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"Calling Function: {function_name}({function_args})")
                    
                    if function_name in self.function_registry:
                        function_to_call = self.function_registry[function_name]
                        try:
                            # Execute the actual function
                            result = await function_to_call(**function_args)
                        except Exception as e:
                            result = f"Error executing function: {e}"

                        # --- OBSERVATION Step ---
                        # Append the result of the tool call to the history
                        print(f"Observation: {result}")
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(result), # Result must be a string
                        })
                    else:
                         print(f"Error: Function {function_name} not found.")

                # Go to the next iteration of the loop
                continue

            else:
                # --- FINAL RESPONSE Step ---
                # The AI decided it's done and will respond directly to the user.
                print("AI decided to give a final answer.")
                return response_message.content or "Task completed."

        return "The agent reached the maximum number of steps without providing a final answer."

# --- Example Usage ---
async def main():
    brain = AIBrain()
    
    # A simple, single-step request
    # user_input = "Add a task to buy bread"

    # A more complex, multi-step request that requires a loop
    user_input = "Please create a new task to 'Plan the weekend trip', and then immediately update its description to 'Need to book flights and hotel'."

    final_response = await brain.run_agent_loop(user_input)
    print("\n--- Final Response to User ---")
    print(final_response)

if __name__ == "__main__":
    asyncio.run(main())