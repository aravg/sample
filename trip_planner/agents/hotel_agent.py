"""Hotel Agent — Finds hotels within budget."""
from state import TripState
from tools.hotel_tools import search_hotels


def hotel_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    destination = prefs.get("destination", "")
    days = prefs.get("days", 5)
    total_budget = prefs.get("budget", 30000)
    travelers = prefs.get("travelers", 1)
    hotel_pref = prefs.get("hotel_preference", "mid-range")
    transport_cost = state.get("transport_data", {}).get("estimated_cost", 0) or 0

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["hotel"] = retry_counts.get("hotel", 0) + 1

    available_for_hotel = total_budget - transport_cost
    nights = max(days - 1, 1)
    budget_per_night = available_for_hotel * 0.35 / max(nights, 1)
    budget_per_night = max(budget_per_night, 500)

    try:
        hotel_data = search_hotels(
            city=destination,
            budget_per_night=budget_per_night,
            nights=nights,
            travelers=travelers,
            preference=hotel_pref,
        )
        hotel_data["agent_status"] = "success"
        hotel_data["budget_per_night_allowed"] = budget_per_night
        return {**state, "hotel_data": hotel_data, "retry_counts": retry_counts}
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"Hotel Agent error: {str(e)}")
        return {**state,
                "hotel_data": {"error": str(e), "agent_status": "failed"},
                "errors": errors,
                "retry_counts": retry_counts}
