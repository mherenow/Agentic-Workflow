"""
Tool Agent Module

This module defines an agent responsible for executing tasks using appropriate tools
from the tool registry. It extracts the necessary parameters from task descriptions
and handles the execution of tools, updating task status and results.
"""

from src.utils.nvidia_llm import NvidiaNIMClient
from src.tools.registry import ToolRegistry
from src.utils.state import Task

class ToolAgent:
    """
    Agent responsible for executing tasks using registered tools.
    
    This agent extracts the necessary parameters from task descriptions,
    executes the appropriate tool, and updates task status and results.
    """
    
    def __init__(self, tool_registry: ToolRegistry, api_key: str):
        """
        Initialize the Tool Agent.
        
        Args:
            tool_registry (ToolRegistry): Registry containing available tools
            api_key (str): API key for the NVIDIA NIM LLM service
        """
        self.llm = NvidiaNIMClient(api_key)
        self.tool_registry = tool_registry

    def execute_task(self, task: Task) -> Task:
        """
        Execute a task using the appropriate tool.
        
        This method:
        1. Retrieves the appropriate tool from the registry
        2. Uses the LLM to extract specific input parameters from the task description
        3. Executes the tool with the extracted parameters
        4. Updates the task status and result/error
        
        Args:
            task (Task): The task to execute
            
        Returns:
            Task: The updated task with execution results or error information
        """
        try:
            # Get the appropriate tool from the registry
            tool = self.tool_registry.get_tool(task.tool_used)
            if not tool:
                task.status = "failed"
                task.error = f"Tool '{task.tool_used}' not available"
                return task
                
            # Create a prompt to extract the specific input needed for the tool
            extraction_prompt = f"""Extract the specific input needed for the {task.tool_used} tool from this task:
"{task.description}"

For example:
- If tool is "calculator" and task is "calculate 25 + 30", respond with: 25 + 30
- If tool is "calculator" and task is "add estimated taxes and fees to flight price of $500", respond with: 500
- If tool is "web_search" and task is "search for weather in NYC", respond with: weather in NYC
- If tool is "weather" and task is "get weather for Boston", respond with: Boston

For calculator tasks related to flights, taxes, or fees, extract the numerical values if present, or use relevant default values.

Respond with ONLY the extracted input, no additional text."""
            
            # Use the LLM to extract the specific input for the tool
            query_response = self.llm.invoke(extraction_prompt, temperature=0.0)
            tool_input = query_response.strip()

            # Execute the tool with the extracted input
            result = tool.execute(tool_input)

            # Update the task with the result or error
            if result.get("success", True):
                task.result = result.get("result", str(result))
                task.status = "completed"
            else:
                task.status = "failed"
                task.error = result.get("error", "Tool execution failed")
            return task
        
        except Exception as e:
            # Handle any exceptions during execution
            task.status = "failed"
            task.error = f"Execution error: {str(e)}"
            return task
        