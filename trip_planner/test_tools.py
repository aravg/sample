import sys
sys.path.insert(0, '.')

from tools.weather_tools import get_weather_forecast
w = get_weather_forecast('Goa', 3)
print(f"Weather: {w['summary']}")

from tools.transport_tools import search_flights
f = search_flights('Bangalore', 'Goa', '2026-06-20', 2)
print(f"Flights: {f['cheapest']['airline']} - Rs.{f['cheapest']['total_price_inr']}")

from tools.hotel_tools import search_hotels
h = search_hotels('Goa', budget_per_night=3000, nights=4, travelers=2)
print(f"Hotel: {h['best_pick']['name']} - Rs.{h['best_pick']['total_cost_inr']}")

from tools.places_tools import get_tourist_attractions
p = get_tourist_attractions('Goa', ['beach', 'nightlife'])
print(f"Places: {len(p['attractions'])} attractions found")

from tools.budget_tools import calculate_budget
b = calculate_budget(9000, 11200, 600, 7500, 10, 5, 2)
print(f"Budget total: Rs.{b['total_inr']}")

from memory.vector_store import VectorMemory
vm = VectorMemory(user_id='test_user')
vm.add_memory("Visited Goa, loved the beaches", {"destination": "Goa", "budget": 30000})
results = vm.search("beach trip")
print(f"Memory: {len(results)} results found")

from memory.session_store import TripDatabase
db = TripDatabase()
print("Database: initialized OK")

print("\nAll tool tests PASSED!")
