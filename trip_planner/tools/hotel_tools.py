from typing import Dict, Any, List


_HOTEL_DB = {
    "goa": [
        {"name": "Taj Fort Aguada Resort", "area": "North Goa", "stars": 5,
         "price_per_night": 8500, "amenities": ["pool", "spa", "beach access", "restaurant"],
         "rating": 4.7, "type": "luxury"},
        {"name": "La Calypso Hotel", "area": "Calangute", "stars": 3,
         "price_per_night": 2800, "amenities": ["pool", "restaurant", "wifi"],
         "rating": 4.2, "type": "mid-range"},
        {"name": "Zostel Goa", "area": "Anjuna", "stars": 2,
         "price_per_night": 800, "amenities": ["common area", "wifi", "cafe"],
         "rating": 4.5, "type": "budget/hostel"},
        {"name": "Alila Diwa Goa", "area": "South Goa", "stars": 5,
         "price_per_night": 12000, "amenities": ["infinity pool", "spa", "beach", "dining"],
         "rating": 4.8, "type": "luxury"},
        {"name": "Hotel Golden Palms", "area": "Panaji", "stars": 3,
         "price_per_night": 2200, "amenities": ["restaurant", "wifi", "AC"],
         "rating": 4.0, "type": "mid-range"},
    ],
    "delhi": [
        {"name": "The Leela Palace", "area": "Chanakyapuri", "stars": 5,
         "price_per_night": 18000, "amenities": ["pool", "spa", "multiple restaurants"],
         "rating": 4.9, "type": "luxury"},
        {"name": "Bloom Hotel", "area": "Vasant Kunj", "stars": 3,
         "price_per_night": 2500, "amenities": ["restaurant", "wifi", "gym"],
         "rating": 4.3, "type": "mid-range"},
        {"name": "Zostel Delhi", "area": "Paharganj", "stars": 1,
         "price_per_night": 600, "amenities": ["common room", "wifi"],
         "rating": 4.1, "type": "budget"},
    ],
    "manali": [
        {"name": "Solang Valley Resort", "area": "Solang", "stars": 4,
         "price_per_night": 5500, "amenities": ["mountain view", "spa", "bonfire"],
         "rating": 4.5, "type": "premium"},
        {"name": "Snow Valley Resorts", "area": "Mall Road", "stars": 3,
         "price_per_night": 2800, "amenities": ["restaurant", "wifi", "heater"],
         "rating": 4.2, "type": "mid-range"},
        {"name": "Zostel Manali", "area": "Old Manali", "stars": 2,
         "price_per_night": 700, "amenities": ["common area", "wifi"],
         "rating": 4.6, "type": "budget"},
    ],
    "jaipur": [
        {"name": "Rambagh Palace", "area": "Central Jaipur", "stars": 5,
         "price_per_night": 25000, "amenities": ["palace", "spa", "pool", "dining"],
         "rating": 4.9, "type": "luxury"},
        {"name": "Hotel Pearl Palace", "area": "Hathroi Fort", "stars": 2,
         "price_per_night": 1500, "amenities": ["rooftop restaurant", "wifi"],
         "rating": 4.4, "type": "budget-premium"},
    ],
}


def search_hotels(
    city: str,
    budget_per_night: float,
    nights: int,
    travelers: int = 1,
    preference: str = "mid-range",
) -> Dict[str, Any]:
    city_key = city.lower().strip()
    hotels = _HOTEL_DB.get(city_key, _generic_hotels(city, budget_per_night))

    filtered = [h for h in hotels if h["price_per_night"] <= budget_per_night]
    if not filtered:
        filtered = sorted(hotels, key=lambda x: x["price_per_night"])[:3]

    if preference in ("luxury", "premium"):
        filtered = sorted(filtered, key=lambda x: -x["stars"])
    elif preference == "budget":
        filtered = sorted(filtered, key=lambda x: x["price_per_night"])
    else:
        filtered = sorted(filtered, key=lambda x: -x["rating"])

    recommendations = []
    for h in filtered[:3]:
        total = h["price_per_night"] * nights
        recommendations.append({
            **h,
            "total_cost_inr": total,
            "nights": nights,
            "cost_per_person": total // max(travelers, 1),
        })

    best = recommendations[0] if recommendations else None
    return {
        "city": city,
        "recommendations": recommendations,
        "best_pick": best,
        "budget_per_night": budget_per_night,
        "nights": nights,
    }


def _generic_hotels(city: str, budget: float) -> List[Dict]:
    return [
        {"name": f"Grand {city} Hotel", "area": "City Center", "stars": 4,
         "price_per_night": min(budget, 5000), "amenities": ["restaurant", "wifi", "pool"],
         "rating": 4.2, "type": "mid-range"},
        {"name": f"{city} Budget Inn", "area": "Market Area", "stars": 2,
         "price_per_night": min(budget * 0.4, 1500), "amenities": ["wifi", "AC"],
         "rating": 3.8, "type": "budget"},
        {"name": f"The {city} Luxury", "area": "Premium Zone", "stars": 5,
         "price_per_night": budget * 1.5, "amenities": ["pool", "spa", "fine dining"],
         "rating": 4.7, "type": "luxury"},
    ]
