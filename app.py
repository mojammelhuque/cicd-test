import os
from datetime import datetime, timezone

import requests
import streamlit as st

API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def build_location_query(country: str, city: str, postcode: str) -> str:
    if city:
        return f"{city},{country}" if country else city
    if postcode:
        return f"{postcode},{country}" if country else postcode
    return country or "London"


def fetch_weather_data(city: str, country: str = "", postcode: str = ""):
    query = build_location_query(country, city, postcode)
    if API_KEY == "demo":
        return {
            "name": city or postcode or "London",
            "sys": {"country": country or "GB"},
            "main": {"temp": 18, "feels_like": 17, "humidity": 60},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 7},
            "coord": {"lat": 51.5074, "lon": -0.1278},
            "list": [
                {
                    "dt": 1700000000,
                    "main": {"temp": 18, "feels_like": 17, "temp_min": 15, "temp_max": 20},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                },
                {
                    "dt": 1700086400,
                    "main": {"temp": 17, "feels_like": 16, "temp_min": 14, "temp_max": 19},
                    "weather": [{"main": "Clouds", "description": "few clouds"}],
                },
                {
                    "dt": 1700172800,
                    "main": {"temp": 16, "feels_like": 15, "temp_min": 13, "temp_max": 18},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                },
                {
                    "dt": 1700259200,
                    "main": {"temp": 15, "feels_like": 14, "temp_min": 12, "temp_max": 17},
                    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                },
                {
                    "dt": 1700345600,
                    "main": {"temp": 19, "feels_like": 18, "temp_min": 16, "temp_max": 21},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                },
                {
                    "dt": 1700432000,
                    "main": {"temp": 20, "feels_like": 19, "temp_min": 17, "temp_max": 23},
                    "weather": [{"main": "Clouds", "description": "broken clouds"}],
                },
                {
                    "dt": 1700518400,
                    "main": {"temp": 18, "feels_like": 17, "temp_min": 15, "temp_max": 20},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                },
            ],
        }

    params = {"q": query, "appid": API_KEY, "units": "metric"}
    forecast_response = requests.get(f"{BASE_URL}/forecast", params=params, timeout=20)
    forecast_response.raise_for_status()
    current_response = requests.get(f"{BASE_URL}/weather", params=params, timeout=20)
    current_response.raise_for_status()

    current_data = current_response.json()
    forecast_data = forecast_response.json()
    current_data["list"] = forecast_data.get("list", [])[:7]
    return current_data


def summarize_forecast(payload):
    grouped = {}

    for item in payload.get("list", []):
        dt = item.get("dt")
        if dt is None:
            continue

        day_key = datetime.fromtimestamp(dt, timezone.utc).date().isoformat()
        bucket = grouped.setdefault(
            day_key,
            {"temps": [], "temp_min_values": [], "temp_max_values": [], "feels_like_values": [], "condition": "N/A", "description": "N/A"},
        )

        main = item.get("main", {})
        weather = (item.get("weather") or [{}])[0]
        temp = main.get("temp")
        if temp is not None:
            bucket["temps"].append(temp)
        temp_min = main.get("temp_min", temp)
        temp_max = main.get("temp_max", temp)
        if temp_min is not None:
            bucket["temp_min_values"].append(temp_min)
        if temp_max is not None:
            bucket["temp_max_values"].append(temp_max)
        feels_like = main.get("feels_like", temp)
        if feels_like is not None:
            bucket["feels_like_values"].append(feels_like)
        if weather.get("main"):
            bucket["condition"] = weather.get("main")
        if weather.get("description"):
            bucket["description"] = weather.get("description")

    days = []
    for day_key in sorted(grouped):
        bucket = grouped[day_key]
        temps = bucket["temps"]
        temp_min_values = bucket["temp_min_values"] or temps
        temp_max_values = bucket["temp_max_values"] or temps
        feels_values = bucket["feels_like_values"] or temps
        days.append(
            {
                "date": datetime.fromisoformat(f"{day_key}T00:00:00+00:00").strftime("%a %d %b"),
                "temp_min": round(min(temp_min_values)),
                "temp_max": round(max(temp_max_values)),
                "feels_like": round(sum(feels_values) / len(feels_values)),
                "condition": bucket["condition"],
                "description": bucket["description"],
            }
        )

    return days[:7]


def render_weather():
    st.title("7-Day Local Weather Forecast")
    st.write("Check the weather for your location.")

    with st.form("weather_form"):
        country = st.text_input("Country", value="GB")
        city = st.text_input("City")
        postcode = st.text_input("Postcode")
        submitted = st.form_submit_button("Get Forecast")

    if not submitted:
        return

    try:
        data = fetch_weather_data(city=city, country=country, postcode=postcode)
    except Exception as exc:
        st.error(f"Unable to fetch weather data: {exc}")
        return

    location_name = data.get("name")
    country_name = data.get("sys", {}).get("country", "")
    st.subheader(f"{location_name}, {country_name}")

    current = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    wind = data.get("wind", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{round(current.get('temp', 0))}°C")
    col2.metric("Feels like", f"{round(current.get('feels_like', 0))}°C")
    col3.metric("Humidity", f"{current.get('humidity', 0)}%")

    st.write(f"Condition: {weather.get('main', 'N/A')} - {weather.get('description', 'N/A')}")
    st.write(f"Wind speed: {wind.get('speed', 0)} m/s")

    lat = data.get("coord", {}).get("lat")
    lon = data.get("coord", {}).get("lon")
    if lat is not None and lon is not None:
        st.map({"lat": [lat], "lon": [lon]})

    forecast = summarize_forecast(data)
    st.subheader("Next 7 Days")
    for day in forecast:
        st.write(f"{day['date']} — {day['condition']} ({day['description']}) | {day['temp_min']}°C to {day['temp_max']}°C | Feels like {day['feels_like']}°C")


if __name__ == "__main__":
    render_weather()
