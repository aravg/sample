import requests
from typing import Dict, Any
from config import OPENWEATHERMAP_API_KEY


def get_weather_forecast(city: str, days: int = 5) -> Dict[str, Any]:
    """Fetch weather forecast from OpenWeatherMap API with mock fallback."""
    if OPENWEATHERMAP_API_KEY:
        return _fetch_from_api(city, days)
    return _mock_weather(city, days)


def _fetch_from_api(city: str, days: int) -> Dict[str, Any]:
    try:
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_resp = requests.get(
            geo_url,
            params={"q": city, "limit": 1, "appid": OPENWEATHERMAP_API_KEY},
            timeout=10,
        )
        geo_data = geo_resp.json()
        if not geo_data:
            return _mock_weather(city, days)

        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_resp = requests.get(
            forecast_url,
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric",
                "cnt": days * 8,
            },
            timeout=10,
        )
        data = forecast_resp.json()
        return _parse_forecast(city, data, days)
    except Exception as e:
        return _mock_weather(city, days)


def _parse_forecast(city: str, data: dict, days: int) -> Dict[str, Any]:
    daily = {}
    for item in data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {
                "temp_min": item["main"]["temp_min"],
                "temp_max": item["main"]["temp_max"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
            }
        else:
            daily[date]["temp_min"] = min(daily[date]["temp_min"], item["main"]["temp_min"])
            daily[date]["temp_max"] = max(daily[date]["temp_max"], item["main"]["temp_max"])

    forecasts = []
    for date, info in list(daily.items())[:days]:
        forecasts.append({"date": date, **info})

    return {
        "city": city,
        "forecasts": forecasts,
        "summary": _weather_summary(forecasts),
        "source": "OpenWeatherMap API",
    }


def _weather_summary(forecasts: list) -> str:
    if not forecasts:
        return "Weather data unavailable"
    descriptions = [f["description"] for f in forecasts]
    avg_max = sum(f["temp_max"] for f in forecasts) / len(forecasts)
    predominant = max(set(descriptions), key=descriptions.count)
    return f"Mostly {predominant}, avg high {avg_max:.1f}°C over trip period"


def _mock_weather(city: str, days: int) -> Dict[str, Any]:
    city_lower = city.lower()
    if any(k in city_lower for k in ["goa", "kerala", "mumbai", "chennai"]):
        base_temp, desc = 30, "partly cloudy with sea breeze"
        humidity = 75
    elif any(k in city_lower for k in ["delhi", "jaipur", "agra"]):
        base_temp, desc = 28, "clear sky"
        humidity = 45
    elif any(k in city_lower for k in ["manali", "shimla", "leh", "darjeeling"]):
        base_temp, desc = 12, "cool and clear"
        humidity = 60
    else:
        base_temp, desc = 25, "pleasant weather"
        humidity = 60

    forecasts = []
    from datetime import date, timedelta
    for i in range(days):
        d = (date.today() + timedelta(days=i)).isoformat()
        import random
        variation = random.randint(-3, 3)
        forecasts.append({
            "date": d,
            "temp_min": base_temp - 5 + variation,
            "temp_max": base_temp + variation,
            "description": desc,
            "humidity": humidity,
            "wind_speed": round(random.uniform(5, 20), 1),
        })

    return {
        "city": city,
        "forecasts": forecasts,
        "summary": f"Mostly {desc}, avg high {base_temp}°C. {_packing_tip(desc)}",
        "source": "Estimated (add OpenWeatherMap API key for real data)",
    }


def _packing_tip(desc: str) -> str:
    if "rain" in desc or "cloud" in desc:
        return "Pack a light raincoat."
    if "cool" in desc or "cold" in desc:
        return "Carry warm layers."
    return "Light cotton clothing recommended."
