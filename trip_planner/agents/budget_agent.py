"""Budget Agent — Calculates and optimizes trip budget."""
from state import TripState
from tools.budget_tools import calculate_budget, optimize_budget


def budget_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    transport_data = state.get("transport_data", {})
    hotel_data = state.get("hotel_data", {})
    places_data = state.get("places_data", {})

    total_budget = prefs.get("budget", 30000)
    days = prefs.get("days", 5)
    travelers = prefs.get("travelers", 1)

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["budget"] = retry_counts.get("budget", 0) + 1

    transport_cost = transport_data.get("estimated_cost", 0) or 0
    best_hotel = hotel_data.get("best_pick", {}) or {}
    hotel_cost = best_hotel.get("total_cost_inr", 0) or 0

    luxury = prefs.get("luxury_level", "mid-range")
    if luxury == "luxury":
        food_daily = 1200
        activities_cost = 3000 * days
    elif luxury == "budget":
        food_daily = 300
        activities_cost = 500 * days
    else:
        food_daily = 600
        activities_cost = 1500 * days

    attractions = places_data.get("attractions", [])
    entry_fees = sum(
        a.get("entry_fee", 0) or a.get("cost_inr", 0)
        for a in attractions[:6]
    )
    activities_cost += entry_fees

    budget_calc = calculate_budget(
        transport_cost=transport_cost,
        hotel_cost=hotel_cost,
        food_daily=food_daily,
        activities_cost=activities_cost,
        misc_pct=10,
        days=days,
        travelers=travelers,
    )

    optimization = optimize_budget(
        total_budget=total_budget,
        breakdown=budget_calc["breakdown"],
        current_total=budget_calc["total_inr"],
    )

    budget_summary = {
        **budget_calc,
        **optimization,
        "total_budget_allocated": total_budget,
        "is_within_budget": budget_calc["total_inr"] <= total_budget,
        "agent_status": "success",
    }
    return {**state, "budget_summary": budget_summary, "retry_counts": retry_counts}
