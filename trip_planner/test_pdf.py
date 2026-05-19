import sys
sys.path.insert(0, '.')

from utils.pdf_generator import TripPDFGenerator

sample_data = {
    "trip_preferences": {
        "source": "Bangalore",
        "destination": "Goa",
        "days": 5,
        "travelers": 2,
        "budget": 30000,
        "travel_type": "couple",
        "dates": {"start": "2026-06-20", "end": "2026-06-25", "display": "June 20-25, 2026"},
    },
    "user_profile": {"name": "Test Traveler"},
    "weather_data": {
        "city": "Goa",
        "summary": "Mostly partly cloudy with sea breeze, avg high 30C.",
        "forecasts": [
            {"date": "2026-06-20", "temp_min": 25, "temp_max": 30, "description": "partly cloudy", "humidity": 75, "wind_speed": 12},
            {"date": "2026-06-21", "temp_min": 26, "temp_max": 31, "description": "clear sky", "humidity": 70, "wind_speed": 10},
            {"date": "2026-06-22", "temp_min": 24, "temp_max": 29, "description": "light rain", "humidity": 80, "wind_speed": 15},
        ],
    },
    "hotel_data": {
        "recommendations": [
            {"name": "La Calypso Hotel", "area": "Calangute", "stars": 3, "price_per_night": 2800,
             "total_cost_inr": 11200, "rating": 4.2, "amenities": ["pool", "restaurant", "wifi"]},
        ],
        "best_pick": {"name": "La Calypso Hotel", "price_per_night": 2800, "total_cost_inr": 11200,
                      "rating": 4.2, "amenities": ["pool", "restaurant"]},
    },
    "transport_data": {
        "recommendation": "SpiceJet flight for Rs.7800 total",
        "estimated_cost": 9000,
        "flights": {"flights": [
            {"airline": "SpiceJet", "duration": "1h 05m", "price_inr": 3900, "total_price_inr": 7800, "date": "2026-06-20"},
            {"airline": "IndiGo", "duration": "1h 10m", "price_inr": 4500, "total_price_inr": 9000, "date": "2026-06-20"},
        ]},
        "trains": {"trains": [
            {"name": "Goa Express", "number": "10104", "duration": "12h 30m", "price_inr": 850, "total_price_inr": 1700, "date": "2026-06-20"},
        ]},
    },
    "places_data": {
        "attractions": [
            {"name": "Baga Beach", "type": "beach", "entry_fee": 0, "best_time": "6am-10pm", "description": "Popular beach with water sports"},
            {"name": "Basilica of Bom Jesus", "type": "heritage", "entry_fee": 0, "best_time": "9am-6pm", "description": "UNESCO World Heritage Church"},
            {"name": "Fort Aguada", "type": "heritage", "entry_fee": 30, "best_time": "9:30am-5:30pm", "description": "17th century fort"},
        ],
        "local_experiences": ["Sunset cruise on Mandovi River", "Cooking class - Goan fish curry"],
    },
    "budget_summary": {
        "breakdown": {"transport": 9000, "accommodation": 11200, "food": 6000, "activities": 3500, "miscellaneous": 2970},
        "total_inr": 32670,
        "per_person_inr": 16335,
        "daily_avg_inr": 6534,
        "suggestions": ["Consider train to save Rs.7000 on transport"],
        "total_budget_allocated": 30000,
    },
    "itinerary": {
        "days": [
            {"day": 1, "title": "Arrival & First Impressions",
             "activities": [
                 {"time": "Morning", "description": "Fly from Bangalore to Goa (SpiceJet, 1h 05m)", "cost": 0},
                 {"time": "Afternoon", "description": "Check in to La Calypso Hotel, Calangute", "cost": 0},
                 {"time": "Evening", "description": "Stroll on Calangute Beach, sunset views", "cost": 0},
             ],
             "food": "Welcome dinner at a Goan seafood shack", "accommodation": "La Calypso Hotel"},
            {"day": 2, "title": "Beaches & Water Sports",
             "activities": [
                 {"time": "Morning", "description": "Baga Beach - water sports (parasailing, jet ski)", "cost": 1500},
                 {"time": "Afternoon", "description": "Lunch at beachside shack, relax at Anjuna Beach", "cost": 0},
                 {"time": "Evening", "description": "Sunset at Vagator Beach", "cost": 0},
             ],
             "food": "Seafood lunch at beach shack, dinner at Gunpowder Restaurant", "accommodation": "La Calypso Hotel"},
        ],
        "tips": ["Carry sunscreen", "Try the local Feni (Goan spirit)", "Book water sports in advance"],
        "highlights": ["Baga Beach", "Fort Aguada", "Nightlife at Tito's"],
    },
    "final_plan": {
        "destination": "Goa",
        "source": "Bangalore",
        "total_cost": 32670,
        "highlights": ["Baga Beach", "Fort Aguada"],
        "status": "approved",
    },
}

gen = TripPDFGenerator()
pdf_path = gen.generate(sample_data, filename="test_goa_trip.pdf")
print(f"PDF generated: {pdf_path}")

import os
size = os.path.getsize(pdf_path)
print(f"File size: {size:,} bytes")
print("PDF test PASSED!")
