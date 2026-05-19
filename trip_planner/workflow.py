"""
LangGraph Multi-Agent Trip Planner Workflow
Orchestrator → Specialized Agents → PDF Report
"""
from langgraph.graph import StateGraph, END
from state import TripState
from agents import (
    orchestrator_node, orchestrator_router,
    user_input_node,
    memory_retrieval_node, memory_update_node,
    weather_node, transport_node, hotel_node, places_node,
    budget_node, itinerary_node, review_node,
    pdf_generator_node,
)


def gather_data_node(state: TripState) -> TripState:
    """Run all data-gathering agents (weather, hotel, transport, places) in sequence."""
    state = weather_node(state)
    state = transport_node(state)
    state = hotel_node(state)
    state = places_node(state)
    return {**state, "current_step": "data_gathered"}


def build_workflow() -> StateGraph:
    graph = StateGraph(TripState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("user_input", user_input_node)
    graph.add_node("memory_retrieval", memory_retrieval_node)
    graph.add_node("gather_data", gather_data_node)
    graph.add_node("budget", budget_node)
    graph.add_node("itinerary", itinerary_node)
    graph.add_node("review", review_node)
    graph.add_node("memory_update", memory_update_node)
    graph.add_node("pdf_generator", pdf_generator_node)

    graph.set_entry_point("orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        orchestrator_router,
        {
            "user_input": "user_input",
            "memory_retrieval": "memory_retrieval",
            "gather_data": "gather_data",
            "budget": "budget",
            "itinerary": "itinerary",
            "review": "review",
            "memory_update": "memory_update",
            "pdf_generator": "pdf_generator",
            "end": END,
        },
    )

    graph.add_edge("user_input", "orchestrator")
    graph.add_edge("memory_retrieval", "orchestrator")
    graph.add_edge("gather_data", "orchestrator")
    graph.add_edge("budget", "orchestrator")
    graph.add_edge("itinerary", "orchestrator")
    graph.add_edge("review", "orchestrator")
    graph.add_edge("memory_update", "orchestrator")
    graph.add_edge("pdf_generator", "orchestrator")

    return graph.compile()


_compiled_workflow = None


def get_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_workflow()
    return _compiled_workflow
