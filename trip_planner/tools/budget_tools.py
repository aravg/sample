from typing import Dict, Any


def calculate_budget(
    transport_cost: float,
    hotel_cost: float,
    food_daily: float,
    activities_cost: float,
    misc_pct: float,
    days: int,
    travelers: int,
) -> Dict[str, Any]:
    food_total = food_daily * days * travelers
    misc = (transport_cost + hotel_cost + food_total + activities_cost) * (misc_pct / 100)
    total = transport_cost + hotel_cost + food_total + activities_cost + misc

    return {
        "breakdown": {
            "transport": round(transport_cost, 2),
            "accommodation": round(hotel_cost, 2),
            "food": round(food_total, 2),
            "activities": round(activities_cost, 2),
            "miscellaneous": round(misc, 2),
        },
        "total_inr": round(total, 2),
        "per_person_inr": round(total / max(travelers, 1), 2),
        "daily_avg_inr": round(total / max(days, 1), 2),
    }


def optimize_budget(
    total_budget: float,
    breakdown: Dict[str, float],
    current_total: float,
) -> Dict[str, Any]:
    if current_total <= total_budget:
        return {
            "status": "within_budget",
            "savings": round(total_budget - current_total, 2),
            "suggestions": ["You are within budget. Consider some premium experiences!"],
            "optimized_breakdown": breakdown,
        }

    overshoot = current_total - total_budget
    suggestions = []
    optimized = dict(breakdown)

    if breakdown.get("accommodation", 0) > total_budget * 0.4:
        reduction = min(breakdown["accommodation"] * 0.25, overshoot)
        optimized["accommodation"] -= reduction
        overshoot -= reduction
        suggestions.append(
            f"Switch to a more affordable hotel (save ₹{reduction:.0f})"
        )

    if overshoot > 0 and breakdown.get("transport", 0) > 5000:
        reduction = min(breakdown["transport"] * 0.2, overshoot)
        optimized["transport"] -= reduction
        overshoot -= reduction
        suggestions.append(
            f"Consider train instead of flight (save ₹{reduction:.0f})"
        )

    if overshoot > 0 and breakdown.get("food", 0) > 0:
        reduction = min(breakdown["food"] * 0.15, overshoot)
        optimized["food"] -= reduction
        overshoot -= reduction
        suggestions.append(
            f"Mix street food with restaurants (save ₹{reduction:.0f})"
        )

    if overshoot > 0:
        suggestions.append(
            f"Still ₹{overshoot:.0f} over budget — consider reducing trip duration by 1 day"
        )

    return {
        "status": "over_budget" if overshoot > 0 else "optimized",
        "overshoot_inr": max(0, overshoot),
        "suggestions": suggestions,
        "optimized_breakdown": {k: round(v, 2) for k, v in optimized.items()},
        "new_total": round(sum(optimized.values()), 2),
    }
