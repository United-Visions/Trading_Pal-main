from typing import Dict, Any, List, Optional

class Tool:
    def __init__(self, name: str, description: str, function: callable, required_params: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.function = function
        self.required_params = required_params or []

    def execute(self, **kwargs):
        """Execute tool function with parameter validation"""
        try:
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in self.required_params}
            return self.function(**filtered_kwargs)
        except Exception as e:
            print(f"Tool execution error: {str(e)}")
            raise

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, function: callable, required_params: Optional[List[str]] = None):
        """Register a new tool with required parameters"""
        self.tools[name] = Tool(name, description, function, required_params)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all tools"""
        descriptions = []
        for tool in self.tools.values():
            params = ", ".join(tool.required_params) if tool.required_params else "none"
            descriptions.append(
                f"Tool: {tool.name}\n"
                f"Description: {tool.description}\n"
                f"Required Parameters: {params}\n"
            )
        return "\n".join(descriptions)
