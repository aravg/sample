from typing import Dict, Any, List


_PLACES_DB = {
    "goa": {
        "beaches": [
            {"name": "Baga Beach", "type": "beach", "entry_fee": 0, "best_time": "6am-10pm",
             "description": "Popular beach with water sports, nightlife, shacks"},
            {"name": "Palolem Beach", "type": "beach", "entry_fee": 0, "best_time": "sunrise-sunset",
             "description": "Serene crescent-shaped beach, perfect for couples"},
            {"name": "Anjuna Beach", "type": "beach", "entry_fee": 0, "best_time": "anytime",
             "description": "Rocky beach famous for flea market and trance parties"},
            {"name": "Agonda Beach", "type": "beach", "entry_fee": 0, "best_time": "morning",
             "description": "Pristine, quiet beach ideal for relaxation"},
        ],
        "heritage": [
            {"name": "Basilica of Bom Jesus", "type": "heritage", "entry_fee": 0,
             "best_time": "9am-6pm", "description": "UNESCO World Heritage Site, 16th century church"},
            {"name": "Fort Aguada", "type": "heritage", "entry_fee": 30,
             "best_time": "9:30am-5:30pm", "description": "17th century Portuguese fort with lighthouse"},
            {"name": "Old Goa Churches", "type": "heritage", "entry_fee": 0,
             "best_time": "morning", "description": "Collection of historic Portuguese-era churches"},
        ],
        "nightlife": [
            {"name": "Tito's Club", "type": "nightlife", "entry_fee": 500,
             "best_time": "10pm-4am", "description": "Iconic Goa nightclub at Baga"},
            {"name": "Club Cubana", "type": "nightlife", "entry_fee": 1000,
             "best_time": "9pm-3am", "description": "Hilltop open-air club, Arpora"},
        ],
        "food": [
            {"name": "Gunpowder Restaurant", "type": "food", "avg_cost_inr": 600,
             "cuisine": "South Indian/Goan", "description": "Authentic Goan seafood"},
            {"name": "Infantaria Bakery", "type": "food", "avg_cost_inr": 300,
             "cuisine": "Bakery/Cafe", "description": "Famous for breakfast and pastries"},
            {"name": "Shacks on Baga Beach", "type": "food", "avg_cost_inr": 500,
             "cuisine": "Seafood/Multi-cuisine", "description": "Fresh seafood by the beach"},
        ],
        "activities": [
            {"name": "Water Sports at Calangute", "type": "activity", "cost_inr": 1500,
             "description": "Parasailing, jet ski, banana boat rides"},
            {"name": "Dudhsagar Falls Trek", "type": "activity", "cost_inr": 800,
             "description": "Stunning 310m waterfall accessible by jeep safari"},
            {"name": "Spice Plantation Tour", "type": "activity", "cost_inr": 400,
             "description": "Guided tour of spice farms with Goan lunch"},
        ],
    },
    "delhi": {
        "monuments": [
            {"name": "Red Fort", "type": "monument", "entry_fee": 50,
             "best_time": "9am-6pm", "description": "UNESCO World Heritage Mughal fort"},
            {"name": "Qutub Minar", "type": "monument", "entry_fee": 40,
             "best_time": "7am-5pm", "description": "73m tall 12th century minaret"},
            {"name": "India Gate", "type": "monument", "entry_fee": 0,
             "best_time": "any time", "description": "War memorial and iconic landmark"},
            {"name": "Humayun's Tomb", "type": "monument", "entry_fee": 40,
             "best_time": "7am-6pm", "description": "Mughal architecture predecessor to Taj Mahal"},
        ],
        "culture": [
            {"name": "Chandni Chowk", "type": "culture", "entry_fee": 0,
             "best_time": "10am-8pm", "description": "Historic market, street food paradise"},
            {"name": "Lotus Temple", "type": "culture", "entry_fee": 0,
             "best_time": "9am-5:30pm", "description": "Iconic Bahai temple in lotus shape"},
            {"name": "Akshardham Temple", "type": "culture", "entry_fee": 0,
             "best_time": "10am-6:30pm", "description": "Modern Hindu temple complex"},
        ],
        "food": [
            {"name": "Karim's, Jama Masjid", "type": "food", "avg_cost_inr": 400,
             "cuisine": "Mughlai", "description": "Legendary Mughlai cuisine since 1913"},
            {"name": "Paranthe Wali Gali", "type": "food", "avg_cost_inr": 150,
             "cuisine": "Indian Street Food", "description": "Famous stuffed paratha street in Chandni Chowk"},
        ],
    },
    "manali": {
        "nature": [
            {"name": "Solang Valley", "type": "nature", "entry_fee": 0,
             "best_time": "9am-5pm", "description": "Snow valley with skiing and adventure sports"},
            {"name": "Rohtang Pass", "type": "nature", "entry_fee": 500,
             "best_time": "May-October", "description": "Scenic high mountain pass at 3978m"},
            {"name": "Beas River Rafting", "type": "activity", "cost_inr": 600,
             "description": "White water rafting on the Beas river"},
        ],
        "culture": [
            {"name": "Hadimba Temple", "type": "culture", "entry_fee": 0,
             "best_time": "8am-6pm", "description": "Ancient wood and stone temple in deodar forest"},
            {"name": "Old Manali", "type": "culture", "entry_fee": 0,
             "best_time": "anytime", "description": "Quaint cafes, hippie culture, riverside walks"},
        ],
    },
}


