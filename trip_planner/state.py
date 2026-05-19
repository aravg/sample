from typing import TypedDict, Optional, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class TripState(TypedDict):
    # ── User inputs ──────────────────────────────────────────────────────────
    user_profile: Dict[str, Any]          # name, email, traveler count, type
    trip_preferences: Dict[str, Any]      # source, dest, dates, budget, prefs

    # ── Agent outputs ────────────────────────────────────────────────────────
    weather_data: Dict[str, Any]
    hotel_data: Dict[str, Any]
    transport_data: Dict[str, Any]
    places_data: Dict[str, Any]
    budget_summary: Dict[str, Any]
    itinerary: Dict[str, Any]

    # ── Control flow ─────────────────────────────────────────────────────────
    review_status: Dict[str, Any]         # approved, issues, retry_agents
    pdf_status: Dict[str, Any]            # generated, path, error
    orchestrator_decision: Dict[str, Any] # next_step, reason, conflicts

    # ── Memory ───────────────────────────────────────────────────────────────
    past_trips: List[Dict[str, Any]]
    user_preferences_memory: Dict[str, Any]

    # ── Retry tracking ───────────────────────────────────────────────────────
    retry_counts: Dict[str, int]
    errors: List[str]

    # ── Conversation ─────────────────────────────────────────────────────────
    messages: Annotated[List, add_messages]

    # ── Final output ─────────────────────────────────────────────────────────
    final_plan: Optional[Dict[str, Any]]
    pdf_path: Optional[str]
    current_step: str                     # tracks workflow stage


def initial_state() -> TripState:
    return TripState(
        user_profile={},
        trip_preferences={},
        weather_data={},
        hotel_data={},
        transport_data={},
        places_data={},
        budget_summary={},
        itinerary={},
        review_status={},
        pdf_status={},
        orchestrator_decision={},
        past_trips=[],
        user_preferences_memory={},
        retry_counts={},
        errors=[],
        messages=[],
        final_plan=None,
        pdf_path=None,
        current_step="start",
    )
