from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass
    
    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the tool with the given input."""
        pass

class ToolRegistry:
    """Registry for managing and accessing tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """Get a list of all available tool names."""
        return list(self._tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get a dictionary of tool names and their descriptions."""
        return {name: tool.description for name, tool in self._tools.items()}
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the registry."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all tools from the registry."""
        self._tools.clear()
    
    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools