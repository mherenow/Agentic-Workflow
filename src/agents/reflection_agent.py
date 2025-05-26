"""
Reflection Agent Module

This module defines an agent that evaluates the progress and results of task execution,
determines if the original query has been adequately addressed, and suggests refinements
to the plan when necessary.
"""

from src.utils.nvidia_llm import NvidiaNIMClient
from src.utils.state import WorkflowState
from typing import List, Dict

class ReflectionAgent:
    """
    Agent responsible for evaluating task execution progress and suggesting plan refinements.
    
    This agent analyzes the results of completed tasks, identifies issues with failed tasks,
    and suggests modifications or additions to the plan to better address the user's query.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Reflection Agent.
        
        Args:
            api_key (str): API key for the NVIDIA NIM LLM service
        """
        self.llm = NvidiaNIMClient(api_key)
    
    def should_refine_plan(self, state: WorkflowState) -> bool:
        """
        Determine if the current plan needs refinement.
        
        This method evaluates the state of task execution and determines if:
        1. Too many iterations have already occurred
        2. Tasks have failed and need to be modified
        3. No tasks have been completed or are pending
        4. Completed tasks don't adequately address the original query
        
        Args:
            state (WorkflowState): Current state of the workflow
            
        Returns:
            bool: True if the plan should be refined, False otherwise
        """
        # Categorize tasks by status
        completed_tasks = [task for task in state["tasks"] if task.status == "completed"]
        failed_tasks = [task for task in state["tasks"] if task.status == "failed"]
        pending_tasks = [task for task in state["tasks"] if task.status == "pending"]

        # Limit the number of iterations to prevent infinite loops
        if state["iteration_count"] >= 3:
            return False
        
        # Refine the plan if there are failed tasks and we haven't tried too many times
        if failed_tasks and state["iteration_count"] < 2:
            return True
        
        # Refine if no tasks have been completed or are pending
        if not completed_tasks and not pending_tasks and state["iteration_count"] < 1:
            return True
        
        # If tasks have been completed, check if they adequately address the query
        if completed_tasks:
            analysis_prompt = f"""Analyze if the original query has been adequately addressed:

Original Query: {state["original_query"]}

Completed Tasks:
{chr(10).join([f"- {t.description}: {t.result}" for t in completed_tasks])}

Failed Tasks:
{chr(10).join([f"- {t.description}: {t.error}" for t in failed_tasks])}

Question: Does the completed work adequately address the original query? 
Respond with only "yes" or "no"."""
            
            response = self.llm.invoke(analysis_prompt, temperature=0.1)
            return "no" in response.lower()
        
        return False
    
    def suggest_refinements(self, state: WorkflowState) -> List[Dict]:
        """
        Suggest refinements to the current plan.
        
        This method suggests:
        1. Modifications to failed tasks to make them simpler or more likely to succeed
        2. Additional tasks if no tasks have been completed successfully
        
        Args:
            state (WorkflowState): Current state of the workflow
            
        Returns:
            List[Dict]: A list of refinement suggestions, where each suggestion is
                       a dictionary with action type and parameters
        """
        # Categorize tasks by status
        failed_tasks = [t for t in state["tasks"] if t.status == "failed"]
        completed_tasks = [t for t in state["tasks"] if t.status == "completed"]

        refinements = []

        # Generate refinements for failed tasks
        for task in failed_tasks:
            refinement_prompt = f"""The task "{task.description}" failed with error: {task.error}

Suggest a simpler alternative task that might work better.
Respond with only the new task description, no additional text."""

            response = self.llm.invoke(refinement_prompt, temperature=0.2)
            
            refinements.append({
                "action": "modify",
                "task_id": task.id,
                "new_description": response.strip(),
                "new_tool": task.tool_used  # Keep same tool for now
            })
        
        # Suggest additional tasks if needed
        if not completed_tasks:
            additional_prompt = f"""The original query "{state["original_query"]}" hasn't been adequately addressed.
            
Suggest one additional simple task that could help answer this query.
Available tools: web_search, calculator, weather

Respond in format: "task description|tool_name"
Example: "search for Python tutorials|web_search"
"""
            
            response = self.llm.invoke(additional_prompt, temperature=0.2)

            if "|" in response:
                parts = response.strip().split("|")
                if len(parts) == 2:
                    refinements.append({
                        "action": "add",
                        "description": parts[0].strip(),
                        "tool": parts[1].strip()
                    })
        return refinements
    