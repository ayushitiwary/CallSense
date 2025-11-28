"""
LangGraph workflow for CallSense multi-agent system.
"""
from langgraph.graph import StateGraph, END
from agents import (
    CallIntakeAgent,
    TranscriptionAgent,
    SummarizationAgent,
    QualityScoringAgent,
    RoutingAgent
)
from models import CallAnalysis
from typing import TypedDict, Any, Optional, Union


class CallState(TypedDict):
    """State object passed between agents."""
    raw_input: str
    intake_data: dict
    transcript: Any
    summary: Any
    qa_scores: Any
    recommendations: list
    tags: list
    error: Optional[str]


def create_callsense_graph():
    """Create the CallSense workflow graph."""

    # Initialize agents
    intake_agent = CallIntakeAgent()
    transcription_agent = TranscriptionAgent()
    summarization_agent = SummarizationAgent()
    quality_agent = QualityScoringAgent()
    routing_agent = RoutingAgent()

    # Define node functions
    def intake_node(state: CallState) -> CallState:
        """Process call intake."""
        try:
            intake_data = intake_agent.process(state["raw_input"])
            state["intake_data"] = intake_data
            if not intake_data["is_valid"]:
                state["error"] = intake_data["reason"]
        except Exception as e:
            state["error"] = f"Intake error: {str(e)}"
        return state

    def transcription_node(state: CallState) -> CallState:
        """Process transcription."""
        try:
            transcript = transcription_agent.process(state["intake_data"])
            state["transcript"] = transcript
        except Exception as e:
            state["error"] = f"Transcription error: {str(e)}"
        return state

    def summarization_node(state: CallState) -> CallState:
        """Generate summary."""
        try:
            summary = summarization_agent.process(state["transcript"])
            state["summary"] = summary
        except Exception as e:
            state["error"] = f"Summarization error: {str(e)}"
        return state

    def quality_scoring_node(state: CallState) -> CallState:
        """Score call quality."""
        try:
            qa_scores = quality_agent.process(state["transcript"], state["summary"])
            state["qa_scores"] = qa_scores
        except Exception as e:
            state["error"] = f"Quality scoring error: {str(e)}"
        return state

    def routing_node(state: CallState) -> CallState:
        """Generate recommendations and tags."""
        try:
            routing_data = routing_agent.process(state["summary"], state["qa_scores"])
            state["recommendations"] = routing_data["recommendations"]
            state["tags"] = routing_data["tags"]
        except Exception as e:
            state["error"] = f"Routing error: {str(e)}"
        return state

    # Build the graph using StateGraph
    workflow = StateGraph(CallState)

    # Add nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("transcription", transcription_node)
    workflow.add_node("summarization", summarization_node)
    workflow.add_node("quality_scoring", quality_scoring_node)
    workflow.add_node("routing", routing_node)

    # Set entry point
    workflow.set_entry_point("intake")

    # Add edges with conditional routing
    workflow.add_conditional_edges(
        "intake",
        lambda state: "continue" if state.get("intake_data", {}).get("is_valid", False) else "end",
        {
            "continue": "transcription",
            "end": END
        }
    )

    workflow.add_edge("transcription", "summarization")
    workflow.add_edge("summarization", "quality_scoring")
    workflow.add_edge("quality_scoring", "routing")
    workflow.add_edge("routing", END)

    return workflow.compile()


def process_call(raw_input: str) -> Union[CallAnalysis, dict]:
    """
    Process a call through the complete workflow.

    Args:
        raw_input: Raw transcript text

    Returns:
        CallAnalysis object or error dict
    """
    graph = create_callsense_graph()

    # Initialize state
    initial_state = CallState(
        raw_input=raw_input,
        intake_data={},
        transcript=None,
        summary=None,
        qa_scores=None,
        recommendations=[],
        tags=[],
        error=None
    )

    # Run the workflow
    result = graph.invoke(initial_state)

    # Check for errors
    if result.get("error"):
        return {"error": result["error"]}

    # Build final analysis
    try:
        analysis = CallAnalysis(
            transcript=result["transcript"],
            summary=result["summary"],
            qa_scores=result["qa_scores"],
            recommendations=result["recommendations"],
            tags=result["tags"]
        )
        return analysis
    except Exception as e:
        return {"error": f"Failed to build analysis: {str(e)}"}
