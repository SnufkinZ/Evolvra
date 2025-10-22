# brain/llm_provider.py
from openai import AsyncOpenAI
from typing import List, Dict, Any
import os
import json

class LLMProvider:
    def __init__(self):
        self.clients = {
            "fast": AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")),
            "powerful": AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")),
            # "o3": AnthropicClient(...),
            # "gpt5": ...
        }

    async def think_with_tools(self, messages: List[Dict], tools: List[Dict] = "", model_choice: str = "powerful") -> Dict[str, Any]:
        """Generates a response from the chosen LLM with tool usage."""        
        if model_choice == "powerful":
            client = self.clients[model_choice]

            response = await client.chat.completions.create(
                model="gpt-5", # This would also be dynamic
                messages=messages,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        
        elif model_choice == "fast":
            client = self.clients[model_choice]
            response = await client.chat.completions.create(
                model="gpt-5", # This would also be dynamic
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            return response.choices[0].message
        
        else:
            raise ValueError("Requested LLM model is not available.")

        