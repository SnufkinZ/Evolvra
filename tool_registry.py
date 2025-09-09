from typing import Callable, Dict, Any, List

class ToolRegistry:
    def __init__(self):
        # The key is the tool name for the LLM.
        # The value now stores WHERE to find the function.
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, source_repo: str, method_name: str, description: str, parameters: dict):
        """
        Registers a tool by specifying its source repository and method name.
        
        :param name: The name the LLM will use (e.g., "get_overdue_tasks").
        :param source_repo: The name of the repository instance (e.g., "task_repo").
        :param method_name: The actual method name on the repository object (e.g., "get_overdue_tasks").
        """
        self.tools[name] = {
            "source_repo": source_repo,
            "method_name": method_name,
            "description": description,
            "parameters": parameters
        }

    def get_tool_definitions_for_llm(self) -> List[Dict[str, Any]]:
        """Formats the tools into the JSON schema OpenAI expects."""
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": data["description"],
                    "parameters": data["parameters"]
                }
            } for name, data in self.tools.items()
        ]