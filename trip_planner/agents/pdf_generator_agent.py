"""PDF Generator Agent — Generates the final downloadable travel report."""
from state import TripState
from utils.pdf_generator import TripPDFGenerator


def pdf_generator_node(state: TripState) -> TripState:
    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts["pdf"] = retry_counts.get("pdf", 0) + 1

    try:
        generator = TripPDFGenerator()
        prefs = state.get("trip_preferences", {})
        dest = prefs.get("destination", "Trip")
        source = prefs.get("source", "")

        trip_data = {
            "trip_preferences": prefs,
            "user_profile": state.get("user_profile", {}),
            "weather_data": state.get("weather_data", {}),
            "hotel_data": state.get("hotel_data", {}),
            "transport_data": state.get("transport_data", {}),
            "places_data": state.get("places_data", {}),
            "budget_summary": state.get("budget_summary", {}),
            "itinerary": state.get("itinerary", {}),
            "final_plan": state.get("final_plan", {}),
        }

        pdf_path = generator.generate(trip_data)
        pdf_status = {
            "generated": True,
            "path": pdf_path,
            "agent_status": "success",
        }
        return {
            **state,
            "pdf_path": pdf_path,
            "pdf_status": pdf_status,
            "retry_counts": retry_counts,
            "current_step": "pdf_generated",
        }
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"PDF Generator error: {str(e)}")
        return {
            **state,
            "pdf_status": {"generated": False, "error": str(e), "agent_status": "failed"},
            "errors": errors,
            "retry_counts": retry_counts,
        }
