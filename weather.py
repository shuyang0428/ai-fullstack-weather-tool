"""A tiny Open-Meteo daily weather lookup."""

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DAY_INDEX = {"today": 0, "tomorrow": 1, "day_after_tomorrow": 2}
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "rime fog", 51: "light drizzle", 53: "moderate drizzle",
    55: "dense drizzle", 61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow", 80: "rain showers",
    81: "moderate rain showers", 82: "violent rain showers", 95: "thunderstorm",
    96: "thunderstorm with hail", 99: "severe thunderstorm with hail",
}


def get_weather(city, day="today"):
    """Return a weather dictionary for city and one supported relative day."""
    if day not in DAY_INDEX:
        return {"error": "day must be today, tomorrow, or day_after_tomorrow"}
    if not isinstance(city, str) or not city.strip():
        return {"error": "city must be a non-empty string"}

    try:
        location = requests.get(
            GEOCODING_URL, params={"name": city, "count": 1}, timeout=10
        ).json().get("results", [])
        if not location:
            return {"error": f"city not found: {city}"}
        place = location[0]
        daily = requests.get(
            FORECAST_URL,
            params={
                "latitude": place["latitude"], "longitude": place["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "timezone": "auto", "forecast_days": 3,
            },
            timeout=10,
        ).json()["daily"]
        index = DAY_INDEX[day]
        precipitation = daily["precipitation_sum"][index]
        code = daily["weather_code"][index]
        return {
            "max_temperature": daily["temperature_2m_max"][index],
            "min_temperature": daily["temperature_2m_min"][index],
            "precipitation": precipitation,
            "weather_condition": WEATHER_CODES.get(code, "unknown"),
            "need_umbrella": precipitation > 0,
        }
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        return {"error": f"weather request failed: {exc}"}
