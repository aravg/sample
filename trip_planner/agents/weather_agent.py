"""Weather Agent — Fetches weather forecast for the destination."""
from state import TripState
from tools.weather_tools import get_weather_forecast


def weather_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    destination = prefs.get("destination", "")
    days = prefs.get("days", 5)

    if not destination:
        errors = list(state.get("errors", []))
        errors.append("Weather Agent: No destination specified")
        return {**state, "errors": errors}

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["weather"] = retry_counts.get("weather", 0) + 1

    try:
        weather_data = get_weather_forecast(destination, days)
        weather_data["agent_status"] = "success"
        return {**state, "weather_data": weather_data, "retry_counts": retry_counts}
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"Weather Agent error: {str(e)}")
        return {**state,
                "weather_data": {"error": str(e), "agent_status": "failed", "city": destination},
                "errors": errors,
                "retry_counts": retry_counts}
