from .base_agent import BaseAgent

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=13.08&longitude=80.27&current_weather=true"
)

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail",
}


class WeatherAgent(BaseAgent):
    def execute(self, query: str) -> dict:
        try:
            data = self.fetch_with_retry(API_URL)
            cw = data.get("current_weather", {})
            code = cw.get("weathercode", -1)
            return {
                "status": "success",
                "agent": "weather",
                "raw_data": data,
                "processed": {
                    "location": "Chennai, India (13.08°N, 80.27°E)",
                    "temperature_c": cw.get("temperature"),
                    "windspeed_kmh": cw.get("windspeed"),
                    "wind_direction_deg": cw.get("winddirection"),
                    "condition": WMO_CODES.get(code, f"Code {code}"),
                    "time": cw.get("time"),
                },
            }
        except Exception as e:
            return {"status": "error", "agent": "weather", "error": str(e)}
