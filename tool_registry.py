from typing import Callable, Dict, Any, List


class ToolRegistry:
    def __init__(self):
        # The key is the tool name for the LLM.
        # The value now stores WHERE to find the function.
        self.tools: Dict[str, Dict[str, Any]] = {}
        
    def register_from_repository(self, repo_name: str, repo_instance: object):
        """Reads all master tool definitions from a repository and stores them."""
        tool_definitions = repo_instance.get_tool_definitions()
        for definition in tool_definitions:
            tool_name = definition["function"]["name"]
            self.tools[tool_name] = {
                "source_repo": repo_name,
                "master_definition": definition
            }

    def get_definitions_for_llm(self) -> List[Dict[str, Any]]:
        """
        VIEW #1: Generates the list in the exact format OpenAI needs.
        This method now correctly STRIPS OUT our internal keys.
        """
        llm_tools = []
        for name, data in self.tools.items():
            # Get the full master definition
            master_def = data["master_definition"]
            
            # Create a clean copy for the LLM. It only contains 'type' and 'function'.
            clean_def = {
                "type": master_def["type"],
                "function": master_def["function"]
            }
            llm_tools.append(clean_def)
            
        return llm_tools

    def get_tool_for_execution(self, name: str) -> Dict[str, Any] | None:
        """
        VIEW #2: Provides the internal information the AIBrain needs to execute the tool.
        """
        tool_data = self.tools.get(name)
        if not tool_data:
            return None
        
        return {
            "source_repo": tool_data["source_repo"],
            # Extract the internal method name from the master definition
            "internal_method_name": tool_data["master_definition"]["internal_method_name"]
        }