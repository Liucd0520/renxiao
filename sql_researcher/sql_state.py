"""State definitions for SQL Research workflow."""

import operator
from typing import Annotated, Optional, List, Dict, Any

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# Structured Outputs for LLM calls

class ClarifyWithUser(BaseModel):
    """Result of clarification check."""
    need_clarification: bool = Field(
        description="Whether clarification is needed"
    )
    question: str = Field(
        default="",
        description="Clarifying question if needed"
    )
    verification: str = Field(
        default="",
        description="Verification message if no clarification needed"
    )


class SQLSubQuestion(BaseModel):
    """A decomposed sub-question for SQL research."""
    id: int = Field(description="Sub-question ID")
    question: str = Field(description="The sub-question text")
    rationale: str = Field(description="Why this sub-question is needed")
    depends_on: List[int] = Field(
        default=[],
        description="IDs of sub-questions this depends on"
    )


class DecomposeResult(BaseModel):
    """Result of question decomposition."""
    original_question: str = Field(description="The original user question")
    research_strategy: str = Field(
        description="Overall strategy for answering the question"
    )
    sub_questions: List[SQLSubQuestion] = Field(
        description="List of decomposed sub-questions"
    )
    is_simple: bool = Field(
        default=False,
        description="Whether this is a simple question (no decomposition needed)"
    )


class ConductSQLResearch(BaseModel):
    """Tool call to conduct SQL research on a sub-question."""
    research_topic: str = Field(
        description="The sub-question to research via SQL"
    )
    context: Optional[str] = Field(
        default=None,
        description="Context from previous sub-questions"
    )


class SQLResearchComplete(BaseModel):
    """Tool call to indicate SQL research is complete."""
    summary: str = Field(
        description="Summary of research findings"
    )


# State Definitions

def override_reducer(current_value, new_value):
    """Reducer that allows overriding values."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    if isinstance(current_value, list) and isinstance(new_value, list):
        return current_value + new_value
    return new_value


class SQLAgentInputState(MessagesState):
    """Input state for SQL research agent."""
    pass


class SQLAgentState(MessagesState):
    """Main state for SQL research agent."""

    supervisor_messages: Annotated[
        list[MessageLikeRepresentation], override_reducer
    ] = []
    research_brief: Optional[str] = None
    sub_questions: Optional[List[SQLSubQuestion]] = None
    sql_results: Annotated[List[Dict[str, Any]], override_reducer] = []
    notes: Annotated[list[str], override_reducer] = []
    final_report: Optional[str] = None
    decomposition_feedback: Annotated[List[str], override_reducer] = []  # User feedback for re-decomposition


class SQLSupervisorState(TypedDict):
    """State for SQL research supervisor."""

    supervisor_messages: Annotated[
        list[MessageLikeRepresentation], override_reducer
    ]
    research_brief: str
    sub_questions: List[SQLSubQuestion]
    completed_questions: List[int]
    sql_results: Annotated[List[Dict[str, Any]], override_reducer]
    notes: Annotated[list[str], override_reducer]
    research_iterations: int


class SQLResearcherState(TypedDict):
    """State for individual SQL researchers."""

    researcher_messages: Annotated[
        list[MessageLikeRepresentation], operator.add
    ]
    tool_call_iterations: int
    research_topic: str
    context: Optional[str]
    sql_query: Optional[str]
    sql_result: Optional[str]


class SQLResearcherOutputState(BaseModel):
    """Output from SQL researcher."""

    compressed_research: str = Field(description="Compressed research findings")
    sql_query: Optional[str] = Field(default=None, description="SQL query used")
    sql_result: Optional[str] = Field(default=None, description="SQL execution result")
