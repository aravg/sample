"""Transport Agent — Finds flights, trains, and routes."""
from state import TripState
from tools.transport_tools import search_flights, search_trains, get_route_info


def transport_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    source = prefs.get("source", "")
    destination = prefs.get("destination", "")
    dates = prefs.get("dates", {})
    start_date = dates.get("start", "")
    end_date = dates.get("end", "")
    travelers = prefs.get("travelers", 1)
    transport_pref = prefs.get("transport_preference", "flight")

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["transport"] = retry_counts.get("transport", 0) + 1

    try:
        transport_data = {
            "source": source,
            "destination": destination,
            "outbound_date": start_date,
            "return_date": end_date,
            "travelers": travelers,
            "preferred_mode": transport_pref,
        }

        transport_data["flights"] = search_flights(source, destination, start_date, travelers)
        transport_data["return_flights"] = search_flights(destination, source, end_date, travelers)
        transport_data["trains"] = search_trains(source, destination, start_date, travelers)
        transport_data["route_info"] = get_route_info(source, destination)

        if transport_pref == "flight":
            transport_data["recommendation"] = (
                f"Recommended: {transport_data['flights'].get('cheapest', {}).get('airline', 'Flight')} "
                f"for ₹{transport_data['flights'].get('cheapest', {}).get('total_price_inr', 0):,.0f}"
            )
            transport_data["estimated_cost"] = (
                (transport_data["flights"].get("cheapest", {}).get("total_price_inr", 0) or 0) +
                (transport_data["return_flights"].get("cheapest", {}).get("total_price_inr", 0) or 0)
            )
        else:
            cheapest_train = transport_data["trains"].get("cheapest", {})
            train_cost = cheapest_train.get("total_price_inr", 0) or 0
            transport_data["recommendation"] = (
                f"Recommended: {cheapest_train.get('name', 'Train')} "
                f"for ₹{train_cost:,.0f}"
            )
            transport_data["estimated_cost"] = train_cost * 2

        transport_data["agent_status"] = "success"
        return {**state, "transport_data": transport_data, "retry_counts": retry_counts}

    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"Transport Agent error: {str(e)}")
        return {**state,
                "transport_data": {"error": str(e), "agent_status": "failed"},
                "errors": errors,
                "retry_counts": retry_counts}
