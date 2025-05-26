"""
Plan Agent Module

This module defines a planning agent that breaks down user queries into specific,
actionable sub-tasks that can be executed by the workflow's tool agent.
"""

from src.utils.nvidia_llm import NvidiaNIMClient
from src.utils.state import WorkflowState, Task
import json
from typing import List

class PlanAgent:
    """
    Agent responsible for creating execution plans by breaking down user queries 
    into specific, actionable tasks that can be executed using available tools.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Plan Agent.
        
        Args:
            api_key (str): API key for the NVIDIA NIM LLM service
        """
        self.llm = NvidiaNIMClient(api_key)
    
    def plan(self, state: WorkflowState, available_tools: List[str]) -> List[Task]:
        """
        Create a plan of tasks based on the user's query and available tools.
        
        Args:
            state (WorkflowState): Current state of the workflow, including the original query
            available_tools (List[str]): List of tool names available for task execution
            
        Returns:
            List[Task]: A list of Task objects representing the execution plan
        """
        tools_str = "\n".join(available_tools)
    
        prompt = f"""You are a planning agent that breaks down user queries into specific, actionable sub-tasks.

Available tools:
{tools_str}

User Query: {state["original_query"]}

Rules:
1. Create 2-5 specific sub-tasks
2. Each task should use one available tool
3. Tasks should be in logical execution order
4. Be specific about what information is needed

Special instructions for flight-related tasks:
- If the user is asking about booking a flight, include a task to search for flight information
- For calculator tasks related to flight pricing, always include specific numerical values (use average prices if needed)
- For example, "Calculate estimated price with taxes and fees for a $1200 flight" instead of just "Add taxes and fees to flight price"

CRITICAL: Respond with ONLY a valid JSON array, no additional text or explanation:
[
    {{"description": "specific task description", "tool": "tool_name"}},
    {{"description": "another specific task", "tool": "tool_name"}}
]"""
    
        response = self.llm.invoke(prompt, temperature=0.1)

        try:
            # Clean up response if it contains markdown code blocks
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:-3]

            # Parse the JSON response
            tasks_data = json.loads(clean_response)
            tasks = []

            # Create Task objects from the parsed data
            for i, task_data in enumerate(tasks_data):
                if isinstance(task_data, dict) and "description" in task_data and "tool" in task_data:
                    task = Task(
                        id = i + 1,
                        description = task_data["description"],
                        status = "pending",
                        tool_used=task_data["tool"]
                    )
                    tasks.append(task)

            return tasks if tasks else self._create_fallback_task(state)
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response}")
            return self._create_fallback_task(state)
    
    def _create_fallback_task(self, state: WorkflowState) -> List[Task]:
        """
        Create a fallback task when plan generation fails.
        
        Args:
            state (WorkflowState): Current state of the workflow
            
        Returns:
            List[Task]: A single web search task as a fallback
        """
        return [Task(
            id=1,
            description=f"Search for information about: {state['original_query']}",
            status="pending",
            tool_used="web_search"
        )]