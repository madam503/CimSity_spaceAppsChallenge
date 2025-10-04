import requests
from fastapi import HTTPException
from city_env_toolkit.config import OPENWEATHER_API_KEY, CITIES

BASE_URL = "http://api.openweathermap.org/data/2.5"

def get_weather_data(city_name: str):
    """Fetches real-time weather information from the OpenWeatherMap API."""
    if city_name not in CITIES:
        return {"error": "Unknown city"}
    
    city_info = CITIES[city_name]
    lat, lon = city_info["lat"], city_info["lon"]
    
    url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "temp_c": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"]
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Weather service unavailable: {e}")

def get_air_pollution_data(city_name: str):
    """Fetches real-time air pollution information from the OpenWeatherMap API."""
    if city_name not in CITIES:          
        return {"error": "Unknown city"}
    
    city_info = CITIES[city_name]           
    lat, lon = city_info["lat"], city_info["lon"]

    url = f"{BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        air_data = response.json()["list"][0]
        return {
            "aqi": air_data["main"]["aqi"],
            "co": air_data["components"]["co"],
            "pm2_5": air_data["components"]["pm2_5"]
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Air pollution service unavailable: {e}")