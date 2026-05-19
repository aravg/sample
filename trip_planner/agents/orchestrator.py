"""
Orchestrator Agent — The brain of the multi-agent system.
Decides which agent runs next, handles conflicts, validates final output.
"""
import json
from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from state import TripState
from config import get_llm

ORCHESTRATOR_SYSTEM = """You are the Orchestrator Agent of an AI Trip Planner system.
You manage a multi-agent workflow and decide which agent should run next.

Available agents:
- user_input: Collect and validate user requirements
- memory_retrieval: Fetch past user preferences
- gather_data: Run weather, hotel, transport, places agents in parallel
- budget: Calculate and optimize budget
- itinerary: Generate day-wise itinerary
- review: Validate and check for conflicts
- memory_update: Save this trip to memory
- pdf_generator: Generate final PDF report
- end: Workflow complete

Current workflow stages (in order):
1. user_input → 2. memory_retrieval → 3. gather_data → 4. budget → 5. itinerary → 6. review → 7. (retry or approve) → 8. memory_update → 9. pdf_generator → end

Rules:
- If review has issues requiring retry, route back to the failing agent
- If gather_data is done and no budget yet, route to budget
- If budget is done and no itinerary, route to itinerary
- If itinerary is done and no review, route to review
- If review approved, route to memory_update then pdf_generator
- If review approved and memory updated, route to pdf_generator
- If pdf generated, route to end
- Never retry more than 3 times for any agent

Respond ONLY with valid JSON:
{
  "next_step": "<agent_name>",
  "reason": "<brief reason>",
  "conflicts": [],
  "retry_agent": null
}"""


def orchestrator_node(state: TripState) -> TripState:
    """Orchestrator decides the next step in the workflow."""
    llm = get_llm(temperature=0)

    _current_step = state.get("current_step", "start")
    state_summary = {
        "current_step": _current_step,
        "has_user_input": bool(state.get("trip_preferences")),
        "has_memory": bool(state.get("user_preferences_memory")),
        "has_weather": bool(state.get("weather_data")),
        "has_hotel": bool(state.get("hotel_data")),
        "has_transport": bool(state.get("transport_data")),
        "has_places": bool(state.get("places_data")),
        "has_budget": bool(state.get("budget_summary")),
        "has_itinerary": bool(state.get("itinerary")),
        "review_status": state.get("review_status", {}),
        "pdf_status": state.get("pdf_status", {}),
        "retry_counts": state.get("retry_counts", {}),
        "errors": state.get("errors", []),
        "has_memory_updated": _current_step in ("memory_updated", "pdf_generated"),
    }

    messages = [
        SystemMessage(content=ORCHESTRATOR_SYSTEM),
        HumanMessage(content=f"Current system state:\n{json.dumps(state_summary, indent=2)}\n\nWhat should be the next step?"),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        decision = json.loads(content)
    except Exception as e:
        decision = _fallback_decision(state_summary)

    decision = _validate_decision(decision, state_summary)
    return {**state, "orchestrator_decision": decision, "current_step": decision.get("next_step", "end")}


def orchestrator_router(state: TripState) -> str:
    """Route to the next node based on orchestrator decision."""
    decision = state.get("orchestrator_decision", {})
    next_step = decision.get("next_step", "end")

    valid_steps = {
        "user_input", "memory_retrieval", "gather_data",
        "budget", "itinerary", "review",
        "memory_update", "pdf_generator", "end",
    }
    return next_step if next_step in valid_steps else "end"


def _validate_decision(decision: Dict, state_summary: Dict) -> Dict:
    """Override invalid LLM routing decisions to prevent loops and skipped steps."""
    next_step = decision.get("next_step")
    review = state_summary["review_status"]

    # Never skip pdf_generator when ending
    if next_step == "end" and not state_summary["pdf_status"].get("generated"):
        return {"next_step": "pdf_generator", "reason": "Generate PDF before ending"}

    # Don't loop back to memory_update once it's done
    if next_step == "memory_update" and state_summary.get("has_memory_updated"):
        return {"next_step": "pdf_generator", "reason": "Memory updated, generate PDF"}

    if not review or review.get("approved"):
        return decision

    # Prevent re-routing to the same retry agent after the retry has already run
    retry_agent = review.get("retry_agent")
    if retry_agent and next_step == retry_agent:
        counts_at_review = review.get("retry_counts_at_review", {})
        current = state_summary["retry_counts"].get(retry_agent, 0)
        at_review = counts_at_review.get(retry_agent, 0)
        if current > at_review:
            return {"next_step": "review", "reason": f"Re-reviewing after {retry_agent} retry"}

    return decision


def _fallback_decision(state_summary: Dict) -> Dict:
    """Rule-based fallback when LLM fails."""
    if not state_summary["has_user_input"]:
        return {"next_step": "user_input", "reason": "Need user input first"}
    if not state_summary["has_memory"]:
        return {"next_step": "memory_retrieval", "reason": "Retrieve user memory"}
    if not (state_summary["has_weather"] and state_summary["has_hotel"]
            and state_summary["has_transport"]):
        return {"next_step": "gather_data", "reason": "Gather trip data"}
    if not state_summary["has_budget"]:
        return {"next_step": "budget", "reason": "Calculate budget"}
    if not state_summary["has_itinerary"]:
        return {"next_step": "itinerary", "reason": "Generate itinerary"}

    review = state_summary["review_status"]
    if not review:
        return {"next_step": "review", "reason": "Review the plan"}
    if review.get("approved"):
        if not state_summary["has_memory_updated"]:
            return {"next_step": "memory_update", "reason": "Update memory"}
        if not state_summary["pdf_status"].get("generated"):
            return {"next_step": "pdf_generator", "reason": "Generate PDF"}
        return {"next_step": "end", "reason": "Done"}

    retry_agent = review.get("retry_agent")
    retry_counts = state_summary["retry_counts"]
    if retry_agent:
        counts_at_review = review.get("retry_counts_at_review", {})
        current = retry_counts.get(retry_agent, 0)
        at_review = counts_at_review.get(retry_agent, 0)
        if current <= at_review and current < 3:
            return {"next_step": retry_agent, "reason": f"Retry {retry_agent}", "retry_agent": retry_agent}
        if current > at_review:
            return {"next_step": "review", "reason": "Re-reviewing after retry"}
    return {"next_step": "pdf_generator", "reason": "Max retries reached, proceed"}
