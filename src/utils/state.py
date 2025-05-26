from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a single task in the workflow."""
    id: int
    description: str
    status: str = "pending"  # pending, completed, failed
    tool_used: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None

class WorkflowState(TypedDict):
    """Represents the state of the entire workflow."""
    original_query: str
    tasks: List[Task]
    current_task_id: Optional[int]
    iteration_count: int
    final_answer: Optional[str]
    should_continue: bool
    feedback: List[str]
    needs_replan: Optional[bool]
