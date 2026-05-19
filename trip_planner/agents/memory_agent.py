"""Memory Agent — Retrieves and updates user preferences and trip history."""
import json
from state import TripState
from memory.vector_store import VectorMemory
from memory.session_store import TripDatabase


def memory_retrieval_node(state: TripState) -> TripState:
    """Retrieve past user preferences from memory stores."""
    user_profile = state.get("user_profile", {})
    user_id = user_profile.get("user_id", "default")

    vector_mem = VectorMemory(user_id=user_id)
    db = TripDatabase()

    vector_prefs = vector_mem.get_user_preferences()
    past_trips = db.get_user_trips(user_id, limit=3)
    db_profile = db.get_user_profile(user_id)

    prefs = {**vector_prefs}
    if db_profile and db_profile.get("preferences"):
        prefs.update(db_profile["preferences"])

    past_destinations = [t.get("destination", "") for t in past_trips if t.get("destination")]
    if past_destinations:
        prefs["past_destinations"] = past_destinations

    prefs["trip_count"] = len(past_trips)

    return {
        **state,
        "user_preferences_memory": prefs,
        "past_trips": past_trips,
        "current_step": "memory_retrieved",
    }


def memory_update_node(state: TripState) -> TripState:
    """Save the current trip plan to memory for future reference."""
    user_profile = state.get("user_profile", {})
    user_id = user_profile.get("user_id", "default")
    prefs = state.get("trip_preferences", {})

    vector_mem = VectorMemory(user_id=user_id)
    db = TripDatabase()

    memory_content = (
        f"Trip to {prefs.get('destination', '')} from {prefs.get('source', '')} "
        f"for {prefs.get('days', 0)} days. "
        f"Travel type: {prefs.get('travel_type', '')}. "
        f"Budget: {prefs.get('budget', 0)}. "
        f"Hotel preference: {prefs.get('hotel_preference', '')}. "
        f"Interests: {', '.join(prefs.get('interests', []))}."
    )
    vector_mem.add_memory(memory_content, metadata={
        "destination": prefs.get("destination"),
        "budget": prefs.get("budget"),
        "hotel_preference": prefs.get("hotel_preference"),
        "travel_type": prefs.get("travel_type"),
    })

    trip_record = {
        "trip_preferences": prefs,
        "final_plan": state.get("final_plan", {}),
        "pdf_path": state.get("pdf_path", ""),
    }
    try:
        db.save_trip(user_id, trip_record)
    except Exception:
        pass

    if user_profile.get("name"):
        try:
            db.save_user_profile(
                user_id,
                user_profile.get("name", ""),
                user_profile.get("email", ""),
                {
                    "preferred_hotel": prefs.get("hotel_preference"),
                    "preferred_travel_type": prefs.get("travel_type"),
                    "last_destination": prefs.get("destination"),
                },
            )
        except Exception:
            pass

    return {**state, "current_step": "memory_updated"}
