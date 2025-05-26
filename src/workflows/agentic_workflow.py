"""
Agentic Workflow Module

This module defines the core workflow for the agentic system, orchestrating the interaction
between different agents (planning, execution, and reflection) to process user queries
through a series of steps: planning, execution, reflection, and finalization.
"""

from langgraph.graph import StateGraph, END
from src.utils.nvidia_llm import NvidiaNIMClient
from src.utils.state import WorkflowState, Task
from src.agents.plan_agent import PlanAgent
from src.agents.tool_agent import ToolAgent
from src.agents.reflection_agent import ReflectionAgent
from src.tools.registry import ToolRegistry
from src.tools.web_search import WebSearchTool
from src.tools.calculator import CalculatorTool
from src.tools.weather import WeatherTool
from config.settings import NVIDIA_API_KEY, TAVILY_API_KEY

def create_workflow() -> StateGraph:
    """
    Create and configure the agentic workflow graph.
    
    This function:
    1. Sets up the tool registry with available tools
    2. Initializes the planning, tool execution, and reflection agents
    3. Defines the node functions for each stage of the workflow
    4. Creates and configures the workflow graph with appropriate edges and conditions
    
    Returns:
        StateGraph: A compiled workflow graph ready for execution
    """
    # Initialize tool registry and register available tools
    tool_registry = ToolRegistry()
    tool_registry.register_tool(WebSearchTool(TAVILY_API_KEY))
    tool_registry.register_tool(CalculatorTool())
    tool_registry.register_tool(WeatherTool())
    
    # Initialize agents
    plan_agent = PlanAgent(NVIDIA_API_KEY)
    tool_agent = ToolAgent(tool_registry, NVIDIA_API_KEY)
    reflection_agent = ReflectionAgent(NVIDIA_API_KEY)
    
    def plan_node(state: WorkflowState) -> WorkflowState:
        """
        Plan node function that creates or updates the task plan.
        
        This function:
        1. Checks if tasks need to be created or updated
        2. Uses the plan agent to create tasks based on available tools
        3. Updates the state with the new tasks
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            WorkflowState: Updated workflow state with new tasks
        """
        if not state["tasks"] or state.get("needs_replan", False):
            available_tools = tool_registry.list_tools()
            tasks = plan_agent.plan(state, available_tools)
            state["tasks"] = tasks
            state["needs_replan"] = False
        return state
    
    def execute_node(state: WorkflowState) -> WorkflowState:
        """
        Execute node function that processes pending tasks.
        
        This function:
        1. Finds the first pending task in the task list
        2. Uses the tool agent to execute the task
        3. Updates the task status, result, and error information
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            WorkflowState: Updated workflow state with task execution results
        """
        for task in state["tasks"]:
            if task.status == "pending":
                executed_task = tool_agent.execute_task(task)
                task.status = executed_task.status
                task.result = executed_task.result
                task.error = executed_task.error
                break  # Execute one task at a time
        return state
    
    def reflect_node(state: WorkflowState) -> WorkflowState:
        """
        Reflect node function that evaluates and refines the plan.
        
        This function:
        1. Uses the reflection agent to determine if the plan needs refinement
        2. If refinement is needed, gets suggestions for modifications or additions
        3. Applies the refinements to the tasks
        4. Updates the iteration count and continuation flag
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            WorkflowState: Updated workflow state with refinements applied
        """
        needs_refinement = reflection_agent.should_refine_plan(state)
        
        if needs_refinement and state["iteration_count"] < 3:
            refinements = reflection_agent.suggest_refinements(state)
            
            for refinement in refinements:
                if refinement["action"] == "modify":
                    # Modify an existing task
                    for task in state["tasks"]:
                        if task.id == refinement["task_id"]:
                            task.description = refinement["new_description"]
                            task.status = "pending"
                            task.error = None
                            break
                elif refinement["action"] == "add":
                    # Add a new task
                    new_task = Task(
                        id=len(state["tasks"]) + 1,
                        description=refinement["description"],
                        status="pending",
                        tool_used=refinement["tool"]
                    )
                    state["tasks"].append(new_task)
            
            state["iteration_count"] += 1
            state["should_continue"] = True
        else:
            state["should_continue"] = False
        
        return state
        
    def finalize_node(state: WorkflowState) -> WorkflowState:
        """
        Finalize node function that synthesizes the final answer.
        
        This function:
        1. Collects results from all completed tasks
        2. Uses the LLM to synthesize a comprehensive answer
        3. Updates the state with the final answer
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            WorkflowState: Updated workflow state with the final answer
        """
        completed_tasks = [t for t in state["tasks"] if t.status == "completed"]
        
        if completed_tasks:
            nvidia_client = NvidiaNIMClient(NVIDIA_API_KEY)
            
            # Format completed tasks
            task_results = []
            for t in completed_tasks:
                task_results.append(f"Task: {t.description}\nResult: {t.result}\n")
            
            synthesis_prompt = f"""Based on the completed tasks below, provide a comprehensive answer to the original query.

Original Query: {state["original_query"]}

Completed Tasks and Results:
{"".join(task_results)}

Provide a clear, comprehensive answer that directly addresses the original query."""

            final_answer = nvidia_client.invoke(synthesis_prompt, temperature=0.1)
            state["final_answer"] = final_answer
        else:
            state["final_answer"] = "I apologize, but I wasn't able to complete any tasks to answer your query. Please try rephrasing your question or check if the required tools are available."
        
        return state
    
    def should_continue(state: WorkflowState) -> str:
        """
        Determine the next node in the workflow based on the current state.
        
        This function checks:
        1. If there are pending tasks -> continue execution
        2. If reflection suggested continuing -> go to reflection
        3. Otherwise -> finalize the workflow
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            str: The name of the next node to transition to
        """
        pending_tasks = [t for t in state["tasks"] if t.status == "pending"]
        
        if pending_tasks:
            return "execute"
        elif state.get("should_continue", False):
            return "reflect"
        else:
            return "finalize"
    
    # Create the workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes for each stage of the workflow
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("reflect", reflect_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set the entry point to the planning node
    workflow.set_entry_point("plan")
    
    # Configure edges between nodes
    workflow.add_edge("plan", "execute")
    workflow.add_conditional_edges(
        "execute",
        should_continue,
        {
            "execute": "execute",  # If there are pending tasks, continue execution
            "reflect": "reflect",   # If reflection is needed, go to reflect node
            "finalize": "finalize"  # Otherwise, finalize the workflow
        }
    )
    workflow.add_conditional_edges(
        "reflect",
        should_continue,
        {
            "execute": "plan",      # If new tasks were added, go back to planning
            "finalize": "finalize"  # Otherwise, finalize the workflow
        }
    )
    workflow.add_edge("finalize", END)  # End the workflow after finalization
    
    # Compile and return the workflow
    return workflow.compile()