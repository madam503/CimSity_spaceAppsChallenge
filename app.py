# filename: app.py
from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI(title="Jeju Data + Gemini API")

# ----- CONFIG -----
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_KEY"  # replace with your OpenWeatherMap key
JEJU_LAT = 33.4996
JEJU_LON = 126.5312

# Gemini integration placeholder
def get_gemini_insight(data):
    """
    This function will eventually send 'data' to Gemini
    and return human-readable insights.
    For now, it just summarizes AQI and weather.
    """
    aqi = data["air_pollution"]["aqi"]
    temp = data["weather"]["temp_c"]
    humidity = data["weather"]["humidity"]
    
    insight = f"Current AQI in Jeju-si is {aqi} (moderate). " \
              f"Temperature is {temp}°C with humidity {humidity}%."
    return insight

# ----- ROUTES -----
@app.get("/api/jeju/air_pollution")
def get_air_pollution():
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={JEJU_LAT}&lon={JEJU_LON}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Normalize JSON
    air_data = data["list"][0]
    normalized = {
        "location": "Jeju-si",
        "air_pollution": {
            "aqi": air_data["main"]["aqi"],
            "co": air_data["components"]["co"],
            "no2": air_data["components"]["no2"],
            "o3": air_data["components"]["o3"],
            "pm2_5": air_data["components"]["pm2_5"],
            "pm10": air_data["components"]["pm10"]
        },
        "timestamp": air_data["dt"]
    }
    return normalized

@app.get("/api/jeju/weather")
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={JEJU_LAT}&lon={JEJU_LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    normalized = {
        "location": "Jeju-si",
        "weather": {
            "temp_c": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["description"]
        },
        "timestamp": int(datetime.now().timestamp())
    }
    return normalized

@app.get("/api/jeju/insights")
def get_jeju_insights():
    # Fetch real-time air pollution
    air = get_air_pollution()
    # Fetch real-time weather
    weather = get_weather()
    
    combined_data = {
        "air_pollution": air["air_pollution"],
        "weather": weather["weather"],
        "location": "Jeju-si",
        "timestamp": int(datetime.now().timestamp())
    }
    
    # Gemini insight (currently placeholder)
    insight_text = get_gemini_insight(combined_data)
    combined_data["insight"] = insight_text
    
    return combined_data