def get_tourist_attractions(city: str, interests: List[str] = None) -> Dict[str, Any]:
    city_key = city.lower().strip()
    places_data = _PLACES_DB.get(city_key, {})

    if not places_data:
        return _generic_places(city)

    all_places = []
    for category, items in places_data.items():
        for item in items:
            all_places.append({**item, "category": category})

    if interests:
        interest_lower = [i.lower() for i in interests]
        filtered = [
            p for p in all_places
            if any(i in p.get("type", "").lower() or i in p.get("category", "").lower()
                   for i in interest_lower)
        ]
        if filtered:
            all_places = filtered

    top_picks = all_places[:8]
    return {
        "city": city,
        "attractions": top_picks,
        "total_found": len(all_places),
        "categories": list(places_data.keys()),
        "recommendation": f"Must-visit: {top_picks[0]['name']}" if top_picks else "Explore the city",
    }


def get_local_experiences(city: str) -> Dict[str, Any]:
    experiences = {
        "goa": [
            "Sunset cruise on Mandovi River",
            "Village tour of Divar Island",
            "Cooking class — Goan fish curry",
            "Casino night at a floating casino",
            "Yoga retreat at Arambol beach",
        ],
        "delhi": [
            "Street food tour of Old Delhi",
            "Rickshaw ride through Chandni Chowk",
            "Sound & Light show at Red Fort",
            "Craft shopping at Dilli Haat",
        ],
        "manali": [
            "Apple orchard walk",
            "Camping under the stars at Camping Site",
            "Local Himachali food tasting",
            "Paragliding at Solang Valley",
        ],
    }
    city_exp = experiences.get(city.lower(), [
        f"City sightseeing tour of {city}",
        "Local market exploration",
        "Cultural show / folk dance",
    ])
    return {"city": city, "local_experiences": city_exp}


def _generic_places(city: str) -> Dict[str, Any]:
    return {
        "city": city,
        "attractions": [
            {"name": f"{city} City Center", "type": "sightseeing", "entry_fee": 0,
             "description": "Main city center area"},
            {"name": f"{city} Museum", "type": "culture", "entry_fee": 50,
             "description": "Local history and culture museum"},
        ],
        "categories": ["sightseeing", "culture", "food"],
        "recommendation": f"Search 'top places to visit in {city}' for detailed listings",
    }
