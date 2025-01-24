from typing import Dict, Any, List

class Tool:
    def __init__(self, name: str, description: str, function: callable, required_params: List[str] = None):
        self.name = name
        self.description = description
        self.function = function
        self.required_params = required_params or []

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, function: callable, required_params: List[str] = None):
        self.tools[name] = Tool(name, description, function, required_params)

    def get_tool(self, name: str) -> Tool:
        return self.tools.get(name)

    def get_tool_descriptions(self) -> str:
        descriptions = []
        for tool in self.tools.values():
            params = ", ".join(tool.required_params) if tool.required_params else "none"
            descriptions.append(f"Tool: {tool.name}\nDescription: {tool.description}\nRequired Parameters: {params}\n")
        return "\n".join(descriptions)
