"""Places Explorer Agent — Finds tourist attractions and local experiences."""
from state import TripState
from tools.places_tools import get_tourist_attractions, get_local_experiences


def places_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    destination = prefs.get("destination", "")
    interests = prefs.get("interests", [])
    weather = state.get("weather_data", {})

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["places"] = retry_counts.get("places", 0) + 1

    if not destination:
        return {**state, "places_data": {"error": "No destination", "agent_status": "failed"}}

    weather_summary = weather.get("summary", "").lower()
    adjusted_interests = list(interests)
    if "rain" in weather_summary and "indoor" not in adjusted_interests:
        adjusted_interests.append("indoor")
        adjusted_interests.append("culture")
    elif "clear" in weather_summary and "beach" not in adjusted_interests:
        if "goa" in destination.lower() or "kerala" in destination.lower():
            adjusted_interests.append("beach")

    try:
        attractions = get_tourist_attractions(destination, adjusted_interests)
        experiences = get_local_experiences(destination)

        places_data = {
            **attractions,
            "local_experiences": experiences.get("local_experiences", []),
            "weather_adjusted": bool(adjusted_interests != interests),
            "agent_status": "success",
        }
        return {**state, "places_data": places_data, "retry_counts": retry_counts}
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"Places Agent error: {str(e)}")
        return {**state,
                "places_data": {"error": str(e), "agent_status": "failed"},
                "errors": errors,
                "retry_counts": retry_counts}
