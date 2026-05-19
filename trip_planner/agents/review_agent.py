"""Final Review Agent — Validates the plan, detects conflicts, approves or flags issues."""
import json
from langchain_core.messages import HumanMessage, SystemMessage
from state import TripState
from config import get_llm

SYSTEM_PROMPT = """You are the Final Review Agent for a trip planning system.
Review the complete trip plan and check for:
1. Budget conflicts (total cost vs allocated budget)
2. Itinerary completeness (all days covered)
3. Hotel fit (price within budget per night)
4. Weather suitability (outdoor activities on rainy days)
5. Transport feasibility

Return ONLY valid JSON:
{
  "approved": true/false,
  "issues": [],
  "conflicts": [],
  "retry_agent": null,
  "review_notes": "Overall assessment",
  "confidence_score": 0-100
}

If approved=false, set retry_agent to one of: "hotel", "budget", "itinerary", "transport"
Only flag real issues, not minor ones. Approve if plan is reasonably complete."""


def review_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    budget_summary = state.get("budget_summary", {})
    itinerary = state.get("itinerary", {})
    weather = state.get("weather_data", {})
    hotel = state.get("hotel_data", {})
    transport = state.get("transport_data", {})

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["review"] = retry_counts.get("review", 0) + 1

    total_budget = prefs.get("budget", 0)
    total_cost = budget_summary.get("total_inr", 0)
    overshoot_pct = ((total_cost - total_budget) / total_budget * 100) if total_budget else 0
    days_planned = len(itinerary.get("days", []))
    days_required = prefs.get("days", 0)

    context = {
        "budget_allocated": total_budget,
        "budget_estimated": total_cost,
        "overshoot_percent": round(overshoot_pct, 1),
        "days_planned": days_planned,
        "days_required": days_required,
        "itinerary_complete": days_planned >= days_required,
        "hotel_found": bool(hotel.get("best_pick")),
        "transport_found": bool(transport.get("estimated_cost")),
        "weather_summary": weather.get("summary", ""),
        "itinerary_status": itinerary.get("agent_status", ""),
        "retry_counts": retry_counts,
    }

    llm = get_llm(temperature=0)
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Review this trip plan:\n{json.dumps(context, indent=2)}"),
        ])
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        review = json.loads(content)
    except Exception:
        review = _rule_based_review(context)

    review["agent_status"] = "success"
    review["retry_counts_at_review"] = dict(retry_counts)

    if not review.get("approved") and retry_counts.get("review", 0) >= 3:
        review["approved"] = True
        review["review_notes"] += " (Auto-approved after max retries)"

    final_plan = None
    if review.get("approved"):
        final_plan = _compile_final_plan(state)

    return {
        **state,
        "review_status": review,
        "final_plan": final_plan,
        "retry_counts": retry_counts,
        "current_step": "reviewed",
    }


def _rule_based_review(context: dict) -> dict:
    issues = []
    conflicts = []
    retry_agent = None

    overshoot = context.get("overshoot_percent", 0)
    if overshoot > 30:
        conflicts.append(f"Budget exceeds limit by {overshoot:.1f}%")
        retry_agent = "budget"
    elif overshoot > 0:
        issues.append(f"Slightly over budget by {overshoot:.1f}%")

    if not context.get("itinerary_complete"):
        issues.append(f"Itinerary has {context['days_planned']}/{context['days_required']} days")
        if not retry_agent:
            retry_agent = "itinerary"

    if not context.get("hotel_found"):
        issues.append("No hotel found within budget")
        if not retry_agent:
            retry_agent = "hotel"

    approved = len(conflicts) == 0
    return {
        "approved": approved,
        "issues": issues,
        "conflicts": conflicts,
        "retry_agent": retry_agent if not approved else None,
        "review_notes": "Plan looks good" if approved else f"Issues found: {'; '.join(conflicts)}",
        "confidence_score": 90 if approved else 60,
    }


def _compile_final_plan(state: TripState) -> dict:
    prefs = state.get("trip_preferences", {})
    return {
        "destination": prefs.get("destination"),
        "source": prefs.get("source"),
        "days": prefs.get("days"),
        "travelers": prefs.get("travelers"),
        "total_cost": state.get("budget_summary", {}).get("total_inr", 0),
        "highlights": state.get("itinerary", {}).get("highlights", []),
        "hotel": state.get("hotel_data", {}).get("best_pick", {}).get("name", "N/A"),
        "transport": state.get("transport_data", {}).get("recommendation", "N/A"),
        "status": "approved",
    }
