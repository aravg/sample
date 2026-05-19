"""User Input Agent — Collects and validates user requirements."""
import json
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage
from state import TripState
from config import get_llm

SYSTEM_PROMPT = """You are the User Input Agent. Extract and validate trip planning requirements.

Given user input, return a structured JSON with:
{
  "source": "city name",
  "destination": "city name",
  "days": <number>,
  "travelers": <number>,
  "budget": <total INR as number>,
  "travel_type": "solo|couple|family|business",
  "hotel_preference": "budget|mid-range|luxury",
  "food_preferences": ["preference1", "preference2"],
  "transport_preference": "flight|train|bus|car",
  "interests": ["beach", "nightlife", "heritage", "adventure", etc],
  "dates": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "display": "human readable"
  },
  "luxury_level": "budget|mid-range|luxury"
}

If specific dates are not given, use dates starting 30 days from today.
Return ONLY valid JSON."""


def user_input_node(state: TripState) -> TripState:
    """Process and structure user input."""
    messages = state.get("messages", [])
    prefs = state.get("trip_preferences", {})

    if prefs and prefs.get("destination"):
        return state

    user_text = ""
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "human":
            user_text = msg.content
        elif isinstance(msg, dict) and msg.get("role") == "human":
            user_text = msg.get("content", "")

    if not user_text:
        user_text = _extract_from_profile(state.get("user_profile", {}))

    llm = get_llm(temperature=0)
    start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Today is {datetime.now().strftime('%Y-%m-%d')}. Extract trip details from:\n{user_text}"),
        ])
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        parsed = json.loads(content)
    except Exception:
        parsed = _default_preferences(user_text)

    parsed.setdefault("dates", {
        "start": start_date,
        "end": (datetime.strptime(start_date, "%Y-%m-%d") +
                timedelta(days=parsed.get("days", 5))).strftime("%Y-%m-%d"),
        "display": f"{parsed.get('days', 5)} days from {start_date}",
    })

    return {**state, "trip_preferences": parsed, "current_step": "user_input_done"}


def _extract_from_profile(profile: dict) -> str:
    parts = []
    if profile.get("destination"):
        parts.append(f"Trip to {profile['destination']}")
    if profile.get("source"):
        parts.append(f"from {profile['source']}")
    if profile.get("days"):
        parts.append(f"for {profile['days']} days")
    if profile.get("budget"):
        parts.append(f"budget {profile['budget']}")
    return " ".join(parts) or "Plan a 5-day trip to Goa from Bangalore for a couple with budget 30000"


def _default_preferences(text: str) -> dict:
    text_lower = text.lower()
    destinations = ["goa", "delhi", "manali", "jaipur", "kerala", "mumbai", "agra", "shimla"]
    destination = next((d.capitalize() for d in destinations if d in text_lower), "Goa")

    import re
    days_match = re.search(r"(\d+)\s*(?:-?\s*day|days)", text_lower)
    days = int(days_match.group(1)) if days_match else 5

    budget_match = re.search(r"(?:₹|rs\.?|inr)?\s*(\d[\d,]*)", text_lower)
    budget = float(budget_match.group(1).replace(",", "")) if budget_match else 30000

    travel_type = "couple"
    for t in ["solo", "family", "couple", "business"]:
        if t in text_lower:
            travel_type = t
            break

    return {
        "source": "Bangalore",
        "destination": destination,
        "days": days,
        "travelers": 2 if travel_type == "couple" else 1,
        "budget": budget,
        "travel_type": travel_type,
        "hotel_preference": "mid-range",
        "food_preferences": ["local cuisine", "seafood"] if "goa" in text_lower else ["local cuisine"],
        "transport_preference": "flight" if "flight" in text_lower else "train",
        "interests": [],
        "luxury_level": "mid-range",
    }
