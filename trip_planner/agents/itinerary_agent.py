"""Itinerary Agent — Generates a detailed day-wise trip plan using LLM."""
import json
from langchain_core.messages import HumanMessage, SystemMessage
from state import TripState
from config import get_llm

SYSTEM_PROMPT = """You are an expert travel planner. Create a detailed, day-wise itinerary.

Return ONLY valid JSON in this exact format:
{
  "days": [
    {
      "day": 1,
      "title": "Arrival & Exploration",
      "activities": [
        {"time": "Morning", "description": "Activity description", "cost": 0},
        {"time": "Afternoon", "description": "Activity description", "cost": 500},
        {"time": "Evening", "description": "Activity description", "cost": 200}
      ],
      "food": "Breakfast at hotel, lunch at local restaurant, dinner at seafood shack",
      "accommodation": "Hotel name"
    }
  ],
  "tips": [
    "Travel tip 1",
    "Travel tip 2"
  ],
  "highlights": ["Key highlight 1", "Key highlight 2"]
}

Make it realistic, personalized, and budget-conscious. Include specific places from the provided data."""


def itinerary_node(state: TripState) -> TripState:
    prefs = state.get("trip_preferences", {})
    weather = state.get("weather_data", {})
    hotel = state.get("hotel_data", {})
    places = state.get("places_data", {})
    budget = state.get("budget_summary", {})
    transport = state.get("transport_data", {})

    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["itinerary"] = retry_counts.get("itinerary", 0) + 1

    best_hotel = hotel.get("best_pick", {}) or {}
    attractions = places.get("attractions", [])[:8]
    experiences = places.get("local_experiences", [])[:5]

    context = f"""
Trip Details:
- From: {prefs.get('source')} → To: {prefs.get('destination')}
- Duration: {prefs.get('days')} days
- Travelers: {prefs.get('travelers')} ({prefs.get('travel_type')})
- Budget: ₹{prefs.get('budget', 0):,.0f} total
- Transport: {transport.get('recommendation', 'N/A')}
- Hotel: {best_hotel.get('name', 'N/A')} at ₹{best_hotel.get('price_per_night', 0)}/night

Weather:
{weather.get('summary', 'Pleasant weather expected')}

Top Attractions:
{json.dumps([{'name': a['name'], 'type': a.get('type'), 'entry_fee': a.get('entry_fee', 0),
              'description': a.get('description', '')} for a in attractions], indent=2)}

Local Experiences: {', '.join(experiences)}

Food Preferences: {', '.join(prefs.get('food_preferences', ['local cuisine']))}
Interests: {', '.join(prefs.get('interests', []))}

Budget Breakdown:
- Transport: ₹{budget.get('breakdown', {}).get('transport', 0):,.0f}
- Hotel: ₹{budget.get('breakdown', {}).get('accommodation', 0):,.0f}
- Food: ₹{budget.get('breakdown', {}).get('food', 0):,.0f}
- Activities: ₹{budget.get('breakdown', {}).get('activities', 0):,.0f}
"""

    llm = get_llm(temperature=0.7)
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Create a {prefs.get('days')}-day itinerary:\n{context}"),
        ])
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        itinerary = json.loads(content)
        itinerary["agent_status"] = "success"
    except Exception as e:
        itinerary = _fallback_itinerary(prefs, attractions, best_hotel)
        itinerary["agent_status"] = "fallback"

    return {**state, "itinerary": itinerary, "retry_counts": retry_counts}


def _fallback_itinerary(prefs: dict, attractions: list, hotel: dict) -> dict:
    days = prefs.get("days", 5)
    dest = prefs.get("destination", "destination")
    hotel_name = hotel.get("name", f"{dest} Hotel")

    day_list = []
    titles = [
        "Arrival & First Impressions",
        "Major Attractions",
        "Hidden Gems & Local Culture",
        "Adventure & Activities",
        "Relaxation & Departure",
    ]
    for i in range(days):
        attractions_today = attractions[i*2:(i+1)*2] if attractions else []
        day = {
            "day": i + 1,
            "title": titles[i] if i < len(titles) else f"Day {i+1} Exploration",
            "activities": [],
            "food": "Breakfast at hotel, lunch at local restaurant, dinner at recommended eatery",
            "accommodation": hotel_name,
        }
        if i == 0:
            day["activities"] = [
                {"time": "Morning", "description": f"Arrive at {dest}, check in to {hotel_name}", "cost": 0},
                {"time": "Afternoon", "description": "Rest and freshen up, explore nearby area", "cost": 200},
                {"time": "Evening", "description": f"Evening walk and welcome dinner at {dest}", "cost": 500},
            ]
        elif i == days - 1:
            day["activities"] = [
                {"time": "Morning", "description": "Last-minute shopping and souvenir buying", "cost": 300},
                {"time": "Afternoon", "description": "Check out from hotel, head to transport terminal", "cost": 0},
                {"time": "Evening", "description": f"Depart from {dest}", "cost": 0},
            ]
        else:
            acts = []
            for j, a in enumerate(attractions_today):
                time = ["Morning", "Afternoon", "Evening"][j % 3]
                acts.append({
                    "time": time,
                    "description": f"Visit {a['name']} — {a.get('description', '')}",
                    "cost": a.get("entry_fee", 0),
                })
            if not acts:
                acts = [{"time": "All Day", "description": f"Explore {dest} at leisure", "cost": 0}]
            day["activities"] = acts
        day_list.append(day)

    return {
        "days": day_list,
        "tips": [
            f"Carry cash for small shops in {dest}",
            "Book attractions in advance during peak season",
            "Stay hydrated and carry sunscreen",
        ],
        "highlights": [a["name"] for a in attractions[:3]],
    }
