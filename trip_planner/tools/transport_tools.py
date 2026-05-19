from typing import Dict, Any, List
import random


_ROUTE_DB = {
    ("bangalore", "goa"): {
        "distance_km": 560,
        "flights": [
            {"airline": "IndiGo", "duration": "1h 10m", "price_inr": 4500, "class": "Economy"},
            {"airline": "Air India", "duration": "1h 15m", "price_inr": 5800, "class": "Economy"},
            {"airline": "SpiceJet", "duration": "1h 05m", "price_inr": 3900, "class": "Economy"},
        ],
        "trains": [
            {"name": "Goa Express", "number": "10104", "duration": "12h 30m", "price_inr": 850, "class": "Sleeper"},
            {"name": "Mandovi Express", "number": "10112", "duration": "14h", "price_inr": 1200, "class": "3AC"},
        ],
        "road": {"duration": "9-10 hours", "distance": "560 km", "bus_price_inr": 700},
    },
    ("delhi", "agra"): {
        "distance_km": 206,
        "flights": [],
        "trains": [
            {"name": "Gatimaan Express", "number": "12050", "duration": "1h 40m", "price_inr": 1500, "class": "EC"},
            {"name": "Taj Express", "number": "12280", "duration": "2h 15m", "price_inr": 700, "class": "CC"},
        ],
        "road": {"duration": "3-4 hours", "distance": "206 km", "bus_price_inr": 200},
    },
    ("mumbai", "goa"): {
        "distance_km": 590,
        "flights": [
            {"airline": "IndiGo", "duration": "1h 05m", "price_inr": 4200, "class": "Economy"},
            {"airline": "GoAir", "duration": "1h 10m", "price_inr": 3800, "class": "Economy"},
        ],
        "trains": [
            {"name": "Konkan Kanya Express", "number": "10112", "duration": "8h", "price_inr": 950, "class": "Sleeper"},
            {"name": "Mandovi Express", "number": "10104", "duration": "9h", "price_inr": 1400, "class": "3AC"},
        ],
        "road": {"duration": "10-11 hours", "distance": "590 km", "bus_price_inr": 800},
    },
}


def search_flights(
    source: str, destination: str, date: str, travelers: int = 1
) -> Dict[str, Any]:
    key = (_normalize(source), _normalize(destination))
    rev_key = (_normalize(destination), _normalize(source))
    route = _ROUTE_DB.get(key) or _ROUTE_DB.get(rev_key)

    if route and route["flights"]:
        flights = []
        for f in route["flights"]:
            price = f["price_inr"] * travelers
            flights.append({**f, "total_price_inr": price, "date": date})
        return {
            "source": source,
            "destination": destination,
            "date": date,
            "travelers": travelers,
            "flights": flights,
            "cheapest": min(flights, key=lambda x: x["total_price_inr"]),
            "recommendation": f"Book {flights[0]['airline']} for fastest option",
        }

    price = random.randint(3500, 8000) * travelers
    return {
        "source": source,
        "destination": destination,
        "date": date,
        "travelers": travelers,
        "flights": [
            {
                "airline": "IndiGo",
                "duration": "1h 30m",
                "price_inr": price // travelers,
                "total_price_inr": price,
                "class": "Economy",
                "date": date,
            }
        ],
        "cheapest": {"airline": "IndiGo", "total_price_inr": price},
        "recommendation": "Check official airline websites for current prices",
    }


def search_trains(
    source: str, destination: str, date: str, travelers: int = 1
) -> Dict[str, Any]:
    key = (_normalize(source), _normalize(destination))
    rev_key = (_normalize(destination), _normalize(source))
    route = _ROUTE_DB.get(key) or _ROUTE_DB.get(rev_key)

    if route and route["trains"]:
        trains = []
        for t in route["trains"]:
            price = t["price_inr"] * travelers
            trains.append({**t, "total_price_inr": price, "date": date})
        return {
            "source": source,
            "destination": destination,
            "date": date,
            "travelers": travelers,
            "trains": trains,
            "cheapest": min(trains, key=lambda x: x["total_price_inr"]),
        }

    return {
        "source": source,
        "destination": destination,
        "date": date,
        "travelers": travelers,
        "trains": [],
        "note": "Check IRCTC for train availability",
    }


def get_route_info(source: str, destination: str) -> Dict[str, Any]:
    key = (_normalize(source), _normalize(destination))
    rev_key = (_normalize(destination), _normalize(source))
    route = _ROUTE_DB.get(key) or _ROUTE_DB.get(rev_key)
    if route:
        return {
            "source": source,
            "destination": destination,
            "distance_km": route["distance_km"],
            "road_info": route.get("road", {}),
        }
    return {
        "source": source,
        "destination": destination,
        "note": "Use Google Maps for accurate route details",
    }


def _normalize(name: str) -> str:
    return name.lower().strip()
